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

## Not yet specified

- Which starter skills ship with the demo (beyond the format decision, now decided in [Clippy's own chat loop and skill-as-tool](tickets/002-clippy-chat-loop-and-skill-as-tool.md)).
- Config/secrets layout for Clippy (endpoint, model, Pi invocation); the [Demo provider and model](tickets/008-demo-provider-and-model.md) grilling pins the first half.

## Out of scope

- Full chat history persistence / session tree (Pi's world, not Clippy's demo).
- Plugin/marketplace distribution of Clippy or its skills.
- Shipping/installing Clippy beyond running it from this repo.
- OpenCode as an additional doer for the demo (Pi is the doer; OpenCode remains a possible later abstraction).