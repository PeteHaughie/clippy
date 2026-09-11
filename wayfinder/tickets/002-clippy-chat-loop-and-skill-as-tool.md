---
id: 002
title: Clippy's own chat loop and skill-as-tool
type: research
status: open
assignee:
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