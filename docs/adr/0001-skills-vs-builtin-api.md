# ADR-0001: Distinguish Clippy skills from the built-in command API

## Status

Accepted

## Context

Clippy has two overlapping "capability" surfaces that users and maintainers
conflate:

1. **Skills** — `clippy/skills/<name>/SKILL.md` folders. Loaded into the Pi brain
   via `--skill` (from `resolve_skill_paths()`, `clippy/memory.py`) as
   model-invocable tools under the [Agent Skills standard](https://agentskills.io/specification).
   The model invokes them to emit host directives and do work.
2. **Built-in API** — host-intercepted slash commands (`/help`, `/mood`, `/move`,
   `/delegate`, `/where`) implemented in `Session.prompt()`. Deterministic,
   bypass the model, and are the reliable demo path.

The conflation: `move` and `sub-clippy` are skill folders **and** have
deterministic slash commands (`/move`, `/delegate`). Users read them as "built-in
API" because the command is how they're reliably exercised, but the folders exist
to teach the *model* to autonomously emit `[CLIPPY::MOVE]` / `[CLIPPY::DELEGATE]`
directives which the host executes. Research in this repo
(`research/chat-loop.md`, `wayfinder/tickets/002`, `019`) documents that skills
are on-demand and that small models won't reliably invoke them on their own —
which is exactly why the deterministic commands exist as an overlay.

Clippy currently has no user-facing way to enumerate his skills, so we need
`/skills` (list) and `/skill <name>` (invoke). The open question is how the two
surfaces relate and what `/skills` should present.

## Decision Drivers

- **Determinism is preferred wherever possible** (maintainer requirement).
- `/skills` should reflect the skill folder contents as the single source of
  truth, not a parallel taxonomy.
- Slash commands must not be relabelled "skills" merely because they are
  slash-accessed.
- Skills added later (new folder or `skills.allow`) should surface
  automatically.

## Considered Options

### Option A — "folder truth"

`/skills` lists `resolve_skill_paths()` (`memory`, `move`, `sub-clippy` + any
allowlisted skills). `/skill <name> [request]` invokes a folder item:
`move` → `/move` logic, `sub-clippy` → `/delegate` logic (deterministic), and
`memory` / user skills → brain routing ("Use the '<name>' skill to handle
this: …"). The listing annotates which skills have a built-in command alias.

- **Pros**: matches "list the folder contents"; future-proof; one consistent
  rule; the dual nature is made explicit rather than hidden.
- **Cons**: `move`/`sub-clippy` appear as skills, which reads oddly to anyone who
  thinks of them as commands; `/move` vs `/skill move` is a mild redundancy.

### Option B — "command first"

Treat `move`/`sub-clippy` as built-in API only; `/skills` lists just the model
skills that lack a command (`memory` + allowlisted skills).

- **Pros**: avoids the `/move` vs `/skill move` redundancy.
- **Cons**: diverges from the folder as source of truth; requires an arbitrary
  "is this a skill or a command?" classification rule that will age badly as new
  skills arrive.

## Decision

Adopt **Option A (folder truth)**:

- `/skills` lists the enabled skill folder (`resolve_skill_paths()`), each item
  with its `SKILL.md` name + description, annotated with a built-in command alias
  where one exists (`move` → `/move`, `sub-clippy` → `/delegate`).
- `/skill <name> [request]` invokes a skill: deterministic built-in API for
  `move` and `sub-clippy`, brain routing for `memory` and any other/user skill.
- `/move` and `/delegate` remain built-in API aliases and are **not** relabelled
  as skills in the command help; `/help` lists commands and points at `/skills`
  for the skill list.

## Rationale

1. **Single source of truth** — the folder. Every enabled skill is listed and
   invocable; none is silently hidden by a classification rule.
2. **Determinism where the host can provide it** — `move` / `sub-clippy` map to
   the existing deterministic commands; the model is only relied on for skills
   with no host implementation (`memory`, user skills).
3. **Transparency** — the dual nature of `move`/`sub-clippy` (skill folder +
   command alias) is annotated in the listing instead of being a source of
   confusion.

## Consequences

### Positive

- Clippy can enumerate his skills (`/skills`) and invoke one by name (`/skill`).
- New skills (folder or `skills.allow`) appear automatically with no code change.
- The skill/command distinction is documented both in code annotations and here.

### Negative

- `/move` and `/skill move …` are two paths to the same behavior. Accepted: the
  command is the ergonomic alias; the skill path keeps the model (and users)
  able to reference the capability by its canonical name.
- `/skill` invocation of brain-routed skills (`memory`, user skills) is
  model-dependent and may not fire reliably on small models — the same known
  limit as autonomous skill use.

### Risks

- Users may expect `/skill <name>` to be fully deterministic for every skill.
  Mitigation: the `/skills` listing and `/help` wording make clear which skills
  are host-backed (deterministic) versus model-backed.

## Implementation Notes

- `clippy/memory.list_skills()` parses each exposed `SKILL.md`'s YAML frontmatter
  (`name`, `description`) from `resolve_skill_paths()`.
- `Session.prompt()` handles `/skills` (list) and `/skill <name> [request]`
  (invoke); unknown skill names and missing requests return helpful messages.
- `HELP_TEXT` keeps commands (built-in API) and skills (folder) distinct and
  points `/help` → `/skills`.

## References

- `clippy/memory.py` — `resolve_skill_paths()` / skill allowlist
- `clippy/skills/{memory,move,sub-clippy}/SKILL.md`
- `research/chat-loop.md` — skill-as-tool mapping, "skills are on-demand" note
- `wayfinder/tickets/002-clippy-chat-loop-and-skill-as-tool.md`
- `wayfinder/tickets/017-skills-allowlist-sandbox-memory.md`
- `wayfinder/tickets/019-sub-clippy-composition-skill.md` (small-model reliability note)