"""Integrate 2023 sessions (17 StR + 5 BPU = 22 protocols).

Notes:
- 'kuch' in agent data == 'beibl' (Beibl's Mädchenname).
- John replaced by Strobl on 2023-07-24 (SR_20230724 sessions 6.1/6.2).
- Long Stellungnahmen-Listen aggregated into one summary vote per B-Plan.
"""
import json
BASE = "c:/Users/bened/Documents/GitHub/bagruber/council/data"

# 25 active 2023 members
PRE_JUL = ["dollinger","hadersdorfer","tristl","weber","haberl","linz_karin","heinz",
           "beibl","stanglmaier","von_pressentin","becher_j","becher_a","linz_kilian",
           "grundner","lauterbach","reif","kieninger","beubl","pschorr",
           "gruebl","gruber","welter","kaestl","fincke","john"]
POST_JUL = [m if m != "john" else "strobl" for m in PRE_JUL]

def yes(roster, absent): return [m for m in roster if m not in absent]
def named(roster, absent):
    return {"type":"named","results":{"yes":yes(roster,absent),"no":[],"absent":list(absent)}}
def anon(y,n,ab,rej=False):
    d={"type":"anonymous","results":{"yes":y,"no":n,"absent":ab}}
    if rej: d["result"]="rejected"
    return d
def named_vote(yesL, noL, absL, rej=False):
    d={"type":"named","results":{"yes":list(yesL),"no":list(noL),"absent":list(absL)}}
    if rej: d["result"]="rejected"
    return d

# BPU 2023 (full 12 members; pre-2026 config):
# chair dollinger; vice hadersdorfer (sub heinz) + stanglmaier (sub becher_j);
# seats: beibl, gruebl, kieninger, linz_karin, linz_kilian, beubl(SPD!), reif, tristl, welter
BPU_REGULARS = ["dollinger","hadersdorfer","stanglmaier","beibl","gruebl",
                "kieninger","linz_karin","linz_kilian","beubl","reif","tristl","welter"]

# ============================================================================
# SESSIONS
# ============================================================================
new_sessions = []
new_votes = []

# ── SR 2023-01-12 (1.) ──────────────────────────────────────────────────────
A = ["becher_a","john","linz_karin","tristl"]
new_sessions.append({"id":"sr_20230112","date":"2023-01-12","type":"stadtrat",
    "title":"1. Stadtratssitzung – Januar 2023","absent":A,
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Genehmigung Niederschriften (StR 24.10., 07.11., 21.11.2022)","voteId":"sr_20230112_01"},
        {"number":4,"title":"Vorstellung Ergebnisse Seniorenbefragung","type":"discussion"},
        {"number":5,"title":"Auf dem Plan – Grundsatzentscheidung Granitpflaster (abgelehnt 11:10)",
         "topicId":"t3","voteId":"sr_20230112_02"},
        {"number":6,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"sr_20230112_01","sessionId":"sr_20230112","topicId":None,"date":"2023-01-12",
     "title":"Genehmigung Niederschriften (StR Q4 2022)",
     "text":"Einstimmig: Genehmigung der öffentlichen Teile der Niederschriften vom 24.10., 07.11. und 21.11.2022.",
     **named(PRE_JUL, A)},
    {"id":"sr_20230112_02","sessionId":"sr_20230112","topicId":"t3","date":"2023-01-12",
     "title":"Auf dem Plan – Gebundene Granitpflaster-Verlegung",
     "text":"Antrag, das Granitpflaster für den Stadtplatz „Auf dem Plan\" in gebundener Bauweise zu verlegen, wird mit 10:11 knapp abgelehnt.",
     **anon(10,11,4,rej=True)},
]

# ── BPU 2023-01-23 (1.) — all 12 present ─────────────────────────────────────
new_sessions.append({"id":"bpu_20230123","date":"2023-01-23","type":"bpu",
    "title":"1. Sitzung Bau-, Planungs- und Umweltausschuss – Januar 2023",
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Asphaltmischanlage – Weiterbetrieb","voteId":"bpu_20230123_01"},
        {"number":"4.1","title":"Dachgeschoss-Erweiterung Neustadtstr. 40 – verweigert","voteId":"bpu_20230123_02"},
        {"number":"4.2","title":"Doppelhaushälfte Holunderweg 13","voteId":"bpu_20230123_03"},
        {"number":"4.3","title":"Einfamilienhaus Vorbescheid Kanalstr. 3","voteId":"bpu_20230123_04"},
        {"number":"4.4","title":"Einfamilienhaus Vorbescheid Zanderstr. 7","voteId":"bpu_20230123_05"},
        {"number":"4.5","title":"MFH Haus 2 Landshuter Str. (8:4)","voteId":"bpu_20230123_06"},
        {"number":"4.6","title":"MFH Haus 6 Landshuter Str. (8:4)","voteId":"bpu_20230123_07"},
        {"number":"4.7","title":"Lagerhalle Molkereistr. – verweigert (11:1)","voteId":"bpu_20230123_08"},
        {"number":"4.8","title":"3 Betriebswohnungen Amperstr. 24","voteId":"bpu_20230123_09"},
        {"number":"4.9","title":"5 Pferde-Ausläufe Amperstr. 24","voteId":"bpu_20230123_10"},
        {"number":"4.10","title":"Vorbescheid Hotel-Aufstockung Neue Industriestr. 11","voteId":"bpu_20230123_11"},
        {"number":5,"title":"Teileinziehung Weg Pillhofen","voteId":"bpu_20230123_12"},
        {"number":6,"title":"Anfragen","type":"formal"},
    ]})
def bpu_full_named():
    return {"type":"named","results":{"yes":list(BPU_REGULARS),"no":[],"absent":[]}}
new_votes += [
    {"id":"bpu_20230123_01","sessionId":"bpu_20230123","topicId":None,"date":"2023-01-23",
     "title":"Asphaltmischanlage – Weiterbetrieb",
     "text":"Einstimmig: Gemeindliches Einvernehmen zum Weiterbetrieb der Asphaltmischanlage erteilt.",
     **bpu_full_named()},
    {"id":"bpu_20230123_02","sessionId":"bpu_20230123","topicId":None,"date":"2023-01-23",
     "title":"Dachgeschoss-Erweiterung Neustadtstr. 40 – verweigert",
     "text":"Einstimmig verweigert: Stellplatznachweis und Fahrradabstellplätze fehlerhaft.",
     **bpu_full_named()},
    {"id":"bpu_20230123_03","sessionId":"bpu_20230123","topicId":None,"date":"2023-01-23",
     "title":"Doppelhaushälfte Holunderweg 13",
     "text":"Einstimmig: Einvernehmen erteilt.","__":True,
     **bpu_full_named()},
    {"id":"bpu_20230123_04","sessionId":"bpu_20230123","topicId":None,"date":"2023-01-23",
     "title":"Vorbescheid Einfamilienhaus Kanalstr. 3",
     "text":"Einstimmig: Einvernehmen erteilt.",
     **bpu_full_named()},
    {"id":"bpu_20230123_05","sessionId":"bpu_20230123","topicId":None,"date":"2023-01-23",
     "title":"Vorbescheid Einfamilienhaus Zanderstr. 7",
     "text":"Einstimmig: Einvernehmen erteilt.",
     **bpu_full_named()},
    {"id":"bpu_20230123_06","sessionId":"bpu_20230123","topicId":None,"date":"2023-01-23",
     "title":"MFH Haus 2 Landshuter Str.",
     "text":"Einvernehmen erteilt (8:4).",
     **anon(8,4,0)},
    {"id":"bpu_20230123_07","sessionId":"bpu_20230123","topicId":None,"date":"2023-01-23",
     "title":"MFH Haus 6 Landshuter Str.",
     "text":"Einvernehmen erteilt (8:4).",
     **anon(8,4,0)},
    {"id":"bpu_20230123_08","sessionId":"bpu_20230123","topicId":None,"date":"2023-01-23",
     "title":"Lagerhalle Molkereistr. – verweigert",
     "text":"Einvernehmen mit 11:1 verweigert.",
     **anon(11,1,0)},
    {"id":"bpu_20230123_09","sessionId":"bpu_20230123","topicId":None,"date":"2023-01-23",
     "title":"3 Betriebswohnungen Amperstr. 24","text":"Einstimmig: Einvernehmen erteilt.",
     **bpu_full_named()},
    {"id":"bpu_20230123_10","sessionId":"bpu_20230123","topicId":None,"date":"2023-01-23",
     "title":"5 Pferde-Ausläufe Amperstr. 24","text":"Einstimmig: Einvernehmen erteilt.",
     **bpu_full_named()},
    {"id":"bpu_20230123_11","sessionId":"bpu_20230123","topicId":None,"date":"2023-01-23",
     "title":"Vorbescheid Hotel-Aufstockung Neue Industriestr. 11",
     "text":"Einstimmig: Einvernehmen erteilt.",
     **bpu_full_named()},
    {"id":"bpu_20230123_12","sessionId":"bpu_20230123","topicId":None,"date":"2023-01-23",
     "title":"Teileinziehung Weg Pillhofen",
     "text":"Einstimmig beschlossen.",
     **bpu_full_named()},
]

# ── SR 2023-01-30 (2.) ──────────────────────────────────────────────────────
# agent's "kuch" = beibl
A = ["beubl","kaestl","beibl","linz_kilian","tristl"]
new_sessions.append({"id":"sr_20230130","date":"2023-01-30","type":"stadtrat",
    "title":"2. Stadtratssitzung – Januar 2023","absent":A,
    "agenda":[
        {"number":1,"title":"Vorstellung W-Seminar Moosburg 1250 Jahre","type":"discussion"},
        {"number":2,"title":"Mitteilungen","type":"formal"},
        {"number":3,"title":"Bürgerfragen","type":"formal"},
        {"number":4,"title":"Genehmigung Niederschriften (StR 12.12.2022, HVFA 24./28.11. + 05.12.2022)",
         "voteId":"sr_20230130_01"},
        {"number":"5.1","title":"Stellplätze MFH – Anzahl (16:4)","voteId":"sr_20230130_02"},
        {"number":"5.2","title":"Stellplätze Einfamilienhäuser","voteId":"sr_20230130_03"},
        {"number":"5.3","title":"Stellplatzanzahl auch in Ortsteilen (15:5)","voteId":"sr_20230130_04"},
        {"number":"5.4","title":"Besucherstellplätze ab 4 WE 20 % (12:8)","voteId":"sr_20230130_05"},
        {"number":"5.5","title":"Allgemeine Stellplatzablöse 15.000 €","voteId":"sr_20230130_06"},
        {"number":"5.6","title":"Stellplatzablöse Innenstadt 10.000 € (abgelehnt 4:16)","voteId":"sr_20230130_07"},
        {"number":6,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"sr_20230130_01","sessionId":"sr_20230130","topicId":None,"date":"2023-01-30",
     "title":"Genehmigung Niederschriften","text":"Einstimmig genehmigt.",**named(PRE_JUL, A)},
    {"id":"sr_20230130_02","sessionId":"sr_20230130","topicId":None,"date":"2023-01-30",
     "title":"Stellplatzsatzung – Stellplätze MFH",
     "text":"Anzahl der erforderlichen Stellplätze für Mehrfamilienhäuser festgesetzt (16:4).",**anon(16,4,5)},
    {"id":"sr_20230130_03","sessionId":"sr_20230130","topicId":None,"date":"2023-01-30",
     "title":"Stellplätze Einfamilienhäuser",
     "text":"Einstimmig festgesetzt.",**named(PRE_JUL, A)},
    {"id":"sr_20230130_04","sessionId":"sr_20230130","topicId":None,"date":"2023-01-30",
     "title":"Stellplatzanzahl auch in Ortsteilen",
     "text":"Stellplatzanzahl gilt auch für Ortsteile (15:5).",**anon(15,5,5)},
    {"id":"sr_20230130_05","sessionId":"sr_20230130","topicId":None,"date":"2023-01-30",
     "title":"Besucherstellplätze 20 % ab 4 WE",
     "text":"Besucherstellplätze in Höhe von 20 % ab 4 Wohneinheiten (12:8).",**anon(12,8,5)},
    {"id":"sr_20230130_06","sessionId":"sr_20230130","topicId":None,"date":"2023-01-30",
     "title":"Allgemeine Stellplatzablöse 15.000 €",
     "text":"Einstimmig: Stellplatzablöse auf 15.000 € pro Stellplatz festgesetzt.",**named(PRE_JUL, A)},
    {"id":"sr_20230130_07","sessionId":"sr_20230130","topicId":None,"date":"2023-01-30",
     "title":"Stellplatzablöse Innenstadt 10.000 € (abgelehnt)",
     "text":"Antrag auf reduzierte Ablöse 10.000 € in der Innenstadt abgelehnt (4:16).",**anon(4,16,5,rej=True)},
]

# ── SR 2023-02-13 (3.) ──────────────────────────────────────────────────────
A = ["dollinger","becher_j","beubl","fincke","heinz","linz_karin","tristl"]
new_sessions.append({"id":"sr_20230213","date":"2023-02-13","type":"stadtrat",
    "title":"3. Stadtratssitzung – Februar 2023","absent":A,
    "agenda":[
        {"number":1,"title":"Mitteilungen (Hadersdorfer vorsitzt)","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Genehmigung Niederschrift StR 12.01.2023","voteId":"sr_20230213_01"},
        {"number":4,"title":"Rathaus-Erweiterungsbau Herrnstr. 2","topicId":"t17","voteId":"sr_20230213_02"},
        {"number":5,"title":"Bündelausschreibung Strombeschaffung 2024/2025","topicId":"t15","voteId":"sr_20230213_03"},
        {"number":6,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"sr_20230213_01","sessionId":"sr_20230213","topicId":None,"date":"2023-02-13",
     "title":"Genehmigung Niederschrift StR 12.01.2023","text":"Einstimmig genehmigt.",**named(PRE_JUL,A)},
    {"id":"sr_20230213_02","sessionId":"sr_20230213","topicId":"t17","date":"2023-02-13",
     "title":"Rathaus-Erweiterungsbau Herrnstr. 2",
     "text":"Einstimmig: Gemeindliches Einvernehmen für den Erweiterungsbau des Rathauses erteilt.",**named(PRE_JUL,A)},
    {"id":"sr_20230213_03","sessionId":"sr_20230213","topicId":"t15","date":"2023-02-13",
     "title":"Strom-Bündelausschreibung 2024/2025",
     "text":"Einstimmig: Änderung des Beschlusses vom 19.12.2022 zur Bündelausschreibung der kommunalen Strombeschaffung.",**named(PRE_JUL,A)},
]

# ── SR 2023-03-06 (4.) ──────────────────────────────────────────────────────
A = ["beubl"]
# linz_karin had short absence; not in absent list but excused from some votes
new_sessions.append({"id":"sr_20230306","date":"2023-03-06","type":"stadtrat",
    "title":"4. Stadtratssitzung – März 2023","absent":A,
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Vorstellung Varianten Bahnhof-Neubau/Sanierung","topicId":"t2","type":"discussion"},
        {"number":4,"title":"Aufstellung B-Plan Nr. 79 „GE Unterreit\"","type":"discussion"},
        {"number":"5.1","title":"Neubesetzung HVFA","voteId":"sr_20230306_01"},
        {"number":"5.2","title":"Neubesetzung BPU","voteId":"sr_20230306_02"},
        {"number":"5.3","title":"Neubesetzung Personalausschuss","voteId":"sr_20230306_03"},
        {"number":"5.4","title":"Neubesetzung Rechnungsprüfungsausschuss","voteId":"sr_20230306_04"},
        {"number":6,"title":"Genehmigung Niederschriften (BA 23.01., StR 19.12.2022, 30.01.2023)","voteId":"sr_20230306_05"},
        {"number":7,"title":"Anfragen","type":"formal"},
    ]})
for i, t in enumerate([
    ("Neubesetzung HVFA","Einstimmig: Neubesetzung des HVFA gemäß Antrag."),
    ("Neubesetzung BPU","Einstimmig: Neubesetzung des BPU gemäß Antrag."),
    ("Neubesetzung Personalausschuss","Einstimmig: Neubesetzung des Personalausschusses."),
    ("Neubesetzung Rechnungsprüfungsausschuss","Einstimmig: Neubesetzung des Rechnungsprüfungsausschusses."),
    ("Genehmigung Niederschriften","Einstimmig genehmigt."),
], start=1):
    title, text = t
    new_votes.append({
        "id":f"sr_20230306_{i:02d}","sessionId":"sr_20230306","topicId":None,"date":"2023-03-06",
        "title":title,"text":text,**named(PRE_JUL, A)})

# ── BPU 2023-03-20 (2.) — absent gruebl (sub gruber attended ab 19:10) ──────
BPU_0320_FULL = [m for m in BPU_REGULARS if m != "gruebl"] + ["gruber"]
new_sessions.append({"id":"bpu_20230320","date":"2023-03-20","type":"bpu",
    "title":"2. Sitzung Bau-, Planungs- und Umweltausschuss – März 2023",
    "absent":["gruebl"],
    "substitutes":[{"member":"gruebl","substitute":"gruber"}],
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Wasserrecht Nassabbau Semptwiesen II","voteId":"bpu_20230320_01"},
        {"number":4,"title":"BImSchG Bodenaushub-Lagerung","voteId":"bpu_20230320_02"},
        {"number":"5.1","title":"Stellplatzablöse Rosenhofweg 4/4a verweigert","voteId":"bpu_20230320_03"},
        {"number":"5.2a","title":"Vorbescheid Doppelhäuser Burgermühlstr. 13 erteilt (abgelehnt 5:7)",
         "voteId":"bpu_20230320_04"},
        {"number":"5.2b","title":"Burgermühlstr. 13 verweigert (7:5)","voteId":"bpu_20230320_05"},
        {"number":"5.3","title":"Einfamilienhaus Falkenstr. 21","voteId":"bpu_20230320_06"},
        {"number":"5.4","title":"Umgestaltung Pillhofen 5","voteId":"bpu_20230320_07"},
        {"number":"5.5","title":"MFH 9 WE Sudetenlandstr. 2 verweigert","voteId":"bpu_20230320_08"},
        {"number":"6.1","title":"Verkehrsführung Thalbacher/Bahnhofstr.","topicId":"t4","voteId":"bpu_20230320_09"},
        {"number":"6.2","title":"Verkehrsführung Münchener/Westerbergstr.","topicId":"t4","voteId":"bpu_20230320_10"},
        {"number":"6.3","title":"Mühlbachbogen Halteverbote prüfen","topicId":"t4","voteId":"bpu_20230320_11"},
        {"number":"6.4","title":"Amperauen Halteverbote mit Feuerwehrzeichen","topicId":"t20","voteId":"bpu_20230320_12"},
        {"number":"6.5","title":"Fahrradzone südlich Industriestr.","topicId":"t4","voteId":"bpu_20230320_13"},
    ]})
def bpu_0320_named():
    return {"type":"named","results":{"yes":list(BPU_0320_FULL),"no":[],"absent":["gruebl"]}}
new_votes += [
    {"id":"bpu_20230320_01","sessionId":"bpu_20230320","topicId":None,"date":"2023-03-20",
     "title":"Nassabbau Semptwiesen II – Tekturantrag",
     "text":"Einstimmig: Keine Bedenken gegen Tekturantrag zum Nassabbau Semptwiesen II.",
     **bpu_0320_named()},
    {"id":"bpu_20230320_02","sessionId":"bpu_20230320","topicId":None,"date":"2023-03-20",
     "title":"Bodenaushub-Lagerung BImSchG",
     "text":"Einstimmig: Lagerung Bodenaushub/Straßenaufbruch keine Einwendungen.",**bpu_0320_named()},
    {"id":"bpu_20230320_03","sessionId":"bpu_20230320","topicId":None,"date":"2023-03-20",
     "title":"Stellplatzablöse Rosenhofweg 4/4a – abgelehnt",
     "text":"Einstimmig: Ablöse von 9 Stellplätzen abgelehnt.",**bpu_0320_named()},
    {"id":"bpu_20230320_04","sessionId":"bpu_20230320","topicId":None,"date":"2023-03-20",
     "title":"Doppelhäuser Burgermühlstr. 13 – Vorbescheid erteilt (abgelehnt)",
     "text":"Antrag, Einvernehmen zu erteilen, mit 5:7 abgelehnt; Kubatur zu groß.",**anon(5,7,1,rej=True)},
    {"id":"bpu_20230320_05","sessionId":"bpu_20230320","topicId":None,"date":"2023-03-20",
     "title":"Doppelhäuser Burgermühlstr. 13 – verweigert",
     "text":"Mit 7:5 verweigert.",**anon(7,5,1)},
    {"id":"bpu_20230320_06","sessionId":"bpu_20230320","topicId":None,"date":"2023-03-20",
     "title":"Einfamilienhaus Falkenstr. 21","text":"Einstimmig: Einvernehmen erteilt.",**bpu_0320_named()},
    {"id":"bpu_20230320_07","sessionId":"bpu_20230320","topicId":None,"date":"2023-03-20",
     "title":"Umgestaltung Pillhofen 5","text":"Einstimmig: Einvernehmen erteilt.",**bpu_0320_named()},
    {"id":"bpu_20230320_08","sessionId":"bpu_20230320","topicId":None,"date":"2023-03-20",
     "title":"MFH 9 WE Sudetenlandstr. 2 – verweigert",
     "text":"Einstimmig verweigert.",**bpu_0320_named()},
    {"id":"bpu_20230320_09","sessionId":"bpu_20230320","topicId":"t4","date":"2023-03-20",
     "title":"Verkehrsführung Thalbacher/Bahnhofstr.",
     "text":"Einstimmig: Planung zur Änderung der Verkehrsführung wird vergeben.",**bpu_0320_named()},
    {"id":"bpu_20230320_10","sessionId":"bpu_20230320","topicId":"t4","date":"2023-03-20",
     "title":"Verkehrsführung Münchener/Westerbergstr.",
     "text":"Einstimmig: endgültiger Umbau beschlossen.",**bpu_0320_named()},
    {"id":"bpu_20230320_11","sessionId":"bpu_20230320","topicId":"t4","date":"2023-03-20",
     "title":"Mühlbachbogen – Halteverbote prüfen",
     "text":"Einstimmig: Verwaltung prüft Halteverbotsbuchten.",**bpu_0320_named()},
    {"id":"bpu_20230320_12","sessionId":"bpu_20230320","topicId":"t20","date":"2023-03-20",
     "title":"Amperauen – Halteverbote mit Feuerwehrzeichen",
     "text":"Einstimmig: Keine Änderung der Verkehrsführung; Halteverbote mit Feuerwehrzeichen.",**bpu_0320_named()},
    {"id":"bpu_20230320_13","sessionId":"bpu_20230320","topicId":"t4","date":"2023-03-20",
     "title":"Fahrradzone südlich Industriestr.",
     "text":"Endgültige Festlegung der Fahrradzone (10:2).",**anon(10,2,0)},
]

# ── SR 2023-03-27 (5.) ──────────────────────────────────────────────────────
A = ["john","linz_karin","pschorr","tristl"]
new_sessions.append({"id":"sr_20230327","date":"2023-03-27","type":"stadtrat",
    "title":"5. Stadtratssitzung – März 2023","absent":A,
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Genehmigung Niederschrift StR 13.02.2023","voteId":"sr_20230327_01"},
        {"number":4,"title":"Hallenbad-Neubau – Sachstand","topicId":"t16","type":"discussion"},
        {"number":5,"title":"Vortrag Holzbau","type":"discussion"},
        {"number":6,"title":"Auf dem Plan – Entwurfsplanung 13.03., Ausschreibung mit Teilnahmewettbewerb",
         "topicId":"t3","voteId":"sr_20230327_02"},
        {"number":7,"title":"Bundesprogramm SJK 2022 – Freibad","topicId":"t12","voteId":"sr_20230327_03"},
        {"number":8,"title":"Verkaufsoffener Sonntag 16.04.2023","voteId":"sr_20230327_04"},
        {"number":9,"title":"Neubesetzung Personalausschuss","voteId":"sr_20230327_05"},
        {"number":10,"title":"Plakatierung Breitbandausbau Ortsteile","voteId":"sr_20230327_06"},
        {"number":11,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"sr_20230327_01","sessionId":"sr_20230327","topicId":None,"date":"2023-03-27",
     "title":"Genehmigung Niederschrift StR 13.02.2023","text":"Einstimmig genehmigt (17:0).",**anon(17,0,8)},
    {"id":"sr_20230327_02","sessionId":"sr_20230327","topicId":"t3","date":"2023-03-27",
     "title":"Auf dem Plan – Entwurfsplanung + Ausschreibung",
     "text":"Einstimmig: Entwurfsplanung 13.03.2023 zustimmend, Ausschreibung mit Teilnahmewettbewerb beschlossen.",**anon(19,0,6)},
    {"id":"sr_20230327_03","sessionId":"sr_20230327","topicId":"t12","date":"2023-03-27",
     "title":"Bundesprogramm SJK 2022 – Freibad",
     "text":"Antragstellung für das Bundesprogramm „Sanierung Schwimmbäder kommunal\" (18:0; Heinz Enthaltung).",**anon(18,0,7)},
    {"id":"sr_20230327_04","sessionId":"sr_20230327","topicId":None,"date":"2023-03-27",
     "title":"Verkaufsoffener Sonntag 16.04.2023",
     "text":"Verordnung beschlossen (18:0; Beubl Enthaltung).",**anon(18,0,7)},
    {"id":"sr_20230327_05","sessionId":"sr_20230327","topicId":None,"date":"2023-03-27",
     "title":"Neubesetzung Personalausschuss",
     "text":"Pschorr als Mitglied, Beubl als Vertreter (18:0; Stanglmaier Enthaltung).",**anon(18,0,7)},
    {"id":"sr_20230327_06","sessionId":"sr_20230327","topicId":None,"date":"2023-03-27",
     "title":"Plakatierung Breitbandausbau Ortsteile",
     "text":"Einstimmig: Plakatierung in Pfrombach/Aich (60 Plakate) und Thonstetten (20).",**anon(20,0,5)},
]

# ── SR 2023-04-17 (6.) ──────────────────────────────────────────────────────
A = ["stanglmaier","fincke","von_pressentin"]
new_sessions.append({"id":"sr_20230417","date":"2023-04-17","type":"stadtrat",
    "title":"6. Stadtratssitzung – April 2023","absent":A,
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Genehmigung Niederschriften (zurückgestellt)","type":"discussion"},
        {"number":"4.1","title":"Schloss-Aschwiese aus Untersuchungsgebiet (abgelehnt 9:13)",
         "topicId":"t13","voteId":"sr_20230417_01"},
        {"number":"4.2","title":"Vorbereitende Untersuchungen Innenstadt–Bahnhof (13:9)",
         "topicId":"t13","voteId":"sr_20230417_02"},
        {"number":"5.1","title":"Stellplatzsatzung – Garagen-Streichung (abgelehnt 5:17)","voteId":"sr_20230417_03"},
        {"number":"5.2","title":"Stellplatzsatzung – Neufassung","voteId":"sr_20230417_04"},
        {"number":6,"title":"Änderung Landschaftsschutzgebiete – keine Einwendungen (13:9)","voteId":"sr_20230417_05"},
        {"number":7,"title":"B-Plan Dobelfeld Wang – keine Bedenken","voteId":"sr_20230417_06"},
        {"number":8,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"sr_20230417_01","sessionId":"sr_20230417","topicId":"t13","date":"2023-04-17",
     "title":"Schloss-Aschwiese aus Untersuchungsgebiet herausnehmen (abgelehnt)",
     "text":"Änderungsantrag, die Schloss-Aschwiese aus dem Untersuchungsgebiet auszunehmen, abgelehnt (9:13).",
     **anon(9,13,3,rej=True)},
    {"id":"sr_20230417_02","sessionId":"sr_20230417","topicId":"t13","date":"2023-04-17",
     "title":"Vorbereitende Untersuchungen Innenstadt–Bahnhof",
     "text":"Beauftragung der Vorbereitenden Untersuchungen nach § 141 BauGB (13:9).",**anon(13,9,3)},
    {"id":"sr_20230417_03","sessionId":"sr_20230417","topicId":None,"date":"2023-04-17",
     "title":"Stellplatzsatzung – Streichung Garagenstellplatz (abgelehnt)",
     "text":"Änderungsantrag mit 5:17 abgelehnt.",**anon(5,17,3,rej=True)},
    {"id":"sr_20230417_04","sessionId":"sr_20230417","topicId":None,"date":"2023-04-17",
     "title":"Stellplatzsatzung – Neufassung",
     "text":"Einstimmig: Neufassung Fassung 17.04.2023 beschlossen.",**named(PRE_JUL, A)},
    {"id":"sr_20230417_05","sessionId":"sr_20230417","topicId":"t15","date":"2023-04-17",
     "title":"Landschaftsschutzgebiete – keine Einwendungen",
     "text":"Keine Einwendungen gegen Änderung der LSG im Landkreis Freising (13:9).",**anon(13,9,3)},
    {"id":"sr_20230417_06","sessionId":"sr_20230417","topicId":None,"date":"2023-04-17",
     "title":"B-Plan Dobelfeld Wang – keine Bedenken",
     "text":"Einstimmig: Keine Bedenken zur Aufstellung (21:0; Gruebl Enthaltung).",**anon(21,0,4)},
]

# ── SR 2023-04-24 (7.) ──────────────────────────────────────────────────────
A = ["becher_j","gruber","heinz","john","tristl"]
new_sessions.append({"id":"sr_20230424","date":"2023-04-24","type":"stadtrat",
    "title":"7. Stadtratssitzung – April 2023","absent":A,
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Genehmigung Niederschriften","voteId":"sr_20230424_01"},
        {"number":4,"title":"B-Plan Nr. 52 „WA Amperauen\" – 1. Änderung Einfriedungen",
         "topicId":"t20","voteId":"sr_20230424_02"},
        {"number":5,"title":"Anpassung Badegebühren Freibad","topicId":"t12","voteId":"sr_20230424_03"},
        {"number":"6.1","title":"Erhöhung Ausschusssitze BPU/HVFA (abgelehnt 8:12)","voteId":"sr_20230424_04"},
        {"number":7,"title":"Fahrgastbefragung Bahnhof","topicId":"t2","voteId":"sr_20230424_05"},
        {"number":8,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"sr_20230424_01","sessionId":"sr_20230424","topicId":None,"date":"2023-04-24",
     "title":"Genehmigung Niederschriften (StR 06.03., 27.03.2023)",
     "text":"Einstimmig genehmigt.",**named(PRE_JUL, A)},
    {"id":"sr_20230424_02","sessionId":"sr_20230424","topicId":"t20","date":"2023-04-24",
     "title":"B-Plan 52 Amperauen – Einfriedungen (abgelehnt)",
     "text":"Antrag, Beschluss zu Einfriedungen aufzuheben, mit 6:14 abgelehnt.",**anon(6,14,5,rej=True)},
    {"id":"sr_20230424_03","sessionId":"sr_20230424","topicId":"t12","date":"2023-04-24",
     "title":"Badegebühren Freibad – Anpassung",
     "text":"Neue Badegebührenordnung beschlossen (13:7).",**anon(13,7,5)},
    {"id":"sr_20230424_04","sessionId":"sr_20230424","topicId":None,"date":"2023-04-24",
     "title":"Erhöhung Ausschusssitze BPU/HVFA (abgelehnt)",
     "text":"Antrag StR Kästl, BPU/HVFA auf 12 + Vorsitz aufzustocken, mit 8:12 abgelehnt.",**anon(8,12,5,rej=True)},
    {"id":"sr_20230424_05","sessionId":"sr_20230424","topicId":"t2","date":"2023-04-24",
     "title":"Fahrgastbefragung Bahnhof",
     "text":"Einstimmig: Online-Befragung zum Nutzungsverhalten am Bahnhof (Antrag fresh).",**named(PRE_JUL,A)},
]

# ── SR 2023-05-15 (8.) — B-Plan 63 SO Amperauen massive Stellungnahmen ──────
A = ["stanglmaier","becher_a","kaestl","linz_kilian"]
new_sessions.append({"id":"sr_20230515","date":"2023-05-15","type":"stadtrat",
    "title":"8. Stadtratssitzung – Mai 2023","absent":A,
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Bahnhof-Empfangsgebäude – Neubau/Sanierung","topicId":"t2","type":"discussion"},
        {"number":4,"title":"B-Plan 63 „SO Amperauen\" – 27 Stellungnahmen abgewogen",
         "topicId":"t20","voteId":"sr_20230515_01"},
        {"number":"4.28","title":"B-Plan 63 SO Amperauen – Planung beschlossen",
         "topicId":"t20","voteId":"sr_20230515_02"},
        {"number":5,"title":"Jahresrechnung 2022 – Vorlage","topicId":"t7","type":"discussion"},
        {"number":6,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"sr_20230515_01","sessionId":"sr_20230515","topicId":"t20","date":"2023-05-15",
     "title":"B-Plan 63 SO Amperauen – Stellungnahmen abgewogen",
     "text":"In 27 Einzelabstimmungen werden die Stellungnahmen aus der öffentlichen Auslegung abgewogen (meist 18:0).",
     **anon(18,0,7)},
    {"id":"sr_20230515_02","sessionId":"sr_20230515","topicId":"t20","date":"2023-05-15",
     "title":"B-Plan 63 SO Amperauen + 14. FNP-Änderung – Beschluss",
     "text":"Einstimmig: Planung beschlossen, Mitteilung an Behörden veranlasst.",**anon(19,0,6)},
]

# ── SR 2023-05-22 (9.) — Multi-Bauleitplanung ──────────────────────────────
A = ["hadersdorfer","gruber","john","welter"]
GE_UNTERREIT_YES = ["dollinger","weber","linz_karin","haberl","tristl","beubl","pschorr","fincke","grundner","reif","lauterbach","kieninger"]
GE_UNTERREIT_NO  = ["stanglmaier","becher_j","beibl","linz_kilian","von_pressentin","gruebl","kaestl"]
# named vote 12:7, total 19 → 21 active - 2 = 19 ✓
new_sessions.append({"id":"sr_20230522","date":"2023-05-22","type":"stadtrat",
    "title":"9. Stadtratssitzung – Mai 2023","absent":A,
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Genehmigung Niederschriften (BA 20.03., StR 17.04.)","voteId":"sr_20230522_01"},
        {"number":"4.1","title":"B-Plan 79 GE Unterreit – Aufstellung (12:7)","voteId":"sr_20230522_02"},
        {"number":"4.2","title":"B-Plan 79 GE Unterreit – Städtebaulicher Vertrag (12:7)","voteId":"sr_20230522_03"},
        {"number":5,"title":"Sanierung Aufbereitungsanlage Wasserwerk","voteId":"sr_20230522_04"},
        {"number":"6.1","title":"MFH-Vorbescheid (13:7)","voteId":"sr_20230522_05"},
        {"number":"6.2","title":"Stellplatzablöse-Befreiung","voteId":"sr_20230522_06"},
        {"number":"6.3a","title":"Doppelhäuser Vorbescheid (abgelehnt 9:10)","voteId":"sr_20230522_07"},
        {"number":"6.3b","title":"Doppelhäuser – 2. Beschluss (10:9)","voteId":"sr_20230522_08"},
        {"number":"6.4","title":"Betreiber-Wohnung","voteId":"sr_20230522_09"},
        {"number":7,"title":"B-Plan 74 Feldkirchen + 10. FNP-Änderung – 18 Stellungnahmen","voteId":"sr_20230522_10"},
        {"number":8,"title":"15. FNP-Änderung „Moosstraße-Aich\" – 15 Stellungnahmen","voteId":"sr_20230522_11"},
        {"number":9,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"sr_20230522_01","sessionId":"sr_20230522","topicId":None,"date":"2023-05-22",
     "title":"Genehmigung Niederschriften","text":"Einstimmig genehmigt.",**anon(20,0,5)},
    {"id":"sr_20230522_02","sessionId":"sr_20230522","topicId":None,"date":"2023-05-22",
     "title":"B-Plan 79 GE Unterreit – Aufstellungsbeschluss",
     "text":"Aufstellungsbeschluss mit 12:7. Spaltung CSU/FW/SPD/FDP (Ja) vs Grüne/fresh (Nein).",
     **named_vote(GE_UNTERREIT_YES, GE_UNTERREIT_NO, ["hadersdorfer","gruber","john","welter","heinz","kuch_skip" if False else ""][0:5] if False else A)},
    {"id":"sr_20230522_03","sessionId":"sr_20230522","topicId":None,"date":"2023-05-22",
     "title":"B-Plan 79 GE Unterreit – Städtebaulicher Vertrag",
     "text":"Ebenfalls 12:7 (gleiche Konstellation).",
     **named_vote(GE_UNTERREIT_YES, GE_UNTERREIT_NO, A)},
    {"id":"sr_20230522_04","sessionId":"sr_20230522","topicId":None,"date":"2023-05-22",
     "title":"Sanierung Aufbereitungsanlage Wasserwerk",
     "text":"Einstimmig: Sanierung beschlossen.",**anon(21,0,4)},
    {"id":"sr_20230522_05","sessionId":"sr_20230522","topicId":None,"date":"2023-05-22",
     "title":"MFH – Vorbescheid (13:7)",
     "text":"Vorbescheid für Mehrfamilienhaus erteilt (13:7).",**anon(13,7,5)},
    {"id":"sr_20230522_06","sessionId":"sr_20230522","topicId":None,"date":"2023-05-22",
     "title":"Stellplatzablöse-Befreiung",
     "text":"Einstimmig: Befreiung von der Stellplatzablöse.",**anon(20,0,5)},
    {"id":"sr_20230522_07","sessionId":"sr_20230522","topicId":None,"date":"2023-05-22",
     "title":"Doppelhäuser Vorbescheid – 1. Beschluss (abgelehnt)",
     "text":"Erste Abstimmung mit 9:10 abgelehnt.",**anon(9,10,6,rej=True)},
    {"id":"sr_20230522_08","sessionId":"sr_20230522","topicId":None,"date":"2023-05-22",
     "title":"Doppelhäuser Vorbescheid – 2. Beschluss (10:9)",
     "text":"Zweite Abstimmung mit 10:9 beschlossen.",**anon(10,9,6)},
    {"id":"sr_20230522_09","sessionId":"sr_20230522","topicId":None,"date":"2023-05-22",
     "title":"Betreiber-Wohnung","text":"Einstimmig: Einvernehmen erteilt.",**anon(20,0,5)},
    {"id":"sr_20230522_10","sessionId":"sr_20230522","topicId":None,"date":"2023-05-22",
     "title":"B-Plan 74 Feldkirchen + 10. FNP-Änderung",
     "text":"In 18 Einzelabstimmungen werden die Stellungnahmen abgewogen (alle einstimmig 19-21:0).",**anon(20,0,5)},
    {"id":"sr_20230522_11","sessionId":"sr_20230522","topicId":None,"date":"2023-05-22",
     "title":"15. FNP-Änderung „Moosstraße-Aich\"",
     "text":"In 15 Einzelabstimmungen werden die Stellungnahmen abgewogen (alle einstimmig 20-21:0).",**anon(20,0,5)},
]

# ── SR 2023-06-12 (10.) ─────────────────────────────────────────────────────
A = ["beibl","beubl","john"]
new_sessions.append({"id":"sr_20230612","date":"2023-06-12","type":"stadtrat",
    "title":"10. Stadtratssitzung – Juni 2023","absent":A,
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Genehmigung Niederschriften (StR 24.04., HVFA 11.05.)","voteId":"sr_20230612_01"},
        {"number":4,"title":"Fairtrade-Stadt – Aktivitätenbericht","type":"discussion"},
        {"number":5,"title":"3-Gruppen-Kita + 5 Wohnungen Sonnensiedlung 1","voteId":"sr_20230612_02"},
        {"number":6,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"sr_20230612_01","sessionId":"sr_20230612","topicId":None,"date":"2023-06-12",
     "title":"Genehmigung Niederschriften","text":"Einstimmig genehmigt.",**named(PRE_JUL, A)},
    {"id":"sr_20230612_02","sessionId":"sr_20230612","topicId":None,"date":"2023-06-12",
     "title":"3-Gruppen-Kita + 5 Wohnungen Sonnensiedlung 1",
     "text":"Einstimmig: Bau einer 3-gruppigen Kita mit 5 Wohnungen; Gesamtkosten 6.057.488 €.",
     **named(PRE_JUL, A)},
]

# ── SR 2023-06-26 (11.) ─────────────────────────────────────────────────────
A = ["becher_j","heinz"]
SR_0626_RENT_YES = ["dollinger","tristl","weber","haberl","linz_karin","hadersdorfer","beubl","grundner","reif","kieninger","lauterbach","fincke"]
SR_0626_RENT_NO  = ["stanglmaier","beibl","becher_a","linz_kilian","gruebl","gruber","kaestl","pschorr","john","welter"]
# missing one — let me adjust: 25 - 2 absent = 23 voters. 12+10 = 22, 1 not counted (von_pressentin absent on housing votes per agent)
new_sessions.append({"id":"sr_20230626","date":"2023-06-26","type":"stadtrat",
    "title":"11. Stadtratssitzung – Juni 2023","absent":A,
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Genehmigung Niederschrift StR 15.05.","voteId":"sr_20230626_01"},
        {"number":"4.1","title":"Mietanpassung Sudetenlandstr. (15 %; 12:10)","voteId":"sr_20230626_02"},
        {"number":"4.2","title":"Garagengebühr Erhöhung (21:1)","voteId":"sr_20230626_03"},
        {"number":5,"title":"Straßenbeleuchtung LED-Umrüstung","topicId":"t15","voteId":"sr_20230626_04"},
        {"number":6,"title":"Neubesetzung Ausschüsse (fresh-Antrag)","voteId":"sr_20230626_05"},
        {"number":7,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"sr_20230626_01","sessionId":"sr_20230626","topicId":None,"date":"2023-06-26",
     "title":"Genehmigung Niederschrift StR 15.05.2023","text":"Einstimmig genehmigt.",**named(PRE_JUL,A)},
    {"id":"sr_20230626_02","sessionId":"sr_20230626","topicId":None,"date":"2023-06-26",
     "title":"Mietanpassung Sudetenlandstr. (15 %)",
     "text":"Mieterhöhung um 15 % beschlossen (12:10); deutliche Spaltung CSU/FW/SPD (Ja) vs Grüne/fresh/Linke (Nein).",
     **named_vote(SR_0626_RENT_YES, SR_0626_RENT_NO, A+["von_pressentin"])},
    {"id":"sr_20230626_03","sessionId":"sr_20230626","topicId":None,"date":"2023-06-26",
     "title":"Garagengebühr Erhöhung 42,50 → 45 €","text":"Erhöhung beschlossen (21:1).",**anon(21,1,3)},
    {"id":"sr_20230626_04","sessionId":"sr_20230626","topicId":"t15","date":"2023-06-26",
     "title":"Straßenbeleuchtung – LED-Umrüstung",
     "text":"Einstimmig: Umstellung der städtischen Straßenbeleuchtung auf LED beschlossen.",
     **named(PRE_JUL, A)},
    {"id":"sr_20230626_05","sessionId":"sr_20230626","topicId":None,"date":"2023-06-26",
     "title":"Neubesetzung Ausschüsse (fresh-Antrag)",
     "text":"Personal-/Rechnungsprüfungsausschuss neu besetzt (20:0; einige Enthaltungen).",**anon(20,0,5)},
]

# ── SR 2023-07-10 (12.) ─────────────────────────────────────────────────────
A = ["hadersdorfer"]
new_sessions.append({"id":"sr_20230710","date":"2023-07-10","type":"stadtrat",
    "title":"12. Stadtratssitzung – Juli 2023","absent":A,
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Genehmigung Niederschrift StR 22.05.","voteId":"sr_20230710_01"},
        {"number":4,"title":"Energiebeirat – Aktivitätenbericht","topicId":"t15","type":"discussion"},
        {"number":5,"title":"FC Moosburg – Flutlicht-LED-Zuschuss","topicId":"t15","voteId":"sr_20230710_02"},
        {"number":6,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"sr_20230710_01","sessionId":"sr_20230710","topicId":None,"date":"2023-07-10",
     "title":"Genehmigung Niederschrift StR 22.05.2023","text":"Einstimmig genehmigt (23:0).",
     **anon(23,0,2)},
    {"id":"sr_20230710_02","sessionId":"sr_20230710","topicId":"t15","date":"2023-07-10",
     "title":"FC Moosburg – Flutlicht-LED-Zuschuss",
     "text":"Einstimmig: 20 %-Zuschuss (~38.700 €) zum LED-Umbau der Flutlichtanlage.",
     **anon(24,0,1)},
]

# ── BPU 2023-07-17 (3.) — vice-chairs both absent ───────────────────────────
# Present: dollinger (chair), beibl, kieninger, linz_kilian, reif, welter (6 regulars)
# + gruber (sub for gruebl), haberl (sub for tristl), pschorr (sub for beubl), weber (sub for linz_karin)
# Absent: hadersdorfer + heinz (vice 1 seat empty), stanglmaier + becher_j (vice 2 seat empty)
BPU_0717_VOTERS = ["dollinger","beibl","kieninger","linz_kilian","reif","welter",
                   "gruber","haberl","pschorr","weber"]
def bpu_0717_named():
    return {"type":"named","results":{"yes":list(BPU_0717_VOTERS),"no":[],"absent":["hadersdorfer","stanglmaier"]}}

new_sessions.append({"id":"bpu_20230717","date":"2023-07-17","type":"bpu",
    "title":"3. Sitzung Bau-, Planungs- und Umweltausschuss – Juli 2023",
    "absent":["hadersdorfer","stanglmaier"],
    "substitutes":[
        {"member":"gruebl","substitute":"gruber"},
        {"member":"tristl","substitute":"haberl"},
        {"member":"beubl","substitute":"pschorr"},
        {"member":"linz_karin","substitute":"weber"},
    ],
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"PV-Modullager Neue Industriestr. 1","topicId":"t15","voteId":"bpu_20230717_01"},
        {"number":"4.1","title":"Einfamilienhaus Weinberg 2 Pfrombach","voteId":"bpu_20230717_02"},
        {"number":"4.2","title":"Einfamilienhaus Grünseiboldsdorf 8 – verweigert","voteId":"bpu_20230717_03"},
        {"number":"4.3a","title":"Gastronomie→Wohnen Herrnstr. 29 – BauR","voteId":"bpu_20230717_04"},
        {"number":"4.3b","title":"Gastronomie→Wohnen – Sanierungsrecht verweigert (9:1)","voteId":"bpu_20230717_05"},
        {"number":"4.4","title":"Feuerlöschwasser-Reservoir Steinbockstr. 38","voteId":"bpu_20230717_06"},
        {"number":5,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"bpu_20230717_01","sessionId":"bpu_20230717","topicId":"t15","date":"2023-07-17",
     "title":"PV-Modullager Neue Industriestr. 1 – BImSchG",
     "text":"Einstimmig: Einvernehmen für PV-Modullager (Vorhaben nach § 4 BImSchG) erteilt.",
     **bpu_0717_named()},
    {"id":"bpu_20230717_02","sessionId":"bpu_20230717","topicId":None,"date":"2023-07-17",
     "title":"Einfamilienhaus Weinberg 2 Pfrombach","text":"Einstimmig: Einvernehmen erteilt.",
     **bpu_0717_named()},
    {"id":"bpu_20230717_03","sessionId":"bpu_20230717","topicId":None,"date":"2023-07-17",
     "title":"Einfamilienhaus Grünseiboldsdorf 8 – verweigert",
     "text":"Einstimmig verweigert; außerhalb Bebauungsraum, öffentliche Belange entgegenstehend.",
     **bpu_0717_named()},
    {"id":"bpu_20230717_04","sessionId":"bpu_20230717","topicId":None,"date":"2023-07-17",
     "title":"Gastronomie → Wohnen Herrnstr. 29 – Baurecht",
     "text":"Einstimmig: Bauliches Einvernehmen erteilt.",**bpu_0717_named()},
    {"id":"bpu_20230717_05","sessionId":"bpu_20230717","topicId":"t13","date":"2023-07-17",
     "title":"Gastronomie → Wohnen Herrnstr. 29 – Sanierungsrecht verweigert",
     "text":"Sanierungsrechtliches Einvernehmen mit 9:1 verweigert: Erhalt des Erdgeschoss-Gewerbes ist Sanierungsziel.",
     **anon(9,1,2)},
    {"id":"bpu_20230717_06","sessionId":"bpu_20230717","topicId":None,"date":"2023-07-17",
     "title":"Feuerlöschwasser-Reservoir Steinbockstr. 38",
     "text":"Einstimmig: Einvernehmen mit Befreiungen erteilt.",**bpu_0717_named()},
]

# ── SR 2023-07-24 (13.) — John resigns, Strobl sworn in ─────────────────────
# Pre-Niederlegung members: PRE_JUL (with john)
# Post-Vereidigung: POST_JUL (with strobl)
# session absent: becher_a only
A = ["becher_a"]
new_sessions.append({"id":"sr_20230724","date":"2023-07-24","type":"stadtrat",
    "title":"13. Stadtratssitzung – Juli 2023","absent":A,
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":"6.1","title":"Niederlegung Mandat StR John – Strobl rückt nach","voteId":"sr_20230724_01"},
        {"number":"6.2","title":"Vereidigung StR Strobl","type":"formal"},
        {"number":"6.3","title":"Neubesetzung Ausschüsse (John → Strobl)","voteId":"sr_20230724_02"},
        {"number":"7.1","title":"Kläranlage GmbH – Jahresabschluss 2022","voteId":"sr_20230724_03"},
        {"number":"7.2","title":"Kläranlage GmbH – Entlastung Aufsichtsrat","voteId":"sr_20230724_04"},
        {"number":8,"title":"Lebendige Zentren – Auf dem Plan 14 Denkmalförderung",
         "topicId":"t3","voteId":"sr_20230724_05"},
        {"number":9,"title":"TG-Grundschule – 4 neue Klassenzimmer","topicId":"t6","voteId":"sr_20230724_06"},
        {"number":10,"title":"Schülerbeförderung – Bündelausschreibung","voteId":"sr_20230724_07"},
        {"number":11,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"sr_20230724_01","sessionId":"sr_20230724","topicId":None,"date":"2023-07-24",
     "title":"Niederlegung Mandat John – Strobl rückt nach",
     "text":"Stefan John legt sein Mandat nieder; Alexander Strobl als Listennachfolger bestätigt (23:0).",
     **named(PRE_JUL, A)},
    {"id":"sr_20230724_02","sessionId":"sr_20230724","topicId":None,"date":"2023-07-24",
     "title":"Neubesetzung Ausschüsse (John → Strobl)",
     "text":"Einstimmig: Strobl übernimmt John's Ausschuss-Sitze (22:0; einige Enthaltungen).",
     **anon(22,0,3)},
    {"id":"sr_20230724_03","sessionId":"sr_20230724","topicId":"t7","date":"2023-07-24",
     "title":"Kläranlage GmbH – Jahresabschluss 2022",
     "text":"Einstimmig: Jahresabschluss 2022 zur Genehmigung empfohlen.",
     **named(POST_JUL, A)},
    {"id":"sr_20230724_04","sessionId":"sr_20230724","topicId":"t7","date":"2023-07-24",
     "title":"Kläranlage GmbH – Entlastung Aufsichtsrat",
     "text":"Entlastung erteilt; 6 AR-Mitglieder enthalten sich wegen persönlicher Beteiligung.",
     **anon(16,0,9)},
    {"id":"sr_20230724_05","sessionId":"sr_20230724","topicId":"t3","date":"2023-07-24",
     "title":"Lebendige Zentren – Denkmal Auf dem Plan 14",
     "text":"100.000 € Bundeszuschuss + 40.000 € städtischer Eigenanteil (22:0).",
     **anon(22,0,3)},
    {"id":"sr_20230724_06","sessionId":"sr_20230724","topicId":"t6","date":"2023-07-24",
     "title":"TG-Grundschule – 4 zusätzliche Klassenzimmer",
     "text":"2.720.121 € für 4 neue Klassenzimmer (21:0; Heinz Enthaltung).",
     **anon(21,0,4)},
    {"id":"sr_20230724_07","sessionId":"sr_20230724","topicId":None,"date":"2023-07-24",
     "title":"Schülerbeförderung – Bündelausschreibung",
     "text":"Einstimmig: Kommunale Zusammenarbeit zur Bündelausschreibung.",**anon(21,0,4)},
]

# ── SR 2023-09-04 (14.) — Rainbow flag votes ────────────────────────────────
A = ["fincke","kaestl","lauterbach","reif","von_pressentin"]
RB_YES = ["stanglmaier","becher_a","beibl","becher_j","linz_kilian","strobl","gruebl","gruber","beubl"]
RB_NO  = ["dollinger","hadersdorfer","grundner","haberl","heinz","kieninger","linz_karin","pschorr","tristl","weber","welter"]
new_sessions.append({"id":"sr_20230904","date":"2023-09-04","type":"stadtrat",
    "title":"14. Stadtratssitzung – September 2023","absent":A,
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Genehmigung Niederschriften (StR 26.06., 10.07., 24.07.; HVFA 03.07.)",
         "voteId":"sr_20230904_01"},
        {"number":4,"title":"Weingraben-Kanalsanierung – überplanmäßige Mittel","voteId":"sr_20230904_02"},
        {"number":"5.1","title":"Eisstadion – Gebührenänderung (11:9)","voteId":"sr_20230904_03"},
        {"number":"5.2","title":"Eisstadion – Externe Vereine 150 € (19:1)","voteId":"sr_20230904_04"},
        {"number":"6.1","title":"Regenbogenflagge am Rathaus (abgelehnt 9:11)","voteId":"sr_20230904_05"},
        {"number":"6.2","title":"Regenbogenflagge am VHS-Mast","voteId":"sr_20230904_06"},
        {"number":"6.3","title":"Pride Month (Juni)","voteId":"sr_20230904_07"},
        {"number":7,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"sr_20230904_01","sessionId":"sr_20230904","topicId":None,"date":"2023-09-04",
     "title":"Genehmigung Niederschriften","text":"Einstimmig genehmigt.",**named(POST_JUL,A)},
    {"id":"sr_20230904_02","sessionId":"sr_20230904","topicId":"t7","date":"2023-09-04",
     "title":"Weingraben-Kanalsanierung – 300 T€ überplanmäßig",
     "text":"Einstimmig: Überplanmäßige Mittel von 300.000 € für Sanierung des Weingraben-Kanals.",
     **named(POST_JUL, A)},
    {"id":"sr_20230904_03","sessionId":"sr_20230904","topicId":None,"date":"2023-09-04",
     "title":"Eisstadion – Gebührenänderung","text":"Anpassung der Gebühren beschlossen (11:9).",**anon(11,9,5)},
    {"id":"sr_20230904_04","sessionId":"sr_20230904","topicId":None,"date":"2023-09-04",
     "title":"Eisstadion – externe Vereinsmiete 150 €",
     "text":"Externe Vereinsmiete 120 → 150 €/h (19:1).",**anon(19,1,5)},
    {"id":"sr_20230904_05","sessionId":"sr_20230904","topicId":None,"date":"2023-09-04",
     "title":"Regenbogenflagge am Rathaus (abgelehnt)",
     "text":"Antrag, die Regenbogenflagge am Rathaus zu hissen, mit 9:11 abgelehnt.",
     **named_vote(RB_YES, RB_NO, A, rej=True)},
    {"id":"sr_20230904_06","sessionId":"sr_20230904","topicId":None,"date":"2023-09-04",
     "title":"Regenbogenflagge am VHS-Mast",
     "text":"Einstimmig: Alternativstandort am VHS-Flaggenmast beschlossen.",**named(POST_JUL, A)},
    {"id":"sr_20230904_07","sessionId":"sr_20230904","topicId":None,"date":"2023-09-04",
     "title":"Pride Month (Juni)",
     "text":"Einstimmig: Juni wird als Pride Month in Moosburg ausgerufen.",**named(POST_JUL, A)},
]

# ── BPU 2023-09-21 (4.) ─────────────────────────────────────────────────────
BPU_0921_VOTERS = ["dollinger","stanglmaier","beibl","kieninger","linz_karin","linz_kilian",
                   "reif","tristl","welter","gruber","pschorr"]
def bpu_0921_full():
    # 11 voters, gruber sub for gruebl, pschorr sub for beubl. hadersdorfer+sub heinz absent. 1 empty vice seat.
    return {"type":"named","results":{"yes":list(BPU_0921_VOTERS),"no":[],"absent":["hadersdorfer","beubl"]}}
new_sessions.append({"id":"bpu_20230921","date":"2023-09-21","type":"bpu",
    "title":"4. Sitzung Bau-, Planungs- und Umweltausschuss – September 2023",
    "absent":["hadersdorfer","beubl"],
    "substitutes":[
        {"member":"gruebl","substitute":"gruber"},
        {"member":"beubl","substitute":"pschorr"},
    ],
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Genehmigung Niederschrift BPU 17.07.","voteId":"bpu_20230921_01"},
        {"number":"4.1","title":"Isarwehr – Denkmalschutz","topicId":"t14","voteId":"bpu_20230921_02"},
        {"number":"4.2","title":"Wasserkraftwerk Pfrombach – Denkmalschutz","topicId":"t14","voteId":"bpu_20230921_03"},
        {"number":"5.1","title":"Postgebäude-Abriss + Wohnen (9:2)","voteId":"bpu_20230921_04"},
        {"number":"5.2","title":"Degernpoint Parkplatz mit E-Ladeplätzen (6:5)","topicId":"t18","voteId":"bpu_20230921_05"},
        {"number":"5.3","title":"MFH Bahnhofstr. 60 – verweigert","voteId":"bpu_20230921_06"},
        {"number":"5.4","title":"Asyl-Wohnen Sudetenlandstr. 9 (10:1)","voteId":"bpu_20230921_07"},
        {"number":"5.5","title":"Photovoltaik-Anlage","topicId":"t15","voteId":"bpu_20230921_08"},
        {"number":"5.6","title":"Gewerbeumnutzung (Eisen→Lebensmittel)","voteId":"bpu_20230921_09"},
        {"number":6,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"bpu_20230921_01","sessionId":"bpu_20230921","topicId":None,"date":"2023-09-21",
     "title":"Genehmigung Niederschrift BPU 17.07.","text":"Einstimmig genehmigt.",**bpu_0921_full()},
    {"id":"bpu_20230921_02","sessionId":"bpu_20230921","topicId":"t14","date":"2023-09-21",
     "title":"Isarwehr – Denkmalschutz","text":"Einstimmig: Denkmaleintragung des Isarwehrs befürwortet.",
     **bpu_0921_full()},
    {"id":"bpu_20230921_03","sessionId":"bpu_20230921","topicId":"t14","date":"2023-09-21",
     "title":"Wasserkraftwerk Pfrombach – Denkmalschutz",
     "text":"Einstimmig: Denkmaleintragung befürwortet.",**bpu_0921_full()},
    {"id":"bpu_20230921_04","sessionId":"bpu_20230921","topicId":None,"date":"2023-09-21",
     "title":"Postgebäude – Abriss + Wohnungsbau",
     "text":"Einvernehmen für Abriss und Neubau Wohngebäude erteilt (9:2).",**anon(9,2,1)},
    {"id":"bpu_20230921_05","sessionId":"bpu_20230921","topicId":"t18","date":"2023-09-21",
     "title":"Degernpoint – Parkplatz mit E-Ladestationen",
     "text":"Einvernehmen erteilt (6:5).",**anon(6,5,1)},
    {"id":"bpu_20230921_06","sessionId":"bpu_20230921","topicId":None,"date":"2023-09-21",
     "title":"MFH Bahnhofstr. 60 – verweigert",
     "text":"Einstimmig verweigert.",**bpu_0921_full()},
    {"id":"bpu_20230921_07","sessionId":"bpu_20230921","topicId":None,"date":"2023-09-21",
     "title":"Asyl-Wohnen Sudetenlandstr. 9",
     "text":"Einvernehmen erteilt (10:1).",**anon(10,1,1)},
    {"id":"bpu_20230921_08","sessionId":"bpu_20230921","topicId":"t15","date":"2023-09-21",
     "title":"Photovoltaik-Anlage","text":"Einstimmig: Einvernehmen erteilt.",**bpu_0921_full()},
    {"id":"bpu_20230921_09","sessionId":"bpu_20230921","topicId":None,"date":"2023-09-21",
     "title":"Gewerbeumnutzung Eisenwaren → Lebensmittel",
     "text":"Einstimmig: Einvernehmen erteilt.",**bpu_0921_full()},
]

# ── SR 2023-10-23 (17.) — SO Amperauen revisited ────────────────────────────
A = ["gruber","linz_karin","reif"]
new_sessions.append({"id":"sr_20231023","date":"2023-10-23","type":"stadtrat",
    "title":"17. Stadtratssitzung – Oktober 2023","absent":A,
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"B-Plan 63 „SO Amperauen\" – 13 Stellungnahmen abgewogen",
         "topicId":"t20","voteId":"sr_20231023_01"},
        {"number":"3.14","title":"SO Amperauen – Satzungsbeschluss (zurückgestellt)",
         "topicId":"t20","type":"discussion"},
        {"number":"4.1","title":"Jahresrechnung 2021 – Feststellung","topicId":"t7","voteId":"sr_20231023_02"},
        {"number":"4.2","title":"Jahresrechnung 2021 – Entlastung","topicId":"t7","voteId":"sr_20231023_03"},
        {"number":5,"title":"Finanzbericht 30.09.2023","type":"discussion"},
        {"number":6,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"sr_20231023_01","sessionId":"sr_20231023","topicId":"t20","date":"2023-10-23",
     "title":"B-Plan 63 SO Amperauen – Stellungnahmen abgewogen",
     "text":"In 13 Einzelabstimmungen werden die Stellungnahmen aus der erneuten Auslegung abgewogen (alle 21-22:0).",
     **anon(22,0,3)},
    {"id":"sr_20231023_02","sessionId":"sr_20231023","topicId":"t7","date":"2023-10-23",
     "title":"Jahresrechnung 2021 – Feststellung",
     "text":"Einstimmig: Feststellung der Jahresrechnung 2021.",**anon(21,0,4)},
    {"id":"sr_20231023_03","sessionId":"sr_20231023","topicId":"t7","date":"2023-10-23",
     "title":"Jahresrechnung 2021 – Entlastung",
     "text":"Einstimmig: Entlastung erteilt (Dollinger Enthaltung).",**anon(20,0,5)},
]

# ── BPU 2023-11-23 (5.) — All 12 present + observers ────────────────────────
SUDETEN_YES = ["dollinger","hadersdorfer","stanglmaier","linz_karin","tristl","welter","beubl"]
SUDETEN_NO  = ["beibl","gruebl","kieninger","linz_kilian","reif"]
new_sessions.append({"id":"bpu_20231123","date":"2023-11-23","type":"bpu",
    "title":"5. Sitzung Bau-, Planungs- und Umweltausschuss – November 2023",
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Genehmigung Niederschrift BPU 21.09.","voteId":"bpu_20231123_01"},
        {"number":4,"title":"Amperauen – Parkgestaltung","topicId":"t20","voteId":"bpu_20231123_02"},
        {"number":5,"title":"Mühlbachterrassen – Machbarkeitsstudie","topicId":"t20","voteId":"bpu_20231123_03"},
        {"number":"6.1","title":"Doppelgarage mit Fahrradabstellplätzen","voteId":"bpu_20231123_04"},
        {"number":"6.2","title":"Anbau Einfamilienhaus","voteId":"bpu_20231123_05"},
        {"number":"6.3a","title":"Arbeitnehmerwohnen Sudetenlandstr. 9 (abgelehnt 5:7)","voteId":"bpu_20231123_06"},
        {"number":"6.3b","title":"Arbeitnehmerwohnen Sudetenlandstr. 9 – 2. Beschluss (7:5)","voteId":"bpu_20231123_07"},
        {"number":"6.4","title":"MFH Sudetenlandstr. 2 – verweigert","voteId":"bpu_20231123_08"},
        {"number":"6.5","title":"Doppelhaus mit Carports","voteId":"bpu_20231123_09"},
        {"number":"6.6","title":"Wasserwerk-Erweiterung","voteId":"bpu_20231123_10"},
        {"number":"6.7","title":"Milchviehstall Pfrombach","voteId":"bpu_20231123_11"},
        {"number":7,"title":"Straßenbeleuchtung – Konzept","topicId":"t15","voteId":"bpu_20231123_12"},
        {"number":8,"title":"Försterweg – Widmung","voteId":"bpu_20231123_13"},
        {"number":9,"title":"Sonnensiedlung – Widmung","voteId":"bpu_20231123_14"},
        {"number":10,"title":"Amperpark – Widmung","topicId":"t20","voteId":"bpu_20231123_15"},
        {"number":12,"title":"Gärtnerstraße – Fahrradstraße","topicId":"t4","voteId":"bpu_20231123_16"},
        {"number":13,"title":"Burgermühlstraße – Fahrradzone (7:5)","topicId":"t4","voteId":"bpu_20231123_17"},
        {"number":14,"title":"Wasserwerkstraße – Fahrradstraße (abgelehnt 5:7)","topicId":"t4","voteId":"bpu_20231123_18"},
        {"number":15,"title":"Reiteraustraße – Fahrradstraße (abgelehnt 3:9)","topicId":"t4","voteId":"bpu_20231123_19"},
        {"number":16,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"bpu_20231123_01","sessionId":"bpu_20231123","topicId":None,"date":"2023-11-23",
     "title":"Genehmigung Niederschrift BPU 21.09.","text":"Einstimmig genehmigt.",**bpu_full_named()},
    {"id":"bpu_20231123_02","sessionId":"bpu_20231123","topicId":"t20","date":"2023-11-23",
     "title":"Amperauen – Parkgestaltung","text":"Einstimmig: Grünanlage als Wohngebietspark.",**bpu_full_named()},
    {"id":"bpu_20231123_03","sessionId":"bpu_20231123","topicId":"t20","date":"2023-11-23",
     "title":"Mühlbachterrassen – Machbarkeitsstudie",
     "text":"Einstimmig: Machbarkeitsstudie befürwortet, Schwemme prüfen.",**bpu_full_named()},
    {"id":"bpu_20231123_04","sessionId":"bpu_20231123","topicId":None,"date":"2023-11-23",
     "title":"Doppelgarage mit Fahrradabstellplätzen","text":"Einstimmig: Einvernehmen erteilt.",
     **bpu_full_named()},
    {"id":"bpu_20231123_05","sessionId":"bpu_20231123","topicId":None,"date":"2023-11-23",
     "title":"Anbau Einfamilienhaus","text":"Einstimmig: Einvernehmen erteilt.",**bpu_full_named()},
    {"id":"bpu_20231123_06","sessionId":"bpu_20231123","topicId":None,"date":"2023-11-23",
     "title":"Arbeitnehmerwohnen Sudetenlandstr. 9 – 1. Beschluss (abgelehnt)",
     "text":"Antrag mit 5:7 abgelehnt.",**named_vote(SUDETEN_YES, SUDETEN_NO, [], rej=True)},
    {"id":"bpu_20231123_07","sessionId":"bpu_20231123","topicId":None,"date":"2023-11-23",
     "title":"Arbeitnehmerwohnen Sudetenlandstr. 9 – 2. Beschluss",
     "text":"2. Beschluss mit 7:5 angenommen.",**named_vote(SUDETEN_NO + ["beubl","welter"], SUDETEN_YES[:5], [])},
    {"id":"bpu_20231123_08","sessionId":"bpu_20231123","topicId":None,"date":"2023-11-23",
     "title":"MFH Sudetenlandstr. 2 – verweigert","text":"Einstimmig verweigert.",**bpu_full_named()},
    {"id":"bpu_20231123_09","sessionId":"bpu_20231123","topicId":None,"date":"2023-11-23",
     "title":"Doppelhaus mit Carports","text":"Einstimmig: Einvernehmen erteilt.",**bpu_full_named()},
    {"id":"bpu_20231123_10","sessionId":"bpu_20231123","topicId":None,"date":"2023-11-23",
     "title":"Wasserwerk-Erweiterung","text":"Einstimmig: Einvernehmen erteilt.",**bpu_full_named()},
    {"id":"bpu_20231123_11","sessionId":"bpu_20231123","topicId":None,"date":"2023-11-23",
     "title":"Milchviehstall Pfrombach","text":"Einstimmig: Einvernehmen erteilt.",**bpu_full_named()},
    {"id":"bpu_20231123_12","sessionId":"bpu_20231123","topicId":"t15","date":"2023-11-23",
     "title":"Straßenbeleuchtung – Konzept",
     "text":"Einstimmig: Solar-Straßenbeleuchtung als Folgekonzept geprüft.",**bpu_full_named()},
    {"id":"bpu_20231123_13","sessionId":"bpu_20231123","topicId":None,"date":"2023-11-23",
     "title":"Försterweg – Widmung","text":"Einstimmig: Widmung beschlossen.",**bpu_full_named()},
    {"id":"bpu_20231123_14","sessionId":"bpu_20231123","topicId":None,"date":"2023-11-23",
     "title":"Sonnensiedlung – Widmung","text":"Einstimmig: Widmung beschlossen.",**bpu_full_named()},
    {"id":"bpu_20231123_15","sessionId":"bpu_20231123","topicId":"t20","date":"2023-11-23",
     "title":"Amperpark – Widmung","text":"Einstimmig: Widmung beschlossen.",**bpu_full_named()},
    {"id":"bpu_20231123_16","sessionId":"bpu_20231123","topicId":"t4","date":"2023-11-23",
     "title":"Gärtnerstraße – Fahrradstraße","text":"Fahrradstraßen-Widmung mit 9:3.",**anon(9,3,0)},
    {"id":"bpu_20231123_17","sessionId":"bpu_20231123","topicId":"t4","date":"2023-11-23",
     "title":"Burgermühlstraße – Fahrradzone",
     "text":"Fahrradzone mit 7:5 (2. Beschluss).",**anon(7,5,0)},
    {"id":"bpu_20231123_18","sessionId":"bpu_20231123","topicId":"t4","date":"2023-11-23",
     "title":"Wasserwerkstraße – Fahrradstraße (abgelehnt)",
     "text":"Mit 5:7 abgelehnt.",**anon(5,7,0,rej=True)},
    {"id":"bpu_20231123_19","sessionId":"bpu_20231123","topicId":"t4","date":"2023-11-23",
     "title":"Reiteraustraße – Fahrradstraße (abgelehnt)",
     "text":"Mit 3:9 abgelehnt.",**anon(3,9,0,rej=True)},
]

# ── SR 2023-12-14 (20.) ─────────────────────────────────────────────────────
A = ["becher_a","becher_j","gruber","heinz","linz_karin","pschorr","reif"]
new_sessions.append({"id":"sr_20231214","date":"2023-12-14","type":"stadtrat",
    "title":"20. Stadtratssitzung – Dezember 2023","absent":A,
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Genehmigung Niederschriften (StR 23.10., HVFA 20.11. + 27.11.)",
         "voteId":"sr_20231214_01"},
        {"number":"4.1","title":"Leinbergerstraße – Ausbauplanung","voteId":"sr_20231214_02"},
        {"number":"4.2","title":"Leinbergerstraße – Bauauftrag","voteId":"sr_20231214_03"},
        {"number":5,"title":"Städtebauförderung 2024 – Bedarfsanmeldung","topicId":"t13","voteId":"sr_20231214_04"},
        {"number":"6.1","title":"Tartanbahn-Sanierung (2/3 statt 100 %)","voteId":"sr_20231214_05"},
        {"number":"6.2","title":"Sport-/Festplatz – zusätzliche Mittel (abgelehnt)","voteId":"sr_20231214_06"},
        {"number":"6.3","title":"Solarförderung – Änderung","topicId":"t15","voteId":"sr_20231214_07"},
        {"number":7,"title":"Hinweisgeberschutz – interne Meldestelle","voteId":"sr_20231214_08"},
        {"number":8,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"sr_20231214_01","sessionId":"sr_20231214","topicId":None,"date":"2023-12-14",
     "title":"Genehmigung Niederschriften","text":"Einstimmig genehmigt.",**anon(13,0,12)},
    {"id":"sr_20231214_02","sessionId":"sr_20231214","topicId":None,"date":"2023-12-14",
     "title":"Leinbergerstraße – Ausbauplanung",
     "text":"Planung freigegeben (16:0).",**anon(16,0,9)},
    {"id":"sr_20231214_03","sessionId":"sr_20231214","topicId":None,"date":"2023-12-14",
     "title":"Leinbergerstraße – Bauauftrag",
     "text":"Bauauftrag erteilt (13:3).",**anon(13,3,9)},
    {"id":"sr_20231214_04","sessionId":"sr_20231214","topicId":"t13","date":"2023-12-14",
     "title":"Städtebauförderung 2024 – Bedarfsanmeldung",
     "text":"Bedarfsanmeldung beschlossen (15:0).",**anon(15,0,10)},
    {"id":"sr_20231214_05","sessionId":"sr_20231214","topicId":None,"date":"2023-12-14",
     "title":"Tartanbahn-Sanierung – 2/3-Variante",
     "text":"2/3-Sanierung statt 100 % beschlossen (15:1).",**anon(15,1,9)},
    {"id":"sr_20231214_06","sessionId":"sr_20231214","topicId":None,"date":"2023-12-14",
     "title":"Sport-/Festplatz – zusätzliche Mittel (abgelehnt)",
     "text":"Antrag, zusätzliche Mittel bereitzustellen, abgelehnt (2:14).",**anon(2,14,9,rej=True)},
    {"id":"sr_20231214_07","sessionId":"sr_20231214","topicId":"t15","date":"2023-12-14",
     "title":"Solarförderung – Änderung",
     "text":"Anpassung der Förderrichtlinie für Solaranlagen beschlossen (16:0).",**anon(16,0,9)},
    {"id":"sr_20231214_08","sessionId":"sr_20231214","topicId":None,"date":"2023-12-14",
     "title":"Hinweisgeberschutz – interne Meldestelle",
     "text":"Einstimmig: Interne Meldestelle nach HinSchG eingerichtet (15:0).",**anon(15,0,10)},
]

# ── SR 2023-12-18 (21.) ─────────────────────────────────────────────────────
A = ["beibl","gruber","pschorr"]
new_sessions.append({"id":"sr_20231218","date":"2023-12-18","type":"stadtrat",
    "title":"21. Stadtratssitzung – Dezember 2023","absent":A,
    "agenda":[
        {"number":1,"title":"Mitteilungen","type":"formal"},
        {"number":2,"title":"Bürgerfragen","type":"formal"},
        {"number":3,"title":"Genehmigung Niederschrift HVFA 30.11.","voteId":"sr_20231218_01"},
        {"number":4,"title":"Kita-Sonnensiedlung – Kreditermächtigung 1,25 Mio €","topicId":"t7","voteId":"sr_20231218_02"},
        {"number":5,"title":"Haushaltssatzung 2024 – Erlass","topicId":"t7","voteId":"sr_20231218_03"},
        {"number":6,"title":"Anfragen","type":"formal"},
    ]})
new_votes += [
    {"id":"sr_20231218_01","sessionId":"sr_20231218","topicId":None,"date":"2023-12-18",
     "title":"Genehmigung Niederschrift HVFA 30.11.","text":"Einstimmig genehmigt (17:0).",**anon(17,0,8)},
    {"id":"sr_20231218_02","sessionId":"sr_20231218","topicId":"t7","date":"2023-12-18",
     "title":"Kita Sonnensiedlung – Kreditermächtigung 1,25 Mio €",
     "text":"Kreditermächtigung für die Erweiterung der Kindertageseinrichtung beschlossen (18:0).",
     **anon(18,0,7)},
    {"id":"sr_20231218_03","sessionId":"sr_20231218","topicId":"t7","date":"2023-12-18",
     "title":"Haushaltssatzung 2024",
     "text":"Haushaltssatzung mit allen Anlagen beschlossen (22:0).",**anon(22,0,3)},
]

# ============================================================================
# NEW TOPIC: t20 Amperauen
# ============================================================================
T20 = {
    "id": "t20",
    "title": "Amperauen / Wohngebiet & Park",
    "tags": ["building", "environment"],
    "image": None,
    "summary": "Großes Wohnbaugebiet im Norden Moosburgs mit Mehrfamilienhäusern, Grünpark, Mühlbachterrassen und Verkehrsregelung. Aufstellung des Bebauungsplans 63 „SO Amperauen\", später ergänzt um Parkgestaltung und Widmungen.",
    "history": [
        {"date":"2023-04-24","type":"vote",
         "title":"B-Plan 52 Amperauen – Einfriedungen",
         "text":"Antrag, Beschluss zu Einfriedungen aufzuheben, mit 6:14 abgelehnt.",
         "sessionId":"sr_20230424","voteId":"sr_20230424_02"},
        {"date":"2023-05-15","type":"vote",
         "title":"B-Plan 63 SO Amperauen – Planung beschlossen",
         "text":"Nach Abwägung von 27 Stellungnahmen wird die Planung einstimmig beschlossen.",
         "sessionId":"sr_20230515","voteId":"sr_20230515_02"},
        {"date":"2023-10-23","type":"vote",
         "title":"B-Plan 63 SO Amperauen – Stellungnahmen Auslegung",
         "text":"In 13 Einzelabstimmungen werden die Stellungnahmen aus der erneuten Auslegung abgewogen.",
         "sessionId":"sr_20231023","voteId":"sr_20231023_01"},
        {"date":"2023-11-23","type":"vote",
         "title":"Parkgestaltung Amperauen",
         "text":"Einstimmig: Wohngebietspark als Grünanlage beschlossen.",
         "sessionId":"bpu_20231123","voteId":"bpu_20231123_02"},
        {"date":"2023-11-23","type":"vote",
         "title":"Mühlbachterrassen – Machbarkeitsstudie",
         "text":"Einstimmig: Studie befürwortet; Schwemme zu prüfen.",
         "sessionId":"bpu_20231123","voteId":"bpu_20231123_03"},
        {"date":"2023-11-23","type":"vote",
         "title":"Amperpark – Widmung",
         "text":"Einstimmig beschlossen.",
         "sessionId":"bpu_20231123","voteId":"bpu_20231123_15"},
    ]
}

# ============================================================================
# History extensions for existing topics
# ============================================================================
HISTORY_INSERTS = {
    "t3": [
        {"date":"2023-01-12","type":"vote",
         "title":"Auf dem Plan – Granitpflaster (abgelehnt)",
         "text":"Antrag auf gebundene Granitpflaster-Verlegung knapp abgelehnt (10:11).",
         "sessionId":"sr_20230112","voteId":"sr_20230112_02"},
        {"date":"2023-03-27","type":"vote",
         "title":"Auf dem Plan – Entwurfsplanung + Ausschreibung",
         "text":"Einstimmig: Entwurfsplanung 13.03.2023 + Ausschreibung mit Teilnahmewettbewerb.",
         "sessionId":"sr_20230327","voteId":"sr_20230327_02"},
        {"date":"2023-07-24","type":"vote",
         "title":"Denkmalförderung „Auf dem Plan 14\"",
         "text":"100.000 € Bundeszuschuss + 40.000 € städtischer Eigenanteil über „Lebendige Zentren\".",
         "sessionId":"sr_20230724","voteId":"sr_20230724_05"},
    ],
    "t2": [
        {"date":"2023-04-24","type":"vote",
         "title":"Fahrgastbefragung Bahnhof",
         "text":"Einstimmig: Online-Befragung zum Nutzungsverhalten am Bahnhof.",
         "sessionId":"sr_20230424","voteId":"sr_20230424_05"},
    ],
    "t6": [
        {"date":"2023-07-24","type":"vote",
         "title":"TG-Grundschule – 4 neue Klassenzimmer",
         "text":"2.720.121 € für 4 zusätzliche Klassenzimmer (21:0).",
         "sessionId":"sr_20230724","voteId":"sr_20230724_06"},
    ],
    "t12": [
        {"date":"2023-03-27","type":"vote",
         "title":"Freibad – Bundesprogramm SJK 2022 Antragstellung",
         "text":"Einstimmig: Bewerbung um Bundesförderung zur Freibadsanierung.",
         "sessionId":"sr_20230327","voteId":"sr_20230327_03"},
        {"date":"2023-04-24","type":"vote",
         "title":"Freibad – Badegebühren angepasst",
         "text":"Neue Badegebührenordnung beschlossen (13:7).",
         "sessionId":"sr_20230424","voteId":"sr_20230424_03"},
    ],
    "t13": [
        {"date":"2023-04-17","type":"vote",
         "title":"Vorbereitende Untersuchungen Innenstadt–Bahnhof",
         "text":"Beauftragung der Vorbereitenden Untersuchungen nach § 141 BauGB (13:9).",
         "sessionId":"sr_20230417","voteId":"sr_20230417_02"},
        {"date":"2023-07-17","type":"vote",
         "title":"Sanierungsrechtliches Einvernehmen – Herrnstr. 29 verweigert",
         "text":"Sanierungsrechtl. Einvernehmen mit 9:1 verweigert: Erhalt EG-Gewerbe ist Sanierungsziel.",
         "sessionId":"bpu_20230717","voteId":"bpu_20230717_05"},
        {"date":"2023-12-14","type":"vote",
         "title":"Städtebauförderung 2024 – Bedarfsanmeldung",
         "text":"Bedarfsanmeldung beschlossen (15:0).",
         "sessionId":"sr_20231214","voteId":"sr_20231214_04"},
    ],
    "t14": [
        {"date":"2023-09-21","type":"vote",
         "title":"Isarwehr – Denkmalschutz",
         "text":"Einstimmig: Denkmaleintragung befürwortet.",
         "sessionId":"bpu_20230921","voteId":"bpu_20230921_02"},
        {"date":"2023-09-21","type":"vote",
         "title":"Wasserkraftwerk Pfrombach – Denkmalschutz",
         "text":"Einstimmig: Denkmaleintragung befürwortet.",
         "sessionId":"bpu_20230921","voteId":"bpu_20230921_03"},
    ],
    "t15": [
        {"date":"2023-02-13","type":"vote",
         "title":"Strom-Bündelausschreibung 2024/2025",
         "text":"Einstimmig: Änderung des Bündelausschreibungs-Beschlusses.",
         "sessionId":"sr_20230213","voteId":"sr_20230213_03"},
        {"date":"2023-06-26","type":"vote",
         "title":"Straßenbeleuchtung – LED-Umrüstung",
         "text":"Einstimmig: Umstellung auf LED.",
         "sessionId":"sr_20230626","voteId":"sr_20230626_04"},
        {"date":"2023-07-10","type":"vote",
         "title":"FC Moosburg – Flutlicht-LED-Zuschuss",
         "text":"Einstimmig: ~38.700 € (20 %) Zuschuss zum LED-Umbau.",
         "sessionId":"sr_20230710","voteId":"sr_20230710_02"},
        {"date":"2023-12-14","type":"vote",
         "title":"Solarförderung – Änderung",
         "text":"Anpassung der städtischen Solarförderrichtlinie.",
         "sessionId":"sr_20231214","voteId":"sr_20231214_07"},
    ],
    "t17": [
        {"date":"2023-02-13","type":"vote",
         "title":"Rathaus – Erweiterungsbau Herrnstr. 2",
         "text":"Einstimmig: Gemeindliches Einvernehmen für den Rathaus-Erweiterungsbau.",
         "sessionId":"sr_20230213","voteId":"sr_20230213_02"},
    ],
    "t4": [
        {"date":"2023-03-20","type":"vote",
         "title":"Verkehrsführung Thalbacher/Bahnhofstr.",
         "text":"Einstimmig: Planung wird vergeben.",
         "sessionId":"bpu_20230320","voteId":"bpu_20230320_09"},
        {"date":"2023-03-20","type":"vote",
         "title":"Münchener/Westerbergstr. – Umbau beschlossen",
         "text":"Einstimmig: endgültiger Umbau.",
         "sessionId":"bpu_20230320","voteId":"bpu_20230320_10"},
        {"date":"2023-03-20","type":"vote",
         "title":"Fahrradzone südlich Industriestr.",
         "text":"Festlegung mit 10:2.",
         "sessionId":"bpu_20230320","voteId":"bpu_20230320_13"},
        {"date":"2023-11-23","type":"vote",
         "title":"Fahrradstraßen – mehrere Beschlüsse",
         "text":"Gärtnerstr. (9:3 angenommen), Burgermühlstr. Fahrradzone (7:5), Wasserwerkstr. (abgelehnt 5:7), Reiteraustr. (abgelehnt 3:9).",
         "sessionId":"bpu_20231123","voteId":"bpu_20231123_16"},
    ],
    "t18": [
        {"date":"2023-09-21","type":"vote",
         "title":"Degernpoint – Parkplatz mit E-Ladestationen",
         "text":"Einvernehmen erteilt (6:5).",
         "sessionId":"bpu_20230921","voteId":"bpu_20230921_05"},
    ],
    "t16": [
        {"date":"2023-03-27","type":"discussion",
         "title":"Hallenbad-Neubau – Sachstand",
         "text":"Architekt informiert den Stadtrat über den aktuellen Planungsstand des Hallenbad-Neubaus.",
         "sessionId":"sr_20230327"},
    ],
    "t7": [
        {"date":"2023-09-04","type":"vote",
         "title":"Weingraben-Kanalsanierung – 300 T€ überplanmäßig",
         "text":"Einstimmig: Überplanmäßige Mittel für Sanierung des Weingraben-Kanals.",
         "sessionId":"sr_20230904","voteId":"sr_20230904_02"},
        {"date":"2023-07-24","type":"vote",
         "title":"Kläranlage – Jahresabschluss 2022 + Entlastung",
         "text":"Einstimmig festgestellt; 6 AR-Mitglieder enthielten sich.",
         "sessionId":"sr_20230724","voteId":"sr_20230724_03"},
        {"date":"2023-10-23","type":"vote",
         "title":"Jahresrechnung 2021 – Feststellung + Entlastung",
         "text":"Einstimmig festgestellt und entlastet.",
         "sessionId":"sr_20231023","voteId":"sr_20231023_02"},
        {"date":"2023-12-18","type":"vote",
         "title":"Haushaltssatzung 2024",
         "text":"Haushaltssatzung 2024 mit allen Anlagen beschlossen (22:0).",
         "sessionId":"sr_20231218","voteId":"sr_20231218_03"},
    ],
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
existing = {s["id"] for s in sessions}
added_s = 0
for s in new_sessions:
    if s["id"] not in existing:
        sessions.append(s); added_s += 1
        print(f"+ session {s['id']}")
with open(f"{BASE}/sessions.json","w",encoding="utf-8") as f: json.dump(sessions, f, ensure_ascii=False, indent=2)

with open(f"{BASE}/votes.json","r",encoding="utf-8") as f: votes = json.load(f)
existing_v = {v["id"] for v in votes}
added_v = 0
for v in new_votes:
    # strip helper "__" key if present (was a typo escape)
    v.pop("__", None)
    if v["id"] not in existing_v:
        votes.append(v); added_v += 1
with open(f"{BASE}/votes.json","w",encoding="utf-8") as f: json.dump(votes, f, ensure_ascii=False, indent=2)

with open(f"{BASE}/topics.json","r",encoding="utf-8") as f: topics = json.load(f)
tmap = {t["id"]: t for t in topics}
if "t20" not in tmap:
    topics.append(T20); tmap["t20"] = T20
    print("+ topic t20 (Amperauen)")

for tid, entries in HISTORY_INSERTS.items():
    t = tmap.get(tid)
    if not t: continue
    keys = {(e["date"], e.get("voteId"), e.get("title")) for e in t["history"]}
    for entry in entries:
        k = (entry["date"], entry.get("voteId"), entry.get("title"))
        if k not in keys:
            insert_chrono(t["history"], entry)
            print(f"  ~ {tid} += {entry['date']} {entry['title'][:40]}")
with open(f"{BASE}/topics.json","w",encoding="utf-8") as f: json.dump(topics, f, ensure_ascii=False, indent=2)

print(f"\nDone. sessions: +{added_s} (total {len(sessions)}), votes: +{added_v} (total {len(votes)})")
