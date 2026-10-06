# `js/core.js` — geteilte Logik für Mandate und Stimmen

`Council` ist das gemeinsame Modul für die Stellen, die sonst je eigene
Antworten auf dieselbe Frage gäben:

| Konsument | Was er braucht |
|---|---|
| `views/profil.js`, Sitzungsliste | Pro Beschluss: wie hat diese Person gestimmt? |
| `views/profil.js`, Statistik-Card | Dieselbe Frage, aber als Aggregat |
| `views/naehe.js` | Dieselbe Frage, um Paare zu vergleichen |
| `parliament.js` | Dieselbe Frage, pro Sitz im Halbrund |
| `views/fraktion.js`, `parliament.js`, `profil.js` | In welcher Fraktion saß jemand an diesem Tag? |

## Mandate

Mandat, Fraktion und Rolle stehen als **eine geordnete Liste von Abschnitten**
am Mitglied:

```jsonc
"mandates": [
  { "from": "2014-05-01", "to": "2020-05-01", "party": "fw", "role": "councillor" },
  { "from": "2020-05-01", "to": "2025-01",    "party": "fw", "role": "mayor" },
  { "from": "2025-01",    "to": "2026-04-30", "party": "parteilos", "role": "mayor" }
]
```

Drei Regeln, und sie sind der ganze Trick:

1. **Eine Lücke zwischen zwei Abschnitten ist eine Unterbrechung des Mandats.**
   Marschoun saß 2014 bis 2020 und wieder seit 2026; dazwischen zählt er nicht.
2. **Kein Abstand heißt Fraktions- oder Rollenwechsel, nicht neues Mandat.**
   Dollinger blieb durchgehend im Rat, wurde 2020 Bürgermeister und trat 2025
   bei den Freien Wählern aus.
3. **Berühren sich zwei Abschnitte an ihrer Grenze, gilt der spätere.**
   Hadersdorfer wechselte am 06.10.2017 zur CSU — dieser Tag gehört schon der
   CSU. Monatsangaben (`"2025-01"`) meinen als Ende den Monatsletzten.

```js
Council.memberActiveAt(m, "2023-07-24")  // → true/false
Council.mandateAt(m, "2023-07-24")       // → der Abschnitt, oder null
Council.partyAt(m, "2023-07-24")         // → "fw" | null
Council.mandateSpans(m)                  // → die echten Mandatszeiten
Council.partySpans(m)                    // → Zeitspannen je Fraktion
```

`mandateSpans` fasst zusammenhängende Abschnitte zusammen und beantwortet
„seit wann im Rat"; `partySpans` fasst nach Fraktion zusammen und beantwortet
„wann bei wem". Beides braucht das Profil, und beides ist etwas anderes als
die rohe Abschnittsliste: ein Ausschusssitz endet mit dem *Mandat*, nicht mit
einem Fraktionswechsel.

`from`, `to`, `party` und `role` am Mitglied selbst gibt es nicht; `daten.js`
leitet sie beim Laden aus erstem und letztem Abschnitt ab, damit die Views den
Jetzt-Zustand direkt lesen können.

## Gremien

```js
Council.bodyConfigAt(bpu, "2026-01-01")   // → seatConfig, am Datum gültig
Council.isRegularOf(member, body, date)   // → true bei Stamm-Sitz, nicht bei Vertretung
```

Gremien ohne Perioden (Aufsichtsrat, Verbandsrat) tragen ihre Besetzung direkt
am Objekt. Gremien mit Perioden haben außerhalb aller Perioden **keine**
bekannte Besetzung — nicht etwa die heutige.

## Vote-Status

```js
Council.voteStatus(memberId, vote, session, member)
//   → 'yes' | 'no' | 'absent'
//     'yes-inferred' | 'no-inferred'   einstimmig anonym, aus der Anwesenheit abgeleitet
//     'excluded'                        anwesend, aber persönlich beteiligt (Art. 49 GO)
//     'abstained'                       anwesend, enthalten
//     'restricted'                      anwesend, aber nicht stimmberechtigt
//     'unknown'                         nicht überliefert
//     null                              an dem Tag nicht im Rat
```

Quellen, in dieser Reihenfolge geprüft:

1. Kein Mandat am Tag der Sitzung → `null`
2. `vote.excluded` nennt die Person → je nach `reason`
3. `session.absent` nennt sie → `'absent'`
4. Namentliche Abstimmung → die Listen in `vote.results`
5. `vote.voters[id].vote` → diese Stimme
6. `vote.results.absent_ids` → `'absent'`
7. Einstimmig anonym und `inferable !== false` → `'yes-inferred'` / `'no-inferred'`
8. Sonst → `'unknown'`

Punkt 2 steht bewusst vor Punkt 3: wer befangen ist, war ja da. Die Gründe sind
ein fester Satz — `beteiligung`, `enthaltung`, `nicht_stimmberechtigt`,
`kein_mandat`, `kurz_abwesend`. Alles andere fällt auf `'absent'` durch, und
genau das ist einmal passiert: ein Eintrag mit dem Prosa-Grund „persönliche
Beteiligung" zeigte den Bürgermeister bei seiner eigenen Entlastung als
abwesend. Deshalb prüft der Validator die Codes.

`inferable` steuert Punkt 7: `false` sperrt die Ableitung ganz (die
Niederschrift weist weniger Stimmen aus als Stimmberechtigte da waren),
`"teilweise"` sperrt sie nur für die, die laut `session.partial` später kamen
oder früher gingen.

```js
Council.voteStatusLabel("yes-inferred", true)  // → "Ja*"
Council.voteStatusTitle("absent")              // → "Abwesend"
Council.isUnanimous(vote)                      // → true/false
```

## Herkunft

`source` sagt, woher das Ergebnis stammt, `voters[<id>]` woher die einzelne
Stimme. Beide sprechen dieselbe Sprache:

```jsonc
"source": { "tier": "tracked", "by": "gruber" },
"voters": {
  "strobl": { "vote": "yes", "tiers": ["selbstauskunft"], "by": "strobl",
              "evidence": "soft", "note": "„ein Kompromiss …“" }
}
```

| `tier` | Bedeutung |
|---|---|
| `protocol-explicit` | Die Niederschrift nennt jeden Namen. |
| `protocol-implicit` | Einstimmig, aus der Anwesenheit erschlossen. |
| `tracked` | Von einer benannten Person im Saal erfasst. |
| `press` | Aus einem Zeitungsartikel rekonstruiert. |
| `selbstauskunft` | Aus eigenen Notizen eines Mitglieds. |
| `result-only` | Nur Ja und Nein überliefert, sonst nichts. |

`result-only` ist die unterste Stufe und hat bewusst keine Beschriftung: zu
benennen gibt es nichts, und `views/voten.js` setzt dort seinen eigenen Satz.
Vorher stand bei diesen 329 Beschlüssen gar keine Stufe, und „keine Stufe"
hieß an drei Stellen etwas anderes.

```js
Council.voterTiers(vote, "gruber")     // → Belege dieser Stimme, stärkster zuerst
Council.sourceLabel(vote)              // → "Aus Presseberichten"
Council.evidenceNote(vote, "strobl")   // → Hinweis bei evidence: "soft"
Council.statusProvenance(status, vote, "strobl")   // beides für title-Attribute
```

Ein `voters`-Eintrag **ohne** `vote` trägt nur die Herkunft; die Listen in
`results` behalten dann das Wort. `evidence: "soft"` heißt: die Quelle berichtet,
wie diese Person *argumentiert* hat, nicht wie sie gestimmt hat. Die Position
steht trotzdem im Datensatz — mit Hinweis, ohne eigene Farbe.

## Wie ändere ich Verhalten?

**„Enthaltungen sollen im Profil anders aussehen":** in `voteStatusLabel` und
`voteStatusTitle` die Beschriftung von `'abstained'` ändern; der Status selbst
kommt schon aus `vote.excluded`.

**„Die Ableitung aus Einstimmigkeit ist mir zu mutig":** in Punkt 7 die beiden
`return`s auf `'unknown'` setzen. Ja\*/Nein\* verschwinden überall.

**„Vertretungen sollen als regulär zählen":** in `isRegularOf` zusätzlich durch
`cfg.seats[].sub` und `cfg.vicechairs[].sub` gehen. Die Statistik zählte dann
auch Vertretungs-Stimmen mit.

## Datenmodell (Kurzfassung)

```jsonc
// data/bodies.json → [].seatConfigs[]
{
  "from": "2020-05-01", "to": "2026-04-30",
  "chair":  "dollinger",
  "vicechairs": [{ "member": "hadersdorfer", "sub": "heinz" }],
  "seats": [
    { "member": "kieninger", "sub": "…" },
    { "occupants": [{ "member": "john", "to": "2023-07-23" },
                    { "member": "strobl", "from": "2023-07-24" }] }
  ]
}
```

Annahme: **ein Sitz ist nie unbesetzt.** Bei Niederlegung übernimmt sofort die
Nachfolge (`occupants` mit lückenlosen `from`/`to`). Wer bei einer Abstimmung
stimmberechtigt war, ergibt sich damit eindeutig aus Datum, Gremienbesetzung,
`session.absent` und `session.substitutes`.

Die vollständige Form aller Dateien steht als JSON Schema in `data/schema/`.

## Wo wird's benutzt?

- `views/profil.js` → `computeVotingStats`, `renderMemberTimeline`
- `views/naehe.js` → `stances`, `similarity`, `partyAtDate`
- `views/fraktion.js` → `partySpans`
- `parliament.js` → `voteResMap`, `partyAt` (Sitzfärbung im Halbrund)
- `js/daten.js` → `memberActiveAt`, und das Ableiten von `from`/`to`/`party`/`role`

## Tests

```bash
node --test "tests/*.test.mjs"
```

`tests/core.test.mjs` prüft Mandate, Gremienbesetzung, alle Zweige von
`voteStatus` und die Herkunft; `tests/naehe.test.mjs` das Ähnlichkeitsmaß an
erfundenen Daten.
