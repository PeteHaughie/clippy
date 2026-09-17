# Time awareness + task scheduling for Clippy

Research + decision behind Clippy's wall-clock scheduler (date: 2026-09-17).

## The problem

Clippy had zero time awareness: `datetime.now()` was used only for log/scratch
timestamps; the brain never saw the current time; there was no wall-clock
scheduler. We wanted Clippy to (a) know the current time, and (b) do things on
a timer — without tying a model up with a heartbeat call (idle model turns are
still billed tokens).

## Findings (the wheels that exist)

- **Host owns the clock; the model never computes time.** Hermes Agent's
  temporal-awareness RFC: the runtime computes current time + idle deltas
  deterministically and injects a small per-turn header into prompt assembly
  (e.g. `[Current time: …]`), ~1 token, zero model heartbeat. Prepending a
  timestamp to every historical message bloats context; a transient per-turn
  header is the fix. (Corroborated by `chronos` and `agent-wallclock`: giving a
  model timestamps is not enough — the host must decide *when* to inject them.)
- **Daemon owns waiting; the model owns judgment** (Cryochamber / Sundial): the
  host scheduler sleeps on the clock and only wakes the model when a task is
  *actually due* (`wake → observe → act → choose next wake → hibernate`). This
  is the anti-heartbeat pattern the user asked for.
- **Cron is a wake source, not the whole scheduler.** Mature systems converge on
  "a wall-clock tick + a persistent state machine / DAG":
  - `marianmeres/workflow` — durable FSM instances that "sleep for days waiting
    for a signal or a timer," driven by a cron tick flipping
    `waiting + wake_at <= now()` rows to pending.
  - `autumn-harvest` / `workflow-graph` / `Kontroler` — cron timetables +
    task/run state machines (`PENDING → QUEUED → RUNNING → SUCCEEDED/RETRY/
    FAILED`), with `next_run_at` recomputed after each fire.
  - Cloacina draws the line cleanly: cron/date decides *when*; the graph/FSM
    decides *what happens* and the lifecycle.
- **APScheduler** is the mature in-process cron wheel (date/interval/cron
  triggers, persistent job stores) — but it owns its own thread and an opaque
  job store. Clippy already has a loop (pyglet/GLib) and a graph-model
  philosophy (`clippy/model.py` declares state machines as graph data executed
  by `StateMachine`), so APScheduler would be a parallel wheel that can't
  produce a model-passable schedule.

## Decision

- **Graph/FSM scheduler on the existing loop, no APScheduler, no new thread.**
  A scheduled task is a `StateMachine` running the `SCHEDULED_TASK` config
  (`pending → due → fired → rescheduled|done`) from `clippy/model.py`. The
  wall-clock tick from `Session.update` is the only "cron": it fires tasks whose
  `wake_at` has passed. Persisted to JSONL (`~/.clippy/scheduler.jsonl`) so
  tasks survive Clippy's volatile session state and reload on restart
  (overdue tasks fire on the next tick).
- **Time awareness is host-injected.** The model cannot run `date` in sandbox
  mode (`SANDBOX_TOOLS = read/grep/find/ls` — no bash), so the host prepends a
  per-turn header (`[Current local time: …]`) plus a short schedule brief to
  every brain-bound prompt. A `/time` command answers deterministically.
- **Actions**: host effects (pane message, mood) are free; `brain` actions are
  queued and fired only when the prime is idle (no heartbeat).
- **Commands**: `/remind <when> <what>`, `/schedule`, `/schedule cancel <id>`,
  `/time`. Round-one triggers: one-shot (`in N <unit>` / `at HH:MM`), interval
  (`every N <unit>`), and `daily at HH:MM`.
- **Roadmap** (not built): a `schedule` skill emitting
  `[CLIPPY::SCHEDULE] <when> | <what>` for model-initiated scheduling, and full
  cron-expression syntax (e.g. `croniter`) if needed.

## Consequence

Clippy is time-aware without burning tokens on a heartbeat: the host owns the
clock, the scheduler is a graph/state machine in the codebase's own idiom, and
the schedule is serializable and passable to the model. The trade-off accepted:
scheduling is in-process (tasks only fire while Clippy runs; the JSONL store
makes them survive restarts, not a system daemon).

## References

- `clippy/model.py` (graph model / state-machine configs) — the repo's
  "graph-model" context
- `clippy/statemachine.py` — StateMachine runtime (timeouts drive `SCHEDULED_TASK`)
- `clippy/scheduler.py`, `clippy/timeutil.py` — the implementation
- Hermes Agent temporal-awareness RFC; `chronos` (arxiv 2510.23853);
  `agent-wallclock`; Cryochamber "daemon owns waiting"; APScheduler docs;
  `marianmeres/workflow`, `autumn-harvest`, `workflow-graph` (cron tick + FSM)