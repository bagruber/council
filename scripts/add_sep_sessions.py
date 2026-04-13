import json

BASE = "c:/Users/bened/Documents/GitHub/bagruber/council/data"

new_sessions = [
    {
        "id": "sr_20250908",
        "date": "2025-09-08",
        "type": "stadtrat",
        "title": "12. Stadtratssitzung – September 2025",
        "absent": ["hadersdorfer", "stanglmaier", "becher_a", "kaestl", "lauterbach", "linz_kilian", "tristl", "weber"],
        "agenda": [
            {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
            {"number": 2, "title": "Bürgerfragen gem. § 27 Abs. 2 GeschO/StR", "type": "formal"},
            {"number": 3, "title": "Genehmigung der öffentlichen Niederschriften (StR 02.06., 14.07. und 28.07.2025)", "voteId": "sr_20250908_01"},
            {"number": 4, "title": "Verkehrsberuhigung Schulzentrum Süd – Informationsveranstaltung", "topicId": "t8", "voteId": "sr_20250908_02"},
            {"number": "5.1", "title": "Neubau MFH Weihmühlstraße 18 – Einvernehmen", "voteId": "sr_20250908_03"},
            {"number": "5.1b", "title": "Neubau MFH Weihmühlstraße 18 – Abweichung BayBO Spielplatz", "voteId": "sr_20250908_04"},
            {"number": "5.2", "title": "Wohnanlage Stadtwaldstraße 9, 9a, 9b – Einvernehmen verweigert (8:9 / 12:5)", "voteId": "sr_20250908_06"},
            {"number": 6, "title": "ED 99 Nordumfahrung Erding – keine Einwendungen zum Planfeststellungsbeschluss", "voteId": "sr_20250908_07"},
            {"number": "7.1", "title": "Berufung Wahlleiterin Kommunalwahl 2026", "voteId": "sr_20250908_08"},
            {"number": "7.2", "title": "Berufung stellvertretender Wahlleiter Kommunalwahl 2026", "voteId": "sr_20250908_09"},
            {"number": 8, "title": "Anfragen", "type": "formal"}
        ]
    },
    {
        "id": "sr_20250922",
        "date": "2025-09-22",
        "type": "stadtrat",
        "title": "13. Stadtratssitzung – September 2025",
        "absent": ["hadersdorfer", "heinz", "von_pressentin", "weber", "welter"],
        "agenda": [
            {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
            {"number": 2, "title": "Bürgerfragen gem. § 27 Abs. 2 GeschO/StR", "type": "formal"},
            {"number": "3.1", "title": "Zinssatz Abwassergebühren ab 2026 (3 %)", "voteId": "sr_20250922_01"},
            {"number": "3.2", "title": "Auflösung Rücklage Abschreibungen", "voteId": "sr_20250922_02"},
            {"number": "3.3", "title": "Gebührensatz Abwasserentsorgung 2026–2029", "voteId": "sr_20250922_03"},
            {"number": "4.1", "title": "Aufhebung Fäkalschlammentsorgungssatzung (FES/GS-FES)", "voteId": "sr_20250922_04"},
            {"number": "4.2", "title": "Neuerlass Kläranlagenbenutzungsordnung", "voteId": "sr_20250922_05"},
            {"number": "5.1", "title": "Sanierungsgebiet Innenstadt–Bahnhof – Abwägung Stellungnahmen", "topicId": "t13", "voteId": "sr_20250922_06"},
            {"number": "5.2", "title": "Sanierungsgebiet – Billigung Ziele und Zwecke", "topicId": "t13", "voteId": "sr_20250922_07"},
            {"number": "5.3", "title": "Sanierungsgebiet – Förmliche Festlegung als Satzung", "topicId": "t13", "voteId": "sr_20250922_08"},
            {"number": 6, "title": "Zweckvereinbarung Erhalt Wachbaracken Stalag VII A", "topicId": "t14", "voteId": "sr_20250922_09"},
            {"number": 7, "title": "Verordnung Sonntagsöffnung Verkaufsstellen", "voteId": "sr_20250922_10"},
            {"number": 8, "title": "Anfragen", "type": "formal"}
        ]
    }
]

with open(f"{BASE}/sessions.json", "r", encoding="utf-8") as f:
    sessions = json.load(f)
sessions.extend(new_sessions)
with open(f"{BASE}/sessions.json", "w", encoding="utf-8") as f:
    json.dump(sessions, f, ensure_ascii=False, indent=2)
print(f"sessions.json: {len(sessions)} sessions")
