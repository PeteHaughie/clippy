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

import time
import traceback

import pyglet  # noqa: F401  (import parity with controller)

from .controller import TOOL_HINTS
from .events import AgentEventRouter, EventSink
from .moods import Moods
from .model import PRIME_CONVERSATION
from .statemachine import StateMachine

#: Minimum interval between stream pushes to the pane. The router re-sends the
#: full accumulated buffer on every delta; serializing and evaluating that in
#: the webview per token is O(n²), so coalesce here and flush the latest text on
#: a frame tick (and always before a bubble is finalized).
STREAM_MIN_INTERVAL = 0.05


class PrimeController(EventSink):
    def __init__(self, shell, brain, moods: Moods | None = None):
        self.shell = shell
        self.brain = brain
        self.moods = moods or shell.avatar.moods
        self.router = AgentEventRouter(self)
        self.sm = StateMachine(PRIME_CONVERSATION)
        #: Optional pane wiring (set by the app). When present, the thinking/
        #: answer deltas stream into a live markdown bubble in the pane.
        self.pane = None
        #: Optional callbacks wired by the app (pane integration).
        self.on_answer = None      # on_assistant_text(final_text) -> callable
        self.on_ui_request = None  # on_extension_ui_request(event) -> callable
        #: Coalesced stream push: (kind, latest_full_text) awaiting the next
        #: allowed push, and the monotonic time of the last push.
        self._stream_pending: tuple[str, str] | None = None
        self._stream_last = 0.0

    # ------------------------------------------------------------- control

    def update(self, dt: float):
        try:
            self._drain()
        except Exception:
            print("[prime] update error (kept alive):", flush=True)
            traceback.print_exc()
        # Flush any coalesced stream text on the frame tick, even if no new
        # delta arrived, so a pause still shows the latest reasoning/answer.
        self._flush_stream()

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

    def stream_start(self):
        self._stream_pending = None
        self._stream_last = 0.0
        if self.pane is not None:
            self.pane.stream_start()

    def stream_thinking(self, text: str):
        self._stream_pending = ("thinking", text)
        self._flush_stream()

    def stream_text(self, text: str):
        self._stream_pending = ("text", text)
        self._flush_stream()

    def _flush_stream(self, force: bool = False):
        """Push the latest coalesced stream text, at most every
        ``STREAM_MIN_INTERVAL`` (or immediately when ``force``)."""
        if self.pane is None or self._stream_pending is None:
            return
        now = time.monotonic()
        if not force and (now - self._stream_last) < STREAM_MIN_INTERVAL:
            return
        kind, text = self._stream_pending
        self._stream_pending = None
        self._stream_last = now
        if kind == "thinking":
            self.pane.stream_thinking(text)
        else:
            self.pane.stream_text(text)

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
        # Only a *final* assistant message is the turn's answer. A ``toolUse``
        # message means the model is still working; error/aborted are handled
        # by retry/exit. Acting on those would finalize the stream bubble early
        # and pair memory with partial text.
        if stop_reason not in AgentEventRouter.FINAL_STOP_REASONS:
            return
        # Make sure the last reasoning/answer text is in the pane before the
        # final text replaces the answer.
        self._flush_stream(force=True)
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
        # Close the run's bubble if the final message_end did not (e.g. a turn
        # that produced only thinking). Passing "" leaves the streamed answer
        # untouched, so it never duplicates the answer that message_end showed.
        if self.pane is not None:
            self._flush_stream(force=True)
            self.pane.stream_end("")

    def ui_request(self, ev):
        self.shell.dialog_pending = True
        if self.on_ui_request:
            self.on_ui_request(ev)

    def waiting(self):
        self.shell.express("listening")
        self.shell.set_bubble("(waiting for you…)")

    def exit(self, code: int):
        print(f"[prime] brain exited ({code})", flush=True)
        # Back to idle so scheduled brain actions are not blocked on a dead
        # process, and close any open stream bubble.
        self.sm.fire("exit")
        if self.pane is not None:
            self._flush_stream(force=True)
            self.pane.stream_end("")
        self.shell.express("alert")
        self.shell.set_bubble(f"brain exited ({code})")

    def unparseable(self, raw: str):
        self.shell.set_bubble("(unparseable event from brain)")