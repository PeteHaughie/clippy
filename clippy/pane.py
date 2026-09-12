"""Clippy's projection surface: the transparent floating chat pane.

A borderless, transparent, always-on-top ``NSPanel`` + ``WKWebView`` rendering
the vendored w1c chat pane (ticket 010/011/014), wired to the prime Pi brain
over the 011 bridge:

* JS → Python: ``postMessage`` ``{type:"chat", text}`` → ``on_chat`` callback
  (the app routes it to ``brain.prompt``); ``{type:"ui_response", id, …}`` →
  ``on_ui_response`` (routes to ``brain.send`` for extension dialogs).
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
    NSPanel,
    NSWindowStyleMaskBorderless,
    NSWindowStyleMaskNonactivatingPanel,
)
from Foundation import NSMakeRect, NSObject, NSURL
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
        self._val = 0
        self._dir = 1

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
        elif kind == "debug":
            print(
                f"[pane] js: {data.get('text') or data.get('body') or data}",
                flush=True,
            )

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

    def _sprite_top(self):
        loc = self.shell.get_location()
        pad = 20
        return loc[1] + pad + self.shell.avatar.frame_h * self.shell.avatar.scale

    def _frame(self):
        loc = self.shell.get_location()
        rim = PANE_H * 0.12  # bottom 12% transparent so the avatar shows through
        sprite_top = self._sprite_top()
        x = loc[0] + 24
        y = max(20, int(sprite_top - rim * 0.5))
        return (x, y, PANE_W, PANE_H)

    # ------------------------------------------------------------ lifecycle

    def summon(self):
        if self.panel is None:
            self.create()
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