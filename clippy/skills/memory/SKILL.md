---
name: memory
description: Persist and recall the user's long-term memory across Clippy sessions. Use when a new durable fact, preference, decision, or correction emerges, or when the user asks "remember…" / "what do you know about…".
---

# Clippy memory

Clippy is a desktop assistant that should remember its user across sessions.
This skill is how you do it.

## The store

Memory lives in `~/.clippy/memory/`:

- `~/.clippy/memory/INDEX.md` — a short index: one line per note, `[topic] path.md`.
- `~/.clippy/memory/<topic>.md` — the notes themselves (plain Markdown).

The INDEX is appended to every session's system prompt, so you always know
the store exists and what it contains. Topic files are read on demand.

## When to write

Add or update a note when the user reveals something durable:

- **Preferences** ("I prefer…", "please always…", "don't use X").
- **Decisions** reached together.
- **Corrections** about the user, their system, or your own behaviour.
- **Facts** worth remembering across sessions (names, machines, projects).

Trivia and one-off task chatter should NOT be persisted.

## How to write

1. Read `~/.clippy/memory/INDEX.md` first (or `read` a topic file if you know it).
2. Update the relevant topic file (create it if missing) with the new fact —
   keep it terse, dated with `## YYYY-MM-DD` for new entries.
3. Add/refresh the INDEX line so the next session can find it.

Use the `write`/`edit` tools. Work within `~/.clippy/memory/` only.

## How to recall

When asked "what do you know about X" (or a task needs prior context):

1. Check the INDEX (already in your system prompt).
2. `read` the matching topic file(s) and answer from them.
3. If nothing is there, say so plainly — do not invent memories.