# ADR-0005: Pane HTML sanitization is an allowlist

## Status

Accepted

## Context

The chat pane renders model output (and, in build mode, content the model
fetches) as markdown. `marked` parses it but does **not** sanitize, and the
result is inserted into the DOM. The pane owns a `window.webkit.messageHandlers`
bridge (chat, `mode_toggle`, `ui_response`), so script injection is a
high-value target.

The original sanitizer was a **blocklist**: it removed a fixed set of tags and
`on*` attributes and blocked `javascript:` in `href`/`src`. Blocklists silently
let through anything the author didn't think of — `xlink:href`, `srcset`,
`formaction`, `data:`/`vbscript:` URLs, SVG `<a xlink:href>`, etc.

## Decision Drivers

- Model/web output is untrusted (prompt injection is expected local-agent risk).
- No new runtime dependency was desired for a local tool (no DOMPurify/jsdom).
- The security-critical predicates should be **unit-testable**.

## Considered Options

### Option A — Harden the blocklist

Add the missing tags/attributes/schemes to the deny list.

### Option B — Vendor DOMPurify

Robust, but adds a vendored dependency and needs a DOM for tests.

### Option C — Allowlist module (chosen)

Replace the blocklist with an explicit **allowlist** of tags, per-tag
attributes, and URL schemes, extracted into `assets/pane/sanitize.js`. Pure
predicates (`isAllowedTag`, `isAllowedAttr`, `safeUrl`) are tested from Node; the
DOM walk is thin. The pane **fails closed** if the module is missing.

## Decision

Adopt **Option C**. `marked` still parses; everything it produces passes through
the allowlist before insertion. URL attributes are scheme-checked (`http`,
`https`, `mailto` for `href`; `http`/`https` for `src`), control characters are
stripped to defeat scheme smuggling, and `target` is dropped with `rel` hardened.

Links never navigate the pane: the native webview navigation policy in
`clippy/pane.py` (`_classify_navigation`) cancels any navigation that is not the
pane's own document and opens `http`/`https`/`mailto` URLs in the OS default
browser. The sanitizer's `target` removal is the first line of that defence.

## Rationale

1. An allowlist is fail-closed by construction — unknown tags/attrs are dropped.
2. No dependency; offline.
3. The predicates are plain functions, unit-testable without a DOM.

## Consequences

### Positive

- The known bypasses (`data:`, `xlink:href`, `srcset`, …) are gone.
- Sanitizer policy is testable (`tests/test_sanitize.mjs`).

### Negative / Risks

- The allowlist must be extended deliberately if new markdown features are
  wanted (e.g. `<details>`).
- The DOM walk still uses the browser's parser; the allowlist is the boundary.

## Implementation Notes

- `assets/pane/sanitize.js`; wired in `assets/pane/w1c_pane.html`
  (`<script src="sanitize.js">`, fail-closed fallback).
- `clippy/pane.py` — `_classify_navigation` (allow/open/drop) called from the
  macOS navigation delegate and the WebKitGTK `decide-policy` handler; external
  links open in the OS browser, the pane document is the only committed URL.
- `tests/test_sanitize.mjs` (XSS corpus); `tests/test_pane_links.py`
  (navigation classification).

## References

- Commit `5950659` — security hardening
- `docs/remediation-plan.md` — Phase 1
