---
name: memory
description: Recall the user's long-term memory across Clippy sessions. Use when the user asks "what do you know about…" or a task needs prior context. Persistence is handled in the background by Clippy's memory curator.
---

# Clippy memory

Clippy is a desktop assistant that should remember its user across sessions.
Recall is this skill; persistence is handled by a background memory curator.

## The store

Memory lives in `~/.clippy/memory/`:

- `~/.clippy/memory/INDEX.md` — a short index: one line per note, `[topic] path.md`.
- `~/.clippy/memory/<topic>.md` — the notes themselves (plain Markdown).

The INDEX is appended to every session's system prompt, so you always know
the store exists and what it contains. Topic files are read on demand.

## How to recall

When asked "what do you know about X" (or a task needs prior context):

1. Check the INDEX (already in your system prompt).
2. `read` the matching topic file(s) and answer from them.
3. If nothing is there, say so plainly — do not invent memories.

## Persistence

You do not write memory yourself. When the user reveals something durable (a
preference, decision, correction, or lasting fact), note it for them and let the
memory curator persist it — do not attempt to edit `~/.clippy/memory/`.