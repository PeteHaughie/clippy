# ADR-0004: Screen geometry in the shell's coordinate space; cursor-poll drag

## Status

Accepted

## Context

Clippy's avatar window is a pyglet window; the chat pane is a separate
WebKit/GTK window anchored beside it. On a two-monitor Linux box (XWayland) the
following were broken:

- `ClippyShell.visible_screen()` only worked on macOS (`_nswindow`); on Linux it
  returned `None`, so `_visible_rect()` was a hardcoded `(0,0,1920,1080)`.
- `_clamp` pinned moves inside that fake rect, so Clippy could not reach a second
  monitor and `/move <x> <y>` was clamped back.
- The window was **not grabbable at all**: pyglet's `WINDOW_STYLE_OVERLAY`
  forces `set_mouse_passthrough(True)` on X11, and pyglet 2.1.16's
  `set_mouse_passthrough(False)` raises (`XShapeCombineMask` has a bad ctypes
  signature), so the click-through could never be undone.
- `on_mouse_drag` was delta-driven; moving the window changes the next event's
  delta, so drags self-cancelled.

There is also a coordinate-space split: pyglet uses X11 root (device) units,
while the pane's GTK backend uses GDK logical units — on HiDPI these differ by
the global XWayland scale (2× on the dev box).

## Decision Drivers

- Recognise and respect **all** monitors, including work areas (panels/docks).
- Drag must work and cross monitors.
- Keep the avatar's moves self-consistent with pyglet `set_location`.
- Do not regress the pane (it was already correct).

## Considered Options

- **Geometry source**: pyglet screens (same space as `set_location`) vs GDK
  monitors (logical) vs AppKit `NSScreen` (macOS).
- **Drag**: keep delta-driven vs poll the global cursor (`XQueryPointer`).
- **Window style**: overlay (always-on-top + forced click-through) vs borderless
  + manual always-on-top.

## Decision

- Add **`clippy/screens.py`**: pure geometry helpers (containment, nearest,
  clamp, spot, drag target) split from platform backends, so the maths is
  unit-testable without a display.
  - **Linux**: screens from pyglet (the same space as `set_location`); work areas
    from GDK monitors scaled into that space (global scale inferred from the
    monitor at the origin); cursor via `XQueryPointer`.
  - **macOS**: a stub that keeps pyglet behaviour (primary screen, no inset) with
    a TODO for the AppKit `NSScreen`/`setFrameTopLeftPoint_` rewrite.
- `ClippyShell` delegates `position`/`_visible_rect`/`_clamp`/`move_to`/
  `move_to_spot` to `screens`; `_clamp` targets the point's work area, so moves
  cross monitors; `/move monitor <n> [spot]` and `/monitors` were added.
- **Drag** records the grab offset on press and, while held, polls the global
  cursor each frame, placing the window at `cursor − offset` clamped to the
  **union** of work areas. Delta drag remains only as the macOS fallback.
- **Keep `WINDOW_STYLE_OVERLAY`** (for `_NET_WM_STATE_ABOVE`) but override
  `set_mouse_passthrough` to drive the X11 input **region** directly (empty =
  click-through, full-window = normal), bypassing pyglet's broken `False` path.

## Consequences

### Positive

- Multi-monitor moves, monitor commands, and drag (across monitors) work on
  Linux; the window is grabbable.
- Geometry maths is unit-tested without a display.
- macOS behaviour is preserved (stub), not regressed.

### Negative / Risks

- macOS multi-monitor remains imperfect until the AppKit rewrite (documented).
- GDK↔pyglet scale inference assumes a global XWayland scale; a full-geometry
  fallback covers the failure case.
- If pyglet ever reports a single screen for a multi-monitor desktop, the
  Linux backend falls back to scaled GDK geometry.

## Implementation Notes

- `clippy/screens.py`, `clippy/shell.py`, `clippy/session.py` (sub-clippy spawn
  position), `clippy/subagent.py`/`session.py` (`parse_move` → `MoveSpec`).
- `tests/test_screens.py`; end-to-end verified under Xvfb (press lands, 1:1 drag).

## References

- Commits `bd66462` (multi-monitor + drag), `fe8800c` (ungrabbable fix)
- `docs/remediation-plan.md` — Phase 7
- pyglet `window/xlib/__init__.py` (`WINDOW_STYLE_OVERLAY` → passthrough)
