---
id: 006
title: One-shot demo scenario
type: grilling
status: closed
assignee: pete
blocked_by: []
resolution: The demo script is locked — one command, no interactivity. `python main.py --delegate` (or with an explicit task) runs the whole alive-loop: prime Clippy floats, a sub-clippy is summoned, its thinking streams in the bubble, it works with tool hints, celebrates, explodes, then dismisses while the prime stays up. Default task is a hello.py create+run, working in a fresh sandboxed scratch dir, auto-falling back to a deterministic mock when the oMLX box is offline.
labels: [wayfinder:grilling]
---

## Question

What is the exact demo script that makes the thing feel alive — one Clippy, one subagent spawn, thinking in the bubble, explosion on completion?

Grill the human on: the concrete task the sub-clippy performs (something quick, visible, satisfying), where it happens (sandboxed at first — so maybe a hello-world repo or a scratch dir), what "success" looks like on screen, and where the real explosion gif comes in. This is the acceptance test for the whole demo; its shape should inform the other tickets.

## Resolution: the demo script (acceptance test)

All four grilling questions answered to the current built behavior — the demo rides the 004 beaten path, no new machinery.

**The one command:** `python main.py --delegate` (optional task argument; omitted = default). Add `--real` to force the real Pi sub-agent, otherwise auto-mock-fallback when the oMLX box is offline. The D key was removed from the shell — the demo is deliberately non-interactive.

## Projection acceptance (post-015/016/017)

The prime + pane scenario is now the companion acceptance: `python main.py --brain [prompt]` starts a sandboxed Pi RPC brain (`--tools read,grep,find,ls`), summons the w1c pane (N summon / X hide), streams the answer into the bubble + pane, Tab re-spawns to build mode (full tools + `clippy-gate.ts`) where a mutating write asks a w1c confirm card (Allow writes / Deny blocks), skills are allowlisted (`--no-skills --skill …` incl. the always-on memory skill), and memory INDEX is injected via `--append-system-prompt`. The `--delegate` sub-clippy explosion beat is unchanged and still passes.

**The one command:** `python main.py --delegate` (optional task argument; omitted = default). Add `--real` to force the real Pi sub-agent, otherwise auto-mock-fallback when the oMLX box is offline. The D key was removed from the shell — the demo is deliberately non-interactive.

**The task:** create `hello.py` that prints "Hello from sub-clippy!", run it, report the output.

**Where it works:** a fresh sandboxed scratch dir `~/.clippy/scratch/<timestamp>/`.

**What "alive" looks like on screen (the beats):**
1. Prime Clippy floats at `(60,420)`.
2. Sub-clippy appears at `(560,420)` — a second, non-overlapping window.
3. Its bubble streams thinking deltas, then shows "working… (<tool>)" during bash/write, then the tool result text.
4. On success: `idle` → `celebrate`, bubble "Task complete!", then the full-screen explosion (real green-screen gif, GLSL keyed path).
5. ~1s after the blast the sub window dismisses; prime stays up. On failure: `alert` mood + error bubble, window auto-closes after 4s.

**Success = exactly one sub spawn, thinking in the bubble, visible explosion, sub dismissed, prime alive.** Rehearsed end-to-end with the real oMLX box (moods thinking/working/celebrate seen, explosion triggered, window closed, `hello.py` artifact in the scratch dir) and headlessly with the deterministic mock (PASS).

**Tuning during the grilling session:** the bare-shader explosion project was completely invisible (raw pixel coords fed as clip-space → clipped off-screen) until the vertex shader adopted pyglet's `WindowBlock` projection; the chroma-key alpha was also inverted (kept green opaque, made fire transparent) and the baked-sprite path never advanced frames. All fixed + verified in `clippy/explosion.py` (commit `ac18138`).