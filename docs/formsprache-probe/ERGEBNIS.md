# Formsprache im Stadtrat: Ergebnis der Probe

*Stand 16.09.2026. Umgesetzt und in `main` gemergt, damit live auf
moosburg.eu/stadtrat/. Die Entscheidungen sind **vorläufig**: Kanon ist allein
`../moosburg-design/css/theme.css`; das Protokoll dort führt den Verlauf.*

Grundlage: `docs/briefing-formsprache.md` (AP 0 bis 9) und zwei Rückmeldungsrunden
von Benedict am 15. und 16.09.2026. Die Vergleichsbilder liegen als Vorlagen:
[Beschlussvorlage](https://claude.ai/artifact/3pZ2PBGcT5tRp7QC5QKUKd),
[Zweite Lesung](https://claude.ai/artifact/CjfKtaZwwokhbZsCd2p5wk),
[Gremienfarben](https://claude.ai/artifact/CPBkQ1QxwC6mGFDbbCgdqf).

## Was jetzt gilt

| Bereich | Entscheidung |
|---|---|
| Schriften | Source Serif 4 (Titel), Atkinson Hyperlegible Next (Text), Madelon Script (Handschrift), self-hosted in `fonts/`. Die Null mit Schrägstrich bleibt. |
| Icons | Phosphor, Gewicht `regular`, als Inline-Sprite mit den alten Material-IDs. Auch die Kontaktwege auf Profilen. |
| Versalien | keine mehr. |
| Kategorien | Kategoriezeile mit Icon und Name im dunklen Ton der Themenfarbe, Klecks in den Köpfen von Themenfeld und Dossier, nicht in Listen. |
| Seitenköpfe | hell, Titel oben links mit Handschrift („nachvollziehbar“, „öffentlich“, „gewählt“), Federzeichnung `rathausC` ab 1280 px nur auf Themen. |
| Farbflächen | nur über die ganze Breite: Band im Kopf von Themenfeld (tiefer Ton der Themenfarbe) und Sitzung (Farbe des Gremiums). Dossier und Fraktion bleiben hell. Kein Stripe als Abschluss. |
| Gremienfarben | Stadtrat Tiefrot `#6d0818`, BPU Erdbraun `#4a2a17`, HVFA Nachtblau `#26295e`, jeweils der dunkle Ton der Farbe aus Kalender und Diagrammen. Trägt auch die Termin-Card. |
| Navigation | Variante A ab 1024 px, darunter App-Leiste und Tab-Leiste mit Pillen. Drei Tabs: Themen, Kalender, Gremien. |
| Über das Projekt | Panel im Kopf, mobil als Blatt: Beschreibung, Barrierefreiheits-Schalter, Datenlage, Kontakt, Impressum, Quellcode, dazu der Weg zurück auf moosburg.eu. |
| Aktive Zustände | `red-700` auf `red-50`. |
| Ecken | 4 px für Marken, 8 px für Kacheln, Flächen, Suche und Knöpfe (seit 16.09. Kanon-Wert), Pille für Chips und Tab-Markierung. |
| Suche | überall derselbe Bestand, auch Gremien; die Reihenfolge der Gruppen richtet sich nach dem Tab. |

## Änderungen an Inhalt und Daten (16.09.2026)

- **Einstellungen als Tab entfallen.** Impressum und Kontakt standen schon in „Über
  das Projekt“, die beiden Schalter sind dorthin gezogen. `#/einstellungen` führt
  auf die Startseite. Mobil öffnet ein Info-Knopf das Blatt.
- **Kein stellvertretender Vorsitz.** Es gibt ihn offiziell nicht; Zweiter und
  Dritter Bürgermeister sind es implizit. Die beiden `vicechairs`-Einträge des BPU
  (Hadersdorfer, Stanglmaier) sind normale Sitze geworden, damit sie weiter als
  Mitglieder zählen. Vorsitzender ist überall der amtierende Erste Bürgermeister,
  einzige Ausnahme bleibt der Rechnungsprüfungsausschuss.
- **HVFA 2020 bis 2026:** Der Sitz stand als „Hobmaier, Vertretung Gruber“, obwohl
  Hobmaier erst im Oktober 2024 in den Rat kam. Nach Auskunft von Benedict war er
  volles Mitglied; der Sitz ist gedreht. **Offen:** Wer den Sitz zwischen Mai 2020
  und Oktober 2022 hatte, ist nicht abgebildet.
- **Ämter über Wahlperioden hinweg** werden zusammengeführt, wenn keine Lücke
  bleibt (Stanglmaier: „Dritter Bürgermeister 2014–heute“ statt zwei Zeilen).
  Monatsangaben wie `2020-05` zählen dabei ab Monatsanfang bzw. bis Monatsende.
- **„Im Rat seit“** ist raus, die Mandatszeile darüber sagt dasselbe.
- **Weg ins Themenfeld** steht bei einem gesetzten Filter über der Liste, mit
  Klecks und heller Tönung des Feldes statt Kante.

## Prüfungen

- 41 Verhaltensprüfungen grün: Kopf und Panel (Esc, Klick außerhalb, Fokus
  zurück), Blatt „Alle Themen“ per Tastatur, Filter über die URL, Tab-Leiste ab
  1024 px ausgeblendet, klebende Offsets, „Größere Schrift“ ohne Überlauf.
- 15 Routen ohne fehlendes oder leeres Icon.
- Nachher-Aufnahmen in 1440 und 390 px ohne Konsolenfehler und ohne waagrechten
  Überlauf; die erste Themenkarte steht mobil im ersten Bildschirm.
- Kontrast: Kategorie-Töne mindestens 4,5:1 auf Creme und Weiß (Wirtschaft
  braucht −0,40 statt −0,35); Creme auf den Bändern mindestens 8,4:1; Creme auf
  den Gremienfarben 11,6 bis 12,6:1.

## Gefundene Fehler

- Ab dem zweiten Thema war der Chip in einer Themenkarte ein verschachtelter Link
  (`.map(categoryChip)` gab den Index als `asLink` weiter).
- `termine.json` wurde von der App nicht geladen.
- Der Kontakt-Text behauptete, alle Ergebnisse entsprächen den Niederschriften.
- `.stat-value` in `css/style.css` trifft keine Stelle mehr (nicht geändert).

## Offen

- Die Farben der Gremien sind gesetzt, aber nicht bestätigt: Schema 1 aus der
  Vorlage. Die Alternativen bräuchten neue Farben für Kalenderpunkte und
  Diagramme.
- Gremium als Kategoriezeile gibt es im Kalenderblatt und im Sitzungskopf; für
  Suche, Datenlage und Profil-Zeitstrahl ist es offen.
- Ink-Art je Thema (Idee vom 15.09.2026).
- Der Portal-Einschub „In eigener Sache“ schließt noch mit dem Stripe ab.

## Für die nächsten Proben

- **Band über die ganze Breite** im Kopf: `margin-inline: calc(50% - 50vw)` plus
  `padding-inline: calc(50vw - 50%)`, dazu `body { overflow-x: clip }`, weil
  `50vw` eine sichtbare Scrollleiste mitzählt. Folgen Karten, greift
  `:has(+ …)` für die Überlappung, sonst schließt das Band normal ab.
- **Kein Stripe** an Zwischenebenen, wenn er schon im Kopf steht.
- **Keine einseitige Farbkante** an Karten, auch nicht als Datenmarke.
- **Kategoriezeile statt Wiederholung:** Steht das Gremium in der Zeile, heißt der
  Titel darunter nur noch „2. Sitzung“ plus Datum.
- Ein `hidden` gebautes Gegenstück (die kompakte Termin-Zeile) hilft beim
  Vergleich, muss aber vor dem Merge wieder raus.
