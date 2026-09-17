---
id: 026
title: Sub-clippys can schedule tasks (delegated scheduling)
type: research
status: open
assignee:
blocked_by: []
labels: [wayfinder:research]
---

## Question

A delegated sub-clippy currently cannot set schedules or reminders — it can
only post an OS notification via `[CLIPPY::NOTIFY]` (ticket 034, plan B). Can a
worker also schedule a wall-clock task by emitting
`[CLIPPY::SCHEDULE] <when> | <what>`, which the host turns into a durable
scheduler entry?

## Context

- Workers already load the `notify` skill via `--skill` (`PiSubAgent.skills`,
  set in `_spawn_worker`); the `schedule` skill would follow the same path.
- The host parses worker directives in `_on_sub_done` (currently only
  `[CLIPPY::NOTIFY]` via `parse_notify`); scheduling would add `parse_schedule`
  there, creating a `TaskScheduler` entry (validated through `parse_trigger`, so
  only `in`/`at`/`every`/`daily` forms are accepted).
- Trust consideration: a fire-and-forget, sandboxed (read/search-only) worker
  creating *durable host state* is a bigger privilege than a notification. The
  effect is bounded (host-validated triggers + notify action), but worth
  deciding explicitly.

## Directions

- Add `schedule` to the worker's `--skill` list alongside `notify`.
- In `_on_sub_done`, run `parse_schedule(report)`; if it yields a trigger+what,
  schedule a notify task, strip the directive from the relayed report.
- Decide whether workers scheduling is allowed unconditionally or gated (e.g.
  only non-sandboxed tasks).

## Resolution

(open — pending decision on the trust boundary)