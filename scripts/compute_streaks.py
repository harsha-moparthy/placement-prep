#!/usr/bin/env python3
"""Compute per-person commit streaks from git history -> data/generated/streaks.json.
Requires full clone (fetch-depth: 0). Dates in UTC."""
import json, os, subprocess, datetime
from collections import defaultdict

PEOPLE = {"harsha": ["harsha-moparthy", "harsha moparthy", "srihamop"],
          "akanksh": ["avakanksh", "akanksh"]}
BOTS = ["github-actions", "[bot]"]

log = subprocess.run(
    ["git", "log", "--format=%an|%ae|%ad", "--date=format-local:%Y-%m-%d"],
    capture_output=True, text=True, env={**os.environ, "TZ": "UTC"}).stdout

days = defaultdict(lambda: defaultdict(int))
unknown = set()
for line in log.splitlines():
    name, email, date = line.split("|")
    ident = (name + " " + email).lower()
    if any(b in ident for b in BOTS):
        continue
    person = next((p for p, keys in PEOPLE.items() if any(k in ident for k in keys)), None)
    if person is None:
        unknown.add(f"{name} <{email}>")
        continue
    days[person][date] += 1

def streaks(heat):
    today = datetime.date.today()
    cur = 0
    d = today
    # current streak: today counts if present; else start from yesterday
    if str(d) not in heat:
        d -= datetime.timedelta(days=1)
    while str(d) in heat:
        cur += 1
        d -= datetime.timedelta(days=1)
    longest = run = 0
    prev = None
    for ds in sorted(heat):
        cur_d = datetime.date.fromisoformat(ds)
        run = run + 1 if prev and (cur_d - prev).days == 1 else 1
        longest = max(longest, run)
        prev = cur_d
    return cur, longest

users = {}
for p in PEOPLE:
    heat = dict(days.get(p, {}))
    cur, longest = streaks(heat)
    users[p] = {"current_streak": cur, "longest_streak": longest,
                "total_days": len(heat), "heatmap": heat}

out = {"generated": datetime.datetime.now(datetime.timezone.utc).isoformat(), "users": users}
os.makedirs("data/generated", exist_ok=True)
with open("data/generated/streaks.json", "w") as f:
    json.dump(out, f, indent=1)
print("unknown authors ignored:", sorted(unknown))
