"""Clippy's persistent memory + skills allowlist (ticket 017).

* **Memory:** a deterministic store at ``~/.clippy/memory/`` with an ``INDEX.md``
  injected into every Pi brain session via ``--append-system-prompt`` (the
  research finding: skills alone are on-demand, so presence must be injected).
  A ``memory`` skill (shipped in ``clippy/skills/memory``) tells the model
  read/write discipline.
* **Skills allowlist:** an editable ``skills.allow`` in the merged config
  (``clippy/config.json`` overridden by ``~/.clippy/config.json``). The memory
  skill is always on; anything else only if the user lists it.
"""

from pathlib import Path

from .moods import load_config

CLIPPY_ROOT = Path.home() / ".clippy"
MEMORY_DIR = CLIPPY_ROOT / "memory"
MEMORY_INDEX = MEMORY_DIR / "INDEX.md"

SKILLS_DIR = Path(__file__).resolve().parent / "skills"

INDEX_STUB = (
    "# Clippy memory index\n\n"
    "One line per note: `[topic] path.md`. Kept current by the `memory` skill.\n"
)


def ensure_memory() -> Path:
    """Create the memory store + INDEX stub if missing. Returns the INDEX path."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    if not MEMORY_INDEX.exists():
        MEMORY_INDEX.write_text(INDEX_STUB)
    return MEMORY_INDEX


def resolve_skill_paths() -> list[str]:
    """Absolute skill paths to expose: the always-on memory skill + the user's
    ``skills.allow`` list (``~``-expanded). Empty allowlist still ships memory."""
    config = load_config().get("skills", {})
    allow = config.get("allow") or []
    paths = [str(Path(p).expanduser()) for p in allow]
    memory_skill = SKILLS_DIR / "memory"
    if memory_skill.exists() and str(memory_skill) not in paths:
        paths.insert(0, str(memory_skill))
    return paths