# Code review remediation plan

Status: **implemented** (see [Result](#result)) · origin: codebase review
(chat-sequence logic, security, performance)

This document records the issues found in a review of the Clippy app and the
plan to fix them. Each item names the owning module, the fix, and how it is
verified. Findings were reproduced against commit `32cbdf7`.

## Decisions taken

The review left five open questions. The choices made for this pass:

- **A. Pane sanitizer** — replace the blocklist with an **explicit allowlist**
  (tags + attributes + URL schemes), extracted into
  `assets/pane/sanitize.js` so its security predicates (`isAllowedTag`,
  `isAllowedAttr`, `safeUrl`) are pure and unit-testable from Node without a
  DOM. No new dependencies (no DOMPurify/jsdom); consistent with the vendored,
  offline-first approach.
- **B. Speech bubble** — the avatar shell stores `_bubble` but never draws it;
  the window is sized to the avatar and has no room for a bubble. The live
  stream bubble lives in the pane, which is where the user actually reads.
  This pass **documents the shell `set_bubble` API as non-visual** and
  **corrects the README** rather than resizing the avatar window. Rendering it
  (or removing the API) remains a follow-up product decision.
- **C. Stream bubble scope** — implement the README's **one bubble per agent
  run** (one user prompt), not one per assistant message. The router opens the
  bubble once per run and keeps it across tool-call turns; the final answer
  replaces whatever streamed in.
- **D. Tests** — add a stdlib `tests/` package (`unittest`, no new deps) plus a
  Node test for the pane sanitizer predicates.
- **E. Granularity** — security first, then correctness, then robustness/perf,
  then cleanup, each item independently verifiable.

## Phase 0 — Test safety net

There were no tests. Add `tests/` (stdlib `unittest`) covering the pure logic
touched below, and a `tests/test_sanitize.mjs` (Node) for the pane sanitizer
predicates. Run with:

```
.venv/bin/python -m unittest discover -s tests
node --test tests/test_sanitize.mjs
```

## Phase 1 — Security

| # | Issue | Fix | Verify |
|---|---|---|---|
| 1.1 | `--delegate` spawns a sub-agent with `tools=None`, i.e. Pi's full default tool set and no gate (`session.py:931-944`, `model.py:296`, `subagent.py:188`) | Default to `SANDBOX_TOOLS` in `Delegation.make`/`delegate`/`_spawn_worker`; make `PiSubAgent` refuse a `None` allowlist | unit: delegation tools are sandbox; `_cmd()` contains `--tools` |
| 1.2 | Build-mode gate is a deny-list covering only `bash,write,edit` (`clippy-gate.ts:20`) | Gate by **allowlist of read-only tools**; block everything unknown; keep fail-closed `!hasUI` | unit (gate policy ported/asserted); manual build-mode check |
| 1.3 | Pane sanitizer is a blocklist with `data:`/`xlink:href`/`srcset`/… bypasses (`w1c_pane.html:260-280`) | Allowlist sanitizer in `assets/pane/sanitize.js` | Node test: XSS corpus produces no executable/navigable payload |
| 1.4 | `notify()` builds AppleScript from Python `repr` (`notify.py:17-30`) | Escape `\` and `"` for AppleScript; keep `notify-send` argv | unit: quoted/backslash text yields a balanced script |

## Phase 2 — Chat-sequence correctness

| # | Issue | Fix | Verify |
|---|---|---|---|
| 2.5 | Intermediate `stopReason=toolUse` messages are treated as final answers (`events.py:306-316`, `prime.py:99-104`) | Final only for `stop`/`length`; `toolUse` ignored; `error`/`aborted` route to alert/exit | unit: toolUse does not finalize/trigger directives |
| 2.6 | Final answer can render twice (message_end then settled both `stream_end` text) (`prime.py:111-119`, `session.py:804-811`, `w1c_pane.html:337-360`) | Pane `stream_end` only replaces the answer for non-empty text; Python finalizes exactly once | JS/logic test + manual |
| 2.7 | Stream scope is per assistant message, README says per turn (`events.py:107`) | Open one bubble per agent run; represent `turn_start`/`turn_end` distinctly | unit: one `stream_start` per run |
| 2.8 | `parse_delegation` needs `[CLIPPY::END]`; schedule/notify tolerate its absence (`subagent.py:35-54`) | Allow the close marker to be optional (end of line) | unit: open block without close still delegates |
| 2.9 | `_pending_user_text` set for commands and not cleared on empty answers; `_curator_busy` can stick `True` (`session.py:222-226,815-854`) | Set staging only for brain-bound messages; clear on every answer; reset busy in `finally` | unit: `/help` not paired; busy resets |
| 2.10 | Prefix matching lets `/helper`, `/exiting` shadow commands (`session.py:311-360`) | Match the command token exactly (followed by space/end) | unit: `/helper` → unknown command |

## Phase 3 — Robustness

| # | Issue | Fix | Verify |
|---|---|---|---|
| 3.11 | `at`/`daily` hours not range-checked → `ValueError` in `_next_wake`; `Session.update` has no job isolation (`scheduler.py:76-81,152-165`, `session.py:211-239`) | Validate `0≤h≤23`, `0≤m≤59`; wrap each queued job in try/except | unit: `at 99:00` rejected; raising job does not kill tick |
| 3.12 | No `exit` transition: a crashed brain leaves the prime SM out of `idle` forever (`model.py:346-359`, `prime.py:130-133`) | Add `* → idle` on `exit` | unit: after exit, `is_in("idle")` |
| 3.13 | Leaked stderr fd if `Popen` raises; `--real` bypasses `pi_ready` (`brain.py:150-163`) | Close fd on failure; guard `--real` when `pi` is absent | unit: bad command surfaces cleanly |

## Phase 4 — Performance

| # | Issue | Fix | Verify |
|---|---|---|---|
| 4.14 | Full accumulated buffer pushed to the webview on every delta (`events.py:275-294`) | Throttle pushes (≈50 ms), always final on `message_end`/`stream_end` | unit: N deltas ⇒ bounded pushes, final delivered |
| 4.15 | Chat log flushes per delta (`chatlog.py:56-57`) | Buffer and flush on a timer / turn boundary | unit: one flush per turn |
| 4.16 | `pi_ready()` runs `pi --list-models` on every spawn/toggle/curate (`subagent.py:124-145`) | Cache the result for the process; expose refresh | unit: second call does no subprocess |

## Phase 5 — Cleanup

| # | Issue | Fix | Verify |
|---|---|---|---|
| 5.17 | Shell `set_bubble`/`mode`/`dialog_pending` are never rendered (`shell.py:176-178`) | Document as non-visual (pane owns the live bubble); fix README | review |
| 5.18 | README claims a Node DOM-shim test and a shell speech/status line; curator boundary is a soft risk | Correct docs; note accepted risks (soft `~/.clippy/memory` boundary; default-on transcripts) | review |

## Phase 6 — Consent-gated worker escalation (Option A)

A follow-up gap: in build mode, delegating a task that needs `bash` simply
failed — workers are hard-sandboxed regardless of mode and run as one-shot
`pi --mode json -p` processes where `ctx.hasUI === false`, so a gate can only
block, never ask. There was no way to grant a worker command access.

Chosen fix (Option A — per-delegation grant):

| # | Issue | Fix | Verify |
|---|---|---|---|
| 6.1 | Workers are always read-only; no consent path | Host raises a `review` card (Allow / Read-only / Suggest / Dismiss) before spawning in build mode; `/delegate --allow` and `[CLIPPY::DELEGATE::ELEVATED]` request it in any mode | `tests/test_delegation_consent.py` |
| 6.2 | Clippy-originated cards can't be resolved (`ui_response` always forwards to the prime) | Host-dialog registry (`_host_dialogs`, `host-` ids) resolved locally in `ui_response`; also fixes `/test card` | routing tests |
| 6.3 | Missed prompts when away | Summon the pane and post an OS notification when a card is raised; **no auto-deny** (waits indefinitely) | unit + manual |
| 6.4 | Policy/docs said workers never mutate | Relax `worker_sandbox` constraint; update `sub-clippy` skill + README | review |

Scope and accepted risk: the grant is **per delegation/run**, not per command —
once allowed, the worker can run any command until it finishes (granting `bash`
makes the tool list cosmetic). `Suggest` runs read-only with the user's guidance
appended; `Dismiss` spawns nothing; no confirmable pane (NullPane) fails safe to
read-only. The prime can *request* escalation but never grants it — only the user does.

## Phase 7 — Multi-monitor geometry, dragging, and monitor commands

Follow-up gap: Clippy didn't recognise multiple monitors. On Linux
`visible_screen()` returned `None` (no `_nswindow`) so `_visible_rect()` was a
hardcoded `(0,0,1920,1080)`; `_clamp` pinned him inside it (no cross-monitor
moves); and the delta-driven `on_mouse_drag` self-cancelled (moving the window
changes the next event's delta), so he wasn't really draggable.

| # | Issue | Fix | Verify |
|---|---|---|---|
| 7.1 | Linux hardcoded screen; moves pinned to one monitor | New `clippy/screens.py`: pyglet screens (same space as `set_location`) + GDK work areas scaled into that space; `clamp` targets the point's screen | `tests/test_screens.py`, real-backend smoke |
| 7.2 | Drag not working (delta feedback) | `on_mouse_press` records the grab offset; `update` polls the global cursor (`XQueryPointer`) and places the window at `cursor − offset`, clamped to the union of work areas (cross-monitor). Falls back to delta drag where no global cursor exists | drag-target unit test + Xvfb end-to-end |
| 7.2b | Window was click-through, so no events arrived at all | pyglet's `WINDOW_STYLE_OVERLAY` forces `set_mouse_passthrough(True)` on X11, and pyglet 2.1.16's `set_mouse_passthrough(False)` raises (`XShapeCombineMask` has a bad ctypes signature), so it could never be undone. `ClippyShell` now overrides `set_mouse_passthrough` to drive the input *region* directly (empty = click-through, full-window = normal), keeping the overlay's always-on-top | Xvfb: overlay = no events; region reset = press + 1:1 drag |
| 7.3 | No monitor awareness in commands | `/monitors`; `/move monitor <n> [spot]`; `[CLIPPY::MOVE] monitor <n> [spot]`; `/where` reports the monitor. `MoveSpec` value type shared by `/move` and the directive | `tests/test_screens.py`, `tests/test_directives.py` |
| 7.4 | macOS | Stubbed (`_MacBackend`): keeps pyglet behaviour (primary screen, no work-area inset) with a TODO for the AppKit `NSScreen`/`setFrameTopLeftPoint_` rewrite | review |

Notes:
- Work areas respect panels/docks; the GDK→pyglet scale is inferred from the
  monitor at the origin (XWayland global scale), with a full-geometry fallback.
- Monitor numbering is **1-based, left-to-right**; `/move monitor <n>` centres.
- The pane was **not** touched (it was already correct); `_visible_rect` now
  feeds it a real work area, which only affects edge clamping.

## Result

All items implemented. Verification:

```
.venv/bin/python -m unittest discover -s tests   # 75 tests, OK
node --test tests/test_sanitize.mjs              # 3 tests, OK
.venv/bin/python -m py_compile clippy/*.py main.py
CLIPPY_HOME=$(mktemp -d) .venv/bin/python -m clippy.brain --mock   # SETTLED
```

Notes on the choices made while implementing:

- The **one-bubble-per-run** change lives in `AgentEventRouter` (`_stream_open`,
  `_begin_run`); `turn_start`/`turn_end` are now distinct `Ev`s. Only the prime
  gates on `FINAL_STOP_REASONS` — worker controllers still record every stop
  reason so terminal (`error`/`aborted`) detection is unchanged.
- Stream pushes are coalesced in `PrimeController` (`STREAM_MIN_INTERVAL`, 50 ms)
  and force-flushed before a bubble is finalized; the pane still coalesces its
  own re-render.
- The pane sanitizer is a separate allowlist module (`assets/pane/sanitize.js`)
  so its predicates are unit-tested from Node; it fails **closed** if the module
  is missing.
- `pi_ready()` is memoised (`refresh=True` to re-probe).
- The shell speech bubble was **documented as non-visual** rather than resized or
  removed (decision B) — a follow-up product decision.

### Follow-ups (not in this pass)

- Render (or delete) the shell speech/status surface — needs a UI decision and
  avatar-window layout work.
- The memory curator's `~/.clippy/memory/` boundary remains prompt-enforced; a
  filesystem sandbox would be the real fix.
- **Per-command consent** (Options B/C from the review discussion): an interactive
  `--mode rpc` worker with the gate, or host-mediated execution where the worker
  stays read-only and the host runs approved commands. Option A's per-delegation
  grant is the accepted trade-off for now.
