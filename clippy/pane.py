"""Clippy's projection surface: the floating chat pane.

The pane renders the vendored w1c chat pane (ticket 010/011/014) in a
borderless, always-on-top window and is wired to the prime Pi brain over the
011 bridge:

* JS → Python: ``postMessage`` ``{type:"chat", text}`` → ``on_chat`` callback
  (the app routes it to ``brain.prompt``); ``{type:"ui_response", id, …}`` →
  ``on_ui_response`` (routes to ``brain.send`` for extension dialogs);
  ``{type:"pane_move", …}`` / ``{type:"pane_resize", …}`` → the window is
  moved/resized on screen (the pane's title bar drags it, a dedicated
  bottom-right handle resizes it, so the pane behaves like a normal OS pane).
* Python → JS: ``__addMessage(role, text)`` for answers, ``__uiRequest(event)``
  to render Pi's ``extension_ui_request`` dialogs (confirm/select/input/editor)
  as w1c cards, and ``__focusInput`` for the active-mode keyboard path.

Two backends expose the same bridge name (``clippy``) and the same Python→JS
API, so ``assets/pane/w1c_pane.html`` and the vendored w1c/marked bundles are
shared verbatim:

* **macOS** — ``WKWebView`` in a transparent ``NSPanel`` (AppKit/WebKit from
  pyobjc). Repaint lever from ticket 010: non-activating panels freeze
  WKWebView compositing, so ``mode="active"`` (default) makes the panel
  key-capable and activates the app on summon so the pane repaints live and
  accepts typing. Screen coords are AppKit bottom-left origin.
* **Linux** — ``WebKitGTK`` 4.1 in a borderless ``Gtk.Window`` (PyGObject).
  The GTK main loop owns the main thread and the avatar's pyglet windows are
  pumped from a 16ms GLib timer (see ``run_integrated`` in main.py). Screen
  coords are GDK top-left origin; the drag/resize logic otherwise mirrors the
  macOS backend, polling the cursor each frame instead of trusting webview
  CSS deltas.

Import order matters on macOS: the pyobjc runtime must come up before pyglet,
so the app imports ``objc`` before this module (guarded on ``sys.platform``).
If neither backend is importable, ``Pane`` is ``NullPane``: the avatar and the
brain still run, Clippy just has nowhere to draw his chart.
"""

import dataclasses
import json
import os
import sys
from pathlib import Path

if sys.platform == "darwin":
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
        NSWorkspace,
    )
    from Foundation import NSMakeRect, NSObject, NSPoint, NSSize, NSURL
    from WebKit import (
        WKNavigationActionPolicyAllow,
        WKNavigationActionPolicyCancel,
        WKWebView,
        WKWebViewConfiguration,
    )

import pyglet

REPO_ROOT = Path(__file__).resolve().parent.parent
PANE_HTML = REPO_ROOT / "assets" / "pane" / "w1c_pane.html"
ASSETS_DIR = REPO_ROOT / "assets"
#: The pane's own document URL. The only navigation the webview is ever
#: allowed to commit to; everything else is intercepted (see
#: ``_classify_navigation``).
PANE_URI = PANE_HTML.resolve().as_uri()

PANE_W, PANE_H = 340, 460  # points; Retina scales pixels x2 for capture
BRIDGE_NAME = "clippy"
MIN_PANE_W, MIN_PANE_H = 260, 300


# ------------------------------------------------------------- shared glue
# Pure helpers shared by both backends so the JavaScript contract stays
# identical regardless of which host window renders the pane.


class _JsMixin:
    """The Python→JS API both backends emit (identical bridge calls)."""

    def add_message(self, role: str, text: str):
        """Append a message bubble to the pane (role: 'you' | 'clippy').
        Clippy bubbles render the text as markdown in the pane."""
        self._evaluate(
            f"window.__addMessage({json.dumps(role)}, {json.dumps(text)});"
        )

    # ------------------------------------------------ reasoning stream
    # One growing bubble per assistant turn. The router re-sends the *full*
    # accumulated thinking/answer text on every delta; the pane re-renders the
    # partial markdown so formatting appears as it streams. stream_end() closes
    # the bubble (final answer text replaces whatever streamed in, so host
    # directives like [CLIPPY::DELEGATE] never linger on screen).

    def stream_start(self):
        """Begin a live reasoning-stream bubble (a new assistant turn)."""
        self._evaluate("window.__streamStart();")

    def stream_thinking(self, text: str):
        """Push the full accumulated thinking (reasoning) text."""
        self._evaluate(f"window.__streamThinking({json.dumps(text)});")

    def stream_text(self, text: str):
        """Push the full accumulated answer text."""
        self._evaluate(f"window.__streamText({json.dumps(text)});")

    def stream_end(self, final_text: str):
        """Finalize the bubble, showing ``final_text`` as the answer."""
        self._evaluate(f"window.__streamEnd({json.dumps(final_text)});")

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


def _route_js_message(body, pane):
    """Route one webview ``postMessage`` payload (JSON string) like the macOS
    backend did: chat / ui_response / mode_toggle callbacks and the drag /
    resize state machine. ``pane`` is the host object exposing ``on_chat``,
    ``on_ui_response``, ``on_mode_toggle``, ``on_move``, ``on_resize`` and
    ``_on_pane_move``/``_on_pane_resize``."""
    data = {}
    if isinstance(body, str):
        try:
            data = json.loads(body)
        except Exception:
            data = {"text": body}
    kind = data.get("type")
    if kind == "chat":
        text = data.get("text", "")
        if pane.on_chat:
            pane.on_chat(text)
    elif kind == "ui_response":
        if pane.on_ui_response:
            pane.on_ui_response(
                data.get("id"),
                {k: v for k, v in data.items() if k not in ("type", "id")},
            )
    elif kind == "mode_toggle":
        if pane.on_mode_toggle:
            pane.on_mode_toggle()
    elif kind == "pane_move":
        if pane.on_move is not None:
            pane.on_move(data)
        else:
            pane._on_pane_move(data)
    elif kind == "pane_resize":
        if pane.on_resize is not None:
            pane.on_resize(data)
        else:
            pane._on_pane_resize(data)
    elif kind == "debug":
        print(
            f"[pane] js: {data.get('text') or data.get('body') or data}",
            flush=True,
        )


def _anchor_box(shell, w: float, h: float) -> tuple:
    """Compute the pane's spot beside Clippy in pyglet top-left coords:
    to his right, tops aligned, clamped to the visible screen.
    ``(px, py, w, h)`` with ``(px, py)`` the pane's top-left corner."""
    sx, sy = shell.position          # Clippy window top-left (top-origin)
    sw, _ = shell.size               # Clippy window width
    gap = 12
    px = sx + sw + gap                # pane top-left, top-origin
    py = sy                           # pane top aligned with Clippy's top
    # Keep the pane fully on the visible screen (clamp in top-origin).
    vx, vy, vw, vh = shell._visible_rect()
    px = max(vx + 8, min(px, vx + vw - w - 8))
    py = max(vy + 8, min(py, vy + vh - h - 8))
    return px, py, w, h


# ------------------------------------------------------ external navigation
# The pane is a locked-down chat surface (ADR-0005): it must never navigate its
# webview away from its own document, or a model-rendered link would replace
# the chat with a web page. Both backends ask ``_classify_navigation`` what to
# do with each navigation request and hand external URLs to the OS browser.
# The predicate is pure so it can be unit-tested without a webview
# (tests/test_pane_links.py).


def _classify_navigation(uri, pane_uri: str = PANE_URI) -> str:
    """Classify a webview navigation request.

    ``"allow"`` — the pane's own document (the initial load) or an internal
    ``about:`` document: let the webview commit it.
    ``"open"`` — an external ``http``/``https``/``mailto`` URL: cancel the
    in-webview navigation and open it in the OS default handler.
    ``"drop"`` — anything else (relative/``file:`` URLs, or no URL at all):
    cancel silently so the pane can never navigate off its document.
    """
    u = str(uri or "").strip()
    if u == pane_uri or u.lower().startswith("about:"):
        return "allow"
    scheme = u.split(":", 1)[0].lower() if ":" in u else ""
    if scheme in ("http", "https", "mailto"):
        return "open"
    return "drop"


def _open_external(uri: str):
    """Open a URL in the OS default handler (browser / mail client)."""
    try:
        if sys.platform == "darwin":
            NSWorkspace.sharedWorkspace().openURL_(NSURL.URLWithString_(uri))
        elif Gtk is not None:
            Gtk.show_uri_on_window(None, uri, Gdk.CURRENT_TIME)
        else:
            import webbrowser

            webbrowser.open(uri)
    except Exception as exc:  # pragma: no cover — platform shell failure
        print(f"[pane] could not open {uri!r}: {exc}", flush=True)


if sys.platform == "darwin":

    # ------------------------------------------------------ macOS backend
    # Transparent floating WKWebView panel: the layout and geometry notes
    # below are AppKit-specific (bottom-left screen origin, CSS px / Retina
    # mismatch, non-activating-panel compositing freeze). These helper classes
    # are only defined on macOS — they derive from pyobjc classes.

    class MacKeyablePanel(NSPanel):
        """A borderless transparent panel that can still become key window so
        the webview can grab keystrokes. Normal borderless panels refuse this."""

        def canBecomeKeyWindow(self):
            return True

        def canBecomeMainWindow(self):
            return True

    class BridgeHandler(NSObject):
        """WKScriptMessageHandler delegate: routes webview postMessage
        to Python."""

        def userContentController_didReceiveScriptMessage_(self, controller, message):
            cb = getattr(self, "py_callback", None)
            if cb:
                cb(message.name(), message.body())

    class NavDelegate(NSObject):
        """WKNavigationDelegate: signals when the pane document has finished
        loading, and keeps every external link out of the pane's webview.

        The pane is a locked-down chat surface, so any navigation that is not
        the pane's own document is cancelled; ``http``/``https``/``mailto``
        URLs are handed to the OS default browser instead (see
        ``_classify_navigation``)."""

        def webView_didFinishNavigation_(self, webview, navigation):
            cb = getattr(self, "py_on_load", None)
            if cb:
                cb()

        def webView_decidePolicyForNavigationAction_decisionHandler_(
            self, webview, action, decision_handler
        ):
            try:
                target = action.targetFrame()
                # A nil target frame is a new-window navigation; treat it as
                # main-frame (nothing may escape the pane either way).
                is_main = target is None or target.isMainFrame()
            except Exception:
                is_main = True
            uri = ""
            if is_main:
                try:
                    uri = action.request().URL().absoluteString()
                except Exception:
                    uri = ""
            verdict = _classify_navigation(uri) if is_main else "allow"
            if verdict == "open":
                _open_external(uri)
            if verdict == "allow":
                decision_handler(WKNavigationActionPolicyAllow)
            else:
                decision_handler(WKNavigationActionPolicyCancel)

    class Pane(_JsMixin):
        """Transparent floating WKWebView panel rendering the w1c chat pane."""

        #: Can raise and answer Clippy-originated consent cards.
        can_confirm = True

        def __init__(self, shell, mode: str = "active"):
            self.shell = shell
            self.mode = mode
            self.panel = None
            self.webview = None
            self.bridge = None
            self.navdelegate = None
            self._loaded = False
            #: JS queued before the webview finished loading, flushed on load
            #: (mirrors the Linux backend). Without this, an early
            #: ``__addMessage``/consent card posted right after summon would be
            #: silently dropped — evaluateJavaScript is a no-op pre-load.
            self._pending: list[str] = []
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
            panel = MacKeyablePanel.alloc().initWithContentRect_styleMask_backing_defer_(
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
            pending, self._pending = self._pending, []
            for js in pending:
                self._evaluate(js)
            self._evaluate("window.__focusInput();")

        # -------------------------------------------------------------- bridge

        def _on_js_message(self, name, body):
            _route_js_message(body, self)

        # ------------------------------------------------------ pane geometry
        # The pane's w1c title bar drags it (pane_move) and the bottom-right
        # handle resizes it (pane_resize); the pane JS posts cursor deltas and the
        # host moves/resizes the real NSPanel. Deltas are CSS px (right +, down +);
        # the panel frame is AppKit bottom-left origin, so y is negated on move.

        MIN_PANE_W, MIN_PANE_H = MIN_PANE_W, MIN_PANE_H

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
            if self.webview is None:
                return
            if not self._loaded:
                self._pending.append(js)
                return

            def _done(result, error):
                if error is not None:
                    print(
                        f"[pane] js error: {error.localizedDescription()} in "
                        f"{js[:60]!r}",
                        flush=True,
                    )

            self.webview.evaluateJavaScript_completionHandler_(js, _done)

        # ------------------------------------------------- API (from _JsMixin)

        def start_driver(self):
            """Track the cursor while the pane is dragged/resized (main thread).
            (The demo progress-bar driver was removed — it evaluated JS in the
            webview on a timer forever, which made the pane sluggish.)"""
            pyglet.clock.schedule_interval(self._geom_tick, 1 / 60)

        # ------------------------------------------------------------- geometry

        def _anchor_frame(self) -> tuple:
            """The pane's spot beside Clippy: to his right, tops aligned, so the
            chat window never overlaps the avatar and its bottom-right corner
            (the resize handle) is clearly its own. Keeps the current size, so a
            user-resized pane re-anchors without shrinking back to the default."""
            px, py, w, h = _anchor_box(self.shell, *self._frame_size())
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


# ------------------------------------------------------- Linux backend
# WebKitGTK 4.1 borderless window rendering the same vendored w1c pane.
# Screen coords are GDK top-left origin, so unlike the macOS backend y is
# never negated: window.move() and window.resize() grow down/right from the
# top-left corner. The drag/resize state machine mirrors the macOS one, and
# both rely on the 16ms GLib pump in main.run_integrated to share the main
# thread with the pyglet avatar.

else:

    class NullPane:
        """Inert fallback for platforms/installs where no pane backend is
        available (missing pyobjc outside macOS, or missing PyGObject /
        WebKitGTK on Linux). The avatar and the brain still run; Clippy just
        has nowhere to render the chat chart."""

        wants_integrated_loop = False
        #: No webview → no way to ask the user, so no consent-gated escalation.
        can_confirm = False

        def __init__(self, shell, mode: str = "active"):
            self.shell = shell
            self.mode = mode
            self.on_chat = None
            self.on_ui_response = None
            self.on_mode_toggle = None
            self.on_move = None
            self.on_resize = None

        def start_driver(self):
            pass

        def add_message(self, role: str, text: str):
            pass

        def stream_start(self):
            pass

        def stream_thinking(self, text: str):
            pass

        def stream_text(self, text: str):
            pass

        def stream_end(self, final_text: str):
            pass

        def ui_request(self, event: dict):
            pass

        def set_progress(self, value: float):
            pass

        def set_mode(self, mode: str):
            pass

        def summon(self):
            pass

        def hide(self):
            pass

        def close(self):
            pass

    try:
        # WebKitGTK's accelerated-compositing path is slow under XWayland without
        # GPU acceleration and shares the main thread with the avatar pump, which
        # makes pane input feel laggy. Force the simpler (non-composited)
        # renderer; must be set before WebKit initialises.
        os.environ.setdefault("WEBKIT_DISABLE_COMPOSITING_MODE", "1")
        import gi

        gi.require_version("Gdk", "3.0")
        gi.require_version("Gtk", "3.0")
        gi.require_version("WebKit2", "4.1")
        from gi.repository import Gdk, GLib, Gtk, WebKit2
    except (ImportError, ValueError) as exc:
        Gtk = WebKit2 = Gdk = GLib = None
        print(
            "[pane] WebKitGTK unavailable; chat pane disabled: "
            f"{exc} (Linux needs PyGObject + the system girepository/WebKitGTK "
            "dev package)",
            flush=True,
        )

    if Gtk is not None:

        class GtkPane(_JsMixin):
            """Borderless always-on-top WebKitGTK window rendering the w1c pane."""

            #: Tells main.py to run the integrated pyglet+GTK loop (--brain only).
            wants_integrated_loop = True
            #: Can raise and answer Clippy-originated consent cards.
            can_confirm = True
            MIN_PANE_W, MIN_PANE_H = MIN_PANE_W, MIN_PANE_H

            def __init__(self, shell, mode: str = "active"):
                self.shell = shell
                self.mode = mode
                self._window = None
                self._webview = None
                self._loaded = False
                self._pending = []
                #: Callbacks set by the app (see the macOS backend).
                self.on_chat = None
                self.on_ui_response = None
                self.on_mode_toggle = None
                self.on_move = None
                self.on_resize = None
                #: User-driven geometry + in-flight drag/resize bookkeeping —
                #: identical semantics to the macOS backend (see above).
                self._user_origin: tuple[float, float] | None = None
                self._user_size: tuple[float, float] | None = None
                self._anchor_shell: tuple[int, int] | None = None
                self._dragging = False
                self._resizing = False
                self._drag_mouse: tuple[float, float] | None = None
                self._drag_off: tuple[float, float] | None = None
                self._resize_mouse: tuple[float, float] | None = None
                self._resize_start: tuple[float, float] | None = None

            # ------------------------------------------------------------ creation

            def create(self):
                x, y, w, h = self._frame()
                win = Gtk.Window()
                win.set_title("Clippy chat")
                win.set_decorated(False)
                win.set_keep_above(True)
                win.set_skip_taskbar_hint(True)
                win.set_resizable(True)
                win.set_default_size(int(w), int(h))
                win.set_position(Gtk.WindowPosition.NONE)
                # WM 'close' on the pane just hides it; the app keeps running.
                win.connect("delete-event", lambda *_: self._on_delete())

                # Solid teal backdrop so the pane isn't painted transparent (X11
                # has no per-pixel alpha for regular windows); the w1c theme fills
                # the whole pane with the same teal anyway.
                bg = Gdk.RGBA()
                bg.parse("#0b7f7f")
                bg.alpha = 1.0

                ucm = WebKit2.UserContentManager()
                try:
                    ucm.register_script_message_handler(BRIDGE_NAME)
                except Exception as exc:  # pragma: no cover — re-summon path
                    print(f"[pane] bridge '{BRIDGE_NAME}' re-registered: {exc}", flush=True)
                ucm.connect(
                    f"script-message-received::{BRIDGE_NAME}", self._on_script_message
                )

                webview = WebKit2.WebView.new_with_user_content_manager(ucm)
                try:
                    webview.set_background_color(bg)
                except Exception:
                    pass
                webview.connect("load-changed", self._on_load_changed)
                webview.connect("decide-policy", self._on_decide_policy)
                webview.load_uri(PANE_HTML.resolve().as_uri())

                win.add(webview)
                win.move(int(x), int(y))

                self._window = win
                self._webview = webview
                print(f"[pane] created {w}x{h}pt (mode={self.mode})", flush=True)

            def _on_delete(self):
                self.hide()
                return True

            def _on_load_changed(self, webview, event):
                if event == WebKit2.LoadEvent.FINISHED:
                    self._loaded = True
                    pending, self._pending = self._pending, []
                    for js in pending:
                        self._evaluate(js)
                    self._evaluate("window.__focusInput();")

            # -------------------------------------------------------------- bridge

            def _on_js_message(self, name, body):
                _route_js_message(body, self)

            def _on_decide_policy(self, webview, decision, decision_type):
                """Keep external links out of the pane: cancel any navigation
                that is not the pane's own document and hand ``http``/``https``/
                ``mailto`` URLs to the OS browser (mirrors the macOS navigation
                delegate). Returns True when the decision is handled here."""
                if decision_type != WebKit2.PolicyDecisionType.NAVIGATION_ACTION:
                    return False
                try:
                    uri = decision.get_navigation_action().get_request().get_uri()
                except Exception:
                    uri = None
                verdict = _classify_navigation(uri)
                if verdict == "allow":
                    return False  # let WebKit commit the pane's own document
                if verdict == "open":
                    _open_external(uri)
                decision.ignore()
                return True

            def _on_script_message(self, ucm, result):
                """Emit the posted JSON string exactly like WKScriptMessage.body."""
                js = result.get_js_value()
                try:
                    text = js.to_string()
                except Exception:
                    text = ""
                self._on_js_message(BRIDGE_NAME, text)

            # ------------------------------------------------------ pane geometry
            # GDK root is top-left origin, so followed 1:1: move()/resize() grow
            # down/right and `my` grows downward (no negation anywhere).

            def _mouse_global(self):
                display = Gdk.Display.get_default()
                if display is None:
                    return None
                seat = display.get_default_seat()
                pointer = seat.get_pointer()
                _, root_x, root_y = pointer.get_position()
                return (root_x, root_y)

            def _panel_global_origin(self):
                if self._window is None:
                    return None
                return self._window.get_position()

            def _set_frame_from_global(self, gx: float, gy: float):
                self._move_panel(gx, gy)

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
                # Top-left origin: dragging DOWN grows the pane (its bottom edge
                # follows the handle), so the vertical delta is added, not negated.
                w = w0 + (mx - self._resize_mouse[0])
                h = h0 + (my - self._resize_mouse[1])
                self._resize_panel(int(w), int(h))

            def _geom_tick(self, dt):
                if self._window is None:
                    return
                if self._dragging:
                    self._drag_tick()
                if self._resizing:
                    self._resize_tick()

            def _move_panel(self, x: float, y: float):
                if self._window is None:
                    return
                self._window.move(int(x), int(y))
                self._remember_geometry()

            def _resize_panel(self, w: int, h: int):
                if self._window is None:
                    return
                w = max(self.MIN_PANE_W, int(w))
                h = max(self.MIN_PANE_H, int(h))
                self._window.resize(int(w), int(h))
                self._remember_geometry()

            def _sync_webview(self):
                """The webview is the window's only child, so GTK keeps it sized
                to the window automatically — nothing to force (contrast the
                macOS backend, which must resize WKWebView on every change)."""
                pass

            def _frame_origin(self):
                if self._window is None:
                    return None
                return self._window.get_position()

            def _frame_size(self):
                if self._window is None:
                    return (PANE_W, PANE_H)
                return self._window.get_size()

            def _remember_geometry(self):
                if self._window is None:
                    return
                self._user_origin = self._frame_origin()
                self._user_size = self._frame_size()
                self._anchor_shell = self.shell.get_location()

            def _evaluate(self, js):
                if self._webview is None:
                    return
                if not self._loaded:
                    self._pending.append(js)
                    return

                def _done(webview, result, data):
                    try:
                        webview.evaluate_javascript_finish(result)
                    except GLib.Error as error:
                        print(
                            f"[pane] js error: {error.message} in {js[:60]!r}",
                            flush=True,
                        )

                try:
                    self._webview.evaluate_javascript(js, -1, None, None, None, _done, None)
                except GLib.Error as error:
                    print(
                        f"[pane] js error: {error.message} in {js[:60]!r}",
                        flush=True,
                    )

            # ------------------------------------------------- API (from _JsMixin)

            def start_driver(self):
                """Track the cursor while the pane is dragged/resized (main thread).
                (The demo progress-bar driver was removed — it evaluated JS in the
                webview on a timer forever, which made the pane sluggish.)"""
                pyglet.clock.schedule_interval(self._geom_tick, 1 / 60)

            # ------------------------------------------------------------- geometry

            def _anchor_frame(self) -> tuple:
                return _anchor_box(self.shell, *self._frame_size())  # top-left origin

            def _frame(self):
                if self._user_origin is not None and self._anchor_shell is not None:
                    if self.shell.get_location() == self._anchor_shell:
                        x, y = self._user_origin
                        w, h = self._user_size or (PANE_W, PANE_H)
                        return (x, y, w, h)
                    self._user_origin = None
                    self._user_size = None
                    self._anchor_shell = None
                return self._anchor_frame()

            # ------------------------------------------------------- position API

            @property
            def position(self):
                """The pane's top-left ``(x, y)`` (top-origin), or None before
                creation. GTK already reports top-left, so no conversion."""
                if self._window is None:
                    return None
                return self._window.get_position()

            def move_to(self, x: int, y: int):
                if self._window is None:
                    return
                self._move_panel(int(x), int(y))

            # ------------------------------------------------------------ lifecycle

            def summon(self):
                if self._window is None:
                    self.create()
                else:
                    if self._user_origin is not None:
                        if self.shell.get_location() != self._anchor_shell:
                            self._user_origin = None
                            self._user_size = None
                            self._anchor_shell = None
                            x, y, w, h = self._anchor_frame()
                            self._window.move(int(x), int(y))
                            self._window.resize(int(w), int(h))
                if self.mode == "active":
                    self._window.show_all()
                    self._window.present()
                    self._evaluate("window.__focusInput();")
                else:
                    self._window.show_all()
                print(f"[pane] summoned (mode={self.mode})", flush=True)
                pyglet.clock.schedule_once(lambda dt: self._refocus(0), 1.0)

            def _refocus(self, attempt):
                if self._window is None or not self._window.is_visible():
                    return
                self._evaluate("window.__focusInput();")
                if attempt < 3:
                    pyglet.clock.schedule_once(lambda dt: self._refocus(attempt + 1), 0.8)

            def hide(self):
                if self._window is not None:
                    self._window.hide()
                    print("[pane] hidden", flush=True)

            def close(self):
                if self._window is not None:
                    self._window.hide()
                    self._window.destroy()
                    self._window = None
                    self._webview = None

        Pane = GtkPane

    else:
        Pane = NullPane