"""Big update:
1. Fix bpu_20251208: correct vote totals (sum to 12), convert to named.
2. Categories: replace tags.json with new 10-category structure (icon + colour).
3. Update topics with multi-category tagging.
4. Add 2026+ committee compositions as seatConfigs (multi-period structure).
"""
import json

BASE = "c:/Users/bened/Documents/GitHub/bagruber/council/data"

# ============================================================================
# 1. bpu_20251208: correct + convert to named
# ============================================================================
with open(f"{BASE}/votes.json","r",encoding="utf-8") as f: votes = json.load(f)

YES_1208 = ["dollinger", "hadersdorfer", "stanglmaier", "linz_karin", "tristl",
            "marcus", "kieninger", "reif", "beibl", "linz_kilian"]
# Wait — re-check with agent data:
# Present voting: dollinger, hadersdorfer, stanglmaier, beibl, linz_kilian, marcus, reif, tristl (8)
# Subs present but not voting: gruber, lauterbach, weber
# Absent (no sub voting): hobmaier, kieninger, linz_karin, welter
# So named conversion: yes = 8 voters; absent = 4 regulars (hobmaier, kieninger, linz_karin, welter)
YES_1208 = ["dollinger", "hadersdorfer", "stanglmaier", "beibl", "linz_kilian",
            "marcus", "reif", "tristl"]
ABS_1208 = ["hobmaier", "kieninger", "linz_karin", "welter"]

for v in votes:
    if v['id'].startswith('bpu_20251208_'):
        v['type'] = 'named'
        v['results'] = {"yes": YES_1208, "no": [], "absent": ABS_1208}
        print(f"~ {v['id']} → named (8:0:4)")

with open(f"{BASE}/votes.json","w",encoding="utf-8") as f: json.dump(votes, f, ensure_ascii=False, indent=2)

# Also fix sessions.json — add absent list to bpu_20251208 for clarity (already has substitutes)
with open(f"{BASE}/sessions.json","r",encoding="utf-8") as f: sessions = json.load(f)
for s in sessions:
    if s['id'] == 'bpu_20251208':
        s['absent'] = ABS_1208
        print(f"~ session bpu_20251208 absent list set: {ABS_1208}")
with open(f"{BASE}/sessions.json","w",encoding="utf-8") as f: json.dump(sessions, f, ensure_ascii=False, indent=2)

# ============================================================================
# 2. Categories (replaces tags)
# ============================================================================
CATEGORIES = [
    {"id": "mobility",       "name": "Mobilität & Verkehr",       "icon": "commute",              "color": "#5B9BD5"},
    {"id": "building",       "name": "Bau & Planung",             "icon": "architecture",         "color": "#8B7355"},
    {"id": "sports",         "name": "Sport & Vereine",           "icon": "sports",               "color": "#9B59B6"},
    {"id": "culture",        "name": "Geschichte & Kultur",       "icon": "museum",               "color": "#C2185B"},
    {"id": "environment",    "name": "Umwelt, Natur & Erholung",  "icon": "park",                 "color": "#4CAF50"},
    {"id": "education",      "name": "Bildung & Erziehung",       "icon": "school",               "color": "#F57C00"},
    {"id": "social",         "name": "Gesundheit & Soziales",     "icon": "volunteer_activism",   "color": "#E91E63"},
    {"id": "budget",         "name": "Haushalt & Finanzen",       "icon": "account_balance",      "color": "#00B4D8"},
    {"id": "economy",        "name": "Wirtschaft & Marketing",    "icon": "storefront",           "color": "#F9A825"},
    {"id": "infrastructure", "name": "Sicherheit & Infrastruktur","icon": "shield",               "color": "#455A64"},
]
with open(f"{BASE}/tags.json","w",encoding="utf-8") as f:
    json.dump(CATEGORIES, f, ensure_ascii=False, indent=2)
print(f"~ tags.json replaced with {len(CATEGORIES)} categories")

# ============================================================================
# 3. Topic categories (multi-tagging)
# ============================================================================
TOPIC_CATEGORIES = {
    "t1":  ["sports", "building"],
    "t2":  ["building", "infrastructure"],
    "t3":  ["mobility"],
    "t4":  ["mobility"],
    "t5":  ["building"],
    "t6":  ["education", "building"],
    "t7":  ["budget"],
    "t8":  ["mobility", "education"],
    "t9":  ["mobility"],
    "t10": ["economy"],
    "t11": ["culture"],
    "t12": ["sports"],
    "t13": ["building"],
    "t14": ["culture"],
    "t15": ["infrastructure", "environment"],
    "t16": ["sports"],
    "t17": ["building"],
    "t18": ["building", "economy"],
    "t19": ["sports", "building"],
}

with open(f"{BASE}/topics.json","r",encoding="utf-8") as f: topics = json.load(f)
for t in topics:
    new = TOPIC_CATEGORIES.get(t["id"])
    if new:
        t["tags"] = new
        print(f"~ {t['id']}: tags = {new}")
with open(f"{BASE}/topics.json","w",encoding="utf-8") as f: json.dump(topics, f, ensure_ascii=False, indent=2)

# ============================================================================
# 4. 2026+ Committee compositions (seatConfigs)
# ============================================================================
# Structure: bodies[i].seatConfigs = [{from, to, chair, vicechairs, seats}]
# Existing top-level chair/vicechairs/seats represent the 2020-2026 config.

with open(f"{BASE}/members.json","r",encoding="utf-8") as f: members_data = json.load(f)
bodies = members_data["bodies"]

# Order seats per Moosburg convention: CSU → SPD → AfD → Linke → fresh → FW → Grüne
# (in array order = BM-links to BM-rechts)
def party_of(member_id):
    for m in members_data["members"]:
        if m["id"] == member_id:
            return m.get("party")
    return "?"

PARTY_ORDER = ["csu", "spd", "afd", "linke", "fresh", "fw", "gruene"]

def sort_by_party(seat_list):
    return sorted(seat_list, key=lambda s: PARTY_ORDER.index(party_of(s["member"])) if party_of(s["member"]) in PARTY_ORDER else 99)

# Capture existing config as the 2020-2026 entry
def capture_existing(body):
    return {
        "from": "2020-05-01", "to": "2026-04-30",
        "chair":      body.get("chair"),
        "vicechairs": body.get("vicechairs", []),
        "seats":      body.get("seats", []),
        **({"chairSub": body["chairSub"]} if body.get("chairSub") else {}),
    }

# BPU 2026+ ----------------------------------------------------------
BPU_2026_SEATS = [
    # CSU 4
    {"member": "linz_karin"},
    {"member": "tristl"},
    {"member": "schweiger"},
    # SPD 1
    {"member": "marschoun", "sub": "marcus"},   # SPD: gegenseitig
    # AfD 1
    {"member": "welter", "sub": "ghadieh"},     # AfD: gegenseitig
    # fresh 1
    {"member": "sabanovic", "sub": "dick"},     # fresh: gegenseitig (except PA)
    # FW 2
    {"member": "sixt"},
    {"member": "meier"},
    # Grüne 1
    {"member": "beibl"},
]
BPU_2026_CONFIG = {
    "from": "2026-05-01",
    "chair": "mader",
    "vicechairs": [
        {"member": "hadersdorfer"},   # 2. BM — assumed (TBD)
        {"member": "stanglmaier"},    # 3. BM — assumed (TBD)
    ],
    "seats": BPU_2026_SEATS,
}

# HVFA 2026+ ---------------------------------------------------------
HVFA_2026_SEATS_RAW = ["heinz", "reither", "kehlringer", "tristl",
                       "marcus", "ghadieh", "dick",
                       "grundner", "lauterbach",
                       "linz_kilian", "ruemelin"]
def to_seat(mid):
    seat = {"member": mid}
    p = party_of(mid)
    # subs known
    if p == "spd": seat["sub"] = "marschoun" if mid == "marcus" else "marcus"
    elif p == "afd": seat["sub"] = "welter" if mid == "ghadieh" else "ghadieh"
    elif p == "fresh": seat["sub"] = "sabanovic" if mid == "dick" else "dick"
    return seat

HVFA_2026_CONFIG = {
    "from": "2026-05-01",
    "chair": "mader",
    "seats": [to_seat(m) for m in HVFA_2026_SEATS_RAW],
}

# PA 2026+ -----------------------------------------------------------
# Personalausschuss: Reither, Schweiger, Röck, Meier, Dick (5)
# Fresh sub in PA = Strobl (exception)
PA_2026_CONFIG = {
    "from": "2026-05-01",
    "chair": "mader",
    "seats": [
        {"member": "reither"},
        {"member": "schweiger"},
        {"member": "dick", "sub": "strobl"},   # fresh sub = strobl (PA exception)
        {"member": "meier"},
        {"member": "roeck"},
    ],
}

# RPA 2026+ ----------------------------------------------------------
# Members: Tristl, Linz Karin, Beibl, Meier, Sabanovic (5)
# Chair: TBD (Lauterbach was old chair but not in member list — needs confirmation)
RPA_2026_CONFIG = {
    "from": "2026-05-01",
    "chair": None,   # TBD — Lauterbach was previous chair
    "seats": [
        {"member": "linz_karin"},
        {"member": "tristl"},
        {"member": "sabanovic", "sub": "dick"},   # fresh: gegenseitig
        {"member": "meier"},
        {"member": "beibl"},
    ],
}

# Apply 2026+ configs
NEW_CONFIGS = {
    "bpu":  BPU_2026_CONFIG,
    "hvfa": HVFA_2026_CONFIG,
    "pa":   PA_2026_CONFIG,
    "rpa":  RPA_2026_CONFIG,
}

for body in bodies:
    bid = body["id"]
    if bid in NEW_CONFIGS:
        existing = capture_existing(body)
        new = NEW_CONFIGS[bid]
        # sort new seats per party order
        new["seats"] = sort_by_party(new["seats"])
        body["seatConfigs"] = [existing, new]
        # also replace top-level fields with the new (current) period
        body["chair"]      = new.get("chair")
        body["vicechairs"] = new.get("vicechairs", [])
        body["seats"]      = new["seats"]
        if "chairSub" in new: body["chairSub"] = new["chairSub"]
        elif "chairSub" in body: del body["chairSub"]
        print(f"~ {bid}: seatConfigs added; current period set to 2026+")

with open(f"{BASE}/members.json","w",encoding="utf-8") as f: json.dump(members_data, f, ensure_ascii=False, indent=2)

print("\nDone.")
