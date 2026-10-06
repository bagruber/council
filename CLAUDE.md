# Council Transparency App – Moosburg a.d. Isar

## Stack & Architektur

- Vanilla JS, kein Framework, keine externen Dependencies (Parliament-Chart ist pure SVG, kein D3)
- Hash-basiertes Routing (`#/member/id`, `#/topic/id`, `#/?tags=...`, etc.)
- Lokaler Webserver zum Testen: `npx serve`
- Tests: `node --test "tests/*.test.mjs"` (ohne Abhängigkeit)
- Nach jeder Änderung an CSS oder JS: `python scripts/stamp_assets.py`
- Single-page App: `index.html` + `js/core.js` + `js/app.js` + `js/parliament.js` + `css/style.css`
- `js/core.js` (`Council`): geteilte Perioden- & Vote-Status-Logik für app.js und parliament.js, siehe `docs/CORE.md`
- Fonts self-hosted in `fonts/` (DSGVO: keine CDN-Requests), eingebunden über `css/fonts.css`

## Datenquellen

### Aktuell: Statische JSON-Dateien
- `data/members.json` — Mitglieder mit `mandates` (Zeitraum, Fraktion, Rolle je Abschnitt) und `succeeds`
- `data/parties.json` — Fraktionen und beide Sitzordnungen (Halbrund und physischer Kreis)
- `data/bodies.json` — Gremien mit `seatConfigs`
- `data/media.json` — Medien
- `data/topics.json` — Themen mit Timeline-History
- `data/sessions.json` — das vollständige Sitzungsregister: auch Sitzungen ohne Niederschrift und angekündigte, mit `niederschrift` und Zeiten
- `data/votes.json` — Abstimmungen; `source` für den Beschluss, `voters` für die einzelne Stimme, kein eigenes Datum
- `data/tags.json` — Themen-Tags
- `data/press.json` — Presseartikel als eigenständige Entitäten (ID-Format: `{media}_{YYYY-MM-DD}_{slug}`)

Die Form steht als JSON Schema in `data/schema/`; `python scripts/validate_data.py`
prüft dagegen und zusätzlich den Zusammenhang zwischen den Dateien
(`pip install -r scripts/requirements.txt`).

### Bilder
- `img/topics/` — Bilder für Themen-Timelines, referenziert über `image`-Feld in topics.json

### Geplant: OParl API
- Standardisierte REST/JSON-Schnittstelle für Ratsinformationssysteme
- Anonymer, lesender Zugriff auf Sitzungs-, Gremien- und Dokumentendaten
- Referenzdoku: `quellen/knowledge/oparl-api.md`
- Schrittweise Integration: OParl-Daten ersetzen nach und nach hardcoded JSON
- Mapping: OParl-Objekttypen → lokale Datenstrukturen (siehe `quellen/knowledge/data-mapping.md`)

### Nicht im Repo: `quellen/`
Rohquellen und Arbeitsnotizen liegen in `quellen/` und sind in der `.gitignore`.
GitHub Pages liefert das Repo roh aus — was hier eingecheckt ist, ist öffentlich.
Darin: `knowledge/` (themenübergreifendes Wissen, Quellenverweise, OParl-Doku),
`crawl/` (Presserecherche im Rohzustand). Eingepflegt wird nach `data/*.json`,
und die sind die Auskunft. Methodik gehört erklärt, aber als Text in der App —
nicht als Rohfassung im Repo.
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

Maßgeblich ist `docs/formsprache-probe/ERGEBNIS.md`; der Farbkanon liegt in
`../moosburg-design/css/theme.css` und kommt über `node scripts/hole-tokens.mjs`
als `css/tokens.css` herein — dort nichts von Hand ändern.

- Gedecktes Wappenrot, Gold als Akzent, Regenbogen für die Nebenfarben. **Keine
  Verläufe.**
- Source Serif 4 für Titel, Atkinson Hyperlegible Next für Text, Madelon Script
  für die Handschrift. Self-hosted in `fonts/` (DSGVO), eingebunden über
  `css/fonts.css`.
- Keine Versalien, keine einseitige Farbkante an Karten (siehe PLATTFORM.md).
- Ein Aufklapp-Muster im Haus: `<details>` mit `+`/`–` rechts.
- Heller, freundlicher Look, einheitlich über die ganze Plattform
- Wiederkehrende Elemente (Chips, Badges, Cards, Links) konsistent gestalten
- Informationsdichte balancieren: Details versteckt oder auf eigenen Seiten
- Nicht alles muss auf den ersten Blick sichtbar sein
- Parteien haben eigene Farben, die durchgängig verwendet werden

## Code-Stil

- Code darf nicht LLM-generiert wirken
- Kommentare minimal und natürlich halten
- Keine unnötigen Abstraktionen oder Utilities für einmalige Operationen
- Keine Docstrings oder Type-Annotations wo nicht nötig

## Konfiguration

- `const SHOW_PRONOUNS = true/false` in `js/app.js` — Pronomen ein-/ausblenden
