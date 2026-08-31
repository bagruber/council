# Stadtratstransparenz Moosburg

Eine Web-App, die das Abstimmungsverhalten im Moosburger Stadtrat (und in seinen
Ausschüssen) öffentlich nachvollziehbar macht. Themen, Sitzungen, Anträge,
Pressemitteilungen und Mitglieder-Profile sind miteinander verzahnt und über
eine Suche und Filter zugänglich.

🔗 **Live:** [bagruber.github.io/council](https://bagruber.github.io/council/)

> ⚠️ **Hinweis:** Dieses Projekt ist **nicht** offiziell durch die Stadt
> Moosburg a.d. Isar getragen oder beauftragt. Es ist ein privates
> Public-Interest-Technology-Vorhaben zur Förderung von Transparenz in der
> Lokalpolitik.
>
> Inhalte werden weitgehend automatisiert aus den öffentlichen Niederschriften
> extrahiert. Trotz sorgfältiger Prüfung können Übertragungsfehler entstehen —
> im Zweifel sind die [Original-Niederschriften der Stadt
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

- Vanilla JS, keine Frameworks, keine npm-Runtime-Dependencies.
- D3 nicht mehr benötigt — die Parlament-Visualisierung läuft auf eigenem
  Pure-SVG-Code in `js/parliament.js`.
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
│   ├── core.js             # geteilte Vote-/Period-Logik (siehe docs/CORE.md)
│   ├── parliament.js       # Sitzverteilungs-Visualisierung
│   ├── app.js              # Einstieg als ES-Modul (siehe docs/MODULE.md)
│   ├── daten.js            # JSON-Bestand und Nachschlage-Maps
│   ├── routing.js          # Hash-Routen, Tabs
│   ├── suche.js            # globale Suche
│   ├── hilfen.js           # Format-Helfer
│   └── views/              # eine Datei je Seite
├── data/
│   ├── members.json        # Mitglieder, Parteien, Gremien, Medien
│   ├── sessions.json       # Sitzungen + Tagesordnung
│   ├── votes.json          # Einzel-Abstimmungen
│   ├── topics.json         # Themen + Timeline-History
│   ├── tags.json           # Themen-Kategorien
│   ├── press.json          # Presseartikel
│   ├── termine.json        # angekündigte, noch nicht gehaltene Sitzungen
│   └── niederschriften/    # PDFs der Original-Niederschriften
├── img/
│   ├── members/            # Profilbilder (WebP, 1x + 2x)
│   │   └── originals/      # PNG-Master-Kopien
│   └── topics/             # Thumbnails für Themen-Cards
├── scripts/
│   ├── validate_data.py    # Integritätscheck über alle data/*.json
│   ├── build_data.py       # konsolidiertes bundle.json (optional)
│   ├── compress_member_images.py
│   └── add_*_data.py       # historische Integrations-Skripte
├── .claude/skills/         # Skill-Dokumentation für Pflege per LLM
└── docs/CORE.md            # Walkthrough zur geteilten Vote-Logik
```

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
python scripts/validate_data.py
```

Bei Exit-Code 0 ist alles konsistent. Warnings sind Hinweise, keine Blocker.

## Datenmodell (Kurzfassung)

```jsonc
// data/members.json
{
  "members": [
    {
      "id": "gruber",
      "name": "Benedict Arya Gruber",
      "firstName": "Benedict", "lastName": "Gruber",
      "party": "fresh",
      "from": "2022-10-24",
      "role": "councillor"
    }
  ],
  "parties": [...],
  "bodies": [
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
}
```

Stamm-Annahme: **Sitze sind nie unbesetzt.** Nachrücker:innen übernehmen am
Folgetag des Ausscheidens — eindeutig per `occupants[]`-Historie.

Mehr Detail dazu im [`docs/CORE.md`](docs/CORE.md), das auch die zentrale
Vote-Status-Logik (yes / no / absent / inferiert / unknown) beschreibt.

## Geschwister-Apps

Teil einer kleinen Familie von Anwendungen rund um Transparenz und
Datenarbeit in der Kommune Moosburg:

- **bagruber/council** *(dieses Repo)* — die öffentliche Transparenz-App.
- **[bagruber/council-voting-tool](https://github.com/bagruber/council-voting-tool)** —
  Live-Erfassung von Anwesenheit und Abstimmungen während der Sitzung.
  Nutzt das gleiche `members.json`-Datenmodell.
- **[bagruber/datahub](https://github.com/bagruber/datahub)** — interaktives
  Umfrage- und Daten-Dashboard.

Designsprache (Moosburg-Rot, Gold-Akzent, warmes Off-White) ist über alle
drei Apps konsistent.

## Lizenz & Verantwortung

Code: MIT. Daten: Auszug aus öffentlich zugänglichen Niederschriften der Stadt
Moosburg — die Niederschriften selbst sind die maßgebliche Quelle.

Verantwortlich für Inhalt und Betrieb: Benedict Arya Gruber, von 2022 bis 2026
Digitalisierungsreferent der Stadt Moosburg a.d. Isar. Dieses Projekt entsteht
unabhängig in privater Initiative.

Fehler oder Verbesserungsvorschläge bitte als
[GitHub-Issue](https://github.com/bagruber/council/issues) melden.
