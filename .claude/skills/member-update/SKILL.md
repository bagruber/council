---
name: member-update
description: Trägt einen Mitglieder-Wechsel sauber in members.json ein — Nachrücker:in tritt ein, Vorgänger:in scheidet aus, Funktionen wechseln (3. BM, Referent:in), Ausschuss-Sitze gehen über. Setzt automatisch das to-Datum des Vorgängers, das from-Datum der Nachfolge, und ergänzt seatConfigs.occupants. Kann auch reine Funktions-Updates (Referatswechsel, Vize-BM-Wechsel) abdecken.
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

```jsonc
// data/members.json
{
  "id": "strobl", "name": "...",
  "from": "2023-07-24",            // tag der Vereidigung / Nachrückung
  "to":   null,                    // null = aktuell aktiv
  "periods": [ ... ],              // OPTIONAL: nur bei nicht-zusammenhängenden Mandaten
  "party": "spd", "partyHistory": [...],
  "role": "councillor" | "mayor",
  "title": "3. Bürgermeister:in",  // OPTIONAL, aktuelle Funktion
  "profile": {
    "titles": [                    // OPTIONAL: vollständige Funktions-Historie
      {"title": "3. Bürgermeister", "from": "2022-10-24", "to": "2024-10-20"}
    ],
    "motions": [...]
  }
}
```

```jsonc
// data/members.json → bodies[].seatConfigs[].seats[]
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

- `member.to = YYYY-MM-DD` (Tag vor Eintritt der Nachfolge).
- Falls eine Niederschrift den Tag bestätigt, voteId/sessionId zur Doku im commit message erwähnen.

### 3. Nachfolger:in

- Falls schon in `members.json`: `member.from = YYYY-MM-DD` setzen, `member.to = null` (falls vorher gesetzt).
- Falls neu: vollen Datensatz anlegen — id (snake_case Nachname), name, party, role, from. Bild-Datei `img/members/originals/<id>.png` einfordern.

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

- **Marschoun-Muster**: Person war früher schon mal im Rat, kommt zurück → `periods: [...]` statt `from`/`to`.
- **Mitten in Sitzung**: Niederlegung passiert in einer Sitzung; Voten *vor* der Vereidigung gehören dem Vorgänger, *nach* der Nachfolge dem Nachfolger. Beim Einarbeiten der Niederschrift entsprechend per-Vote die `voters`-Map nutzen.
- **Stellvertreter:in-Wechsel** (häufiger als Hauptsitz-Wechsel): nur die `sub`-Felder der relevanten `vicechairs[]` / `seats[]` updaten. Keine `occupants`-Historie nötig, weil Stellv. nicht stimmen, wenn der Hauptsitz da ist — und wenn er stimmt, ergibt sich's aus der Niederschrift.
