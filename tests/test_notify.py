"""AppleScript string encoding: no injection via quotes/backslashes."""

import subprocess
import unittest
from unittest import mock

from clippy import notify


class AppleScriptStringTests(unittest.TestCase):
    def test_wraps_in_double_quotes(self):
        self.assertEqual(notify._applescript_string("hello"), '"hello"')

    def test_escapes_quotes_and_backslashes(self):
        self.assertEqual(
            notify._applescript_string('a"b\\c'), '"a\\"b\\\\c"'
        )

    def test_escapes_control_whitespace(self):
        self.assertEqual(
            notify._applescript_string("a\nb\tc\rd"), '"a\\nb\\tc\\rd"'
        )

    def test_injection_payload_stays_inside_the_literal(self):
        payload = 'x" & (do shell script "id") & "'
        encoded = notify._applescript_string(payload)
        # Every interior double quote is escaped, so the literal cannot be
        # closed early to inject AppleScript.
        self.assertEqual(
            encoded, '"x\\" & (do shell script \\"id\\") & \\""'
        )

    @mock.patch("clippy.notify.shutil.which", return_value="/usr/bin/osascript")
    @mock.patch("clippy.notify.subprocess.run")
    def test_osascript_uses_escaped_literal(self, run, _which):
        notify.notify('Ti"tle', 'bo"dy')
        script = run.call_args[0][0][2]
        self.assertIn('display notification "bo\\"dy"', script)
        self.assertIn('with title "Ti\\"tle"', script)
        self.assertTrue(script.count('"') % 2 == 0)


if __name__ == "__main__":
    unittest.main()
