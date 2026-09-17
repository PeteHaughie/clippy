# Gemini ephemeral / generative UI — research findings

Research for Clippy: what Google has actually shipped/announced around **dynamically
generated, rendered, interactive UI** from Gemini (not just text), the open-source
landscape for agentic/generative UI, and the conventional OSS stack for rendering
image/video/map in an agent UI. Date of research: 2026-09-18.

Bottom line up front: Google's generative-UI story is real and now has an SDK and an
open protocol. The flagship shipped artifact is **Gemini 3's "Generative UI"**
(research blog + paper, live in the Gemini app and Google Search AI Mode), the
developer-facing pieces are the **A2UI protocol** (streaming JSON UI) and the
**GenUI SDK for Flutter** (alpha), and the agentic-browsing side runs on **Gemini in
Chrome / auto browse** (Project Mariner was retired). There is no official "UI Studio"
or "Gimbal" toolkit; "Android generative UI" today means GenUI-for-Compose-adjacent
work and Gemini-in-Android-Studio code generation.

---

## 1. Gemini ephemeral / generative UI — what it is and what's shipped

**Definition.** "Generative UI" = the model generates *not just content but the
interface itself* — web pages, games, tools, and interactive apps rendered on the fly
for any prompt, instead of a static/markdown "wall of text" (Google Research, Nov 18
2025: https://research.google/blog/generative-ui-a-rich-custom-visual-interactive-user-experience-for-any-prompt).
Paper: "Generative UI: LLMs are Effective UI Generators", project page + PAGEN
(human-expert dataset) at https://generativeui.github.io/. The implementation is
Gemini 3 Pro + (1) a server exposing tools like image generation and web search,
(2) crafted system instructions, (3) post-processors; output is a fully generated
HTML/CSS/JS page rendered as-is in the user's browser (ibid.). Human-preference ELO
1710.7 vs. human-expert sites ~highest, far above markdown/text baselines; generation
can take a minute+ and has occasional inaccuracies (ibid.).

**Shipped in products:**
- **Gemini app** — two experiments: *dynamic view* (full generative-UI experience
  built with Gemini's agentic coding) and *visual layout* (styling controls), rolling
  out with Gemini 3 (Nov 18 2025) (research blog; https://blog.google/products-and-platforms/products/gemini/gemini-3-collection;
  product commentary: 9to5Google, Nov 25 2025, https://9to5google.com/2025/11/25/gemini-generative-uis-apps — secondary).
- **Google Search AI Mode** — generative UI with interactive tools/simulations
  (e.g. a loan calculator or physics sim), "Thinking" model, US AI Pro/Ultra
  subscribers (research blog, ibid.; https://blog.google/products-and-platforms/products/gemini/gemini-3-collection).
- **GenUI SDK for Flutter** — announced with Gemini 3, now `genui ^0.10.2` on pub.dev
  (verified publisher `labs.flutter.dev`, BSD-3-Clause, ~29k downloads, 192 likes;
  https://pub.dev/packages/genui). Renders structured (JSON) AI output as Flutter UI
  from a developer-defined **widget catalog**; user interaction updates a client-side
  data model fed back to the agent. Status: **highly experimental / alpha**
  (https://github.com/flutter/genui, README; https://docs.flutter.dev/ai/genui,
  "in alpha and is likely to change").

**The protocol: A2UI ("Agent to UI").** The SDK and the Gemini-style generative-UI
rendering are built on **A2UI** — a streaming, JSON-based, transport-agnostic protocol
where an agent sends `createSurface` / `updateComponents` / `updateDataModel` /
`deleteSurface` messages and a renderer progressively draws native widgets
(https://a2ui.org/; spec v0.9.1 "current production", v1.0 candidate:
https://a2ui.org/specification/v0.9.1-a2ui). Originally developed in Google's org
(github.com/google/A2UI v0.8 spec history), now stewarded by the independent
`a2ui-project` org (Apache-2.0, 16.4k stars): https://github.com/a2ui-project/a2ui.
GenUI for Flutter supports A2UI v0.9; a `genui_a2a` package connects to A2A/A2UI
agent servers (https://docs.flutter.dev/ai/genui; https://github.com/flutter/genui).
Flutter's own I/O 2026 talk positions it as "Flutter + A2UI = GenUI"
(https://docs.flutter.dev/ai/genui). A sibling protocol, **AG-UI** (agent→user UI
events, from the CopilotKit/LangChain ecosystem, MIT, ~16k stars), is listed as an
A2UI transport binding (https://github.com/ag-ui-protocol/ag-ui;
https://a2ui.org/specification/v0.9-a2ui).

**Agentic browsing / live interactive UI in the browser:**
- **Project Mariner** — Gemini-powered browser agent (takes screenshots of the tab,
  sends to Gemini, drives the page), announced Dec 11 2024 (WIRED:
  https://www.wired.com/story/google-gemini-2-ai-assistant-release/; TechCrunch:
  https://techcrunch.com/2024/12/11/google-unveils-project-mariner-ai-agents-to-use-the-web-for-you),
  rolled out at I/O May 20 2025 (dashboard, cloud VMs, up to 10 parallel tasks;
  Mariner capabilities into the Gemini API/Vertex AI — TechCrunch:
  https://techcrunch.com/2025/05/20/google-rolls-out-project-mariner-its-web-browsing-ai-agent).
  **Retired May 4, 2026**; "its technology voyaged to other Google products"
  (https://labs.google.com/mariner/landing).
- **Gemini in Chrome** — floating window → **side panel**, **Connected Apps**
  (Gmail inline compose, Calendar, Maps, Flights, etc.), **auto browse** (agentic
  multi-step browsing, AI Pro/Ultra US preview), **Nano Banana** in-browser image
  edit, and the open **Universal Commerce Protocol (UCP)** for agentic commerce
  (Google, Jan 28 2026: https://blog.google/products-and-platforms/products/chrome/gemini-3-auto-browse/;
  9to5Google, Jan 28 2026: https://9to5google.com/2026/01/28/gemini-chrome-side-panel-more —
  secondary). June 2026: "Select from screen" tool added; **Gemini 3.5 Flash gains a
  built-in computer-use tool** for browser/mobile/desktop agents (9to5Google, Jun 24
  2026: https://9to5google.com/2026/06/24/gemini-chrome-select-screen — secondary).

**Official APIs/SDKs (the "UI surface" for developers):** the Gemini API itself has
no HTML/UI output type. The developer-facing UI surfaces are: A2UI protocol + GenUI
Flutter SDK (above), the **Live API** for real-time audio/video/voice streaming with
tool use and ephemeral tokens (https://ai.google.dev/gemini-api/docs/live;
https://ai.google.dev/gemini-api/docs/live-api/ephemeral-tokens), the **Interactions
API** (default since June 2026) for agentic multi-turn state
(https://ai.google.dev/api), and **Gen Media APIs** (Imagen image, Veo video)
(ibid.). **App Actions** (Google Assistant intent mapping + inline inventory, widgets)
is the *older, non-generative* Android-to-assistant surface — not generative UI
(https://developers.google.com/assistant/app). **No "Gimbal"/UI-toolkit exists**:
"Android generative UI" today means the GenUI Flutter SDK (targets Android/iOS/macOS/web:
https://pub.dev/packages/genui) plus Gemini codegen in Android Studio — screenshot→
Jetpack Compose ("Generate UI with image attachments"), "Transform UI with Gemini" on
Compose previews, "Match UI to Target Image"
(https://developer.android.com/studio/gemini/generate-ui-with-images;
https://developer.android.com/studio/gemini/transform-ui) — and **Google AI Studio
Build mode**, which generates whole native Android (Kotlin+Compose) apps from a prompt
with a browser-based emulator (https://ai.google.dev/gemini-api/docs/aistudio-android).

---

## 2. News timeline (2024–2026)

- **2024-12-11** — Gemini 2.0 + Project Mariner prototype (Chrome extension; screenshots→Gemini→actions). (WIRED, TechCrunch, above.)
- **2025-05-06** — Gemini 2.5 Pro (I/O edition) tuned for building interactive web apps; +147 Elo WebDev Arena; Canvas. (https://blog.google/products-and-platforms/products/gemini/gemini-2-5-pro-updates)
- **2025-05-20** — I/O 2025: Mariner rollout (AI Ultra), Agent Mode preview, Mariner→Gemini API/Vertex AI. (TechCrunch, above.)
- **2025-09** — Gemini button launches in Chrome preview. (The Register, Jan 29 2026: https://www.theregister.com/2026/01/29/chrome_gemini_pane; Computerworld, Dec 9 2025: https://www.computerworld.com/article/4103343/gemini-for-chrome-gets-a-second-ai-agent-to-watch-over-it.html — both secondary.)
- **2025-11-18** — **Gemini 3** + Generative UI research + dynamic view / visual layout + AI Mode gen UI + GenUI Flutter SDK (alpha) + Antigravity. (research.google blog; https://blog.google/products-and-platforms/products/gemini/gemini-3-collection; https://www.infoq.com/news/2025/11/google-gemini-3 — secondary.)
- **2025-11-20** — A2UI spec v0.9 published at a2ui.org; v1.0 candidate follows. (https://a2ui.org/)
- **2025-12-19** — Google Developers: "Real-World Agent Examples with Gemini 3" (browser-use, Agno). (https://developers.googleblog.com/real-world-agent-examples-with-gemini-3)
- **2026-01-28** — Gemini in Chrome: side panel, auto browse, Connected Apps, UCP, Nano Banana. (blog.google, above.)
- **2026-05-04** — Project Mariner shut down; tech folded into other products. (https://labs.google.com/mariner/landing)
- **2026-06-24** — Gemini 3.5 Flash built-in computer use; "Select from screen". (9to5Google, above — secondary.)
- **2026-09-17** — Google Research: generative UI for teachers creating learning interactives. (https://research.google/blog/the-future-of-practice-enabling-teachers-to-create-learning-interactives-with-generative-ui/)

---

## 3. Mature open-source projects (agentic / generative UI, screen understanding, UI automation)

Verified via GitHub API, 2026-09-18 (stars/license/activity current as of that date).

| Project | What it does | License | Stars / activity | Media support |
|---|---|---|---|---|
| **browser-use/browser-use** | LLM-driven browser agent (Playwright/CDP): navigate, click, fill forms, extract; CLI, Python lib, cloud. (https://github.com/browser-use/browser-use) | MIT | **~115k** (114,984); pushed Sep 15 2026 | DOM/accessibility-first; screenshots & `record_video_dir` MP4 recording supported |
| **bytedance/UI-TARS + UI-TARS-desktop** | Native **GUI agent** VLM models + desktop app: perceives screenshots, plans, clicks/keys; local or remote VM operators; Agent TARS stack; UI-TARS-2 adds multi-turn RL + GUI-SDK (https://github.com/bytedance/UI-TARS-desktop; https://github.com/bytedance/UI-TARS; UI-TARS-2 report: https://arxiv.org/html/2509.02544v1) | Apache-2.0 | UI-TARS 11.5k (pushed Jan 2026); UI-TARS-desktop **39k** (pushed Sep 11 2026) | **Image (screen) native** — pure screenshot perception; no video/map rendering (it *reads* screen, doesn't render media) |
| **microsoft/playwright-mcp** | MCP server for browser automation via Playwright's **accessibility tree** (no vision model needed); also Playwright CLI+skills (https://github.com/microsoft/playwright-mcp) | Apache-2.0 | **37.2k**; pushed Sep 17 2026 | DOM/accessibility only; screenshots on demand |
| **web-infra-dev/Midscene** (Bytedance) | Web GUI automation SDK ("GUI Agent for E2E Testing") using VLM grounding; JS/Python; pairs with UI-TARS models (https://github.com/web-infra-dev/midscene) | MIT | **14.9k**; pushed Sep 17 2026 | DOM + screenshot/visual grounding |
| **ag-ui-protocol/ag-ui** | AG-UI protocol + SDKs + Dojo to bring agents into frontends (event stream, shared state, tool calls, generative UI) (https://github.com/ag-ui-protocol/ag-ui; https://docs.ag-ui.com/introduction) | MIT | **15.9k**; pushed Sep 17 2026 | Protocol, not a renderer — works with any frontend |
| **a2ui-project/a2ui** | A2UI spec + reference renderers/transports (AG-UI, A2A bindings) (https://github.com/a2ui-project/a2ui; https://a2ui.org/) | Apache-2.0 | **16.4k**; pushed Sep 17 2026 | Declarative JSON UI; renderer-host-specific |
| **flutter/genui** | GenUI SDK for Flutter: widget-catalog-driven generative UI (https://github.com/flutter/genui; https://pub.dev/packages/genui) | BSD-3-Clause | **1.8k**; pushed Sep 14 2026 | Native Flutter widgets; deps include `video_player` (media) |
| **google/A2UI** | Original A2UI home (v0.8 spec history) — **moved** to `a2ui-project`; note: `google-research/screen-use` does **not** exist as a repo (verified). | Apache-2.0 (a2ui-project) | — | — |

Notes: There is **no mature Google-owned OSS "screen-use" browser agent** (github
`google-research/screen-use` returns 404; verified 2026-09-18). The term "screen-use"
survives in small community repos (e.g. `tongriyaotxt/screen-use`, a 1-star MIT Windows
desktop "browser-use for the desktop", https://github.com/tongriyaotxt/screen-use) and
as a research direction (Google DeepMind's multimodal grounding). The proprietary
computer-use baselines are Anthropic Computer Use, OpenAI Operator, and Google's
Mariner→Gemini 3.5 Flash computer-use tool (9to5Google, above). For a desktop agent,
the **UI-TARS stack is the reference**; for web, **browser-use + playwright-mcp**.

---

## 4. Image / video / map rendering stack in an agent UI

The conventional open-source answer is: **an embedded webview or browser host (DOM +
canvas + WebGL) that renders a page the agent generated or described** — Google's own
generative UI is literally "a fully-generated web page rendered as-is on the user's
browser" (research.google blog, above). Concretely, for each media type:

- **Images** — plain HTML: `<img>` (or `<picture>`/`srcset`), CSS, `canvas` 2D, and
  WebGL for generated/processed images; client-side processing via `canvas` + a
  library like Pillow/Sharp on the server. No special engine needed.
- **Video** — the `<video>` element + Media Source Extensions. The two dominant OSS
  players are **hls.js** (HLS via MSE; https://github.com/video-dev/hls.js, 16.9k
  stars, Apache-2.0, pushed Sep 17 2026) and **Shaka Player** (DASH/HLS;
  https://github.com/shaka-project/shaka-player — API lookup for `google/shaka-player`
  failed, repo now under `shaka-project`). For native/Flutter, **`video_player`**
  (which `genui` already depends on) plus `video_player_win`, or libVLC/GStreamer for
  desktop transcoding (FFmpeg for encode).
- **Maps** — **MapLibre GL JS** (BSD-3-Clause, ~11.7k stars, WebGL vector tiles, ~4.3M
  weekly npm downloads at v6.6.0; https://github.com/maplibre/maplibre-gl-js,
  https://www.npmjs.com/package/maplibre-gl) or **Leaflet** (BSD-2-Clause, 45.6k
  stars, simpler raster tiles; https://github.com/Leaflet/Leaflet). Both drop into a
  webview/DOM. In Flutter: `flutter_map` (BSD-3-Clause, 3k stars,
  https://github.com/fleaflet/flutter_map) or `maplibre_gl`.

So the mature stack for an agent UI = **webview/browser host → HTML/JS DOM renderer
(<img>, <video>+hls.js, canvas/WebGL) with MapLibre or Leaflet for maps**, wired to
the agent through a protocol like A2UI/AG-UI (or plain streaming markdown/HTML), with
FFmpeg/hls.js for the media pipeline. If you're building the UI in-process rather than
in a webview, GenUI-for-Flutter already brings `video_player`, `url_launcher`, and
markdown/audio widgets and you add `flutter_map`/`maplibre_gl` for maps.

---

## 5. Gaps for Clippy — graph primitives for image/video/map + generative UI

Clippy's graph (`clippy/model.py`) declares the control plane as typed nodes/edges.
What it models today, and the gaps the research exposes.

**Current primitives.** Node kinds: `external | process | resource | value |
state | component | capability | interface | output`. Edge kinds: `produces |
consumed_by | drives | projects_to | triggers | opens | rendered_as |
injected_into | constrains | completes | displays`. The UI-relevant graph today:
`pane` (an `interface`), `dialog` (a `state`), `rendered_as {channel: card}`
(dialog→pane), `displays {channel: badge}` (mode→pane), plus `chat_input`,
`task`, `shell`. The `output` node kind exists but is unused.

**Gap 1 — a generative-UI surface protocol.** Google's generative UI renders a
*component tree*, streamed through **A2UI** (`createSurface / updateComponents /
updateDataModel / deleteSurface`) or the sibling **AG-UI**; the Flutter **GenUI**
SDK renders a widget catalog from that JSON. Clippy's pane has only `__uiRequest`
(single-card dialogs) — a proto-A2UI. **Gap:** a `surface`/`view` node + a
streaming `surface`/`materializes` edge (brain → view) that carries a component
tree, not just one card. The graph's `output` kind is the natural home for a
rendered surface.

**Gap 2 — media primitives.** The mature OSS stack (research §4) is a webview
host rendering `<img>`, `<video>`+hls.js, canvas/WebGL, and **MapLibre/Leaflet**
for maps. Clippy's pane *is* a webview, so rendering is possible — but the graph
has **no `media`/`asset` resource node, no `map`/`view` node, and no edge that
routes a model-produced image/video/map into the pane.** **Gap:** add `asset`
(value) and `media` (resource) node kinds (or a `view` component), plus a
`renders`/`streams` edge from those into the pane.

**Gap 3 — media pipeline.** Image/video generation (Imagen/Veo via Gen Media
APIs) and serving (hls.js/FFmpeg) are absent. **Gap:** a `media_pipeline`/`asset`
node representing generated media + its transport into the webview.

**Split-vs-integrate recommendation.** The research's mature stack (webview host
+ A2UI/AG-UI protocol + media libs) is a **clean seam**: the pane is already an
isolated vendored artifact (`assets/pane/`), and A2UI is a transport-agnostic
protocol. **Recommendation: keep Clippy integrated for now, but draw a protocol
boundary** — the brain emits A2UI-shaped surface messages into the pane (extend
`__uiRequest` → a component-tree surface), and the pane stays a pure renderer.
That makes the renderer **splittable into a separate project/package** later
(like `flutter/genui` or an A2UI web renderer) without touching the session
graph or scheduler. If the UI surface "explodes" in scope (media pipelines, map
views, generative surfaces), spin the renderer out as its own repo behind that
protocol — the graph changes needed (Gaps 1–3) are additive and stay in Clippy's
core.

---

## 6. Sources / references

Primary:
- Google Research — Generative UI blog + paper + PAGEN: https://research.google/blog/generative-ui-a-rich-custom-visual-interactive-user-experience-for-any-prompt · https://generativeui.github.io/
- Gemini 3 announcement hub: https://blog.google/products-and-platforms/products/gemini/gemini-3-collection
- Gemini in Chrome / auto browse / UCP: https://blog.google/products-and-platforms/products/chrome/gemini-3-auto-browse/
- Project Mariner shut-down: https://labs.google.com/mariner/landing
- Gemini 2.5 Pro web-apps update: https://blog.google/products-and-platforms/products/gemini/gemini-2-5-pro-updates
- GenUI SDK for Flutter: https://docs.flutter.dev/ai/genui · https://github.com/flutter/genui · https://pub.dev/packages/genui
- A2UI protocol: https://a2ui.org/specification/v0.9.1-a2ui · https://github.com/a2ui-project/a2ui
- Gemini API reference / Live API: https://ai.google.dev/api · https://ai.google.dev/gemini-api/docs/live
- Android Studio Gemini UI codegen: https://developer.android.com/studio/gemini/generate-ui-with-images · https://developer.android.com/studio/gemini/transform-ui
- Google AI Studio Android app build: https://ai.google.dev/gemini-api/docs/aistudio-android
- App Actions: https://developers.google.com/assistant/app
- Google Research gen-UI for teachers: https://research.google/blog/the-future-of-practice-enabling-teachers-to-create-learning-interactives-with-generative-ui/
- Google Developers "Real-World Agent Examples with Gemini 3": https://developers.googleblog.com/real-world-agent-examples-with-gemini-3
- AG-UI: https://github.com/ag-ui-protocol/ag-ui · https://docs.ag-ui.com/introduction

Repos verified via GitHub API (2026-09-18): browser-use/browser-use, bytedance/UI-TARS, bytedance/UI-TARS-desktop, microsoft/playwright-mcp, web-infra-dev/midscene, a2ui-project/a2ui, ag-ui-protocol/ag-ui, flutter/genui, Leaflet/Leaflet, maplibre/maplibre-gl-js, video-dev/hls.js, fleaflet/flutter_map.

Secondary (news/critique; stated as such above): 9to5Google, TechCrunch, WIRED, The Verge, InfoQ, Computerworld, The Register.