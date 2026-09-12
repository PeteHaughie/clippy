---
id: 017
title: Skills allowlist, sandbox toggle, persistent memory
type: prototype
status: closed
assignee: pete
blocked_by: [015, 016]
labels: [wayfinder:prototype]
---

## Question

How does Clippy scope its brain: an editable skills allowlist, sandbox-by-default with a build-mode toggle, and persistent cross-session memory?

## Resolution

- **Skills allowlist** — `clippy/config.json` `skills.allow` (deep-merged with `~/.clippy/config.json`). `clippy/memory.resolve_skill_paths()` returns absolute paths (user list + always-on memory skill). `PiBrain` gained a `skills` param → `--no-skills --skill <path>…` (Pi's documented additive combo), so only listed skills surface — your `disable-model-invocation` skills only if listed (Pi ignores that field).
- **Sandbox by default / build on toggle** — `main.py` `PrimeSession`: sandbox spawn = `--tools read,grep,find,ls` (read/search only, scratch-dir cwd); build spawn = full tools + `-e clippy-gate.ts` (approval cards). Pi sets tools at spawn only, so **Tab re-spawns the brain** (research-verified). Badge in the pane statusbar reflects live mode.
- **Persistent memory** — research finding: skills are on-demand, so presence must be injected. `clippy/memory.ensure_memory()` creates `~/.clippy/memory/INDEX.md`; it's passed as `--append-system-prompt` on every spawn (verified: Pi confirmed it sees the index). `clippy/skills/memory/SKILL.md` teaches read/write discipline (write preferences/decisions/corrections to topic files; recall from INDEX). RAG deferred (decision: Pi-level memory now).

## Acceptance

`main.py --brain` starts sandboxed (badge 🛡); Tab → build (badge 🔨) re-spawns with the gate; a build-mode write asks a w1c confirm card. Memory INDEX persists and is injected every session.