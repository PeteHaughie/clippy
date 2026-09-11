"""Spike entry point for ticket 003: floating transparent Clippy window.

Controls:
  P  toggle click-through (default ON, so the avatar never steals clicks)
  T  toggle Thinking / RestPose animation
  Space  Wave
  E  trigger the explosion
  Q  quit

Flags:
  --mood <name> [--hint <hint>]  drive a single mood once, then quit
  --moodcycle                    play every mood in sequence, then quit
"""

import argparse
import sys

import pyglet

from clippy.avatar import Avatar
from clippy.moods import Moods
from clippy.shell import ClippyShell

ONE_SHOT_HOLD = 1.5  # seconds after a one-shot mood before moving on


def duration_of(avatar: Avatar, name: str) -> float:
    anim = avatar.animations[name]
    return sum(fr["duration"] for fr in anim["frames"]) / 1000.0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", type=float, default=3.0)
    parser.add_argument("--no-shader", action="store_true", help="use ffmpeg-baked frames")
    parser.add_argument("--mood", help="play one mood then quit")
    parser.add_argument("--hint", help="activity hint for --mood")
    parser.add_argument("--moodcycle", action="store_true", help="play every mood in sequence then quit")
    args = parser.parse_args()

    shell = ClippyShell(scale=args.scale, live_key=not args.no_shader)
    shell.show()
    pyglet.clock.schedule_interval(shell.update, 1 / 60)

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