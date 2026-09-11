# Clippy's own chat loop and skill-as-tool — research findings

Research for ticket **002 — Clippy's own chat loop and skill-as-tool** (`wayfinder/tickets/002-clippy-chat-loop-and-skill-as-tool.md`).
Scope: the mechanics of Clippy's Python chat loop against an OpenAI-compatible endpoint, and how agent-skill `SKILL.md` files map onto callable tools.

Verification environment (this machine, pyenv Python 3.11.13):

```
openai       2.36.0   (installed)
httpx        0.28.1   (installed — openai SDK dependency)
langchain    not installed
langgraph    not installed
```

---

## 1. Which library for an OpenAI-compatible chat + tools loop in 2026

**Recommendation: the official `openai` Python SDK, version 2.36.0 (verified locally), driving the Chat Completions API (`chat.completions.create`) — one small hand-rolled tools loop on top. Not LangChain/LangGraph, not raw httpx.**

Rationale and citations:

- **The SDK is current and actively maintained for exactly this API surface.** The `openai-python` code generator (Stainless) maps 1:1 to the current OpenAPI spec: `chat.completions.create` accepts `tools`, `tool_choice`, `parallel_tool_calls`, `max_tokens`, `max_completion_tokens`, and returns `ChatCompletion` (non-stream) or `Stream[ChatCompletionChunk]` (stream). Verified in the installed package: `openai/resources/chat/completions/completions.py:248` (create signature), `:1197` (master create), `:1213` (return type `ChatCompletion | Stream[ChatCompletionChunk]`).
- **`base_url` is a first-class constructor argument, so any OpenAI-compatible endpoint works.** Resolution order in the SDK: explicit `base_url` argument → `OPENAI_BASE_URL` env var → default `https://api.openai.com/v1` (`openai/_client.py:212-228`). This is exactly the pattern OpenAI-compatible providers document for their own endpoints; DeepSeek's official quickstart shows `OpenAI(api_key=…, base_url="https://api.deepseek.com")` with the OpenAI SDK (https://api-docs.deepseek.com/ — "Your First API Call"). The SDK sends `Authorization: Bearer {api_key}` for any key value supplied (`openai/_client.py:455-465`), so a dummy key works against local servers that ignore auth.
- **Chat Completions, not the Responses API.** OpenAI is steering new work toward the Responses API (GPT-6 Astra requires it; the function-calling guide's Chat Completions examples use `gpt-5.6` "for compatibility": https://developers.openai.com/api/docs/guides/function-calling). But Clippy's requirement is *any* OpenAI-compatible provider (local vLLM/Ollama, DeepSeek, Qwen, etc.). Those endpoints implement `/v1/chat/completions`, not Responses. DeepSeek's reference is explicitly the OpenAI-format `/chat/completions` endpoint (https://api-docs.deepseek.com/api/create-chat-completion). So: Chat Completions is the interoperability lingua franca; the official SDK's Chat Completions support is stable and backwards-compatible per OpenAI's API compatibility policy (https://developers.openai.com/api/reference/overview — "Backwards compatibility").
- **LangChain/LangGraph add orchestration abstraction we don't need.** The loop in §2 is a ~40-line deterministic while-loop. LangChain is not installed here and adds a provider-agnostic layer on top of what `chat.completions.create` already gives us; it also tends to lag OpenAI-spec changes and hides the SSE/tool-call details Clippy needs for the speech-bubble streaming effect (§3). Keep the dependency surface tiny for a desktop app.
- **Raw httpx:** only justified if the SDK's feature set gets in the way; it doesn't. The SDK is a thin typed wrapper over httpx and already brings httpx 0.28.1. Prefer it for structured types, retries/timeouts, and SSE decoding (`openai/_streaming.py:283` `SSEDecoder`).

---

## 2. The end-to-end tools / function-calling round-trip (Chat Completions)

The canonical five-step flow (OpenAI function-calling guide, https://developers.openai.com/api/docs/guides/function-calling — "The tool calling flow"): (1) request with tools → (2) model returns tool call → (3) app executes it → (4) second request with the tool output → (5) final response (or more tool calls).

Concretely on `/v1/chat/completions`:

1. **Request 1 — system + user + `tools` array.** Each tool is `{type: "function", function: {name, description?, parameters}}` where `parameters` is a JSON Schema object (`ChatCompletionFunctionToolParam`/`FunctionDefinition` in the installed SDK: `openai/types/chat/chat_completion_function_tool_param.py`, `openai/types/shared_params/function_definition.py`; chat reference: https://developers.openai.com/api/reference/resources/chat#completions-create-chat-completion → `tools`). Function names: `[a-zA-Z0-9_-]`, max 64 chars.
   ```python
   client.chat.completions.create(model=..., messages=[...], tools=[...])
   ```
   `tool_choice` defaults to `"auto"` when tools are present — the model decides whether/how many to call (chat reference, `tool_choice`; guide "Additional configurations → Tool choice").

2. **Response — assistant `tool_calls`.** The returned `ChatCompletionMessage` carries `tool_calls: [{id, type: "function", function: {name, arguments}}]`, where **`arguments` is a JSON-encoded string** you must parse; `message.content` may be `null`, and `finish_reason: "tool_calls"` (chat reference → `Returns` → `ChatCompletionMessage.tool_calls`; guide "Handling function calls"). Responses may contain **zero, one, or multiple** calls — code should assume several (guide, "Handling function calls").

3. **Execute on the app side**, parsing each `call.id`, `call.function.name`, `json.loads(call.function.arguments)`.

4. **Request 2 — append results.** Append (a) the assistant message with the `tool_calls` verbatim, then (b) **one `role: "tool"` message per tool call**: `{role: "tool", tool_call_id: <call.id>, content: <string result>}` (chat reference → `messages` → `ChatCompletionToolMessageParam {content, role: "tool", tool_call_id}`; installed SDK `openai/types/chat/chat_completion_tool_message_param.py`). Result content is free-form (JSON string, plain text, `"success"`) — the model interprets it (guide, "Formatting results").
   ```python
   messages += [assistant_msg_with_tool_calls] + [{"role": "tool", "tool_call_id": tc.id, "content": result} for tc in tool_calls]
   ```

5. **Loop** until a completion returns no `tool_calls` / `finish_reason != "tool_calls"`. Each round does another API call; chat completions is stateless, so the **full message list is re-sent every round**.

OpenAI-compatible specifics:

- DeepSeek confirms the identical wire protocol and even stricter notes: tool message needs `tool_call_id`; assistant `tool_calls` carry `id/type/function{name, arguments}`; tool names must be **unique** and max **128** chars (https://api-docs.deepseek.com/api/create-chat-completion → `messages` / `tools`).
- Some providers require assistant tool-call messages to be echoed back unmodified; the OpenAI reference makes `content` on `ChatCompletionToolMessageParam` required, so always pass content.
- For OpenAI reasoning models (GPT-5/o4-mini) any reasoning items returned alongside tool calls must also be passed back with tool outputs (function-calling guide, note under "Function tool example"). Clippy's provider-agnostic loop should carry whatever extra assistant fields the provider emits (see §3 `reasoning_content`).

---

## 3. Streaming the model's output (and the "thinking in the speech bubble" feed)

**Mechanics (OpenAI chat completions streaming reference, https://developers.openai.com/api/reference/resources/chat/subresources/completions/streaming-events):**

- Set `stream: true`; the SDK returns `Stream[ChatCompletionChunk]` (`openai/resources/chat/completions/completions.py:599`, `:1213`), iterated with `for chunk in stream:`. SSE is decoded by the SDK's `SSEDecoder` (`openai/_streaming.py:283`).
- Each chunk is a `chat.completion.chunk` with `choices[].delta` and `choices[].finish_reason`; the stream ends with `data: [DONE]` (`stream_options.include_usage` adds a final usage chunk; reference `stream_options`, `usage`).
- `delta` fields: `content`, `role`, `refusal`, `tool_calls`, and deprecated `function_call` (streaming-events reference → `delta` schema; installed SDK `openai/types/chat/chat_completion_chunk.py` `ChoiceDelta`).
- **Tool-call streaming:** `delta.tool_calls` is an array keyed by `index`; the first delta of a call carries `id`, `type`, `function.name`, and **subsequent deltas carry only incremental `function.arguments` fragments** — the caller must accumulate argument fragments per index until `finish_reason: "tool_calls"`. This is exactly the guide's "Accumulating tool_call deltas" pattern and is confirmed in DeepSeek's streaming schema: "The first chunk of each tool call carries the `id`, `type` and `function` fields; subsequent chunks only carry the function arguments" (https://api-docs.deepseek.com/api/create-chat-completion → streaming response).

**Reasoning / thinking content — the speech-bubble feed:**

- **OpenAI's own Chat Completions schema has no reasoning field.** `delta` contains only `content/role/refusal/tool_calls/function_call`; reasoning tokens are counted in `usage.completion_tokens_details.reasoning_tokens` but not exposed as streamed text (streaming-events reference; `completion_tokens_details`). OpenAI's visible "thinking" stream lives in the Responses API events (`reasoning` item types), which generic OpenAI-compatible providers don't serve.
- **OpenAI-compatible providers surface it as a non-standard extra field: `delta.reasoning_content`** (and `message.reasoning_content` in non-streaming). DeepSeek documents exactly this for thinking mode: `reasoning_content` on both the assistant message and the stream delta, described as "The reasoning contents of the assistant message, before the final answer" (https://api-docs.deepseek.com/api/create-chat-completion → Responses → `message` / streaming `delta`).
- **How Clippy reads it:** the SDK's pydantic models use `extra="allow"` (`openai/_models.py:118-120`), so `delta.reasoning_content` passes through as an extra attribute on `ChatCompletionChunk`/`ChoiceDelta` even though it isn't in the typed schema. Pattern: accumulate `chunk.choices[0].delta.reasoning_content` (if present) into the "thinking" bubble text, and `delta.content` into the main text — the reasoning stream precedes the answer, which matches the ticket's "thinking shows in the bubble" demo. Qwen-family endpoints use the same `reasoning_content` convention; Clippy should read it defensively (`getattr(delta, "reasoning_content", None)`) because OpenAI itself will never send it.

---

## 4. SKILL.md → callable tool: how the agent-skill format maps onto a JSON-schema tool

**The agent-skill format (primary spec: https://agentskills.io/specification.md; directory conventions + progressive disclosure: https://agentskills.io/home.md):**

A skill is a folder with `SKILL.md` (YAML frontmatter + Markdown body) and optional `scripts/` (executable code), `references/` (docs), `assets/` (templates/data). Frontmatter fields defined by the spec:

| field | required | constraints | relevant to tool exposure |
|---|---|---|---|
| `name` | yes | 1–64 chars, `a-z0-9` + hyphens, matches folder name | becomes the tool/function name |
| `description` | yes | 1–1024 chars, "what it does and when to use it" | becomes the tool `description` |
| `license` | no | — | — |
| `compatibility` | no | 1–500 chars | may gate exposure per endpoint |
| `metadata` | no | string→string map only | could carry hints, **no JSON-schema params** |
| `allowed-tools` | no | space-separated pre-approved tools (experimental) | pre-approval list, not params |

Notable: **the spec defines parameter-schema-like fields only via `metadata` (string→string), and it has no invocation-allowance field** such as `disable-model-invocation`. Progressive disclosure (load name+description ~100 tokens at startup; full body on activation; resources on demand) is explicitly designed to keep context cheap — exactly the right property for a tools array that is billed as input tokens.

**The local skills (`/Users/petehaughie/.agents/skills/`), read to ground the mapping in reality:**

- `research/SKILL.md` — frontmatter `name`, `description` only (no disable flag) → model-invocable.
- `wayfinder/SKILL.md` — `name`, `description`, `disable-model-invocation: true` → user-invoked only.
- `handoff/SKILL.md` — `name`, `description`, `argument-hint: "…"`, `disable-model-invocation: true` → user-invoked; `argument-hint` describes what a human passes to it.
- `grill-with-docs/SKILL.md` — `description`, `disable-model-invocation: true` → user-invoked.

`disable-model-invocation` and `argument-hint` are **vendor extensions**, not part of the agentskills.io spec; opencode's own skill docs recognize only `name/description/license/compatibility/metadata` and state "Unknown frontmatter fields are ignored" (https://opencode.ai/docs/skills → "Write frontmatter"). So Clippy must pick its own convention for these extension fields (recommendation below).

**The mapping (what Clippy does per skill at startup):**

```
SKILL.md                 →  tools[i] = {
  name (frontmatter)         type: "function",
  description (frontmatter)  function: {
                               name: <skill name>,              # spec name rules (a-z0-9 + "-") are a subset of the
                                                               # API's allowed [a-zA-Z0-9_-] ≤64 — valid as-is
                               description: <skill description> # spec: "what it does and when to use it" == the API's
                                                               # definition: "details on when and how to use the function"
                               parameters: {
                                 type: "object",
                                 properties: {
                                   request: {                  # single free-text arg; the spec defines no structured params
                                     type: "string",
                                     description: <argument-hint, if present, else "Describe the task to perform">,
                                   },
                                 },
                                 required: ["request"],
                                 additionalProperties: false,
                               },
                             },
                          }
  scripts/ + references/ + assets/  →  the tool's IMPLEMENTATION
```

Key mapping points, cited:

1. **Frontmatter `name` + `description` → `function.name` + `function.description`.** The agent-skill `description` contract ("Describes what the skill does and when to use it", spec § description) is semantically identical to the API's `description` ("A description of what the function does, used by the model to choose when and how to call the function", chat reference → `FunctionDefinition`; guide "Best practices for defining functions" says to put "when (and when not)" guidance there). Note the API caps tool names at 64 (OpenAI) / 128 (DeepSeek); spec caps skill names at 64 — compatible.
2. **There are no structured parameters in the skill spec**, so the practical tool signature is a single free-text argument (e.g. `request`), carrying a prompt that names the skill. The payload Clippy feeds to the skill is: the full `SKILL.md` body (instructions stay out of the tool description to bound per-request tokens — guide "Token Usage": function definitions are injected into the request and billed as input tokens; specs' progressive-disclosure exists to keep exactly this small).
3. **`scripts/` + `references/` + `assets/` are the implementation.** Agentskills.io: "scripts/ Optional: executable code … agents follow the instructions, optionally executing bundled code or loading referenced files" (home) / spec "Optional directories". So a skill tool call = Clippy loads the folder, and either (a) runs the SKILL.md procedures itself with Clippy's built-in tools, or (b) for a heavy skill such as wayfinder, delegates to a sub-agent (a separate Pi instance per the map's standing preference — `wayfinder/map.md` "Notes": "subagent = separate Pi instance"). The result is returned as the `role: "tool"` message string. `disable-model-invocation: true` skills (wayfinder, handoff, grill-with-docs) must **not** be put in the `tools` array — only model-safe skills (research) cross the boundary.
4. **`argument-hint` (vendor extension, present in `handoff/SKILL.md`) is the natural `request` parameter description** — "What will the next session be used for?" — mirroring what the model should put in the free-text argument.
5. **Progressive disclosure ↔ tools budget:** keep few tools (guide: "fewer than 20 functions available at the start of a turn … soft suggestion"; "Token Usage" — descriptions inflate input tokens). The spec's 1024-char description cap and 5000-token/500-line SKILL.md guidance keep a tool small.

---

## 5. Gotchas (learning from the reference docs)

- **`base_url` handling.** SDK order: constructor `base_url` → `OPENAI_BASE_URL` env → `https://api.openai.com/v1` (`openai/_client.py:212-228`). OpenAI's default includes `/v1`; providers differ (DeepSeek's is `https://api.deepseek.com`, and its quickstart uses the OpenAI SDK with that base: https://api-docs.deepseek.com/). Keep the base URL configurable and pass it explicitly — do not rely on the default for non-OpenAI endpoints.
- **Dummy `api_key` for local endpoints.** The SDK always attaches `Authorization: Bearer {api_key}` when a key is set (`openai/_client.py:455-465`). Local OpenAI-compatible servers (vLLM/Ollama/LM Studio-style) accept any non-empty string, so pass e.g. `"clippy-local"`; a missing/empty key must be avoided because the SDK then suppresses the header.
- **`tool_choice` enforcement.** Values and semantics (`none`/`auto`/`required`/named `{"type":"function","function":{"name":…}}`): chat reference → `tool_choice`. DeepSeek gotcha: **`required` and named tool choices return HTTP 400 in thinking mode** — disable thinking first or stick to `auto` (https://api-docs.deepseek.com/api/create-chat-completion → `tool_choice`). Clippy should treat forced choices as best-effort per endpoint.
- **Parallel tool calls.** A single response can contain several `tool_calls` (guide "Parallel function calling"); the loop must fan out and append one `role:"tool"` message per `tool_call_id`. `parallel_tool_calls: false` forces 0-or-1 if a given endpoint misbehaves with parallel calls (chat reference → `parallel_tool_calls`).
- **`max_tokens` vs `max_completion_tokens`.** OpenAI has deprecated `max_tokens` for reasoning-model outputs in favor of `max_completion_tokens` (chat reference → `max_tokens`/`max_completion_tokens`; the latter counts reasoning + visible tokens). OpenAI-compatible providers (DeepSeek) still document `max_tokens` and default it (8K plain / 64K thinking here: https://api-docs.deepseek.com/api/create-chat-completion → `max_tokens`). Send the field the configured provider documents — provider-aware, default sensible cap (e.g. 2048) so a single tool round-trip can't run away.
- **Tools-array schema surface (OpenAI-compatible variance).** Some OpenAI-compatible endpoints support only `type: "function"` tools (DeepSeek: "Currently, only functions are supported as a tool"; also requires tool names unique, ≤128: api-docs.deepseek.com). OpenAI itself documents non-strict-by-default for Chat Completions; `strict: true` requires `additionalProperties: false` + all props `required` or the request is rejected (function-calling guide "Strict mode"). Clippy's generated skill-tool schema (single required string + `additionalProperties: false`) is strict-mode-safe everywhere.
- **Unknown/extra response fields.** The SDK's models are `extra="allow"`, so provider extensions like `reasoning_content` survive untouched (`openai/_models.py:118-120`) — read them with `getattr`, and be ready to echo provider-specific assistant fields back into the next completion (guide's reasoning-items note).
- **Streaming is SSE.** Generic servers emit `data: {…}` lines and terminate with `data: [DONE]` (streaming-events reference; DeepSeek streaming example shows the same wire format, https://api-docs.deepseek.com/api/create-chat-completion → streaming). The SDK's `Stream` handles SSE decoding, but a proxy/inference-server quirk to watch: some local servers buffer chunks, so the bubble can appear to "pulse" — flush on your side.

---

## Recommended stack

- **Loop library:** official `openai` Python SDK — verified **2.36.0** installed here. Use `client.chat.completions.create` (Chat Completions, not Responses), constructing the client per provider with `OpenAI(api_key=…, base_url=…)`. Streaming via the returned `Stream[ChatCompletionChunk]`. No LangChain/LangGraph; no raw httpx.
- **Tools loop:** hand-rolled ~40-line loop: send messages+tools → read `message.tool_calls` → execute (see mapping) → echo assistant message + append `role:"tool"` results → repeat until no tool calls. Handle parallel calls; guard with a max-rounds cap.
- **Streaming/thinking:** accumulate `delta.content` for the reply and `delta.reasoning_content` (if present; `getattr`-safe) for the speech-bubble thinking feed.
- **Skill-as-tool:** a skill folder (name/description/`disable-model-invocation` frontmatter, optional scripts+references) turns into one `type:"function"` tool: frontmatter `name`→function `name`, `description`→function `description`, single free-text `request` parameter, SKILL.md body + scripts/references as the implementation. Skills with `disable-model-invocation: true` are excluded from the `tools` array.

## SKILL.md → tool mapping (summary)

| SKILL.md / skill dir | tool JSON / implementation |
|---|---|
| frontmatter `name` | `function.name` (valid: spec charset ⊆ API charset; ≤64) |
| frontmatter `description` | `function.description` ("what it does **and when to use it**") |
| `argument-hint` (vendor ext., e.g. handoff) | description of the `request` free-text parameter |
| no structured params in spec | `request: {"type":"string"}` — the only parameter |
| `disable-model-invocation: true` (vendor ext., e.g. wayfinder/handoff/grill-with-docs) | NOT exposed as a tool; user-invocation-only |
| `scripts/` `references/` `assets/` | the tool implementation: run SKILL.md procedures in-process or delegate (sub-agent per map.md) |
| SKILL.md body | loaded on invocation, not baked into the tool description (token budget) |

## Open questions / risks

- **Which provider/model** sits behind Clippy's endpoint is still un-chosen (`wayfinder/map.md` "Not yet specified"). `reasoning_content` streaming (the bubble feed) only exists on providers with a thinking mode — confirm the concrete provider emits it before designing the bubble around it.
- **Delegation semantics of a skill-as-tool**: in-process (Clippy executes SKILL.md procedures with its own tools) vs sub-agent (separate Pi instance, per the map's preference). The tool result string differs a lot (inline text vs sub-agent event summary), and the map's "sub-clippy articulates current thinking" question is open.
- **Tool budget & context:** tools are billed as input tokens; a directory of skills could exceed the "~20 tools" soft guidance. Need a per-session whitelist (which skills are model-callable) — tied to the `disable-model-invocation` policy decision.
- **`max_tokens` vs `max_completion_tokens` ambiguity** across endpoints; resolve per-provider at config time.
- **`tool_choice` + thinking-mode 400s** (DeepSeek) mean the loop should not force tool calls for reasoning-capable endpoints.
- **Vendor extension drift**: `disable-model-invocation`/`argument-hint` aren't in the agentskills.io spec; if the spec gains these fields later, Clippy's convention should follow it.