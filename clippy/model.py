"""Canonical graph model for Clippy (graph-model skill, phases 1–3).

The runtime is a set of *projections* of this model: the control plane is
declared here as typed nodes, edges and constraints, and the code that talks
to Pi or renders pixels reads this model instead of carrying ad-hoc state of
its own.

Contained here:

* **Primitives** — :class:`Node`, :class:`Edge`, :class:`Constraint`,
  :class:`Model` (a graph with lookups and a Markdown ``dump`` projection).
* **Typed events** — the ``Ev`` hierarchy a Pi event stream normalises into
  (one catalog for both RPC ``message_update`` and ``--mode json`` wire
  shapes).
* **State-machine configs** — ``WORKER_LIFECYCLE`` and ``PRIME_CONVERSATION``
  as graph data (states = nodes, transitions = edges, timeouts + effects +
  guards by name). The runtime in :mod:`clippy.statemachine` executes them.
* **The session graph** — :func:`build_session_graph` returns the canonical
  topology (processes → event streams → controllers → state machines →
  projections) with provenance tags (wayfinder ticket ids) and the constraint
  set. :mod:`clippy.session` wires it.

Phases: P1 typed events · P2 state machines · P3 session graph.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, ClassVar

# ---------------------------------------------------------------- primitives


@dataclass(frozen=True)
class Node:
    id: str
    kind: str  # external|process|resource|value|state|component|capability|interface|output
    name: str
    attrs: dict = field(default_factory=dict)
    provenance: tuple = ()  # wayfinder ticket ids


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    kind: str  # produces|consumed_by|drives|projects_to|triggers|opens|rendered_as|injected_into|constrains|completes|displays
    attrs: dict = field(default_factory=dict)
    provenance: tuple = ()


@dataclass(frozen=True)
class Constraint:
    name: str
    expr: str
    provenance: tuple = ()


class Model:
    """A directed graph of typed nodes/edges/constraints with projections."""

    def __init__(self):
        self._nodes: dict[str, Node] = {}
        self._edges: list[Edge] = []
        self._constraints: list[Constraint] = []

    def node(self, id, kind, name, **kw) -> Node:
        node = Node(id=id, kind=kind, name=name, **kw)
        self._nodes[id] = node
        return node

    def edge(self, src, dst, kind, **kw) -> Edge:
        edge = Edge(src=src, dst=dst, kind=kind, **kw)
        self._edges.append(edge)
        return edge

    def constrain(self, name, expr, **kw) -> Constraint:
        c = Constraint(name=name, expr=expr, **kw)
        self._constraints.append(c)
        return c

    @property
    def nodes(self):
        return list(self._nodes.values())

    @property
    def edges(self):
        return list(self._edges)

    @property
    def constraints(self):
        return list(self._constraints)

    def node_of(self, id) -> Node | None:
        return self._nodes.get(id)

    def edges_from(self, src, kind=None) -> list[Edge]:
        return [
            e for e in self._edges
            if e.src == src and (kind is None or e.kind == kind)
        ]

    def edges_to(self, dst, kind=None) -> list[Edge]:
        return [
            e for e in self._edges
            if e.dst == dst and (kind is None or e.kind == kind)
        ]

    def edges_of(self, kind) -> list[Edge]:
        return [e for e in self._edges if e.kind == kind]

    def validate_topology(self, required: list[tuple[str, str, str]]) -> list[str]:
        """Structural check: every ``(src, dst, kind)`` in ``required`` must be
        present as an edge. Returns the list of missing connections."""
        present = {(e.src, e.dst, e.kind) for e in self._edges}
        return [f"{s} -[{k}]-> {d}" for (s, d, k) in required if (s, d, k) not in present]

    def dump(self) -> str:
        """Project the model to Markdown (the graph-model skill's deliverable)."""
        lines = ["# Clippy model graph", ""]
        lines.append("## Nodes")
        for n in self.nodes:
            prov = f"  ({', '.join(n.provenance)})" if n.provenance else ""
            attrs = f"  {n.attrs}" if n.attrs else ""
            lines.append(f"- `{n.id}` ({n.kind}): {n.name}{attrs}{prov}")
        lines.append("")
        lines.append("## Edges")
        for e in self.edges:
            prov = f"  ({', '.join(e.provenance)})" if e.provenance else ""
            attrs = f"  {e.attrs}" if e.attrs else ""
            lines.append(f"- `{e.src}` -[{e.kind}]-> `{e.dst}`{attrs}{prov}")
        lines.append("")
        lines.append("## Constraints")
        for c in self.constraints:
            prov = f"  ({', '.join(c.provenance)})" if c.provenance else ""
            lines.append(f"- **{c.name}**: {c.expr}{prov}")
        return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- typed events

#: A typed event is a frozen value; the router in :mod:`clippy.events` normalises
#: raw Pi JSONL into one of these. ``kind`` is a stable semantic name.
@dataclass(frozen=True)
class Ev:
    kind: ClassVar[str] = "ev"


@dataclass(frozen=True)
class AgentStart(Ev):
    kind: ClassVar[str] = "agent_start"


@dataclass(frozen=True)
class TurnStart(Ev):
    kind: ClassVar[str] = "turn_start"


@dataclass(frozen=True)
class TurnEnd(Ev):
    kind: ClassVar[str] = "turn_end"


@dataclass(frozen=True)
class MessageStart(Ev):
    role: str = ""
    kind: ClassVar[str] = "message_start"


@dataclass(frozen=True)
class ThinkingDelta(Ev):
    delta: str = ""
    kind: ClassVar[str] = "thinking_delta"


@dataclass(frozen=True)
class ThinkingEnd(Ev):
    content: str = ""
    kind: ClassVar[str] = "thinking_end"


@dataclass(frozen=True)
class TextDelta(Ev):
    delta: str = ""
    kind: ClassVar[str] = "text_delta"


@dataclass(frozen=True)
class ToolCallStart(Ev):
    tool: str = ""
    kind: ClassVar[str] = "toolcall_start"


@dataclass(frozen=True)
class ToolExecStart(Ev):
    tool: str = ""
    args: dict = field(default_factory=dict)
    kind: ClassVar[str] = "tool_execution_start"


@dataclass(frozen=True)
class ToolExecEnd(Ev):
    tool: str = ""
    result_text: str = ""
    is_error: bool = False
    kind: ClassVar[str] = "tool_execution_end"


@dataclass(frozen=True)
class MessageEnd(Ev):
    role: str = ""
    stop_reason: str = ""
    text: str = ""
    #: ``True`` for the nested stream marker under ``message_update`` /
    #: ``assistant_message_event`` (kind ``message_end``/``text_end``). Pi
    #: ships one of those *and* the authoritative top-level ``message_end``
    #: with the full message; the marker must not fire the sink twice.
    nested: bool = False
    kind: ClassVar[str] = "message_end"


@dataclass(frozen=True)
class Markup(Ev):
    """Silent stream marker (thinking_start/text_start/text_end, …): Pi emits
    these around a section; they carry no content worth surfacing and must
    not reach the sink."""

    kind: ClassVar[str] = "markup"


@dataclass(frozen=True)
class AgentEnd(Ev):
    will_retry: bool = False
    kind: ClassVar[str] = "agent_end"


@dataclass(frozen=True)
class AgentSettled(Ev):
    kind: ClassVar[str] = "agent_settled"


@dataclass(frozen=True)
class UiRequest(Ev):
    id: str = ""
    method: str = ""
    payload: dict = field(default_factory=dict)
    kind: ClassVar[str] = "extension_ui_request"


@dataclass(frozen=True)
class UiPromptStart(Ev):
    kind: ClassVar[str] = "ui_prompt_start"


@dataclass(frozen=True)
class Response(Ev):
    command: str = ""
    success: bool = False
    data: dict = field(default_factory=dict)
    kind: ClassVar[str] = "response"


@dataclass(frozen=True)
class Exit(Ev):
    code: int = 0
    kind: ClassVar[str] = "exit"


@dataclass(frozen=True)
class Unknown(Ev):
    raw: str = ""
    kind: ClassVar[str] = "unknown"


EV_KINDS: dict[str, type] = {
    ev.kind: ev for ev in (
        AgentStart, TurnStart, TurnEnd, MessageStart, ThinkingDelta, ThinkingEnd,
        TextDelta, ToolCallStart, ToolExecStart, ToolExecEnd, MessageEnd,
        AgentEnd, AgentSettled, UiRequest, UiPromptStart, Response, Exit, Unknown,
    )
}


# ------------------------------------------------------- value types
#: P5: the graph's ``task`` node is backed by this typed value (a delegation
#: request) instead of a bare string + text protocol. Not an ``Ev`` — it's a
#: value projected through the ``task`` node, not something the event router
#: consumes.


@dataclass(frozen=True)
class Delegation:
    id: str = ""
    text: str = ""
    tools: tuple = ()          # worker tool allowlist (e.g. SANDBOX_TOOLS)
    model: str = ""            # worker model; "" = use the host default
    source: str = ""           # "chat" | "directive" | "startup" — provenance
    kind: ClassVar[str] = "task"

    @classmethod
    def make(
        cls,
        text: str,
        tools=(),
        model: str = "",
        source: str = "",
    ) -> "Delegation":
        import uuid

        return cls(id=uuid.uuid4().hex[:8], text=text, tools=tuple(tools),
                   model=model, source=source)


# ------------------------------------------------------- state-machine configs
#: Shapes are graph data: states = nodes, transitions = edges. ``timeout`` /
#: ``on_timeout`` / ``on_enter`` / ``guard`` / ``effect`` name runtime-provided
#: implementations (see :mod:`clippy.statemachine`).

WORKER_LIFECYCLE: dict = {
    "initial": "running",
    "states": {
        "running": {},
        "celebrating": {
            "timeout": "celebrate_duration",
            "on_timeout": "celebrate_done",
            "on_enter": "celebrate",
        },
        "exploding": {"on_enter": "explode"},
        "dismissing": {
            "timeout": "dismiss_delay",
            "on_timeout": "dismiss_done",
        },
        "failed": {
            "timeout": "fail_hold",
            "on_timeout": "fail_done",
            "on_enter": "fail",
        },
        "dismissed": {"on_enter": "close"},
    },
    "transitions": [
        {"src": "running", "trigger": "exit", "guard": "success", "to": "celebrating"},
        {"src": "running", "trigger": "exit", "guard": "fail", "to": "failed"},
        {"src": "celebrating", "trigger": "celebrate_done", "to": "exploding"},
        {"src": "exploding", "trigger": "explosion_done", "to": "dismissing"},
        {"src": "dismissing", "trigger": "dismiss_done", "to": "dismissed"},
        {"src": "failed", "trigger": "fail_done", "to": "dismissed"},
    ],
}

PRIME_CONVERSATION: dict = {
    "initial": "idle",
    "states": {
        "idle": {},
        "working": {},
        "answering": {},
    },
    "transitions": [
        {"src": "*", "trigger": "turn_started", "to": "working"},
        {"src": "*", "trigger": "answer", "to": "answering"},
        # A dead brain process must return the SM to idle so queued scheduled
        # brain actions are not stalled forever waiting for an idle prime.
        {"src": "*", "trigger": "exit", "to": "idle"},
        {"src": "*", "trigger": "settled", "to": "idle"},
        {"src": "*", "trigger": "retry", "to": "working"},
    ],
}

#: Lifecycle of a scheduled task (time-and-scheduling, graph/FSM scheduler).
#: The wall-clock tick is the only "cron": a host loop calls ``wake`` on tasks
#: whose ``wake_at`` has passed (see :class:`clippy.scheduler.TaskScheduler`).
#: ``on_enter: "fire"`` runs the task's action when it becomes due; recurring
#: tasks rearm back to ``pending`` (recomputing ``wake_at``), one-shots go to
#: ``done``.
SCHEDULED_TASK: dict = {
    "initial": "pending",
    "states": {
        "pending": {
            "timeout": "until_due",
            "on_timeout": "wake",
        },
        "due": {"on_enter": "fire"},
        "fired": {},
        "cancelled": {},
        "done": {},
    },
    "transitions": [
        {"src": "pending", "trigger": "wake", "to": "due"},
        {"src": "due", "trigger": "fire_done", "to": "fired"},
        {"src": "fired", "trigger": "rearm", "to": "pending"},   # recurring
        {"src": "fired", "trigger": "complete", "to": "done"},   # one-shot
        {"src": "*", "trigger": "cancel", "to": "cancelled"},
    ],
}

# ------------------------------------------------------------ session graph

#: The canonical topology (phase 3). Wired by :mod:`clippy.session`; validated
#: structurally before the app runs.
SESSION_NODES: list[tuple[str, str, str, tuple]] = [
    # id, kind, name, provenance
    ("prime", "external", "Pi RPC process (long-lived brain)", ("015",)),
    ("worker", "external", "Pi --mode json process (one-shot sub-clippy)", ("004", "019")),
    ("event_stream_prime", "interface", "typed event stream from prime", ("015",)),
    ("event_stream_worker", "interface", "typed event stream from worker", ("004", "019")),
    ("prime_controller", "operation", "routers prime events to mood/pane/shell", ("015", "021")),
    ("worker_controller", "operation", "runs the worker lifecycle", ("004", "019", "022")),
    ("mood_sm", "state", "avatar mood state machine", ("003", "022")),
    ("prime_conversation_sm", "state", "idle/working/answering", ("021", "022")),
    ("worker_lifecycle_sm", "state", "running→celebrating→exploding→dismissed", ("004", "022")),
    ("shell", "component", "floating avatar window (status line, bubble, mood)", ("003",)),
    ("shell_worker", "component", "sub-clippy's floating window", ("004",)),
    ("pane", "interface", "w1c chat pane + dialog cards + mode badge", ("010", "016")),
    ("task", "value", "delegation request (typed Delegation)", ("019",), {"type": "Delegation"}),
    ("dialog", "state", "pending consent card", ("016",)),
    ("mode", "state", "sandbox | build", ("005", "017")),
    ("memory_store", "resource", "~/.clippy/memory INDEX + topic files", ("017",)),
    ("skill_allowlist", "constraint", "editable skills.allow (memory, sub-clippy always on)", ("017",)),
    ("consent_gate", "capability", "build-mode approval extension (fail-closed)", ("016",)),
]

SESSION_EDGES: list[tuple[str, str, str, dict, tuple]] = [
    # src, dst, kind, attrs, provenance
    ("prime", "event_stream_prime", "produces", {}, ("015",)),
    ("event_stream_prime", "prime_controller", "consumed_by", {}, ("015", "021")),
    ("prime_controller", "prime_conversation_sm", "drives", {}, ("021", "022")),
    ("prime_controller", "mood_sm", "drives", {}, ("021", "022")),
    ("prime_controller", "shell", "projects_to", {"channel": "mood"}, ("015",)),
    ("prime_controller", "shell", "projects_to", {"channel": "bubble"}, ("015",)),
    ("prime_controller", "pane", "projects_to", {"channel": "answer"}, ("015", "016")),
    ("prime_controller", "pane", "projects_to", {"channel": "card"}, ("016", "021")),
    ("prime_controller", "dialog", "opens", {}, ("016", "021")),
    ("dialog", "pane", "rendered_as", {"channel": "card"}, ("016",)),
    ("chat_input", "prime", "triggers", {"channel": "prompt"}, ("015",)),
    ("chat_input", "task", "triggers", {"channel": "delegate"}, ("019",)),
    ("task", "worker", "depends_on", {}, ("019",)),
    ("task", "worker", "triggers", {"channel": "spawn"}, ("019",)),
    ("worker", "event_stream_worker", "produces", {}, ("004",)),
    ("event_stream_worker", "worker_controller", "consumed_by", {}, ("004", "021")),
    ("worker_controller", "worker_lifecycle_sm", "drives", {}, ("004", "022")),
    ("worker_controller", "shell_worker", "projects_to", {"channel": "mood"}, ("004",)),
    ("worker_controller", "shell_worker", "projects_to", {"channel": "bubble"}, ("004",)),
    ("task", "prime", "completes", {"channel": "report"}, ("019",)),
    ("mode", "prime", "constrains", {"channel": "spawn"}, ("005", "017")),
    ("memory_store", "prime", "injected_into", {}, ("017",)),
    ("skill_allowlist", "prime", "constrains", {}, ("017",)),
    ("consent_gate", "prime", "constrains", {"channel": "build"}, ("016",)),
    ("mode", "pane", "displays", {"channel": "badge"}, ("016", "020")),
    ("mode", "shell", "displays", {"channel": "status"}, ("020",)),
]

SESSION_CONSTRAINTS: list[tuple[str, str, tuple]] = [
    # name, expr, provenance
    ("sandbox", "mode==sandbox ⇒ prime.tools=={read,grep,find,ls} ∧ ¬consent_gate", ("005", "017")),
    ("build", "mode==build ⇒ prime.tools==full ∧ consent_gate", ("005", "016")),
    ("worker_sandbox", "worker.tools=={read,grep,find,ls} unless a user-granted escalation (per worker run)", ("019",)),
    ("single_worker", "exactly-one active worker at a time (else task dropped)", ("004", "019")),
    ("gate_fail_closed", "consent_gate refuses tool when ¬hasUI", ("016",)),
    ("respawn_on_toggle", "mode toggle ⇒ respawn prime (Pi fixes tools at spawn)", ("005", "017")),
]


def build_session_graph() -> Model:
    """The canonical session topology with provenance and constraints."""
    model = Model()
    for row in SESSION_NODES:
        if len(row) == 5:
            id, kind, name, prov, attrs = row
        else:
            id, kind, name, prov = row
            attrs = {}
        model.node(id, kind, name, attrs=attrs, provenance=prov)
    for (src, dst, kind, attrs, prov) in SESSION_EDGES:
        model.edge(src, dst, kind, attrs=attrs, provenance=prov)
    for (name, expr, prov) in SESSION_CONSTRAINTS:
        model.constrain(name, expr, provenance=prov)
    return model


def required_topology() -> list[tuple[str, str, str]]:
    """The connections the app must wire (structural validation target)."""
    return [
        ("prime", "event_stream_prime", "produces"),
        ("event_stream_prime", "prime_controller", "consumed_by"),
        ("prime_controller", "pane", "projects_to"),
        ("prime_controller", "dialog", "opens"),
        ("dialog", "pane", "rendered_as"),
        ("chat_input", "prime", "triggers"),
        ("chat_input", "task", "triggers"),
        ("task", "worker", "triggers"),
        ("worker", "event_stream_worker", "produces"),
        ("event_stream_worker", "worker_controller", "consumed_by"),
        ("worker_controller", "worker_lifecycle_sm", "drives"),
        ("mode", "prime", "constrains"),
        ("memory_store", "prime", "injected_into"),
        ("mode", "pane", "displays"),
    ]


def json_of_event(ev: Ev) -> str:
    return json.dumps({"kind": ev.kind, **_payload(ev)})


def _payload(ev: Ev) -> dict:
    return {
        f.name: getattr(ev, f.name)
        for f in type(ev).__dataclass_fields__.values()
        if f.name != "kind"
    }