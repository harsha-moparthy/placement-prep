---
title: Tasks & Issues
tags: [manual]
---

The [Tasks board](https://harsha-moparthy.github.io/placement-prep/static/dashboard.html) is a two-person kanban rendered from **open GitHub Issues**. Closing the issue removes the card.

## Creating work
Use [New issue](https://github.com/harsha-moparthy/placement-prep/issues/new/choose) — three forms:

| Template | Purpose | Auto-labels |
|---|---|---|
| Task | assigned prep work with definition of done | `type:task` |
| Question | a doubt for your partner | `type:question`, `needs-triage` |
| Post-mortem | quick log of a failed problem | `postmortem` |

## Label taxonomy

- Track: `track:dsa` `track:cp` `track:ml` `track:quant`
- Priority: `p1-today` (red) · `p2-this-week` (orange) · `p3-backlog`
- Flow: `needs-triage`, `review` (created by the spaced-review bot)

**Assign the issue** to `harsha-moparthy` or `AvAkanksh` — unassigned issues fall into the "unassigned" column.

## Refresh behavior
Any issue event (open/close/label/assign/edit) triggers the `snapshot-tasks` Action, which rewrites `tasks.json` (~30 s). The board shows the snapshot age; a warning banner appears if data is >6 h old, which means the Action failed — see [[manual/troubleshooting|Troubleshooting]].

## Question flow
1. Ask in giscus on the relevant page (once enabled) or open a Question issue.
2. Partner answers in-thread; if it becomes real work, add labels + assignee, and it appears on the board.
