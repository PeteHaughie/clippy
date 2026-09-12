---
id: 024
title: Roots of truth for paths/config/scratch (P4)
type: refactor
status: closed
assignee: pete
blocked_by: [021, 022, 023]
labels: [wayfinder:prototype]
---

## Question

`CLIPPY_ROOT` / `SCRATCH_ROOT` / `make_scratch_dir` were re-derived in
several modules, the config loader lived in `moods.py` (and the dead
`llmconfig.py` stacked env+secrets+config on top), and the brain imported
`CLIPPY_ROOT` without using it. Where should the app's filesystem and config
truth actually live?

## Resolution

- **`clippy/roots.py`** — the single roots-of-truth for the filesystem: `CLIPPY_ROOT`
  (honouring an opt-in `CLIPPY_HOME` env override so headless verification / CI
  stays hermetic without touching the real `~/.clippy`), `SCRATCH_ROOT`,
  `MEMORY_DIR`, `MEMORY_INDEX`, `USER_CONFIG`, plus the repo-internal
  `PACKAGE_DIR` / `SKILLS_DIR` / `DEFAULTS_CONFIG` and the one
  `make_scratch_dir()` (the subagent + brain duplicates removed).
- **`clippy/config.py`** — the one canonical config loader: shipped defaults
  (`clippy/config.json`) deep-merged under `~/.clippy/config.json`
  (`deep_merge` + `load_config`, relocated from `moods.py`).
- **Consumers** — `subagent.py`, `brain.py`, `memory.py`, `moods.py` import
  from `roots`/`config`; the brain's unused `CLIPPY_ROOT` import dropped.
- **Dead code deleted** — `llmconfig.py`, `secrets.local.json.example`, the
  `"llm"` block in `config.json`, and the never-called `write_user_config`.

## Findings that mattered

- `CLIPPY_HOME` (opt-in) is what makes the headless check hermetic: without it,
  `ensure_memory()` / `make_scratch_dir()`/`load_config()` assertions write
  into the real `~/.clippy`. Default behaviour is byte-unchanged.
- `write_user_config` was never called anywhere — config defaults now live only
  in the shipped `config.json`.

## Acceptance

Headless, hermetic (`CLIPPY_HOME` pointed at a temp dir): roots resolve under
the override; `make_scratch_dir()` creates under `SCRATCH_ROOT`; `ensure_memory()`
writes `memory/INDEX.md`; `load_config()` deep-merges a seeded user override
while keeping unrelated defaults; `resolve_skill_paths()` returns the always-on
`memory`/`sub-clippy` skills + allowlist; `PiSubAgent`/`MockSubAgent`/`MockBrain`
constructors use scratch dirs. `py_compile` clean; `python -m clippy.brain --mock`
settles; `import clippy.session` OK. With `CLIPPY_HOME` unset the default path
still resolves to `~/.clippy` and reads the real user config.