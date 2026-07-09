#!/usr/bin/env python3
"""Scan content/ frontmatter + data/roadmap.yaml -> data/generated/progress.json."""
import json, os, glob, datetime, yaml

with open("data/roadmap.yaml") as f:
    roadmap = yaml.safe_load(f)

def frontmatter(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError:
        print(f"WARN bad frontmatter: {path}")
        return {}

# done[track][topic] = set of authors with a done note
done = {}
for path in glob.glob("content/**/*.md", recursive=True):
    if "/templates/" in path:
        continue
    fm = frontmatter(path)
    if fm.get("status") == "done" and fm.get("track") and fm.get("topic") and fm.get("author"):
        done.setdefault(fm["track"], {}).setdefault(str(fm["topic"]), set()).add(str(fm["author"]))

people = list(roadmap.get("people", {}))
tracks = {}
for tid, t in roadmap["tracks"].items():
    topics = {}
    counts = {p: 0 for p in people}
    for topic in t["topics"]:
        st = {p: ("done" if p in done.get(tid, {}).get(topic["id"], set()) else "todo") for p in people}
        topics[topic["id"]] = {"title": topic["title"], "status": st}
        for p in people:
            counts[p] += st[p] == "done"
    total = len(t["topics"])
    tracks[tid] = {"title": t["title"], "owner": t.get("owner"), "total": total,
                   "users": {p: {"done": counts[p], "pct": round(100 * counts[p] / total)} for p in people},
                   "topics": topics}

out = {"generated": datetime.datetime.now(datetime.timezone.utc).isoformat(), "tracks": tracks}
os.makedirs("data/generated", exist_ok=True)
with open("data/generated/progress.json", "w") as f:
    json.dump(out, f, indent=1)
print("ok")
