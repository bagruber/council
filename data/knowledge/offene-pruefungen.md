# Offene Prüfungen

Einträge, die im Bestand stehen, aber noch gegengeprüft werden müssen. Sie
tragen im Datensatz `source.provisional: true` und werden in der Oberfläche
nicht als vorläufig ausgewiesen — die Markierung ist reine Buchführung.

Wenn geprüft: Flag entfernen und die Zeile hier streichen.

| Abstimmung | Datum | Was ist vorläufig | Woher |
|---|---|---|---|
| `sr_20250224_01` Kostenloser Hallenbadeintritt für Kinder | 24.02.2025 | Die Ja-Seite außer Beibl: fresh, Linke, Grüne, Beubl (8 Personen) | eigene Notizen |

Bestätigt ist an diesem Votum nur, was der Merkur-Artikel vom 24.02.2025 nennt:
Beibl dafür, Dollinger und Pschorr dagegen.

Die abgeleiteten acht ergeben zusammen mit Beibl exakt die neun Ja-Stimmen der
Niederschrift — das stützt die Notiz, beweist sie aber nicht. Denkbar wäre, dass
sich zwei Abweichungen gegenseitig aufheben.

---

## Andere offene Punkte ohne Dateneintrag

Diese stehen nirgends im Bestand, sollen aber nicht verlorengehen.

- **HVFA 07.12.2023, Pressestelle schaffen.** Die Sitzung steht im
  Sitzungsregister (19:00–22:35), eine Niederschrift liegt nicht vor. Notiz aus
  dem Gedächtnis: dagegen FW und Dollinger, Welter, Tristl. Die genannten
  Personen passen nicht zur gespeicherten Ausschussbesetzung — entweder waren
  Vertretungen da, oder es war doch das Plenum.
- **Drei Niederschriften mit Vertretungen** (`bpu_20240715`, `bpu_20240930`,
  `hvfa_20241128`): Anwesenheitsliste vorhanden, aber nicht eingearbeitet. Beim
  HVFA weicht die Liste von unserer Ausschussbesetzung 2020–2026 ab (Fincke,
  Lauterbach, Kilian Linz, Welter stehen dort als Ausschussmitglieder).
- **`sr_20220919_03` Verkaufsoffener Sonntag.** Johns Nein ist belegt, die
  17 Ja-Stimmen bleiben offen: die Sitzungsliste kennt sechs Abwesende, die
  Abstimmung zählt sieben.
- **`sr_20230626_03` Garagengebühr** (21:1). Ginge auf, wenn die eine
  Gegenstimme bekannt wäre.
- **`sr_20241021_03` Jugendbeauftragter** (15:2, 21.10.2024). Belegt aus dem
  Merkur-Artikel: Pschorr dagegen; Gruber, Hobmaier, Strobl und Beubl dafür.
  Vorläufig dazu die vier anwesenden Grünen (Kilian Linz, Beibl, Alexandra
  Becher, von Pressentin) und Dollinger — Stanglmaier, Johannes Becher und
  Kästl kamen laut Niederschrift erst um 19:30 bzw. 20:10, Fincke fehlte ganz,
  Grübl zählt nach seiner Niederlegung nicht mehr mit. Es bleibt eine Lücke von
  einer Stimme: 25 minus sieben Abwesende wären 18, abgestimmt haben 17.

---

## Aus der Presserecherche vom 02.09.2026

Eingetragen nach Durchsicht, mit diesen Resten:

- **`sr_20210208_07` Aufnahme aus Moria — erledigt, 15:6 ist richtig.** Beide
  Blätter schreiben 16:6, die Niederschrift 15:6. Aufgelöst durch die Zeile
  „StR Welter hat wegen kurzfristiger Abwesenheit nicht an der Abstimmung
  teilgenommen": 25 Sitze, 3 sitzungsabwesend, Welter nicht mitgestimmt — bleiben
  21 Stimmen, und 15 + 6 sind 21. Die Zeitungen haben ihn mitgezählt. Der Eintrag
  stand im Datensatz bereits korrekt unter `excluded`.
  **Lehre für die Presserecherche:** Weicht eine Zeitungszahl um genau eins ab,
  zuerst `excluded` und `session.absent` prüfen, bevor die Niederschrift in
  Zweifel gezogen wird.
- **`bpu_20240715_05` bis `_09` Rockermaier, je 7:4.** Die vier Nein-Stimmen
  sind aus der SZ namentlich belegt, damit ist diese Seite vollständig. Die
  Ja-Seite bleibt offen: anwesend waren laut den namentlichen Voten desselben
  Abends zwölf, abgestimmt haben elf. Wer von den übrigen acht nicht mitgestimmt
  hat, steht nicht fest — deshalb wurden die Voten nicht auf `named` gehoben.
  Die Anwesenheitsliste dieser Niederschrift ist ohnehin noch nicht eingearbeitet
  (siehe oben).
- **`sr_20230424_04` Ausschussgröße.** Die schon länger eingetragenen Positionen
  (Kästl, Grübl dafür; Dollinger, Weber, Kieninger, Pschorr dagegen) tragen keine
  `voterEvidence`-Markierung und gelten damit als harte Belege. Für Grübl
  („unterstützte das") ist das streng genommen zu viel — beim nächsten Anfassen
  auf `weich` setzen.
- **`sr_20210308_16` ist invertiert.** Der Beschluss lautet, von der Aufstellung
  eines Bebauungsplans *abzusehen*. Wer den Bebauungsplan wollte, steht dort mit
  Nein. Beim Nachtragen weiterer Stimmen aus diesem TOP nicht verwechseln.
- **Artikel-ID `merkur_2023-04-24_ausschussgroesse`** trägt das Sitzungsdatum,
  erschienen ist der Text am 27.04.2023. Das Feld `date` steht auf dem
  Erscheinungsdatum, die ID nicht — bei Gelegenheit angleichen.
