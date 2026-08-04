# Plattform-Kontext

Wo diese App läuft und was beim Ändern zu beachten ist. Der übergreifende
Kontext steht im Repo `bagruber/moosburg-eu` in `BRIEFING.md`.

*Stand: August 2026*

---

## Diese App läuft zweifach

| | Adresse | Quelle |
|---|---|---|
| GitHub Pages | `bagruber.github.io/council/` | Branch `parliament-v2`, roh ausgeliefert |
| moosburg.eu | `moosburg.eu/stadtrat/` | Branch `parliament-v2` über `.github/workflows/deploy.yml` |

**Beide kommen aus `parliament-v2`.** Ein Commit dorthin erreicht beide
Varianten — es braucht keine Doppelpflege. Ein Commit nach `main` erscheint
dagegen **nirgends**: `main` liegt zurück und ist an keinen der beiden
Auslieferungswege angeschlossen.

Sollte `parliament-v2` je nach `main` gemergt werden, müssen beide Stellen
umgestellt werden: die Pages-Quelle in den Repo-Einstellungen und der Trigger
in `deploy.yml`.

## Was nicht mit auf den Server geht

Der Workflow schließt aus:

| Ausschluss | Warum |
|---|---|
| `img/members/originals/**` | 167 MB unkomprimierte PNG-Vorlagen, aus denen die `.webp` erzeugt wurden. Die Seite referenziert sie nirgends. Ohne sie sinkt der Upload von 199 MB auf 32 MB. |
| Werkzeug-Ordner mit führendem Punkt | Konkrete Einträge siehe `deploy.yml`. `**/.git*` deckt `.github` und `.gitignore` ab, **nicht** beliebige Punkt-Ordner: Deren `.md`-Dateien fielen zwar unter `**/*.md`, die leeren Verzeichnisse landeten trotzdem auf dem Server. Wer einen neuen anlegt, trägt ihn nach. |
| `docs/**`, `scripts/**`, `**/*.md`, `debug.log` | Gehört nicht zur ausgelieferten Seite. |

Der erste Deploy überträgt rund 32 MB und dauert etwa zwei Minuten, danach
läuft er inkrementell.

## Pfade müssen relativ bleiben

Die App liegt auf moosburg.eu in einem Unterordner. Alle Verweise sind relativ
(`fetch("data/topics.json")`, `src="js/app.js"`) — deshalb funktioniert sie
dort ohne jede Anpassung. Ein führender Slash würde das brechen.

## Was die serverweite `.htaccess` vorgibt

Auf moosburg.eu wirkt eine `.htaccess` aus dem Repo `moosburg-eu` auf alle
Unterordner mit. Relevant hier:

- **JS und CSS werden nicht gecacht** — die Pfade sind fest und ohne Hash.
  Nach einem Deploy kann trotzdem ein harter Reload nötig sein, weil Browser
  auch ohne Anweisung heuristisch cachen.
- **Verzeichnisauflistung ist aus**, `/stadtrat/data/` ist also nicht browsebar.
- **Punkt-Pfade liefern 403.**

Auf GitHub Pages gilt davon nichts — dort greift keine `.htaccess`.

## Datenmodell: Herkunft der Stimmen

Jede Abstimmung trägt optional ein `source`-Objekt. Die Stufe entscheidet, was
`renderVoteSource` anzeigt:

```json
"source": { "tier": "tracked", "by": "gruber", "byName": "Vorname Nachname" }
```

| `tier` | Bedeutung |
|---|---|
| `protocol-explicit` | Die Niederschrift nennt jeden Namen. |
| `protocol-implicit` | Einstimmig, aus der Anwesenheit erschlossen. |
| `tracked` | Von einer benannten Person im Saal erfasst. |
| `press` | Aus einem Zeitungsartikel rekonstruiert. |

`by` ist eine Mitglieds-ID aus `data/members.json` und verlinkt aufs Profil.
`byName` fängt alle ab, die **kein Mandat** haben — Presseleute etwa. Ohne
diesen Fallback stünde die Stufe „mitgeschrieben" da, ohne zu sagen von wem,
und das ist der halbe Wert der Angabe.

### Woher `tracked`-Daten kommen

Das Sitzungstool (`bagruber/council-voting-tool`) kann den öffentlichen Teil
einer Sitzung nach `moosburg.eu/api/sessions` übermitteln. Das ist ein
**Posteingang**, kein Live-Feed: Der Weg von dort in `data/votes.json` ist
Handarbeit, weil erst dabei die Zuordnung zu Dossiers, Anträgen und Presse
entsteht — genau das, was diese App ausmacht.

Abholen und übertragen ist im README von `moosburg-eu` beschrieben. Das Feld
`erfasstVon` des abgeholten Datensatzes liefert `by` und `byName`.

## Gestaltung

Die Farb- und Schrift-Tokens stehen in [DESIGN.md](DESIGN.md).

### Verbotenes Muster: der einseitige Kantenakzent

Ein dekorativer Farbbalken entlang **einer** Kante einer Karte oder Box ist in
allen Moosburg-Projekten unerwünscht — er ist die Standardausgabe gängiger
Vorlagen und dekoriert eine Unterscheidung, die die Hierarchie ohnehin trägt.

Stattdessen typografisch unterscheiden oder über die ganze Fläche (eigener
Grundton samt Rahmen).

**Keine Verstöße:** Der Aktiv-Unterstrich der Tab-Navigation ist eine
Zustandsanzeige, die Zeitstrahl-Schiene in `Geschichte` ist Struktur, der
Zitat-Einzug von `.vote-text` ist klassische Typografie mit neutraler
Haarlinie. Diese drei bleiben.

### Ein Aufklapp-Muster im Haus

Für zusammenklappbare Abschnitte gibt es genau eine Sprache: `<details>` mit
`+`/`–` als Marker rechts, ohne den nativen Dreiecks-Marker. Verwendet von
`.voting-stats` und `.home-meta`. Neue Aufklapper übernehmen sie, statt eine
zweite einzuführen.

### Rangfolge auf der Startseite

Die Zahlen zum Bestand (Statistik, Datenlage, Presse) stehen **über** der
Themenliste, aber zugeklappt. Sie ordnen ein, was folgt — dafür müssen sie
davor stehen. Aufgeklappt würden sie die Themen unter die Falz drücken, und
die sind der eigentliche Einstieg.
