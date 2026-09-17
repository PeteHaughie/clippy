"""Single roots-of-truth for Clippy's filesystem layout (ticket 024 / P4).

Every module asks the same three questions — where the user home dir lives,
where scratch work goes, where memory/config live — and gets the answer
here, instead of re-deriving ``Path.home() / ".clippy"`` in several places.

``CLIPPY_ROOT`` honours the optional ``CLIPPY_HOME`` env override so headless
verification (and tests/CI) stays hermetic without touching the real
``~/.clippy``; the default is unchanged.
"""

import datetime
import os
from pathlib import Path


def _default_root() -> Path:
    override = os.environ.get("CLIPPY_HOME", "").strip()
    if override:
        return Path(override).expanduser()
    return Path.home() / ".clippy"


CLIPPY_ROOT = _default_root()
SCRATCH_ROOT = CLIPPY_ROOT / "scratch"
LOGS_DIR = CLIPPY_ROOT / "logs"
MEMORY_DIR = CLIPPY_ROOT / "memory"
MEMORY_INDEX = MEMORY_DIR / "INDEX.md"
USER_CONFIG = CLIPPY_ROOT / "config.json"

#: Repo-internal locations (read-only; independent of CLIPPY_HOME).
PACKAGE_DIR = Path(__file__).resolve().parent
SKILLS_DIR = PACKAGE_DIR / "skills"
DEFAULTS_CONFIG = PACKAGE_DIR / "config.json"


def make_scratch_dir() -> Path:
    """Create and return a timestamped working directory under SCRATCH_ROOT."""
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    d = SCRATCH_ROOT / stamp
    d.mkdir(parents=True, exist_ok=True)
    return d