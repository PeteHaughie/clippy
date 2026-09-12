---
id: 022
title: Explicit state machines (graph-model P2)
type: prototype
status: closed
assignee: pete
blocked_by: [021]
labels: [wayfinder:prototype]
---

## Question

Three state machines were hand-rolled as scattered flags, if/elif chains and timer arithmetic: the avatar's mood rules (continuous/oneshot/interrupt), the worker lifecycle (`running→celebrating→exploding→dismissing→failed` + timers + a `done`/`_expired` predicate), and the prime conversation phase (a vestigial `state` attribute that was never updated). How do we make state explicit and declarative?

## Resolution

- **`clippy/statemachine.py`** — a tiny runtime over graph-declared configs. States = nodes, transitions = edges (`trigger` + optional named `guard`/`effect`/`to`), timed states auto-fire an `on_timeout` trigger. `"*"` src matches any state; `to` may be a callable.
- **`clippy/model.py`** — `WORKER_LIFECYCLE` and `PRIME_CONVERSATION` as data (states + transitions + timeout/effect/guard names).
- **`clippy/avatar.py`** — `build_mood_sm`: the interruption decision is the `mood_allow` guard; playback (animation, wrap, idle-pool rotation) stays in the Avatar as the projection. `current_mood` reads the SM.
- **`clippy/controller.py`** — `SubClippyController` runs `WORKER_LIFECYCLE` with effects (celebrate/explode/fail/close), guards (success/fail) and timeouts (celebrate duration, dismiss delay, fail hold). Timers are now state timeouts; `done` is a reachability check on `dismissed`.
- **`clippy/prime.py`** — `PrimeController` runs `PRIME_CONVERSATION` (idle→working→answering→idle); the previously-vestigial phase is real and drives settled/retry handling.

## Acceptance

Headless: MoodSM drops a one-shot during a continuous mood but lets `alert` interrupt; the worker lifecycle runs the mock script to `dismissed` on success and `failed` on non-zero exit, firing `on_complete` correctly; the prime controller returns to `idle` after an answer. (Timers driven via the clock loop as before.)