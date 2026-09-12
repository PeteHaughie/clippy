"""Clippy's projection surface: the transparent floating chat pane.

A borderless, transparent, always-on-top ``NSPanel`` + ``WKWebView`` rendering
the vendored w1c chat pane (ticket 010/011/014), wired to the prime Pi brain
over the 011 bridge:

* JS → Python: ``postMessage`` ``{type:"chat", text}`` → ``on_chat`` callback
  (the app routes it to ``brain.prompt``); ``{type:"ui_response", id, …}`` →
  ``on_ui_response`` (routes to ``brain.send`` for extension dialogs);
  ``{type:"pane_move", …}`` / ``{type:"pane_resize", …}`` → the panel is
  moved/resized on screen (the pane's title bar drags it, a dedicated
  bottom-right handle resizes it, so the pane behaves like a normal OS pane).
* Python → JS: ``__addMessage(role, text)`` for answers, ``__uiRequest(event)``
  to render Pi's ``extension_ui_request`` dialogs (confirm/select/input/editor)
  as w1c cards, and ``__focusInput`` for the active-mode keyboard path.

Repaint lever from ticket 010: non-activating panels freeze WKWebView
compositing, so ``mode="active"`` (default) makes the panel key-capable and
activates the app on summon so the pane repaints live and accepts typing.

Import order matters: the pyobjc runtime must come up before pyglet, so the
app imports ``objc`` before this module.
"""

import dataclasses
import json
import os
from pathlib import Path

import objc  # noqa: F401  (ensures the pyobjc runtime is up first)
from AppKit import (
    NSApplication,
    NSBackingStoreBuffered,
    NSColor,
    NSFloatingWindowLevel,
    NSEvent,
    NSPanel,
    NSWindowStyleMaskBorderless,
    NSWindowStyleMaskNonactivatingPanel,
)
from Foundation import NSMakeRect, NSObject, NSPoint, NSSize, NSURL
from WebKit import WKWebView, WKWebViewConfiguration

import pyglet

REPO_ROOT = Path(__file__).resolve().parent.parent
PANE_HTML = REPO_ROOT / "assets" / "pane" / "w1c_pane.html"
ASSETS_DIR = REPO_ROOT / "assets"

PANE_W, PANE_H = 340, 460  # points; Retina scales pixels x2 for capture
BRIDGE_NAME = "clippy"


class KeyablePanel(NSPanel):
    """A borderless transparent panel that can still become key window so the
    webview can grab keystrokes. Normal borderless panels refuse this."""

    def canBecomeKeyWindow(self):
        return True

    def canBecomeMainWindow(self):
        return True


class BridgeHandler(NSObject):
    """WKScriptMessageHandler delegate: routes webview postMessage to Python."""

    def userContentController_didReceiveScriptMessage_(self, controller, message):
        cb = getattr(self, "py_callback", None)
        if cb:
            cb(message.name(), message.body())


class NavDelegate(NSObject):
    """WKNavigationDelegate: signals when the pane document has finished
    loading, so driver/focus/card JS only runs once the page is live."""

    def webView_didFinishNavigation_(self, webview, navigation):
        cb = getattr(self, "py_on_load", None)
        if cb:
            cb()


class Pane:
    """Transparent floating WKWebView panel rendering the w1c chat pane."""

    def __init__(self, shell, mode: str = "active"):
        self.shell = shell
        self.mode = mode
        self.panel = None
        self.webview = None
        self.bridge = None
        self.navdelegate = None
        self._loaded = False
        #: Callbacks set by the app.
        self.on_chat = None          # on_chat(text) — user typed in the pane
        self.on_ui_response = None   # on_ui_response(id, payload) — dialog answered
        self.on_mode_toggle = None   # on_mode_toggle() — Tab pressed in the pane
        #: Drag/resize geometry arrives on WebKit's script-handler thread (see
        #: session.py): the app marshals it onto the main frame tick, then calls
        #: _on_pane_move/_on_pane_resize *on the main thread*. AppKit frame
        #: mutations must never run on the bridge thread or the pane jumps.
        self.on_move = None          # on_move(data) → queued, run on main thread
        self.on_resize = None        # on_resize(data) → queued, run on main thread
        self._val = 0
        self._dir = 1
        #: User-driven geometry: the pane's last dragged/resized frame and the
        #: shell location it was anchored to then. hide()/summon() reuse it;
        #: if Clippy himself moves, the pane re-anchors beside him.
        self._user_origin: tuple[float, float] | None = None
        self._user_size: tuple[float, float] | None = None
        self._anchor_shell: tuple[int, int] | None = None
        #: In-flight drag/resize bookkeeping (bridge → panel). The panel follows the
        #: cursor's *AppKit screen position* (polled on the main thread), so no
        #: webview CSS deltas are involved — immune to the CSS px/Retina scale
        #: mismatch and the move/resize feedback that plagued delta-driven moves.
        self._dragging = False
        self._resizing = False
        self._drag_mouse: tuple[float, float] | None = None   # cursor at drag start
        self._drag_off: tuple[float, float] | None = None      # cursor − panel origin
        self._resize_mouse: tuple[float, float] | None = None  # cursor at resize start
        self._resize_start: tuple[float, float] | None = None  # panel size at start

    # ------------------------------------------------------------ creation

    def create(self):
        frame = self._frame()
        style = NSWindowStyleMaskBorderless | NSWindowStyleMaskNonactivatingPanel
        panel = KeyablePanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(*frame), style, NSBackingStoreBuffered, False
        )
        panel.setFloatingPanel_(True)
        panel.setOpaque_(False)
        panel.setBackgroundColor_(NSColor.clearColor())
        panel.setHasShadow_(False)
        panel.setIgnoresMouseEvents_(False)  # interactive: chat input + consent cards
        panel.setHidesOnDeactivate_(False)
        panel.setLevel_(NSFloatingWindowLevel)
        panel.setReleasedWhenClosed_(False)

        config = WKWebViewConfiguration.alloc().init()
        ucc = config.userContentController()
        bridge = BridgeHandler.alloc().init()
        bridge.py_callback = self._on_js_message
        ucc.addScriptMessageHandler_name_(bridge, BRIDGE_NAME)

        webview = WKWebView.alloc().initWithFrame_configuration_(
            NSMakeRect(0, 0, PANE_W, PANE_H), config
        )
        webview.setValue_forKey_(False, "drawsBackground")
        webview.setWantsLayer_(True)

        panel.setContentView_(webview)

        html_url = NSURL.fileURLWithPath_(str(PANE_HTML))
        base_url = NSURL.fileURLWithPath_(str(ASSETS_DIR))
        webview.loadFileURL_allowingReadAccessToURL_(html_url, base_url)

        self.panel = panel
        self.webview = webview
        self.bridge = bridge
        self.navdelegate = NavDelegate.alloc().init()
        self.navdelegate.py_on_load = self._on_webview_loaded
        webview.setNavigationDelegate_(self.navdelegate)
        # Match the webview to the panel's size (a persisted user-resized pane
        # must not leave the HTML viewport at the 340x460 default).
        self._sync_webview()
        print(f"[pane] created {PANE_W}x{PANE_H}pt (mode={self.mode})", flush=True)

    def _on_webview_loaded(self):
        self._loaded = True
        self._evaluate("window.__focusInput();")
        self.set_progress(self._val)

    # -------------------------------------------------------------- bridge

    def _on_js_message(self, name, body):
        data = {}
        if isinstance(body, str):
            try:
                data = json.loads(body)
            except Exception:
                data = {"text": body}
        kind = data.get("type")
        if kind == "chat":
            text = data.get("text", "")
            if self.on_chat:
                self.on_chat(text)
        elif kind == "ui_response":
            if self.on_ui_response:
                self.on_ui_response(
                    data.get("id"),
                    {k: v for k, v in data.items() if k not in ("type", "id")},
                )
        elif kind == "mode_toggle":
            if self.on_mode_toggle:
                self.on_mode_toggle()
        elif kind == "pane_move":
            if self.on_move is not None:
                self.on_move(data)
            else:
                self._on_pane_move(data)
        elif kind == "pane_resize":
            if self.on_resize is not None:
                self.on_resize(data)
            else:
                self._on_pane_resize(data)
        elif kind == "debug":
            print(
                f"[pane] js: {data.get('text') or data.get('body') or data}",
                flush=True,
            )

    # ------------------------------------------------------ pane geometry
    # The pane's w1c title bar drags it (pane_move) and the bottom-right
    # handle resizes it (pane_resize); the pane JS posts cursor deltas and the
    # host moves/resizes the real NSPanel. Deltas are CSS px (right +, down +);
    # the panel frame is AppKit bottom-left origin, so y is negated on move.

    MIN_PANE_W, MIN_PANE_H = 260, 300

    # ---------------------------------------------------- cursor geometry
    # The w1c title bar / resize handle post drag start/end; while active the
    # panel tracks the cursor's AppKit screen position (polled each frame).
    # This keeps everything in AppKit points — no webview CSS px, no scale
    # factor, no feedback — so the pane follows the cursor 1:1 on screen.

    def _mouse_global(self) -> tuple[float, float]:
        p = NSEvent.mouseLocation()
        return (p.x, p.y)

    def _panel_global_origin(self):
        """The panel's origin in global screen coords (bottom-left origin)."""
        if self.panel is None:
            return None
        screen = self.panel.screen()
        so = screen.frame().origin
        o = self.panel.frame().origin
        return (so.x + o.x, so.y + o.y)

    def _set_frame_from_global(self, gx: float, gy: float):
        screen = self.panel.screen()
        so = screen.frame().origin
        self._move_panel(gx - so.x, gy - so.y)

    def _on_pane_move(self, data: dict):
        phase = data.get("phase")
        if phase == "start":
            mouse = self._mouse_global()
            origin = self._panel_global_origin()
            if origin is None:
                return
            self._drag_mouse = mouse
            self._drag_off = (mouse[0] - origin[0], mouse[1] - origin[1])
            self._dragging = True
        elif phase == "end":
            self._dragging = False
            self._drag_mouse = None
            self._drag_off = None

    def _drag_tick(self):
        if not self._dragging or self._drag_off is None or self._drag_mouse is None:
            return
        mx, my = self._mouse_global()
        # Keep the grab point under the cursor: target origin = cursor − offset.
        self._set_frame_from_global(mx - self._drag_off[0], my - self._drag_off[1])

    def _on_pane_resize(self, data: dict):
        phase = data.get("phase")
        if phase == "start":
            self._resize_mouse = self._mouse_global()
            self._resize_start = self._frame_size()
            self._resizing = True
        elif phase == "end":
            self._resizing = False
            self._resize_mouse = None
            self._resize_start = None

    def _resize_tick(self):
        if not self._resizing or self._resize_start is None or self._resize_mouse is None:
            return
        mx, my = self._mouse_global()
        w0, h0 = self._resize_start
        w = w0 + (mx - self._resize_mouse[0])
        # AppKit y grows upward, so dragging DOWN decreases `my` — which should
        # grow the pane (its bottom edge follows the handle). Negate the delta.
        h = h0 - (my - self._resize_mouse[1])
        self._resize_panel(int(w), int(h))

    def _geom_tick(self, dt):
        if self.panel is None:
            return
        if self._dragging:
            self._drag_tick()
        if self._resizing:
            self._resize_tick()

    def _move_panel(self, x: float, y: float):
        if self.panel is None:
            return
        self.panel.setFrameOrigin_(NSPoint(x, y))
        self._remember_geometry()

    def _resize_panel(self, w: int, h: int):
        if self.panel is None:
            return
        w = max(self.MIN_PANE_W, int(w))
        h = max(self.MIN_PANE_H, int(h))
        # setContentSize_ keeps the panel's top-left fixed on this borderless
        # NSPanel, growing down/right — the normal OS-pane resize feel. Do NOT
        # also move the origin here: that drifted the top edge, shifted the
        # webview's clientY and fed back into the deltas (runaway sizing).
        self.panel.setContentSize_(NSSize(w, h))
        self._sync_webview()
        self._remember_geometry()

    def _sync_webview(self):
        """Force the WKWebView to match the panel's content size, so the HTML
        layout viewport (100vh) always tracks the panel. Without this the
        webview can hold a stale viewport after a resize, leaving a gap below
        the chat window and the resize handle drifting away from the corner."""
        if self.panel is None or self.webview is None:
            return
        size = self.panel.frame().size
        self.webview.setFrameSize_(NSSize(size.width, size.height))

    def _frame_origin(self):
        if self.panel is None:
            return None
        o = self.panel.frame().origin
        return (o.x, o.y)

    def _frame_size(self):
        if self.panel is None:
            return (PANE_W, PANE_H)
        s = self.panel.frame().size
        return (s.width, s.height)

    def _remember_geometry(self):
        """Snapshot the pane's frame and which shell location it was anchored
        to, so hide/summon keeps the user's layout until Clippy moves."""
        if self.panel is None:
            return
        self._user_origin = self._frame_origin()
        self._user_size = self._frame_size()
        self._anchor_shell = self.shell.get_location()

    def _evaluate(self, js):
        if self.webview is None or not self._loaded:
            return

        def _done(result, error):
            if error is not None:
                print(
                    f"[pane] js error: {error.localizedDescription()} in "
                    f"{js[:60]!r}",
                    flush=True,
                )

        self.webview.evaluateJavaScript_completionHandler_(js, _done)

    # ---------------------------------------------------------------- API

    def add_message(self, role: str, text: str):
        """Append a message bubble to the pane (role: 'you' | 'clippy')."""
        self._evaluate(
            f"window.__addMessage({json.dumps(role)}, {json.dumps(text)});"
        )

    def ui_request(self, event: dict):
        """Render a Pi ``extension_ui_request`` as a card/dialog in the pane.

        ``event`` is the normalized :class:`clippy.model.UiRequest` (an *Ev*
        dataclass). The webview contract is a flat dict — the payload fields
        (md: ``method``/``title``/``message``/``options``/…) live under
        ``payload``, so flatten them to the top level before serializing.
        """
        flat = dataclasses.asdict(event)
        flat.update(flat.pop("payload", {}) or {})
        print(f"[pane] ui_request {flat.get('method')} id={flat.get('id')}", flush=True)
        self._evaluate(f"window.__uiRequest({json.dumps(flat)});")

    def set_progress(self, value: float):
        self._evaluate(f"window.__setProgress({json.dumps(round(value))});")

    def set_mode(self, mode: str):
        """Show the sandbox/build badge in the pane statusbar."""
        self._evaluate(f"window.__setMode({json.dumps(mode)});")

    def start_driver(self):
        """Optional demo driver: tick the pane's progress bar."""
        pyglet.clock.schedule_interval(self._drive, 0.4)
        # Track the cursor while the pane is being dragged/resized (main thread).
        pyglet.clock.schedule_interval(self._geom_tick, 1 / 60)

    def _drive(self, dt):
        if self.webview is None or self.panel is None or not self.panel.isVisible():
            return
        v = self._val + 5 * self._dir
        if v >= 100:
            v = 100
            self._dir = -1
        if v <= 0:
            v = 0
            self._dir = 1
        self._val = v
        self.set_progress(v)

    # ------------------------------------------------------------- geometry

    def _anchor_frame(self) -> tuple:
        """The pane's spot beside Clippy: to his right, tops aligned, so the
        chat window never overlaps the avatar and its bottom-right corner
        (the resize handle) is clearly its own. Keeps the current size, so a
        user-resized pane re-anchors without shrinking back to the default."""
        w, h = self._frame_size()
        sx, sy = self.shell.position          # Clippy window top-left (top-origin)
        sw, _ = self.shell.size               # Clippy window width
        gap = 12
        px = sx + sw + gap                    # pane top-left, top-origin
        py = sy                               # pane top aligned with Clippy's top
        # Keep the pane fully on the visible screen (clamp in top-origin).
        vx, vy, vw, vh = self.shell._visible_rect()
        px = max(vx + 8, min(px, vx + vw - w - 8))
        py = max(vy + 8, min(py, vy + vh - h - 8))
        ns = self.shell.visible_screen()
        screen_h = int(ns.frame().size.height) if ns else 1440
        return (px, screen_h - py - h, w, h)  # AppKit bottom-left origin

    def _frame(self):
        if self._user_origin is not None and self._anchor_shell is not None:
            if self.shell.get_location() == self._anchor_shell:
                x, y = self._user_origin
                w, h = self._user_size or (PANE_W, PANE_H)
                return (x, y, w, h)
            # Clippy moved since the pane was dragged: re-anchor beside him.
            self._user_origin = None
            self._user_size = None
            self._anchor_shell = None
        return self._anchor_frame()

    # ------------------------------------------------------- position API
    # Mirror of the shell's position API, in pyglet top-origin screen coords.

    @property
    def position(self):
        """The pane's top-left ``(x, y)`` on screen, or None before creation."""
        if self.panel is None:
            return None
        f = self.panel.frame()
        screen = self.panel.screen()
        sh = screen.frame().size.height if screen else 0
        return (int(f.origin.x), int(sh - (f.origin.y + f.size.height)))

    def move_to(self, x: int, y: int):
        """Move the pane so its top-left is at ``(x, y)`` (top-origin coords)."""
        if self.panel is None:
            return
        screen = self.panel.screen()
        sh = screen.frame().size.height if screen else 0
        w, h = self._frame_size()
        self._move_panel(int(x), sh - int(y) - h)

    # ------------------------------------------------------------ lifecycle

    def summon(self):
        if self.panel is None:
            self.create()
        else:
            # Re-anchor beside Clippy if he moved since the pane was last
            # placed (drag or /move); otherwise keep the user's layout.
            if self._user_origin is not None:
                if self.shell.get_location() != self._anchor_shell:
                    self._user_origin = None
                    self._user_size = None
                    self._anchor_shell = None
                    x, y, w, h = self._anchor_frame()
                    self.panel.setFrameOrigin_(NSPoint(x, y))
                    self.panel.setContentSize_(NSSize(w, h))
        self._sync_webview()
        self.panel.orderOut_(None)
        if self.mode == "active":
            NSApplication.sharedApplication().activateIgnoringOtherApps_(True)
            self.panel.makeKeyAndOrderFront_(None)
            self.panel.makeFirstResponder_(self.webview)
            self._evaluate("window.__focusInput();")
        else:
            self.panel.orderFrontRegardless()
        print(f"[pane] summoned (mode={self.mode})", flush=True)
        pyglet.clock.schedule_once(lambda dt: self._refocus(0), 1.0)

    def _refocus(self, attempt):
        if self.panel is None or not self.panel.isVisible():
            return
        self.panel.makeFirstResponder_(self.webview)
        self._evaluate("window.__focusInput();")
        if attempt < 3:
            pyglet.clock.schedule_once(lambda dt: self._refocus(attempt + 1), 0.8)

    def hide(self):
        if self.panel is not None:
            self.panel.orderOut_(None)
            print("[pane] hidden", flush=True)

    def close(self):
        if self.panel is not None:
            self.panel.orderOut_(None)
            self.panel.close()
            self.panel = None
            self.webview = None