---
id: 012
title: 95CSS styled knowledge graph (+ resolver port)
type: grilling
status: open
assignee:
blocked_by: [002]
labels: [wayfinder:grilling]
---

## Question

Adopt the methodology of `PeteHaughie/HTML-components-canvas-graph` into the Clippy pane: the assistant emits declarative `spec` JSON which a strict resolver validates against a *styled knowledge graph* of available components, then assembles the card DOM in the pane. For Clippy the component palette is 95CSS (classes, not custom elements), so the graph must be curated by hand.

## Frames

- **Dependency (Pete decision):** built behind ticket 002 (Clippy's own chat loop + skills) — the graph is what lets the agent's emitted specs be *valid*, so it lands after tool/skill use is in place. Do NOT start until 002 unlocks.
- Palette: ~15 95CSS components (button/input/checkbox/radio/select/range/color, dialog, tabs, fieldset/legend, progress, scrollbar, header/nav, utilities). Nodes carry: class names, capability tags, composition (nesting) edges, forbidden combos.
- **Overlay rule relaxes:** the canvas prototype banned overlays/dialogs because they didn't paint into a snapshot; in the live DOM pane, 95CSS dialogs/tabs/selects work naturally — the graph can allow them.
- Graph source differs from the prototype: no `custom-elements.json` exists for 95CSS — hand-curate `graph.json` (see vendored 95css.min.css for the authoritative class list).
- Resolver: port of the prototype's resolver contract (`spec` tree → validation vs graph → assembled DOM), minimal since palette is small.
- Ephemeral semantics carried over: per-message cards, spec JSON hidden while streaming, stale cards disabled, not dismissible.

Note: this is the "moving parts" the human flagged — ephemeral UI is *only* meaningful once tool/skill use (002) exists to emit specs, and *only* valid once the styled graph (this ticket) bounds what may be emitted. Ticket 013 depends here.