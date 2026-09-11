"""Resolve Clippy's chat-loop endpoint (OpenAI-compatible, BYOK).

Precedence (highest first):
1. Environment: ``OPENAI_BASE_URL``, ``OPENAI_API_KEY``, ``CLIPPY_MODEL``
2. ``clippy/secrets.local.json`` (gitignored): ``{"api_key": "sk-…"}``
3. Merged config (shipped ``clippy/config.json`` overridden by ``~/.clippy/config.json``)
"""

import json
import os
from pathlib import Path

from .moods import load_config

CLIPPY_DIR = Path(__file__).resolve().parent
SECRETS_FILE = CLIPPY_DIR / "secrets.local.json"
SECRETS_EXAMPLE = CLIPPY_DIR / "secrets.local.json.example"


class EndpointError(RuntimeError):
    pass


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        raise EndpointError(f"invalid JSON in {path}: {exc}") from exc


def _env(key: str) -> str | None:
    value = os.environ.get(key, "").strip()
    return value or None


def resolve_endpoint(require_key: bool = True) -> dict:
    """Return ``{"base_url", "api_key", "model", "provider"}``."""
    config = load_config().get("llm", {})
    secrets = _read_json(SECRETS_FILE)

    base_url = (
        _env("OPENAI_BASE_URL")
        or config.get("base_url")
        or ""
    ).rstrip("/")
    model = _env("CLIPPY_MODEL") or config.get("model") or ""
    api_key = _env("OPENAI_API_KEY") or secrets.get("api_key") or ""
    provider = config.get("provider", "openai-compatible")

    if require_key and not api_key:
        if not base_url:
            raise EndpointError(
                "No LLM endpoint configured. Set OPENAI_BASE_URL / CLIPPY_MODEL "
                "env vars, or add base_url + model to ~/.clippy/config.json."
            )
        raise EndpointError(
            "No API key configured. Create clippy/secrets.local.json from "
            "clippy/secrets.local.json.example, or set OPENAI_API_KEY. "
            "Use a dummy key ('clippy-local') for local servers that ignore auth."
        )

    if not base_url:
        base_url = "https://api.openai.com/v1"
    if not model:
        raise EndpointError(
            "No model configured. Set CLIPPY_MODEL env or model in ~/.clippy/config.json."
        )

    return {
        "base_url": base_url,
        "api_key": api_key,
        "model": model,
        "provider": provider,
    }


def write_secrets_example():
    """Materialise clippy/secrets.local.json.example if missing."""
    if not SECRETS_EXAMPLE.exists() and not SECRETS_FILE.exists():
        SECRETS_EXAMPLE.write_text('{\n  "api_key": "sk-your-key-here"\n}\n')
    return SECRETS_EXAMPLE