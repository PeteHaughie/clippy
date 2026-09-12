---
id: 015
title: PiBrain RPC prime
type: prototype
status: closed
assignee: pete
blocked_by: [018]
labels: [wayfinder:prototype]
---

## Question

How does Clippy's prime conversation run on Pi as its brain/doer over RPC — one long-lived `pi --mode rpc --no-session` process, driven from Python, streaming events to the desktop surface?

## Resolution

`clippy/brain.py` — `PiBrain` (real) + `MockBrain` (offline stand-in), both conforming to a `Brain` interface with `prompt/steer/follow_up/get_state/stop`:

- Spawn `pi --mode rpc --no-session --model …`, `Popen` with strict `\n`-only JSONL framing (strip a trailing `\r`), events parsed onto a `queue.Queue` for the main-thread controller. Verified against rpc.md "Framing".
- Commands are `json.dumps(cmd)+"\n"` on stdin under a write lock; responses stream back as `response` events.
- `clippy/prime.py` — `PrimeController` consumes the queue on the clock (reuses the event→mood mapping family from `controller.py`): `message_update` thinking/text/toolcall deltas → moods+bubble, `agent_start/agent_settled` → listening/idle, `extension_ui_request` → `on_ui_request` hook, assistant `message_end` → `on_answer` hook (extracts text blocks).
- Headless selftest: `python -m clippy.brain [--mock] [--prompt …]` — verified live against the local oMLX box (round-trip → `agent_settled`) and with the mock.
- Live RPC testing this session: **RPC is NOT broken**; the earlier "hang" was my harness closing stdin (pi exits cleanly on client EOF, code 0, no stderr). With a held-open stdin the full turn streams and settles.

Model: `omlx/gemma-4-12B-it-qat-OptiQ-4bit` (same family as sub-clippies). Mock emits the same event shapes with `message_end.content` blocks so `extract_text` works identically.

## Acceptance

`python -m clippy.brain --prompt "Reply with exactly: OK"` → streams deltas and prints `SETTLED` (real); `--mock` → `SETTLED` offline.