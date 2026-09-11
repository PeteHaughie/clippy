"""The floating Clippy window: transparent, always-on-top, click-through
off by default and toggleable. Hosts the animated avatar and the explosion."""

import pyglet
from pyglet.window import FPSDisplay, Window

from .avatar import Avatar
from .explosion import Explosion


class ClippyShell(Window):
    def __init__(self, scale: float = 3.0, live_key: bool = True):
        self.avatar = Avatar(scale=scale)
        self.explosion = Explosion(live_key=live_key, scale=scale)
        padding = 20
        w = int(self.avatar.frame_w * scale) + padding * 2
        h = int(self.avatar.frame_h * scale) + padding * 2
        super().__init__(
            w,
            h,
            caption="Clippy",
            resizable=False,
            style=Window.WINDOW_STYLE_OVERLAY,
            visible=False,
        )
        self.set_location(60, 420)
        self.set_mouse_passthrough(True)
        self.passthrough = True
        self.fps = FPSDisplay(window=self)
        self.thinking = False
        self.label = pyglet.text.Label(
            "I'd like to help! (press : for menu)",
            font_name="Helvetica",
            font_size=10,
            color=(255, 255, 255, 255),
            multiline=True,
            width=w - 12,
            anchor_x="left",
            anchor_y="bottom",
        )

    def show(self, state: bool = True):
        self.set_visible(state)

    def toggle_passthrough(self):
        self.passthrough = not self.passthrough
        self.set_mouse_passthrough(self.passthrough)
        print(f"[clippy] click-through = {self.passthrough}")

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.P:
            self.toggle_passthrough()
        elif symbol == pyglet.window.key.SPACE:
            self.avatar.play("Wave")
        elif symbol == pyglet.window.key.T:
            self.thinking = not self.thinking
            self.avatar.play("Thinking" if self.thinking else "RestPose")
        elif symbol == pyglet.window.key.E:
            self.explosion.trigger()
        elif symbol == pyglet.window.key.Q:
            pyglet.app.exit()
        else:
            self.avatar.play("GetAttention")

    def on_draw(self):
        self.clear()
        pad = 20
        self.avatar.sprite.position = (pad, pad, 0)
        self.avatar.draw()
        self.explosion.x = pad
        self.explosion.y = pad
        self.explosion.draw()
        self.label.x = pad
        self.label.y = int(pad + self.avatar.frame_h * self.avatar.scale) + 6
        self.label.text = (
            "computing…" if self.thinking else "I'd like to help! (P pass / T think / E explode / Q quit)"
        )
        self.label.draw()
        self.fps.draw()

    def update(self, dt: float):
        self.avatar.update(dt)
        self.explosion.update(dt)