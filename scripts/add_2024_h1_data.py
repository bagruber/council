"""
Integrate 12 sessions from Feb–July 2024 (Stadtrat + BPU).
- Aggregate identical sub-votes (e.g. 15 Stellungnahmen all 21:0) into a single entry.
- Convert clearly unanimous votes to named where attendance is precise.
- Topic updates:
  * Replace t15 (PV Kuttenweide) with broader t15 'Energie & Klimawende'.
  * New topics: t18 Gewerbegebiet Degernpoint, t19 DAV Kletterhalle.
  * Extend t5 Rockermaier, t6 Theresia-Gerhardinger-Grundschule (renamed), t7 Haushalt,
    t8 Schulwegsicherheit, t14 Wachbaracken, t4 Verkehrsberuhigung.
"""
import json

BASE = "c:/Users/bened/Documents/GitHub/bagruber/council/data"

# 25 active members (Feb-Jul 2024): gruebl active, no hobmaier yet
ALL_2024 = [
    "dollinger", "hadersdorfer", "tristl", "weber", "haberl",
    "linz_karin", "heinz",
    "beibl", "stanglmaier", "von_pressentin", "becher_j", "becher_a", "linz_kilian",
    "grundner", "lauterbach", "reif", "kieninger",
    "beubl", "pschorr",
    "gruebl", "gruber",
    "welter", "kaestl", "fincke", "strobl",
]

def yes_list(absent): return [m for m in ALL_2024 if m not in absent]
def named(absent):   return {"type": "named", "results": {"yes": yes_list(absent), "no": [], "absent": list(absent)}}
def anon(y, n, ab, rej=False):
    d = {"type": "anonymous", "results": {"yes": y, "no": n, "absent": ab}}
    if rej: d["result"] = "rejected"
    return d

# ============================================================================
# SESSIONS
# ============================================================================
new_sessions = []

# ── SR 2024-02-19 (3. Sitzung) ───────────────────────────────────────────────
# absent (full): stanglmaier, becher_a, becher_j, tristl (4)
# Late: haberl, gruber, gruebl, beibl, von_pressentin (all by 19:10)
# Vote count 21-0 across the board → consistent with 25-4 = 21 when all late had arrived
new_sessions.append({
    "id": "sr_20240219",
    "date": "2024-02-19",
    "type": "stadtrat",
    "title": "3. Stadtratssitzung – Februar 2024",
    "absent": ["stanglmaier", "becher_a", "becher_j", "tristl"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Genehmigung Niederschrift StR 15.01.2024", "voteId": "sr_20240219_01"},
        {"number": 4, "title": "Bauleitplanung Nr. 80 \"Degernpoint Nordost II\" – Aufstellung (15 Stellungnahmen)",
         "topicId": "t18", "voteId": "sr_20240219_02"},
        {"number": 5, "title": "Erstaufforstungserlaubnis Pfrombach", "voteId": "sr_20240219_03"},
        {"number": 6, "title": "Anfragen", "type": "formal"},
    ]
})

# ── SR 2024-03-04 (4. Sitzung) ───────────────────────────────────────────────
new_sessions.append({
    "id": "sr_20240304",
    "date": "2024-03-04",
    "type": "stadtrat",
    "title": "4. Stadtratssitzung – März 2024",
    "absent": ["beubl", "weber"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Genehmigung Niederschriften (StR 18.12.2023, 01.02.2024)", "voteId": "sr_20240304_01"},
        {"number": 4, "title": "Bauleitplanung Nr. 65 \"Aich Kirchfeldstraße\" – Abwägung Stellungnahmen (16 Sub-Voten)",
         "voteId": "sr_20240304_02"},
        {"number": "4.17", "title": "B-Plan Nr. 65 \"Aich Kirchfeldstraße\" – Satzungsbeschluss (15:7)",
         "voteId": "sr_20240304_03"},
        {"number": "5.1", "title": "Europawahl 2024 – Wahlhelferbonus (abgelehnt)", "voteId": "sr_20240304_04"},
        {"number": "5.2", "title": "Europawahl 2024 – Erfrischungsgeld 40 €", "voteId": "sr_20240304_05"},
        {"number": 6, "title": "Anfragen", "type": "formal"},
    ]
})

# ── BPU 2024-03-14 (1. BPU) ──────────────────────────────────────────────────
# 12 BPU members. Absent: stanglmaier (+ sub becher_j absent), linz_karin (+ sub weber absent), beubl (sub pschorr present)
# Present voters (10): dollinger, hadersdorfer, beibl, gruebl, kieninger, linz_kilian, reif, tristl, welter, pschorr (sub for beubl)
BPU_0314_VOTERS = ["dollinger", "hadersdorfer", "beibl", "gruebl", "kieninger",
                   "linz_kilian", "reif", "tristl", "welter", "pschorr"]
def bpu_0314_named(absent_extra=[]):
    yes = [m for m in BPU_0314_VOTERS if m not in absent_extra]
    return {"type": "named", "results": {"yes": yes, "no": [], "absent": ["stanglmaier", "linz_karin"] + list(absent_extra)}}

new_sessions.append({
    "id": "bpu_20240314",
    "date": "2024-03-14",
    "type": "bpu",
    "title": "1. Sitzung Bau-, Planungs- und Umweltausschuss – März 2024",
    "absent": ["stanglmaier", "linz_karin"],
    "substitutes": [{"member": "beubl", "substitute": "pschorr"}],
    "agenda": [
        {"number": 1, "title": "Mitteilungen", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Bauleitplanung Nr. 56 \"Unteres Gereut\" – Überprüfung abgelehnt", "voteId": "bpu_20240314_01"},
        {"number": "4.1", "title": "Dachgeschoss-Ausbau Bergstr. 27 Pfrombach", "voteId": "bpu_20240314_02"},
        {"number": "4.2", "title": "Doppelhäuser Thalbach Str. 108", "voteId": "bpu_20240314_03"},
        {"number": "4.3", "title": "Dachgeschoss-Ausbau Fasanenstr. 7", "voteId": "bpu_20240314_04"},
        {"number": "4.4a", "title": "Arbeitnehmerwohnheim Sudetenlandstr. 9 – Einvernehmen erteilt (abgelehnt 1:9)",
         "voteId": "bpu_20240314_05"},
        {"number": "4.4b", "title": "Arbeitnehmerwohnheim Sudetenlandstr. 9 – Einvernehmen verweigert (9:1)",
         "voteId": "bpu_20240314_06"},
        {"number": "4.5", "title": "Wohngebäude St.-Georg-Str. 26 Aich", "voteId": "bpu_20240314_07"},
        {"number": "4.6", "title": "Mehrfamilienhaus Mainburger Str. 5 – Einvernehmen verweigert (10:0)",
         "voteId": "bpu_20240314_08"},
        {"number": 5, "title": "Anfragen und Sonstiges", "type": "formal"},
    ]
})

# ── SR 2024-03-18 (5. Sitzung) ───────────────────────────────────────────────
new_sessions.append({
    "id": "sr_20240318",
    "date": "2024-03-18",
    "type": "stadtrat",
    "title": "5. Stadtratssitzung – März 2024",
    "absent": ["beubl", "von_pressentin", "weber"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Genehmigung Niederschrift StR 19.02.2024", "voteId": "sr_20240318_01"},
        {"number": 4, "title": "B-Plan Nr. 77 \"Rockermaier Areal\" – Abwägung Stellungnahmen (21 Sub-Voten)",
         "topicId": "t5", "voteId": "sr_20240318_02"},
        {"number": "4.22a", "title": "Rockermaier – Erneute Auslegung", "topicId": "t5", "voteId": "sr_20240318_03"},
        {"number": "4.22b", "title": "Rockermaier – Planänderungen (Energie, Solar, Dachform)",
         "topicId": "t5", "voteId": "sr_20240318_04"},
        {"number": 5, "title": "Verkaufsoffener Sonntag 14.04.2024 (21:1)", "voteId": "sr_20240318_05"},
        {"number": 6, "title": "Anfragen", "type": "formal"},
    ]
})

# ── SR 2024-04-08 (6. Sitzung) ───────────────────────────────────────────────
new_sessions.append({
    "id": "sr_20240408",
    "date": "2024-04-08",
    "type": "stadtrat",
    "title": "6. Stadtratssitzung – April 2024",
    "absent": ["stanglmaier", "kaestl"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Genehmigung Niederschriften (StR 04.03., 18.03.2024)", "voteId": "sr_20240408_01"},
        {"number": 4, "title": "Bericht Stadtgärtnerei – Zustand Stadtwald", "type": "discussion"},
        {"number": "5.1", "title": "Altersteilzeit-Verzicht (abgelehnt 3:20)", "voteId": "sr_20240408_02"},
        {"number": "5.2", "title": "Altersteilzeit gesetzlich mit Bedingungen (20:3)", "voteId": "sr_20240408_03"},
        {"number": 6, "title": "Einfamilienhaus Grünseiboldsdorf 11", "voteId": "sr_20240408_04"},
        {"number": 7, "title": "Vorlage Jahresrechnung 2023", "topicId": "t7", "type": "discussion"},
        {"number": 8, "title": "Anfragen", "type": "formal"},
    ]
})

# ── SR 2024-04-22 (7. Sitzung) ───────────────────────────────────────────────
new_sessions.append({
    "id": "sr_20240422",
    "date": "2024-04-22",
    "type": "stadtrat",
    "title": "7. Stadtratssitzung – April 2024",
    "absent": ["fincke", "von_pressentin"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Genehmigung Niederschriften", "voteId": "sr_20240422_01"},
        {"number": 4, "title": "Dokumentation Wachbaracken Stalag VII A – Präsentation",
         "topicId": "t14", "type": "discussion"},
        {"number": 5, "title": "Berichtigung B-Plan Nr. 65 \"Aich-Kirchfeldstraße\" – Datum (15:7)", "voteId": "sr_20240422_02"},
        {"number": 6, "title": "Anfragen", "type": "formal"},
    ]
})

# ── SR 2024-05-06 (8. Sitzung) ───────────────────────────────────────────────
new_sessions.append({
    "id": "sr_20240506",
    "date": "2024-05-06",
    "type": "stadtrat",
    "title": "8. Stadtratssitzung – Mai 2024",
    "absent": ["stanglmaier", "grundner"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Genehmigung Niederschrift BPU 14.03.2024", "voteId": "sr_20240506_01"},
        {"number": 4, "title": "Regionalplan München – Windenergie-Steuerungskonzept",
         "topicId": "t15", "voteId": "sr_20240506_02"},
        {"number": "5.1", "title": "Feststellung Jahresrechnung 2022", "topicId": "t7", "voteId": "sr_20240506_03"},
        {"number": "5.2", "title": "Entlastung zur Jahresrechnung 2022", "topicId": "t7", "voteId": "sr_20240506_04"},
        {"number": 6, "title": "Anfragen", "type": "formal"},
    ]
})

# ── SR 2024-06-10 (9. Sitzung) ───────────────────────────────────────────────
new_sessions.append({
    "id": "sr_20240610",
    "date": "2024-06-10",
    "type": "stadtrat",
    "title": "9. Stadtratssitzung – Juni 2024",
    "absent": ["hadersdorfer", "stanglmaier", "becher_a", "becher_j", "beubl", "heinz", "welter"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Genehmigung Niederschriften (StR 08.04. + 22.04.2024)", "voteId": "sr_20240610_01"},
        {"number": "4.1", "title": "Arbeitsmarktzulage Erzieher/Kinderpfleger 120€/Monat (15:3)", "voteId": "sr_20240610_02"},
        {"number": "4.2", "title": "Arbeitsmarktzulage – Zuschuss freie Träger", "voteId": "sr_20240610_03"},
        {"number": "5.1", "title": "Kindergartengebühren – Erhöhung um 30€ (10:8)", "voteId": "sr_20240610_04"},
        {"number": "5.2", "title": "Geschwisterermäßigung abschaffen (abgelehnt 7:11)", "voteId": "sr_20240610_05"},
        {"number": "5.3", "title": "Verwaltungsgebühr Neuanmeldung 10€ (17:1)", "voteId": "sr_20240610_06"},
        {"number": "5.5", "title": "Kindergartensatzung Schlussabstimmung (15:3)", "voteId": "sr_20240610_07"},
        {"number": "6.1", "title": "Schulwegpläne TG/Anton-Vizthum (abgelehnt 11:7)",
         "topicId": "t8", "voteId": "sr_20240610_08"},
        {"number": "6.2", "title": "Tempo-30-Zone Banater/Neustadt-/Sudetenlandstr./Neue Industriestr. (13:5)",
         "topicId": "t4", "voteId": "sr_20240610_09"},
        {"number": "8.1", "title": "AWO Küche + Einzelwohnen – Machbarkeitsstudie", "voteId": "sr_20240610_10"},
        {"number": "8.2", "title": "AWO – Abweichung Abstandsflächensatzung", "voteId": "sr_20240610_11"},
        {"number": 9, "title": "Anfragen", "type": "formal"},
    ]
})

# ── SR 2024-06-17 (10. Sitzung) ──────────────────────────────────────────────
new_sessions.append({
    "id": "sr_20240617",
    "date": "2024-06-17",
    "type": "stadtrat",
    "title": "10. Stadtratssitzung – Juni 2024",
    "absent": ["hadersdorfer", "stanglmaier", "beubl", "von_pressentin"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Genehmigung Niederschrift StR 06.05.2024", "voteId": "sr_20240617_01"},
        {"number": 4, "title": "Jugendsozialarbeit TG-Grundschule – Aufstockung auf 100%",
         "topicId": "t6", "voteId": "sr_20240617_02"},
        {"number": 5, "title": "B-Plan Nr. 80 \"Degernpoint Nordost II\" – Abwägung (11 Stellungnahmen)",
         "topicId": "t18", "voteId": "sr_20240617_03"},
        {"number": "5.12", "title": "B-Plan Nr. 80 – Satzungs- und Feststellungsbeschluss",
         "topicId": "t18", "voteId": "sr_20240617_04"},
        {"number": "6.1", "title": "Rockermaier-Straßenname – Saliterstraße", "topicId": "t5", "voteId": "sr_20240617_05"},
        {"number": "6.2", "title": "Rockermaier-Straßenname – Weihmühlstraße (Anbindung)",
         "topicId": "t5", "voteId": "sr_20240617_06"},
        {"number": "6.3", "title": "Rockermaier-Straßenname – Graf-Burkhard-Straße (12:8)",
         "topicId": "t5", "voteId": "sr_20240617_07"},
        {"number": "7.1", "title": "B-Plan \"MI Moos\" – Aufstellung", "voteId": "sr_20240617_08"},
        {"number": "7.2", "title": "B-Plan \"MI Moos\" – Städtebaulicher Vertrag", "voteId": "sr_20240617_09"},
        {"number": 8, "title": "Anfragen", "type": "formal"},
    ]
})

# ── SR 2024-07-01 (11. Sitzung) ──────────────────────────────────────────────
new_sessions.append({
    "id": "sr_20240701",
    "date": "2024-07-01",
    "type": "stadtrat",
    "title": "11. Stadtratssitzung – Juli 2024",
    "absent": ["fincke", "heinz", "kaestl", "von_pressentin"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Genehmigung Niederschrift StR 10.06.2024 (vertagt)", "type": "discussion"},
        {"number": 4, "title": "Kommunale Wärmeplanung – Zwischenergebnis", "topicId": "t15", "voteId": "sr_20240701_01"},
        {"number": "5.1", "title": "Kläranlage GmbH – Jahresabschluss 2023", "voteId": "sr_20240701_02"},
        {"number": "5.2", "title": "Kläranlage GmbH – Entlastung Aufsichtsrat 2023", "voteId": "sr_20240701_03"},
        {"number": 6, "title": "Finanzbericht 30.06.2024", "type": "discussion"},
        {"number": 7, "title": "Überplanmäßige Ausgaben (635.266,42 €)", "topicId": "t7", "voteId": "sr_20240701_04"},
        {"number": 8, "title": "Anfragen", "type": "formal"},
    ]
})

# ── BPU 2024-07-15 (2. BPU) ──────────────────────────────────────────────────
# Absent: stanglmaier (sub becher_j attended)
# Present: 12 (all seats filled via stanglmaier→becher_j substitution)
BPU_0715_VOTERS = ["dollinger", "hadersdorfer", "becher_j", "beibl", "beubl", "gruebl",
                   "kieninger", "linz_karin", "linz_kilian", "reif", "tristl", "welter"]
def bpu_0715_named():
    return {"type": "named", "results": {"yes": list(BPU_0715_VOTERS), "no": [], "absent": []}}

new_sessions.append({
    "id": "bpu_20240715",
    "date": "2024-07-15",
    "type": "bpu",
    "title": "2. Sitzung Bau-, Planungs- und Umweltausschuss – Juli 2024",
    "substitutes": [{"member": "stanglmaier", "substitute": "becher_j"}],
    "agenda": [
        {"number": 1, "title": "Mitteilungen", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": "3.1a", "title": "Münchener Straße – zusätzliche Ampel für Schulweg",
         "topicId": "t8", "voteId": "bpu_20240715_01"},
        {"number": "3.1b", "title": "Münchener Straße – Verlegung bestehende LSA prüfen",
         "topicId": "t8", "voteId": "bpu_20240715_02"},
        {"number": "4.1", "title": "Kindergarten Erzgebirgstraße – Einvernehmen", "voteId": "bpu_20240715_03"},
        {"number": 5, "title": "Sonderlandeplatz \"Auf der Kippe\" – Änderung Genehmigung", "voteId": "bpu_20240715_04"},
        {"number": "6.2", "title": "Rockermaier – Tiefgarage 96 WE (7:4)", "topicId": "t5", "voteId": "bpu_20240715_05"},
        {"number": "6.3", "title": "Rockermaier – MFH 3/4/5 (36 WE) (7:4)", "topicId": "t5", "voteId": "bpu_20240715_06"},
        {"number": "6.4", "title": "Rockermaier – MFH 6 (18 WE) (7:4)", "topicId": "t5", "voteId": "bpu_20240715_07"},
        {"number": "6.5", "title": "Rockermaier – MFH 7 (15 WE) (7:4)", "topicId": "t5", "voteId": "bpu_20240715_08"},
        {"number": "6.6", "title": "Rockermaier – MFH 8+9 (27 WE) (7:4)", "topicId": "t5", "voteId": "bpu_20240715_09"},
        {"number": "6.7", "title": "DAV Kletter- und Boulderhalle Stadtwaldstr. 115",
         "topicId": "t19", "voteId": "bpu_20240715_10"},
        {"number": "6.8", "title": "Ferienhaus Langer Weg 3", "voteId": "bpu_20240715_11"},
        {"number": 7, "title": "Anfragen und Sonstiges", "type": "formal"},
    ]
})

# ── SR 2024-07-22 (12. Sitzung) ──────────────────────────────────────────────
new_sessions.append({
    "id": "sr_20240722",
    "date": "2024-07-22",
    "type": "stadtrat",
    "title": "12. Stadtratssitzung – Juli 2024",
    "absent": ["stanglmaier", "heinz", "tristl"],
    "agenda": [
        {"number": 1, "title": "Mitteilungen", "type": "formal"},
        {"number": 2, "title": "Bürgerfragen", "type": "formal"},
        {"number": 3, "title": "Genehmigung Niederschriften (StR 10.06. + 01.07.2024)", "voteId": "sr_20240722_01"},
        {"number": "4.1", "title": "Eisstadion – Gebühren Vereinsnutzung 2024/2025 (17:4)", "voteId": "sr_20240722_02"},
        {"number": "4.2", "title": "Eisstadion – Benutzungs- und Gebührensatzung", "voteId": "sr_20240722_03"},
        {"number": 5, "title": "Anfragen", "type": "formal"},
    ]
})

# ============================================================================
# VOTES
# ============================================================================
new_votes = []

# sr_20240219 — all 21:0 (4 absent)
_abs_0219 = ["stanglmaier", "becher_a", "becher_j", "tristl"]
new_votes += [
    {"id":"sr_20240219_01","sessionId":"sr_20240219","topicId":None,"date":"2024-02-19",
     "title":"Genehmigung Niederschrift StR 15.01.2024",
     "text":"Der Stadtrat genehmigt einstimmig die öffentliche Niederschrift vom 15.01.2024.",
     **named(_abs_0219)},
    {"id":"sr_20240219_02","sessionId":"sr_20240219","topicId":"t18","date":"2024-02-19",
     "title":"B-Plan Nr. 80 \"Degernpoint Nordost II\" – Stellungnahmen",
     "text":"In 15 Einzelabstimmungen werden alle Stellungnahmen (Behörden, Verbände, Bürger) einstimmig (21:0) zur Kenntnis genommen bzw. abgewogen; der Entwurf wird zur erneuten Auslegung freigegeben.",
     **named(_abs_0219)},
    {"id":"sr_20240219_03","sessionId":"sr_20240219","topicId":None,"date":"2024-02-19",
     "title":"Erstaufforstungserlaubnis Pfrombach",
     "text":"Einstimmig: Erlaubnis zur Erstaufforstung auf Flurnummer 772 in Pfrombach erteilt.",
     **named(_abs_0219)},
]

# sr_20240304
new_votes += [
    {"id":"sr_20240304_01","sessionId":"sr_20240304","topicId":None,"date":"2024-03-04",
     "title":"Genehmigung Niederschriften (StR 18.12.2023, 01.02.2024)",
     "text":"Der Stadtrat genehmigt einstimmig die öffentlichen Niederschriften.",
     **anon(22, 0, 3)},
    {"id":"sr_20240304_02","sessionId":"sr_20240304","topicId":None,"date":"2024-03-04",
     "title":"B-Plan Nr. 65 \"Aich Kirchfeldstraße\" – Abwägung Stellungnahmen",
     "text":"In 16 Einzelabstimmungen werden die einzelnen Stellungnahmen (Behörden, Verbände, Bürger) zum Wohngebiet Kirchfeldstraße abgewogen; meist einstimmig 20-21:0 (Heinz mehrfach befangen).",
     **anon(20, 0, 5)},
    {"id":"sr_20240304_03","sessionId":"sr_20240304","topicId":None,"date":"2024-03-04",
     "title":"B-Plan Nr. 65 \"Aich Kirchfeldstraße\" – Satzungsbeschluss",
     "text":"Der Bebauungsplan Nr. 65 wird mit 15:7 als Satzung beschlossen.",
     **anon(15, 7, 3)},
    {"id":"sr_20240304_04","sessionId":"sr_20240304","topicId":None,"date":"2024-03-04",
     "title":"Wahlhelferbonus Europawahl 2024 (abgelehnt)",
     "text":"Antrag auf zusätzliche Bonuszahlung für Wahlhelfer wird mit 1:22 abgelehnt.",
     **anon(1, 22, 2, rej=True)},
    {"id":"sr_20240304_05","sessionId":"sr_20240304","topicId":None,"date":"2024-03-04",
     "title":"Erfrischungsgeld 40 € Europawahl 2024",
     "text":"Wahlhelfer erhalten einstimmig 40 € Erfrischungsgeld pro Wahltag.",
     **anon(23, 0, 2)},
]

# bpu_20240314 — 10 voters
new_votes += [
    {"id":"bpu_20240314_01","sessionId":"bpu_20240314","topicId":None,"date":"2024-03-14",
     "title":"B-Plan Nr. 56 \"Unteres Gereut\" – Überprüfung abgelehnt",
     "text":"Einstimmig: Der Bauausschuss lehnt eine Überprüfung des B-Plans Nr. 56 ab und hält an den Planungszielen fest.",
     **bpu_0314_named()},
    {"id":"bpu_20240314_02","sessionId":"bpu_20240314","topicId":None,"date":"2024-03-14",
     "title":"Dachgeschoss-Ausbau Bergstr. 27 Pfrombach",
     "text":"Einstimmig: Gemeindliches Einvernehmen erteilt.",
     **bpu_0314_named()},
    {"id":"bpu_20240314_03","sessionId":"bpu_20240314","topicId":None,"date":"2024-03-14",
     "title":"Doppelhäuser Thalbach Str. 108",
     "text":"Einstimmig: Gemeindliches Einvernehmen erteilt.",
     **bpu_0314_named()},
    {"id":"bpu_20240314_04","sessionId":"bpu_20240314","topicId":None,"date":"2024-03-14",
     "title":"Dachgeschoss-Ausbau Fasanenstr. 7",
     "text":"Einstimmig: Gemeindliches Einvernehmen erteilt.",
     **bpu_0314_named()},
    {"id":"bpu_20240314_05","sessionId":"bpu_20240314","topicId":None,"date":"2024-03-14",
     "title":"Arbeitnehmerwohnheim Sudetenlandstr. 9 – Einvernehmen erteilt (abgelehnt)",
     "text":"Antrag, das Einvernehmen für Nutzungsänderung zu Arbeitnehmerwohnheim zu erteilen, wird mit 1:9 abgelehnt.",
     **anon(1, 9, 2, rej=True)},
    {"id":"bpu_20240314_06","sessionId":"bpu_20240314","topicId":None,"date":"2024-03-14",
     "title":"Arbeitnehmerwohnheim Sudetenlandstr. 9 – Einvernehmen verweigert",
     "text":"Einvernehmen mit 9:1 verweigert (Stellplatz-/Spielplatzproblematik).",
     **anon(9, 1, 2)},
    {"id":"bpu_20240314_07","sessionId":"bpu_20240314","topicId":None,"date":"2024-03-14",
     "title":"Wohngebäude St.-Georg-Str. 26 Aich",
     "text":"Einstimmig: Gemeindliches Einvernehmen erteilt.",
     **bpu_0314_named()},
    {"id":"bpu_20240314_08","sessionId":"bpu_20240314","topicId":None,"date":"2024-03-14",
     "title":"MFH Mainburger Str. 5 – Einvernehmen verweigert",
     "text":"Einstimmig (0:10) verweigert: Baukörper fügt sich nicht ein, Stellplatzthematik.",
     **anon(0, 10, 2, rej=True)},
]

# sr_20240318
_abs_0318 = ["beubl", "von_pressentin", "weber"]
new_votes += [
    {"id":"sr_20240318_01","sessionId":"sr_20240318","topicId":None,"date":"2024-03-18",
     "title":"Genehmigung Niederschrift StR 19.02.2024",
     "text":"Genehmigt; Heinz enthält sich teilweise wegen persönlicher Beteiligung.",
     **anon(21, 0, 4)},
    {"id":"sr_20240318_02","sessionId":"sr_20240318","topicId":"t5","date":"2024-03-18",
     "title":"B-Plan Nr. 77 \"Rockermaier Areal\" – Abwägung Stellungnahmen",
     "text":"In 21 Einzelabstimmungen werden die Stellungnahmen aus der ersten öffentlichen Auslegung abgewogen; meist 20-21:0 mit Befangenheits-Enthaltungen.",
     **anon(20, 0, 5)},
    {"id":"sr_20240318_03","sessionId":"sr_20240318","topicId":"t5","date":"2024-03-18",
     "title":"Rockermaier – Erneute Öffentliche Auslegung",
     "text":"Einstimmig: Der überarbeitete Bebauungsplan-Entwurf geht in die erneute öffentliche Auslegung.",
     **anon(21, 0, 4)},
    {"id":"sr_20240318_04","sessionId":"sr_20240318","topicId":"t5","date":"2024-03-18",
     "title":"Rockermaier – Planänderungen (Energie, Solar, Dachform)",
     "text":"Einstimmig beschlossen: Anpassungen zur energetischen Optimierung, Vorgaben zu Solarenergie und Dachformen.",
     **anon(21, 0, 4)},
    {"id":"sr_20240318_05","sessionId":"sr_20240318","topicId":None,"date":"2024-03-18",
     "title":"Verkaufsoffener Sonntag 14.04.2024",
     "text":"Verordnung mit 21:1 beschlossen.",
     **anon(21, 1, 3)},
]

# sr_20240408
_abs_0408 = ["stanglmaier", "kaestl"]
new_votes += [
    {"id":"sr_20240408_01","sessionId":"sr_20240408","topicId":None,"date":"2024-04-08",
     "title":"Genehmigung Niederschriften (StR 04.03. + 18.03.2024)",
     "text":"Der Stadtrat genehmigt einstimmig die öffentlichen Niederschriften.",
     **named(_abs_0408)},
    {"id":"sr_20240408_02","sessionId":"sr_20240408","topicId":None,"date":"2024-04-08",
     "title":"Altersteilzeit – Verzicht auf Freiwilligkeitsregelung (abgelehnt)",
     "text":"Antrag, freiwillige Altersteilzeit-Verträge auszuschließen, wird mit 3:20 abgelehnt.",
     **anon(3, 20, 2, rej=True)},
    {"id":"sr_20240408_03","sessionId":"sr_20240408","topicId":None,"date":"2024-04-08",
     "title":"Altersteilzeit – gesetzliche Regelung mit Bedingungen",
     "text":"Altersteilzeit nach gesetzlichen Regeln mit detaillierten Bedingungen (Dauer, Gehalt, Versicherungsbeiträge) (20:3).",
     **anon(20, 3, 2)},
    {"id":"sr_20240408_04","sessionId":"sr_20240408","topicId":None,"date":"2024-04-08",
     "title":"Einfamilienhaus Grünseiboldsdorf 11",
     "text":"Einstimmig: Gemeindliches Einvernehmen erteilt.",
     **named(_abs_0408)},
]

# sr_20240422
_abs_0422 = ["fincke", "von_pressentin"]
new_votes += [
    {"id":"sr_20240422_01","sessionId":"sr_20240422","topicId":None,"date":"2024-04-22",
     "title":"Genehmigung Niederschriften",
     "text":"Der Stadtrat genehmigt einstimmig die öffentlichen Niederschriften.",
     **named(_abs_0422)},
    {"id":"sr_20240422_02","sessionId":"sr_20240422","topicId":None,"date":"2024-04-22",
     "title":"Berichtigung B-Plan Nr. 65 \"Aich-Kirchfeldstraße\"",
     "text":"Datumskorrektur im Satzungsbeschluss (Inhalt unverändert) – wieder 15:7 (gleiche Mehrheitsverhältnisse).",
     **anon(15, 7, 3)},
]

# sr_20240506
_abs_0506 = ["stanglmaier", "grundner"]
new_votes += [
    {"id":"sr_20240506_01","sessionId":"sr_20240506","topicId":None,"date":"2024-05-06",
     "title":"Genehmigung Niederschrift BPU 14.03.2024",
     "text":"Der Stadtrat genehmigt einstimmig die öffentliche Niederschrift der BPU-Sitzung.",
     **anon(22, 0, 3)},
    {"id":"sr_20240506_02","sessionId":"sr_20240506","topicId":"t15","date":"2024-05-06",
     "title":"Regionalplan München – Windenergie",
     "text":"Der Stadtrat nimmt das Steuerungskonzept für Windenergie zur Kenntnis (18:4); Empfehlung: Windvorrangfläche in der Region Kirchamper.",
     **anon(18, 4, 3)},
    {"id":"sr_20240506_03","sessionId":"sr_20240506","topicId":"t7","date":"2024-05-06",
     "title":"Feststellung Jahresrechnung 2022",
     "text":"Einstimmig festgestellt; Bürgermeister Dollinger enthält sich wegen persönlicher Beteiligung.",
     **anon(22, 0, 3)},
    {"id":"sr_20240506_04","sessionId":"sr_20240506","topicId":"t7","date":"2024-05-06",
     "title":"Entlastung zur Jahresrechnung 2022",
     "text":"Entlastung einstimmig erteilt; Dollinger enthält sich wegen persönlicher Beteiligung.",
     **anon(21, 0, 4)},
]

# sr_20240610
_abs_0610 = ["hadersdorfer", "stanglmaier", "becher_a", "becher_j", "beubl", "heinz", "welter"]
new_votes += [
    {"id":"sr_20240610_01","sessionId":"sr_20240610","topicId":None,"date":"2024-06-10",
     "title":"Genehmigung Niederschriften (StR 08.04. + 22.04.2024)",
     "text":"Der Stadtrat genehmigt einstimmig die öffentlichen Niederschriften.",
     **named(_abs_0610)},
    {"id":"sr_20240610_02","sessionId":"sr_20240610","topicId":None,"date":"2024-06-10",
     "title":"Arbeitsmarktzulage Erzieher/Kinderpfleger",
     "text":"Pädagogisches Personal in Kindertageseinrichtungen erhält ab 01.09.2024 monatlich 120 € Arbeitsmarktzulage für zunächst zwei Jahre (15:3).",
     **anon(15, 3, 7)},
    {"id":"sr_20240610_03","sessionId":"sr_20240610","topicId":None,"date":"2024-06-10",
     "title":"Arbeitsmarktzulage – Zuschuss freie Träger",
     "text":"Einstimmig: Die Stadt gewährt freien Kita-Trägern einen entsprechenden Zuschuss.",
     **named(_abs_0610)},
    {"id":"sr_20240610_04","sessionId":"sr_20240610","topicId":None,"date":"2024-06-10",
     "title":"Kindergartengebühren – Erhöhung 30 €",
     "text":"Kindergarten-Gebühren ab Kita-Jahr 2024/25 um 30 € pro Buchungskategorie erhöht (10:8).",
     **anon(10, 8, 7)},
    {"id":"sr_20240610_05","sessionId":"sr_20240610","topicId":None,"date":"2024-06-10",
     "title":"Geschwisterermäßigung abschaffen (abgelehnt)",
     "text":"Antrag, die Geschwisterermäßigung aufzuheben, wird mit 7:11 abgelehnt.",
     **anon(7, 11, 7, rej=True)},
    {"id":"sr_20240610_06","sessionId":"sr_20240610","topicId":None,"date":"2024-06-10",
     "title":"Verwaltungsgebühr Neuanmeldung 10 €",
     "text":"Verwaltungsgebühr für Neu-/Wiederanmeldungen von 5 € auf 10 € erhöht (17:1).",
     **anon(17, 1, 7)},
    {"id":"sr_20240610_07","sessionId":"sr_20240610","topicId":None,"date":"2024-06-10",
     "title":"Kindergartensatzung – Schlussabstimmung",
     "text":"5. Änderung der Kindergartensatzung mit Geschwisterermäßigung und unveränderten Essensgeldern beschlossen (15:3).",
     **anon(15, 3, 7)},
    {"id":"sr_20240610_08","sessionId":"sr_20240610","topicId":"t8","date":"2024-06-10",
     "title":"Schulwegpläne TG-Grundschule + Anton-Vizthum (abgelehnt)",
     "text":"Antrag, für die zwei Grundschulen Schulwegpläne zu erstellen, wird mit 11:7 abgelehnt.",
     **anon(7, 11, 7, rej=True)},
    {"id":"sr_20240610_09","sessionId":"sr_20240610","topicId":"t4","date":"2024-06-10",
     "title":"Tempo-30-Zone Wohngebiet",
     "text":"Wohngebiet zwischen Banater-, Neustadt-, Sudetenland- und Neuer Industriestraße als Tempo-30-Zone ausgewiesen (13:5).",
     **anon(13, 5, 7)},
    {"id":"sr_20240610_10","sessionId":"sr_20240610","topicId":None,"date":"2024-06-10",
     "title":"AWO Küche + Einzelwohnen – Machbarkeitsstudie",
     "text":"Einstimmig: Stadtrat nimmt die Machbarkeitsstudie zustimmend zur Kenntnis und signalisiert grundsätzliche Bereitschaft zur Baugenehmigung.",
     **named(_abs_0610)},
    {"id":"sr_20240610_11","sessionId":"sr_20240610","topicId":None,"date":"2024-06-10",
     "title":"AWO – Abweichung Abstandsflächensatzung",
     "text":"Einstimmig: Erforderliche Abweichung von der Abstandsflächensatzung genehmigt.",
     **named(_abs_0610)},
]

# sr_20240617
_abs_0617 = ["hadersdorfer", "stanglmaier", "beubl", "von_pressentin"]
new_votes += [
    {"id":"sr_20240617_01","sessionId":"sr_20240617","topicId":None,"date":"2024-06-17",
     "title":"Genehmigung Niederschrift StR 06.05.2024",
     "text":"Der Stadtrat genehmigt einstimmig die öffentliche Niederschrift.",
     **anon(20, 0, 5)},
    {"id":"sr_20240617_02","sessionId":"sr_20240617","topicId":"t6","date":"2024-06-17",
     "title":"Jugendsozialarbeit TG-Grundschule – Aufstockung auf 100 %",
     "text":"Einstimmig: Die Stelle der Jugendsozialarbeit an der Theresia-Gerhardinger-Grundschule wird von 50 % auf 100 % aufgestockt; die Stadt übernimmt die Hälfte der Personal- und Sachkosten.",
     **anon(20, 0, 5)},
    {"id":"sr_20240617_03","sessionId":"sr_20240617","topicId":"t18","date":"2024-06-17",
     "title":"B-Plan Nr. 80 \"Degernpoint Nordost II\" – Abwägung Stellungnahmen",
     "text":"In 11 Einzelabstimmungen werden die Stellungnahmen der erneuten öffentlichen Auslegung abgewogen; alle einstimmig 20:0.",
     **anon(20, 0, 5)},
    {"id":"sr_20240617_04","sessionId":"sr_20240617","topicId":"t18","date":"2024-06-17",
     "title":"B-Plan Nr. 80 – Satzungs- und Feststellungsbeschluss",
     "text":"Einstimmig: 16. Änderung des Flächennutzungsplans und Bebauungsplan Nr. 80 \"Degernpoint Nordost II\" als Satzung beschlossen.",
     **anon(20, 0, 5)},
    {"id":"sr_20240617_05","sessionId":"sr_20240617","topicId":"t5","date":"2024-06-17",
     "title":"Rockermaier – Straßenname Saliterstraße",
     "text":"Einstimmig: Die Haupterschließungsstraße des Rockermaier-Areals heißt Saliterstraße.",
     **anon(20, 0, 5)},
    {"id":"sr_20240617_06","sessionId":"sr_20240617","topicId":"t5","date":"2024-06-17",
     "title":"Rockermaier – Anbindung Weihmühlstraße",
     "text":"Einstimmig: Die Anbindung an die Industriestraße erhält den Namen Weihmühlstraße.",
     **anon(20, 0, 5)},
    {"id":"sr_20240617_07","sessionId":"sr_20240617","topicId":"t5","date":"2024-06-17",
     "title":"Rockermaier – Graf-Burkhard-Straße",
     "text":"Mit 12:8 beschlossen: Interne Einbahnstraße im Rockermaier-Areal heißt Graf-Burkhard-Straße.",
     **anon(12, 8, 5)},
    {"id":"sr_20240617_08","sessionId":"sr_20240617","topicId":None,"date":"2024-06-17",
     "title":"B-Plan \"MI Moos\" – Aufstellung",
     "text":"Einstimmig: Aufstellungsbeschluss für Mischgebiet \"MI Moos\" (§ 30 BauGB i.V.m. § 6 BauNVO).",
     **anon(20, 0, 5)},
    {"id":"sr_20240617_09","sessionId":"sr_20240617","topicId":None,"date":"2024-06-17",
     "title":"B-Plan \"MI Moos\" – Städtebaulicher Vertrag",
     "text":"Einstimmig: Verwaltung wird zum Abschluss eines städtebaulichen Vertrages ermächtigt; Vorhabenträger trägt Planungskosten.",
     **anon(20, 0, 5)},
]

# sr_20240701
_abs_0701 = ["fincke", "heinz", "kaestl", "von_pressentin"]
new_votes += [
    {"id":"sr_20240701_01","sessionId":"sr_20240701","topicId":"t15","date":"2024-07-01",
     "title":"Kommunale Wärmeplanung – Zwischenergebnis",
     "text":"Einstimmig: Der Stadtrat nimmt den aktuellen Stand der kommunalen Wärmeplanung zur Kenntnis.",
     **anon(20, 0, 5)},
    {"id":"sr_20240701_02","sessionId":"sr_20240701","topicId":None,"date":"2024-07-01",
     "title":"Kläranlage GmbH – Jahresabschluss 2023",
     "text":"Einstimmig: Empfehlung zur Genehmigung des Jahresabschlusses 2023; Jahresüberschuss 296.622,96 € + Gewinnvortrag 1.630.617,43 € wird neu vorgetragen.",
     **anon(21, 0, 4)},
    {"id":"sr_20240701_03","sessionId":"sr_20240701","topicId":None,"date":"2024-07-01",
     "title":"Kläranlage GmbH – Entlastung Aufsichtsrat 2023",
     "text":"Empfehlung zur Entlastung des Aufsichtsrats für 2023; 8 Mitglieder enthielten sich (Aufsichtsratsmitglieder).",
     **anon(13, 0, 12)},
    {"id":"sr_20240701_04","sessionId":"sr_20240701","topicId":"t7","date":"2024-07-01",
     "title":"Überplanmäßige Ausgaben",
     "text":"Einstimmig: Über- und außerplanmäßige Ausgaben von 635.266,42 € genehmigt (Betriebsstromkosten, Investitionen). Deckung durch Schlüsselzuweisungen, DigitalPakt-Mittel und Rücklage.",
     **anon(21, 0, 4)},
]

# bpu_20240715 — 12 voters (all seats filled)
new_votes += [
    {"id":"bpu_20240715_01","sessionId":"bpu_20240715","topicId":"t8","date":"2024-07-15",
     "title":"Münchener Straße – zusätzliche Schulweg-Ampel",
     "text":"Einstimmig: Zusätzliche Fußgängerampel auf der Münchener Straße zur Schulwegsicherung beschlossen; Umsetzung im laufenden Jahr.",
     **bpu_0715_named()},
    {"id":"bpu_20240715_02","sessionId":"bpu_20240715","topicId":"t8","date":"2024-07-15",
     "title":"Münchener Straße – Verlegung bestehender LSA prüfen",
     "text":"Einstimmig: Verwaltung wird beauftragt, eine mögliche Verlegung der bestehenden Lichtsignalanlage (Richtung Friedhof) zu prüfen.",
     **bpu_0715_named()},
    {"id":"bpu_20240715_03","sessionId":"bpu_20240715","topicId":None,"date":"2024-07-15",
     "title":"Kindergarten Erzgebirgstraße – Einvernehmen",
     "text":"Einstimmig: Gemeindliches Einvernehmen für den Neubau des Kindergartens an der Erzgebirgstraße erteilt.",
     **bpu_0715_named()},
    {"id":"bpu_20240715_04","sessionId":"bpu_20240715","topicId":None,"date":"2024-07-15",
     "title":"Sonderlandeplatz \"Auf der Kippe\" – Änderung Genehmigung",
     "text":"Einstimmig: Keine Einwände gegen den Antrag des Fliegerclubs auf Änderung/Verlängerung der Betriebsgenehmigung.",
     **bpu_0715_named()},
    {"id":"bpu_20240715_05","sessionId":"bpu_20240715","topicId":"t5","date":"2024-07-15",
     "title":"Rockermaier – gemeinsame Tiefgarage (96 WE)",
     "text":"Mit 7:4 beschlossen: Gemeindliches Einvernehmen und Stellplatz-Abweichung für die Tiefgarage; Bewilligung erst nach Abschluss des städtebaulichen Vertrages.",
     **anon(7, 4, 1)},
    {"id":"bpu_20240715_06","sessionId":"bpu_20240715","topicId":"t5","date":"2024-07-15",
     "title":"Rockermaier – MFH 3/4/5 (36 WE)",
     "text":"Mit 7:4 beschlossen: Einvernehmen und Stellplatzbefreiung; Bewilligung erst nach Vertragsabschluss.",
     **anon(7, 4, 1)},
    {"id":"bpu_20240715_07","sessionId":"bpu_20240715","topicId":"t5","date":"2024-07-15",
     "title":"Rockermaier – MFH 6 (18 WE)",
     "text":"Mit 7:4 beschlossen: Einvernehmen und Stellplatzbefreiung; Bewilligung erst nach Vertragsabschluss.",
     **anon(7, 4, 1)},
    {"id":"bpu_20240715_08","sessionId":"bpu_20240715","topicId":"t5","date":"2024-07-15",
     "title":"Rockermaier – MFH 7 (15 WE)",
     "text":"Mit 7:4 beschlossen: Einvernehmen und Stellplatzbefreiung; Bewilligung erst nach Vertragsabschluss.",
     **anon(7, 4, 1)},
    {"id":"bpu_20240715_09","sessionId":"bpu_20240715","topicId":"t5","date":"2024-07-15",
     "title":"Rockermaier – MFH 8+9 (27 WE)",
     "text":"Mit 7:4 beschlossen: Einvernehmen und Stellplatzbefreiung; Bewilligung erst nach Vertragsabschluss.",
     **anon(7, 4, 1)},
    {"id":"bpu_20240715_10","sessionId":"bpu_20240715","topicId":"t19","date":"2024-07-15",
     "title":"DAV Kletter- und Boulderhalle Stadtwaldstr. 115",
     "text":"Einstimmig: Gemeindliches Einvernehmen für den Neubau einer Kletter- und Boulderhalle mit Lager erteilt.",
     **bpu_0715_named()},
    {"id":"bpu_20240715_11","sessionId":"bpu_20240715","topicId":None,"date":"2024-07-15",
     "title":"Ferienhaus Langer Weg 3 – Umnutzung",
     "text":"Einstimmig: Gemeindliches Einvernehmen für die Umnutzung eines Einfamilienhauses zum Ferienhaus erteilt.",
     **bpu_0715_named()},
]

# sr_20240722
_abs_0722 = ["stanglmaier", "heinz", "tristl"]
new_votes += [
    {"id":"sr_20240722_01","sessionId":"sr_20240722","topicId":None,"date":"2024-07-22",
     "title":"Genehmigung Niederschriften (StR 10.06. + 01.07.2024)",
     "text":"Der Stadtrat genehmigt einstimmig die öffentlichen Niederschriften.",
     **anon(21, 0, 4)},
    {"id":"sr_20240722_02","sessionId":"sr_20240722","topicId":None,"date":"2024-07-22",
     "title":"Eisstadion – Gebühren Vereinsnutzung 2024/2025",
     "text":"Gebührenordnung Vereinsnutzung beschlossen (Training EVM/EVA 60 €/h, Hobby 150 €/h; weitere Bestimmungen zu Spielen, Werbung, Stornierungen) (17:4).",
     **anon(17, 4, 4)},
    {"id":"sr_20240722_03","sessionId":"sr_20240722","topicId":None,"date":"2024-07-22",
     "title":"Eisstadion – Benutzungs- und Gebührensatzung",
     "text":"Einstimmig: Anpassungen der Benutzungs- und Gebührensatzung Eisstadion beschlossen.",
     **anon(22, 0, 3)},
]

# ============================================================================
# TOPICS
# ============================================================================
# t15 dissolved: PV Kuttenweide entries go into broader "Energie & Klimawende" topic.
# t6: rename + summary tweak.
# New topics: t18 Gewerbegebiet Degernpoint, t19 DAV Kletterhalle.

T15_NEW = {
    "id": "t15",
    "title": "Energie & Klimawende",
    "tags": ["energy", "infrastructure"],
    "image": None,
    "summary": "Moosburgs Schritte hin zu einer klimaneutralen Versorgung: Stromausschreibung mit 100 % Ökostrom, kommunale Wärmeplanung als strategische Grundlage, einzelne PV-Freiflächenanlagen und Stellungnahmen zum Windenergie-Steuerungskonzept des Regionalplans München.",
    "history": [
        {"date": "2024-05-06", "type": "vote",
         "title": "Stellungnahme Regionalplan Windenergie",
         "text": "Der Stadtrat nimmt das Steuerungskonzept Windenergie des Regionalplans München zur Kenntnis (18:4); empfiehlt eine Windvorrangfläche in der Region Kirchamper.",
         "sessionId": "sr_20240506", "voteId": "sr_20240506_02"},
        {"date": "2024-07-01", "type": "vote",
         "title": "Kommunale Wärmeplanung – Zwischenergebnis",
         "text": "Stadtrat nimmt den Zwischenstand der kommunalen Wärmeplanung einstimmig zur Kenntnis.",
         "sessionId": "sr_20240701", "voteId": "sr_20240701_01"},
        {"date": "2025-02-10", "type": "vote",
         "title": "PV Kuttenweide – Aufstellungsbeschluss B-Plan",
         "text": "Einstimmig: Aufstellung des B-Plans \"SO Freiflächen-PV-Anlage Kuttenweide\" im Parallelverfahren mit dem Flächennutzungsplan.",
         "sessionId": "sr_20250210", "voteId": "sr_20250210_04"},
        {"date": "2025-02-10", "type": "vote",
         "title": "PV Kuttenweide – Städtebaulicher Vertrag",
         "text": "Einstimmig: Bürgermeister ermächtigt, mit dem Vorhabenträger einen städtebaulichen Vertrag abzuschließen.",
         "sessionId": "sr_20250210", "voteId": "sr_20250210_05"},
        {"date": "2025-02-24", "type": "vote",
         "title": "Strom-Ausschreibung – 100 % Ökostrom",
         "text": "Variante 2 (100 % Ökostrom ohne Neuanlagenquote) wird beschlossen; Variante 1 mit Neuanlagenquote wird abgelehnt (8:12).",
         "sessionId": "sr_20250224", "voteId": "sr_20250224_05"},
        {"date": "2025-06-23", "type": "vote",
         "title": "Kommunale Wärmeplanung – Abschlussbericht",
         "text": "Stadtrat anerkennt den Abschlussbericht der kommunalen Wärmeplanung als strategische Grundlage für Energie- und Infrastrukturentscheidungen.",
         "sessionId": "sr_20250623", "voteId": "sr_20250623_01"}
    ]
}

T18_NEW = {
    "id": "t18",
    "title": "Gewerbegebiet Degernpoint",
    "tags": ["building", "infrastructure"],
    "image": None,
    "summary": "Erweiterung und Anpassung des Gewerbegebiets Degernpoint im Norden Moosburgs: Aufstellung und Satzungsbeschluss für \"Degernpoint Nordost II\" (B-Plan 80) sowie 4. Änderung des bestehenden B-Plans Nr. 50 mit flexiblerer Parzellierung.",
    "history": [
        {"date": "2024-02-19", "type": "vote",
         "title": "B-Plan Nr. 80 \"Degernpoint Nordost II\" – Stellungnahmen abgewogen",
         "text": "15 Einzelabstimmungen einstimmig (21:0); der Entwurf geht in die erneute Auslegung.",
         "sessionId": "sr_20240219", "voteId": "sr_20240219_02"},
        {"date": "2024-06-17", "type": "vote",
         "title": "B-Plan Nr. 80 – Satzungs- und Feststellungsbeschluss",
         "text": "Einstimmig: 16. Änderung des Flächennutzungsplans und Bebauungsplan Nr. 80 als Satzung beschlossen.",
         "sessionId": "sr_20240617", "voteId": "sr_20240617_04"},
        {"date": "2025-01-20", "type": "vote",
         "title": "4. Änderung B-Plan Nr. 50 – Aufstellungsbeschluss",
         "text": "Einstimmig: Aufstellungsbeschluss mit flexibler Parzellierung für Handwerk/Gewerbe; SWM-Umspannwerk eingeplant.",
         "sessionId": "sr_20250120", "voteId": "sr_20250120_05"}
    ]
}

T19_NEW = {
    "id": "t19",
    "title": "DAV Kletter- und Boulderhalle",
    "tags": ["sports", "building"],
    "image": None,
    "summary": "Neubau einer Kletter- und Boulderhalle des Deutschen Alpenvereins (Sektion Moosburg) an der Stadtwaldstraße 115. Die Stadt unterstützt das Projekt mit einem Zuschuss von 20 % der förderfähigen Baukosten und erteilte das gemeindliche Einvernehmen.",
    "history": [
        {"date": "2024-07-15", "type": "vote",
         "title": "Einvernehmen für Kletter-/Boulderhalle",
         "text": "Einstimmig: Bauausschuss erteilt das gemeindliche Einvernehmen für den Neubau an der Stadtwaldstraße 115.",
         "sessionId": "bpu_20240715", "voteId": "bpu_20240715_10"},
        {"date": "2024-11-18", "type": "vote",
         "title": "Zuschuss DAV Kletter-/Boulderhalle",
         "text": "Einstimmig: Stadt unterstützt DAV-Sektion mit 20 % der förderfähigen Baukosten (max. ca. 292.000 €).",
         "sessionId": "sr_20241118", "voteId": "sr_20241118_04"}
    ]
}

# Extensions to existing topics
T5_INSERTS = [
    {"date": "2024-03-18", "type": "vote",
     "title": "B-Plan Nr. 77 Rockermaier – Erneute Auslegung",
     "text": "Einstimmig: Nach Abwägung der Stellungnahmen geht der überarbeitete B-Plan-Entwurf erneut in die öffentliche Auslegung; Anpassungen zu Energie, Solar und Dachformen werden beschlossen.",
     "sessionId": "sr_20240318", "voteId": "sr_20240318_03"},
    {"date": "2024-06-17", "type": "vote",
     "title": "Rockermaier-Areal – Straßennamen festgelegt",
     "text": "Hauptstraße = Saliterstraße (einstimmig), Anbindung Industriestraße = Weihmühlstraße (einstimmig), interne Einbahnstraße = Graf-Burkhard-Straße (12:8).",
     "sessionId": "sr_20240617", "voteId": "sr_20240617_05"},
    {"date": "2024-07-15", "type": "vote",
     "title": "Einvernehmen für Wohnbauten Rockermaier",
     "text": "Bauausschuss erteilt mit jeweils 7:4 das Einvernehmen für die 5 Mehrfamilienhäuser (Tiefgarage, 96 WE) und MFH 3-9 (insg. 96 WE); Bewilligung erst nach Abschluss des städtebaulichen Vertrags.",
     "sessionId": "bpu_20240715", "voteId": "bpu_20240715_05"}
]

T14_INSERTS = [
    {"date": "2024-04-22", "type": "milestone",
     "title": "Dokumentation Wachbaracken vorgestellt",
     "text": "Die historische Dokumentation der Wachbaracken des Stalag VII A wird dem Stadtrat als Grundlage für die weitere denkmalgerechte Sicherung präsentiert.",
     "sessionId": "sr_20240422"}
]

T7_INSERTS = [
    {"date": "2024-05-06", "type": "vote",
     "title": "Jahresrechnung 2022 + Entlastung",
     "text": "Einstimmig festgestellt und Entlastung erteilt; Bürgermeister Dollinger enthält sich wegen persönlicher Beteiligung.",
     "sessionId": "sr_20240506", "voteId": "sr_20240506_03"},
    {"date": "2024-07-01", "type": "vote",
     "title": "Überplanmäßige Ausgaben 635 T€",
     "text": "Einstimmig: Über- und außerplanmäßige Ausgaben von 635.266,42 € (v.a. Betriebsstromkosten) genehmigt.",
     "sessionId": "sr_20240701", "voteId": "sr_20240701_04"}
]

T8_INSERTS = [
    {"date": "2024-06-10", "type": "vote",
     "title": "Schulwegpläne TG-Grundschule/Anton-Vizthum abgelehnt",
     "text": "Der Stadtrat lehnt mit 11:7 den Antrag ab, für die zwei Grundschulen Schulwegpläne erstellen zu lassen.",
     "sessionId": "sr_20240610", "voteId": "sr_20240610_08"},
    {"date": "2024-07-15", "type": "vote",
     "title": "Münchener Straße – zusätzliche Schulweg-Ampel",
     "text": "Einstimmig: Zusätzliche Fußgängerampel auf der Münchener Straße zur Schulwegsicherung; Verwaltung prüft parallel die Verlegung der bestehenden LSA.",
     "sessionId": "bpu_20240715", "voteId": "bpu_20240715_01"}
]

T4_INSERTS = [
    {"date": "2024-06-10", "type": "vote",
     "title": "Tempo-30-Zone Wohngebiet",
     "text": "Wohngebiet zwischen Banater-, Neustadt-, Sudetenland- und Neuer Industriestraße als Tempo-30-Zone ausgewiesen (13:5).",
     "sessionId": "sr_20240610", "voteId": "sr_20240610_09"}
]

T6_RENAME = {
    "title": "Theresia-Gerhardinger-Grundschule",
    "summary": "Die Theresia-Gerhardinger-Grundschule im Norden Moosburgs wird umfassend erweitert und generalsaniert (geschätzt 33 Mio. €). Parallel werden Begleitthemen wie die Jugendsozialarbeit gestärkt und eine Kostenkommission begleitet das Projekt."
}

# ============================================================================
# APPLY
# ============================================================================
def insert_chrono(history, entry):
    for i, e in enumerate(history):
        if e["date"] > entry["date"]:
            history.insert(i, entry); return
    history.append(entry)

with open(f"{BASE}/sessions.json","r",encoding="utf-8") as f: sessions = json.load(f)
existing_sids = {s["id"] for s in sessions}
added_s = 0
for s in new_sessions:
    if s["id"] not in existing_sids:
        sessions.append(s); added_s += 1
        print(f"+ session {s['id']}")
with open(f"{BASE}/sessions.json","w",encoding="utf-8") as f: json.dump(sessions, f, ensure_ascii=False, indent=2)
print(f"sessions.json: +{added_s}, total {len(sessions)}")

with open(f"{BASE}/votes.json","r",encoding="utf-8") as f: votes = json.load(f)
existing_vids = {v["id"] for v in votes}
added_v = 0
for v in new_votes:
    if v["id"] not in existing_vids:
        votes.append(v); added_v += 1
with open(f"{BASE}/votes.json","w",encoding="utf-8") as f: json.dump(votes, f, ensure_ascii=False, indent=2)
print(f"votes.json: +{added_v}, total {len(votes)}")

with open(f"{BASE}/topics.json","r",encoding="utf-8") as f: topics = json.load(f)
tmap = {t["id"]: t for t in topics}

# Replace t15
for i, t in enumerate(topics):
    if t["id"] == "t15":
        topics[i] = T15_NEW
        tmap["t15"] = T15_NEW
        print("~ t15 replaced (PV Kuttenweide → Energie & Klimawende)")
        break

# Rename t6
t6 = tmap.get("t6")
if t6:
    t6["title"] = T6_RENAME["title"]
    t6["summary"] = T6_RENAME["summary"]
    print("~ t6 renamed → " + T6_RENAME["title"])

# Add new topics
for nt in [T18_NEW, T19_NEW]:
    if nt["id"] not in tmap:
        topics.append(nt); tmap[nt["id"]] = nt
        print(f"+ topic {nt['id']} ({nt['title']})")

# Insert history entries
INSERTS = {"t5": T5_INSERTS, "t7": T7_INSERTS, "t8": T8_INSERTS, "t14": T14_INSERTS, "t4": T4_INSERTS}
for tid, entries in INSERTS.items():
    t = tmap.get(tid)
    if not t: continue
    existing_keys = {(e["date"], e.get("voteId"), e.get("title")) for e in t["history"]}
    for entry in entries:
        key = (entry["date"], entry.get("voteId"), entry.get("title"))
        if key not in existing_keys:
            insert_chrono(t["history"], entry)
            print(f"  ~ {tid} += {entry['date']} {entry['title'][:40]}")

with open(f"{BASE}/topics.json","w",encoding="utf-8") as f: json.dump(topics, f, ensure_ascii=False, indent=2)
print(f"topics.json: total {len(topics)}")

print("\nDone.")
