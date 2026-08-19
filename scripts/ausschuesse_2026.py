"""Ergaenzt die Ausschussbesetzung der Wahlperiode 2026-2032.

Die Sitze standen schon, die Vertretungen fehlten. Nachgetragen aus der
Bestellungsliste der Stadt; der Aufsichtsrat Klaeranlage bekommt zusaetzlich
erstmals Perioden, weil er bisher nur eine einzige Besetzung kannte — die
von 2020-2026, die damit faelschlich auch fuer 2026 gegolten haette.

Aufruf ohne Argument = Probelauf, --apply schreibt.
"""
import json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(BASE, 'data', 'members.json')

# Ordentliches Mitglied -> Vertretung, je Gremium
SUBS = {
    'bpu': {'stanglmaier': 'linz_kilian', 'beibl': 'roeck',
            'hadersdorfer': 'kehlringer', 'linz_karin': 'reither',
            'marschoun': 'marcus', 'meier': 'lauterbach',
            'sabanovic': 'dick', 'schweiger': 'heinz',
            'sixt': 'grundner', 'tristl': 'haberl', 'welter': 'ghadieh'},
    'hvfa': {'lauterbach': 'meier', 'ghadieh': 'welter', 'dick': 'sabanovic',
             'grundner': 'sixt', 'heinz': 'schweiger', 'kehlringer': 'hadersdorfer',
             'linz_kilian': 'beibl', 'marcus': 'marschoun', 'reither': 'linz_karin',
             'ruemelin': 'roeck', 'tristl': 'haberl'},
    'pa': {'dick': 'strobl', 'meier': 'sixt', 'reither': 'kehlringer',
           'roeck': 'ruemelin', 'schweiger': 'linz_karin'},
    'rpa': {'beibl': 'linz_kilian', 'linz_karin': 'heinz', 'meier': 'sixt',
            'sabanovic': 'dick', 'tristl': 'haberl'},
}

AR_2026 = [('stanglmaier', 'roeck'), ('dick', 'sabanovic'), ('haberl', 'tristl'),
           ('hadersdorfer', 'heinz'), ('marcus', 'marschoun'), ('sixt', 'meier'),
           ('welter', 'ghadieh')]


def fill(cfg, table, label):
    """Vertretungen in einen Sitzblock schreiben, ohne die Reihenfolge zu ruehren."""
    for group in ('vicechairs', 'seats'):
        for s in cfg.get(group) or []:
            want = table.get(s['member'])
            if not want:
                print('  ? ' + label + ': keine Vertretung fuer ' + s['member'])
                continue
            if s.get('sub') and s['sub'] != want:
                print('  ! ' + label + ': ' + s['member'] + ' hatte '
                      + s['sub'] + ', jetzt ' + want)
            s['sub'] = want


def main():
    do_apply = '--apply' in sys.argv
    data = json.load(open(PATH, encoding='utf-8'))
    bodies = {b['id']: b for b in data['bodies']}

    for bid, table in SUBS.items():
        b = bodies[bid]
        cfg = next(c for c in b['seatConfigs'] if c['from'] == '2026-05-01')
        fill(cfg, table, bid)
        # Die oberste Ebene fuehrt die laufende Besetzung — die Gremienkarte
        # liest sie direkt, ohne Datum.
        fill(b, table, bid + ' (aktuell)')
        seen = {s['member'] for s in cfg['seats']} \
             | {v['member'] for v in cfg.get('vicechairs') or []}
        extra = set(table) - seen
        if extra:
            print('  ! ' + bid + ': nicht zugeordnet ' + str(sorted(extra)))
        print('  ' + bid + ': ' + str(len(seen)) + ' ordentliche Sitze')

    ar = bodies['ar_klaeranlage']
    if 'seatConfigs' not in ar:
        ar['seatConfigs'] = [
            {'from': '2020-05-01', 'to': '2026-04-30',
             'chair': ar['chair'], 'seats': ar['seats']},
            {'from': '2026-05-01', 'chair': 'mader',
             'seats': [{'member': m, 'sub': s} for m, s in AR_2026]},
        ]
        ar['chair'] = 'mader'
        ar['seats'] = [{'member': m, 'sub': s} for m, s in AR_2026]
        print('  ar_klaeranlage: zwei Perioden angelegt, 7 Sitze ab 2026')
    else:
        print('  ar_klaeranlage: hat schon Perioden, unveraendert')

    if do_apply:
        with open(PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print('\ngeschrieben')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
