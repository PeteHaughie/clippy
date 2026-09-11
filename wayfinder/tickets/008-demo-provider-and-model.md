---
id: 008
title: Demo provider and model
type: grilling
status: open
assignee:
blocked_by: []
labels: [wayfinder:grilling]
---

## Question

Which OpenAI-compatible provider and model powers Clippy's own chat loop for the demo?

Grill the human on: the concrete endpoint (OpenAI, DeepSeek, a local server) and model for the one-shot demo; where the API key lives and how Clippy gets it (config file, env); and whether the provider emits `reasoning_content` in streaming — the research notes that field is the bubble's thinking feed and OpenAI never sends it, so the bubble design in [Sub-clippy lifecycle and explosion] waits on this. Also confirm Pi's doer provider/model (Pi supports 15+ providers; may differ from Clippy's).