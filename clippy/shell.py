"""The floating Clippy window: transparent, always-on-top, click-through
off by default and toggleable. Hosts the animated avatar and the explosion."""

import pyglet
from pyglet.window import FPSDisplay, Window

from .avatar import Avatar
from .explosion import Explosion


class ClippyShell(Window):
    def __init__(self, scale: float = 3.0, live_key: bool = True, position=(60, 420)):
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
        self.set_location(*position)
        self.set_mouse_passthrough(True)
        self.passthrough = True
        self.fps = FPSDisplay(window=self)
        self._exploded = False
        self.thinking = False
        self._bubble = ""
        self.label = pyglet.text.Label(
            "",
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

    def express(self, mood: str, hint: str | None = None, text: str | None = None):
        """Drive the avatar's mood (future controller / socket entry point)."""
        accepted = self.avatar.express(mood, hint)
        if text is not None:
            self.thinking = False if mood != "thinking" else True
        return accepted

    def set_bubble(self, text: str):
        """Replace the speech-bubble line shown above the avatar."""
        self._bubble = text

    def dismiss(self):
        """Close this window (used after the sub-clippy explosion)."""
        self.set_visible(False)
        self.close()

    def trigger_explosion(self):
        """Start the blast and retire the avatar for good so the explosion
        hands over cleanly: no clippy sprite lingering in or after the fire."""
        self.explosion.trigger()
        self._exploded = True

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.P:
            self.toggle_passthrough()
        elif symbol == pyglet.window.key.SPACE:
            self.express("greeting", hint=None)
        elif symbol == pyglet.window.key.T:
            self.thinking = not self.thinking
            self.express("thinking" if self.thinking else "idle")
        elif symbol == pyglet.window.key.E:
            self.trigger_explosion()
        elif symbol == pyglet.window.key.Q:
            pyglet.app.exit()
        else:
            self.express("greeting", hint=None)

    def on_draw(self):
        self.clear()
        pad = 20
        if not self._exploded:
            self.avatar.sprite.position = (pad, pad, 0)
            self.avatar.draw()
        self.explosion.x = pad
        self.explosion.y = pad
        self.explosion.draw()
        self.label.x = pad
        self.label.y = int(pad + self.avatar.frame_h * self.avatar.scale) + 6
        mood = self.avatar.current_mood
        bubble = self._bubble.replace("\n", " ") if self._bubble else "(idle)"
        self.label.text = (
            f"mood:{mood} · {bubble} (P pass / T think / E explode / Q quit)"
        )
        self.label.draw()
        self.fps.draw()

    def update(self, dt: float):
        self.avatar.update(dt)
        self.explosion.update(dt)