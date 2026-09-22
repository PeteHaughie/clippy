"""Screen geometry: pure helpers, monitor ordering, and move-spec parsing."""

import unittest
from unittest import mock

from clippy import screens
from clippy.subagent import parse_move_spec

# Two monitors: primary 1920x1080 at the origin, secondary 3840x2400 to its
# right (in the shell's device units).
PRIMARY = (0, 0, 1920, 1080)
SECOND = (3840, 0, 3840, 2400)


class FakeBackend:
    def __init__(self, rects, primary=None):
        self._rects = list(rects)
        self._primary = primary

    def screens(self):
        return list(self._rects)

    def workareas(self):
        return list(self._rects)

    def primary(self):
        return self._primary

    def window_top_left(self, win):
        return (0, 0)

    def set_window_top_left(self, win, x, y):
        pass

    def pointer_global(self, win):
        return None


class PureGeometryTests(unittest.TestCase):
    def test_containing_and_nearest(self):
        rects = [PRIMARY, SECOND]
        self.assertEqual(screens.rect_containing(100, 100, rects), PRIMARY)
        self.assertEqual(screens.rect_containing(4000, 100, rects), SECOND)
        # A point in the gap between the two picks the nearer monitor.
        self.assertEqual(screens.nearest_rect(3000, 100, rects), SECOND)

    def test_clamp_to_rect_keeps_window_inside(self):
        # Window 200x200, target off the top-left of PRIMARY.
        self.assertEqual(screens.clamp_to_rect(-50, -50, 200, 200, PRIMARY), (8, 8))
        # Off the bottom-right.
        self.assertEqual(
            screens.clamp_to_rect(9999, 9999, 200, 200, PRIMARY), (1712, 872)
        )

    def test_clamp_to_rects_crosses_monitors(self):
        rects = [PRIMARY, SECOND]
        # A point inside SECOND stays there (not pulled back to primary).
        x, y = screens.clamp_to_rects(4000, 100, 200, 200, rects)
        self.assertEqual((x, y), (4000, 100))

    def test_spot_in_rect(self):
        w, h = 200, 200
        self.assertEqual(screens.spot_in_rect("top-left", w, h, PRIMARY), (12, 12))
        self.assertEqual(
            screens.spot_in_rect("bottom-right", w, h, PRIMARY), (1708, 868)
        )
        self.assertEqual(screens.spot_in_rect("center", w, h, PRIMARY), (860, 440))

    def test_drag_target_tracks_cursor_minus_offset(self):
        rects = [PRIMARY, SECOND]
        # Grab 20px in from the left, drag the cursor to (4050, 300).
        target = screens.drag_target((4050, 300), (20, 10), 200, 200, rects)
        self.assertEqual(target, (4030, 290))


class MonitorListingTests(unittest.TestCase):
    def test_left_to_right_order_and_primary_flag(self):
        with mock.patch.object(
            screens, "_backend", FakeBackend([SECOND, PRIMARY], primary=PRIMARY)
        ):
            areas = screens.list_workareas()
        self.assertEqual([a["index"] for a in areas], [1, 2])
        self.assertEqual(areas[0]["rect"], PRIMARY)
        self.assertTrue(areas[0]["primary"])
        self.assertEqual(areas[1]["rect"], SECOND)
        self.assertFalse(areas[1]["primary"])

    def test_lookup_helpers(self):
        with mock.patch.object(
            screens, "_backend", FakeBackend([PRIMARY, SECOND], primary=PRIMARY)
        ):
            self.assertEqual(screens.workarea_by_index(2), SECOND)
            self.assertIsNone(screens.workarea_by_index(9))
            self.assertEqual(screens.monitor_index_for_point(4000, 50), 2)
            self.assertEqual(screens.monitor_index_for_point(50, 50), 1)

    def test_clamp_to_workarea_uses_target_screen(self):
        with mock.patch.object(
            screens, "_backend", FakeBackend([PRIMARY, SECOND], primary=PRIMARY)
        ):
            # Target on SECOND → clamped within SECOND's bounds.
            x, y = screens.clamp_to_workarea(99999, 50, 200, 200)
            self.assertEqual(x, SECOND[0] + SECOND[2] - 200 - screens.MARGIN)


class ParseMoveSpecTests(unittest.TestCase):
    def test_coords(self):
        spec = parse_move_spec("10 20")
        self.assertEqual((spec.mode, spec.x, spec.y), ("coords", 10, 20))

    def test_spot(self):
        spec = parse_move_spec("Top-Right")
        self.assertEqual((spec.mode, spec.spot), ("spot", "top-right"))

    def test_monitor_centre(self):
        spec = parse_move_spec("monitor 2")
        self.assertEqual((spec.mode, spec.monitor, spec.spot), ("monitor", 2, ""))

    def test_monitor_spot(self):
        spec = parse_move_spec("monitor 1 bottom-left")
        self.assertEqual(
            (spec.mode, spec.monitor, spec.spot), ("monitor", 1, "bottom-left")
        )

    def test_empty(self):
        self.assertIsNone(parse_move_spec(""))

    def test_malformed_monitor_is_spot(self):
        spec = parse_move_spec("monitor")
        self.assertEqual(spec.mode, "spot")


class RealBackendSmokeTests(unittest.TestCase):
    def test_list_workareas_does_not_raise(self):
        # On a headless box this may be empty; it must never raise.
        self.assertIsInstance(screens.list_workareas(), list)


if __name__ == "__main__":
    unittest.main()
