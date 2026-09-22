"""Worker tool-allowlist safety: a delegation is always at most sandboxed."""

import unittest

from clippy import subagent
from clippy.subagent import SANDBOX_TOOLS, PiSubAgent, SUB_SANDBOX_TOOLS
from clippy.session import resolve_worker_tools


class ResolveWorkerToolsTests(unittest.TestCase):
    def test_empty_everywhere_falls_back_to_sandbox(self):
        self.assertEqual(tuple(resolve_worker_tools((), None)), tuple(SANDBOX_TOOLS))

    def test_caller_tools_used_when_delegation_has_none(self):
        self.assertEqual(resolve_worker_tools((), ["read"]), ("read",))

    def test_delegation_tools_win(self):
        self.assertEqual(resolve_worker_tools(["write"], ["read"]), ("write",))

    def test_none_is_never_returned(self):
        self.assertTrue(resolve_worker_tools((), None))


class PiSubAgentGuardTests(unittest.TestCase):
    def test_none_tools_is_refused(self):
        with self.assertRaises(ValueError):
            PiSubAgent(task="t", tools=None)

    def test_sandbox_tools_reach_the_command_line(self):
        agent = PiSubAgent(task="t", tools=SANDBOX_TOOLS)
        cmd = agent._cmd()
        self.assertIn("--tools", cmd)
        self.assertEqual(cmd[cmd.index("--tools") + 1], ",".join(SANDBOX_TOOLS))

    def test_alias_is_the_same_list(self):
        self.assertEqual(SUB_SANDBOX_TOOLS, SANDBOX_TOOLS)
        self.assertIs(subagent.SANDBOX_TOOLS, subagent.SUB_SANDBOX_TOOLS)


if __name__ == "__main__":
    unittest.main()
