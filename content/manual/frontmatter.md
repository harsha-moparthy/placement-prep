---
title: Frontmatter Reference
tags: [manual]
---

Frontmatter is the YAML block between `---` lines at the top of every note. It drives all automation.

| Field | Values | Consumed by |
|---|---|---|
| `title` | any string | page title, search, review reminders |
| `track` | `dsa` `cp` `ml` `quant` | progress computation |
| `topic` | a topic `id` from `data/roadmap.yaml` | progress computation |
| `status` | `in-progress` / `done` | progress: `done` fills the bar |
| `author` | `harsha` / `akanksh` | progress per person, review assignment |
| `next_review` | `YYYY-MM-DD` | spaced-review reminder issues |
| `tags` | list | tag pages, search |
| `draft` | `true` | excluded from the published site |

## Complete example

```yaml
---
title: "PM: Trapping Rain Water"
track: dsa
topic: sliding-window
status: done
author: harsha
next_review: 2026-07-12
tags: [postmortem, dsa/two-pointers]
---
```

> [!warning] All four of `track`, `topic`, `status`, `author` must be present for a note to count toward the roadmap. A typo in `topic` (not matching a roadmap id) silently counts as nothing — check the roadmap page after pushing.
