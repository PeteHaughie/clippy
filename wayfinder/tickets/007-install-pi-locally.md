---
id: 007
title: Install Pi locally
type: task
status: closed
assignee: petehaughie
blocked_by: []
labels: [wayfinder:task]
---

## Resolution

Installed by Pete. Verified: `pi` at `/opt/homebrew/bin/pi`, version **0.85.1** on the PATH. No `~/.pi` config directory yet (no provider auth set up — waits on [Demo provider and model]).

Unblocks: [Sub-clippy lifecycle and explosion].

## Question

Install Pi on this Mac so the sub-clippy prototype has a doer to drive.

Findings from [Pi drive surface]: pi is not installed; Node v26.8.2 + npm 11.19.1 present; the natural install is `npm install -g --ignore-scripts @earendil-works/pi-coding-agent` (v0.85.1). A fresh `pi --mode json -p "1+1"` run should return without error (needs an API key in `~/.pi/agent/auth.json` or env — the provider key can wait on the Demo provider and model ticket, but note what happens without one).

Resolution records: install command used, `pi --version` output, whether a smoke prompt succeeded, and the auth/config state Clippy will inherit.