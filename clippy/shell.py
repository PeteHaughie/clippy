"""The floating Clippy window: transparent, always-on-top, draggable.

Hosts the animated avatar and the explosion, and exposes the position API
(:meth:`ClippyShell.position` / :meth:`ClippyShell.move_to` /
:meth:`ClippyShell.move_to_spot`) so Clippy knows where he is on screen and
can be asked (by the user or the brain) to move himself around. The old
click-through mode is still available via :meth:`ClippyShell.toggle_passthrough`
but is off by default so the window can be grabbed and dragged."""

import pyglet
from pyglet.gl import current_context
from pyglet.window import FPSDisplay, Window

from .avatar import Avatar, frame_size
from .explosion import Explosion


class ClippyShell(Window):
    def __init__(self, scale: float = 3.0, live_key: bool = True, position=(60, 420)):
        # Whichever context was current before this window is created must be
        # restored before returning: the new window's switch_to() below makes
        # ITS context current, and GL objects of OTHER shells (label, sprite)
        # are invalid if built/drawn from a foreign context. Restoring keeps
        # the caller's window current so e.g. spawning a sub-clippy mid-loop
        # never taints the main shell's GL state.
        prev = current_context
        padding = 20
        fw, fh = frame_size()
        w = int(fw * scale) + padding * 2
        h = int(fh * scale) + padding * 2
        super().__init__(
            w,
            h,
            caption="Clippy",
            resizable=False,
            style=Window.WINDOW_STYLE_OVERLAY,
            visible=False,
        )
        # GL objects (avatar sprite, explosion shader/textures) need a current
        # context; the pyglet Window (and its context) only exists from here on.
        self.switch_to()
        self.avatar = Avatar(scale=scale)
        self.explosion = Explosion(live_key=live_key, scale=scale)
        self.set_location(*position)
        self.passthrough = False
        self.fps = FPSDisplay(window=self)
        self._exploded = False
        self.thinking = False
        #: Prime-shell status (Phase 3): sandbox/build badge + pending-dialog
        #: flag, fed by Session / PrimeController. None = not a prime shell.
        self.mode: str | None = None
        self.dialog_pending = False
        self._bubble = ""
        self.label = self._make_label(w - 12)
        if prev is not None:
            prev.set_current()

    def _make_label(self, width: int):
        return pyglet.text.Label(
            "",
            font_name="Helvetica",
            font_size=10,
            color=(255, 255, 255, 255),
            multiline=True,
            width=width,
            anchor_x="left",
            anchor_y="bottom",
        )

    def show(self, state: bool = True):
        self.set_visible(state)

    def toggle_passthrough(self):
        self.passthrough = not self.passthrough
        self.set_mouse_passthrough(self.passthrough)
        print(f"[clippy] click-through = {self.passthrough}")

    # ------------------------------------------------------- position API
    # Screen coordinates follow pyglet's convention: (x, y) is the window's
    # top-left corner, y grows *downward* from the top of the screen.

    @property
    def position(self) -> tuple[int, int]:
        """Where Clippy's top-left corner is on screen, ``(x, y)``."""
        return self.get_location()

    @property
    def size(self) -> tuple[int, int]:
        """Clippy's window footprint, ``(width, height)``."""
        return self.width, self.height

    def visible_screen(self):
        """The AppKit screen the window currently sits on (None if unknown)."""
        ns = getattr(self, "_nswindow", None)
        if ns is None:
            return None
        try:
            return ns.screen()
        except Exception:
            return None

    def _visible_rect(self) -> tuple[int, int, int, int]:
        """Usable screen area ``(x, y, w, h)`` in pyglet top-left coords:
        the screen frame minus the menu bar and dock, so Clippy never hides
        behind them."""
        ns = self.visible_screen()
        if ns is None:
            return 0, 0, 1920, 1080
        frame = ns.frame()
        vis = ns.visibleFrame()
        x = int(vis.origin.x - frame.origin.x)
        w = int(vis.size.width)
        top = int(frame.size.height - (vis.origin.y - frame.origin.y + vis.size.height))
        h = int(vis.size.height)
        return x, top, w, h

    def _clamp(self, x: int, y: int) -> tuple[int, int]:
        """Clamp a requested top-left ``(x, y)`` so the window stays fully on
        the visible screen."""
        w, h = self.size
        sx, sy, sw, sh = self._visible_rect()
        margin = 8
        x = max(sx + margin, min(int(x), sx + sw - w - margin))
        y = max(sy + margin, min(int(y), sy + sh - h - margin))
        return x, y

    def move_to(self, x: int, y: int):
        """Move Clippy so his top-left corner is at ``(x, y)`` (clamped on-screen)."""
        self.set_location(*self._clamp(x, y))

    def move_by(self, dx: int, dy: int):
        """Shift Clippy by ``(dx, dy)`` in the position-API coordinate space."""
        x, y = self.get_location()
        self.move_to(x + dx, y + dy)

    #: Named spots Clippy can move to (:meth:`move_to_spot`).
    SPOTS = (
        "top-left", "top-right", "bottom-left", "bottom-right",
        "center", "left", "right", "top", "bottom",
    )

    def move_to_spot(self, name: str) -> bool:
        """Move Clippy to a named spot on his current screen. Returns False if
        the spot is unknown."""
        key = (name or "").strip().lower()
        if key not in self.SPOTS:
            return False
        sx, sy, sw, sh = self._visible_rect()
        w, h = self.size
        m = 12
        cx = sx + (sw - w) // 2
        cy = sy + (sh - h) // 2
        if key == "top-left":
            x, y = sx + m, sy + m
        elif key == "top-right":
            x, y = sx + sw - w - m, sy + m
        elif key == "bottom-left":
            x, y = sx + m, sy + sh - h - m
        elif key == "bottom-right":
            x, y = sx + sw - w - m, sy + sh - h - m
        elif key == "center":
            x, y = cx, cy
        elif key == "left":
            x, y = sx + m, cy
        elif key == "right":
            x, y = sx + sw - w - m, cy
        elif key == "top":
            x, y = cx, sy + m
        else:  # bottom
            x, y = cx, sy + sh - h - m
        self.set_location(x, y)
        return True

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
        if symbol == pyglet.window.key.SPACE:
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
        # Draw under this window's OWN context. on_draw can be dispatched from
        # pyglet's queued event list (dispatch_pending_events) at a moment when
        # a different window's context is current (e.g. a sub-clippy's window
        # was just shown/exposed). Without this, the label/sprite GL objects
        # get committed under a foreign context and the next draw raises a
        # GLException from glBufferSubData. No-op when already current.
        self.switch_to()
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
        parts = []
        if self.mode:
            parts.append(f"mode:{'🛡' if self.mode == 'sandbox' else '🔨'}")
        parts.append(f"mood:{mood}")
        if self.dialog_pending:
            parts.append("dialog:waiting")
        self.label.text = (
            f"{' · '.join(parts)} · {bubble} (T think / E explode / Q quit)"
        )
        try:
            self.label.draw()
        except pyglet.gl.lib.GLException:
            # pyglet 2.1.x text layout can overflow its vertex buffer
            # (glBufferSubData -> GL_INVALID_VALUE) when the status label's
            # text length swings hard while a second window's on_draw
            # interleaves. The label is cosmetic; rebuild it and keep the loop
            # alive instead of crashing.
            self.label = self._make_label(self.width - 12)
            self.label.text = (
                f"{' · '.join(parts)} · {bubble} (T think / E explode / Q quit)"
            )
            try:
                self.label.draw()
            except pyglet.gl.lib.GLException:
                pass  # if the fresh label also fails, skip drawing this frame
        self.fps.draw()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Drag Clippy around by grabbing any part of his window. Mouse deltas
        are up-positive (pyglet convention); screen y is top-origin, so the
        vertical delta is negated."""
        self.move_by(dx, -dy)

    def update(self, dt: float):
        # sprite.image swaps rebuild vertex lists, which needs the window's GL
        # context current — pyglet only makes it current during on_draw.
        self.switch_to()
        self.avatar.update(dt)
        self.explosion.update(dt)