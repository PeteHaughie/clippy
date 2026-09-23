# ADR-0007: Pane links open in the OS browser; navigation is intercepted natively

## Status

Accepted

## Context

The chat pane renders model output as markdown (ADR-0005), so an answer can
contain ordinary `<a href="…">` links. The pane's webview **is** the chat UI —
its document is the surface, not a page you browse. Any committed navigation
replaces the entire chat with a web page, which is what happened when a link
was clicked: the WKWebView (macOS) / WebKitGTK (Linux) view navigated to the
target.

The pane is a locked-down projection: the bridge exposes only `chat`,
`ui_response`, `mode_toggle` and the drag/resize channels, and model/web content
is untrusted (prompt injection is an expected local-agent risk). A link must
reach a real browser without ever being able to move the pane off its document.

## Decision Drivers

- A clicked link must open in the user's real browser context.
- The pane must be unable to navigate away — fail-closed, including relative and
  `file:` URLs, not just `http(s)`.
- One policy, shared by both backends, with a predicate that is unit-testable
  without a display or webview (consistent with ADR-0004).
- No new dependency, and no script execution from page content.

## Considered Options

- **Option A — JS click interception + bridge message.** A delegated click
  handler in `w1c_pane.html` calls `preventDefault()` and posts an `open_url`
  message to Python, which opens the browser.
- **Option B — Native navigation policy (chosen).** Intercept at the engine
  boundary: macOS `webView:decidePolicyForNavigationAction:decisionHandler:`;
  Linux WebKitGTK `decide-policy`. Cancel everything that is not the pane's own
  document; hand external URLs to the OS.
- **Option C — `target="_blank"` + a `createWebView` delegate.** In WKWebView a
  `target="_blank"` link is a no-op unless a new-window delegate is implemented,
  so this is really Option B with extra moving parts.

## Decision

Adopt **Option B**. A single pure predicate drives both backends:

`_classify_navigation(uri) -> "allow" | "open" | "drop"`

- `allow` — exactly the pane's own document (`PANE_URI`) or an internal
  `about:` document: the webview commits it.
- `open` — an external `http:`/`https:`/`mailto:` URL: cancel the in-webview
  navigation and open it via `_open_external` (`NSWorkspace.openURL_` on macOS,
  `Gtk.show_uri_on_window` on Linux).
- `drop` — anything else (relative/`file:` URLs, or no URL): cancel silently.

macOS implements this in `NavDelegate.webView_decidePolicyForNavigationAction_decisionHandler_`
(nil target frame treated as main-frame); Linux connects `decide-policy` and
ignores the navigation. ADR-0005's sanitizer remains the first line — it
scheme-checks `href` and drops `target` so nothing sidesteps this layer.

## Rationale

1. **Fail-closed at the engine boundary.** The policy is not a page-level click
   handler: it also catches middle-clicks, the context menu, subframes, and
   programmatic navigation, and it cannot be bypassed from the DOM.
2. **One predicate, two backends.** The allow/open/drop rule lives in a plain
   function, unit-tested in `tests/test_pane_links.py`; the backends only supply
   the native hook.
3. **`target="_blank"` alone breaks links.** Without a `createWebView` delegate
   WKWebView ignores `_blank` links, so Option C would need the same policy
   anyway; Option A is bypassable.
4. **Defence in depth with ADR-0005.** The sanitizer constrains what a link may
   be; the navigation policy constrains where the pane may go.

## Consequences

### Positive

- Chat links open in the OS default browser; the pane keeps its chat.
- The pane cannot be navigated off its document by any means.
- Navigation policy is testable without a webview.
- No new runtime dependency.

### Negative / Risks

- `mailto:` is delegated to the OS mail handler (the intended behaviour, but no
  in-pane mail UI).
- In-page anchor/relative links are dropped rather than scrolled; the chat has
  no such links today.
- Two small native handlers must be kept in step; both delegate to the same
  predicate to limit drift.

## Implementation Notes

- `clippy/pane.py` — `_classify_navigation`, `_open_external`, `PANE_URI`; macOS
  `NavDelegate`; `GtkPane._on_decide_policy`.
- `assets/pane/sanitize.js` — comment updated: links open in the OS browser, not
  the pane (sanitizer still drops `target` / hardens `rel`).
- `tests/test_pane_links.py` — allow/open/drop cases.
- `webbrowser.open` is the fallback when neither native handler is available.

## References

- Commit `346afb4` — open chat links in the OS browser
- `docs/adr/0005-pane-html-sanitization.md` — the sanitizer allowlist
- `docs/adr/0004-screen-geometry-and-drag.md` — backend-split + testable-helper precedent
- `WKNavigationDelegate.decidePolicyForNavigationAction:`; WebKitGTK `decide-policy`
