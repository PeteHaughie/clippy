# ADR-0002: Bridge MCP servers into Pi via an extension

## Status

Accepted

## Context

Clippy is a projection over Pi: **Pi owns tools, skills, providers and
approvals**. A user-provided **MCP** (Model Context Protocol) server — e.g.
`personal-assistant-mcp` at `~/Projects/personal-assistant-mcp` — exposes typed,
guardrailed tools that internally run shell commands, and is meant to be usable
by an agent **without shell access** (the sandboxed prime).

Pi 0.85.1 has **no built-in MCP**: there are no `mcp` strings in the bundle, no
`docs/mcp.md`, and `docs/usage.md` states Pi "intentionally does not include
built-in MCP… build or install those workflows as extensions or packages." So
exposing MCP requires a bridge. The tools must reach both the prime and
sub-clippies, in **sandbox** and **build** mode.

Relevant Pi facts (verified in `@earendil-works/pi-coding-agent@0.85.1`):

- Extensions can register LLM-callable tools via `pi.registerTool()` and can be
  loaded per-process with `-e`.
- `--tools` is a strict allowlist covering **built-in, extension and custom**
  tools; a spike confirmed `--tools read,<custom>` activates an
  extension-registered tool.
- Extension factories must not start background processes; use `session_start`
  and register an idempotent `session_shutdown` cleanup.
- `tool_call` fires for custom tools too, so `clippy-gate.ts` can gate them.

## Decision Drivers

- Pi stays the single owner of tools — no parallel tool taxonomy in Clippy.
- **No new runtime dependency / no npm install / offline-friendly** for a
  personal tool.
- Tools available to the prime **and** sub-clippies, in sandbox and build.
- New servers should be **config-only** (no code change).
- The existing consent gate must be able to see the bridged tools.

## Considered Options

### Option A — Pi extension bridge with a hand-rolled stdio client (chosen)

A `clippy-mcp.ts` extension reads server config from `CLIPPY_MCP_SERVERS`,
spawns each stdio server, handshakes, `tools/list`, and `registerTool`s each.
Clippy's host side (`clippy/mcp.py`) resolves names and the sandbox allowlist.

### Option B — Vendor `@modelcontextprotocol/sdk`

A package-style extension with `node_modules`. Pi only bundles core packages
(`typebox`, `@earendil-works/pi-*`); the SDK would need a managed `npm install`
(and network) at setup.

### Option C — Clippy-side (Python) MCP client + IPC to an extension

Duplicates the client and adds a socket/protocol between Clippy and the Pi
child.

### Option D — Host-mediated directive execution

The model emits a directive and Clippy runs the command. Re-implements tool
calling and loses Pi's native tool loop.

## Decision

Adopt **Option A**. The MCP client lives in the Pi extension
(`clippy/extensions/mcp-client.js`, plain ESM, newline-delimited JSON-RPC 2.0);
the host side (`clippy/mcp.py`) reads the `mcp.servers` config, resolves tool
names (config list or a cached `tools/list` query), and produces
`CLIPPY_MCP_SERVERS` + the flat name list used for `--tools` /
`CLIPPY_GATE_ALLOW`. Tools are registered under **bare names by default** (an
optional per-server `prefix` exists for collisions) so they match the
`personal-assistant-mcp` skill's documented names. `PiBrain`/`PiSubAgent` gained
`env=` (and `extensions=` for workers) to carry this to every spawn.

## Rationale

1. The extension is Pi's supported extension point; Pi remains the tool owner.
2. Hand-rolled client = no dependency, no install step, works offline.
3. `--tools` accepting custom names (spike) lets sandbox enable exactly the
   configured tools alongside the read-only built-ins.
4. Config-only onboarding of new servers.

## Consequences

### Positive

- MCP tools are available to the prime and sub-clippies in every mode.
- New servers are a `mcp.servers` entry; no code change.
- The gate still sees bridged tools (wholesale-trusted via `CLIPPY_GATE_ALLOW`).

### Negative

- Two small MCP clients exist (host `mcp.py` query + extension `mcp-client.js`).
- Each Pi spawn starts its own server child (≈1 s for `uv run`); the host query
  is cached, but `--tools` needs names at spawn.
- Trusted wholesale: MCP tools are auto-allowed, including destructive ones, in
  sandbox and build — the server is treated as the guardrail.

### Risks

- MCP protocol drift; the hand-rolled client speaks only
  initialize / initialized / tools/list / tools/call.
- A slow or broken server must never block Pi startup — the bridge logs and
  skips it.

## Implementation Notes

- `clippy/extensions/clippy-mcp.ts`, `clippy/extensions/mcp-client.js`
- `clippy/mcp.py`; `MCP_EXT` + `_brain_kwargs` / `_spawn_worker` in
  `clippy/session.py`; `env=`/`extensions=` in `clippy/brain.py`,
  `clippy/subagent.py`
- `tests/test_mcp.py`, `tests/fake_mcp_server.py`,
  `tests/test_mcp_client.mjs`, `tests/fake_mcp_server.mjs`

## References

- Commit `7c1c5a8` — MCP bridge + providers
- `docs/remediation-plan.md` — Phase 8
- Pi package docs: `docs/extensions.md` (Custom Tools, lifecycle),
  `docs/settings.md` (`defaultTools` vs `--tools`), `docs/usage.md`
- `research/pi-community-deep-dive.md`, `research/pi-drive-surface.md`
