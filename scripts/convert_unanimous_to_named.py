import json

BASE = "c:/Users/bened/Documents/GitHub/bagruber/council/data"

with open(f"{BASE}/votes.json", "r", encoding="utf-8") as f:
    votes = json.load(f)

with open(f"{BASE}/sessions.json", "r", encoding="utf-8") as f:
    sessions = json.load(f)

# ── Member lists ──────────────────────────────────────────────────────────────
# Active until May 2026 (old council), beubl active until 2025-03, marcus from 2025-01
ALL_DEC2024 = [
    "dollinger", "hadersdorfer", "tristl", "weber", "haberl",
    "linz_karin", "heinz",
    "beibl", "stanglmaier", "von_pressentin", "becher_j", "becher_a", "linz_kilian",
    "grundner", "lauterbach", "reif", "kieninger",
    "beubl", "pschorr",   # SPD: beubl still active in Dec 2024
    "gruber", "hobmaier",  # fresh
    "welter",              # AfD
    "kaestl",              # ÖDP
    "fincke",              # FDP
    "strobl",              # Linke
]

# From 2025-03-24: beubl gone, marcus joined
ALL_2025 = [
    "dollinger", "hadersdorfer", "tristl", "weber", "haberl",
    "linz_karin", "heinz",
    "beibl", "stanglmaier", "von_pressentin", "becher_j", "becher_a", "linz_kilian",
    "grundner", "lauterbach", "reif", "kieninger",
    "pschorr", "marcus",   # SPD: marcus replaced beubl
    "gruber", "hobmaier",
    "welter",
    "kaestl",
    "fincke",
    "strobl",
]

def make_named(all_members, absent):
    yes = [m for m in all_members if m not in absent]
    return {"type": "named", "results": {"yes": yes, "no": [], "absent": list(absent)}}

# ── Per-vote conversion specs ─────────────────────────────────────────────────
# Format: vote_id -> (all_members_list, absent_list)
CONVERSIONS = {}

# sr_20241209 – absent: becher_j, heinz, hobmaier, kaestl, kieninger, linz_karin, reif
_absent_1209 = ["becher_j", "heinz", "hobmaier", "kaestl", "kieninger", "linz_karin", "reif"]
for vid in ["sr_20241209_01", "sr_20241209_02", "sr_20241209_03", "sr_20241209_04",
            "sr_20241209_06", "sr_20241209_07", "sr_20241209_08"]:
    CONVERSIONS[vid] = (ALL_DEC2024, _absent_1209)

# sr_20250324 – partial arrivals tracked per vote
# dollinger full absent; becher_a 18:10, linz_kilian 18:15, hobmaier 18:25, kaestl 18:50
CONVERSIONS["sr_20250324_01"] = (ALL_2025, ["dollinger", "becher_a", "linz_kilian", "hobmaier", "kaestl"])
CONVERSIONS["sr_20250324_02"] = (ALL_2025, ["dollinger", "becher_a", "linz_kilian", "hobmaier", "kaestl"])
CONVERSIONS["sr_20250324_03"] = (ALL_2025, ["dollinger", "linz_kilian", "hobmaier", "kaestl"])
CONVERSIONS["sr_20250324_04"] = (ALL_2025, ["dollinger", "kaestl"])
CONVERSIONS["sr_20250324_05"] = (ALL_2025, ["dollinger", "kaestl"])
CONVERSIONS["sr_20250324_06"] = (ALL_2025, ["dollinger", "kaestl"])
CONVERSIONS["sr_20250324_07"] = (ALL_2025, ["dollinger"])

# sr_20251013 – stanglmaier, fincke, von_pressentin, welter full absent
# vote 01: hadersdorfer briefly absent (explicit in protocol)
# vote 02: beibl not yet arrived (arrived 19:20, before vote 4.2 which shows 21 total)
CONVERSIONS["sr_20251013_01"] = (ALL_2025, ["stanglmaier", "fincke", "von_pressentin", "welter", "hadersdorfer"])
CONVERSIONS["sr_20251013_02"] = (ALL_2025, ["stanglmaier", "fincke", "von_pressentin", "welter", "beibl"])

# sr_20251029 – stanglmaier, becher_a, becher_j, heinz, linz_karin, tristl, von_pressentin absent
_absent_1029 = ["stanglmaier", "becher_a", "becher_j", "heinz", "linz_karin", "tristl", "von_pressentin"]
for vid in ["sr_20251029_01", "sr_20251029_02", "sr_20251029_03",
            "sr_20251029_04", "sr_20251029_05", "sr_20251029_09"]:
    CONVERSIONS[vid] = (ALL_2025, _absent_1029)

# sr_20251201 – gruber, grundner, kieninger absent; hobmaier arrived between votes 03 and 05
_absent_1201 = ["gruber", "grundner", "kieninger"]
for vid in ["sr_20251201_01", "sr_20251201_02", "sr_20251201_05",
            "sr_20251201_06", "sr_20251201_07", "sr_20251201_10"]:
    CONVERSIONS[vid] = (ALL_2025, _absent_1201)
# vote 03 (Gehwegausbau): hobmaier arrived after this vote
CONVERSIONS["sr_20251201_03"] = (ALL_2025, ["gruber", "grundner", "kieninger", "hobmaier"])

# sr_20251215 – becher_a, becher_j, fincke, grundner, kieninger, strobl, von_pressentin absent
_absent_1215 = ["becher_a", "becher_j", "fincke", "grundner", "kieninger", "strobl", "von_pressentin"]
for vid in ["sr_20251215_01", "sr_20251215_02", "sr_20251215_03", "sr_20251215_04"]:
    CONVERSIONS[vid] = (ALL_2025, _absent_1215)

# sr_20260112 – becher_a, becher_j, hobmaier, kaestl absent
_absent_0112 = ["becher_a", "becher_j", "hobmaier", "kaestl"]
for vid in ["sr_20260112_01", "sr_20260112_02", "sr_20260112_03", "sr_20260112_04"]:
    CONVERSIONS[vid] = (ALL_2025, _absent_0112)

# sr_20260202 – beibl, heinz, hobmaier absent (22-yes votes only, PDF unreadable)
_absent_0202 = ["beibl", "heinz", "hobmaier"]
for vid in ["sr_20260202_01", "sr_20260202_02", "sr_20260202_03", "sr_20260202_08"]:
    CONVERSIONS[vid] = (ALL_2025, _absent_0202)

# sr_20260223 – becher_a, becher_j, gruber, hadersdorfer, heinz, hobmaier, von_pressentin absent
# (sessions.json missing hobmaier; subagent confirms 18 voters = 25-7)
_absent_0223 = ["becher_a", "becher_j", "gruber", "hadersdorfer", "heinz", "hobmaier", "von_pressentin"]
for vid in ["sr_20260223_02", "sr_20260223_03", "sr_20260223_05"]:
    CONVERSIONS[vid] = (ALL_2025, _absent_0223)

# ── Apply conversions ─────────────────────────────────────────────────────────
converted = 0
vote_map = {v["id"]: v for v in votes}

for vote_id, (all_members, absent) in CONVERSIONS.items():
    if vote_id not in vote_map:
        print(f"WARN: {vote_id} not found in votes.json")
        continue
    vote = vote_map[vote_id]
    if vote["type"] != "anonymous":
        print(f"SKIP: {vote_id} is already type={vote['type']}")
        continue
    if vote["results"]["no"] != 0:
        print(f"SKIP: {vote_id} has no={vote['results']['no']} (not unanimous)")
        continue
    named = make_named(all_members, absent)
    # verify count
    expected_yes = vote["results"]["yes"]
    actual_yes = len(named["results"]["yes"])
    if actual_yes != expected_yes:
        print(f"WARN: {vote_id} expected yes={expected_yes}, got {actual_yes} – check absent list!")
    else:
        vote["type"] = named["type"]
        vote["results"] = named["results"]
        converted += 1
        print(f"OK: {vote_id} → named ({actual_yes} yes, {len(named['results']['absent'])} absent)")

# ── Fix sessions.json absent arrays ──────────────────────────────────────────
session_map = {s["id"]: s for s in sessions}

# sr_20251201: add absent array (missing)
s1201 = session_map.get("sr_20251201")
if s1201 and "absent" not in s1201:
    s1201["absent"] = ["gruber", "grundner", "kieninger"]
    print("sessions: added absent to sr_20251201")

# sr_20260223: add hobmaier (7th absent person confirmed by vote counts)
s0223 = session_map.get("sr_20260223")
if s0223 and "hobmaier" not in s0223.get("absent", []):
    s0223["absent"].append("hobmaier")
    print("sessions: added hobmaier to sr_20260223 absent")

# ── Write ─────────────────────────────────────────────────────────────────────
with open(f"{BASE}/votes.json", "w", encoding="utf-8") as f:
    json.dump(votes, f, ensure_ascii=False, indent=2)

with open(f"{BASE}/sessions.json", "w", encoding="utf-8") as f:
    json.dump(sessions, f, ensure_ascii=False, indent=2)

print(f"\nDone: {converted} votes converted to named type.")
