# Daten-Mapping: OParl → Council App

## Übersicht

Die App nutzt aktuell statische JSON-Dateien. Langfristig sollen Teile davon aus der OParl API bezogen werden. Dieses Dokument beschreibt das Mapping und die Integrationsstrategie.

## Mapping OParl → Lokale Strukturen

| Lokal | OParl-Typ | Status | Anmerkungen |
|-------|-----------|--------|-------------|
| `members[].firstName/lastName` | `oparl:Person.name` | manuell | OParl hat nur `name`, Vor-/Nachname müssen ggf. geparst werden |
| `members[].party` | `oparl:Membership` → `oparl:Organization` (Fraktion) | manuell | Partei über Fraktionsmitgliedschaft ableitbar |
| `members[].role` | `oparl:Membership.role` | manuell | mayor/councillor aus Rolle in der Body-Organisation |
| `members[].from/to` | `oparl:Membership.startDate/endDate` | manuell | |
| `members[].profile` | — | nur lokal | Pronomen, Identity, Kontakt, Motions: kein OParl-Pendant |
| `bodies[]` | `oparl:Organization` | manuell | Gremien mit Sitzen, Stellvertretern |
| `sessions[]` | `oparl:Meeting` | **OParl-Kandidat** | Datum, Tagesordnung direkt übernehmbar |
| `sessions[].agenda[]` | `oparl:AgendaItem` | **OParl-Kandidat** | TOP-Nummer, Titel, Verweis auf Paper |
| `topics[]` | — | nur lokal | Themen-Aggregation existiert nicht in OParl |
| `topics[].history[]` | — | nur lokal | Manuelle Timeline, verlinkt Sessions/Votes |
| `topics[].history[].press[]` | — | nur lokal | Presseartikel-Links, manuell gepflegt |
| `votes[]` | `oparl:AgendaItem.result` (teilweise) | hybrid | OParl hat nur Ergebnis-Text, keine Einzelstimmen |
| `votes[].results` (named) | — | nur lokal / Niederschrift | `{ yes: [...ids], no: [...ids], absent: [...ids] }` |
| `votes[].results` (anonymous) | — | nur lokal / Niederschrift | `{ yes: N, no: N, absent: N }`, optional `absent_ids: [...]` |
| `sessions[].absent` | `oparl:Meeting` (teilweise) | hybrid | Ganzsitzungs-Abwesenheit, aus Niederschrift oder OParl |
| `tags[]` | — | nur lokal | Themen-Kategorisierung |
| `media[]` | — | nur lokal | Presse-Quellen mit Logo/Farbe |

## Integrationsstrategie

### Phase 1: Statisch (aktuell)
Alle Daten in JSON-Dateien, manuell gepflegt.

### Phase 2: OParl-Import
- Sitzungen und Tagesordnungen aus OParl abrufen
- Abgleich mit lokalen Sessions über Datum + Titel
- Neue Sitzungen automatisch anlegen, bestehende ergänzen
- Dokumente (Einladung, Niederschrift) als Links einbinden
- Import-Script: `tools/oparl-import.js` (geplant)

### Phase 3: Hybrides Modell
- OParl als Basis für Sitzungen, Gremien, Personen
- Lokale Anreicherung: Themen, Votes, Profile, Presse
- Knowledge Base für kontextuelles Wissen

## Knowledge Base Struktur

```
data/
  knowledge/
    oparl-api.md          — API-Referenz
    data-mapping.md       — dieses Dokument
  members.json            — Mitglieder + Profile + Gremien
  sessions.json           — Sitzungen + Tagesordnung
  topics.json             — Themen + Timeline + Presse
  votes.json              — Abstimmungen + Einzelstimmen
  tags.json               — Kategorien
```

### Prinzipien für die Knowledge Base

1. **Themen sind die Aggregationseinheit** — nicht Sitzungen oder Dokumente
2. **Vernetzung über IDs** — `sessionId`, `voteId`, `topicId`, `memberId` verknüpfen alles
3. **Presse als Kontext** — Artikel werden History-Einträgen oder Sessions zugeordnet
4. **Aufwärtskompatibel** — neue Felder ergänzen, bestehende nie umbenennen
5. **Keine Duplikation** — externe Quellen verlinken, nicht kopieren
6. **Rückwärts erweiterbar** — historische Daten können jederzeit nachgetragen werden

### Vote-Inferenz

Für anonyme Abstimmungen werden Einzelstimmen geschlussfolgert, wo das Ergebnis eindeutig ist:

| Bedingung | Schlussfolgerung | UI-Anzeige |
|-----------|-----------------|------------|
| `yes > 0, no == 0` | alle Anwesenden haben zugestimmt | `ja*` (halbtransparent) |
| `no > 0, yes == 0` | alle Anwesenden haben abgelehnt | `nein*` (halbtransparent) |
| `yes > 0, no > 0` | nicht zuordenbar | `?` |

Abwesenheit wird in dieser Reihenfolge geprüft:
1. `session.absent[]` — ganze Sitzung verpasst (öffentlich bekannt)
2. `vote.results.absent_ids[]` — temporäre Abwesenheit bei einzelnem TOP (aus Niederschrift)
3. `member.from/to` — Mitglied in dieser Periode noch nicht / nicht mehr aktiv → wird ausgeblendet

Wenn keine Abwesenheitsinfo vorliegt, wird angenommen, dass das Mitglied anwesend war.

### Erweiterungspfade

- `topics[].history[].documents[]` — Links zu Niederschriften, Vorlagen (aus OParl Files)
- `topics[].image` — Titelbild pro Thema (für Timeline-Darstellung)
- `sessions[].niederschrift` — URL zur offiziellen Niederschrift (aus OParl File)
- `members[].voteHistory` — wird zur Laufzeit aus votes.json aggregiert, nicht gespeichert
- `topics[].related[]` — Querverweise zwischen verwandten Themen
