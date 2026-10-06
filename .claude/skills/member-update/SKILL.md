---
name: member-update
description: Trägt einen Mitglieder-Wechsel sauber in members.json und bodies.json ein — Nachrücker:in tritt ein, Vorgänger:in scheidet aus, Funktionen wechseln (3. BM, Referent:in), Ausschuss-Sitze gehen über. Schliesst den Mandatsabschnitt des Vorgängers, öffnet den der Nachfolge, setzt succeeds und ergänzt seatConfigs.occupants. Kann auch reine Funktions-Updates (Referatswechsel, Vize-BM-Wechsel) abdecken.
---

# Mitglieder-Update einarbeiten

## Auslöser

- Niederlegung: „X legt sein/ihr Mandat zum DD.MM.YYYY nieder, Y rückt nach"
- Funktionswechsel: „X übernimmt 3. BM von Y", „X wird Seniorenreferent:in"
- Ausschuss-Umbesetzung: „X wechselt aus dem BPU in den HVFA"
- Neue Partei-Zugehörigkeit oder Austritt
- Sterbefall, Rücktritt aus persönlichen Gründen, Wahlperiode-Ende

## Eingabe vom User

Mindestens: wer, was, wann. Beispiele:

- „Stefan John legt zum 24.07.2023 nieder, Strobl rückt nach"
- „Marcus übernimmt SPD-Sitz im BPU von Beubl zum 24.03.2025"
- „Kehlringer wird ab Mai 2026 neuer Klima-Referent"

## Datenmodell (Cheatsheet)

Seit Oktober 2026 liegt der Bestand in vier Dateien: `members.json`,
`parties.json` (Fraktionen und beide Sitzordnungen), `bodies.json`,
`media.json`. Die Form steht in `data/schema/*.schema.json`.

```jsonc
// data/members.json
{
  "id": "strobl",
  "firstName": "...", "lastName": "...",
  // Mandat, Fraktion und Rolle in einer geordneten Liste. Kein Abstand
  // zwischen zwei Abschnitten heisst Fraktions- oder Rollenwechsel, eine
  // Luecke heisst unterbrochenes Mandat (Marschoun 2014-2020 und seit 2026).
  // Beruehren sich zwei Abschnitte an ihrer Grenze, gilt der spaetere.
  "mandates": [
    {"from": "2023-07-24", "party": "linke", "role": "councillor"}
  ],
  "succeeds": ["john"],            // OPTIONAL: fuer wen nachgerueckt wurde
  "title": "3. Bürgermeister:in",  // OPTIONAL, aktuelle Funktion
  "profile": {
    "titles": [                    // OPTIONAL: vollständige Funktions-Historie
      {"title": "3. Bürgermeister", "from": "2022-10-24", "to": "2024-10-20"}
    ],
    "motions": [...]
  }
}
```

`from`, `to`, `party` und `role` am Mitglied gibt es nicht mehr; die App
leitet sie beim Laden aus dem ersten und letzten Abschnitt ab.

```jsonc
// data/bodies.json → [].seatConfigs[].seats[]
{
  "occupants": [
    {"member": "john",   "from": "2020-05-01", "to": "2023-07-23"},
    {"member": "strobl", "from": "2023-07-24"}
  ]
}
```

## Vorgehen

### 1. Datum klären

Absolutes Datum. Nie „nächste Woche" oder „Mai". Wenn User unklar, **nachfragen**.

### 2. Vorgänger:in

- Im letzten Abschnitt von `mandates` das `to` setzen (Tag vor Eintritt der Nachfolge).
- Falls eine Niederschrift den Tag bestätigt, voteId/sessionId zur Doku im commit message erwähnen.

### 3. Nachfolger:in

- Falls schon in `members.json` (Rückkehr): einen neuen Abschnitt an `mandates` anhängen, mit `from` und ohne `to`.
- Falls neu: vollen Datensatz anlegen — id (snake_case Nachname), firstName, lastName, ein `mandates`-Abschnitt. Bild-Datei `img/members/originals/<id>.png` einfordern.
- `succeeds: ["<id der vorgängerin>"]` setzen. Mehrere nur, wenn mehrere gleichzeitig ausschieden und nicht überliefert ist, wer für wen nachrückte. **Beim Wechsel der Wahlperiode gibt es keine Nachfolge** — dort wurde gewählt.

### 4. seatConfigs.occupants

Wenn die Stelle ein Plenum-Sitz (= jedes Mitglied) ist: nur members.json updaten, plenum hat keine seatConfigs.

Wenn die Stelle ein Ausschuss-Sitz ist (BPU, HVFA, PA, RPA): den passenden `seats[]`-Eintrag im aktuellen `seatConfigs`-Block finden. Falls noch keine `occupants[]`-Historie existiert (nur `member`-Feld), umstellen auf `occupants[]` mit dem alten `member`+passenden `to`-Datum und dem neuen Eintrag.

### 5. Funktionen / Referate

`member.profile.titles[]` ergänzen mit `{title, from, to?}`. Beim Vorgänger das `to` setzen.

### 6. Plenum-Seat-Continuity (wichtig!)

Plenum-Sitze haben in `bodies[plenum].seats[]` `occupants[]`-Arrays. Beim Nachrücken muss der Eintrag dort auch ergänzt werden — sonst zeigt die Sitzungssaal-Visualisierung weiterhin den Vorgänger.

### 7. Validate

```bash
python scripts/validate_data.py
```

Erwartete clean. Wenn Warnings über Period-Overlap auftauchen — fixen.

### 8. Commit

`member: Strobl rückt für John nach (24.07.2023)` o.ä. — kurz, faktisch, kein „Co-Authored-By Claude".

## Edge Cases

- **Marschoun-Muster**: Person war früher schon mal im Rat, kommt zurück → zweiter Abschnitt in `mandates` mit einer Lücke davor.
- **Fraktionswechsel mitten im Mandat**: den laufenden Abschnitt mit `to` auf den Wechseltag schliessen und einen neuen mit demselben `from` anlegen. Kein `succeeds`, das Mandat läuft weiter.
- **Mitten in Sitzung**: Niederlegung passiert in einer Sitzung; Voten *vor* der Vereidigung gehören dem Vorgänger, *nach* der Nachfolge dem Nachfolger. Beim Einarbeiten der Niederschrift entsprechend per-Vote die `voters`-Map nutzen.
- **Stellvertreter:in-Wechsel** (häufiger als Hauptsitz-Wechsel): nur die `sub`-Felder der relevanten `vicechairs[]` / `seats[]` updaten. Keine `occupants`-Historie nötig, weil Stellv. nicht stimmen, wenn der Hauptsitz da ist — und wenn er stimmt, ergibt sich's aus der Niederschrift.
