// Tiny stdio MCP server for the Node mcp-client tests (paginates tools/list).
import { createInterface } from "node:readline";

function send(obj) {
  process.stdout.write(JSON.stringify(obj) + "\n");
}

createInterface({ input: process.stdin }).on("line", (line) => {
  let msg;
  try {
    msg = JSON.parse(line);
  } catch {
    return;
  }
  if (msg.method === "initialize") {
    send({
      jsonrpc: "2.0",
      id: msg.id,
      result: {
        protocolVersion: "2024-11-05",
        capabilities: {},
        serverInfo: { name: "fake", version: "0" },
      },
    });
  } else if (msg.method === "tools/list") {
    const cursor = (msg.params || {}).cursor;
    if (!cursor) {
      send({
        jsonrpc: "2.0",
        id: msg.id,
        result: {
          tools: [{ name: "alpha", description: "a", inputSchema: { type: "object", properties: {} } }],
          nextCursor: "c1",
        },
      });
    } else {
      send({ jsonrpc: "2.0", id: msg.id, result: { tools: [{ name: "beta", description: "b" }] } });
    }
  } else if (msg.method === "tools/call") {
    const name = (msg.params || {}).name;
    if (name === "boom") {
      send({ jsonrpc: "2.0", id: msg.id, result: { isError: true, content: [{ type: "text", text: "nope" }] } });
    } else {
      send({ jsonrpc: "2.0", id: msg.id, result: { content: [{ type: "text", text: "ok:" + name }] } });
    }
  }
});
