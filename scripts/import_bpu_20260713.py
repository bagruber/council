"""Traegt die Niederschrift der BPU-Sitzung vom 13.07.2026 ein.

Zwoelf Sitze, elf haben abgestimmt: zehn regulaere Mitglieder und Gunnar
Marcus als Vertreter fuer Christoph Marschoun. Christian Schweiger fehlte ohne
Vertretung -- auch sein Stellvertreter Rudolf Heinz war entschuldigt.

Wie bei den BPU-Sitzungen bisher fuehren die namentlichen Listen die zwoelf
Sitze unter ihren regulaeren Inhabern. Vertretene stehen in `absent`, wer sie
vertreten hat, in `session.substitutes`. Die Stimmprobe laeuft deshalb ueber
beides: elf Stimmen = zehn Regulaere plus eine Vertretung.

Nicht verwendet: das Mitschrift-Archiv zum selben Datum. Es ist ein Testlauf
("Demo" im Titel, 04:51 Uhr, eine Abstimmung namens "awawdawd") und widerspricht
der Niederschrift in der Anwesenheit.

Zwei Faelle, die nicht mechanisch sind:
  * TOP 6: "Herr Sabanovic war zum Zeitpunkt der Abstimmung nicht anwesend."
    10 statt 11 Stimmen -- Sabanovic in `absent` und in `excluded`.
  * TOP 5: Variante 1 scheitert 4:7 und bleibt anonym, Variante 2 geht
    einstimmig durch.
"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')

SID = 'bpu_20260713'
DATE = '2026-07-13'
ABWESEND = ['marschoun', 'schweiger']
VERTRETUNG = [{'member': 'marschoun', 'substitute': 'marcus'}]

PARAGRAF_36A = ('Der Bauausschuss stimmt dem beantragten Vorhaben nach § 36 a Abs. 1 BauGB '
                'nicht zu. Das Vorhaben ist mit den Vorstellungen der Stadt hinsichtlich der '
                'städtebaulichen Entwicklung und Ordnung in diesem Bereich nicht vereinbar.')

# (Titel, Text, Ja, Nein, Topic, kurzfristig abwesend, abgelehnt)
BESCHLUESSE = [
    ('Blütenstr. 5 – Einvernehmen verweigert',
     'Der Bauausschuss verweigert zum beantragten Vorhaben das gemeindliche Einvernehmen. '
     'Ein dreigeschossiger Baukörper mit einer Wandhöhe von ca. 8,9 m fügt sich nicht in die '
     'nähere Umgebung ein. Die Anforderungen an gesunde Wohnverhältnisse in der Nachbarschaft '
     'bleiben nicht gewahrt.', 11, 0, None, [], False),
    ('Blütenstr. 5 – Zustimmung nach § 36a BauGB verweigert',
     PARAGRAF_36A, 11, 0, None, [], False),
    ('Asternstr. 50 – Einvernehmen erteilt',
     'Der Bauausschuss erteilt zum beantragten Bauvorhaben das gemeindliche Einvernehmen und '
     'stimmt den erforderlichen Befreiungen von den Festsetzungen des Bebauungsplans zu.',
     11, 0, None, [], False),
    ('Landshuter Str. 34 – Einvernehmen zum Vorbescheid erteilt',
     'Der Bauausschuss erteilt zum beantragten Vorbescheid das gemeindliche Einvernehmen.',
     11, 0, None, [], False),
    ('Landshuter Str. 34 – Zustimmung nach § 36a BauGB verweigert',
     PARAGRAF_36A, 11, 0, None, [], False),
    ('Digitale Schulwegpläne – vertagt, Entscheidung im Stadtrat',
     'Der Bauausschuss beschließt, die Beschlussfassung über den Antrag von Bündnis 90/Die '
     'Grünen zu vertagen. Die Beschlussfassung über dieses Thema soll im Stadtrat erfolgen.',
     11, 0, 't8', [], False),
    ('Tempo 30 Münchener Straße – Variante 1 abgelehnt',
     'Der Vorschlag, Tempo 30 von Montag bis Freitag von 7.00 bis 16.30 Uhr im Bereich der '
     'Anton-Vitzthum-Grundschule in Variante 1 anzuordnen, findet mit 4:7 keine Mehrheit.',
     4, 7, 't8', [], True),
    ('Tempo 30 Münchener Straße – Variante 2 beschlossen',
     'Der Bau-, Planungs- und Umweltausschuss stimmt der Anordnung einer '
     'Geschwindigkeitsbegrenzung von 30 km/h von Montag bis Freitag von 7.00 Uhr bis '
     '16.30 Uhr im Bereich der Anton-Vitzthum-Grundschule mit der Variante 2 zu.',
     11, 0, 't8', [], False),
    ('Widmung Ortsstraße „Semptanger"',
     'Der Bau-, Planungs- und Umweltausschuss beschließt, die Straße „Semptanger" mit den '
     'Fl.Nrn. 608/14 und 608/38 der Gemarkung Pfrombach nach Art. 6 BayStrWG als Ortsstraße '
     'zu widmen.', 10, 0, None, ['sabanovic'], False),
    ('Widmung Fußgängerweg „Semptanger"',
     'Der Bau-, Planungs- und Umweltausschuss beschließt, den beschränkt-öffentlichen Weg '
     '„Semptanger" mit den Teilflächen der Flurnummern 608/13 und 667 der Gemarkung Pfrombach '
     'nach Art. 6 BayStrWG als öffentlichen Fußgängerweg zu widmen.', 11, 0, None, [], False),
]

# (Nummer, Titel, Typ, Beschluesse als 1-basierte Positionen, Topic, Notiz)
AGENDA = [
    ('1', 'Mitteilungen des Ersten Bürgermeisters', 'formal', [], None, None),
    ('2', 'Bürgerfragen gem. § 27 Abs. 2 und § 36 Abs. 1 GeschO/StR', 'formal', [], None, None),
    ('3', 'Baugesuche und Anträge', None, [], None, None),
    ('3.1', 'Neubau e. Wohnhauses mit drei Wohnungen u. Stellplätzen - Blütenstr. 5',
     None, [1, 2], None, None),
    ('3.2', 'Neubau eines Einfamilienhauses mit Doppelgarage - Asternstr. 50',
     None, [3], None, None),
    ('3.3', 'Neubau eines Wohnquartiers mit vier Mehrfamilienhäusern - Landshuter Str. 34',
     None, [4, 5], None, None),
    ('3.4', 'Abbruch d. besteh. Dachgeschosses u. Aufstockung e. Obergeschosses u. e. '
            'Dachgeschosses m. Erricht. zweier Dachgauben - Drosselweg 7',
     'discussion', [], None, 'Kein Beschluss erforderlich, es wurde nur ein Meinungsbild eingeholt.'),
    ('4', 'Antrag Bündnis 90/DIE GRÜNEN; Sichere Straßen für Alle - Schulwegsicherheit durch '
          'digitale Schulwegpläne', None, [6], 't8', None),
    ('5', 'Anordnung von Tempo 30 km/h in der Münchener Straße auf Höhe der '
          'Anton-Vitzthum-Grundschule', None, [7, 8], 't8', None),
    ('6', 'Widmung der Straße "Semptanger"', None, [9], None, None),
    ('7', 'Widmung öffentlicher Fußgängerweg "Semptanger"', None, [10], None, None),
    ('8', 'Anfragen und Sonstiges', 'formal', [], None, None),
]

HISTORY = [
    {'date': DATE, 'type': 'vote',
     'title': 'Digitale Schulwegpläne an den Stadtrat verwiesen',
     'text': 'Der Bauausschuss vertagt den Antrag von Bündnis 90/Die Grünen auf digitale '
             'Schulwegpläne einstimmig: entscheiden soll der Stadtrat.',
     'sessionId': SID, 'pos': 6},
    {'date': DATE, 'type': 'vote',
     'title': 'Tempo 30 vor der Anton-Vitzthum-Grundschule',
     'text': 'Variante 1 scheitert mit 4:7, Variante 2 geht einstimmig durch: Tempo 30 '
             'werktags von 7 bis 16.30 Uhr in der Münchener Straße.',
     'sessionId': SID, 'pos': 8},
]


def load(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f:
        return json.load(f)


def save(name, obj):
    with open(os.path.join(DATA, name), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def sitze(members_doc):
    """Die zwoelf regulaeren Sitzinhaber des BPU an diesem Tag."""
    bpu = next(b for b in members_doc['bodies'] if b['id'] == 'bpu')
    cfg = next(c for c in bpu['seatConfigs']
               if (c.get('from') or '0') <= DATE and (not c.get('to') or c['to'] >= DATE))
    ids = [cfg['chair']] + [v['member'] for v in cfg.get('vicechairs') or []] \
        + [s['member'] for s in cfg['seats']]
    assert len(ids) == 12 and len(set(ids)) == 12, ids
    return ids


def main():
    sessions, votes, topics = load('sessions.json'), load('votes.json'), load('topics.json')
    if any(s['id'] == SID for s in sessions):
        raise SystemExit(SID + ' steht schon in sessions.json')

    regulaer = sitze(load('members.json'))
    for mid in ABWESEND:
        assert mid in regulaer, mid
    anwesend = [m for m in regulaer if m not in ABWESEND]
    vertreter = len(VERTRETUNG)

    neu = []
    for i, (titel, text, ja, nein, topic, kurz, abgelehnt) in enumerate(BESCHLUESSE, start=1):
        vid = '%s_%02d' % (SID, i)
        stimmend = [m for m in anwesend if m not in kurz]
        assert len(stimmend) + vertreter == ja + nein, \
            '%s: %d Regulaere + %d Vertretung, aber %d Stimmen' % (vid, len(stimmend), vertreter, ja + nein)
        v = {'id': vid, 'sessionId': SID, 'topicId': topic, 'date': DATE,
             'title': titel, 'text': text}
        if nein == 0:
            v['type'] = 'named'
            v['results'] = {'yes': stimmend, 'no': [], 'absent': ABWESEND + kurz}
            v['source'] = {'tier': 'protocol-implicit'}
        else:
            v['type'] = 'anonymous'
            v['results'] = {'yes': ja, 'no': nein, 'absent': 12 - ja - nein}
        if abgelehnt:
            v['result'] = 'rejected'
        if kurz:
            v['excluded'] = [{'member': m, 'reason': 'kurzfristig abwesend'} for m in kurz]
            v['note'] = 'Herr Sabanovic war zum Zeitpunkt der Abstimmung nicht anwesend.'
        neu.append(v)

    agenda = []
    for nummer, titel, typ, pos, topic, notiz in AGENDA:
        item = {'number': nummer, 'title': titel}
        if typ:
            item['type'] = typ
        if pos:
            item['voteId'] = neu[pos[0] - 1]['id']
            if len(pos) > 1:
                item['voteIds'] = [neu[p - 1]['id'] for p in pos]
        if topic:
            item['topicId'] = topic
        if notiz:
            item['note'] = notiz
        agenda.append(item)

    sessions.append({
        'id': SID, 'date': DATE, 'type': 'bpu',
        'title': '2. Sitzung Bau-, Planungs- und Umweltausschuss – Juli 2026',
        'absent': ABWESEND, 'substitutes': VERTRETUNG, 'agenda': agenda,
    })
    sessions.sort(key=lambda s: (s['date'], s['id']))
    votes += neu
    votes.sort(key=lambda v: (v['date'], v['id']))

    t8 = next(t for t in topics if t['id'] == 't8')
    for h in HISTORY:
        h = dict(h)
        h['voteId'] = neu[h.pop('pos') - 1]['id']
        t8['history'].append(h)
    t8['history'].sort(key=lambda h: h['date'])

    save('sessions.json', sessions)
    save('votes.json', votes)
    save('topics.json', topics)
    print('%s: %d Beschlüsse, %d TOPs' % (SID, len(neu), len(agenda)))


if __name__ == '__main__':
    main()
