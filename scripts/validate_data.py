"""End-to-end integrity check across all data/*.json files.

Run via:  python scripts/validate_data.py
Exit code 0 = clean, 1 = problems found.

Prueft zweierlei: die Form gegen data/schema/*.schema.json (braucht
jsonschema, siehe scripts/requirements.txt) und den Zusammenhang zwischen
den Dateien.

Catches the kinds of issues that have bitten us before:
  - Vote yes/no/absent arrays don't sum to expected body size
  - vote.sessionId points to a non-existent session
  - vote.topicIds points to a non-existent topic
  - session.agenda[].voteIds references a missing vote
  - Abstimmungen, die kein Tagesordnungspunkt nennt (sie fehlen auf der Sitzungsseite)
  - session.agenda[].topicId references a missing topic
  - session.absent ids that aren't valid members
  - history entry references missing sessionId/voteId
  - history entry whose vote carries no topicIds (undercounts the dossier)
  - press references with broken ids
  - Mandatsabschnitte: Reihenfolge, Ueberlappung, Fraktion, Rolle, succeeds
  - BPU composition mismatch (welter-on-BPU-2022 type issues)
  - duplicate ids in press, sessions, votes, topics, members
  - Sitzungsregister: niederschrift-Stufe, ID zu Datum und Gremium, Zeiten
  - Identitaetsmerkmale ohne belegte Selbstauskunft
"""
import json, sys, os
from collections import Counter, defaultdict

BASE = os.path.join(os.path.dirname(__file__), "..", "data")
SCHEMA = os.path.join(BASE, "schema")

def load(name):
    with open(os.path.join(BASE, name), encoding="utf-8") as f:
        return json.load(f)

problems = []
warnings = []
def err(msg):  problems.append(msg)
def warn(msg): warnings.append(msg)


def schema_pruefer():
    """Je Datei ein Pruefer gegen data/schema/<name>.schema.json.

    Das Schema sagt, wie eine Datei aussieht; die Pruefungen darunter sagen,
    ob sie zusammenpasst. Beides wird gebraucht: eine formal gueltige Datei
    kann immer noch auf eine sessionId zeigen, die es nicht gibt.
    """
    schemata = {}
    for datei in os.listdir(SCHEMA):
        if datei.endswith(".schema.json"):
            with open(os.path.join(SCHEMA, datei), encoding="utf-8") as f:
                schemata[datei] = json.load(f)
    registry = Registry().with_resources(
        (name, Resource.from_contents(doc, default_specification=DRAFT202012))
        for name, doc in schemata.items())
    return {name.removesuffix(".schema.json"):
            jsonschema.Draft202012Validator(doc, registry=registry)
            for name, doc in schemata.items()}


try:
    import jsonschema
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012
except ImportError:
    warn("jsonschema fehlt - Formpruefung uebersprungen "
         "(pip install -r scripts/requirements.txt)")
else:
    pruefer = schema_pruefer()
    for name in ("members", "parties", "bodies", "media", "sessions",
                 "votes", "topics", "press", "tags"):
        # Zehn Meldungen reichen; bei einem Formfehler sind sie meist alle
        # dieselbe Ursache.
        for fehler in sorted(pruefer[name].iter_errors(load(name + ".json")),
                             key=str)[:10]:
            ort = "/".join(str(x) for x in fehler.absolute_path) or "(Wurzel)"
            err(f"{name}.json {ort}: {fehler.message}")

members = load("members.json")
parties = load("parties.json")["parties"]
bodies  = load("bodies.json")
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
# Das Datum steht an der Sitzung, nicht mehr an jeder Abstimmung.
session_date = lambda v: (session_by_id.get(v["sessionId"]) or {}).get("date")
vote_by_id    = {v["id"]: v for v in votes}

for v in votes:
    if v["sessionId"] not in session_ids:
        err(f"vote {v['id']}: sessionId '{v['sessionId']}' missing")
    for tid in v.get("topicIds", []):
        if tid not in topic_ids:
            err(f"vote {v['id']}: topicIds '{tid}' missing")

NIEDERSCHRIFT = {"vollständig", "auszug", "keine"}
PRAEFIX = {"stadtrat": "sr", "bpu": "bpu", "hvfa": "hvfa"}

for s in sessions:
    # Seit Oktober 2026 ist sessions.json das vollstaendige Register und
    # ersetzt sessionlengths.json und termine.json. Jede Sitzung sagt, was von
    # ihr vorliegt; ob sie war, sagt ihr Datum.
    stufe = s.get("niederschrift")
    if stufe not in NIEDERSCHRIFT:
        err(f"session {s['id']}: niederschrift '{stufe}' - erlaubt sind {sorted(NIEDERSCHRIFT)}")
    if s.get("type") not in PRAEFIX:
        err(f"session {s['id']}: unbekanntes Gremium '{s.get('type')}'")
    else:
        soll = PRAEFIX[s["type"]] + "_" + s["date"].replace("-", "")
        if s["id"] != soll:
            err(f"session {s['id']}: ID passt nicht zu Datum und Gremium (erwartet {soll})")
    if stufe == "auszug" and not (s.get("source") or {}).get("kind") == "webauszug":
        err(f"session {s['id']}: als Auszug gefuehrt, aber ohne source.kind webauszug")
    if stufe != "keine" and not s.get("agenda"):
        err(f"session {s['id']}: {stufe} veroeffentlicht, aber ohne Tagesordnung")
    if s.get("end") and not s.get("start"):
        err(f"session {s['id']}: Ende ohne Beginn")

    for i, item in enumerate(s.get("agenda", [])):
        for vid in item.get("voteIds", []):
            if vid not in vote_ids:
                err(f"session {s['id']} agenda[{i}]: voteId '{vid}' missing")
            elif item.get("topicId") and vote_by_id[vid].get("topicIds")                     and item["topicId"] not in vote_by_id[vid]["topicIds"]:
                warn(f"session {s['id']} agenda[{i}]: Punkt zeigt auf Thema "
                     f"{item['topicId']}, die Abstimmung {vid} nicht "
                     f"(sondern auf {vote_by_id[vid]['topicIds']})")
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

# Was kein Tagesordnungspunkt nennt, erscheint auf der Sitzungsseite nicht.
genannt = {vid for x in sessions for a in x.get("agenda", [])
           for vid in a.get("voteIds", [])}
for v in votes:
    if v["id"] not in genannt:
        warn(f"vote {v['id']}: kein Tagesordnungspunkt nennt ihn - "
             f"er fehlt auf der Sitzungsseite")

IDENTITY_WERTE = {"queer", "migrant", "flinta", "disability"}

for m in members:
    profile = m.get("profile") or {}
    for i, mo in enumerate(profile.get("motions", []) or []):
        for pid in mo.get("press", []) or []:
            if pid not in press_ids:
                err(f"member {m['id']} motion[{i}]: press '{pid}' missing")

    # Identitaetsmerkmale sind besondere Kategorien nach Art. 9 DSGVO und
    # brauchen eine belegte Selbstauskunft. Ohne Quelle zeigt die App sie
    # nicht; hier stehen sie als Warnung, damit sie nicht vergessen werden.
    ident = profile.get("identity")
    if ident is None:
        pass
    elif isinstance(ident, list):
        warn(f"member {m['id']}: identity {ident} ohne Quelle - wird nicht angezeigt")
    elif not isinstance(ident, dict):
        err(f"member {m['id']}: identity hat ein unbekanntes Format ({type(ident).__name__})")
    else:
        werte = ident.get("values") or []
        if not werte:
            err(f"member {m['id']}: identity ohne values")
        unbekannt = set(werte) - IDENTITY_WERTE
        if unbekannt:
            err(f"member {m['id']}: identity kennt {sorted(unbekannt)} nicht")
        if not ident.get("source"):
            warn(f"member {m['id']}: identity {werte} ohne Quelle - wird nicht angezeigt")
        elif not ident.get("date"):
            warn(f"member {m['id']}: identity belegt, aber ohne Datum der Auskunft")

# ── Vote totals against body composition ─────────────────────────────────────
def expected_seats(sid):
    if sid.startswith("bpu"):  return 12
    # 11 Stadträte und Vorsitz, so beschlossen am 04.05.2020 (TOP 3.2)
    if sid.startswith("hvfa"): return 12
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
    if not all(isinstance(r.get(k), int) for k in ("yes","no")):
        err(f"vote {v['id']}: anonymous results must have integer yes/no")
    # absent darf fehlen: Beschlussauszuege nennen keine Anwesenheit, und eine
    # 0 waere dort eine Behauptung. Wenn sie dasteht, muss sie eine Zahl sein.
    if "absent" in r and not isinstance(r["absent"], int):
        err(f"vote {v['id']}: anonymous results.absent must be an integer")
    for mid in (v.get("voters") or {}):
        if mid not in member_ids:
            err(f"vote {v['id']}: voters['{mid}'] not a member")

# -- Historie gegen votes[].topicIds --
# Steht ein Votum in der Historie eines Dossiers, soll es dieses Dossier auch
# in topicIds nennen -- sonst zaehlt es dort nicht und erscheint auf der
# Feldseite als themenloser Einzelbeschluss.
vote_by_id = {v['id']: v for v in votes}
for t in topics:
    for h in t.get('history', []):
        v = vote_by_id.get(h.get('voteId'))
        if v is None:
            continue
        if not v.get('topicIds'):
            warn(f"topic {t['id']}: vote {v['id']} steht in der Historie, tragt aber "
                 f"keine topicIds -- zaehlt in keinem Dossier")
        elif t['id'] not in v['topicIds']:
            warn(f"topic {t['id']}: vote {v['id']} steht in der Historie, nennt aber "
                 f"nur {v['topicIds']} -- zaehlt in diesem Dossier nicht")

# ── Member periods ───────────────────────────────────────────────────────────
PARTY_IDS = {p["id"] for p in parties}
ROLLEN = {"councillor", "mayor"}

for m in members:
    mandate = m.get("mandates")
    if not mandate:
        err(f"member {m['id']}: ohne mandates")
        continue
    for i, p in enumerate(mandate):
        if not p.get("from"):
            err(f"member {m['id']} mandates[{i}]: ohne from")
        if p.get("from") and p.get("to") and p["from"] > p["to"]:
            err(f"member {m['id']} mandates[{i}]: from {p['from']} > to {p['to']}")
        if p.get("party") not in PARTY_IDS:
            err(f"member {m['id']} mandates[{i}]: unbekannte Fraktion {p.get('party')!r}")
        if p.get("role") not in ROLLEN:
            err(f"member {m['id']} mandates[{i}]: unbekannte Rolle {p.get('role')!r}")
    # Die Abschnitte stehen in zeitlicher Reihenfolge; sie duerfen sich an
    # ihrer Grenze beruehren (dort gilt der spaetere), aber nicht ueberlappen.
    for a, b in zip(mandate, mandate[1:]):
        if not a.get("to"):
            err(f"member {m['id']}: Abschnitt ohne Ende, aber ein weiterer folgt")
        elif b["from"] < a["to"]:
            warn(f"member {m['id']}: Mandatsabschnitte ueberlappen ({a} / {b})")

    for vorher in m.get("succeeds", []):
        if vorher not in member_ids:
            err(f"member {m['id']}: succeeds '{vorher}' ist kein Mitglied")

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
        datum = session_date(v)
        if not datum: continue
        members_at = seat_members_at(bpu, datum)
        cast = set(v["results"]["yes"] + v["results"]["no"] + v["results"]["absent"])
        # subs not in BPU but voting → conflict only if regular IS in seat list
        session = session_by_id.get(v["sessionId"], {})
        subs = {s["substitute"] for s in (session.get("substitutes") or [])}
        stray = (cast - members_at) - subs
        if stray:
            warn(f"vote {v['id']}: id(s) {stray} cast vote but aren't in BPU composition for {datum}")

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
