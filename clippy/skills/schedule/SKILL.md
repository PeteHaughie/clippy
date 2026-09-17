---
name: schedule
description: Schedule a timed reminder or alarm. Use when the user asks to be reminded or alerted at a time or on a schedule ("set an alarm for 20 minutes", "remind me at 14:30", "every 2 hours", "daily at 9:00"). Emits the [CLIPPY::SCHEDULE] directive that Clippy's host turns into a wall-clock scheduled task with an OS notification.
---

# Scheduling reminders

Clippy can schedule reminders and alarms on a wall clock. End your reply with a
`[CLIPPY::SCHEDULE] <when> | <what>` block so the host can schedule it. (The
`[CLIPPY::END]` close marker is optional.)

Supported `<when>` forms (use one of these exactly):

- `in N <unit>` — e.g. `in 20 minutes`, `in 2 hours`, `in 30 seconds`.
- `at HH:MM` — e.g. `at 14:30` (today, or tomorrow if it has passed).
- `every N <unit>` — e.g. `every 2 hours` (repeating).
- `daily at HH:MM` — e.g. `daily at 9:00` (repeating).

`<what>` is the reminder text the notification will show.

Example:

```
[CLIPPY::SCHEDULE] in 20 minutes | Time to take a break
```

When the time comes, Clippy posts an OS notification. Repeating schedules
(`every` / `daily at`) keep firing; one-off schedules fire once.