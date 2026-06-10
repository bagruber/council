# Projektkontext – Council Transparency App Moosburg a.d. Isar

> Stand: 2026-06-10. Dient als Restart-Dokument für LLMs.

---

## Worum geht es

Eine Transparenz-App für den Stadtrat Moosburg a.d. Isar (Bayern). Ziel: Abstimmungsverhalten, Themen-Timelines und Sitzungsgeschichte öffentlich und durchsuchbar machen. Der Betreiber ist selbst Stadtrat (fresh-Fraktion, seit Oktober 2022 im Amt nach Nachrücken für Neumayr).

Lokale URL zum Testen: `npx serve` im Root.
Keine Dependencies im Frontend – Vanilla JS, Parliament-Chart ist pure SVG (kein D3). Fonts self-hosted in `fonts/`.

---

## Tech-Stack

- `index.html` + `js/core.js` + `js/app.js` + `js/parliament.js` + `css/style.css` + `css/fonts.css`
- `js/core.js` (`Council`): geteilte Perioden- & Vote-Status-Logik (siehe `docs/CORE.md`)
- Hash-basiertes Routing: `#/member/{id}`, `#/topic/{id}`, `#/session/{id}`, Tag-Filter `#/?tags={id},{id}`
- Farbpalette: Rot-Gradient primary, Gold accent, Rainbow secondaries
- `const SHOW_PRONOUNS = true/false` in `js/app.js`

---

## Datenquellen (alle handgepflegt)

| Datei | Inhalt |
|---|---|
| `data/members.json` | Alle Stadtratsmitglieder, Parteien, Mandate, Ausschusssitze |
| `data/sessions.json` | Sitzungen mit Tagesordnung und Absenzen |
| `data/votes.json` | Abstimmungen mit Einzel- oder Gesamtstimmen |
| `data/topics.json` | Themen mit Timeline-History |
| `data/tags.json` | Tags für Topics |
| `data/press.json` | Presseartikel (ID-Schema: `{media}_{YYYY-MM-DD}_{slug}`) |
| `data/bundle.json` | Kombiniertes Paket (Build-Artefakt via `scripts/build_data.py`) |

---

## Datenstruktur-Konventionen

### sessions.json

```json
{
  "id": "sr_20241021",
  "date": "2024-10-21",
  "type": "stadtrat",          // "stadtrat" | "bpu" | "hvfa" | "pa" | "rpa"
  "title": "...",
  "absent": ["gruebl", "..."],  // Stadtrat: alle Abwesenden; BPU: nur ohne Vertretung
  "substitutes": [              // nur BPU/Ausschüsse
    { "member": "gruebl", "substitute": "gruber" }
  ],
  "agenda": [
    {
      "number": "4.3.1",
      "title": "Kurztitel",
      "voteId": "sr_20241021_03",   // optional
      "topicId": "t5",               // optional
      "type": "formal" | "discussion" // wenn kein Vote
    }
  ]
}
```

**Wichtig bei BPU-Sitzungen:** `absent` = abwesend OHNE Vertretung; wer eine Vertretung hat, steht nur in `substitutes`.

### votes.json

```json
{
  "id": "sr_20241021_03",
  "sessionId": "sr_20241021",
  "topicId": "t5",           // null wenn kein Thema
  "date": "2024-10-21",
  "title": "Kurzbezeichnung Beschluss",
  "text": "Volltext des Beschlusses.",
  "type": "named",           // "named" | "anonymous"
  "result": "rejected",      // optional: "rejected" | "passed" (nur bei anonymen)
  "results": {
    // named:
    "yes": ["dollinger", "gruber", ...],
    "no": ["stanglmaier", ...],
    "absent": ["beubl", ...]
    // anonymous:
    // "yes": 15, "no": 7, "absent": 3
  }
}
```

**Gesamtstimmen:** 25 Mitglieder (24 StR + 1 BM Dollinger). Bei BPU/HVFA sind es je nach Gremium weniger.

**Einstimmige Votes (named):** `no: []`, Text enthält „Einstimmig".

### members.json (Struktur)

Jedes Mitglied hat u.a.:
- `id` (z.B. `"gruber"`, `"stanglmaier"`)
- `name`, `party` (z.B. `"fresh"`, `"CSU"`, `"SPD"`, `"FW"`, `"Grüne"`, `"Linke"`)
- `from`, `to` (Amtszeiten, ISO-Datum)
- `profile.motions[]` – eingebrachte Anträge
- `seatConfigs` – Ausschusssitze und Funktionen

---

## Gremien und Mitgliederzahl

| Gremium | Kürzel | Mitglieder |
|---|---|---|
| Stadtrat | `sr` | 25 (24 StR + BM) |
| Bau-, Planungs- und Umweltausschuss | `bpu` | ~12 |
| Hauptverwaltungs- und Finanzausschuss | `hvfa` | ~9 |
| Personalausschuss | `pa` | ~7 |
| Rechnungsprüfungsausschuss | `rpa` | ~5 |

---

## Mitglieder-IDs (wichtigste)

| ID | Name | Partei | Besonderheit |
|---|---|---|---|
| `dollinger` | Josef Dollinger | CSU | 1. Bürgermeister |
| `hadersdorfer` | Michael Hadersdorfer | CSU | 2. BM |
| `stanglmaier` | ... | CSU | 3. BM |
| `gruber` | Benedict Gruber | fresh | App-Betreiber, ab 24.10.2022 (nachrückt für Neumayr) |
| `neumayr` | ... | fresh | bis 24.10.2022 |
| `john` | ... | SPD | bis 24.07.2023 (dann Strobl) |
| `strobl` | ... | Linke/SPD | ab 24.07.2023 |
| `gruebl` | ... | CSU | bis ~21.10.2024 (dann Hobmaier) |
| `hobmaier` | ... | CSU | ab 21.10.2024 |
| `beubl` | ... | CSU | bis ~24.03.2025 (dann Marcus) |
| `marcus` | Gunnar Marcus | SPD | ab 24.03.2025 |
| `kieninger` | ... | fresh | neueres Mitglied |

Weitere: `becher_a`, `becher_j`, `beibl`, `fincke`, `grundner`, `haberl`, `heinz`, `kaestl`, `lauterbach`, `linz_karin`, `linz_kilian`, `pschorr`, `reif`, `tristl`, `von_pressentin`, `weber`, `welter`

---

## Themen (topics) – aktuelle IDs

| ID | Thema |
|---|---|
| t1 | SGT Istanbul Vereinsheim |
| t2 | Bahnhof Moosburg |
| t3 | Auf dem Plan (Stadtplatzsanierung) |
| t4 | Verkehr / Radwege |
| t5 | Rockermaier Areal (B-Plan 77) |
| t6 | Theresia-Gerhardinger-Grundschule |
| t7 | Haushalt / Finanzen |
| t8 | Schulwege / Schulzentrum Süd |
| t9 | Kreisverkehr Landshuter/Stadtwaldstr. |
| t10 | Wirtschaftsförderung / Stadtmarketing |
| t11 | Legal Wall / Street Art |
| t12 | Freibad / Schwimmbäder |
| t13 | Sanierungsgebiet Innenstadt–Bahnhof |
| t14 | Stalag VII A / Wachbaracken |
| t15 | Energie / Windenergie / PV / LED |
| t16 | Hallenbad |
| t17 | Rathaus Sanierung/Erweiterung |
| t18 | Degernpoint (Gewerbegebiet) |
| t19 | DAV Kletter-/Boulderhalle |
| t20 | Amperauen / B-Plan 63 |

---

## Sitzungsabdeckung – Stand 2026-06-10

Die App deckt alle Sitzungen ab, die in der **Bürgerinfo-Niederschrift** veröffentlicht wurden. Vollständig eingetragen:

**2022:** StR 05.09., 19.09., 24.10. | BPU 17.11.
**2023:** StR 12.01., 30.01., 13.02., 06.03., 27.03., 17.04., 24.04., 15.05., 22.05., 12.06., 26.06., 10.07., 24.07., 04.09., 23.10., 14.12., 18.12. | BPU 23.01., 20.03., 17.07., 21.09., 23.11.
**2024:** StR 19.02., 04.03., 18.03., 08.04., 22.04., 06.05., 10.06., 17.06., 22.07., 02.12., 09.12., 16.12. | BPU 14.03., 15.07., 30.09. | HVFA 28.11.
**2025:** StR 20.01., 10.02., 24.02., 24.03., 10.04., 28.04., 02.06., 23.06., 14.07., 28.07., 08.09., 22.09., 13.10., 29.10., 01.12., 15.12. | BPU 16.01., 17.03., 22.05., 06.10., 08.12.
**2026:** StR 12.01., 02.02., 23.02.

**Zusätzlich in Daten (ohne Bürgerinfo-Niederschrift, direkt eingetragen):**
StR 01.07.2024, 02.09.2024, 23.09.2024, 07.10.2024, 21.10.2024, 04.11.2024, 18.11.2024, 10.11.2025

---

## ⚠️ Bekannte offene Punkte

### 1. Fehlende Sitzung: BPU/HVFA 21.07.2025
Die Gemeinschaftssitzung BPU + HVFA vom **21. Juli 2025** fehlt komplett in `sessions.json` und `votes.json`. Belegt durch Agenda-TOP in bpu_20251006: „Genehmigung Niederschrift BPU 21.07.2025". Niederschrift-PDF sollte in `data/niederschriften/` liegen.

### 2. Sessions ohne `absent`-Feld
- `sr_20251110` (10.11.2025): kein `absent`-Array
- `bpu_20231123` (23.11.2023): kein `absent`-Array, keine `substitutes`
- `hvfa_20241128`: kein `absent`-Array (bei HVFA evtl. bewusst weggelassen)

### 3. StR 12.05.2025 (7. Stadtratssitzung)
Existierte nachweislich (in sr_20250714 Niederschrift-Genehmigung erwähnt), hat aber keine Bürgerinfo-Niederschrift und ist daher **nicht** in der Ziel-Liste und **nicht** in den Daten. Kein Handlungsbedarf.

---

## Wichtige Workflow-Regeln

### Niederschrift einarbeiten
1. PDF liegt in `data/niederschriften/`
2. Skill `/niederschrift-einarbeiten` verwenden (liest PDF, trägt Sessions + Votes + ggf. Topics ein)
3. Danach Skill `/validate-data` ausführen

### Topic-Watchlist
`data/knowledge/topic-watchlist.md` — vom User benannte Themen, die auf jeden
Fall eigene Topic-Seiten bekommen sollen. Wird beim Einarbeiten von
Niederschriften geprüft; die Anlage von Watchlist-Themen ist vorab genehmigt
(kein Nachfragen, aber in der Zusammenfassung erwähnen).

### Namenskonventionen
- Session-IDs: `{typ}_{YYYYMMDD}` (z.B. `sr_20250602`, `bpu_20250522`)
- Vote-IDs: `{sessionId}_{NN}` (zweistellig, z.B. `sr_20250602_01`)
- Press-IDs: `{media}_{YYYY-MM-DD}_{slug}`
- Topic-IDs: `t{N}` (fortlaufend, nächste wäre `t21`)

### Named vs. Anonymous Votes
- **Named** wenn die Niederschrift Einzelstimmen nennt (meist bei knappen oder kontroversen Votes + erste Vote je Sitzung)
- **Anonymous** wenn nur Gesamtzahlen (z.B. „15:7")
- Bei einstimmigen Votes: entweder named mit `no: []` oder anonymous mit `no: 0`

### Absenzen
- In `sessions.absent`: immer ALLE abwesenden Stadtratsmitglieder (für Stadtratssitzungen)
- In `votes.results.absent`: alle die bei DIESER spezifischen Abstimmung abwesend waren (kann abweichen wenn jemand kurz rausgeht)
- Für BPU-Sitzungen: `sessions.absent` = nur die ohne Vertretung; `sessions.substitutes` = die mit Vertretung

### Einstimmige named Votes
Wenn in Niederschrift „einstimmig" steht und Einzelstimmen nicht aufgeführt:
→ alle Anwesenden in `yes`, keine in `no`, Abwesende aus `session.absent` in `absent`

---

## Skills (slash commands)

| Skill | Zweck |
|---|---|
| `/niederschrift-einarbeiten` | PDF-Niederschrift → sessions/votes/topics |
| `/validate-data` | Validierung aller JSON-Dateien |
| `/build-data` | bundle.json neu bauen |
| `/member-update` | Mitgliederwechsel eintragen |
| `/antrag-einarbeiten` | Antrag in member.profile.motions |
| `/presseartikel-einarbeiten` | Press-Eintrag + Verlinkung |
| `/topic-anlegen` | Neues Thema anlegen |

---

## Daten-Validierung

Script: `scripts/validate_data.py`. Prüft referentielle Integrität (z.B. ob voteIds in sessions auch in votes existieren, ob member-IDs gültig sind). Immer nach größeren Änderungen ausführen.

---

## Git-Branch-Konvention

Aktueller Branch: `parliament-v2`. Main-Branch für PRs: `main`.
