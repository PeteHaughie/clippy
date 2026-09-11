---
id: 011
title: Interactive pane: JS<->Python bridge
type: prototype
status: open
assignee:
blocked_by: []
labels: [wayfinder:prototype]
---

## Question

Make the 95CSS pane interactive: real typing to-and-fro in the chat, and two-way JS<->Python control. How do we bridge WebKit's JS and the Python process cleanly, and how do we get live compositor updates while the pane is visible?

## Frames

- Bridge options: `WKScriptMessageHandler` (`contentController.addScriptMessageHandler`) for JS→Python; `evaluateJavaScript` for Python→JS (already proven in ticket 010 to *execute*); vs pywebview's `window.evaluate_js` / `js_api` (pywebview stayed out of the spike; revisit here where its conveniences earn their keep).
- **Live-compositor problem from 010:** the non-activating background panel freezes repaints. Options: activate the shell/panel when visible (`NSApp activate`), raise window level + activate policy, or drive animation on the GL side; decide which gives real updates without stealing focus (non-activating panels by design don't take key focus — square this with needing an input text field).
- Key/focus choreography: input needs keyboard focus; currently everything is click-through / non-activating. Spelling out the summon-to-type interaction is the meat of this ticket.

## Acceptance (draft)

Paddle the sum-benefit js_api vs raw message handler with measurements; pane repaints live while visible; typing is accepted and round-trips Python→(LLM/mock later); N/X still works.