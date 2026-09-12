"""Sub-Clippy lifecycle (phase 2, graph-model refactor).

Consumes a sub-agent's event queue on the main thread and drives the shell
through the **worker lifecycle state machine** (declared as graph data in
:data:`clippy.model.WORKER_LIFECYCLE`):

    running → celebrating → exploding → dismissing → dismissed
        └──failed──────────────────────────────┘

Event parsing + thinking/text accumulation live in the shared
:class:`clippy.events.AgentEventRouter`; this controller is an
:class:`clippy.events.EventSink` that reacts. Only touches pyglet-rendering
APIs from the main thread (the queue is produced by a background thread in
:mod:`clippy.subagent`).
"""

import pyglet

from .events import AgentEventRouter, EventSink
from .moods import Moods
from .model import WORKER_LIFECYCLE
from .statemachine import StateMachine

#: Danger words/tool names → working-mood hint.
TOOL_HINTS = {
    "bash": "build",
    "write": "write",
    "read": "read",
    "search": "search",
    "print": "print",
    "save": "save",
    "mail": "mail",
}

DISMISS_DELAY = 1.0  # seconds after the explosion finishes before closing
FAIL_HOLD = 4.0      # seconds a failure window stays before closing

TERMINAL_STOP_REASONS = {"error", "aborted"}


def _celebrate_seconds(shell) -> float:
    anim = shell.avatar.animations.get("Congratulate")
    if not anim:
        return 3.0
    return max(sum(fr["duration"] for fr in anim["frames"]) / 1000.0, 0.1)


class SubClippyController(EventSink):
    def __init__(self, shell, subagent, moods: Moods | None = None, on_complete=None):
        self.shell = shell
        self.subagent = subagent
        self.moods = moods or shell.avatar.moods
        self.on_complete = on_complete  # on_complete(failed: bool, report: str)
        self.failure = None
        self.answer = ""
        self._last_stop_reason = None
        self.router = AgentEventRouter(self)
        self.sm = StateMachine(
            WORKER_LIFECYCLE,
            effects=self._effects(),
            guards=self._guards(),
            timeouts=self._timeouts(),
        )

    @property
    def done(self) -> bool:
        return self.sm.done

    # ------------------------------------------------------------- machine

    def _effects(self):
        return {
            "celebrate": self._celebrate,
            "explode": lambda _arg: self.shell.trigger_explosion(),
            "fail": self._fail,
            "close": lambda _arg: self.shell.close(),
        }

    def _guards(self):
        return {
            "success": lambda _sm, failed: not failed,
            "fail": lambda _sm, failed: bool(failed),
        }

    def _timeouts(self):
        return {
            "celebrate_duration": lambda: _celebrate_seconds(self.shell),
            "dismiss_delay": lambda: DISMISS_DELAY,
            "fail_hold": lambda: FAIL_HOLD,
        }

    def _celebrate(self, _arg):
        self.shell.express("idle")
        self.shell.express("celebrate")
        self.shell.set_bubble("Task complete!")

    def _fail(self, _arg):
        self.shell.express("alert")  # interrupt-ok, wins over continuous moods
        self.shell.set_bubble(f"⚠ {self.failure}")

    # ------------------------------------------------------------- control

    def update(self, dt: float):
        self.sm.tick(dt)
        self._drain()
        self.sm.tick(dt)
        if self.sm.is_in("exploding") and not self.shell.explosion.active:
            self.sm.fire("explosion_done")

    def _drain(self):
        q = self.subagent.queue
        while True:
            try:
                raw = q.get_nowait()
            except Exception:
                break
            self.router.feed_raw(raw)

    def force_quit(self):
        self.subagent.stop()
        self.shell.close()

    # -------------------------------------------------------------- events

    def thinking(self, text: str):
        self.shell.express("thinking")
        self.shell.set_bubble(text)

    def text(self, text: str):
        self.shell.express("thinking")
        self.shell.set_bubble(text)

    def tool_start(self, tool: str):
        hint = TOOL_HINTS.get(tool, "create")
        self.shell.express("working", hint=hint)
        self.shell.set_bubble(f"working… ({tool})")

    def tool_end(self, ev):
        self.shell.express("thinking")
        if ev.result_text:
            self.shell.set_bubble(ev.result_text[-140:])
        if ev.is_error:
            self.failure = self.failure or ev.result_text or f"{ev.tool} failed"

    def message_end(self, stop_reason: str, text: str):
        self._last_stop_reason = stop_reason
        if text:
            self.answer = text

    def retry(self):
        self.shell.express("thinking")
        self.shell.set_bubble("retrying…")

    def unparseable(self, raw: str):
        self.shell.set_bubble("(unparseable event from sub-agent)")

    def exit(self, exit_code: int):
        failed = exit_code != 0 or self._last_stop_reason in TERMINAL_STOP_REASONS
        if self._last_stop_reason in TERMINAL_STOP_REASONS:
            self.failure = self.failure or f"agent stopped ({self._last_stop_reason})"
        if exit_code != 0:
            self.failure = self.failure or f"sub-agent exited {exit_code}"
        if self.on_complete:
            self.on_complete(failed, self.answer or self.failure or "")
        self.sm.fire("exit", failed)