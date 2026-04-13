import json

BASE = "c:/Users/bened/Documents/GitHub/bagruber/council/data"

# ── Member helpers ────────────────────────────────────────────────────────────
ALL_2025 = [
    "dollinger", "hadersdorfer", "tristl", "weber", "haberl",
    "linz_karin", "heinz",
    "beibl", "stanglmaier", "von_pressentin", "becher_j", "becher_a", "linz_kilian",
    "grundner", "lauterbach", "reif", "kieninger",
    "pschorr", "marcus",
    "gruber", "hobmaier",
    "welter", "kaestl", "fincke", "strobl",
]

def yes_list(absent):
    return [m for m in ALL_2025 if m not in absent]

# ── Sessions ──────────────────────────────────────────────────────────────────
new_sessions = [
    {
        "id": "sr_20250714",
        "date": "2025-07-14",
        "type": "stadtrat",
        "title": "10. Stadtratssitzung – Juli 2025",
        "absent": ["hobmaier", "reif"],
        "agenda": [
            {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
            {"number": 2, "title": "Bürgerfragen gem. § 27 Abs. 2 GeschO/StR", "type": "formal"},
            {"number": 3, "title": "Genehmigung der öffentlichen Niederschriften (StR 12.05. und 02.06.2025)",
             "voteId": "sr_20250714_01"},
            {"number": 4, "title": "Sanierungsgebiet Innenstadt–Bahnhof – Beschlussfassung vertagt",
             "topicId": "t13", "type": "discussion"},
            {"number": "5a", "title": "Grundschule – Klimatisierung (abgelehnt 10:13)",
             "topicId": "t6", "voteId": "sr_20250714_02"},
            {"number": "5b", "title": "Grundschule – Dachbegrünung (abgelehnt 5:18)",
             "topicId": "t6", "voteId": "sr_20250714_03"},
            {"number": "5c", "title": "Grundschule – Tiefgarage",
             "topicId": "t6", "voteId": "sr_20250714_04"},
            {"number": "5d", "title": "Grundschule – Campus-Vernetzung Variante 2",
             "topicId": "t6", "voteId": "sr_20250714_05"},
            {"number": "5e", "title": "Grundschule – Rückbau Bühnentechnik",
             "topicId": "t6", "voteId": "sr_20250714_06"},
            {"number": 5, "title": "Erweiterung und Generalsanierung Theresia-Gerhardinger-Grundschule – Förderantrag",
             "topicId": "t6", "voteId": "sr_20250714_07"},
            {"number": 6, "title": "Sanierung Parkplatz Alte Polizei",
             "voteId": "sr_20250714_08"},
            {"number": 7, "title": "Anfragen", "type": "formal"},
        ]
    },
    {
        "id": "sr_20250728",
        "date": "2025-07-28",
        "type": "stadtrat",
        "title": "11. Stadtratssitzung – Juli 2025",
        "absent": ["stanglmaier", "becher_a"],
        "agenda": [
            {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
            {"number": 2, "title": "Bürgerfragen gem. § 27 Abs. 2 GeschO/StR", "type": "formal"},
            {"number": 3, "title": "Genehmigung der öffentlichen Niederschrift (StR 23.06.2025)",
             "voteId": "sr_20250728_01"},
            {"number": 4, "title": "Umrüstung Straßenbeleuchtung auf LED",
             "voteId": "sr_20250728_02"},
            {"number": 5, "title": "Rücknahme Abbruchbeschluss Wachbaracken Schlesierstraße (2012)",
             "topicId": "t14", "voteId": "sr_20250728_03"},
            {"number": "6.1", "title": "Kläranlage Moosburg GmbH – Jahresabschluss 2024",
             "voteId": "sr_20250728_04"},
            {"number": "6.2", "title": "Kläranlage Moosburg GmbH – Entlastung Aufsichtsrat 2024",
             "voteId": "sr_20250728_05"},
            {"number": "7a", "title": "Stellplatzsatzung – Abstufung nach Wohnungsgröße",
             "voteId": "sr_20250728_06"},
            {"number": 7, "title": "1. Änderung der Stellplatzsatzung",
             "voteId": "sr_20250728_07"},
            {"number": 8, "title": "Satzung Spielplatzpflicht für Wohngebäude",
             "voteId": "sr_20250728_08"},
            {"number": 9, "title": "Wasserrecht – Antrag Stadtwerke München",
             "voteId": "sr_20250728_09"},
            {"number": 10, "title": "Bahnübergang Unterreit/Reiteraustraße – Schließung",
             "voteId": "sr_20250728_10"},
            {"number": 11, "title": "Anfragen", "type": "formal"},
        ]
    }
]

# ── Votes ─────────────────────────────────────────────────────────────────────
_absent_0714 = ["hobmaier", "reif"]
_absent_0714_early = ["hobmaier", "reif", "haberl", "kaestl", "strobl"]
_absent_0728 = ["stanglmaier", "becher_a"]

new_votes = [
    # ── sr_20250714 ──────────────────────────────────────────────────────────
    {
        "id": "sr_20250714_01",
        "sessionId": "sr_20250714",
        "topicId": None,
        "date": "2025-07-14",
        "title": "Genehmigung Niederschriften StR 12.05./02.06.2025",
        "text": "Der Stadtrat genehmigt die öffentlichen Teile der Niederschriften der Stadtratssitzungen vom 12.05.2025 und 02.06.2025.",
        "type": "named",
        "results": {
            "yes": yes_list(_absent_0714_early),
            "no": [],
            "absent": _absent_0714_early
        }
    },
    {
        "id": "sr_20250714_02",
        "sessionId": "sr_20250714",
        "topicId": "t6",
        "date": "2025-07-14",
        "title": "Grundschule – Klimatisierung abgelehnt",
        "text": "Der Antrag, die Grundschule mit einer zentralen Klimatisierungsanlage auszustatten, wird abgelehnt.",
        "type": "anonymous",
        "result": "rejected",
        "results": {"yes": 10, "no": 13, "absent": 2}
    },
    {
        "id": "sr_20250714_03",
        "sessionId": "sr_20250714",
        "topicId": "t6",
        "date": "2025-07-14",
        "title": "Grundschule – Dachbegrünung abgelehnt",
        "text": "Der Antrag, eine Dachbegrünung als Kosteneinsparmaßnahme vorzusehen, wird abgelehnt.",
        "type": "anonymous",
        "result": "rejected",
        "results": {"yes": 5, "no": 18, "absent": 2}
    },
    {
        "id": "sr_20250714_04",
        "sessionId": "sr_20250714",
        "topicId": "t6",
        "date": "2025-07-14",
        "title": "Grundschule – Tiefgarage beschlossen",
        "text": "Der Stadtrat beschließt, eine Tiefgarage im Rahmen der Schulerweiterung vorzusehen.",
        "type": "named",
        "results": {
            "yes": yes_list(_absent_0714),
            "no": [],
            "absent": _absent_0714
        }
    },
    {
        "id": "sr_20250714_05",
        "sessionId": "sr_20250714",
        "topicId": "t6",
        "date": "2025-07-14",
        "title": "Grundschule – Campus-Vernetzung Variante 2",
        "text": "Der Stadtrat beschließt die Umsetzung der Campus-Vernetzung nach Variante 2.",
        "type": "anonymous",
        "results": {"yes": 21, "no": 2, "absent": 2}
    },
    {
        "id": "sr_20250714_06",
        "sessionId": "sr_20250714",
        "topicId": "t6",
        "date": "2025-07-14",
        "title": "Grundschule – Rückbau Bühnentechnik",
        "text": "Der Stadtrat beschließt den Rückbau der vorhandenen Bühnentechnik als Kosteneinsparmaßnahme.",
        "type": "named",
        "results": {
            "yes": yes_list(_absent_0714),
            "no": [],
            "absent": _absent_0714
        }
    },
    {
        "id": "sr_20250714_07",
        "sessionId": "sr_20250714",
        "topicId": "t6",
        "date": "2025-07-14",
        "title": "Grundschule – Kostenberechnung und Förderantrag",
        "text": "Der Stadtrat nimmt die Kostenberechnung für die Erweiterung und Generalsanierung der Theresia-Gerhardinger-Grundschule zustimmend zur Kenntnis. Die Verwaltung wird ermächtigt, den Förderantrag bei der Regierung von Oberbayern zu stellen.",
        "type": "named",
        "results": {
            "yes": yes_list(_absent_0714),
            "no": [],
            "absent": _absent_0714
        }
    },
    {
        "id": "sr_20250714_08",
        "sessionId": "sr_20250714",
        "topicId": None,
        "date": "2025-07-14",
        "title": "Sanierung Parkplatz Alte Polizei",
        "text": "Der Stadtrat beschließt die Sanierung des Parkplatzes Alte Polizei mit einem Kostenrahmen von 45.000 €. Die Maßnahme soll im Juli 2025 umgesetzt werden.",
        "type": "anonymous",
        "results": {"yes": 19, "no": 3, "absent": 3}
    },

    # ── sr_20250728 ──────────────────────────────────────────────────────────
    {
        "id": "sr_20250728_01",
        "sessionId": "sr_20250728",
        "topicId": None,
        "date": "2025-07-28",
        "title": "Genehmigung Niederschrift StR 23.06.2025",
        "text": "Der Stadtrat genehmigt den öffentlichen Teil der Niederschrift der Stadtratssitzung vom 23.06.2025.",
        "type": "anonymous",
        "results": {"yes": 20, "no": 0, "absent": 5}
    },
    {
        "id": "sr_20250728_02",
        "sessionId": "sr_20250728",
        "topicId": None,
        "date": "2025-07-28",
        "title": "Umrüstung Straßenbeleuchtung auf LED",
        "text": "Der Stadtrat nimmt den aktuellen Stand der LED-Umrüstung zur Kenntnis. Die Verwaltung wird beauftragt, die Ausschreibungsunterlagen bis Ende 2025 vorzubereiten; die Umsetzung ist für 2026 vorgesehen.",
        "type": "anonymous",
        "results": {"yes": 21, "no": 0, "absent": 4}
    },
    {
        "id": "sr_20250728_03",
        "sessionId": "sr_20250728",
        "topicId": "t14",
        "date": "2025-07-28",
        "title": "Abbruchbeschluss Wachbaracken aufgehoben",
        "text": "Der Stadtrat hebt den Beschluss vom 10.12.2012 zum Abbruch der Wachbaracken an der Schlesierstraße 3 und 5 auf. Stattdessen soll eine denkmalgerechte Sanierung und Erhaltung angestrebt werden. Ein Nutzungskonzept wird erarbeitet.",
        "type": "anonymous",
        "results": {"yes": 19, "no": 1, "absent": 5}
    },
    {
        "id": "sr_20250728_04",
        "sessionId": "sr_20250728",
        "topicId": None,
        "date": "2025-07-28",
        "title": "Kläranlage GmbH – Jahresabschluss 2024",
        "text": "Der Stadtrat stellt den Jahresabschluss 2024 der Kläranlage Moosburg GmbH fest. Der Jahresüberschuss in Höhe von 218.841,06 € wird auf neue Rechnung vorgetragen; die Gewinnrücklage beträgt nunmehr 2.146.081,45 €.",
        "type": "anonymous",
        "results": {"yes": 22, "no": 0, "absent": 3}
    },
    {
        "id": "sr_20250728_05",
        "sessionId": "sr_20250728",
        "topicId": None,
        "date": "2025-07-28",
        "title": "Kläranlage GmbH – Entlastung Aufsichtsrat 2024",
        "text": "Der Stadtrat erteilt dem Aufsichtsrat der Kläranlage Moosburg GmbH für das Geschäftsjahr 2024 Entlastung. Die Aufsichtsratsmitglieder (Dollinger, Weber, Haberl, Reif, Hobmaier) nehmen an der Abstimmung nicht teil.",
        "type": "anonymous",
        "results": {"yes": 17, "no": 0, "absent": 8}
    },
    {
        "id": "sr_20250728_06",
        "sessionId": "sr_20250728",
        "topicId": None,
        "date": "2025-07-28",
        "title": "Stellplatzsatzung – Abstufung nach Wohnungsgröße",
        "text": "Der Stadtrat beschließt die Aufnahme einer Abstufung der Stellplatzpflicht nach Wohnungsgröße in die Satzung: bis 40 m² = 1,2 Stellplätze; 40–100 m² = 1,8; über 100 m² = 2,0.",
        "type": "anonymous",
        "results": {"yes": 22, "no": 1, "absent": 2}
    },
    {
        "id": "sr_20250728_07",
        "sessionId": "sr_20250728",
        "topicId": None,
        "date": "2025-07-28",
        "title": "1. Änderung der Stellplatzsatzung",
        "text": "Der Stadtrat beschließt die 1. Änderung der Stellplatzsatzung mit der beschlossenen Abstufung der Stellplatzpflicht nach Wohnungsgröße.",
        "type": "named",
        "results": {
            "yes": yes_list(_absent_0728),
            "no": [],
            "absent": list(_absent_0728)
        }
    },
    {
        "id": "sr_20250728_08",
        "sessionId": "sr_20250728",
        "topicId": None,
        "date": "2025-07-28",
        "title": "Satzung Spielplatzpflicht für Wohngebäude",
        "text": "Der Stadtrat erlässt die Satzung zur Einführung einer Pflicht zum Nachweis eines Spielplatzes für Kinder bei neuen Wohngebäuden. Die Satzung tritt am 01.10.2025 in Kraft.",
        "type": "named",
        "results": {
            "yes": yes_list(_absent_0728),
            "no": [],
            "absent": list(_absent_0728)
        }
    },
    {
        "id": "sr_20250728_09",
        "sessionId": "sr_20250728",
        "topicId": None,
        "date": "2025-07-28",
        "title": "Wasserrecht – Uppenbornwerke Kanalsanierung",
        "text": "Der Stadtrat stimmt dem wasserrechtlichen Planfeststellungsverfahren der Stadtwerke München für die Sanierung des Uppenbornwerkes zu. Für das Moosburger Stadtgebiet werden keine Einwände erhoben.",
        "type": "named",
        "results": {
            "yes": yes_list(_absent_0728),
            "no": [],
            "absent": list(_absent_0728)
        }
    },
    {
        "id": "sr_20250728_10",
        "sessionId": "sr_20250728",
        "topicId": None,
        "date": "2025-07-28",
        "title": "Bahnübergang Unterreit/Reiteraustraße",
        "text": "Der Stadtrat bestätigt die Notwendigkeit des Bahnübergangs Unterreit/Reiteraustraße und fordert die Deutsche Bahn auf, die erforderlichen Instandhaltungsmaßnahmen durchzuführen, um eine Schließung zu verhindern.",
        "type": "named",
        "results": {
            "yes": yes_list(_absent_0728),
            "no": [],
            "absent": list(_absent_0728)
        }
    },
]

# ── Load and extend sessions ──────────────────────────────────────────────────
with open(f"{BASE}/sessions.json", "r", encoding="utf-8") as f:
    sessions = json.load(f)

existing_ids = {s["id"] for s in sessions}
added_sessions = 0
for s in new_sessions:
    if s["id"] not in existing_ids:
        sessions.append(s)
        added_sessions += 1
        print(f"session added: {s['id']}")

with open(f"{BASE}/sessions.json", "w", encoding="utf-8") as f:
    json.dump(sessions, f, ensure_ascii=False, indent=2)

# ── Load and extend votes ─────────────────────────────────────────────────────
with open(f"{BASE}/votes.json", "r", encoding="utf-8") as f:
    votes = json.load(f)

existing_vids = {v["id"] for v in votes}
added_votes = 0
for v in new_votes:
    if v["id"] not in existing_vids:
        votes.append(v)
        added_votes += 1

with open(f"{BASE}/votes.json", "w", encoding="utf-8") as f:
    json.dump(votes, f, ensure_ascii=False, indent=2)
print(f"votes added: {added_votes}")

# ── Update topics ─────────────────────────────────────────────────────────────
with open(f"{BASE}/topics.json", "r", encoding="utf-8") as f:
    topics = json.load(f)

topic_map = {t["id"]: t for t in topics}

# t6: Grundschule – add 2025-07-14 entry before the December entries
t6 = topic_map.get("t6")
if t6:
    entry_0714 = {
        "date": "2025-07-14",
        "type": "vote",
        "title": "Kostenberechnung und Förderantrag genehmigt",
        "text": (
            "Der Stadtrat nimmt die Kostenberechnung zustimmend zur Kenntnis. Zur Kosteneinsparung werden "
            "Klimatisierung (10:13) und Dachbegrünung (5:18) abgelehnt; Tiefgarage (23:0), "
            "Campus-Vernetzung Variante 2 (21:2) und Rückbau der Bühnentechnik (23:0) werden beschlossen. "
            "Die Verwaltung wird ermächtigt, den Förderantrag bei der Regierung von Oberbayern zu stellen."
        ),
        "sessionId": "sr_20250714",
        "voteId": "sr_20250714_07"
    }
    # Insert chronologically: after any entry < 2025-07-15, before entries >= 2025-07-15
    dates = [e["date"] for e in t6["history"]]
    if "2025-07-14" not in dates:
        inserted = False
        for i, e in enumerate(t6["history"]):
            if e["date"] >= "2025-07-15":
                t6["history"].insert(i, entry_0714)
                inserted = True
                break
        if not inserted:
            t6["history"].append(entry_0714)
        print(f"t6 updated: {len(t6['history'])} history entries")

# t14: Wachbaracken – add 2025-07-28 entry as the earliest vote
t14 = topic_map.get("t14")
if t14:
    entry_0728 = {
        "date": "2025-07-28",
        "type": "vote",
        "title": "Abbruchbeschluss 2012 aufgehoben",
        "text": (
            "Der Stadtrat hebt den Beschluss vom 10.12.2012 zum Abbruch der historischen Wachbaracken "
            "an der Schlesierstraße auf. Stattdessen soll eine denkmalgerechte Sanierung angestrebt werden. "
            "Ein Nutzungskonzept wird erarbeitet; eine Zweckvereinbarung mit dem Landkreis Freising soll folgen."
        ),
        "sessionId": "sr_20250728",
        "voteId": "sr_20250728_03"
    }
    dates = [e["date"] for e in t14["history"]]
    if "2025-07-28" not in dates:
        inserted = False
        for i, e in enumerate(t14["history"]):
            if e["date"] >= "2025-07-29":
                t14["history"].insert(i, entry_0728)
                inserted = True
                break
        if not inserted:
            t14["history"].append(entry_0728)
        print(f"t14 updated: {len(t14['history'])} history entries")

with open(f"{BASE}/topics.json", "w", encoding="utf-8") as f:
    json.dump(topics, f, ensure_ascii=False, indent=2)

print(f"\nDone: {added_sessions} sessions, {added_votes} votes, topics updated.")
