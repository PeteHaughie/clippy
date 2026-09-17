"""Host-owned time helpers for Clippy's time awareness.

The host owns the clock (see ADR/research time-and-scheduling): it computes the
current time deterministically and injects a tiny per-turn header into the
brain's prompts — the model never parses timestamps or runs ``date`` (it has no
bash in sandbox mode). ``time_header()`` returns the compact line to prepend.
"""

import datetime


def now_local() -> datetime.datetime:
    return datetime.datetime.now().astimezone()


def format_wallclock(dt: "datetime.datetime | str | None" = None) -> str:
    """``2026-09-17 19:00 (Thu)`` local. Accepts a datetime or an ISO string."""
    if isinstance(dt, str):
        dt = datetime.datetime.fromisoformat(dt)
    dt = dt or now_local()
    return dt.strftime("%Y-%m-%d %H:%M (%a)")


def time_header() -> str:
    """Compact per-turn temporal header for brain prompts.

    ``[Current local time: 2026-09-17 19:00 (Thu), Europe/London]`` — one short
    line the host computes with zero model cost.
    """
    dt = now_local()
    tz = dt.tzname() or "local"
    return f"[Current local time: {format_wallclock(dt)}, {tz}]"


def humanize(dt: datetime.datetime | None = None) -> str:
    """Friendly phrasing for the /time command: "It's 19:00 on Thursday."."""
    dt = dt or now_local()
    return f"It's {dt.strftime('%-I:%M %p').lower()} on {dt.strftime('%A')}."