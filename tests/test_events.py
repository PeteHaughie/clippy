"""Event routing: final-answer gating and one stream bubble per run."""

import types
import unittest
from unittest import mock

from clippy.events import AgentEventRouter, EventSink
from clippy.model import (
    AgentSettled,
    AgentStart,
    MessageEnd,
    MessageStart,
    TextDelta,
    ThinkingDelta,
)
from clippy.moods import Moods


class RecordingSink:
    """Duck-typed sink: every method access returns a recorder."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _record(*args):
            self.calls.append((name, args))
        return _record


class RouterStreamScopeTests(unittest.TestCase):
    def test_one_stream_per_agent_run(self):
        sink = RecordingSink()
        router = AgentEventRouter(sink)
        router.feed(AgentStart())
        router.feed(MessageStart(role="assistant"))
        router.feed(ThinkingDelta(delta="hmm"))
        router.feed(MessageStart(role="assistant"))  # tool-call turn
        router.feed(TextDelta(delta="partial"))
        router.feed(MessageEnd(role="assistant", stop_reason="toolUse", text="partial"))
        router.feed(MessageEnd(role="assistant", stop_reason="stop", text="final"))
        router.feed(AgentSettled())
        starts = [c for c in sink.calls if c[0] == "stream_start"]
        self.assertEqual(len(starts), 1, sink.calls)

    def test_new_run_opens_a_new_bubble(self):
        sink = RecordingSink()
        router = AgentEventRouter(sink)
        router.feed(AgentStart())
        router.feed(MessageStart(role="assistant"))
        router.feed(AgentSettled())
        router.feed(AgentStart())
        router.feed(MessageStart(role="assistant"))
        starts = [c for c in sink.calls if c[0] == "stream_start"]
        self.assertEqual(len(starts), 2, sink.calls)

    def test_message_end_reaches_sink_for_all_stop_reasons(self):
        # The router must still report toolUse/error so worker controllers can
        # track the terminal stop reason; only the *prime* gates on it.
        sink = RecordingSink()
        router = AgentEventRouter(sink)
        router.feed(MessageEnd(role="assistant", stop_reason="toolUse", text="x"))
        ends = [c for c in sink.calls if c[0] == "message_end"]
        self.assertEqual(len(ends), 1)
        self.assertEqual(ends[0][1][0], "toolUse")


class FakePane:
    def __init__(self):
        self.calls = []

    def stream_start(self):
        self.calls.append(("stream_start",))

    def stream_thinking(self, text):
        self.calls.append(("stream_thinking", text))

    def stream_text(self, text):
        self.calls.append(("stream_text", text))

    def stream_end(self, text):
        self.calls.append(("stream_end", text))


class FakeBrain:
    queue = None


class PrimeMessageEndTests(unittest.TestCase):
    def _controller(self):
        from clippy.prime import PrimeController

        shell = types.SimpleNamespace(
            avatar=types.SimpleNamespace(moods=Moods()),
            dialog_pending=False,
        )
        shell.express = lambda *a, **k: True
        shell.set_bubble = lambda text: None
        ctrl = PrimeController(shell, FakeBrain())
        ctrl.pane = FakePane()
        ctrl.answers = []

        # Mirror Session._on_answer: surface the final answer into the pane.
        def _answer(text):
            ctrl.answers.append(text)
            ctrl.pane.stream_end(text)

        ctrl.on_answer = _answer
        return ctrl

    def test_tool_use_is_not_a_final_answer(self):
        ctrl = self._controller()
        ctrl.router.feed(MessageEnd(role="assistant", stop_reason="toolUse", text="partial"))
        self.assertEqual(ctrl.answers, [])

    def test_stop_is_a_final_answer(self):
        ctrl = self._controller()
        ctrl.router.feed(MessageEnd(role="assistant", stop_reason="stop", text="final"))
        self.assertEqual(ctrl.answers, ["final"])

    def test_stream_pushes_are_coalesced(self):
        ctrl = self._controller()
        with mock.patch("clippy.prime.time.monotonic", return_value=1000.0):
            ctrl.stream_text("a")
            ctrl.stream_text("ab")
            ctrl.stream_text("abc")
        pushes = [c for c in ctrl.pane.calls if c[0] == "stream_text"]
        self.assertEqual(pushes, [("stream_text", "a")])
        with mock.patch("clippy.prime.time.monotonic", return_value=1001.0):
            ctrl._flush_stream()
        pushes = [c for c in ctrl.pane.calls if c[0] == "stream_text"]
        self.assertEqual(
            pushes, [("stream_text", "a"), ("stream_text", "abc")]
        )

    def test_exit_returns_prime_to_idle(self):
        ctrl = self._controller()
        ctrl.router.feed(AgentStart())  # turn_started -> working
        self.assertTrue(ctrl.sm.is_in("working"))
        ctrl.exit(1)
        self.assertTrue(ctrl.sm.is_in("idle"))

    def test_answer_is_not_duplicated_on_settle(self):
        ctrl = self._controller()
        ctrl.router.feed(AgentStart())
        ctrl.router.feed(MessageStart(role="assistant"))
        ctrl.router.feed(TextDelta(delta="final"))
        ctrl.router.feed(MessageEnd(role="assistant", stop_reason="stop", text="final"))
        ctrl.router.feed(AgentSettled())
        ends = [c for c in ctrl.pane.calls if c[0] == "stream_end"]
        # message_end finalizes with the text; settled closes with "" only.
        self.assertEqual(ends, [("stream_end", "final"), ("stream_end", "")])


if __name__ == "__main__":
    unittest.main()
