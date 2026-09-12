# w1c vendor — provenance

Retro web-component library (`desertthunder/w1c`) vendored for Clippy's WKWebView pane.

## Pinned source

- `@w1c/components` **0.1.0-next.0** (npm `latest`), deps bundled: `@w1c/dnd@0.1.0-next.0`, `@w1c/fonts@0.1.0-next.0`, `lit@^3.3.2`.
- Theme: `themes/windows-95.css` + `styles/{tokens,utilities,native}.css`.
- Fonts: IBM Plex Serif 400/600/700, IBM Plex Mono 400/600/700 (latin, woff2) and IBM Plex Sans Variable (latin wght, woff2-variations), via Fontsource.
  Latin-only override authored here (the stock `@w1c/fonts/windows.css` pulls cyrillic/greek/latin-ext/vietnamese and woff+woff2 duplication).
- License: MIT (w1c) · OFL-1.1 (IBM Plex). See `node_modules/@w1c/{components,fonts}/LICENSE`.

## Bundled output (what gets committed)

- `w1c.bundle.js` — single-file **classic-script IIFE**: all `@w1c/components` classes + lit runtime inlined. ESM would be
  preferable, but WKWebView refuses to execute `type=module` scripts over `file://` (opaque origin / CORS), so the spike loads
  the bundle as a plain `<script>`. **Verified under `file://` at the correct path:** `customElements.get('w1c-window') === DEFINED`,
  shadow roots present, 7 IBM Plex faces registered, live JS runs. ~157 KB.
- `w1c.css` — tokens + windows-95 theme + utilities + native styles; 7 latin woff2 faces inlined as data URIs. ~208 KB.

## Verified in the spike (ticket 014)

- Load from `w1c_pane.html` (which sits in `assets/pane/`) must use the vendor dir **without** `../`: `vendor/w1c/w1c.css`,
  `vendor/w1c/w1c.bundle.js`. The `../vendor/w1c/…` form resolves to `assets/vendor/w1c/` which does NOT exist — the elements
  staying UNDEFINED was this path bug, not the bundle format (the earlier ESM attempt was confounded by the same wrong path).
- windows-95 theme titlebar paints the navy gradient `#000080 → #1084d0` (blue-dominant pixels, full-width); the component
  paints it on the `header` inside `w1c-titlebar`'s shadow root (probe the shadow `header`, not the host).
- Keep the pane page `html,body { height:100%; overflow:hidden }` + `input.focus({preventScroll:true})` or focus scrolls the
  chrome away (titlebar rect.top went 1 → −211).

## Rebuild recipe (npm registry reachable; raw.githubusercontent.com is not)

```
mkdir /tmp/w1c-vendor && cd /tmp/w1c-vendor
npm i @w1c/components@0.1.0-next.0 @fontsource/ibm-plex-serif @fontsource/ibm-plex-mono @fontsource-variable/ibm-plex-sans esbuild
# entry.js:  import '@w1c/components';
# entry.css: @import './fonts-latin.css'; @import '@w1c/components/styles/tokens.css';
#            @import './theme-windows-95-local.css'; @import '@w1c/components/styles/utilities.css';
#            @import '@w1c/components/styles/native.css';
#  fonts-latin.css      = latin-only @font-face (see repo history / handoff notes)
#  theme-windows-95-local.css = windows-95.css WITHOUT the '@w1c/fonts/windows.css' and relative '../styles/tokens.css' imports
# NOTE: build IIFE (classic script), not ESM — see the bundle note above.
npx esbuild entry.js  --bundle --format=iife --target=safari16 --minify --outfile=w1c.bundle.js
npx esbuild entry.css --bundle --loader:.woff2=dataurl --outfile=w1c.css
```

Commit the two built files (not node_modules). Re-run the probe in the spike doc after rebuilding.