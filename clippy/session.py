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

import queue
from pathlib import Path

import pyglet

from .brain import DEFAULT_MODEL, MockBrain, PiBrain
from .controller import SubClippyController
from .memory import ensure_memory, resolve_skill_paths
from .model import build_session_graph, required_topology
from .pane import Pane
from .prime import PrimeController
from .shell import ClippyShell
from .subagent import (
    DEFAULT_TASK,
    DELEGATE_CMD,
    MockSubAgent,
    PiSubAgent,
    parse_delegation,
    parse_move,
    pi_ready,
)

#: Read/search-only tool allowlist for a sandboxed conversation (005).
SANDBOX_TOOLS = ["read", "grep", "find", "ls"]
#: Build-mode consent gate extension (016): asks before mutating tools.
GATE_EXT = str(
    Path(__file__).resolve().parent / "extensions" / "clippy-gate.ts"
)

#: Reliable chat commands the user types in the pane (host-intercepted, like
#: /delegate): move Clippy to a spot or absolute coords, ask where he is, or
#: list what's possible. Anything else the user types goes to the brain.
HELP_CMD = "/help"
MOOD_CMD = "/mood"
MOVE_CMD = "/move"
WHERE_CMD = "/where"

#: Shown by /help (markdown — the pane renders clippy bubbles as markdown).
HELP_TEXT = (
    "Here's what I can do:\n"
    "- `/help` — show this list\n"
    "- `/mood` — list my moods; `/mood <name>` plays any of the catalog's "
    "animations directly (e.g. `/mood greet`, `/mood working build`, "
    "`/mood GestureRight`), and `/mood idle <animation>` pins a specific "
    "idle animation\n"
    "- `/delegate <task>` — hand a self-contained task to a sub-clippy worker\n"
    "  and it reports back (e.g. `/delegate count the markdown files`)\n"
    "- `/move <spot>` or `/move <x> <y>` — move me on screen (spots: "
    "top-left / top-right / bottom-left / bottom-right / center / left / "
    "right / top / bottom)\n"
    "- `/where` — tell you where I am on screen\n\n"
    "Anything else, just chat! You can also press **Tab** in the pane to "
    "toggle between sandbox (read-only) and build (mutation-gated) mode."
)


class Session:
    def __init__(self, shell, model: str = DEFAULT_MODEL, real: bool = False):
        self.shell = shell
        self.model = model
        self.real = real
        self.mode = "sandbox"
        self.brain = None
        self.prime_controller = None
        self._worker_controller = None

        self.graph = build_session_graph()
        self._validate_topology()

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
        """Run queued JS→Python callbacks on the main thread (one per frame)."""
        while True:
            try:
                job = self._pending.get_nowait()
            except queue.Empty:
                return
            kind = job[0]
            if kind == "chat":
                self.prompt(job[1])
            elif kind == "ui_response":
                self.ui_response(job[1], job[2])
            elif kind == "mode_toggle":
                self.toggle()
            elif kind == "pane_move":
                self.pane._on_pane_move(job[1])
            elif kind == "pane_resize":
                self.pane._on_pane_resize(job[1])

    def dump(self) -> str:
        return self.graph.dump()

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
            print(f"[clippy] prime brain: {self.mode} mode on Pi RPC ({self.model})")
        else:
            brain = MockBrain()
            print("[clippy] Pi not ready — prime brain on mock")
        self.brain = brain
        self.prime_controller = PrimeController(self.shell, brain)
        self._bind_prime()
        self.shell.mode = self.mode
        self.shell.dialog_pending = False
        brain.start()
        pyglet.clock.schedule_interval(self.prime_controller.update, 1 / 60)
        self.pane.set_mode(self.mode)

    def prompt(self, text: str):
        stripped = text.strip()
        low = stripped.lower()
        if low.startswith(HELP_CMD):
            self.pane.add_message("clippy", HELP_TEXT)
            return
        if low.startswith(WHERE_CMD):
            x, y = self.shell.position
            self.pane.add_message("clippy", f"I'm at ({x}, {y}).")
            return
        if low.startswith(MOOD_CMD):
            self._run_mood(stripped[len(MOOD_CMD):].strip())
            return
        if low.startswith(MOVE_CMD):
            self._run_move(self._command_move_spec(stripped[len(MOVE_CMD):].strip()))
            return
        if low.startswith(DELEGATE_CMD):
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
        self.brain.prompt(text, streaming_behavior="followUp")

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
        self.prompt(f"Mode is now {self.mode}.")

    def _on_answer(self, text: str):
        """Prime's final message: surface it in the pane, and if it carries a
        [CLIPPY::DELEGATE] directive (the sub-clippy composition skill), spawn
        a sandboxed worker for the task and steer its report back in. A
        [CLIPPY::MOVE] directive moves Clippy on screen (the move skill)."""
        print(f"[clippy] answer {len(text)}b", flush=True)
        clean, task = parse_delegation(text)
        clean, move = parse_move(clean)
        if task:
            self.shell.set_bubble("(handing off to a sub-clippy…)")
            self.delegate(task, tools=SANDBOX_TOOLS, on_complete=self._on_sub_done)
        if move:
            self._run_move(move)
        # The reasoning-stream bubble already shows the live answer; close it
        # with the final, directive-stripped text (replaces anything that
        # streamed in, so [CLIPPY::DELEGATE]/[CLIPPY::MOVE] never linger).
        # stream_end("") on a reply that was entirely directives just closes
        # the bubble.
        if clean:
            self.pane.stream_end(clean)
        elif task:
            self.pane.stream_end(
                "I've handed that to a sub-clippy — report back shortly."
            )
        else:
            self.pane.stream_end("")

    def _on_sub_done(self, failed: bool, report: str):
        self.shell.set_bubble("(sub-clippy finished — relaying)")
        if report:
            self.pane.add_message("clippy", f"Sub-clippy reported: {report}")
        self.brain.steer(
            "The delegated sub-clippy finished"
            f"{' with an error' if failed else ''}. "
            f"Relay its report to the user plainly: {report or '(no report)'}"
        )

    # --------------------------------------------------------------- worker

    def delegate(self, task: str = DEFAULT_TASK, tools=None, on_complete=None) -> bool:
        """Spawn a sub-clippy for ``task``. Returns False if already delegating.
        The slot frees itself when the worker completes, so a later delegation
        can start a new one."""
        if self._worker_controller is not None:
            print("[clippy] already delegating")
            return False

        def _wrap(failed: bool, report: str):
            self._worker_controller = None
            if on_complete:
                on_complete(failed, report)

        self._worker_controller = self._spawn_worker(task, tools=tools, on_complete=_wrap)
        return True

    def _spawn_worker(self, task: str, tools=None, on_complete=None) -> SubClippyController:
        if self.real or pi_ready():
            agent = PiSubAgent(task=task, model=self.model, tools=tools)
            print(f"[clippy] delegating to PI sub-agent ({self.model})")
        else:
            agent = MockSubAgent(task=task)
            print("[clippy] PI not ready — delegating to mock sub-agent")
        # Sub-clippy renders at 75% of Prime's scale and spawns beside him (to
        # the right), never directly on top — the sub window is sized from the
        # smaller avatar, so it also fits the delegate bubble on screen.
        prime_scale = getattr(self.shell.avatar, "scale", 3.0)
        sub_scale = round(prime_scale * 0.75, 2)
        px, py = self.shell.position
        pw, _ph = self.shell.size
        sx, sy = px + pw + 12, py
        shell = ClippyShell(scale=sub_scale, position=(sx, sy))
        ctrl = SubClippyController(shell, agent, on_complete=on_complete)
        shell.show()
        # On X11/XWayland the constructor's set_location runs before the window
        # is mapped and the WM ignores it, so both shells land at the same spot
        # ("sub-clippy on top of Prime"). Re-assert the position now that the
        # window is mapped so the sub actually sits beside Prime.
        shell.set_location(sx, sy)
        pyglet.clock.schedule_interval(shell.update, 1 / 60)
        pyglet.clock.schedule_interval(ctrl.update, 1 / 60)
        agent.start()
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
        ok = self.delegate(task, tools=SANDBOX_TOOLS, on_complete=self._on_sub_done)
        if not ok:
            self.pane.add_message(
                "clippy", "A sub-clippy is already at work — let it finish first."
            )
        else:
            self.pane.add_message(
                "clippy", "Handed that to a sub-clippy — report back shortly."
            )
            self.brain.steer(f"The user delegated this task to a sub-clippy: {task}")