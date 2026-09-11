---
title: Clippy — a working local demo
labels: [wayfinder:map]
---

# Clippy: Clippy as an interface to an LLM endpoint

## Destination

A working local demo on this Mac: **Clippy in a floating always-on-top desktop window** chats to an **OpenAI-compatible LLM endpoint**, owns **skills + tools** (agent-skill `SKILL.md` format, exposed as callable tools), is **sandboxed by default with a per-conversation build-mode toggle** (permission rules), and **delegates actual coding tasks to Pi** (pi.dev) as the under-the-hood doer. When Clippy (prime) issues a subagentic call, a **new Clippy instance is summoned** — a separate Pi instance whose live thinking/action event stream is articulated aloud in a speech bubble — and on task completion the sub-clippy's **animated avatar explodes dramatically** (explosion gif). The demo is "alive" when: one Clippy → one subagent spawn → its thinking shows in the bubble → explosion on completion.

## Notes

- **Domain:** a desktop companion/animation experiment; Python UI stack (tkinter/pyqt/Toga) for the floating window; Pi (pi.dev) as the coding doer via its RPC/SDK + event stream; OpenAI-compatible endpoint for Clippy's own chat loop.
- **Skills to consult:** `wayfinder` (this), `research`. The `grilling` / `domain-modeling` / `prototype` skills referenced by wayfinder are not installed on this machine — HITL tickets are worked directly with the human. Run `/setup-matt-pocock-skills` if the tracker + those skills are wanted later.
- **Standing preferences:** sandboxed by default, build mode as a per-conversation toggle; subagent = separate Pi instance; skills reuse the agent-skill format; explosion gif supplied by Pete later.
- **Explosion gif:** still to be provided by Pete ("will provide later"); sub-clippy tickets should assume the asset arrives, not block on it.

## Decisions so far

<!-- the index: one line per closed ticket, enough to judge relevance, then zoom the link for the detail the ticket holds -->

## Not yet specified

- Which specific provider/model sits behind Clippy's own OpenAI-compatible endpoint (and where the API key/config lives).
- Which starter skills ship with the demo (beyond the format decision).
- Whether OpenCode must also be a doer for the demo, or Pi alone suffices.
- Config/secrets layout for Clippy (endpoint, model, Pi invocation).
- Tkinter vs PyQt vs Toga for the floating window — that's ticket selection, but the *window chrome* (frameless, always-on-top, rounded) is assumed.
- Whether "sub-clippy articulates current thinking" means streaming Pi's thinking events live into the bubble, or a paraphrase after the fact.

## Out of scope

- Full chat history persistence / session tree (Pi's world, not Clippy's demo).
- Plugin/marketplace distribution of Clippy or its skills.
- Shipping/installing Clippy beyond running it from this repo.
- OpenCode as an additional doer for the demo (Pi is the doer; OpenCode remains a possible later abstraction).