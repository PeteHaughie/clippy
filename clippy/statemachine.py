"""Tiny runtime for the graph-declared state machines (phase 2).

Configs (e.g. :data:`clippy.model.WORKER_LIFECYCLE`) are plain graph data:
``states`` are nodes, ``transitions`` are edges. This module executes them
deterministically. Runtime-provided pieces are looked up *by name*:

* ``timeout``  → a callable returning seconds, resolved from ``timeouts`` at
  state entry; the state auto-fires its ``on_timeout`` trigger when it lapses.
* ``guard``    → a predicate ``(sm, *args) -> bool`` from ``guards``; a failing
  guard skips that transition.
* ``on_enter`` → an effect ``(arg) -> None`` from ``effects``, run on entry.

``"*"`` as a transition ``src`` matches any state. A transition ``to`` may be a
string or a callable ``(sm, *args) -> str``.
"""

from __future__ import annotations

from typing import Callable


class StateMachine:
    def __init__(
        self,
        config: dict,
        *,
        effects: dict[str, Callable] | None = None,
        guards: dict[str, Callable] | None = None,
        timeouts: dict[str, Callable] | None = None,
    ):
        self.config = config
        self.effects = effects or {}
        self.guards = guards or {}
        self.timeouts = timeouts or {}
        self.current = config["initial"]
        self._timeout_left: float | None = None
        self._enter(self.current, None)

    # ------------------------------------------------------------- state io

    def _enter(self, name: str, arg):
        self.current = name
        state = self.config["states"][name]
        if state.get("on_enter"):
            self._run(state["on_enter"], arg)
        timeout = state.get("timeout")
        if timeout is not None:
            resolved = self.timeouts.get(timeout) if isinstance(timeout, str) else timeout
            self._timeout_left = resolved() if callable(resolved) else float(resolved)
        else:
            self._timeout_left = None

    def _run(self, effect_name: str, arg):
        fn = self.effects.get(effect_name)
        if fn:
            fn(arg)

    # -------------------------------------------------------------- queries

    def is_in(self, *states) -> bool:
        return self.current in states

    @property
    def done(self) -> bool:
        return self.current == "dismissed"

    # -------------------------------------------------------------- control

    def fire(self, trigger: str, *args, force: bool = False) -> bool:
        """Apply the first matching (src, trigger) transition whose guard
        passes. Returns True if a transition was taken.

        ``force=True`` skips guard evaluation — used for user-driven commands
        (e.g. ``/mood``) that must switch even when the automatic controller's
        interruption rules would otherwise drop the transition.
        """
        for tr in self.config["transitions"]:
            if tr["src"] != "*" and tr["src"] != self.current:
                continue
            if tr["trigger"] != trigger:
                continue
            guard = tr.get("guard")
            if not force and guard:
                guard_fn = self.guards.get(guard)
                if guard_fn and not guard_fn(self, *args):
                    continue
            target = tr.get("to")
            if callable(target):
                target = target(self, *args)
            if target != self.current:
                self._enter(target, args[0] if args else None)
            return True
        return False

    def tick(self, dt: float):
        """Drive timeout transitions."""
        if self._timeout_left is None:
            return
        self._timeout_left -= dt
        if self._timeout_left > 0:
            return
        self._timeout_left = None
        on_timeout = self.config["states"][self.current].get("on_timeout")
        if on_timeout:
            self.fire(on_timeout)