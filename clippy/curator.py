"""Background memory curator: a proxy model that owns memory writes.

Deciding *what* is worth remembering is a judgment task and memory writes need
write/edit tools, which the sandboxed prime brain does not have. So a separate,
short-lived Pi sub-agent ("the curator") is spawned in the background (batched —
every ``memory.every_n_turns`` user turns) to read the transcript, decide which
facts are durable, and persist them to ``~/.clippy/memory/``. The prime brain
keeps *recall* (the INDEX is injected into its system prompt; it can read topic
files), but no longer owns persistence. See ADR-0001 for the skill/API split.

The curator reuses :class:`clippy.subagent.PiSubAgent` (same ``pi --mode json``
plumbing, background read thread, JSONL queue); it is fire-and-forget. The write
discipline here is the same content that used to live in
``clippy/skills/memory/SKILL.md`` (now recall-only for the prime brain).
"""

import datetime
from pathlib import Path

from .roots import MEMORY_DIR, make_scratch_dir
from .subagent import PiSubAgent, MockSubAgent

#: The curator's system prompt: the memory write discipline. Only touch
#: ``~/.clippy/memory/`` (soft boundary — accepted risk for a local demo).
MEMORY_CURATOR_SYSTEM_PROMPT = (
    "You are Clippy's memory curator. Your job is to decide which facts in the "
    "provided conversation are durable and persist them to ~/.clippy/memory/.\n\n"
    "The store:\n"
    "- ~/.clippy/memory/INDEX.md — a short index: one line per note, `[topic] path.md`.\n"
    "- ~/.clippy/memory/<topic>.md — the notes themselves (plain Markdown).\n\n"
    "When to write:\n"
    "- Preferences (\"I prefer…\", \"please always…\", \"don't use X\").\n"
    "- Decisions reached together.\n"
    "- Corrections about the user, their system, or your own behaviour.\n"
    "- Facts worth remembering across sessions (names, machines, projects).\n\n"
    "Trivia and one-off task chatter must NOT be persisted.\n\n"
    "How to write:\n"
    "1. Read ~/.clippy/memory/INDEX.md first (or a topic file if you know it).\n"
    "2. Update the relevant topic file (create it if missing) with the new fact — "
    "keep it terse, dated with `## YYYY-MM-DD` for new entries.\n"
    "3. Add/refresh the INDEX line so the next session can find it.\n\n"
    "Use the write/edit tools. Work within ~/.clippy/memory/ ONLY. If nothing "
    "durable emerges, do nothing."
)


class MemoryCurator(PiSubAgent):
    """Real curator: a short-lived Pi sub-agent with memory write tools.

    Runs with the sandbox read tools plus write/edit, scoped to the memory dir
    by the system prompt. ``cwd`` is a scratch dir so the sub-agent's own
    ``subagent.cmd`` / ``subagent.stderr.log`` do not pollute the memory store.
    """

    def __init__(
        self,
        transcript: str,
        model: str,
        memory_dir: Path = MEMORY_DIR,
        cwd: Path | None = None,
    ):
        super().__init__(
            task=transcript,
            system_prompt=MEMORY_CURATOR_SYSTEM_PROMPT,
            model=model,
            thinking=True,
            cwd=cwd or make_scratch_dir(),
            tools=["read", "grep", "find", "ls", "write", "edit"],
        )
        self.memory_dir = Path(memory_dir)


class MockMemoryCurator(MockSubAgent):
    """Deterministic stand-in for offline runs / ``pi_ready()`` False.

    Instead of calling a model, it appends a dated, transcript-derived note to
    the memory store and refreshes the INDEX, so tests can assert persistence.
    """

    def __init__(self, transcript: str, memory_dir: Path = MEMORY_DIR, cwd: Path | None = None):
        super().__init__(task=transcript, cwd=cwd)
        self.memory_dir = Path(memory_dir)

    def _emit(self):
        try:
            self._persist()
            self._q.put({"type": "agent_start"})
            self._q.put(
                {"type": "message_start", "message": {"role": "assistant", "content": []}}
            )
            self._q.put(
                {
                    "type": "message_end",
                    "message": {
                        "role": "assistant",
                        "stopReason": "stop",
                        "content": [{"type": "text", "text": "Memory curated."}],
                    },
                }
            )
            self._q.put({"type": "agent_end", "willRetry": False})
            self._q.put({"type": "agent_settled"})
        finally:
            self._q.put({"type": "sub_exit", "exit_code": 0})

    def _persist(self):
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        today = datetime.date.today().isoformat()
        note = self.memory_dir / "curated.md"
        with note.open("a", encoding="utf-8") as fh:
            fh.write(f"## {today}\n\nMockMemoryCurator persisted: {self.task[:200]}\n")
        line = "[curated] curated.md\n"
        index = self.memory_dir / "INDEX.md"
        if index.exists():
            text = index.read_text(encoding="utf-8")
            if line not in text:
                with index.open("a", encoding="utf-8") as fh:
                    fh.write(line)
        else:
            index.write_text("# Clippy memory index\n\n" + line, encoding="utf-8")