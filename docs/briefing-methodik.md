# Briefing: Seite „So entsteht diese Seite“ (`#/methodik`)

*Angelegt am 07.10.2026. Status: **offen, noch nichts umgesetzt.** Alle Fragen sind
entschieden, siehe Abschnitt 5.*

Ziel ist eine Seite in der App, die den Weg der Daten erklärt: woher sie kommen, wo ein
Sprachmodell mitarbeitet und wo feste Rechenregeln greifen, wie die Herkunft der
Einzelstimmen zu lesen ist, welche Regeln der Gemeindeordnung und welche Hausregeln
gelten, wer die Seite betreibt und wie sie technisch gebaut ist. Dieses Briefing ist so
geschrieben, dass eine neue Sitzung ohne Vorwissen loslegen kann. Zuerst die Abschnitte
1 bis 3 ganz lesen, dann die Arbeitspakete der Reihe nach. Jedes endet mit einer
Abnahme.

---

## 1. Rahmen

### Der Entwurf

Text und Aufbau stehen in einem abgestimmten Entwurf. Er ist die Vorlage für Inhalt,
Reihenfolge und Prozessbild, **nicht** für den Code: er ist eine eigenständige HTML-Seite
mit eigenen Stilen und hart kodierten Zahlen.

- lokal: `quellen/entwuerfe/methodik-entwurf.html` (in der `.gitignore`, nicht im Repo)
- online: https://claude.ai/artifact/BXi6nFVBAVMcxPU4vbf1vL (Version 3)

Gelb gestrichelte Kästen darin sind Notizen und kein Seitentext.

### Quellen, in dieser Reihenfolge lesen

| Quelle | Wozu |
|---|---|
| `CLAUDE.md`, `~/.claude/CLAUDE.md` | Arbeitsweise, Code-Stil, keine Erwähnung von KI in Commits und Code. Die Ausnahme für diese Seite steht in Abschnitt 2. |
| `docs/formsprache-probe/ERGEBNIS.md` | Geltende Formsprache, maßgeblich für alles Optische. |
| `PLATTFORM.md` | Zwei Auslieferungen, CSP von moosburg.eu (`style-src 'self'`), relative Pfade, verbotener Kantenakzent. |
| `docs/MODULE.md`, `docs/CORE.md` | Modul-Schnitt, Vote-Status-Logik, Ausschlussgründe. |
| `js/views/datenlage.js`, `js/daten.js` | Vorbild für die neue View und Quelle der Live-Zahlen (`bestand()`, `sessionRegister()`, `votenVon()`, `tierCounts()`). |
| `scripts/*.py` (Docstrings) | Die Rechenregeln, die die Seite beschreibt. Der Seitentext muss zu ihnen passen. |
| `.claude/skills/*/SKILL.md` | Die Pflege-Abläufe, also das, was das Prozessbild abbildet. |

### Entscheidungen vom 07.10.2026

| Frage | Entscheidung |
|---|---|
| Ort | Eigene Route `#/methodik`. Im Über-Panel verlinkt, gegenseitig mit der Datenlage verlinkt. Die Legende der Abstimmungsansicht wird kürzer und verweist hierher. |
| Zahlen | Alle live aus dem Bestand, nichts hart kodiert. |
| Sprachmodell | Offen benennen, dass eines mitarbeitet. **Modell und Anbieter werden nicht genannt**, nur, dass das im Grunde jedes aktuelle Sprachmodell kann. KI erscheint nur als Teil des Datenprozesses, **nie als Teil der Entwicklung** der App. |
| Enthaltung | Ein gemeinsamer Punkt für Enthaltungsverbot und Protokollfall, siehe 3.4. |
| Betreiber | Dritte Person. Die Einladung an andere Akteure im Optativ („Idealerweise …“, „Wünschenswert wäre …“). |
| Durchsicht | Wie bei allem anderen: Das Sprachmodell liefert den ersten Aufschlag, ein Mensch korrigiert und gibt frei. |
| Lizenz | Alles nichtkommerziell, mit einer Zusatzerlaubnis für die Presse, siehe AP 7. |
| Fraktionsseite | Die Anzeige der häufigsten Abweichung bleibt. Sie ist eine Zählung und kein Urteil. |
| Prozessbild | Interaktiv: Hervorheben nach Art des Schritts und ein Erklärkasten. |
| Publikum | Gleichrangig Bürger:innen, Presse, Verwaltung und technisch Interessierte. Für alle etwas. Technik in aufklappbaren Abschnitten. |

---

## 2. Leitplanken für den Text

- **Ausnahme von der Attributionsregel:** Auf dieser Seite, und nur hier, steht, dass ein
  Sprachmodell Niederschriften liest und Zuordnungen vorschlägt. Commits, Code-Kommentare
  und alle anderen Texte bleiben ohne jede Erwähnung.
- **Nicht mehr versprechen, als passiert.** Die Arbeitsteilung ist überall dieselbe:
  Das Sprachmodell liefert den ersten Aufschlag, ein Mensch korrigiert und gibt frei. So
  formulieren, ohne Ausschmückung. Nicht behaupten, jeder Wert werde einzeln gegen das
  PDF verglichen.
- **Beschreiben, nicht bewerten.** Keine Adjektive über Beschlüsse oder Personen.
- **Betreiber in dritter Person.** Benedict Gruber, Stadtrat für fresh vom 10.10.2022 bis
  30.04.2026 und in dieser Zeit Digitalisierungsreferent. Seit Mai 2026 nicht mehr im Rat.
- Wortwahl der App beibehalten: „aus eigenen Notizen rekonstruiert“, nie „aus der
  Erinnerung“. „Nur Amtliches wird zum Bestand.“
- Schreibweise der Formsprache: keine Versalien, keine Verläufe, kein einseitiger
  Kantenakzent, das Aufklapp-Muster `<details>` mit `+`/`–` rechts.

---

## 3. Inhalt, Abschnitt für Abschnitt

Reihenfolge wie im Entwurf. Der Wortlaut des Entwurfs ist abgestimmt und kann übernommen
werden, mit den hier genannten Ausnahmen.

### 3.1 Kopf

Titel „So entsteht diese Seite“, Vorspann, darunter Sprungmarken zu den Abschnitten.
**Achtung:** Hash-Routing. `#/methodik#herkunft` funktioniert nicht. Sprungziele als
Unterpfad lösen (`#/methodik/herkunft`, View scrollt zum Abschnitt) oder per
`scrollIntoView` auf Klick.

### 3.2 Der Weg der Daten (Prozessbild)

Fünf Quellen, je ein Einarbeitungsschritt, eine Sammelschiene in „Rechenregeln und
Prüfung“, dann „Öffentliche Dateien“. Jeder Teilschritt trägt eine Markierung:

| Form | Farbe | Bedeutung |
|---|---|---|
| Raute | Gold (`--accent`) | Sprachmodell |
| Quadrat | Tinte (`--text`) | Skript mit festen Regeln |
| Kreis | Wappenrot (`--primary`) | Mensch entscheidet |

Zuordnung (aus den Skills und Skripten abgeleitet, vor dem Bau gegenprüfen):

| Quelle | Schritte |
|---|---|
| Niederschrift | ◆ liest PDF (Skill `niederschrift-einarbeiten`) · ◆ schlägt Dossier vor · ● Durchsicht und Zuordnung |
| Beschlussauszug | ■ `parse_bpu_webauszug.py` · ● Durchsicht |
| Mitschrift im Saal | ● Übertrag von Hand, erst wenn die Niederschrift vorliegt |
| Presse | ■ `scripts/crawl/extract.py` (Vorschlag mit Belegsatz) · ◆ Zuordnung (Skill `presseartikel-einarbeiten`) · ● Prüfung am Artikel |
| Eigene Notizen | ■ `offene_stimmen.py` · ■ `selbstauskunft.py` |
| Rechenregeln und Prüfung | ■ `mark_inferable.py` · ■ `complete_votes.py` · ■ `mandatswechsel_stimmrecht.py` · ■ `teilanwesenheit.py` · ■ `validate_data.py` · ● Freigabe |
| Öffentliche Dateien | Git, Browser rechnet selbst (`core.js`), beim Besuch läuft kein Sprachmodell |

Interaktion wie im Entwurf:
- Die Legende ist zugleich ein Filter: drei Knöpfe mit `aria-pressed`. Der aktive Knopf
  dimmt alle Teilschritte anderer Art.
- Ein Klick auf einen Kasten füllt den Erklärkasten darunter (`aria-live="polite"`). Die
  Kästen sind `<button>`. Beim Laden ist „Niederschrift“ gewählt, damit der Kasten nie
  leer ist.
- Ab etwa 860 px ein Raster mit sechs Spalten (Quelle, Einarbeiten, Schiene,
  Rechenregeln, Pfeil, Bestand). Darunter eine senkrechte Kette. Die Zeilen sind
  `display: contents` und werden mobil zu eigenen Blöcken.
- Die Schiene wird per Skript auf die Mitte des ersten und des letzten Anschlusses
  gesetzt, bei `resize` und nach `document.fonts.ready`.

Zahlen in den Quellkästen live: Sitzungen mit Niederschrift / alle (`bestand()`),
Sitzungen mit Auszug, Zahl der Presseartikel (`pressData.length`).

### 3.3 Wo ein Sprachmodell mitarbeitet

Wortlaut aus dem Entwurf (Version 3). Er nennt kein Modell und keinen Anbieter. Die
Gegenüberstellung „übernimmt / übernimmt nicht“ bleibt. Zur linken Liste gehört auch
„Kurztexte zu Dossiers und Einträge der Zeitleisten entwerfen“. Laut Skill
`topic-anlegen` entwirft das Modell `summary` und `history[].text`. Unter den beiden
Listen steht ausdrücklich die Arbeitsteilung: erster Aufschlag vom Sprachmodell,
Korrekturen und Freigabe durch einen Menschen. Das gilt für Übertragungen, Zuordnungen und
Kurztexte gleichermaßen.

Zahlen live: Zahl der Niederschriften, Zahl der Abstimmungen, Jahr der ersten Sitzung
(`bestand().seit`).

### 3.4 Woher die Einzelstimmen stammen

- Ein Balken über alle Abstimmungen, maßstabsgetreu, in der bestehenden Rampe
  `.tier-*`. Darunter die sechs Stufen mit Zahl und Anteil. Jede Stufe verlinkt auf den
  Filter der Datenlage (`#/datenlage/explicit` usw.). Zählung exakt wie auf der Datenlage
  (`tierCounts(sessionRegister().flatMap(votenVon))`), damit beide Seiten dieselben
  Zahlen zeigen.
- Drei Rechenregeln als Sitzbilder (22:0, 21:0 mit Sternchen, 15:7 mit errechneter
  Gegenseite). Diese Beispiele sind erfunden und als Beispiel erkennbar, also statisch.
  Die 90-%-Schwelle als Konstante neben `THRESHOLD` in `mark_inferable.py` erwähnen, nicht
  im Text frei erfinden.
- Hinweis auf weiche Belege (`voterEvidence`).

### 3.5 Regeln der Gemeindeordnung

**Enthaltung, ein gemeinsamer Punkt.** Art. 48 Abs. 1 Satz 2 GO lautet wörtlich: „Kein
Mitglied darf sich der Stimme enthalten.“ (geprüft am 07.10.2026 auf gesetze-bayern.de).
Ausnahmen, in denen jemand anwesend ist und weder Ja noch Nein sagt:

1. **Niederschriften aus der Zeit vor dem eigenen Mandat.** Das ist gelebte Praxis und
   steht nicht in der GO, deshalb ohne Paragraf formulieren. Beleg ist
   `sr_20260518_01`: Die Notiz am Vote sagt, neun der elf Neuen hätten sich enthalten und
   zwei zugestimmt, welche zwei, steht nicht in der Niederschrift. Die Daten führen alle
   elf als `nicht_stimmberechtigt` (Anzeige „n.b.“), weil sich die Enthaltungen
   niemandem zuordnen lassen. **So bleibt es.** Die Seite erklärt den Fall und verlinkt
   die Sitzung.
2. **Persönliche Beteiligung (Art. 49 GO).** Typische Fälle: Entlastung des Aufsichtsrats
   der Kläranlage Moosburg GmbH, eigene Bauvorhaben, Beschlüsse über das eigene Amt.
   Zahl live: Abstimmungen mit mindestens einem `excluded`-Eintrag mit Grund
   `beteiligung` (am 07.10.: 52).

Weitere Punkte wie im Entwurf: wer mitstimmt (Sitzzahlen aus `bodies.json`, nicht hart
kodiert), Mandatswechsel (Zahl live: Sitzungen mit `kein_mandat`, am 07.10.: 4), kurz
draußen ist nicht abwesend.

### 3.6 Hausregeln

Wie im Entwurf. Die Zahl der Sitzungen ohne Veröffentlichung live (`bestand().keine`).
Unter „Beschreiben, nicht bewerten“ steht der Satz zur Fraktionsabweichung als Zählung.

### 3.7 Wer dahintersteht

Dritte Person, Wortlaut aus dem Entwurf (Version 3). Die Einladung im Optativ, als Weg
das Kontaktformular (`data-modal="kontakt-modal"`).

### 3.8 Technik

Aufklappbar, wie im Entwurf. Der Abschnitt „Offene Daten“ hängt an AP 7.

### 3.9 Teil von moosburg.eu

Kurzer Absatz wie im Entwurf: ehrenamtlich, quelloffen, kostenlos, ohne Werbung, ohne
Tracking. **Nicht** „Open Source“ schreiben: Mit einer nichtkommerziellen Lizenz ist der
Code einsehbar, aber nicht Open Source im Sinne der OSI. „Quelloffen“ im Sinne von
„Quellcode öffentlich“ ist in Ordnung.

---

## 4. Arbeitspakete

### AP 1: Route und View

- `js/views/methodik.js` nach dem Muster von `datenlage.js`, Export `renderMethodik`.
- `js/routing.js`: Route `/methodik` (mit Unterpfad für Sprungziele, siehe 3.1).
- Über-Panel in `index.html`: Eintrag „So entsteht diese Seite“ neben „Woher die Daten
  kommen“, Icon aus dem vorhandenen Sprite.
- `js/suche.js`: Eintrag neben dem der Datenlage.
- Datenlage: im Kopf ein Satz mit Link auf `#/methodik`. Methodik verlinkt umgekehrt.
- Danach `python scripts/stamp_assets.py`.

**Abnahme:** `#/methodik` rendert mit Zurück-Link und ohne Konsolenfehler. Panel, Suche
und Datenlage führen hin, die Methodik führt zurück.

### AP 2: Texte und Live-Zahlen

Alle Abschnitte aus 3.1 bis 3.9 mit Live-Zahlen. Neue Zählungen (Beteiligung,
Mandatswechsel) gehören als kleine Funktionen nach `daten.js`, wenn sie auch anderswo
gebraucht werden, sonst in die View.

**Abnahme:** Jede Zahl auf der Seite ist gegen die Datenlage oder ein Python-Einzeiler über
`data/*.json` geprüft. Kein Zahlwort ist hart kodiert, außer in den erfundenen
Sitzbild-Beispielen.

### AP 3: Prozessbild

HTML und CSS in `css/style.css`, mit den Rollen-Tokens der App (`--primary`,
`--accent`, `--text`, `--border`, `--surface`). Keine neuen Farbwerte.

**CSP beachten:** moosburg.eu setzt `style-src 'self'`. Statische `style`-Attribute sind
mit `d46813c` aus dem Markup verschwunden. Dynamische Werte (Balkenbreiten, Position der
Schiene) über `el.style` setzen, nicht als Attribut im Markup. `datenlage.js` setzt für
`.tier-bar` und `.reg-dot` noch `style`-Attribute per `innerHTML`. Ob die auf moosburg.eu
greifen, ist ungeprüft. Falls nicht, ist das ein eigener Fehler, der getrennt behoben
wird. Nicht nachahmen.

**Abnahme:** In 1440 und 390 px kein waagrechter Überlauf. Alle Knöpfe per Tastatur
bedienbar, Fokus sichtbar. Hervorheben und Erklärkasten funktionieren.
`prefers-reduced-motion` schaltet die Übergänge ab. „Größere Schrift“ bricht das Raster
nicht.

### AP 4: Legende kürzen

In `index.html` den Block „Woher die Einzelstimmen stammen“ auf zwei Sätze und einen Link
auf `#/methodik/herkunft` kürzen. Dabei den Satz zur Befangenheit korrigieren: Er sagt
„ebenso selten wie die Enthaltung“, obwohl die Daten keine einzige `enthaltung`
enthalten. Die Prozentangabe dort live oder ganz weglassen.

**Abnahme:** Die Legende widerspricht der Methodik-Seite nirgends.

### AP 5: README und CLAUDE.md

- README: „Inhalte werden weitgehend automatisiert extrahiert“ an die Seite angleichen
  und auf `#/methodik` verweisen.
- CLAUDE.md: eine Zeile, dass die Methodik-Seite mitzieht, wenn sich ein Pflege-Ablauf
  ändert (neuer Skill, neues Skript, neue Herkunftsstufe).

### AP 6: Tests

Wenn neue Zählfunktionen in `daten.js` landen, je ein Test in `tests/`.
`node --test "tests/*.test.mjs"` grün.

### AP 7: Lizenz

Entscheidung: alles nichtkommerziell. Umsetzung:

- **Daten und Texte:** CC BY-NC 4.0. Datei `LICENSE-DATA` mit Verweis auf den
  offiziellen Lizenztext, Geltungsbereich `data/` (ohne `data/niederschriften/`, die
  amtlichen PDFs sind Werke der Stadt) und die Texte der App.
- **Code:** PolyForm Noncommercial 1.0.0 statt MIT. Creative-Commons-Lizenzen sind für
  Software ungeeignet. `LICENSE` ersetzen, mit der „Required Notice“-Zeile.
- Frühere Stände bleiben MIT. Das lässt sich nicht zurücknehmen und muss nirgends stehen.
- Fremdes behält seine Lizenz: Schriften in `fonts/` (OFL), Phosphor-Icons (MIT). Die
  Hinweise bleiben erhalten.
- **Zusatzerlaubnis für die Presse** (entschieden am 07.10.2026), in `LICENSE-DATA`, im
  README und im Technik-Abschnitt der Seite gleichlautend, sinngemäß: „Über die Lizenz
  hinaus dürfen Medien die Daten und Grafiken für redaktionelle Berichterstattung nutzen,
  auch wenn sie kommerziell arbeiten, sofern die Quelle genannt wird.“ Das ist eine
  zusätzliche Erlaubnis neben CC BY-NC 4.0, keine Änderung der Lizenz. Creative Commons
  sieht solche Zusatzerlaubnisse ausdrücklich vor.
- README-Abschnitt „Lizenz & Verantwortung“ und der Technik-Abschnitt der Seite
  entsprechend.

**Abnahme:** Lizenzdateien vorhanden, README und Seite nennen dieselben Lizenzen, Hinweise
für Fremdes intakt.

---

## 5. Nachträglich entschieden (07.10.2026)

1. **Durchsicht:** Wie bei allem anderen liefert das Sprachmodell den ersten Aufschlag,
   ein Mensch korrigiert und gibt frei. Das gilt auch für die Kurztexte der Dossiers. Die
   Sätze im Entwurf (Version 3) sind daran angepasst.
2. **Presse:** Ja, Zusatzerlaubnis für redaktionelle Berichterstattung, siehe AP 7.

---

## 6. Abnahme gesamt

- `python scripts/validate_data.py` ohne Fehler (Daten werden nicht geändert, aber zur
  Sicherheit).
- `node --test "tests/*.test.mjs"` grün.
- `python scripts/stamp_assets.py` gelaufen.
- Aufnahmen in 1440 und 390 px ohne Konsolenfehler und ohne waagrechten Überlauf.
- Jede Zahl stimmt mit der Datenlage überein.
- Kein Modell- oder Anbietername auf der Seite, keine Erwähnung von KI außerhalb der
  Seite.
