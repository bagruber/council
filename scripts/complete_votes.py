"""Vervollstaendigt Abstimmungen, bei denen eine Seite schon voll ist.

Wenn alle Ja-Stimmen benannt sind und feststeht, wer gefehlt hat, dann sind die
uebrigen Anwesenden zwangslaeufig die Nein-Stimmen. Das ist keine Vermutung,
sondern Subtraktion — und gilt symmetrisch fuer die Gegenrichtung.

Die Herkunftsstufe bleibt die der Ausgangsdaten; ein `provisional`-Flag
vererbt sich mit, weil die Ableitung nicht besser sein kann als das, woraus
sie folgt.

Aufruf ohne Argument = Probelauf, --apply schreibt.
"""
import json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')


def active(m, d):
    sp = m.get('periods') or [{'from': m.get('from'), 'to': m.get('to')}]
    return any((s.get('from') or '0') <= d and (not s.get('to') or s['to'] >= d)
               for s in sp)


def main():
    do_apply = '--apply' in sys.argv
    load = lambda n: json.load(open(os.path.join(DATA, n), encoding='utf-8'))
    votes, sessions = load('votes.json'), load('sessions.json')
    members = load('members.json')['members']
    smap = {s['id']: s for s in sessions}

    done = []
    for v in votes:
        if v['type'] != 'anonymous':
            continue
        s = smap.get(v['sessionId'])
        if not s or 'absent' not in s:
            continue
        r = v['results']
        ex = [e['member'] for e in v.get('excluded') or []]
        out = list(dict.fromkeys(list(s['absent']) + ex))
        if len(out) != r['absent']:
            continue                      # weitere Kurzabwesenheiten, nicht zuzuordnen

        live = [m['id'] for m in members if active(m, v['date'])]
        present = [i for i in live if i not in out]
        if len(present) != r['yes'] + r['no']:
            continue

        voters = v.get('voters') or {}
        yes = [i for i in present if voters.get(i) == 'yes']
        no = [i for i in present if voters.get(i) == 'no']
        if len(yes) == r['yes'] and len(no) < r['no']:
            no = [i for i in present if i not in yes]
        elif len(no) == r['no'] and len(yes) < r['yes']:
            yes = [i for i in present if i not in no]
        else:
            continue

        v['type'] = 'named'
        v['results'] = {'yes': yes, 'no': no, 'absent': out}
        v.pop('voters', None)
        done.append((v['id'], v['date'], len(yes), len(no), len(out),
                     (v.get('source') or {}).get('provisional')))

    for vid, d, y, n, a, prov in done:
        print('  = %-18s %s  %2d:%-2d + %d%s' % (vid, d, y, n, a,
              '   (vorlaeufig)' if prov else ''))
    print(str(len(done)) + ' Abstimmungen vervollstaendigt')

    if do_apply and done:
        with open(os.path.join(DATA, 'votes.json'), 'w', encoding='utf-8') as f:
            json.dump(votes, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print('\ngeschrieben')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
