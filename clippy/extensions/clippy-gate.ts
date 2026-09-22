/**
 * Clippy build-mode gate (ticket 016).
 *
 * Loaded only on the prime Pi RPC process when Clippy is in BUILD mode
 * (full tools). It fails CLOSED: every tool call must either be on the
 * read-only allowlist or be explicitly confirmed by the human through
 * `ctx.ui.confirm`, which surfaces on the RPC wire as an
 * `extension_ui_request` the Python host turns into a card in the pane. The
 * host's `extension_ui_response` resolves the dialog.
 *
 * This is an ALLOWLIST, not a deny-list: a new or unknown mutating tool does
 * not slip through just because it wasn't named. If there is no UI to confirm
 * on (`ctx.hasUI === false`), every non-read-only call is blocked.
 *
 * Extend the trusted read-only set via env: CLIPPY_GATE_ALLOW=read,grep,...
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

/** Tools considered non-mutating and safe to run without confirmation. */
const DEFAULT_READ_ONLY = ["read", "grep", "find", "ls", "search"];

export default function (pi: ExtensionAPI) {
	const readOnly = new Set(
		(process.env.CLIPPY_GATE_ALLOW ?? DEFAULT_READ_ONLY.join(","))
			.split(",")
			.map((s) => s.trim())
			.filter(Boolean),
	);

	pi.on("tool_call", async (event, ctx) => {
		// Read-only tools never mutate the system; let them run.
		if (readOnly.has(event.toolName)) return undefined;

		const input = event.input ?? {};
		let detail = "";
		if (event.toolName === "bash") detail = String(input.command ?? "");
		else if (event.toolName === "write" || event.toolName === "edit")
			detail = String(input.file_path ?? input.path ?? "");
		else detail = JSON.stringify(input);

		if (!ctx.hasUI) {
			return {
				block: true,
				reason: `${event.toolName} blocked (not on the read-only allowlist and no UI for confirmation)`,
			};
		}

		const confirmed = await ctx.ui.confirm(
			`Allow ${event.toolName}?${detail ? `\n\n  ${detail}` : ""}`
		);

		if (!confirmed) {
			return { block: true, reason: "Blocked by user" };
		}
		return undefined;
	});
}
