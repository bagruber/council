"""
Apply Gruber's voting data + Strobl-as-known-dissenter conversions + Windenergie
named-dissenters + press articles + new councillor contacts.
"""
import json
BASE = "c:/Users/bened/Documents/GitHub/bagruber/council/data"

with open(f"{BASE}/votes.json","r",encoding="utf-8") as f: votes = json.load(f)
with open(f"{BASE}/sessions.json","r",encoding="utf-8") as f: sessions = json.load(f)
with open(f"{BASE}/press.json","r",encoding="utf-8") as f: press = json.load(f)
with open(f"{BASE}/members.json","r",encoding="utf-8") as f: members = json.load(f)

vmap = {v["id"]: v for v in votes}
smap = {s["id"]: s for s in sessions}
pmap = {p["id"]: p for p in press}
mmap = {m["id"]: m for m in members["members"]}

# Helper for the 2020-2026 council
ALL_2024 = ["dollinger","hadersdorfer","tristl","weber","haberl","linz_karin","heinz",
            "beibl","stanglmaier","von_pressentin","becher_j","becher_a","linz_kilian",
            "grundner","lauterbach","reif","kieninger","beubl","pschorr",
            "gruebl","gruber","welter","kaestl","fincke","strobl"]
ALL_POST_OCT21 = ["dollinger","hadersdorfer","tristl","weber","haberl","linz_karin","heinz",
                  "beibl","stanglmaier","von_pressentin","becher_j","becher_a","linz_kilian",
                  "grundner","lauterbach","reif","kieninger","beubl","pschorr",
                  "gruber","hobmaier","welter","kaestl","fincke","strobl"]
ALL_POST_MAR2025 = ["dollinger","hadersdorfer","tristl","weber","haberl","linz_karin","heinz",
                    "beibl","stanglmaier","von_pressentin","becher_j","becher_a","linz_kilian",
                    "grundner","lauterbach","reif","kieninger","pschorr","marcus",
                    "gruber","hobmaier","welter","kaestl","fincke","strobl"]

def add_voters(vote_id, voters):
    v = vmap.get(vote_id)
    if not v:
        print(f"  ! {vote_id} not found")
        return
    v.setdefault("voters", {})
    v["voters"].update(voters)
    print(f"  ~ {vote_id}: voters += {voters}")

def convert_named(vote_id, yes, no, absent):
    v = vmap.get(vote_id)
    if not v:
        print(f"  ! {vote_id} not found")
        return
    v["type"] = "named"
    v["results"] = {"yes": list(yes), "no": list(no), "absent": list(absent)}
    if "voters" in v: del v["voters"]
    print(f"  ~ {vote_id} → named ({len(yes)}:{len(no)}:{len(absent)})")

# ── 1. Gruber's votes on anonymous-only sessions (partial voters) ───────────
print("Gruber votes (partial):")
GRUBER_VOTES = {
    "sr_20260202_06":  "yes",   # Tempo 20 Stadtplatz
    "sr_20251110_05":  "yes",   # Kreisverkehr Landshuter
    "sr_20251029_08":  "yes",   # Vereinsförderrichtlinien gesamt
    "bpu_20251006_04": "yes",   # Sudetenlandstr. 28 — Gruber subbed for Hobmaier
    "sr_20250908_06":  "yes",   # Verweigerung Einvernehmen Stadtwaldstraße 9
    "sr_20250728_03":  "yes",   # Abbruchbeschluss Wachbaracken aufgehoben
    "sr_20250728_06":  "yes",   # Stellplatzsatzung Abstufung
    "sr_20250714_08":  "no",    # Parkplatz Alte Polizei
    "sr_20250623_02":  "yes",   # Parkplatz Alte Polizei zurückgestellt
    "bpu_20250522_02": "yes",   # Fußgängerüberweg Sudetenlandstr (sub)
    "bpu_20250522_07": "yes",   # MFH Bahnhofstr. 60 verweigert (sub)
    "bpu_20250522_09": "no",    # MFH Neustadtstr. 17 erteilt (abgelehnt) (sub)
    "sr_20250224_01":  "yes",   # Hallenbadeintritt Kinder (abgelehnt) — Gruber wanted free entry
    "bpu_20250116_02": "yes",   # 3. WE Thalbacher Str. 85 verweigert (sub)
    "bpu_20250116_03": "no",    # Wohnanlage Stadtwaldstr 9 erteilt (abgelehnt) (sub)
    "bpu_20250116_04": "yes",   # Wohnanlage Stadtwaldstr 9 verweigert (sub)
    "sr_20241104_03":  "yes",   # MFH 12 WE Bahnhofstr. 60 Anhörung
    "sr_20241021_03":  "yes",   # Schaffung Jugendreferent
    "sr_20241021_08":  "yes",   # Hebesatz Grundsteuer A 2025
    "sr_20241021_11":  "yes",   # Hallenbad Öffnungszeiten
    "bpu_20240930_03": "no",    # MFH 12 WE Bahnhofstr. 60 erteilt (abgelehnt) (sub) — wait gruber WAS sub for gruebl earlier
    "bpu_20240930_04": "yes",   # MFH 12 WE Bahnhofstr. 60 verweigert
    "sr_20240610_09":  "yes",   # Tempo-30-Zone Wohngebiet
    "sr_20240408_02":  "no",    # Altersteilzeit Verzicht (abgelehnt)
    "sr_20240408_03":  "yes",   # Altersteilzeit gesetzlich
    "bpu_20240314_05": "no",    # Arbeitnehmerwohnheim erteilt (abgelehnt) (sub)
    "bpu_20240314_06": "yes",   # Arbeitnehmerwohnheim verweigert (sub)
}
for vid, status in GRUBER_VOTES.items():
    add_voters(vid, {"gruber": status})

# ── 2. Strobl-only-dissenter votes — fully convertible ──────────────────────
print("\nStrobl-pattern (Strobl = lone dissenter):")

# sr_20240304_04 Wahlhelferbonus 1:22:2  (Strobl yes, others no, session_absent=[beubl,weber])
convert_named("sr_20240304_04",
    yes=["strobl"],
    no=[m for m in ALL_2024 if m not in ("strobl","beubl","weber")],
    absent=["beubl","weber"])

# sr_20240304_05 Erfrischungsgeld 40€ 23:0:2 — unanimous (all 23 present voted yes)
convert_named("sr_20240304_05",
    yes=[m for m in ALL_2024 if m not in ("beubl","weber")],
    no=[],
    absent=["beubl","weber"])

# sr_20240318_05 Verkaufsoffener Sonntag 2024-04 21:1:3 (session_absent=[beubl,von_pressentin,weber])
convert_named("sr_20240318_05",
    yes=[m for m in ALL_2024 if m not in ("strobl","beubl","von_pressentin","weber")],
    no=["strobl"],
    absent=["beubl","von_pressentin","weber"])

# sr_20240610_06 Verwaltungsgebühr 10€ 17:1:7 (session_absent matches 7)
SR_0610_ABS = ["hadersdorfer","stanglmaier","becher_a","becher_j","beubl","heinz","welter"]
convert_named("sr_20240610_06",
    yes=[m for m in ALL_2024 if m not in (SR_0610_ABS + ["strobl"])],
    no=["strobl"],
    absent=SR_0610_ABS)

# sr_20250324_08 Verkaufsoffener Sonntag 2025-04 23:1:1 (session_absent=[dollinger])
convert_named("sr_20250324_08",
    yes=[m for m in ALL_POST_MAR2025 if m not in ("strobl","dollinger")],
    no=["strobl"],
    absent=["dollinger"])

# sr_20250922_10 Sonntagsöffnung 2025-09 19:1:5 (session_absent=[hadersdorfer,heinz,von_pressentin,weber,welter])
SR_0922_ABS = ["hadersdorfer","heinz","von_pressentin","weber","welter"]
convert_named("sr_20250922_10",
    yes=[m for m in ALL_POST_MAR2025 if m not in (SR_0922_ABS + ["strobl"])],
    no=["strobl"],
    absent=SR_0922_ABS)

# ── 3. Partial-known dissenter votes (Strobl) ───────────────────────────────
print("\nStrobl-pattern (partial):")
# sr_20240923_06 Sonntag 2024-10: Strobl no, but 1 extra brief absent unknown
add_voters("sr_20240923_06", {"strobl": "no"})

# ── 4. Windenergie partial ──────────────────────────────────────────────────
print("\nWindenergie:")
add_voters("sr_20240506_02", {"tristl":"no","lauterbach":"no","haberl":"no","welter":"no"})

# ── 5. Press articles ───────────────────────────────────────────────────────
print("\nPress articles:")
NEW_PRESS = [
    {
        "id": "sz_2024-03_erfrischungsgeld",
        "media": "sz",
        "date": "2024-03-04",
        "title": "Erfrischungsgeld für Wahlhelfer",
        "url": "https://www.sueddeutsche.de/muenchen/freising/moosburg-europawahl-wahlhelfer-erfrischungsgeld-zusatzleistungen-1.6453020"
    },
    {
        "id": "merkur_2024-06_kitagebuehren",
        "media": "merkur",
        "date": "2024-06-10",
        "title": "Kinderbetreuung in Moosburg wird teurer",
        "url": "https://www.merkur.de/lokales/freising/moosburg-ort29088/kitagebuehren-kinderbetreuung-in-moosburg-wird-teurer-buergermeister-ich-denke-das-ist-zumutbar-93123706.html"
    },
    {
        "id": "sz_2024-06_kitas-arbeitsmarktzulage",
        "media": "sz",
        "date": "2024-06-10",
        "title": "Kitas, Personalgewinnung, Gebührenerhöhung",
        "url": "https://www.sueddeutsche.de/muenchen/freising/moosburg-stadtrat-kitas-personalgewinnung-arbeitsmarktzulage-kindergartengebuehren-erhoehung-lux.9MD2NeWAwJXXzbYHDJmd8D"
    },
    {
        "id": "sz_2024-05_windenergie",
        "media": "sz",
        "date": "2024-05-06",
        "title": "Windenergie-Vorrangflächen: Bürgergenossenschaft für Kirchamper",
        "url": "https://www.sueddeutsche.de/muenchen/freising/moosburg-windenergie-vorrangflaechen-kirchamper-windrad-buerger-energiegenossenschaft-regionalplan-muenchen-1.7012405"
    }
]
for p in NEW_PRESS:
    if p["id"] not in pmap:
        press.append(p)
        pmap[p["id"]] = p
        print(f"  + {p['id']}")

# Link press to agenda items in sessions.json
def link_press(session_id, agenda_number, press_ids):
    s = smap.get(session_id)
    if not s: return
    for item in s.get("agenda", []):
        if str(item.get("number")) == str(agenda_number):
            existing = item.setdefault("press", [])
            for pid in press_ids:
                if pid not in existing: existing.append(pid)
            print(f"  ~ {session_id} item {agenda_number} press += {press_ids}")
            return

link_press("sr_20240304", "5.2", ["sz_2024-03_erfrischungsgeld"])
link_press("sr_20240610", "5.5", ["merkur_2024-06_kitagebuehren", "sz_2024-06_kitas-arbeitsmarktzulage"])
link_press("sr_20240610", "4.1", ["sz_2024-06_kitas-arbeitsmarktzulage"])
link_press("sr_20240506", 4,    ["sz_2024-05_windenergie"])

# ── 6. New councillor contact data ──────────────────────────────────────────
print("\nNew councillor contacts:")
CONTACTS = {
    "ghadieh":    {"email": "praxis@umc-international.de"},
    "kehlringer": {"email": "lorena.kehlringer@gmx.de", "instagram": "@lorenakehlringer"},
    "marschoun":  {"email": "christoph.marschoun@montessori-freising.de"},
    "meier":      {"email": "meier@bausanierung-meier.de"},
    "reither":    {"email": "reither-stadtrat@web.de"},
    "roeck":      {"email": "matthias.roeck@gruene-moosburg.de", "instagram": "@roecknroller"},
    "ruemelin":   {"email": "ramona.ruemelin@gruene-moosburg.de", "instagram": "@ramona_ruemelin"},
    "schweiger":  {"email": "christian.schweiger@schweiger-feldkirchen.de"},
    "sixt":       {"email": "sepp.sixt@googlemail.com", "instagram": "@josef_sixt96"},
}
for mid, c in CONTACTS.items():
    m = mmap.get(mid)
    if not m: continue
    m.setdefault("profile", {}).setdefault("contact", {}).update(c)
    print(f"  ~ {mid}: {list(c.keys())}")

# ── Save ─────────────────────────────────────────────────────────────────────
with open(f"{BASE}/votes.json","w",encoding="utf-8") as f: json.dump(votes, f, ensure_ascii=False, indent=2)
with open(f"{BASE}/sessions.json","w",encoding="utf-8") as f: json.dump(sessions, f, ensure_ascii=False, indent=2)
with open(f"{BASE}/press.json","w",encoding="utf-8") as f: json.dump(press, f, ensure_ascii=False, indent=2)
with open(f"{BASE}/members.json","w",encoding="utf-8") as f: json.dump(members, f, ensure_ascii=False, indent=2)
print("\nSaved.")
