# Placement Prep — Harsha × Akanksh

Shared knowledge base + coordination system for Dec-2026 placements. Quartz 5 on GitHub Pages.

**Live site:** https://harsha-moparthy.github.io/placement-prep

## Daily workflow
1. Write markdown notes in `content/<track>/` (LaTeX: `$...$` inline, `$$` blocks on their own lines; Obsidian syntax works).
2. Frontmatter drives everything: `track`, `topic` (ids in `data/roadmap.yaml`), `status: done`, `author: harsha|akanksh`, `next_review: YYYY-MM-DD`.
3. `git add -A && git commit && git push` → site auto-deploys.

## Boards (under `/static/` on the live site)
- **dashboard.html** — open GitHub Issues as a two-person kanban (labels: `track:*`, `p1-today|p2-this-week|p3-backlog`)
- **streaks.html** — commit-day heatmap + current/longest streaks (nightly)
- **roadmap.html** — per-track syllabus progress from note frontmatter

## Automation (`.github/workflows/`)
- `deploy.yml` — build + Pages on push
- `snapshot-tasks.yml` / `compute-streaks.yml` / `compute-progress.yml` — refresh `data/generated/*.json` (committed with `[skip ci]`)
- `spaced-review.yml` — nightly: opens `review` issues for notes whose `next_review` has arrived (+2d → +1w → +3w)

## Policy v1
2-week self-certified checkpoints; buffer week each month-end (catch-up, else revision); blocked weeks become Reading Weeks; weekly puzzle hour; bi-weekly teaching swap; cross-domain mocks each phase.

## For LLMs / AI assistants
Read [llm_help.md](llm_help.md) before drafting any content — frontmatter contract, rendering rules, and the full issue→fix catalog.

## Local dev
Node 22+. `npm ci && node ./quartz/bootstrap-cli.mjs plugin install && node ./quartz/bootstrap-cli.mjs build --serve`

