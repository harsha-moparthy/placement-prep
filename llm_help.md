# llm_help.md — Instructions for any LLM drafting content for this repo

You are writing for **placement-prep** (https://harsha-moparthy.github.io/placement-prep/), a Quartz 5 static site auto-deployed from this repo via GitHub Actions. Two users: **harsha** (`harsha-moparthy`, tracks: dsa/cp/ml) and **akanksh** (`AvAkanksh`, track: quant). Follow this file exactly; deviations break automation silently.

---

## 1. Where files go

| Content type | Path | Template to copy |
|---|---|---|
| Study article / concept note | `content/<track>/<slug>.md` (`dsa` `cp` `ml` `quant`) | — |
| Problem post-mortem | `content/<track>/pm-<slug>.md` | `content/templates/postmortem.md` |
| Weekly cycle card | `content/retros/cycle-<n>.md` | `content/templates/weekly-cycle.md` |
| Mock scorecard | `content/mocks/<date>-<names>.md` | `content/templates/mock-scorecard.md` |
| Images for a note | `content/<track>/attachments/<name>.png` | — |
| Manual/wiki pages | `content/manual/<slug>.md` | — |

Slugs: lowercase, hyphens, no spaces, no unicode. Never write into `public/` (build output, wiped), `data/generated/` (machine-owned), or `quartz/` (engine) unless explicitly asked.

## 2. Frontmatter contract (automation reads this)

```yaml
---
title: "Human Readable Title"
track: ml            # dsa | cp | ml | quant — must match folder
topic: transformers  # MUST be an exact id from data/roadmap.yaml for that track
status: in-progress  # in-progress | done  (done moves the roadmap progress bar)
author: harsha       # harsha | akanksh (lowercase)
next_review: 2026-07-12   # OPTIONAL, ISO date; triggers spaced-review reminder issues
tags: [ml/transformers]   # optional, hierarchical with /
---
```

Rules:
- All four of `track`, `topic`, `status`, `author` present → note counts toward roadmap. Any missing/typo → silently ignored.
- Check valid `topic` ids in `data/roadmap.yaml` before writing. Never invent ids.
- Only set `status: done` when the human says the topic is finished. Default to `in-progress` for reference articles you draft.
- `draft: true` hides a page from the published site.
- YAML gotcha: titles containing `:` must be quoted.

## 3. Markdown rules (Quartz 5, Obsidian-flavored)

- **Block LaTeX: `$$` delimiters MUST be alone on their own lines.** `$$x$$` inline on one line does NOT render. Inline math uses single `$...$`. KaTeX renders at build time; stick to standard LaTeX (`\mathbb`, `\operatorname`, `\binom`, matrices, aligned all work; exotic packages don't).
- Images: `![[image.png]]` or `![alt](attachments/image.png)`. Paths are **case-sensitive**; file must live under `content/`. Width: `![[image.png|400]]`.
- Internal links: `[[ml/tokenization]]` or `[[ml/tokenization|display text]]` — path relative to `content/`, no `.md`.
- Links to the boards must be **full URLs** (`https://harsha-moparthy.github.io/placement-prep/static/dashboard.html`), never `/static/...` — the SPA router breaks relative static links.
- Callouts: `> [!tip] Title` / `note` / `warning` / `danger` / `example` / `question`. Append `-` after `]` for collapsed.
- Mermaid: fenced block with `mermaid` language. Renders client-side on the live site (raw text under `file://` preview is expected, not a bug). Avoid `&`, `(`/`)` inside node labels — quote labels if needed.
- Code blocks: always specify the language. Escape nested triple-backticks with a 4-backtick fence.
- Headings start at `##` (`#` is reserved for the page title from frontmatter).

## 4. Content style contract (what the humans expect)

1. **Simple English** — a first-year undergrad must follow it. Analogies over jargon. Define every term at first use.
2. **Interview-first**: prioritize what top-company loops (Meta/Google/Amazon/quant firms) actually ask. No tail research ideas; one line max for frontier topics.
3. **Worked examples are mandatory** for algorithms: small numbers, computed by hand, shown step by step (e.g., BPE merges on a 4-word corpus; RoPE dot product with real values).
4. **Grounding is mandatory**: only state facts you verified against a fetched source or computed yourself. End articles with a grounding note listing sources. Paraphrase scraped material, never copy. Never cite a URL you did not fetch. Say "unverified" rather than guess.
5. Structure: numbered `##` sections; comparison table near the end; close with an "interview questions" section including expected-answer hints.
6. Every math-heavy article should include at least one generated figure (matplotlib, save to `attachments/`, dpi≥120) and one runnable code snippet (numpy-level, no framework bloat).

## 5. Build & verify (before any push)

```bash
export PATH="$HOME/.local/share/mise/installs/node/22/bin:$PATH"   # need Node >= 22
node ./quartz/bootstrap-cli.mjs build          # must exit clean
# visual check (macOS):
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless \
  --virtual-time-budget=9000 --screenshot=/tmp_check.png --window-size=1300,2000 \
  "file://$PWD/public/<track>/<slug>.html"
```

Checklist: LaTeX rendered (no raw `$$`)? images present? tables aligned? code highlighted? frontmatter box shows the tags? Then:

```bash
git add content && git commit -m "content: <what>" && git pull --rebase && git push
```

Always `git pull --rebase` before push — bots commit JSON to main continuously.

## 6. Automation map (what your push triggers)

| Event | Workflow | Effect |
|---|---|---|
| push touching `content/**` | deploy | site rebuilds (~2 min) |
| push touching `content/**` or `data/roadmap.yaml` | compute-progress | roadmap bars update (`progress.json`) |
| push touching `content/**`; nightly 00:00 IST | compute-streaks | streak calendar updates |
| any issue event | snapshot-tasks | tasks dashboard updates |
| nightly 03:30 IST | spaced-review | opens `review` issues for due `next_review` dates |

Generated JSON commits carry `[skip ci]` — do not imitate that tag in content commits (it would skip deploying your article).

## 7. Exhaustive issue → fix catalog

**Rendering**
- Raw `$$...$$` visible → delimiters not on their own lines. Fix formatting.
- Formula renders wrong → KaTeX unsupported macro; rewrite with standard commands.
- Broken image → wrong case, wrong relative path, or file outside `content/`.
- Mermaid shows as text on the live site (not just file://) → syntax error in the diagram; validate at mermaid.live.
- Note missing from site → deploy failed (check Actions tab), `draft: true`, or file in `templates/`/`private/` (ignored).
- Wikilink renders as plain text → target path doesn't exist; check exact path relative to `content/`.
- Table broken → missing `|---|` separator row or unescaped `|` inside a cell (use `\|`).

**Automation/data**
- Roadmap bar didn't move → frontmatter incomplete, `topic` id mismatch vs `roadmap.yaml`, or CDN cache (wait ≤5 min, hard refresh).
- Board banner "Data is Nh old" → that workflow failed; open Actions, read log, re-run.
- Streak not counted → commit author identity doesn't match (`harsha-moparthy|harsha moparthy|srihamop` / `avakanksh|akanksh`), or UTC day rollover (05:30 IST).
- Duplicate review issues → never rename a note while an open review issue points at it; close the issue first.
- Task not on dashboard → issue is closed, or snapshot hasn't run since the change (any issue edit re-triggers).

**Git/build**
- Push rejected (non-fast-forward) → `git pull --rebase` then push.
- Conflict in `data/generated/*.json` → take remote (`git checkout --theirs data/generated && git add data/generated`); never hand-edit.
- `npx quartz ...` says "could not determine executable" → use `node ./quartz/bootstrap-cli.mjs ...` directly.
- Build error "Could not resolve ../../.quartz/plugins" → plugins not installed: `node ./quartz/bootstrap-cli.mjs plugin install --concurrency 2`.
- Plugin build fails on fresh clone → stale lockfile: `... plugin install --latest`.
- OOM during plugin install → add `--concurrency 1`.
- Build fails after config edit → YAML indentation error in `quartz.config.yaml`; validate nesting of `options:`.

**Content quality regressions to avoid**
- Copying scraped text verbatim (plagiarism + license risk) — always paraphrase.
- Citing unfetched URLs, inventing paper numbers, or unverified benchmark claims.
- Marking `status: done` on the human's behalf.
- Adding new roadmap topic ids from an article instead of editing `data/roadmap.yaml` deliberately.
- Overwriting `quartz/static/*.html` boards when asked to write articles.

## 8. Quick article skeleton (copy this)

```md
---
title: "Concept X: One-line Promise"
track: ml
topic: <valid-id>
status: in-progress
author: harsha
tags: [ml/x]
---

Hook: why this exists in one paragraph, no jargon.

## 1. The problem it solves
## 2. Method A (with equation + intuition)
## 3. Worked example by hand (small numbers, every step shown)
## 4. Method B / comparisons
## 5. Comparison table (memorize this)
## 6. Code (minimal numpy)
## 7. Questions actually asked in interviews (with answer hints)

*Grounding: <sources actually fetched/computed>.*
```
