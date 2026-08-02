"""Stuft die geteilten Abstimmungen mit bekannten Einzelstimmen als `tracked` ein.

Die Niederschriften nennen bei diesen Voten nur das Ergebnis. Die Einzelstimmen
stammen aus eigener Mitschrift — in `voters` tauchen fast ausschließlich die
fresh-Mandate auf (26× gruber, 12× hobmaier, 1× strobl).

Wo ein Presseartikel dasselbe Abstimmungsverhalten berichtet, wird das über
`pressVerified` und die Artikel-ID festgehalten.
"""
import json, os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
TRACKER = 'gruber'

# Voten, deren Abstimmungsverhalten zusätzlich in der Presse berichtet wurde
PRESS_VERIFIED = {
    'sr_20240506_02': 'sz_2024-05_windenergie',
    'sr_20260112_06': 'merkur_2026-01-12_parken-plan',
    'sr_20260112_07': 'br_2025-09_falschparken-plan',
    'sr_20260202_04': 'merkur_2026-02-02_studentenwohnheim',
}


def split(v):
    r = v['results']
    return (bool(r['yes'] and r['no']) if v['type'] == 'named'
            else bool(r['yes'] and r['no']))


def main():
    path = os.path.join(DATA, 'votes.json')
    votes = json.load(open(path, encoding='utf-8'))
    n = 0
    for v in votes:
        if v.get('source') or not split(v):
            continue
        if v['type'] != 'named' and not v.get('voters'):
            continue                       # nur Aggregat bekannt → bleibt offen
        src = {'tier': 'tracked', 'by': TRACKER,
               'pressVerified': v['id'] in PRESS_VERIFIED}
        if v['id'] in PRESS_VERIFIED:
            src['pressId'] = PRESS_VERIFIED[v['id']]
        v['source'] = src
        n += 1

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(votes, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'{n} Votes als tracked/{TRACKER} eingestuft, '
          f'{sum(1 for v in votes if v.get("source", {}).get("pressVerified"))} presseverifiziert')


if __name__ == '__main__':
    main()
