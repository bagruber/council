"""Entscheidet je Abstimmung, ob sich das Verhalten der Anwesenden ableiten lässt.

Bei einem einstimmigen Ergebnis liegt der Schluss nahe: wer da war, hat so
gestimmt. Das gilt aber nur, wenn auch alle mitgestimmt haben. Weist die
Niederschrift weniger Stimmen aus als Stimmberechtigte anwesend waren, fehlt
jemand — und man weiss nicht, wer.

Die Abwägung: bei einer Lücke von einer Stimme unter zweiundzwanzig wären 21
richtige Ableitungen verloren, um eine falsche zu vermeiden. Deshalb wird
abgeleitet, solange mindestens 90 % der Stimmberechtigten mitgestimmt haben —
und die Ableitung ist in der Oberfläche als solche markiert. Darunter bleibt
es beim Fragezeichen.

Zwei Ursachen für Lücken sind bekannt und werden vorher herausgerechnet:
  * Wechselsitzungen — wer an diesem Tag ausscheidet, teilt sich den Sitz mit
    der Person, die nachrückt. Das ist ein Sitz, nicht zwei.
  * Entlastung des Aufsichtsrats der Kläranlage — dessen Mitglieder stimmen
    über die eigene Entlastung nicht mit. Wer dem Aufsichtsrat wann angehörte,
    geben die Daten nicht her; die Lücke ist damit erklärt, aber nicht
    auflösbar. Solche Voten bleiben bewusst ohne Ableitung.

Die 90 %-Schwelle setzt eine Anwesenheitsliste voraus. Sitzungen, die nur als
Beschlussauszug der Stadt vorliegen (`session.source.kind == 'webauszug'`),
haben keine — dort wird nur abgeleitet, wenn alle Sitze mitgestimmt haben.
"""
import json, os, re

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
THRESHOLD = 0.9

ENTLASTUNG = re.compile(r'entlastung.*aufsichtsrat|aufsichtsrat.*entlastung', re.I)
ENTLASTUNG_NOTE = ('Die Mitglieder des Aufsichtsrats stimmen über ihre eigene '
                   'Entlastung nicht mit. Deshalb liegt die Zahl der Stimmen '
                   'unter der Zahl der Anwesenden.')
WEBAUSZUG_NOTE = ('Für diese Sitzung ist keine Anwesenheitsliste veröffentlicht. '
                  'Da nicht alle Sitze mitgestimmt haben, lässt sich das '
                  'Stimmverhalten niemandem zuordnen.')

TEIL_NOTE = ('Es haben weniger mitgestimmt als anwesend waren. Die Niederschrift '
             'vermerkt {n} Person{s}, die später kam{s} oder früher ging{s} — deren '
             'Stimme bleibt offen, für die übrigen Anwesenden gilt das einstimmige '
             'Ergebnis.')


def load(n):
    return json.load(open(os.path.join(DATA, n), encoding='utf-8'))


def active(m, d):
    spans = m.get('periods') or [{'from': m.get('from'), 'to': m.get('to')}]
    return any((s.get('from') or '0') <= d and (not s.get('to') or s['to'] >= d)
               for s in spans)


def seats_on(members, date):
    """Aktive Mandate, Wechseltage als ein Sitz gezählt."""
    live = [m for m in members if active(m, date)]
    incoming = {m['id'] for m in live if m.get('from') == date}
    if not incoming:
        return live
    return [m for m in live if not (m.get('to') == date and incoming)]


def body_size(sid, members, date):
    if sid.startswith('sr_'):
        return len(seats_on(members, date))
    body = next((b for b in members_data['bodies']
                 if b.get('id') == sid.split('_')[0]), None)
    if not body:
        return None
    configs = body.get('seatConfigs') or []
    cfg = next((c for c in configs
                if (c.get('from') or '0') <= date and (not c.get('to') or c['to'] >= date)),
               None) or (None if configs else body)
    if cfg is None:
        return None      # Gremium hat Perioden, aber keine fuer dieses Datum
    return 1 + len(cfg.get('vicechairs', [])) + len(cfg.get('seats', []))


def main():
    global members_data
    members_data = load('members.json')
    members = members_data['members']
    sessions = {s['id']: s for s in load('sessions.json')}
    path = os.path.join(DATA, 'votes.json')
    votes = json.load(open(path, encoding='utf-8'))

    stats = {'ableitbar': 0, 'teilweise': 0, 'entlastung': 0,
             'ohne anwesenheit': 0, 'zu grosse lücke': 0}
    for v in votes:
        v.pop('inferable', None)
        if v.get('note', '').startswith('Es haben weniger mitgestimmt'):
            v.pop('note')
        if v['type'] != 'anonymous':
            continue
        r = v['results']
        if r['yes'] and r['no']:
            continue                                   # geteilt → ohnehin '?'

        sess = sessions.get(v['sessionId'])
        size = body_size(v['sessionId'], members, v['date'])
        if not sess or not size:
            continue

        # `kein_mandat` heisst: an diesem Votum hielt die andere Person des
        # Wechsels den Sitz. Der Sitz stimmt mit, nur eben durch sie.
        excl = len([e for e in v.get('excluded', [])
                    if e.get('reason') != 'kein_mandat'])
        entitled = size - len(sess.get('absent', [])) - excl
        voted = r['yes'] + r['no']

        if ENTLASTUNG.search(v['title']):
            v['inferable'] = False
            v.setdefault('note', ENTLASTUNG_NOTE)
            stats['entlastung'] += 1
        elif (sess.get('source') or {}).get('kind') == 'webauszug' and voted < size:
            # Ohne Anwesenheitsliste gibt es keine Toleranz: fehlt auch nur eine
            # Stimme, ist unbekannt, wer gefehlt hat.
            v['inferable'] = False
            v.setdefault('note', WEBAUSZUG_NOTE)
            stats['ohne anwesenheit'] += 1
        elif entitled > 0 and voted / entitled < THRESHOLD:
            # Nennt die Niederschrift, wer später kam oder früher ging, und
            # reicht diese Gruppe aus, um die Lücke zu erklären, dann ist nur
            # deren Stimme offen — der Rest des Saals hat einstimmig so
            # gestimmt, wie das Ergebnis sagt.
            teil = [e['member'] for e in sess.get('partial') or []]
            if teil and entitled - voted <= len(teil):
                v['inferable'] = 'teilweise'
                v.setdefault('note', TEIL_NOTE.format(
                    n=len(teil), s='' if len(teil) == 1 else 'n'))
                stats['teilweise'] += 1
            else:
                v['inferable'] = False
                stats['zu grosse lücke'] += 1
        else:
            stats['ableitbar'] += 1

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(votes, f, ensure_ascii=False, indent=2)
        f.write('\n')
    for k, n in stats.items():
        print(f'  {k:18} {n:4}')


if __name__ == '__main__':
    main()
