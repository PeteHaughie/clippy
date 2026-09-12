"""Session graph (phase 3): the app's topology as data, wired from edges.

:class:`Session` owns the live app: the prime Pi process (or mock), the prime
controller, the pane, and one sub-clippy worker at a time. Its wiring is a
*projection of* :func:`clippy.model.build_session_graph` — the callback
channels (answer/card/prompt) come from the graph's ``projects_to`` /
``triggers`` / ``rendered_as`` edges, and the topology is validated
structurally before the app runs. ``Session.dump()`` is the provenance view:
"why does this event reach the pane?".

Mode (sandbox ↔ build) re-spawns the prime because Pi 0.85.1 fixes the tool
set at spawn only (research/pi-community-deep-dive.md §3).
"""

from __future__ import annotations

from pathlib import Path

import pyglet

from .brain import DEFAULT_MODEL, MockBrain, PiBrain
from .controller import SubClippyController
from .memory import ensure_memory, resolve_skill_paths
from .model import build_session_graph, required_topology
from .pane import Pane
from .prime import PrimeController
from .subagent import (
    DEFAULT_TASK,
    DELEGATE_CMD,
    MockSubAgent,
    PiSubAgent,
    parse_delegation,
    pi_ready,
)

#: Read/search-only tool allowlist for a sandboxed conversation (005).
SANDBOX_TOOLS = ["read", "grep", "find", "ls"]
#: Build-mode consent gate extension (016): asks before mutating tools.
GATE_EXT = str(
    Path(__file__).resolve().parent / "extensions" / "clippy-gate.ts"
)

SUB_POS = (560, 420)


class Session:
    def __init__(self, shell, model: str = DEFAULT_MODEL, real: bool = False):
        self.shell = shell
        self.model = model
        self.real = real
        self.mode = "sandbox"
        self.brain = None
        self.prime_controller = None
        self._worker_controller = None

        self.graph = build_session_graph()
        self._validate_topology()

        self.pane = Pane(shell)
        shell.pane = self.pane
        self.pane.start_driver()
        self.pane.on_mode_toggle = self.toggle

        self._spawn_prime()
        self._wire()

    # ------------------------------------------------------------ topology

    def _validate_topology(self):
        missing = self.graph.validate_topology(required_topology())
        if missing:
            raise RuntimeError(
                "session graph missing required connections:\n- " + "\n- ".join(missing)
            )

    def _wire(self):
        """Bind callbacks from the graph edges (the wiring is a projection)."""
        for e in self.graph.edges_of("projects_to"):
            if e.dst == "pane" and e.attrs.get("channel") == "answer":
                self.prime_controller.on_answer = self._on_answer
            elif e.dst == "pane" and e.attrs.get("channel") == "card":
                self.prime_controller.on_ui_request = self.pane.ui_request
        for e in self.graph.edges_of("triggers"):
            if e.src == "chat_input" and e.dst == "prime":
                self.pane.on_chat = self.prompt  # prompt() also dispatches /delegate
        for e in self.graph.edges_of("rendered_as"):
            if e.src == "dialog" and e.dst == "pane":
                self.pane.on_ui_response = self.ui_response

    def dump(self) -> str:
        return self.graph.dump()

    # --------------------------------------------------------------- prime

    def _brain_kwargs(self) -> dict:
        kwargs = {"model": self.model}
        if self.mode == "sandbox":
            kwargs["tools"] = SANDBOX_TOOLS
        else:
            kwargs["extensions"] = [GATE_EXT]
        kwargs["append_system_prompt"] = ensure_memory()
        kwargs["skills"] = resolve_skill_paths()
        return kwargs

    def _spawn_prime(self):
        if self.real or pi_ready():
            brain = PiBrain(**self._brain_kwargs())
            print(f"[clippy] prime brain: {self.mode} mode on Pi RPC ({self.model})")
        else:
            brain = MockBrain()
            print("[clippy] Pi not ready — prime brain on mock")
        self.brain = brain
        self.prime_controller = PrimeController(self.shell, brain)
        self.shell.mode = self.mode
        self.shell.dialog_pending = False
        brain.start()
        pyglet.clock.schedule_interval(self.prime_controller.update, 1 / 60)
        self.pane.set_mode(self.mode)

    def prompt(self, text: str):
        stripped = text.strip()
        if stripped.lower().startswith(DELEGATE_CMD):
            task = stripped[len(DELEGATE_CMD):].strip()
            if not task:
                self.pane.add_message(
                    "clippy", "What should the sub-clippy do? e.g. `/delegate count the markdown files`"
                )
                return
            self._start_delegation(task)
            return
        self.brain.prompt(text, streaming_behavior="followUp")

    def ui_response(self, rid, payload: dict):
        self.brain.send({"type": "extension_ui_response", "id": rid, **payload})
        self.shell.dialog_pending = False

    def toggle(self):
        self.brain.stop()
        self.mode = "build" if self.mode == "sandbox" else "sandbox"
        print(f"[clippy] mode -> {self.mode} (re-spawning brain)")
        self._spawn_prime()
        self.prompt(f"Mode is now {self.mode}.")

    def _on_answer(self, text: str):
        """Prime's final message: surface it in the pane, and if it carries a
        [CLIPPY::DELEGATE] directive (the sub-clippy composition skill), spawn
        a sandboxed worker for the task and steer its report back in."""
        clean, task = parse_delegation(text)
        if task:
            self.shell.set_bubble("(handing off to a sub-clippy…)")
            self.delegate(task, tools=SANDBOX_TOOLS, on_complete=self._on_sub_done)
        if clean:
            self.pane.add_message("clippy", clean)
        elif task:
            self.pane.add_message(
                "clippy", "I've handed that to a sub-clippy — report back shortly."
            )

    def _on_sub_done(self, failed: bool, report: str):
        self.shell.set_bubble("(sub-clippy finished — relaying)")
        if report:
            self.pane.add_message("clippy", f"Sub-clippy reported: {report}")
        self.brain.steer(
            "The delegated sub-clippy finished"
            f"{' with an error' if failed else ''}. "
            f"Relay its report to the user plainly: {report or '(no report)'}"
        )

    # --------------------------------------------------------------- worker

    def delegate(self, task: str = DEFAULT_TASK, tools=None, on_complete=None) -> bool:
        """Spawn a sub-clippy for ``task``. Returns False if already delegating.
        The slot frees itself when the worker completes, so a later delegation
        can start a new one."""
        if self._worker_controller is not None:
            print("[clippy] already delegating")
            return False

        def _wrap(failed: bool, report: str):
            self._worker_controller = None
            if on_complete:
                on_complete(failed, report)

        self._worker_controller = self._spawn_worker(task, tools=tools, on_complete=_wrap)
        return True

    def _spawn_worker(self, task: str, tools=None, on_complete=None) -> SubClippyController:
        if self.real or pi_ready():
            agent = PiSubAgent(task=task, model=self.model, tools=tools)
            print(f"[clippy] delegating to PI sub-agent ({self.model})")
        else:
            agent = MockSubAgent(task=task)
            print("[clippy] PI not ready — delegating to mock sub-agent")
        shell = ClippyShell(position=SUB_POS)
        ctrl = SubClippyController(shell, agent, on_complete=on_complete)
        shell.show()
        pyglet.clock.schedule_interval(shell.update, 1 / 60)
        pyglet.clock.schedule_interval(ctrl.update, 1 / 60)
        agent.start()
        return ctrl

    def _start_delegation(self, task: str):
        self.shell.set_bubble("(handing off to a sub-clippy…)")
        ok = self.delegate(task, tools=SANDBOX_TOOLS, on_complete=self._on_sub_done)
        if not ok:
            self.pane.add_message(
                "clippy", "A sub-clippy is already at work — let it finish first."
            )
        else:
            self.pane.add_message(
                "clippy", "Handed that to a sub-clippy — report back shortly."
            )
            self.brain.steer(f"The user delegated this task to a sub-clippy: {task}")