"""Pane navigation policy: which webview navigations are allowed, opened
externally, or dropped (see clippy/pane.py::_classify_navigation)."""

import unittest

from clippy.pane import PANE_URI, _classify_navigation

PANE = "file:///opt/clippy/assets/pane/w1c_pane.html"


class ClassifyNavigation(unittest.TestCase):
    def test_pane_document_and_about_are_allowed(self):
        self.assertEqual(_classify_navigation(PANE, PANE), "allow")
        self.assertEqual(_classify_navigation("about:blank", PANE), "allow")
        self.assertEqual(_classify_navigation("about:srcdoc", PANE), "allow")

    def test_external_schemes_open_in_browser(self):
        for url in (
            "http://example.com",
            "https://example.com/path?q=1#frag",
            "HTTPS://EXAMPLE.COM",
            "mailto:someone@example.com",
        ):
            self.assertEqual(_classify_navigation(url, PANE), "open", url)

    def test_everything_else_is_dropped(self):
        for url in (
            "",
            None,
            "file:///etc/passwd",
            "../relative.md",
            "index.html",
            "javascript:alert(1)",
            "data:text/html,<script>1</script>",
            "ftp://example.com/x",
        ):
            self.assertEqual(_classify_navigation(url, PANE), "drop", repr(url))

    def test_default_pane_uri_is_this_checkouts_document(self):
        self.assertTrue(PANE_URI.startswith("file:"))
        self.assertTrue(PANE_URI.endswith("w1c_pane.html"))
        self.assertEqual(_classify_navigation(PANE_URI), "allow")


if __name__ == "__main__":
    unittest.main()
