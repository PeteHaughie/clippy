/*
 * Minimal MCP stdio client (newline-delimited JSON-RPC 2.0).
 *
 * Clippy bridges stdio MCP servers into Pi as custom tools. This is the client
 * half — hand-rolled so the extension needs no npm dependencies and works
 * offline. It speaks just enough of the protocol for a tool bridge:
 * initialize → notifications/initialized → tools/list (paginated) → tools/call.
 *
 * Plain ESM (no TypeScript) so it can be unit-tested directly with Node.
 */

import { spawn } from "node:child_process";

const PROTOCOL_VERSION = "2024-11-05";
const DEFAULT_TIMEOUT_MS = 60_000;

export class McpClient {
  constructor({ command, env = {}, name = "mcp" } = {}) {
    if (!Array.isArray(command) || command.length === 0) {
      throw new Error("McpClient requires a non-empty command array");
    }
    this.command = command;
    this.env = env;
    this.name = name;
    this.proc = null;
    this._nextId = 1;
    this._pending = new Map();
    this._buf = "";
    this._closed = false;
  }

  /** Spawn the server and complete the MCP handshake. */
  async start() {
    await new Promise((resolve, reject) => {
      this.proc = spawn(this.command[0], this.command.slice(1), {
        stdio: ["pipe", "pipe", "pipe"],
        env: { ...process.env, ...this.env },
      });
      this.proc.once("error", reject);
      this.proc.stdout.setEncoding("utf8");
      this.proc.stdout.on("data", (chunk) => this._onData(chunk));
      // Drain stderr so a chatty server can't block on a full pipe.
      this.proc.stderr.setEncoding("utf8");
      this.proc.stderr.on("data", () => {});
      this.proc.on("exit", () => this._failAll(new Error(`mcp '${this.name}' exited`)));
      resolve();
    });
    await this.request("initialize", {
      protocolVersion: PROTOCOL_VERSION,
      capabilities: {},
      clientInfo: { name: "clippy", version: "1" },
    });
    this._send({ jsonrpc: "2.0", method: "notifications/initialized" });
  }

  /** All tools the server exposes, following pagination. */
  async listTools() {
    const tools = [];
    let cursor;
    do {
      const res = await this.request("tools/list", cursor ? { cursor } : {});
      tools.push(...((res && res.tools) || []));
      cursor = res && res.nextCursor;
    } while (cursor);
    return tools;
  }

  /** Invoke a tool. Returns the raw MCP result ({ content, isError, ... }). */
  callTool(name, args = {}, timeoutMs = DEFAULT_TIMEOUT_MS) {
    return this.request("tools/call", { name, arguments: args }, timeoutMs);
  }

  request(method, params = {}, timeoutMs = DEFAULT_TIMEOUT_MS) {
    if (this._closed) return Promise.reject(new Error("mcp client closed"));
    const id = this._nextId++;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this._pending.delete(id);
        reject(new Error(`mcp request timed out: ${method}`));
      }, timeoutMs);
      this._pending.set(id, { resolve, reject, timer });
      try {
        this._send({ jsonrpc: "2.0", id, method, params });
      } catch (err) {
        clearTimeout(timer);
        this._pending.delete(id);
        reject(err);
      }
    });
  }

  close() {
    this._closed = true;
    this._failAll(new Error("mcp client closed"));
    if (!this.proc) return;
    try {
      this.proc.stdin.end();
    } catch {}
    try {
      this.proc.kill();
    } catch {}
    this.proc = null;
  }

  // -------------------------------------------------------------- internals

  _send(obj) {
    if (!this.proc || !this.proc.stdin.writable) {
      throw new Error(`mcp '${this.name}' not running`);
    }
    this.proc.stdin.write(JSON.stringify(obj) + "\n");
  }

  _onData(chunk) {
    this._buf += chunk;
    let idx;
    while ((idx = this._buf.indexOf("\n")) !== -1) {
      const line = this._buf.slice(0, idx).trim();
      this._buf = this._buf.slice(idx + 1);
      if (!line) continue;
      let msg;
      try {
        msg = JSON.parse(line);
      } catch {
        continue; // not a JSON-RPC line (log noise)
      }
      if (msg && msg.id != null && this._pending.has(msg.id)) {
        const entry = this._pending.get(msg.id);
        clearTimeout(entry.timer);
        this._pending.delete(msg.id);
        if (msg.error) entry.reject(new Error(msg.error.message || "mcp error"));
        else entry.resolve(msg.result);
      }
    }
  }

  _failAll(err) {
    for (const entry of this._pending.values()) {
      clearTimeout(entry.timer);
      entry.reject(err);
    }
    this._pending.clear();
  }
}
