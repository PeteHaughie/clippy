# ADR-0003: Worker trust model — sandbox by default, per-delegation consent

## Status

Accepted

## Context

Sub-clippies (`/delegate`, the `[CLIPPY::DELEGATE]` directive, `--delegate`)
are separate Pi processes. Two hard constraints shaped the trust model:

1. **Workers were read-only, always.** `_spawn_worker` hard-coded the
   read/search sandbox, and `PiSubAgent` did not load the build-mode gate. A
   delegated task that needed `bash` simply failed — even in build mode.
2. **A one-shot worker cannot ask mid-run.** Workers run
   `pi --mode json -p --no-session`, where `ctx.hasUI === false`, so a gate can
   only *block*, never prompt (Pi fail-closes). Only `--mode rpc` supports the
   `extension_ui_request` → card → `extension_ui_response` round-trip.

So "let a worker run a script" had to be a **spawn-time** decision, not a
per-call one, unless workers were converted to interactive RPC.

## Decision Drivers

- The user's expectation: in build mode, delegating a task that needs commands
  should **ask**, not silently refuse.
- Do not weaken the sandbox default for the common case.
- Keep the change proportional to a personal tool (no worker-pane/UI build-out).
- Preserve the security hardening that made workers sandbox-by-default.

## Considered Options

### Option A — Per-delegation consent grant (chosen)

In build mode (or when explicitly requested), the host raises a **review card**
(Allow / Read-only / Suggest / Dismiss) before spawning. Allow → that one worker
runs with the full mutating tool set for its run; Read-only → sandbox; Suggest →
sandbox with the user's guidance appended; Dismiss → nothing spawns. `/delegate
--allow` and the `[CLIPPY::DELEGATE::ELEVATED]` directive request the card in
any mode. The prime can *request* escalation but never grants it.

### Option B — Interactive RPC worker + per-command gate

Convert escalated workers to `--mode rpc`, load `clippy-gate.ts`, route the
worker's UI requests to the pane. True per-command consent, but the sub-clippy
has no pane (cards would land in the prime's pane), plus a lifecycle/ownership
rewrite.

### Option C — Host-mediated execution

The worker stays read-only and emits a request; the host runs the command with
consent and steers the output back. True one-time semantics, but re-implements
tool execution and needs an RPC worker anyway.

## Decision

Adopt **Option A**: per-delegation consent. Workers remain sandboxed by default
(`resolve_worker_tools` can never return an empty/"all tools" set; `PiSubAgent`
refuses `tools=None`). Escalation is `ESCALATED_TOOLS` for one worker run. MCP
tools are additionally trusted wholesale (see ADR-0002) and available to workers.

## Rationale

1. Matches the user's mental model ("ask me") without a protocol rewrite.
2. Keeps the read-only default and the existing hardening intact.
3. The card already existed as infrastructure (`Pane.ui_request`); a host-dialog
   registry was the only new piece.

## Consequences

### Positive

- Build-mode delegations can mutate after an explicit, per-run grant.
- Sandbox mode and startup `--delegate` stay read-only.
- Host-originated cards resolve locally (also fixes `/test card`).

### Negative

- The grant is **per delegation/run**, not per command: once allowed, the worker
  can run any command until it finishes (granting `bash` makes the tool list
  cosmetic). Documented as the accepted trade-off.
- No auto-deny: an unanswered card waits indefinitely (by request); the pane is
  summoned and an OS notification posted so it isn't missed.

### Risks

- A user could over-grant. Mitigation: the card copy states the scope plainly.

## Implementation Notes

- `Session._confirm_escalation`, `_host_dialog`/`_host_dialogs`,
  `_spawn_delegation`, `ESCALATED_TOOLS`; `parse_delegation` returns an
  `elevated` flag; the pane's `review` card.
- `clippy-gate.ts` is an allowlist; trusted MCP tools are added via
  `CLIPPY_GATE_ALLOW`.
- `model.py` `worker_sandbox` constraint relaxed to "read-only unless a
  user-granted escalation (per worker run)".
- `tests/test_delegation_consent.py`.

## References

- Commit `e34513b` — consent-gated worker escalation
- Commit `5950659` — security hardening (sandbox-by-default workers)
- `docs/remediation-plan.md` — Phases 1, 6
- `research/pi-community-deep-dive.md` (`ctx.hasUI` in json vs rpc)
