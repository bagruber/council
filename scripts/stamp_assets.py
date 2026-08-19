"""Haengt eine Inhaltskennung an die Asset-Verweise in index.html.

Ohne sie liefert der Browser nach einem Deploy weiter die alte Datei aus —
GitHub Pages setzt zwar max-age=600, aus dem Disk-Cache kommt eine offene
Registerkarte aber auch danach noch an den alten Stand. Ein veraenderter
Query-String macht daraus eine andere URL, und der Cache greift nicht mehr.

Ein gemeinsamer Hash ueber alle Assets: aendert sich eine Datei, laedt der
Browser alle neu. Das kostet ein paar Kilobyte und spart die Fehlersuche.

Vor jedem Commit laufen lassen, der CSS oder JS anfasst.
"""
import hashlib, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = ['css/fonts.css', 'css/style.css',
          'js/core.js', 'js/parliament.js', 'js/app.js']
LINK = re.compile(r'(href|src)="((?:css|js)/[\w.-]+)(?:\?v=[0-9a-f]+)?"')


def main():
    h = hashlib.sha1()
    for rel in ASSETS:
        h.update(open(os.path.join(BASE, rel), 'rb').read())
    tag = h.hexdigest()[:8]

    path = os.path.join(BASE, 'index.html')
    src = open(path, encoding='utf-8').read()
    out = LINK.sub(lambda m: m.group(1) + '="' + m.group(2) + '?v=' + tag + '"', src)
    if out == src:
        print('unveraendert (' + tag + ')')
        return
    open(path, 'w', encoding='utf-8', newline='').write(out)
    print(str(len(LINK.findall(out))) + ' Verweise auf ' + tag + ' gesetzt')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
