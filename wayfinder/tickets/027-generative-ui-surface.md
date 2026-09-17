---
id: 027
title: Generative UI surface + media primitives in the graph
type: task
status: open
assignee:
blocked_by: []
labels: [wayfinder:task]
---

## Question

Clippy's pane renders only single-card dialogs (`__uiRequest`); it has no way to
render a streaming generative-UI component tree, and no graph primitives for
image/video/map media. What additions to the graph (`clippy/model.py`) let the
brain drive a generative UI surface and route media into the pane — behind a
protocol boundary that keeps the renderer splittable into its own project later?

## Context

Research (ticket-adjacent, `research/gemini-ephemeral-ui.md`) found:

- Google's generative UI (Gemini 3) renders a component tree via the **A2UI**
  protocol (`createSurface / updateComponents / updateDataModel /
  deleteSurface`; `a2ui-project/a2ui`, Apache-2.0) or sibling **AG-UI**; the
  Flutter **GenUI** SDK renders a widget catalog from it.
- The mature OSS media stack for an agent UI is a **webview host** rendering
  `<img>`, `<video>`+hls.js, canvas/WebGL, and **MapLibre/Leaflet** for maps.
  Clippy's pane is already a webview, so rendering is possible.

Current graph primitives: node kinds `external|process|resource|value|state|
component|capability|interface|output`; edge kinds `produces|consumed_by|drives|
projects_to|triggers|opens|rendered_as|injected_into|constrains|completes|
displays`. The `output` node kind exists but is unused; `pane` is an
`interface`; `dialog → pane` is `rendered_as {channel: card}`.

Gaps identified (research §5):
1. **Generative-UI surface** — a `surface`/`view` node + a streaming
   `materializes` edge carrying an A2UI-style component tree (the `output` kind
   is the natural home).
2. **Media primitives** — no `asset`/`media` resource node, no `map`/`view`
   node, no edge routing model-produced image/video/map into the pane.
3. **Media pipeline** — no asset/pipeline node for generated media (Imagen/Veo
   via Gen Media APIs) + transport (hls.js/FFmpeg).

## Directions

- Extend `__uiRequest` in the pane into an A2UI-shaped surface protocol
  (`__surfaceCreate`/`__surfaceUpdateComponents`/`__surfaceUpdateDataModel`/
  `__surfaceDelete`) so the pane is a pure renderer behind a transport-agnostic
  protocol.
- Add graph primitives (additive, no removals): an `output`-kind `surface` node;
  `asset`/`media` resource nodes; `materializes`/`renders`/`streams` edges from
  brain → surface → pane.
- Draw the split seam: the renderer (pane + protocol) should be extractable into
  a separate project/package (like `flutter/genui`) without touching the session
  graph or scheduler.
- Media: image/video/map views in the pane via `<img>`/`<video>`+hls.js and
  MapLibre/Leaflet; a pipeline node for generated media.

## Resolution

(open — pending implementation)