---
id: 020
title: Shell status-line surface (mode badge + dialog indicator)
type: prototype
status: closed
assignee: pete
blocked_by: [016]
labels: [wayfinder:prototype]
---

## Question

The sandbox/build mode badge and the pending-approval state live in the pane statusbar (016). The map flags that they should "also surface" in the pyglet shell status line above the avatar.

## Resolution

- **`clippy/shell.py`** — `ClippyShell` gains `mode` (str|None) and `dialog_pending` (bool) state (None on non-prime shells). The status line is now segmented: `mode:🛡`/`mode:🔨` when a mode is set, `mood:<name>`, and `dialog:waiting` while a consent card is pending — e.g. `mode:🛡 · mood:thinking · (working…) (P pass / T think / E explode / Q quit)`.
- **`clippy/prime.py`** — `PrimeController` sets `shell.dialog_pending = True` on `extension_ui_request`.
- **`main.py`** — `PrimeSession` sets `shell.mode` on every spawn (sandbox/build, and on Tab toggle) and clears `dialog_pending` when a `ui_response` is sent back to the brain.

## Acceptance

The prime shell's status line shows the live mode badge and a `dialog:waiting` segment while a build-mode approval card is up; the badge updates on Tab toggle. (Visual — live-run item; app boots and draws the segmented line.)