"""Clippy's merged configuration (ticket 024 / P4).

The one canonical config loader: shipped defaults (``clippy/config.json``)
deep-merged under the optional user override (``~/.clippy/config.json``).
:func:`load_config` is the single entry point — previously this lived in
``moods.py`` and the (now deleted) ``llmconfig.py`` stacked a third source
on top.
"""

import copy
import json

from .roots import DEFAULTS_CONFIG, USER_CONFIG


def deep_merge(base: dict, override: dict) -> dict:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config() -> dict:
    data = json.loads(DEFAULTS_CONFIG.read_text())
    if USER_CONFIG.exists():
        data = deep_merge(data, json.loads(USER_CONFIG.read_text()))
    return data