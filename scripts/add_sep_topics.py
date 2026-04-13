import json

BASE = "c:/Users/bened/Documents/GitHub/bagruber/council/data"

with open(f"{BASE}/topics.json", "r", encoding="utf-8") as f:
    topics = json.load(f)

# ── Update t8 (Schulwegsicherheit): insert 2025-09-08 entry chronologically ───
for t in topics:
    if t["id"] == "t8":
        new_entry = {
            "date": "2025-09-08",
            "type": "committee",
            "title": "Informationsveranstaltung beschlossen",
            "text": "CSU-Fraktion und StR Fincke beantragen die Aufhebung eines BPU-Beschlusses vom 21.07.2025. Der Stadtrat einigt sich einstimmig auf einen Mittelweg: In Abstimmung mit den betroffenen Schulen wird eine Informationsveranstaltung zu möglichen Verkehrsmaßnahmen durchgeführt. Die bevorzugte Variante kommt danach zur Abstimmung.",
            "sessionId": "sr_20250908",
            "voteId": "sr_20250908_02"
        }
        # insert before first entry that is >= 2025-09-09
        inserted = False
        for i, entry in enumerate(t["history"]):
            if entry["date"] >= "2025-09-09":
                t["history"].insert(i, new_entry)
                inserted = True
                break
        if not inserted:
            t["history"].append(new_entry)
        print(f"t8 updated: {len(t['history'])} history entries")
        break

# ── New t13: Sanierungsgebiet Zwischen Innenstadt und Bahnhof ────────────────
t13 = {
    "id": "t13",
    "title": "Sanierungsgebiet Innenstadt–Bahnhof",
    "tags": ["innercity", "infrastructure", "building"],
    "image": None,
    "summary": "Das Sanierungsgebiet \u201eZwischen Innenstadt und Bahnhof\u201c wird nach vorbereitenden Untersuchungen und öffentlicher Beteiligung förmlich festgelegt. Ziel ist die städtebauliche Aufwertung des Bereichs zwischen Stadtplatz und Bahnhofsgelände. Die Schloss Aschwiese wird nach Einwendungen aus dem Umgriff herausgenommen.",
    "history": [
        {
            "date": "2025-01-01",
            "type": "milestone",
            "title": "Vorbereitende Untersuchungen abgeschlossen",
            "text": "Auf Grundlage der Vorbereitenden Untersuchungen gemäß §§ 137, 139 BauGB werden Ziele und Zwecke der Sanierung erarbeitet. Das Sanierungsgebiet umfasst den Bereich zwischen Innenstadt und Bahnhof."
        },
        {
            "date": "2025-09-22",
            "type": "vote",
            "title": "Sanierungsgebiet förmlich festgelegt",
            "text": "Der Stadtrat beschließt einstimmig die Sanierungssatzung \u201eZwischen Innenstadt und Bahnhof\u201c (§ 142 BauGB). Vereinfachtes Verfahren, Laufzeit 15 Jahre. Die Schloss Aschwiese wird auf Einwendung des AELF Ebersberg-Erding aus dem Umgriff herausgenommen.",
            "sessionId": "sr_20250922",
            "voteId": "sr_20250922_08"
        }
    ]
}

# ── New t14: Wachbaracken Stalag VII A ────────────────────────────────────────
t14 = {
    "id": "t14",
    "title": "Erhalt Wachbaracken Stalag VII A",
    "tags": ["culture"],
    "image": None,
    "summary": "Die historischen Wachbaracken des Stalag VII A – eines der größten alliierten Kriegsgefangenenlager des Zweiten Weltkriegs bei Moosburg – sollen dauerhaft erhalten werden. Stadt und Landkreis Freising schließen eine Zweckvereinbarung zum gemeinsamen Erhalt der Bausubstanz.",
    "history": [
        {
            "date": "2024-12-09",
            "type": "vote",
            "title": "Förderantrag Stalag Moosburg e.V.",
            "text": "Der Stadtrat beschließt über einen Förderantrag des Stalag Moosburg e.V., der sich für die Erinnerungsarbeit rund um das Stalag VII A engagiert.",
            "sessionId": "sr_20241209",
            "voteId": "sr_20241209_07"
        },
        {
            "date": "2025-09-22",
            "type": "vote",
            "title": "Zweckvereinbarung mit Landkreis Freising",
            "text": "Der Stadtrat ermächtigt Bürgermeister Dollinger einstimmig zum Abschluss einer Zweckvereinbarung mit dem Landkreis Freising zum dauerhaften Erhalt der historischen Wachbaracken des Stalag VII A.",
            "sessionId": "sr_20250922",
            "voteId": "sr_20250922_09"
        }
    ]
}

topics.append(t13)
topics.append(t14)

with open(f"{BASE}/topics.json", "w", encoding="utf-8") as f:
    json.dump(topics, f, ensure_ascii=False, indent=2)
print(f"topics.json: {len(topics)} topics")
