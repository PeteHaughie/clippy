---
id: 004
title: Sub-clippy lifecycle and explosion
type: prototype
status: open
assignee:
blocked_by: [003, 007, 008]
labels: [wayfinder:prototype]
---

## Question

How does a subagentic call summon a new Clippy instance, show its thinking, and explode on completion?

Prototype the lifecycle: Clippy (prime) delegates → a new Clippy instance is summoned as a separate Pi instance → its live thinking/action events stream into the speech bubble + avatar states → on task completion the avatar *explodes dramatically* with the explosion gif → window dismissed.

- Sizing one subagent spawn (rules/skill tool that triggers it, the prompt handed to Pi, where the subtask works).
- Feeding Clippy's bubble from the Pi event stream (link to Pi drive surface ticket's answer).
- Proving the explosion: the gif asset is supplied later by Pete; the prototype stubs it and the ticket notes it waits for the real asset.
- No CLI scaffolding/install to judge yet — rough and dirty is fine.

Links the prototype as an asset. Resolution records the lifecycle shape that works.