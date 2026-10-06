# Briefing: Refactoring für einen seriöseren Auftritt

*Angelegt am 06.10.2026, Stand des Befunds: Commit `ff33dd1`. Status: **offen, noch
nichts umgesetzt.***

Ziel: Die App soll ruhig, seriös und professionell wirken, in der Oberfläche wie im Code
und in den Daten. Dieses Briefing ist so geschrieben, dass eine neue Sitzung ohne Vorwissen
loslegen kann: zuerst die Abschnitte 1 bis 3 ganz lesen, dann die Arbeitspakete der Reihe
nach. Jedes Arbeitspaket endet mit einer Abnahme; erst wenn sie erfüllt ist, kommt das
nächste.

Die Zahlen im Befund sind am 06.10.2026 gemessen. Vor jedem Arbeitspaket gegenprüfen, der
Bestand wächst weiter.

---

## 1. Rahmen

### Quellen, in dieser Reihenfolge lesen

| Quelle | Wozu |
|---|---|
| `CLAUDE.md`, `~/.claude/CLAUDE.md` | Arbeitsweise: chirurgische Änderungen, keine Abstraktion auf Vorrat, Abhängigkeiten nach `hausbasis/baseline.json`, keine Erwähnung von KI in Commits und Code. |
| `docs/formsprache-probe/ERGEBNIS.md` | Die geltende Formsprache. **Maßgeblich** für alles Optische. |
| `../moosburg-design/css/theme.css` | Kanon der Tokens. `css/tokens.css` ist nur eine erzeugte Kopie. |
| `docs/MODULE.md`, `docs/CORE.md` | Modul-Schnitt und Vote-Status-Logik. |
| `PLATTFORM.md` | Zwei Auslieferungen (GitHub Pages, moosburg.eu), Deploy-Ausschlüsse, relative Pfade. |
| `OFFENE-PUNKTE.md` | Bekannte Schulden, teils hier aufgegriffen. |
| `.claude/skills/*/SKILL.md` | Die Pflege-Abläufe. Sie beschreiben das Datenformat und müssen mitziehen, wenn es sich ändert. |

### Nicht verhandelbar

- **Daten bleiben inhaltlich gleich.** Umbauten am Format sind verlustfrei. Für jede
  Migration gilt: Vor und nach dem Umbau liefert `Council.voteStatus` für jedes Paar aus
  Mitglied und Abstimmung dasselbe, und jede Route zeigt dieselben Zahlen (Ausnahme: AP 3
  korrigiert widersprüchliche Zählungen absichtlich).
- **Die Niederschrift hat Vorrang.** Reihenfolge und Benennung nur aus der Niederschrift,
  ohne sie keine Stimmen eintragen. Am Bestand der Stimmen ändert dieses Refactoring nichts.
- **Kein Build-Step, keine Laufzeit-Abhängigkeit.** Vanilla JS als ES-Module, Pfade
  relativ.
- **Formsprache bleibt.** Abweichungen nur mit Begründung und Rückfrage.
- **Skills mitziehen.** Ändert ein Arbeitspaket das Datenformat, werden die betroffenen
  Skills im selben Schritt angepasst.

## 2. Entscheidungen von Benedict (06.10.2026)

| Frage | Entscheidung |
|---|---|
| Identitätsmerkmale (`profile.identity`) und Pronomen | Bleiben, aber **nur mit belegter Selbstauskunft**. Die Quelle steht im Datensatz; was sich nicht belegen lässt, fällt weg. Hintergrund: Herkunft und sexuelle Orientierung sind besondere Kategorien nach Art. 9 DSGVO. |
| Kontakt-Icons auf Profilen | Bleiben in ihren Markenfarben, als begründete Ausnahme vom Kanon. |
| Illustrierte Porträts | Bleiben vorerst. Nur die Überlappung von Bild und Name auf dem Handy wird behoben. |
| `img/members/originals/` (167 MB PNG) | Bleiben lokal, kommen aus dem Repo (`.gitignore`, `git rm --cached`). Die Historie wird **nicht** umgeschrieben. |
| Datenfelder | Erst nur vereinheitlichen. Die Umbenennung nach OParl ist ein späterer Schritt (Abschnitt 6). |

## 3. Befund

### Was der Seriosität am meisten schadet

1. **Widersprüchliche Zahlen.** Startseite: „173 Sitzungen, 135 von 175 mit
   Niederschrift“. Datenlage: „117 / 175“. Statistik: „175 Sitzungen, 172 davon mit
   Dauer“. Ursache: zwei Register (`sessions.json` und `sessionlengths.json`) und drei
   Zählstellen mit verschiedener Definition (`views/themen.js` Z. 19 und 40,
   `views/statistik.js` Z. 100 und 238). `sessions.json` zählt Sitzungen mit bloßem
   Beschlussauszug als „mit Niederschrift“.
2. **Identitätsangaben ohne Beleg.** 12 Personen tragen `identity`, 44 `pronouns`. Keine
   Angabe nennt eine Quelle. Auffällig: Banner und Bauer haben FLINTA, aber keine Pronomen.
3. **Rohquellen sind öffentlich.** `data/vote_tracking/*.zip` und
   `data/antraege/*.pdf` liefert moosburg.eu aus (HTTP 200 am 06.10.2026), ebenso GitHub
   Pages, und das Repo ist öffentlich. **Jede der fünf getrackten ZIPs enthält eine
   `nichtoeffentlich.json`** (4 bis 5 KB, Inhalt nicht geöffnet), vermutlich Notizen aus
   nichtöffentlichen Sitzungsteilen. Das berührt die Verschwiegenheitspflicht (Art. 20
   GO Bayern). **Am 06.10.2026 erledigt:** Rohdaten des Vote-Trackings liegen nur noch
   lokal (Entscheidung Benedict), `data/vote_tracking/` steht in der `.gitignore`, die
   eingepflegten Stimmen bleiben in `votes.json`. In der Git-Historie sind die ZIPs noch
   abrufbar; ob sie bereinigt wird, ist offen (Abschnitt 5). Die untrackte
   `data/Strobl eigene Protokolle Stadtrat.docx` ginge mit einem `git add .` ebenfalls
   online.
4. **Entwicklermeldung in der Oberfläche.** Laden die Daten nicht, steht dort „Bitte mit
   einem lokalen Webserver öffnen (z.B. `npx serve`)“, per Inline-Style (`js/app.js`).
5. **Kalender:** Die nächste Sitzung steht im Kasten, ist im Monatsraster aber nicht
   markiert. Das Raster liest nur `sessions.json`, nicht `termine.json`.

### Oberfläche

- Über 30 verschiedene `font-size`-Werte in `css/style.css` (0.72, 0.74, 0.75, 0.78, 0.8,
  0.8125, 0.82 rem …, dazu px). Abstände nicht gezählt, vermutlich ähnlich.
- 39 verschiedene Hex-Farben. `--text-muted: #6F6F6F` liegt neben dem Kanon
  (`--color-ink-muted`). Unbenutzt: `--purple`, `--gap`. Tag-Farben stehen als Hex in
  `data/tags.json`.
- `css/tokens.css` ist vom 16.09. und führt noch Playfair und Inter. Der Kanon hat seit
  26.09. Source Serif 4 und Atkinson Hyperlegible Next; `style.css` überschreibt die
  Schrift-Tokens lokal.
- Suche und Themen-Chips stehen auf jeder Seite, auch auf Sitzung, Statistik und
  Datenlage.
- Statistik, Datenlage und Presseschau hängen unter dem Tab „Themen“.
- Jeder Tagesordnungspunkt ist eine Karte, darin der Abstimmungsblock als zweite Karte.
  Formelle Punkte („Mitteilungen“, „Bürgerfragen“) bekommen eine volle Karte.
- Personenprofil: 21.700 px hoch am Rechner, 28.200 px mobil. Mobil überlappt das Porträt
  Name und Fraktion.
- Kein `document.title` je Route, keine Open-Graph-Angaben.

### Daten

- Herkunft einer Stimme verteilt auf `type`, `source.tier`, `inferable`, `voters`,
  `voterSource`, `voterSourceBy`, `voterEvidence`, `voterHints`. 329 Voten ohne Stufe
  (implizit „nur Ergebnis“).
- `topicId` an Vote, Tagesordnungspunkt und History; `vote.date` dupliziert das
  Sitzungsdatum; Tagesordnungspunkte haben `voteId` **und** `voteIds`.
- `members.json` hält sechs Sammlungen: `parties`, `seatOrder`, `councilOrder`,
  `members`, `bodies`, `media`. Die beiden Sitzordnungen sind **bewusst** zwei (Halbrund
  und physischer Kreis).
- Mandatszeiten in `from`/`to`, `periods`, `partyHistory`, `roleHistory`,
  `profile.committees`, `bodies[].seatConfigs[].occupants`.
- Nachfolge wird heuristisch erkannt (gleiche Fraktion, Eintritt höchstens 31 Tage nach
  Austritt, `drawSimGraph` in `views/naehe.js`). Wer bei Wagner/Altenbeck →
  Kilian Linz/A. Becher wem folgte, steht nirgends.
- `termine.json` enthält ein Prosa-Feld `note`. Feldnamen mischen Englisch und Deutsch
  (`termine`, `figures`, `field`, `voterHints`).
- Beim Start lädt jede Seite alle acht JSON-Dateien, rund 1,3 MB ungepackt. Ob
  moosburg.eu komprimiert, ist nicht geprüft.

### Code

- 97 × `innerHTML` mit Daten, kein Escaping. Harmlos, solange nur eigene JSON-Dateien
  kommen; vor OParl oder Uploads Pflicht.
- `core.js` und `parliament.js` sind klassische Skripte mit Globalen (`Council`,
  `VoteVis`), englisch kommentiert, mit Kasten-Trennern `// ── … ───`.
- `views/naehe.js` 734 Zeilen (Maß, Matrix, Netz in Fläche und Raum),
  `views/statistik.js` 661 (drei Seiten), `views/profil.js` 665.
- Doppelte Logik: Mandats-/Periodenprüfung mindestens dreimal (`Council.memberActiveAt`,
  `initNaehe`, `drawSimGraph`), Sitzungszählung dreimal. 31 Inline-Styles im JS.
- 639 von 5.178 JS-Zeilen sind Kommentare. 32 × „Probe Formsprache, vorläufig“, obwohl
  die Probe abgeschlossen ist. Kommentare als Änderungsprotokoll („Bis August 2026 …“,
  „Früher hingen …“). 90 Gedankenstriche im JS, 36 im CSS. Umschrift „ueber“ neben
  „über“.
- Keine Tests im Repo.

### Ballast

- `.git` 339 MB, davon 167 MB die PNG-Originale.
- Ungenutzt: `img/exampleplacement.png` (9,2 MB), `img/brushstrokeexample.svg`,
  `img/hauptstrasse.svg`, `img/logos/CSU.svg`, `img/logos/Merkur.de_Logo_10.2022.svg`.
  Die übrigen `brushstrokeA*.svg` sind in Gebrauch (`views/profil.js`).
- Zu groß: `img/topics/legal-wall.jpg` (2,2 MB), `fonts/MadelonScript.otf` (kein woff2).
- 38 von 56 Skripten werden nirgends erwähnt, einmalige Importe (`add_*`, `apply_*`,
  `fix_*`, `import_*`, `big_update_2026.py` …). In Gebrauch und zu behalten:
  `validate_data.py`, `build_data.py`, `build_icon_sprite.mjs`, `hole-tokens.mjs`,
  `stamp_assets.py`, `compress_member_images.py`, `crawl/`, und die von Skills oder Doku
  genannten (`selbstauskunft.py`, `offene_stimmen.py`, `anwesenheitsluecken.py`,
  `mark_inferable.py`, `teilanwesenheit.py`, `mandatswechsel_stimmrecht.py`). Vor dem
  Löschen erneut mit `grep` prüfen.
- Veraltete Doku: `CLAUDE.md` („Rot-Gradient“), `README.md` (Projektstruktur, Emoji,
  „D3 nicht mehr benötigt“), `docs/briefing-formsprache.md` (481 Zeilen, erledigt).
  `data/knowledge/project-context.md` (602 Zeilen) sichten.

## 4. Arbeitspakete

Jedes Paket ein eigener Commit (oder wenige), jeweils mit Deploy erst nach Rückfrage.

### AP 0: Sicherheitsnetz

- Vorher-Aufnahmen aller Routen in 1440 und 390 px: `/`, `/feld/sports`, `/topic/t3`,
  `/session/sr_20260720`, `/kalender`, `/gremien`, `/member/gruber`, `/fraktion/csu`,
  `/statistik`, `/datenlage`, `/presse`. Dazu je Route die Seitenhöhe und die
  Konsolenfehler.
- Ein Snapshot der abgeleiteten Daten als JSON: `voteStatus` für alle Paare aus Mitglied
  und Abstimmung, die Zählungen der drei Übersichtsseiten, die Nähe-Werte je Periode.
  Spätere Pakete vergleichen dagegen.
- Unit-Tests mit `node --test` (keine Abhängigkeit) für Ähnlichkeitsmaß, `voteStatus`,
  Periodenlogik und Nachfolge-Erkennung.
- Werkzeug: lokaler Server `python -m http.server 8765`, Playwright aus
  `../etymology/node_modules/playwright` mit dem installierten Chrome
  (`executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe"`).
  Playwright kommt **nicht** ins Repo (Entscheidung 06.10.2026). Die Prüfskripte vom
  06.10. lagen nur in einem Sitzungs-Scratchpad und sind neu zu schreiben, außerhalb des
  Repos. Erst wenn das Ausleihen bricht, als Dev-Abhängigkeit mit der Version aus
  `hausbasis/baseline.json`.

**Abnahme:** Aufnahmen und Snapshot liegen außerhalb von `data/`, Tests grün.

### AP 1: Rechtliches und Öffentliches

- Identität und Pronomen: Für jede Angabe die Selbstauskunft suchen und als Quelle
  eintragen, Format etwa `"identity": {"values": ["flinta"], "source": "selbstauskunft",
  "date": "…"}`. Unbelegtes Benedict vorlegen, nicht eigenmächtig löschen. Validator
  lehnt Angaben ohne Quelle ab. `views/profil.js` liest das neue Format.
- Rohquellen: `quellen/` neben `data/` anlegen, vom Deploy ausgeschlossen
  (`.github/workflows/moosburg-eu.yml`, `PLATTFORM.md`). Welche Dateien öffentlich
  bleiben dürfen (Mitschriften-ZIPs, Antrags-PDF), entscheidet Benedict. Was nicht
  öffentlich sein soll, muss auch aus dem Repo, denn GitHub Pages liefert alles aus. Die
  Historie bleibt dabei öffentlich, außer sie wird umgeschrieben.
- `.gitignore` gegen versehentliches Einchecken (`data/*.docx`).
- Fehlermeldung beim Laden: für die Öffentlichkeit formulieren, Klasse statt Inline-Style.

**Abnahme:** Die Pfade aus dem Befund liefern auf moosburg.eu 404 oder sind bewusst
freigegeben; jedes Profil zeigt nur belegte Angaben.

### AP 2: Aufräumen

- `img/members/originals/` in die `.gitignore`, `git rm -r --cached`, Dateien bleiben
  lokal. Deploy-Ausschluss dafür entfernen, `PLATTFORM.md` nachziehen.
- Ungenutzte Bilder löschen, `legal-wall.jpg` als WebP, Madelon Script als woff2.
- Einmalige Skripte löschen (die Historie behält sie).
- `node scripts/hole-tokens.mjs`, danach die lokalen Schrift-Überschreibungen in
  `style.css` entfernen, soweit der Kanon sie abdeckt.
- Doku: `CLAUDE.md` und `README.md` aktualisieren, `docs/briefing-formsprache.md` nach
  `docs/archiv/`.
- Kalender-Bug: `termine.json` im Monatsraster markieren (wird mit AP 3 hinfällig, falls
  AP 3 direkt folgt).

**Achtung beim Löschen von Ordnern:** Die FTP-Deploy-Action (v4.3.5) adressiert zu
löschende Ordner absolut (`/stadtrat/…`) und scheitert mit `550 No such file or
directory`. Der Lauf bricht ab, ohne seinen Sync-Stand zu speichern, und jeder weitere
Deploy scheitert an derselben Stelle. Am 06.10.2026 so geschehen mit
`data/vote_tracking/`; behoben mit einem einmaligen Workflow, der per `curl` relativ zum
FTP-Login löscht (`DELE`, `RMD`) und `stadtrat/.ftp-deploy-sync-state.json` entfernt
(Commit `2b336a3`, danach wieder gelöscht). Wer in AP 2 einen ganzen Ordner aus dem
ausgelieferten Bestand nimmt, plant das ein oder behebt die Ursache im Workflow. Auf dem
Server liegen außerdem leere Ordner `data/knowledge/` und `data/docs/`.

**Abnahme:** alle Routen ohne 404 und ohne Konsolenfehler, Aufnahmen gleich zu AP 0.

### AP 3: Ein Sitzungsregister

- `sessions.json` wird das vollständige Register, auch für Sitzungen ohne Niederschrift:
  `niederschrift: "vollständig" | "auszug" | "keine"`, `status: "angekündigt" |
  "gehalten"`, `start`/`end` aus `sessionlengths.json`, Termine aus `termine.json`.
  Danach entfallen `sessionlengths.json` und `termine.json`.
- Eine Zählstelle in `daten.js`; Startseite, Statistik und Datenlage lesen nur von dort.
- Skills `niederschrift-einarbeiten`, `validate-data`, `build-data` anpassen.

**Abnahme:** Die drei Seiten nennen dieselben Zahlen, mit einer Definition, die auf der
Seite steht. Die nächste Sitzung erscheint im Kalenderraster.

### AP 4: Datenmodell vereinheitlichen

- Herkunft: ein `source`-Objekt mit Stufe, Urheber, Belegen; Stufe immer explizit.
- `voteIds` immer als Liste. Für jede Verknüpfung festlegen, wo sie gepflegt wird; die
  Gegenrichtung baut `daten.js` beim Laden oder der Validator prüft sie. `vote.date`
  ableiten.
- `members.json` teilen in `members.json`, `parties.json` (mit beiden Sitzordnungen),
  `bodies.json`, `media.json`.
- Mandate als `mandates: [{from, to, party}]`, Nachfolge explizit als `succeeds`
  (ersetzt die Heuristik in `views/naehe.js`). Wagner und Altenbeck schieden
  gleichzeitig aus; auf Altenbeck folgte, wer von Kilian Linz und A. Becher auf der
  Liste 2020 weiter oben stand, auf Wagner der andere. Die Rangfolge 2020 liegt nicht
  vor (in `profile.elections` steht nur 2026). Bis sie bekannt ist, bleibt es bei den
  vier Kreuzpaaren; laut Benedict ist die Zuordnung für das Nähe-Netz fast egal.
- Feldnamen einheitlich (Englisch, wie die Mehrheit), Prosa aus den Daten.
- JSON-Schema je Datei, `validate_data.py` prüft dagegen.
- Alle Skills nachziehen, besonders `member-update` und `niederschrift-einarbeiten`.

**Abnahme:** Validator grün, Daten-Snapshot identisch zu AP 0, Aufnahmen gleich.

### AP 5: Code

- `html`-Tagged-Template mit Escaping, die 97 Stellen umstellen.
- `core.js` und `parliament.js` als ES-Module; `docs/MODULE.md` und `docs/CORE.md`
  anpassen.
- Schnitte: `naehe.js` in Maß und Zeichnen, `statistik.js` in drei Seiten, `profil.js`
  nach der Gliederung aus AP 6.
- Doppelte Logik zusammenführen (Perioden, Mandate, Zählungen), Inline-Styles zu
  Klassen.
- Kommentare: nur das Warum, meist ein bis zwei Zeilen. Datierte Probe-Vermerke und
  Änderungsgeschichte raus, die gehört in Commits. Deutsch mit Umlauten; Bezeichner nur
  umbenennen, wo ohnehin angefasst. Kasten-Trenner und gehäufte Gedankenstriche weg.

**Abnahme:** Tests grün, Daten-Snapshot identisch, Aufnahmen gleich.

### AP 6: Oberfläche

- Typo-Skala mit sechs bis sieben Stufen als Token, Abstandsskala ebenso, alle Werte
  ersetzen.
- Farben: jede aus dem Kanon oder mit einem Satz begründet. `--text-muted` auf
  `--color-ink-muted` oder begründen. Tag-Farben aus den Daten in Tokens. Ausnahme
  Kontakt-Icons (Markenfarben) festhalten.
- Seitenköpfe nach Typ: Übersichten mit Suche und Chips, Detailseiten mit Zurück,
  Brotkrume, Titel; Suche dort als Icon.
- Statistik, Datenlage, Presseschau in einen Bereich „Daten & Methodik“ unter „Über das
  Projekt“; Methodik-Texte dorthin, unter Diagrammen eine Zeile.
- Weniger Karten: keine Karte in der Karte, formelle Tagesordnungspunkte als
  eingeklappte Zeile, dichte Daten als Liste mit Linien.
- Profil gliedern: Kerndaten und Mandate oben, Abstimmungen, Anträge, Ähnlichkeit
  eingeklappt oder als Unterseiten. Überlappung von Porträt und Name mobil beheben.
- `document.title` je Route, Open-Graph-Angaben.
- Barrierefreiheit: Dialoge (Rolle, Fokusfalle), Fokus-Ringe, Kontrast prüfen.
- Die Handschrift hinter den Titeln bleibt auf allen drei Übersichten (Entscheidung
  06.10.2026).

**Abnahme:** Vorher-Nachher-Vergleich mit Benedict durchgesehen, Profil unter 3.000 px im
Ausgangszustand, kein waagrechter Überlauf bei 390 px, keine Konsolenfehler.

## 5. Offene Fragen an Benedict

1. Dürfen Antrags-PDF (`data/antraege/`) und Arbeitsnotizen (`data/knowledge/`,
   `data/crawl/BERICHT.md`, `data/seating-proposal.md`) öffentlich bleiben? Die
   Mitschriften-ZIPs sind entschieden (nur lokal).
2. Git-Historie umschreiben, um die ZIPs aus alten Commits zu entfernen (dann auch die
   PNG-Originale), oder hinnehmen?

## 6. Später: OParl

Nicht Teil dieses Refactorings, aber die Richtung für die Feldnamen nach AP 4:

| Heute | OParl |
|---|---|
| `session` | `Meeting` |
| Tagesordnungspunkt (`agenda`) | `AgendaItem` |
| `member` | `Person` |
| Mandat (`mandates`) | `Membership` |
| `body` | `Organization` |
| Antrag (`profile.motions`) | `Paper` |

Details und Zuordnung in `data/knowledge/data-mapping.md` und
`data/knowledge/oparl-api.md`. Vor der Umbenennung muss AP 5 (Escaping) stehen.
