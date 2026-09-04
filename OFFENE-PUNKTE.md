# Offene Punkte

*Notiert am 30.08.2026. Erledigte Punkte bitte streichen, nicht abhaken - die
Datei soll kurz bleiben.*

## Der Werkzeugstand ist aus einem Clone nicht rekonstruierbar

`.gitignore` schliesst `package.json` und `package-lock.json` aus. Damit ist
das einzige Dokument, das einen Node-Anteil beschreiben wuerde, aus der
Historie genommen. Wer klont, sieht in `index.html` drei plain
`<script src="js/...">` und sonst nichts - kein Bundler, kein CDN, keine
Fremdabhaengigkeit. Das ist eine vertretbare Bauweise, sie ist nur nirgends
als solche festgehalten, und ausserhalb des Repos ist daraus die Behauptung
"React, TypeScript, Vite" geworden.

Die 40 Skripte in `scripts/` sind Python und haben weder `requirements.txt`
noch `pyproject.toml`. Sie erzeugen `data/bundle.json`, das ebenfalls ignoriert
wird. Der Teil des Projekts, der die Substanz liefert - die Datenpipeline -
ist damit der am schlechtesten dokumentierte.

**Empfehlung, hier bewusst nicht ausgefuehrt:** eine `requirements.txt` (oder
ein `pyproject.toml`, falls ohnehin ein venv im Spiel ist), und zwei Saetze im
README, dass das Frontend absichtlich ohne Build laeuft. Was in die
`.gitignore` gehoert und was ein Projekt ueber sich behauptet, ist eine
Entscheidung und keine Aufraeumarbeit.

## Haengt an gruber.am

Die Projektliste auf gruber.am liest **nichts** aus diesem Repo. Der Eintrag
wird von Hand in `gruberam/site/src/data/projects.ts` gepflegt und stand am
30.08.2026 so drin:

```ts
id: "council"
stack: ["Python", "JavaScript"]
```

Bis zum 30.08.2026 stand dort `["React", "TypeScript", "Vite"]` - wovon nichts je in diesem Repo lag.

Wer hier die Sprache, das Framework oder die Datenbank wechselt, das Repo
umbenennt, archiviert oder privat schaltet, muss den Eintrag dort nachziehen.
Die Seite merkt es von allein nicht.

Alle Repos mit so einem Abschnitt finden:

```bash
grep -rl "Haengt an gruber.am" ~/Documents/GitHub/bagruber/*/OFFENE-PUNKTE.md
```

## Eine Farbe steht neben dem Kanon

`--text-muted: #6F6F6F` in `css/style.css` ist der letzte Farbwert, der nicht
aus `css/tokens.css` kommt. Der Kanon fuehrt `--color-ink-muted: #6f6b63`, also
denselben Ton eine Spur waermer. Ob das Absicht war, laesst sich der Datei nicht
mehr ansehen.

Entweder auf `var(--color-ink-muted)` umstellen (dann faellt der Unterschied
niemandem auf, und die Farbe kann nicht mehr driften) oder mit einem Satz
begruenden, warum diese App hier abweicht. Ebenfalls nicht aus dem Kanon,
aber begruendet: die Abstimmungsfarben, das ausgewaschene Gold `--gap` und
`--surface`.
