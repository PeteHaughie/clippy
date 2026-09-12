---
id: 021
title: Unified typed event model (graph-model P1)
type: prototype
status: closed
assignee: pete
blocked_by: [015]
labels: [wayfinder:prototype]
---

## Question

Pi ships the same logical event under two wire shapes (RPC `message_update.assistantMessageEvent.type` vs `--mode json` `assistant_message_event.eventType`), and both controllers compensated ad hoc — including the `type`/`eventType` precedence bug class fixed once in ticket 019 and still latent in prime.py. How do we make event routing one definition of truth?

## Resolution

- **`clippy/model.py`** — the typed `Ev` catalog (AgentStart, TurnStart, MessageStart, ThinkingDelta/End, TextDelta, ToolCallStart, ToolExecStart/End, MessageEnd, AgentEnd, AgentSettled, UiRequest, UiPromptStart, Response, Exit, Unknown) as frozen dataclasses with stable `kind` names.
- **`clippy/events.py::normalize(raw) → Ev`** — maps **either** wire shape (and the host's synthetic `brain_exit`/`sub_exit`/`unparseable`) onto the catalog; `extract_text`/`extract_result_text` unified. The `eventType or type` resolution now lives in exactly one place.
- **`clippy/events.py::AgentEventRouter`** — owns the shared thinking/text buffers + bubble-worthy substrings + tool bubbles; controllers become `EventSink`s that react, instead of re-parsing events. The duplicated `_handle`/`_handle_update`/`_on_tool_start`/`_on_tool_end` from prime.py + controller.py are gone.

## Findings that mattered

- The two wire shapes really do collide on the same semantic event (thinking/text deltas, message_end); normalising at the boundary removes the divergence structurally rather than patching each controller.
- `message_end` carries the final text in `message.content` on RPC but only a `stopReason` in `--mode json` — the router falls back to its accumulated `text` buffer, so both paths yield the same `message_end(stop_reason, text)`.

## Acceptance

Headless: identical events from both wire shapes normalise to equal `Ev` objects; router accumulates and dispatches; prime + worker controllers run the mock scripts through it unchanged (same answers, same lifecycle).