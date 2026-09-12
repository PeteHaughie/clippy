# Wayfinder issue index

Map: [Clippy: Clippy as an interface to an LLM endpoint](map.md) (label `wayfinder:map`)

Legend: ✅ closed · ⬜ open but blocked · 👀 open/unblocked/unclaimed (takeable frontier) · 🅿️ open/decision-resolved/implement-progress parked

| id | title | type | status | blocked by | in ticket |
|----|-------|------|--------|------------|-----------|
| 001 | Pi drive surface | research | ✅ | — | [001-pi-drive-surface.md](tickets/001-pi-drive-surface.md) |
| 002 | Clippy's own chat loop and skill-as-tool | research | ✅ | — | [002-clippy-chat-loop-and-skill-as-tool.md](tickets/002-clippy-chat-loop-and-skill-as-tool.md) |
| 003 | Floating window with animated avatar | prototype | ✅ | — | [003-floating-window-with-animated-avatar.md](tickets/003-floating-window-with-animated-avatar.md) |
| 004 | Sub-clippy lifecycle and explosion | prototype | ✅ | — | [004-sub-clippy-lifecycle-and-explosion.md](tickets/004-sub-clippy-lifecycle-and-explosion.md) |
| 005 | Sandbox by default, build mode on toggle | grilling | ✅ | — | [005-sandbox-by-default-build-mode-on-toggle.md](tickets/005-sandbox-by-default-build-mode-on-toggle.md) |
| 006 | One-shot demo scenario | grilling | ✅ | — | [006-one-shot-demo-scenario.md](tickets/006-one-shot-demo-scenario.md) |
| 007 | Install Pi locally | task | ✅ | — | [007-install-pi-locally.md](tickets/007-install-pi-locally.md) |
| 008 | Demo provider and model | grilling | ✅ | — | [008-demo-provider-and-model.md](tickets/008-demo-provider-and-model.md) |
| 009 | Contextual animation moods + agent API | prototype | ✅ | — | [009-contextual-animation-moods-and-agent-api.md](tickets/009-contextual-animation-moods-and-agent-api.md) |
| 010 | HTML/CSS/JS pane spike (95CSS) | prototype | ✅ | — | [010-html-css-js-pane-spike.md](tickets/010-html-css-js-pane-spike.md) |
| 011 | Interactive pane: JS↔Python bridge | prototype | ✅ | — | [011-interactive-pane-bridge.md](tickets/011-interactive-pane-bridge.md) |
| 012 | w1c knowledge graph (+ resolver port) | grilling | ✅ | — (superseded by 016) | [012-95css-styled-knowledge-graph.md](tickets/012-95css-styled-knowledge-graph.md) |
| 013 | Ephemeral card pipeline in the pane | prototype | ✅ | — (delivered by 016) | [013-ephemeral-card-pipeline.md](tickets/013-ephemeral-card-pipeline.md) |
| 014 | w1c pane spike (web components, windows-95 theme) | prototype | ✅ | — | [014-w1c-pane-spike.md](tickets/014-w1c-pane-spike.md) |
| 015 | PiBrain RPC prime | prototype | ✅ | 018 | [015-pibrain-rpc-prime.md](tickets/015-pibrain-rpc-prime.md) |
| 016 | Projection surface — approval cards + dialog surface | prototype | ✅ | 015 | [016-projection-surface-approval-cards.md](tickets/016-projection-surface-approval-cards.md) |
| 017 | Skills allowlist, sandbox toggle, persistent memory | prototype | ✅ | 015, 016 | [017-skills-allowlist-sandbox-memory.md](tickets/017-skills-allowlist-sandbox-memory.md) |
| 018 | Pi community deep-dive | research | ✅ | — | [018-pi-community-deep-dive.md](tickets/018-pi-community-deep-dive.md) |

**Frontier (takeable next):** the 018/015/016/017 arc delivered the projection architecture. Next candidates: a Clippy-owned sub-clippy **composition skill** (Prime prompts `/skill:…` to spawn a pared-down child), RAG memory if markdown memory proves thin, and wiring the mode badge/cards into the shell status line.