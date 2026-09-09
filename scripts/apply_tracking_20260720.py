"""Loest TOP 9 der Sitzung vom 20.07.2026 aus der Mitschrift auf.

Die Niederschrift fuehrt zu diesem Punkt einen Beschluss: Zulage ab 01.09.2026
auf 125 EUR, 13:10. Die Mitschrift in `data/vote_tracking/` zeigt, dass es drei
Abstimmungen waren:

    20:19  130 EUR   10:13  abgelehnt
    20:20  125 EUR   13:10  angenommen
    20:24  Gesamtbeschluss  23:0  angenommen

Damit steht nicht nur da, was beschlossen wurde, sondern auch, worueber vorher
gestritten wurde -- und dass am Ende alle mitgingen. Die 13:10 der Mitschrift
deckt sich mit der Niederschrift; die Namen dazu gibt nur die Mitschrift her,
deshalb Stufe `tracked`.

Die uebrigen sechs Beschluesse des Abends bestaetigt die Mitschrift Person fuer
Person. Sie bleiben auf `protocol-implicit`: aus Anwesenheitsliste und
Einstimmigkeit folgen dieselben Namen, und die Niederschrift ist die staerkere
Quelle. Angefasst werden sie nicht.

Nur `oeffentlich.json` wird gelesen. Was im nichtoeffentlichen Teil passiert
ist, gehoert nicht in diese App.
"""
import json, os, zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')
ZIP = os.path.join(DATA, 'vote_tracking', 'protokoll-2026-07-20_plenum.zip')

SID = 'sr_20260720'
DATE = '2026-07-20'

# Mitschrift-Titel -> (Vote-ID, Titel, Text, abgelehnt?)
BESCHLUESSE = [
    ('130€ Zulage', SID + '_07',
     'Arbeitsmarktzulage – Änderungsantrag auf 130 € abgelehnt',
     'Der Antrag, die Arbeitsmarktzulage auf 130,00 € zu erhöhen, findet mit 10:13 '
     'keine Mehrheit.', True),
    ('125€ Zulage', SID + '_08',
     'Arbeitsmarktzulage Erzieher/Kinderpfleger – Erhöhung auf 125 €',
     'Der Stadtrat beschließt, die Arbeitsmarktzulage ab 01.09.2026 auf 125,00 € zu '
     'erhöhen. Der Beschluss, den die Niederschrift ausweist.', False),
    ('Gesamtbeschluss', SID + '_09',
     'Arbeitsmarktzulage – Gesamtbeschluss',
     'Der Gesamtbeschluss über die Weitergewährung der Arbeitsmarktzulage geht '
     'einstimmig durch – nach zwei Abstimmungen über die Höhe, in denen sich der Rat '
     'in zwei fast gleich große Lager teilte.', False),
]


def load(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f:
        return json.load(f)


def save(name, obj):
    with open(os.path.join(DATA, name), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    with zipfile.ZipFile(ZIP) as z:
        mit = json.loads(z.read('oeffentlich.json').decode('utf-8'))
    name2id = {m['name']: m['id'] for m in mit['anwesenheit']}
    nach_titel = {a['titel']: a for a in mit['abstimmungen']}

    sessions, votes = load('sessions.json'), load('votes.json')
    session = next(s for s in sessions if s['id'] == SID)
    abwesend = session['absent']

    neu = []
    for titel, vid, kurz, text, abgelehnt in BESCHLUESSE:
        a = nach_titel[titel]
        ja = [name2id[n] for n in a['ja']]
        nein = [name2id[n] for n in a['nein']]
        assert len(ja) + len(nein) + len(abwesend) == 25, vid
        v = {'id': vid, 'sessionId': SID, 'topicId': None, 'date': DATE,
             'title': kurz, 'text': text, 'type': 'named',
             'results': {'yes': ja, 'no': nein, 'absent': list(abwesend)},
             'source': {'tier': 'tracked', 'by': 'gruber', 'pressVerified': False}}
        if abgelehnt:
            v['result'] = 'rejected'
        neu.append(v)

    votes = [v for v in votes if v['id'] != SID + '_07'] + neu
    votes.sort(key=lambda v: (v['date'], v['id']))

    top9 = next(i for i in session['agenda'] if i['number'] == '9')
    top9['voteId'] = neu[0]['id']
    top9['voteIds'] = [v['id'] for v in neu]

    save('votes.json', votes)
    save('sessions.json', sessions)
    print('TOP 9 aufgelöst: %s' % ', '.join('%s (%d:%d)' % (
        v['id'], len(v['results']['yes']), len(v['results']['no'])) for v in neu))


if __name__ == '__main__':
    main()
