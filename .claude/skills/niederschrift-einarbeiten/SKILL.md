---
name: niederschrift-einarbeiten
description: Liest eine oder mehrere Niederschriften (PDFs in data/niederschriften/) und integriert sie in sessions.json, votes.json und topics.json. Erkennt Stadtrat, BPU und HVFA, leitet named-Voten aus Anwesenheit ab, schlägt Topic-Erweiterungen oder neue Topics vor.
---

# Niederschriften einarbeiten

Use this skill to integrate Moosburger Niederschriften (StR/BPU/HVFA protocols) into the data layer.

## Inputs

User typically mentions which PDFs to process — sometimes just "die neuen Niederschriften" (find by `git status` / folder diff). PDFs live in `data/niederschriften/` and follow the naming `SR_YYYYMMDD.pdf`, `BPU_YYYYMMDD.pdf`, `HVF_YYYYMMDD.pdf`.

## Process

### 1. Determine unprocessed PDFs

`data/sessions.json` ist seit Oktober 2026 das vollständige Register: es führt
auch Sitzungen, von denen nichts veröffentlicht ist (`niederschrift: "keine"`)
sowie angekündigte. Eine neue Niederschrift legt deshalb meist **keinen neuen
Eintrag** an, sondern füllt einen vorhandenen.

```bash
python3 -c "
import json, os
pdfs = {os.path.splitext(p)[0].lower().replace('hvf_','hvfa_') for p in os.listdir('data/niederschriften')}
with open('data/sessions.json') as f: reg = json.load(f)
fertig = {s['id'] for s in reg if s.get('niederschrift') == 'vollständig'}
leer = {s['id'] for s in reg if s.get('niederschrift') == 'keine'}
print('Unprocessed:', sorted(pdfs - fertig))
print('davon schon im Register (ergänzen, nicht anlegen):', sorted((pdfs - fertig) & leer))
"
```

### 2. Extract data from PDFs

For more than ~3 PDFs, spawn one or two **Explore subagents** in parallel — give each 5–7 files. Otherwise just `Read({file_path: ..., pages: "1-N"})` directly.

Tell the subagent to use the Read tool's native PDF support — explicitly mention `Read({file_path: ...})` works and DO NOT use pdftotext/bash.

For each session extract:
- **Session metadata**: date (YYYY-MM-DD), type (stadtrat/bpu/hvfa), session number/title, e.g. `"4. Stadtratssitzung – März 2024"`.
- **Absent members (full session)** as member IDs (snake_case lastnames).
- **Partial attendees** with times — `"haberl ab 18:15"`, `"tristl bis 20:40"`.
- **Per-vote brief absences** if explicitly noted.
- **Complete agenda** with item numbers (3, 4.1, 5a, …). Immer als Text, nie als Zahl — `6.10` ist keine `6.1`.
- **All votes**: item number, short title, 1–2-sentence summary, yes/no/absent counts (totals: 25 stadtrat, 12 BPU, 8 HVFA pre-2026 or 12 from 2026+), unanimous flag, rejected flag, any named/roll-call vote info.

### 3. Period-aware member roster

Active members depend on session date — pick the right roster:

| Period | List |
|---|---|
| 2014-09 → 2020-04 (PRE-Mai 2020) | check members.json: ein Abschnitt in `mandates` enthält das Datum |
| 2020-05 → 2021-10 (Wittmann era) | standard 2020-2026 with wittmann/neumayr as fresh |
| 2021-10 → 2022-10 (Grübl/Neumayr) | gruebl + neumayr |
| 2022-10 → 2024-10 (Grübl/Gruber) | gruebl + gruber |
| 2024-10-21 → 2025-03-24 (Hobmaier/Gruber, Beubl SPD) | hobmaier + gruber + beubl |
| 2025-03-24 → 2026-04-30 (Hobmaier/Gruber, Marcus SPD) | hobmaier + gruber + marcus |
| 2026-05-01 → 2032-04-30 | new council (Mader BM, Dick + Sabanovic fresh, etc.) |

For BPU/HVFA: use the `seatConfigs` to determine the right composition for that vote date.

### 4. Build session/vote entries

- IDs: `sr_YYYYMMDD`, `bpu_YYYYMMDD`, `hvfa_YYYYMMDD`. Vote IDs: `<session>_NN` sequential.
- Steht die Sitzung schon im Register, den vorhandenen Eintrag ergänzen:
  `niederschrift` auf `"vollständig"` setzen, `title`, `absent`, `agenda`
  hinzufügen, `start`/`end` gegen die Niederschrift prüfen. **ID, Datum und
  Gremium nicht ändern** — der Validator prüft, dass die ID zu beidem passt.
- Session shape:
  ```json
  {
    "id": "sr_YYYYMMDD",
    "date": "YYYY-MM-DD",
    "type": "stadtrat",
    "niederschrift": "vollständig",
    "start": "19:00",
    "end": "21:30",
    "title": "N. Stadtratssitzung – Monat YYYY",
    "absent": ["id1", "id2"],
    "substitutes": [{"member": "regular_id", "substitute": "sub_id"}],
    "agenda": [
      {"number": "3", "title": "...", "voteIds": ["sr_YYYYMMDD_01"], "topicId": "tN" /* optional */, "press": ["..."] /* optional */},
      {"number": "4", "title": "...", "type": "discussion"} /* non-voting */
    ]
  }
  ```
- Vote shape:
  - **Named** (unanimous derivable from attendance):
    ```json
    {"id":"...","sessionId":"...","topicIds":["tN"],
     "title":"...","text":"...",
     "type":"named",
     "results":{"yes":[...ids],"no":[...ids],"absent":[...ids]},
     "source":{"tier":"protocol-explicit"}}
    ```
  - **Anonymous** (split or partial knowledge):
    ```json
    {"id":"...","sessionId":"...","topicIds":["tN"],
     "title":"...","text":"...",
     "type":"anonymous",
     "results":{"yes":N,"no":N,"absent":N},
     "source":{"tier":"protocol-implicit"},
     /* OPTIONAL, wo einzelne Stimmen bekannt sind */
     "voters":{"member_id":{"vote":"yes|no|absent"}}
    }
    ```

**Die Stufe ist Pflicht.** `source.tier` sagt, woher das Ergebnis stammt:

| tier | wann |
|---|---|
| `protocol-explicit` | Die Niederschrift nennt jeden Namen. |
| `protocol-implicit` | Einstimmig, Einzelstimmen aus der Anwesenheit abgeleitet. |
| `tracked` | Im Saal mitgeschrieben; `by` nennt die Person. |
| `press` | Aus einem Zeitungsartikel rekonstruiert; `pressId` nennt ihn. |
| `selbstauskunft` | Aus eigenen Notizen eines Mitglieds. |
| `result-only` | Nur Ja und Nein überliefert, sonst nichts. |

`voters[<id>]` trägt dieselbe Sprache für die einzelne Stimme: `vote`,
`tiers` (Belege, stärkster zuerst), `by` (wer sie berichtet hat), `evidence`
(`"soft"` = aus einer Wortmeldung erschlossen, nicht als Stimme berichtet)
und `note`. Ein Eintrag ohne `vote` trägt nur die Herkunft.
- For **rejected** votes (more no than yes, or expressly noted): set `"result": "rejected"` on the vote object.

### Sitzungen ohne Niederschrift

Zwei Fälle, die gleich aussehen und streng zu trennen sind.

**a) Beschlussauszug im Ratsinformationssystem** — die Ergebnisse stehen
öffentlich, nur ohne Anwesenheitsliste. Das ist amtlich.

```json
"niederschrift": "auszug",
"source": { "kind": "webauszug", "url": "https://www.moosburg.de/…" }
```

**Niemals eine PDF dafür erzeugen**, verlinkt wird die Seite der Stadt. Die
Ergebnisse dürfen eingetragen werden. Was ohne Niederschrift **wartet**:

- **Stimmverhalten.** Ohne Anwesenheitsliste ist nicht zuzuordnen, wer wie
  gestimmt hat. Einzige Ausnahme: haben **alle** Sitze mitgestimmt (BPU: 12),
  waren alle regulären Sitze da → `named` mit vollständiger Besetzung. Sonst
  `anonymous`, **kein `absent`-Array** (leer hieße „alle da"), und
  `mark_inferable.py` sperrt die Ableitung.
- **Die Dossier-Zuordnung.** `topicIds` bleibt leer, bis die Niederschrift
  sagt, was beschlossen wurde. Ein Beschluss im falschen Dossier erzählt eine
  falsche Geschichte.

**b) Nur eigene Mitschrift (Vote-Tracking-ZIP), nichts Veröffentlichtes** —
dann gehören **keine Ergebnisse** in den Bestand. Die Tagesordnungspunkte
dürfen stehen, mehr nicht:

```json
"niederschrift": "keine"
```

Dasselbe gilt für Sitzungen, die noch nicht stattgefunden haben: Tagesordnung
ja, Inhalte nein. Die Mitschrift wandert in `votes.json`, sobald die
Niederschrift da ist und sie bestätigt.

### 5. Convert to named where derivable

Rule: if `yes_count + no_count == 25 − len(session.absent)` AND vote is unanimous (no=0 or yes=0), expand:
- `yes` = all active members of body that day, minus session.absent
- `no` = []
- `absent` = session.absent

For BPU/HVFA: same logic but using committee composition (chair + vicechairs + seats).

If vote is unanimous but attendance doesn't match cleanly (extra brief absences), **leave anonymous** or add an explanatory note in `voters`.

Kurzfristige Abwesenheit, Befangenheit und fehlendes Stimmrecht stehen in
`excluded: [{"member": "...", "reason": "..."}]`. Erlaubt sind nur die Codes
`beteiligung`, `enthaltung`, `nicht_stimmberechtigt`, `kein_mandat` und
`kurz_abwesend` — Prosa als Grund fällt stillschweigend auf „abwesend".

### 6. Aggregate sub-votes when appropriate

If 10+ procedural sub-votes (e.g. „15 Stellungnahmen alle 21:0") share the same result, combine into a single „Sammelvote"-entry with `text` describing the count of individual decisions. Distinct outcomes (Satzungsbeschluss, Verfahrenswechsel, …) stay separate.

### 7. Topic assignment

Existing topics (check `data/topics.json` for current list and titles):
- t1–t19 currently exist; titles may evolve.

**Watchlist zuerst:** `quellen/knowledge/topic-watchlist.md` enthält vom User
benannte Themen, die auf jeden Fall eigene Topic-Seiten bekommen sollen.
Passt ein TOP zu einem Watchlist-Eintrag:
- Topic existiert schon (Status = `tN`) → normal zuordnen.
- Topic existiert nicht → anlegen (Schema siehe `topic-anlegen`-Skill). Die
  Anlage ist durch den Watchlist-Eintrag vorab genehmigt — nicht erneut
  nachfragen, aber in der Zusammenfassung erwähnen. Danach Status-Spalte der
  Watchlist auf die neue `tN` setzen.

**Kandidaten danach:** dieselbe Datei führt unten Themen, die für ein eigenes
Dossier noch zu dünn sind, und Stränge, die aus einem bestehenden Thema
herausgelöst gehören. Für jeden TOP ohne passendes Topic:
- Steht schon eine Zeile dafür → Belege und Datum ergänzen. Ab dem zweiten
  Beschluss in einer zweiten Sitzung den Vorschlag in der Zusammenfassung
  nennen (anlegen erst nach Zuruf).
- Steht keine Zeile, sieht der TOP aber nach einem wiederkehrenden Thema aus →
  neue Kandidatenzeile schreiben statt es zu vergessen.

Rules:
- If a vote clearly belongs to an existing topic → `topicIds` am Vote setzen, `topicId` am Tagesordnungspunkt dazu. **`topicIds` ist eine Liste:** gehört ein Beschluss fachlich in zwei Dossiers (eine Kreditermächtigung ist Vorhaben *und* Haushalt), nennt er beide. Steht er in der Historie eines Dossiers, muss er es auch in `topicIds` nennen — der Validator prüft das.
- Add a `history` entry to the topic in `topics.json`:
  ```json
  {"date":"YYYY-MM-DD","type":"vote|milestone|committee|proposal",
   "title":"...","text":"...","sessionId":"...","voteId":"...","press":[...]}
  ```
- If a theme appears in 2+ sessions and isn't covered → **propose a new topic** (don't silently invent — surface the proposal in your summary message). Aim for broad-but-cohesive topics; avoid topics that exist for a single vote.
- Tags: pick from existing categories (`data/tags.json`): `mobility`, `building`, `sports`, `culture`, `environment`, `education`, `social`, `budget`, `economy`, `infrastructure`. Multi-tagging allowed (e.g. `["building", "economy"]` for Gewerbegebiet).

### 8. Write data and verify

- Use a Python helper script (under `scripts/`) when bulk-integrating, especially if more than a handful of votes are involved. Pattern: load JSONs → modify dicts → save.
- **Always validate** that named-vote arrays sum to expected (25/12/8 depending on body/period).
- For brand-new members not yet in `members.json` (e.g. surprise nachgerückte Person): pause and ask the user before adding — der Eintrag braucht `mandates` und `succeeds`, siehe `/member-update`.

### 9. Commit

- Stage all changes including the new PDFs (in `data/niederschriften/`) and the helper script.
- Commit message format: `+N sessions {Monat range}; topics: …` — short, factual, no emojis, no "Co-Authored-By Claude".
- Push to working branch and fast-forward `main` so Pages picks it up.

## Edge cases & traps

- **AR Kläranlage-Entlastung**: members on the AR (currently Dollinger, Weber, Haberl, Reif, Hobmaier 2020–2026) are excluded from this specific vote. Set them as `absent` in the named conversion.
- **Niederlegung-Sitzungen**: e.g. sr_20241021 has a member-change mid-session. Pre-Niederlegung votes use the old member; post-Niederlegung votes use the successor. Wer an einem Votum den Sitz nicht hielt, bekommt `excluded` mit `reason: "kein_mandat"`.
- **„Einvernehmen verweigert"** votes are often shown as e.g. `10:0` — the *resolution* is to deny; passing the resolution means 10 yes, 0 no. Don't flip to no=10 unless the framing was actually `Einvernehmen erteilt`.
- **Tag „innercity"** is legacy — prefer the new 10 categories from `data/tags.json`.
- **Strobl-only-dissenter** votes (verkaufsoffene Sonntage, Wahlhelferbonus etc.) are typically fully reconstructable. Convert to named with strobl in `no` and rest in `yes`.

## Quick sanity checks

```bash
python3 -c "
import json
with open('data/votes.json') as f: votes = json.load(f)
for v in votes:
    if v['type'] != 'named': continue
    r = v['results']
    total = len(r['yes']) + len(r['no']) + len(r['absent'])
    sid = v['sessionId']
    expected = 12 if sid.startswith('bpu') else (8 if sid.startswith('hvfa') and sid < 'hvfa_20260501' else 25)
    if total != expected:
        print(f\"{v['id']}: {total} (expected {expected})\")
"
```
