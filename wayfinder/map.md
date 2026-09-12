---
title: Clippy — a working local demo
labels: [wayfinder:map]
---

# Clippy: a desktop projection over Pi

## Destination

A working local demo on this Mac: **Clippy is a projection into userland from the system** — a floating always-on-top desktop window (animated avatar + w1c chat pane) wrapped around **Pi** (pi.dev) as the universal brain/doer. Pi owns tools, skills (agent-skill `SKILL.md`, allowlisted), providers, sessions, and approvals. Clippy owns the avatar, the pane, the dialog/card surface (Pi's `extension_ui_request` → w1c cards), persistent memory wrangling, and sub-clippy orchestration. Sandboxed by default; a Tab toggle re-spawns the brain in build mode where mutating tools ask for consent through approval cards. The demo is "alive" when: type in the pane → Pi answers with its thinking in the bubble → a sandboxed write is blocked (or, in build mode, approved via a card) → skills/memory are in play → a sub-clippy spawn still thinks in its bubble and explodes on completion.

## Notes

- **Domain:** a desktop companion/animation experiment; Python all the way down (per Pete). UI shell = **pyglet 2.x** window + **pyobjc** NSWindow tweaks + a transparent WKWebView **NSPanel** pane (`clippy/pane.py`, the 010/011/014 proven harness). The brain = **Pi over RPC** (`pi --mode rpc --no-session`, `clippy/brain.py`): strict JSONL in/out, `prompt`/`steer`/`follow_up`, event stream → moods/bubble, `extension_ui_request` → cards. No OpenAI-SDK chat loop — Pi is the endpoint (research 002's own-loop plan was superseded by the projection pivot).
- **Pi is the doer AND the brain** — one long-lived RPC process for the prime conversation; one-shot `--mode json` children for fire-and-forget sub-clippies. Pi 0.85.1 installed at `/opt/homebrew/bin/pi`; local oMLX box is the provider (`~/.pi/agent/models.json`).
- **Skills to consult:** `wayfinder` (this), `research`. HITL grilling is worked directly with the human.
- **Standing preferences:** sandboxed by default; build mode = per-conversation toggle (Tab), enforced at spawn (Pi sets tools at spawn; re-spawn on toggle) + approval cards in build mode; skills via an editable allowlist; persistent memory injected deterministically (`--append-system-prompt INDEX.md`), never via a skill alone; subagent = separate Pi instance; explosion gif in `assets/`.
- **Explosion gif:** `assets/Green_Screen_Explosion-ezgif.com-crop.gif` — 180×180, 37 frames @10fps, chroma-keyed (ffmpeg-baked safe path + live GLSL shader).
- **Spritesheet:** classic Microsoft Agent Clippy from `pi0/clippy` (jsDelivr mirror), `map.png`, 41 animations. Proseance: Microsoft IP, fine for local demo, don't ship commercially.

## Decisions so far

<!-- the index: one line per closed ticket, enough to judge relevance, then zoom the link for the detail the ticket holds -->

- [Pi drive surface](tickets/001-pi-drive-surface.md): Pi's four modes; **RPC** = the designed embed surface for a Python host (Popen + `\n`-only JSONL, `prompt`/`steer`/`follow_up`/`abort`, `extension_ui_request`); `--mode json -p --no-session` = the one-shot sub-task recipe.
- [Pi community deep-dive](tickets/018-pi-community-deep-dive.md): the official subagent recipe IS the ecosystem primitive (no in-process context-scoping API); memory = markdown files + **deterministic context injection** (append-system-prompt/AGENTS.md — a skill alone is on-demand); **no per-turn tool switching** on RPC, but `tool_call` (built-ins incl.) can block → an extension + `ctx.ui.confirm` = host-driven consent loop; no built-in `ask_question` (vestigial example).
- [PiBrain RPC prime](tickets/015-pibrain-rpc-prime.md): `clippy/brain.py` (`PiBrain` real + `MockBrain` offline) + `clippy/prime.py` (`PrimeController`: event→mood/bubble mapping, `on_answer`/`on_ui_request` hooks). Verified live (RPC round-trip → `agent_settled`) + mock. RPC "hang" earlier was my harness closing stdin (pi exits cleanly on client EOF).
- [Projection surface / approval cards](tickets/016-projection-surface-approval-cards.md): `clippy/pane.py` (w1c WKWebView pane, chat + dialog surface), `clippy/extensions/clippy-gate.ts` (build-mode consent gate, fail-closed), `__uiRequest` dialog cards. **Verified live:** write → `extension_ui_request confirm` → Allow writes file / Deny blocks (isError, no file).
- [Skills allowlist, sandbox, memory](tickets/017-skills-allowlist-sandbox-memory.md): editable `skills.allow` (`--no-skills --skill …`), sandbox=`--tools read,grep,find,ls`, build=full+gated, Tab re-spawns; memory = `~/.clippy/memory/INDEX.md` injected via `--append-system-prompt` (Pi confirmed it sees it) + `memory` skill.
- [Sub-clippy composition skill](tickets/019-sub-clippy-composition-skill.md): `clippy/skills/sub-clippy` (always-on) teaches the prime to delegate research legwork; **`/delegate <task>`** chat command (host-intercepted, deterministic) + autonomous `[CLIPPY::DELEGATE]…[CLIPPY::END]` directive; `parse_delegation`; children are sandboxed read/search-only; reports relay back through the prime. (Mechanism proven live; gemma-12B won't reliably invoke the skill on its own → the command is the demo path.)
- [Shell status-line surface](tickets/020-shell-status-line-surface.md): mode badge (🛡/🔨) + `dialog:waiting` segment in the shell status line, fed from `PrimeSession`/`PrimeController`.
- **Graph-model refactor (021–023):** the control plane is a typed graph. [Typed event model](tickets/021-typed-event-model.md) (`clippy/model.py` `Ev` catalog + `clippy/events.py` `normalize` + `AgentEventRouter` — one definition of truth for both wire shapes); [explicit state machines](tickets/022-explicit-state-machines.md) (`clippy/statemachine.py` runtime over graph-declared `WORKER_LIFECYCLE`/`PRIME_CONVERSATION`/MoodSM configs); [declarative session graph](tickets/023-declarative-session-graph.md) (`clippy/session.py::Session` wires callbacks as a projection of `build_session_graph()`; main.py is just an entry point). Renderers (avatar playback, explosion, pane JS) stay leaf projections.
- [Roots of truth for paths/config/scratch](tickets/024-roots-of-truth.md): `clippy/roots.py` (single `CLIPPY_ROOT`/`SCRATCH_ROOT`/`MEMORY_*`/`USER_CONFIG`/`SKILLS_DIR`/`make_scratch_dir`, opt-in `CLIPPY_HOME` for hermetic checks) + `clippy/config.py` (the one `load_config`/`deep_merge`); duplicated defs removed from subagent/brain/memory/moods; dead `llmconfig.py` + `secrets.local.json.example` + `"llm"` block deleted. Verified headless/hermetic.
- [Floating window with animated avatar](tickets/003-floating-window-with-animated-avatar.md): pyglet 2.1 + pyobjc, `WINDOW_STYLE_OVERLAY` transparent always-on-top click-through; shell↔brain = the brain queue (sockets not needed).
- [Contextual animation moods + agent API](tickets/009-contextual-animation-moods-and-agent-api.md): 8 semantic moods + hints; controller-driven; shipped defaults in `clippy/config.json`, user override `~/.clippy/config.json`.
- [Sub-clippy lifecycle and explosion](tickets/004-sub-clippy-lifecycle-and-explosion.md): second `ClippyShell` per delegation; `clippy/subagent.py` (`PiSubAgent` `--mode json` + mock) + `clippy/controller.py` maps events → moods → celebrate → explode → dismiss.
- [Demo provider and model](tickets/008-demo-provider-and-model.md): BYOK OpenAI-compatible endpoint was for Clippy's own loop — **superseded**: Pi owns the provider now (omlx). `clippy/llmconfig.py` kept only as reference; not used by the brain (deleted in 024).
- [One-shot demo scenario](tickets/006-one-shot-demo-scenario.md): `python main.py --delegate` is the sub-clippy acceptance; `main.py --brain [prompt]` is the new prime+pane acceptance.
- [HTML/CSS/JS pane spike](tickets/010-html-css-js-pane-spike.md) + [Interactive pane bridge](tickets/011-interactive-pane-bridge.md) + [w1c pane spike](tickets/014-w1c-pane-spike.md): the pane harness this architecture rides.
- [Sandbox by default, build mode on toggle](tickets/005-sandbox-by-default-build-mode-on-toggle.md): grilling locked the principles; implemented under the RPC reality (tools at spawn, re-spawn on toggle, approval cards in build mode).
- GUI cards: [012 w1c knowledge graph](tickets/012-95css-styled-knowledge-graph.md) + [013 ephemeral card pipeline](tickets/013-ephemeral-card-pipeline.md) were framed around agent-emitted spec JSON — **superseded**: cards now come from Pi's `extension_ui_request` (016). See tickets for the pivot.

## Not yet specified / next

- **Live full-loop acceptance run** (needs a real Aqua session): `--brain` pane typing → Pi answers with thinking in the bubble; sandboxed write blocked; Tab → build → approval card Allow/Deny; `/delegate` sub-clippy spawn → think → explode. Each piece is verified in isolation (and headless for the graph refactor); the interactive loop is not.
- Graph-refactor leftovers: **P4** single roots-of-truth for paths/config/scratch — **done** (tickets/024-roots-of-truth.md); **P5** a typed `Task` node for delegation (today a bare string + text protocol) remains.
- RAG/vector memory (decision: Pi-level markdown memory now; RAG only if it proves insufficient).

## Out of scope

- Full chat-history session tree as a product (Pi's sessions already do per-project JSONL continuity; Clippy stays `--no-session`).
- Plugin/marketplace distribution of Clippy or its skills.
- Shipping/installing Clippy beyond running it from this repo.
- OpenCode as an additional doer (Pi is the doer; OpenCode a possible later abstraction).
- Approval-based hot-steering of permissions into a live Pi process (Pi fixes tools at spawn; toggling re-spawns).