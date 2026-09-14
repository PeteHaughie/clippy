# marked vendor — provenance

`marked` (MarkedJS) vendored for Clippy's WKWebView pane: renders the model's
markdown (the "reasoning stream") as formatted HTML inside chat bubbles.

## Pinned source

- `marked` **18.0.13** (npm `latest`), `lib/marked.umd.js`.
- License: MIT. See `node_modules/marked/LICENSE`.

## Bundled output (what gets committed)

- `marked.umd.js` — the stock UMD build, copied verbatim. Classic-script UMD,
  so it sets `globalThis.marked` / `window.marked` under `file://` (WKWebView
  refuses `type=module` over `file://` — same constraint as the w1c bundle).
  ~46 KB, unminified.

## Rebuild recipe

```
npm i marked@18.0.13
cp node_modules/marked/lib/marked.umd.js assets/pane/vendor/marked/marked.umd.js
```

Marked only parses to HTML; raw-HTML sanitization lives in `w1c_pane.html`
(see `renderMarkdown`), not in the vendored file.