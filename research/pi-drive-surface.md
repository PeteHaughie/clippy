# Pi drive surface — research findings

Research for the "Pi drive surface" wayfinder ticket: how Clippy (a Python desktop app)
can drive Pi (the Earendil coding agent, npm package `@earendil-works/pi-coding-agent`)
programmatically from Python, and how sub-task Pi instances are spawned.

Investigated: 2026-09-11, against primary sources only (pi.dev docs, the pi GitHub
repo `github.com/earendil-works/pi` on `main`, the npm page, and the OpenClaw repo/docs).
The local machine state (question 6) was checked directly on this Mac (branch `research/pi-drive-surface`).

---

## 1. Pi's four invocation modes and which fits a Python wrapper

Primary source: `packages/coding-agent/README.md` and `packages/coding-agent/docs/*`.

"Pi runs in four modes: interactive, print or JSON, RPC for process integration, and an
SDK for embedding in your own apps."
— `packages/coding-agent/README.md`, "Programmatic usage" intro
(https://github.com/earendil-works/pi/blob/main/packages/coding-agent/README.md)

CLI mode flags (README "Modes" table):

| Flag | Description |
| --- | --- |
| (default) | Interactive mode |
| `-p`, `--print` | Print response and exit |
| `--mode json` | Output all events as JSON lines (docs/json.md) |
| `--mode rpc` | RPC mode for process integration (docs/rpc.md) |

- **Interactive** — TUI, requires a terminal; not suitable for headless Python driving.
- **Print/JSON** — one-shot, non-interactive. `pi -p "prompt"` prints the final response
  and exits. `pi --mode json "prompt"` prints *all session events* as JSON lines to
  stdout (docs/json.md). In print mode pi also reads piped stdin and merges it into the
  initial prompt: `cat README.md | pi -p "Summarize this text"` (README "Modes").
- **RPC** — designed specifically "This is useful for embedding the agent in other
  applications, IDEs, or custom UIs" (docs/rpc.md, intro) and is the documented path for
  non-Node hosts: the RPC doc includes a ready-to-use **Python client example**
  (docs/rpc.md, "Example: Basic Client (Python)", built on `subprocess.Popen`).
- **SDK** — Node.js/TypeScript-only, in-process embedding (`AgentSession`). See Q4.

**Fit for Clippy:** For a Python process that spawns/wraps Pi, **RPC mode is the native
answer** — it exists ("RPC for process integration") and ships a Python example in its
protocol doc. **`--mode json`** is the right fit for short-lived one-shot sub-tasks
(matches Pi's own subagent example, see Q5). The SDK cannot be called from Python
(Node-only). Interactive mode is explicitly for the terminal.

### JSON mode exact CLIs

- `pi --mode json "Your prompt"` — "Outputs all session events as JSON lines to stdout."
  (https://pi.dev/docs/latest/jsonmd — "JSON Event Stream Mode"; repo file
  `packages/coding-agent/docs/json.md`)
- `pi -p "..."` / `pi --print "..."` — "Print response and exit" (README CLI Reference,
  "Modes").
- Example in the doc: `pi --mode json "List files" 2>/dev/null | jq -c 'select(.type == "message_end")'`
  (docs/json.md, "Example").
- Session/one-shot flags relevant to wrapping: `--no-session` (ephemeral, don't save),
  `--name`, `--session-dir`, `--model`, `--provider`, `--thinking`, `--tools`,
  `--no-tools`, `-e/--extension`, `-a/--approve -na/--no-approve` (project trust),
  `--no-context-files` (READMEmd "Session Options", "Tool Options", "Resource Options",
  "Other Options", "Modes"). Non-interactive modes never show the trust prompt
  (README "Project Trust").

### JSON event stream shape (what `--mode json` emits)

Each line of stdout is one JSON object. First line is the session header; then events
as they occur (docs/json.md, "Output Format"):

```json
{"type":"session","version":3,"id":"uuid","timestamp":"...","cwd":"/path"}
{"type":"agent_start"}
{"type":"turn_start"}
{"type":"message_start","message":{...}}
{"type":"message_update","usage":{...},"assistantMessageEvent":{"type":"text_delta","contentIndex":0,"delta":"Hello"}}
{"type":"message_end","message":{...}}
{"type":"turn_end","message":{...},"toolResults":[]}
{"type":"agent_end","messages":[...]}
```

Wire event type is `JsonAgentSessionEvent` (defined in
`packages/coding-agent/src/modes/json-event.ts`); it equals `AgentSessionEvent` except
streaming message updates drop cumulative snapshots:
- `message_update` records are **delta-only** — they omit the cumulative `message` field
  and `assistantMessageEvent.partial` to keep stream size linear; clients reassemble live
  text / thinking / tool-call args from `contentIndex` + `delta`; `message_update`'s
  top-level `usage` is the latest cumulative provider-reported usage and can stay zero
  until completion. `toolcall_start` additionally carries constant-sized `id` and
  `toolName`.
- `message_end` contains the final authoritative message (docs/json.md, "Output Format").

---

## 2. Can the event stream expose live "current thinking and actions"?

**Yes — in both `--mode json` and RPC/SDK**, via `message_update` deltas plus
`tool_execution_*` events.

Source: `packages/coding-agent/docs/rpc.md`, "Events" and "message_update (Streaming)".

Event types that exist (RPC doc "Event Types" table, and the JSON-mode equivalent):

- **Thinking/planning** : yes, as streamed blocks. `message_update` carries
  `assistantMessageEvent.type` of one of: `text_start`, `text_delta`, `text_end`,
  **`thinking_start`, `thinking_delta`, `thinking_end`**, `toolcall_start`,
  `toolcall_delta`, `toolcall_end` (rpc.md "message_update (Streaming)" table). Example:

  ```json
  {"type":"message_update","usage":{...},"assistantMessageEvent":{"type":"thinking_delta","contentIndex":0,"delta":"..."}}
  ```

  The SDK doc confirms the same: `case "message_update": if (event.assistantMessageEvent.type === "thinking_delta") { // Thinking output (if thinking enabled) }`
  (docs/sdk.md, "Events"). Thinking is only present when the model/level supports it;
  thinking is enabled/tuned via `--thinking <level>` on the CLI, `/thinking`, or RPC
  `set_thinking_level` (README "Model Options"; rpc.md "Thinking").

- **Tool-use as it happens**: two complementary channels.
  1. Streaming assistant-side tool calls: `toolcall_start` (includes call `id` and
     `toolName`), `toolcall_delta` (argument chunks — buffer these), `toolcall_end`
     (full completed `toolCall`), all under `assistantMessageEvent` (rpc.md
     "message_update (Streaming)").
  2. Execution-side events: `tool_execution_start` / `tool_execution_update` /
     `tool_execution_end`, keyed by `toolCallId`, carrying `args` and — during
     execution — `partialResult.content` with the *accumulated* output so far, so
     clients "simply replace their display on each update" (e.g. live bash output):

  ```json
  {"type":"tool_execution_start","toolCallId":"call_abc123","toolName":"bash","args":{"command":"ls -la"}}
  {"type":"tool_execution_end","toolCallId":"call_abc123","toolName":"bash","result":{...},"isError":false}
  ```

- **Lifecycle/turn-level** (also useful for a live activity view): `agent_start`,
  `agent_end`, `agent_settled`, `turn_start`, `turn_end`, `message_start`,
  `message_end`, `queue_update`, `compaction_start/end`, `auto_retry_start/end`,
  `summarization_retry_*`, `extension_error` (full table in rpc.md "Event Types").

So yes: a client can render live thinking deltas and every tool call + its streaming
output in near-real-time from the event stream.

---

## 3. RPC mode: JSON protocol over stdin/stdout from a non-Node host

Primary source: `packages/coding-agent/docs/rpc.md`
(https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/rpc.md).

- **Start**: `pi --mode rpc [options]`. Common options: `--provider`, `--model`,
  `--name/-n`, `--no-session`, `--session-dir` (rpc.md "Starting RPC Mode").
- **Framing**: "RPC mode uses strict JSONL semantics with LF (`\n`) as the only record
  delimiter." Split records on `\n` only, accept optional `\r\n` by stripping a trailing
  `\r`. "Do not use generic line readers that treat Unicode separators as newlines" —
  specifically Node `readline` is non-compliant because it also splits on `U+2028`/`U+2029`,
  which are valid inside JSON strings (rpc.md "Framing"). A Python reader should therefore
  split on `\n` itself (as the Python example does).
- **Model**: Commands (JSON objects) → stdin, one per line. Agent events → stdout as JSON
  lines. Responses are `{"type":"response","command":...,"success":true/false,"data":...}`
  with optional `error` on failure. Commands may carry an optional `id` echoed back in the
  response for correlation; `bash_execution_update` events carry the `id` of their
  originating `bash` command (rpc.md "Protocol Overview", "Error Handling").
- **Command surface** (rpc.md "Commands"): `prompt` (with `images`, and `streamingBehavior:
  "steer" | "followUp"`), `steer`, `follow_up`, `abort`, `clear_queue`, `new_session`,
  `get_state`, `get_messages`, `set_model`, `cycle_model`, `get_available_models`,
  `set_thinking_level`, `cycle_thinking_level`, `get_available_thinking_levels`,
  `set_steering_mode`, `set_follow_up_mode`, `compact`, `set_auto_compaction`,
  `set_auto_retry`, `abort_retry`, `bash` (direct shell exec whose output joins context on
  the next prompt), `abort_bash`, `get_session_stats`, `export_html`, `switch_session`,
  `fork`, `clone`, `get_fork_messages`, `get_entries`, `get_tree`,
  `get_last_assistant_text`, `set_session_name`, `get_commands`.
- **State visibility**: `get_state` returns `model`, `thinkingLevel`, `isStreaming`,
  `isCompacting`, `steeringMode`, `followUpMode`, `sessionFile`, `sessionId`,
  `messageCount`, `pendingMessageCount`, etc. — useful for a host to poll liveness
  (rpc.md "get_state").
- **Extension UI sub-protocol**: extensions that call `ctx.ui.select/confirm/input/editor`
  emit `extension_ui_request` on stdout and block until the host replies with
  `extension_ui_response` on stdin (matching `id`); `notify`, `setStatus`, `setWidget`,
  `setTitle`, `set_editor_text` are fire-and-forget. `ctx.mode === "rpc"`,
  `ctx.hasUI === true` in RPC mode. So permission/confirmation flows can be driven from
  the Python host (rpc.md "Extension UI Protocol").
- **Official Python example** exists inside the protocol doc (rpc.md "Example: Basic
  Client (Python)"): `subprocess.Popen(["pi","--mode","rpc","--no-session"], stdin=PIPE,
  stdout=PIPE, text=True)`, a `send(cmd)` that writes `json.dumps(cmd)+"\n"` and flushes,
  and a `read_events()` that yields `json.loads(line)` for each stdout line. This is the
  exact pattern Clippy would replicate.

---

## 4. SDK mode (embed Pi programmatically) — and OpenClaw as the real integration

Primary sources: `packages/coding-agent/docs/sdk.md`, README, and the OpenClaw repo/docs.

- SDK lives **in the same npm package**: "The SDK is included in the main package. No
  separate installation needed." (docs/sdk.md "Installation"). Usage is
  `import { createAgentSession, ModelRuntime, SessionManager } from "@earendil-works/pi-coding-agent"`,
  then `const {session} = await createAgentSession(...)`, `session.subscribe(events)`,
  `await session.prompt(text)` (README "SDK"; sdk.md "Quick Start").
- It is a **Node/TypeScript in-process** API (`AgentSession`, event subscription,
  `AgentSessionRuntime` for session replacement). The pi README explicitly steers
  Node users to the SDK and everyone else to RPC: rpc.md "Note for Node.js/TypeScript
  users: … consider using `AgentSession` directly … For a subprocess-based TypeScript
  client, see rpc-client.ts". sdk.md "RPC Mode Alternative" gives the tradeoff: "RPC mode
  is preferred when: You're integrating from another language / You want process
  isolation / You're building a language-agnostic client."
- pi README points to OpenClaw as the canonical real-world SDK integration
  ("See openclaw/openclaw for a real-world SDK integration" — README, `src/core`,
  "Programmatic usage" section header context).

**OpenClaw (github.com/OpenClaw/OpenClaw)** — validated on its GitHub repo and official
docs (Pi Integration Architecture page, e.g. mirror
https://docs.openclaw.ac.cn/pi; source under `src/agents/pi-embedded-runner/`):

- OpenClaw embeds Pi as a library — it does **not** spawn the `pi` CLI and does **not**
  use RPC/serial mode. It imports the SDK packages
  (`@earendil-works/pi-agent-core`, `@earendil-works/pi-ai`,
  `@earendil-works/pi-coding-agent`, `@earendil-works/pi-tui`) and instantiates
  `AgentSession` directly (docs "Pi Integration Architecture", "Overview" /
  "Package dependencies"; confirmed in repo source, e.g.
  `src/agents/pi-embedded-runner/compact.ts` importing `createAgentSession, SessionManager`
  — github.com/OpenClaw/OpenClaw blob `b79effe`).
- Flow: entry point `runEmbeddedPiAgent()` → `runEmbeddedAttempt()` → builds a
  `DefaultResourceLoader` (cwd, agentDir, settingsManager, additionalExtensionPaths),
  `await resourceLoader.reload()`, then
  `createAgentSession({cwd, agentDir, authStorage, modelRegistry, model, thinkingLevel, tools, customTools, sessionManager, settingsManager, resourceLoader})`,
  applies a system-prompt override, subscribes to session events
  (`message_start/_update/_end`, `tool_execution_*`, `turn_*`, `agent_*`,
  compaction/retry), and drives with `session.prompt(effectivePrompt, {images})`.
  It replaces default tools entirely via `customTools` (`splitSdkTools()` returns
  `{builtInTools: [], customTools}`), injects its own auth/credential profiles
  (`AuthStorage`/`ModelRegistry` wrappers), its own session persistence
  (`SessionManager.open(...)`), custom pi extensions (compaction safeguards, context
  pruning), and streams channel replies via callbacks (docs "Pi Integration
  Architecture"; source files enumerated in its "File structure").
- **Relevance to Clippy**: this is the strongest evidence of what full programmatic
  embedding buys you (custom tools, custom system prompts, arbitrary auth, custom
  persistence) — but it is fundamentally a Node/TS model. A Python desktop app cannot
  take this path directly; it must either (a) run Pi by subprocess (RPC / json mode,
  Q1/Q3/Q5), or (b) run a thin Node bridge process that uses the SDK (a local
  "pi-gateway" in the app bundle). Option (b) is what OpenClaw does architecturally,
  minus the subprocess boundary.

---

## 5. Sub-task / sub-agent spawning — "one Pi instance per sub-clippy"

Primary source: `packages/coding-agent/README.md` ("Philosophy: No sub-agents"),
`examples/extensions/subagent/` (README + `index.ts`).

### Pi ships without sub-agents
"Pi ships with powerful defaults but skips features like sub agents and plan mode"
(README intro) and under Philosophy: "**No sub-agents.** There's many ways to do this.
Spawn pi instances via tmux, or build your own with extensions, or install a package that
does it your way." So sub-agents are an app-level concern, and the app chooses the
mechanism.

### The official subagent example extension — the pattern to copy
`packages/coding-agent/examples/extensions/subagent/` is Pi's own answer. Its README:
"Each subagent runs in a separate `pi` process." Workflow prompts run chains
(scout → planner → worker). Modes: single, parallel (max 8 tasks, 4 concurrent), chain.
Agents are Markdown files with YAML frontmatter (`name`, `description`, `tools`,
`model`); the system prompt in the file is loaded and pushed as the child's appended
prompt; each child runs with an isolated context window.

From `examples/extensions/subagent/index.ts` (verified source, ~line 2804):

```ts
const args: string[] = ["--mode", "json", "-p", "--no-session"];
if (model) args.push("--model", model);
if (inheritsDispatchConfig && dispatchDefaults.thinkingLevel) {
  args.push("--thinking", dispatchDefaults.thinkingLevel);
}
if (agent.tools && agent.tools.length > 0) args.push("--tools", agent.tools.join(","));
args.push("--append-system-prompt", tmpPromptPath);   // agent system prompt from a temp .md file
args.push(`Task: ${task}`);                          // the prompt message itself
```

- `getPiInvocation()` resolves how to re-invoke Pi: if running from a real script, it
  spawns the current runtime (`process.execPath`, script, …args); otherwise plain `pi`
  (source `getPiInvocation`, ~line 2716). For sub-agents it spawns with `shell:false`,
  `stdio:["ignore","pipe","pipe"]`, `cwd: cwd ?? defaultCwd`, and parses stdout as JSONL
  (buffer split on `\n`).
- Sub-agent completion is tracked from JSON events: `message_end` (assistant messages;
  aggregates `usage`, `stopReason`, model) and `tool_result_end`, then the `close`
  handler resolves with the **process exit code**. Failure is defined as
  `exitCode !== 0 || stopReason === "error" || stopReason === "aborted"`
  (`isFailedResult`, source ~line 2600). Markdown output, tool-call rendering, usage,
  and abort (SIGINT propagation to child pids) are app-side.

This makes `pi --mode json -p --no-session` the **documented, proven "one fresh process
per task" recipe** — directly reproducible from Python's `subprocess.Popen`.

### The three options (README Philosophy) for "one Pi instance per sub-clippy"

| Option | Lifecycle model | Fit for Clippy sub-agents |
| --- | --- | --- |
| **A. Fresh `pi --mode json -p --no-session` per sub-task** (official subagent example) | Process per task; exit = done | Best for short-lived sub-clippies; structured events, exit-code completion, zero state coupling. |
| **B. One long-lived `pi --mode rpc` process per sub-clippy** | Process per instance; open channel; prompt/steer/followUp/abort; `agent_settled` = done | Best for a persistent sub-clippy that a user can keep messaging (reply to, steer, follow-up) and whose progress needs rich live events; steerable mid-run. Built for non-Node hosts (Python). |
| **C. tmux panes (README's literal suggestion)** | OS-visible terminal per instance; interact via tmux UX | Only if you want human-visible interactive panes and full observability ("Full observability, direct interaction" — README Philosophy). Harder to parse structured output from Python; needed only for the "watch it happen in your own terminal" scenario. |

**Recommendation for L2/L3 sub-clippies (the "one Pi instance per sub-clippy" ticket):**
- Default: **B** — one `pi --mode rpc --no-session` process per sub-clippy, kept alive
  for the conversation; rich live thinking/tool deltas, steer/follow-up queueing, and
  clean terminal-completion signalling.
- For fire-and-forget sub-tasks (a scouted research task, a small patch), **A** matches
  the official subagent example exactly and is simplest (process boundary = isolation;
  exit code = completion).
- Use C (tmux) only when human observability of the agent's terminal is a product goal.

### Lifecycle signals that a task completed
- **Process exit code** — authoritative for A (the subagent extension resolves on
  `proc.on("close")` and treats non-zero as error; source ~line 2880–3018).
- **`agent_end`** — "One low-level agent run completes (may still be followed by retry,
  compaction, or queued continuations)" (rpc.md "Event Types").
- **`agent_settled`** — "Agent run is fully settled; no automatic retry, compaction retry,
  or queued continuation remains" — this is the **terminal** "fully done" event and the
  right completion signal for long-lived RPC instances (rpc.md "Event Types").
- **`message_end` / `turn_end`** — per-message/turn completion; assistant messages carry
  `stopReason` ∈ `"stop" | "length" | "toolUse" | "error" | "aborted"` (rpc.md "Types").
- RPC `get_state` exposes `isStreaming`, `isCompacting`, `messageCount` for polling
  liveness; `abort` returns only after the session is idle (rpc.md).
- The subagent example also uses `stopReason === "error" | "aborted"` on the final
  assistant message as a failure signal (source, ~line 2600).

---

## 6. Installation reality on this Mac

Checked on this machine (branch `research/pi-drive-surface`):

- **Pi is NOT installed.** `which pi` → not found; `pi --version` → command not found.
  Not present in global npm (`npm list -g` empty/`pi` absent); no binary at
  `/usr/local/bin/pi` or `/opt/homebrew/bin/pi`; no `~/.pi` or `~/.pi/agent` directory.
- Node toolchain **is** present: node `v26.8.2`, npm `11.19.1`, both at
  `/opt/homebrew/bin` (Homebrew). `tmux` is installed at `/opt/homebrew/bin/tmux`.
- Official install paths (README "Quick Start"; pi.dev/docs/latest):
  - script installer: `curl -fsSL https://pi.dev/install.sh | sh`
  - npm (recommended, `--ignore-scripts`): `npm install -g --ignore-scripts @earendil-works/pi-coding-agent`
  - uninstall: `npm uninstall -g @earendil-works/pi-coding-agent`
  - self-update: `pi update --self` / reinstall even if current: `pi update --self --force`
- npm package reality: `@earendil-works/pi-coding-agent` v0.85.1, published ~6 days ago
  (as of 2026-09-11), 45 versions, ~1.98M weekly downloads, MIT
  (https://www.npmjs.com/package/@earendil-works/pi-coding-agent).
- Installer vs npm: both are supported; the script installer exists mainly for
  non-npm environments. On this Mac, the natural install is the Homebrew-node npm path
  (`npm install -g --ignore-scripts @earendil-works/pi-coding-agent`), which
  Clippy's packaging/CI should do (or vendor/package Pi as part of the app bundle).

---

## Recommended drive surface

**Primary: RPC mode, one `pi --mode rpc --no-session` process per sub-clippy.**
- First-party, language-agnostic protocol with a Python client example in the doc
  (`packages/coding-agent/docs/rpc.md` — Popen, JSONL in/out, `\n`-only framing).
- Rich live events: `message_update` gives text + thinking + tool-call deltas;
  `tool_execution_*` gives every tool invocation with streaming output — exactly the
  "current thinking and actions" feed a desktop UI wants (Q2).
- Bidirectional drive: `prompt` / `steer` / `follow_up` / `abort` / `get_state` /
  `set_thinking_level` / extension-UI confirmations — a true conversational surface.
- Completion: watch `agent_settled` (fully settled) per prompt, fall back on
  `get_state`/process signals for liveness.

**Sub-tasks (one-shot sub-clippies): fresh `pi --mode json -p --no-session` per task** —
the exact pattern Pi's own subagent example extension uses
(`examples/extensions/subagent/index.ts`, args at ~line 2804). Process exit code +
`message_end`/`tool_result_end` events determine completion; emulate the example's
failure rule (`exitCode !== 0 || stopReason error/aborted`).

**Do not use** the interactive TUI from Python, and **do not (initially) attempt the
Node SDK** from Python; if full OpenClaw-style embedding (custom tools/system prompts)
is ever needed, the path is a thin Node bridge process using
`createAgentSession()` (as OpenClaw does in `src/agents/pi-embedded-runner/`), not a
direct Python SDK call.

**tmux** is only relevant if humans must watch sub-agents in real terminals (README's
own suggestion for sub-agents under "No sub-agents").

## Open questions / risks

- **Auth & config isolation.** RPC/json instances share one config dir by default
  (`~/.pi/agent`; override `PI_CODING_AGENT_DIR`, README "Environment Variables", SDK
  "Directories"). Multiple sub-clippies will share credentials from `auth.json` / env
  keys; per-instance isolation needs `--session-dir`/`PI_CODING_AGENT_DIR` or a shared
  auth story (Claude subscriptions vs API keys, README "Providers & Models").
- **Project trust.** Interactive mode asks; non-interactive modes don't and fall back to
  `defaultProjectTrust` (`ask`/`never` ignore project `.pi` resources). To load project
  skills/settings/extensions in a wrapped instance you must pass `-a/--approve` or set
  `defaultProjectTrust: "always"` (README "Project Trust"). Decide per-project.
- **Delta-only streaming.** `message_update` is intentionally non-cumulative; the client
  must assemble partials with `contentIndex` and treat `message_end` as authoritative
  (docs/json.md; rpc.md). Also provider usage may be 0 mid-stream.
- **Version skew.** Fast-moving package (0.85.1, 45 versions, ~1.98M weekly downloads).
  Pin the version Clippy bundles; `pi update --self --force` exists for reinstalls.
- **Framing discipline.** RPC JSONL must be split on `\n` only — Python's `splitlines()`
  could split on Unicode separators inside JSON; the doc explicitly flags this and the
  Python example avoids it (rpc.md "Framing").
- **Sub-agent provenance/observability.** Pi sets `AI_AGENT=pi` and
  `PI_CODING_AGENT=true` for child processes (README "Environment Variables"); a spawned
  `pi` under Clippy won't by itself know it's a sub-clippy — pass a marker (e.g.
  `--name`, `--system-prompt`/`--append-system-prompt`) so nested Pi identifies itself.
- **Python → RPC edge cases to test first**: keep-alive/backpressure on long stdout
  streams, concurrency (parallel sub-clippies), and abort semantics (`abort`,
  `clear_queue`, then process kill if needed) mirror what the subagent example does with
  SIGINT propagation.