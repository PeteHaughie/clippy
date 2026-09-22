"""Scheduler trigger validation: bad input is rejected, never raised."""

import unittest

from clippy.scheduler import _next_wake, _now, parse_trigger


class ParseTriggerTests(unittest.TestCase):
    def test_valid_at(self):
        trigger, what = parse_trigger("at 23:59 take a break")
        self.assertEqual(trigger, {"type": "at", "hour": 23, "minute": 59})
        self.assertEqual(what, "take a break")

    def test_out_of_range_hour_rejected(self):
        self.assertEqual(parse_trigger("at 99:00 x"), ({}, ""))
        self.assertEqual(parse_trigger("daily at 25:00 x"), ({}, ""))

    def test_out_of_range_minute_rejected(self):
        self.assertEqual(parse_trigger("at 10:99 x"), ({}, ""))

    def test_valid_daily(self):
        trigger, _ = parse_trigger("daily at 9:05 standup")
        self.assertEqual(trigger, {"type": "daily", "hour": 9, "minute": 5})

    def test_zero_interval_rejected(self):
        self.assertEqual(parse_trigger("every 0 minutes x"), ({}, ""))
        self.assertEqual(parse_trigger("in 0 seconds x"), ({}, ""))

    def test_valid_relative(self):
        trigger, _ = parse_trigger("in 5 minutes stretch")
        self.assertEqual(trigger, {"type": "in", "seconds": 300})

    def test_next_wake_never_raises_for_valid_trigger(self):
        _next_wake({"type": "at", "hour": 0, "minute": 0}, _now())
        _next_wake({"type": "daily", "hour": 23, "minute": 59}, _now())


if __name__ == "__main__":
    unittest.main()
