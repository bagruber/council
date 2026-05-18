"""End-to-end integrity check across all data/*.json files.

Run via:  python scripts/validate_data.py
Exit code 0 = clean, 1 = problems found.

Catches the kinds of issues that have bitten us before:
  - Vote yes/no/absent arrays don't sum to expected body size
  - vote.sessionId points to a non-existent session
  - vote.topicId points to a non-existent topic
  - session.agenda[].voteId references a missing vote
  - session.agenda[].topicId references a missing topic
  - session.absent ids that aren't valid members
  - history entry references missing sessionId/voteId
  - press references with broken ids
  - member period gaps / overlaps within member.periods[]
  - BPU composition mismatch (welter-on-BPU-2022 type issues)
  - duplicate ids in press, sessions, votes, topics, members
"""
import json, sys, os
from collections import Counter, defaultdict

BASE = os.path.join(os.path.dirname(__file__), "..", "data")

def load(name):
    with open(os.path.join(BASE, name), encoding="utf-8") as f:
        return json.load(f)

problems = []
warnings = []
def err(msg):  problems.append(msg)
def warn(msg): warnings.append(msg)

members_doc = load("members.json")
members = members_doc["members"]
parties = members_doc.get("parties", [])
bodies  = members_doc.get("bodies", [])
sessions = load("sessions.json")
votes    = load("votes.json")
topics   = load("topics.json")
press    = load("press.json")

member_ids  = {m["id"] for m in members}
session_ids = {s["id"] for s in sessions}
vote_ids    = {v["id"] for v in votes}
topic_ids   = {t["id"] for t in topics}
press_ids   = {p["id"] for p in press}
body_ids    = {b["id"] for b in bodies}

# ── Duplicates ───────────────────────────────────────────────────────────────
for label, items in [("member", [m["id"] for m in members]),
                     ("session",[s["id"] for s in sessions]),
                     ("vote",   [v["id"] for v in votes]),
                     ("topic",  [t["id"] for t in topics]),
                     ("press",  [p["id"] for p in press])]:
    dups = [k for k,c in Counter(items).items() if c>1]
    for d in dups: err(f"duplicate {label} id: {d}")

# ── Cross references ─────────────────────────────────────────────────────────
session_by_id = {s["id"]: s for s in sessions}
vote_by_id    = {v["id"]: v for v in votes}

for v in votes:
    if v["sessionId"] not in session_ids:
        err(f"vote {v['id']}: sessionId '{v['sessionId']}' missing")
    if v.get("topicId") and v["topicId"] not in topic_ids:
        err(f"vote {v['id']}: topicId '{v['topicId']}' missing")

for s in sessions:
    for i, item in enumerate(s.get("agenda", [])):
        vid = item.get("voteId")
        if vid and vid not in vote_ids:
            err(f"session {s['id']} agenda[{i}]: voteId '{vid}' missing")
        tid = item.get("topicId")
        if tid and tid not in topic_ids:
            err(f"session {s['id']} agenda[{i}]: topicId '{tid}' missing")
        for pid in item.get("press", []):
            if pid not in press_ids:
                err(f"session {s['id']} agenda[{i}]: press '{pid}' missing")
    for mid in s.get("absent", []):
        if mid not in member_ids:
            err(f"session {s['id']} absent: '{mid}' not a member")
    for sub in s.get("substitutes", []) or []:
        for fld in ("member","substitute"):
            if sub.get(fld) not in member_ids:
                err(f"session {s['id']} substitutes: '{sub.get(fld)}' not a member")

for t in topics:
    for i, h in enumerate(t.get("history", [])):
        sid = h.get("sessionId")
        if sid and sid not in session_ids:
            err(f"topic {t['id']} history[{i}]: sessionId '{sid}' missing")
        vid = h.get("voteId")
        if vid and vid not in vote_ids:
            err(f"topic {t['id']} history[{i}]: voteId '{vid}' missing")
        for pid in h.get("press", []) or []:
            if pid not in press_ids:
                err(f"topic {t['id']} history[{i}]: press '{pid}' missing")

for m in members:
    profile = m.get("profile") or {}
    for i, mo in enumerate(profile.get("motions", []) or []):
        for pid in mo.get("press", []) or []:
            if pid not in press_ids:
                err(f"member {m['id']} motion[{i}]: press '{pid}' missing")

# ── Vote totals against body composition ─────────────────────────────────────
def expected_seats(sid):
    if sid.startswith("bpu"):  return 12
    if sid.startswith("hvfa"): return 8 if sid < "hvfa_20260501" else 12
    return 25

for v in votes:
    if v.get("type") != "named": continue
    r = v["results"]
    total = len(r["yes"]) + len(r["no"]) + len(r["absent"])
    exp = expected_seats(v["sessionId"])
    if total != exp:
        err(f"vote {v['id']}: named arrays sum to {total}, expected {exp}")
    for mid in r["yes"] + r["no"] + r["absent"]:
        if mid not in member_ids:
            err(f"vote {v['id']}: '{mid}' in results but not a member")

for v in votes:
    if v.get("type") != "anonymous": continue
    r = v["results"]
    if not all(isinstance(r.get(k), int) for k in ("yes","no","absent")):
        err(f"vote {v['id']}: anonymous results must have integer yes/no/absent")
    for mid in (v.get("voters") or {}):
        if mid not in member_ids:
            err(f"vote {v['id']}: voters['{mid}'] not a member")

# ── Member periods ───────────────────────────────────────────────────────────
for m in members:
    periods = m.get("periods") or [{"from": m.get("from"), "to": m.get("to")}]
    for p in periods:
        if p.get("from") and p.get("to") and p["from"] > p["to"]:
            err(f"member {m['id']} period: from {p['from']} > to {p['to']}")
    # Sort and check for overlap
    sortable = [p for p in periods if p.get("from")]
    sortable.sort(key=lambda p: p["from"])
    for a, b in zip(sortable, sortable[1:]):
        if a.get("to") and b["from"] <= a["to"]:
            warn(f"member {m['id']}: periods overlap ({a} / {b})")

# ── BPU composition vs actual votes (welter-on-BPU-2022 etc.) ────────────────
def body_config_at(body, date):
    cfgs = body.get("seatConfigs") or []
    if not cfgs: return body
    for c in cfgs:
        f, t = c.get("from"), c.get("to")
        if (not f or f <= date) and (not t or date <= t):
            return c
    return body

def seat_members_at(body, date):
    cfg = body_config_at(body, date)
    out = set()
    if cfg.get("chair"): out.add(cfg["chair"])
    for vc in cfg.get("vicechairs", []) or []:
        if vc.get("member"): out.add(vc["member"])
    for s in cfg.get("seats", []) or []:
        if s.get("member"): out.add(s["member"])
        for o in s.get("occupants", []) or []:
            of, ot = o.get("from"), o.get("to")
            if of and date < of: continue
            if ot:
                tm = ot+"-99" if len(ot)==7 else ot
                if date > tm: continue
            out.add(o["member"])
    return out

bpu = next((b for b in bodies if b["id"]=="bpu"), None)
if bpu:
    for v in votes:
        if not v["sessionId"].startswith("bpu"): continue
        if v.get("type") != "named": continue
        members_at = seat_members_at(bpu, v["date"])
        cast = set(v["results"]["yes"] + v["results"]["no"] + v["results"]["absent"])
        # subs not in BPU but voting → conflict only if regular IS in seat list
        session = session_by_id.get(v["sessionId"], {})
        subs = {s["substitute"] for s in (session.get("substitutes") or [])}
        stray = (cast - members_at) - subs
        if stray:
            warn(f"vote {v['id']}: id(s) {stray} cast vote but aren't in BPU composition for {v['date']}")

# ── Press date sanity ────────────────────────────────────────────────────────
import re
for p in press:
    if not re.match(r"\d{4}-\d{2}-\d{2}", p.get("date","")):
        err(f"press {p['id']}: invalid date '{p.get('date')}'")

# ── Report ───────────────────────────────────────────────────────────────────
print(f"Checked: {len(members)} members, {len(sessions)} sessions, {len(votes)} votes, "
      f"{len(topics)} topics, {len(press)} press")
print(f"Problems: {len(problems)}, Warnings: {len(warnings)}")
for p in problems: print(" ✗", p)
for w in warnings: print(" ⚠", w)
sys.exit(1 if problems else 0)
