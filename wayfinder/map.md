---
title: Clippy — a working local demo
labels: [wayfinder:map]
---

# Clippy: Clippy as an interface to an LLM endpoint

## Destination

A working local demo on this Mac: **Clippy in a floating always-on-top desktop window** chats to an **OpenAI-compatible LLM endpoint**, owns **skills + tools** (agent-skill `SKILL.md` format, exposed as callable tools), is **sandboxed by default with a per-conversation build-mode toggle** (permission rules), and **delegates actual coding tasks to Pi** (pi.dev) as the under-the-hood doer. When Clippy (prime) issues a subagentic call, a **new Clippy instance is summoned** — a separate Pi instance whose live thinking/action event stream is articulated aloud in a speech bubble — and on task completion the sub-clippy's **animated avatar explodes dramatically** (explosion gif). The demo is "alive" when: one Clippy → one subagent spawn → its thinking shows in the bubble → explosion on completion.

## Notes

- **Domain:** a desktop companion/animation experiment; Python all the way down (per Pete). UI shell = **pyglet 2.x** window + **pyobjc** NSWindow tweaks (transparent framebuffer, `setOpaque:NO`, `clearColor`, no shadow, `CGWindowLevel` floating, `ignoresMouseEvents` pass-through toggle); shell talks to the brain over **sockets**. Pi (pi.dev) as the coding doer via its RPC/SDK + event stream; OpenAI-compatible endpoint for Clippy's own chat loop.
- **Skills to consult:** `wayfinder` (this), `research`. The `grilling` / `domain-modeling` / `prototype` skills referenced by wayfinder are not installed on this machine — HITL tickets are worked directly with the human. Run `/setup-matt-pocock-skills` if the tracker + those skills are wanted later.
- **Standing preferences:** sandboxed by default, build mode as a per-conversation toggle; subagent = separate Pi instance; skills reuse the agent-skill format; explosion gif supplied by Pete later.
- **Explosion gif:** now in `assets/` — `Green_Screen_Explosion-ezgif.com-crop.gif`: 180×180, 37 frames @10fps, fully opaque green `(36,252,1)` background → needs chroma-key. Do both: ffmpeg-baked transparent frames (safe path) + live GLSL chroma-key shader (showcase).
- **Spritesheet:** classic Microsoft Agent Clippy from `pi0/clippy` (jsDelivr mirror) — `map.png` 3348×3162, 124×93 cells, `agent.ts` with 41 animations (Wave/Thinking/GetAttention/Congratulate/GetArtsy/Writing/Greeting + idle sets + RestPose). Proseance: Microsoft IP, fine for local demo, don't ship commercially. Fetch pinned, not `@main`.

## Decisions so far

<!-- the index: one line per closed ticket, enough to judge relevance, then zoom the link for the detail the ticket holds -->

- [Pi drive surface](tickets/001-pi-drive-surface.md): Pi RPC mode (`pi --mode rpc --no-session`) per sub-clippy; one-shot sub-tasks via `pi --mode json -p --no-session`; thinking + tool events stream live; Pi not installed yet (npm install path settled); SDK is Node-only. Graduated [Install Pi locally](tickets/007-install-pi-locally.md) into a task ticket, and unblocked [Sub-clippy lifecycle and explosion](tickets/004-sub-clippy-lifecycle-and-explosion.md)'s dependency on it.
- [Clippy's own chat loop and skill-as-tool](tickets/002-clippy-chat-loop-and-skill-as-tool.md): official `openai` SDK 2.36.0, Chat Completions; hand-rolled tools loop; SKILL.md frontmatter → function (single free-text `request` arg), `disable-model-invocation` skills excluded; `reasoning_content` optional stream for the bubble. Graduated [Demo provider and model](tickets/008-demo-provider-and-model.md) into a grilling ticket.
- [Floating window with animated avatar](tickets/003-floating-window-with-animated-avatar.md): **pyglet 2.1 + pyobjc** for the window shell — `WINDOW_STYLE_OVERLAY` gives transparent framebuffer + always-on-top + click-through natively; shell↔brain will be sockets. Classic Clippy spritesheet from `pi0/clippy` (43 animations, 124×93 cells). Explosion pre-baked + live GLSL chroma-key shader. Stack is locked.
- [Contextual animation moods + agent API](tickets/009-contextual-animation-moods-and-agent-api.md): 8 semantic moods (thinking/working/listening/greeting/farewell/celebrate/confused/alert) + activity hints for `working` (build→GetTechy etc.); controller-driven (no model tool); idle rotation after a configurable delay; shipped defaults in `clippy/config.json`, user override deep-merged at `~/.clippy/config.json`. Wire schema `{"type":"express",…}` reserved for the future brain→shell socket (ticket 004/008).
- [Demo provider and model](tickets/008-demo-provider-and-model.md): **BYOK OpenAI-compatible endpoint** for Clippy's chat loop (no vendor lock-in); thinking bubble uses `reasoning_content` with graceful fallback to content stream. Secrets: shipped `clippy/config.json` `llm` section (no secrets) + gitignored `clippy/secrets.local.json` + env override, precedence env > secrets > config (`clippy/llmconfig.resolve_endpoint()`). Pi (doer) same provider family; its own auth configured in ticket 004.
- [Sub-clippy lifecycle and explosion](tickets/004-sub-clippy-lifecycle-and-explosion.md): a second `ClippyShell` window at a distinct position per sub-agent call; `clippy/subagent.py` (real Pi `--mode json` subprocess + mock fallback) streams JSONL onto a queue; `clippy/controller.py` polls it on the main clock and maps events → moods/bubble → celebrate → explosion → dismiss. Real sub-agent verified live against the local oMLX box (`omlx/gemma-4-12B-it-qat-OptiQ-4bit` default, `qwen3.8-27B-mlx-4bit` for streaming reasoning); provider wired into `~/.pi/agent/models.json`. Pyglet 2.x note: `GL_QUADS` is gone (use `GL_TRIANGLE_FAN`) and shader uniforms use `program["u"] = value`.
- [One-shot demo scenario](tickets/006-one-shot-demo-scenario.md): the acceptance test is now a script, deliberately non-interactive — `python main.py --delegate` (D key removed). Task = create+run `hello.py` in a fresh scratch dir; beats = sub summoned → thinking in bubble → tool-hint work → celebrate → explosion → sub dismisses, prime stays. Auto-mock-fallback when the oMLX box is offline. Rehearsed end-to-end real (moods thinking/working/celebrate, explosion, close, artifact) + headless mock (PASS). Fixes this session: explosion shader needed pyglet's `WindowBlock` projection (raw pixel coords were clipped) + correct chroma-key direction + baked frames advancing.
- [HTML/CSS/JS pane spike](tickets/010-html-css-js-pane-spike.md): **proven** — a transparent, floating, click-through NSPanel + WKWebView renders a **95CSS** (Win95) mock chat pane next to the pyglet window (plain pyobjc on the shared NSApplication loop; no pywebview). HTTPS-verified: chrome paints, `map.png` rich content loads via `file://`, JS executes, transparency confirmed (hidden-vs-shown diff 0.65%), N/X churn + clean quit. **Finding:** background non-activating panels freeze WKWebView compositor updates after first paint — JS runs but doesn't repaint live → interactive pane (011) must address foreground/active rendering. Paves the GUI direction: chat pane + ephemeral rich cards, 95CSS palette, methodology port from `PeteHaughie/HTML-components-canvas-graph` (spec JSON → strict resolver → styled knowledge graph).
- GUI direction (tickets 011–013, backburner): 011 interactive JS↔Python bridge (frontier, unblocked); 012 95CSS styled knowledge graph + resolver port (⬜ gated on 002 — human decision: graph after tool/skill use); 013 ephemeral card pipeline (blocked by 011+012). Rendering is plain DOM (Pete: no html-in-canvas snapshots in Clippy).

## Not yet specified

- Which starter skills ship with the demo (beyond the format decision, now decided in [Clippy's own chat loop and skill-as-tool](tickets/002-clippy-chat-loop-and-skill-as-tool.md)).
- Clippy's own chat loop is researched (ticket 002) but the loop code itself is not yet built; the sub-clippy delegation path (ticket 004) is the built proof. The demo's "one Clippy → one subagent spawn" acceptance is satisfied by `main.py --delegate` (see ticket 006). Endpoint base_url/model for Clippy's own loop come from `clippy/llmconfig` / `~/.clippy/config.json`.

## Out of scope

- Full chat history persistence / session tree (Pi's world, not Clippy's demo).
- Plugin/marketplace distribution of Clippy or its skills.
- Shipping/installing Clippy beyond running it from this repo.
- OpenCode as an additional doer for the demo (Pi is the doer; OpenCode remains a possible later abstraction).