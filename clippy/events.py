"""Normalisation and shared routing for Pi's event streams (phase 1).

Pi ships the *same logical event* under two wire shapes:

* RPC / brain:  ``{"type": "message_update", "assistantMessageEvent": {"type": "thinking_delta", ...}}``
* ``--mode json``: ``{"type": "assistant_message_event", "eventType": "thinking_delta", ...}``

:func:`normalize` maps **either** shape onto the typed ``Ev`` catalog in
:mod:`clippy.model` — one definition of truth, so the ``type`` vs ``eventType``
routing bug class (ticket 019) cannot recur. :class:`AgentEventRouter` then
owns the shared accumulation (thinking/text buffers, bubble text, tool
bubbles) that :class:`clippy.prime.PrimeController` and
:class:`clippy.controller.SubClippyController` used to duplicate; controllers
implement :class:`EventSink` and react, they don't re-parse events.
"""

from __future__ import annotations

import json

from .model import (
    AgentEnd,
    AgentSettled,
    AgentStart,
    Ev,
    Exit,
    MessageEnd,
    MessageStart,
    Response,
    TextDelta,
    ThinkingDelta,
    ThinkingEnd,
    ToolCallStart,
    ToolExecEnd,
    ToolExecStart,
    TurnStart,
    UiPromptStart,
    UiRequest,
    Unknown,
)


def extract_text(message: dict) -> str:
    """Join the plain-text blocks of an assistant message."""
    content = (message or {}).get("content") or []
    return "".join(
        b.get("text", "")
        for b in content
        if isinstance(b, dict) and b.get("type") == "text"
    ).strip()


def extract_result_text(result: dict) -> str:
    """Join the text blocks of a tool-execution result."""
    content = (result or {}).get("content") or []
    return " ".join(
        b.get("text", "")
        for b in content
        if isinstance(b, dict) and b.get("type") == "text"
    ).strip()


def _update_event(ev: dict) -> Ev:
    """Normalise a delta/markup event. Works for both the nested
    ``assistantMessageEvent`` dict and a top-level ``assistant_message_event``."""
    kind = ev.get("eventType") or ev.get("type")
    if kind == "thinking_delta":
        return ThinkingDelta(delta=ev.get("delta", ""))
    if kind == "thinking_end":
        return ThinkingEnd(content=ev.get("content", ""))
    if kind == "text_delta":
        return TextDelta(delta=ev.get("delta", ""))
    if kind == "toolcall_start":
        return ToolCallStart(tool=ev.get("toolName", ""))
    if kind in ("message_end", "text_end"):
        return MessageEnd(stop_reason=ev.get("stopReason", ""))
    return Unknown(raw=json.dumps(ev))


def normalize(raw: dict) -> Ev:
    """Map one raw Pi JSONL event onto the typed catalog."""
    if not isinstance(raw, dict):
        return Unknown(raw=str(raw))
    t = raw.get("type")
    if t == "agent_start":
        return AgentStart()
    if t == "agent_settled":
        return AgentSettled()
    if t in ("turn_start", "turn_end"):
        return TurnStart()
    if t == "message_start":
        return MessageStart(role=(raw.get("message") or {}).get("role", ""))
    if t == "message_end":
        msg = raw.get("message") or {}
        return MessageEnd(
            role=msg.get("role", ""),
            stop_reason=msg.get("stopReason", ""),
            text=extract_text(msg),
        )
    if t == "message_update":
        return _update_event(raw.get("assistantMessageEvent") or {})
    if t == "assistant_message_event":
        return _update_event(raw)
    if t == "tool_execution_start":
        return ToolExecStart(tool=raw.get("toolName", ""), args=raw.get("args") or {})
    if t == "tool_execution_end":
        return ToolExecEnd(
            tool=raw.get("toolName", ""),
            result_text=extract_result_text(raw.get("result")),
            is_error=bool(raw.get("isError")),
        )
    if t == "agent_end":
        return AgentEnd(will_retry=bool(raw.get("willRetry")))
    if t == "extension_ui_request":
        return UiRequest(
            id=raw.get("id", ""),
            method=raw.get("method", ""),
            payload={k: v for k, v in raw.items() if k not in ("type", "id")},
        )
    if t == "ui_prompt_start":
        return UiPromptStart()
    if t == "response":
        return Response(
            command=raw.get("command", ""),
            success=bool(raw.get("success")),
            data=raw.get("data") or {},
        )
    if t in ("brain_exit", "sub_exit"):
        return Exit(code=raw.get("exit_code", 0))
    if t == "unparseable":
        return Unknown(raw=raw.get("raw", ""))
    return Unknown(raw=json.dumps(raw))


# ------------------------------------------------------------------ sink

class EventSink:
    """Reactions to normalised events. The router does the parsing and buffer
    bookkeeping; a sink turns each semantic call into shell/pane/lifecycle
    effects. Every method is a no-op by default."""

    def agent_start(self):
        pass

    def turn_started(self):
        pass

    def thinking(self, text: str):
        pass

    def text(self, text: str):
        pass

    def tool_start(self, tool: str):
        pass

    def tool_end(self, ev: ToolExecEnd):
        pass

    def message_end(self, stop_reason: str, text: str):
        pass

    def retry(self):
        pass

    def settled(self):
        pass

    def ui_request(self, ev: UiRequest):
        pass

    def waiting(self):
        pass

    def exit(self, code: int):
        pass

    def unparseable(self, raw: str):
        pass


# ------------------------------------------------------------------ router

class AgentEventRouter:
    """Shared event accumulation for a conversation's event stream.

    Owns the ``thinking`` / ``text`` buffers and the bubble-worthy substrings,
    then hands each semantic event to ``sink``. Both the prime and worker
    controllers embed one of these — the parsing duplication is gone.
    """

    #: Bubble preview length (thinking/answer slice shown above the avatar).
    BUBBLE_LEN = 140

    def __init__(self, sink: EventSink):
        self.sink = sink
        self.thinking = ""
        self.text = ""
        self._handlers = {
            "agent_start": self._on_agent_start,
            "turn_start": self._noop,
            "message_start": self._on_message_start,
            "thinking_delta": self._on_thinking_delta,
            "thinking_end": self._on_thinking_end,
            "text_delta": self._on_text_delta,
            "toolcall_start": self._on_tool_start,
            "tool_execution_start": self._on_tool_start,
            "tool_execution_end": self._on_tool_end,
            "message_end": self._on_message_end,
            "agent_end": self._on_agent_end,
            "agent_settled": self._on_agent_settled,
            "extension_ui_request": self._on_ui_request,
            "ui_prompt_start": self._on_ui_prompt_start,
            "response": self._noop,
            "exit": self._on_exit,
            "unknown": self._on_unknown,
        }

    def feed(self, ev: Ev):
        handler = self._handlers.get(ev.kind)
        if handler is not None:
            handler(ev)

    def feed_raw(self, raw: dict):
        self.feed(normalize(raw))

    def _noop(self, ev):
        pass

    def _on_message_start(self, ev: MessageStart):
        if ev.role == "assistant":
            self.thinking = ""
            self.text = ""
            self.sink.turn_started()

    def _on_thinking_delta(self, ev: ThinkingDelta):
        self.thinking += ev.delta
        self.sink.thinking(self.thinking.strip()[-self.BUBBLE_LEN:] or "(thinking)")

    def _on_thinking_end(self, ev: ThinkingEnd):
        self.thinking = (ev.content or self.thinking).strip()
        if self.thinking:
            self.sink.thinking(self.thinking[-self.BUBBLE_LEN:])

    def _on_text_delta(self, ev: TextDelta):
        self.text += ev.delta
        self.sink.text(self.text.strip()[-self.BUBBLE_LEN:] or "(answering)")

    def _on_tool_start(self, ev):
        self.sink.tool_start(ev.tool)

    def _on_tool_end(self, ev: ToolExecEnd):
        self.sink.tool_end(ev)

    def _on_message_end(self, ev: MessageEnd):
        if ev.role and ev.role != "assistant":
            return
        self.sink.message_end(ev.stop_reason, ev.text or self.text.strip())

    def _on_agent_end(self, ev: AgentEnd):
        if ev.will_retry:
            self.sink.retry()

    def _on_agent_settled(self, ev):
        self.sink.settled()

    def _on_ui_request(self, ev: UiRequest):
        self.sink.ui_request(ev)

    def _on_ui_prompt_start(self, ev):
        self.sink.waiting()

    def _on_exit(self, ev: Exit):
        self.sink.exit(ev.code)

    def _on_unknown(self, ev: Unknown):
        self.sink.unparseable(ev.raw)

    def _on_agent_start(self, ev):
        self.sink.agent_start()