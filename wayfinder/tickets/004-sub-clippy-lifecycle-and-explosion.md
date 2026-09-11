---
id: 004
title: Sub-clippy lifecycle and explosion
type: prototype
status: closed
assignee: pete
blocked_by: [003, 007, 008]
resolution: Second pyglet window at a distinct position, driven by a main-thread controller that consumes a Pi `--mode json` event stream. Verified with the real sub-agent against the local oMLX box.
labels: [wayfinder:prototype]
---

## Question

How does a subagentic call summon a new Clippy instance, show its thinking, and explode on completion?

Prototype the lifecycle: Clippy (prime) delegates → a new Clippy instance is summoned as a separate Pi instance → its live thinking/action events stream into the speech bubble + avatar states → on task completion the avatar *explodes dramatically* with the explosion gif → window dismissed.

- Sizing one subagent spawn (rules/skill tool that triggers it, the prompt handed to Pi, where the subtask works).
- Feeding Clippy's bubble from the Pi event stream (link to Pi drive surface ticket's answer).
- Proving the explosion: the gif asset is supplied later by Pete; the prototype stubs it and the ticket notes it waits for the real asset.
- No CLI scaffolding/install to judge yet — rough and dirty is fine.

Links the prototype as an asset. Resolution records the lifecycle shape that works.

## Resolution

Lifecycle shape that works (prototyped + verified live):

1. **Prime** is one `ClippyShell` window at a fixed position (`60,420`); **sub-clippy** is a *second* `ClippyShell` window at a distinct position (`560,420`), same pyglet process (event loop), never overlapping the prime.
2. Delegation is triggered by the **D** key on the prime window or the `--delegate "<task>"` CLI flag; only one sub-clippy is allowed at a time.
3. A sub-agent is spawned as a **separate Pi process**: `pi --mode json -p --no-session --name subclippy-<ts> --model omlx/… "<task>"` running in a fresh scratch dir `~/.clippy/scratch/<timestamp>/`. Output is JSONL read by a background thread onto a `queue.Queue`.
4. A `SubClippyController` polled by the clock loop on the main thread maps events to the mood/bubble API from ticket 009: `thinking_delta`/`text_delta` → `thinking` + living bubble text, `tool_execution_start` → `working` + hint from the tool name, done → `idle`→`celebrate`, failure → `alert` + error bubble.
5. On success (exit code 0, stop reason not `error`/`aborted`) → celebrate → trigger the explosion → when it finishes, wait 1s → `shell.dismiss()` (hide + close). Prime stays up. Failure windows auto-close after 4s.
6. Models: `omlx/Qwen3.8-27B-MLX-4bit` streams `reasoning_content` (rich thinking bubble); `omlx/gemma-4-12B-it-qat-OptiQ-4bit` is the cheap default (content stream only). Both registered in `~/.pi/agent/models.json` with `compat.supportsDeveloperRole/supportsReasoningEffort=false`.

Verified: two windows coexist at distinct coordinates; real Pi subagent on the local oMLX box ran, streamed the thinking bubble, exploded and dismissed at ~32s while the prime stayed alive; mock fallback covers an offline box. Two pyglet 2.x traps fixed along the way (GL_QUADS removed; `set_uniform` replaced by `program["u"] = …`, shader uniform assignment is `vec3` not `vec4`). A `--delegate --real` run is the living demo: `main.py --delegate "<task>"`.