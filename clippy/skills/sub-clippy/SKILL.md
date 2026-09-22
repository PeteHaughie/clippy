---
name: sub-clippy
description: Delegate a self-contained task to a fire-and-forget sub-clippy worker. Use when a task is research or reading legwork that would clutter the main conversation and can be fully specified in one prompt. Emits the [CLIPPY::DELEGATE] directive that Clippy's host turns into a second, sandboxed Pi instance.
---

# Sub-clippy delegation

Clippy is a projection over Pi. When a task is well-suited to a worker, Clippy
spawns a **sub-clippy**: a separate sandboxed Pi instance in its own window
that thinks out loud, does the legwork, reports back, and disappears. You stay
available to the user meanwhile.

This skill is how you request one.

> **Critical:** this file is an instruction, never output. Do NOT quote,
> paste, or summarise this skill in a reply. When you delegate, the directive
> block below must contain ONLY the user's task — never the protocol.

## When to delegate

Hand off tasks that are:

- **Research / reading legwork** — "find out X", "summarise these files",
  "enumerate the options", "check the docs for Y".
- **Fully specifiable in one prompt** — the child cannot ask follow-up
  questions, so the task must be complete on its own.
- **Long-running or verbose** — the kind of work that would clutter this
  conversation with many tool turns.

Do NOT delegate when:

- The answer is quick and you can give it now.
- The task needs your current context, your approvals, or the user's input.
- The task **writes, installs, or mutates anything** and you are in **sandbox**
  mode — a sandboxed sub-clippy is read/search-only. Never ask it to create
  files or run mutating commands in sandbox mode.

In **build** mode a worker may be granted command access, but only the user can
grant it: you request it, the host shows them an Allow / Read-only / Suggest /
Dismiss card, and the worker runs read-only unless they Allow. Use the elevated
directive below when — and only when — the task genuinely needs to run or write
something.

## How to delegate

Two ways — prefer the command for the user, the directive only for
autonomous delegation.

### 1. Tell the user to use the command (reliable)

The host intercepts `/delegate` directly, so this always works. When the user
asks for something delegate-worthy, end your reply with:

> I can hand that to a sub-clippy — just type `/delegate <task>`.

One line, no ceremony. The user types it in the pane, the host spawns the
worker, and its report comes back into this conversation for you to relay.

### 2. Autonomous directive (when you must)

Only if you cannot wait for the user and the task is fully specifiable. End
your reply with the directive block. The task must be self-contained: the
goal, the inputs (paths or subjects), and what to report. One task per block,
one block per reply.

```
[CLIPPY::DELEGATE]
<Task description. Self-contained: goal, inputs, expected report.>
[CLIPPY::END]
```

If the task needs to run commands or write files (build mode only), use the
elevated form — the host will ask the user for consent before granting it:

```
[CLIPPY::DELEGATE::ELEVATED]
<Task description. Self-contained: goal, inputs, expected report.>
[CLIPPY::END]
```

The host strips the block from what the user sees and spawns the worker.
After delegating, stay quiet and let the user know the report is coming.

## After handing off

A sub-clippy's report comes back into this conversation, and you relay it to
the user in your next reply. If it failed, say so plainly.