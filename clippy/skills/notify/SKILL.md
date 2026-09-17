---
name: notify
description: Surface a desktop notification right now. Use when something important completes or needs the user's attention while they may not be watching the chat pane (e.g. a research or long-running task finished, a result is ready). Emits the [CLIPPY::NOTIFY] directive that Clippy's host turns into an OS notification.
---

# Desktop notifications

Clippy can post an OS-level desktop notification immediately. End your reply
with a `[CLIPPY::NOTIFY] <text>` block when you want to surface something the
user may miss in the pane. (The `[CLIPPY::END]` close marker is optional.)

Example:

```
The search finished — I found 12 results. [CLIPPY::NOTIFY] The search finished with 12 results.
```

Use it for task completions, long-running work that just finished, or important
results. Prefer a notification over burying the answer only in the pane when the
user may be looking elsewhere.