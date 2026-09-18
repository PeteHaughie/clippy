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
| 019 | Sub-clippy composition skill | prototype | ✅ | 017 | [019-sub-clippy-composition-skill.md](tickets/019-sub-clippy-composition-skill.md) |
| 020 | Shell status-line surface (mode badge + dialog indicator) | prototype | ✅ | 016 | [020-shell-status-line-surface.md](tickets/020-shell-status-line-surface.md) |
| 021 | Unified typed event model (graph-model P1) | prototype | ✅ | 015 | [021-typed-event-model.md](tickets/021-typed-event-model.md) |
| 022 | Explicit state machines (graph-model P2) | prototype | ✅ | 021 | [022-explicit-state-machines.md](tickets/022-explicit-state-machines.md) |
| 023 | Declarative session graph (graph-model P3) | prototype | ✅ | 021, 022 | [023-declarative-session-graph.md](tickets/023-declarative-session-graph.md) |
| 024 | Roots of truth for paths/config/scratch (P4) | refactor | ✅ | 021, 022, 023 | [024-roots-of-truth.md](tickets/024-roots-of-truth.md) |
| 025 | OS-level alarms independent of Clippy | research | 👀 | — | [025-os-level-notifications.md](tickets/025-os-level-notifications.md) |
| 026 | Sub-clippys can schedule tasks (delegated scheduling) | research | ✅ | — | [026-subclippy-scheduling.md](tickets/026-subclippy-scheduling.md) |
| 027 | Generative UI surface + media primitives in the graph | task | 👀 | — | [027-generative-ui-surface.md](tickets/027-generative-ui-surface.md) |

**Frontier (takeable next):** the control plane is now a typed graph (`clippy/model.py` + `session.py`). Remaining candidates: **live full-loop acceptance run** (needs a real Aqua session — `--brain` pane typing, Tab→build approval card, `/delegate` sub-clippy), graph-refactor leftover **P5** typed `Task` node, and **RAG memory** if markdown memory proves thin.