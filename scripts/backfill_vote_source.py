"""Setzt das Herkunfts-Feld `source` auf allen Votes, bei denen es sich
mechanisch ableiten lässt.

  protocol-explicit  — die Niederschrift führt die Einzelstimmen auf
                       („Namentliche Abstimmung")
  protocol-implicit  — einstimmig, Einzelstimmen aus der Anwesenheit ableitbar

Alles Übrige (geteilte Abstimmungen) bleibt ohne `source` und muss einzeln
als `press` oder `tracked` eingestuft werden.
"""
import json, os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# Niederschriften mit ausgewiesener namentlicher Abstimmung
EXPLICIT = {'sr_20230904_05'}      # Regenbogenflagge am Rathaus, 9:11


def unanimous(v):
    r = v['results']
    if v['type'] == 'named':
        return not r['yes'] or not r['no']
    return r['yes'] == 0 or r['no'] == 0


def main():
    path = os.path.join(DATA, 'votes.json')
    votes = json.load(open(path, encoding='utf-8'))
    stats = {'explicit': 0, 'implicit': 0, 'offen': 0, 'schon gesetzt': 0}
    offen = []

    for v in votes:
        if v.get('source'):
            stats['schon gesetzt'] += 1
            continue
        if v['id'] in EXPLICIT:
            v['source'] = {'tier': 'protocol-explicit'}
            stats['explicit'] += 1
        elif unanimous(v):
            v['source'] = {'tier': 'protocol-implicit'}
            stats['implicit'] += 1
        else:
            stats['offen'] += 1
            if v['type'] == 'named' or v.get('voters'):
                offen.append(v)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(votes, f, ensure_ascii=False, indent=2)
        f.write('\n')

    for k, n in stats.items():
        print(f'  {k:14} {n:4}')
    print(f'\nGeteilte Abstimmungen mit Einzelstimmen, die eine Einstufung '
          f'brauchen: {len(offen)}')
    for v in sorted(offen, key=lambda x: x['date']):
        r = v['results']
        n = (f"{len(r['yes'])}:{len(r['no'])}" if v['type'] == 'named'
             else f"{r['yes']}:{r['no']} (+{len(v.get('voters', {}))} Einzelstimmen)")
        print(f"  {v['date']}  {v['id']:20} {n:28} {v['title'][:52]}")


if __name__ == '__main__':
    main()
