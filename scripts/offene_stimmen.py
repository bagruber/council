"""Listet je Person die Abstimmungen, bei denen ihr Verhalten unklar bleibt.

Spiegelt die Statuslogik aus js/core.js (voteStatus, isRegularOf) — unklar
heisst hier genau das, was die App als "?" zeigt: ein geteiltes Ergebnis ohne
Einzelstimmen, oder eine einstimmige Abstimmung, bei der weniger Stimmen
abgegeben als Stimmberechtigte anwesend waren (`inferable: false`).

Sitzungen ohne veroeffentlichte Anwesenheitsliste (Beschlussauszuege der
Stadt, `source.kind == webauszug`) bleiben aussen vor: dort liegt die
Unklarheit an der fehlenden Liste, nicht am Abstimmungsergebnis.

Aufruf:
    python scripts/offene_stimmen.py hobmaier gruebl neumayr
    python scripts/offene_stimmen.py --out docs/offene-stimmen.txt <ids...>
"""
import json, os, sys, argparse
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')

BODY_OF_TYPE = {'stadtrat': 'plenum', 'bpu': 'bpu', 'hvfa': 'hvfa'}


def load(n):
    return json.load(open(os.path.join(DATA, n), encoding='utf-8'))


def within(span, date):
    von, bis = span.get('from'), span.get('to')
    if bis and len(bis) == 7:
        bis += '-99'
    return not (von and date < von) and not (bis and date > bis)


def aktiv_am(m, date):
    perioden = m.get('periods') or [{'from': m.get('from'), 'to': m.get('to')}]
    return any(within(p, date) for p in perioden)


def config_am(body, date):
    configs = body.get('seatConfigs')
    if not configs:
        return body
    for c in configs:
        if within(c, date):
            return c
    return {}


def regulaer(mid, body, date):
    cfg = config_am(body, date)
    if cfg.get('chair') == mid:
        return True
    if any(v['member'] == mid for v in cfg.get('vicechairs') or []):
        return True
    for s in cfg.get('seats') or []:
        if s.get('member') == mid:
            return True
        if any(o['member'] == mid and within(o, date) for o in s.get('occupants') or []):
            return True
    return False


def status(mid, vote, session, member):
    if member and not aktiv_am(member, vote['date']):
        return None
    ex = next((e for e in vote.get('excluded') or [] if e['member'] == mid), None)
    if ex:
        return {'beteiligung': 'excluded', 'enthaltung': 'abstained',
                'nicht_stimmberechtigt': 'restricted',
                'kein_mandat': 'restricted'}.get(ex['reason'], 'absent')
    if session and mid in (session.get('absent') or []):
        return 'absent'

    r = vote['results']
    if vote['type'] == 'named':
        for feld, wert in (('yes', 'yes'), ('no', 'no'), ('absent', 'absent')):
            if mid in r[feld]:
                return wert
        return None
    if (vote.get('voters') or {}).get(mid):
        return vote['voters'][mid]
    if mid in (r.get('absent_ids') or []):
        return 'absent'
    if vote.get('inferable') == 'teilweise' and any(
            e['member'] == mid for e in (session or {}).get('partial') or []):
        return 'unknown'
    if vote.get('inferable') is not False:
        if r['yes'] > 0 and r['no'] == 0:
            return 'yes-inferred'
        if r['no'] > 0 and r['yes'] == 0:
            return 'no-inferred'
    return 'unknown'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ids', nargs='+')
    ap.add_argument('--out')
    args = ap.parse_args()

    members = {m['id']: m for m in load('members.json')['members']}
    bodies = {b['id']: b for b in load('members.json')['bodies']}
    sessions = {s['id']: s for s in load('sessions.json')}
    votes = load('votes.json')

    fehlt = [i for i in args.ids if i not in members]
    if fehlt:
        sys.exit('Unbekannte ids: ' + ', '.join(fehlt))

    offen = defaultdict(list)
    for v in votes:
        session = sessions.get(v['sessionId'])
        bid = BODY_OF_TYPE.get((session or {}).get('type'))
        if not session or not bid:
            continue
        if (session.get('source') or {}).get('kind') == 'webauszug':
            continue
        body = bodies.get(bid)
        if not body:
            continue
        for mid in args.ids:
            m = members[mid]
            if bid == 'plenum':
                if not aktiv_am(m, v['date']):
                    continue
            elif not regulaer(mid, body, v['date']):
                continue
            if status(mid, v, session, m) == 'unknown':
                offen[mid].append((v, session, bid))

    zeilen = []
    zeilen.append('Offene Stimmen — Abstimmungen ohne überliefertes Verhalten')
    zeilen.append('=' * 72)
    zeilen.append('')
    zeilen.append('Nur Sitzungen mit veröffentlichter Anwesenheitsliste. Beschlussauszüge')
    zeilen.append('der Stadt (BPU ohne Anwesenheitsliste) sind bewusst nicht enthalten.')
    zeilen.append('')
    zeilen.append('Grund "geteilt"      — Ergebnis ging auseinander, Einzelstimmen nicht')
    zeilen.append('                        überliefert. Ja oder Nein, beides möglich.')
    zeilen.append('Grund "nicht ableitbar" — einstimmig, aber weniger Stimmen als Anwesende.')
    zeilen.append('                        Ein Nein ist ausgeschlossen: entweder Ja oder')
    zeilen.append('                        gar nicht mitgestimmt.')
    zeilen.append('')

    for mid in args.ids:
        m = members[mid]
        eintraege = offen[mid]
        nach_sitzung = defaultdict(list)
        for v, session, bid in eintraege:
            nach_sitzung[session['id']].append((v, session, bid))

        zeilen.append('')
        zeilen.append('=' * 72)
        zeilen.append(f"{m['firstName']} {m['lastName']} ({m['party']})")
        zeilen.append(f"{len(eintraege)} offene Abstimmungen in {len(nach_sitzung)} Sitzungen")
        zeilen.append('=' * 72)
        if not eintraege:
            zeilen.append('  (keine)')
            continue
        for sid in sorted(nach_sitzung, key=lambda s: nach_sitzung[s][0][1]['date']):
            gruppe = nach_sitzung[sid]
            session = gruppe[0][1]
            zeilen.append('')
            zeilen.append(f"  {session['date']}  {session['title']}  [{gruppe[0][2]}]")
            for v, _, _ in gruppe:
                r = v['results']
                grund = 'nicht ableitbar' if v.get('inferable') is False else 'geteilt'
                zeilen.append(f"      {r['yes']:>2}:{r['no']:<3} {grund:15s} "
                              f"{v['id']:18s} {v['title']}")

    text = '\n'.join(zeilen) + '\n'
    if args.out:
        ziel = os.path.join(ROOT, args.out)
        os.makedirs(os.path.dirname(ziel), exist_ok=True)
        open(ziel, 'w', encoding='utf-8').write(text)
        print('geschrieben:', args.out)
        for mid in args.ids:
            print(f'  {mid:12s} {len(offen[mid]):3d}')
    else:
        print(text)


if __name__ == '__main__':
    main()
