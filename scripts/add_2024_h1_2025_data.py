"""
Master script:
- Adds 14 new sessions (9 from 2024 incl. HVFA + 5 from 2025 H1)
- Adds all corresponding votes (named where unanimous & derivable, otherwise anonymous)
- Converts existing sr_20241216 anonymous unanimous votes to named
- Renames t7 (Haushalt) and t12 (Freibad)
- Adds new topics t16 (Hallenbad) and t17 (Rathaus-Sanierung)
- Extends existing topics with history entries from new sessions
"""
import json

BASE = "c:/Users/bened/Documents/GitHub/bagruber/council/data"

# ── Member rosters ────────────────────────────────────────────────────────────
ALL_PRE_OCT21 = [  # before hobmaier swearing-in (2024-10-21); gruebl active
    "dollinger", "hadersdorfer", "tristl", "weber", "haberl",
    "linz_karin", "heinz",
    "beibl", "stanglmaier", "von_pressentin", "becher_j", "becher_a", "linz_kilian",
    "grundner", "lauterbach", "reif", "kieninger",
    "beubl", "pschorr",
    "gruebl", "gruber",
    "welter", "kaestl", "fincke", "strobl",
]

ALL_POST_OCT21 = [  # hobmaier in, gruebl out; beubl still active
    "dollinger", "hadersdorfer", "tristl", "weber", "haberl",
    "linz_karin", "heinz",
    "beibl", "stanglmaier", "von_pressentin", "becher_j", "becher_a", "linz_kilian",
    "grundner", "lauterbach", "reif", "kieninger",
    "beubl", "pschorr",
    "gruber", "hobmaier",
    "welter", "kaestl", "fincke", "strobl",
]

ALL_POST_MAR2025 = [  # beubl out, marcus in
    "dollinger", "hadersdorfer", "tristl", "weber", "haberl",
    "linz_karin", "heinz",
    "beibl", "stanglmaier", "von_pressentin", "becher_j", "becher_a", "linz_kilian",
    "grundner", "lauterbach", "reif", "kieninger",
    "pschorr", "marcus",
    "gruber", "hobmaier",
    "welter", "kaestl", "fincke", "strobl",
]

def yes_list(roster, absent):
    return [m for m in roster if m not in absent]

def named(roster, absent):
    return {"type": "named", "results": {"yes": yes_list(roster, absent), "no": [], "absent": list(absent)}}

def anon(yes, no, absent_count, rejected=False):
    d = {"type": "anonymous", "results": {"yes": yes, "no": no, "absent": absent_count}}
    if rejected: d["result"] = "rejected"
    return d

# ============================================================================
# SESSIONS
# ============================================================================
new_sessions = []

# ── BPU 2024-09-30 ────────────────────────────────────────────────────────────
# 12 BPU members; subs: stanglmaier→becher_j, beubl→pschorr, gruebl→gruber (gruber ab 19:10)
new_sessions.append({
    "id": "bpu_20240930",
    "date": "2024-09-30",
    "type": "bpu",
    "title": "3. Sitzung Bau-, Planungs- und Umweltausschuss – September 2024",
    "substitutes": [
        {"member": "stanglmaier", "substitute": "becher_j"},
        {"member": "beubl", "substitute": "pschorr"},
        {"member": "gruebl", "substitute": "gruber"},
    ],
    "agenda": [
        {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Auftragsvergabe Solarleuchten Rennweg / Schloss-Asch-Wiese", "voteId": "bpu_20240930_01"},
        {"number": "4.1", "title": "Allwetterausläufe Pferde Amperstr. 24", "voteId": "bpu_20240930_02"},
        {"number": "4.2a", "title": "Mehrfamilienhaus 12 WE Bahnhofstr. 60 – Einvernehmen erteilt (abgelehnt)", "voteId": "bpu_20240930_03"},
        {"number": "4.2b", "title": "Mehrfamilienhaus 12 WE Bahnhofstr. 60 – Einvernehmen verweigert", "voteId": "bpu_20240930_04"},
        {"number": "4.3", "title": "MFH 6 WE Mainburger Str. 5 – Einvernehmen verweigert", "voteId": "bpu_20240930_05"},
        {"number": "4.4", "title": "Bullenmastall Kirchamper 6", "voteId": "bpu_20240930_06"},
        {"number": "4.5", "title": "Wohngebäude 9 WE St.-Georg-Str. 26", "voteId": "bpu_20240930_07"},
        {"number": "4.6", "title": "Maschinenhalle St.-Georg-Str. 60", "voteId": "bpu_20240930_08"},
        {"number": "4.7", "title": "Wohnhaus 2 WE Blütenstr. 46", "voteId": "bpu_20240930_09"},
        {"number": "4.8", "title": "6 Sozialwohnungen Unterreiterweg 13", "voteId": "bpu_20240930_10"},
        {"number": 5, "title": "Anfragen und Sonstiges", "type": "formal"},
    ]
})

# ── SR 2024-09-02 ─────────────────────────────────────────────────────────────
new_sessions.append({
    "id": "sr_20240902",
    "date": "2024-09-02",
    "type": "stadtrat",
    "title": "13. Stadtratssitzung – September 2024",
    "absent": ["hadersdorfer", "fincke", "gruber", "grundner", "haberl", "heinz", "kaestl", "lauterbach", "linz_kilian", "tristl", "stanglmaier"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Genehmigung Niederschrift StR 22.07.2024", "voteId": "sr_20240902_01"},
        {"number": "4.1", "title": "Bürogebäude Jungheinrich Degernpoint", "voteId": "sr_20240902_02"},
        {"number": "4.2", "title": "Werbeanlagen Jungheinrich", "voteId": "sr_20240902_03"},
        {"number": "5.1", "title": "B-Plan 77 Rockermaier – Stellungnahme Wasserwirtschaft", "topicId": "t5", "voteId": "sr_20240902_04"},
        {"number": "5.2", "title": "B-Plan 77 Rockermaier – Stellungnahme Altlasten", "topicId": "t5", "voteId": "sr_20240902_05"},
        {"number": "5.3", "title": "B-Plan 77 Rockermaier – Stellungnahmen Brandschutz/Sonstige", "topicId": "t5", "voteId": "sr_20240902_06"},
        {"number": "5.4", "title": "B-Plan 77 Rockermaier – Stellungnahme Naturschutz", "topicId": "t5", "voteId": "sr_20240902_07"},
        {"number": "5.5", "title": "B-Plan 77 Rockermaier – Stellungnahme Gesundheit", "topicId": "t5", "voteId": "sr_20240902_08"},
        {"number": "5.6", "title": "B-Plan 77 Rockermaier – Stellungnahme Wasserrecht", "topicId": "t5", "voteId": "sr_20240902_09"},
        {"number": "5.7", "title": "B-Plan 77 Rockermaier Areal – Satzungsbeschluss", "topicId": "t5", "voteId": "sr_20240902_10"},
        {"number": 6, "title": "Beteiligungsberichte 2015–2023", "voteId": "sr_20240902_11"},
        {"number": 7, "title": "Anfragen", "type": "formal"},
    ]
})

# ── SR 2024-09-23 ─────────────────────────────────────────────────────────────
new_sessions.append({
    "id": "sr_20240923",
    "date": "2024-09-23",
    "type": "stadtrat",
    "title": "14. Stadtratssitzung – September 2024",
    "absent": ["hadersdorfer", "gruebl", "heinz", "kaestl", "linz_karin"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Genehmigung Niederschrift StR 17.06.2024", "voteId": "sr_20240923_01"},
        {"number": "4.1", "title": "B-Plan 79 GE Unterreit – Entwurfsbilligung (12:7)", "voteId": "sr_20240923_02"},
        {"number": "4.2", "title": "B-Plan 79 Unterreit – Lärmschutzwand erforderlich", "voteId": "sr_20240923_03"},
        {"number": "5.1", "title": "Mietkonditionen Böhmerwaldstr. – Neuvermietung 11,50 €/m² (12:7)", "voteId": "sr_20240923_04"},
        {"number": "5.2", "title": "Mietkonditionen Böhmerwaldstr. – Auslaufen Mietabsenkung", "voteId": "sr_20240923_05"},
        {"number": 6, "title": "Verordnung verkaufsoffener Sonntag 20.10.2024", "voteId": "sr_20240923_06"},
        {"number": 7, "title": "Sanierung Rathaus – Fassade und 1./2. OG", "topicId": "t17", "voteId": "sr_20240923_07"},
        {"number": 8, "title": "Anfragen", "type": "formal"},
    ]
})

# ── SR 2024-10-07 ─────────────────────────────────────────────────────────────
# vote 3 (17:8); votes 5,6,8 (19:6 / 20:5)
# session absent (5 listed): hadersdorfer, becher_j, beubl, gruebl, heinz
# But vote 3 shows 8 absent; later votes 5,6,8 show 6/5 absent — inconsistency suggests partial attendance.
# I'll record session absent as 5 listed; mark vote 3 specifically with 3 extra unknown briefly absent (anonymous).
new_sessions.append({
    "id": "sr_20241007",
    "date": "2024-10-07",
    "type": "stadtrat",
    "title": "15. Stadtratssitzung – Oktober 2024",
    "absent": ["hadersdorfer", "becher_j", "beubl", "gruebl", "heinz"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Genehmigung Niederschrift StR 02.09.2024", "voteId": "sr_20241007_01"},
        {"number": 4, "title": "Auf dem Plan – Bericht der Kreisarchäologin", "topicId": "t3", "type": "discussion"},
        {"number": 5, "title": "Vorbereitende Untersuchungen Innenstadt–Bahnhof", "topicId": "t13", "voteId": "sr_20241007_02"},
        {"number": 6, "title": "Vermietungskonditionen Sonnensiedlung 1", "voteId": "sr_20241007_03"},
        {"number": 7, "title": "Finanzbericht 30.09.2024", "type": "discussion"},
        {"number": 8, "title": "Überplanmäßige Ausgaben Betriebsstrom", "topicId": "t7", "voteId": "sr_20241007_04"},
        {"number": 9, "title": "Anfragen", "type": "formal"},
    ]
})

# ── SR 2024-10-21 ─────────────────────────────────────────────────────────────
# Transition session: gruebl out, hobmaier in (during item 4.2 Vereidigung)
# Session-level "absent" only lists those absent from full session
new_sessions.append({
    "id": "sr_20241021",
    "date": "2024-10-21",
    "type": "stadtrat",
    "title": "16. Stadtratssitzung – Oktober 2024",
    "absent": ["hadersdorfer", "fincke", "haberl", "reif"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Genehmigung Niederschriften (BA 15.07., StR 23.09.2024)", "voteId": "sr_20241021_01"},
        {"number": "4.1", "title": "Niederlegung Mandat StR Grübl – Hobmaier rückt nach", "voteId": "sr_20241021_02"},
        {"number": "4.2", "title": "Vereidigung StR Hobmaier", "type": "formal"},
        {"number": "4.3.1", "title": "Schaffung Jugendreferent (15:2)", "voteId": "sr_20241021_03"},
        {"number": "4.3.2", "title": "Berufung Grübl als Jugendreferent", "voteId": "sr_20241021_04"},
        {"number": "4.3.3", "title": "Aufwandsentschädigung Jugendreferent", "voteId": "sr_20241021_05"},
        {"number": "4.4", "title": "Neubesetzung Ausschüsse / AR Kläranlage", "voteId": "sr_20241021_06"},
        {"number": 5, "title": "TG-Grundschule – Containeranlage (vertagt)", "topicId": "t6", "type": "discussion"},
        {"number": 6, "title": "B-Plan 66 Oberes Gereut Nordost – Verfahrenswechsel", "voteId": "sr_20241021_07"},
        {"number": "7.1", "title": "Hebesatz Grundsteuer A 2025 (12:6)", "topicId": "t7", "voteId": "sr_20241021_08"},
        {"number": "7.2", "title": "Hebesatzsatzung 2025 gesamt", "topicId": "t7", "voteId": "sr_20241021_09"},
        {"number": 8, "title": "6 Sozialwohnungen Unterreiterweg 13 – Bauauftrag", "voteId": "sr_20241021_10"},
        {"number": "9.1", "title": "Hallenbad Öffnungszeiten (19:1)", "topicId": "t16", "voteId": "sr_20241021_11"},
        {"number": "9.2", "title": "Hallenbad Gebühren und Tarife", "topicId": "t16", "voteId": "sr_20241021_12"},
        {"number": 10, "title": "Anfragen", "type": "formal"},
    ]
})

# ── SR 2024-11-04 ─────────────────────────────────────────────────────────────
new_sessions.append({
    "id": "sr_20241104",
    "date": "2024-11-04",
    "type": "stadtrat",
    "title": "17. Stadtratssitzung – November 2024",
    "absent": ["becher_j", "heinz"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Flächennutzungsplan – Schul-/Sportflächen", "topicId": "t6", "voteId": "sr_20241104_01"},
        {"number": 4, "title": "Vorbescheid MFH Mainburger Str. 5 – Anhörung Ersetzung Einvernehmen", "voteId": "sr_20241104_02"},
        {"number": 5, "title": "Vorbescheid MFH 12 WE Bahnhofstr. 60 – Anhörung Ersetzung Einvernehmen (19:2)", "voteId": "sr_20241104_03"},
        {"number": 6, "title": "Straßenname „Semptanger\"", "voteId": "sr_20241104_04"},
        {"number": 7, "title": "Hallenbad – Freier Eintritt Kinder Weihnachtsferien (vertagt 12:9)", "topicId": "t16", "voteId": "sr_20241104_05"},
        {"number": 8, "title": "Anfragen", "type": "formal"},
    ]
})

# ── SR 2024-11-18 ─────────────────────────────────────────────────────────────
# session absent: heinz, reif, tristl
# Partial: becher_j ab 18:10, gruber ab 18:08, kaestl ab 18:13, von_pressentin ab 18:15
# vote 6 yes=17 absent=8: 5 brief absent (becher_j, von_pressentin, lauterbach, weber, kaestl per agent)
new_sessions.append({
    "id": "sr_20241118",
    "date": "2024-11-18",
    "type": "stadtrat",
    "title": "18. Stadtratssitzung – November 2024",
    "absent": ["heinz", "reif", "tristl"],
    "agenda": [
        {"number": 2, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
        {"number": 3, "title": "Bürgerfragen", "type": "formal"},
        {"number": 4, "title": "Genehmigung Niederschriften (BA 30.09., StR 07.10. + 21.10.)", "voteId": "sr_20241118_01"},
        {"number": 5, "title": "Flexx Bus On Demand – Information", "type": "discussion"},
        {"number": 6, "title": "Autohaus-Erweiterung Sempt 7", "voteId": "sr_20241118_02"},
        {"number": 7, "title": "Rücklagenbildung Regiebetriebe", "topicId": "t7", "voteId": "sr_20241118_03"},
        {"number": 8, "title": "Zuschuss DAV Kletter-/Boulderhalle (€292.000 / 20%)", "voteId": "sr_20241118_04"},
        {"number": 9, "title": "Kläranlage GmbH – Satzungsänderung Nachhaltigkeitsbericht", "voteId": "sr_20241118_05"},
        {"number": 10, "title": "Anfragen", "type": "formal"},
    ]
})

# ── HVFA 2024-11-28 ───────────────────────────────────────────────────────────
new_sessions.append({
    "id": "hvfa_20241128",
    "date": "2024-11-28",
    "type": "hvfa",
    "title": "3. Sitzung Hauptverwaltungs- und Finanzausschuss – November 2024",
    "agenda": [
        {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Haushaltsberatung – Statusbericht", "type": "discussion"},
        {"number": 4, "title": "Kläranlage Wirtschaftsplan – Vorstellung", "type": "discussion"},
        {"number": 5, "title": "Beschaffungen Feuerwehr", "type": "discussion"},
        {"number": "6.2.1", "title": "Antrag Seniorenbeirat – Amtsblatt für alle Haushalte (abgelehnt)", "topicId": "t10", "voteId": "hvfa_20241128_01"},
        {"number": "6.2.2", "title": "Solarstrom-Förderrichtlinie – Antrag Lauterbach (zurückgezogen)", "type": "discussion"},
        {"number": 7, "title": "Anfragen", "type": "formal"},
    ]
})

# ── SR 2024-12-02 ─────────────────────────────────────────────────────────────
new_sessions.append({
    "id": "sr_20241202",
    "date": "2024-12-02",
    "type": "stadtrat",
    "title": "19. Stadtratssitzung – Dezember 2024",
    "absent": ["stanglmaier", "becher_a", "heinz", "reif", "kaestl", "fincke"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Genehmigung Niederschrift StR 04.11.2024", "voteId": "sr_20241202_01"},
        {"number": 4, "title": "BayKIT e.G. – Mitgliedschaft", "voteId": "sr_20241202_02"},
        {"number": 5, "title": "Anfragen", "type": "formal"},
    ]
})

# ── BPU 2025-01-16 ────────────────────────────────────────────────────────────
# Substitutes: stanglmaier→becher_j; absent (no sub): linz_karin (weber sub also absent)
# Partial: hadersdorfer ab 19:15
new_sessions.append({
    "id": "bpu_20250116",
    "date": "2025-01-16",
    "type": "bpu",
    "title": "1. Sitzung Bau-, Planungs- und Umweltausschuss – Januar 2025",
    "absent": ["linz_karin"],
    "substitutes": [{"member": "stanglmaier", "substitute": "becher_j"}],
    "agenda": [
        {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": "3.1", "title": "Abgrabungsrecht Grube Stünzbach – Tektur", "voteId": "bpu_20250116_01"},
        {"number": "3.2", "title": "3. Wohneinheit Thalbacher Str. 85 – Einvernehmen verweigert", "voteId": "bpu_20250116_02"},
        {"number": "3.3a", "title": "Wohnanlage Stadtwaldstr. 9 – Einvernehmen erteilt (abgelehnt 3:8)", "voteId": "bpu_20250116_03"},
        {"number": "3.3b", "title": "Wohnanlage Stadtwaldstr. 9 – Einvernehmen verweigert", "voteId": "bpu_20250116_04"},
        {"number": "3.4", "title": "Lagerhalle Oberpolln 2", "voteId": "bpu_20250116_05"},
        {"number": "3.5", "title": "Hofladen Vorbescheid Amperstr. 6", "voteId": "bpu_20250116_06"},
        {"number": "3.6", "title": "Fahrzeughalle FFW – Einvernehmen erteilt", "voteId": "bpu_20250116_07"},
        {"number": "3.7", "title": "Vorbescheid MFH Moosstr. 15b – Einvernehmen verweigert", "voteId": "bpu_20250116_08"},
        {"number": 4, "title": "Anfragen und Sonstiges", "type": "formal"},
    ]
})

# ── SR 2025-01-20 ─────────────────────────────────────────────────────────────
# 3 absent (stanglmaier, linz_karin, von_pressentin); partial: hadersdorfer 18:10, becher_j 18:40, beibl bis 20:30, kaestl ab 20:25
# Vote 3 yes=19 absent=5 (early)
# Vote 4 yes=21 absent=4 (later)
# Votes 7-8 yes=21 absent=4 (later)
# Vote 9 yes=19 absent=6 (latest, beibl gone, gruber/fincke?)
new_sessions.append({
    "id": "sr_20250120",
    "date": "2025-01-20",
    "type": "stadtrat",
    "title": "1. Stadtratssitzung – Januar 2025",
    "absent": ["stanglmaier", "linz_karin", "von_pressentin"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Genehmigung Niederschriften (HVFA 28.11.; StR 18.11., 02.12., 09.12.2024)", "voteId": "sr_20250120_01"},
        {"number": 4, "title": "TG-Grundschule – Vorstellung Entwurfsplanung", "topicId": "t6", "voteId": "sr_20250120_02"},
        {"number": 5, "title": "Vorstellung Geschäftsstellenleiterin Moosburg Marketing", "type": "discussion"},
        {"number": 6, "title": "B-Plan 81 MI Moos – Einstellung des Bauleitplanverfahrens", "voteId": "sr_20250120_03"},
        {"number": "7.1", "title": "4. Änderung B-Plan 50 Degernpoint – Verfahrenswechsel", "voteId": "sr_20250120_04"},
        {"number": "7.2", "title": "4. Änderung B-Plan 50 Degernpoint – Aufstellungsbeschluss", "voteId": "sr_20250120_05"},
        {"number": "8.1", "title": "Umlegungsverfahren Degernpoint II – Anordnung", "voteId": "sr_20250120_06"},
        {"number": "8.2", "title": "Umlegungsverfahren Degernpoint II – Kostenverteilung", "voteId": "sr_20250120_07"},
        {"number": 9, "title": "Übertragung Haushaltsreste 2024", "topicId": "t7", "voteId": "sr_20250120_08"},
        {"number": 10, "title": "Anfragen", "type": "formal"},
    ]
})

# ── SR 2025-04-10 ─────────────────────────────────────────────────────────────
# Hadersdorfer presides; dollinger absent; absent: dollinger, gruber, hobmaier, kaestl, lauterbach, weber
# vote 3: yes=19 absent=6
# vote 4.1.1 (E-Auto Beschluss 1, 15:4): split
# votes 4.1.2 + 4.2: yes=19 (and 18 with weber added or beibl gone)
new_sessions.append({
    "id": "sr_20250410",
    "date": "2025-04-10",
    "type": "stadtrat",
    "title": "5. Stadtratssitzung – April 2025",
    "absent": ["dollinger", "gruber", "hobmaier", "kaestl", "lauterbach", "weber"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Genehmigung Niederschriften (StR 24.02., BPU 17.03.2025)", "voteId": "sr_20250410_01"},
        {"number": "4.1a", "title": "E-Auto Parken – 2. Änderung Parkgebühren-Satzung (15:4)", "voteId": "sr_20250410_02"},
        {"number": "4.1b", "title": "E-Auto Parken – Protest gegen Staatsregierung", "voteId": "sr_20250410_03"},
        {"number": "4.2", "title": "Erhöhung Parkgebühren Bahnhof/Stadionstraße", "voteId": "sr_20250410_04"},
        {"number": 5, "title": "Anfragen", "type": "formal"},
    ]
})

# ── SR 2025-04-28 ─────────────────────────────────────────────────────────────
# Absent: gruber, heinz, hobmaier, von_pressentin, welter (5)
# Partial: becher_j ab 19:15, kaestl ab 19:17, linz_karin bis 21:15
new_sessions.append({
    "id": "sr_20250428",
    "date": "2025-04-28",
    "type": "stadtrat",
    "title": "6. Stadtratssitzung – April 2025",
    "absent": ["gruber", "heinz", "hobmaier", "von_pressentin", "welter"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Genehmigung Niederschrift StR 24.03.2025", "voteId": "sr_20250428_01"},
        {"number": 4, "title": "Plakatanschlagtafeln Jägerstr. 2 – Einvernehmen verweigert", "voteId": "sr_20250428_02"},
        {"number": 5, "title": "B-Plan Isarstraße – Antrag Deutinger abgelehnt (18:2)", "voteId": "sr_20250428_03"},
        {"number": "6a", "title": "Badegebühren Freibad – Änderungsantrag Marcus (abgelehnt 2:18)", "topicId": "t12", "voteId": "sr_20250428_04"},
        {"number": "6b", "title": "Badegebühren Freibad – Änderungsantrag Stanglmaier (Abendkarte ab 17 Uhr; 19:1)", "topicId": "t12", "voteId": "sr_20250428_05"},
        {"number": 6, "title": "Badegebührenordnung Freibad (Variante A; 19:1)", "topicId": "t12", "voteId": "sr_20250428_06"},
        {"number": 7, "title": "Anfragen", "type": "formal"},
    ]
})

# ── BPU 2025-05-22 ────────────────────────────────────────────────────────────
# Absent: hadersdorfer + heinz (sub), hobmaier + gruber (sub), kieninger, linz_karin
# Subs present: lauterbach (for kieninger), weber (for linz_karin)
new_sessions.append({
    "id": "bpu_20250522",
    "date": "2025-05-22",
    "type": "bpu",
    "title": "3. Sitzung Bau-, Planungs- und Umweltausschuss – Mai 2025",
    "absent": ["hadersdorfer", "hobmaier"],
    "substitutes": [
        {"member": "kieninger", "substitute": "lauterbach"},
        {"member": "linz_karin", "substitute": "weber"},
    ],
    "agenda": [
        {"number": 1, "title": "Mitteilungen", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": "3.1", "title": "Tempo 30 Neustadtstraße", "topicId": "t4", "voteId": "bpu_20250522_01"},
        {"number": "3.2", "title": "Fußgängerüberweg Sudetenlandstraße – abgelehnt", "topicId": "t4", "voteId": "bpu_20250522_02"},
        {"number": "3.3", "title": "Fahrradstraße Stadtbadstraße – abgelehnt", "topicId": "t4", "voteId": "bpu_20250522_03"},
        {"number": "4.1", "title": "Doppelhaushälften Auenstr. 32/32a", "voteId": "bpu_20250522_04"},
        {"number": "4.2", "title": "Doppelhaushälften Auenstr. 34/34a", "voteId": "bpu_20250522_05"},
        {"number": "4.3", "title": "MFH Merkurstr. 8 – Einvernehmen verweigert", "voteId": "bpu_20250522_06"},
        {"number": "4.4", "title": "MFH Bahnhofstr. 60 (12 WE) – Einvernehmen verweigert (9:1)", "voteId": "bpu_20250522_07"},
        {"number": "4.5", "title": "MFH Mainburger Str. 5 (8 WE) – Einvernehmen verweigert", "voteId": "bpu_20250522_08"},
        {"number": "4.6a", "title": "MFH Neustadtstr. 17 – Einvernehmen erteilt (abgelehnt 0:10)", "voteId": "bpu_20250522_09"},
        {"number": "4.6b", "title": "MFH Neustadtstr. 17 – Einvernehmen verweigert", "voteId": "bpu_20250522_10"},
        {"number": 5, "title": "Lebendige Zentren – Giebelsanierung Herrnstr. 23", "topicId": "t13", "voteId": "bpu_20250522_11"},
        {"number": 6, "title": "Anfragen und Sonstiges", "type": "formal"},
    ]
})

# ============================================================================
# VOTES
# ============================================================================
new_votes = []

# Helper for BPU
def bpu_vote(vid, sid, topic, date, title, text, type_d):
    v = {"id": vid, "sessionId": sid, "topicId": topic, "date": date, "title": title, "text": text}
    v.update(type_d)
    return v

# === BPU 2024-09-30 ==========================================================
# 12 BPU voters when all there. gruber arrives 19:10 – early votes 11.
BPU_0930_VOTERS_FULL = ["dollinger", "hadersdorfer", "becher_j", "beibl", "gruber",
                       "kieninger", "linz_karin", "linz_kilian", "pschorr", "reif",
                       "tristl", "welter"]
BPU_0930_VOTERS_EARLY = [m for m in BPU_0930_VOTERS_FULL if m != "gruber"]
def bpu_named(voters_yes, absent):
    return {"type": "named", "results": {"yes": list(voters_yes), "no": [], "absent": list(absent)}}

new_votes += [
    {"id":"bpu_20240930_01","sessionId":"bpu_20240930","topicId":None,"date":"2024-09-30",
     "title":"Solarleuchten Rennweg / Schloss-Asch-Wiese",
     "text":"Auftragsvergabe für LED-Solarleuchten an HL LICHTTECHNIK (40.864,60 €).",
     **bpu_named(BPU_0930_VOTERS_EARLY, ["gruber"])},
    {"id":"bpu_20240930_02","sessionId":"bpu_20240930","topicId":None,"date":"2024-09-30",
     "title":"Allwetterausläufe Pferde Amperstr. 24",
     "text":"Gemeindliches Einvernehmen für Pferdeauslauf erteilt.",
     **bpu_named(BPU_0930_VOTERS_EARLY, ["gruber"])},
    {"id":"bpu_20240930_03","sessionId":"bpu_20240930","topicId":None,"date":"2024-09-30",
     "title":"MFH 12 WE Bahnhofstr. 60 – Einvernehmen erteilt (abgelehnt)",
     "text":"Antrag, Einvernehmen für 12-Wohneinheiten-MFH zu erteilen, wird abgelehnt (4:8).",
     **anon(4, 8, 0, rejected=True)},
    {"id":"bpu_20240930_04","sessionId":"bpu_20240930","topicId":None,"date":"2024-09-30",
     "title":"MFH 12 WE Bahnhofstr. 60 – Einvernehmen verweigert",
     "text":"Einvernehmen wird verweigert; Baukörper und 3-geschossigkeit fügen sich nicht in Eigenart ein (8:4).",
     **anon(8, 4, 0)},
    {"id":"bpu_20240930_05","sessionId":"bpu_20240930","topicId":None,"date":"2024-09-30",
     "title":"MFH 6 WE Mainburger Str. 5 – Einvernehmen verweigert",
     "text":"Einvernehmen einstimmig verweigert; Maß baulicher Nutzung nicht ortstypisch.",
     **bpu_named(BPU_0930_VOTERS_FULL, [])},
    {"id":"bpu_20240930_06","sessionId":"bpu_20240930","topicId":None,"date":"2024-09-30",
     "title":"Bullenmastall Kirchamper 6","text":"Gemeindliches Einvernehmen einstimmig erteilt.",
     **bpu_named(BPU_0930_VOTERS_FULL, [])},
    {"id":"bpu_20240930_07","sessionId":"bpu_20240930","topicId":None,"date":"2024-09-30",
     "title":"Wohngebäude 9 WE St.-Georg-Str. 26","text":"Einvernehmen einstimmig erteilt.",
     **bpu_named(BPU_0930_VOTERS_FULL, [])},
    {"id":"bpu_20240930_08","sessionId":"bpu_20240930","topicId":None,"date":"2024-09-30",
     "title":"Maschinenhalle St.-Georg-Str. 60","text":"Einvernehmen einstimmig erteilt.",
     **bpu_named(BPU_0930_VOTERS_FULL, [])},
    {"id":"bpu_20240930_09","sessionId":"bpu_20240930","topicId":None,"date":"2024-09-30",
     "title":"Wohnhaus 2 WE Blütenstr. 46","text":"Einvernehmen mit Befreiungen einstimmig erteilt.",
     **bpu_named(BPU_0930_VOTERS_FULL, [])},
    {"id":"bpu_20240930_10","sessionId":"bpu_20240930","topicId":None,"date":"2024-09-30",
     "title":"6 Sozialwohnungen Unterreiterweg 13","text":"Einvernehmen einstimmig erteilt.",
     **bpu_named(BPU_0930_VOTERS_FULL, [])},
]

# === SR 2024-09-02 ===========================================================
# 14 yes for early (11 absent including stanglmaier partial)
ABS_0902 = ["hadersdorfer", "fincke", "gruber", "grundner", "haberl", "heinz", "kaestl",
            "lauterbach", "linz_kilian", "tristl", "stanglmaier"]
new_votes += [
    {"id":"sr_20240902_01","sessionId":"sr_20240902","topicId":None,"date":"2024-09-02",
     "title":"Genehmigung Niederschrift StR 22.07.2024",
     "text":"Der Stadtrat genehmigt den öffentlichen Teil der Niederschrift vom 22.07.2024.",
     **named(ALL_PRE_OCT21, ABS_0902)},
    {"id":"sr_20240902_02","sessionId":"sr_20240902","topicId":None,"date":"2024-09-02",
     "title":"Bürogebäude Jungheinrich Degernpoint",
     "text":"Gemeindliches Einvernehmen für Büro- und Ausstellungsgebäude erteilt.",
     **named(ALL_PRE_OCT21, ABS_0902)},
    {"id":"sr_20240902_03","sessionId":"sr_20240902","topicId":None,"date":"2024-09-02",
     "title":"Werbeanlagen Jungheinrich","text":"Einvernehmen für Werbeanlagen erteilt.",
     **named(ALL_PRE_OCT21, ABS_0902)},
] + [
    # 5.1-5.6 Stellungnahmen B-Plan 77 Rockermaier (alle 14:0:11)
    {"id":f"sr_20240902_{i+4:02d}","sessionId":"sr_20240902","topicId":"t5","date":"2024-09-02",
     "title":title,"text":text, **named(ALL_PRE_OCT21, ABS_0902)}
    for i, (title, text) in enumerate([
        ("B-Plan 77 Rockermaier – Stellungnahme Wasserwirtschaft",
         "Stellungnahme der Wasserwirtschaftsbehörde zur Kenntnis genommen; keine Einwendungen."),
        ("B-Plan 77 Rockermaier – Stellungnahme Altlasten",
         "Stellungnahme zu Altlasten zur Kenntnis genommen; keine Bedenken."),
        ("B-Plan 77 Rockermaier – Stellungnahmen Brandschutz/Sonstige",
         "Sonstige fachliche Stellungnahmen ohne Einwendungen."),
        ("B-Plan 77 Rockermaier – Stellungnahme Naturschutz",
         "Naturschutzbehörde stimmt Plan zu."),
        ("B-Plan 77 Rockermaier – Stellungnahme Gesundheit",
         "Gesundheitliche Stellungnahme zur Kenntnis genommen."),
        ("B-Plan 77 Rockermaier – Stellungnahme Wasserrecht",
         "Wasserrechtliche Stellungnahme ohne Einwendungen."),
    ])
] + [
    {"id":"sr_20240902_10","sessionId":"sr_20240902","topicId":"t5","date":"2024-09-02",
     "title":"B-Plan 77 Rockermaier – Satzungsbeschluss",
     "text":"Der Stadtrat beschließt den Bebauungsplan Nr. 77 „Rockermaier Areal\" als Satzung (12:2).",
     **anon(12, 2, 11)},
    {"id":"sr_20240902_11","sessionId":"sr_20240902","topicId":None,"date":"2024-09-02",
     "title":"Beteiligungsberichte 2015–2023",
     "text":"Beteiligungsberichte zur Kenntnis genommen; werden öffentlich gemacht.",
     **named(ALL_PRE_OCT21, ABS_0902)},
]

# === SR 2024-09-23 ===========================================================
# Absent: hadersdorfer, gruebl, heinz, kaestl, linz_karin (5) → 19 voters present, 1 brief absent in some votes
ABS_0923 = ["hadersdorfer", "gruebl", "heinz", "kaestl", "linz_karin"]
new_votes += [
    {"id":"sr_20240923_01","sessionId":"sr_20240923","topicId":None,"date":"2024-09-23",
     "title":"Genehmigung Niederschrift StR 17.06.2024","text":"Niederschrift einstimmig genehmigt.",
     **named(ALL_PRE_OCT21, ABS_0923)},
    {"id":"sr_20240923_02","sessionId":"sr_20240923","topicId":None,"date":"2024-09-23",
     "title":"B-Plan 79 GE Unterreit – Entwurfsbilligung",
     "text":"Der Stadtrat billigt den Entwurf des B-Plans 79 (GE Unterreit) mit 12:7 Stimmen.",
     **anon(12, 7, 6)},
    {"id":"sr_20240923_03","sessionId":"sr_20240923","topicId":None,"date":"2024-09-23",
     "title":"B-Plan 79 Unterreit – Lärmschutzwand erforderlich",
     "text":"Eine Lärmschutzwand entlang ST 2350 wird erforderlich (16:3).",
     **anon(16, 3, 6)},
    {"id":"sr_20240923_04","sessionId":"sr_20240923","topicId":None,"date":"2024-09-23",
     "title":"Mietkonditionen Böhmerwaldstr. – Neuvermietung 11,50 €/m²",
     "text":"Neue Miete auf 11,50 €/m² festgesetzt; Tiefgarage 25 €/Monat (12:7).",
     **anon(12, 7, 6)},
    {"id":"sr_20240923_05","sessionId":"sr_20240923","topicId":None,"date":"2024-09-23",
     "title":"Mietkonditionen Böhmerwaldstr. – Auslaufen Mietabsenkung",
     "text":"Bestehende Mietabsenkungen laufen zum 01.04.2025 aus; Mieten künftig 10 €/m² (18:1).",
     **anon(18, 1, 6)},
    {"id":"sr_20240923_06","sessionId":"sr_20240923","topicId":None,"date":"2024-09-23",
     "title":"Verkaufsoffener Sonntag 20.10.2024","text":"Verordnung beschlossen (18:1).",
     **anon(18, 1, 6)},
    {"id":"sr_20240923_07","sessionId":"sr_20240923","topicId":"t17","date":"2024-09-23",
     "title":"Sanierung Rathaus – Fassade und 1./2. OG",
     "text":"Verwaltung wird einstimmig beauftragt, Fachplaner für Kostenberechnung und Planung zu beauftragen.",
     **named(ALL_PRE_OCT21, ABS_0923)},
]

# === SR 2024-10-07 ===========================================================
# Vote 3 yes=17 (3 extra absent unknown – keep anonymous)
# Votes 5,6,8 yes=19/20 (close to 25-5=20, but vote 5 shows 19 = 1 partial absent)
ABS_1007 = ["hadersdorfer", "becher_j", "beubl", "gruebl", "heinz"]
new_votes += [
    {"id":"sr_20241007_01","sessionId":"sr_20241007","topicId":None,"date":"2024-10-07",
     "title":"Genehmigung Niederschrift StR 02.09.2024","text":"Niederschrift einstimmig genehmigt.",
     **anon(17, 0, 8)},
    {"id":"sr_20241007_02","sessionId":"sr_20241007","topicId":"t13","date":"2024-10-07",
     "title":"Vorbereitende Untersuchungen Innenstadt–Bahnhof",
     "text":"Der Stadtrat nimmt den Entwurf der Vorbereitenden Untersuchungen zur Kenntnis und beauftragt die Verwaltung mit TÖB- und Öffentlichkeitsbeteiligung.",
     **anon(19, 0, 6)},
    {"id":"sr_20241007_03","sessionId":"sr_20241007","topicId":None,"date":"2024-10-07",
     "title":"Vermietungskonditionen Sonnensiedlung 1",
     "text":"Miete 11,50 €/m² für die 5 Wohneinheiten der neuen Anlage festgesetzt.",
     **named(ALL_PRE_OCT21, ABS_1007)},
    {"id":"sr_20241007_04","sessionId":"sr_20241007","topicId":"t7","date":"2024-10-07",
     "title":"Überplanmäßige Ausgaben Betriebsstrom",
     "text":"Genehmigung von 160.000 € überplanmäßiger Ausgaben für Betriebsstromkosten (Energiekrise).",
     **named(ALL_PRE_OCT21, ABS_1007)},
]

# === SR 2024-10-21 (transition) ==============================================
ABS_1021_PRE = ["hadersdorfer", "fincke", "haberl", "reif", "stanglmaier", "becher_j", "kaestl", "hobmaier"]
ABS_1021_POST = ["hadersdorfer", "fincke", "haberl", "reif"]
new_votes += [
    {"id":"sr_20241021_01","sessionId":"sr_20241021","topicId":None,"date":"2024-10-21",
     "title":"Genehmigung Niederschriften (BA 15.07., StR 23.09.2024)",
     "text":"Niederschriften einstimmig genehmigt.",
     **anon(17, 0, 8)},
    {"id":"sr_20241021_02","sessionId":"sr_20241021","topicId":None,"date":"2024-10-21",
     "title":"Niederlegung Mandat Grübl – Hobmaier rückt nach",
     "text":"Niederlegung des Mandats von StR Grübl wird festgestellt; Michael Hobmaier rückt als Listennachfolger nach.",
     **anon(17, 0, 8)},
    {"id":"sr_20241021_03","sessionId":"sr_20241021","topicId":None,"date":"2024-10-21",
     "title":"Schaffung Stelle Jugendreferent",
     "text":"Schaffung der Funktion Jugendreferent (15:2).",
     **anon(15, 2, 8)},
    {"id":"sr_20241021_04","sessionId":"sr_20241021","topicId":None,"date":"2024-10-21",
     "title":"Berufung Grübl als Jugendreferent",
     "text":"Julian Grübl wird einstimmig zum Jugendreferenten berufen.",
     **anon(17, 0, 8)},
    {"id":"sr_20241021_05","sessionId":"sr_20241021","topicId":None,"date":"2024-10-21",
     "title":"Aufwandsentschädigung Jugendreferent",
     "text":"Monatliche Aufwandsentschädigung in Höhe der Referentenpauschale festgesetzt.",
     **anon(17, 0, 8)},
    {"id":"sr_20241021_06","sessionId":"sr_20241021","topicId":None,"date":"2024-10-21",
     "title":"Neubesetzung Ausschüsse / AR Kläranlage",
     "text":"Hobmaier ersetzt Grübl im Aufsichtsrat Kläranlage; weitere Besetzungsänderungen gemäß Anlage.",
     **anon(17, 0, 8)},
    {"id":"sr_20241021_07","sessionId":"sr_20241021","topicId":None,"date":"2024-10-21",
     "title":"B-Plan 66 Oberes Gereut Nordost – Verfahrenswechsel",
     "text":"Wechsel ins Regelverfahren beschlossen; bisherige Auslegung gilt als § 3/§ 4 Abs. 1 BauGB.",
     **anon(17, 0, 8)},
    {"id":"sr_20241021_08","sessionId":"sr_20241021","topicId":"t7","date":"2024-10-21",
     "title":"Hebesatz Grundsteuer A 2025",
     "text":"Anhebung Grundsteuer A auf 390 % (12:6).",
     **anon(12, 6, 7)},
    {"id":"sr_20241021_09","sessionId":"sr_20241021","topicId":"t7","date":"2024-10-21",
     "title":"Hebesatzsatzung 2025",
     "text":"Grundsteuer A 390 %, B 400 %, Gewerbesteuer 380 % (Schlussabstimmung).",
     **anon(18, 0, 7)},
    {"id":"sr_20241021_10","sessionId":"sr_20241021","topicId":None,"date":"2024-10-21",
     "title":"6 Sozialwohnungen Unterreiterweg 13 – Bauauftrag",
     "text":"Bau von 6 Sozialwohnungen für 2025 beschlossen.",
     **anon(18, 0, 7)},
    {"id":"sr_20241021_11","sessionId":"sr_20241021","topicId":"t16","date":"2024-10-21",
     "title":"Hallenbad Öffnungszeiten",
     "text":"Vorläufige Öffnungszeiten festgesetzt: Mo geschlossen, Di–Fr 7–20/21 Uhr, Sa/So 9–18 Uhr (19:1).",
     **anon(19, 1, 5)},
    {"id":"sr_20241021_12","sessionId":"sr_20241021","topicId":"t16","date":"2024-10-21",
     "title":"Hallenbad Gebühren und Tarife",
     "text":"Gebührenstruktur und Tarifordnung beschlossen; Verwaltung prüft 2-Stunden-Rabatt-Ticket.",
     **anon(20, 0, 5)},
]

# === SR 2024-11-04 ===========================================================
# absent: becher_j, heinz (2) → 23 voters; vote 7 yes=12 no=9 = 21 voters; 4 absent total
ABS_1104 = ["becher_j", "heinz"]
ABS_1104_v7 = ["becher_j", "heinz"]  # vote 7 had 21 total, 4 absent; 2 extra unknown
new_votes += [
    {"id":"sr_20241104_01","sessionId":"sr_20241104","topicId":"t6","date":"2024-11-04",
     "title":"Flächennutzungsplan-Änderung – Schul-/Sportflächen",
     "text":"Flächen 703 und 704/6 (Gemarkung Moosburg) werden im FNP als Gemeinbedarfsfläche Schule/Sport ausgewiesen.",
     **anon(21, 0, 4)},
    {"id":"sr_20241104_02","sessionId":"sr_20241104","topicId":None,"date":"2024-11-04",
     "title":"Vorbescheid MFH Mainburger Str. 5 – Anhörung Ersetzung Einvernehmen",
     "text":"Stadtrat lehnt Bauvorhaben einstimmig ab; Maß baulicher Nutzung nicht ortstypisch.",
     **anon(21, 0, 4)},
    {"id":"sr_20241104_03","sessionId":"sr_20241104","topicId":None,"date":"2024-11-04",
     "title":"Vorbescheid MFH 12 WE Bahnhofstr. 60 – Anhörung Ersetzung Einvernehmen",
     "text":"Drei-geschossiges Bauvorhaben fügt sich nicht in Eigenart ein (19:2).",
     **anon(19, 2, 4)},
    {"id":"sr_20241104_04","sessionId":"sr_20241104","topicId":None,"date":"2024-11-04",
     "title":"Straßenname „Semptanger\"",
     "text":"Innere Erschließungsstraße erhält Namen „Semptanger\".",
     **anon(21, 0, 4)},
    {"id":"sr_20241104_05","sessionId":"sr_20241104","topicId":"t16","date":"2024-11-04",
     "title":"Hallenbad – Freier Eintritt Kinder Weihnachtsferien (vertagt)",
     "text":"Antrag StRin Beibl auf kostenlosen Hallenbadeintritt für Kinder/Jugendliche in den Weihnachtsferien wird auf Januar vertagt (12:9).",
     **anon(12, 9, 4)},
]

# === SR 2024-11-18 ===========================================================
# session-absent: heinz, reif, tristl. Late arrivals: becher_j 18:10, gruber 18:08, kaestl 18:13, von_pressentin 18:15.
# vote 4 (Genehmigung) 22 yes 3 absent: all partials there (22 = 25-3)
# vote 6 (Autohaus) 17 yes 8 absent: 5 brief (becher_j, von_pressentin, lauterbach, weber, kaestl)
# vote 7 (Rücklagen) 20 yes 5 absent: 2 brief (becher_j, kaestl)
# vote 8 (DAV) 22 yes 3 absent: all there
ABS_1118 = ["heinz", "reif", "tristl"]
ABS_1118_v6 = ABS_1118 + ["becher_j", "von_pressentin", "lauterbach", "weber", "kaestl"]
ABS_1118_v7 = ABS_1118 + ["becher_j", "kaestl"]
new_votes += [
    {"id":"sr_20241118_01","sessionId":"sr_20241118","topicId":None,"date":"2024-11-18",
     "title":"Genehmigung Niederschriften (BA 30.09., StR 07.10. + 21.10.)",
     "text":"Niederschriften einstimmig genehmigt.",
     **named(ALL_POST_OCT21, ABS_1118)},
    {"id":"sr_20241118_02","sessionId":"sr_20241118","topicId":None,"date":"2024-11-18",
     "title":"Autohaus-Erweiterung Sempt 7",
     "text":"Gemeindliches Einvernehmen für Lager-/Servicehalle des Autohauses erteilt.",
     **named(ALL_POST_OCT21, ABS_1118_v6)},
    {"id":"sr_20241118_03","sessionId":"sr_20241118","topicId":"t7","date":"2024-11-18",
     "title":"Rücklagenbildung Regiebetriebe",
     "text":"BgA-Gewinne werden vollständig in Rücklagen eingestellt; weitere Beschlüsse nach Jahresabschluss.",
     **named(ALL_POST_OCT21, ABS_1118_v7)},
    {"id":"sr_20241118_04","sessionId":"sr_20241118","topicId":None,"date":"2024-11-18",
     "title":"Zuschuss DAV Kletter-/Boulderhalle",
     "text":"Stadt unterstützt DAV-Sektion mit 20 % der förderfähigen Baukosten (max. ca. 292.000 €).",
     **named(ALL_POST_OCT21, ABS_1118)},
    {"id":"sr_20241118_05","sessionId":"sr_20241118","topicId":None,"date":"2024-11-18",
     "title":"Kläranlage GmbH – Satzungsänderung Nachhaltigkeitsbericht",
     "text":"Befreiung von Nachhaltigkeitsberichtspflicht (§ 289b ff HGB), sofern nicht gesetzlich gefordert.",
     **named(ALL_POST_OCT21, ABS_1118)},
]

# === HVFA 2024-11-28 =========================================================
new_votes += [
    {"id":"hvfa_20241128_01","sessionId":"hvfa_20241128","topicId":"t10","date":"2024-11-28",
     "title":"Antrag Seniorenbeirat – Amtsblatt-Verteilung (abgelehnt)",
     "text":"HVFA lehnt Verteilung eines kommunalen Amtsblatts an alle Haushalte ab; Aufwand und Kosten nicht verhältnismäßig.",
     **anon(8, 0, 0)},
]

# === SR 2024-12-02 ===========================================================
ABS_1202 = ["stanglmaier", "becher_a", "heinz", "reif", "kaestl", "fincke"]
new_votes += [
    {"id":"sr_20241202_01","sessionId":"sr_20241202","topicId":None,"date":"2024-12-02",
     "title":"Genehmigung Niederschrift StR 04.11.2024","text":"Niederschrift einstimmig genehmigt.",
     **named(ALL_POST_OCT21, ABS_1202)},
    {"id":"sr_20241202_02","sessionId":"sr_20241202","topicId":None,"date":"2024-12-02",
     "title":"BayKIT e.G. – Mitgliedschaft",
     "text":"Stadt tritt der bayerischen kommunalen IT-Genossenschaft bei (Einmalige 1.000 €, jährliche Beiträge).",
     **named(ALL_POST_OCT21, ABS_1202)},
]

# === BPU 2025-01-16 ==========================================================
# 12 BPU members. Substitutes: stanglmaier→becher_j. Absent: linz_karin (sub weber also absent → seat empty)
# Vote 3.1 (10:0): hadersdorfer not yet (ab 19:15) → 10 voters
# Votes 3.2+ (11 total or close): hadersdorfer arrived → 11 voters
BPU_0116_REGS = ["dollinger", "hadersdorfer", "becher_j", "beibl", "beubl",
                "hobmaier", "kieninger", "linz_kilian", "reif", "tristl", "welter"]
BPU_0116_EARLY = [m for m in BPU_0116_REGS if m != "hadersdorfer"]
new_votes += [
    {"id":"bpu_20250116_01","sessionId":"bpu_20250116","topicId":None,"date":"2025-01-16",
     "title":"Abgrabungsrecht Grube Stünzbach – Tektur",
     "text":"Einvernehmen für Tektur und Aufwertung des Abbaugebiets erteilt.",
     **bpu_named(BPU_0116_EARLY, ["hadersdorfer", "linz_karin"])},
    {"id":"bpu_20250116_02","sessionId":"bpu_20250116","topicId":None,"date":"2025-01-16",
     "title":"3. Wohneinheit Thalbacher Str. 85 – Einvernehmen verweigert",
     "text":"Einvernehmen verweigert; Befreiung würde Grundzüge des Bebauungsplans berühren (10:1).",
     **anon(10, 1, 1)},
    {"id":"bpu_20250116_03","sessionId":"bpu_20250116","topicId":None,"date":"2025-01-16",
     "title":"Wohnanlage Stadtwaldstr. 9 – Einvernehmen erteilt (abgelehnt)",
     "text":"Antrag, Einvernehmen für 21-WE-Wohnanlage zu erteilen, wird abgelehnt (3:8).",
     **anon(3, 8, 1, rejected=True)},
    {"id":"bpu_20250116_04","sessionId":"bpu_20250116","topicId":None,"date":"2025-01-16",
     "title":"Wohnanlage Stadtwaldstr. 9 – Einvernehmen verweigert",
     "text":"Einvernehmen verweigert; Gesamtlänge Baukörper 1 fügt sich nicht in Umgebung ein (8:3).",
     **anon(8, 3, 1)},
    {"id":"bpu_20250116_05","sessionId":"bpu_20250116","topicId":None,"date":"2025-01-16",
     "title":"Lagerhalle Oberpolln 2","text":"Einvernehmen einstimmig erteilt.",
     **bpu_named(BPU_0116_REGS, ["linz_karin"])},
    {"id":"bpu_20250116_06","sessionId":"bpu_20250116","topicId":None,"date":"2025-01-16",
     "title":"Hofladen Vorbescheid Amperstr. 6","text":"Einvernehmen einstimmig erteilt.",
     **bpu_named(BPU_0116_REGS, ["linz_karin"])},
    {"id":"bpu_20250116_07","sessionId":"bpu_20250116","topicId":None,"date":"2025-01-16",
     "title":"Fahrzeughalle FFW","text":"Gemeindliches Einvernehmen einstimmig erteilt.",
     **bpu_named(BPU_0116_REGS, ["linz_karin"])},
    {"id":"bpu_20250116_08","sessionId":"bpu_20250116","topicId":None,"date":"2025-01-16",
     "title":"Vorbescheid MFH Moosstr. 15b – Einvernehmen verweigert",
     "text":"Einvernehmen einstimmig verweigert; Baukörper überschreitet Ausdehnung und Höhe.",
     **bpu_named(BPU_0116_REGS, ["linz_karin"])},
]

# === SR 2025-01-20 ===========================================================
# Active = ALL_POST_OCT21 (beubl active, marcus not yet sworn in)
# Session absent (full): stanglmaier, linz_karin, von_pressentin (3) → 22 normal present
# Partial: hadersdorfer 18:10, becher_j 18:40, beibl bis 20:30, kaestl ab 20:25
# Vote 3 (19:5 = 19 voters, 6 absent): early - hadersdorfer/becher_j/kaestl not yet
# Vote 4 (21:4): hadersdorfer arrived but becher_j and kaestl still not (21 = 25-4)
# Votes 7,8 (21:4): same time period
# Vote 9 (19:6): later - beibl gone (20:30), kaestl arrived (20:25)? 25-19=6. With beibl gone and kaestl there would be 23 - 2 brief = 21. doesn't match. Likely both gruber and fincke briefly absent + beibl gone
ABS_0120_v3 = ["stanglmaier", "linz_karin", "von_pressentin", "hadersdorfer", "becher_j", "kaestl"]
ABS_0120_v4 = ["stanglmaier", "linz_karin", "von_pressentin", "becher_j", "kaestl"]   # hadersdorfer arrived
ABS_0120_v9 = ["stanglmaier", "linz_karin", "von_pressentin", "beibl", "gruber", "fincke"]  # speculative
new_votes += [
    {"id":"sr_20250120_01","sessionId":"sr_20250120","topicId":None,"date":"2025-01-20",
     "title":"Genehmigung Niederschriften (HVFA 28.11. + StR 18.11., 02.12., 09.12.2024)",
     "text":"Niederschriften einstimmig genehmigt.",
     **named(ALL_POST_OCT21, ABS_0120_v3)},
    {"id":"sr_20250120_02","sessionId":"sr_20250120","topicId":"t6","date":"2025-01-20",
     "title":"TG-Grundschule – Vorstellung Entwurfsplanung",
     "text":"Entwurfsplanung wird zustimmend zur Kenntnis genommen; Verwaltung wird mit Kostenberechnung und Untersuchung Parkdeck-Alternative beauftragt.",
     **named(ALL_POST_OCT21, ABS_0120_v4)},
    {"id":"sr_20250120_03","sessionId":"sr_20250120","topicId":None,"date":"2025-01-20",
     "title":"B-Plan 81 MI Moos – Verfahrenseinstellung",
     "text":"Bauleitplanverfahren wird eingestellt.",
     **named(ALL_POST_OCT21, ABS_0120_v4)},
    {"id":"sr_20250120_04","sessionId":"sr_20250120","topicId":None,"date":"2025-01-20",
     "title":"4. Änderung B-Plan 50 Degernpoint – Verfahrenswechsel",
     "text":"Wechsel ins Regelverfahren mit flexibler Parzellierung; SWM-Umspannwerk eingeplant.",
     **named(ALL_POST_OCT21, ABS_0120_v4)},
    {"id":"sr_20250120_05","sessionId":"sr_20250120","topicId":None,"date":"2025-01-20",
     "title":"4. Änderung B-Plan 50 Degernpoint – Aufstellungsbeschluss",
     "text":"Aufstellungsbeschluss; frühzeitige Öffentlichkeits- und Behördenbeteiligung wird angeordnet.",
     **named(ALL_POST_OCT21, ABS_0120_v4)},
    {"id":"sr_20250120_06","sessionId":"sr_20250120","topicId":None,"date":"2025-01-20",
     "title":"Umlegungsverfahren Degernpoint II – Anordnung",
     "text":"Umlegungsverfahren nach BauGB angeordnet; Befugnis auf ADBV Freising übertragen.",
     **named(ALL_POST_OCT21, ABS_0120_v4)},
    {"id":"sr_20250120_07","sessionId":"sr_20250120","topicId":None,"date":"2025-01-20",
     "title":"Umlegungsverfahren Degernpoint II – Kostenverteilung",
     "text":"Stadt trägt Verfahrenskosten; Verfahrensbeteiligte erstatten anteilige Kosten.",
     **named(ALL_POST_OCT21, ABS_0120_v4)},
    {"id":"sr_20250120_08","sessionId":"sr_20250120","topicId":"t7","date":"2025-01-20",
     "title":"Übertragung Haushaltsreste 2024",
     "text":"Übertragung der Haushaltsreste 2024 gemäß Beschlussvorschlag beschlossen.",
     **anon(19, 0, 6)},  # ambiguous brief absences
]

# === SR 2025-04-10 ===========================================================
# Hadersdorfer presides (Dollinger absent). Active = ALL_POST_MAR2025 (marcus in, beubl out)
# absent: dollinger, gruber, hobmaier, kaestl, lauterbach, weber (6)
ABS_0410 = ["dollinger", "gruber", "hobmaier", "kaestl", "lauterbach", "weber"]
new_votes += [
    {"id":"sr_20250410_01","sessionId":"sr_20250410","topicId":None,"date":"2025-04-10",
     "title":"Genehmigung Niederschriften (StR 24.02., BPU 17.03.2025)",
     "text":"Niederschriften einstimmig genehmigt.",
     **named(ALL_POST_MAR2025, ABS_0410)},
    {"id":"sr_20250410_02","sessionId":"sr_20250410","topicId":None,"date":"2025-04-10",
     "title":"E-Auto Parken – 2. Änderung Parkgebühren-Satzung",
     "text":"Anpassung der Parkgebührenverordnung und Satzung Parkhaus/Parkplatz Am Bahnhof beschlossen (15:4).",
     **anon(15, 4, 6)},
    {"id":"sr_20250410_03","sessionId":"sr_20250410","topicId":None,"date":"2025-04-10",
     "title":"E-Auto Parken – Protest gegen Staatsregierung",
     "text":"Protestbeschluss gegen die Staatsregierung; Forderung nach Ausgleich entgangener Einnahmen und unbürokratischem Verfahren.",
     **named(ALL_POST_MAR2025, ABS_0410)},
    {"id":"sr_20250410_04","sessionId":"sr_20250410","topicId":None,"date":"2025-04-10",
     "title":"Erhöhung Parkgebühren Bahnhof/Stadionstraße",
     "text":"1. Änderung Parkgebührenverordnung – Erhöhung der Gebühren im Bahnhofbereich.",
     **anon(18, 0, 7)},  # different absent count: 25-18=7
]

# === SR 2025-04-28 ===========================================================
# Active = ALL_POST_MAR2025; absent: gruber, heinz, hobmaier, von_pressentin, welter (5)
# Partials: becher_j 19:15, kaestl 19:17, linz_karin bis 21:15
# Vote 3 (18:7): becher_j, kaestl not yet → 25-7=18 ✓
# Vote 4 (18:7): same
# Vote 5 (18 yes 2 no 5 absent): 18+2=20 → 5 absent (just session) → maybe later, all there. But only 20 voted means 5 absent. With session absent 5 = 20 voters ✓
# Vote 6a/6b/6 (rejected/passing): yes+no+absent = 25
ABS_0428_v3 = ["gruber", "heinz", "hobmaier", "von_pressentin", "welter", "becher_j", "kaestl"]
ABS_0428_late = ["gruber", "heinz", "hobmaier", "von_pressentin", "welter"]
new_votes += [
    {"id":"sr_20250428_01","sessionId":"sr_20250428","topicId":None,"date":"2025-04-28",
     "title":"Genehmigung Niederschrift StR 24.03.2025","text":"Niederschrift einstimmig genehmigt.",
     **named(ALL_POST_MAR2025, ABS_0428_v3)},
    {"id":"sr_20250428_02","sessionId":"sr_20250428","topicId":None,"date":"2025-04-28",
     "title":"Plakatanschlagtafeln Jägerstr. 2 – Einvernehmen verweigert",
     "text":"Einvernehmen einstimmig verweigert; Nähe zur Ampelkreuzung beeinträchtigt Verkehrssicherheit.",
     **named(ALL_POST_MAR2025, ABS_0428_v3)},
    {"id":"sr_20250428_03","sessionId":"sr_20250428","topicId":None,"date":"2025-04-28",
     "title":"B-Plan Isarstraße – Antrag Deutinger abgelehnt",
     "text":"Antrag auf Aufstellung eines B-Plans für Wohnbebauung an der Isarstraße abgelehnt (18:2).",
     **anon(18, 2, 5, rejected=True)},
    {"id":"sr_20250428_04","sessionId":"sr_20250428","topicId":"t12","date":"2025-04-28",
     "title":"Badegebühren Freibad – Änderungsantrag Marcus (abgelehnt)",
     "text":"Antrag StR Marcus auf Einzelpreise (Erw. 5 €, Kinder 2,50 €) wird abgelehnt (2:18).",
     **anon(2, 18, 5, rejected=True)},
    {"id":"sr_20250428_05","sessionId":"sr_20250428","topicId":"t12","date":"2025-04-28",
     "title":"Badegebühren Freibad – Änderungsantrag Stanglmaier",
     "text":"Antrag Dr. Stanglmaier: Abendkarte ab 17 Uhr (statt 18 Uhr); angenommen (19:1).",
     **anon(19, 1, 5)},
    {"id":"sr_20250428_06","sessionId":"sr_20250428","topicId":"t12","date":"2025-04-28",
     "title":"Badegebührenordnung Freibad",
     "text":"Beschluss der Badegebührenordnung mit Stanglmaier-Änderung; Variante A mit günstigeren Saisonkarten (19:1).",
     **anon(19, 1, 5)},
]

# === BPU 2025-05-22 ==========================================================
# Active BPU members: dollinger (chair), stanglmaier (vice 2), beibl, marcus(SPD seat now), reif, tristl, welter, linz_kilian
# Subs present: lauterbach (kieninger), weber (linz_karin)
# Absent: hadersdorfer (with sub heinz also absent → vice 1 seat empty), hobmaier (with sub gruber also absent → seat empty)
# 10 voters present
BPU_0522_VOTERS = ["dollinger", "stanglmaier", "beibl", "marcus", "reif", "tristl",
                  "welter", "linz_kilian", "lauterbach", "weber"]
new_votes += [
    {"id":"bpu_20250522_01","sessionId":"bpu_20250522","topicId":"t4","date":"2025-05-22",
     "title":"Tempo 30 Neustadtstraße",
     "text":"Geschwindigkeitsbeschränkung 30 km/h von Driescherstraße bis Schlesierstraße in beide Richtungen einstimmig zugestimmt.",
     **bpu_named(BPU_0522_VOTERS, ["hadersdorfer", "hobmaier"])},
    {"id":"bpu_20250522_02","sessionId":"bpu_20250522","topicId":"t4","date":"2025-05-22",
     "title":"Fußgängerüberweg Sudetenlandstraße – abgelehnt",
     "text":"Antrag der Initiative auf Errichtung eines Fußgängerüberwegs wird abgelehnt (9:1).",
     **anon(9, 1, 2, rejected=True)},
    {"id":"bpu_20250522_03","sessionId":"bpu_20250522","topicId":"t4","date":"2025-05-22",
     "title":"Fahrradstraße Stadtbadstraße – abgelehnt",
     "text":"Antrag auf Fahrradstraße und Zufahrtssperrung des Parkplatzes wird einstimmig abgelehnt.",
     **bpu_named(BPU_0522_VOTERS, ["hadersdorfer", "hobmaier"])},
    {"id":"bpu_20250522_04","sessionId":"bpu_20250522","topicId":None,"date":"2025-05-22",
     "title":"Doppelhaushälften Auenstr. 32/32a","text":"Einvernehmen einstimmig erteilt; Stellplatznachweis erforderlich.",
     **bpu_named(BPU_0522_VOTERS, ["hadersdorfer", "hobmaier"])},
    {"id":"bpu_20250522_05","sessionId":"bpu_20250522","topicId":None,"date":"2025-05-22",
     "title":"Doppelhaushälften Auenstr. 34/34a","text":"Einvernehmen einstimmig erteilt.",
     **bpu_named(BPU_0522_VOTERS, ["hadersdorfer", "hobmaier"])},
    {"id":"bpu_20250522_06","sessionId":"bpu_20250522","topicId":None,"date":"2025-05-22",
     "title":"MFH Merkurstr. 8 (6 WE) – Einvernehmen verweigert",
     "text":"Einvernehmen einstimmig verweigert; Wandhöhe und Dachneigung sowie nicht-konforme Fahrradabstellplätze.",
     **bpu_named(BPU_0522_VOTERS, ["hadersdorfer", "hobmaier"])},
    {"id":"bpu_20250522_07","sessionId":"bpu_20250522","topicId":None,"date":"2025-05-22",
     "title":"MFH Bahnhofstr. 60 (12 WE) – Einvernehmen verweigert",
     "text":"GRZ/GFZ und 3-geschossigkeit fügen sich nicht in Eigenart ein (9:1).",
     **anon(9, 1, 2)},
    {"id":"bpu_20250522_08","sessionId":"bpu_20250522","topicId":None,"date":"2025-05-22",
     "title":"MFH Mainburger Str. 5 (8 WE) – Einvernehmen verweigert",
     "text":"Einvernehmen einstimmig verweigert; tatsächliche Grundfläche fügt sich nicht in Eigenart.",
     **bpu_named(BPU_0522_VOTERS, ["hadersdorfer", "hobmaier"])},
    {"id":"bpu_20250522_09","sessionId":"bpu_20250522","topicId":None,"date":"2025-05-22",
     "title":"MFH Neustadtstr. 17 – Einvernehmen erteilt (abgelehnt)",
     "text":"Antrag, das Einvernehmen zu erteilen, wird einstimmig abgelehnt (0:10).",
     **anon(0, 10, 2, rejected=True)},
    {"id":"bpu_20250522_10","sessionId":"bpu_20250522","topicId":None,"date":"2025-05-22",
     "title":"MFH Neustadtstr. 17 – Einvernehmen verweigert",
     "text":"Einvernehmen einstimmig verweigert; Maß baulicher Nutzung, Versiegelung, Stellplatz-/Spielplatzpflicht.",
     **bpu_named(BPU_0522_VOTERS, ["hadersdorfer", "hobmaier"])},
    {"id":"bpu_20250522_11","sessionId":"bpu_20250522","topicId":"t13","date":"2025-05-22",
     "title":"Lebendige Zentren – Giebelsanierung Herrnstr. 23",
     "text":"Bewilligungsantrag zur Städtebauförderung „Lebendige Zentren\"; pauschal 20.000 € Förderung, Stadt-Eigenanteil 8.000 €.",
     **bpu_named(BPU_0522_VOTERS, ["hadersdorfer", "hobmaier"])},
]

# ============================================================================
# Convert sr_20241216 anonymous votes to named (now that we have absent list)
# absent: becher_a, beubl, heinz, hobmaier, reif, tristl
# But beubl was active till 2025-03 so was on council, hobmaier joined Oct 2024 so on council.
# But session predates marcus joining. Active = ALL_POST_OCT21
ABS_1216 = ["becher_a", "beubl", "heinz", "hobmaier", "reif", "tristl"]
SR_1216_CONVERSIONS = {
    "sr_20241216_01": named(ALL_POST_OCT21, ABS_1216),
    "sr_20241216_02": named(ALL_POST_OCT21, ABS_1216),
    "sr_20241216_03": named(ALL_POST_OCT21, ABS_1216),
}
# Also add "absent" array to sr_20241216 session
SR_1216_ABSENT = ABS_1216

# ============================================================================
# TOPIC UPDATES
# ============================================================================
# t7 rename, t12 rename, t16 new, t17 new, history extensions
TOPIC_RENAMES = {
    "t7": ("Haushalt",
           "Jahreshaushaltssatzungen, Jahresrechnungen, Hebesätze und über-/außerplanmäßige Ausgaben der Stadt Moosburg. Die Stadt steht angesichts der Großprojekte vor einer angespannten Finanzlage."),
    "t12": ("Freibad",
            "Das städtische Freibad an der Stadtbadstraße. Sanierungsplanung, Bundesförderung sowie Anpassungen der Badegebühren."),
}

NEW_TOPICS = [
    {
        "id": "t16",
        "title": "Hallenbad",
        "tags": ["sports", "infrastructure"],
        "image": None,
        "summary": "Eröffnungsbetrieb des neuen Hallenbads. Öffnungszeiten, Tarife und Benutzungsordnung wurden festgelegt; immer wieder beantragte kostenlose Eintritte für Kinder in Ferienzeiten werden kontrovers diskutiert.",
        "history": [
            {"date": "2024-10-21","type": "vote","title": "Öffnungszeiten festgelegt",
             "text":"Vorläufige Öffnungszeiten beschlossen (19:1): Mo geschlossen, Di–Fr 7–20/21 Uhr, Sa/So 9–18 Uhr.",
             "sessionId":"sr_20241021","voteId":"sr_20241021_11"},
            {"date": "2024-10-21","type": "vote","title": "Gebühren und Tarife beschlossen",
             "text":"Gebühren- und Tarifordnung einstimmig beschlossen; Verwaltung soll 2-Stunden-Rabatt-Ticket prüfen.",
             "sessionId":"sr_20241021","voteId":"sr_20241021_12"},
            {"date": "2024-11-04","type": "vote","title": "Antrag freier Kinder-Eintritt vertagt",
             "text":"Antrag StRin Beibl auf kostenlosen Eintritt für Kinder/Jugendliche in den Weihnachtsferien wird auf Januar vertagt (12:9).",
             "sessionId":"sr_20241104","voteId":"sr_20241104_05"},
            {"date": "2024-12-16","type": "vote","title": "Haus- und Badeordnung beschlossen",
             "text":"Stadtrat beschließt einstimmig die Haus- und Badeordnung nach DGfdB-Vorlage.",
             "sessionId":"sr_20241216","voteId":"sr_20241216_03"},
            {"date": "2025-02-24","type": "vote","title": "Antrag freier Kinder-Eintritt abgelehnt",
             "text":"Antrag auf kostenlosen Hallenbadeintritt für Kinder in den Faschings-/Osterferien wird abgelehnt (9:10).",
             "sessionId":"sr_20250224","voteId":"sr_20250224_01"},
        ],
    },
    {
        "id": "t17",
        "title": "Rathaus-Sanierung",
        "tags": ["building", "infrastructure"],
        "image": None,
        "summary": "Mehrjähriges Sanierungsprojekt am historischen Rathaus: Fassade sowie 1. und 2. Obergeschoss in mehreren Bauabschnitten. Die Verwaltung wurde mit Planung und Kostenberechnung beauftragt.",
        "history": [
            {"date": "2024-09-23","type": "vote","title": "Sanierung Rathaus – Fachplaner beauftragt",
             "text":"Verwaltung wird einstimmig beauftragt, Fachplaner für Kostenberechnung und Planung von Fassade und 1./2. OG einzusetzen.",
             "sessionId":"sr_20240923","voteId":"sr_20240923_07"},
            {"date": "2025-03-24","type": "vote","title": "Rathaus 3. BA – Kostenberechnung",
             "text":"Kostenberechnung und Planung mit Gesamtkosten 3.988.000 € einstimmig zustimmend zur Kenntnis genommen.",
             "sessionId":"sr_20250324","voteId":"sr_20250324_07"},
        ],
    },
]

# History entries to insert into existing topics
HISTORY_INSERTS = {
    "t5": [
        {"date":"2024-09-02","type":"vote","title":"B-Plan 77 als Satzung beschlossen",
         "text":"Der Stadtrat beschließt nach Abwägung aller Stellungnahmen den Bebauungsplan Nr. 77 „Rockermaier Areal\" als Satzung (12:2).",
         "sessionId":"sr_20240902","voteId":"sr_20240902_10"},
    ],
    "t6": [
        {"date":"2024-10-21","type":"committee","title":"Containeranlage als Interimslösung – vertagt",
         "text":"Der Stadtrat vertagt die Entscheidung über eine Containeranlage als Interimslösung während der Sanierung.",
         "sessionId":"sr_20241021"},
        {"date":"2024-11-04","type":"vote","title":"Flächennutzungsplan-Änderung Schul-/Sportflächen",
         "text":"Flurstücke 703 und 704/6 werden im FNP als Gemeinbedarfsfläche Schule/Sport ausgewiesen – Grundlage für die Erweiterung.",
         "sessionId":"sr_20241104","voteId":"sr_20241104_01"},
        {"date":"2025-01-20","type":"vote","title":"Entwurfsplanung vorgestellt",
         "text":"Entwurfsplanung wird zustimmend zur Kenntnis genommen; Verwaltung mit Kostenberechnung und Untersuchung Parkdeck-Alternative beauftragt.",
         "sessionId":"sr_20250120","voteId":"sr_20250120_02"},
    ],
    "t7": [
        {"date":"2024-10-07","type":"vote","title":"Überplanmäßige Ausgaben Betriebsstrom",
         "text":"Genehmigung von 160.000 € überplanmäßiger Ausgaben für gestiegene Betriebsstromkosten.",
         "sessionId":"sr_20241007","voteId":"sr_20241007_04"},
        {"date":"2024-10-21","type":"vote","title":"Hebesatzsatzung 2025",
         "text":"Hebesätze für 2025 festgesetzt: Grundsteuer A 390 % (12:6 angehoben), B 400 %, Gewerbesteuer 380 %.",
         "sessionId":"sr_20241021","voteId":"sr_20241021_09"},
        {"date":"2024-11-18","type":"vote","title":"Rücklagenbildung Regiebetriebe",
         "text":"BgA-Gewinne werden vollständig in Rücklagen eingestellt.",
         "sessionId":"sr_20241118","voteId":"sr_20241118_03"},
        {"date":"2024-12-16","type":"vote","title":"Haushaltssatzung 2025",
         "text":"Stadtrat beschließt einstimmig die Haushaltssatzung 2025 mit allen Anlagen.",
         "sessionId":"sr_20241216","voteId":"sr_20241216_02"},
        {"date":"2025-01-20","type":"vote","title":"Übertragung Haushaltsreste 2024",
         "text":"Haushaltsreste 2024 werden übertragen.",
         "sessionId":"sr_20250120","voteId":"sr_20250120_08"},
        {"date":"2025-06-02","type":"vote","title":"Jahresrechnung 2023 festgestellt",
         "text":"Stadtrat stellt die Jahresrechnung 2023 fest; Bürgermeister Dollinger nimmt wegen persönlicher Beteiligung an der Entlastung nicht teil.",
         "sessionId":"sr_20250602","voteId":"sr_20250602_02"},
        {"date":"2025-06-23","type":"committee","title":"Vorlage Jahresrechnung 2024",
         "text":"Jahresrechnung 2024 wird zur Kenntnisnahme vorgelegt.",
         "sessionId":"sr_20250623"},
    ],
    "t10": [
        {"date":"2025-01-20","type":"vote","title":"Gewerbegebiet Degernpoint – 4. Änderung B-Plan 50",
         "text":"Aufstellungsbeschluss für die 4. Änderung des B-Plans 50 mit flexibler Parzellierung für Handwerk/Gewerbe.",
         "sessionId":"sr_20250120","voteId":"sr_20250120_05"},
    ],
    "t13": [
        {"date":"2024-10-07","type":"vote","title":"Vorbereitende Untersuchungen beschlossen",
         "text":"Vorbereitende Untersuchungen nach §§ 137, 139 BauGB werden beauftragt; TÖB- und Öffentlichkeitsbeteiligung folgen.",
         "sessionId":"sr_20241007","voteId":"sr_20241007_02"},
        {"date":"2025-05-22","type":"vote","title":"Lebendige Zentren – Giebelsanierung Herrnstr. 23",
         "text":"Bauausschuss beschließt im Förderprogramm „Lebendige Zentren\" eine Giebelsanierung an der Herrnstraße 23.",
         "sessionId":"bpu_20250522","voteId":"bpu_20250522_11"},
    ],
    "t12": [  # Freibad: Badegebühren-Anpassungen ergänzen
        {"date":"2025-04-28","type":"vote","title":"Badegebührenordnung 2025 beschlossen",
         "text":"Anpassung der Badegebührenordnung; Abendkarte ab 17 Uhr, Variante A mit günstigeren Saisonkarten (19:1).",
         "sessionId":"sr_20250428","voteId":"sr_20250428_06"},
        {"date":"2025-06-02","type":"vote","title":"Redaktionelle Anpassung Badegebühren",
         "text":"Redaktionelle Anpassung der Badegebührenordnung mit Wirkung zur Saison 2025.",
         "sessionId":"sr_20250602","voteId":"sr_20250602_05"},
    ],
}

# ============================================================================
# APPLY ALL CHANGES
# ============================================================================
def insert_chronologically(history, entry):
    for i, e in enumerate(history):
        if e["date"] > entry["date"]:
            history.insert(i, entry)
            return
    history.append(entry)

# Sessions
with open(f"{BASE}/sessions.json", "r", encoding="utf-8") as f:
    sessions = json.load(f)
existing_sids = {s["id"] for s in sessions}
added = 0
for s in new_sessions:
    if s["id"] not in existing_sids:
        sessions.append(s)
        added += 1
        print(f"+ session {s['id']}")

# Add absent to sr_20241216
for s in sessions:
    if s["id"] == "sr_20241216" and "absent" not in s:
        s["absent"] = SR_1216_ABSENT
        print("  ~ added absent to sr_20241216")

with open(f"{BASE}/sessions.json", "w", encoding="utf-8") as f:
    json.dump(sessions, f, ensure_ascii=False, indent=2)
print(f"sessions.json: +{added}, total {len(sessions)}")

# Votes
with open(f"{BASE}/votes.json", "r", encoding="utf-8") as f:
    votes = json.load(f)
vote_map = {v["id"]: v for v in votes}
added_v = 0
for v in new_votes:
    if v["id"] not in vote_map:
        votes.append(v)
        added_v += 1

# Convert sr_20241216 anonymous votes
for vid, conv in SR_1216_CONVERSIONS.items():
    if vid in vote_map:
        v = vote_map[vid]
        v["type"] = conv["type"]
        v["results"] = conv["results"]
        print(f"  ~ converted {vid} → named")

with open(f"{BASE}/votes.json", "w", encoding="utf-8") as f:
    json.dump(votes, f, ensure_ascii=False, indent=2)
print(f"votes.json: +{added_v}, total {len(votes)}")

# Topics
with open(f"{BASE}/topics.json", "r", encoding="utf-8") as f:
    topics = json.load(f)
topic_map = {t["id"]: t for t in topics}

# Renames
for tid, (new_title, new_summary) in TOPIC_RENAMES.items():
    if tid in topic_map:
        t = topic_map[tid]
        t["title"] = new_title
        t["summary"] = new_summary
        print(f"  ~ renamed {tid} → {new_title}")

# New topics
for nt in NEW_TOPICS:
    if nt["id"] not in topic_map:
        topics.append(nt)
        topic_map[nt["id"]] = nt
        print(f"+ topic {nt['id']} ({nt['title']})")

# History inserts (chronologically)
for tid, entries in HISTORY_INSERTS.items():
    if tid not in topic_map:
        print(f"WARN: topic {tid} not found")
        continue
    t = topic_map[tid]
    existing_keys = set()
    for e in t["history"]:
        existing_keys.add((e["date"], e.get("voteId"), e.get("title")))
    for entry in entries:
        key = (entry["date"], entry.get("voteId"), entry.get("title"))
        if key not in existing_keys:
            insert_chronologically(t["history"], entry)
            print(f"  ~ {tid} += {entry['date']} {entry['title'][:40]}")

with open(f"{BASE}/topics.json", "w", encoding="utf-8") as f:
    json.dump(topics, f, ensure_ascii=False, indent=2)
print(f"topics.json: total {len(topics)}")

print("\nDone.")
