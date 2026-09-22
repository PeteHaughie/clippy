"""MCP plumbing: config normalisation, tool resolution, and session wiring."""

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

from clippy import mcp
from clippy.session import MCP_EXT, Session

FAKE_SERVER = str(Path(__file__).resolve().parent / "fake_mcp_server.py")

CONFIG = {
    "mcp": {
        "servers": {
            "pa": {
                "command": ["uv", "run", "server"],
                "env": {"FOO": "bar"},
                "prefix": "pa_",
                "tools": ["get_profile", "add_task"],
            },
            "other": {"command": "server-bin", "tools": ["gamma"]},
        }
    }
}


class LoadServersTests(unittest.TestCase):
    def test_normalises_command_env_prefix_tools(self):
        servers = mcp.load_servers(CONFIG)
        self.assertEqual([s["name"] for s in servers], ["pa", "other"])
        self.assertEqual(servers[0]["command"], ["uv", "run", "server"])
        self.assertEqual(servers[0]["env"], {"FOO": "bar"})
        self.assertEqual(servers[0]["prefix"], "pa_")
        self.assertEqual(servers[0]["tools"], ["get_profile", "add_task"])
        # A bare string command becomes a one-element list.
        self.assertEqual(servers[1]["command"], ["server-bin"])

    def test_empty_and_missing(self):
        self.assertEqual(mcp.load_servers({}), [])
        self.assertEqual(mcp.load_servers({"mcp": {}}), [])
        self.assertEqual(mcp.load_servers({"mcp": {"servers": {"x": {}}}}), [])

    def test_prefixing_and_dedup(self):
        servers = mcp.load_servers(CONFIG)
        names = mcp.exposed_tool_names(servers[:1])
        self.assertEqual(names, ["pa_get_profile", "pa_add_task"])

    def test_extension_env_shape(self):
        env = json.loads(mcp.extension_env(mcp.load_servers(CONFIG)[:1]))
        self.assertEqual(env["servers"][0]["name"], "pa")
        self.assertEqual(env["servers"][0]["prefix"], "pa_")
        self.assertEqual(env["servers"][0]["tools"], ["get_profile", "add_task"])


class QueryTests(unittest.TestCase):
    def setUp(self):
        mcp._TOOL_CACHE.clear()

    def test_queries_a_server_when_tools_absent(self):
        server = {"name": "fake", "command": [sys.executable, FAKE_SERVER],
                  "env": {}, "prefix": "", "tools": []}
        self.assertEqual(mcp.resolve_tools(server), ["alpha", "beta"])
        # Cached: a second call does not re-spawn.
        self.assertEqual(mcp.resolve_tools(server), ["alpha", "beta"])

    def test_bad_command_returns_empty(self):
        server = {"name": "nope", "command": ["/nonexistent/bin"],
                  "env": {}, "prefix": "", "tools": []}
        self.assertEqual(mcp.resolve_tools(server), [])


class BrainWiringTests(unittest.TestCase):
    def _session(self, mode):
        s = Session.__new__(Session)
        s.mode = mode
        s.model = "test-model"
        return s

    def _kwargs(self, mode):
        s = self._session(mode)
        with mock.patch("clippy.session.load_config", return_value=CONFIG):
            return s._brain_kwargs()

    def test_sandbox_includes_mcp_tools_and_env(self):
        kw = self._kwargs("sandbox")
        for name in ("read", "grep", "find", "ls", "pa_get_profile", "pa_add_task"):
            self.assertIn(name, kw["tools"])
        self.assertIn("CLIPPY_MCP_SERVERS", kw["env"])
        self.assertIn(MCP_EXT, kw["extensions"])
        # Sandbox is not gated, so no gate allowlist is needed.
        self.assertNotIn("CLIPPY_GATE_ALLOW", kw["env"])

    def test_build_auto_allows_mcp_tools_at_the_gate(self):
        kw = self._kwargs("build")
        self.assertIn(MCP_EXT, kw["extensions"])
        allow = kw["env"]["CLIPPY_GATE_ALLOW"].split(",")
        self.assertIn("pa_get_profile", allow)
        self.assertIn("pa_add_task", allow)

    def test_no_mcp_config_is_a_noop(self):
        s = self._session("sandbox")
        with mock.patch("clippy.session.load_config", return_value={}):
            kw = s._brain_kwargs()
        self.assertEqual(kw["tools"], ["read", "grep", "find", "ls"])
        self.assertNotIn("env", kw)
        self.assertNotIn(MCP_EXT, kw.get("extensions", []))


if __name__ == "__main__":
    unittest.main()
