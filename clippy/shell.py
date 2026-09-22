"""The floating Clippy window: transparent, always-on-top, draggable.

Hosts the animated avatar and the explosion, and exposes the position API
(:meth:`ClippyShell.position` / :meth:`ClippyShell.move_to` /
:meth:`ClippyShell.move_to_spot`) so Clippy knows where he is on screen and
can be asked (by the user or the brain) to move himself around. The old
click-through mode is still available via :meth:`ClippyShell.toggle_passthrough`
but is off by default so the window can be grabbed and dragged."""

import pyglet
from pyglet.gl import current_context
from pyglet.window import Window

from . import screens
from .avatar import Avatar, frame_size
from .explosion import Explosion


class ClippyShell(Window):
    def __init__(self, scale: float = 1.5, live_key: bool = True, position=(60, 420)):
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
        # Fit the explosion to the window's draw area: the blast frames are far
        # larger than the avatar frame that sizes the window, so scale them down
        # (aspect-preserving) instead of letting the animation overflow.
        self.explosion = Explosion(
            live_key=live_key, scale=scale, fit=(w - 2 * padding, h - 2 * padding)
        )
        screens.set_window_top_left(self, *position)
        self.passthrough = False
        #: Cursor-poll drag (see on_mouse_press / update). ``_drag_offset`` is
        #: the grab point relative to the window's top-left, so the window
        #: tracks the cursor 1:1 without the delta feedback that made the old
        #: delta-driven drag self-cancel.
        self._dragging = False
        self._drag_offset: tuple[int, int] | None = None
        self._exploded = False
        self.thinking = False
        #: Prime-shell status (Phase 3): sandbox/build badge + pending-dialog
        #: flag, fed by Session / PrimeController. None = not a prime shell.
        self.mode: str | None = None
        self.dialog_pending = False
        self._bubble = ""
        if prev is not None:
            prev.set_current()

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
        """Where Clippy's top-left corner is on screen, ``(x, y)`` (global)."""
        return screens.window_top_left(self)

    @property
    def size(self) -> tuple[int, int]:
        """Clippy's window footprint, ``(width, height)``."""
        return self.width, self.height

    def visible_screen(self):
        """The AppKit screen the window currently sits on (None if unknown).

        Kept for the macOS pane backend; geometry itself goes through
        :mod:`clippy.screens`.
        """
        ns = getattr(self, "_nswindow", None)
        if ns is None:
            return None
        try:
            return ns.screen()
        except Exception:
            return None

    def _visible_rect(self) -> tuple[int, int, int, int]:
        """Usable (work) area of the screen Clippy is on, global top-origin."""
        return screens.workarea_for_window(self)

    def monitor_index(self) -> int | None:
        """The 1-based index of the monitor Clippy is currently on."""
        x, y = self.position
        return screens.monitor_index_for_point(x, y)

    def _clamp(self, x: int, y: int) -> tuple[int, int]:
        """Clamp a requested top-left ``(x, y)`` into the target point's work
        area (so a move can cross monitors)."""
        w, h = self.size
        return screens.clamp_to_workarea(x, y, w, h)

    def move_to(self, x: int, y: int):
        """Move Clippy so his top-left corner is at ``(x, y)`` (clamped
        on-screen)."""
        screens.set_window_top_left(self, *self._clamp(x, y))

    def move_by(self, dx: int, dy: int):
        """Shift Clippy by ``(dx, dy)`` in the position-API coordinate space."""
        x, y = self.position
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
        w, h = self.size
        x, y = screens.spot_position(key, w, h, self._visible_rect())
        screens.set_window_top_left(self, *self._clamp(x, y))
        return True

    def move_to_monitor(self, index: int, spot: str | None = None) -> bool:
        """Move Clippy to a 1-based monitor (centre, or a named spot on it).
        Returns False if there is no such monitor or the spot is unknown."""
        rect = screens.workarea_by_index(int(index))
        if rect is None:
            return False
        if spot is not None and spot not in self.SPOTS:
            return False
        w, h = self.size
        x, y = screens.spot_position(spot or "center", w, h, rect)
        x, y = screens.clamp_to_rect(x, y, w, h, rect)
        screens.set_window_top_left(self, x, y)
        return True

    def express(self, mood: str, hint: str | None = None, text: str | None = None, force: bool = False):
        """Drive the avatar's mood (future controller / socket entry point).

        ``force=True`` bypasses the mood-interruption rules for user-driven
        commands (``/mood``).
        """
        accepted = self.avatar.express(mood, hint, force=force)
        if text is not None:
            self.thinking = False if mood != "thinking" else True
        return accepted

    def set_bubble(self, text: str):
        """Record the shell's speech-bubble line.

        NOTE: the avatar window is sized to the sprite and has no room for a
        bubble, so this is currently *non-visual*. The live reasoning/answer
        bubble is rendered by the chat pane. This remains the brain's status
        channel for a future bubble/status surface (see docs/remediation-plan.md).
        """
        self._bubble = text

    def play_idle_animation(self, name: str) -> bool:
        """Pin a specific idle-pool animation (``/mood idle <name>``)."""
        return self.avatar.play_idle_animation(name)

    def play_animation(self, name: str) -> bool:
        """Play any catalog animation directly (``/mood <name>``)."""
        return self.avatar.play_animation(name)

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
        # was just shown/exposed). No-op when already current.
        self.switch_to()
        self.clear()
        pad = 20
        if not self._exploded:
            self.avatar.sprite.position = (pad, pad, 0)
            self.avatar.draw()
        # Center the fitted explosion in the window's draw area.
        ew = self.explosion.frame_size[0] * self.explosion.scale
        eh = self.explosion.frame_size[1] * self.explosion.scale
        self.explosion.x = pad + (self.width - 2 * pad - ew) / 2
        self.explosion.y = pad + (self.height - 2 * pad - eh) / 2
        self.explosion.draw()

    # ------------------------------------------------------------- dragging
    # Delta-driven drags self-cancel: moving the window changes the pointer's
    # window-relative position, so the next event's delta is ~0. Instead, on
    # press we record the grab offset from the window origin and, while held,
    # poll the global cursor each frame and place the window at
    # ``cursor - offset`` (clamped to the union of work areas, so he can cross
    # monitors). Where a global cursor isn't available (the macOS stub), we
    # fall back to the old delta path.

    def on_mouse_press(self, x, y, button, modifiers):
        if button != pyglet.window.mouse.LEFT:
            return
        pointer = screens.pointer_global(self)
        if pointer is None:
            return
        wx, wy = self.position
        self._drag_offset = (pointer[0] - wx, pointer[1] - wy)
        self._dragging = True

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self._dragging = False
            self._drag_offset = None

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Fallback drag for platforms without a global-cursor query (macOS
        stub). Mouse deltas are up-positive; screen y is top-origin."""
        if self._dragging:
            return  # cursor polling handles it
        self.move_by(dx, -dy)

    def _drag_tick(self):
        if not self._dragging or self._drag_offset is None:
            return
        pointer = screens.pointer_global(self)
        if pointer is None:
            return
        w, h = self.size
        x, y = screens.drag_target(
            pointer, self._drag_offset, w, h, screens.list_workarea_rects()
        )
        screens.set_window_top_left(self, x, y)

    def update(self, dt: float):
        # sprite.image swaps rebuild vertex lists, which needs the window's GL
        # context current — pyglet only makes it current during on_draw.
        self.switch_to()
        self._drag_tick()
        self.avatar.update(dt)
        self.explosion.update(dt)