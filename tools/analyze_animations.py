#!/usr/bin/env python3
"""Quantify every animation in assets/clippy/agent.json from the sprite sheet.

Not a vision model — this measures *movement* objectively: for each animation it
crops each frame's cell from map.png and computes the mean absolute pixel change
between consecutive frames. Lower mean movement = calmer. This is the data for
picking calm idle states (e.g. RestPose = 0, IdleSideToSide ~6.7) and for
finessing animations later.

Read-only: loads agent.json + map.png via pyglet, prints a report. No writes,
no new dependencies.

Usage:
  python tools/analyze_animations.py                 # full ranking, calmest -> busiest
  python tools/analyze_animations.py --anim IdleSnooze  # per-frame detail + holds
"""

import argparse
import json
from pathlib import Path

import pyglet

ROOT = Path(__file__).resolve().parent.parent
AGENT = ROOT / "assets" / "clippy" / "agent.json"
MAP = ROOT / "assets" / "clippy" / "map.png"


def _load_sheet():
    data = json.loads(AGENT.read_text())
    img = pyglet.image.load(str(MAP)).get_image_data()
    pixels = memoryview(img.get_data("RGBA", img.width * 4))
    fw, fh = data["framesize"]

    def region(x, y):
        out = []
        for row in range(y, y + fh):
            base = (row * img.width + x) * 4
            out.append(bytes(pixels[base : base + fw * 4]))
        return b"".join(out)

    return data, region


def _diff(a, b):
    sa, sb = memoryview(a), memoryview(b)
    n = len(sa)
    return sum(abs(sa[i] - sb[i]) for i in range(0, n, 4)) / (n // 4)


def _metrics(anim, region):
    frames = anim["frames"]
    prev = None
    moves = []
    for fr in frames:
        x, y = (fr.get("images") or [[0, 0]])[0]
        cur = region(x, y)
        if prev is not None:
            moves.append(_diff(prev, cur))
        prev = cur
    return moves


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--anim", help="show per-frame detail for one animation")
    args = ap.parse_args()

    data, region = _load_sheet()
    animations = data["animations"]

    if args.anim:
        anim = animations.get(args.anim)
        if anim is None:
            raise SystemExit(f"unknown animation {args.anim!r}")
        moves = _metrics(anim, region)
        total = sum(f["duration"] for f in anim["frames"]) / 1000.0
        print(f"{args.anim}: {len(anim['frames'])} frames, {total:.1f}s, "
              f"{len(moves)} transitions")
        print(f"{'transition':>11s} {'movement':>9s} {'frame_ms':>9s}")
        for i, fr in enumerate(anim["frames"]):
            mv = moves[i - 1] if i > 0 and i - 1 < len(moves) else 0.0
            hold = fr["duration"]
            flag = "  <- hold" if hold > 500 or (i > 0 and mv < 0.5) else ""
            print(f"{i:>11d} {mv:9.1f} {hold:9d}{flag}")
        return

    rows = []
    for name, anim in animations.items():
        moves = _metrics(anim, region)
        if not moves:
            continue
        mean = sum(moves) / len(moves)
        rows.append((mean, max(moves), name, len(anim["frames"]),
                     sum(f["duration"] for f in anim["frames"]) / 1000.0))
    rows.sort(key=lambda r: r[0])
    print(f"{'animation':20s} {'n':>4s} {'dur_s':>7s} {'mean_mv':>8s} {'max_mv':>8s}")
    for mean, mx, name, n, dur in rows:
        print(f"{name:20s} {n:4d} {dur:7.1f} {mean:8.1f} {mx:8.1f}")


if __name__ == "__main__":
    main()