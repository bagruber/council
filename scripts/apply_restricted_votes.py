"""Abstimmungen, bei denen ein Teil des Gremiums gar nicht mitstimmen durfte.

Der Fall tritt am Anfang jeder Wahlperiode auf: Wer neu gewählt ist, kann die
Niederschriften von Sitzungen, an denen er nicht teilgenommen hat, nicht
mitgenehmigen. Die Enthaltung ist dann keine Haltung, sondern eine Folge der
Geschäftsordnung — sie darf im Profil nicht wie eine Enthaltung aussehen und
erst recht nicht wie Abwesenheit.

Was sich sicher sagen lässt, wird als Stimme geführt; was offen bleibt, bleibt
offen und steht als Hinweis am Votum.
"""
import json, os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

CASES = [
    {
        'vote': 'sr_20260518_01',
        # Stichtag, ab dem jemand als „neu gewählt" gilt: der erste Tag der
        # neuen Wahlzeit. Wer davor schon Mandat hatte, war bei den zu
        # genehmigenden Sitzungen dabei.
        'since': '2026-05-01',
        'note': 'Neu gewählte Mitglieder konnten die Niederschriften der Sitzungen '
                'vom 25.03., 13.04. und 20.04.2026 nicht mitgenehmigen — sie waren '
                'nicht dabei. Neun der elf enthielten sich, zwei stimmten zu; '
                'welche zwei, hält die Niederschrift nicht fest.',
    },
]


def load(n):
    return json.load(open(os.path.join(DATA, n), encoding='utf-8'))


def active(m, d):
    spans = m.get('periods') or [{'from': m.get('from'), 'to': m.get('to')}]
    return any((s.get('from') or '0') <= d and (not s.get('to') or s['to'] >= d)
               for s in spans)


def main():
    members = load('members.json')['members']
    sessions = {s['id']: s for s in load('sessions.json')}
    path = os.path.join(DATA, 'votes.json')
    votes = json.load(open(path, encoding='utf-8'))
    by_id = {v['id']: v for v in votes}

    for case in CASES:
        v = by_id[case['vote']]
        sess = sessions[v['sessionId']]
        roster = [m for m in members if active(m, v['date'])]
        absent = [m['id'] for m in roster if m['id'] in sess.get('absent', [])]
        present = [m for m in roster if m['id'] not in absent]

        # Stichtag: wer schon am Tag vor Beginn der neuen Wahlzeit Mandat hatte
        day_before = case['since'][:8] + f"{int(case['since'][8:]) - 1:02d}"
        entitled = [m['id'] for m in present if active(m, day_before)]
        restricted = [m['id'] for m in present if m['id'] not in entitled]

        reported = v['results']['yes'] if v['type'] == 'anonymous' else len(v['results']['yes'])
        extra = reported - len(entitled)

        v['type'] = 'named'
        v['results'] = {'yes': entitled, 'no': [], 'absent': absent + restricted}
        v['excluded'] = [{'member': m, 'reason': 'nicht_stimmberechtigt'}
                         for m in restricted]
        v['note'] = case['note']
        v.pop('inferable', None)
        v['source'] = {'tier': 'protocol-implicit'}

        print(f"{v['id']}")
        print(f"  stimmberechtigt und anwesend : {len(entitled)}")
        print(f"  neu gewählt, nicht berechtigt: {len(restricted)}")
        print(f"  entschuldigt                 : {len(absent)}")
        print(f"  Protokoll nennt {reported} Ja — also {extra} Stimme(n) aus der "
              f"nicht berechtigten Gruppe, namentlich nicht überliefert")
        print(f"  Summe {len(entitled) + len(restricted) + len(absent)} von {len(roster)}")

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(votes, f, ensure_ascii=False, indent=2)
        f.write('\n')


if __name__ == '__main__':
    main()
