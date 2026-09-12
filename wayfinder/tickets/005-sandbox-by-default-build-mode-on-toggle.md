---
id: 005
title: Sandbox by default, build mode on toggle
type: grilling
status: closed
assignee: pete
blocked_by: [002]
labels: [wayfinder:grilling]
---

## Implemented (ticket 017, under the RPC reality)

The grilling decision set below is now implemented by `main.py --brain` (ticket 017) with one RPC-driven change: **Pi 0.85.1 sets the tool set at spawn only** (no per-turn tool switching — verified in 015/018), so the Tab toggle **re-spawns the prime brain** rather than steering a live process. Build mode additionally carries the `clippy-gate.ts` approval extension (016): mutating tools (bash/write/edit) ask a w1c confirm card, fail-closed without UI. Sandbox = `--tools read,grep,find,ls` + scratch-dir cwd. Badge (`🛡`/`🔨`) in the pane statusbar. Hot-steering permissions into a live RPC process remains out of scope (spawn-time enforcement).

## Question

How should Clippy's sandbox-by-default / selectable-build-mode behave as a per-conversation permission system?

Grill the human on the permission-rules shape: what a sandboxed conversation can and cannot do (read-only? read + safe tools? all tools but no writes?), what exactly flipping build mode grants (file writes + command exec for that conversation?), where the toggle lives in the window, and how it threads down into the doer (Pi) so its actions respect the same boundary. Also: what happens on mode flip mid-task.

## Resolution (grilling done — parked, NOT implemented)

Decision set is locked; implementation deliberately deferred (demo-first scope; this dips into "serious software territory").

- **Sandbox boundary** = read/search-only tool allowlist (no `bash`/`write`/`edit`), scratch-dir cwd, `--no-context-files`. Pi (v0.85.1, one-shot `--mode json -p --no-session`) has no sandbox directive of its own: the boundary is enforced entirely with flags (`--tools <allowlist>`, `--no-context-files`, `-na`), and non-interactive `-p` mode means an allowlist cannot be talked past — effectively airtight for the demo.
- **Build mode grant** = full tool set, cwd stays the scratch dir (no project reach; context files still ignored unless asked).
- **Toggle** = `Tab` key on the prime shell (opencode-style; works with click-through ON — no clickable widget). Both shells show a 🛡 sandbox / 🔨 build badge in the status line.
- **Mid-task flip** = affects the *next* delegation only; each sub-Clippy's tool set is fixed at spawn. Badge always reflects the live (fix-at-spawn) mode.
- **Demo acceptance** = canonical `--delegate` task becomes read-only ("inspect this directory and summarize what's in it") so the demo proves sandbox-by-default; hello.py build demo still reachable via `--build`.
- Pi's sandbox allowlist tool-names must be enumerated from Pi at impl time (built-ins are read/bash/edit/write; confirm search/glob/grep naming in v0.85.1).

Out of scope for implementation: hot-steering permissions into a live Pi process over RPC; approval-based (human-prompt) writes.