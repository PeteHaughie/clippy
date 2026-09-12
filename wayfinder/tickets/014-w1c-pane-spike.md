---
id: 014
title: w1c pane spike (web components, windows-95 theme)
type: prototype
status: closed
assignee: wayfinder
blocked_by: []
labels: [wayfinder:prototype]
---

## Question

Prove the vendored w1c web-component library (`@w1c/components`, Lit custom elements, windows-95 theme) can replace the hand-curated 95CSS classes in the Clippy pane: bundle boots inside the same WKWebView shell as 010/011, theme chrome paints, the exact 011 bridge contract round-trips, and focus/live behavior holds.

## Resolution (spike PASSED — w1c pane works, pivot approved)

Assets: `w1c_pane_spike.py` (driver, copy of `html_pane_spike.py`) + `assets/pane/w1c_pane.html` + `assets/pane/vendor/w1c/` (`w1c.css` ~208KB with 7 latin IBM-Plex woff2 data URIs, `w1c.bundle.js` ~157KB esbuild **classic IIFE**, `PROVENANCE.md`).

**Verified live (WKWebView, `file://`):**
- **Bundle boots:** w1c custom elements upgrade — `ce-w1c-window: DEFINED`, `shadow-root: SHADOW`, `w1c-button/input/select/tabs` defined, 7 IBM Plex faces registered, progress cycle runs (`jsstate 'JS LIVE n%'`), body `data-w1c: ready`.
- **Theme chrome paints (pixel probe, Retina 2x, pane 340x460pt at 84/691):** navy gradient titlebar `#000080 → #1084d0` present (26,394 blue-dominant px, full-width rows 2-45; band0 mean `(67,99,177)` = blue-dominant), silver chrome `#c0c0c0` (231K px), white content, yellow clippy icon, tan `map.png` card rendered (9.6K px).
- **Live repaint:** two animated captures differ 76.5% of pixels (cycling progress + live text). Frozen (progress gate `window.__paused`) three captures are 0.0% diff — deterministic; the transient silver/white "clipped chrome" frames seen earlier are a WKWebView transparent-compositing flake under live animation, not a CSS gap.
- **Bridge (011 contract unchanged):** mock round-trip `JS → Python → JS` confirmed in the same harness.
- **Focus:** `activeElement` stays `chatinput` across repeated probes after summon.

**Debugging findings (record for 002/013):**
1. **Asset path resolution:** `<link>/<script src="../vendor/w1c/...">` from `assets/pane/w1c_pane.html` resolves to `assets/vendor/w1c/` which does NOT exist (vendor lives at `assets/pane/vendor/w1c/`). Correct relative path is `vendor/w1c/...`. The 95CSS spike had the same latent bug (its measured pixels came from page CSS, not 95CSS). After fixing the path the elements upgrade — the earlier "IIFE still broken" runs were the path bug, not the bundle format.
2. **Focus scrolls the page chrome away:** `input.focus()` on a scrollable document scrolls the viewport (titlebar `getBoundingClientRect().top` went 1 → −211). Fix: `html,body { height:100%; overflow:hidden }` + `input.focus({ preventScroll:true })` — desktop-window semantics, chrome stays put.
3. **CGEvent keyboard synthesis does not land in this shell context** (Accessibility/Input-Monitoring): selftest typed text yields `value:""` on **both** the w1c pane and the 95CSS control — environmental, not w1c. Focus chain + bridge are proven; re-run keyboard typing from a real GUI session.
4. **Transparent WKWebView composites flakily mid-animation** (see Live repaint above) — freeze animations for capture; may matter for 013 live cards.

**Fix-ups needed before 002 re-scope if adopted for the graph palette:** no native `w1c` progress/range/radio elements — pane uses native `<progress>`/styled; card-era elements should track what w1c actually ships (`w1c-window/titlebar/statusbar/tabs/panel/input/button/select/dialog`).

## What changed

- Vendored w1c (`assets/pane/vendor/w1c/`), created `w1c_pane.html`, `w1c_pane_spike.py`, `/tmp` loadtest probe harness. Deleted `assets/pane/vendor/95css/` after PASS (95CSS/w95fa fully out of the tree).
- 012/013 re-scoped to w1c elements; 011/010 untouched (A/B control kept as `html_pane_spike.py`).