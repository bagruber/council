"""Übersicht der Sitzungen, in denen weniger gestimmt haben als anwesend waren.

Zeigt je gesperrtem Beschluss, wie groß die Lücke ist und wer sie tragen kann —
also wer laut Niederschrift später kam oder früher ging. Ist die Lücke größer
als die Zahl dieser Personen, fehlt eine Erklärung; ist sie kleiner, ist nicht
entscheidbar, wer von ihnen gefehlt hat.

Aufruf:  python scripts/anwesenheitsluecken.py --out docs/anwesenheit-luecken.txt
"""
import json, os, sys, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')


def load(n):
    return json.load(open(os.path.join(DATA, n), encoding='utf-8'))


def within(span, d):
    von, bis = span.get('from'), span.get('to')
    if bis and len(bis) == 7:
        bis += '-99'
    return not (von and d < von) and not (bis and d > bis)


def aktiv_am(m, d):
    return any(within(p, d) for p in
               (m.get('periods') or [{'from': m.get('from'), 'to': m.get('to')}]))


def sitze_am(members, d):
    """Aktive Mandate, Wechseltag als ein Sitz."""
    live = [m for m in members if aktiv_am(m, d)]
    rein = {m['id'] for m in live if m.get('from') == d}
    return [m for m in live if not (m.get('to') == d and rein)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out')
    args = ap.parse_args()

    md = load('members.json')
    members, bodies = md['members'], {b['id']: b for b in md['bodies']}
    namen = {m['id']: f"{m['firstName']} {m['lastName']}" for m in members}
    S = {s['id']: s for s in load('sessions.json')}
    votes = load('votes.json')

    proSitzung = {}
    for v in votes:
        if v.get('inferable') not in (False, 'teilweise'):
            continue
        if (v.get('note') or '').startswith(('Für diese Sitzung', 'Die Mitglieder')):
            continue                      # Webauszug und Kläranlage-Entlastung: andere Ursache
        proSitzung.setdefault(v['sessionId'], []).append(v)

    z = []
    z.append('Anwesenheitslücken — wo weniger gestimmt haben als anwesend waren')
    z.append('=' * 74)
    z.append('')
    z.append('Bei diesen einstimmigen Beschlüssen weist die Niederschrift weniger')
    z.append('Stimmen aus, als laut Anwesenheitsliste im Raum waren. Wer nicht')
    z.append('mitgestimmt hat, steht dort nicht.')
    z.append('')
    z.append('"Zeitvermerk" = laut Niederschrift später gekommen oder früher gegangen.')
    z.append('')
    z.append('Reichen die Zeitvermerke aus, um die Lücke zu erklären, wird für alle')
    z.append('übrigen Anwesenden das einstimmige Ergebnis abgeleitet; offen bleibt nur')
    z.append('die Stimme der vermerkten Personen. Reichen sie nicht, bleibt der ganze')
    z.append('Beschluss gesperrt (GESPERRT) — genau die sind zum Nachprüfen interessant.')
    z.append('')

    for sid in sorted(proSitzung, key=lambda s: S[s]['date']):
        s, d = S[sid], S[sid]['date']
        sitze = sitze_am(members, d)
        anwesend = len(sitze) - len(s.get('absent') or [])
        teil = s.get('partial') or []
        z.append('')
        z.append('-' * 74)
        z.append(f"{d}  {s['title']}")
        z.append(f"  {len(sitze)} Sitze · {len(s.get('absent') or [])} abwesend · {anwesend} anwesend")
        if teil:
            z.append(f'  Zeitvermerke ({len(teil)}):')
            for e in teil:
                spanne = []
                if e.get('from'): spanne.append('ab ' + e['from'])
                if e.get('to'):   spanne.append('bis ' + e['to'])
                z.append(f"      {namen[e['member']]:26s} {' '.join(spanne)}")
        else:
            z.append('  Zeitvermerke: keine — die Liste nennt nur ganz Abwesende')
        z.append('')
        for v in sorted(proSitzung[sid], key=lambda v: v['id']):
            r = v['results']
            gestimmt = r['yes'] + r['no']
            luecke = anwesend - gestimmt
            if not teil:
                urteil = 'ohne Träger — Grund unbekannt, GESPERRT'
            elif luecke > len(teil):
                urteil = f'{luecke - len(teil)} über die Zeitvermerke hinaus, GESPERRT'
            else:
                ab = sum(1 for e in teil if e.get('from'))
                bis = sum(1 for e in teil if e.get('to'))
                urteil = (f'getragen von {len(teil)} Zeitvermerken '
                          f'({ab}× später, {bis}× früher weg) — abgeleitet')
            z.append(f"    {r['yes']:>2}:{r['no']:<2}  {gestimmt:2d} von {anwesend:2d} gestimmt"
                     f"  → Lücke {luecke}, {urteil}")
            z.append(f"          {v['id']}  {v['title'][:60]}")

    text = '\n'.join(z) + '\n'
    if args.out:
        ziel = os.path.join(ROOT, args.out)
        os.makedirs(os.path.dirname(ziel), exist_ok=True)
        open(ziel, 'w', encoding='utf-8').write(text)
        print('geschrieben:', args.out, f'({len(proSitzung)} Sitzungen,',
              f'{sum(len(x) for x in proSitzung.values())} Beschlüsse)')
    else:
        print(text)


if __name__ == '__main__':
    main()
