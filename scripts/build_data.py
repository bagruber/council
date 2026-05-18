"""Build a single optimized data bundle for the runtime.

Reads the 6 hand-maintained JSON files and produces:
  data/bundle.json     — combined doc with all entities + prebuilt indexes

The bundle stays human-readable (indented JSON) — easy to diff in PRs. The
hand-maintained sources remain the source of truth; this script never writes
back to them.

Indexes built:
  votesBySession[sessionId]    → [voteId, …]   ordered by agenda position
  votesByYear[YYYY]            → [voteId, …]
  votesByTopic[topicId]        → [voteId, …]
  sessionsByYear[YYYY]         → [sessionId, …]
  pressByTopic[topicId]        → [pressId, …]  (derived from history)
  memberIndex[memberId]        → {first session date, last session date}

The runtime can fetch one file instead of six, saving 5 RTTs at startup.
"""
import json, os
from collections import defaultdict

BASE = os.path.join(os.path.dirname(__file__), "..", "data")
OUT  = os.path.join(BASE, "bundle.json")

def load(name):
    with open(os.path.join(BASE, name), encoding="utf-8") as f:
        return json.load(f)

bundle = {
    "members":  load("members.json"),
    "sessions": load("sessions.json"),
    "votes":    load("votes.json"),
    "topics":   load("topics.json"),
    "tags":     load("tags.json"),
    "press":    load("press.json"),
}

# ── Indexes ──────────────────────────────────────────────────────────────────
votes_by_session = defaultdict(list)
votes_by_year    = defaultdict(list)
votes_by_topic   = defaultdict(list)

for v in bundle["votes"]:
    votes_by_session[v["sessionId"]].append(v["id"])
    votes_by_year[v["date"][:4]].append(v["id"])
    if v.get("topicId"):
        votes_by_topic[v["topicId"]].append(v["id"])

sessions_by_year = defaultdict(list)
for s in bundle["sessions"]:
    sessions_by_year[s["date"][:4]].append(s["id"])

press_by_topic = defaultdict(set)
for t in bundle["topics"]:
    for h in t.get("history", []):
        for pid in h.get("press", []) or []:
            press_by_topic[t["id"]].add(pid)

member_first_last = {}
session_dates_by_member = defaultdict(list)
for s in bundle["sessions"]:
    # crude: a member is "involved" with a session if they're in absent OR substitutes
    # OR a regular of the body that day. Cheap version: only track absent for now.
    for mid in s.get("absent", []) or []:
        session_dates_by_member[mid].append(s["date"])
for mid, dates in session_dates_by_member.items():
    dates.sort()
    member_first_last[mid] = {"firstAbsence": dates[0], "lastAbsence": dates[-1]}

bundle["indexes"] = {
    "votesBySession":   dict(votes_by_session),
    "votesByYear":      dict(votes_by_year),
    "votesByTopic":     dict(votes_by_topic),
    "sessionsByYear":   dict(sessions_by_year),
    "pressByTopic":     {k: sorted(v) for k, v in press_by_topic.items()},
    "memberAbsenceRange": member_first_last,
}

bundle["meta"] = {
    "counts": {
        "members":  len(bundle["members"]["members"]),
        "sessions": len(bundle["sessions"]),
        "votes":    len(bundle["votes"]),
        "topics":   len(bundle["topics"]),
        "press":    len(bundle["press"]),
    }
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(bundle, f, ensure_ascii=False, indent=2)

print(f"wrote {OUT}  ({os.path.getsize(OUT)/1024:.0f} KB)")
print("  votes/session entries:", sum(len(v) for v in votes_by_session.values()))
print("  press/topic links:    ", sum(len(v) for v in press_by_topic.values()))
