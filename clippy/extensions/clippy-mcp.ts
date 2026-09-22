/**
 * Clippy MCP bridge.
 *
 * Pi 0.85.x has no built-in MCP support, so this extension connects to the
 * stdio MCP servers Clippy configures (passed as JSON in the
 * `CLIPPY_MCP_SERVERS` env var) and registers each of their tools as a Pi
 * custom tool. Tool names are `prefix + name` (prefix defaults to ""), so a
 * server can match a skill's documented tool names.
 *
 * Loaded with `-e` on the prime and on sub-clippies. It is a no-op when
 * `CLIPPY_MCP_SERVERS` is unset. Servers are started from `session_start`
 * (never the factory) and killed on `session_shutdown`.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { McpClient } from "./mcp-client.js";

interface ServerSpec {
  name: string;
  command: string[];
  env?: Record<string, string>;
  prefix?: string;
  tools?: string[];
}

function parseServers(): ServerSpec[] {
  const raw = process.env.CLIPPY_MCP_SERVERS;
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed?.servers) ? parsed.servers : [];
  } catch (err) {
    console.error(`[clippy-mcp] bad CLIPPY_MCP_SERVERS: ${err}`);
    return [];
  }
}

/** Map MCP tool-result content onto Pi tool-result content. */
function toPiContent(content: unknown): Array<Record<string, unknown>> {
  const out: Array<Record<string, unknown>> = [];
  for (const block of Array.isArray(content) ? content : []) {
    const b = block as Record<string, unknown>;
    if (b?.type === "text") {
      out.push({ type: "text", text: String(b.text ?? "") });
    } else if (b?.type === "image" && b.data) {
      out.push({ type: "image", data: b.data, mimeType: b.mimeType });
    } else if (b?.type === "resource") {
      const res = (b.resource ?? {}) as Record<string, unknown>;
      if (typeof res.text === "string") out.push({ type: "text", text: res.text });
    }
  }
  if (out.length === 0) out.push({ type: "text", text: "" });
  return out;
}

function firstText(content: unknown): string {
  for (const block of Array.isArray(content) ? content : []) {
    const b = block as Record<string, unknown>;
    if (b?.type === "text" && b.text) return String(b.text);
  }
  return "MCP tool returned an error";
}

export default function (pi: ExtensionAPI) {
  const specs = parseServers();
  const clients = new Map<string, McpClient>();

  const startAll = async () => {
    for (const spec of specs) {
      if (clients.has(spec.name)) continue;
      const client = new McpClient({
        command: spec.command,
        env: spec.env || {},
        name: spec.name,
      });
      try {
        await client.start();
        const tools = await client.listTools();
        const allow =
          spec.tools && spec.tools.length ? new Set(spec.tools) : null;
        let registered = 0;
        for (const tool of tools) {
          if (!tool?.name || (allow && !allow.has(tool.name))) continue;
          registered += 1;
          pi.registerTool({
            name: `${spec.prefix || ""}${tool.name}`,
            label: tool.name,
            description:
              tool.description || `MCP tool '${tool.name}' from ${spec.name}`,
            // Pass the MCP JSON Schema straight through (enums, required, …).
            parameters: (tool.inputSchema ?? {
              type: "object",
              properties: {},
            }) as never,
            async execute(_toolCallId, params, _signal, _onUpdate) {
              const result = await client.callTool(
                tool.name,
                (params ?? {}) as Record<string, unknown>,
              );
              if (result?.isError) {
                throw new Error(firstText(result?.content));
              }
              return {
                content: toPiContent(result?.content),
                details: {
                  mcp: spec.name,
                  tool: tool.name,
                  structured: result?.structuredContent,
                },
              };
            },
          });
        }
        clients.set(spec.name, client);
        console.error(
          `[clippy-mcp] '${spec.name}': ${registered} tool(s) registered`,
        );
      } catch (err) {
        console.error(`[clippy-mcp] server '${spec.name}' unavailable: ${err}`);
        client.close();
      }
    }
  };

  pi.on("session_start", async () => {
    await startAll();
  });

  pi.on("session_shutdown", async () => {
    for (const client of clients.values()) client.close();
    clients.clear();
  });
}
