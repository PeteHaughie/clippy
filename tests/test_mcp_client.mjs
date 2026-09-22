// Node tests for the hand-rolled MCP stdio client against a fake server.
// Run: node --test tests/test_mcp_client.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { McpClient } from "../clippy/extensions/mcp-client.js";

const here = dirname(fileURLToPath(import.meta.url));
const FAKE = join(here, "fake_mcp_server.mjs");

function client() {
  return new McpClient({ command: [process.execPath, FAKE], name: "fake" });
}

test("handshake, paginated tools/list, and tools/call", async () => {
  const c = client();
  await c.start();
  try {
    const tools = await c.listTools();
    assert.deepEqual(
      tools.map((t) => t.name),
      ["alpha", "beta"],
    );
    const ok = await c.callTool("alpha", {});
    assert.equal(ok.isError, undefined);
    assert.equal(ok.content[0].text, "ok:alpha");
    const err = await c.callTool("boom", {});
    assert.equal(err.isError, true);
    assert.equal(err.content[0].text, "nope");
  } finally {
    c.close();
  }
});

test("rejects a bad command", async () => {
  const c = new McpClient({ command: ["/nonexistent/bin"], name: "bad" });
  await assert.rejects(() => c.start());
});
