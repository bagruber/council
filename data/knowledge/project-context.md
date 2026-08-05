# Projektkontext – Council Transparency App Moosburg a.d. Isar

> Stand: 2026-08-05. Dient als Restart-Dokument für LLMs.
> Datenstand: 54 Mitglieder · 129 Sitzungen (20.01.2020–18.05.2026) · 961 Abstimmungen · 27 Dossiers · 19 Presseartikel

---

## Worum geht es

Eine Transparenz-App für den Stadtrat Moosburg a.d. Isar (Bayern). Ziel: Abstimmungsverhalten, Themen-Timelines und Sitzungsgeschichte öffentlich und durchsuchbar machen. Der Betreiber ist selbst Stadtrat (fresh-Fraktion, seit Oktober 2022 im Amt nach Nachrücken für Neumayr).

Lokale URL zum Testen: `npx serve` im Root.
Keine Dependencies im Frontend – Vanilla JS, Parliament-Chart ist pure SVG (kein D3). Fonts self-hosted in `fonts/`.

---

## Tech-Stack

- `index.html` + `js/core.js` + `js/app.js` + `js/parliament.js` + `css/style.css` + `css/fonts.css`
- `js/core.js` (`Council`): geteilte Perioden- & Vote-Status-Logik (siehe `docs/CORE.md`)
- Hash-basiertes Routing: `#/member/{id}`, `#/topic/{id}`, `#/feld/{id}`, `#/session/{id}`, Tag-Filter `#/?tags={id},{id}`
- Icons: Lucide-Sprite, inline in `index.html`. Neu bauen mit `scripts/build_icon_sprite.mjs`
  (braucht `lucide-react` aus einem Nachbarprojekt). IDs heißen `#i-{name}`.
- `const SHOW_PRONOUNS = true/false` in `js/app.js`

**Kein Hash-Anker möglich** — der Hash trägt die Route. Sprünge innerhalb einer Seite
laufen über `scrollIntoView` plus kurzes Aufblitzen (`.tl-flash`), siehe `renderFigures`.

---

## Datenquellen (alle handgepflegt)

| Datei | Inhalt |
|---|---|
| `data/members.json` | Alle Stadtratsmitglieder, Parteien, Mandate, Ausschusssitze |
| `data/sessions.json` | Sitzungen mit Tagesordnung und Absenzen |
| `data/votes.json` | Abstimmungen mit Einzel- oder Gesamtstimmen |
| `data/topics.json` | Themen mit Timeline-History |
| `data/tags.json` | Tags für Topics |
| `data/press.json` | Presseartikel (ID-Schema: `{media}_{YYYY-MM-DD}_{slug}`) |
| `data/sessionlengths.json` | Beginn und Ende **aller** Sitzungen seit Mai 2020, auch der nicht erfassten |
| `data/bundle.json` | Kombiniertes Paket (Build-Artefakt via `scripts/build_data.py`) |

`data/sitzungenlaenge_2020-2026.json` ist dieselbe Liste mit deutschen Schlüsseln und
wird von nichts gelesen — Altlast des Imports.

## Datenlage und Presseschau

Zwei Seiten machen den Bestand selbst zum Gegenstand:

- **`#/datenlage`** — jede Sitzung, die stattgefunden hat, aus `sessionlengths.json` und
  `sessions.json` zusammengeführt. Zeigt Dauer, ob eine Niederschrift vorliegt, wie viele
  Abstimmungen erfasst sind und wie sich deren Herkunftsstufen verteilen. Sitzungen ohne
  Niederschrift stehen bewusst mit drin — aktuell **113 von 168**, die Lücke sind fast
  ausschließlich HVFA-Haushaltsberatungen und BPU-Sitzungen.
- **`#/presse`** — alle verlinkten Zeitungsartikel, nach Jahr, mit Rückverweis auf Sitzung,
  Dossier oder Antrag (`pressContext()` dreht die Verlinkung um).

Die Niederschrift-PDFs lagen bis August 2026 ungenutzt im Repo; Sitzungsseite und
Datenlage verlinken sie jetzt über `protocolUrl()` (`SR_`/`BPU_`/`HVF_` + `YYYYMMDD`).
Die Zuordnung Sitzung ↔ PDF ist 1:1, deshalb gilt „in `sessions.json` erfasst" als
gleichbedeutend mit „Niederschrift liegt vor".

---

## Datenstruktur-Konventionen

### sessions.json

```json
{
  "id": "sr_20241021",
  "date": "2024-10-21",
  "type": "stadtrat",          // "stadtrat" | "bpu" | "hvfa" | "pa" | "rpa"
  "title": "...",
  "absent": ["gruebl", "..."],  // Stadtrat: alle Abwesenden; BPU: nur ohne Vertretung
  "substitutes": [              // nur BPU/Ausschüsse
    { "member": "gruebl", "substitute": "gruber" }
  ],
  "agenda": [
    {
      "number": "4.3.1",
      "title": "Kurztitel",
      "voteId": "sr_20241021_03",   // optional
      "topicId": "t5",               // optional
      "type": "formal" | "discussion" // wenn kein Vote
    }
  ]
}
```

**Wichtig bei BPU-Sitzungen:** `absent` = abwesend OHNE Vertretung; wer eine Vertretung hat, steht nur in `substitutes`.

### Drei Erfassungsstufen je Sitzung

| Stufe | Kennzeichen | Anwesenheit |
|---|---|---|
| **Niederschrift** | PDF in `data/niederschriften/`, kein `source`-Feld | vollständig |
| **Beschlussauszug** | `"source": {"kind": "webauszug", "url": "https://www.moosburg.de/…"}` | **fehlt** |
| **nichts** | nur in `sessionlengths.json` | – |

Manche BPU-Sitzungen erscheinen nie als Niederschrift, sondern nur als Beschlussauszug
auf der Website der Stadt. Verlinkt wird dann die Seite der Stadt, nicht eine Datei —
niemals eine selbst erzeugte PDF. Die Beschlüsse stehen dort, die Anwesenheitsliste nicht.

Daraus folgt für die Ableitung:
- **Alle Sitze haben mitgestimmt** (BPU: 12) → alle regulären Sitze waren da, Vote wird
  `named` mit vollständiger Besetzung.
- **Sonst** → `anonymous` und `inferable: false`. Ein Sitz war leer, aber welcher, steht
  nirgends. Kein `absent`-Array setzen — leer hieße „alle da".

`scripts/mark_inferable.py` setzt das durch: die 90 %-Schwelle setzt eine
Anwesenheitsliste voraus und gilt für Beschlussauszüge nicht.

Eine Zusatzregel aus dem Import vom August 2026: erreicht **irgendeine** Abstimmung der
Sitzung die volle Sitzzahl, war niemand ganztägig abwesend → `absent: []` ist belegt.
Einzelne Voten mit weniger Stimmen sind dann kurzfristige Abwesenheiten.

Im Bestand: 17 Beschlussauszüge (16 BPU-Sitzungen 2020–2025 aus
`scripts/import_bpu_webauszug.py`, dazu BPU 13.04.2026). „Mehrfachbeschluss" im Auszug
heißt: mehrere Einzelbeschlüsse ohne ausgewiesene Zahlen — dafür entsteht **kein** Vote,
nur ein Tagesordnungspunkt mit `note`.

**Vorsicht bei „Beschluss: Abgelehnt".** Das bezieht sich auf das Vorhaben, nicht auf die
Abstimmung. 12:0 heißt, der Beschluss *zur Ablehnung* ging einstimmig durch.
`result: "rejected"` nur setzen, wenn Nein überwiegt.

### votes.json

```json
{
  "id": "sr_20241021_03",
  "sessionId": "sr_20241021",
  "topicId": "t5",           // null wenn kein Thema
  "date": "2024-10-21",
  "title": "Kurzbezeichnung Beschluss",
  "text": "Volltext des Beschlusses.",
  "type": "named",           // "named" | "anonymous"
  "result": "rejected",      // optional: "rejected" | "passed" (nur bei anonymen)
  "results": {
    // named:
    "yes": ["dollinger", "gruber", ...],
    "no": ["stanglmaier", ...],
    "absent": ["beubl", ...]
    // anonymous:
    // "yes": 15, "no": 7, "absent": 3
  },
  "source":    { "tier": "tracked", "by": "gruber", "pressVerified": true, "pressId": "..." },
  "excluded":  [{ "member": "weber", "reason": "beteiligung" }],
  "inferable": false,        // sperrt die Ableitung bei Einstimmigkeit
  "note":      "Erklärung, warum weniger Stimmen als Anwesende"
}
```

### Herkunft des Abstimmungsverhaltens (`source.tier`)

Vier Stufen, absteigend nach Belastbarkeit. Die Oberfläche nennt sie in einer
stillen Fußnote unter dem Vote-Block (`renderVoteSource`).

| Stufe | Bedeutung | Bestand |
|---|---|---|
| `protocol-explicit` | Die Niederschrift nennt jeden Namen (namentliche Abstimmung) | 6 |
| `protocol-implicit` | Einstimmig, also aus der Anwesenheit ableitbar | 537 |
| `press` | Aus einem Presseartikel rekonstruiert, `pressId` verweist darauf | 0 |
| `tracked` | Von einer benannten Person mitgeschrieben (`by`), optional presseverifiziert | 57 |

247 Abstimmungen haben keine Stufe — dort ist nur das Gesamtergebnis bekannt.

### Sonderzustände (`excluded[]`)

Nur wenige Beschlüsse pro Wahlperiode, aber ohne sie wird die Statistik falsch.
`Council.voteStatus()` löst sie vor der Sitzungsabwesenheit auf.

| `reason` | Anzeige | Fall |
|---|---|---|
| `beteiligung` | „bef." (befangen) | Persönliche Beteiligung, Art. 49 GO |
| `enthaltung` | „enth." | Ausdrückliche Enthaltung im Protokoll |
| `nicht_stimmberechtigt` | „n.b." | z.B. neu Gewählte bei der Genehmigung alter Niederschriften |
| `kurzfristig abwesend` | „–" | Kurz raus, zählt als abwesend |

Keiner dieser Zustände zählt in der Statistik als Nein — sie landen im Eimer
„nicht abgestimmt" (`statKey()`).

### Ableitung bei Einstimmigkeit (`scripts/mark_inferable.py`)

Einstimmig heißt: wer da war, hat so gestimmt. Das gilt aber nur, wenn auch alle
mitgestimmt haben. Regel: **abgeleitet wird ab 90 % Beteiligung der Stimmberechtigten**,
und die Ableitung ist in der Oberfläche mit `*` markiert. Zwei Sonderfälle werden
vorher herausgerechnet:

- **Wechselsitzungen** — wer an diesem Tag ausscheidet, teilt sich den Sitz mit der
  Person, die nachrückt. Ein Sitz, nicht zwei. Betraf 22 Abstimmungen.
- **Entlastung des Aufsichtsrats der Kläranlage** — dessen Mitglieder stimmen über die
  eigene Entlastung nicht mit. Wer dem AR wann angehörte, geben die Daten nicht her;
  die Lücke ist erklärt, aber nicht auflösbar. Diese 5 Voten bleiben ohne Ableitung
  und tragen die Begründung in `note`.

Aktuell 39 gesperrte Voten. Die Sperre kostet Information: eine Lücke von einer
Stimme unter 22 würde 21 richtige Ableitungen verwerfen, um eine falsche zu
vermeiden — deshalb die Schwelle statt einer harten Regel.

**Gesamtstimmen:** 25 Mitglieder (24 StR + 1 BM Dollinger). Bei BPU/HVFA sind es je nach Gremium weniger.

**Einstimmige Votes (named):** `no: []`, Text enthält „Einstimmig".

### members.json (Struktur)

Jedes Mitglied hat u.a.:
- `id` (z.B. `"gruber"`, `"stanglmaier"`)
- `name`, `party` (z.B. `"fresh"`, `"CSU"`, `"SPD"`, `"FW"`, `"Grüne"`, `"Linke"`)
- `from`, `to` (Amtszeiten, ISO-Datum), `periods[]` bei Mandaten mit Pause
- `partyHistory[]` bei Fraktionswechsel — das Halbrund färbt den Sitz danach
- `profile.motions[]` – eingebrachte Anträge
- `seatConfigs` – Ausschusssitze und Funktionen

### Kerndaten zur Person (`profile`)

```json
"birthYear": 1994,
"occupation": "Zimmerer",
"district": "Pfrombach",
"elections": [
  { "year": 2026, "votes": 1834, "listRank": 12, "resultRank": 3 }
]
```

Alle Felder optional; die Sektion „Zur Person" auf dem Profil erscheint nur, wenn
mindestens eins gefüllt ist. Ratsjahre werden aus `periods` gerechnet, nicht gespeichert.

`listRank` ist der Platz auf der Liste, `resultRank` der Platz nach Auszählung — die
Differenz zeigt, wen die Wählerinnen und Wähler nach vorn gerückt haben. Beim Ortsteil
nur der Ortsteil, nie die Adresse.

---

## Gremien und Mitgliederzahl

| Gremium | Kürzel | Mitglieder |
|---|---|---|
| Stadtrat | `sr` | 25 (24 StR + BM) |
| Bau-, Planungs- und Umweltausschuss | `bpu` | ~12 |
| Hauptverwaltungs- und Finanzausschuss | `hvfa` | ~9 |
| Personalausschuss | `pa` | ~7 |
| Rechnungsprüfungsausschuss | `rpa` | ~5 |

---

## Mitglieder-IDs (wichtigste)

| ID | Name | Partei | Besonderheit |
|---|---|---|---|
| `dollinger` | Josef Dollinger | CSU | 1. Bürgermeister |
| `hadersdorfer` | Michael Hadersdorfer | CSU | 2. BM |
| `stanglmaier` | ... | CSU | 3. BM |
| `gruber` | Benedict Gruber | fresh | App-Betreiber, 10.10.2022–30.04.2026 (nachgerückt für Neumayr) |
| `neumayr` | ... | fresh | bis 10.10.2022 |
| `marschoun` | ... | SPD | 2014–2020 **und** wieder ab 2026 — einziges Mandat mit Pause |
| `mader` | ... | CSU | 1. Bürgermeister ab 01.05.2026 |
| `john` | ... | SPD | bis 24.07.2023 (dann Strobl) |
| `strobl` | ... | Linke/SPD | ab 24.07.2023 |
| `gruebl` | ... | CSU | bis ~21.10.2024 (dann Hobmaier) |
| `hobmaier` | ... | CSU | ab 21.10.2024 |
| `beubl` | ... | CSU | bis ~24.03.2025 (dann Marcus) |
| `marcus` | Gunnar Marcus | SPD | ab 24.03.2025 |
| `kieninger` | ... | fresh | neueres Mitglied |

Weitere: `becher_a`, `becher_j`, `beibl`, `fincke`, `grundner`, `haberl`, `heinz`, `kaestl`, `lauterbach`, `linz_karin`, `linz_kilian`, `pschorr`, `reif`, `tristl`, `von_pressentin`, `weber`, `welter`

---

## Themen: zwei Ebenen

Seit dem Umbau im Juli 2026 gibt es **Felder** und **Dossiers**.

- **Feld** = die zehn Kategorien aus `tags.json` (mobility, building, sports, culture,
  environment, education, social, budget, economy, infrastructure). Eigene Seite unter
  `#/feld/{id}`, führt die Dossiers des Feldes und die feldbezogenen Abstimmungen ohne
  Dossier auf (`voteInField()` mit Stichwort-Regex).
- **Dossier** = ein Eintrag in `topics.json`, gehört über `field` zu genau einem Feld.

Zusätzliche Felder im Dossier:

| Feld | Werte |
|---|---|
| `type` | `vorhaben` · `konflikt` · `einrichtung` · `regelwerk` · `gebiet` · `zyklus` |
| `status` | `laufend` · `abgeschlossen` · fehlt (bei Dauerthemen wie Haushalt) |
| `partOf` | Dossier-ID, wenn das Vorhaben in einem Gebiet liegt |
| `figures` | Kopftabelle für Größen, die sich wiederholt ändern (Gebühren, Förderhöhen). Zeilen mit `voteId` springen in den Zeitstrahl. |

Wichtiger Grundsatz aus der Diskussion: **die Zahl der vorhandenen Abstimmungen ist
nicht das einzige Kriterium.** Ein einzelnes Bauprojekt ist eine ausreichende Einheit;
umgekehrt kann ein breites Feld wie Radverkehr in Dossiers zerfallen, weil sich Bürger
nicht für den ganzen Bereich interessieren, sondern für die eine Kreuzung.

| ID | Dossier | Feld | Typ |
|---|---|---|---|
| t1 | Vereinsheim SGT Istanbul | sports | vorhaben |
| t2 | Sanierung Bahnhof Moosburg | building | vorhaben |
| t3 | Parksituation Auf dem Plan | mobility | konflikt |
| t4 | Verkehrsberuhigung Innenstadt | mobility | vorhaben |
| t5 | Studentenwohnheim Rockermaier Areal | building | konflikt |
| t6 | Theresia-Gerhardinger-Grundschule | education | vorhaben |
| t7 | Haushalt | budget | zyklus |
| t8 | Schulwegsicherheit | mobility | vorhaben |
| t9 | Kreisverkehr Landshuter Straße | mobility | vorhaben |
| t10 | Wirtschaftsförderung Moosburg | economy | vorhaben |
| t11 | Legal Wall | culture | vorhaben |
| t12 | Freibad | sports | einrichtung |
| t13 | Sanierungsgebiet Innenstadt–Bahnhof | building | gebiet |
| t14 | Erhalt Wachbaracken Stalag VII A | culture | konflikt |
| t16 | Hallenbad | sports | einrichtung |
| t17 | Rathaus-Sanierung | building | vorhaben |
| t18 | Gewerbegebiet Degernpoint | economy | gebiet |
| t19 | DAV Kletter- und Boulderhalle | sports | vorhaben |
| t20 | Amperauen / Wohngebiet & Park | building | gebiet |
| t21 | Kommunale Wärmeplanung | environment | vorhaben |
| t22 | Windenergie im Regionalplan | environment | konflikt |
| t23 | Photovoltaik-Freiflächenanlage Kuttenweide | environment | vorhaben |
| t24 | Straßenbeleuchtung auf LED | infrastructure | vorhaben |
| t25 | Städtische Förderprogramme für Energie | environment | regelwerk |
| t26 | Stromeinkauf der Stadt | infrastructure | zyklus |
| t28 | Gewerbegebiet Pfrombach – Containerbau ELA | economy | konflikt |
| t29 | Bürgerbegehren „Lebenswertes Moosburg“ | building | konflikt |

t15 (Sammelthema Energie) wurde in t21–t26 zerlegt, t27 (Sammelthema Bürgerbegehren)
in t28 und t29. Beide IDs sind vergeben und werden nicht neu benutzt; die nächste
freie ID ist **t30**.

---

## Design

Die App folgt dem offiziellen Moosburger Design-System, nicht dem alten Verlaufs-Look.

- Schrift: **Playfair Display** (Überschriften) + **Inter** (Fließtext), self-hosted in `fonts/`
- Rot gedeckt statt grell: `--primary-dark #6D0818`, `--primary #A50D24`,
  `--primary-bright #C8102E` nur punktuell. `--no #9B0000` bleibt bewusst ein anderes Rot,
  damit ein Link nicht wie eine Ablehnung aussieht.
- Gold `#B8964E`, Creme `#FAF7F2`, Tiefschwarz `#1C1C1C`
- Rainbow-Streifen: 9 feste Segmente, 4 px, **nie als Verlauf**. Einzige Signaturfläche.
- Radien 2–4 px. Keine Verläufe, keine Glassmorphism-Karten.

**Chrome je Bereich** — Navbar und Hero sind eine durchgehende Fläche, deren Farbe aus
`--chrome` kommt und über `body[data-chrome=…]` wechselt (`setChrome()` in `js/app.js`):

| Bereich | Farbe |
|---|---|
| Themen, Dossiers | `--primary` |
| Themenfeld | `--primary-dark` |
| Sitzungen, Kalender | `#6E5A30` Gold-dunkel |
| Gremien, Personen | `--text` Tiefschwarz |
| Einstellungen | Creme, dunkle Schrift |

**Globale Suche** — ein Index über Felder, Dossiers, Abstimmungen, Sitzungen und
Personen (`globalSearch()`), nach Art gruppiert mit Kontingent je Art, damit eine
Kategorie die anderen nicht verdrängt.

---

## Sitzungsabdeckung – Stand 2026-06-10

Der Backlog **2020-01 bis 2021-12** sowie die Lücken 2022 und die Sitzungen der neuen
Wahlperiode (11.05. und 18.05.2026) wurden im Juli 2026 nachgetragen — 38 Niederschriften
in einem Durchlauf über `scripts/add_backlog_2020_2026.py`. Die Anwesenheitslisten aller
38 Sitzungen wurden gegen die Mandatslage geprüft: **0 Abweichungen**.

Die Liste unten ist der Stand davor und beschreibt nur noch, was aus der Bürgerinfo kam:

**2022:** StR 05.09., 19.09., 24.10. | BPU 17.11.
**2023:** StR 12.01., 30.01., 13.02., 06.03., 27.03., 17.04., 24.04., 15.05., 22.05., 12.06., 26.06., 10.07., 24.07., 04.09., 23.10., 14.12., 18.12. | BPU 23.01., 20.03., 17.07., 21.09., 23.11.
**2024:** StR 19.02., 04.03., 18.03., 08.04., 22.04., 06.05., 10.06., 17.06., 22.07., 02.12., 09.12., 16.12. | BPU 14.03., 15.07., 30.09. | HVFA 28.11.
**2025:** StR 20.01., 10.02., 24.02., 24.03., 10.04., 28.04., 02.06., 23.06., 14.07., 28.07., 08.09., 22.09., 13.10., 29.10., 01.12., 15.12. | BPU 16.01., 17.03., 22.05., 06.10., 08.12.
**2026:** StR 12.01., 02.02., 23.02.

**Zusätzlich in Daten (ohne Bürgerinfo-Niederschrift, direkt eingetragen):**
StR 01.07.2024, 02.09.2024, 23.09.2024, 07.10.2024, 21.10.2024, 04.11.2024, 18.11.2024, 10.11.2025

---

## ⚠️ Bekannte offene Punkte

### 0. Aus dem ELA-Umbau (August 2026)
- **Ergebnis des Bürgerentscheids vom 21.11.2021 fehlt.** Keine der vorliegenden
  Niederschriften hält es fest. Der Bebauungsplan wurde 2024 als Satzung beschlossen,
  das Begehren hat sich also nicht durchgesetzt — belegt ist das hier aber nicht.
  Der Zeitstrahl von t28 sagt das offen.
- **Der Parser übersieht Zusatzanträge nach dem Hauptbeschluss.** Beispiel StR
  06.09.2021: der Antrag Stanglmaier, den Bürgerentscheid nur per Briefwahl
  durchzuführen, wurde 9:13 abgelehnt und fehlt in `votes.json`. Vermutlich
  systematisch — Anträge zur Geschäftsordnung stehen im Fließtext nach dem
  eigentlichen TOP-Beschluss.
- **Mandatsbeginn Meier prüfen.** `members.json` führt `from: 2026-05-01`. Damit ergibt
  die Rechnung zur Niederschriftsgenehmigung am 18.05.2026 zwölf fortgeführte plus zwei
  neue Mandate; die Zählung des Betreibers war 13 + 1.

### 0b. Falle: Gremienbesetzung außerhalb aller Perioden
`Council.bodyConfigAt()` fiel früher auf die **oberste `seats`-Ebene** des Gremiums
zurück, wenn keine `seatConfig` das Datum abdeckte — und die ist beim Plenum wie beim
BPU eine Kopie der 2026er Besetzung. Für alte Sitzungen war das Halbrund entweder leer
oder mit den falschen Personen besetzt. Seit August 2026 gibt `bodyConfigAt()` eine
leere Konfiguration zurück, wenn das Gremium Perioden hat, aber keine passt: **lieber
nichts anzeigen als das Falsche.** Gremien ganz ohne Perioden (Aufsichtsrat,
Verbandsrat) nutzen den Rückfall weiterhin.

Folge: für den BPU vor Mai 2020 ist keine Besetzung bekannt. Die beiden Sitzungen vom
27.01. und 02.03.2020 stehen mit ihren Beschlüssen im Bestand, werden aber niemandem
zugeordnet — auch ihre 12:0-Voten nicht.

Zweite Falle im selben Bereich: `buildSeatsFromBody` bevorzugt die Person, die im Vote
auftaucht. Dadurch bleiben falsche Sitzdaten unsichtbar, solange Einzelstimmen
vorliegen — die monatsgenauen Wechseldaten der Periode 2020–2026 waren jahrelang
falsch, ohne aufzufallen (`scripts/fix_seat_dates.py`).

### 0c. Ausschusssitze zeigen nur den letzten Inhaber
In den `seatConfigs` von HVFA, PA und RPA steht je Sitz nur die **zuletzt** amtierende
Person; Vorgänger liegen unverbunden in `pastSeats`. Dadurch bekommt niemand die
Ausschussvoten seiner eigenen Zeit zugeschrieben. Betroffen sind acht Sitze:

| Gremium | Sitz zeigt | Mandat beginnt erst |
|---|---|---|
| hvfa | marcus, hobmaier, becher_a | 2025-03 / 2024-10 / 2022-06 |
| pa | gruber, becher_a | 2022-10 / 2022-06 |
| rpa | marcus, hobmaier, becher_a | 2025-03 / 2024-10 / 2022-06 |

Der BPU-Sitz (altenbeck → linz_kilian) ist im August 2026 aufgelöst worden, weil dort
inzwischen 16 Sitzungen hängen. Die übrigen acht sind offen: welcher Vorgänger zu
welchem Sitz gehört, ist aus `pastSeats` nicht eindeutig — mehrere Einträge tragen
`sub: true`, obwohl sie einen Sitz gehalten haben müssten. Wegen der dünnen
HVFA/PA/RPA-Datenlage (eine einzige erfasste Sitzung) hat das keine Dringlichkeit.

### 1. Fehlende Sitzung: BPU/HVFA 21.07.2025
Die Gemeinschaftssitzung BPU + HVFA vom **21. Juli 2025** fehlt komplett in `sessions.json` und `votes.json`. Belegt durch Agenda-TOP in bpu_20251006: „Genehmigung Niederschrift BPU 21.07.2025". Niederschrift-PDF sollte in `data/niederschriften/` liegen.

### 2. Sessions ohne `absent`-Feld
- `sr_20251110` (10.11.2025): kein `absent`-Array
- `bpu_20231123` (23.11.2023): kein `absent`-Array, keine `substitutes`
- `hvfa_20241128`: kein `absent`-Array (bei HVFA evtl. bewusst weggelassen)

### 3. StR 12.05.2025 (7. Stadtratssitzung)
Existierte nachweislich (in sr_20250714 Niederschrift-Genehmigung erwähnt), hat aber keine Bürgerinfo-Niederschrift und ist daher **nicht** in der Ziel-Liste und **nicht** in den Daten. Kein Handlungsbedarf.

---

## Wichtige Workflow-Regeln

### Niederschrift einarbeiten
1. PDF liegt in `data/niederschriften/`
2. Skill `/niederschrift-einarbeiten` verwenden (liest PDF, trägt Sessions + Votes + ggf. Topics ein)
3. Danach Skill `/validate-data` ausführen

### Tracking aus dem Voting-Tool
Aus dem Projekt `/council-voting-tool` kommen ZIP-Exporte mit JSON. `scripts/add_tracking_2026.py`
gleicht sie über TOP-Nummer und Reihenfolge gegen die Sitzung ab.

- **Das Protokoll wird nie überschrieben.** Wo ein Vote schon `named` ist, meldet das
  Skript einen Konflikt, statt ihn anzuwenden.
- Getrackte Voten bekommen `source: {tier: "tracked", by: "<member-id>"}`.
- ZIPs kommen oft **vor** der zugehörigen Niederschrift. Ohne Protokoll wird nicht
  importiert — sonst fehlt die Anwesenheitsbasis.
- Die enthaltenen `nichtoeffentlich.json` tragen nur Sitzungsmetadaten und Anwesenheit,
  keine Beschlüsse. Sie dürfen ins öffentliche Repo.

### Topic-Watchlist
`data/knowledge/topic-watchlist.md` — vom User benannte Themen, die auf jeden
Fall eigene Topic-Seiten bekommen sollen. Wird beim Einarbeiten von
Niederschriften geprüft; die Anlage von Watchlist-Themen ist vorab genehmigt
(kein Nachfragen, aber in der Zusammenfassung erwähnen).

### Namenskonventionen
- Session-IDs: `{typ}_{YYYYMMDD}` (z.B. `sr_20250602`, `bpu_20250522`)
- Vote-IDs: `{sessionId}_{NN}` (zweistellig, z.B. `sr_20250602_01`)
- Press-IDs: `{media}_{YYYY-MM-DD}_{slug}`
- Topic-IDs: `t{N}` (fortlaufend, nächste freie: `t30`)

### Named vs. Anonymous Votes
- **Named** wenn die Niederschrift Einzelstimmen nennt (meist bei knappen oder kontroversen Votes + erste Vote je Sitzung)
- **Anonymous** wenn nur Gesamtzahlen (z.B. „15:7")
- Bei einstimmigen Votes: entweder named mit `no: []` oder anonymous mit `no: 0`

### Absenzen
- In `sessions.absent`: immer ALLE abwesenden Stadtratsmitglieder (für Stadtratssitzungen)
- In `votes.results.absent`: alle die bei DIESER spezifischen Abstimmung abwesend waren (kann abweichen wenn jemand kurz rausgeht)
- Für BPU-Sitzungen: `sessions.absent` = nur die ohne Vertretung; `sessions.substitutes` = die mit Vertretung

### Einstimmige named Votes
Wenn in Niederschrift „einstimmig" steht und Einzelstimmen nicht aufgeführt:
→ alle Anwesenden in `yes`, keine in `no`, Abwesende aus `session.absent` in `absent`

---

## Skills (slash commands)

| Skill | Zweck |
|---|---|
| `/niederschrift-einarbeiten` | PDF-Niederschrift → sessions/votes/topics |
| `/validate-data` | Validierung aller JSON-Dateien |
| `/build-data` | bundle.json neu bauen |
| `/member-update` | Mitgliederwechsel eintragen |
| `/antrag-einarbeiten` | Antrag in member.profile.motions |
| `/presseartikel-einarbeiten` | Press-Eintrag + Verlinkung |
| `/topic-anlegen` | Neues Thema anlegen |

---

## Daten-Validierung

Script: `scripts/validate_data.py`. Prüft referentielle Integrität (z.B. ob voteIds in sessions auch in votes existieren, ob member-IDs gültig sind). Immer nach größeren Änderungen ausführen.

---

## Git-Branch-Konvention

Aktueller Branch: `parliament-v2`. Main-Branch für PRs: `main`.
