"""Timestamped JSONL chat transcripts for debugging.

One ``.jsonl`` file per conversation: the prime session gets ``*-prime.jsonl``
for its whole run, and every sub-clippy delegation gets its own
``*-subclippy-*.jsonl``. Each line is one JSON object with an ISO-8601 UTC
timestamp and a ``type`` field, so a transcript is greppable / replayable and
order is preserved.

Logging is gated by ``logging.enabled`` in config (default on). Writes happen
on the main thread (the event routers and ``session.update`` both drain there).

Deltas (thinking/stream) are buffered and flushed at turn boundaries (a
``response``/marker line) or once the buffer grows past ``FLUSH_BYTES``, so
there is not a write+flush syscall per token; a crash loses at most the current
turn's in-flight deltas, not the transcript. File handles close via ``atexit``.
"""

import atexit
import datetime
import json
from pathlib import Path

from .roots import LOGS_DIR

#: Kinds that mark a turn/session boundary: flush the buffered deltas.
FLUSH_KINDS = frozenset({"response", "turn_start", "chat_start", "task", "sub_exit"})
#: Flush early if the pending buffer grows past this many bytes.
FLUSH_BYTES = 64 * 1024


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def make_chat_log(label: str) -> Path:
    """A timestamped per-conversation transcript path under ``LOGS_DIR``."""
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    return LOGS_DIR / f"{stamp}-{label}.jsonl"


class ChatLogger:
    """Append-only JSONL transcript for one conversation.

    Each method writes one line: ``{"ts": <UTC>, "type": <kind>, **fields}``.
    """

    def __init__(self, path: Path, label: str | None = None):
        self.path = Path(path)
        self.label = label
        self._fh = None
        self._buf: list[str] = []
        self._buf_bytes = 0
        atexit.register(self.close)

    # ------------------------------------------------------------- writing

    def _write(self, kind: str, **fields) -> None:
        entry = {"ts": _now(), "type": kind}
        if self.label:
            entry["label"] = self.label
        entry.update(fields)
        line = json.dumps(entry, ensure_ascii=False) + "\n"
        self._buf.append(line)
        self._buf_bytes += len(line)
        if kind in FLUSH_KINDS or self._buf_bytes >= FLUSH_BYTES:
            self.flush()

    def flush(self) -> None:
        """Write and flush any buffered lines."""
        if not self._buf:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self._fh is None:
            self._fh = open(self.path, "a", encoding="utf-8")
        self._fh.write("".join(self._buf))
        self._fh.flush()
        self._buf = []
        self._buf_bytes = 0

    # ------------------------------------------------------------- events

    def marker(self, kind: str, **fields) -> None:
        """System marker (chat_start / turn_start / task)."""
        self._write(kind, **fields)

    def user(self, text: str) -> None:
        self._write("user", text=text)

    def thinking(self, delta: str) -> None:
        self._write("thinking", delta=delta)

    def stream(self, delta: str) -> None:
        self._write("stream", delta=delta)

    def tool_call(self, tool: str, args=None) -> None:
        self._write("tool_call", tool=tool, args=args)

    def tool_result(self, tool: str, result: str, is_error: bool = False) -> None:
        self._write("tool_result", tool=tool, result=result, is_error=bool(is_error))

    def response(self, stop_reason: str, text: str) -> None:
        self._write("response", stop_reason=stop_reason, text=text)

    def unknown(self, raw: str) -> None:
        self._write("unknown", raw=raw)

    # ------------------------------------------------------------- teardown

    def close(self) -> None:
        self.flush()
        if self._fh is not None:
            try:
                self._fh.flush()
                self._fh.close()
            finally:
                self._fh = None