"""Provider secrets from ``~/.clippy/secrets.json``.

Pi owns providers and resolves a provider's ``apiKey`` from the environment
(``models.json`` can reference ``$ENV_VAR``). Clippy loads this flat JSON object
into ``os.environ`` so the readiness probe (``pi --list-models``) and every
spawned Pi process see the keys — without putting them in a tracked file or in
``config.json``.

Shape (a flat map, or nested under ``"env"``)::

    { "MAMMOUTH_API_KEY": "sk-..." }
"""

from __future__ import annotations

import json
import os

from .roots import SECRETS_FILE


def load() -> dict[str, str]:
    """The configured secrets (empty if the file is missing or malformed)."""
    if not SECRETS_FILE.exists():
        return {}
    try:
        data = json.loads(SECRETS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    env = data.get("env") if isinstance(data.get("env"), dict) else data
    return {
        str(key): str(value)
        for key, value in env.items()
        if isinstance(value, (str, int, float))
    }


def apply_to_environ() -> dict[str, str]:
    """Merge secrets into ``os.environ`` (an already-set var wins). Returns them."""
    secrets = load()
    for key, value in secrets.items():
        os.environ.setdefault(key, value)
    return secrets
