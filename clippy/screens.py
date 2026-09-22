"""Global screen geometry (single source of truth for Clippy's position).

The avatar window lives in pyglet's coordinate space: ``(x, y)`` is the
window's top-left in **global top-origin** coordinates, y growing downward
across the whole desktop. This module answers the questions the shell and the
move commands need — which screen is a point/window on, what is that screen's
usable (work) area, and how do I place a window there — without the shell
re-deriving screen maths per platform.

Pure geometry (rect selection, clamping, spot maths) is separated from the
platform backends so it is unit-testable with injected rects and no display.

Backends:
* **Linux** — screens from pyglet (already global and the same space as
  ``set_location``); work areas from GDK monitors, scaled from GDK logical units
  into pyglet's device units. The cursor is read with ``XQueryPointer`` so the
  drag loop can poll it (delta-driven moves self-cancel).
* **macOS** — a stub that currently inherits the pyglet behaviour. Proper
  multi-monitor support needs ``NSScreen.frame()/visibleFrame()`` and
  ``NSWindow.setFrameTopLeftPoint_`` (pyglet's own ``set_location`` is
  inconsistent on secondary screens); see ``_MacBackend``.
"""

from __future__ import annotations

import sys
import time

#: ``(x, y, width, height)`` in global top-origin coordinates.
Rect = tuple[int, int, int, int]

#: Default inset kept between a window and the edge of its work area.
MARGIN = 8
#: Screen geometry is cached this long (monitor hot-plug is rare; the drag loop
#: calls this every frame).
_CACHE_TTL = 1.0


# ------------------------------------------------------------ pure geometry


def rect_contains(rect: Rect, x: int, y: int) -> bool:
    rx, ry, rw, rh = rect
    return rx <= x < rx + rw and ry <= y < ry + rh


def rect_containing(x: int, y: int, rects: list[Rect]) -> Rect | None:
    for rect in rects:
        if rect_contains(rect, x, y):
            return rect
    return None


def rect_distance_sq(rect: Rect, x: int, y: int) -> float:
    """Squared distance from ``(x, y)`` to the nearest point of ``rect`` (0 if
    inside). Used to pick the nearest screen for a point in a gap."""
    rx, ry, rw, rh = rect
    dx = max(rx - x, 0, x - (rx + rw - 1))
    dy = max(ry - y, 0, y - (ry + rh - 1))
    return dx * dx + dy * dy


def nearest_rect(x: int, y: int, rects: list[Rect]) -> Rect | None:
    if not rects:
        return None
    return min(rects, key=lambda r: rect_distance_sq(r, x, y))


def clamp_to_rect(x: int, y: int, w: int, h: int, rect: Rect, margin: int = MARGIN) -> tuple[int, int]:
    """Clamp a window's top-left so it stays fully inside ``rect``."""
    rx, ry, rw, rh = rect
    cx = max(rx + margin, min(int(x), rx + rw - w - margin))
    cy = max(ry + margin, min(int(y), ry + rh - h - margin))
    return cx, cy


def clamp_to_rects(x: int, y: int, w: int, h: int, rects: list[Rect], margin: int = MARGIN) -> tuple[int, int]:
    """Clamp to the nearest work area (so a window in a gap between monitors is
    pulled onto the closest one, and can still cross between them)."""
    rect = rect_containing(x, y, rects) or nearest_rect(x, y, rects)
    if rect is None:
        return int(x), int(y)
    return clamp_to_rect(x, y, w, h, rect, margin)


def spot_in_rect(spot: str, w: int, h: int, rect: Rect, margin: int = 12) -> tuple[int, int]:
    """Top-left for a named spot within ``rect``."""
    sx, sy, sw, sh = rect
    cx = sx + (sw - w) // 2
    cy = sy + (sh - h) // 2
    spot = (spot or "").strip().lower()
    if spot == "top-left":
        return sx + margin, sy + margin
    if spot == "top-right":
        return sx + sw - w - margin, sy + margin
    if spot == "bottom-left":
        return sx + margin, sy + sh - h - margin
    if spot == "bottom-right":
        return sx + sw - w - margin, sy + sh - h - margin
    if spot == "left":
        return sx + margin, cy
    if spot == "right":
        return sx + sw - w - margin, cy
    if spot == "top":
        return cx, sy + margin
    if spot == "bottom":
        return cx, sy + sh - h - margin
    return cx, cy  # center / unknown


def drag_target(pointer: tuple[int, int], grab_offset: tuple[int, int],
                w: int, h: int, rects: list[Rect], margin: int = MARGIN) -> tuple[int, int]:
    """Where a dragged window's top-left should be: the cursor minus the grab
    offset, clamped to the union of work areas."""
    return clamp_to_rects(pointer[0] - grab_offset[0], pointer[1] - grab_offset[1],
                          w, h, rects, margin)


# ------------------------------------------------------------------ backends


def _pyglet_screens() -> list[Rect]:
    try:
        import pyglet

        return [
            (int(s.x), int(s.y), int(s.width), int(s.height))
            for s in pyglet.display.get_display().get_screens()
        ]
    except Exception:
        return []


def _pyglet_primary() -> Rect | None:
    try:
        import pyglet

        s = pyglet.display.get_display().get_default_screen()
        return (int(s.x), int(s.y), int(s.width), int(s.height))
    except Exception:
        screens = _pyglet_screens()
        return screens[0] if screens else None


def _gdk_monitors() -> list[tuple[Rect, Rect]]:
    """``[(geometry, workarea)]`` per monitor, in GDK logical units, or []."""
    try:
        import gi

        gi.require_version("Gdk", "3.0")
        from gi.repository import Gdk

        display = Gdk.Display.get_default()
        if display is None:
            return []
        out = []
        for i in range(display.get_n_monitors()):
            mon = display.get_monitor(i)
            g = mon.get_geometry()
            wa = mon.get_workarea()
            out.append(
                ((g.x, g.y, g.width, g.height), (wa.x, wa.y, wa.width, wa.height))
            )
        return out
    except Exception:
        return []


def _scale_rect(rect: Rect, scale: float) -> Rect:
    return tuple(round(v * scale) for v in rect)  # type: ignore[return-value]


def _overlap_area(a: Rect, b: Rect) -> int:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    dx = max(0, min(ax + aw, bx + bw) - max(ax, bx))
    dy = max(0, min(ay + ah, by + bh) - max(ay, by))
    return dx * dy


def _infer_scale(screens: list[Rect], gdk: list[tuple[Rect, Rect]]) -> float:
    """Global device-unit ratio between pyglet (X11 root) and GDK logical units,
    inferred from the screen/monitor that contains the origin."""
    p = rect_containing(0, 0, screens) if screens else None
    g = next((geo for geo, _wa in gdk if rect_contains(geo, 0, 0)), None)
    if p and g and g[2]:
        scale = p[2] / g[2]
        if 0.2 <= scale <= 8.0:
            return scale
    return 1.0


def _xlib_pointer(win) -> tuple[int, int] | None:
    """Global cursor position via ``XQueryPointer`` (no GTK dependency)."""
    try:
        from ctypes import byref, c_int, c_uint

        from pyglet.libs.x11 import xlib

        display = getattr(win, "_x_display", None)
        root = win._get_root() if hasattr(win, "_get_root") else None
        if display is None or root is None:
            return None
        rr, cr = xlib.Window(), xlib.Window()
        rx, ry, wx, wy, mask = c_int(), c_int(), c_int(), c_int(), c_uint()
        ok = xlib.XQueryPointer(
            display, root, byref(rr), byref(cr),
            byref(rx), byref(ry), byref(wx), byref(wy), byref(mask),
        )
        if not ok:
            return None
        return int(rx.value), int(ry.value)
    except Exception:
        return None


class _PygletBackend:
    """Screen geometry via pyglet — the same space as ``set_location``."""

    def screens(self) -> list[Rect]:
        return _pyglet_screens()

    def workareas(self) -> list[Rect]:
        return list(self.screens())

    def primary(self) -> Rect | None:
        return _pyglet_primary()

    def window_top_left(self, win) -> tuple[int, int]:
        return tuple(int(v) for v in win.get_location())  # type: ignore[return-value]

    def set_window_top_left(self, win, x: int, y: int) -> None:
        win.set_location(int(x), int(y))

    def pointer_global(self, win) -> tuple[int, int] | None:
        return None


class _LinuxBackend(_PygletBackend):
    """pyglet geometry + GDK work areas (scaled into pyglet's units) + XQueryPointer."""

    def __init__(self) -> None:
        self._cache: tuple[list[Rect], list[Rect]] | None = None
        self._cache_at = 0.0

    def refresh(self) -> None:
        self._cache = None

    def _rects(self) -> tuple[list[Rect], list[Rect]]:
        # The drag loop clamps every frame; cache briefly so GDK isn't queried
        # 60x/s (monitor hot-plug is rare).
        now = time.monotonic()
        if self._cache is not None and now - self._cache_at < _CACHE_TTL:
            return self._cache
        result = self._compute_rects()
        self._cache = result
        self._cache_at = now
        return result

    def _compute_rects(self) -> tuple[list[Rect], list[Rect]]:
        screens = _pyglet_screens()
        gdk = _gdk_monitors()
        if not gdk:
            return screens, list(screens)
        scale = _infer_scale(screens, gdk)
        geo = [_scale_rect(g, scale) for g, _wa in gdk]
        wa = [_scale_rect(w, scale) for _g, w in gdk]
        # If pyglet collapses the desktop to one screen but GDK sees several,
        # trust GDK's per-monitor geometry so monitor moves still work.
        if len(screens) <= 1 and len(geo) > 1:
            return geo, wa
        out = []
        for scr in screens:
            best, best_ov = scr, -1
            for g, w in zip(geo, wa):
                ov = _overlap_area(scr, g)
                if ov > best_ov:
                    best_ov, best = ov, w
            out.append(best)
        return screens, out

    def screens(self) -> list[Rect]:
        return self._rects()[0]

    def workareas(self) -> list[Rect]:
        return self._rects()[1]

    def pointer_global(self, win) -> tuple[int, int] | None:
        return _xlib_pointer(win)


class _MacBackend(_PygletBackend):
    """TODO(macos): proper multi-monitor support.

    Replace with AppKit ``NSScreen.frame()/visibleFrame()`` (converted to global
    top-origin via the primary screen height) for geometry/work areas, and place
    windows with ``NSWindow.setFrameTopLeftPoint_`` — pyglet's ``set_location``
    ignores the screen's vertical origin, so it is wrong on secondary screens.

    Until then this inherits the pyglet behaviour: it works on the **primary**
    screen only, without the menu-bar/dock work-area inset (the old
    ``visibleFrame`` logic), and ``pointer_global`` returns None so the shell
    falls back to delta-driven dragging. Linux is unaffected.
    """


if sys.platform == "darwin":
    _backend: _PygletBackend = _MacBackend()
elif sys.platform.startswith("linux"):
    _backend = _LinuxBackend()
else:
    _backend = _PygletBackend()


# ------------------------------------------------------------- public API


def list_screens() -> list[Rect]:
    return _backend.screens()


def list_workarea_rects() -> list[Rect]:
    """Raw work-area rects (unordered); see :func:`list_workareas` for the
    1-based, ordered view used by the move commands."""
    return _backend.workareas()


def list_workareas() -> list[dict]:
    """Work areas ordered left-to-right (then top-to-bottom), 1-based."""
    rects = _backend.workareas()
    primary = _backend.primary()
    ordered = sorted(rects, key=lambda r: (r[0], r[1]))
    return [
        {"index": i, "rect": r, "primary": r == primary}
        for i, r in enumerate(ordered, start=1)
    ]


def workarea_for_point(x: int, y: int) -> Rect:
    rects = _backend.workareas()
    return rect_containing(x, y, rects) or nearest_rect(x, y, rects) or (0, 0, 1920, 1080)


def workarea_for_window(win) -> Rect:
    x, y = _backend.window_top_left(win)
    return workarea_for_point(x, y)


def workarea_by_index(index: int) -> Rect | None:
    for wa in list_workareas():
        if wa["index"] == index:
            return wa["rect"]
    return None


def monitor_index_for_point(x: int, y: int) -> int | None:
    for wa in list_workareas():
        if rect_contains(wa["rect"], x, y):
            return wa["index"]
    return None


def window_top_left(win) -> tuple[int, int]:
    return _backend.window_top_left(win)


def set_window_top_left(win, x: int, y: int) -> None:
    _backend.set_window_top_left(win, x, y)


def pointer_global(win) -> tuple[int, int] | None:
    return _backend.pointer_global(win)


def clamp_to_workarea(x: int, y: int, w: int, h: int, margin: int = MARGIN) -> tuple[int, int]:
    """Clamp to the work area of the screen containing (or nearest to) the target."""
    return clamp_to_rect(x, y, w, h, workarea_for_point(x, y), margin)


def clamp_to_union(x: int, y: int, w: int, h: int, margin: int = MARGIN) -> tuple[int, int]:
    """Clamp to the union of all work areas (drag can cross monitors)."""
    return clamp_to_rects(x, y, w, h, _backend.workareas(), margin)


def spot_position(spot: str, w: int, h: int, rect: Rect) -> tuple[int, int]:
    return spot_in_rect(spot, w, h, rect)
