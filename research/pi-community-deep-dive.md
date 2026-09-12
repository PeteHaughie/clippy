# Pi community deep dive — sub-agents, persistent memory, per-action approval on RPC

Research for Clippy: what the Pi ecosystem (beyond the official docs) offers for (1) reduced-context
sub-agent composition, (2) persistent cross-session memory, and (3) per-action approval/consent when
driving Pi 0.85.1 over RPC from a Python desktop host.

Investigated: 2026-09-12, primary sources first — the locally installed package
(`/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/`, v0.85.1: `docs/*.md`,
`examples/extensions/subagent/`, `examples/extensions/permission-gate.ts` etc., `dist/cli/args.js`,
`pi --help`) — then the pi GitHub repo `github.com/earendil-works/pi` on `main`, the pi.dev package
gallery, npm, the agentskills.io spec, and the GitHub/npm ecosystem. Community claims are labeled
**community** and carry their own URL; treat their numbers/features as third-party self-reports.

---

## 1. Sub-agent context composition

### The official recipe is the base primitive
Pi's own subagent example spawns a fresh `pi` process per child with an isolated context window:
`["--mode","json","-p","--no-session"]`, then `--model`, `--thinking`, `--tools <allowlist>`,
`--append-system-prompt <tempfile>` (the agent's system prompt), and the task as the message
(`examples/extensions/subagent/index.ts:300-341`, `getPiInvocation` at `:249-263`). Modes: single,
parallel (max 8 tasks, 4 concurrent), chain with `{previous}` (`examples/extensions/subagent/README.md:90-98`).
Agents are Markdown files with YAML frontmatter `name/description/tools/model`
(`examples/extensions/subagent/README.md:125-155`).

Pi ships with **no sub-agents**: README Philosophy "No sub-agents. There's many ways to do this.
Spawn pi instances via tmux, or build your own with extensions, or install a package that does it
your way." (`packages/coding-agent/README.md`; also `docs/usage.md:309` — "does not include built-in
MCP, sub-agents, permission popups, plan mode…"). So sub-agents are an app-level concern; the
official answer is exactly the spawn-a-child-per-task recipe above, and the ecosystem's job is to
package richer versions of it.

### Distribution channel for community answers
Extensions/skills/prompts are distributed as **pi packages** via `pi install npm:@scope/pkg` /
`git:...` / local paths (`docs/packages.md:18-114`; package manifest `package.json` `pi` key +
`pi-package` keyword, `docs/packages.md:116-131`). The package gallery is `https://pi.dev/packages`.

### Community packages (community, verified on GitHub/npm/pi.dev as of 2026-09-12)
All are thin-to-rich wrappers of the same "fresh child process" primitive — none add an in-process
"reduced context" mechanism beyond `--model`/`--tools`/`--append-system-prompt` per child:

- **`pi-subagents`** (nicobailon) — the flagship; ~3.2–3.4k stars, MIT, 1,225 commits. "async subagent
  delegation with truncation, artifacts, and session sharing". Ships scout/planner/worker/reviewer +
  more, single/parallel/chain, saved workflows, background jobs.
  https://github.com/nicobailon/pi-subagents ; install `npm:pi-subagents`.
- **`@ifi/pi-extension-subagents`** — full-featured orchestration "built on top of nicobailon/pi-subagents":
  parallel-in-chain fan-out/fan-in (`{ parallel: [...] }` steps), reusable `.chain.md` files, run
  history (per-agent JSONL), async/background chains. https://pi.dev/packages/@ifi/pi-extension-subagents ; npm.
- **`@e9n/pi-subagent`** — single/parallel/chain plus **orchestrator** (hierarchical agent trees) and
  **pool** (long-lived agents with persistent context, follow-up sends). Children run `--no-extensions`
  by default with a whitelist; emits `subagent:start/complete` events. https://www.npmjs.com/package/@e9n/pi-subagent.
- **`pi-minimal-subagents`** (max_mill03) — small, opinionated scout/reviewer/worker; deliberately no
  parallel/chain DSL — it relies on pi's native concurrent sibling tool calls for fan-out, and each
  child is a fresh ephemeral `pi` process. https://pi.dev/packages/pi-minimal-subagents.
- **`pi-sub-agent`** (mazli) — single/parallel/chain, 9 bundled agents; sends child prompts over stdin
  (not argv), truncates child output to 2,000 lines/50KB, **blocks recursive subagent fan-out**.
  https://pi.dev/packages/pi-sub-agent.
- **`pi-agent-extensions`** — bundle of 17 extensions incl. multi-agent `workflow`, `loop`, and `control`
  (inter-session control). https://pi.dev/packages/pi-agent-extensions.

No dedicated "pi-ecosystem"/"pi-extensions" org was found; the org is `earendil-works`
(https://github.com/earendil-works — pi, pi-transcribe, website, inkling).

### Context-scoping primitives (per child, CLI level)
Available for scoping a sub-task's context window: `--tools` allowlist, `--exclude-tools`, `--no-tools`,
`--no-builtin-tools`, `--no-extensions`, `--no-skills`, `--no-context-files`, `--no-session`,
`--session-dir`, `--model`, `--thinking`, `-a/--approve`/`-na` (project trust) — `pi --help`,
`docs/usage.md:211-243`. For non-Node hosts, the same spawn-recipe is directly reproducible with
Python `subprocess.Popen` (`docs/rpc.md:1526-1560` Python example; see also
`research/pi-drive-surface.md` §5).

### Recommendations
- The official recipe **is** the ecosystem answer at the primitive level; there is no alternative
  in-process context-scoping API (a child always starts fresh — either a new `pi` process, or a new
  `AgentSession` via the Node SDK, as OpenClaw does in `src/agents/pi-embedded-runner/`).
- For Clippy, do not adopt a heavy community orchestration package; copy the official recipe
  (`--mode json -p --no-session` + per-child `--model`/`--tools`/`--append-system-prompt`) directly in
  Python. Borrow two ideas from the community where cheap: prompt-over-stdin instead of argv
  (`pi-sub-agent`) and pre-empting recursive fan-out by stripping the subagent tool from the child's
  `--tools` allowlist (`pi-sub-agent`; official example already per-agent tool lists).
- If a human-visible fleet is ever a product goal, that is the README's tmux path, not RPC.

---

## 2. Persistent memory

### What Pi sessions give today (cross-session, but not cross-project knowledge)
Sessions auto-save per working directory as JSONL trees at
`~/.pi/agent/sessions/--<path>--/<timestamp>_<uuid>.jsonl` (`docs/session-format.md:5-11`; `docs/sessions.md:5-16`).
Entries are a tree (`id`/`parentId`); `/tree`, `/fork`, `/clone`, labels, compaction, branch summaries
(`docs/sessions.md:69-140`; `docs/session-format.md`). Resume via `pi -c`/`-r`/`--session`/`--fork`
(`docs/sessions.md:9-16`), and over RPC via `new_session`, `switch_session`, `fork`, `clone`,
`get_entries` (durable `since` cursor), `get_tree` (`docs/rpc.md:160-746`). Extension state survives
restarts via `pi.appendEntry()`/custom entries, but custom entries **do not** participate in LLM
context (`docs/session-format.md:263-271`; `docs/extensions.md:1471-1487`). Net: sessions give
*continuity of a conversation*, not an ambient knowledge base that is present in every session.

### Pi primitives that load content into every session (primary sources)
- **Context files** — `~/.pi/agent/AGENTS.md` (global instructions), project `AGENTS.md`/`CLAUDE.md`,
  `AGENTS.override.md` — loaded at startup regardless of project trust (`docs/usage.md:100-107`;
  `docs/quickstart.md:88-103`; `docs/security.md:27`).
- **System prompt files** — `~/.pi/agent/SYSTEM.md` (replaces default) and `~/.pi/agent/APPEND_SYSTEM.md`
  (appends) (`docs/usage.md:115-118`); CLI `--system-prompt` / `--append-system-prompt`
  (`docs/usage.md:243`; `pi --help`).
- **Skills are NOT guaranteed loaded** — progressive disclosure: only the description is always in the
  system prompt; the model must `read` the full `SKILL.md` on demand, and "models don't always do this;
  use prompting or `/skill:name` to force it" (`docs/skills.md:65-72`). Pi implements the
  [Agent Skills standard](https://agentskills.io/specification); skill dirs `~/.pi/agent/skills/`,
  `~/.agents/skills/`, project `.pi/skills`/`.agents/skills`, settings `skills` array, `--skill`
  (`docs/skills.md:24-42`).

### agentskills.io: no memory idiom in the spec
The Agent Skills spec defines only `name/description/license/compatibility/metadata` (plus
`allowed-tools`, `disable-model-invocation` as pi extensions) and has no persistent-memory convention
(`docs/skills.md:140-150`; https://agentskills.io/specification). Memory is application-level. A
memory **skill** is a community pattern, not a spec feature — e.g. `agent-memory` skills in
agent-skill collections (**community**: https://github.com/suucha/agent-skills/skills/agent-memory,
https://github.com/ropl-btc/agent-skills/persistent-memory). The Claude Code "memory bank" idiom —
a `MEMORY.md` index loaded into every session + topic files on demand, under `~/.claude/projects/<p>/memory/`
and `CLAUDE.md` — is Claude/Codex-specific, not agentskills.io (**community**:
https://code.claude.com/docs/en/memory.md, https://github.com/CodyLiska/claude-obsidian-memory).
Pi's relevance: it *does* auto-load `CLAUDE.md` as a context file, so the index-in-context +
topics-on-demand pattern ports cleanly.

### Community memory extensions for pi (community, verified on pi.dev/npm/GitHub)
- **`pi-memory`** (jayzeng) — "most popular memory extension for pi"; qmd semantic search over plain
  markdown in `~/.pi/agent/memory`; injects top-N memory into the system prompt before each turn
  (`before_agent_start`/`context`-style snapshot), daily append-only logs, handoff note on compaction,
  `memory_write`/`memory_forget`/`memory_status` tools. https://pi.dev/packages/pi-memory ; `npm:pi-memory`.
- **`pi-agent-memory`** — adaptation of claude-mem (55k+ stars); cross-engine shared memory
  (Claude/Codex/Cursor/OpenClaw/pi), hybrid FTS5+Chroma search, worker at `localhost:37777`, injects
  observations each turn + `memory_recall` tool. https://pi.dev/packages/pi-agent-memory ;
  https://github.com/HaqimIskandar/pi-agent-memory.
- **`pi-memory-extension`** — human-curated markdown, global `~/.pi/memory/` + workspace `.pi/memory/`
  dual layer, `/memory:*` commands (init/status/checkpoint/promote). https://pi.dev/packages/pi-memory-extension.
- **`pi-persistent-intelligence`** — governed memory (JSONL canonical + markdown projection), session
  search, reviewable curation. https://pi.dev/packages/pi-persistent-intelligence.
- **`josephkern/pi-memory`** — persistent file-based memory extension (**community**:
  https://github.com/josephkern/pi-memory).

All of these implement "memory = markdown files + injection into context at session/turn start", which
is exactly the shape Clippy wants.

### Recommendations for `~/.clippy/memory/*.md` in every session
- **Guaranteed presence: inject deterministically, don't rely on a skill.** Pass
  `--append-system-prompt ~/.clippy/memory/INDEX.md` (a small index: one line per note + file list) on
  every spawned `pi --mode rpc`/`--mode json` process, or maintain `~/.pi/agent/APPEND_SYSTEM.md`
  pointing at it. Skills are on-demand by design (`docs/skills.md:65-72`), so a skill alone will not
  put memory in every session.
- **Skill for read/write discipline:** ship a `clippy-memory` skill (SKILL.md in the Clippy skill
  bundle or `~/.pi/agent/skills/`) that tells the model where notes live (`~/.clippy/memory/`), when to
  write (decisions, preferences, corrections), and to read specific topic files on demand. Pair it with
  the injected INDEX so the model always knows the store exists.
- **Token control (optional):** a ~20-line extension on `before_agent_start` that reads the INDEX and
  appends it to `event.systemPrompt` only when non-empty (`docs/extensions.md:534-560`) — this is what
  `pi-memory`/`pi-agent-memory` do and stays RPC-compatible.
- **Avoid:** vector/DB-backed memory for a desktop assistant's small note set; and never treat a skill
  as "loaded every session".

---

## 3. Per-action approval on RPC

### Verified: no per-turn tool switching on RPC
The full RPC command list is `prompt, steer, follow_up, abort, clear_queue, new_session, get_state,
get_messages, set_model, cycle_model, get_available_models, set_thinking_level,
cycle_thinking_level, get_available_thinking_levels, set_steering_mode, set_follow_up_mode, compact,
set_auto_compaction, set_auto_retry, abort_retry, bash, abort_bash, get_session_stats, export_html,
switch_session, fork, clone, get_fork_messages, get_entries, get_tree, get_last_assistant_text,
set_session_name, get_commands` (`docs/rpc.md` "Commands"). `prompt`/`steer`/`follow_up` carry only
`message`, `images`, `streamingBehavior` — **no `tools` field** (`docs/rpc.md:43-122`); there is **no
`set_tools` command**. Tool-set changes mid-session are possible only *inside* the process: extensions
call `pi.setActiveTools()` (incl. dynamically registered tools) (`docs/extensions.md:1371,1677-1695`),
triggered from a slash command the host can send via `prompt "/cmd"` (`docs/rpc.md:818-853`).

### (a) Can an extension gate mutating built-in tools? Yes — and it needs no custom tool
`tool_call` fires for **every** tool invocation (built-in or extension) before execution and "Can
block" via `{ block: true, reason, terminate }` (`docs/extensions.md:778-818`; lifecycle diagram
"tool_call (can block)" at `:277-314`). `event.input` is mutable (argument patching) before execution.
The official `permission-gate.ts` example gates **bash** (a built-in) with `ctx.ui.select(...)` then
`{ block: true }` (`examples/extensions/permission-gate.ts:13-33`); `protected-paths.ts` blocks
built-in `write`/`edit` on protected paths (`examples/extensions/protected-paths.ts:13-29`).
Extensions load in RPC mode from `~/.pi/agent/extensions/*.ts` (always) or `-e` (`docs/extensions.md:109-135`).
So gating mutating built-ins is exactly the documented mechanism — no `registerTool` required for a gate.

### (b) Documented and community approval extensions
Official/documented pattern: `tool_call` handler + `ctx.ui.confirm/select`, with examples
`permission-gate.ts`, `protected-paths.ts`, `confirm-destructive.ts` (session switch/fork gates),
`project-trust.ts`; extensions.md's example use case list literally opens with "Permission gates
(confirm before `rm -rf`, `sudo`, etc.)" (`docs/extensions.md:18-28`).

Community (**community**, verified on GitHub/npm/pi.dev):
- **`pi-permission-system`** (MasuRii) — "centralized, deterministic permission gates for tool, bash,
  MCP, skill" with `allow/deny/ask`, wildcard bash patterns, Allow Once/Always/Reject; designed so
  OpenCode-style agent permission policies port to pi. https://github.com/MasuRii/pi-permission-system ; `npm:pi-permission-system`.
- **`pi-perm`** (DCRcoder) — intercepts tool calls, applies allow/confirm/block/audit policies, can
  wrap bash commands with the Anthropic Sandbox Runtime. https://github.com/DCRcoder/pi-perm.
- **`@agentapprove/pi`** — approve/deny Pi tool calls from an iPhone/Apple Watch via `tool_call`
  blocking approval. https://pi.dev/packages/@agentapprove/pi.

### (c) Is there a built-in `ask_question` tool? No.
The 0.85.1 built-in tool list is `read, bash, powershell, edit, write, grep, find, ls`
(`docs/usage.md:217`; `pi --help` "Built-in Tool Names"). `--exclude-tools ask_question` appears only
as a help *example* ("Disable one tool while keeping the rest available") in `dist/cli/args.js:372` and
`docs/usage.md:302`, and `excludeTools: ["ask_question"]` repeats it in `docs/sdk.md:550` — a vestigial
example, not a registered tool (grep of the installed bundle finds it only inside those help strings).
The ecosystem supplies question tools as **extensions** — `@pify/ask-question`, `pi-questions`,
`ghoseb/pi-askuserquestion`, `@josephyoung/pi-ask-user-question`, `avtc-pi-ask-user-question`
(**community**: https://pi.dev/packages/@pify/ask-question, https://pi.dev/packages/pi-questions,
https://github.com/ghoseb/pi-askuserquestion) — all built on `ctx.ui.select/input` so they "work in TUI and RPC".

### What is possible at the RPC host level for per-action consent
The consent loop is fully host-driven via the **Extension UI sub-protocol**:
1. An extension's `tool_call` handler calls `ctx.ui.confirm()`/`ctx.ui.select()` (`docs/extensions.md:778-818,2516-2533`).
2. In RPC mode this blocks the tool and emits `{"type":"extension_ui_request","id":...,"method":"confirm"|"select",...}`
   on stdout (`docs/rpc.md:1184-1275`); `timeout` fields auto-resolve if the host is silent.
3. The Python host replies `{"type":"extension_ui_response","id":...,"confirmed":true/false}` (or
   `value`/`cancelled:true`) on stdin; the extension returns `{ block: true, reason }` or lets the call
   proceed (`docs/rpc.md:1352-1374`).
4. `ui_prompt_start`/`ui_prompt_end` notification events let the host show "waiting for user"
   (`docs/extensions.md:583-599`).

In RPC mode `ctx.mode === "rpc"` and `ctx.hasUI === true` (dialogs work); in `-p`/`--mode json`,
`hasUI === false` and the official gate **blocks by default** (fail-closed) (`docs/extensions.md:970-974`;
`examples/extensions/permission-gate.ts:20-23`). `ctx.ui.custom()` returns `undefined` in RPC
(`docs/rpc.md:1195-1205`), so gates must use `confirm`/`select`/`input`/`editor`, not custom components.

**What is not possible at RPC host level:** no per-turn `tools` field on `prompt`/`steer`/`follow_up`;
no `set_tools` command; the host cannot register a tool after spawn (tools come from extensions loaded
at process start, or `pi.setActiveTools()` called by an extension); the host cannot directly invoke a
tool except `bash` (`docs/rpc.md:477-537`). Consent is therefore "extension intercepts each tool call,
host answers the dialog" — not "host rewrites the tool set per turn".

### Recommendations
- Ship a Clippy-owned permission-gate extension (`pi.on("tool_call")` → `ctx.ui.confirm/select`) loaded
  via `-e` or `~/.pi/agent/extensions/` on every RPC spawn. Keep the policy in Clippy (host side), so
  consent UX lives in the desktop app; the extension only needs to (a) match a rule, (b) ask via
  `ctx.ui.confirm`, (c) `{ block: true, reason }` on refusal. Fail closed when `!ctx.hasUI`.
- If a configurable policy file is wanted, `pi-permission-system` is the closest off-the-shelf match
  (allow/deny/ask, bash wildcards) — otherwise the ~30-line official `permission-gate.ts` pattern is enough.
- For the "model proactively asks the user" case, install one of the ask-question extensions
  (`@pify/ask-question` works in RPC) rather than assuming an `ask_question` built-in exists.

---

## Open questions / risks

- **Version skew:** pi moves fast (0.85.1; earlier research recorded 0.85.1 with ~1.98M weekly
  downloads). Community packages (pi-subagents family, pi-memory, pi-permission-system) pin against
  specific pi/Node versions — verify against the bundled pi version before adopting.
- **`tool_call` under parallel tool mode:** siblings are preflighted sequentially but executed
  concurrently; block/terminate semantics across a batch need a test before Clippy trusts them
  (`docs/extensions.md:784-793`).
- **Skills are not guaranteed in every session** (`docs/skills.md:65-72`) — any "memory via skill"
  design must be paired with a deterministic injection (append-system-prompt / AGENTS.md / extension).
- **Fail-closed in headless modes:** `ctx.hasUI === false` in `-p`/json child processes — gates must
  block by default there (official pattern), and Clippy should decide whether sub-tasks inherit the
  gate or run with an explicit `--no-extensions`/tool-scoped policy.
- **`ask_question` example is vestigial:** the help/usage/sdk examples reference an `ask_question`
  tool that is not a 0.85.1 built-in — do not design around it; expect ecosystem extensions to supply it.
- **Community self-reported numbers** (stars, downloads, "most popular") are as displayed on
  GitHub/npm/pi.dev at investigation time; verify on the live pages before citing in product docs.
- **pi.dev package gallery content** was read via search-result pages (pi.dev/packages/<name>); feature
  claims are the packages' own READMEs, not Earendil-verified.