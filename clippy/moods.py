"""Mood catalog for the Clippy avatar.

Loads the shipped defaults from ``clippy/config.json`` and deep-merges the
optional user override at ``~/.clippy/config.json`` on top. Resolves a
``(mood, hint)`` request into a concrete exported animation.
"""

import copy
import json
import random
from pathlib import Path

CLIPPY_CONFIG_DIR = Path.home() / ".clippy"
USER_CONFIG = CLIPPY_CONFIG_DIR / "config.json"

_DEFAULTS_PATH = Path(__file__).resolve().parent / "config.json"

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


def deep_merge(base: dict, override: dict) -> dict:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config() -> dict:
    data = json.loads(_DEFAULTS_PATH.read_text())
    if USER_CONFIG.exists():
        data = deep_merge(data, json.loads(USER_CONFIG.read_text()))
    return data


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


def write_user_config() -> Path:
    """Materialise the shipped defaults at the user override location."""
    CLIPPY_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not USER_CONFIG.exists():
        USER_CONFIG.write_text(_DEFAULTS_PATH.read_text())
    return USER_CONFIG