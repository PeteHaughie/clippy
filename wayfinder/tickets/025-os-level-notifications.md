---
id: 025
title: OS-level alarms independent of Clippy
type: research
status: open
assignee:
blocked_by: []
labels: [wayfinder:research]
---

## Question

Clippy's in-process scheduler (ticket 033) fires only while Clippy is running —
an alarm set for T+20 is lost as a *notification* if Clippy is quit at the due
time (it fires late, as overdue, on the next launch). Can scheduled alarms fire
as OS-level notifications **independent of the Clippy process**, and how far is
that worth going?

## Context

- The current scheduler (`clippy/scheduler.py`) persists tasks to
  `~/.clippy/scheduler.jsonl` and surfaces them via `clippy/notify.py`
  (`osascript` on macOS, `notify-send` on Linux) — timing is in-process.
- To fire without Clippy running we'd need an OS-owned wake source: a
  `launchd` agent / systemd timer that reads the schedule and calls a notifier,
  or an MCP server exposing schedule+notify to any client.
- This is "agentic OS-level" territory (a system daemon owned by the user's OS,
  independent of the app's lifecycle) — a different boundary than the current
  in-process design.

## Directions to investigate

- `launchd` (macOS) / systemd timers (Linux) that run a small script on a
  schedule derived from the scheduler store.
- A tiny standalone CLI/notifier invoked by the OS timer (no Clippy window).
- An MCP server for schedule/notify so the model (or other agents) can manage
  alarms without the Clippy host.
- Trade-offs: OS-privilege surface, cross-platform parity (macOS vs Linux vs
  Wayland notification daemons), keeping the scheduler store as the single
  source of truth.

## Resolution

(open — pending research)