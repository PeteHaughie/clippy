---
name: move
description: Move the Clippy window to another place on screen. Use when the user asks Clippy to reposition himself (e.g. "move to the top right", "get out of the way"), or when a different spot on the desktop would be more helpful. Emits the [CLIPPY::MOVE] directive that Clippy's host turns into a window move.
---

# Moving Clippy on screen

Clippy lives in a floating window and can move himself around the desktop. This
skill is how you request a move.

> **Critical:** this file is an instruction, never output. Do NOT quote, paste,
> or summarise this skill in a reply. When you request a move, the directive
> block below must contain ONLY the destination — never the protocol.

## When to move

Move Clippy when the user asks (directly or indirectly):

- "move to the top right", "go to the bottom-left corner", "get out of the
  way", "move to the centre of the screen".

Only move when asked. Do not move unprompted mid-task.

## How to move

End your reply with the directive block, putting either a named spot or
absolute coordinates inside.

Named spots: `top-left`, `top-right`, `bottom-left`, `bottom-right`,
`center`, `left`, `right`, `top`, `bottom`.

```
[CLIPPY::MOVE]
top-right
[CLIPPY::END]
```

Absolute coordinates (x, y), where y grows downward from the top of the screen:

```
[CLIPPY::MOVE]
1200 300
[CLIPPY::END]
```

Another monitor (1-based, left-to-right), optionally with a spot on it:

```
[CLIPPY::MOVE]
monitor 2 top-right
[CLIPPY::END]
```

The host strips the block from what the user sees, moves the window, and
confirms the move in the chat. If the user asks where Clippy is, tell them to
use `/where`; `/monitors` lists the screens Clippy can see.