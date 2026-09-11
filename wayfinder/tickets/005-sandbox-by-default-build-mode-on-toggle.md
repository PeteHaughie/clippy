---
id: 005
title: Sandbox by default, build mode on toggle
type: grilling
status: open
assignee:
blocked_by: [002]
labels: [wayfinder:grilling]
---

## Question

How should Clippy's sandbox-by-default / selectable-build-mode behave as a per-conversation permission system?

Grill the human on the permission-rules shape: what a sandboxed conversation can and cannot do (read-only? read + safe tools? all tools but no writes?), what exactly flipping build mode grants (file writes + command exec for that conversation?), where the toggle lives in the window, and how it threads down into the doer (Pi) so its actions respect the same boundary. Also: what happens on mode flip mid-task.