# Plan: Artikel gegen den Bestand prüfen

Noch nicht ausgeführt. Beschreibt, wie die 445 gecrawlten Artikel systematisch
gelesen und mit dem gelesen werden, was in `votes.json`, `sessions.json` und
`press.json` steht.

## Warum das nötig ist

Die Zuordnung, die bisher stattgefunden hat, ist mechanisch: Datum plus
Schlagwortabgleich. Sie findet, was übereinstimmt, und übersieht drei Dinge
zuverlässig:

1. **Widersprüche.** Steht im Artikel ein anderes Ergebnis als in der
   Niederschrift, fällt das nur auf, wenn jemand beide Zahlen nebeneinander
   legt. Der Moria-Fall hat gezeigt, dass so ein Widerspruch auflösbar ist —
   und dass die Auflösung schon im Datensatz stand.
2. **Stimmverhalten in Nebensätzen.** Der Extraktor sucht Namen im selben Satz
   wie eine Abstimmungswendung. Steht der Name einen Satz weiter
   („Dagegen stimmten die Grünen. Auch Kästl mochte nicht mit."), findet er
   nichts.
3. **Fraktionsangaben statt Namen.** „Die CSU stimmte geschlossen dagegen" ist
   auswertbar, sobald man weiß, wer an dem Abend für die CSU da war. Kein
   Muster im Extraktor deckt das ab.

## Vorgehen

**Einheit ist die Sitzung, nicht der Artikel.** Alle Artikel zu einem Abend
werden zusammen gelesen, dazu die Tagesordnung, die Ergebnisse und die
Anwesenheit. Sonst lässt sich nicht beurteilen, ob eine Zahl aufgeht.

Pro Sitzung wird geprüft:

| Frage | Woran |
|---|---|
| Nennt der Artikel ein Ergebnis, das von der Niederschrift abweicht? | Zahlen im Text gegen `results` |
| Erklärt sich eine Abweichung durch `excluded` oder `session.absent`? | **Zuerst prüfen** — der Moria-Fall |
| Nennt der Artikel Personen oder Fraktionen mit Position? | gegen `voters`, `voterEvidence` |
| Ist eine bekannte Seite jetzt vollständig? | Ja + Nein + Abwesend = Stimmberechtigte |
| Behandelt der Artikel TOPs, an denen er nicht hängt? | gegen `agenda[].press` |
| Hängt er an TOPs, die er nicht behandelt? | dito, andere Richtung |

**Reihenfolge.** Zuerst die 32 Sitzungen, an denen schon Artikel hängen — dort
ist der Ertrag am höchsten und der Fehler am teuersten. Dann die 159 Artikel
aus dem Arbeitsvorrat, nach Jahr absteigend, weil die jüngeren Sitzungen die
meisten offenen Voten haben.

**Umfang je Durchgang.** Fünf bis acht Sitzungen. Mehr passt nicht in ein
Kontextfenster, ohne dass die Sorgfalt nachlässt — und Sorgfalt ist hier der
einzige Grund, das überhaupt so zu machen.

## Ergebnisformat

Kein automatischer Schreibzugriff. Jeder Durchgang erzeugt einen Vorschlag mit
Belegsatz, wie `BERICHT.md`, getrennt nach:

- **Widerspruch** — Artikel und Bestand sagen Verschiedenes. Immer vorlegen.
- **Neu ableitbar** — Positionen, die der Extraktor nicht gefunden hat.
- **Bestätigt** — Artikel deckt sich mit dem Bestand. Nur zählen, nicht listen.
- **Falsch verknüpft** — Artikel hängt an einem TOP, den er nicht behandelt.

Eingetragen wird erst nach Durchsicht, mit einem Skript nach dem Muster von
`scripts/apply_presse_2026-09.py`.

## Was der Plan nicht leistet

Hinter der Bezahlschranke steht nur der Anfang des Artikels. Bei merkur und SZ
sind das oft die ersten zwei Absätze — das Abstimmungsergebnis steht am Ende.
Die Archivkopien enthalten teils mehr als die Live-Seite, aber nicht immer.
Wo der Text abbricht, bleibt es bei „nicht überliefert"; das ist kein Fehler
der Prüfung, sondern ihre Grenze.
