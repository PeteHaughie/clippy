// Node tests for the pane's allowlist sanitizer predicates (no DOM needed).
// Run: node --test tests/test_sanitize.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const S = require("../assets/pane/sanitize.js");

test("tag allowlist", () => {
  for (const t of ["p", "a", "code", "pre", "table", "ul", "li", "h1", "img"]) {
    assert.equal(S.isAllowedTag(t), true, `${t} should be allowed`);
  }
  for (const t of ["script", "iframe", "object", "embed", "style", "link",
                   "meta", "base", "form", "svg", "math", "template"]) {
    assert.equal(S.isAllowedTag(t), false, `${t} should be blocked`);
  }
});

test("attribute allowlist blocks handlers and exotic attrs", () => {
  assert.equal(S.isAllowedAttr("a", "href"), true);
  assert.equal(S.isAllowedAttr("a", "onclick"), false);
  assert.equal(S.isAllowedAttr("a", "xlink:href"), false);
  assert.equal(S.isAllowedAttr("img", "srcset"), false);
  assert.equal(S.isAllowedAttr("img", "formaction"), false);
  assert.equal(S.isAllowedAttr("code", "class"), true);
  assert.equal(S.isAllowedAttr("p", "style"), false);
  assert.equal(S.isAllowedAttr("div", "class"), true);
});

test("safeUrl allows only safe schemes", () => {
  assert.equal(S.safeUrl("https://example.com/x", "href"), true);
  assert.equal(S.safeUrl("http://example.com", "src"), true);
  assert.equal(S.safeUrl("mailto:a@b.com", "href"), true);
  assert.equal(S.safeUrl("/relative/path", "href"), true);
  assert.equal(S.safeUrl("#fragment", "href"), true);
  assert.equal(S.safeUrl("?q=1", "href"), true);

  assert.equal(S.safeUrl("javascript:alert(1)", "href"), false);
  assert.equal(S.safeUrl("JaVaScRiPt:alert(1)", "href"), false);
  assert.equal(S.safeUrl("java\nscript:alert(1)", "href"), false);
  assert.equal(S.safeUrl("java\tscript:alert(1)", "href"), false);
  assert.equal(S.safeUrl("data:text/html,<script>1</script>", "src"), false);
  assert.equal(S.safeUrl("vbscript:msgbox(1)", "href"), false);
  assert.equal(S.safeUrl("file:///etc/passwd", "src"), false);
  // mailto is not a valid src scheme
  assert.equal(S.safeUrl("mailto:a@b.com", "src"), false);
});
