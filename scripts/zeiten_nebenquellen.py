"""Traegt die Sitzungszeiten aus Niederschrift und Mitschrift als Nebenquellen nach.

`start` und `end` in `sessionlengths.json` kommen vom Sitzungsregister der
Stadt und bleiben massgeblich -- die Dauerstatistik rechnet damit, und nur
diese Quelle deckt alle 173 Sitzungen ab.

Daneben gibt es zwei weitere Zeiten, und keine deckt sich mit dem Register:

    13.04.2026 BPU   Register 19:00-19:20                     Mitschrift 20:34-20:44
    18.05.2026       Register 19:00-20:55                     Mitschrift 19:03-19:42
    29.06.2026       Register 18:00-20:47                     Mitschrift 19:00-20:27
    20.07.2026       Register 18:30-21:00  Niederschrift ab 19:00  Mitschrift 19:15-20:35
    27.07.2026       Register 18:30-22:27                     Mitschrift 18:37-21:19

Eine einfache Regel gibt das nicht her. Die Mitschrift endet regelmaessig
frueher -- sie misst, wie lange mitgeschrieben wurde, nicht wie lange getagt
wurde -- und am 13.04. beginnt sie sogar nach dem Registerende. Nur die
Eroeffnungszeit der Niederschrift ist ueberhaupt eine Aussage ueber die
Sitzung selbst.

Deshalb stehen die Nebenwerte unter `quellen`: sie sind aufgehoben, falls
jemand einmal darauf zurueckgreifen muss, und niemand haelt sie fuer die
Hauptzeit.

Die Mitschrift-Zeiten liest das Skript aus den Archiven in
`data/vote_tracking/`; die Niederschrift-Zeiten stehen unten von Hand, weil sie
nur im PDF stehen.
"""
import json, os, re, zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')
TRACKING = os.path.join(DATA, 'vote_tracking')

# Was das PDF als Eroeffnung nennt. Leer, wo die Niederschrift die Zeile
# unausgefuellt laesst -- das kommt vor.
NIEDERSCHRIFT = {
    ('2026-07-20', 'stadtrat'): {'start': '19:00'},
}


def mitschrift_zeiten():
    """Beginn und Ende je Sitzung aus den Mitschrift-Archiven."""
    out = {}
    for name in sorted(os.listdir(TRACKING)):
        if not name.endswith('.zip'):
            continue
        with zipfile.ZipFile(os.path.join(TRACKING, name)) as z:
            txt = z.read('protokoll.txt').decode('utf-8')
            meta = json.loads(z.read('oeffentlich.json').decode('utf-8'))
        beginn = re.search(r'ANWESENHEIT ZU BEGINN \((\d\d:\d\d)\)', txt)
        ende = re.search(r'(\d\d:\d\d)\s+Sitzung beendet', txt)
        body = 'bpu' if name.endswith('_bpu.zip') else 'stadtrat'
        z = {}
        if beginn:
            z['start'] = beginn.group(1)
        if ende:
            z['end'] = ende.group(1)
        if z:
            out[(meta['sitzung']['datum'], body)] = z
    return out


def main():
    path = os.path.join(DATA, 'sessionlengths.json')
    with open(path, encoding='utf-8') as f:
        lengths = json.load(f)

    mit = mitschrift_zeiten()
    n = 0
    for l in lengths:
        key = (l['date'], l['body'])
        quellen = {}
        if key in NIEDERSCHRIFT:
            quellen['niederschrift'] = NIEDERSCHRIFT[key]
        if key in mit:
            quellen['mitschrift'] = mit[key]
        if quellen:
            l['quellen'] = quellen
            n += 1
            print('%s %-9s Register %s-%s | %s' % (
                l['date'], l['body'], l['start'], l['end'],
                ' | '.join('%s %s-%s' % (k, v.get('start', '?'), v.get('end', '?'))
                           for k, v in quellen.items())))

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(lengths, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('%d Sitzungen mit Nebenquellen' % n)


if __name__ == '__main__':
    main()
