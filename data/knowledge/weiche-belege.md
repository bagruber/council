# Weiche Belege

Wann eine Einzelstimme als *weich* gilt, wie sie gespeichert wird und wo die
Grenze zum harten Beleg liegt. Die Kurzfassung steht in `docs/CORE.md`, hier
die Begründung und die Fälle.

## Hart und weich

**Hart** ist ein Beleg, wenn er die Abstimmung selbst beschreibt:

- Die Niederschrift nennt die Person namentlich, oder ihre Stimme folgt aus
  Anwesenheit und Ergebnis.
- Die Mitschrift aus der Sitzung führt sie in der Ja- oder Nein-Liste.
- Die Zeitung berichtet das Abstimmungsverhalten: „gegen die Stimmen von X“,
  „X stimmte dagegen“, „einzige Gegenstimme war X“.
- Die Stimme ergibt sich aus dem Verfahren. Wer einen Änderungsantrag stellt,
  der abgelehnt wird, hat gegen den ursprünglichen Beschlussvorschlag gestimmt
  (Beibl und Strobl bei der Graf-Burkhard-Straße, `sr_20240617_07`).

**Weich** ist ein Beleg, wenn er nur beschreibt, wie jemand *argumentiert* hat,
und die Stimme daraus erschlossen wird. Die Zeitung zitiert eine Wortmeldung,
nicht eine Handhebung.

## Beispiele: Graf-Burkhard-Straße, 17.06.2024

Aus dem Merkur-Bericht vom 20.06.2024. Alle drei stehen als weiches Ja im
Datensatz:

> Was bei CSU-Fraktionschef Rudolf Heinz wiederum Skepsis hervorrief: „Ich
> weiß nicht, ob in dem Viertel jemals ein Gerber war.“

Heinz zweifelt einen *Gegenvorschlag* an. Dass er deshalb für Graf Burkhard
gestimmt hat, ist ein Schluss über zwei Schritte — naheliegend, aber nicht
berichtet.

> Karin Linz (CSU) hat zwar „nichts gegen Burkhard, aber ich bin schon von
> mehreren Frauen angesprochen worden, ob wir nicht öfter mal Frauen-Namen
> nehmen können“

Das ist die unsicherste der drei Aussagen. „Nichts gegen“ spricht für Ja, das
„aber“ lässt eine Enthaltung oder ein Nein offen.

> Den Vorschlag der Stadtverwaltung „Graf-Burkhard-Straße“ bezeichnete
> Ortschef Josef Dollinger als vernünftig, „weil wir in direkter Nähe die
> Graf-Konrad-Straße haben“.

Die deutlichste Aussage. Weich bleibt sie trotzdem: ein Urteil über den
Vorschlag, keine Stimme.

Aus derselben Logik folgt ein Fall, der schon im Bestand steht: „X unterstützte
das“ ist weich, nicht hart (siehe `offene-pruefungen.md`, `sr_20230424_04`).

## Speicherung

```jsonc
"voters":        { "dollinger": "yes" },
"voterEvidence": { "dollinger": "weich" },
"source":        { "tier": "press", "pressId": "merkur_2024-06-20_…" }
```

- Die Position steht in `voters`, genau wie bei einem harten Beleg.
- `voterEvidence[id] = "weich"` markiert sie. Ohne Eintrag gilt der Beleg als hart.
- Eine Selbstauskunft kommt über `voterSource[id]` dazu, nicht über
  `voterEvidence`. Sie ist eine eigene Herkunft, kein weicher Pressebeleg.

## Darstellung

- Im Profil trägt der Chip dieselbe Farbe wie jede Ja- oder Nein-Stimme, mit
  gepunktetem Unterstrich.
- Der Tooltip lautet „aus einer Wortmeldung erschlossen, nicht als Stimme berichtet“.
- Auf der Sitzungsseite stehen die Namen mit „aus der Debatte“ unter dem Beschluss.

## Regeln

- **Hart schlägt weich.** Kommt für dieselbe Person ein harter Beleg dazu,
  entfällt die Markierung.
- **Die Zahlen gehen vor.** Mehr bekannte Stimmen auf einer Seite, als das
  Ergebnis hergibt, heißt: ein weicher Beleg ist falsch. Er wird entfernt,
  nicht das Ergebnis angezweifelt.
- **Nur Anwesende.** Wer laut Niederschrift fehlte, bekommt keine erschlossene
  Stimme, auch wenn er in der Debatte zitiert wird. Die Debatte kann aus einer
  früheren Sitzung stammen.
- **Im Zweifel nichts eintragen.** Lässt eine Wortmeldung beide Stimmen zu,
  bleibt das Fragezeichen.

## Was nicht weich ist

**Stimmen aus eigenen Notizen** gehören in die Selbstauskunft, nicht zu den
weichen Pressebelegen. Weich heißt: erschlossen aus einer zitierten
Wortmeldung. Wer dagegen aus eigenen Aufzeichnungen weiß, dass „die übrigen
Grünen dagegen“ waren, hat keine Wortmeldung gedeutet, sondern etwas notiert.

So entschieden am 14.09.2026 für `sr_20240617_07`: Becher J., Becher A. und
Linz Kilian stehen dort mit `voterSource: ["selbstauskunft"]`, ohne
`voterEvidence`.

Beschrieben wird die Selbstauskunft als **aus eigenen Notizen rekonstruiert**,
nicht als Angabe aus der Erinnerung — das zweite klingt nach Hörensagen und
wird dem Material nicht gerecht.

## Offen

**Weiche Belege und die Gegenseite.** Ist eine Seite nur mit Hilfe weicher
Belege vollständig, darf die andere Seite dann trotzdem ausgerechnet werden?
Bisher ist das nur mit harten Belegen geschehen.
