# Wayfinding operations (local-markdown tracker)

Clippy uses the **local-markdown tracker**: no external issue tracker is wired up, so the map and its tickets live as Markdown files in this repo, under `wayfinder/`.

## Where things live

- **Map** — `wayfinder/map.md`, the single canonical artifact. Label `wayfinder:map` in frontmatter.
- **Tickets** — one file per issue: `wayfinder/tickets/<NNN>-<slug>.md`. The numeric `id` in frontmatter is the identity.
- **Index** — `wayfinder/README.md` lists every ticket (open and closed), its state, and what it blocks. This is the tracker's "issue list" so the frontier is queryable without opening each file.

## Issue representation (ticket file)

Frontmatter fields:

- `id` — numeric, unique (`001`, `002`, …)
- `title` — the ticket's name (refer to tickets by this name, never by bare id)
- `type` — `research` | `prototype` | `grilling` | `task`
- `status` — `open` | `closed`
- `assignee` — the dev driving it (a session claims a ticket by setting this *first*); empty is unclaimed
- `blocked_by` — list of ticket ids that must be `closed` before this one is takeable
- `labels` — includes the `wayfinder:<type>` label

Body is the `## Question` (the decision or investigation this ticket resolves). The answer is recorded in a `## Resolution` section on close; assets are links, not pasted bodies.

## Blocking

Native dependency edges expressed as `blocked_by` in frontmatter. A ticket is **unblocked** when every id in `blocked_by` is closed. The **frontier** is the set of open, unblocked, unclaimed tickets.

## Frontier query

```
for each ticket file in wayfinder/tickets/:
  open if status == open
  unblocked if all(blocked_by ids are status == closed)
  unclaimed if assignee empty
frontier = tickets satisfying all three
```

The `wayfinder/README.md` index is regenerated (or manually kept) so the frontier is visible at a glance.