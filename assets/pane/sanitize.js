/*
 * Clippy pane HTML sanitizer (allowlist).
 *
 * Model output (and, in build mode, content it fetches) is untrusted and is
 * rendered into the pane from markdown via `marked`. marked does not sanitize,
 * so everything it produces passes through here before it reaches the DOM.
 *
 * The policy is an ALLOWLIST: a tag or attribute that is not named is dropped.
 * That is deliberate — a deny-list silently lets through anything the author
 * did not think of (xlink:href, srcset, formaction, data: URLs, …).
 *
 * The decision functions (`isAllowedTag`, `isAllowedAttr`, `safeUrl`) are pure
 * so they can be unit-tested from Node without a DOM (`tests/test_sanitize.mjs`).
 */
(function (root) {
  "use strict";

  // Tags marked/GFM can legitimately emit for chat markdown.
  var ALLOWED_TAGS = [
    "p", "br", "hr", "strong", "em", "del", "code", "pre", "blockquote",
    "ul", "ol", "li", "h1", "h2", "h3", "h4", "h5", "h6",
    "a", "img", "table", "thead", "tbody", "tr", "th", "td",
  ];

  // Attribute allowlist, per tag. `class` is allowed everywhere (marked tags
  // code fences with `language-*`); `href`/`src` are additionally scheme-checked.
  var ALLOWED_ATTRS = {
    a: ["href", "title", "class"],
    img: ["src", "alt", "title", "class"],
    code: ["class"],
    pre: ["class"],
    ol: ["start", "class"],
    li: ["value", "class"],
    th: ["align", "class"],
    td: ["align", "class"],
    table: ["class"],
    blockquote: ["class"],
  };
  var GLOBAL_ATTRS = ["class"];

  // URL-valued attributes and the schemes they may use. Everything else
  // (data:, javascript:, vbscript:, file:, …) is rejected.
  var URL_ATTRS = { href: true, src: true };
  var ALLOWED_SCHEMES = {
    href: ["http:", "https:", "mailto:"],
    src: ["http:", "https:"],
  };

  var TAG_SET = new Set(ALLOWED_TAGS);

  function isAllowedTag(tag) {
    return TAG_SET.has(String(tag == null ? "" : tag).toLowerCase());
  }

  function isAllowedAttr(tag, name) {
    var t = String(tag == null ? "" : tag).toLowerCase();
    var n = String(name == null ? "" : name).toLowerCase();
    if (!n || n.indexOf("on") === 0) return false; // no event handlers
    if (GLOBAL_ATTRS.indexOf(n) !== -1) return true;
    var perTag = ALLOWED_ATTRS[t];
    return !!perTag && perTag.indexOf(n) !== -1;
  }

  // Is `value` safe for URL attribute `attrName`? Relative URLs, fragments and
  // query strings are fine; absolute URLs must use an allowed scheme.
  function safeUrl(value, attrName) {
    // Strip ASCII control chars/whitespace that can be used to smuggle a
    // scheme past a naive check (e.g. "java\nscript:").
    var v = String(value == null ? "" : value).replace(/[\u0000-\u0020]+/g, "");
    var m = /^([a-z][a-z0-9+.\-]*):/i.exec(v);
    if (!m) return true;
    var schemes = ALLOWED_SCHEMES[String(attrName || "").toLowerCase()] || [];
    return schemes.indexOf(m[1].toLowerCase() + ":") !== -1;
  }

  function sanitize(root) {
    if (!root || !root.querySelectorAll) return root;
    var nodes = Array.prototype.slice.call(root.querySelectorAll("*"));
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      var tag = (el.tagName || el.localName || "").toLowerCase();
      if (!isAllowedTag(tag)) {
        if (el.parentNode) el.parentNode.removeChild(el);
        continue;
      }
      var attrs = Array.prototype.slice.call(el.attributes || []);
      for (var j = 0; j < attrs.length; j++) {
        var name = attrs[j].name;
        if (!isAllowedAttr(tag, name)) {
          el.removeAttribute(attrs[j].name);
        } else if (URL_ATTRS[String(name).toLowerCase()] &&
                   !safeUrl(attrs[j].value, name)) {
          el.removeAttribute(attrs[j].name);
        }
      }
      // Links open in the OS browser, not the pane. The pane's webview
      // intercepts navigation at the native policy layer (clippy/pane.py) and
      // hands http/https/mailto URLs to the default browser; target is still
      // dropped here so nothing escapes that layer.
      if (tag === "a" && el.setAttribute) {
        el.removeAttribute("target");
        el.setAttribute("rel", "noopener noreferrer");
      }
    }
    return root;
  }

  var api = {
    ALLOWED_TAGS: ALLOWED_TAGS,
    isAllowedTag: isAllowedTag,
    isAllowedAttr: isAllowedAttr,
    safeUrl: safeUrl,
    sanitize: sanitize,
  };
  root.ClipSanitize = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
