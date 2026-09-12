/**
 * Clippy build-mode gate (ticket 016).
 *
 * Loaded only on the prime Pi RPC process when Clippy is in BUILD mode
 * (full tools). Intercepts every mutating built-in tool call (bash/write/edit
 * by default) and asks the human for consent through `ctx.ui.confirm`, which
 * surfaces on the RPC wire as an `extension_ui_request` the Python host turns
 * into a card in the pane. The host's `extension_ui_response` resolves the
 * dialog.
 *
 * In modes without a UI (`ctx.hasUI === false`) it fails CLOSED — the mutating
 * call is blocked. Clippy therefore never runs a build-mode brain with an
 * unattended gate: it always answers the dialogs.
 *
 * Gate the set via env: CLIPPY_GATE_TOOLS=bash,write,edit
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const DEFAULT_GATED = ["bash", "write", "edit"];

export default function (pi: ExtensionAPI) {
	const gated = (process.env.CLIPPY_GATE_TOOLS ?? DEFAULT_GATED.join(","))
		.split(",")
		.map((s) => s.trim())
		.filter(Boolean);

	pi.on("tool_call", async (event, ctx) => {
		if (!gated.includes(event.toolName)) return undefined;

		const input = event.input ?? {};
		let detail = "";
		if (event.toolName === "bash") detail = String(input.command ?? "");
		else if (event.toolName === "write" || event.toolName === "edit")
			detail = String(input.file_path ?? input.path ?? "");
		else detail = JSON.stringify(input);

		if (!ctx.hasUI) {
			return {
				block: true,
				reason: `${event.toolName} blocked (no UI for confirmation)`,
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