"""Markiert anonyme Abstimmungen, bei denen die Einstimmigkeit NICHT auf alle
Anwesenden verallgemeinert werden darf.

Beispiel: sr_20260518_01 steht mit 14:0 in der Niederschrift, anwesend waren
aber 23 — neun neu gewählte Mitglieder haben sich enthalten. Ohne Markierung
würde die App allen 23 ein „Ja" zuschreiben.
"""
import json, os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def load(n):
    return json.load(open(os.path.join(DATA, n), encoding='utf-8'))


def active(members, d):
    out = set()
    for m in members:
        spans = m.get('periods') or [{'from': m.get('from'), 'to': m.get('to')}]
        if any((s.get('from') or '0') <= d and (not s.get('to') or s['to'] >= d)
               for s in spans):
            out.add(m['id'])
    return out


def body_size(sid, members, date):
    if sid.startswith('sr_'):
        return len(active(members['members'], date))
    body = next((b for b in members['bodies']
                 if b.get('id') == sid.split('_')[0]), None)
    if not body:
        return None
    cfg = next((c for c in body.get('seatConfigs', [])
                if (c.get('from') or '0') <= date and (not c.get('to') or c['to'] >= date)),
               None) or body
    return 1 + len(cfg.get('vicechairs', [])) + len(cfg.get('seats', []))


def main():
    members = load('members.json')
    sessions = {s['id']: s for s in load('sessions.json')}
    path = os.path.join(DATA, 'votes.json')
    votes = json.load(open(path, encoding='utf-8'))

    n = 0
    for v in votes:
        if v['type'] != 'anonymous':
            continue
        r = v['results']
        if r['yes'] and r['no']:
            continue                                  # geteilt, wird ohnehin '?'
        sess = sessions.get(v['sessionId'])
        size = body_size(v['sessionId'], members, v['date'])
        if not sess or not size:
            continue
        entitled = size - len(sess.get('absent', []))
        if r['yes'] + r['no'] < entitled:
            v['inferable'] = False
            n += 1

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(votes, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'{n} einstimmige anonyme Votes als nicht-ableitbar markiert')


if __name__ == '__main__':
    main()
