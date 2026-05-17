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

```bash
python3 -c "
import json, os
pdfs = {os.path.splitext(p)[0].lower().replace('hvf_','hvfa_') for p in os.listdir('data/niederschriften')}
with open('data/sessions.json') as f: existing = {s['id'] for s in json.load(f)}
print('Unprocessed:', sorted(pdfs - existing))
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
- **Complete agenda** with item numbers (3, 4.1, 5a, …).
- **All votes**: item number, short title, 1–2-sentence summary, yes/no/absent counts (totals: 25 stadtrat, 12 BPU, 8 HVFA pre-2026 or 12 from 2026+), unanimous flag, rejected flag, any named/roll-call vote info.

### 3. Period-aware member roster

Active members depend on session date — pick the right roster:

| Period | List |
|---|---|
| 2014-09 → 2020-04 (PRE-Mai 2020) | check members.json with `from` ≤ date ≤ `to` |
| 2020-05 → 2021-10 (Wittmann era) | standard 2020-2026 with wittmann/neumayr as fresh |
| 2021-10 → 2022-10 (Grübl/Neumayr) | gruebl + neumayr |
| 2022-10 → 2024-10 (Grübl/Gruber) | gruebl + gruber |
| 2024-10-21 → 2025-03-24 (Hobmaier/Gruber, Beubl SPD) | hobmaier + gruber + beubl |
| 2025-03-24 → 2026-04-30 (Hobmaier/Gruber, Marcus SPD) | hobmaier + gruber + marcus |
| 2026-05-01 → 2032-04-30 | new council (Mader BM, Dick + Sabanovic fresh, etc.) |

For BPU/HVFA: use the `seatConfigs` to determine the right composition for that vote date.

### 4. Build session/vote entries

- IDs: `sr_YYYYMMDD`, `bpu_YYYYMMDD`, `hvfa_YYYYMMDD`. Vote IDs: `<session>_NN` sequential.
- Session shape:
  ```json
  {
    "id": "sr_YYYYMMDD",
    "date": "YYYY-MM-DD",
    "type": "stadtrat",
    "title": "N. Stadtratssitzung – Monat YYYY",
    "absent": ["id1", "id2"],
    "substitutes": [{"member": "regular_id", "substitute": "sub_id"}],
    "agenda": [
      {"number": 3, "title": "...", "voteId": "sr_YYYYMMDD_01", "topicId": "tN" /* optional */, "press": ["..."] /* optional */},
      {"number": 4, "title": "...", "type": "discussion"} /* non-voting */
    ]
  }
  ```
- Vote shape:
  - **Named** (unanimous derivable from attendance):
    ```json
    {"id":"...","sessionId":"...","topicId":null,"date":"...",
     "title":"...","text":"...",
     "type":"named",
     "results":{"yes":[...ids],"no":[...ids],"absent":[...ids]}}
    ```
  - **Anonymous** (split or partial knowledge):
    ```json
    {"id":"...","sessionId":"...","topicId":null,"date":"...",
     "title":"...","text":"...",
     "type":"anonymous",
     "results":{"yes":N,"no":N,"absent":N},
     "voters":{"member_id":"yes|no|absent"}  /* OPTIONAL, partial known */
    }
    ```
- For **rejected** votes (more no than yes, or expressly noted): set `"result": "rejected"` on the vote object.

### 5. Convert to named where derivable

Rule: if `yes_count + no_count == 25 − len(session.absent)` AND vote is unanimous (no=0 or yes=0), expand:
- `yes` = all active members of body that day, minus session.absent
- `no` = []
- `absent` = session.absent

For BPU/HVFA: same logic but using committee composition (chair + vicechairs + seats).

If vote is unanimous but attendance doesn't match cleanly (extra brief absences), **leave anonymous** or add an explanatory note in `voters`.

### 6. Aggregate sub-votes when appropriate

If 10+ procedural sub-votes (e.g. „15 Stellungnahmen alle 21:0") share the same result, combine into a single „Sammelvote"-entry with `text` describing the count of individual decisions. Distinct outcomes (Satzungsbeschluss, Verfahrenswechsel, …) stay separate.

### 7. Topic assignment

Existing topics (check `data/topics.json` for current list and titles):
- t1–t19 currently exist; titles may evolve.

Rules:
- If a vote clearly belongs to an existing topic → set `topicId` in agenda item and on the vote.
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
- For brand-new members not yet in `members.json` (e.g. surprise nachgerückte Person): pause and ask the user before adding.

### 9. Commit

- Stage all changes including the new PDFs (in `data/niederschriften/`) and the helper script.
- Commit message format: `+N sessions {Monat range}; topics: …` — short, factual, no emojis, no "Co-Authored-By Claude".
- Push to working branch and fast-forward `main` so Pages picks it up.

## Edge cases & traps

- **AR Kläranlage-Entlastung**: members on the AR (currently Dollinger, Weber, Haberl, Reif, Hobmaier 2020–2026) are excluded from this specific vote. Set them as `absent` in the named conversion.
- **Niederlegung-Sitzungen**: e.g. sr_20241021 has a member-change mid-session. Pre-Niederlegung votes use the old member; post-Niederlegung votes use the successor. The `voters` field can mark this per-vote if both are relevant.
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
