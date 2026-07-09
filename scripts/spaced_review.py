#!/usr/bin/env python3
"""Open reminder issues for notes whose next_review date has arrived (runs in Actions)."""
import json, os, glob, datetime, urllib.request, yaml

REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["GITHUB_TOKEN"]
HDRS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"}
today = datetime.date.today()

def frontmatter(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    try:
        return yaml.safe_load(text[3:end]) or {} if end != -1 else {}
    except yaml.YAMLError:
        return {}

req = urllib.request.Request(
    f"https://api.github.com/repos/{REPO}/issues?state=open&labels=review&per_page=100", headers=HDRS)
with urllib.request.urlopen(req) as r:
    existing = {i["title"] for i in json.load(r)}

opened = 0
for path in glob.glob("content/**/*.md", recursive=True):
    if "/templates/" in path:
        continue
    fm = frontmatter(path)
    nr = fm.get("next_review")
    if isinstance(nr, str):
        try:
            nr = datetime.date.fromisoformat(nr)
        except ValueError:
            continue
    if not isinstance(nr, datetime.date) or nr > today:
        continue
    title = f"Review: {fm.get('title') or path}"
    if title in existing:
        continue
    assignee = {"harsha": "harsha-moparthy", "akanksh": "AvAkanksh"}.get(fm.get("author"))
    body = {"title": title, "labels": ["review"],
            "body": f"Spaced revisit due ({nr}). Note: `{path}`\n\nAfter revisiting: bump `next_review` (+2d -> +1w -> +3w) and close this."}
    if assignee:
        body["assignees"] = [assignee]
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/issues",
                                 data=json.dumps(body).encode(), headers=HDRS, method="POST")
    urllib.request.urlopen(req)
    opened += 1
print(f"opened {opened} review issues")
