"""MCP (Model Context Protocol) plumbing for Clippy.

Pi 0.85.x has **no built-in MCP support**, so Clippy bridges configured stdio
MCP servers into Pi as custom tools via the ``clippy-mcp`` extension
(``clippy/extensions/clippy-mcp.ts``). This module is the host side:

* read the ``mcp`` block from Clippy's merged config,
* resolve each server's tool names (from config, or by a quick stdio
  ``tools/list`` query — cached),
* produce the env blob the extension reads (``CLIPPY_MCP_SERVERS``) and the
  flat tool-name list used for Pi's ``--tools`` allowlist / the gate allowlist.

Config shape (``clippy/config.json`` merged under ``~/.clippy/config.json``)::

    "mcp": {
      "servers": {
        "personal-assistant": {
          "command": ["uv", "run", "--directory", "/path/to/server", "personal-assistant-mcp"],
          "env": {},
          "prefix": "",
          "tools": []
        }
      }
    }

``tools`` is optional: when empty the server is queried for its tool list.
``prefix`` (default empty) is prepended to tool names, so two servers can expose
the same tool name without colliding.
"""

from __future__ import annotations

import json
import os
import select
import subprocess
import time

#: How long to wait for a server to answer ``tools/list`` at spawn time.
TOOL_QUERY_TIMEOUT = 25.0
#: MCP protocol version this client speaks.
PROTOCOL_VERSION = "2024-11-05"

#: ``command tuple`` -> resolved tool names (bare, unprefixed).
_TOOL_CACHE: dict[tuple, list[str]] = {}


# ------------------------------------------------------------------ config


def load_servers(config: dict) -> list[dict]:
    """Normalise the ``mcp.servers`` config block into server dicts."""
    raw = ((config or {}).get("mcp") or {}).get("servers") or {}
    servers: list[dict] = []
    for name, spec in raw.items():
        spec = spec or {}
        command = spec.get("command")
        if isinstance(command, str):
            command = [command]
        if not command:
            continue
        servers.append(
            {
                "name": str(name),
                "command": [str(part) for part in command],
                "env": {str(k): str(v) for k, v in (spec.get("env") or {}).items()},
                "prefix": str(spec.get("prefix") or ""),
                "tools": [str(t) for t in (spec.get("tools") or [])],
            }
        )
    return servers


def tool_name(server: dict, name: str) -> str:
    """The Pi tool name for a server tool (``prefix + name``)."""
    return f"{server['prefix']}{name}"


def resolve_tools(server: dict) -> list[str]:
    """The server's tool names: from config, else queried (cached)."""
    if server["tools"]:
        return list(server["tools"])
    key = tuple(server["command"])
    if key not in _TOOL_CACHE:
        _TOOL_CACHE[key] = _query_tool_names(server)
    return list(_TOOL_CACHE[key])


def exposed_tool_names(servers: list[dict]) -> list[str]:
    """Flat list of Pi tool names across servers (deduped, order preserved)."""
    seen: set[str] = set()
    names: list[str] = []
    for server in servers:
        for tool in resolve_tools(server):
            pi_name = tool_name(server, tool)
            if pi_name not in seen:
                seen.add(pi_name)
                names.append(pi_name)
    return names


def extension_env(servers: list[dict]) -> str:
    """The JSON blob the ``clippy-mcp`` extension reads from its environment."""
    payload = {
        "servers": [
            {
                "name": s["name"],
                "command": s["command"],
                "env": s["env"],
                "prefix": s["prefix"],
                "tools": resolve_tools(s),
            }
            for s in servers
        ]
    }
    return json.dumps(payload)


# ------------------------------------------------------------------ querying


def _send(proc, obj: dict) -> bool:
    try:
        proc.stdin.write(json.dumps(obj) + "\n")
        proc.stdin.flush()
        return True
    except (BrokenPipeError, ValueError, OSError):
        return False


def _await(proc, want_id: int, deadline: float):
    """Read stdout lines until the response with ``want_id`` arrives (or timeout)."""
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        try:
            ready, _, _ = select.select([proc.stdout], [], [], remaining)
        except (OSError, ValueError):
            return None
        if not ready:
            return None
        line = proc.stdout.readline()
        if not line:
            return None
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(msg, dict) and msg.get("id") == want_id:
            return msg


def _query_tool_names(server: dict) -> list[str]:
    env = {**os.environ, **server["env"]}
    try:
        proc = subprocess.Popen(
            server["command"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
            env=env,
        )
    except OSError as exc:
        print(f"[clippy] mcp '{server['name']}' failed to start: {exc}", flush=True)
        return []
    try:
        deadline = time.monotonic() + TOOL_QUERY_TIMEOUT
        if not _send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {},
                    "clientInfo": {"name": "clippy", "version": "1"},
                },
            },
        ):
            return []
        if _await(proc, 1, deadline) is None:
            print(f"[clippy] mcp '{server['name']}' did not initialise", flush=True)
            return []
        _send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        names: list[str] = []
        cursor: str | None = None
        req = 2
        while True:
            params = {"cursor": cursor} if cursor else {}
            if not _send(
                proc,
                {"jsonrpc": "2.0", "id": req, "method": "tools/list", "params": params},
            ):
                break
            msg = _await(proc, req, deadline)
            if msg is None:
                break
            result = msg.get("result") or {}
            names += [
                t.get("name") for t in (result.get("tools") or []) if t.get("name")
            ]
            cursor = result.get("nextCursor")
            if not cursor:
                break
            req += 1
        if not names:
            print(f"[clippy] mcp '{server['name']}' exposed no tools", flush=True)
        return names
    finally:
        _terminate(proc)


def _terminate(proc) -> None:
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
            proc.wait(timeout=5)
        except Exception:
            pass
    for stream in (getattr(proc, "stdin", None), getattr(proc, "stdout", None)):
        try:
            if stream is not None:
                stream.close()
        except Exception:
            pass
