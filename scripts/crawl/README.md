# Presserecherche zum Stimmverhalten

Sucht in Moosburger Zeitung (idowa), Freisinger Tagblatt (merkur) und
Süddeutscher Zeitung nach Artikeln, in denen Stadtratsmitglieder mit ihrem
Abstimmungsverhalten genannt werden, und ordnet die Fundstellen den Voten
in `data/votes.json` zu.

**Die Pipeline schreibt nichts in den Datenbestand.** Ergebnis ist ein
Vorschlag mit Belegsatz in `data/crawl/`, der von Hand geprüft und dann
über `/presseartikel-einarbeiten` bzw. `scripts/apply_presse_stimmen.py`
eingetragen wird.

## Warum nicht direkt bei den Zeitungen

`merkur.de` sperrt in seiner `robots.txt` alles ausser einer namentlichen
Liste von Crawlern:

```
user-agent: *
Allow: /ueber-uns/
Disallow: /
```

Ein eigenes Skript steht nicht auf dieser Liste, also holt es dort auch
nichts. idowa und sueddeutsche.de erlauben den Zugriff, aber ihre Archive
sind nur wenige Wochen tief (idowa) oder werden per JavaScript nachgeladen
(SZ-Suche liefert im HTML null Treffer).

Deshalb laufen beide Schritte über öffentliche, für Maschinen gedachte
Schnittstellen:

| Zweck | Quelle |
|---|---|
| Welche Artikel gibt es? | CDX-Index des Internet Archive |
| Wann ist er erschienen? | `datePublished` in der Archivkopie |
| Volltext | Archivkopie, nie der Verlagsserver |
| Alternativ, mit exaktem Datum | Google-News-RSS (`fetch.py news`) |

Was hinter einer Bezahlschranke steht, steht auch in der Archivkopie nicht
drin — solche Artikel landen im Bericht unter "nur Sitzungsbezug".

## Ablauf

```
python scripts/crawl/targets.py --limit 60 --json   # welche Voten lohnen
python scripts/crawl/fetch.py index                 # Artikel-URLs aus dem Archiv
python scripts/crawl/fetch.py sweep                 # Volltexte holen (~500, dauert)
python scripts/crawl/extract.py --report            # auswerten
```

Ergebnis in `data/crawl/`:

- `targets.json` — Voten, sortiert danach, wie wahrscheinlich die Zeitung
  Namen genannt hat: knappes Ergebnis, einzelne Gegenstimme, Plenum statt
  Ausschuss.
- `index.json` — alle im Archiv bekannten Artikel-URLs der drei Blätter.
- `findings.json` — Artikel, Sitzungszuordnung, gefundene Sätze.
- `BERICHT.md` — dasselbe zum Lesen, getrennt nach "mit Stimmverhalten"
  und "nur Sitzungsbezug".

`match.py` ist der schmalere Weg über einzelne Beschlüsse statt über
Sitzungen — nützlich, wenn gezielt zu einem Votum gesucht wird.

## Wie die Zuordnung zustande kommt

Ein Lokalartikel berichtet von einem Sitzungsabend, nicht von einem TOP.
Deshalb wird zuerst über das Erscheinungsdatum eine Sitzung gesucht (0 bis
14 Tage danach), dann innerhalb dieser Sitzung über Schlagwortabgleich der
passende TOP.

Für die Namen reicht es nicht, dass ein Nachname im Text steht — er muss
im selben Satz wie eine Abstimmungswendung stehen ("gegen die Stimmen
von", "enthielt sich", "stimmte dagegen"). Der Satz wird mitgeschrieben.

Zwei Fallen bleiben und werden im Bericht markiert statt geraten:

- **Gleiche Nachnamen.** Becher (Johannes/Alexandra), Linz (Karin/Kilian).
  Steht der Vorname im Satz, wird aufgelöst, sonst `(?)`.
- **Indirekte Rede.** "X kritisierte den Antrag" heisst nicht, dass X
  dagegen gestimmt hat. Der Bericht liefert den Satz, die Einordnung
  bleibt beim Lesen.
