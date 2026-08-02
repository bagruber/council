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
"""
import json, os, re

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
THRESHOLD = 0.9

ENTLASTUNG = re.compile(r'entlastung.*aufsichtsrat|aufsichtsrat.*entlastung', re.I)
ENTLASTUNG_NOTE = ('Die Mitglieder des Aufsichtsrats stimmen über ihre eigene '
                   'Entlastung nicht mit. Deshalb liegt die Zahl der Stimmen '
                   'unter der Zahl der Anwesenden.')


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
    cfg = next((c for c in body.get('seatConfigs', [])
                if (c.get('from') or '0') <= date and (not c.get('to') or c['to'] >= date)),
               None) or body
    return 1 + len(cfg.get('vicechairs', [])) + len(cfg.get('seats', []))


def main():
    global members_data
    members_data = load('members.json')
    members = members_data['members']
    sessions = {s['id']: s for s in load('sessions.json')}
    path = os.path.join(DATA, 'votes.json')
    votes = json.load(open(path, encoding='utf-8'))

    stats = {'ableitbar': 0, 'entlastung': 0, 'zu grosse lücke': 0}
    for v in votes:
        v.pop('inferable', None)
        if v['type'] != 'anonymous':
            continue
        r = v['results']
        if r['yes'] and r['no']:
            continue                                   # geteilt → ohnehin '?'

        sess = sessions.get(v['sessionId'])
        size = body_size(v['sessionId'], members, v['date'])
        if not sess or not size:
            continue

        excl = len(v.get('excluded', []))
        entitled = size - len(sess.get('absent', [])) - excl
        voted = r['yes'] + r['no']

        if ENTLASTUNG.search(v['title']):
            v['inferable'] = False
            v.setdefault('note', ENTLASTUNG_NOTE)
            stats['entlastung'] += 1
        elif entitled > 0 and voted / entitled < THRESHOLD:
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
