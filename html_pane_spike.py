"""Stage-1 spike: prove HTML/CSS/JS renders in a Python process next to Clippy.

A transparent, floating, click-through NSPanel hosts a WKWebView showing the
95CSS-styled mock chat pane (assets/pane/spike_pane.html). Purely a rendering
proof -- no chat loop, no spec cards, no tools/skills.

Controls (on the Clippy window):
  N  summon the pane        X  hide the pane
  Q  quit                   P/T/Space  inherited demo keys

Run modes:
  default      scripted summon->hide->summon->hide churn, then clean exit
  --manual     no churn; you drive N/X/Q
"""

import argparse
import sys
from pathlib import Path

# Import pyobjc BEFORE pyglet so both ObjC bridges share one runtime cleanly.
import objc  # noqa: F401  (ensures the pyobjc runtime is up first)
from AppKit import (
    NSBackingStoreBuffered,
    NSColor,
    NSFloatingWindowLevel,
    NSPanel,
    NSScreen,
    NSWindowStyleMaskBorderless,
    NSWindowStyleMaskNonactivatingPanel,
)
from Foundation import NSMakeRect, NSURL
from WebKit import WKWebView

import pyglet

from clippy.shell import ClippyShell

REPO_ROOT = Path(__file__).resolve().parent
PANE_HTML = REPO_ROOT / "assets" / "pane" / "spike_pane.html"
ASSETS_DIR = REPO_ROOT / "assets"

PANE_W, PANE_H = 340, 460  # points; Retina scales pixels x2 for capture

CHURN = [(1.2, "summon"), (4.5, "hide"), (8.0, "summon"), (11.5, "hide"), (12.5, "quit")]
# --hold: single summon window long enough to capture the JS animation.
HOLD = [(1.2, "summon"), (6.0, "hide"), (7.0, "quit")]


def _nonactivating_mask():
    return NSWindowStyleMaskBorderless | NSWindowStyleMaskNonactivatingPanel


class Pane:
    """Transparent floating WKWebView panel loading the 95CSS spike html."""

    def __init__(self, shell: ClippyShell, diag: str | None = None):
        self.shell = shell
        self.diag = diag
        self.panel = None
        self.webview = None

    def create(self):
        opaque = self.diag in ("opaque", "whitebg")
        panel_bg = NSColor.redColor() if self.diag == "opaque" else NSColor.clearColor()
        transparent_bg = not (self.diag == "whitebg")
        frame = self._frame()
        style = _nonactivating_mask()
        panel = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(*frame), style, NSBackingStoreBuffered, False
        )
        panel.setFloatingPanel_(True)
        panel.setOpaque_(opaque)
        panel.setBackgroundColor_(panel_bg)
        panel.setHasShadow_(False)
        panel.setIgnoresMouseEvents_(True)
        panel.setHidesOnDeactivate_(False)
        panel.setLevel_(NSFloatingWindowLevel)
        panel.setReleasedWhenClosed_(False)

        webview = WKWebView.alloc().initWithFrame_(NSMakeRect(0, 0, PANE_W, PANE_H))
        if transparent_bg:
            webview.setValue_forKey_(False, "drawsBackground")
        webview.setWantsLayer_(True)

        panel.setContentView_(webview)

        html_url = NSURL.fileURLWithPath_(str(PANE_HTML))
        base_url = NSURL.fileURLWithPath_(str(ASSETS_DIR))
        webview.loadFileURL_allowingReadAccessToURL_(html_url, base_url)

        self.panel = panel
        self.webview = webview
        x, y = int(frame[0]), int(frame[1])
        print(
            f"[pane] created {PANE_W}x{PANE_H}pt at bottom-left ({x},{y}) "
            f"(sprite top {self._sprite_top():.0f}pt)", flush=True
        )
        print(f"[pane] panel.frame() -> {panel.frame()}", flush=True)
        sf = NSScreen.mainScreen().frame()
        print(f"[pane] main screen {sf.size.width:.0f}x{sf.size.height:.0f}pt", flush=True)

    def start_driver(self):
        """Drive the pane's progress from Python (pyglet clock) via
        evaluateJavaScript -- deterministic, immune to WebKit background-timer
        throttling, and a taste of the stage-2 JS<->Python bridge."""
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
        self.webview.evaluateJavaScript_completionHandler_(
            f"window.__setProgress({v});", None
        )

    def _sprite_top(self):
        loc = self.shell.get_location()
        pad = 20
        return loc[1] + pad + self.shell.avatar.frame_h * self.shell.avatar.scale

    def _frame(self):
        loc = self.shell.get_location()
        # Bottom 12% of the pane is transparent so the avatar shows through.
        rim = PANE_H * 0.12
        sprite_top = self._sprite_top()
        x = loc[0] + 24
        y = max(20, int(sprite_top - rim * 0.5))
        return (x, y, PANE_W, PANE_H)

    def summon(self):
        if self.panel is None:
            self.create()
        self.panel.orderOut_(None)
        self.panel.orderFrontRegardless()
        print("[pane] summoned", flush=True)

    def hide(self):
        if self.panel is not None:
            self.panel.orderOut_(None)
            print("[pane] hidden", flush=True)


class SpikeShell(ClippyShell):
    """ClippyShell with N (summon pane) and X (hide pane) added."""

    def __init__(self, *args, **kwargs):
        diag = kwargs.pop("_diag", None)
        super().__init__(*args, **kwargs)
        self.pane = Pane(self, diag=diag)
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
        "--diag",
        choices=["opaque", "whitebg"],
        help="diagnostic panel: opaque red panel | opaque white webview",
    )
    args = parser.parse_args()

    shell = SpikeShell(scale=args.scale, live_key=not args.no_shader, _diag=args.diag)
    shell.show()
    pyglet.clock.schedule_interval(shell.update, 1 / 60)
    print("[spike] keys: N summon pane · X hide pane · Q quit", flush=True)

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