# ADR-0006: Pi owns inference providers; secrets live outside config

## Status

Accepted

## Context

Clippy needs to use a new inference endpoint (an OpenAI-compatible aggregator,
`api.mammouth.ai`) with an API key. The question was where the provider
definition and the key belong. Clippy is a projection over Pi, and Pi owns
providers, models and credentials: it resolves a provider's `apiKey` from the
CLI, `auth.json`, the environment, or `models.json` (in that order), and it can
load custom OpenAI-compatible providers from `~/.pi/agent/models.json`.

Clippy previously hard-coded `DEFAULT_MODEL = "opencode/deepseek-v4-flash"`, and
`pi_ready()` only recognised the `omlx`/`opencode` provider prefixes.

## Decision Drivers

- Pi is the single owner of providers/models (architecture invariant).
- No secrets in tracked files (or in `config.json`).
- A declarative, config-driven setup ("a config.json entry").
- Clippy should be able to default to a chosen model without a CLI flag.

## Considered Options

- **Provider definition**: Clippy `config.json` vs Pi `models.json` vs an
  extension using `pi.registerProvider()`.
- **Secret storage**: literal in `models.json`, Pi `auth.json`, shell env, or a
  Clippy secrets file.

## Decision

- **Provider definitions live in Pi** — `~/.pi/agent/models.json` for custom
  OpenAI-compatible providers (`api: "openai-completions"`, `baseUrl`,
  `apiKey: "$ENV_VAR"`, `models`). `pi.registerProvider()` remains the escape
  hatch for custom auth/streaming.
- **Secrets live in `~/.clippy/secrets.json`** (outside the repo), a flat map of
  env vars. `clippy/secrets.py` loads it into `os.environ` at startup (an
  already-set env var wins) so the readiness probe and every spawned Pi resolve
  `$ENV_VAR` — with no secret in `config.json` or any tracked file.
- **Clippy config holds policy, not providers**: a `model` default
  (`resolve_model()` = `--model` → config `model` → built-in) and
  `providers.ready` (which prefixes count as "real" for the mock fallback;
  default now includes `mammouth`).

## Rationale

1. Keeps the "Pi owns providers" invariant; Clippy only points at a model.
2. `setdefault` means an exported env var still wins — flexible for CI/shells.
3. Config-driven default model + readiness, no code change to add a provider.

## Consequences

### Positive

- Any OpenAI-compatible endpoint is a `models.json` entry plus a secret.
- Keys stay out of the repo and out of `config.json`.
- `pi_ready()` is provider-agnostic via `providers.ready`.

### Negative / Risks

- Two config files (Pi's and Clippy's) are involved; documented in the README.
- `~/.clippy/secrets.json` is plaintext on disk (user-private); rotate keys if
  ever exposed.

## Implementation Notes

- `clippy/secrets.py`, `clippy/roots.py` (`SECRETS_FILE`),
  `Session.resolve_model` / `resolve_model()`, `subagent._ready_providers()`.
- Repo defaults in `clippy/config.json` (`model`, `providers.ready`).
- `tests/test_providers.py`.
- Configured Mammouth in `~/.pi/agent/models.json` (93 models) and
  `~/.clippy/secrets.json`; verified with `pi --list-models mammouth` and a live
  completion.

## References

- Commit `7c1c5a8` — MCP bridge + providers
- `docs/remediation-plan.md` — Phase 9
- Pi package docs: `docs/models.md`, `docs/providers.md` (resolution order)
