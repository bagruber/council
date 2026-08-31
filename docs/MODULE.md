# Modul-Schnitt der App

Seit Phase 4 des Plattform-Umbaus (siehe moosburg-eu/UMBAU.md) ist die
frühere `js/app.js` — 145 KB in einer Datei — in ES-Module geschnitten.
Kein Build-Step: der Browser lädt die Module direkt, `index.html` bindet
`js/app.js` als `type="module"` ein. `core.js` und `parliament.js` bleiben
klassische Skripte mit den Globalen `Council` und `VoteVis`; sie laufen vor
den Modulen und sind aus ihnen heraus sichtbar.

| Modul | Verantwortung |
|---|---|
| `app.js` | Einstieg: Daten laden, Einstellungen, Verdrahtung, Router starten |
| `daten.js` | die sieben JSON-Dateien, Nachschlage-Maps, Daten-Helfer |
| `hilfen.js` | Datums- und Zeitraum-Formatierung |
| `routing.js` | Hash-Routen, Tabs, Seiten-Chrome |
| `suche.js` | globale Suche, Tag-Pillen, Gremien-Suche |
| `views/themen.js` | Startseite, Themenfelder, Dossiers; Brotkrumen und Presse-Links |
| `views/sitzungen.js` | Sitzungsseite mit Tagesordnung |
| `views/kalender.js` | Kalender-Tab |
| `views/voten.js` | der eingebettete Abstimmungsblock |
| `views/statistik.js` | Sitzungsstatistik, Datenlage, Presseschau samt Diagrammen |
| `views/gremien.js` | Gremien-Tab |
| `views/profil.js` | Personenprofil samt Abstimmungsstatistik und Zeitstrahl |
| `views/fraktion.js` | Fraktionsseite samt Geschlossenheit |
| `views/naehe.js` | Ähnlichkeitsmaß, Nähe-Matrix, Nähe-Netz |

Drei Konventionen halten den Schnitt zusammen:

1. **`daten.js` exportiert live bindings.** Die Maps stehen erst nach
   `ladeDaten()`; `app.js` wartet darauf, bevor irgendetwas rendert. Module
   dürfen importierte Daten deshalb nie beim Laden lesen, nur in Funktionen.
2. **Ehemals frei laufende Verdrahtung liegt in init-Funktionen**
   (`initRouting`, `initSuche`, `initStatistik`, `initKalender`,
   `initNaehe`), die `app.js` nach dem Laden in der alten Reihenfolge
   aufruft.
3. **Zirkuläre Importe zwischen `routing.js` und den Views sind gewollt**
   und unkritisch, solange Regel 1 gilt: alle Aufrufe passieren erst nach
   der Initialisierung.

Caching: die Module laden einander über relative Pfade ohne
Cache-Busting-Parameter; die `.htaccess` im Projektstamm setzt deshalb
`no-cache` für HTML, CSS, JS und JSON — der Browser fragt nach und bekommt
304, solange sich nichts geändert hat.
