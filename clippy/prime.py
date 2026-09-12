"""Prime Clippy lifecycle: consume the brain's (Pi RPC) event queue on the
main thread and drive the shell's moods + speech bubble for a live ongoing
conversation.

Unlike :class:`clippy.controller.SubClippyController` (one-shot sub-clippy that
celebrates → explodes → dismisses), the prime is persistent: it listens, works,
answers, and returns to idle, staying ready for the next turn. Hooks let the
pane (ticket 016) render answers and approval cards.
"""

import pyglet  # noqa: F401  (import parity with controller)

from .controller import TOOL_HINTS
from .moods import Moods


def extract_text(message: dict) -> str:
    """Join the plain-text blocks of an assistant message."""
    content = message.get("content") or []
    parts = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "".join(parts).strip()


class PrimeController:
    def __init__(self, shell, brain, moods: Moods | None = None):
        self.shell = shell
        self.brain = brain
        self.moods = moods or shell.avatar.moods
        self.state = "idle"  # idle|working|answering
        self._thinking = ""
        self._text = ""
        self._last_stop_reason = None
        #: Optional callbacks wired by the app (pane integration).
        self.on_answer = None      # on_assistant_text(final_text) -> callable
        self.on_ui_request = None  # on_extension_ui_request(event) -> callable

    # ------------------------------------------------------------- events

    def update(self, dt: float):
        self._drain()

    def _drain(self):
        q = self.brain.queue
        while True:
            try:
                event = q.get_nowait()
            except Exception:
                break
            self._handle(event)

    def _handle(self, event):
        etype = event.get("type")
        if etype == "brain_exit":
            self.shell.express("alert")
            self.shell.set_bubble(f"brain exited ({event.get('exit_code')})")
        elif etype == "unparseable":
            self.shell.set_bubble("(unparseable event from brain)")
        elif etype == "message_start":
            role = (event.get("message") or {}).get("role")
            if role == "assistant":
                self._thinking = ""
                self._text = ""
                self.shell.express("thinking")
        elif etype == "message_update":
            self._handle_update(event.get("assistantMessageEvent") or {})
        elif etype == "message_end":
            self._handle_message_end(event.get("message") or {})
        elif etype == "tool_execution_start":
            self._on_tool_start(event)
        elif etype == "tool_execution_end":
            self._on_tool_end(event)
        elif etype == "agent_start":
            self.shell.express("listening")
            self.shell.set_bubble("(working…)")
        elif etype == "agent_end":
            if event.get("willRetry"):
                self.shell.express("thinking")
                self.shell.set_bubble("retrying…")
        elif etype == "agent_settled":
            self.shell.express("idle")
            if not self._text:
                self.shell.set_bubble("(ready)")
        elif etype == "extension_ui_request":
            if self.on_ui_request:
                self.on_ui_request(event)
        elif etype in ("ui_prompt_start",):
            self.shell.express("listening")
            self.shell.set_bubble("(waiting for you…)")
        elif etype == "response":
            pass  # command ack; nothing to show

    def _handle_update(self, ev):
        kind = ev.get("type") or ev.get("eventType")
        if kind == "thinking_delta":
            self._thinking += ev.get("delta", "")
            self.shell.express("thinking")
            self.shell.set_bubble(self._thinking.strip()[-140:] or "(thinking)")
        elif kind == "thinking_end":
            self._thinking = (ev.get("content") or self._thinking).strip()
            if self._thinking:
                self.shell.set_bubble(self._thinking[-140:])
        elif kind == "text_delta":
            self._text += ev.get("delta", "")
            self.shell.express("thinking")
            self.shell.set_bubble(self._text.strip()[-140:] or "(answering)")
        elif kind == "toolcall_start":
            tool = ev.get("toolName", "")
            hint = TOOL_HINTS.get(tool, "create")
            self.shell.express("working", hint=hint)
            self.shell.set_bubble(f"working… ({tool})")

    def _handle_message_end(self, message):
        if message.get("role") != "assistant":
            return
        self._last_stop_reason = message.get("stopReason")
        text = extract_text(message)
        if text:
            self._text = text
            self.shell.set_bubble(text[-140:])
            if self.on_answer:
                self.on_answer(text)

    def _on_tool_start(self, event):
        tool = event.get("toolName", "")
        hint = TOOL_HINTS.get(tool, "create")
        self.shell.express("working", hint=hint)
        self.shell.set_bubble(f"working… ({tool})")

    def _on_tool_end(self, event):
        self.shell.express("thinking")
        result = event.get("result") or {}
        content = result.get("content") or []
        text = " ".join(
            b.get("text", "")
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        ).strip()
        if text:
            self.shell.set_bubble(text[-140:])