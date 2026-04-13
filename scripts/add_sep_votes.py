import json

BASE = "c:/Users/bened/Documents/GitHub/bagruber/council/data"

absent_0908 = ["hadersdorfer", "stanglmaier", "becher_a", "kaestl", "lauterbach", "linz_kilian", "tristl", "weber"]
present_0908 = ["dollinger", "becher_j", "beibl", "fincke", "gruber", "grundner", "haberl", "heinz",
                "hobmaier", "kieninger", "linz_karin", "marcus", "pschorr", "reif", "strobl", "von_pressentin", "welter"]
present_0908_no_heinz = [m for m in present_0908 if m != "heinz"]
present_0908_no_beibl = [m for m in present_0908 if m != "beibl"]

absent_0922_session = ["hadersdorfer", "heinz", "von_pressentin", "weber", "welter"]
present_0922_early = ["dollinger", "stanglmaier", "becher_a", "becher_j", "beibl", "fincke", "gruber",
                      "grundner", "haberl", "hobmaier", "kieninger", "lauterbach", "linz_karin", "linz_kilian",
                      "marcus", "pschorr", "reif", "strobl", "tristl"]
absent_0922_early = absent_0922_session + ["kaestl"]
present_0922_full = present_0922_early + ["kaestl"]
absent_0922_full = absent_0922_session

new_votes = [
    {
        "id": "sr_20250908_01", "sessionId": "sr_20250908", "topicId": None, "date": "2025-09-08",
        "title": "Genehmigung Niederschriften",
        "text": "Der Stadtrat genehmigt die \u00f6ffentlichen Niederschriften der Stadtratssitzungen vom 02.06.2025, 14.07.2025 und 28.07.2025.",
        "type": "named", "results": {"yes": present_0908, "no": [], "absent": absent_0908}
    },
    {
        "id": "sr_20250908_02", "sessionId": "sr_20250908", "topicId": "t8", "date": "2025-09-08",
        "title": "Informationsveranstaltung Schulzentrum S\u00fcd",
        "text": "Der Stadtrat beschlie\u00dft, in Abstimmung mit den Schulen eine Informationsveranstaltung zu m\u00f6glichen Verkehrsma\u00dfnahmen durchzuf\u00fchren. Die bevorzugte Variante ist dem Stadtrat danach zur Beschlussfassung vorzulegen.",
        "type": "named", "results": {"yes": present_0908, "no": [], "absent": absent_0908}
    },
    {
        "id": "sr_20250908_03", "sessionId": "sr_20250908", "topicId": None, "date": "2025-09-08",
        "title": "Einvernehmen MFH Weihmühlstraße 18",
        "text": "Der Stadtrat erteilt zum Neubau eines Mehrfamilienhauses mit 5 Wohneinheiten an der Weihmühlstraße 18 das gemeindliche Einvernehmen.",
        "type": "named", "results": {"yes": present_0908_no_heinz, "no": [], "absent": absent_0908 + ["heinz"]}
    },
    {
        "id": "sr_20250908_04", "sessionId": "sr_20250908", "topicId": None, "date": "2025-09-08",
        "title": "Abweichung BayBO Spielplatz Weihmühlstraße 18",
        "text": "Der Stadtrat stimmt dem Abweichungsantrag zur BayBO zu: Aufgrund der zukünftig geltenden Satzung kann auf die Errichtung eines Spielplatzes verzichtet werden.",
        "type": "named", "results": {"yes": present_0908_no_heinz, "no": [], "absent": absent_0908 + ["heinz"]}
    },
    {
        "id": "sr_20250908_05", "sessionId": "sr_20250908", "topicId": None, "date": "2025-09-08",
        "title": "Einvernehmen Wohnanlage Stadtwaldstraße 9",
        "text": "Antrag auf Erteilung des gemeindlichen Einvernehmens für den Neubau einer Wohnanlage mit 21 Wohneinheiten und Tiefgarage (Haus A, B, C) an der Stadtwaldstraße 9, 9a, 9b.",
        "type": "anonymous", "result": "rejected", "results": {"yes": 8, "no": 9, "absent": 8}
    },
    {
        "id": "sr_20250908_06", "sessionId": "sr_20250908", "topicId": None, "date": "2025-09-08",
        "title": "Verweigerung Einvernehmen Stadtwaldstraße 9",
        "text": "Der Stadtrat verweigert das gemeindliche Einvernehmen. Die massive Gesamtlänge des Baukörpers 1 (Haus A+B) fügt sich nicht in die nähere Umgebungsbebauung ein. Die Stadtwaldstraße gilt als Zäsur beim Einfügegebot.",
        "type": "anonymous", "results": {"yes": 12, "no": 5, "absent": 8}
    },
    {
        "id": "sr_20250908_07", "sessionId": "sr_20250908", "topicId": None, "date": "2025-09-08",
        "title": "Keine Einwendungen ED 99 Nordumfahrung Erding",
        "text": "Die Stadt Moosburg erhebt gegen den Planfeststellungsbeschluss \u201eED 99 Nordumfahrung Erding mit Verlegung der Staatsstraße 2331\u201c keine Einwendungen.",
        "type": "named", "results": {"yes": present_0908, "no": [], "absent": absent_0908}
    },
    {
        "id": "sr_20250908_08", "sessionId": "sr_20250908", "topicId": None, "date": "2025-09-08",
        "title": "Wahlleiterin Kommunalwahl 2026",
        "text": "Der Stadtrat beruft Frau Evelyn Stadler zur Wahlleiterin gemäß Art. 5 Abs. 1 GLKrWG für die Gemeindewahlen 2026.",
        "type": "named", "results": {"yes": present_0908_no_beibl, "no": [], "absent": absent_0908 + ["beibl"]}
    },
    {
        "id": "sr_20250908_09", "sessionId": "sr_20250908", "topicId": None, "date": "2025-09-08",
        "title": "Stellvertretender Wahlleiter Kommunalwahl 2026",
        "text": "Der Stadtrat beruft Herrn Maximilian Götz zum stellvertretenden Wahlleiter gemäß Art. 5 Abs. 1 GLKrWG für die Gemeindewahlen 2026.",
        "type": "named", "results": {"yes": present_0908_no_beibl, "no": [], "absent": absent_0908 + ["beibl"]}
    },
    {
        "id": "sr_20250922_01", "sessionId": "sr_20250922", "topicId": None, "date": "2025-09-22",
        "title": "Zinssatz Abwassergebühren 3 %",
        "text": "Der Stadtrat beschließt den kalkulatorischen Zinssatz für die Abwassergebührenkalkulation ab 2026 auf 3 % festzusetzen.",
        "type": "named", "results": {"yes": present_0922_early, "no": [], "absent": absent_0922_early}
    },
    {
        "id": "sr_20250922_02", "sessionId": "sr_20250922", "topicId": None, "date": "2025-09-22",
        "title": "Auflösung Rücklage Abschreibungen",
        "text": "Der Stadtrat beschließt die Auflösung der Rücklage für Abschreibungen auf zuwendungsfinanziertes Anlagevermögen ab dem 01.01.2026.",
        "type": "named", "results": {"yes": present_0922_early, "no": [], "absent": absent_0922_early}
    },
    {
        "id": "sr_20250922_03", "sessionId": "sr_20250922", "topicId": None, "date": "2025-09-22",
        "title": "Gebührensatz Abwasserentsorgung 2026–2029",
        "text": "Der Stadtrat setzt die Gebühren für die Abwasserentsorgung 2026–2029 fest: Schmutzwassergebühr 3,32 €/m³, Niederschlagswassergebühr 0,57 €/m².",
        "type": "named", "results": {"yes": present_0922_early, "no": [], "absent": absent_0922_early}
    },
    {
        "id": "sr_20250922_04", "sessionId": "sr_20250922", "topicId": None, "date": "2025-09-22",
        "title": "Aufhebung Fäkalschlammentsorgungssatzung",
        "text": "Der Stadtrat beschließt die Aufhebung der Fäkalschlammentsorgungssatzung (FES) und der Gebührensatzung (GS-FES) vom 22.05.2017 zum 01.10.2025.",
        "type": "named", "results": {"yes": present_0922_early, "no": [], "absent": absent_0922_early}
    },
    {
        "id": "sr_20250922_05", "sessionId": "sr_20250922", "topicId": None, "date": "2025-09-22",
        "title": "Neuerlass Kläranlagenbenutzungsordnung",
        "text": "Der Stadtrat erlässt die Benutzungsordnung für die Kläranlage zur Direktannahme von Fäkalschlamm in der Fassung vom 22.09.2025 mit Inkrafttreten zum 01.10.2025.",
        "type": "named", "results": {"yes": present_0922_early, "no": [], "absent": absent_0922_early}
    },
    {
        "id": "sr_20250922_06", "sessionId": "sr_20250922", "topicId": "t13", "date": "2025-09-22",
        "title": "Abwägung Stellungnahmen Sanierungsgebiet",
        "text": "Der Stadtrat nimmt alle Stellungnahmen zur Kenntnis und passt den Umgriff an: Die Schloss Aschwiese wird auf Einwendung des AELF Ebersberg-Erding herausgenommen.",
        "type": "named", "results": {"yes": present_0922_full, "no": [], "absent": absent_0922_full}
    },
    {
        "id": "sr_20250922_07", "sessionId": "sr_20250922", "topicId": "t13", "date": "2025-09-22",
        "title": "Billigung Ziele Sanierungssatzung",
        "text": "Der Stadtrat billigt die in der Begründung zur Sanierungssatzung genannten Ziele und Zwecke der Sanierung auf Grundlage der Vorbereitenden Untersuchungen.",
        "type": "named", "results": {"yes": present_0922_full, "no": [], "absent": absent_0922_full}
    },
    {
        "id": "sr_20250922_08", "sessionId": "sr_20250922", "topicId": "t13", "date": "2025-09-22",
        "title": "Festlegung Sanierungsgebiet \u201eZwischen Innenstadt und Bahnhof\u201c",
        "text": "Der Stadtrat legt das Sanierungsgebiet \u201eZwischen Innenstadt und Bahnhof\u201c gemäß § 142 Abs. 3 BauGB förmlich als Satzung fest. Vereinfachtes Verfahren, Laufzeit zunächst 15 Jahre.",
        "type": "named", "results": {"yes": present_0922_full, "no": [], "absent": absent_0922_full}
    },
    {
        "id": "sr_20250922_09", "sessionId": "sr_20250922", "topicId": "t14", "date": "2025-09-22",
        "title": "Zweckvereinbarung Erhalt Wachbaracken Stalag VII A",
        "text": "Der Stadtrat ermächtigt den Ersten Bürgermeister zum Abschluss der Zweckvereinbarung mit dem Landkreis Freising zum Erhalt der historischen Wachbaracken des Stalag VII A.",
        "type": "named", "results": {"yes": present_0922_full, "no": [], "absent": absent_0922_full}
    },
    {
        "id": "sr_20250922_10", "sessionId": "sr_20250922", "topicId": None, "date": "2025-09-22",
        "title": "Verordnung Sonntagsöffnung Verkaufsstellen",
        "text": "Der Stadtrat beschließt den Erlass der Verordnung über die Öffnung von Verkaufsstellen an Sonntagen aus Anlass von Märkten, Messen oder ähnlichen Veranstaltungen (19:1).",
        "type": "anonymous", "results": {"yes": 19, "no": 1, "absent": 5}
    },
]

with open(f"{BASE}/votes.json", "r", encoding="utf-8") as f:
    votes = json.load(f)
votes.extend(new_votes)
with open(f"{BASE}/votes.json", "w", encoding="utf-8") as f:
    json.dump(votes, f, ensure_ascii=False, indent=2)
print(f"votes.json: {len(votes)} total")
