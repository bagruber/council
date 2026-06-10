---
name: topic-anlegen
description: Legt ein neues Thema in topics.json an (tN-ID, summary, tags, leerer history-Array). Optional gleich erste history-Einträge aus bestehenden Sessions/Voten/Pressemitteilungen. Verwende dies wenn ein wiederkehrendes Themenfeld (≥2 Sitzungen mit eigenen Voten) sichtbar wird, das noch nicht abgedeckt ist — und User die Anlage bestätigt hat (nie eigenmächtig!).
---

# Neues Thema anlegen

## Wichtig: nicht eigenmächtig

Themen sind die zentrale Navigationseinheit. Falsch zugeschnittene oder zu granulare Themen vermüllen die Übersicht. **Immer erst mit dem User absprechen**, bevor ein Topic angelegt wird (siehe Feedback-Memo „Im Zweifel nachfragen beim Neuzuschnitt von Themen").

Die Niederschriften-Skill schlägt manchmal neue Topics vor — diese Vorschläge sollen aufgelistet, aber nicht direkt umgesetzt werden. Erst nach User-OK diesen Skill aufrufen.

**Ausnahme — Watchlist:** Steht das Thema in `data/knowledge/topic-watchlist.md`, ist die Anlage vorab genehmigt; kein erneutes Nachfragen nötig. Nach Anlage die Status-Spalte des Watchlist-Eintrags auf die neue `tN` setzen und die Anlage in der Zusammenfassung erwähnen.

## Wann ist ein Topic gerechtfertigt?

- **≥ 2 separate Sitzungen** mit eigenen Voten/Diskussionen zum selben Sachgebiet.
- Erkennbar als zusammenhängender **kommunalpolitischer Prozess** (Bauleitplanung, Sanierung, Gebührensatzung, Förderprogramm) — nicht nur eine Einzelfrage.
- **Presse-Berichterstattung** über mehrere Monate.
- Mehrere Mitglieder als Antragsteller:innen / Hauptakteur:innen involviert.

Nicht passend: ein einmaliger Antrag, ein Personalbeschluss, eine routinemäßige Satzungsänderung.

## Datenmodell

```jsonc
// data/topics.json (Array)
{
  "id": "t21",                       // nächste freie tN
  "title": "Hochwasserschutz Amperufer",
  "tags": ["infrastructure", "environment"],   // 1-3 aus data/tags.json
  "image": null,                     // optional: "img/topics/hochwasser.jpg"
  "summary": "1-3 Sätze, was das Thema umfasst und welche Frage politisch entschieden wird.",
  "history": [
    {
      "date": "2023-05-15", "type": "milestone",
      "title": "...", "text": "...",
      "sessionId": "...", "voteId": "...",     // optional
      "press": ["..."]                          // optional
    }
  ]
}
```

`type` der History-Einträge:
- `"vote"` — beschlossene Abstimmung
- `"committee"` — Diskussion ohne Beschluss
- `"milestone"` — externes Ereignis, Förderzusage, Fertigstellung
- `"proposal"` — Antrag eingereicht
- `"press"` — eigenständige Berichterstattung ohne Sitzungskontext

## Vorgehen

1. **Vorschlag formulieren** und mit User abstimmen (Titel, Scope, Tags). Vorschlag enthält:
   - Vorgeschlagener Titel
   - Welche Sitzungen/Voten könnten Initial-History sein (3-5 Einträge reichen)
   - Vorgeschlagene Tags
   - Mögliche Abgrenzungen zu bestehenden Topics
2. Nach OK: nächste freie `tN` ermitteln (`max(int(t['id'][1:]) for t in topics) + 1`).
3. Eintrag anlegen, sortiert nach Datum.
4. Existierende Voten/Sitzungen verknüpfen: pro Vote `topicId` setzen, in der Session-`agenda` ggf. auch.
5. Tags prüfen in `data/tags.json`. Falls passender Tag fehlt → mit User klären, ob neuer Tag oder bestehender genügt.
6. `validate-data` ausführen.
7. Commit: `topic: t21 Hochwasserschutz Amperufer (initial 4 history entries)`.

## Edge Cases

- **Topic existiert schon im weiteren Sinne** (z.B. „Energie/Wärmeplanung" → t15 Energie): bestehendes erweitern statt neues anzulegen.
- **Topic-Image**: Wenn vorhanden, Datei in `img/topics/` ablegen und `image`-Feld setzen. Sonst null.
- **Topic ist zu klein**: weniger als 2-3 substantielle History-Einträge nach Initial-Befüllung? Lieber nicht anlegen, in andere Topic integrieren oder als topiclose Voten lassen.
- **Topic überschneidet**: ein Vote kann nur einem Topic zugeordnet sein. Bei echter Mehrdeutigkeit: User-Entscheidung.
