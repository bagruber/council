---
name: presseartikel-einarbeiten
description: Integriert einen Presseartikel in press.json und verlinkt ihn an den passenden Stellen (Sitzungs-Agendaitem, Topic-Historie, Member-Antrag). Erkennt das Medium aus der URL und erzeugt die ID nach Schema {media}_{YYYY-MM-DD}_{slug}.
---

# Presseartikel einarbeiten

Use this skill whenever the user shares a press article URL (Süddeutsche, Merkur, BR, Moosburger Zeitung, …) and wants it linked into the data.

## Inputs

A URL, optionally accompanied by a hint where it belongs („zur Sitzung", „zum Antrag X", „zum Thema Y"). If the hint is missing, infer the link target from the article content + title + date.

## Process

### 1. Determine media source

Check `data/members.json` → `media` array for the existing sources:

| URL pattern | media id |
|---|---|
| `merkur.de` | `merkur` |
| `sueddeutsche.de` | `sz` |
| `ardmediathek.de` / `br.de` | `br` |
| `moosburger-zeitung.de` | `mz` |
| other | ask user; add to `media` if confirmed |

### 2. Fetch metadata if missing

If the user only gave a URL, use `WebFetch` with prompt „Extract: publication date (DE format), headline, 1-sentence summary, main topic." Read the article enough to:
- Extract publication date (YYYY-MM-DD).
- Compose a short title (max ~50 chars, prefer the article headline).
- Identify the underlying Stadtrat session / topic / Antrag.

### 3. Build press entry

```json
{
  "id": "{media}_{YYYY-MM-DD}_{slug}",
  "media": "merkur",
  "date": "YYYY-MM-DD",
  "title": "Kurztitel",
  "url": "https://..."
}
```

- Slug: 1–3 kebab-cased words capturing the topic (`legal-wall`, `kreisverkehr`, `kitagebuehren`). Keep IDs short and stable.
- Append to `data/press.json`. Don't duplicate existing IDs.

### 4. Link to one or more anchor points

Decide based on the article's content. Multiple links per article are fine.

**a) Agenda item in a session** (most common):
```json
// in data/sessions.json, inside the relevant session.agenda[item]:
"press": ["{press_id}"]
```

**b) Topic history entry**:
```json
// in data/topics.json, inside topics[].history[entry]:
"press": ["{press_id}"]
```

**c) Member-Antrag** (rare — only if the article is specifically about a person's motion):
```json
// in data/members.json, inside member.profile.motions[i]:
"press": ["{press_id}"]
```

**d) Topic-level external link** (when the article is general, not tied to a single vote — currently not yet a first-class field; in that case prefer adding a `milestone` history entry on the topic with the press attached).

### 5. Discovery rules — where does the article belong?

- **Date proximity**: a Merkur/SZ article published within 1–2 days of a session usually reports on that session → link to the relevant agenda item.
- **Key terms in title/url** → map to topic:
  - „Kreisverkehr" → t9
  - „Wachbaracken", „Stalag" → t14
  - „Wohnungsbau", „Rockermaier" → t5
  - „Vereinsheim SGT" → t1
  - „Hallenbad" → t16
  - „Freibad", „Bad" → t12
  - „Grundschule", „Theresia-Gerhardinger" → t6
  - „Sanierungsgebiet", „Lebendige Zentren" → t13
  - „Bahnhof" → t2
  - „Stadtplatz", „Auf dem Plan", „Parken" → t3 or t4
  - „Schulweg", „Schulwegsicherheit" → t8
  - „Wirtschaftsförderung" → t10
  - „Legal Wall" → t11
  - „Rathaus" → t17
  - „Gewerbegebiet", „Degernpoint" → t18
  - „Klettern", „DAV" → t19
  - „Wärmeplanung", „Wind", „PV", „Solar", „Energie" → t15
  - „Haushalt", „Hebesatz", „Jahresrechnung" → t7
- **Politician name in title** → if the article highlights one councillor's motion or statement, also check their `profile.motions[]` for a date match and link there in addition.

### 6. Quick check

```bash
python3 -c "
import json
with open('data/press.json') as f: press = json.load(f)
ids = [p['id'] for p in press]
dups = [i for i in ids if ids.count(i) > 1]
print('Duplicates:', set(dups) or 'none')
print('Total:', len(press))
"
```

Confirm the link shows up in the right place by grepping for the new press id in `data/sessions.json`, `data/topics.json`, or `data/members.json`.

### 7. Commit

Concise message, e.g. `press: SZ-Artikel zu Windenergie + Merkur Kitagebühren`. Push and fast-forward main.

## Edge cases

- **New media outlet** (e.g. taz, BR-Beitrag): ask user before adding to `data/members.json` `media[]`. Provide a name, accent colour and logo path placeholder.
- **Multiple articles same topic same date**: prefix the slug with the medium-specific angle, e.g. `merkur_2024-06-10_kitagebuehren-zumutbar` vs `sz_2024-06-10_kitagebuehren-arbeitsmarktzulage`.
- **Paywall / can't fetch**: ask the user for title + date directly. Don't guess.
- **Article references multiple sessions** (e.g. an analysis piece): link to the topic's history entry rather than a single session item.
