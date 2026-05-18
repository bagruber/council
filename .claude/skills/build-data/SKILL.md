---
name: build-data
description: Baut data/bundle.json (kombinierte JSON + vorberechnete Indizes) aus den 6 hand-gepflegten Datenquellen. Nicht zwingend für die Live-App, aber nützlich für schnelle Querys, Smoke-Tests, Statistiken. Ruft auch validate-data zur Sicherheit auf.
---

# Bundle bauen

## Wann

- Manuell, wenn man eine konsolidierte Sicht auf alle Daten + Indizes braucht (z.B. für Statistik-Querys, Debugging, oder als Quelle für später geplanten Single-Fetch-Loader).
- Nach jedem `niederschrift-einarbeiten`-Lauf praktisch, um zu sehen ob die neuen IDs sich überall sauber verzahnt haben.

Nicht: in der App live referenzieren — die nutzt aktuell weiter die 6 Quelldateien. Wenn das geändert werden soll, ist das eine separate App-Refactor-Aufgabe.

## Wie

```bash
python scripts/validate_data.py    # Pflicht-Vorlauf
python scripts/build_data.py
```

Schreibt `data/bundle.json`.

## Inhalt

```jsonc
{
  "members":  {...},               // 1:1 aus members.json
  "sessions": [...],
  "votes":    [...],
  "topics":   [...],
  "tags":     [...],
  "press":    [...],
  "indexes": {
    "votesBySession":   {"sr_20230112": ["sr_20230112_01", ...]},
    "votesByYear":      {"2023": [...]},
    "votesByTopic":     {"t7": [...]},
    "sessionsByYear":   {"2023": [...]},
    "pressByTopic":     {"t14": ["merkur_2024-...", ...]},
    "memberAbsenceRange": {"john": {"firstAbsence": "...", "lastAbsence": "..."}}
  },
  "meta": {"counts": {...}}
}
```

## Neue Indizes hinzufügen

Wenn ein Konsument einen neuen Lookup braucht: `scripts/build_data.py` → unter `# ── Indexes ──` einfügen, dann unten zu `bundle["indexes"]` hinzufügen. `validate_data.py` läuft die Quelldateien — der Build kann sich darauf verlassen, dass Foreign Keys halten.

## Berichten

Eine Zeile: „Bundle: N KB, Indizes für M Sessions / K Voten gebaut." Falls Validator vorher gelaufen ist, dessen Ergebnis voranstellen.
