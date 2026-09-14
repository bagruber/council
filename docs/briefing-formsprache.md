# Briefing: Formsprache-Probe im Stadtrat

*Angelegt am 14.09.2026. Status: **Probe, nicht freigegeben.** Alles hier setzt
vorläufige Entscheidungen um; nichts davon ist Kanon.*

Dieses Briefing beschreibt, wie die Stadtratstransparenz (`moosburg.eu/stadtrat/`)
probeweise auf die neue Formsprache umgestellt wird. Es ist so geschrieben, dass eine neue
Sitzung ohne Vorwissen loslegen kann: zuerst die Abschnitte 1 bis 3 ganz lesen, dann die
Arbeitspakete der Reihe nach.

**Reihenfolge.** Nach dem Haushalt kommt zuerst die Portalseite
(`../moosburg-eu/docs/briefing-formsprache-portal.md`), dann dieses Projekt, dann der Data
Hub. Die Portal-Probe klärt, wie Schriften und Icons ohne Build-Step eingebunden werden;
ihr Ergebnis (`../moosburg-eu/docs/formsprache-probe/ERGEBNIS.md`, Abschnitt „Ohne
Build-Step gelernt“) vor AP 1 lesen. Liegt es noch nicht vor, klärt AP 1 das selbst.

---

## 1. Worum es geht

In zwei Vorschlagsrunden (11. und 14.09.2026) ist für alle Moosburg-Projekte eine
einheitlichere Formsprache entstanden. Am 14.09.2026 hat Benedict **vorläufige
Entscheidungen** getroffen, haushaltvis hat sie als Erstes erprobt. Der Stadtrat ist die
dichteste App der Familie. Hier zeigt sich, ob Kategoriezeile, Chip-Zeile, Tab-Leiste und
Familien-Navigation auch unter hoher Informationsdichte tragen.

Der Stadtrat gehört zum **Werkzeug-Profil** (`../moosburg-design/README.md`): dichter und
schlichter als ein Auftritt ist erlaubt, fremd aussehen darf er nicht. Wo eine Entscheidung
die Bedienung verschlechtert, gilt das Profil, und die Abweichung wird begründet.

### Quellen, in dieser Reihenfolge lesen

| Quelle | Wozu |
|---|---|
| `../moosburg-design/docs/formsprache/ENTSCHEIDUNGEN.md` | Das Protokoll; Abschnitt 4 hat alle Werte. **Maßgeblich**, falls Briefing und Protokoll auseinanderlaufen. |
| `../haushaltvis/docs/formsprache-probe/ERGEBNIS.md` | Erste Probe: was trug, was nicht, Benedicts Rückmeldung. |
| Vorschlagsseite: https://claude.ai/code/artifact/764bc923-36f6-4751-8e8e-01eddec5c826 | Abschnitt „Suche, Filter, Tabs, Titel“ zeigt den **Stadtrat mobil in 340 px** (App-Leiste, großer Titel, Suche, Chip-Zeile mit „Alle Themen“, Einträge mit Kategoriezeile, Tab-Leiste). Dazu „Navigation für die Familie“ und „Kategorien“. |
| `../moosburg-design/docs/formsprache/artefakt/template.html` | Markup und CSS des Handys: `.appbar`, `.chiprow`, `.chip`, `.pentry`, `.pcat`, `.tabbar`, `.pill`; dazu `.klecks`, `.nav-row`, `.about`. Vorlage für reines CSS. |
| `../moosburg-design/docs/formsprache/artefakt/icons.json` | Phosphor-Icons als Pfaddaten. |
| Branch `probe/formsprache` in `../haushaltvis`: `src/components/Header.tsx`, `src/components/ui.tsx`, `src/lib/kategorien.ts`, `src/lib/colors.ts` | Disclosure „Über das Projekt“, Tab-Leiste, Klecks, Kategorie-Töne, gebaut und geprüft. |
| `CLAUDE.md`, `PLATTFORM.md` (Abschnitt Gestaltung), `docs/MODULE.md`, `OFFENE-PUNKTE.md` | Stack, erlaubte Kanten, Aufklapp-Muster, Rangfolge der Startseite, Modul-Regeln, die Farbe neben dem Kanon. |

## 2. Die Entscheidungen, übersetzt in den Stadtrat

| Entscheidung (14.09.2026) | Heute im Stadtrat | AP |
|---|---|---|
| Schriften Source Serif 4, Atkinson Hyperlegible Next, Madelon Script | Playfair und Inter in `fonts/`; 18 fest eingetragene `font-family` in `css/style.css` | 1 |
| Icon-Set Phosphor (für den Stadtrat vorläufig am 14.09.2026) | Lucide-Sprite in `index.html`, IDs mit Material-Namen | 1 |
| Kaum Versalien | 26 × `text-transform: uppercase` | 2 |
| Kategorien, Variante C | zehn Themen aus `data/tags.json` als `.cat-chip` | 3 |
| Chips als scrollbare Zeile mit „Alle Themen“ (Versuch); einheitliche Suche | zehn `.tag-pill` in bis zu vier Zeilen im farbigen Kopf; Suchfeld mit 4 px | 4 |
| Seitenköpfe, Überlappung Variante 1 | farbiger Kopf je Bereich (`--chrome`), keine Handschrift | 5 |
| Navigation Variante A; Tab-Leiste unten bis 1024 px | Kopf nur mit Logo; Tab-Leiste unten auf allen Breiten, am Desktop über die volle Breite | 6 |
| Farbflächen | keine; Vorschlag der Vorschlagsseite: nächste Sitzung | 7 |
| Ecken 4 und 10 px; Zahlen; kein einseitiger Kantenakzent | 20 feste px-Radien, `--radius` 4 px; drei Kanten-Fundstellen | 8 |
| Status: Rose | **nicht anwendbar**, siehe Abschnitt 3 | keins |

**Nicht Teil der Probe:** Dunkelmodus; das Sitzungstool (`council-voting-tool`, eigener
Kompromiss); Form und Farbe von Parlamentsgrafik, Nähe-Netz und Diagrammen; Partei-,
Abstimmungs- und Gremienfarben; alles unter `data/` und `scripts/`; OParl.

## 3. Rahmen, der nicht verhandelbar ist

**Ablauf: lokal prüfen, nach Freigabe direkt mergen** (Benedict, 14.09.2026). Gearbeitet
wird auf `probe/formsprache`. Eine öffentliche Vorschau gibt es nicht und ist nicht
vorgesehen; geprüft wird lokal mit `npx serve` im Repo-Stamm (siehe `CLAUDE.md`). Nach
Benedicts Freigabe wird der Branch in `main` gemergt und gepusht. Damit ist die Probe
live: `main` wird von GitHub Pages roh ausgeliefert und über
`.github/workflows/moosburg-eu.yml` nach `/stadtrat/` gespiegelt. Alle Projekte teilen ein
FTP-Konto, deshalb den Lauf abwarten, bevor ein anderes Repo pusht. Kleine Commits je
Arbeitspaket, deutsche Commit-Nachrichten, **ohne jeden Hinweis auf KI-Unterstützung**.

**Fremde Dateien.** Am 14.09. lagen `data/vote_tracking/protokoll-2026-07-13_bpu.zip` und
`protokoll-2026-09-07_plenum.zip` unversioniert im Repo. Sie gehören nicht zur Probe und
in keinen ihrer Commits.

**Cache-Busting.** `index.html` lädt CSS und Module mit `?v=`-Stempel, auch in der
Importmap. Nach jeder Änderung an CSS oder JS vor dem Commit `python
scripts/stamp_assets.py` laufen lassen, sonst mischen Browser alte und neue Dateien.

**Kanon nicht anfassen.** `css/tokens.css` ist eine erzeugte Kopie
(`scripts/hole-tokens.mjs`) und wird nie editiert. Abweichungen stehen im `:root`-Block von
`css/style.css`, jede mit dem Kommentar `/* Probe Formsprache, vorläufig (14.09.2026): … */`.
Neue Schriften kommen in `css/fonts.css`.

**Module.** Die Regeln aus `docs/MODULE.md` gelten: importierte Daten nie beim Laden eines
Moduls lesen, nur in Funktionen; neue Verdrahtung in init-Funktionen. Neue
Verantwortlichkeiten in die Tabelle dort eintragen.

**CSP.** Die Domain setzt `script-src 'self'` und `style-src 'self' 'unsafe-inline'`. Kein
Inline-Skript; Schriften nur selbst gehostet.

**Rot im Stadtrat.** Anders als im Haushalt heißt Rot hier nicht Defizit. Aber `--no`
(`#9B0000`) ist das Rot der Ablehnung, und `style.css:26-27` hält fest, dass es sich bewusst
vom Rot der Links unterscheidet. Aktive Zustände nach der Vorschlagsseite in `red-700`
bauen, dann gegen Tinte als Screenshot-Paar vorlegen: Liest sich ein gewählter Chip wie
eine Ablehnung?

**Keine Rose als Status.** Die Rose markiert Projektzustände (online, Vorschau, Archiv). Die
Marken im Stadtrat (Abstimmungsergebnis, Herkunft der Stimmen, Befangenheit) sind
Datenzustände. Sie bekommen keine Rose, genau wie „(nur Plan)“ im Haushalt.

**Texte, die dem Portal widersprechen.** Die Einstellungen nennen die App
„Ratsinformationssystem der Stadt Moosburg a.d. Isar“ (`index.html:123`), der Kontakt
verweist an „die Geschäftsstelle des Stadtrats“ (`index.html:327`). Das Portal betont „kein
Auftritt der Stadt“. Dieselbe Frage steht für die Fußzeile des Data Hub offen. Texte dazu
entstehen in AP 6 als Vorschlag, nichts ohne Benedict ändern.

**Textstimme.** Neuer sichtbarer Text ohne Gedankenstriche; Zahlenbereiche behalten den
Halbgeviertstrich. Bestehende Texte nicht flächendeckend umschreiben (`index.html` hat
einige). Neue Texte vorher zeigen.

**Barrierefreiheit halten.** Die Einstellungen „Größere Schrift“ und „Farbenblind-sichere
Farben“ müssen nach jedem Paket funktionieren. Dazu Tastatur in Tabs, Suche, Modals und
Kalender-Blatt, sichtbarer Fokus, `prefers-reduced-motion` (`style.css:577`).

**Zählung.** `js/routing.js` meldet Routenwechsel an `window.zaehl`. Bleibt unverändert.

---

## 4. Arbeitspakete

Zeilennummern vom Stand `f473fd8`.

### AP 0: Vorbereitung und Vorher-Stand

1. `git status`, dann `git switch -c probe/formsprache` von `main`.
2. `npx serve`, alle Routen einmal mit offener Konsole öffnen: keine Fehler.
3. **Vorher-Screenshots** in 1440 und 390 px, IDs aus den Dateien in `data/` wählen:
   - `#/`, `#/?tags=mobility`, `#/feld/building`
   - ein Dossier `#/topic/…` mit Zeitstrahl, eine Sitzung `#/session/…` mit Tagesordnung
   - `#/statistik`, `#/datenlage`, `#/presse`
   - `#/kalender` mit geöffnetem Tages-Blatt
   - `#/gremien`, ein Profil `#/member/…`, eine Fraktion `#/fraktion/…`
   - `#/einstellungen`, das Legenden-Modal
   - `#/` und das Dossier zusätzlich mit „Größere Schrift“

   Ablage `docs/formsprache-probe/vorher/`, per `.git/info/exclude` ausgenommen. Für 390 px
   Playwright mit `viewport`.

**Prüfung:** Screenshots vollständig, Konsole ohne Fehler.

### AP 1: Schriften und Icons

**Icons: Phosphor** (Benedict, 14.09.2026, vorläufig). Heute baut
`scripts/build_icon_sprite.mjs` ein Sprite aus Lucide; die Quelle ist fest auf
`../pridemap/node_modules/lucide-react` eingetragen, die Symbol-IDs tragen noch
Material-Namen (`i-how_to_vote`).

- **Mechanismus bleibt:** ein Inline-Sprite in `index.html`, die IDs bleiben, damit kein JS
  angefasst wird. Nur die Zeichnungen wechseln. Keine neue Dependency ins Repo, das
  Frontend läuft bewusst ohne Build.
- **Woher die Pfade kommen:** `../moosburg-design/docs/formsprache/artefakt/icons.json`
  enthält nur die Icons der Vorschlagsseite. Wie sie gewonnen wurden, steht in
  `artefakt/README.md` und `build.mjs`; denselben Weg für die Stadtrat-Icons nehmen.
- **Gewicht `regular`**, wie im Stadt-Prototyp (421 von 506 gesetzten Gewichten).
- **Zuordnung:** In der Tabelle `MAP` des Skripts wird aus „Material-Name → Lucide-Name“
  „Material-Name → Phosphor-Name“. Wo der Stadt-Prototyp oder der Haushalt dieselbe
  Bedeutung schon mit einem Phosphor-Icon zeigen, dieses nehmen, zum Beispiel
  `account_balance` `Bank`, `calendar_month` `CalendarDots`, `open_in_new`
  `ArrowSquareOut`, `search` `MagnifyingGlass`, `groups` `UsersThree`, `schedule` `Clock`,
  `email` `Envelope`, `description` `FileText`, `school` `GraduationCap`, `commute` `Bus`,
  `park` `Tree`, `insights` `ChartLineUp`, `settings` `GearSix`.
- **Ohne klares Gegenstück** sind die Symbole für Merkmale und Funktionen (`queer`,
  `flinta`, `migrant`, `disability`, `referent`, `ausschuss`, `vorsitz`, `aufsichtsrat`).
  Dafür eine Vorschlagsliste mit Screenshot vorlegen, nicht selbst festlegen.
- `.icon` (`style.css:145-154`) setzt heute `stroke: currentColor` und `fill: none`.
  Phosphor-Pfade sind gefüllt: auf `fill: currentColor` umstellen und prüfen, dass kein
  anderes SVG mit der Klasse `.icon` davon betroffen ist.

**Prüfung Icons:** Jede ID im Sprite hat eine Phosphor-Zeichnung, keine leere Stelle in
Tabs, Suche, Modals, Themen-Chips und Profilen.

Das Protokoll nannte in Abschnitt 7 bis 14.09. „Material Symbols“; das war veraltet und ist
korrigiert.

**Schritt 1, reiner Umbau ohne Sichtänderung.** Die 18 Stellen mit
`font-family: 'Inter', …` bzw. `'Playfair Display', …` in `style.css` auf
`var(--font-sans)` bzw. `var(--font-display)` umstellen. Eigener Commit. **Prüfung:**
Screenshots aus AP 0 bleiben gleich. Warum zuerst: Danach ist der Schriftwechsel eine Zeile,
und jede Veränderung in Schritt 2 lässt sich eindeutig der Schrift zuordnen.

**Schritt 2, Schriften wechseln.**

- Dateien nach `fonts/` kopieren, Quelle wie im Portal-Briefing, AP 1 (Fontsource 5.3.0,
  Subset `latin`, Source Serif 4 als opsz-Datei, Atkinson wght, Madelon aus
  `../haushaltvis/src/assets/fonts/`). Familiennamen wie in der Haushalt-Probe.
- `@font-face` in `css/fonts.css`, alte Einträge raus, alte Dateien bleiben liegen.
- Im `:root` von `style.css` `--font-display`, `--font-sans`, `--font-script` überschreiben.
- `font-feature-settings: "ss01", "cv11"` am `body` (`style.css:84`) entfernen, die
  Features gehören zu Inter.
- Überschriften bekommen `font-optical-sizing: auto` und `lining-nums`; die bestehende
  `tabular-nums`-Regel (`style.css:93`) wird zu `lining-nums tabular-nums`.
- Die Regel „Titelschrift nie in Datenzellen“ (`style.css:97-98`) bleibt.
- `parliament.js` und die Views setzen keine eigene Schrift; SVG-Text erbt. Prüfen, dass
  Namen in Grafiken mit der breiteren Atkinson nicht überlaufen.

**Prüfung:** gerenderte Schriften nur die drei neuen; „Größere Schrift“ skaliert weiter.

### AP 2: Versalien

**Ist:** 26 × `text-transform: uppercase` in `style.css`, unter anderem `.headline` (99),
`.badge-label` (109), `.nav-logo` (176), `.dd-group` (313), `.dd-type` (355),
`.section-heading` und `.section-label` (483), `.topic-header h1` (505).

**Umsetzung:** Jede Stelle in Satzschreibung, die Sperrung entfällt mit. Je Fundstelle kurz
entscheiden, was sie ist:

- **`.section-label`** („Dossiers“, „Einzelne Beschlüsse“, „Alle Themen“) steht laut
  Kommentar für sich als Überschrift. Wird eine kleine Überschrift in der Titelschrift,
  etwa 1,25 rem, Gewicht 600.
- **`.dd-group`** (Gruppen in der Suche) behält Icon und Farbe, 13 px, 600.
- **`.badge-label`** (Ergebnis-Marken) behält Gewicht und Dichte, nur ohne Versalien. Der
  Stempel-Status mit Versalien ist nicht gewählt.
- Seitentitel ebenfalls in Satzschreibung. Versalien wären dort erlaubt, aber nur als
  seltene Ausnahme; im Stadtrat gibt es keinen Grund dafür.

**Prüfung:** `grep -n "uppercase" css/style.css` ohne unkommentierte Treffer.

### AP 3: Kategorien, Variante C

**Ist:** `data/tags.json` führt zehn Themen mit `name`, `icon` und `color`.
`categoryChip()` (`js/views/themen.js:85`) rendert sie als `.cat-chip` (`style.css:453`):
Pille mit 12 % Tönung, 0,66 rem.

**Soll:**

- **Kategoriezeile** statt Pille: Icon 16 px plus Name 14 px, 600, Satzschreibung, ohne
  Hintergrund. In der Themenliste eine Zeile mit allen Themen des Dossiers, wie `.pcat` im
  Handy der Vorschlagsseite.
- **Unterschied zum Klären:** Das Protokoll setzt den Text in die Kategoriefarbe, das Handy
  der Vorschlagsseite färbt nur das Icon. Bei zwei oder drei Themen je Karte wird eine bunte
  Zeile unruhig. Beides bauen, als Paar vorlegen.
- **Klecks** (46 px) nur in den Köpfen von Themenfeld (`renderField`, `#/feld/…`) und
  Dossier (`renderTopic`, erstes Thema), nie in Listen.
- **Töne.** Die Themenfarben stehen nicht im Kanon (`#5B9BD5`, `#8B7355`, `#F57C00` …).
  Icon und Text bekommen einen dunklen Ton, der Klecks einen hellen, nach derselben Formel
  wie im Haushalt (`tint(farbe, -0.35)` und `tint(farbe, 0.78)`,
  `../haushaltvis/src/lib/colors.ts`). Kontrast mindestens 4,5:1 **auf Creme und auf Weiß**,
  denn die Themenkarten sind weiß. Wo das nicht reicht, den Wert je Farbe absenken.
- **Wo gerechnet wird:** in einer kleinen Hilfsfunktion in `js/hilfen.js`, zur Laufzeit.
  **Nicht** als neue Felder in `tags.json`: council ist die Datenautorität, andere Repos
  lesen die Dateien, und Anzeige-Werte gehören nicht in den Datenbestand.
- Links bleiben Links (`asLink`, verschachtelte Links in Karten weiterhin vermeiden).
- Prüfen, ob „Farbenblind-sichere Farben“ die Themenfarben verändert, und dass es danach
  noch wirkt.

**Offen, nicht in dieser Probe:** Die Gremien (Stadtrat, BPU, HVFA) sind ebenfalls eine
wiederkehrende Kategorie mit eigener Farbleiter (`style.css:36-49`). Im Ergebnis fragen, ob
sie eine Kategoriezeile bekommen.

**Prüfung:** Kontrasttabelle je Thema im Ergebnis (Farbe, Ton, auf Creme, auf Weiß, Icon auf
Klecks).

### AP 4: Suche und Chip-Zeile

**Chip-Zeile** (`#tag-bar`, gefüllt von `syncTagPills` in `js/suche.js`):

- eine waagrecht scrollbare Zeile: „Alle“, dann die zehn Themen, am Ende fest ein Knopf
  „Alle Themen“ mit Icon `SlidersHorizontal`
- der Knopf öffnet die volle Liste als Blatt; das Muster gibt es schon im Kalender
  (`.bottom-sheet`, `style.css:1591`)
- Chips als Pille, `aria-pressed`; Mehrfachauswahl und `?tags=` in der URL bleiben, wie
  sie sind
- Blatt: Fokus hinein, Esc schließt, Fokus zurück auf den Knopf
- gleiche Zeile auf allen Breiten; am Rand ein weiches Ausblenden als Hinweis, dass es
  weitergeht

**Suche** (`#search`, `#gremien-search`):

- Radius 10 px, Icon links (gibt es), Höhe 48 px mobil, 44 px am Desktop
- Steht die Suche nicht mehr auf farbigem Grund (AP 5): 1 px `ink-line` statt
  `shadow-lg`, Fokus über den Fokusring
- Dropdown, Gruppen und Tastatursteuerung unverändert

**Prüfung:** Tastatur durch Chips und Blatt; Filter per URL aufrufbar wie vorher.

### AP 5: Seitenköpfe und Bereichsfarben

**Ist:** Navbar und Suchblock tragen eine Farbe je Bereich (`style.css:66-75`, gesetzt von
`setChrome` in `js/routing.js:37`): Themen `red-700`, Themenfeld `red-900`, Sitzung und
Kalender `gold-700`, Gremien Tinte, Einstellungen Creme. Begründung im Kommentar: Man weiß
am oberen Rand, wo man ist, bevor man liest.

**Vorschlagsseite:** heller Kopf, großer Titel oben links, darunter Suche und Chips. Die
Bereichsfarbe kommt dort nicht vor.

**Offene Gestaltungsfrage, nicht selbst entscheiden:**

- **Variante 1, wie die Vorschlagsseite.** Heller Kopf überall, Orientierung über Seitentitel
  und aktiven Tab.
- **Variante 2.** Heller Kopf; die Bereichsfarbe lebt als deckende Fläche im Seitenkopf der
  Detailseiten weiter (Themenfeld Tiefrot, Sitzung Gold-700). Höchstens eine Fläche pro
  Bildschirm. Tinte ist keine Themenfarbe; für Profil und Fraktion bräuchte es Nachtblau
  oder keine Fläche.

Variante 1 zuerst bauen, Variante 2 auf `#/feld/building` und einer Sitzung dazu, als Paar
vorlegen.

**Farb-Experiment** (Wunsch Benedict, 14.09.2026). Im Stadtrat dürfen die Flächen auch
andere Themenfarben als Rot tragen. Heute verteilt `--chrome` Rot, Tiefrot, Gold-700 und
Tinte auf die Bereiche. Für Variante 2 zusätzlich eine Reihe aus den sechs Themenfarben des
Protokolls zeigen. Vorschlag nach Inhalt:

- Themen und Themenfelder: Tiefrot, die Hausfarbe der Ratsarbeit
- Sitzungen und Kalender: Nachtblau (aus dem Stripe-Indigo)
- Gremien, Profile und Fraktionen: Aubergine (aus dem Purpur-Akzent)
- die Fläche „nächste Sitzung“ (AP 7) in der Farbe der Sitzungen

Regeln dabei:

- Themenfarben nur für Flächen, nie für Datenmarken. Partei-, Abstimmungs- und
  Gremienfarben bleiben unberührt.
- Prüfen, dass kein Flächenton mit einer Parteifarbe aus `data/members.json` verwechselt
  werden kann, vor allem auf Profil- und Fraktionsseiten.
- Kontrastwerte stehen im Protokoll, Abschnitt 6.

Als Screenshot-Reihe vorlegen (dieselbe Seite in mehreren Tönen), nichts festlegen.

**Seitentitel mobil:** „Themen“, „Kalender“, „Gremien“, „Einstellungen“ als H1 oben links, in
der Titelschrift. Unter „Themen“ die Bestandszeile aus `.home-meta-hint`
(„173 Sitzungen, 134 von 175 mit Niederschrift“). Das zugeklappte „Zahlen zum Bestand“
bleibt, wo es ist; die Rangfolge der Startseite ist in `PLATTFORM.md` begründet.

**Überlappung Variante 1** nur auf Themen, Kalender und Gremien, nicht auf Detailseiten.
Werte wie im Portal-Briefing, AP 3: `gold-500` etwa 55 %, 1,45 ×, −6°, `top: -0.42em`,
0,85 em Abstand darüber, Beschnitt nur an der Zeichnung. Wörter als Vorschlag: Themen
„nachvollziehbar“ (so auf der Vorschlagsseite), Kalender „öffentlich“, Gremien „gewählt“.

**Messbares Kriterium:** In 390 × 844 px steht die erste Themenkarte weiterhin im ersten
Bildschirm, wie auf dem Vorher-Screenshot. Schiebt die Überlappung sie darunter, mobil
kleiner setzen oder dort weglassen und das begründen.

**Desktop:** Titel mit Federzeichnung als Maske in Gold, rechts unten angeschnitten.
Vorschlag `rathausC.svg` aus `../moosburg/public/sketches/`: ein Rathaus passt zum Stadtrat,
`rathausB` trägt schon der Haushalt.

**Dossier-Kopf** (`.topic-header h1`, `style.css:505`): Satzschreibung, Klecks aus AP 3.

**Prüfung:** Paar Variante 1 und 2; Screenshot 390 px Startseite.

### AP 6: Navigation

**Ist:** `.navbar` 48 px, klebt oben, nur Logo (Icon `account_balance` plus „Stadtrat
Moosburg“ in Versalien). `.tab-bar` klebt unten auf allen Breiten. `body` hat
`padding-bottom: var(--tab-height)`. Der Stripe klebt unter der Navbar
(`.navbar + .rainbow-stripe`, `style.css:137`).

**Soll ab 1024 px, Variante A:**

```
[Stripe 4 px an der Oberkante]
[Rose] moosburg.eu │ [Logo] Stadtrat Moosburg   Themen  Kalender  Gremien  Einstellungen │ (i) Über das Projekt ▾
```

- Zeile 64 px; Tool-Name in der Titelschrift; Navigation in Satzschreibung, 15 px, aktiv
  600 mit 2 px Unterstreichung (Farbe siehe Abschnitt 3).
- „moosburg.eu“ verlinkt auf `https://moosburg.eu/`, auch in der Pages-Fassung.
- **Logo-Platz:** Rose als Platzhalter. Dass daneben die Rose von „moosburg.eu“ steht, ist
  bis zu den Tool-Logos in Ordnung (Benedict, 14.09.2026). Das Icon `account_balance` im
  heutigen Logo entfällt.
- Tab-Leiste ab 1024 px ausgeblendet, `padding-bottom` nur darunter.
- **„Über das Projekt“** als Disclosure wie im Haushalt: `aria-expanded`, `aria-controls`,
  Esc schließt, Klick außerhalb schließt, Fokus zurück; **kein** `role="menu"`.

**Soll unter 1024 px:**

- App-Leiste: Stripe oben, „Stadtrat Moosburg“ links, rechts ein Rosen-Knopf
  (`aria-label` „moosburg.eu und Über das Projekt“), der ein Blatt mit beiden Einträgen
  öffnet.
- Tab-Leiste unten: Icon mit Pillen-Markierung, Beschriftung 12 px,
  `env(safe-area-inset-bottom)`.

**Code:** in `js/routing.js`, das laut `docs/MODULE.md` Tabs und Seiten-Chrome verantwortet.
Wird es zu groß, eigenes Modul und die Tabelle in `MODULE.md` nachführen.

**Höhen:** `--nav-height` wird zur Kopfhöhe inklusive Stripe, als eine Variable. Alle
`sticky`-Offsets prüfen, die davon abhängen. Die Regel `.navbar + .rainbow-stripe` entfällt.
Kein `backdrop-filter` am Kopf: Im Haushalt wurde der Kopf dadurch zum Bezugsrahmen des
mobilen Blatts.

**Inhalt von „Über das Projekt“, als Vorschlag vorlegen:**

- Titel „Stadtratstransparenz“
- „Abstimmungsverhalten im Moosburger Stadtrat, aufbereitet aus den öffentlichen
  Niederschriften.“
- „Privates Projekt, kein Auftritt der Stadt. Verbindlich bleibt die amtliche
  Niederschrift.“
- Links: Woher die Daten kommen (`#/datenlage`), Kontakt, Impressum und Datenschutz (die
  bestehenden Modals), Quellcode auf GitHub.
- Dazu Textvorschläge für die Einstellungen (`index.html:123`) und das Kontakt-Modal
  (`index.html:327`), die sich nicht mehr als Angebot der Stadt lesen, etwa mit der
  Adresse `info@gruber.am` wie auf dem Portal.

Die Einstellungen behalten die beiden Barrierefreiheits-Schalter. Ihr Block
„Informationen“ bleibt als zweiter Weg, wie der Fuß im Haushalt.

**Prüfung:** Tastatur durch Kopf, Disclosure, Tabs; 1440 px: eine Zeile, keine Tab-Leiste;
390 px: nichts verdeckt Inhalt, Stripe oben, Blatt über der Tab-Leiste.

### AP 7: Farbfläche „nächste Sitzung“

Die Vorschlagsseite nennt die nächste Sitzung oben auf der Startseite als Ort. **Das
kollidiert mit der Rangfolge der Startseite** (`PLATTFORM.md`): Die Themen sind der
Einstieg und sollen nicht unter die Falz rutschen.

- **Vorschlag:** Die Fläche steht oben im Kalender-Tab: Gremium, Datum, Uhrzeit, Knopf
  „Tagesordnung“, sobald es eine Sitzungsseite gibt. Themenfarbe Gold-700 (der
  Terminstrang) oder Tiefrot.
- Auf der Startseite höchstens als kompakte Fassung, eine Zeile hoch. Beide als Paar
  zeigen; Kriterium aus AP 5 (erste Themenkarte im ersten Bildschirm) gilt.
- **Daten:** Aufbau von `data/termine.json` und `sessions.json` vorher lesen. Das nächste
  Datum ab heute wird beim Rendern bestimmt, nie fest eingetragen. Gibt es keines, gibt es
  keine Fläche.
- Werte: Protokoll, Abschnitt 4, Zeile Farbflächen; Stripe als unterer Abschluss. Keine
  Handschrift auf dieser Fläche (Werkzeug-Profil), außer Benedict wünscht es.

### AP 8: Ecken, Kanten, Zahlen, Buttons

**Ecken:** 20 feste px-Radien und `--radius` (4 px). Kacheln (`.topic-card`,
`.stats-teaser`), Modals, Blätter, Buttons und Suche auf 10 px; Marken und kleine
Daten-Chips auf 4 px; Themen-Chips als Pille. Einzeln durchgehen, nicht pauschal ersetzen.

**Einseitige Kanten**, drei Fundstellen:

- `.vote-text` (`style.css:1117`), 2 px in `--border`: Zitat-Einzug, laut `PLATTFORM.md`
  ausdrücklich erlaubt. Bleibt.
- `.source-note` (`style.css:2948`), 3 px in Gold: **verbotenes Muster.** Wird zu einer
  Fläche mit Rahmen oder bekommt ein Icon statt der Kante.
- `.faction-move.in` und `.out` (`style.css:3100-3101`), 3 px in der Farbe der anderen
  Partei: trägt laut Kommentar die Wechselrichtung, also Datenmarke statt Schmuck. Nicht
  umbauen, im Ergebnis zur Bestätigung vorlegen.

**Zahlen:** Kennzahlen mit `lining-nums tabular-nums`, Zahl zuerst, Beschriftung darunter,
wo heute Label über Zahl steht (`.stat-value` und verwandte).

**Buttons:** drei Stufen (primär, tonal, Text-Link), nur wo es Buttons schon gibt. Keine
neuen.

### AP 9: Nachher-Stand, Auswertung, Protokoll

1. `python scripts/stamp_assets.py`, dann Nachher-Screenshots wie in AP 0 nach
   `docs/formsprache-probe/nachher/`, Paare nach `nachher/paare/`.
2. `docs/formsprache-probe/ERGEBNIS.md` nach dem Muster des Haushalts, mit der
   Kontrasttabelle aus AP 3.
3. Protokoll `../moosburg-design/docs/formsprache/ENTSCHEIDUNGEN.md`, Abschnitt „Verlauf“:
   Datum, Branch, Commits, Verweis aufs Ergebnis. Entscheidungen nicht auf endgültig setzen.

**Abschlussprüfung, alle grün:**

- [ ] `grep -n "uppercase" css/style.css` ohne unkommentierte Treffer
- [ ] `grep -n "font-family: '" css/style.css` leer (nur noch Variablen)
- [ ] gerenderte Schriften nur die drei neuen
- [ ] `git diff --stat main -- data/ scripts/` leer
- [ ] alle Routen aus AP 0 ohne Konsolenfehler, `?v=`-Stempel aktuell
- [ ] Tastatur: Tabs, Chips, Blatt, Disclosure, Modals, Kalender
- [ ] „Größere Schrift“ und „Farbenblind-sichere Farben“ wirken
- [ ] 390 px: erste Themenkarte im ersten Bildschirm; 1440 px: Navigation in einer Zeile,
      keine Tab-Leiste
- [ ] 200 % Zoom: Titel mit Überlappung lesbar
- [ ] Vorher/Nachher vollständig, `ERGEBNIS.md` geschrieben, Protokoll nachgeführt

---

## 5. Offene Fragen, die Benedict vorgelegt werden

| Frage | Wie vorlegen |
|---|---|
| Phosphor-Icons für Merkmale und Funktionen (`queer`, `flinta`, `migrant`, `disability`, `referent`, `ausschuss`, `vorsitz`, `aufsichtsrat`) | Vorschlagsliste mit Screenshot |
| Aktive Zustände in Rot oder Tinte, neben dem Ablehnungs-Rot? | Paar Chip-Zeile und Kopf |
| Kategoriezeile: Text in Kategoriefarbe oder nur das Icon? | Paar Themenliste |
| Bereichsfarben: Variante 1 (weg) oder 2 (als Fläche in Detailseiten)? | Paar Themenfeld |
| Handschrift-Wörter „nachvollziehbar“, „öffentlich“, „gewählt“; mobil ja oder nein? | Screenshots |
| Federzeichnung `rathausC`? | Screenshot 1440 px |
| Farbfläche im Kalender oder kompakt auf der Startseite? | Paar |
| Texte für „Über das Projekt“, Einstellungen und Kontakt | Textvorschlag |
| Gremien als Kategoriezeile? | Hinweis |
| Kanten an `.faction-move` als Datenmarke behalten? | Screenshot Profil |
| Farb-Experiment: welche Themenfarbe je Bereich (Tiefrot, Nachtblau, Aubergine oder andere)? | Screenshot-Reihe Themenfeld, Sitzung, Profil |
