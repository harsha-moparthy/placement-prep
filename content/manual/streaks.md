---
title: Streaks
tags: [manual]
---

The [Streaks board](https://harsha-moparthy.github.io/placement-prep/static/streaks.html) shows a LeetCode-style calendar per person, plus current/longest streak, active days, this-week count, and a 14-day team momentum chart.

## What counts
Any **git commit authored by you** on the `main` branch, on that UTC day. Bot commits (`github-actions`) are excluded. Issues and comments do **not** count — only pushed commits.

## Attribution rules
The nightly script matches commit author name/email against:
- harsha: `harsha-moparthy`, `harsha moparthy`, `srihamop`
- akanksh: `avakanksh`, `akanksh`

> [!warning] If your git identity matches none of these, your commits are silently ignored. Check with `git config user.name` / `user.email`. Fix: `git config --global user.email "<github-username>@users.noreply.github.com"`.

## Refresh schedule
- Nightly at **00:00 IST** (cron)
- On every push touching `content/`
- Days roll over at **UTC midnight** (05:30 IST), so a late-night IST commit may land on the "previous" day. Consistent rule, applied to both people.

## Reading the calendar
- Green intensity = commits that day (4 levels), today has a green ring
- "N-day streak at risk — nothing pushed today yet" appears until you push something that day
