"""Integrate 4 protocols 2022: SR 05.09, 19.09, 24.10 (Niederlegung!) + BPU 17.11.

Key context:
- SR_20221024 ist die 17. Sitzung — Niederlegung Neumayr → Eintritt Gruber.
  Gruber ist in dieser Sitzung bereits als Stadtrat gelistet.
- BPU 2022-11-17 hat NUR 12 Mitglieder OHNE Welter (Welter trat erst 2023 in den
  Ausschuss ein). Stattdessen John & Reif als regulärs.
"""
import json

BASE = "c:/Users/bened/Documents/GitHub/bagruber/council/data"

# 25 Mitglieder mit Stand Sept/Okt 2022
ACTIVE_25_PRE = ["dollinger","hadersdorfer","stanglmaier","becher_a","becher_j",
                 "fincke","gruebl","grundner","haberl","heinz","john","kaestl",
                 "kieninger","beibl","lauterbach","linz_karin","linz_kilian",
                 "neumayr","pschorr","reif","tristl","von_pressentin","weber",
                 "welter","beubl"]
ACTIVE_25_POST = [m if m != "neumayr" else "gruber" for m in ACTIVE_25_PRE]

# BPU 2022-11-17: 12 Mitglieder (KEIN Welter, Reif und John regulär)
BPU_2022 = ["dollinger","hadersdorfer","stanglmaier","beubl","gruebl","kieninger",
            "beibl","linz_karin","linz_kilian","reif","tristl","john"]

def named(yes, no, absent, rejected=False):
    d = {"type":"named","results":{"yes":list(yes),"no":list(no),"absent":list(absent)}}
    if rejected: d["result"]="rejected"
    return d

def anon(y, n, ab, rejected=False, voters=None):
    d = {"type":"anonymous","results":{"yes":y,"no":n,"absent":ab}}
    if rejected: d["result"]="rejected"
    if voters: d["voters"]=voters
    return d

new_sessions = []
new_votes = []

# ── SR 2022-09-05 (14. StR) ──────────────────────────────────────────────────
A = ["beubl","kaestl","lauterbach","tristl","weber"]
new_sessions.append({
    "id":"sr_20220905","date":"2022-09-05","type":"stadtrat",
    "title":"14. Stadtratssitzung – September 2022","absent":A,
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Genehmigung Niederschriften (StR 04.04., 04./11./18./25.07.2022)","voteId":"sr_20220905_01"},
        {"number":4,"title":"Sondergebiet Amperauen","type":"discussion"},
        {"number":"4.1","title":"Amperauen – Planungskonzept + Fortführung Bauleitplanung B-Plan 63","voteId":"sr_20220905_02","topicId":"t20"},
        {"number":"4.2","title":"Straßennamenbezeichnung Sondergebiet Amperauen – „Amperpark\"","voteId":"sr_20220905_03","topicId":"t20"},
        {"number":5,"title":"Haushaltsmittel Sturmereignis 20.06.2022 – 100.000 €","voteId":"sr_20220905_04","topicId":"t7"},
        {"number":6,"title":"Antrag Seniorenreferentin Linz – Seniorenbeiratswahl per Briefwahl","voteId":"sr_20220905_05"},
        {"number":7,"title":"Bundesprogramm Sanierung kommunaler Einrichtungen (SJK 2022)","voteId":"sr_20220905_06","topicId":"t12"},
        {"number":8,"title":"KITA Erzgebirgsstraße – 3 Kindergartengruppen","voteId":"sr_20220905_07"},
        {"number":9,"title":"Anfragen","type":"formal"},
    ]})

R = ACTIVE_25_PRE
def yes_(absent): return [m for m in R if m not in absent]

new_votes += [
{"id":"sr_20220905_01","sessionId":"sr_20220905","topicId":None,"date":"2022-09-05",
 "title":"Genehmigung Niederschriften (5 Sitzungen)","text":"NSch Q2/Q3 2022 (öff.) genehmigt.",
 **anon(18,0,7)},
{"id":"sr_20220905_02","sessionId":"sr_20220905","topicId":"t20","date":"2022-09-05",
 "title":"Amperauen – Planungskonzept + Fortführung B-Plan 63","text":"Verwaltung wird mit Fortführung des Bebauungsplans Nr. 63 „SO Amperauen\" gemäß Konzeptvergabe-Gewinner beauftragt; einheitliches Sondergebiet Einzelhandel statt SO+GE-Teilung.",
 **named(yes_(A), [], A)},
{"id":"sr_20220905_03","sessionId":"sr_20220905","topicId":"t20","date":"2022-09-05",
 "title":"Amperauen – Straßenname „Amperpark\"","text":"Neue Erschließungsstraße im SO Amperauen wird „Amperpark\" benannt (12:8 knapp).",
 **anon(12,8,5)},
{"id":"sr_20220905_04","sessionId":"sr_20220905","topicId":"t7","date":"2022-09-05",
 "title":"Haushaltsmittel Sturmereignis 20.06.2022 – 100.000 €","text":"Mittel für Sturmschäden bereitgestellt, Deckung aus Verwaltungshaushalt-Deckungsreserve.",
 **named(yes_(A), [], A)},
{"id":"sr_20220905_05","sessionId":"sr_20220905","topicId":None,"date":"2022-09-05",
 "title":"Seniorenbeiratswahl per Briefwahl","text":"Nach 2 abgelehnten Gegenanträgen schließlich beschlossen: Seniorenbeiratswahl Jan/Feb 2023 als reine Briefwahl (14:6).",
 **anon(14,6,5)},
{"id":"sr_20220905_06","sessionId":"sr_20220905","topicId":"t12","date":"2022-09-05",
 "title":"Bundesprogramm SJK 2022 – Teilnahme","text":"Stadtrat beschließt Teilnahme am Bundesprogramm Sanierung kommunaler Einrichtungen in Sport, Jugend und Kultur, Projektaufruf 2022.",
 **named(yes_(A), [], A)},
{"id":"sr_20220905_07","sessionId":"sr_20220905","topicId":None,"date":"2022-09-05",
 "title":"KITA Erzgebirgsstraße – 3 Kindergartengruppen","text":"Kindertagesstätte mit drei Kindergartengruppen auf Fl.Nr. 1999 beschlossen; Verwaltung darf Planungs-Angebote einholen.",
 **named(yes_(A), [], A)},
]

# ── SR 2022-09-19 (15. StR) ──────────────────────────────────────────────────
A = ["hadersdorfer","stanglmaier","beubl","pschorr","weber","welter"]
new_sessions.append({
    "id":"sr_20220919","date":"2022-09-19","type":"stadtrat",
    "title":"15. Stadtratssitzung – September 2022","absent":A,
    "agenda":[
        {"number":2,"title":"Mitteilungen","type":"formal"},
        {"number":3,"title":"Bürgerfragen","type":"formal"},
        {"number":"4.1","title":"Mehrkosten Baumaßnahme „An der Lände\"","voteId":"sr_20220919_01"},
        {"number":"4.2","title":"Mehrkosten Baumaßnahme „Wendeplatz Thonstetten\"","voteId":"sr_20220919_02"},
        {"number":5,"title":"Verkaufsoffener Sonntag 16. Oktober 2022","voteId":"sr_20220919_03"},
        {"number":6,"title":"Stadtgrünverordnung Moosburg","type":"discussion"},
        {"number":"6.1","title":"Stadtgrünverordnung – Stellungnahme 08.03.2022","voteId":"sr_20220919_04"},
        {"number":"6.2","title":"Stadtgrünverordnung – Stellungnahme 14.03.2022","voteId":"sr_20220919_05"},
        {"number":"6.3","title":"Stadtgrünverordnung – Stellungnahme 15.03.2022","voteId":"sr_20220919_06"},
        {"number":"6.4","title":"Stadtgrünverordnung – Stellungnahme 21.03.2022","voteId":"sr_20220919_07"},
        {"number":"6.5","title":"Stadtgrünverordnung – Stellungnahme LRA Freising 30.05.2022","voteId":"sr_20220919_08"},
        {"number":"6.6","title":"Stadtgrünverordnung – Erlass der Verordnung","voteId":"sr_20220919_09"},
        {"number":"7.1","title":"Eisstadion – Gebührensatzung","voteId":"sr_20220919_10"},
        {"number":"7.2","title":"Kleinschwimmhalle – Gebührenanpassung Saison 2022/23","voteId":"sr_20220919_11","topicId":"t12"},
        {"number":8,"title":"Anfragen","type":"formal"},
    ]})

R = ACTIVE_25_PRE
new_votes += [
{"id":"sr_20220919_01","sessionId":"sr_20220919","topicId":None,"date":"2022-09-19",
 "title":"Mehrkosten „An der Lände\"","text":"Überplanmäßige Haushaltsmittel genehmigt.",**anon(18,0,7)},
{"id":"sr_20220919_02","sessionId":"sr_20220919","topicId":None,"date":"2022-09-19",
 "title":"Mehrkosten „Wendeplatz Thonstetten\"","text":"Überplanmäßige Haushaltsmittel genehmigt.",**anon(18,0,7)},
{"id":"sr_20220919_03","sessionId":"sr_20220919","topicId":None,"date":"2022-09-19",
 "title":"Verkaufsoffener Sonntag 16.10.2022","text":"Verordnung zum verkaufsoffenen Sonntag erlassen (17:1).",**anon(17,1,7)},
{"id":"sr_20220919_04","sessionId":"sr_20220919","topicId":None,"date":"2022-09-19",
 "title":"Stadtgrünverordnung – Stellungnahme 08.03.","text":"Stellungnahme zur Kenntnis; keine Verschärfung nötig (10:9).",**anon(10,9,6)},
{"id":"sr_20220919_05","sessionId":"sr_20220919","topicId":None,"date":"2022-09-19",
 "title":"Stadtgrünverordnung – Stellungnahme 14.03.","text":"Stellungnahme zur Kenntnis; §§ 4/5 als zwingend erforderlich festgestellt (10:9).",**anon(10,9,6)},
{"id":"sr_20220919_06","sessionId":"sr_20220919","topicId":None,"date":"2022-09-19",
 "title":"Stadtgrünverordnung – Stellungnahme 15.03.","text":"Geltungsbereich Kirchamper/Niederambach bestätigt; Ersatzpflanzungs-Kosten als verhältnismäßig erachtet (15:4).",**anon(15,4,6)},
{"id":"sr_20220919_07","sessionId":"sr_20220919","topicId":None,"date":"2022-09-19",
 "title":"Stadtgrünverordnung – Stellungnahme 21.03.","text":"Stellungnahme zur Kenntnis; Tatbestand auch für Bäume >150 cm Durchmesser bleibt (10:9).",**anon(10,9,6)},
{"id":"sr_20220919_08","sessionId":"sr_20220919","topicId":None,"date":"2022-09-19",
 "title":"Stadtgrünverordnung – Stellungnahme LRA Freising","text":"Anmerkungen LRA übernommen, Verordnung nicht verschärft (10:9).",**anon(10,9,6)},
{"id":"sr_20220919_09","sessionId":"sr_20220919","topicId":None,"date":"2022-09-19",
 "title":"Stadtgrünverordnung – Erlass zum 01.10.2022","text":"Stadtgrünverordnung in Fassung 20.09.2022 zum 01.10.2022 erlassen (12:7).",**anon(12,7,6)},
{"id":"sr_20220919_10","sessionId":"sr_20220919","topicId":None,"date":"2022-09-19",
 "title":"Eisstadion – Gebührensatzung","text":"Neue Gebühren (Einzel/Mehrfachkarten/Mietpreise) beschlossen, Auswärtige-Vereins-Miete 100→120 €.",**anon(19,0,6)},
{"id":"sr_20220919_11","sessionId":"sr_20220919","topicId":"t12","date":"2022-09-19",
 "title":"Kleinschwimmhalle – Gebühren 2022/23","text":"Erhöhung der Gebühren und Anpassung der Badegebührenordnung.",**anon(19,0,6)},
]

# ── SR 2022-10-24 (17. StR — Niederlegung/Eintritt Gruber) ───────────────────
# Gruber bereits regulär! Anwesend 23, Abwesend 2 (Beubl, Fincke).
A = ["beubl","fincke"]
R = ACTIVE_25_POST  # gruber statt neumayr
new_sessions.append({
    "id":"sr_20221024","date":"2022-10-24","type":"stadtrat",
    "title":"17. Stadtratssitzung – Oktober 2022 (Niederlegung Neumayr, Eintritt Gruber)","absent":A,
    "agenda":[
        {"number":5,"title":"Mitteilungen","type":"formal"},
        {"number":6,"title":"Bürgerfragen","type":"formal"},
        {"number":7,"title":"Genehmigung Niederschrift StR 05.09.","voteId":"sr_20221024_01"},
        {"number":8,"title":"B-Plan 77 „Rockermaier Areal\" – Stellungnahmen","type":"discussion","topicId":"t5"},
        {"number":"8.1","title":"Vorstellung der Planung Rockermaier Areal","type":"discussion","topicId":"t5"},
        {"number":"8.2–8.16","title":"Sammelvote: 15 Behördenstellungnahmen Rockermaier (einstimmig)","voteId":"sr_20221024_02","topicId":"t5"},
        {"number":"8.17","title":"Stellungnahme Evang.-Luth. Kirchengemeinde","voteId":"sr_20221024_03","topicId":"t5"},
        {"number":"8.18–8.30","title":"Sammelvote: weitere Behördenstellungnahmen + Verkehrsgutachten-Fortschreibung + 1. priv. Einwand (einstimmig)","voteId":"sr_20221024_04","topicId":"t5"},
        {"number":"8.29.1a","title":"Antrag Stanglmaier: Vertagung weiterer Einwendungen","voteId":"sr_20221024_05","topicId":"t5"},
        {"number":"8.31","title":"Privater Einwand 2 – mit Gesamtkonzept Schulbedarf","voteId":"sr_20221024_06","topicId":"t5"},
        {"number":"8.33","title":"Privater Einwand 4 – Energie/Nachhaltigkeit-Hinweise","voteId":"sr_20221024_07","topicId":"t5"},
        {"number":"8.38","title":"Privater Einwand 9 – Planänderungen veranlasst","voteId":"sr_20221024_08","topicId":"t5"},
        {"number":"8.32–8.63","title":"Sammelvote: ~30 weitere private Einwendungen Rockermaier (überwiegend 21:0/22:0)","voteId":"sr_20221024_09","topicId":"t5"},
        {"number":"8.64","title":"Rockermaier – Erneute Auslegung des geänderten Planentwurfs","voteId":"sr_20221024_10","topicId":"t5"},
        {"number":9,"title":"Anfragen","type":"formal"},
    ]})

new_votes += [
{"id":"sr_20221024_01","sessionId":"sr_20221024","topicId":None,"date":"2022-10-24",
 "title":"Genehmigung Niederschrift 05.09.2022","text":"NSch (öff.+nichtöff.) genehmigt.",
 **named(yes_([m for m in R if m in A]+[]) if False else [m for m in R if m not in A], [], A)},
{"id":"sr_20221024_02","sessionId":"sr_20221024","topicId":"t5","date":"2022-10-24",
 "title":"Rockermaier – Sammelvote 15 Behördenstellungnahmen","text":"15 Stellungnahmen (Kreisarchäologie, Vermessung, Ordinariat, Vodafone, Bader Energie, Wasserwerk, Kläranlage, Bauernverband, VG Mauern, bayernets, EBA, Staatl. Bauamt, Energienetze, Reg. Oberbayern, Reg. Planungsverband) – jeweils 22:0 einstimmig.",
 **anon(22,0,3)},
{"id":"sr_20221024_03","sessionId":"sr_20221024","topicId":"t5","date":"2022-10-24",
 "title":"Rockermaier – Evang.-Luth. Kirchengemeinde","text":"Stellungnahme zur Kenntnis; keine Planänderung veranlasst (13:9 split).",
 **anon(13,9,3)},
{"id":"sr_20221024_04","sessionId":"sr_20221024","topicId":"t5","date":"2022-10-24",
 "title":"Rockermaier – Sammelvote 13 Behörden + Verkehrsgutachten + 1. Einwand","text":"13 weitere Behörden-Stellungnahmen (Wasserwirtschaftsamt, Kreisbrandrat, Gesundheits-/Ortsplanungs-/Naturschutz-/Immissionsschutz-/Altlasten-Amt, Straßenverkehrsbeh. B2, ALF Erding, Telekom, SWM Infrastruktur, Heinz Entsorgung) + Fortschreibung Verkehrsgutachten + Einwender 1 – alle 22:0.",
 **anon(22,0,3)},
{"id":"sr_20221024_05","sessionId":"sr_20221024","topicId":"t5","date":"2022-10-24",
 "title":"Vertagung weiterer Einwendungen (Antrag Stanglmaier)","text":"Vertagung der TOPe 8.30 ff. mit 11:11 Stimmen abgelehnt.",
 **anon(11,11,3,rejected=True)},
{"id":"sr_20221024_06","sessionId":"sr_20221024","topicId":"t5","date":"2022-10-24",
 "title":"Rockermaier – Einwender 2: Gesamtkonzept Schulbedarf","text":"Stellungnahme zur Kenntnis; Beschluss, bis zur 2. Auslegung ein Gesamtkonzept für den Schulbedarf zu erstellen (22:0 nach 1. Anlauf 11:11).",
 **anon(22,0,3)},
{"id":"sr_20221024_07","sessionId":"sr_20221024","topicId":"t5","date":"2022-10-24",
 "title":"Rockermaier – Einwender 4 (Energie/Nachhaltigkeit)","text":"Stellungnahme zur Kenntnis; Hinweise zu Energie/Nachhaltigkeit als ausreichend erachtet (12:9 split, Kästl kurz abwesend).",
 **anon(12,9,4)},
{"id":"sr_20221024_08","sessionId":"sr_20221024","topicId":"t5","date":"2022-10-24",
 "title":"Rockermaier – Einwender 9","text":"Notwendige Planänderungen bereits veranlasst (12:9 split, Linz kurz abwesend).",
 **anon(12,9,4)},
{"id":"sr_20221024_09","sessionId":"sr_20221024","topicId":"t5","date":"2022-10-24",
 "title":"Rockermaier – Sammelvote ~30 private Einwendungen","text":"Restliche private Einwendungen (Einwender 3, 5-8, 10-31, 33-34 + Bürgerinitiative „Für ein lebenswertes Moosburg\") und Beschlüsse zu Verkehrsgutachten/Schulbedarf – überwiegend 21:0/22:0 einstimmig zugestimmt.",
 **anon(22,0,3)},
{"id":"sr_20221024_10","sessionId":"sr_20221024","topicId":"t5","date":"2022-10-24",
 "title":"Rockermaier – Erneute Auslegung des Planentwurfs","text":"Planunterlagen Fassung 24.10.2022 zur erneuten öffentlichen Auslegung gemäß § 3 Abs. 2 BauGB gebilligt.",
 **named([m for m in R if m not in A], [], A)},
]

# ── BPU 2022-11-17 (5. BPU) ──────────────────────────────────────────────────
# BPU 2022 ohne Welter. Substitutes: Grundner für Reif (ab Start), Kästl für John (ab 19:40).
# Grübl kommt erst ab 19:10. Welter komplett abwesend (kein Stellv).
# vote 3 = vor 19:10 (10 voters: Grübl & john_seat absent)
# vote 4.1-4.4 = nach 19:10, vor 19:40 (11: john_seat absent)
# vote 4.5+ = nach 19:40 (12 voters: vollbesetzt mit Substitutes)

BPU_FULL = ["dollinger","hadersdorfer","stanglmaier","beubl","gruebl","kieninger",
            "beibl","linz_karin","linz_kilian","grundner","tristl","kaestl"]
# Vote 3 (vor 19:10): grübl + kästl absent → 10 yes
BPU_V3 = [m for m in BPU_FULL if m not in ["gruebl","kaestl"]]
# Vote 4.1-4.4: kästl absent → 11 voters
BPU_PRE_KAESTL = [m for m in BPU_FULL if m != "kaestl"]

new_sessions.append({
    "id":"bpu_20221117","date":"2022-11-17","type":"bpu",
    "title":"5. BPU – November 2022","absent":["welter"],
    "substitutes":[{"member":"reif","substitute":"grundner"},
                   {"member":"john","substitute":"kaestl"}],
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Genehmigung NSch BPU 26.09.2022","voteId":"bpu_20221117_01"},
        {"number":"4.1","title":"Wohn-/Ärztehaus 10 WE Landshuter Str. 22 (mit Längsparker-Empfehlung)","voteId":"bpu_20221117_02"},
        {"number":"4.2","title":"Hackschnitzelheizzentrale Böhmerwaldstr. 41","voteId":"bpu_20221117_03","topicId":"t15"},
        {"number":"4.3","title":"Vorbescheid Mehrparteienhaus 5 WE Stellwerkstr. 40","voteId":"bpu_20221117_04"},
        {"number":"4.4","title":"Landwirtschaftliche Lagerhalle Pillhofen","voteId":"bpu_20221117_05"},
        {"number":"4.5","title":"Einzelhandelsmarkt mit Ärzte-Einheiten Neue Industriestr. 7","voteId":"bpu_20221117_06"},
        {"number":"4.6","title":"Wohnbebauung Landshuter Str. – Sammel (10 Häuser + Lärmschutzwand)","voteId":"bpu_20221117_07"},
        {"number":"4.6.3","title":"Landshuter Str. – Haus 2 (6 WE) Einvernehmen","voteId":"bpu_20221117_08"},
        {"number":"4.6.7","title":"Landshuter Str. – Haus 6 (6 WE) Einvernehmen","voteId":"bpu_20221117_09"},
        {"number":"4.7","title":"Mehrfamilienhaus Goethestr. 4","voteId":"bpu_20221117_10"},
        {"number":"4.8–4.10","title":"Sammelvote: 3 isolierte Befreiungs-Anträge (Amperaustr. 5, Oleanderstr. 4 + 22) – Befreiungen verweigert","voteId":"bpu_20221117_11"},
        {"number":5,"title":"Anfragen","type":"formal"},
    ]})

new_votes += [
{"id":"bpu_20221117_01","sessionId":"bpu_20221117","topicId":None,"date":"2022-11-17",
 "title":"Genehmigung NSch BPU 26.09.2022","text":"Niederschrift einstimmig genehmigt (10:0; vor Eintreffen Grübl/Kästl).",
 **named(BPU_V3,[],["welter","gruebl"])},  # 10+0+2 = 12 (john's seat empty before sub arrived → counted as absent)
{"id":"bpu_20221117_02","sessionId":"bpu_20221117","topicId":None,"date":"2022-11-17",
 "title":"Landshuter Str. 22 – Wohn-/Ärztehaus 10 WE + Längsparker","text":"Einvernehmen erteilt und Längsparker-Empfehlung beschlossen (Mehrfachbeschluss 6:5).",
 **anon(6,5,1)},
{"id":"bpu_20221117_03","sessionId":"bpu_20221117","topicId":"t15","date":"2022-11-17",
 "title":"Hackschnitzelheizzentrale Böhmerwaldstr. 41 – Erweiterung","text":"Einvernehmen zum Umbau der Heizzentrale mit 3. Hackschnitzelkessel + neuer Abgaskaminanlage erteilt.",
 **named(BPU_PRE_KAESTL,[],["welter","john"])},
{"id":"bpu_20221117_04","sessionId":"bpu_20221117","topicId":None,"date":"2022-11-17",
 "title":"Vorbescheid Mehrparteienhaus Stellwerkstr. 40","text":"Einvernehmen erteilt (7:4).",**anon(7,4,1)},
{"id":"bpu_20221117_05","sessionId":"bpu_20221117","topicId":None,"date":"2022-11-17",
 "title":"Lagerhalle Pillhofen","text":"Einvernehmen erteilt (einstimmig 11:0).",
 **named(BPU_PRE_KAESTL,[],["welter","john"])},
{"id":"bpu_20221117_06","sessionId":"bpu_20221117","topicId":None,"date":"2022-11-17",
 "title":"Einzelhandelsmarkt + Ärzte Neue Industriestr. 7","text":"Einvernehmen + Satzungs-Befreiungen einstimmig erteilt.",
 **named(BPU_FULL,[],["welter"])},
{"id":"bpu_20221117_07","sessionId":"bpu_20221117","topicId":None,"date":"2022-11-17",
 "title":"Landshuter Str. – Wohnbebauung Sammelvote (10 Häuser + Lärmschutzwand)","text":"Sammel-Einvernehmen für Haus 1.1, 1.2, 3, 4, 5, 7.1-7.3 (jeweils 9:3) und Lärmschutzwand (10:2). Haus 2 und Haus 6 separat abgelehnt.",
 **anon(9,3,0)},
{"id":"bpu_20221117_08","sessionId":"bpu_20221117","topicId":None,"date":"2022-11-17",
 "title":"Landshuter Str. – Haus 2 (6 WE) Einvernehmen","text":"Einvernehmen NICHT erteilt – Patt 6:6.",
 **anon(6,6,0,rejected=True)},
{"id":"bpu_20221117_09","sessionId":"bpu_20221117","topicId":None,"date":"2022-11-17",
 "title":"Landshuter Str. – Haus 6 (6 WE) Einvernehmen","text":"Einvernehmen NICHT erteilt – Patt 6:6.",
 **anon(6,6,0,rejected=True)},
{"id":"bpu_20221117_10","sessionId":"bpu_20221117","topicId":None,"date":"2022-11-17",
 "title":"Mehrfamilienhaus Goethestr. 4","text":"Einvernehmen erteilt (8:4).",**anon(8,4,0)},
{"id":"bpu_20221117_11","sessionId":"bpu_20221117","topicId":None,"date":"2022-11-17",
 "title":"3 isolierte Befreiungs-Anträge – Sammelvote","text":"Befreiungen für Granitsäulen/Gabionenzaun Amperaustr. 5, Zaun 1,85 m Oleanderstr. 4 und Einfriedung 1,80 m Oleanderstr. 22 jeweils einstimmig 12:0 NICHT erteilt (Befreiung verweigert = Beschluss angenommen).",
 **named(BPU_FULL,[],["welter"])},
]

# ── Apply ────────────────────────────────────────────────────────────────────
with open(f"{BASE}/sessions.json", encoding="utf-8") as f: sessions = json.load(f)
with open(f"{BASE}/votes.json", encoding="utf-8") as f: votes = json.load(f)

existing_sids = {s["id"] for s in sessions}
existing_vids = {v["id"] for v in votes}
for s in new_sessions:
    if s["id"] in existing_sids: print(f"! skip {s['id']} (already exists)")
    else: sessions.append(s); print(f"+ session {s['id']}")
for v in new_votes:
    if v["id"] in existing_vids: print(f"! skip vote {v['id']}")
    else: votes.append(v)

sessions.sort(key=lambda s: s["date"])
votes.sort(key=lambda v: (v["date"], v["id"]))

# ── Topic history additions ──────────────────────────────────────────────────
with open(f"{BASE}/topics.json", encoding="utf-8") as f: topics = json.load(f)
T = {t["id"]:t for t in topics}

extras = [
    ("t20", {"date":"2022-09-05","type":"vote","title":"Amperauen – B-Plan 63 Planungskonzept beschlossen",
            "text":"Fortführung des Bebauungsplans Nr. 63 „SO Amperauen\" auf Grundlage des Konzeptvergabe-Gewinners; einheitliches Sondergebiet Einzelhandel.",
            "sessionId":"sr_20220905","voteId":"sr_20220905_02"}),
    ("t20", {"date":"2022-09-05","type":"vote","title":"Amperauen – Straßenname „Amperpark\" (12:8)",
            "text":"Knapp mehrheitlich für „Amperpark\" als Name der neuen Erschließungsstraße.",
            "sessionId":"sr_20220905","voteId":"sr_20220905_03"}),
    ("t7",  {"date":"2022-09-05","type":"vote","title":"Sturmschäden Juni 2022 – 100.000 € Haushaltsmittel",
            "text":"Mittelbereitstellung für Schäden des Sturmereignisses 20.06.2022.",
            "sessionId":"sr_20220905","voteId":"sr_20220905_04"}),
    ("t5",  {"date":"2022-10-24","type":"milestone","title":"Rockermaier-Areal – Abwägung B-Plan 77 + erneute Auslegung",
            "text":"17. Stadtratssitzung: ~60 Stellungnahmen (Behörden + 31 Bürger + Bürgerinitiative) abgewogen, Verkehrsgutachten fortgeschrieben, Gesamtkonzept Schulbedarf in Auftrag, Planentwurf 24.10.2022 zur erneuten Auslegung gebilligt.",
            "sessionId":"sr_20221024","voteId":"sr_20221024_10"}),
    ("t15", {"date":"2022-11-17","type":"vote","title":"Hackschnitzelheizzentrale Böhmerwaldstr. – Erweiterung",
            "text":"BPU erteilt Einvernehmen zum Umbau mit drittem Hackschnitzelkessel.",
            "sessionId":"bpu_20221117","voteId":"bpu_20221117_03"}),
    ("t12", {"date":"2022-09-05","type":"milestone","title":"Bundesprogramm Schwimmbäder/SJK 2022 – Teilnahme",
            "text":"Teilnahme am Bundesprogramm „Sanierung kommunaler Einrichtungen in den Bereichen Sport, Jugend und Kultur\" einstimmig beschlossen.",
            "sessionId":"sr_20220905","voteId":"sr_20220905_06"}),
    ("t12", {"date":"2022-09-19","type":"vote","title":"Kleinschwimmhalle – Gebührenanpassung 2022/23",
            "text":"Gebührenerhöhung in der vorliegenden Fassung beschlossen.",
            "sessionId":"sr_20220919","voteId":"sr_20220919_11"}),
]
for tid, entry in extras:
    if tid not in T: print(f"! topic {tid} fehlt – skip"); continue
    hist = T[tid].setdefault("history", [])
    if any(h.get("voteId")==entry.get("voteId") for h in hist): continue
    hist.append(entry)
    hist.sort(key=lambda h: h["date"])
    print(f"  ~ {tid} += {entry['date']} {entry['title'][:55]}")

# ── Member period correction: Neumayr.to / Gruber.from ───────────────────────
with open(f"{BASE}/members.json", encoding="utf-8") as f: members_doc = json.load(f)
for m in members_doc["members"]:
    if m["id"] == "neumayr":
        if m.get("to") != "2022-10-23":
            print(f"  ~ neumayr.to: {m.get('to')} → 2022-10-23")
            m["to"] = "2022-10-23"
    elif m["id"] == "gruber":
        if m.get("from") != "2022-10-24":
            print(f"  ~ gruber.from: {m.get('from')} → 2022-10-24")
            m["from"] = "2022-10-24"

# ── Save ─────────────────────────────────────────────────────────────────────
with open(f"{BASE}/sessions.json","w",encoding="utf-8") as f: json.dump(sessions,f,ensure_ascii=False,indent=2)
with open(f"{BASE}/votes.json","w",encoding="utf-8") as f: json.dump(votes,f,ensure_ascii=False,indent=2)
with open(f"{BASE}/topics.json","w",encoding="utf-8") as f: json.dump(topics,f,ensure_ascii=False,indent=2)
with open(f"{BASE}/members.json","w",encoding="utf-8") as f: json.dump(members_doc,f,ensure_ascii=False,indent=2)

print(f"\nDone. sessions: +{len(new_sessions)} (total {len(sessions)}), votes: +{len(new_votes)} (total {len(votes)})")
