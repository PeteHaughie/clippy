---
id: 016
title: Projection surface — approval cards + dialog surface
type: prototype
status: closed
assignee: pete
blocked_by: [015]
labels: [wayfinder:prototype]
---

## Question

How do Pi's `extension_ui_request` dialogs (confirm/select/input/editor) become w1c cards in Clippy's pane, and how does build-mode consent work in v1 (approval cards)?

## Resolution

- `clippy/pane.py` — the 011/014 pane as a reusable module: transparent WKWebView NSPanel, `on_chat` (JS→brain.prompt), `on_ui_response` (dialog answer→brain), `add_message`, `ui_request` (render dialog), `set_mode`, `set_progress`. Active-mode (key-capable + app activation) preserved.
- Pane HTML (`assets/pane/w1c_pane.html`) gains `window.__uiRequest(event)` rendering each method as a w1c card: confirm (Allow/Deny), select (w1c-select), input (w1c-input), editor (textarea), notify (passive). Cancel semantics: confirm→`{confirmed:false}`, others→`{cancelled:true}`; positive→`{value}`/`{confirmed:true}`. Badge `__setMode` (`🛡 sandbox` / `🔨 build`).
- `clippy/extensions/clippy-gate.ts` — build-mode consent gate: `pi.on("tool_call")` intercepts mutating built-ins (bash/write/edit, `CLIPPY_GATE_TOOLS` override), asks `ctx.ui.confirm`, blocks on refusal, **fails closed** when `!ctx.hasUI`. Loaded via `-e` on build-mode spawns only.
- **Verified live over RPC against the oMLX box:** write → gate → `extension_ui_request{method:confirm}` → host `extension_ui_response{confirmed:true}` → file created; `{confirmed:false}` → `tool_execution_end isError` → file NOT created. Full host-driven consent loop from Python.

## Findings that mattered

- No per-turn tool switching on RPC (`prompt`/`steer`/`follow_up` have no `tools` field; no `set_tools`) — confirmed both in docs and by the research agent. Approval = intercept + dialog, not tool-set rewrite.
- An extension gates built-in tools without registering its own (research/pi-community-deep-dive.md §3). `tool_call` can block; `event.input` mutable.

## Acceptance

A build-mode brain's mutating tool call renders a w1c confirm card; Allow proceeds, Deny blocks. Both paths verified live (see resolution).