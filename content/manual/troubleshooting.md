---
title: Troubleshooting
tags: [manual]
---

Every issue we have actually hit, with the fix. Add new ones as they happen.

## Rendering

> [!danger] Block math renders as literal `$$ ... $$`
> The `$$` delimiters must be **on their own lines** — no text before or after on the same line.

> [!danger] Image shows a broken link
> Path is case-sensitive and the file must be under `content/`. `Plot.PNG` ≠ `plot.png`. Prefer keeping images next to the note or in `attachments/`.

> [!danger] Clicking a board link shows a compact/broken page; hard refresh fixes it
> Quartz's SPA router intercepted the link. Board links must be full URLs opening in a new tab (already fixed on the homepage). Inside notes, link boards with full `https://...` URLs, not `/static/...`.

> [!danger] Note doesn't appear on the site
> Check: did the deploy Action pass? Is `draft: true` set? Is the file inside an ignored folder (`private/`, `templates/`)?

## Boards / data

> [!danger] Board shows "Data is Nh old" banner
> The refresh Action failed. Open [Actions](https://github.com/harsha-moparthy/placement-prep/actions), find the red run, read the log. Re-run it from the UI once fixed.

> [!danger] Roadmap bar didn't move after pushing a done note
> 1) Frontmatter must have all four: `track`, `topic`, `status: done`, `author`. 2) `topic` must exactly match an id in `data/roadmap.yaml`. 3) Wait ~1-5 min (CDN cache), hard refresh.

> [!danger] Streak shows 0 despite committing
> Your git author identity doesn't match the attribution list — see [[manual/streaks|Streaks]]. Also remember days roll at UTC midnight.

> [!danger] Task not on the dashboard
> The board only shows **open** issues; check it's assigned (else it's in the unassigned column) and that the snapshot Action ran after your change.

## Git

> [!danger] `git push` rejected: "remote contains work you do not have"
> The bots commit JSON to main. Fix: `git pull --rebase` then push. Make it automatic: `git config pull.rebase true`.

> [!danger] Merge conflict in `data/generated/*.json`
> Never resolve by hand — those files are machine-owned. Take the remote version (`git checkout --theirs data/generated && git add data/generated`) or delete and let the next Action regenerate.

## Local development (optional)

Requires Node ≥ 22.

```bash
npm ci
node ./quartz/bootstrap-cli.mjs plugin install   # add --concurrency 2 on low-RAM machines
node ./quartz/bootstrap-cli.mjs build --serve    # live preview at localhost:8080
```

> [!danger] `npx quartz build` says "could not determine executable"
> Some npx shims fail to resolve the local bin. Use the direct entry point: `node ./quartz/bootstrap-cli.mjs <cmd>`.

> [!danger] Plugins fail to build on a fresh clone
> Lockfile pins went stale: `node ./quartz/bootstrap-cli.mjs plugin install --latest`.

## History of incidents (fixed, kept for reference)
- Pages deploy 404 → Pages wasn't enabled with Source = GitHub Actions before the first deploy.
- Snapshot workflow: "cannot pull with rebase: unstaged changes" → workflows now commit generated JSON **before** rebasing.
- Upstream Quartz CI (preview deployments, dependabot) ran in our repo → removed; only our 5 workflows remain.
