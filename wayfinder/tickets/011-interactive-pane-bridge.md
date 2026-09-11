---
id: 011
title: Interactive pane: JS<->Python bridge
type: prototype
status: closed
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

## Resolution (2026-09-12)

Went with **raw `WKScriptMessageHandler` + `evaluateJavaScript`** (not pywebview) — both proven paths from 010, zero new deps. Verified end-to-end with real keystrokes.

**Bridge**
- JS→Python: `BridgeHandler(NSObject)` implementing `userContentController:didReceiveScriptMessage:` registered via `addScriptMessageHandler:name:` (`"clippy"`). JSON body parsed in Python. Keep a strong ref to the handler (the controller only weakly holds it).
- Python→JS: `evaluateJavaScript:completionHandler:`.
- `--selftest` synthesizes real keystrokes via `CGEventPost` into the focused WKWebView input and confirms: `input.value == ""` after Send and `echoed: true` (the echo bubble exists). Keystrokes also produced `[pane] <- js (clippy): {"type":"chat","text":"hi from keyboard"}` + `bridge round-trip complete`.

**Focus / typing (the freeze + focus problem)**
- The 010 freeze **did not reproduce** after the bridge changes: both `active` and `passive` panes repaint live (0.835% of in-pane pixels change per animation tick, co-located at the progress bar, captured on a healthy-awake display). The freeze was likely 010-build-specific (old html, no activation interplay). Activation is still required for *typing*, so:
- `active` mode (default): on summon → `NSApp activateIgnoringOtherApps_(True)` + `makeKeyAndOrderFront_` + `makeFirstResponder_(webview)` + JS `input.focus()`, retried until `activeElement == chatinput` (probes show it sticks from attempt 0).
- `KeyablePanel(NSPanel)` overrides `canBecomeKeyWindow`/`canBecomeMainWindow` → True, since borderless panels otherwise refuse to become key.
- `setIgnoresMouseEvents_(True)` **stays on** — clippy remains click-through; typing works because key window ≠ mouse window.
- `passive` mode (`PANE_MODE=passive`): pure 010 click-through behavior, no activation/focus.

**Additions to the pane html**
- Chat log `#chat`, enabled input `#chatinput` + Send button, `window.__addMessage(role, text)`, `__focusInput`, `__sendMock` (mock user message through the real bridge), `post('chat', …)` via `messageHandlers.clippy`.

**Test-harness hazards (carry forward)**
- **Display asleep ≡ black + silent**: if the machine idles mid-test, screenshots go black and pyglet init crashes (`CGGetActiveDisplayList` returns 0 while CGMainDisplayID is online). Keep `caffeinate -u -t N` running across the whole capture burst and confirm `CGGetActiveDisplayList` ≥1 at capture time, or results are garbage.

## Acceptance (draft)

Paddle the sum-benefit js_api vs raw message handler with measurements; pane repaints live while visible; typing is accepted and round-trips Python→(LLM/mock later); N/X still works. — **Met**: live repaint measured on-screen; real keystrokes round-trip JS→Python→JS; focus holds; N/X churn + clean exit (EXIT=0) intact.