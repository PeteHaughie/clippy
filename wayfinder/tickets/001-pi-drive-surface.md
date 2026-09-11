---
id: 001
title: Pi drive surface
type: research
status: closed
assignee: wayfinder
blocked_by: []
labels: [wayfinder:research]
---

## Question

How does Clippy drive Pi (pi.dev) programmatically as its coding doer? Specifically:

- The four invocation modes (interactive, print/JSON, RPC over stdio, SDK) — which fits a Python floating-window wrapper?
- What does the JSON event stream / RPC emit, and can it expose the agent's "current thinking and actions" live for the sub-clippy speech bubble?
- How are sub-task Pi instances spawned/isolated (the subagents extension example, tmux pattern, or a fresh `pi --mode json` process), and what lifecycle signals indicate completion?
- Install/version reality on this Mac (`pi` on PATH, Node-based, or via npm package).

Assets produced while answering (Pi docs, the subagents example, event-stream reference) get linked here. Resolution records the recommended drive surface and how it feeds the sub-clippy lifecycle ticket.

## Resolution

Findings asset: [research/pi-drive-surface.md](/Users/petehaughie/Projects/clippy/research/pi-drive-surface.md) (committed on `main`; throwaway branches merged).

**Drive surface: Pi RPC mode** — one `pi --mode rpc --no-session` process per sub-clippy. Language-agnostic JSONL protocol (split on `\n` only) with an official Python `subprocess.Popen` example in `docs/rpc.md`. Lives via `prompt` / `steer` / `follow_up` / `abort` / `get_state`; completion signalled by `agent_settled`.

**Live thinking/actions:** yes — `message_update` streams `thinking_*` and `toolcall_*` deltas; `tool_execution_start/update/end` stream every tool call with accumulated output. Exactly the "articulates its current thinking and actions" feed.

**One-shot sub-tasks:** fresh `pi --mode json -p --no-session` per task — Pi's own subagent example extension recipe; completion = process exit code + `message_end`/`tool_result_end`; failure = `exitCode != 0 || stopReason ∈ {error, aborted}`.

**SDK is Node-only** — not callable from Python; OpenClaw's `createAgentSession()` embedding is the reference for a Node bridge if full embedding is ever needed (not for the demo).

**Install:** pi is NOT installed on this Mac. Node v26.8.2 + npm 11.19.1 present; natural install `npm install -g --ignore-scripts @earendil-works/pi-coding-agent` (v0.85.1). Clippy's setup must do this.

**Risks to carry:** per-instance auth/config isolation (`PI_CODING_AGENT_DIR`/`--session-dir`), project trust (`-a/--approve` needed in non-interactive modes to load project skills), delta-only streaming (reassemble from `contentIndex`; `message_end` authoritative), version pinning.