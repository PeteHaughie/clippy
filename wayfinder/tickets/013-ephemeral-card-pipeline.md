---
id: 013
title: Ephemeral card pipeline in the pane
type: prototype
status: open
assignee:
blocked_by: [002]
labels: [wayfinder:prototype]
---

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