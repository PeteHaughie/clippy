---
id: 003
title: Floating window with animated avatar
type: prototype
status: open
assignee: wayfinder
blocked_by: []
labels: [wayfinder:prototype]
---

## Question

What should the floating Clippy window look and act like, and which Python stack gets us there fastest?

A cheap, rough prototype (frameless/always-on-top/rounded floating panel with an animated paperclip avatar that can also play a gif — the explosion placeholder) to react to.

- Deciding between tkinter / PyQt / Toga based on: frameless always-on-top windows, transparent-ish rounded panels, smooth animation, gif playback, speech-bubble text rendering, and macOS behavior.
- Animated avatar: where the Clippy frames come from (a sprite sheet; the classic Office paperclip animation frames if rights-permitting; or a placeholder), and how "thinking" vs "acting" vs "exploding" states render.
- The minimal window chrome: where the build-mode toggle and the chat bubble live.

Links the prototype as an asset. Resolution records the stack choice + why, and the sprite/avatar plan.