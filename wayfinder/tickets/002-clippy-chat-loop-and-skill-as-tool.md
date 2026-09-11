---
id: 002
title: Clippy's own chat loop and skill-as-tool
type: research
status: closed
assignee: wayfinder
blocked_by: []
labels: [wayfinder:research]
---

## Question

What are the mechanics of Clippy's own chat loop, talking to an OpenAI-compatible endpoint from Python?

- Which OpenAI-compatible chat/function-calling libraries are current and reliable from Python (the official SDK, LangChain-lite, plain httpx)?
- How does an OpenAI-compatible tools/function-calling round-trip work end to end (tool schema → model → tool_choice → tool call → result feed-back)?
- How does an agent-skill `SKILL.md` (Markdown directions, optional scripts) map onto a callable tool — can the skill text become the tool description, and skill scripts the tool implementation?
- Streaming: what shape are token/event chunks, and can they feed the speech-bubble "articulates its thinking" effect?

Assets linked here. Resolution records the recommended chat-loop library, the SKILL.md→tool mapping, and any gotchas.

## Resolution

Findings asset: [research/chat-loop.md](/Users/petehaughie/Projects/clippy/research/chat-loop.md) (committed on `main`; throwaway branches merged).

**Loop library:** official `openai` Python SDK — verified **2.36.0** installed here. `client.chat.completions.create` (Chat Completions, not Responses — generic endpoints implement `/v1/chat/completions`). `base_url` + dummy `api_key` first-class for any OpenAI-compatible provider. No LangChain/LangGraph, no raw httpx.

**Tools loop:** hand-rolled ~40-line loop: send messages+tools → read `message.tool_calls` → execute → echo assistant message verbatim + append one `role:"tool"` message per `tool_call_id` → repeat until no `tool_calls`. Guard max rounds; `arguments` is a JSON string.

**Streaming/thinking feed:** `Stream[ChatCompletionChunk]` SSE; accumulate `delta.content` (answer) and `delta.reasoning_content` (thinking bubble) via `getattr`-safe read — `reasoning_content` is a non-standard provider extension (DeepSeek documents it), OpenAI never sends it. Bubble design must not assume it's present.

**SKILL.md → tool:** frontmatter `name`/`description` → `function.name`/`function.description`; single free-text `request` param (spec has no structured params; `argument-hint` becomes its description); `scripts/`+`references/` are the implementation. Skills with `disable-model-invocation: true` (wayfinder/handoff/grill-with-docs here) excluded from the `tools` array. Keep tool count low (~20 soft budget — tools billed as input tokens).

**Gotchas:** strict-mode-safe schema, `tool_choice` 400s on thinking-mode endpoints (DeepSeek), `max_tokens` vs `max_completion_tokens` per provider, extra-field passthrough (`extra="allow"`).