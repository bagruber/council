# Modul-Schnitt der App

Alles ist ES-Modul, und es gibt keinen Build-Step: der Browser lädt die
Module direkt, `index.html` bindet nur `js/app.js` als `type="module"` ein.
Damit nach einem Deploy niemand auf einer alten Datei sitzenbleibt, schreibt
`python scripts/stamp_assets.py` eine Import Map, die jeden Modulpfad auf
seine gestempelte Fassung umbiegt.

| Modul | Verantwortung |
|---|---|
| `app.js` | Einstieg: Daten laden, Einstellungen, Verdrahtung, Router starten |
| `daten.js` | die neun JSON-Dateien, Nachschlage-Maps, das Sitzungsregister und die eine Zählstelle (`bestand()`); leitet ausserdem ab, was doppelt stand: `vote.date` von der Sitzung, `member.from`/`to`/`party`/`role` vom ersten und letzten Mandatsabschnitt |
| `core.js` | `Council`: Mandate, Gremienbesetzung, Vote-Status, Herkunft — siehe `docs/CORE.md` |
| `html.js` | das `html`-Template, das eingesetzte Werte maskiert |
| `aehnlichkeit.js` | das Ähnlichkeitsmaß über geteilte Beschlüsse, ohne Zugriff aufs Dokument |
| `parliament.js` | `VoteVis`: Ergebnisbalken und Halbrund, reines SVG |
| `hilfen.js` | Datums- und Zeitraum-Formatierung, Töne der Themenfarben |
| `routing.js` | Hash-Routen, Tabs, Seiten-Chrome |
| `kopf.js` | Kopf: „Über das Projekt“ als Panel, mobil als Blatt |
| `suche.js` | globale Suche, Tag-Pillen, Gremien-Suche |
| `views/themen.js` | Startseite, Themenfelder, Dossiers; Brotkrumen und Presse-Links |
| `views/sitzungen.js` | Sitzungsseite mit Tagesordnung |
| `views/kalender.js` | Kalender-Tab |
| `views/voten.js` | der eingebettete Abstimmungsblock |
| `views/diagramme.js` | Werkzeug der Diagramme: Farben, Kartenrahmen, Tooltip, Median |
| `views/statistik.js` | Sitzungsstatistik samt Dauer-Diagrammen und Nähe-Bildern |
| `views/datenlage.js` | das Sitzungsregister und die Herkunftsstufen |
| `views/presse.js` | Presseschau |
| `views/gremien.js` | Gremien-Tab |
| `views/profil.js` | Personenprofil samt Abstimmungsstatistik und Zeitstrahl |
| `views/fraktion.js` | Fraktionsseite samt Geschlossenheit |
| `views/naehe.js` | Nähe-Matrix und Nähe-Netz, gezeichnet |

Vier Konventionen halten den Schnitt zusammen:

1. **`daten.js` exportiert live bindings.** Die Maps stehen erst nach
   `ladeDaten()`; `app.js` wartet darauf, bevor irgendetwas rendert. Module
   dürfen importierte Daten deshalb nie beim Laden lesen, nur in Funktionen.
2. **Verdrahtung liegt in init-Funktionen** (`initRouting`, `initSuche`,
   `initStatistik`, `initKalender`, `initNaehe`), die `app.js` nach dem Laden
   in fester Reihenfolge aufruft.
3. **Zirkuläre Importe zwischen `routing.js` und den Views sind gewollt**
   und unkritisch, solange Regel 1 gilt: alle Aufrufe passieren erst nach
   der Initialisierung.
4. **Markup entsteht über `html`**, nicht über blanke Template-Literale.
   Eingesetzte Werte werden maskiert; verschachtelte `html``-Stücke und
   Listen davon kommen durch, weil sie schon Markup sind. Wo wirklich eine
   Zeichenkette mit Markup eingesetzt werden soll, sagt `roh()` das
   ausdrücklich — und macht es zu einer Stelle, die man beim Lesen sieht.

Was rechnet und was zeichnet, ist getrennt: `aehnlichkeit.js` kennt kein
Dokument und ist deshalb ohne Browser prüfbar (`tests/naehe.test.mjs`),
`views/naehe.js` zeichnet nur.

Caching: die Module laden einander über die Import Map mit Inhaltskennung;
die `.htaccess` im Projektstamm setzt zusätzlich `no-cache` für HTML, CSS, JS
und JSON — der Browser fragt nach und bekommt 304, solange sich nichts
geändert hat.
