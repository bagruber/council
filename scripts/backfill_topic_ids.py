"""Traegt `topicId` auf Voten nach, die in der Historie eines Dossiers stehen.

Die Verknuepfung Votum-Dossier steht an zwei Stellen: `votes[].topicId` und
`topics[].history[].voteId`. Die Historie ist die kuratierte Auswahl, das Feld
die vollstaendige Zuordnung -- der Zaehler "N Abstimmungen" liest das Feld,
die Feldseite listet unter "einzelne Beschluesse" alles ohne Feld. Zehn Voten
standen in einer Historie, ohne das Feld zu tragen: sie fehlten im Zaehler und
tauchten faelschlich als themenlos auf.

Ein Fall ist echt doppelt: `sr_20250120_05` (4. Aenderung B-Plan 50) steht in
der Historie von t10 und t18. `topicId` ist einwertig, also bekommt es t18 --
der Beschluss ist ein Bebauungsplan fuer dieses Gebiet, die
Wirtschaftsfoerderung ist die Lesart daneben. Damit t10 den Beschluss trotzdem
zaehlt, bildet der Zaehler in views/themen.js die Vereinigung aus Feld und
Historie.

Einmal gelaufen am 08.09.2026. `validate_data.py` warnt ab jetzt, wenn die
Luecke wieder aufgeht.
"""
import json, os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# Votum -> Dossier, wenn ein Votum in mehreren Historien steht
PRIMAER = {'sr_20250120_05': 't18'}


def main():
    with open(os.path.join(DATA, 'topics.json'), encoding='utf-8') as f:
        topics = json.load(f)
    with open(os.path.join(DATA, 'votes.json'), encoding='utf-8') as f:
        votes = json.load(f)
    by_id = {v['id']: v for v in votes}

    gesetzt = 0
    for t in topics:
        for h in t.get('history', []):
            vid = h.get('voteId')
            v = by_id.get(vid)
            if not v or v.get('topicId'):
                continue
            tid = PRIMAER.get(vid, t['id'])
            v['topicId'] = tid
            gesetzt += 1
            print('%s -> %s' % (vid, tid))

    if gesetzt:
        with open(os.path.join(DATA, 'votes.json'), 'w', encoding='utf-8') as f:
            json.dump(votes, f, ensure_ascii=False, indent=2)
            f.write('\n')
    print('%d Voten nachgetragen' % gesetzt)


if __name__ == '__main__':
    main()
