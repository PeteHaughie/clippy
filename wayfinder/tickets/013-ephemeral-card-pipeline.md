---
id: 013
title: Ephemeral card pipeline in the pane
type: prototype
status: closed
assignee:
blocked_by: []
labels: [wayfinder:prototype]
---

## Superseded (016)

Delivered, under the projection architecture, by ticket 016: cards are rendered from Pi's `extension_ui_request` dialogs (`confirm`/`select`/`input`/`editor`/`notify`) directly in the pane (`window.__uiRequest`), and form/dialog values round-trip back to the brain as `extension_ui_response`. The "assistant emits a fenced `spec` block → resolver validates (012) → js_api renders" chain is obsolete — the spec channel was framed for the hand-rolled 002 loop. Stale-card/disable semantics are handled per-dialog (buttons disable after an answer). The w1c card gallery styling lives on in the pane.

## Question

Render agent-emitted `spec` JSON as ephemeral w1c cards in the live pane: stream the spec, validate via the styled graph + resolver (012), assemble DOM in the WKWebView (via the 011 bridge — closed ✅), keep cards per-message, disable stale ones as the conversation moves on, and route form values back into the next chat turn.

## Frames

- Full chain: Clippy's chat loop (002) → tools/skills decode a fenced `spec` block → resolver validates against graph.json (012) → `evaluateJavaScript`/js_api renders the card (011) → interactions post form data back → loop.
- Card gallery is the w1c element set (ticket 014 spike): windows/panels/tabs/select/input/button/dialog; native progress for meta/percent; no 95CSS anywhere (vendor/95css deleted).
- Pre-existing prototype assets at `PeteHaughie/HTML-components-canvas-graph` (resolver, spec protocol, stale-card semantics) are the reference implementation to port, NOT running code for Clippy.
- Where the spec is emitted: as part of Clippy's normal chat answer (fenced code block) or a dedicated tool call? Decide with 002.
- 014 findings that apply: freeze/avoid animation during captures (transparent WKWebView compositing flakes); `focus({preventScroll:true})` + `overflow:hidden` so card/focus actions never scroll chrome away.

## Acceptance (draft)

A `--delegate` demo beat renders one graph-validated w1c card (e.g. form + progress) that updates live while the pane is foreground, and a stale card disables when superseded.