---
name: validate-data
description: Führt scripts/validate_data.py über alle data/*.json-Dateien aus und fasst Probleme/Warnungen kurz für den User zusammen. Nutze diesen Skill nach jeder größeren Datenänderung (Niederschrift einarbeiten, Member-Update, Press-Eintrag, Topic-Änderung).
---

# Daten-Integrität prüfen

## Wann

- Nach `niederschrift-einarbeiten`, `presseartikel-einarbeiten`, `member-update`, `antrag-einarbeiten`, `topic-anlegen`.
- Vor jedem Commit, der Datendateien anfasst.
- Wenn die App seltsame Anzeigen liefert (fehlende Voten, kaputte Topic-Links) → erst hier nachsehen, bevor man im Code sucht.

## Wie

```bash
python scripts/validate_data.py
```

Exit-Code 0 = sauber. 1 = Probleme.

## Output interpretieren

- **`✗ Problems`** = harte Fehler, müssen gefixt werden bevor committed wird. Typische Beispiele:
  - `vote ...: named arrays sum to N, expected M` → falsche Anzahl in yes/no/absent (oft: Stellv. doppelt gezählt, oder Mitglied einer Sitzung zugeordnet die er gar nicht hatte)
  - `vote ...: sessionId 'X' missing` → kaputter Fremdschlüssel
  - `duplicate <typ> id: X` → versehentlich doppelt eingefügt
- **`⚠ Warnings`** = Hinweise, die nicht zwingend Fehler sind, aber Aufmerksamkeit verdienen:
  - `id(s) {…} cast vote but aren't in BPU composition for YYYY-MM-DD` → entweder die Person war an dem Tag wirklich nicht im Ausschuss (dann war der Vote falsch zugeordnet), oder die `seatConfigs` in `members.json` ist unvollständig (dann muss dort ein occupant ergänzt werden). Bekannte offene Fälle: Beubl + Grübl im BPU.
  - `member …: periods overlap` → bei Personen mit `member.periods[]` sich überschneidende Zeiträume.

## Fix-Workflow

Bei `Problems`:

1. Erste Zeile lesen → betroffener `id`, betroffene Datei.
2. Direkt im JSON nachsehen (`Grep` o.ä.) — meist offensichtlich, was fehlt/zuviel ist.
3. Korrigieren, dann erneut `python scripts/validate_data.py`. Iterieren bis 0 Problems.

Bei `Warnings`: nicht blockierend, aber im aktuellen Branch sammeln und User auf die Existenz hinweisen.

## Berichten

Eine Zeile reicht: „Validator: X Probleme, Y Warnings. {Kurzdiagnose der Probleme, falls vorhanden}." Keine Auflistung aller Warnings — die kennt der User aus früheren Sessions.
