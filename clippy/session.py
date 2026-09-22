"""Session graph (phase 3): the app's topology as data, wired from edges.

:class:`Session` owns the live app: the prime Pi process (or mock), the prime
controller, the pane, and one sub-clippy worker at a time. Its wiring is a
*projection of* :func:`clippy.model.build_session_graph` — the callback
channels (answer/card/prompt) come from the graph's ``projects_to`` /
``triggers`` / ``rendered_as`` edges, and the topology is validated
structurally before the app runs. ``Session.dump()`` is the provenance view:
"why does this event reach the pane?".

Mode (sandbox ↔ build) re-spawns the prime because Pi 0.85.1 fixes the tool
set at spawn only (research/pi-community-deep-dive.md §3).
"""

from __future__ import annotations

import datetime
import queue
from pathlib import Path

import pyglet

from .brain import DEFAULT_MODEL, MockBrain, PiBrain
from .controller import SubClippyController
from .memory import ensure_memory, resolve_skill_paths
from .model import Delegation, build_session_graph, required_topology
from .pane import Pane
from .prime import PrimeController
from .shell import ClippyShell
from .subagent import (
    DEFAULT_TASK,
    DELEGATE_CMD,
    SANDBOX_TOOLS,
    MockSubAgent,
    PiSubAgent,
    parse_delegation,
    parse_move,
    pi_ready,
)
from .notify import notify
from .scheduler import parse_notify, parse_schedule, parse_trigger
from .timeutil import humanize, time_header

#: Build-mode consent gate extension (016): asks before mutating tools.
GATE_EXT = str(
    Path(__file__).resolve().parent / "extensions" / "clippy-gate.ts"
)

#: Reliable chat commands the user types in the pane (host-intercepted, like
#: /delegate): move Clippy to a spot or absolute coords, ask where he is, or
#: list what's possible. Anything else the user types goes to the brain.
HELP_CMD = "/help"
EXIT_CMD = "/exit"
MOOD_CMD = "/mood"
MOVE_CMD = "/move"
QUIT_CMD = "/quit"
REMIND_CMD = "/remind"
SCHEDULE_CMD = "/schedule"
SKILL_CMD = "/skill"
SKILLS_CMD = "/skills"
TEST_CMD = "/test"
TIME_CMD = "/time"
WHERE_CMD = "/where"

#: Shown by /help (markdown — the pane renders clippy bubbles as markdown).
#: Commands are the built-in API (host-intercepted, deterministic); skills are
#: the skill folder / model tools — see ADR-0001.
HELP_TEXT = (
    "Here's what I can do — **commands** (built-in API):\n"
    "- `/help` — show this list\n"
    "- `/exit` or `/quit` — close Clippy gracefully\n"
    "- `/skills` — list my skills; `/skill <name> [request]` invokes one\n"
    "- `/mood` — list my moods; `/mood <name>` plays any of the catalog's "
    "animations directly (e.g. `/mood greet`, `/mood working build`, "
    "`/mood GestureRight`), and `/mood idle <animation>` pins a specific "
    "idle animation\n"
    "- `/delegate <task>` — hand a self-contained task to a sub-clippy worker\n"
    "  and it reports back (e.g. `/delegate count the markdown files`)\n"
    "- `/move <spot>` or `/move <x> <y>` — move me on screen (spots: "
    "top-left / top-right / bottom-left / bottom-right / center / left / "
    "right / top / bottom)\n"
    "- `/remind <when> <what>` — schedule a reminder (e.g. `/remind in 5 "
    "minutes stretch`, `/remind daily at 9:00 standup`)\n"
    "- `/schedule` — list scheduled tasks; `/schedule cancel <id>` removes one\n"
    "- `/time` — tell you the current time\n"
    "- `/test card` — render a sample consent card (diagnostics)\n"
    "- `/where` — tell you where I am on screen\n\n"
    "**Skills** live in the skill folder (e.g. `memory`, `move`, `sub-clippy`) — "
    "see `/skills`. `/move` and `/delegate` are command aliases for two of "
    "them.\n"
    "Anything else, just chat! You can also press **Tab** in the pane to "
    "toggle between sandbox (read-only) and build (mutation-gated) mode."
)


def command_matches(low: str, cmd: str) -> bool:
    """True if ``low`` is exactly ``cmd`` or ``cmd`` followed by an argument.

    Avoids prefix collisions like ``/helper`` matching ``/help``: the command
    token must end at whitespace or the end of the line.
    """
    return low == cmd or low.startswith(cmd + " ")


def resolve_worker_tools(delegation_tools, caller_tools) -> tuple:
    """Resolve a worker's tool allowlist, never falling through to "all tools".

    Precedence: the delegation's own tools, else the caller's, else the
    standard read/search sandbox. An empty result is impossible — a worker is
    always at most sandboxed.
    """
    return tuple(delegation_tools or ()) or tuple(caller_tools or ()) or tuple(SANDBOX_TOOLS)


class Session:
    def __init__(self, shell, model: str = DEFAULT_MODEL, real: bool = False):
        self.shell = shell
        self.model = model
        self.real = real
        self.mode = "sandbox"
        self.brain = None
        self.prime_controller = None
        self._worker_controller = None
        self._worker_delegation: Delegation | None = None

        self.graph = build_session_graph()
        self._validate_topology()

        cfg = self.shell.avatar.moods.config

        #: Per-conversation JSONL chat log (gated by config logging.enabled).
        #: The prime gets one file for its whole run; each sub-clippy gets its
        #: own file (see _spawn_worker). Everything flushes per line, so logs
        #: survive crashes/hangs.
        self.logging_enabled = bool((cfg.get("logging") or {}).get("enabled", True))
        self._prime_log = None
        if self.logging_enabled:
            from .chatlog import ChatLogger, make_chat_log

            self._prime_log = ChatLogger(make_chat_log("prime"), label="prime")
            self._prime_log.marker("chat_start")

        #: Background memory curator config (memory block). A proxy model owns
        #: memory writes, batched every ``every_n_turns`` user turns (see
        #: clippy/curator.py). Empty ``curator_model`` reuses the prime model.
        memory_cfg = cfg.get("memory") or {}
        self.memory_enabled = bool(memory_cfg.get("enabled", True))
        self.memory_every_n_turns = max(1, int(memory_cfg.get("every_n_turns", 3)))
        self.memory_curator_model = (memory_cfg.get("curator_model") or "").strip() or None
        self._memory_batch: list[tuple[str, str]] = []   # (user_text, answer)
        self._pending_user_text: str | None = None       # latest user message awaiting an answer
        self._curator_busy = False

        self.pane = Pane(shell)
        shell.pane = self.pane
        self.pane.start_driver()
        self.pane.on_mode_toggle = self._queue_toggle
        # Drag/resize geometry must be applied on the main thread (AppKit frame
        # mutations can't run on WebKit's script-handler thread).
        self.pane.on_move = self._queue_pane_move
        self.pane.on_resize = self._queue_pane_resize

        # JS→Python events arrive on WebKit's script-handler thread, never
        # on the main loop thread — queue them and run them on the frame tick
        # so pyglet/WKWebView are only ever re-entered from the main thread
        # (re-spawning a brain from a background thread aborts the app).
        self._pending: queue.Queue = queue.Queue()
        #: Wall-clock graph/FSM scheduler (time-and-scheduling). Runs on the
        #: existing loop; scheduled brain actions are queued and fired when the
        #: prime is idle (no heartbeat — see clippy/scheduler.py).
        from .scheduler import TaskScheduler

        self.scheduler = TaskScheduler(dispatch=self._scheduled_action)
        self._scheduled_brain_q: queue.Queue = queue.Queue()
        pyglet.clock.schedule_interval(self.update, 1 / 60)
        self._spawn_prime()
        self._wire()

    # ------------------------------------------------------------ topology

    def _validate_topology(self):
        missing = self.graph.validate_topology(required_topology())
        if missing:
            raise RuntimeError(
                "session graph missing required connections:\n- " + "\n- ".join(missing)
            )

    def _bind_prime(self):
        """Project the answer/card edges onto the current prime controller.

        ``toggle()`` re-spawns the prime, and each new controller starts with
        ``on_answer``/``on_ui_request`` unset — bind them per spawn or the
        build brain's answers and gate cards are silently dropped. The pane is
        bound per spawn too so the reasoning stream keeps flowing after a
        re-spawn.
        """
        self.prime_controller.pane = self.pane
        for e in self.graph.edges_of("projects_to"):
            if e.dst == "pane" and e.attrs.get("channel") == "answer":
                self.prime_controller.on_answer = self._on_answer
            elif e.dst == "pane" and e.attrs.get("channel") == "card":
                self.prime_controller.on_ui_request = self.pane.ui_request

    def _wire(self):
        """Bind callbacks from the graph edges (the wiring is a projection)."""
        self._bind_prime()
        for e in self.graph.edges_of("triggers"):
            if e.src == "chat_input" and e.dst == "prime":
                self.pane.on_chat = self._queue_chat
        for e in self.graph.edges_of("rendered_as"):
            if e.src == "dialog" and e.dst == "pane":
                self.pane.on_ui_response = self._queue_ui

    def _queue_chat(self, text: str):
        self._pending.put(("chat", text))

    def _queue_ui(self, rid, payload: dict):
        self._pending.put(("ui_response", rid, payload))

    def _queue_toggle(self):
        self._pending.put(("mode_toggle",))

    def _queue_pane_move(self, data: dict):
        self._pending.put(("pane_move", data))

    def _queue_pane_resize(self, data: dict):
        self._pending.put(("pane_resize", data))

    def update(self, dt):
        """Run queued JS→Python callbacks + scheduler ticks on the main thread.

        Each job is isolated: a bad message or a command-parsing error must not
        take down the frame tick (and with it the whole app).
        """
        # Advance the wall-clock scheduler (fires due tasks; brain actions queue
        # until idle).
        try:
            self.scheduler.tick()
        except Exception:
            self._log_error("scheduler.tick")
        while True:
            try:
                job = self._pending.get_nowait()
            except queue.Empty:
                break
            try:
                self._dispatch_job(job)
            except Exception:
                self._log_error(f"job {job[0]!r}")
        # Fire queued scheduled-brain actions only when the prime is idle (its
        # PRIME_CONVERSATION SM is back to "idle"), so we never interrupt a
        # turn and never burn heartbeat tokens.
        if self._scheduled_brain_q.qsize() and self._prime_idle():
            try:
                self.brain.prompt(
                    self._scheduled_brain_q.get_nowait(),
                    streaming_behavior="followUp",
                )
            except Exception:
                self._log_error("scheduled brain prompt")

    def _dispatch_job(self, job):
        kind = job[0]
        if kind == "chat":
            if self._prime_log is not None:
                self._prime_log.user(job[1])
            self.prompt(job[1])
        elif kind == "ui_response":
            self.ui_response(job[1], job[2])
        elif kind == "mode_toggle":
            self.toggle()
        elif kind == "pane_move":
            self.pane._on_pane_move(job[1])
        elif kind == "pane_resize":
            self.pane._on_pane_resize(job[1])

    @staticmethod
    def _log_error(where: str):
        import traceback

        print(f"[clippy] {where} failed (kept alive):", flush=True)
        traceback.print_exc()

    def _prime_idle(self) -> bool:
        sm = getattr(self.prime_controller, "sm", None)
        return sm is None or sm.is_in("idle")

    def _scheduled_action(self, action: dict):
        """Dispatch a scheduled task's action (host effect or queued brain)."""
        kind = action.get("type")
        if kind == "pane":
            self.pane.add_message("clippy", action.get("text", ""))
        elif kind == "notify":
            # OS notification; fall back to a pane message when no notifier.
            if not notify(action.get("title", "Clippy"), action.get("text", "")):
                self.pane.add_message("clippy", action.get("text", ""))
        elif kind == "mood":
            self.shell.express(action.get("mood", "greeting"), hint=action.get("hint"), force=True)
        elif kind == "brain":
            # Queue; drained in update() when the prime is idle.
            self._scheduled_brain_q.put(action.get("text", ""))
        else:
            print(f"[clippy] unknown scheduled action {action!r}", flush=True)

    def dump(self) -> str:
        text = self.graph.dump()
        d = self._worker_delegation
        if d is not None:
            text += (
                "\n## Current delegation\n"
                f"- id: {d.id}\n"
                f"- text: {d.text}\n"
                f"- tools: {', '.join(d.tools)}\n"
                f"- model: {d.model or '(default)'}\n"
                f"- source: {d.source}\n"
            )
        else:
            text += "\n## Current delegation\n- none\n"
        return text

    # --------------------------------------------------------------- prime

    def _brain_kwargs(self) -> dict:
        kwargs = {"model": self.model}
        if self.mode == "sandbox":
            kwargs["tools"] = SANDBOX_TOOLS
        else:
            kwargs["extensions"] = [GATE_EXT]
        kwargs["append_system_prompt"] = ensure_memory()
        kwargs["skills"] = resolve_skill_paths()
        return kwargs

    def _spawn_prime(self):
        if self.prime_controller is not None:
            pyglet.clock.unschedule(self.prime_controller.update)
        if self.real or pi_ready():
            brain = PiBrain(**self._brain_kwargs())
            label = f"{self.mode} mode on Pi RPC ({self.model})"
        else:
            brain = MockBrain()
            label = "mock (Pi not ready)"
        try:
            brain.start()
        except OSError as exc:
            # `--real` (or a stale PATH) can point at a missing/broken binary;
            # degrade to the mock rather than crash the app on startup.
            print(f"[clippy] brain failed to start ({exc}); using mock", flush=True)
            brain = MockBrain()
            brain.start()
            label = f"mock (start failed: {exc})"
        print(f"[clippy] prime brain: {label}")
        self.brain = brain
        self.prime_controller = PrimeController(self.shell, brain)
        # Keep the same per-run chat log attached across Tab-toggle re-spawns.
        if self._prime_log is not None:
            self.prime_controller.router.logger = self._prime_log
        self._bind_prime()
        self.shell.mode = self.mode
        self.shell.dialog_pending = False
        pyglet.clock.schedule_interval(self.prime_controller.update, 1 / 60)
        self.pane.set_mode(self.mode)

    def prompt(self, text: str, remember: bool = True):
        """Handle one chat input. Commands are answered locally; anything else
        goes to the brain. ``remember=False`` marks host-generated turns (mode
        changes) that should not be staged for memory curation."""
        stripped = text.strip()
        low = stripped.lower()
        if command_matches(low, HELP_CMD):
            self.pane.add_message("clippy", HELP_TEXT)
            return
        if command_matches(low, EXIT_CMD) or command_matches(low, QUIT_CMD):
            self._quit()
            return
        if command_matches(low, WHERE_CMD):
            x, y = self.shell.position
            self.pane.add_message("clippy", f"I'm at ({x}, {y}).")
            return
        if command_matches(low, MOOD_CMD):
            self._run_mood(stripped[len(MOOD_CMD):].strip())
            return
        if command_matches(low, MOVE_CMD):
            self._run_move(self._command_move_spec(stripped[len(MOVE_CMD):].strip()))
            return
        # Exact-token matching keeps /skills and /skill distinct (see
        # command_matches); the folder remains the source of truth.
        if command_matches(low, SKILLS_CMD):
            self._list_skills()
            return
        if command_matches(low, SKILL_CMD):
            arg = stripped[len(SKILL_CMD):].strip()
            name, _, request = arg.partition(" ")
            self._invoke_skill(name.strip(), request.strip())
            return
        if command_matches(low, TEST_CMD):
            self._run_test(stripped[len(TEST_CMD):].strip())
            return
        if command_matches(low, TIME_CMD):
            self.pane.add_message("clippy", humanize())
            return
        if command_matches(low, REMIND_CMD):
            self._run_remind(stripped[len(REMIND_CMD):].strip())
            return
        if command_matches(low, SCHEDULE_CMD):
            self._run_schedule(stripped[len(SCHEDULE_CMD):].strip())
            return
        if command_matches(low, DELEGATE_CMD):
            task = stripped[len(DELEGATE_CMD):].strip()
            if not task:
                self.pane.add_message(
                    "clippy", "What should the sub-clippy do? e.g. `/delegate count the markdown files`"
                )
                return
            self._start_delegation(task)
            return
        if stripped.startswith("/"):
            # Unknown slash command. Don't forward it to the brain: it would be
            # read as a normal user message and can get mixed up with pending
            # brain context (e.g. a delegation relay), producing the confused
            # "stale command alongside fresh one" replies. Answer locally.
            self.pane.add_message(
                "clippy",
                f"`{stripped}` isn't a command I know — try `/help` to see "
                "what I can do.",
            )
            return
        # Brain-bound: inject a compact host-computed time header so Clippy is
        # time-aware without a heartbeat (the model can't run `date` in sandbox),
        # plus a short pointer to the next scheduled task.
        if remember:
            # Stage the user's message for the memory curator; only a real
            # user turn qualifies (not a slash command, not a host message).
            self._pending_user_text = stripped
        self.brain.prompt(
            f"{time_header()} Scheduled: {self.scheduler.brief()}\n\n{text}",
            streaming_behavior="followUp",
        )

    # ------------------------------------------------------------- movement

    def _command_move_spec(self, arg: str) -> str | tuple[int, int] | None:
        """Interpret a /move argument: ``<x> <y>`` coords or a named spot."""
        if not arg:
            return None
        parts = arg.split()
        if len(parts) == 2:
            try:
                return (int(parts[0]), int(parts[1]))
            except ValueError:
                return None
        return arg.strip().lower()

    def _run_move(self, spec: str | tuple[int, int] | None):
        """Apply a move spec (spot name or (x, y)) and confirm in the pane.
        Used by both the /move command and the brain's [CLIPPY::MOVE] block."""
        if isinstance(spec, tuple):
            x, y = spec
            self.shell.move_to(x, y)
            self.pane.add_message("clippy", f"Moved to ({x}, {y}).")
            return
        if isinstance(spec, str) and spec in self.shell.SPOTS:
            self.shell.move_to_spot(spec)
            self.pane.add_message("clippy", f"Moved to {spec}.")
            return
        self.pane.add_message(
            "clippy",
            "`/move <spot>` (top-left/top-right/bottom-left/bottom-right/"
            "center/left/right/top/bottom) or `/move <x> <y>`.",
        )

    # ----------------------------------------------------------- time/tasks

    def _run_remind(self, arg: str):
        """Schedule a reminder: ``/remind <when> <what>`` (wall-clock,
        JSONL-persisted — survives restarts)."""
        trigger, what = parse_trigger(arg)
        if not trigger or not what:
            self.pane.add_message(
                "clippy",
                "I can schedule: `/remind in 5 minutes <what>`, "
                "`/remind at 14:30 <what>`, `/remind every 2 hours <what>`, or "
                "`/remind daily at 9:00 <what>`.",
            )
            return
        task = self.scheduler.add(trigger, {"type": "notify", "title": "Reminder", "text": what})
        from .timeutil import format_wallclock

        self.pane.add_message(
            "clippy",
            f"Reminder set for **{format_wallclock(task.wake_at)}** "
            f"(`{task.id}`): {what}",
        )

    def _run_schedule(self, arg: str):
        """List or cancel scheduled tasks: ``/schedule``, ``/schedule cancel <id>``."""
        rest = arg.strip()
        if rest.lower().startswith("cancel"):
            task_id = rest.split(None, 1)[1].strip() if " " in rest else ""
            if task_id and self.scheduler.cancel(task_id):
                self.pane.add_message("clippy", f"Cancelled task `{task_id}`.")
            else:
                self.pane.add_message("clippy", f"No scheduled task `{task_id}`.")
            return
        tasks = self.scheduler.list()
        if not tasks:
            self.pane.add_message("clippy", "Nothing scheduled.")
            return
        from .timeutil import format_wallclock

        lines = [f"I have {len(tasks)} scheduled task(s):"]
        for d in tasks:
            what = d["action"].get("text") or d["action"].get("mood") or d["action"].get("type")
            lines.append(f"- `{d['id']}` — **{format_wallclock(d['wake_at'])}** · {what}")
        self.pane.add_message("clippy", "\n".join(lines))

    def _quit(self):
        """Gracefully close the app: show a goodbye, then end the main loop so
        main.py can stop the brain and the loggers/curator can flush."""
        self.pane.add_message("clippy", "Goodbye! 👋")
        # Exit on the next pump so the pane repaints the goodbye and any pending
        # scheduler/log writes flush before the loop ends.
        pyglet.clock.schedule_once(lambda dt: pyglet.app.exit(), 0.4)

    # ---------------------------------------------------------------- moods

    def _list_moods(self) -> str:
        """Markdown summary of the moods AND every catalog animation, so the
        user can pick any of them (``/mood <name>`` plays it directly)."""
        moods = self.shell.avatar.moods
        animations = self.shell.avatar.animations
        lines = ["**Moods** (`/mood <mood>`):"]
        # idle lives under the top-level config "idle" key, not the "moods"
        # block, so list it explicitly (with its settle pose + pool).
        lines.append(
            f"- `idle` — {moods.idle['settle']} / pool: "
            + ", ".join(moods.idle["pool"])
        )
        for name in sorted(moods.available_moods()):
            spec = moods.moods[name]
            anims = spec.get("animations") or []
            hints = spec.get("hints") or {}
            parts = [f"`{name}`"]
            if anims:
                parts.append(", ".join(anims))
            if hints:
                parts.append(f"hints: {', '.join(sorted(hints))}")
            lines.append("- " + " — ".join(parts))
        # Animations not referenced by any mood/hint can still be played
        # directly — group them so the full catalog is discoverable.
        referenced = set(moods.idle["pool"]) | {moods.idle["settle"]}
        for spec in moods.moods.values():
            referenced.update(spec.get("animations") or [])
            referenced.update((spec.get("hints") or {}).values())
        extras = sorted(a for a in animations if a not in referenced)
        if extras:
            lines.append("**Play any animation directly** (`/mood <name>`):")
            groups = {}
            for a in extras:
                key = (
                    "gestures" if a.startswith("Gesture")
                    else "looks" if a.startswith("Look")
                    else "misc"
                )
                groups.setdefault(key, []).append(a)
            for key in ("gestures", "looks", "misc"):
                if groups.get(key):
                    lines.append(f"- {key}: {', '.join(f'`{a}`' for a in groups[key])}")
        return "\n".join(lines)

    def _run_mood(self, arg: str):
        """Handle the /mood command: list the catalog, drive a mood (optionally
        with a hint), or play ANY animation from the catalog directly. Uses
        ``force=True`` so any mood can be shown even while a continuous mood is
        running."""
        moods = self.shell.avatar.moods
        animations = self.shell.avatar.animations
        parts = arg.split()
        mood = parts[0].lower() if parts else ""
        hint = parts[1].lower() if len(parts) > 1 else None
        if not mood:
            self.pane.add_message("clippy", self._list_moods())
            return
        # "idle" is a real mood but lives under the top-level config "idle"
        # key, so it isn't in the "moods" catalog — add it to the valid set.
        valid_moods = {"idle"} | set(moods.available_moods())
        anim_lookup = {a.lower(): a for a in animations}

        if mood in valid_moods:
            hints = (moods.moods.get(mood) or {}).get("hints") or {}
            # /mood idle <pool-animation> pins a specific idle-pool animation.
            if mood == "idle" and hint:
                pool = {a.lower(): a for a in moods.idle["pool"]}
                if hint in pool:
                    if not (self.shell.express("idle", force=True)
                            and self.shell.play_idle_animation(pool[hint])):
                        self.pane.add_message("clippy", f"`{pool[hint]}` couldn't be played.")
                        return
                    self.pane.add_message("clippy", f"Playing idle animation `{pool[hint]}`.")
                    return
            if hint is not None and hint not in hints:
                if not hints:
                    self.pane.add_message(
                        "clippy", f"`{mood}` doesn't take a hint."
                    )
                else:
                    self.pane.add_message(
                        "clippy",
                        f"`{mood}` doesn't have a `{hint}` hint — its hints are: "
                        f"{', '.join(sorted(hints))}.",
                    )
                return
            if not self.shell.express(mood, hint=hint, force=True):
                self.pane.add_message("clippy", f"`{mood}` couldn't be played.")
                return
            resolved = moods.resolve(mood, hint)
            label = mood + (f"/{hint}" if hint else "")
            self.pane.add_message(
                "clippy",
                f"Playing `{label}`" + (f" — `{resolved}`" if resolved else "") + ".",
            )
            return

        # Not a mood — maybe a direct animation name from the catalog.
        if mood in anim_lookup:
            name = anim_lookup[mood]
            if not self.shell.play_animation(name):
                self.pane.add_message("clippy", f"`{name}` couldn't be played.")
                return
            self.pane.add_message("clippy", f"Playing animation `{name}`.")
            return

        self.pane.add_message(
            "clippy",
            f"`{mood}` isn't a mood or animation I know — try `/mood` for the "
            "full list.",
        )

    # ---------------------------------------------------------------- skills
    # Skills live in the skill folder (clippy/skills or skills.allow) and are
    # model-invocable tools. /skills lists them; /skill <name> invokes one —
    # deterministically via the built-in API for host-backed skills (move,
    # sub-clippy), brain-routed for the rest. See ADR-0001.

    #: Built-in command aliases for host-backed skills, shown in the /skills
    #: listing so the dual nature (skill folder + deterministic command) is
    #: explicit rather than confusing.
    SKILL_ALIASES = {"move": "/move", "sub-clippy": "/delegate"}
    #: Backing note for skills handled by a background process or the host
    #: rather than a command alias.
    SKILL_BACKING = {
        "memory": "background curator",
        "schedule": "host schedules a task",
        "notify": "host posts an OS notification",
    }

    def _list_skills(self):
        from .memory import list_skills

        skills = list_skills()
        if not skills:
            self.pane.add_message(
                "clippy", "I don't have any skills enabled right now."
            )
            return
        lines = [f"I have {len(skills)} skill(s):"]
        for s in skills:
            line = f"- **{s['name']}**"
            if s["description"]:
                line += f" — {s['description']}"
            alias = self.SKILL_ALIASES.get(s["name"])
            backing = self.SKILL_BACKING.get(s["name"])
            if alias:
                line += f" *(alias: `{alias}`)*"
            elif backing:
                line += f" *({backing})*"
            lines.append(line)
        lines.append("\n`/skill <name> [request]` invokes one (commands like "
                     "`/move` and `/delegate` are the built-in API — see `/help`).")
        self.pane.add_message("clippy", "\n".join(lines))

    def _invoke_skill(self, name: str, request: str):
        from .memory import list_skills

        skills = {s["name"].lower(): s for s in list_skills()}
        key = name.lower()
        if not name or key not in skills:
            known = ", ".join(f"`{s['name']}`" for s in list_skills())
            self.pane.add_message(
                "clippy",
                f"`{name or '<name>'}` isn't a skill I have — try `/skills` "
                f"(available: {known}).",
            )
            return
        skill = skills[key]
        skill_name = skill["name"]
        hint = skill["description"] or f"The `{skill_name}` skill"

        # Host-backed skills are invoked deterministically through the built-in
        # API (they need a concrete request to act on).
        if skill_name == "move":
            if not request:
                self.pane.add_message(
                    "clippy", f"{hint} — e.g. `/skill move top-left`."
                )
                return
            self._run_move(self._command_move_spec(request))
            return
        if skill_name == "sub-clippy":
            if not request:
                self.pane.add_message(
                    "clippy",
                    f"{hint} — e.g. `/skill sub-clippy count the markdown files`.",
                )
                return
            self._start_delegation(request)
            return
        if skill_name == "memory":
            # Memory writes are owned by the background curator (a proxy model
            # with write/edit tools), not the sandboxed prime brain — spawn it
            # directly with the request.
            if not request:
                self.pane.add_message(
                    "clippy",
                    f"{hint} — e.g. `/skill memory remember that I like espresso`.",
                )
                return
            self._curate([("", request)])
            self.pane.add_message(
                "clippy", "Handing that to my memory curator."
            )
            return
        if skill_name == "schedule":
            # Reuse the /remind path: `<when> <what>` → wall-clock task + notify.
            if not request:
                self.pane.add_message(
                    "clippy",
                    f"{hint} — e.g. `/skill schedule in 5 minutes take a break`.",
                )
                return
            self._run_remind(request)
            return
        if skill_name == "notify":
            if not request:
                self.pane.add_message(
                    "clippy", f"{hint} — e.g. `/skill notify Search finished`."
                )
                return
            if not notify("Clippy", request):
                self.pane.add_message("clippy", request)
            else:
                self.pane.add_message("clippy", "Notification sent.")
            return

        # Everything else (user-allowlisted skills) is a model tool: route the
        # request to the brain so it invokes the skill and streams the result
        # into the pane.
        if not request:
            self.pane.add_message(
                "clippy",
                f"{hint} — add a request, e.g. `/skill {skill_name} <what to do>`.",
            )
            return
        self.brain.prompt(
            f"Use the '{skill_name}' skill to handle this request: {request}",
            streaming_behavior="followUp",
        )

    # ------------------------------------------------------- diagnostics

    _TEST_CARD_PAYLOADS = {
        "confirm": {"title": "Test consent card", "message": "Allow the test tool call?"},
        "select": {"title": "Test select", "message": "Pick an option:", "options": ["one", "two", "three"]},
        "input": {"title": "Test input", "message": "Enter a value:", "placeholder": "type here…", "default": "hello"},
        "editor": {"title": "Test editor", "message": "Edit the value:", "default": "line one\nline two"},
        "notify": {"title": "Test notify", "message": "This is a test notification card."},
    }

    def _run_test(self, arg: str):
        """Diagnostics: ``/test card [method]`` renders a sample dialog card via
        the real ``extension_ui_request → pane.ui_request`` path, so the
        ephemeral UI graph can be exercised from sandbox/mock mode."""
        sub, _, rest = arg.partition(" ")
        sub = (sub or "card").lower()
        if sub == "card":
            method = (rest or "confirm").strip().lower()
            if method not in self._TEST_CARD_PAYLOADS:
                self.pane.add_message(
                    "clippy",
                    "`/test card` methods: "
                    + ", ".join(f"`{m}`" for m in self._TEST_CARD_PAYLOADS)
                    + ".",
                )
                return
            from .model import UiRequest

            ev = UiRequest(
                id="test-card",
                method=method,
                payload=self._TEST_CARD_PAYLOADS[method],
            )
            self.pane.ui_request(ev)  # exact production path → __uiRequest → card
            return
        self.pane.add_message(
            "clippy", "Diagnostics: try `/test card [confirm|select|input|editor|notify]`."
        )

    def ui_response(self, rid, payload: dict):
        print(
            f"[clippy] ui_response {rid} "
            f"confirmed={payload.get('confirmed')} cancelled={payload.get('cancelled')}",
            flush=True,
        )
        self.brain.send({"type": "extension_ui_response", "id": rid, **payload})
        self.shell.dialog_pending = False

    def toggle(self):
        self.brain.stop()
        self.mode = "build" if self.mode == "sandbox" else "sandbox"
        print(f"[clippy] mode -> {self.mode} (re-spawning brain)")
        self._spawn_prime()
        self.prompt(f"Mode is now {self.mode}.", remember=False)

    def _on_answer(self, text: str):
        """Prime's final message: surface it in the pane, and handle any
        directives: [CLIPPY::DELEGATE] spawns a worker, [CLIPPY::MOVE] moves
        Clippy, [CLIPPY::SCHEDULE] schedules a wall-clock notify task, and
        [CLIPPY::NOTIFY] posts an OS notification."""
        print(f"[clippy] answer {len(text)}b", flush=True)
        clean, task = parse_delegation(text)
        clean, move = parse_move(clean)
        clean, trigger, schedule_what = parse_schedule(clean)
        clean, notify_text = parse_notify(clean)
        if task:
            self.shell.set_bubble("(handing off to a sub-clippy…)")
            self.delegate(
                task,
                tools=SANDBOX_TOOLS,
                on_complete=self._on_sub_done,
                source="directive",
            )
        if move:
            self._run_move(move)
        if trigger and schedule_what:
            from .timeutil import format_wallclock

            sched = self.scheduler.add(
                trigger, {"type": "notify", "title": "Reminder", "text": schedule_what}
            )
            self.pane.add_message(
                "clippy",
                f"Reminder set for **{format_wallclock(sched.wake_at)}** "
                f"(`{sched.id}`): {schedule_what}",
            )
        if notify_text:
            if not notify("Clippy", notify_text):
                self.pane.add_message("clippy", notify_text)
        # The reasoning-stream bubble already shows the live answer; close it
        # with the final, directive-stripped text (replaces anything that
        # streamed in, so [CLIPPY::DELEGATE]/[CLIPPY::MOVE]/[CLIPPY::SCHEDULE]/
        # [CLIPPY::NOTIFY] never linger).
        # stream_end("") on a reply that was entirely directives just closes
        # the bubble.
        if clean:
            self.pane.stream_end(clean)
        elif task or (trigger and schedule_what):
            self.pane.stream_end(
                "I've handled that for you."
            )
        else:
            self.pane.stream_end("")
        # Memory curation (batched): pair the user's message that started this
        # turn with the final answer, and hand the batch to the background
        # curator once it reaches the configured turn count.
        self._account_memory(clean)

    def _account_memory(self, clean: str):
        """Pair the staged user turn with the final answer for the curator.

        The staged turn is cleared on *every* final answer, even a directive-only
        or empty one, so a later unrelated answer can never be paired with it.
        """
        if self._pending_user_text is None:
            return
        user_text = self._pending_user_text
        self._pending_user_text = None
        if self.memory_enabled and clean:
            self._memory_batch.append((user_text, clean))
            if (
                len(self._memory_batch) >= self.memory_every_n_turns
                and not self._curator_busy
            ):
                self._curate(self._memory_batch)
                self._memory_batch = []

    def _curate(self, turns: list[tuple[str, str]]):
        """Fire-and-forget a background memory curator over ``turns``."""
        from .curator import MemoryCurator, MockMemoryCurator
        from .roots import MEMORY_DIR

        transcript = "\n\n".join(
            f"USER: {user}\nCLIPPY: {answer}" if user else answer
            for user, answer in turns
        )
        model = self.memory_curator_model or self.model
        # Use the module-level pi_ready (same gate as _spawn_worker), not a
        # fresh import, so tests/offline fall back to the mock curator.
        if self.real or pi_ready():
            agent = MemoryCurator(transcript, model=model, memory_dir=MEMORY_DIR)
        else:
            agent = MockMemoryCurator(transcript, memory_dir=MEMORY_DIR)
        self._curator_busy = True

        def _drain():
            try:
                while True:
                    try:
                        ev = agent.queue.get(timeout=300)
                    except Exception:
                        # Queue timeout / drain error: stop waiting. The
                        # `finally` below makes sure the slot is released even
                        # if the curator never emits sub_exit (hung process).
                        break
                    if ev.get("type") == "sub_exit":
                        break
            finally:
                self._curator_busy = False

        import threading

        threading.Thread(target=_drain, daemon=True).start()
        agent.start()
        print(f"[clippy] memory curator running ({len(turns)} turn(s))", flush=True)

    def _on_sub_done(self, failed: bool, report: str):
        self.shell.set_bubble("(sub-clippy finished — relaying)")
        # A delegated worker may schedule a reminder via a [CLIPPY::SCHEDULE]
        # directive — strip it from the report and create a wall-clock notify
        # task (same bounded triggers + action as the prime's schedule path).
        report, trigger, schedule_what = parse_schedule(report)
        if trigger and schedule_what:
            from .timeutil import format_wallclock

            sched = self.scheduler.add(
                trigger, {"type": "notify", "title": "Reminder", "text": schedule_what}
            )
            self.pane.add_message(
                "clippy",
                f"Reminder set for **{format_wallclock(sched.wake_at)}** "
                f"(`{sched.id}`): {schedule_what}",
            )
        # A delegated worker may also post its own OS notification via a
        # [CLIPPY::NOTIFY] directive — strip it from the report and surface it.
        report, notify_text = parse_notify(report)
        if notify_text:
            notify("Sub-clippy", notify_text)
        else:
            # No worker-authored notification: post the generic completion ping.
            notify(
                "Sub-clippy finished",
                ("Finished with an error." if failed else "Done.")
                + (f" {report[:120]}" if report else ""),
            )
        if report:
            self.pane.add_message("clippy", f"Sub-clippy reported: {report}")
        self.brain.steer(
            "The delegated sub-clippy finished"
            f"{' with an error' if failed else ''}. "
            f"Relay its report to the user plainly: {report or '(no report)'}"
        )

    # --------------------------------------------------------------- worker

    def delegate(
        self,
        task: Delegation | str = DEFAULT_TASK,
        tools=None,
        on_complete=None,
        source: str = "startup",
    ) -> bool:
        """Spawn a sub-clippy for ``task`` (a typed :class:`Delegation`, or a
        bare string coerced to one). Returns False if already delegating.
        The slot frees itself when the worker completes, so a later delegation
        can start a new one."""
        if self._worker_controller is not None:
            print("[clippy] already delegating")
            return False
        if isinstance(task, Delegation):
            d = task
            if (not d.tools and tools) or not d.source:
                # Fill missing pieces (tools and/or source tag) in one re-make.
                # An empty tool set falls back to the sandbox, never "all tools".
                d = Delegation.make(
                    d.text,
                    tools=d.tools or tools or SANDBOX_TOOLS,
                    model=d.model,
                    source=d.source or source,
                )
        else:
            d = Delegation.make(
                task, tools=tools or SANDBOX_TOOLS, model=self.model, source=source
            )
        self._worker_delegation = d

        def _wrap(failed: bool, report: str):
            self._worker_controller = None
            self._worker_delegation = None
            if on_complete:
                on_complete(failed, report)

        self._worker_controller = self._spawn_worker(d, on_complete=_wrap)
        return True

    def _spawn_worker(self, task: Delegation, tools=None, on_complete=None) -> SubClippyController:
        from .roots import SKILLS_DIR

        text = task.text
        model = task.model or self.model
        # Workers are sandboxed by default: the delegation's tools, else the
        # caller's, else the standard read/search sandbox — never Pi's full set.
        tools = resolve_worker_tools(task.tools, tools)
        if self.real or pi_ready():
            # Workers learn the notify + schedule protocols (emit
            # [CLIPPY::NOTIFY] / [CLIPPY::SCHEDULE]) so a delegated task can
            # surface its own notification or schedule a reminder.
            agent = PiSubAgent(
                task=text,
                model=model,
                tools=tools,
                skills=[
                    str(SKILLS_DIR / "notify"),
                    str(SKILLS_DIR / "schedule"),
                ],
            )
            label = f"PI sub-agent ({model})"
        else:
            agent = MockSubAgent(task=text)
            label = "mock sub-agent (Pi not ready)"
        try:
            agent.start()
        except OSError as exc:
            # A missing/broken `pi` must not crash the delegation path.
            print(f"[clippy] sub-agent failed to start ({exc}); using mock", flush=True)
            agent = MockSubAgent(task=text)
            agent.start()
            label = f"mock sub-agent (start failed: {exc})"
        print(f"[clippy] delegating to {label}")
        # Sub-clippy renders at 75% of Prime's scale and spawns beside him (to
        # the right), never directly on top — the sub window is sized from the
        # smaller avatar, so it also fits the delegate bubble on screen.
        prime_scale = getattr(self.shell.avatar, "scale", 1.5)
        sub_scale = round(prime_scale * 0.75, 2)
        px, py = self.shell.position
        pw, _ph = self.shell.size
        sx, sy = px + pw + 12, py
        shell = ClippyShell(scale=sub_scale, position=(sx, sy))
        ctrl = SubClippyController(shell, agent, on_complete=on_complete)
        # Each delegation gets its own chat transcript.
        if self.logging_enabled:
            from .chatlog import ChatLogger, make_chat_log

            stamp = datetime.datetime.now().strftime("%H%M%S")
            worker_log = ChatLogger(make_chat_log(f"subclippy-{stamp}"), label="subclippy")
            worker_log.marker("task", text=text, model=model)
            ctrl.router.logger = worker_log
        shell.show()
        # On X11/XWayland the constructor's set_location runs before the window
        # is mapped and the WM ignores it, so both shells land at the same spot
        # ("sub-clippy on top of Prime"). Re-assert the position now that the
        # window is mapped so the sub actually sits beside Prime.
        shell.set_location(sx, sy)
        pyglet.clock.schedule_interval(shell.update, 1 / 60)
        pyglet.clock.schedule_interval(ctrl.update, 1 / 60)
        # The worker's construction and show() both make ITS GL context current
        # (ClippyShell.__init__ -> switch_to(), show() -> _map() -> on_expose ->
        # on_draw). Restore the prime shell's context so any main-shell GL work
        # after this (settled()'s express, the label redraw) runs under the main
        # window's context — otherwise its sprite/label buffers get rebuilt under
        # the worker's context and the next main on_draw raises a GLException.
        self.shell.switch_to()
        return ctrl

    def _start_delegation(self, task: str):
        self.shell.set_bubble("(handing off to a sub-clippy…)")
        ok = self.delegate(
            task,
            tools=SANDBOX_TOOLS,
            on_complete=self._on_sub_done,
            source="chat",
        )
        if not ok:
            self.pane.add_message(
                "clippy", "A sub-clippy is already at work — let it finish first."
            )
        else:
            self.pane.add_message(
                "clippy", "Handed that to a sub-clippy — report back shortly."
            )
            self.brain.steer(f"The user delegated this task to a sub-clippy: {task}")