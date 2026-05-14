"""
Update members.json:
- Switch from YYYY-MM to YYYY-MM-DD format
- Correct dates per official Stadt-Moosburg dataset (Heinz/Tristl/Wagner/Kaestl ab 2014,
  Grundner ab 2016-01-11, Haberl ab 2018-11-23, John ab 2017-12-11, Marcus ab 2025-03-24,
  Gruber ab 2022-10-10, Gruebl/Hobmaier exact dates, ...)
- Add `periods` array for Marschoun (2014-2020 SPD + 2026+ SPD)
- Add 10 new members from 2014-2020 period (Banner, Bauer, Groeneveld, Hilberg, Kerscher,
  Köhler, Müller, Schaffer, Schweiger, Zitzlsberger)
"""
import json

BASE = "c:/Users/bened/Documents/GitHub/bagruber/council/data"

with open(f"{BASE}/members.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# ── Updates to existing members: {id: {field: newValue, ...}} ────────────────
# Use None to keep existing value; specify only what changes.
# For dates: YYYY-MM-DD. Convention: first day for "from", last day of month for unspecified "to".
UPDATES = {
    "meinelt":        {"from": "2002-05-01", "to": "2020-04-30"},
    "dollinger":      {"from": "2020-05-01", "to": "2026-04-30"},
    "mader":          {"from": "2026-05-01"},
    "linz_karin":     {"from": "2014-05-01"},
    "heinz":          {"from": "2014-05-01"},           # corrected from 2020-05
    "hadersdorfer":   {"from": "2014-05-01"},
    "tristl":         {"from": "2014-05-01"},           # corrected from 2020-05
    "weber":          {"from": "2002-05-01", "to": "2026-04-30"},
    "haberl":         {"from": "2018-11-23", "to": "2026-04-30"},  # corrected from 2020-05
    "kehlringer":     {"from": "2026-05-01"},
    "reither":        {"from": "2026-05-01"},
    "beibl":          {"from": "2020-05-01"},
    "stanglmaier":    {"from": "2000-05-01"},
    "wagner":         {"from": "2014-05-01", "to": "2022-05-31"},  # corrected from 2020-05
    "altenbeck":      {"from": "1991-05-01", "to": "2022-05-31"},
    "von_pressentin": {"from": "2020-05-01", "to": "2026-04-30"},
    "becher_j":       {"from": "2008-05-01", "to": "2026-04-30"},
    "becher_a":       {"from": "2022-06-20", "to": "2026-04-30"},
    "linz_kilian":    {"from": "2022-06-20"},
    "roeck":          {"from": "2026-05-01"},
    "ruemelin":       {"from": "2026-05-01"},
    "grundner":       {"from": "2016-01-11"},           # corrected from 2020-05
    "lauterbach":     {"from": "2020-05-01"},
    "reif":           {"from": "2014-05-01", "to": "2026-04-30"},
    "kieninger":      {"from": "2014-05-01", "to": "2026-04-30"},
    "sixt":           {"from": "2026-05-01"},
    "meier":          {"from": "2026-05-01"},
    "beubl":          {"from": "1989-05-01", "to": "2025-03-24"},
    "pschorr":        {"from": "1972-05-01", "to": "2026-04-30"},
    "marcus":         {"from": "2025-03-24"},           # corrected from 2025-01
    "wittmann":       {"from": "2020-05-01", "to": "2021-10-25"},
    "neumayr":        {"from": "2020-05-01", "to": "2022-01-31"},
    "gruebl":         {"from": "2021-10-25", "to": "2024-10-21"},
    "gruber":         {"from": "2022-10-10", "to": "2026-04-30"},  # corrected from 2022-01
    "hobmaier":       {"from": "2024-10-21", "to": "2026-04-30"},
    "dick":           {"from": "2026-05-01"},
    "sabanovic":      {"from": "2026-05-01"},
    "welter":         {"from": "2020-05-01"},
    "ghadieh":        {"from": "2026-05-01"},
    "kaestl":         {"from": "2014-05-01", "to": "2026-04-30"},  # corrected from 2020-05
    "fincke":         {"from": "2020-05-01", "to": "2026-04-30"},
    "john":           {"from": "2017-12-11", "to": "2023-07-24"},  # corrected from 2020-05
    "strobl":         {"from": "2023-07-24"},
}

# ── Marschoun: periods array (two non-contiguous mandate periods) ────────────
MARSCHOUN_PERIODS = [
    {"from": "2014-05-01", "to": "2020-04-30"},
    {"from": "2026-05-01"}
]

# ── Member to apply roleHistory date precision for dollinger ─────────────────
DOLLINGER_ROLE_HISTORY = [
    {"role": "councillor", "from": "2014-05-01", "to": "2020-04-30"}
]

# ── New members for 2014–2020 period ────────────────────────────────────────
NEW_MEMBERS = [
    # CSU
    {
        "id": "banner", "firstName": "Sibylle", "lastName": "Banner",
        "party": "csu", "role": "councillor",
        "from": "2018-05-14", "to": "2020-04-30",
        "profile": { "identity": ["flinta"] }
    },
    {
        "id": "kerscher", "firstName": "Thomas", "lastName": "Kerscher",
        "party": "csu", "role": "councillor",
        "from": "2014-05-01", "to": "2020-04-30"
    },
    {
        "id": "mueller_a", "firstName": "Andreas", "lastName": "Müller",
        "title": "Dipl. Ing.",
        "party": "csu", "role": "councillor",
        "from": "2014-05-01", "to": "2020-04-30"
    },
    {
        "id": "schaffer", "firstName": "Bernd", "lastName": "Schaffer",
        "party": "csu", "role": "councillor",
        "from": "2014-05-01", "to": "2018-05-14"
    },
    {
        "id": "schweiger", "firstName": "Christian", "lastName": "Schweiger",
        "party": "csu", "role": "councillor",
        "from": "2026-05-01"
    },
    # Grüne
    {
        "id": "bauer", "firstName": "Irene", "lastName": "Bauer",
        "party": "gruene", "role": "councillor",
        "from": "2014-05-01", "to": "2020-04-30",
        "profile": { "identity": ["flinta"] }
    },
    # FW
    {
        "id": "groeneveld", "firstName": "Hinrich", "lastName": "Groeneveld",
        "party": "fw", "role": "councillor",
        "from": "2014-05-01", "to": "2015-12-21"
    },
    # UMB
    {
        "id": "hilberg", "firstName": "Michael", "lastName": "Hilberg",
        "party": "umb", "role": "councillor",
        "from": "2014-05-01", "to": "2018-11-05"
    },
    {
        "id": "koehler", "firstName": "Erwin", "lastName": "Köhler",
        "party": "umb", "role": "councillor",
        "from": "2014-05-01", "to": "2020-04-30",
        "profile": {
            "titles": [
                {"title": "Referent für Wasser- und Abwasserangelegenheiten, Hochwasserschutz",
                 "from": "2014-05-01", "to": "2020-04-30"}
            ]
        }
    },
    # LINKE
    {
        "id": "zitzlsberger", "firstName": "Johann", "lastName": "Zitzlsberger",
        "party": "linke", "role": "councillor",
        "from": "2014-05-01", "to": "2017-12-11"
    },
]

# ── Apply ────────────────────────────────────────────────────────────────────
mmap = {m["id"]: m for m in data["members"]}

for mid, changes in UPDATES.items():
    m = mmap.get(mid)
    if not m:
        print(f"WARN: {mid} not found")
        continue
    for k, v in changes.items():
        m[k] = v

# Marschoun: switch to periods array; keep from/to as outer bounds
marschoun = mmap.get("marschoun")
if marschoun:
    marschoun["from"] = "2014-05-01"
    marschoun["to"]   = None
    marschoun["periods"] = MARSCHOUN_PERIODS

# Dollinger roleHistory
dollinger = mmap.get("dollinger")
if dollinger:
    dollinger["roleHistory"] = DOLLINGER_ROLE_HISTORY

# Add new members
existing_ids = {m["id"] for m in data["members"]}
for nm in NEW_MEMBERS:
    if nm["id"] not in existing_ids:
        # ensure 'to' field shape consistency
        if "to" not in nm:
            nm["to"] = None
        if "profile" not in nm:
            nm["profile"] = {}
        data["members"].append(nm)
        print(f"+ {nm['id']} ({nm['firstName']} {nm['lastName']})")

# Save
with open(f"{BASE}/members.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nDone. Total members: {len(data['members'])}")
