"""Sub-Clippy lifecycle: consume a sub-agent's event queue on the main
thread and drive the shell through thinking → working → complete/fail →
celebrate → explosion → dismiss.

Sits alongside ``ClippyShell.update`` in the clock loop. Only touches
pyglet-rendering APIs from the main thread (the event queue is produced by a
background thread in :mod:`clippy.subagent`).
"""

import pyglet

from .moods import Moods

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


class SubClippyController:
    def __init__(self, shell, subagent, moods: Moods | None = None):
        self.shell = shell
        self.subagent = subagent
        self.moods = moods or shell.avatar.moods
        self.state = "running"  # running|celebrating|exploding|dismissing|failed
        self.failure = None
        self._text = ""
        self._thinking = ""
        self._last_stop_reason = None
        self._timers = {"celebrate": 0.0, "explode": 0.0, "dismiss": 0.0}

    @property
    def done(self) -> bool:
        return self.state in ("exploding", "dismissing", "failed") and self._expired()

    # ------------------------------------------------------------- events

    def update(self, dt: float):
        if self.state in ("dismissing", "failed"):
            self._tick(dt)
        self._drain()
        self._tick(dt)

    def _drain(self):
        q = self.subagent.queue
        while True:
            try:
                event = q.get_nowait()
            except Exception:
                break
            self._handle(event)

    def _handle(self, event):
        etype = event.get("type")
        if etype == "sub_exit":
            self._on_exit(event.get("exit_code"))
        elif etype == "message_update" and event.get("assistantMessageEvent"):
            self._handle_assistant(event["assistantMessageEvent"])
        elif etype == "assistant_message_event":
            self._handle_assistant(event)
        elif etype == "message_end":
            self._last_stop_reason = (event.get("message") or {}).get("stopReason")
        elif etype == "tool_execution_start":
            self._on_tool_start(event)
        elif etype == "tool_execution_end":
            self._on_tool_end(event)
        elif etype == "agent_end":
            self._on_agent_end(event)
        elif etype == "agent_settled":
            pass

    def _handle_assistant(self, ev):
        kind = ev.get("type") or ev.get("eventType")
        if kind == "thinking_delta":
            self._thinking += ev.get("delta", "")
            self.shell.express("thinking")
            self.shell.set_bubble(self._thinking.strip()[-140:])
        elif kind == "text_delta":
            self._text += ev.get("delta", "")
            self.shell.express("thinking")
            self.shell.set_bubble(self._text.strip()[-140:])
        elif kind == "thinking_end":
            self._thinking = (ev.get("content") or self._thinking).strip()[-140:]
            self.shell.set_bubble(self._thinking or self._text)
        elif kind == "text_end":
            pass

    def _on_tool_start(self, event):
        tool = event.get("toolName", "")
        hint = TOOL_HINTS.get(tool, "create")
        self.shell.express("working", hint=hint)
        self.shell.set_bubble(f"working… ({tool})")

    def _on_tool_end(self, event):
        self.shell.express("thinking")
        result = event.get("result") or {}
        content = result.get("content") or []
        text = " ".join(
            b.get("text", "")
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        ).strip()
        if text:
            self.shell.set_bubble(text[-140:])
        if event.get("isError"):
            self.failure = self.failure or text or f"{event.get('toolName')} failed"

    def _on_agent_end(self, event):
        if event.get("willRetry"):
            self._thinking = ""
            self.shell.express("thinking")
            self.shell.set_bubble("retrying…")

    # ------------------------------------------------------------- phases

    def _on_exit(self, exit_code: int):
        failed = exit_code != 0 or self._last_stop_reason in TERMINAL_STOP_REASONS
        if self._last_stop_reason in TERMINAL_STOP_REASONS:
            self.failure = self.failure or f"agent stopped ({self._last_stop_reason})"
        if exit_code != 0:
            self.failure = self.failure or f"sub-agent exited {exit_code}"
        if failed:
            self._begin_fail()
        else:
            self._begin_celebrate()

    def _begin_celebrate(self):
        self.state = "celebrating"
        self.shell.express("idle")
        self.shell.express("celebrate")
        self.shell.set_bubble("Task complete!")
        celebrate = self.shell.avatar.animations.get("Congratulate")
        secs = 3.0
        if celebrate:
            secs = max(sum(fr["duration"] for fr in celebrate["frames"]) / 1000.0, 0.1)
        self._timers["celebrate"] = secs

    def _begin_fail(self):
        self.state = "failed"
        self.failure = self.failure or "sub-agent failed"
        self.shell.express("alert")  # interrupt-ok, wins over continuous moods
        self.shell.set_bubble(f"⚠ {self.failure}")
        self._timers["dismiss"] = FAIL_HOLD

    def _tick(self, dt: float):
        if self.state == "celebrating":
            self._timers["celebrate"] -= dt
            if self._timers["celebrate"] <= 0:
                self.state = "exploding"
                self.shell.trigger_explosion()
        elif self.state == "exploding":
            if not self.shell.explosion.active:
                self._timers["dismiss"] = DISMISS_DELAY
                self.state = "dismissing"
        elif self.state in ("dismissing", "failed"):
            self._timers["dismiss"] -= dt
            if self._timers["dismiss"] <= 0:
                self._dismiss()

    def _expired(self) -> bool:
        return self._timers["dismiss"] <= 0 and self.state in ("dismissing", "failed")

    def _dismiss(self):
        self.state = "dismissed"
        self.shell.close()

    def force_quit(self):
        self.subagent.stop()
        self.shell.close()