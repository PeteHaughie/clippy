---
id: 010
title: HTML/CSS/JS pane spike (95CSS)
type: prototype
status: closed
assignee: wayfinder
blocked_by: []
labels: [wayfinder:prototype]
---

## Question

Prove HTML + CSS + JS can render in a Python process alongside the pyglet Clippy window — the prerequisite for the GUI design direction: a Win95-styled chat pane (95CSS) with ephemeral rich-content cards, built with the methodology of `PeteHaughie/HTML-components-canvas-graph`.

## Resolution (spike PASSED — webview pane works)

Assets: `html_pane_spike.py` (driver) + `assets/pane/spike_pane.html` + `assets/pane/vendor/95css/` (95CSS v0.4.2 pinned/vendored via GitHub API blobs — raw HTTPS is unreachable from this shell, API blobs work).

**Architecture (locked):** a borderless, non-activating, click-through, floating **NSPanel** created via **plain pyobjc** (no pywebview this stage) *inside a pyglet-`schedule_once` callback on the shared NSApplication run loop* — no second run loop. Hosts a layer-backed `WKWebView` with `drawsBackground` off; loads the local html via `loadFileURL_allowingReadAccessToURL_` (read access granted to `assets/` so the `map.png` card can load via `file://`). Pane positioned to overlap the avatar so transparency is provable. Keys: N summon, X hide, Q quit (ClippyShell subclass keeps P/T/Space/E).

**Empirically verified by pixel probes of `screencapture` crops (Retina 2x: pane 340x460pt at x84/y691 = px cols 168-848, rows-from-top 578-1498):**
- **HTML+CSS render:** 95CSS chrome painted — navy header ≈ `(42,26,131)` = `#000080`, silver body ≈ `#c0c0c0` when shown vs `(10,10,10)` desktop when hidden.
- **Rich content:** `map.png` rendered in the image card (2331 magenta pixels — pi0/clippy sprite-sheet is magenta).
- **JS executes:** progress `<progress>` fill `>0%` (768 green px) from a markup value of `0` — JS wrote it. Bootstrap also mutates the status cell synchronously ("JS BOOTED").
- **Transparency:** the pane's transparent bottom rim differs hidden-vs-shown by only 0.65% of pixels — desktop/avatar show straight through; no black box.
- **Lifecycle:** scripted N→X→N→X churn stable, all events fired, exit code 0, no traceback.

**Key finding (drives stage 2):** WKWebView in a *background, non-activating* panel paints its first frame then **freezes compositor updates** — JS timers (setInterval) and even Python-driven `evaluateJavaScript` DOM mutations do not repaint afterward (verified: two captures 1.8s apart byte-identical in the dialog during a live cycle). JS *executes* (progress fill proves it) but background panels don't get live frame updates. Ticketed into stage 2: the interactive pane must run foreground/active (or the shell must be activated), or animation moves into GL.

Vendor notes: `95css.min.css` has exactly one external dependency — sibling `fonts/w95fa.{woff2,woff,otf}` (url `../fonts/…`, family `w95fa`); every other asset is an inline SVG data-URI. Layout must mirror that depth.

Deferred (NOT this spike): chat loop, spec cards, resolver, tools/skills. See tickets 011 (bridge), 012 (graph, gated on 002), 013 (card pipeline).