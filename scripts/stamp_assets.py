"""Haengt eine Inhaltskennung an die Asset-Verweise in index.html.

Ohne sie liefert der Browser nach einem Deploy weiter die alte Datei aus —
GitHub Pages setzt zwar max-age=600, aus dem Disk-Cache kommt eine offene
Registerkarte aber auch danach noch an den alten Stand. Ein veraenderter
Query-String macht daraus eine andere URL, und der Cache greift nicht mehr.

Ein gemeinsamer Hash ueber alle Assets: aendert sich eine Datei, laedt der
Browser alle neu. Das kostet ein paar Kilobyte und spart die Fehlersuche.

Die drei Einstiege in index.html reichen dafuer nicht. `js/app.js` ist ein
ES-Modul und importiert `./daten.js`, `./routing.js` und die Views mit ihren
blanken Pfaden — die haben keinen Query-String, also greift dort der Cache
weiter, auch wenn app.js neu geladen wurde. Genau das ist beim Deploy am
08.09.2026 aufgefallen: gestempelt war der Einstieg, veraendert waren die
Views. Deshalb schreibt das Skript zusaetzlich eine Import Map, die jeden
Modulpfad auf seine gestempelte Fassung umbiegt.

Vor jedem Commit laufen lassen, der CSS oder JS anfasst.
"""
import hashlib, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINK = re.compile(r'(href|src)="((?:css|js)/[\w./-]+?)(?:\?v=[0-9a-f]+)?"')
MAP = re.compile(r'<script type="importmap">.*?</script>\n', re.S)
MAP_ANCHOR = '<script src="js/core.js'

# js/core.js und js/parliament.js sind klassische Skripte und stehen mit
# Query-String direkt in index.html; sie brauchen keinen Map-Eintrag.
KLASSISCH = ('js/core.js', 'js/parliament.js')


def assets():
    """Jede CSS- und JS-Datei, die der Browser laedt — Reihenfolge stabil."""
    found = []
    for top in ('css', 'js'):
        for root, dirs, files in os.walk(os.path.join(BASE, top)):
            dirs.sort()
            for f in sorted(files):
                if f.endswith(('.css', '.js')):
                    rel = os.path.relpath(os.path.join(root, f), BASE)
                    found.append(rel.replace(os.sep, '/'))
    return sorted(found)


def main():
    files = assets()
    h = hashlib.sha1()
    for rel in files:
        with open(os.path.join(BASE, rel), 'rb') as f:
            h.update(f.read())
    tag = h.hexdigest()[:8]

    module_map = ',\n    '.join(
        '"./%s": "./%s?v=%s"' % (rel, rel, tag)
        for rel in files if rel.endswith('.js') and rel not in KLASSISCH)
    block = ('<script type="importmap">\n{\n  "imports": {\n    '
             + module_map + '\n  }\n}\n</script>\n')

    path = os.path.join(BASE, 'index.html')
    with open(path, encoding='utf-8') as f:
        src = f.read()

    out = LINK.sub(lambda m: m.group(1) + '="' + m.group(2) + '?v=' + tag + '"', src)
    out = MAP.sub('', out).replace(MAP_ANCHOR, block + MAP_ANCHOR, 1)

    if out == src:
        print('unveraendert (' + tag + ')')
        return
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(out)
    print('%d Verweise und %d Modulpfade auf %s gesetzt'
          % (len(LINK.findall(out)), module_map.count('": "') , tag))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
