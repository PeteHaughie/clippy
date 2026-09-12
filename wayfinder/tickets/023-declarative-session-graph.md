---
id: 023
title: Declarative session graph (graph-model P3)
type: prototype
status: closed
assignee: pete
blocked_by: [021, 022]
labels: [wayfinder:prototype]
---

## Question

The app's topology was procedural lambdas in main.py (`on_answer`, `on_ui_request`, `on_chat`, `on_ui_response`, `set_mode`, `dialog_pending`) scattered across PrimeSession + Delegator. How do we make the connection graph — processes → event streams → controllers → state machines → projections — explicit, inspectable, and validated?

## Resolution

- **`clippy/model.py::build_session_graph()`** — the canonical topology as data: 18 typed nodes (prime/worker processes, event streams, controllers, state machines, shell/pane/dialog projections, mode, memory/skill/consent-gate constraints), 25 typed edges (`produces`, `consumed_by`, `drives`, `projects_to{channel}`, `opens`, `rendered_as`, `triggers`, `completes`, `injected_into`, `constrains`, `displays`), 6 constraints, all with provenance tags (wayfinder ticket ids). `required_topology()` is the structural validation target; `Model.validate_topology` fails on missing connections.
- **`clippy/session.py::Session`** — absorbs PrimeSession + Delegator: owns the prime brain (or mock), the prime controller, the pane, mode/respawn, and one worker at a time. The callback wiring is a **projection of the graph**: `projects_to{pane,answer}` → `on_answer`, `projects_to{pane,card}` → `on_ui_request`, `triggers{chat_input→prime}` → `on_chat`, `rendered_as{dialog→pane}` → `on_ui_response`. `Session.dump()` renders the provenance view ("why does this reach the pane?").
- **`main.py`** — reduced to entry-point + PrimeShell keys; constructs one `Session`.

## Findings that mattered

- `chat_input` has two trigger edges (→`prime` prompt, →`task` delegate): `prompt()` dispatches `/delegate` internally, so the delegate edge is declared in the graph but wired through the same handler.
- Wiring from graph edges means a new channel is impossible to forget: if an edge kind/channel isn't bound, `Session._wire` simply doesn't bind it — the topology validation catches missing edges first.

## Acceptance

Headless: `build_session_graph()` validates against `required_topology()` with zero missing; Session imports cleanly and wires from the graph. The GUI boot (pane summon, Tab respawn) is unchanged behaviorally and verified at the live acceptance run (CG display needed).