"""Clippy's persistent memory + skills allowlist (ticket 017).

* **Memory:** a deterministic store at ``~/.clippy/memory/`` with an ``INDEX.md``
  injected into every Pi brain session via ``--append-system-prompt`` (the
  research finding: skills alone are on-demand, so presence must be injected).
  A ``memory`` skill (shipped in ``clippy/skills/memory``) tells the model
  read/write discipline.
* **Skills allowlist:** an editable ``skills.allow`` in the merged config
  (``clippy/config.json`` overridden by ``~/.clippy/config.json``). The
  Clippy-owned skills (``memory``, ``sub-clippy``) are always on; anything
  else only if the user lists it.
"""

from pathlib import Path

from .config import load_config
from .roots import MEMORY_DIR, MEMORY_INDEX, SKILLS_DIR

#: Clippy-owned skills always exposed regardless of the user's allowlist: the
#: memory-store protocol, the sub-clippy delegation protocol, and the
#: movement protocol.
ALWAYS_ON_SKILLS = ("memory", "sub-clippy", "move")

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
    """Absolute skill paths to expose: the always-on Clippy skills (memory,
    sub-clippy) + the user's ``skills.allow`` list (``~``-expanded). An empty
    allowlist still ships the Clippy-owned skills."""
    config = load_config().get("skills", {})
    allow = config.get("allow") or []
    paths = [str(Path(p).expanduser()) for p in allow]
    for name in ALWAYS_ON_SKILLS:
        skill_dir = SKILLS_DIR / name
        if skill_dir.exists() and str(skill_dir) not in paths:
            paths.insert(0, str(skill_dir))
    return paths


def _parse_skill_frontmatter(md: Path) -> tuple[str, str]:
    """Return ``(name, description)`` from a SKILL.md's YAML frontmatter block.

    Falls back to the directory name / empty description when the file is
    missing or has no ``---`` frontmatter block.
    """
    name = md.parent.name
    description = ""
    if not md.exists():
        return name, description
    parts = md.read_text(encoding="utf-8").split("---", 2)
    if len(parts) < 2:
        return name, description
    for line in parts[1].splitlines():
        stripped = line.strip()
        if stripped.startswith("name:"):
            name = stripped.split(":", 1)[1].strip().strip("'\"") or name
        elif stripped.startswith("description:"):
            description = stripped.split(":", 1)[1].strip().strip("'\"")
    return name, description


def list_skills() -> list[dict]:
    """Name + description for every exposed skill (``resolve_skill_paths()``),
    parsed from each ``SKILL.md``'s YAML frontmatter. Sorted by name."""
    out = []
    for path in resolve_skill_paths():
        skill_dir = Path(path)
        name, description = _parse_skill_frontmatter(skill_dir / "SKILL.md")
        out.append(
            {"name": name, "description": description, "path": str(skill_dir)}
        )
    return sorted(out, key=lambda s: s["name"])