"""Traegt den Beschlussauszug der Stadtratssitzung vom 15.06.2026 ein.

Quelle ist der oeffentliche Beschlussauszug der Stadt, keine Niederschrift.
Damit gilt dasselbe wie bei den BPU-Auszuegen (`import_bpu_webauszug.py`):
Tagesordnung, Beschlussart und Stimmenzahlen liegen vor, die Anwesenheitsliste
nicht -> `source.kind = webauszug`.

Die hoechste Stimmenzahl des Abends ist 24 von 25 Sitzen. Mindestens eine
Person hat also durchgehend gefehlt, wer, steht nirgends. Deshalb bekommt
weder die Sitzung ein `absent` noch ein Votum ein `results.absent` — eine
Null waere hier eine Behauptung, keine Angabe. Alle neun Voten bleiben
`anonymous` ohne `source.tier` und zaehlen in der Datenlage als
"nur Ergebnis".
"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')

SID = 'sr_20260615'
DATE = '2026-06-15'

# (TOP, Titel, Ja, Nein, Topic, Text)
BESCHLUESSE = [
    ('3', 'Genehmigung der öffentlichen Niederschriften (StR 11.05.2026; StR 18.05.2026)',
     23, 0, None, 'Beschlossen mit 23:0.'),
    ('4', '19. Änderung des Flächennutzungsplans Bereich "Degernpoint Nord" - Aufstellungsbeschluss',
     23, 0, 't18', 'Aufstellungsbeschluss für die 19. Änderung des Flächennutzungsplans '
                   'im Bereich Degernpoint Nord, beschlossen mit 23:0.'),
    ('5.1', 'Vorbescheid - Neubau eines Logistikgebäudes - Driescherstr. 3',
     24, 0, None, 'Beschlossen mit 24:0.'),
    ('5.2', 'Genehmigung Vorbescheid z. Neubau e. Mehrfamilienhauses mit 7 Wohneinheiten - '
            'Sternstr. 12 - Klageerhebung gegen die Genehmigung',
     23, 0, None, 'Klage gegen die Genehmigung des Vorbescheids, beschlossen mit 23:0. '
                  'Der Bauausschuss hatte die Klage am 13.04.2026 empfohlen.'),
    ('6.1', 'Bestellung des Vorsitzes und der Stellvertretung des Rechnungsprüfungsausschusses',
     24, 0, None, 'Beschlossen mit 24:0.'),
    ('6.2', 'Festsetzung der Dienstaufwandsentschädigung für den Ersten Bürgermeister',
     21, 2, None, 'Beschlossen mit 21:2.'),
    ('6.3', 'Beschluss über die Festsetzung der Aufwandsentschädigung für den Zweiten und '
            'Dritten Bürgermeister',
     21, 1, None, 'Beschlossen mit 21:1.'),
    ('6.4', 'Besetzung des Energiebeirates und der Fairtrade Lenkungsgruppe',
     24, 0, None, 'Mehrfachbeschluss über die Besetzung beider Gremien, beschlossen mit 24:0. '
                  'Der Auszug weist die Einzelbeschlüsse nicht getrennt aus.'),
    ('7.2', 'Sanierung des Rathauses Moosburg | Fassadensanierung und Sanierung der oberen '
            'Geschosse - 3.BA - Entscheidung über das Farbkonzept der Fassade',
     12, 11, 't17', 'Das Farbkonzept für die Fassade wird mit 12:11 beschlossen — die '
                    'knappste Entscheidung des Abends. Vorausgegangen war eine Ortseinsicht '
                    'vor dem Rathaus mit Begutachtung der Farbmuster.'),
]

# Tagesordnung: (Nummer, Titel, type) — type None heisst Sachpunkt bzw. Sammel-TOP
AGENDA = [
    ('1', 'Mitteilungen des Ersten Bürgermeisters', 'formal'),
    ('2', 'Bürgerfragen gem. § 27 Abs. 2 GeschO/StR', 'formal'),
    ('3', 'Genehmigung der öffentlichen Niederschriften (StR 11.05.2026; StR 18.05.2026)', None),
    ('4', '19. Änderung des Flächennutzungsplans Bereich "Degernpoint Nord" - Aufstellungsbeschluss', None),
    ('5', 'Baugesuche und Anträge', None),
    ('5.1', 'Vorbescheid - Neubau eines Logistikgebäudes - Driescherstr. 3', None),
    ('5.2', 'Genehmigung Vorbescheid z. Neubau e. Mehrfamilienhauses mit 7 Wohneinheiten - '
            'Sternstr. 12 - Klageerhebung gegen die Genehmigung', None),
    ('6', 'Stadtrats- und Bürgermeisterangelegenheiten', None),
    ('6.1', 'Bestellung des Vorsitzes und der Stellvertretung des Rechnungsprüfungsausschusses', None),
    ('6.2', 'Festsetzung der Dienstaufwandsentschädigung für den Ersten Bürgermeister', None),
    ('6.3', 'Beschluss über die Festsetzung der Aufwandsentschädigung für den Zweiten und '
            'Dritten Bürgermeister', None),
    ('6.4', 'Besetzung des Energiebeirates und der Fairtrade Lenkungsgruppe', None),
    ('7', 'Sanierung des Rathauses Moosburg - Fassadensanierung und Sanierung der oberen Geschosse', None),
    ('7.1', 'Kurze Ortseinsicht vor dem Rathaus mit Begutachtung der Farbmuster und '
            'Erläuterung durch Architekten Paringer', None),
    ('7.2', 'Sanierung des Rathauses Moosburg | Fassadensanierung und Sanierung der oberen '
            'Geschosse - 3.BA - Entscheidung über das Farbkonzept der Fassade', None),
    ('8', 'Anfragen', 'formal'),
]

HISTORY = {
    't18': {
        'date': DATE, 'type': 'vote',
        'title': '19. FNP-Änderung "Degernpoint Nord" – Aufstellungsbeschluss',
        'text': 'Der Stadtrat stellt den Flächennutzungsplan für den Bereich Degernpoint '
                'Nord zur Änderung auf, 23:0.',
        'sessionId': SID, 'voteId': None,
    },
    't17': {
        'date': DATE, 'type': 'vote',
        'title': 'Rathaus 3. BA – Farbkonzept der Fassade',
        'text': 'Nach einer Ortseinsicht mit Farbmustern entscheidet sich der Stadtrat mit '
                '12:11 für ein Farbkonzept. Die knappste Abstimmung des Abends.',
        'sessionId': SID, 'voteId': None,
    },
}


def load(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f:
        return json.load(f)


def save(name, obj):
    with open(os.path.join(DATA, name), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    sessions, votes, topics = load('sessions.json'), load('votes.json'), load('topics.json')
    if any(s['id'] == SID for s in sessions):
        raise SystemExit(SID + ' steht schon in sessions.json')

    vote_by_top, new_votes = {}, []
    for i, (top, title, yes, no, topic, text) in enumerate(BESCHLUESSE, start=1):
        vid = '%s_%02d' % (SID, i)
        vote_by_top[top] = vid
        new_votes.append({
            'id': vid, 'sessionId': SID, 'topicId': topic, 'date': DATE,
            'title': title, 'text': text,
            'type': 'anonymous', 'results': {'yes': yes, 'no': no},
        })

    agenda = []
    for number, title, kind in AGENDA:
        item = {'number': number, 'title': title}
        if kind:
            item['type'] = kind
        if number in vote_by_top:
            item['voteId'] = vote_by_top[number]
        for _, _, _, _, topic, _ in [b for b in BESCHLUESSE if b[0] == number]:
            if topic:
                item['topicId'] = topic
        agenda.append(item)

    session = {
        'id': SID, 'date': DATE, 'type': 'stadtrat',
        'title': '8. Stadtratssitzung – Juni 2026',
        'agenda': agenda,
        'source': {'kind': 'webauszug', 'url': None},
    }

    sessions.append(session)
    sessions.sort(key=lambda s: (s['date'], s['id']))
    votes.extend(new_votes)
    votes.sort(key=lambda v: (v['date'], v['id']))

    for tid, entry in HISTORY.items():
        topic = next(t for t in topics if t['id'] == tid)
        entry = dict(entry)
        entry['voteId'] = next(v['id'] for v in new_votes if v['topicId'] == tid)
        topic['history'].append(entry)
        topic['history'].sort(key=lambda h: h['date'])

    save('sessions.json', sessions)
    save('votes.json', votes)
    save('topics.json', topics)
    print('%s: %d Beschlüsse, %d TOPs' % (SID, len(new_votes), len(agenda)))


if __name__ == '__main__':
    main()
