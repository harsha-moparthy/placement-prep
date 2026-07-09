---
title: Spaced Review
tags: [manual]
---

Implements the **+2d → +1w → +3w** revisit schedule automatically.

## Workflow

```mermaid
flowchart LR
  A[Fail/struggle on a problem] --> B["Write post-mortem note<br/>next_review: today+2d"]
  B --> C[Nightly bot checks dates]
  C -->|date arrived| D[Opens Issue titled Review: ...<br/>assigned to the author]
  D --> E[You revisit the problem]
  E --> F["Bump next_review (+1w, then +3w)<br/>tick the revisit log, close the Issue"]
  F --> C
```

## Rules
- The bot runs nightly (03:30 IST) and looks at every note's `next_review`.
- It never duplicates: if an open `review` issue with the same title exists, it skips.
- After the third successful revisit (+3w), delete the `next_review` field — the loop ends.
- If a revisit fails (could not re-solve), reset to +2d and restart the ladder.

## Post-mortem discipline
The template (`content/templates/postmortem.md`) forces the four fields that matter: struggle time, your approach, the one-sentence unlock, and the pattern. Fill them immediately after the failure — quality here is what makes the revisit worth anything.
