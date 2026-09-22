"""Directive parsing: close marker is optional for every directive type."""

import unittest

from clippy.scheduler import parse_notify, parse_schedule, parse_trigger
from clippy.subagent import parse_delegation, parse_move


class DelegationTests(unittest.TestCase):
    def test_with_close_marker(self):
        clean, task = parse_delegation("Before [CLIPPY::DELEGATE] do X [CLIPPY::END] after")
        self.assertEqual(task, "do X")
        self.assertNotIn("CLIPPY", clean)
        self.assertIn("Before", clean)
        self.assertIn("after", clean)

    def test_without_close_marker_delegates_to_end_of_line(self):
        clean, task = parse_delegation("Before\n[CLIPPY::DELEGATE] do X\nSome trailing text")
        self.assertEqual(task, "do X")
        self.assertNotIn("CLIPPY::DELEGATE", clean)
        self.assertIn("Some trailing text", clean)

    def test_no_block(self):
        self.assertEqual(parse_delegation("just text"), ("just text", None))

    def test_empty_task_is_none(self):
        clean, task = parse_delegation("[CLIPPY::DELEGATE][CLIPPY::END]")
        self.assertIsNone(task)


class MoveTests(unittest.TestCase):
    def test_named_spot_without_close(self):
        clean, spec = parse_move("Moved.\n[CLIPPY::MOVE] top-left")
        self.assertEqual(spec, "top-left")
        self.assertNotIn("CLIPPY::MOVE", clean)

    def test_coords_with_close(self):
        clean, spec = parse_move("[CLIPPY::MOVE] 10 20 [CLIPPY::END] done")
        self.assertEqual(spec, (10, 20))
        self.assertEqual(clean, "done")


class ScheduleDirectiveTests(unittest.TestCase):
    def test_schedule_without_close(self):
        clean, trigger, what = parse_schedule("ok\n[CLIPPY::SCHEDULE] in 5 minutes | stretch")
        self.assertEqual(trigger, {"type": "in", "seconds": 300})
        self.assertEqual(what, "stretch")
        self.assertNotIn("CLIPPY::SCHEDULE", clean)

    def test_notify_without_close(self):
        clean, text = parse_notify("ok\n[CLIPPY::NOTIFY] done now")
        self.assertEqual(text, "done now")
        self.assertNotIn("CLIPPY::NOTIFY", clean)


if __name__ == "__main__":
    unittest.main()
