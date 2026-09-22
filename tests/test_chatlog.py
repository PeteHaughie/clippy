"""Chat log batching and pi_ready caching."""

import json
import pathlib
import tempfile
import unittest
from unittest import mock

from clippy import subagent
from clippy.chatlog import ChatLogger


class ChatLogBatchingTests(unittest.TestCase):
    def setUp(self):
        self.dir = pathlib.Path(tempfile.mkdtemp())
        self.path = self.dir / "c.jsonl"

    def test_deltas_buffered_until_turn_boundary(self):
        log = ChatLogger(self.path, label="t")
        log.thinking("a")
        log.stream("b")
        self.assertFalse(self.path.exists())  # nothing flushed yet
        log.response("stop", "ab")
        kinds = [json.loads(l)["type"] for l in self.path.read_text().splitlines()]
        self.assertEqual(kinds, ["thinking", "stream", "response"])
        log.close()

    def test_close_flushes_pending(self):
        log = ChatLogger(self.path, label="t")
        log.thinking("partial")
        log.close()
        kinds = [json.loads(l)["type"] for l in self.path.read_text().splitlines()]
        self.assertEqual(kinds, ["thinking"])


class PiReadyCacheTests(unittest.TestCase):
    def setUp(self):
        self._orig = subagent._pi_ready_cache
        subagent._pi_ready_cache = None

    def tearDown(self):
        subagent._pi_ready_cache = self._orig

    def test_result_is_cached_and_refreshable(self):
        with mock.patch.object(
            subagent, "_probe_pi_ready", return_value=True
        ) as probe:
            self.assertTrue(subagent.pi_ready())
            self.assertTrue(subagent.pi_ready())
            probe.assert_called_once()
            subagent.pi_ready(refresh=True)
            self.assertEqual(probe.call_count, 2)


if __name__ == "__main__":
    unittest.main()
