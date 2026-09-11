"""Spike entry point for ticket 003: floating transparent Clippy window.

Controls:
  P  toggle click-through (default ON, so the avatar never steals clicks)
  T  toggle Thinking / RestPose animation
  Space  Wave
  E  trigger the explosion
  Q  quit
"""

import argparse
import sys

import pyglet

from clippy.shell import ClippyShell


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", type=float, default=3.0)
    parser.add_argument("--no-shader", action="store_true", help="use ffmpeg-baked frames")
    args = parser.parse_args()

    shell = ClippyShell(scale=args.scale, live_key=not args.no_shader)
    shell.show()
    pyglet.clock.schedule_interval(shell.update, 1 / 60)
    pyglet.app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())