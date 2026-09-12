"""Prime Clippy lifecycle (phase 2, graph-model refactor).

Consume the prime's (Pi RPC) event stream on the main thread and drive the
shell's moods + speech bubble for a live ongoing conversation. Event parsing
and thinking/text accumulation live in the shared
:class:`clippy.events.AgentEventRouter`; this controller is an
:class:`clippy.events.EventSink` that reacts. The conversation phase is tracked
by :data:`clippy.model.PRIME_CONVERSATION` (idle → working → answering → idle).

Unlike the one-shot sub-clippy (:class:`clippy.controller.SubClippyController`),
the prime is persistent: it listens, works, answers, and returns to idle.
Hooks let the pane (ticket 016) render answers and approval cards.
"""

import pyglet  # noqa: F401  (import parity with controller)

from .controller import TOOL_HINTS
from .events import AgentEventRouter, EventSink
from .moods import Moods
from .model import PRIME_CONVERSATION
from .statemachine import StateMachine


class PrimeController(EventSink):
    def __init__(self, shell, brain, moods: Moods | None = None):
        self.shell = shell
        self.brain = brain
        self.moods = moods or shell.avatar.moods
        self.router = AgentEventRouter(self)
        self.sm = StateMachine(PRIME_CONVERSATION)
        #: Optional callbacks wired by the app (pane integration).
        self.on_answer = None      # on_assistant_text(final_text) -> callable
        self.on_ui_request = None  # on_extension_ui_request(event) -> callable

    # ------------------------------------------------------------- control

    def update(self, dt: float):
        self._drain()

    def _drain(self):
        q = self.brain.queue
        while True:
            try:
                raw = q.get_nowait()
            except Exception:
                break
            self.router.feed_raw(raw)

    # -------------------------------------------------------------- events

    def agent_start(self):
        self.sm.fire("turn_started")
        self.shell.express("listening")
        self.shell.set_bubble("(working…)")

    def turn_started(self):
        self.sm.fire("turn_started")
        self.shell.express("thinking")

    def thinking(self, text: str):
        self.shell.express("thinking")
        self.shell.set_bubble(text)

    def text(self, text: str):
        self.shell.express("thinking")
        self.shell.set_bubble(text)

    def tool_start(self, tool: str):
        hint = TOOL_HINTS.get(tool, "create")
        self.shell.express("working", hint=hint)
        self.shell.set_bubble(f"working… ({tool})")

    def tool_end(self, ev):
        self.shell.express("thinking")
        if ev.result_text:
            self.shell.set_bubble(ev.result_text[-140:])

    def message_end(self, stop_reason: str, text: str):
        self.sm.fire("answer")
        if text:
            self.shell.set_bubble(text[-140:])
            if self.on_answer:
                self.on_answer(text)

    def retry(self):
        self.sm.fire("retry")
        self.shell.express("thinking")
        self.shell.set_bubble("retrying…")

    def settled(self):
        self.sm.fire("settled")
        self.shell.express("idle")
        if not self.router.text:
            self.shell.set_bubble("(ready)")

    def ui_request(self, ev):
        self.shell.dialog_pending = True
        if self.on_ui_request:
            self.on_ui_request(ev)

    def waiting(self):
        self.shell.express("listening")
        self.shell.set_bubble("(waiting for you…)")

    def exit(self, code: int):
        self.shell.express("alert")
        self.shell.set_bubble(f"brain exited ({code})")

    def unparseable(self, raw: str):
        self.shell.set_bubble("(unparseable event from brain)")