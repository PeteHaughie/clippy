"""OS-level desktop notifications for Clippy (time-and-scheduling).

A scheduled task or a ``[CLIPPY::NOTIFY]`` directive can surface a real desktop
notification — useful when the user isn't watching the pane. No MCP server, no
new dependencies:

* macOS — ``osascript`` ``display notification`` (built-in, no extra install).
* Linux — ``notify-send`` (libnotify, shipped on most desktops).
* Unavailable — ``notify()`` returns ``False`` so the caller can fall back to a
  pane message.
"""

import shutil
import subprocess


def _applescript_string(value: str) -> str:
    """Render ``value`` as a quoted AppleScript string literal.

    AppleScript string literals use double quotes and recognise the usual
    backslash escapes, so ``repr`` is not a valid encoder (it can emit single
    quotes, which AppleScript does not treat as a string delimiter, and leaves
    quotes/backslashes unescaped). Escape explicitly.
    """
    escaped = (
        str(value)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )
    return f'"{escaped}"'


def _osascript(title: str, text: str) -> bool:
    script = (
        f"display notification {_applescript_string(text)} "
        f"with title {_applescript_string(title)}"
    )
    try:
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return True


def _notify_send(title: str, text: str) -> bool:
    try:
        subprocess.run(
            ["notify-send", title, text],
            capture_output=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return True


def notify(title: str, text: str) -> bool:
    """Post an OS notification. Returns False if no notifier is available.

    Callers should fall back to a pane message when this returns False.
    """
    text = (text or "").strip()
    title = (title or "Clippy").strip()
    if not text:
        return False
    if shutil.which("osascript"):
        return _osascript(title, text)
    if shutil.which("notify-send"):
        return _notify_send(title, text)
    return False