#!/usr/bin/env python3
"""Snapshot open GitHub issues -> data/generated/tasks.json (runs in Actions)."""
import json, os, urllib.request, datetime

REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["GITHUB_TOKEN"]

def fetch(page):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/issues?state=open&per_page=100&page={page}",
        headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)

tasks, page = [], 1
while True:
    batch = fetch(page)
    if not batch:
        break
    for it in batch:
        if "pull_request" in it:
            continue
        tasks.append({
            "number": it["number"],
            "title": it["title"],
            "labels": [l["name"] for l in it["labels"]],
            "assignees": [a["login"] for a in it["assignees"]],
            "url": it["html_url"],
            "created_at": it["created_at"],
        })
    page += 1

out = {"generated": datetime.datetime.now(datetime.timezone.utc).isoformat(), "tasks": tasks}
os.makedirs("data/generated", exist_ok=True)
with open("data/generated/tasks.json", "w") as f:
    json.dump(out, f, indent=1)
print(f"wrote {len(tasks)} tasks")
