"""Sitzordnung 2014-2020 nach dem Muster von 2020 und drei Fraktionswechsel.

Das Halbrund fuellt sich von rechts nach links: Index 0 sitzt am rechten Rand,
der letzte Sitz einer Reihe am linken. Bei 24 Sitzen sind es 10 innen und 14
aussen. Fraktionsfolge von rechts nach links: CSU, FW, SPD, OeDP, Linke, UMB,
Gruene.

Die Sitze folgen der Wahl von 2014; wer die Fraktion wechselt, behaelt seinen
Platz. Damit das nicht als Fehler gelesen wird, sitzen die beiden Wechsler am
Rand ihres Blocks zur neuen Fraktion hin: Hadersdorfer am FW-Rand zur CSU,
Wagner am UMB-Rand zu den Gruenen. Ab dem Wechseldatum waechst der Nachbarblock
optisch um einen Sitz, statt dass ein fremder Punkt mitten im Block steht.
"""
import json, os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# rechts → links, innere Reihe (10) dann aeussere Reihe (14)
INNER = [
    'heinz', 'kerscher', 'tristl',                            # CSU
    'hadersdorfer', 'dollinger',                              # FW (Hadersdorfer ab Okt 2017 CSU)
    'beubl',                                                  # SPD
    [('zitzlsberger', None, '2017-12-11'), ('john', '2017-12-11', None)],   # Linke
    'wagner',                                                 # UMB (ab Feb 2017 Grüne)
    'bauer', 'stanglmaier',                                   # Grüne
]
OUTER = [
    'linz_karin', 'mueller_a', 'weber',                       # CSU
    [('schaffer', None, '2018-05-14'), ('banner', '2018-05-14', None)],     # CSU
    'kieninger', 'reif',                                      # FW
    [('groeneveld', None, '2015-12-21'), ('grundner', '2016-01-11', None)], # FW
    'marschoun', 'pschorr',                                   # SPD
    'kaestl',                                                 # ÖDP
    'koehler',                                                # UMB
    [('hilberg', None, '2018-11-05'), ('haberl', '2018-11-23', None)],      # UMB
    'altenbeck', 'becher_j',                                  # Grüne
]

# Die Bürgerinfo führt alle drei unter ihrer heutigen Fraktion. Hadersdorfer und
# Wagner wechselten mitten in der Periode, Haberl erst mit der Wahl 2020 — er
# rückte für Hilberg auf einen UMB-Sitz nach und blieb es bis zum Periodenende.
PARTY_SWITCH = {
    'hadersdorfer': ('fw',  'csu',    '2017-10-06'),
    'wagner':       ('umb', 'gruene', '2017-02-15'),
    'haberl':       ('umb', 'csu',    '2020-05-01'),
}


def seat(spec):
    if isinstance(spec, str):
        return {'occupants': [{'member': spec}]}
    occ = []
    for mid, fr, to in spec:
        e = {'member': mid}
        if fr: e['from'] = fr
        if to: e['to'] = to
        occ.append(e)
    return {'occupants': occ}


def main():
    path = os.path.join(DATA, 'members.json')
    data = json.load(open(path, encoding='utf-8'))

    plenum = next(b for b in data['bodies'] if b.get('type') == 'plenum')
    cfg = next(c for c in plenum['seatConfigs'] if c.get('from') == '2014-05-01')
    cfg['seats'] = [seat(s) for s in INNER + OUTER]

    by = {m['id']: m for m in data['members']}
    for mid, (old, new, when) in PARTY_SWITCH.items():
        by[mid]['partyHistory'] = [
            {'party': old, 'from': by[mid]['from'], 'to': when},
            {'party': new, 'from': when, 'to': None},
        ]

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

    print(f'  innen {len(INNER)}, aussen {len(OUTER)}, gesamt {len(cfg["seats"])}')
    for mid, (old, new, when) in PARTY_SWITCH.items():
        print(f'  {mid}: {old} → {new} am {when}')


if __name__ == '__main__':
    main()
