---
title: Manual
tags: [manual]
---

Everything about how this site works. Read [[manual/writing-notes|Writing Notes]] first.

## Pages
- [[manual/writing-notes|Writing Notes]] — markdown, LaTeX, images, callouts, diagrams
- [[manual/frontmatter|Frontmatter Reference]] — the fields that drive automation
- [[manual/roadmap|Roadmap & Progress]] — how progress bars compute and update
- [[manual/tasks-and-issues|Tasks & Issues]] — labels, dashboard, question triage
- [[manual/streaks|Streaks]] — how streaks are counted and refreshed
- [[manual/spaced-review|Spaced Review]] — the +2d / +1w / +3w revision system
- [[manual/policy|Coordination Policy]] — cycles, buffers, collisions, junctions
- [[manual/troubleshooting|Troubleshooting]] — every issue we have hit, with fixes

## The system in one diagram

```mermaid
flowchart LR
  A[Write note in content/] -->|git push| B[GitHub Actions]
  B --> C[Quartz build → GitHub Pages]
  B --> D[compute-progress → progress.json]
  E[Create/edit Issues] --> F[snapshot-tasks → tasks.json]
  B --> G[compute-streaks → streaks.json]
  D & F & G --> H[Boards read JSON from raw.githubusercontent]
  I[next_review date arrives] --> J[spaced-review opens reminder Issue]
```
