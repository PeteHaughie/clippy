---
id: 018
title: Pi community deep-dive
type: research
status: closed
assignee: wayfinder
blocked_by: []
labels: [wayfinder:research]
---

## Question

What does the Pi (earendil-works/pi-coding-agent) ecosystem already offer for the three things Clippy needs from its brain/doer, beyond what the in-repo research (pi-drive-surface.md) already documented?

1. **Sub-agent context composition** — reduced-context sub-clippies composed by Prime Clippy. The official recipe is `examples/extensions/subagent/` (scout/planner/worker chains, per-child `--model`+`--tools`+`--append-system-prompt`). Are there community extensions/packages that do this better (context scoping, parallel fan-out, chain orchestration)?
2. **Persistent memory** — Clippy is a desktop assistant that must remember across sessions. What do Pi sessions (`~/.pi/agent/sessions`, fork/clone, `switch_session`) give today, and do community extensions add memory patterns (markers, note files, memory skills, RAG)?
3. **Per-action approval on RPC** — for build-mode consent cards. Pi 0.85.1 RPC has no per-turn tool switching; the path is `extension_ui_request.confirm` (host answers). Are there community approval/guard extensions, or a documented pattern for gating mutating tools (bash/write/edit) behind host approval?

## Resolution

Findings asset: [research/pi-community-deep-dive.md](/Users/petehaughie/Projects/clippy/research/pi-community-deep-dive.md).

- **Sub-agents:** the official recipe (fresh `pi --mode json -p --no-session` + per-child `--model`/`--tools`/`--append-system-prompt`) IS the ecosystem primitive; community packages (`pi-subagents`, `@ifi/pi-extension-subagents`, `@e9n/pi-subagent`, …) are richer wrappers of the same spawn, no in-process context-scoping API. Clippy copies the recipe in Python; borrow prompt-over-stdin + child-tool-allowlist recursion-guard ideas.
- **Memory:** Pi sessions give per-project JSONL continuity, not ambient knowledge; custom entries stay out of LLM context. Skills are on-demand (not guaranteed loaded). Robust pattern = deterministic injection of `~/.clippy/memory/INDEX.md` via `--append-system-prompt` on every spawn + a `clippy-memory` skill for read/write discipline. Community (pi-memory, pi-agent-memory) confirm markdown-files + context-injection.
- **Per-action approval on RPC:** no per-turn tool switching (no `tools` on prompt/steer/follow_up, no `set_tools`). But `tool_call` fires for every tool (built-in incl.) and can block → an extension gates `bash`/`write`/`edit` without registering a tool; in RPC its `ctx.ui.confirm/select` becomes `extension_ui_request` → host replies `extension_ui_response` (fully host-driven consent loop). Fail closed when `!ctx.hasUI`. No built-in `ask_question` (vestigial help example).

## Decisions it feeds

- 015 PiBrain RPC prime (session/steering choices)
- 016 projection surface (approval cards, extension UI protocol)
- 017 skills allowlist + memory (memory pattern to adopt)

## Decisions it feeds

- 015 PiBrain RPC prime (session/steering choices)
- 016 projection surface (approval cards, extension UI protocol)
- 017 skills allowlist + memory (memory pattern to adopt)