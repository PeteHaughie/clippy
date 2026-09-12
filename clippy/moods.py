"""Mood catalog for the Clippy avatar.

Consumes the merged config from :mod:`clippy.config` — shipped defaults
(``clippy/config.json``) deep-merged under the optional user override
(``~/.clippy/config.json``). Resolves a ``(mood, hint)`` request into a
concrete exported animation.
"""

import random

from .config import load_config

#: Moods that hold until the controller switches away.
CONTINUOUS_MOODS = frozenset({"idle", "thinking", "working", "listening"})

#: Moods that may interrupt a currently-running continuous mood.
INTERRUPT_MOODS = frozenset({"alert"})

#: Wire schema for the future brain → shell channel (ticket 004/008).
#: {"type": "express", "mood": "working", "hint": "build", "text": "…"}
EXPRESS_SCHEMA = {
    "type": "express",
    "properties": {
        "mood": "one of the mood keys (see clippy/config.json)",
        "hint": "activity refinement for the 'working' mood (e.g. build/write/search)",
        "text": "speech-bubble text to accompany the mood",
    },
}


class Moods:
    def __init__(self, config: dict | None = None):
        self.config = config or load_config()
        self.idle = self.config["idle"]
        self.moods = self.config["moods"]

    def is_continuous(self, mood: str) -> bool:
        spec = self.moods.get(mood)
        return mood in CONTINUOUS_MOODS or bool(spec.get("continuous"))

    def can_interrupt(self, mood: str) -> bool:
        spec = self.moods.get(mood, {})
        return mood in INTERRUPT_MOODS or bool(spec.get("interrupt_ok"))

    def resolve(self, mood: str, hint: str | None = None) -> str | None:
        """Return the exported animation name for a (mood, hint) request.

        Falls back to a random pick among the mood's animations, then to the
        idle settle pose if the mood is unknown.
        """
        spec = self.moods.get(mood)
        if spec is None:
            return self.idle["settle"]
        animations = spec.get("animations") or []
        hints = spec.get("hints") or {}
        if hint in hints:
            return hints[hint]
        if animations:
            return random.choice(animations)
        return self.idle["settle"]

    def available_moods(self) -> list[str]:
        return list(self.moods)