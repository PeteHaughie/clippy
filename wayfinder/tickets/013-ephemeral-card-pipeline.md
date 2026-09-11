---
id: 013
title: Ephemeral card pipeline in the pane
type: prototype
status: open
assignee:
blocked_by: [011, 012]
labels: [wayfinder:prototype]
---

## Question

Render agent-emitted `spec` JSON as ephemeral 95CSS cards in the live pane: stream the spec, validate via the styled graph + resolver (012), assemble DOM in the WKWebView (via the 011 bridge), keep cards per-message, disable stale ones as the conversation moves on, and route form values back into the next chat turn.

## Frames

- Full chain: Clippy's chat loop (002) → tools/skills decode a fenced `spec` block → resolver validates against graph.json (012) → `evaluateJavaScript`/js_api renders the card (011) → interactions post form data back → loop.
- Pre-existing prototype assets at `PeteHaughie/HTML-components-canvas-graph` (resolver, spec protocol, stale-card semantics) are the reference implementation to port, NOT running code for Clippy.
- Where the spec is emitted: as part of Clippy's normal chat answer (fenced code block) or a dedicated tool call? Decide with 002.

## Acceptance (draft)

A `--delegate` demo beat renders one graph-validated 95CSS card (e.g. form + progress) that updates live while the pane is foreground, and a stale card disables when superseded.