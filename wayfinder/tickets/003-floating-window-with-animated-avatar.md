---
id: 003
title: Floating window with animated avatar
type: prototype
status: closed
assignee: wayfinder
blocked_by: []
labels: [wayfinder:prototype]
resolution: done
---

## Question

What should the floating Clippy window look and act like, and which Python stack gets us there fastest?

A cheap, rough prototype (frameless/always-on-top/rounded floating panel with an animated paperclip avatar that can also play a gif — the explosion placeholder) to react to.

- Deciding between tkinter / PyQt / Toga based on: frameless always-on-top windows, transparent-ish rounded panels, smooth animation, gif playback, speech-bubble text rendering, and macOS behavior.
- Animated avatar: where the Clippy frames come from (a sprite sheet; the classic Office paperclip animation frames if rights-permitting; or a placeholder), and how "thinking" vs "acting" vs "exploding" states render.
- The minimal window chrome: where the build-mode toggle and the chat bubble live.

Links the prototype as an asset. Resolution records the stack choice + why, and the sprite/avatar plan.

## Resolution

**Stack:** pyglet 2.1.16 + pyobjc 10.3.2 in `clippy/.venv` (Python 3.11.13). No tkinter/PyQt/Toga — pyglet's `WINDOW_STYLE_OVERLAY` gives transparent framebuffer + always-on-top (`NSStatusWindowLevel`) + click-through (`set_mouse_passthrough()`) out of the box, all three toggles pyobjc-native. pygame/SDL2 transparent windows on macOS are painful (`SDL_WINDOW_TRANSPARENT` is SDL3-only) and pygame+moderngl loses the native window-level control. pyglet also has native GLSL shader support for the live chroma-key showcase.

**Sprite/avatar plan:** Classic Microsoft Agent Clippy from `pi0/clippy` (jsDelivr, pinned to commit `748f199f0187`): `map.png` 3348×3162, cells 124×93, 43 animations (Wave/Thinking/RestPose/GetAttention/Congratulate/Writing/Greeting/GetArtsy + idle sets). `agent.ts` converted to `assets/clippy/agent.json` via node. Avatar class slices `map.png` into pyglet texture regions and plays frame sequences at the durations declared in the JSON.

**Explosion gif:** pre-baked transparent PNG frames via `ffmpeg chromakey` (safe path, all green keyed to alpha) in `assets/clippy/explosion/`. Live GLSL chroma-key shader path loads the raw green frames from `assets/clippy/explosion-green/` and keys them in a fragment shader at render time (showcase of pyglet shader support).

**Build artifact:** `clippy/` package with `avatar.py`, `explosion.py`, `shell.py`; `main.py` entry point. Controls: `P` toggle pass-through, `T` toggle Thinking/RestPose, `Space` Wave, `E` explosion, `Q` quit. Verified on screen: transparent window, sprite animation, click-through toggle all working. Run with `./.venv/bin/python main.py`.