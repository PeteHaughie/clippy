"""Atomic demo: plays only the Clippy explosion animation in its own window.

Run:  .venv/bin/python explosion_demo.py [--scale 3.0] [--no-shader] [--repeat]

  E  re-trigger the explosion
  Q  quit
"""

import argparse
import sys

import pyglet
from pyglet.window import FPSDisplay, Window

from clippy.explosion import Explosion

PAD = 24
POS = (60, 200)
TRIGGER_DELAY = 0.5  # seconds before the first blast


class ExplosionDemo(Window):
    explosion: Explosion

    def __init__(self, live_key: bool = True, scale: float = 3.0, repeat: bool = False):
        self.live_key = live_key
        self.zoom = scale
        self.repeat = repeat
        self.explosion = Explosion(live_key=live_key, scale=scale)
        fw, fh = self.explosion.frame_size
        w = int(fw * self.zoom) + PAD * 2
        h = int(fh * self.zoom) + PAD * 2
        super().__init__(
            w, h,
            caption="Clippy explosion",
            resizable=False,
            style=Window.WINDOW_STYLE_OVERLAY,
        )
        self.set_location(*POS)
        self.fps = FPSDisplay(window=self)
        print(
            f"[demo] explosion {fw}x{fh} @scale {scale} "
            f"({int(fw*scale)}x{int(fh*scale)}), "
            f"{self.explosion.frame_count} frames, "
            f"mode={'shader' if live_key else 'baked'}"
        )

    def fire(self):
        if self.explosion.active:
            return
        self.explosion.trigger()
        print("[demo] BANG")

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.E:
            self.fire()
        elif symbol == pyglet.window.key.Q:
            pyglet.app.exit()

    def on_draw(self):
        self.clear()
        self.explosion.x = PAD
        self.explosion.y = PAD
        self.explosion.draw()
        self.fps.draw()

    def update(self, dt):
        self.explosion.update(dt)
        if not self.explosion.active and self.repeat:
            self.fire()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", type=float, default=3.0)
    parser.add_argument("--no-shader", action="store_true", help="use baked frames instead of GLSL key")
    parser.add_argument("--repeat", action="store_true", help="keep exploding forever")
    args = parser.parse_args()

    demo = ExplosionDemo(live_key=not args.no_shader, scale=args.scale, repeat=args.repeat)
    pyglet.clock.schedule_interval(demo.update, 1 / 60)
    if not args.repeat:
        pyglet.clock.schedule_once(lambda dt: demo.fire(), TRIGGER_DELAY)
        # The animation is ~4s; give it room, then quit.
        pyglet.clock.schedule_once(lambda dt: pyglet.app.exit(), TRIGGER_DELAY + 8)
    pyglet.app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())