"""Consent-gated worker escalation: card routing and decision mapping."""

import types
import unittest
from unittest import mock

from clippy.session import ESCALATED_TOOLS, Session
from clippy.subagent import SANDBOX_TOOLS


class FakePane:
    can_confirm = True

    def __init__(self):
        self.requests = []
        self.messages = []

    def ui_request(self, ev):
        self.requests.append(ev)

    def add_message(self, role, text):
        self.messages.append((role, text))

    def summon(self):
        pass


def make_session(*, mode="build", can_confirm=True):
    s = Session.__new__(Session)
    s._host_dialogs = {}
    s.mode = mode
    s.sent = []
    s.pane = FakePane()
    s.pane.can_confirm = can_confirm
    s.shell = types.SimpleNamespace(
        dialog_pending=False, set_bubble=lambda text: None
    )
    s.brain = types.SimpleNamespace(send=lambda cmd: s.sent.append(cmd))
    return s


class HostDialogRoutingTests(unittest.TestCase):
    @mock.patch("clippy.session.notify")
    def test_host_dialog_resolves_locally_not_to_brain(self, _notify):
        s = make_session()
        got = []
        rid = s._host_dialog("review", "Title", "Message", got.append)
        self.assertEqual(len(s.pane.requests), 1)
        self.assertEqual(s.pane.requests[0].method, "review")
        self.assertEqual(s.pane.requests[0].id, rid)
        self.assertTrue(s.shell.dialog_pending)

        s.ui_response(rid, {"decision": "allow"})
        self.assertEqual(got, [{"decision": "allow"}])
        self.assertFalse(s.shell.dialog_pending)
        self.assertEqual(s.sent, [])  # never forwarded to the prime brain

    @mock.patch("clippy.session.notify")
    def test_unknown_id_still_forwards_to_brain(self, _notify):
        s = make_session()
        s.ui_response("pi-123", {"confirmed": True})
        self.assertEqual(len(s.sent), 1)
        self.assertEqual(s.sent[0]["id"], "pi-123")
        self.assertTrue(s.sent[0]["confirmed"])

    @mock.patch("clippy.session.notify")
    def test_host_dialog_notifies(self, notify):
        s = make_session()
        s._host_dialog("review", "Title", "Please approve", lambda p: None)
        notify.assert_called_once()


class EscalationDecisionTests(unittest.TestCase):
    @mock.patch("clippy.session.notify")
    def _ask(self, _notify, **kwargs):
        s = make_session(**kwargs)
        runs = []
        s._confirm_escalation("do it", lambda tools, t: runs.append((tools, t)))
        return s, runs

    def test_allow_grants_escalated_tools(self):
        s, runs = self._ask()
        s.ui_response(s.pane.requests[0].id, {"decision": "allow"})
        self.assertEqual(runs, [(ESCALATED_TOOLS, "do it")])

    def test_deny_falls_back_to_read_only(self):
        s, runs = self._ask()
        s.ui_response(s.pane.requests[0].id, {"decision": "deny"})
        self.assertEqual(runs, [(SANDBOX_TOOLS, "do it")])

    def test_suggest_appends_guidance_and_stays_read_only(self):
        s, runs = self._ask()
        s.ui_response(
            s.pane.requests[0].id,
            {"decision": "suggest", "suggestion": "use /tmp only"},
        )
        self.assertEqual(runs[0][0], SANDBOX_TOOLS)
        self.assertIn("do it", runs[0][1])
        self.assertIn("use /tmp only", runs[0][1])

    def test_dismiss_runs_nothing(self):
        s, runs = self._ask()
        s.ui_response(s.pane.requests[0].id, {"decision": "dismiss"})
        self.assertEqual(runs, [])

    def test_no_confirmable_pane_fails_safe(self):
        s, runs = self._ask(can_confirm=False)
        self.assertEqual(s.pane.requests, [])
        self.assertEqual(runs, [(SANDBOX_TOOLS, "do it")])


class StartDelegationTests(unittest.TestCase):
    def _spy(self, s):
        spawned = []
        s._spawn_delegation = lambda task, tools, source, on_complete=None: (
            spawned.append((tools, task)) or True
        )
        s.brain.steer = lambda msg: None
        return spawned

    def test_build_mode_asks_and_allows(self):
        s = make_session(mode="build")
        spawned = self._spy(s)
        s._start_delegation("task")
        self.assertEqual(len(s.pane.requests), 1)  # card raised
        self.assertEqual(spawned, [])  # not spawned until answered
        s.ui_response(s.pane.requests[0].id, {"decision": "allow"})
        self.assertEqual(spawned, [(ESCALATED_TOOLS, "task")])

    def test_sandbox_mode_does_not_ask(self):
        s = make_session(mode="sandbox")
        spawned = self._spy(s)
        s._start_delegation("task")
        self.assertEqual(s.pane.requests, [])
        self.assertEqual(spawned, [(SANDBOX_TOOLS, "task")])

    def test_explicit_elevated_asks_in_sandbox(self):
        s = make_session(mode="sandbox")
        spawned = self._spy(s)
        s._start_delegation("task", elevated=True)
        self.assertEqual(len(s.pane.requests), 1)
        s.ui_response(s.pane.requests[0].id, {"decision": "allow"})
        self.assertEqual(spawned, [(ESCALATED_TOOLS, "task")])


if __name__ == "__main__":
    unittest.main()
