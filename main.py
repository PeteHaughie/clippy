"""Spike entry point for ticket 003: floating transparent Clippy window.

Controls:
  T  toggle Thinking / RestPose animation
  Space  Wave
  E  trigger the explosion
  N  summon the chat pane (--brain mode)      X  hide the pane
  Tab  toggle sandbox ↔ build (--brain mode)
  Q  quit

Clippy's window is draggable (grab any part of it and move). In the chat
pane, `/move <spot>` / `/move <x> <y>` move Clippy, `/where` reports his
position, and the brain can move him too via a [CLIPPY::MOVE] directive.

Flags:
  --mood <name> [--hint <hint>]  drive a single mood once, then quit
  --moodcycle                    play every mood in sequence, then quit
  --delegate [task]              summon a sub-clippy (optional task; uses the
                                 default when omitted)
  --brain [prompt]               start the prime Pi brain (RPC) + chat pane;
                                 optional opening prompt (greeting by default)
  --real                         force the real Pi sub-agent (oMLX) instead of
                                 auto-falling back to the mock
  --model <omlx/model>           which oMLX model the real sub-agent uses
  --vsync                        force GLX buffer-swap vsync on (Linux defaults
                                 it off to avoid XWayland/Mutter overlay flicker)

On Linux, ``--brain`` also forces Mesa's software GL (llvmpipe) for the avatar:
the hardware GLX path flickers under XWayland while the WebKitGTK pane is
active. Set ``LIBGL_ALWAYS_SOFTWARE=0`` to keep hardware GL.

The app itself is a projection of the session graph (clippy/session.py /
clippy/model.py): the control plane is declared as typed nodes/edges/
constraints, and this entry point just constructs a :class:`Session`.
"""

import argparse
import os
import sys

# Import the pyobjc runtime BEFORE pyglet so both ObjC bridges share one
# runtime cleanly (proven harness in w1c_pane_spike.py) — macOS only. On other
# platforms pyglet is enough; the pane module picks its own backend (see
# clippy/pane.py).
if sys.platform == "darwin":
    import objc  # noqa: F401  (ensures the pyobjc runtime is up first)

# Force the GTK chat pane onto the X11 (XWayland) backend on Linux so window
# move()/resize() work for anchoring it beside the avatar; pyglet already runs
# under XWayland here. Must happen before the pane module initialises GTK.
if sys.platform != "darwin":
    os.environ.setdefault("GDK_BACKEND", "x11")

# Under XWayland/Mesa (radeonsi) the avatar's hardware GLX rendering flickers
# while the WebKitGTK pane is active — two GL clients on the same GPU. The pane
# is CPU-rendered and the avatar is tiny, so force Mesa's software rasteriser
# (llvmpipe) for the --brain path; it is stable and cheap here. Must be set
# before pyglet loads the GL driver. Override with LIBGL_ALWAYS_SOFTWARE=0 to
# keep hardware GL.
if sys.platform.startswith("linux") and any(
    a == "--brain" or a.startswith("--brain=") for a in sys.argv
):
    os.environ.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")

import pyglet

from clippy.moods import Moods
from clippy.session import Session
from clippy.shell import ClippyShell
from clippy.subagent import DEFAULT_TASK

ONE_SHOT_HOLD = 1.5  # seconds after a one-shot mood before moving on

PRIME_POS = (60, 420)

#: GTK/WebKit main-context pump interval (ms) in the integrated loop. Kept at
#: ~60 fps so pane input stays responsive.
PUMP_MS = 16


def run_integrated():
    """Run the avatar on pyglet's own event loop while pumping GTK.

    pyglet's loop (``pyglet.app.run``) is the stable render path: the non-brain
    mode uses it and the always-on-top transparent overlay does not flicker. The
    earlier design let GTK own the loop and pumped pyglet from a GLib timer;
    under XWayland/Mutter that made the overlay flicker and eventually vanish,
    even though the avatar kept drawing. So here pyglet owns the loop and a
    clock callback drains the GTK/WebKit main context (what WebKitGTK needs to
    keep working). The loop ends when pyglet wants out (Q, or the last Clippy
    window closing).
    """
    from gi.repository import GLib

    ctx = GLib.MainContext.default()

    def _pump_gtk(_dt):
        # Drain pending GTK/WebKit sources without blocking. Capped so a chatty
        # source can never starve the avatar's frame.
        for _ in range(64):
            if not ctx.pending():
                break
            ctx.iteration(False)

    pyglet.clock.schedule_interval(_pump_gtk, PUMP_MS / 1000.0)
    print("[clippy] running pyglet loop + GTK main-context pump", flush=True)
    pyglet.app.run(interval=1 / 60)


def duration_of(avatar, name: str) -> float:
    anim = avatar.animations[name]
    return sum(fr["duration"] for fr in anim["frames"]) / 1000.0


class PrimeShell(ClippyShell):
    """ClippyShell with N/X (pane) and Tab (sandbox↔build) for --brain mode."""

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.N:
            if self.pane is not None:
                self.pane.summon()
        elif symbol == pyglet.window.key.X:
            if self.pane is not None:
                self.pane.hide()
        elif symbol == pyglet.window.key.TAB:
            if self.session is not None:
                self.session.toggle()
        else:
            super().on_key_press(symbol, modifiers)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", type=float, default=1.5)
    parser.add_argument("--no-shader", action="store_true", help="use ffmpeg-baked frames")
    parser.add_argument("--mood", help="play one mood then quit")
    parser.add_argument("--hint", help="activity hint for --mood")
    parser.add_argument("--moodcycle", action="store_true", help="play every mood in sequence then quit")
    parser.add_argument("--delegate", nargs="?", const=DEFAULT_TASK, help="summon a sub-clippy for this task at startup (default task when omitted)")
    parser.add_argument("--brain", nargs="?", const="", help="start the prime Pi brain (RPC) and give it this opening prompt (default greeting when omitted)")
    parser.add_argument("--real", action="store_true", help="force the real Pi sub-agent")
    parser.add_argument(
        "--model",
        default=None,
        help="model for the real Pi brain/sub-agent (default: config 'model', else built-in)",
    )
    parser.add_argument(
        "--vsync",
        action="store_true",
        help="force GLX buffer-swap vsync on (default: off on Linux, which "
        "avoids XWayland/Mutter transparent-overlay flicker)",
    )
    args = parser.parse_args()

    # Must be set before any window/context is created. On XWayland a vsync'd
    # GLX swap can stall or present stale buffers on a transparent overlay,
    # which shows up as the whole avatar blinking; so Linux defaults to vsync
    # off (tearing is a non-issue for this low-rate, mostly-static sprite).
    # Other platforms keep pyglet's default (on) unless --vsync is given.
    if args.vsync:
        pyglet.options["vsync"] = True
    elif sys.platform.startswith("linux"):
        pyglet.options["vsync"] = False

    shell = PrimeShell(scale=args.scale, live_key=not args.no_shader, position=PRIME_POS)
    shell.show()
    shell.pane = None
    shell.session = None
    pyglet.clock.schedule_interval(shell.update, 1 / 60)

    session = None
    if args.delegate:
        session = Session(shell, model=args.model, real=args.real)
        shell.session = session
        session.delegate(args.delegate)

    if args.brain is not None:
        session = Session(shell, model=args.model, real=args.real)
        shell.session = session
        opening = args.brain or (
            "Give the user a one-line friendly greeting and say you're ready."
        )
        session.prompt(opening)
        print(f"[clippy] prime opening: {opening!r}")
        pyglet.clock.schedule_once(lambda dt: session.pane.summon(), 0.9)

    moods = shell.avatar.moods

    if args.moodcycle:
        run_cycle(shell, moods)
    elif args.mood:
        hint = args.hint or ("build" if args.mood == "working" else None)
        if not shell.express(args.mood, hint=hint):
            print(f"[clippy] mood '{args.mood}' ignored (rule) or unknown")
        resolved = shell.avatar.moods.resolve(args.mood, hint)
        hold = 0
        if not moods.is_continuous(args.mood) and resolved:
            hold = duration_of(shell.avatar, resolved) + ONE_SHOT_HOLD
        if hold:
            pyglet.clock.schedule_once(lambda dt: pyglet.app.exit(), hold)
    if (
        args.brain is not None
        and session is not None
        and getattr(session.pane, "wants_integrated_loop", False)
    ):
        run_integrated()
    else:
        pyglet.app.run()
    if session is not None:
        session.brain.stop()
    return 0


def run_cycle(shell: ClippyShell, moods: Moods):
    seq = [(m, None) for m in moods.available_moods()]
    seq[seq.index(("working", None))] = ("working", "build")
    holds = []
    for (mood, hint) in seq:
        resolved = moods.resolve(mood, hint)
        if moods.is_continuous(mood):
            holds.append(3.5)
        elif resolved:
            holds.append(duration_of(shell.avatar, resolved) + ONE_SHOT_HOLD)
        else:
            holds.append(1.0)
    total = 0.0
    for i, ((mood, hint), hold) in enumerate(zip(seq, holds)):
        pyglet.clock.schedule_once(lambda dt, m=mood, h=hint: shell.express(m, hint=h), total)
        total += hold
    pyglet.clock.schedule_once(lambda dt: pyglet.app.exit(), total + 0.5)
    print(f"[clippy] moodcycle: {', '.join(m for m, _ in seq)}")
    for (mood, hint), hold in zip(seq, holds):
        print(f"  {mood:10s} hint={hint or '-':<10} hold={hold:5.1f}s")


if __name__ == "__main__":
    sys.exit(main())