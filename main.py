"""Spike entry point for ticket 003: floating transparent Clippy window.

Controls:
  P  toggle click-through (default ON, so the avatar never steals clicks)
  T  toggle Thinking / RestPose animation
  Space  Wave
  E  trigger the explosion
  N  summon the chat pane (--brain mode)      X  hide the pane
  Q  quit

Flags:
  --mood <name> [--hint <hint>]  drive a single mood once, then quit
  --moodcycle                    play every mood in sequence, then quit
  --delegate [task]              summon a sub-clippy (optional task; uses the
                                 default when omitted)
  --brain [prompt]               start the prime Pi brain (RPC) + chat pane;
                                 optional opening prompt (greeting by default)
  --real                         force the real Pi sub-agent (oMLX) instead of
                                 auto-falling back to the mock
  --model <omlx/model>           which oMLX model the real sub-agent uses
"""

import argparse
import sys
from pathlib import Path

# Import the pyobjc runtime BEFORE pyglet so both ObjC bridges share one
# runtime cleanly (proven harness in w1c_pane_spike.py). The pane module
# imports AppKit/WebKit after this guard.
import objc  # noqa: F401
import pyglet

from clippy.avatar import Avatar
from clippy.brain import MockBrain, PiBrain
from clippy.controller import SubClippyController
from clippy.memory import ensure_memory, resolve_skill_paths
from clippy.moods import Moods
from clippy.pane import Pane
from clippy.prime import PrimeController
from clippy.shell import ClippyShell
from clippy.subagent import (
    DEFAULT_MODEL,
    DEFAULT_TASK,
    DELEGATE_CMD,
    MockSubAgent,
    PiSubAgent,
    pi_ready,
    parse_delegation,
)

ONE_SHOT_HOLD = 1.5  # seconds after a one-shot mood before moving on

PRIME_POS = (60, 420)
SUB_POS = (560, 420)

#: Read/search-only tool allowlist for a sandboxed conversation (005).
SANDBOX_TOOLS = ["read", "grep", "find", "ls"]
#: Build-mode consent gate extension (016): asks before mutating tools.
GATE_EXT = str(Path(__file__).resolve().parent / "clippy" / "extensions" / "clippy-gate.ts")


def duration_of(avatar: Avatar, name: str) -> float:
    anim = avatar.animations[name]
    return sum(fr["duration"] for fr in anim["frames"]) / 1000.0


class Delegator:
    """Owns the one sub-clippy the demo allows at a time."""

    def __init__(self, prime: ClippyShell, real: bool, model: str):
        self.prime = prime
        self.real = real
        self.model = model
        self.controller = None

    def _spawn(self, task: str, tools=None, on_complete=None) -> SubClippyController:
        if self.real or pi_ready():
            agent = PiSubAgent(task=task, model=self.model, tools=tools)
            print(f"[clippy] delegating to PI sub-agent ({self.model})")
        else:
            agent = MockSubAgent(task=task)
            print("[clippy] PI not ready — delegating to mock sub-agent")
        shell = ClippyShell(position=SUB_POS)
        ctrl = SubClippyController(shell, agent, on_complete=on_complete)
        shell.show()
        pyglet.clock.schedule_interval(shell.update, 1 / 60)
        pyglet.clock.schedule_interval(ctrl.update, 1 / 60)
        agent.start()
        return ctrl

    def delegate(self, task: str = DEFAULT_TASK, tools=None, on_complete=None) -> bool:
        """Spawn a sub-clippy for ``task``. Returns False if already delegating.
        The controller slot frees itself when the worker completes, so a later
        delegation can start a new one."""
        if self.controller is not None:
            print("[clippy] already delegating")
            return False

        def _wrap(failed: bool, report: str):
            self.controller = None
            if on_complete:
                on_complete(failed, report)

        self.controller = self._spawn(task, tools=tools, on_complete=_wrap)
        return True


class PrimeSession:
    """Owns the prime brain + controller and re-spawns the Pi process when the
    user toggles sandbox ↔ build (Pi 0.85.1 sets the tool set at spawn only —
    verified in research/pi-community-deep-dive.md §3)."""

    def __init__(self, shell: ClippyShell, delegator: Delegator, model: str, real: bool):
        self.shell = shell
        self.delegator = delegator
        self.model = model
        self.real = real
        self.pane = shell.pane
        self.mode = "sandbox"
        self.brain = None
        self.controller = None
        self._spawn()

    def _brain_kwargs(self) -> dict:
        kwargs = {"model": self.model}
        if self.mode == "sandbox":
            kwargs["tools"] = SANDBOX_TOOLS
        else:
            kwargs["extensions"] = [GATE_EXT]
        kwargs["append_system_prompt"] = ensure_memory()
        kwargs["skills"] = resolve_skill_paths()
        return kwargs

    def _spawn(self):
        if self.real or pi_ready():
            brain = PiBrain(**self._brain_kwargs())
            print(f"[clippy] prime brain: {self.mode} mode on Pi RPC ({self.model})")
        else:
            brain = MockBrain()
            print("[clippy] Pi not ready — prime brain on mock")
        self.brain = brain
        self.controller = PrimeController(self.shell, brain)
        self.controller.on_answer = self._on_answer
        self.controller.on_ui_request = self.pane.ui_request
        self.shell.mode = self.mode
        self.shell.dialog_pending = False
        brain.start()
        pyglet.clock.schedule_interval(self.controller.update, 1 / 60)
        self.pane.set_mode(self.mode)

    def prompt(self, text: str):
        stripped = text.strip()
        if stripped.lower().startswith(DELEGATE_CMD):
            task = stripped[len(DELEGATE_CMD):].strip()
            if not task:
                self.pane.add_message(
                    "clippy", "What should the sub-clippy do? e.g. `/delegate count the markdown files`"
                )
                return
            self._start_delegation(task)
            return
        self.brain.prompt(text, streaming_behavior="followUp")

    def _start_delegation(self, task: str):
        self.shell.set_bubble("(handing off to a sub-clippy…)")
        ok = self.delegator.delegate(
            task,
            tools=SANDBOX_TOOLS,
            on_complete=self._on_sub_done,
        )
        if not ok:
            self.pane.add_message(
                "clippy", "A sub-clippy is already at work — let it finish first."
            )
        else:
            self.pane.add_message(
                "clippy", "Handed that to a sub-clippy — report back shortly."
            )
            self.brain.steer(
                f"The user delegated this task to a sub-clippy: {task}"
            )

    def ui_response(self, rid, payload: dict):
        self.brain.send({"type": "extension_ui_response", "id": rid, **payload})
        self.shell.dialog_pending = False

    def _on_answer(self, text: str):
        """Prime's final message: surface it in the pane, and if it carries a
        [CLIPPY::DELEGATE] directive (the sub-clippy composition skill), spawn
        a sandboxed worker for the task and steer its report back in."""
        clean, task = parse_delegation(text)
        if task:
            self.shell.set_bubble("(handing off to a sub-clippy…)")
            self.delegator.delegate(
                task,
                tools=SANDBOX_TOOLS,
                on_complete=self._on_sub_done,
            )
        if clean:
            self.pane.add_message("clippy", clean)
        elif task:
            self.pane.add_message(
                "clippy", "I've handed that to a sub-clippy — report back shortly."
            )

    def _on_sub_done(self, failed: bool, report: str):
        self.shell.set_bubble("(sub-clippy finished — relaying)")
        if report:
            self.pane.add_message("clippy", f"Sub-clippy reported: {report}")
        self.brain.steer(
            "The delegated sub-clippy finished"
            f"{' with an error' if failed else ''}. "
            f"Relay its report to the user plainly: {report or '(no report)'}"
        )

    def toggle(self):
        self.brain.stop()
        self.mode = "build" if self.mode == "sandbox" else "sandbox"
        print(f"[clippy] mode -> {self.mode} (re-spawning brain)")
        self._spawn()
        self.prompt(f"Mode is now {self.mode}.")


class PrimeShell(ClippyShell):
    """ClippyShell with N/X (pane) and Tab (sandbox↔build) for --brain mode."""

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.N:
            if self.pane is not None:
                self.pane.summon()
        elif symbol == pyglet.window.key.X:
            if self.pane is not None:
                self.pane.hide()
        elif symbol == pyglet.window.key.TAB:
            if self.session is not None:
                self.session.toggle()
        else:
            super().on_key_press(symbol, modifiers)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", type=float, default=3.0)
    parser.add_argument("--no-shader", action="store_true", help="use ffmpeg-baked frames")
    parser.add_argument("--mood", help="play one mood then quit")
    parser.add_argument("--hint", help="activity hint for --mood")
    parser.add_argument("--moodcycle", action="store_true", help="play every mood in sequence then quit")
    parser.add_argument("--delegate", nargs="?", const=DEFAULT_TASK, help="summon a sub-clippy for this task at startup (default task when omitted)")
    parser.add_argument("--brain", nargs="?", const="", help="start the prime Pi brain (RPC) and give it this opening prompt (default greeting when omitted)")
    parser.add_argument("--real", action="store_true", help="force the real Pi sub-agent")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="omlx model for the real sub-agent")
    args = parser.parse_args()

    shell = PrimeShell(scale=args.scale, live_key=not args.no_shader)
    shell.show()
    shell.pane = None
    shell.session = None
    pyglet.clock.schedule_interval(shell.update, 1 / 60)

    delegator = Delegator(shell, real=args.real, model=args.model)
    if args.delegate:
        delegator.delegate(args.delegate)

    session = None
    if args.brain is not None:
        pane = Pane(shell)
        shell.pane = pane
        pane.start_driver()

        session = PrimeSession(shell, delegator, model=args.model, real=args.real)
        shell.session = session
        pane.on_chat = session.prompt
        pane.on_ui_response = session.ui_response

        opening = args.brain or (
            "Give the user a one-line friendly greeting and say you're ready."
        )
        session.prompt(opening)
        print(f"[clippy] prime opening: {opening!r}")
        pyglet.clock.schedule_once(lambda dt: pane.summon(), 0.9)

    moods = shell.avatar.moods

    if args.moodcycle:
        run_cycle(shell, moods)
    elif args.mood:
        hint = args.hint or ("build" if args.mood == "working" else None)
        if not shell.express(args.mood, hint=hint):
            print(f"[clippy] mood '{args.mood}' ignored (rule) or unknown")
        resolved = shell.avatar.moods.resolve(args.mood, hint)
        hold = 0
        if not moods.is_continuous(args.mood) and resolved:
            hold = duration_of(shell.avatar, resolved) + ONE_SHOT_HOLD
        if hold:
            pyglet.clock.schedule_once(lambda dt: pyglet.app.exit(), hold)
    pyglet.app.run()
    if session is not None:
        session.brain.stop()
    return 0


def run_cycle(shell: ClippyShell, moods: Moods):
    seq = [(m, None) for m in moods.available_moods()]
    seq[seq.index(("working", None))] = ("working", "build")
    holds = []
    for (mood, hint) in seq:
        resolved = moods.resolve(mood, hint)
        if moods.is_continuous(mood):
            holds.append(3.5)
        elif resolved:
            holds.append(duration_of(shell.avatar, resolved) + ONE_SHOT_HOLD)
        else:
            holds.append(1.0)
    total = 0.0
    for i, ((mood, hint), hold) in enumerate(zip(seq, holds)):
        pyglet.clock.schedule_once(lambda dt, m=mood, h=hint: shell.express(m, hint=h), total)
        total += hold
    pyglet.clock.schedule_once(lambda dt: pyglet.app.exit(), total + 0.5)
    print(f"[clippy] moodcycle: {', '.join(m for m, _ in seq)}")
    for (mood, hint), hold in zip(seq, holds):
        print(f"  {mood:10s} hint={hint or '-':<10} hold={hold:5.1f}s")


if __name__ == "__main__":
    sys.exit(main())