---
id: 008
title: Demo provider and model
type: grilling
status: closed
assignee: wayfinder
blocked_by: []
labels: [wayfinder:grilling]
resolution: done
---

## Superseded (projection pivot)

Clippy no longer runs its own chat loop — Pi is the brain/doer and owns provider config (`~/.pi/agent/models.json`, omlx). The BYOK endpoint machinery (`clippy/llmconfig.py`) was never consumed by a loop and now serves as reference only. The demo provider/model decision is moot: Pi's omlx box drives everything.

## Question

Which OpenAI-compatible provider and model powers Clippy's own chat loop for the demo?

Grill the human on: the concrete endpoint (OpenAI, DeepSeek, a local server) and model for the one-shot demo; where the API key lives and how Clippy gets it (config file, env); and whether the provider emits `reasoning_content` in streaming — the research notes that field is the bubble's thinking feed and OpenAI never sends it, so the bubble design in [Sub-clippy lifecycle and explosion] waits on this. Also confirm Pi's doer provider/model (Pi supports 15+ providers; may differ from Clippy's).

## Resolution

Grilled Pete (2026-09-11); machine checked first (no keys in env/shell/keychain, no local server running, Pi installed but `~/.pi/agent/auth.json` empty).

**Clippy's chat endpoint — BYOK OpenAI-compatible.** No vendor lock-in: any endpoint speaking `/chat/completions` (OpenAI, DeepSeek, OpenRouter, local Ollama/LM Studio/vLLM). base_url + model live in config layers, api_key in a gitignored local secrets file.

**Thinking bubble — graceful fallback.** Stream `reasoning_content` when the provider sends it (DeepSeek/Qwen/thinking-capable, per ticket-002 research), else fall back to `content`. No requirement to pick a thinking provider.

**Secrets layout — config + gitignored local secrets (locked:**
- Shipped `clippy/config.json` gained an `llm` section: `{"provider": "openai-compatible", "base_url": "", "model": ""}` (no secrets).
- User overrides via `~/.clippy/config.json` (base_url/model), deep-merged.
- API key in `clippy/secrets.local.json` (gitignored; `secrets.local.json.example` committed as template).
- **Precedence (verified by tests):** env (`OPENAI_BASE_URL` / `OPENAI_API_KEY` / `CLIPPY_MODEL`) > `secrets.local.json` > merged config.
- Errors surfaced clearly: no endpoint / no key / no model; dummy key (`clippy-local`) permitted for local servers that ignore auth. Default base_url `https://api.openai.com/v1` if unset and a key is present.

**Pi (doer) — same provider family as Clippy.** Pi's auth is genuinely separate (`~/.pi/agent/auth.json` / env, or a `models.json` entry for a custom OpenAI-compatible endpoint); Pi credential setup is ticket 004's doer-side step, recorded here as policy only.

**Build artifact:** `clippy/llmconfig.py` — `resolve_endpoint()` returns `{base_url, api_key, model, provider}`, consumed by the chat loop when it is built (ticket 004). No live calls this ticket (no key configured, loop not built).