---
id: 001
title: Pi drive surface
type: research
status: open
assignee:
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