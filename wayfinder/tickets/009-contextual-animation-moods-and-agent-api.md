---
id: 009
title: Contextual animation moods + agent API
type: prototype
status: closed
assignee: wayfinder
blocked_by: []
labels: [wayfinder:prototype]
resolution: done
---

## Question

What are Clippy's semantic animation states (the moods the life itself adopts), and what API does a controller use to drive them?

Clippy has 43 raw animations. The shell should expose a small, contextually-aware mood vocabulary (idle / thinking / working / listening / greeting / farewell / celebrate / confused / alert) that a future ClippyController (sub-clippy lifecycle, ticket 004/008) maps lifecycle events onto — controller-driven, no model tool.

- Small fixed mood set with activity hints (working hint `build`→GetTechy, `write`→Writing, …).
- One-shot moods play once then return to idle; continuous moods hold and wrap.
- Idle auto-rotation after a delay, tunable via a config file (`clippy/config.json` + `~/.clippy/config.json` override).
- Explosion stays a shell event, not a mood.

Links the prototype as an asset. Resolution records the mood catalog and the interruption/rotation rules that work.

## Resolution

**Catalog (8 moods):** `thinking` (Thinking/Processing), `working` (hint-refined: build→GetTechy, write→Writing, read→CheckingSomething, search→Searching, mail→SendMail, print→Print, save→Save, artsy→GetArtsy, wizard→GetWizardy, explain→Explain, show→Show), `listening` (Hearing_1), `greeting` (Greeting/Wave/GetAttention), `farewell` (GoodBye), `celebrate` (Congratulate), `confused` (IdleHeadScratch), `alert` (Alert — interrupt-ok). `idle` is implicit and handled by the avatar's rotation state machine.

**Avatar state machine (`clippy/avatar.py`):** continuous moods hold and wrap to frame 0 when the animation list ends; one-shot moods play once then settle to `RestPose` and start the idle rotation timer. Interruption rules: continuous replaces continuous; only `alert` (marked `interrupt_ok`) may interrupt a running continuous mood; other one-shots during continuous are dropped. Frames without `images` in agent.json are treated as hold-frames (repeat last region).

**Idle rotation with delay (`clippy/moods.py` + `clippy/avatar.py`):** after a non-idle mood finishes, settle on `RestPose` for `idle.initial_delay_sec` (default 10s), then rotate among `idle.pool` every `idle.rotate_interval_sec` (default 45s), picking at random, avoiding the last anim.

**Config file:** shipped defaults in `clippy/config.json`; deep-merged user override at `~/.clippy/config.json` (written via `write_user_config()`). Covers delay, interval, pool, and all mood→animation/hint mappings. Deep merge ensures partial overrides don't clobber unrelated sections.

**Wire schema for the future brain→shell socket (ticket 004/008):** `{"type":"express","mood":"thinking","hint":"build","text":"…"}` defined in `moods.EXPRESSES_SCHEMA` as documentation; no LLM tool — controller-driven only, per the user's scope lock.

**Bug fixes in this ticket:** the original `avatar.py` froze on the last frame of non-looping animations (no auto-return to idle); frames with no `images` key in agent.json (`Greeting`, `Hide`, etc.) crashed `_play` with a `KeyError`; a zero-frame-duration path could spin the update loop infinitely.