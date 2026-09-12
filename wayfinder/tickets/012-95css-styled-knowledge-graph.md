---
id: 012
title: w1c knowledge graph (+ resolver port)
type: grilling
status: closed
assignee:
blocked_by: []
labels: [wayfinder:grilling]
---

## Superseded (016)

The "assistant emits declarative `spec` JSON → strict resolver validates against a styled knowledge graph" mechanism was framed for Clippy's own hand-rolled chat loop + skills (ticket 002). The projection pivot (map.md) makes Pi the brain: cards now arrive as Pi's `extension_ui_request` dialogs and are rendered directly by `__uiRequest` in the pane (ticket 016). The graph/resolver is no longer the mechanism; the w1c element palette + card styling it wanted to bound lives on in `assets/pane/w1c_pane.html`. Reopen only if a separate model-emitted spec channel is ever wanted.

## Question

Adopt the methodology of `PeteHaughie/HTML-components-canvas-graph` into the Clippy pane: the assistant emits declarative `spec` JSON which a strict resolver validates against a *styled knowledge graph* of available components, then assembles the card DOM in the pane. The palette is the vendored **w1c** library (`@w1c/components`, Lit custom elements) — custom elements, not classes (see ticket 014 for what actually loads/ships).

## Frames

- **Dependency (Pete decision):** built behind ticket 002 (Clippy's own chat loop + skills) — the graph is what lets the agent's emitted specs be *valid*, so it lands after tool/skill use is in place. Do NOT start until 002 unlocks.
- Palette: the w1c elements available post-014 spike — `w1c-window` (chrome rows titlebar/toolbar/content/statusbar, slots), `w1c-titlebar`, `w1c-statusbar`, `w1c-tabs`, `w1c-panel`, `w1c-input` (has `focus()`), `w1c-button`, `w1c-select`, `w1c-dialog`; native `<progress>` stays (no w1c progress/range/radio — theme them in the pane). Nodes carry: tag, capabilities, attributes/reflected props + `slot` composition (nesting) edges, forbidden combos, exported `part` names for theme overrides (e.g. `w1c-window::part(content)`).
- Graph source: w1c ships no `custom-elements.json` — hand-curate `graph.json` (see vendored bundle + `node_modules/@w1c/components` dist for the element/prop surface).
- Resolver: port of the prototype's resolver contract (`spec` tree → validation vs graph → assembled DOM), minimal since palette is small.
- Ephemeral semantics carried over: per-message cards, spec JSON hidden while streaming, stale cards disabled, not dismissible.

Note: this is the "moving parts" the human flagged — ephemeral UI is *only* meaningful once tool/skill use (002) exists to emit specs, and *only* valid once the styled graph (this ticket) bounds what may be emitted. Ticket 013 depends here.