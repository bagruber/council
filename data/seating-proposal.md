# Sitzordnung Stadtrat Moosburg

## Geometrie

Das Plenum hat **24 Sitze in 2 Reihen** + **1 BM** (Bürgermeister, unterhalb des Hufeisens).

- **Innenreihe**: 10 Sitze (Index 1–10)
- **Außenreihe**: 14 Sitze (Index 11–24)
- **BM**: 1 Sitz, unterhalb der Saalmitte

Nummerierung läuft vom **BM-links** (= Audience-rechts) im Uhrzeigersinn (von außen betrachtet) über den oberen Bogen bis zum **BM-rechts** (Audience-links):

```
                            18    17                          
                  19                       16                 
         20       7      6      5      4       15             
    21                                              14        
              8                              3                
22            9                              2              13
     23                                            12         
                 10                       1                   
            24                                  11            
                          ◯ BM
```

(BM ist die Person in der Mitte unten. Audience-Sicht: Saal von außen.)

**BM-Sicht** (BM schaut auf den Saal):
- BM-links (= politisch links nach deutscher Konvention): Sitze 1–10 niedrige Nummern
- BM-rechts: Sitze 10, 24 (rechte Seite)

## Datenstruktur-Vorschlag

In `members.json` bei `bodies.plenum`:

```json
{
  "id": "plenum",
  "name": "Stadtrat",
  ...
  "rows": 2,
  "seats": [
    // Index 0 = Sitz 1 (innen, BM-links)
    { "occupants": [{ "member": "<id>", "from": "2020-05" }] },
    ...
    // Sitz mit Nachrücker:
    { "occupants": [
      { "member": "wittmann", "to": "2021-10" },
      { "member": "gruebl",   "from": "2021-10", "to": "2024-10" },
      { "member": "hobmaier", "from": "2024-10" }
    ]},
    ...
  ]
}
```

## 2020–2026 Sitzverteilung (zum Ausfüllen)

Parteien in BM-links-zu-BM-rechts Reihenfolge — du legst fest:
- Grüne (6): linker Block
- FW (4)
- fresh (2 zeitgleich; Sitzhistorie: wittmann→gruebl→hobmaier auf einem Sitz; neumayr→gruber auf dem anderen)
- Linke (1)
- ÖDP (1)
- FDP (1)
- AfD (1)
- SPD (2; beubl→marcus auf einem)
- CSU (6): rechter Block

### Innenreihe (Sitze 1–10)

| Sitz | Person(en) mit Zeitraum |
|------|-------------------------|
| 1    | _____ |
| 2    | _____ |
| 3    | _____ |
| 4    | _____ |
| 5    | _____ |
| 6    | _____ |
| 7    | _____ |
| 8    | _____ |
| 9    | _____ |
| 10   | _____ |

### Außenreihe (Sitze 11–24)

| Sitz | Person(en) mit Zeitraum |
|------|-------------------------|
| 11   | _____ |
| 12   | _____ |
| 13   | _____ |
| 14   | _____ |
| 15   | _____ |
| 16   | _____ |
| 17   | _____ |
| 18   | _____ |
| 19   | _____ |
| 20   | _____ |
| 21   | _____ |
| 22   | _____ |
| 23   | _____ |
| 24   | _____ |

### BM
| Sitz | Person(en) mit Zeitraum |
|------|-------------------------|
| BM   | dollinger (2020-05 → 2026-05), mader (2026-05 →) |

---

## Hinweise

- **Sub-Reihenfolge**: Wo in der Reihe sitzen die jeweiligen Parteien? Häufige Konvention: politisch links auf BM-links. Heißt für Moosburg: Grüne 1–3 innen + 11–13 außen?
- **fresh-Sitze** sind speziell: 2 Sitze, jeder mit eigener Nachrücker-Kette.
- **Wittmann ↔ Gruebl ↔ Hobmaier**: wittmann (bis 10/2021), gruebl (10/2021 bis 10/2024), hobmaier (ab 10/2024) — gleicher Sitz.
- **Neumayr ↔ Gruber**: neumayr (bis 01/2022), gruber (ab 01/2022) — gleicher Sitz.
- **Beubl ↔ Marcus**: beubl (bis 03/2025), marcus (ab 03/2025) — gleicher Sitz.

Wenn du keine genaue Sitzverteilung im Kopf hast, kann ich auch einen sinnvollen Vorschlag generieren — basierend auf `seatOrder` aus `members.json` und einer Heuristik (Fraktionen zusammen, größere am Rand, Sprecher/Bürgermeister-Stellvertreter näher am BM).
