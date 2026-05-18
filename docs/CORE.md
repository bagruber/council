# `js/core.js` — geteilte Logik für Voten & Perioden

`Council` ist das gemeinsame Modul für drei Stellen, die zuvor je eigene
Implementierungen hatten:

| Konsument | Was er braucht |
|---|---|
| `app.js` Profilansicht (Sitzungsliste) | Pro Vote: wie hat dieses Mitglied gestimmt? Label "Ja"/"Nein"/"Ja\*"/"?" |
| `app.js` Statistik-Card | Gleiche Frage, aber als grobe Eimer (yes/no/absent/unknown) für Aggregate |
| `parliament.js` Sitzfarbe | Gleiche Frage, aber pro Sitz in der Visualisierung |

Davor: drei leicht unterschiedliche Implementierungen, drei Fehlerquellen.
Jetzt: eine Funktion, drei Wrapper.

## API

### Perioden

```js
Council.memberActiveAt(member, "2023-07-24")  // → true/false
Council.bodyConfigAt(bpu, "2026-01-01")       // → seatConfig aktiv am Datum
Council.isRegularOf(member, body, date)       // → true wenn Stamm-Sitz (kein Stellv.)
```

`memberActiveAt` versteht sowohl `member.from`/`member.to` (Standardfall) als
auch `member.periods: [{from,to}, …]` (z.B. Marschoun 2014–2020 + 2026–).

### Vote-Status

```js
Council.voteStatus(memberId, vote, session, member)
//   → 'yes' | 'no' | 'absent'
//     'yes-inferred' | 'no-inferred'    (einstimmig anon, abgeleitet)
//     'unknown'                          (split anon, ohne voters-Info)
//     null                               (Mitglied an dem Tag nicht im Rat)
```

Quellen-Priorität (in dieser Reihenfolge geprüft):

1. **Nicht aktiv** an `vote.date` → `null`
2. **session.absent** enthält Member → `'absent'`
3. **Named vote** mit yes/no/absent Arrays → entsprechender Status
4. **`vote.voters[id]`** (Anonym-Vote mit Teil-Information, z.B. selbst angegeben) → der eingetragene Status
5. **`vote.results.absent_ids`** (selten, brief absence im Vote) → `'absent'`
6. **Einstimmig anonym** (no=0 oder yes=0) → `'yes-inferred'`/`'no-inferred'`
7. Sonst → `'unknown'`

### Hilfs-Wrapper

```js
Council.voteStatusLabel("yes-inferred", true)  // → "Ja*"
Council.voteStatusLabel("absent")              // → "–"
Council.voteStatusBucket("yes-inferred")       // → "yes"  (für Aggregate)
```

## Wie ändere ich Verhalten?

**„Ich will, dass Enthaltungen im Profil anders dargestellt werden":** in
`voteStatus` einen neuen Status `'abstain'` returnen (z.B. wenn `vote.voters[id]
=== "abstain"`), in `voteStatusLabel` ein Label hinzufügen, in
`voteStatusBucket` zuordnen.

**„Anonym-Mehrheits-Inferenz ist mir zu mutig":** in Punkt 6 die beiden
`return`s auf `'unknown'` setzen. Ja*/Nein\* verschwinden überall.

**„Wer ist Stellvertreter zählt auch als regulär":** in `isRegularOf` zusätzlich
durch `cfg.seats[].sub` und `cfg.vicechairs[].sub` iterieren. Statistik würde
dann auch Substitutes-Voten mitzählen.

## Datenmodell (Kurzfassung)

```jsonc
// data/members.json → bodies[].seatConfigs[]
{
  "from": "2020-05-01", "to": "2026-04-30",
  "chair":  "dollinger",
  "vicechairs": [{ "member": "hadersdorfer", "sub": "heinz" },
                 { "member": "stanglmaier",  "sub": "becher_j" }],
  "seats": [
    { "member": "kieninger", "sub": "..." },                  // einfacher Sitz
    { "occupants": [{ "member": "john", "from": "...", "to": "2023-07-23" },
                    { "member": "strobl", "from": "2023-07-24" }] }  // Nachfolge
  ]
}
```

Annahme: **Ein Sitz ist nie unbesetzt.** Bei Niederlegung übernimmt sofort der
Nachfolger (`occupants` mit lückenlosen `from`/`to`). Ausschuss-Sitze haben
zudem immer einen `sub` (Stellvertreter). Wer bei einer Abstimmung
stimmberechtigt war, ergibt sich somit eindeutig aus Datum + Body-Config +
session.absent + session.substitutes.

## Wo wird's benutzt?

- `app.js` → `getMemberVoteStatus`, `computeVotingStats` (Profilansicht & Statistik-Card)
- `parliament.js` → `voteResMap` (Sitzfärbung im Sitzungssaal)
