"""Namentliche Abstimmungen aus den Niederschriften übernehmen.

Wo der Stadtrat namentliche Abstimmung beschlossen hat, führt die Niederschrift
jede Stimme einzeln auf. Das ist die belastbarste Quelle, die es gibt — sie
ersetzt jede Ableitung und jede Mitschrift.

Die Listen sind hier von Hand übertragen, weil die Protokolle vier verschiedene
Schreibweisen verwenden (zweispaltige Tabelle, Fließtext, „die übrigen …") und
ein Parser dafür mehr Risiko als Nutzen bringt. Jede Liste ist gegen das
Ergebnis der jeweiligen Abstimmung geprüft.

Nicht übernommen: die namentliche Abstimmung vom 22.02.2021 (TOP 3.70,
Billigungsbeschluss ELA). Sie liegt in einem Sammelvote aus sieben Beschlüssen
mit identischem Ergebnis — die Namen würden sechs Abstimmungen zugeschrieben,
die sie nicht belegen.
"""
import json, os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

ROLLCALL = [
    {
        # 25.05.2020, TOP 6.19 — B-Plan 65 „Aich Kirchfeldstraße", Stellungnahme
        # Naturschutzbehörde. Abgelehnt 11:12. Heinz persönlich beteiligt.
        'votes': ['sr_20200525_15'],
        'yes': ['dollinger', 'hadersdorfer', 'weber', 'linz_karin', 'haberl',
                'pschorr', 'welter', 'grundner', 'reif', 'lauterbach', 'kieninger'],
        'no': 'übrige',
        'excluded': [('heinz', 'beteiligung')],
    },
    {
        # 07.06.2021, kostenloser Freibad-Eintritt für Kinder unter 12. 11:7.
        'votes': ['sr_20210607_08'],
        'yes': ['stanglmaier', 'becher_j', 'beibl', 'wagner', 'wittmann', 'john',
                'beubl', 'haberl', 'linz_karin', 'weber', 'heinz'],
        'no': ['dollinger', 'kieninger', 'lauterbach', 'grundner', 'pschorr',
               'tristl', 'welter'],
    },
    {
        # 06.09.2021, Bürgerbegehren „ACKERLAND IN BAUERNHAND", Beschluss 2a:
        # den Zielen zustimmen. Abgelehnt 10:12.
        'votes': ['sr_20210906_03'],
        'yes': ['stanglmaier', 'becher_j', 'beibl', 'altenbeck', 'wagner',
                'von_pressentin', 'neumayr', 'wittmann', 'john', 'beubl'],
        'no': 'übrige',
    },
    {
        # 22.05.2023, TOP 4.2 — B-Plan 79 „GE Unterreit". Der Vermerk steht am
        # Ende des Tagesordnungspunkts und gilt für beide Beschlüsse, die beide
        # mit 12:7 ergingen. Heinz persönlich beteiligt.
        'votes': ['sr_20230522_02', 'sr_20230522_03'],
        'yes': ['dollinger', 'weber', 'linz_karin', 'haberl', 'tristl', 'beubl',
                'pschorr', 'fincke', 'grundner', 'reif', 'lauterbach', 'kieninger'],
        'no': ['stanglmaier', 'becher_a', 'becher_j', 'beibl', 'linz_kilian',
               'von_pressentin', 'gruebl'],
        'excluded': [('heinz', 'beteiligung')],
    },
]


def load(n):
    return json.load(open(os.path.join(DATA, n), encoding='utf-8'))


def active(members, date):
    out = []
    for m in members:
        spans = m.get('periods') or [{'from': m.get('from'), 'to': m.get('to')}]
        if any((s.get('from') or '0') <= date and (not s.get('to') or s['to'] >= date)
               for s in spans):
            out.append(m['id'])
    return out


def main():
    members = load('members.json')['members']
    sessions = {s['id']: s for s in load('sessions.json')}
    path = os.path.join(DATA, 'votes.json')
    votes = json.load(open(path, encoding='utf-8'))
    by_id = {v['id']: v for v in votes}

    ok = True
    for rc in ROLLCALL:
        for vid in rc['votes']:
            v = by_id[vid]
            sess = sessions[v['sessionId']]
            roster = active(members, v['date'])
            excl = [e[0] for e in rc.get('excluded', [])]

            yes = rc['yes']
            if rc['no'] == 'übrige':
                # „die übrigen anwesenden Stadtratsmitglieder mit Nein"
                no = [m for m in roster
                      if m not in yes and m not in excl
                      and m not in sess.get('absent', [])]
            else:
                no = rc['no']
            absent = [m for m in roster if m not in yes and m not in no]

            before = v['results']
            want = (before['yes'], before['no']) if v['type'] == 'anonymous' \
                else (len(before['yes']), len(before['no']))
            if (len(yes), len(no)) != want:
                print(f"  ✗ {vid}: Liste {len(yes)}:{len(no)} passt nicht zum "
                      f"Protokollergebnis {want[0]}:{want[1]}")
                ok = False
                continue

            v['type'] = 'named'
            v['results'] = {'yes': yes, 'no': no, 'absent': absent}
            v['source'] = {'tier': 'protocol-explicit'}
            v.pop('voters', None)
            v.pop('inferable', None)
            if rc.get('excluded'):
                v['excluded'] = [{'member': m, 'reason': r} for m, r in rc['excluded']]
            print(f"  ✓ {vid}  {len(yes)}:{len(no)} namentlich, "
                  f"{len(absent)} nicht abgestimmt")

    if ok:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(votes, f, ensure_ascii=False, indent=2)
            f.write('\n')
        n = sum(1 for v in votes
                if v.get('source', {}).get('tier') == 'protocol-explicit')
        print(f"\n{n} Abstimmungen mit namentlichem Protokolleintrag")
    else:
        print('\nAbbruch — nichts geschrieben.')


if __name__ == '__main__':
    main()
