"""PiBrain — a long-lived Pi RPC process as Clippy's brain/doer.

Clippy is a *projection* over Pi: Pi owns tools, skills, providers, sessions
and approvals; Clippy owns the desktop surface (avatar, pane, cards). This
module is the Python host for the one ``pi --mode rpc --no-session`` process
that powers the prime Clippy conversation.

Two implementations of the :class:`Brain` interface:

* :class:`PiBrain`  — real Pi over RPC. Spawns ``pi --mode rpc`` with strict
  JSONL framing (split on ``\\n`` only, strip a trailing ``\\r``), writes
  commands on stdin, streams every event onto a :class:`queue.Queue` for the
  main-thread controller.
* :class:`MockBrain` — scripted stand-in that emits the same event shapes
  without a model; the demo default when Pi (or a configured provider) is
  unavailable.

References: ``pi`` local docs at
``/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/docs/rpc.md``
(Framing, Commands, Events, Extension UI Protocol); verified live against the
local oMLX box.
"""

import json
import os
import select
import subprocess
import threading
import queue
import time
from pathlib import Path

from .roots import make_scratch_dir
from .subagent import pi_ready

#: Default prime model: OpenCode Zen (cloud) reasoning — the local oMLX box
#: hasn't tested well enough to run the prime, so default to cloud until a
#: better local model is found.
DEFAULT_MODEL = "opencode/deepseek-v4-flash"

#: Desktop-assistant persona; Clippy is for organisation, research and light
#: system maintenance — not a programming agent.
DEFAULT_SYSTEM_PROMPT = (
    "You are Clippy, a friendly desktop assistant companion that lives in a "
    "floating window. You help the user with organisation, research, and "
    "light system maintenance. Work in your scratch directory. Be concise, "
    "warm, and honest. Do not ask unnecessary questions."
)


class Brain:
    """Common interface for the prime's reasoning process.

    Events are plain dicts pushed onto ``queue``; the controller consumes
    them on the main thread. ``prompt`` enqueues a user turn (returns
    immediately; events stream asynchronously).
    """

    kind = "abstract"

    def start(self):
        raise NotImplementedError

    @property
    def queue(self) -> queue.Queue:
        raise NotImplementedError

    def prompt(self, message: str, streaming_behavior: str | None = None, images=None):
        raise NotImplementedError

    def steer(self, message: str, images=None):
        raise NotImplementedError

    def follow_up(self, message: str, images=None):
        raise NotImplementedError

    def get_state(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError


class PiBrain(Brain):
    """Real Pi driven over RPC from Python."""

    kind = "pi"

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        system_prompt: str | None = None,
        tools: list[str] | None = None,
        extensions: list[str] | None = None,
        append_system_prompt: Path | None = None,
        skills: list[str] | None = None,
        name: str | None = None,
        cwd: Path | None = None,
        no_session: bool = True,
        thinking: bool | None = None,
    ):
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools
        self.extensions = extensions or []
        self.append_system_prompt = append_system_prompt
        self.skills = skills
        self.name = name
        self.cwd = cwd or make_scratch_dir()
        self.no_session = no_session
        self.thinking = thinking
        self._q: queue.Queue = queue.Queue()
        self._proc: subprocess.Popen | None = None
        self._reader: threading.Thread | None = None
        self._lock = threading.Lock()
        self._stderr_path = self.cwd / "brain.stderr.log"
        env = os.environ.get("CLIPPY_TRANSCRIPT")
        self._transcript = Path(env) if env else None
        self._xf: object | None = None

    @property
    def queue(self) -> queue.Queue:
        return self._q

    def _cmd(self) -> list[str]:
        cmd = ["pi", "--mode", "rpc"]
        if self.no_session:
            cmd.append("--no-session")
        if self.name:
            cmd += ["--name", self.name]
        if self.model:
            cmd += ["--model", self.model]
        if self.system_prompt:
            cmd += ["--system-prompt", self.system_prompt]
        if self.append_system_prompt:
            cmd += ["--append-system-prompt", str(self.append_system_prompt)]
        if self.tools:
            cmd += ["--tools", ",".join(self.tools)]
        for ext in self.extensions:
            cmd += ["-e", str(ext)]
        if self.skills:
            # Editable allowlist: disable auto-discovery, expose only these.
            cmd += ["--no-skills"]
            for skill in self.skills:
                cmd += ["--skill", str(skill)]
        if self.thinking is not None:
            cmd += ["--thinking", "high" if self.thinking else "off"]
        return cmd

    def start(self):
        self.cwd.mkdir(parents=True, exist_ok=True)
        stderr_fh = open(self._stderr_path, "w")
        if self._transcript is not None:
            self._xf = open(self._transcript, "a")
        try:
            self._proc = subprocess.Popen(
                self._cmd(),
                cwd=str(self.cwd),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=stderr_fh,
                text=True,
                bufsize=1,
            )
        except OSError:
            # Don't leak the log/transcript handles when the process can't start.
            stderr_fh.close()
            if self._xf is not None:
                self._xf.close()
                self._xf = None
            raise
        self.cwd.joinpath("brain.cmd").write_text(" ".join(self._cmd()) + "\n")
        self._reader = threading.Thread(
            target=self._read_stdout, args=(stderr_fh,), daemon=True
        )
        self._reader.start()

    def _read_stdout(self, stderr_fh):
        assert self._proc is not None and self._proc.stdout is not None
        for line in self._proc.stdout:
            line = line.rstrip("\r")
            if not line.strip():
                continue
            with self._lock:
                self._log("<<", line)
            try:
                self._q.put(json.loads(line))
            except json.JSONDecodeError:
                self._q.put({"type": "unparseable", "raw": line})
        code = self._proc.wait()
        stderr_fh.close()
        if self._xf is not None:
            self._xf.close()
            self._xf = None
        self._q.put({"type": "brain_exit", "exit_code": code})

    def _log(self, direction: str, line: str):
        """Tee one side of the RPC exchange to the transcript file."""
        if self._xf is None:
            return
        try:
            self._xf.write(f"{direction} {line.rstrip()}\n")
            self._xf.flush()
        except OSError:
            pass

    def send(self, cmd: dict):
        if self._proc is None or self._proc.stdin is None:
            raise RuntimeError("brain not started")
        with self._lock:
            self._log(">>", json.dumps(cmd))
            self._proc.stdin.write(json.dumps(cmd) + "\n")
            self._proc.stdin.flush()

    def prompt(self, message: str, streaming_behavior: str | None = None, images=None):
        cmd: dict = {"type": "prompt", "message": message}
        if streaming_behavior:
            cmd["streamingBehavior"] = streaming_behavior
        if images:
            cmd["images"] = images
        self.send(cmd)

    def steer(self, message: str, images=None):
        cmd: dict = {"type": "steer", "message": message}
        if images:
            cmd["images"] = images
        self.send(cmd)

    def follow_up(self, message: str, images=None):
        cmd: dict = {"type": "follow_up", "message": message}
        if images:
            cmd["images"] = images
        self.send(cmd)

    def get_state(self):
        self.send({"type": "get_state"})

    def abort(self):
        self.send({"type": "abort"})

    def clear_queue(self):
        self.send({"type": "clear_queue"})

    def stop(self):
        if self._proc is not None and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()


# ------------------------------------------------ mock events (prime-shaped)

_MOCK_THINKING = [
    "I'll take a quick look and give a tidy answer.",
    "Keeping it brief — no tool work needed for this one.",
]

_MOCK_TEXT = (
    "On it. Everything's in order on my side — I'll summarise once I've "
    "checked the details."
)


class MockBrain(Brain):
    """Deterministic offline stand-in for the demo / when Pi is unavailable."""

    kind = "mock"

    def __init__(self, cwd: Path | None = None):
        self.cwd = cwd or make_scratch_dir()
        self._q: queue.Queue = queue.Queue()
        self._threads: list[threading.Thread] = []

    @property
    def queue(self) -> queue.Queue:
        return self._q

    def start(self):
        self.cwd.mkdir(parents=True, exist_ok=True)

    def prompt(self, message: str, streaming_behavior: str | None = None, images=None):
        t = threading.Thread(target=self._respond, args=(message,), daemon=True)
        self._threads.append(t)
        t.start()

    def steer(self, message: str, images=None):
        self._respond_quick(f"(steer noted) {message}")

    def follow_up(self, message: str, images=None):
        self._respond_quick(f"(follow-up) {message}")

    def get_state(self):
        self._q.put(
            {
                "type": "response",
                "command": "get_state",
                "success": True,
                "data": {"isStreaming": False, "messageCount": 0, "mock": True},
            }
        )

    def send(self, cmd: dict):
        """No-op host→brain RPC for the mock: just surface the command (e.g. an
        ``extension_ui_response`` resolving a dialog card) so the round trip is
        visible in mock mode."""
        print(f"[mock-brain] send {json.dumps(cmd, ensure_ascii=False)}", flush=True)

    def stop(self):
        pass

    # -------------------------------------------------------------- script

    def _respond_quick(self, text: str):
        t = threading.Thread(target=self._respond, args=(text,), daemon=True)
        self._threads.append(t)
        t.start()

    def _respond(self, message: str):
        self._q.put({"type": "agent_start"})
        self._q.put({"type": "turn_start"})
        self._q.put(
            {"type": "message_start", "message": {"role": "assistant", "content": []}}
        )
        for chunk in _MOCK_THINKING:
            self._q.put(
                {
                    "type": "message_update",
                    "assistantMessageEvent": {"type": "thinking_delta", "delta": chunk + "\n"},
                }
            )
            time.sleep(0.9)
        self._q.put(
            {
                "type": "message_update",
                "assistantMessageEvent": {"type": "thinking_end", "content": " ".join(_MOCK_THINKING)},
            }
        )
        self._q.put(
            {
                "type": "message_update",
                "assistantMessageEvent": {"type": "text_delta", "delta": _MOCK_TEXT},
            }
        )
        self._q.put(
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "stopReason": "stop",
                    "content": [{"type": "text", "text": _MOCK_TEXT}],
                },
            }
        )
        self._q.put({"type": "turn_end", "message": {}, "toolResults": []})
        self._q.put({"type": "agent_end", "willRetry": False})
        self._q.put({"type": "agent_settled"})


# ---------------------------------------------------------------- selftest


def _condensed(event: dict) -> str:
    t = event.get("type")
    if t == "message_update":
        a = event.get("assistantMessageEvent", {})
        return f"  update {a.get('type')}: {a.get('delta', '')[:70]!r}"
    if t == "message_end":
        return (
            f"  message_end stop={event.get('message', {}).get('stopReason')} "
            f"role={event.get('message', {}).get('role')}"
        )
    if t == "response":
        return f"  response {event.get('command')} success={event.get('success')}"
    return f"  {t}"


def run_selftest(prompt_text: str = "Reply with exactly: OK", use_mock: bool = False) -> int:
    """Headless brain round-trip: prompt once, print the condensed stream."""
    if use_mock:
        brain: Brain = MockBrain()
        print("[selftest] mock brain")
    else:
        if not pi_ready():
            print("[selftest] pi not ready — use --mock for offline")
            return 2
        brain = PiBrain(model=DEFAULT_MODEL)
        print(f"[selftest] pi brain ({DEFAULT_MODEL})")
    brain.start()
    brain.prompt(prompt_text)
    settled = False
    deadline = time.time() + 150
    while time.time() < deadline:
        try:
            ev = brain.queue.get(timeout=0.5)
        except queue.Empty:
            if brain.kind == "pi" and brain._proc and brain._proc.poll() is not None:
                break
            continue
        print(_condensed(ev))
        if ev.get("type") == "agent_settled":
            settled = True
            break
        if ev.get("type") == "brain_exit":
            print(f"  brain_exit code={ev.get('exit_code')}")
            break
    print("[selftest]", "SETTLED" if settled else "TIMEOUT")
    brain.stop()
    return 0 if settled else 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Headless brain selftest")
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--prompt", default="Reply with exactly: OK")
    args = parser.parse_args()
    raise SystemExit(run_selftest(args.prompt, use_mock=args.mock))