"""Traegt die Sitzverteilung des Stadtrats 2014-2020 nach.

Das Plenum hatte bisher nur seatConfigs ab 2020-05-01. Fuer aeltere Sitzungen
fiel `Council.bodyConfigAt` auf die oberste `seats`-Ebene zurueck — und die
traegt den 2026er Rat mit `from: 2026-05-01` an jedem Sitz. Ergebnis: bei jeder
Sitzung vor Mai 2020 war das gesamte Halbrund leer.

24 Sitze plus Erste Buergermeisterin Meinelt. Vier Sitze wechseln waehrend der
Periode die Person. Die Reihenfolge ist nach Fraktionen gruppiert — die
tatsaechliche Sitzordnung dieser Periode ist nicht ueberliefert.
"""
import json, os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

SEATS = [
    # LINKE
    [('zitzlsberger', None, '2017-12-11'), ('john', '2017-12-11', None)],
    # Grüne
    ['stanglmaier'], ['altenbeck'], ['bauer'], ['becher_j'], ['wagner'],
    # ÖDP
    ['kaestl'],
    # SPD
    ['beubl'], ['marschoun'], ['pschorr'],
    # UMB — der Sitz Hilbergs ging nach dessen Ausscheiden an Haberl (CSU)
    [('hilberg', None, '2018-11-05'), ('haberl', '2018-11-23', None)],
    ['koehler'],
    # FW
    ['dollinger'],
    [('groeneveld', None, '2015-12-21'), ('grundner', '2016-01-11', None)],
    ['kieninger'], ['reif'],
    # CSU
    ['hadersdorfer'], ['heinz'], ['kerscher'], ['linz_karin'], ['mueller_a'],
    ['tristl'], ['weber'],
    [('schaffer', None, '2018-05-14'), ('banner', '2018-05-14', None)],
]

# Referate und Funktionen dieser Periode, soweit die Bürgerinfo sie ausweist
TITLES = {
    'stanglmaier': 'Dritter Bürgermeister',
    'kaestl':      'Finanzreferent',
    'pschorr':     'Schulreferent',
    'reif':        'Migrations- und Integrationsreferent',
    'weber':       'Partnerschaftsreferent',
}


def seat(spec):
    occ = []
    for o in spec:
        if isinstance(o, str):
            occ.append({'member': o})
            continue
        mid, fr, to = o
        e = {'member': mid}
        if fr: e['from'] = fr
        if to: e['to'] = to
        occ.append(e)
    return {'occupants': occ}


def main():
    path = os.path.join(DATA, 'members.json')
    data = json.load(open(path, encoding='utf-8'))

    plenum = next(b for b in data['bodies'] if b.get('type') == 'plenum')
    plenum['seatConfigs'].insert(0, {
        'from': '2014-05-01',
        'to': '2020-04-30',
        'rows': 2,
        'chair': 'meinelt',
        'seats': [seat(s) for s in SEATS],
    })

    by = {m['id']: m for m in data['members']}
    for mid, title in TITLES.items():
        titles = by[mid].setdefault('profile', {}).setdefault('titles', [])
        if any(t['title'] == title and t['from'].startswith('2014') for t in titles):
            continue
        titles.insert(0, {'title': title, 'from': '2014-05-01', 'to': '2020-04-30'})

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

    members = {m['id'] for m in data['members']}
    used = [o['member'] for s in plenum['seatConfigs'][0]['seats'] for o in s['occupants']]
    print(f'  {len(SEATS)} Sitze, {len(used)} Besetzungen, Vorsitz meinelt')
    print(f'  unbekannte IDs: {sorted(set(used) - members) or "keine"}')


if __name__ == '__main__':
    main()
