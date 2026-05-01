# München-Mockup

Statisches Mockup zur Vorstellung des App-Konzepts für München.

## Struktur

- `index.html` — Übersicht mit Demo-Themenliste und Beispielprofil
- `topic.html` — Beispiel-Topic „Tram-Westtangente" (Timeline + Hufeisen-Abstimmung)
- `profile.html` — Beispielprofil Christian Ude (SPD, Alt-OB)
- `css/munich.css` — Farb-Overrides (Schwarz / München-Gold)

Erbt sonst `../css/style.css` und `../img/members/ude.png.png` aus dem Hauptprojekt.

## Lokal anschauen

Vom Repo-Root:

```bash
npx serve
# dann http://localhost:3000/munich/
```

## Als Subdomain deployen

Zwei Wege:

1. **GitHub Pages mit Rewrite/Pfad**: Auf eigener Domain `munich.example.com` per CNAME auf den `gh-pages`-Branch zeigen und nur den `munich/`-Inhalt deployen (eigener Repo / Branch oder `--directory munich`).
2. **Netlify/Vercel**: Site mit Build-Verzeichnis `munich/` anlegen, Subdomain im Dashboard konfigurieren.

Inhalt ist statisch — kein Build, keine Abhängigkeiten zur Laufzeit.

## Hinweis

Alle Inhalte sind frei erfunden und dienen ausschließlich der Layout-Demonstration. Die echten Münchner Stadtratsvorgänge sind nicht abgebildet.
