"""Graph/FSM task scheduler for Clippy (time-and-scheduling).

A scheduled task is a small :class:`clippy.statemachine.StateMachine` running
the :data:`clippy.model.SCHEDULED_TASK` config (pending → due → fired →
rescheduled|done). The wall-clock tick — driven from ``Session.update`` — is the
only "cron": it fires tasks whose ``wake_at`` has passed and advances the FSM.
The schedule itself is graph data, persisted to JSONL so tasks survive Clippy's
volatile session state and reload on the next run.

Triggers (round one): one-shot ``at``/``in``, ``interval``, and ``daily``. An
action is either a deterministic host effect (pane message, mood) or a ``brain``
prompt — which the host queues and fires when the prime is idle (no heartbeat).
"""

import datetime
import json
import time
import uuid
from pathlib import Path

from .model import SCHEDULED_TASK
from .roots import SCHEDULER_FILE
from .statemachine import StateMachine

#: Time-unit multipliers for the /remind parser.
_UNIT_SECONDS = {
    "s": 1, "sec": 1, "secs": 1, "second": 1, "seconds": 1,
    "m": 60, "min": 60, "mins": 60, "minute": 60, "minutes": 60,
    "h": 3600, "hr": 3600, "hrs": 3600, "hour": 3600, "hours": 3600,
    "d": 86400, "day": 86400, "days": 86400,
}


def _now() -> datetime.datetime:
    return datetime.datetime.now().astimezone()


def _to_iso(dt: datetime.datetime) -> str:
    return dt.astimezone().isoformat()


def parse_trigger(text: str) -> tuple[dict, str]:
    """Parse ``/remind <when> <what>`` into ``(trigger, what)``.

    Supported round-one forms:
      ``in N <unit>``        e.g. "in 5 minutes"   → one-shot
      ``at HH:MM``           e.g. "at 14:30"        → one-shot today/tomorrow
      ``every N <unit>``     e.g. "every 2 hours"   → interval
      ``daily at HH:MM``     e.g. "daily at 9:00"   → daily
    Returns ``({}, "")`` for an unrecognised trigger. The ``what`` text keeps
    its original case.
    """
    import re

    def _unit_seconds(word: str) -> int | None:
        w = word.lower()
        if w in _UNIT_SECONDS:
            return _UNIT_SECONDS[w]
        if w.endswith("s") and w[:-1] in _UNIT_SECONDS:
            return _UNIT_SECONDS[w[:-1]]
        return None

    m = re.match(r"in\s+(\d+)\s*([a-z]+)\b(.*)", text, re.IGNORECASE | re.DOTALL)
    if m:
        n, unit, rest = int(m.group(1)), m.group(2), m.group(3)
        secs = _unit_seconds(unit)
        if secs:
            return {"type": "in", "seconds": n * secs}, rest.strip()
    m = re.match(r"every\s+(\d+)\s*([a-z]+)\b(.*)", text, re.IGNORECASE | re.DOTALL)
    if m:
        n, unit, rest = int(m.group(1)), m.group(2), m.group(3)
        secs = _unit_seconds(unit)
        if secs:
            return {"type": "interval", "seconds": n * secs}, rest.strip()
    m = re.match(r"daily\s+at\s+(\d{1,2}):(\d{2})\b(.*)", text, re.IGNORECASE | re.DOTALL)
    if m:
        return {"type": "daily", "hour": int(m.group(1)), "minute": int(m.group(2))}, m.group(3).strip()
    m = re.match(r"at\s+(\d{1,2}):(\d{2})\b(.*)", text, re.IGNORECASE | re.DOTALL)
    if m:
        return {"type": "at", "hour": int(m.group(1)), "minute": int(m.group(2))}, m.group(3).strip()
    return {}, ""


def _next_wake(trigger: dict, now: datetime.datetime) -> datetime.datetime:
    t = trigger.get("type")
    if t == "in":
        return now + datetime.timedelta(seconds=trigger["seconds"])
    if t == "at":
        when = now.replace(hour=trigger["hour"], minute=trigger["minute"], second=0, microsecond=0)
        if when <= now:
            when += datetime.timedelta(days=1)  # "at 9:00" after 9:00 → tomorrow
        return when
    if t == "daily":
        when = now.replace(hour=trigger["hour"], minute=trigger["minute"], second=0, microsecond=0)
        if when <= now:
            when += datetime.timedelta(days=1)
        return when
    if t == "interval":
        return now + datetime.timedelta(seconds=trigger["seconds"])
    raise ValueError(f"unknown trigger {trigger!r}")


class Task:
    """One scheduled task: a SCHEDULED_TASK state machine + trigger + action."""

    def __init__(self, trigger: dict, action: dict, wake_at: datetime.datetime, task_id: str | None = None):
        self.id = task_id or uuid.uuid4().hex[:8]
        self.trigger = trigger
        self.action = action
        self.wake_at = wake_at
        self.created_at = _now()

    def is_recurring(self) -> bool:
        return self.trigger.get("type") in ("interval", "daily")


class TaskScheduler:
    """JSONL-persisted graph/FSM scheduler driven by a wall-clock tick."""

    def __init__(self, dispatch=None, path: Path = SCHEDULER_FILE):
        self.dispatch = dispatch or (lambda action: None)
        self.path = Path(path)
        self._tasks: dict[str, Task] = {}
        self._sms: dict[str, StateMachine] = {}
        self._last_mono = time.monotonic()
        self._load()

    # ------------------------------------------------------------- access

    def list(self) -> list[dict]:
        return [
            {
                "id": t.id,
                "trigger": t.trigger,
                "action": t.action,
                "wake_at": _to_iso(t.wake_at),
                "state": self._sms[t.id].current,
            }
            for t in self._tasks.values()
            if self._sms[t.id].current not in ("done", "cancelled")
        ]

    def cancel(self, task_id: str) -> bool:
        sm = self._sms.get(task_id)
        if sm is None:
            return False
        sm.fire("cancel")
        self._save()
        return True

    def brief(self, limit: int = 3) -> str:
        """Compact model-passable summary of upcoming tasks (for injection)."""
        upcoming = sorted(
            self.list(), key=lambda d: d["wake_at"]
        )[:limit]
        if not upcoming:
            return "Nothing scheduled."
        lines = ["Upcoming schedule:"]
        for d in upcoming:
            lines.append(
                f"- {d['wake_at'][:16]} — {d['action'].get('text') or d['action'].get('mood') or d['action'].get('type')}"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------- control

    def add(self, trigger: dict, action: dict) -> Task:
        task = Task(trigger, action, _next_wake(trigger, _now()))
        self._tasks[task.id] = task
        self._sms[task.id] = self._make_sm(task)
        self._save()
        return task

    def _make_sm(self, task: Task) -> StateMachine:
        return StateMachine(
            SCHEDULED_TASK,
            effects={"fire": lambda _arg: self.dispatch(task.action)},
            timeouts={"until_due": lambda: self._until_due(task)},
        )

    def _until_due(self, task: Task) -> float:
        return max(0.0, (task.wake_at - _now()).total_seconds())

    def tick(self, now: datetime.datetime | None = None):
        """Advance every task's FSM by real elapsed time; fire due tasks."""
        now = now or _now()
        mono = time.monotonic()
        dt = mono - self._last_mono
        self._last_mono = mono
        for task in list(self._tasks.values()):
            sm = self._sms[task.id]
            if sm.current in ("done", "cancelled"):
                continue
            before = sm.current
            sm.tick(max(0.0, dt))
            if sm.current == "due" and before == "pending":
                sm.fire("fire_done")
                if task.is_recurring():
                    task.wake_at = _next_wake(task.trigger, now)
                    sm.fire("rearm")
                else:
                    sm.fire("complete")
                self._save()

    # ------------------------------------------------------------- persistence

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fh:
            for task in self._tasks.values():
                rec = {
                    "id": task.id,
                    "trigger": task.trigger,
                    "action": task.action,
                    "wake_at": _to_iso(task.wake_at),
                    "created_at": _to_iso(task.created_at),
                    "state": self._sms[task.id].current,
                }
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def _load(self):
        if not self.path.exists():
            return
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("state") in ("done", "cancelled"):
                continue
            wake = datetime.datetime.fromisoformat(rec["wake_at"])
            task = Task(
                rec["trigger"], rec["action"], wake, task_id=rec["id"]
            )
            if rec.get("created_at"):
                try:
                    task.created_at = datetime.datetime.fromisoformat(rec["created_at"])
                except ValueError:
                    pass
            self._tasks[task.id] = task
            self._sms[task.id] = self._make_sm(task)