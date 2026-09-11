"""Interactive pane (ticket 011): JS<->Python bridge on the 95CSS chat pane.

Builds on the 010 rendering spike. The pane's HTML now exposes a typed input
and a script-message channel (window.webkit.messageHandlers.clippy). Python
receives messages via a WKScriptMessageHandler delegate and answers via
evaluateJavaScript; a scripted mock round-trip exercises the full loop.

Repaint lever (010 finding: background non-activating panels freeze WKWebView
compositing):  ``--mode active`` (default) activates the app + key-capable
panel + firstResponder(webview) on summon so the pane repaints live and
accepts typing; ``--mode passive`` is the pure click-through 010 behavior.

Controls (on the Clippy window):
  N  summon the pane        X  hide the pane
  Q  quit                   P/T/Space  inherited demo keys

Run modes:
  default      scripted summon->hide->summon->hide churn (+ mock round-trip)
  --hold       single summon window
  --manual     no churn; you drive N/X/Q (and type into the pane)
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Import pyobjc BEFORE pyglet so both ObjC bridges share one runtime cleanly.
import objc  # noqa: F401  (ensures the pyobjc runtime is up first)
from AppKit import (
    NSApplication,
    NSBackingStoreBuffered,
    NSColor,
    NSFloatingWindowLevel,
    NSPanel,
    NSScreen,
    NSWindowStyleMaskBorderless,
    NSWindowStyleMaskNonactivatingPanel,
)
from Foundation import NSMakeRect, NSURL
from WebKit import WKWebView, WKWebViewConfiguration

# pyobjc's NSObject lives behind the explicit re-export; import it last
# so it never shadowed the pyobjc runtime guards above.
from Foundation import NSObject

import pyglet

from clippy.shell import ClippyShell

REPO_ROOT = Path(__file__).resolve().parent
PANE_HTML = REPO_ROOT / "assets" / "pane" / "spike_pane.html"
ASSETS_DIR = REPO_ROOT / "assets"

PANE_W, PANE_H = 340, 460  # points; Retina scales pixels x2 for capture
BRIDGE_NAME = "clippy"

CHURN = [(1.2, "summon"), (4.5, "hide"), (8.0, "summon"), (11.5, "hide"), (12.5, "quit")]
# --hold: single summon window long enough to capture the JS animation.
HOLD = [(1.2, "summon"), (6.0, "hide"), (7.0, "quit")]


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


class Pane:
    """Transparent floating WKWebView panel loading the 95CSS pane html."""

    def __init__(self, shell: ClippyShell, mode: str = "active", diag: str | None = None,
                 selftest: bool = False):
        self.shell = shell
        self.mode = mode
        self.diag = diag
        self.selftest = selftest
        self.panel = None
        self.webview = None
        self.bridge = None
        self._echoed = False

    # ------------------------------------------------------------ creation

    def create(self):
        opaque = self.diag in ("opaque", "whitebg")
        panel_bg = NSColor.redColor() if self.diag == "opaque" else NSColor.clearColor()
        transparent_bg = not (self.diag == "whitebg")
        frame = self._frame()
        style = NSWindowStyleMaskBorderless | NSWindowStyleMaskNonactivatingPanel
        panel = KeyablePanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(*frame), style, NSBackingStoreBuffered, False
        )
        panel.setFloatingPanel_(True)
        panel.setOpaque_(opaque)
        panel.setBackgroundColor_(panel_bg)
        panel.setHasShadow_(False)
        panel.setIgnoresMouseEvents_(True)  # clippy stays click-through
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
        if transparent_bg:
            webview.setValue_forKey_(False, "drawsBackground")
        webview.setWantsLayer_(True)

        panel.setContentView_(webview)

        html_url = NSURL.fileURLWithPath_(str(PANE_HTML))
        base_url = NSURL.fileURLWithPath_(str(ASSETS_DIR))
        webview.loadFileURL_allowingReadAccessToURL_(html_url, base_url)

        self.panel = panel
        self.webview = webview
        self.bridge = bridge
        x, y = int(frame[0]), int(frame[1])
        print(
            f"[pane] created {PANE_W}x{PANE_H}pt at bottom-left ({x},{y}) "
            f"(sprite top {self._sprite_top():.0f}pt)", flush=True
        )
        print(f"[pane] panel.frame() -> {panel.frame()}", flush=True)
        sf = NSScreen.mainScreen().frame()
        print(f"[pane] main screen {sf.size.width:.0f}x{sf.size.height:.0f}pt", flush=True)

    # -------------------------------------------------------------- bridge

    def _on_js_message(self, name, body):
        print(f"[pane] <- js ({name}): {body}", flush=True)
        data = {}
        if isinstance(body, str):
            try:
                data = json.loads(body)
            except Exception:
                data = {"text": body}
        if data.get("type") == "chat":
            text = data.get("text", "")
            js = (
                "window.__addMessage('clippy', 'echo: ' + "
                + json.dumps(text)
                + "); document.getElementById('jsstate').textContent = 'bridge: ok';"
            )
            self.webview.evaluateJavaScript_completionHandler_(js, None)
            self._echoed = True
            print("[pane] bridge round-trip complete", flush=True)

    def _evaluate(self, js):
        if self.webview is None:
            return
        self.webview.evaluateJavaScript_completionHandler_(js, None)

    def _eval_probe(self, js, label):
        def done(result, error):
            print(f"[pane] probe {label}: result={result!r} error={error!r}", flush=True)

        self.webview.evaluateJavaScript_completionHandler_(js, done)

    # -------------------------------------------------------------- driver

    def start_driver(self):
        """Python-side progress driver (pyglet clock). Round-trip proof and a
        taste of the stage-3 JS<->Python bridge."""
        self._val = 0
        self._dir = 1
        pyglet.clock.schedule_interval(self._drive, 0.25)

    def _drive(self, dt):
        if self.webview is None or self.panel is None:
            return
        if not self.panel.isVisible():
            return
        v = self._val + 5 * self._dir
        if v >= 100:
            v = 100
            self._dir = -1
        if v <= 0:
            v = 0
            self._dir = 1
        self._val = v
        self._evaluate(f"window.__setProgress({v});")

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
        # Give the webview a beat to settle, then probe focus + echo.
        pyglet.clock.schedule_once(lambda dt: self._probe_focus(0), 1.2)

    def _probe_focus(self, attempt):
        if self.panel is None or not self.panel.isVisible():
            return
        # Make key + first responder each round; WebKit only honours
        # input.focus() once the webview is genuinely the key view.
        self.panel.makeFirstResponder_(self.webview)
        self._evaluate("window.__focusInput();")
        self._eval_probe(
            "document.activeElement ? (document.activeElement.id || "
            "document.activeElement.tagName) : 'none'",
            f"activeElement#{attempt}",
        )
        if attempt == 0 and not self._echoed:
            self._evaluate("window.__sendMock();")
        if attempt == 1 and self.selftest:
            # Focus has settled; synthesize real keystrokes now.
            self._selftest_typing()
        if attempt < 4:
            pyglet.clock.schedule_once(lambda dt: self._probe_focus(attempt + 1), 0.8)

    # ---- real-keyboard self test (CGEventPost → focused WKWebView input)
    _SELFTEST_TEXT = "hi from keyboard"

    _ANSI_KEYCODES = {
        "a": 0, "b": 11, "c": 8, "d": 2, "e": 14, "f": 3, "g": 5, "h": 4,
        "i": 34, "j": 38, "k": 40, "l": 37, "m": 46, "n": 45, "o": 31,
        "p": 35, "q": 12, "r": 15, "s": 1, "t": 17, "u": 32, "v": 9,
        "w": 13, "x": 7, "y": 16, "z": 6,
    }
    KEY_ENTER, KEY_SPACE = 36, 49

    def _selftest_typing(self):
        try:
            import Quartz
        except Exception as exc:
            print(f"[pane] selftest: Quartz unavailable ({exc})", flush=True)
            return
        print(f"[pane] selftest: typing {self._SELFTEST_TEXT!r} via CGEvent", flush=True)

        def tap(keycode, down):
            e = Quartz.CGEventCreateKeyboardEvent(None, keycode, down)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, e)

        def tap_char(ch):
            code = self._ANSI_KEYCODES.get(ch.lower(), None)
            if code is None:
                return False
            tap(code, True)
            tap(code, False)
            return True

        for ch in self._SELFTEST_TEXT:
            if ch == " ":
                tap(self.KEY_SPACE, True)
                tap(self.KEY_SPACE, False)
            elif not tap_char(ch):
                print(f"[pane] selftest: no keycode for {ch!r}", flush=True)
                return
        tap(self.KEY_ENTER, True)  # Send
        tap(self.KEY_ENTER, False)
        # Give WebKit a beat to process the keystrokes, then verify.
        pyglet.clock.schedule_once(lambda dt: self._selftest_verify(), 1.0)

    def _selftest_verify(self):
        js = (
            "JSON.stringify({"
            "  value: document.getElementById('chatinput').value,"
            "  echoed: [...document.querySelectorAll('.msg.clippy')]"
            "      .some(m => m.textContent.includes('echo: hi from keyboard'))"
            "})"
        )
        self._eval_probe(js, "selftest")

    def hide(self):
        if self.panel is not None:
            self.panel.orderOut_(None)
            print("[pane] hidden", flush=True)


class SpikeShell(ClippyShell):
    """ClippyShell with N (summon pane) and X (hide pane) added."""

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop("_mode", "active")
        diag = kwargs.pop("_diag", None)
        selftest = kwargs.pop("_selftest", False)
        super().__init__(*args, **kwargs)
        self.pane = Pane(self, mode=mode, diag=diag, selftest=selftest)
        self.pane.start_driver()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.N:
            self.pane.summon()
        elif symbol == pyglet.window.key.X:
            self.pane.hide()
        else:
            super().on_key_press(symbol, modifiers)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scale", type=float, default=3.0)
    parser.add_argument("--no-shader", action="store_true", help="use ffmpeg-baked frames")
    parser.add_argument("--manual", action="store_true", help="no churn; drive N/X yourself")
    parser.add_argument("--hold", action="store_true", help="single hold window (JS-animation capture)")
    parser.add_argument(
        "--mode",
        choices=["passive", "active"],
        default=os.environ.get("PANE_MODE", "active"),
        help="active: key-capable + app-activated on summon (typing+live repaint); passive: pure click-through 010 behavior",
    )
    parser.add_argument(
        "--diag",
        choices=["opaque", "whitebg"],
        help="diagnostic panel: opaque red panel | opaque white webview",
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="synthesize real keystrokes into the pane and verify the round trip",
    )
    args = parser.parse_args()

    shell = SpikeShell(
        scale=args.scale, live_key=not args.no_shader,
        _mode=args.mode, _diag=args.diag, _selftest=args.selftest,
    )
    shell.show()
    pyglet.clock.schedule_interval(shell.update, 1 / 60)
    print(f"[spike] keys: N summon pane · X hide pane · Q quit  (mode={args.mode})", flush=True)

    if not args.manual:
        seq = HOLD if args.hold else CHURN
        for delay, action in seq:
            pyglet.clock.schedule_once(
                lambda dt, a=action: (
                    shell.pane.summon() if a == "summon"
                    else shell.pane.hide() if a == "hide"
                    else pyglet.app.exit()
                ),
                delay,
            )
        print(f"[spike] {'hold' if args.hold else 'scripted churn'}: " f"{[(d, a) for d, a in seq]}", flush=True)

    pyglet.app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())