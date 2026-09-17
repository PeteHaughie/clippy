"""Sub-agent spawning for the Clippy delegation demo.

Two implementations of the :class:`SubAgent` interface:

* :class:`PiSubAgent`  — real sub-Clippy: a separate Pi process launched in
  ``--mode json`` with its own system prompt, streaming JSONL events onto a
  :class:`queue.Queue` for the controller to consume on the main thread.
* :class:`MockSubAgent` — scripted stand-in that emits the same JSONL-shaped
  events without a model, used as the demo default / fallback when Pi (or a
  configured provider) is unavailable.
"""

import datetime
import json
import re
import shutil
import subprocess
import threading
import queue
import time
from pathlib import Path

from .roots import make_scratch_dir

#: Read/search-only tool allowlist for delegated sub-clippies (005/017).
SUB_SANDBOX_TOOLS = ["read", "grep", "find", "ls"]

#: The composition-skill directive (clippy/skills/sub-clippy): the prime ends
#: its reply with a [CLIPPY::DELEGATE] block; the host turns it into a worker.
DELEGATE_OPEN = "[CLIPPY::DELEGATE]"
DELEGATE_CLOSE = "[CLIPPY::END]"
#: Reliable chat command the user types in the pane: ``/delegate <task>``. The
#: host intercepts it directly (no model compliance needed for the demo path).
DELEGATE_CMD = "/delegate"
_DELEGATE_RE = re.compile(
    r"\[CLIPPY::DELEGATE\]\s*(.*?)\s*\[CLIPPY::END\]", re.DOTALL
)


def parse_delegation(text: str) -> tuple[str, str | None]:
    """Return ``(clean_text, task)`` for an assistant reply.

    If the reply carries a ``[CLIPPY::DELEGATE] … [CLIPPY::END]`` block, ``task``
    is its (stripped) content and the block is removed from ``clean_text``.
    Without a block, ``(text, None)``.
    """
    if not text:
        return "", None
    m = _DELEGATE_RE.search(text)
    if not m:
        return text, None
    task = m.group(1).strip()
    clean = (text[: m.start()] + text[m.end():]).strip()
    return clean, (task or None)

#: The movement directive (clippy/skills/move): the brain ends its reply with
#: a [CLIPPY::MOVE] block to move Clippy on screen; the host turns it into a
#: move (named spot or absolute x y).
MOVE_OPEN = "[CLIPPY::MOVE]"
_MOVE_RE = re.compile(
    r"\[CLIPPY::MOVE\]\s*(.*?)\s*\[CLIPPY::END\]", re.DOTALL
)


def parse_move(text: str) -> tuple[str, str | tuple[int, int] | None]:
    """Return ``(clean_text, move_spec)`` for an assistant reply.

    If the reply carries a ``[CLIPPY::MOVE] … [CLIPPY::END]`` block, the block
    is stripped from ``clean_text`` and ``move_spec`` is either an absolute
    ``(x, y)`` pair or a named-spot string (validated by the caller against
    the shell's known spots). Without a block, ``(text, None)``.
    """
    if not text:
        return "", None
    m = _MOVE_RE.search(text)
    if not m:
        return text, None
    spec = m.group(1).strip()
    clean = (text[: m.start()] + text[m.end():]).strip()
    if not spec:
        return clean, None
    parts = spec.split()
    if len(parts) == 2:
        try:
            return clean, (int(parts[0]), int(parts[1]))
        except ValueError:
            pass
    return clean, spec  # named spot; caller validates

#: Default sub-Clippy model (OpenCode Zen DeepSeek V4 Flash).
DEFAULT_MODEL = "opencode/deepseek-v4-flash"

#: Cheap bang-for-buck alternative.
CHEAP_MODEL = "opencode/deepseek-v4-flash"

DEFAULT_SYSTEM_PROMPT = (
    "You are a subagent instance of Clippy working on a delegated task. "
    "Work autonomously in this directory. Prefer the bash tool for build/run "
    "steps. Report a short final answer to the task. Do not ask questions."
)

DEFAULT_TASK = (
    "In this directory create hello.py that prints 'Hello from sub-clippy!' "
    "when run, run it, and report what it printed."
)


class SubAgent:
    """Common interface. Events are plain dicts pushed onto ``queue``."""

    kind = "abstract"

    def start(self):
        raise NotImplementedError

    @property
    def queue(self) -> queue.Queue:
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError


def pi_ready() -> bool:
    """True if a real Pi binary is on PATH with a known real provider configured.

    Providers we treat as "real": ``omlx`` (oMLX, tailnet or local) and
    ``opencode`` (OpenCode Zen/cloud OpenAI-compatible). A config that only
    has e.g. the stock Pi cloud provider should not be treated as ready for
    the local loop.
    """
    if shutil.which("pi") is None:
        return False
    try:
        out = subprocess.run(
            ["pi", "--list-models"],
            capture_output=True,
            text=True,
            timeout=60,
        ).stdout
    except (subprocess.SubprocessError, OSError):
        return False
    return any(
        line.startswith(("omlx", "opencode")) for line in out.splitlines()
    )


class PiSubAgent(SubAgent):
    kind = "pi"

    def __init__(
        self,
        task: str = DEFAULT_TASK,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        model: str = DEFAULT_MODEL,
        thinking: bool = True,
        cwd: Path | None = None,
        tools: list[str] | None = None,
        skills: list[str] | None = None,
    ):
        self.task = task
        self.system_prompt = system_prompt
        self.model = model
        self.thinking = thinking
        self.cwd = cwd or make_scratch_dir()
        self.tools = tools
        self.skills = skills
        self._q: queue.Queue = queue.Queue()
        self._proc: subprocess.Popen | None = None
        self._thread: threading.Thread | None = None
        self._stderr_path = self.cwd / "subagent.stderr.log"

    @property
    def queue(self) -> queue.Queue:
        return self._q

    def _cmd(self) -> list[str]:
        name = f"subclippy-{datetime.datetime.now().strftime('%H%M%S')}"
        cmd = [
            "pi",
            "--mode", "json",
            "-p",
            "--no-session",
            "--name", name,
            "--model", self.model,
            "--system-prompt", self.system_prompt,
        ]
        if self.tools:
            cmd += ["--tools", ",".join(self.tools)]
        if self.skills:
            # Explicit skill allowlist (mirrors PiBrain): disable auto-discovery
            # and expose only the given Clippy skills (e.g. notify for workers).
            cmd += ["--no-skills"]
            for skill in self.skills:
                cmd += ["--skill", str(skill)]
        cmd += [self.task]
        return cmd

    def start(self):
        cmd = self._cmd()

        stderr_fh = open(self._stderr_path, "w")
        self._proc = subprocess.Popen(
            cmd,
            cwd=str(self.cwd),
            stdout=subprocess.PIPE,
            stderr=stderr_fh,
            text=True,
        )
        self.cwd.joinpath("subagent.cmd").write_text(" ".join(cmd) + "\n")
        self._thread = threading.Thread(
            target=self._read_stdout, args=(stderr_fh,), daemon=True
        )
        self._thread.start()

    def _read_stdout(self, stderr_fh):
        assert self._proc is not None and self._proc.stdout is not None
        for line in self._proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                self._q.put(json.loads(line))
            except json.JSONDecodeError:
                self._q.put({"type": "unparseable", "raw": line})
        code = self._proc.wait()
        stderr_fh.close()
        self._q.put({"type": "sub_exit", "exit_code": code})

    def stop(self):
        if self._proc is not None and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()


# ------------------------------------------------ mock events

_MOCK_SCRIPT = [
    {"type": "agent_start", "mock": True},
    {"type": "message_start", "message": {"role": "assistant", "content": []}},
    {"type": "assistant_message_event", "eventType": "thinking_delta", "delta": "I need to create a small script, then run it to confirm it works.\n"},
    {"type": "assistant_message_event", "eventType": "thinking_delta", "delta": "A hello-world program is the cleanest way to show the delegation loop end to end.\n"},
    {"type": "message_update", "assistantMessageEvent": {"type": "thinking_end"}},
    {"type": "assistant_message_event", "eventType": "text_delta", "delta": "I'll write hello.py and run it."},
    {"type": "assistant_message_event", "eventType": "toolcall_start", "id": "mock_call_1", "toolName": "bash"},
    {"type": "message_update", "assistantMessageEvent": {"type": "message_end", "stopReason": "toolUse"}},
    {"type": "tool_execution_start", "toolCallId": "mock_call_1", "toolName": "bash", "args": {"command": "cat > hello.py << 'EOF'\nprint('Hello from sub-clippy!')\nEOF"}},
    {"type": "tool_execution_update", "toolCallId": "mock_call_1", "partialResult": {"content": [{"type": "text", "text": ""}]}},
    {"type": "tool_execution_end", "toolCallId": "mock_call_1", "result": {"content": [{"type": "text", "text": ""}]}, "isError": False},
    {"type": "assistant_message_event", "eventType": "toolcall_start", "id": "mock_call_2", "toolName": "bash"},
    {"type": "message_update", "assistantMessageEvent": {"type": "message_end", "stopReason": "toolUse"}},
    {"type": "tool_execution_start", "toolCallId": "mock_call_2", "toolName": "bash", "args": {"command": "python3 hello.py"}},
    {"type": "tool_execution_update", "toolCallId": "mock_call_2", "partialResult": {"content": [{"type": "text", "text": "Hello from sub-clippy!\n"}]}},
    {"type": "tool_execution_end", "toolCallId": "mock_call_2", "result": {"content": [{"type": "text", "text": "Hello from sub-clippy!\n"}]}, "isError": False},
    {"type": "assistant_message_event", "eventType": "text_delta", "delta": "The script ran and printed **Hello from sub-clippy!**"},
    {"type": "message_end", "message": {"role": "assistant", "stopReason": "stop", "content": [{"type": "text", "text": "The script ran and printed **Hello from sub-clippy!**"}]}},
    {"type": "agent_end", "willRetry": False},
    {"type": "agent_settled"},
]

_MOCK_STEP_SECONDS = 2.5


class MockSubAgent(SubAgent):
    kind = "mock"

    def __init__(self, task: str = DEFAULT_TASK, cwd: Path | None = None):
        self.task = task
        self.cwd = cwd or make_scratch_dir()
        self._q: queue.Queue = queue.Queue()
        self._thread: threading.Thread | None = None

    @property
    def queue(self) -> queue.Queue:
        return self._q

    def start(self):
        self._thread = threading.Thread(target=self._emit, daemon=True)
        self._thread.start()

    def _emit(self):
        try:
            for event in _MOCK_SCRIPT:
                self._q.put(dict(event))
                time.sleep(_MOCK_STEP_SECONDS)
            self._q.put({"type": "sub_exit", "exit_code": 0})
        finally:
            pass

    def stop(self):
        pass