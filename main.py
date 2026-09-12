"""Spike entry point for ticket 003: floating transparent Clippy window.

Controls:
  P  toggle click-through (default ON, so the avatar never steals clicks)
  T  toggle Thinking / RestPose animation
  Space  Wave
  E  trigger the explosion
  N  summon the chat pane (--brain mode)      X  hide the pane
  Tab  toggle sandbox ↔ build (--brain mode)
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

The app itself is a projection of the session graph (clippy/session.py /
clippy/model.py): the control plane is declared as typed nodes/edges/
constraints, and this entry point just constructs a :class:`Session`.
"""

import argparse
import sys

# Import the pyobjc runtime BEFORE pyglet so both ObjC bridges share one
# runtime cleanly (proven harness in w1c_pane_spike.py). The pane module
# imports AppKit/WebKit after this guard.
import objc  # noqa: F401
import pyglet

from clippy.moods import Moods
from clippy.session import Session
from clippy.shell import ClippyShell
from clippy.subagent import DEFAULT_MODEL, DEFAULT_TASK

ONE_SHOT_HOLD = 1.5  # seconds after a one-shot mood before moving on

PRIME_POS = (60, 420)


def duration_of(avatar, name: str) -> float:
    anim = avatar.animations[name]
    return sum(fr["duration"] for fr in anim["frames"]) / 1000.0


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

    shell = PrimeShell(scale=args.scale, live_key=not args.no_shader, position=PRIME_POS)
    shell.show()
    shell.pane = None
    shell.session = None
    pyglet.clock.schedule_interval(shell.update, 1 / 60)

    session = None
    if args.delegate:
        session = Session(shell, model=args.model, real=args.real)
        shell.session = session
        session.delegate(args.delegate)

    if args.brain is not None:
        session = Session(shell, model=args.model, real=args.real)
        shell.session = session
        opening = args.brain or (
            "Give the user a one-line friendly greeting and say you're ready."
        )
        session.prompt(opening)
        print(f"[clippy] prime opening: {opening!r}")
        pyglet.clock.schedule_once(lambda dt: session.pane.summon(), 0.9)

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