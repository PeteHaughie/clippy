# Clippy

A floating desktop companion for macOS — an animated **Clippy** avatar in a transparent,
always-on-top window with a retro chat pane, powered by **Pi** (pi.dev) as its brain and
doer.

Clippy is a *projection into userland from the system*: **Pi owns tools, skills, providers,
sessions and approvals**; Clippy owns the desktop surface (the avatar, the w1c chat pane,
dialog cards), persistent memory, and sub-clippy orchestration. It is a local demo/experiment
— Python all the way down, with a pyglet window, a pyobjc `NSPanel` + `WKWebView` pane, and a
long-lived Pi RPC process as the prime brain.

---

## Demo

The app is "alive" when you can: type in the pane → Pi answers with its **thinking streaming
live into a formatted markdown bubble** in the pane → a sandboxed write is blocked (or, in
build mode, approved via a consent card) → skills/memory are in play → a `/delegate` spawns a
sub-clippy that thinks in its own bubble and **explodes** on completion.

```
python main.py --brain              # prime Clippy + chat pane (sandbox mode)
python main.py --delegate           # summon a sub-clippy for the default task
python main.py --mood celebrate     # play one mood, then quit
python main.py --moodcycle          # play every mood in sequence, then quit
```

If a real Pi + provider isn't available, the app **automatically falls back to deterministic
mock brains** so the demo still runs offline (see [MockBrain](#brains)).

---

## Features

- **Floating animated avatar** — transparent, always-on-top, draggable overlay window
  (pyglet 2.x + pyobjc). Animated moods (thinking / working / listening / celebrating / …)
  driven by the conversation state, with a live speech bubble and status line.
- **Retro chat pane** — a borderless transparent `NSPanel` hosting a `WKWebView` running the
  vendored **w1c** retro web-components chat UI (windows-95 theme). Resizable, draggable,
  re-anchors beside Clippy when he moves.
- **Live markdown reasoning stream** — Pi's `thinking` (reasoning) and answer deltas stream
  into one growing bubble per turn, rendered as formatted HTML (`**bold**`, lists, code
  blocks, tables, links…) via a vendored `marked` parser. Thinking is collapsible; the final
  answer is flushed directive-free.
- **Approval cards** — Pi's `extension_ui_request` renders as w1c cards (confirm/select/
  input/editor/notify) with answers round-tripped back to Pi. Build mode gates mutating tools
  behind a fail-closed consent extension.
- **Sandbox by default, build on toggle** — sandbox exposes read-only tools; `Tab` re-spawns
  the brain in build mode where writes ask for consent.
- **Persistent memory** — `~/.clippy/memory/INDEX.md` is injected deterministically into every
  brain session (`--append-system-prompt`), plus a `memory` skill for read/write discipline.
- **Skills allowlist** — Clippy-owned skills (`memory`, `sub-clippy`, `move`) are always on;
  the user's `skills.allow` in config adds more (Pi auto-discovery is disabled with a
  non-empty allowlist).
- **Sub-clippy delegation** — `/delegate <task>` (or an autonomous `[CLIPPY::DELEGATE]`
  directive) spawns a separate one-shot Pi sub-agent in its own floating shell that works,
  reports back, celebrates and **explodes** on completion.
- **Position API** — Clippy knows where he is on screen and can be moved by you (`/move`,
  drag) or by the brain (`[CLIPPY::MOVE]`).

---

## Architecture

```
                 ┌──────────────────────────── pyglet / pyobjc (main thread) ────────────────────────────┐
                 │                                                                                        │
   user          │   ┌──────────────┐  moods/bubble   ┌────────────────┐   typed events   ┌────────────┐  │
 ───────────────▶│   │  avatar shell │◀─────────────── │ PrimeController │◀──────────────── │  PiBrain   │  │
   chat input    │   └──────────────┘                  └────────────────┘                  └─────┬──────┘  │
                 │        ▲ answers / cards / stream                            RPC JSONL        │ pi --mode rpc
                 │   ┌────┴────────────┐            ┌─────────────┐                 ┌──────────▼─────────┐
                 │   │  w1c pane       │◀──────────▶│   Session   │                 │        Pi          │
                 │   │ (WKWebView)     │  JS bridge  │  (graph)    │                 │  tools·skills·prov │
                 │   └─────────────────┘            └──────┬──────┘                 └─────────────────────┘
                 │                                        │ delegate
                 │   ┌──────────────┐   events    ┌───────▼──────┐   one-shot JSON ┌─────────────────────┐
                 │   │ sub-clippy    │◀─────────── │SubClippyCtrl │◀──────────────── │      PiSubAgent     │
                 │   │ shell (+boom) │             └──────────────┘                  └─────────────────────┘
                 └────────────────────────────────────────────────────────────────────────────────────────┘
```

- **Projection over Pi.** Pi is the doer *and* the brain: one long-lived `pi --mode rpc
  --no-session` process for the prime conversation; one-shot `--mode json` children for
  fire-and-forget sub-clippies. Clippy never re-implements the agent loop.
- **The control plane is a typed graph** (`clippy/model.py`): nodes, edges and constraints
  declare the topology (18 nodes / 25 edges / 6 constraints), and `Session` wires callbacks
  as a *projection of the graph edges*. The topology is validated at startup
  (`Session.dump()` explains "why does this event reach the pane?").
- **One definition of truth for events** (`clippy/events.py`): Pi ships the same logical event
  under two wire shapes (`message_update.assistantMessageEvent.type` vs
  `assistant_message_event.eventType`); `normalize()` maps both onto one typed `Ev` catalog,
  and `AgentEventRouter` owns the shared thinking/text buffers.
- **State machines as data** (`clippy/statemachine.py`): `PRIME_CONVERSATION`,
  `WORKER_LIFECYCLE` and the avatar's MoodSM are declared as data and executed generically.
- **Renderers are leaf projections** — avatar playback, the explosion and the pane JS never
  know about the graph; they just react to controller calls.

### Brains

| Class | Where | Real/Offline | Notes |
|---|---|---|---|
| `PiBrain` | `clippy/brain.py` | Real | Long-lived `pi --mode rpc` over strict JSONL; streams events onto a queue for the main thread |
| `MockBrain` | `clippy/brain.py` | Offline | Deterministic scripted stand-in (auto-used when Pi/provider is unavailable) |
| `PiSubAgent` | `clippy/subagent.py` | Real | One-shot `pi --mode json -p --no-session` child per delegation |
| `MockSubAgent` | `clippy/subagent.py` | Offline | Scripted sub-clippy demo (writes `hello.py`, runs it, reports, explodes) |

---

## Requirements

- **macOS** — the pane uses AppKit/WebKit (`WKWebView`, `NSPanel`); everything is Cocoa.
- **Python 3.11+** with a venv containing `pyglet`, `pyobjc` and `pillow`
  (verified on 3.11.13: `pyglet 2.1.16`, `pyobjc 10.3.2`, `pillow 12.3.0`).
- **Pi CLI** — `pi` 0.85.x (the `@earendil-works/pi-coding-agent` npm package, installed e.g.
  at `/opt/homebrew/bin/pi`) with a real provider configured:
  - **oMLX** — a local model box (tailnet or local), provider prefix `omlx`, or
  - **OpenCode Zen** (cloud) — provider prefix `opencode`.
- The default reasoning model is `opencode/deepseek-v4-flash` (cloud). The local oMLX box
  hasn't tested well enough to run the prime yet — Clippy defaults to cloud until a better
  local model is found. `pi_ready()` treats a config with *only* the stock Pi cloud provider
  as not ready.

---

## Setup

```bash
# 1. Python environment
python3 -m venv .venv
.venv/bin/pip install pyglet pyobjc pillow

# 2. Pi (see pi's own docs; already-configured provider required for real mode)
npm install -g @earendil-works/pi-coding-agent   # or install per the pi docs
pi --list-models                                  # should list omlx… or opencode…

# 3. Run — with a provider it goes real; without one it falls back to mock
python main.py --brain
```

No other config is required to start: sandbox mode, the skills allowlist, memory index and
scratch dir are all created/used on demand. See [Configuration](#configuration).

---

## Running

`main.py` is the entry point. Flags:

| Flag | Meaning |
|---|---|
| `--brain [prompt]` | Start the prime Pi brain (RPC) + summon the chat pane. Optional opening prompt (a friendly greeting by default). |
| `--delegate [task]` | Summon a sub-clippy for a task at startup (default task when omitted). |
| `--mood <name>` | Play one mood then quit. `--hint <hint>` narrows it (e.g. `--mood working --hint build`). |
| `--moodcycle` | Play every mood in sequence, then quit. |
| `--real` | Force the real Pi sub-agent/brain instead of the auto mock fallback. |
| `--model <model>` | Model for the real brain/sub-agent (default `opencode/deepseek-v4-flash`). |
| `--scale <n>` | Avatar scale (default `3.0`). |
| `--no-shader` | Use ffmpeg-baked explosion frames instead of the live GLSL chroma-key shader. |

### Controls

**Keyboard (avatar window):**

| Key | Action |
|---|---|
| `Space` | Wave / greeting |
| `T` | Toggle Thinking ↔ RestPose animation |
| `E` | Trigger the explosion |
| `Q` | Quit |
| `N` / `X` | Summon / hide the chat pane (`--brain` mode) |
| `Tab` | Toggle sandbox ↔ build (`--brain` mode) |
| drag | Grab Clippy anywhere and move him |

**Chat commands (pane):**

| Command | Action |
|---|---|
| `/move <spot>` or `/move <x> <y>` | Move Clippy (spots: `top-left`, `center`, …) |
| `/where` | Report Clippy's current position |
| `/delegate <task>` | Spawn a sandboxed sub-clippy for the task |

The brain can also move Clippy itself via a `[CLIPPY::MOVE]` directive, and delegate via a
`[CLIPPY::DELEGATE] … [CLIPPY::END]` block (the `sub-clippy` composition skill).

### Modes

- **Sandbox (default)** — the brain is spawned with read/search-only tools
  (`read`, `grep`, `find`, `ls`).
- **Build** — `Tab` re-spawns the brain with full tools behind the `clippy-gate.ts` consent
  extension: mutating tool calls raise a fail-closed approval card (Allow/Deny).

Pi fixes its tool set at spawn time, so toggling mode re-spawns the brain (Pi 0.85.x).

---

## Project structure

```
assets/
  clippy/            spritesheet (map.png), agent definition, explosion frames
  pane/              w1c_pane.html + vendored w1c components + marked (markdown rendering)
  Green_Screen_Explosion…gif   baked explosion source
clippy/
  brain.py           PiBrain (RPC) + MockBrain
  prime.py           PrimeController — prime lifecycle, streams reasoning to the pane
  controller.py      SubClippyController — worker lifecycle (celebrate → explode → dismiss)
  subagent.py        PiSubAgent (--mode json) + MockSubAgent + /delegate + /move parsing
  session.py         Session — the app topology as data, wired from the graph
  model.py           typed graph: nodes/edges/constraints + Ev catalog + state-machine configs
  events.py          normalize() (both Pi wire shapes) + AgentEventRouter
  statemachine.py    generic state-machine runtime over graph-declared configs
  pane.py            transparent WKWebView NSPanel, JS↔Python bridge, markdown streaming API
  shell.py           floating pyglet window (avatar + explosion + position API)
  avatar.py, moods.py, explosion.py   avatar playback, mood rules, explosion
  memory.py          persistent memory (INDEX.md) + skills allowlist
  config.py, roots.py, config.json    merged config + single roots-of-truth for paths
  skills/            always-on agent skills: memory, sub-clippy, move
  extensions/        clippy-gate.ts build-mode consent extension
main.py              entry point
research/            pi deep-dives and drive-surface notes
wayfinder/           ticket index + map (how the demo got built)
```

---

## Configuration

Config is merged from `clippy/config.json` (defaults) and `~/.clippy/config.json` (user
override, wins). Keys cover the avatar's idle/mood animation pools, mood hints, and the
`skills.allow` list.

Roots of truth (all honour the optional `CLIPPY_HOME` env override for hermetic/headless
runs — default `~/.clippy`):

| Path | Purpose |
|---|---|
| `~/.clippy/config.json` | User config override |
| `~/.clippy/memory/INDEX.md` | Persistent memory, injected into every brain session |
| `~/.clippy/scratch/<timestamp>/` | Working directory for brain/sub-agent work |
| `~/.clippy/brain.stderr.log` etc. | Brain/sub-agent stderr + transcripts (with `CLIPPY_TRANSCRIPT`) |

---

## Development & verification

The codebase is verified headless where the GUI can't run:

```bash
.venv/bin/python -m py_compile clippy/*.py main.py          # compile check
.venv/bin/python -m clippy.brain --mock                       # headless brain round-trip → SETTLED
.venv/bin/python -m clippy.brain --prompt "Reply with: OK"   # headless round-trip against real Pi
```

Structural guarantees: `Session` validates the session graph's required topology at startup
(raises listing any missing connections); the typed-event catalog and state machines are
exercised headless. The pane's markdown/stream JS logic is tested with a Node DOM shim.

To run checks hermetically without touching the real `~/.clippy`:

```bash
CLIPPY_HOME="$(mktemp -d)" .venv/bin/python -m clippy.brain --mock
```

---

## Provenance & license

- **Spritesheet/art:** classic Microsoft Agent Clippy (from `pi0/clippy`). **Microsoft IP —
  fine for a local demo, do not ship commercially.**
- **Vendored web components:** `w1c` (`@w1c/components`, MIT) and `marked` (MIT) — see
  `assets/pane/vendor/*/PROVENANCE.md`.
- **Explosion:** `assets/Green_Screen_Explosion-ezgif.com-crop.gif`.

Research notes (`research/`) and the wayfinder ticket index (`wayfinder/`) document the
design journey and the "why" behind the architecture.