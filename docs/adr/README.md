# Architecture Decision Records

This directory records significant architectural decisions for Clippy.

## Index

| ADR | Title | Status | Date |
| --- | --- | --- | --- |
| [0001](0001-skills-vs-builtin-api.md) | Distinguish skills from the built-in command API | Accepted | 2026-09-17 |
| [0002](0002-mcp-bridge.md) | Bridge MCP servers into Pi via an extension | Accepted | 2026-09-22 |
| [0003](0003-worker-trust-model.md) | Worker trust model — sandbox by default, per-delegation consent | Accepted | 2026-09-22 |
| [0004](0004-screen-geometry-and-drag.md) | Screen geometry in the shell's coordinate space; cursor-poll drag | Accepted | 2026-09-22 |
| [0005](0005-pane-html-sanitization.md) | Pane HTML sanitization is an allowlist | Accepted | 2026-09-22 |
| [0006](0006-providers-and-secrets.md) | Pi owns inference providers; secrets live outside config | Accepted | 2026-09-22 |

## Creating a new ADR

1. Copy the MADR structure from an existing ADR.
2. Number sequentially (`0002-…`).
3. Fill in Status / Context / Decision Drivers / Considered Options / Decision / Rationale / Consequences / References.
4. Add a row to the index above.
5. Status lifecycle: Proposed → Accepted → Deprecated → Superseded (never edit an accepted ADR in place — write a new one to supersede).