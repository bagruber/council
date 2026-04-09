# Council Transparency App – Moosburg a.d. Isar

## Stack & Architektur

- Vanilla JS, kein Framework, keine npm-Dependencies
- D3.js v7 (nur für Parliament-Visualisierung)
- Hash-basiertes Routing (`#/member/id`, `#/topic/id`, etc.)
- Lokaler Webserver zum Testen: `npx serve`
- Single-page App: `index.html` + `js/app.js` + `js/parliament.js` + `css/style.css`

## Datenquellen

### Aktuell: Statische JSON-Dateien
- `data/members.json` — Mitglieder, Parteien, Gremien, Medien
- `data/topics.json` — Themen mit Timeline-History
- `data/sessions.json` — Sitzungen mit Tagesordnung
- `data/votes.json` — Abstimmungen mit Einzelstimmen
- `data/tags.json` — Themen-Tags

### Geplant: OParl API
- Standardisierte REST/JSON-Schnittstelle für Ratsinformationssysteme
- Anonymer, lesender Zugriff auf Sitzungs-, Gremien- und Dokumentendaten
- Referenzdoku: `data/knowledge/oparl-api.md`
- Schrittweise Integration: OParl-Daten ersetzen nach und nach hardcoded JSON
- Mapping: OParl-Objekttypen → lokale Datenstrukturen (siehe `data/knowledge/data-mapping.md`)

### Geplant: Knowledge Base
- Zusätzliche Infos aus Niederschriften, Presseartikeln, manuellen Eingaben
- Struktur: `data/knowledge/` — themenübergreifendes Wissen, Quellenverweise
- Ziel: Hochgradig vernetzte Informationen innerhalb der Plattform
- Aufwärtskompatibel: Datenstruktur muss wachsen können (Vergangenheit + Zukunft)

## Datenstruktur-Prinzipien

- Themen (`topics`) sind die zentrale Navigationseinheit, nicht Einzeldokumente
- Jedes Thema hat eine Timeline aus History-Einträgen (Meilensteine, Anträge, Abstimmungen)
- History-Einträge verlinken zu Sessions, Votes und Presseartikeln
- Abstimmungsverhalten wird transparent gemacht, auch in Member-Profilen
- Externe Quellen (Presse, Dokumente) werden verlinkt, nicht dupliziert
- Relative Datumsangaben immer in absolute Daten umwandeln

## UI & Design

- Moosburg-Farbpalette: Rot-Gradient primary, Gold accent, Rainbow secondaries
- Heller, freundlicher Look
- Einheitliche Designsprache über die gesamte Plattform
- Wiederkehrende Elemente (Chips, Badges, Cards, Links) konsistent gestalten
- Informationsdichte balancieren: Details versteckt oder auf eigenen Seiten
- Nicht alles muss auf den ersten Blick sichtbar sein
- Bildmaterial in Themen-Timelines modern und ansprechend einbauen (Zukunft)
- Parteien haben eigene Farben, die durchgängig verwendet werden

## Code-Stil

- Code darf nicht LLM-generiert wirken
- Kommentare minimal und natürlich halten
- Keine unnötigen Abstraktionen oder Utilities für einmalige Operationen
- Keine Docstrings oder Type-Annotations wo nicht nötig

## Konfiguration

- `const SHOW_PRONOUNS = true/false` in `js/app.js` — Pronomen ein-/ausblenden
