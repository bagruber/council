# Stadtratstransparenz Moosburg

Eine Web-App, die das Abstimmungsverhalten im Moosburger Stadtrat (und in seinen
Ausschüssen) öffentlich nachvollziehbar macht. Themen, Sitzungen, Anträge,
Pressemitteilungen und Mitglieder-Profile sind miteinander verzahnt und über
eine Suche und Filter zugänglich.

**Live:** [moosburg.eu/stadtrat](https://moosburg.eu/stadtrat/) und
[bagruber.github.io/council](https://bagruber.github.io/council/)

> **Hinweis:** Dieses Projekt ist **nicht** offiziell durch die Stadt
> Moosburg a.d. Isar getragen oder beauftragt. Es ist ein privates
> Public-Interest-Technology-Vorhaben zur Förderung von Transparenz in der
> Lokalpolitik.
>
> Die Inhalte stammen aus den öffentlichen Niederschriften der Stadt. Ein
> Sprachmodell liefert beim Einarbeiten den ersten Aufschlag, ein Mensch
> korrigiert und gibt frei; wie genau, erklärt die Seite
> [„So entsteht diese Seite"](https://moosburg.eu/stadtrat/#/methodik). Trotz
> sorgfältiger Prüfung können Übertragungsfehler entstehen — im Zweifel sind
> die [Original-Niederschriften der Stadt
> Moosburg](https://moosburg.ratsinfomanagement.net/) verbindlich.

## Was zeigt die App?

- **Themen:** zentrale Navigationseinheit. Jedes Thema (Bahnhof, Auf dem Plan,
  Wachbaracken, Energie, …) hat eine chronologische Timeline aus Voten,
  Meilensteinen, Anträgen und Presseberichten.
- **Sitzungen:** alle StR-, BPU- und HVFA-Sitzungen mit Tagesordnung und
  Einzel-Voten.
- **Abstimmungen:** Plenumsvisualisierung mit Sitzfärbung nach Partei und
  individuellem Verhalten (Ja/Nein/Abwesend, bei einstimmigen Anonym-Voten
  zusätzlich abgeleitet).
- **Mitglieder-Profile:** Mandat, Funktionen, Parteizugehörigkeits-Historie,
  aggregierte Abstimmungsstatistik, Anträge.
- **Presse:** zentrale Sammlung von Artikeln, verknüpft mit Sitzungen, Themen
  oder Anträgen.

## Stack

Bewusst minimal:

- Vanilla JS als ES-Module, kein Build-Step, keine Laufzeit-Abhängigkeit.
  Der Browser lädt die Module direkt; `python scripts/stamp_assets.py` hängt
  nach jeder Änderung an CSS oder JS eine Inhaltskennung an die Pfade.
- Die Parlaments-Visualisierung ist eigener SVG-Code in `js/parliament.js`,
  kein D3.
- Hash-basiertes Routing (`#/topic/t3`, `#/member/gruber`, `#/session/sr_20240612`).
- Statische JSON-Dateien als Datenquelle (siehe `data/`).
- Deployment aus `main`, sowohl auf GitHub Pages als auch nach
  `moosburg.eu/stadtrat/`. Siehe [PLATTFORM.md](PLATTFORM.md).

## Projektstruktur

```
council/
├── index.html              # Single-page Shell
├── css/style.css
├── js/
│   ├── app.js              # Einstieg (siehe docs/MODULE.md)
│   ├── core.js             # geteilte Mandats- und Vote-Logik (docs/CORE.md)
│   ├── daten.js            # JSON-Bestand, Nachschlage-Maps, Sitzungsregister
│   ├── html.js             # Markup-Template mit Escaping
│   ├── aehnlichkeit.js     # das Ähnlichkeitsmaß, ohne DOM
│   ├── parliament.js       # Ergebnisbalken und Halbrund, reines SVG
│   ├── routing.js          # Hash-Routen, Tabs
│   ├── suche.js            # globale Suche
│   ├── hilfen.js           # Format-Helfer
│   └── views/              # eine Datei je Seite
├── data/
│   ├── members.json        # Mitglieder mit Mandatsabschnitten
│   ├── parties.json        # Fraktionen + beide Sitzordnungen
│   ├── bodies.json         # Gremien + Besetzung je Periode
│   ├── media.json          # Zeitungen und Sender
│   ├── sessions.json       # Sitzungsregister + Tagesordnung
│   ├── votes.json          # Einzel-Abstimmungen
│   ├── topics.json         # Themen + Timeline-History
│   ├── tags.json           # Themen-Kategorien
│   ├── press.json          # Presseartikel
│   ├── schema/             # JSON Schema je Datei
│   └── niederschriften/    # PDFs der Original-Niederschriften
├── img/
│   ├── members/            # Profilbilder (WebP, 1x + 2x)
│   └── topics/             # Bilder für Themen-Timelines
├── fonts/                  # self-hosted woff2, keine CDN-Requests
├── tests/                  # node --test, ohne Abhängigkeit
├── scripts/
│   ├── validate_data.py    # Integritätscheck über alle data/*.json
│   ├── build_data.py       # konsolidiertes bundle.json (optional)
│   ├── stamp_assets.py     # Inhaltskennung an CSS-/JS-Pfade
│   ├── hole-tokens.mjs     # Farbkanon aus bagruber/moosburg-design holen
│   └── crawl/              # Presserecherche
├── .claude/skills/         # Skill-Dokumentation für Pflege per LLM
└── docs/CORE.md            # Walkthrough zur geteilten Vote-Logik
```

Nicht im Repo, aber lokal vorhanden: `quellen/` (Rohquellen und
Arbeitsnotizen) und `img/members/originals/` (PNG-Vorlagen der Porträts).
GitHub Pages liefert `main` roh aus — was eingecheckt ist, ist öffentlich.

## Lokal entwickeln

```bash
# Beliebiger statischer Webserver, z.B.
npx serve
# oder
python -m http.server 8000
```

App im Browser unter `http://localhost:8000/` öffnen. Kein Build-Step, keine
Compile-Phase — Änderungen an JS/CSS/Daten sind nach Reload sichtbar.

## Daten pflegen

Die Hauptarbeit am Projekt ist das laufende Einarbeiten neuer Niederschriften
und Pressemitteilungen. Pro Aufgabe gibt es eine
[Skill-Beschreibung](.claude/skills/) (auch ohne LLM als Anleitung lesbar):

- `niederschrift-einarbeiten` — PDF → Sitzung + Voten + Topic-History
- `presseartikel-einarbeiten` — Artikel-URL → press.json + Verlinkungen
- `member-update` — Personalwechsel im Stadtrat oder in Ausschüssen
- `antrag-einarbeiten` — Stadtratsantrag ins Member-Profil
- `topic-anlegen` — neues Themenfeld (nur nach Absprache)
- `validate-data` — Integritätscheck nach jeder Änderung

Nach jeder Datenänderung:

```bash
pip install -r scripts/requirements.txt   # einmalig
python scripts/validate_data.py
```

Geprüft wird zweierlei: die Form gegen `data/schema/*.schema.json` und der
Zusammenhang zwischen den Dateien. Bei Exit-Code 0 ist alles konsistent;
Warnings sind Hinweise, keine Blocker.

Die geteilte Vote- und Mandatslogik ist getestet:

```bash
node --test "tests/*.test.mjs"
```

## Datenmodell (Kurzfassung)

Mandat, Fraktion und Rolle stehen als eine geordnete Liste von Abschnitten am
Mitglied. Eine Lücke dazwischen ist eine Unterbrechung des Mandats, kein
Abstand heißt Fraktions- oder Rollenwechsel, und wo zwei Abschnitte sich an
ihrer Grenze berühren, gilt der spätere.

```jsonc
// data/members.json
[
  {
    "id": "strobl",
    "firstName": "…", "lastName": "Strobl",
    "mandates": [
      { "from": "2023-07-24", "party": "linke", "role": "councillor" }
    ],
    "succeeds": ["john"]
  }
]
```

```jsonc
// data/bodies.json
[
  { "id": "bpu", "name": "Bau-, Planungs- und Umweltausschuss",
    "seatConfigs": [
      { "from": "2020-05-01", "to": "2026-04-30",
        "chair": "dollinger",
        "vicechairs": [...],
        "seats": [
          { "occupants": [
              { "member": "wittmann", "from": "2020-05-01", "to": "2021-10-24" },
              { "member": "gruebl",   "from": "2021-10-25", "to": "2024-10-21" },
              { "member": "hobmaier", "from": "2024-10-22" }
            ],
            "sub": "gruber"
          }
        ]
      }
    ]
  }
]
```

Stamm-Annahme: **Sitze sind nie unbesetzt.** Nachrücker:innen übernehmen am
Folgetag des Ausscheidens — eindeutig per `occupants[]`-Historie.

Die vollständige Form aller Dateien steht als JSON Schema in
[`data/schema/`](data/schema/). Mehr Detail im [`docs/CORE.md`](docs/CORE.md),
das auch die Vote-Status-Logik beschreibt.

## Geschwister-Apps

Teil einer kleinen Familie von Anwendungen rund um Transparenz und
Datenarbeit in der Kommune Moosburg:

- **bagruber/council** *(dieses Repo)* — die öffentliche Transparenz-App.
- **[bagruber/council-voting-tool](https://github.com/bagruber/council-voting-tool)** —
  Live-Erfassung von Anwesenheit und Abstimmungen während der Sitzung.
  Nutzt das gleiche `members.json`-Datenmodell.
- **[bagruber/datahub](https://github.com/bagruber/datahub)** — interaktives
  Umfrage- und Daten-Dashboard.

Die Designsprache ist über alle drei Apps konsistent; der Kanon liegt in
**[bagruber/moosburg-design](https://github.com/bagruber/moosburg-design)**
und kommt per `node scripts/hole-tokens.mjs` als `css/tokens.css` herein.

## Lizenz & Verantwortung

Alles nichtkommerziell:

| | |
|---|---|
| **Code** | [PolyForm Noncommercial 1.0.0](LICENSE) |
| **Daten und Texte** | [CC BY-NC 4.0](LICENSE-DATA) |

**Zusätzlich für die Presse:** Über die Lizenz hinaus dürfen Medien die Daten
und Grafiken für redaktionelle Berichterstattung nutzen, auch wenn sie
kommerziell arbeiten, sofern die Quelle genannt wird.

Nicht davon erfasst: die Niederschriften in `data/niederschriften/` als
amtliche Werke der Stadt, die Schriften in `fonts/` (SIL OFL) und die
Phosphor-Icons (MIT). Weil die Lizenzen nichtkommerziell sind, ist der
Quellcode zwar einsehbar, aber nicht Open Source im Sinne der OSI —
„quelloffen" trifft es.

Die Daten sind ein Auszug aus öffentlich zugänglichen Unterlagen der Stadt
Moosburg; die Niederschriften selbst bleiben die maßgebliche Quelle.

Verantwortlich für Inhalt und Betrieb: Benedict Arya Gruber, von 2022 bis 2026
Digitalisierungsreferent der Stadt Moosburg a.d. Isar. Dieses Projekt entsteht
unabhängig in privater Initiative.

Fehler oder Verbesserungsvorschläge bitte als
[GitHub-Issue](https://github.com/bagruber/council/issues) melden.
