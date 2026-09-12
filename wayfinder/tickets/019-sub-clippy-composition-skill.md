---
id: 019
title: Sub-clippy composition skill
type: prototype
status: closed
assignee: pete
blocked_by: [017]
labels: [wayfinder:prototype]
---

## Question

How does Clippy hand a self-contained task to a pared-down sub-clippy worker — context composed through a Clippy-owned skill (map "Not yet specified / next" #1)?

## Resolution

- **`clippy/skills/sub-clippy/SKILL.md`** (always-on, with `memory`) — teaches the prime when to delegate (research/reading legwork, fully specifiable in one prompt) and when not to (writes/mutations — a sub-clippy is sandboxed read/search-only; tasks needing context/approvals; quick answers). Two paths:
  - **`/delegate <task>` chat command** (reliable): the host intercepts it in the pane, no model compliance needed. The skill tells the prime to offer it ("I can hand that to a sub-clippy — just type `/delegate <task>`").
  - **Autonomous `[CLIPPY::DELEGATE] … [CLIPPY::END]` directive**: only when the prime must act unaided. Anti-echo guard added after a live test showed gemma-12B regurgitating the skill file instead of tasking a worker.
- **`clippy/subagent.py`** — `parse_delegation(text) -> (clean, task)` (strips a directive block from a reply), `DELEGATE_CMD`, `SUB_SANDBOX_TOOLS`, `PiSubAgent.tools` param + `_cmd()` builder (mirrors `PiBrain`).
- **`clippy/controller.py`** — `SubClippyController` captures the child's final `answer` and fires `on_complete(failed, report)`; fixed a latent event-routing bug (`kind` preferred `type` over `eventType`, so top-level `assistant_message_event` deltas never rendered).
- **`clippy/memory.py`** — `ALWAYS_ON_SKILLS = ("memory", "sub-clippy")`; an empty `skills.allow` still ships both Clippy-owned protocols.
- **`main.py`** — `PrimeSession` intercepts `/delegate` → `Delegator.delegate(task, tools=SANDBOX_TOOLS, on_complete=…)`; the `on_answer` hook scans for the autonomous directive and delegates on it; the child's report is relayed into the pane and steered back into the prime conversation. `Delegator` frees its slot on completion so later delegations can spawn fresh workers.

## Findings that mattered

- The mechanism is solid: a live end-to-end run had the real prime emit a directive → host parsed it → spawned a real sandboxed `--mode json` child → it settled and exited 0.
- gemma-12B (omlx) does **not reliably invoke the skill** on natural prompts: it either echoed the skill file (when prompted "use your skill") or echoed the user's prompt (when asked naturally). Hence `/delegate` — the deterministic demo path — while the directive stays for the autonomous case.

## Acceptance

Typing `/delegate <task>` in the pane spawns a sandboxed sub-clippy that thinks in its own bubble and explodes on completion; its report returns to the pane and the prime relays it. (Interactive step — live-run item; headless controller success/failure paths and the real spawn loop verified.)