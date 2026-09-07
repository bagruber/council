"""Niederschriften der 4. und 5. Stadtratssitzung 2026 einarbeiten.

SR 25.03.2026 und SR 20.04.2026 — beide noch im alten Stadtrat (Dollinger).
Einstimmige Beschlüsse werden aus der Anwesenheitsliste zu named-Voten
aufgelöst, geteilte bleiben anonym.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')


def load(n):
    return json.load(open(os.path.join(DATA, n), encoding='utf-8'))


def save(n, o):
    with open(os.path.join(DATA, n), 'w', encoding='utf-8') as f:
        json.dump(o, f, ensure_ascii=False, indent=2)
        f.write('\n')


# Anwesenheit laut Niederschrift
ABWESEND = {
    'sr_20260325': ['stanglmaier', 'becher_a', 'becher_j', 'gruber'],
    'sr_20260420': ['gruber', 'heinz'],
}

members = load('members.json')


def aktiv_am(m, datum):
    # Geteilte Mandate (Marschoun) liegen in periods; from/to spannt die Lücke.
    perioden = m.get('periods') or [{'from': m.get('from'), 'to': m.get('to')}]
    return any((not p.get('from') or p['from'] <= datum)
               and (not p.get('to') or p['to'] >= datum) for p in perioden)


def anwesend(sid, datum):
    return [m['id'] for m in members['members']
            if aktiv_am(m, datum) and m['id'] not in ABWESEND[sid]]


P325 = anwesend('sr_20260325', '2026-03-25')
P420 = anwesend('sr_20260420', '2026-04-20')
assert len(P325) == 21 and len(P420) == 23, (len(P325), len(P420))


def named(sid, datum, nr, titel, text, topic=None, ohne=None):
    """Einstimmig — Einzelstimmen aus der Anwesenheit. `ohne`: (id, grund)."""
    da = list(P325 if sid == 'sr_20260325' else P420)
    fehlt = list(ABWESEND[sid])
    v = {'id': f'{sid}_{nr:02d}', 'sessionId': sid, 'topicId': topic, 'date': datum,
         'title': titel, 'text': text, 'type': 'named'}
    if ohne:
        da.remove(ohne[0])
        fehlt.append(ohne[0])
    v['results'] = {'yes': da, 'no': [], 'absent': fehlt}
    v['source'] = {'tier': 'protocol-implicit'}
    if ohne:
        v['excluded'] = [{'member': ohne[0], 'reason': ohne[1]}]
    return v


def anonym(sid, datum, nr, titel, text, ja, nein, topic=None, ohne=None):
    """Geteilt — nur das Aggregat ist bekannt."""
    v = {'id': f'{sid}_{nr:02d}', 'sessionId': sid, 'topicId': topic, 'date': datum,
         'title': titel, 'text': text, 'type': 'anonymous',
         'results': {'yes': ja, 'no': nein, 'absent': 25 - ja - nein}}
    if ohne:
        v['excluded'] = [{'member': ohne[0], 'reason': ohne[1]}]
    return v


D3, D4 = '2026-03-25', '2026-04-20'

votes_neu = [
    named('sr_20260325', D3, 1, 'Genehmigung der öffentlichen Niederschriften',
          'Der Stadtrat genehmigt den öffentlichen Teil der Niederschrift der Stadtratssitzungen vom 02.02.2026 und 23.02.2026.'),
    anonym('sr_20260325', D3, 2, 'Klageverfahren Studentenwohnheim Rockermaier Areal',
           'Der Stadtrat beschließt, die Klage gegen die Baugenehmigung für das Studentenwohnheim auf Flurnummer 673 gemäß dem noch abzuschließenden Vergleichsvertrag zurückzuziehen. Bürgermeister und Verwaltung ziehen die Klage zurück, sobald die Voraussetzungen des Vergleichs vorliegen.',
           20, 1, topic='t5'),
    named('sr_20260325', D3, 3, 'Theresia-Gerhardinger-Grundschule – Ergebnis der Kostenkommission',
          'Dem Ergebnis der Kostenkommission mit Kosteneinsparungsvorschlägen in Höhe von 516.477,63 € brutto wird die Zustimmung erteilt.',
          topic='t6'),
    anonym('sr_20260325', D3, 4, 'B-Plan Nr. 66 „Oberes Gereuth Nord-Ost" – Billigungsbeschluss',
           'Der Stadtrat nimmt den Entwurf des Bebauungsplans mit Grünordnungsplan, Begründung und Umweltbericht in der Fassung vom 26.02.2026 zur Kenntnis und billigt die Planunterlagen zur öffentlichen Auslegung nach § 3 Abs. 2 BauGB.',
           19, 1, ohne=('fincke', 'kurzfristig abwesend')),
    named('sr_20260325', D3, 5, 'Deichsanierung BA 07 – Projekt Isar 2020',
          'Der Stadtrat erteilt zum Antrag des Freistaats Bayern auf wasserrechtliche Plangenehmigung zur Sanierung des Deichabschnitts BA 07 das gemeindliche Einvernehmen, einschließlich der Ausnahmen von den Festsetzungen des Natura-2000-Gebiets „Isarauen von Unterföhring bis Landshut".',
          ohne=('fincke', 'kurzfristig abwesend')),
    anonym('sr_20260325', D3, 6, '„Bauturbo" – Anpassung der Geschäftsordnung',
           'Der Stadtrat beschließt die 1. Änderung der Geschäftsordnung des Stadtrats. Die Änderung betrifft § 13 Abs. 2 Nr. 4 Nr. 1 und regelt die Zustimmung der Gemeinde nach § 36a BauGB.',
           17, 4),

    anonym('sr_20260420', D4, 1, 'Studentenwohnheim Saliterstraße 8 und 10',
           'Das gemeindliche Einvernehmen ist nach § 36 BauGB nicht erforderlich, da der gemeindliche Planungswille durch Wahrung des Bebauungsplans gewürdigt wurde. Der Stadtrat beschließt, keine weiteren Maßnahmen zur Sicherung der Bauleitplanung nach §§ 14 und 15 BauGB zu treffen.',
           22, 1, topic='t5'),
    anonym('sr_20260420', D4, 2, 'Mehrfamilienhaus mit 23 Wohneinheiten – Graf-Burkhard-Straße 2',
           'Der Stadtrat erteilt das gemeindliche Einvernehmen und stimmt den beantragten Befreiungen von den Festsetzungen des Bebauungsplans zu.',
           22, 1, topic='t5'),
    anonym('sr_20260420', D4, 3, 'Mehrfamilienhaus mit 16 Wohneinheiten – Weihmühlstraße 21',
           'Der Stadtrat erteilt das gemeindliche Einvernehmen und stimmt den beantragten Befreiungen von den Festsetzungen des Bebauungsplans zu.',
           21, 1, topic='t5', ohne=('hadersdorfer', 'kurzfristig abwesend')),
    named('sr_20260420', D4, 4, 'Erweiterungsbau Theresia-Gerhardinger-Grundschule',
          'Der Stadtrat erteilt zum Erweiterungsbau der Theresia-Gerhardinger-Grundschule mit Tiefgarage das gemeindliche Einvernehmen.',
          topic='t6'),
    anonym('sr_20260420', D4, 5, '18. Änderung Flächennutzungsplan – Windkraft Lohbert',
           'Der Stadtrat beschließt die 18. Änderung des Flächennutzungsplans im Regelverfahren nach § 2 BauGB. Der Umgriff umfasst das Flurstück 579 der Gemarkung Niederambach; die Verwaltung erstellt die Planunterlagen und führt die Beteiligungen durch.',
           20, 3),
    named('sr_20260420', D4, 6, '2. Änderung B-Plan Nr. 3 „Thalbacher Au Süd-Ost"',
          'Der Stadtrat nimmt den städtebaulichen Entwurf (Variante 3) in der Fassung vom 13.04.2026 zur Kenntnis und beschließt die 2. Änderung im vereinfachten Verfahren nach § 13 BauGB. Der Entwurf wird weiter ausgearbeitet und vor den Beteiligungen erneut vorgelegt.'),
    named('sr_20260420', D4, 7, 'Aufstellungsbeschluss B-Plan Nr. 83 „Erweiterung Gymnasium"',
          'Der Stadtrat beschließt die Aufstellung des Bebauungsplans „Erweiterung Gymnasium" für das Flurstück 703 der Gemarkung Moosburg a.d. Isar im vereinfachten Verfahren nach § 13 BauGB. Als Art der baulichen Nutzung wird ein Sondergebiet „Schule" festgesetzt.'),
    named('sr_20260420', D4, 8, 'Gemeinsamer Datenschutzbeauftragter – Aufhebungsvereinbarung',
          'Der Stadtrat stimmt der Kündigung der Zweckvereinbarung zwischen dem Landkreis Freising und den beteiligten Gebietskörperschaften über die gemeinsame Bestellung eines Datenschutzbeauftragten zum 01.07.2026 zu und beauftragt den Ersten Bürgermeister mit den weiteren Schritten.'),
    named('sr_20260420', D4, 9, 'Feststellung der Jahresrechnung 2024',
          'Der Stadtrat stellt die Jahresrechnung nach Art. 102 Abs. 3 Satz 1 GO fest. Die Verwaltung nimmt zu den Feststellungen des Rechnungsprüfungsausschusses Stellung.',
          topic='t7'),
    named('sr_20260420', D4, 10, 'Entlastung zur Jahresrechnung 2024',
          'Der Stadtrat erteilt die Entlastung gem. Art. 102 Abs. 3 Satz 1 GO zur Jahresrechnung 2024.',
          topic='t7', ohne=('dollinger', 'persönliche Beteiligung')),
]

sessions_neu = [
    {'id': 'sr_20260325', 'date': D3, 'type': 'stadtrat',
     'title': '4. Stadtratssitzung – März 2026',
     'absent': ABWESEND['sr_20260325'],
     'agenda': [
         {'number': '3', 'title': 'Mitteilungen des Ersten Bürgermeisters', 'type': 'formal'},
         {'number': '4', 'title': 'Bürgerfragen gem. § 27 Abs. 2 GeschO/StR', 'type': 'formal'},
         {'number': '5', 'title': 'Genehmigung der öffentlichen Niederschriften (StR 02.02.2026; StR 23.02.2026)',
          'voteId': 'sr_20260325_01'},
         {'number': '6', 'title': 'Klageverfahren - Studentenwohnheim Rockermaier Areal - weiteres Vorgehen',
          'topicId': 't5', 'voteId': 'sr_20260325_02'},
         {'number': '7', 'title': 'Erweiterung Theresia-Gerhardinger-Grundschule; Ergebnisse Kostenkommission mit Beschlussfassung zum Entwurf',
          'topicId': 't6', 'voteId': 'sr_20260325_03'},
         {'number': '8', 'title': 'B-Plan Nr. 66 "Oberes Gereuth Nordost" - Vorstellung aktuelle Planung - Billigungsbeschluss',
          'voteId': 'sr_20260325_04'},
         {'number': '9', 'title': 'Vollzug der Wassergesetze; Antrag Freistaat Bayern auf wasserrechtliche Plangenehmigung zur Sanierung des Deichabschnitts BA 07, Projekt Isar 2020',
          'voteId': 'sr_20260325_05'},
         {'number': '10', 'title': 'Vollzug der Baugesetze; "Bauturbo" - Zustimmung der Gemeinde gem. § 36a BauGB - Anpassung der Geschäftsordnung',
          'voteId': 'sr_20260325_06'},
         {'number': '11', 'title': 'Anfragen', 'type': 'formal'},
     ]},
    {'id': 'sr_20260420', 'date': D4, 'type': 'stadtrat',
     'title': '5. Stadtratssitzung – April 2026',
     'absent': ABWESEND['sr_20260420'],
     'agenda': [
         {'number': '3', 'title': 'Mitteilungen des Ersten Bürgermeisters', 'type': 'formal'},
         {'number': '4', 'title': 'Bürgerfragen gem. § 27 Abs. 2 GeschO/StR', 'type': 'formal'},
         {'number': '5', 'title': 'Baugesuche und Anträge'},
         {'number': '5.1', 'title': 'Errichtung eines Studentenwohnheims bestehend aus vier Wohngebäude und zugehöriger Tiefgarage - Saliterstr. 8 und 10',
          'topicId': 't5', 'voteId': 'sr_20260420_01'},
         {'number': '5.2', 'title': 'Neubau eines Mehrfamilienwohnhaus mit 23 Wohneinheiten und Tiefgarage - Graf-Burkhard-Str. 2',
          'topicId': 't5', 'voteId': 'sr_20260420_02'},
         {'number': '5.3', 'title': 'Neubau eines Mehrfamilienwohnhauses mit 16 Wohneinheiten und Tiefgarage - Weihmühlstr. 21',
          'topicId': 't5', 'voteId': 'sr_20260420_03'},
         {'number': '5.4', 'title': 'Erweiterungsbau Theresia-Gerhardinger-Grundschule mit Tiefgarage',
          'topicId': 't6', 'voteId': 'sr_20260420_04'},
         {'number': '6', 'title': 'Aufstellungsbeschluss 18. Änderung Flächennutzungsplan - Windkraft Lohbert',
          'voteId': 'sr_20260420_05'},
         {'number': '7', 'title': 'Aufstellungsbeschluss zur 2. Änderung des Bebauungsplan Nr. 3 "Thalbacher Au Süd-Ost"',
          'voteId': 'sr_20260420_06'},
         {'number': '8', 'title': 'Aufstellungsbeschluss B-Plan Nr. 83 "Erweiterung Gymnasium"',
          'voteId': 'sr_20260420_07'},
         {'number': '9', 'title': 'Beschluss über die Aufhebungsvereinbarung der Zweckvereinbarung zur Bestellung eines gemeinsamen Datenschutzbeauftragten',
          'voteId': 'sr_20260420_08'},
         {'number': '10', 'title': 'Beschlüsse zur Jahresrechnung 2024'},
         {'number': '10.1', 'title': 'Beschluss über die Feststellung der Jahresrechnung 2024',
          'topicId': 't7', 'voteId': 'sr_20260420_09'},
         {'number': '10.2', 'title': 'Beschluss über die Entlastung des RPA zur Jahresrechnung 2024',
          'topicId': 't7', 'voteId': 'sr_20260420_10'},
         {'number': '11', 'title': 'Anfragen', 'type': 'formal'},
     ]},
]

historie = {
    't5': [
        {'date': D3, 'type': 'vote', 'title': 'Klage wird zurückgezogen',
         'text': 'Nach dem ausgehandelten Vergleichsvertrag zieht die Stadt ihre Klage gegen die Baugenehmigung zurück (20:1). Damit endet das Verfahren, das der Stadtrat im Februar beschlossen hatte.',
         'sessionId': 'sr_20260325', 'voteId': 'sr_20260325_02'},
        {'date': D4, 'type': 'vote', 'title': 'Keine weiteren Sicherungsmaßnahmen',
         'text': 'Für das Studentenwohnheim an der Saliterstraße ist das gemeindliche Einvernehmen nicht erforderlich. Der Stadtrat verzichtet mit 22:1 auf weitere Maßnahmen zur Sicherung der Bauleitplanung.',
         'sessionId': 'sr_20260420', 'voteId': 'sr_20260420_01'},
        {'date': D4, 'type': 'vote', 'title': 'Einvernehmen für zwei Mehrfamilienhäuser',
         'text': 'Graf-Burkhard-Straße 2 (23 Wohneinheiten, 22:1) und Weihmühlstraße 21 (16 Wohneinheiten, 21:1) erhalten das gemeindliche Einvernehmen samt Befreiungen vom Bebauungsplan.',
         'sessionId': 'sr_20260420', 'voteId': 'sr_20260420_02'},
    ],
    't6': [
        {'date': D3, 'type': 'vote', 'title': 'Kostenkommission spart 516.000 €',
         'text': 'Die Kostenkommission legt ihre Vorschläge vor: 516.477,63 € brutto weniger als geplant. Der Stadtrat stimmt dem Ergebnis einstimmig zu.',
         'sessionId': 'sr_20260325', 'voteId': 'sr_20260325_03'},
        {'date': D4, 'type': 'vote', 'title': 'Einvernehmen für den Erweiterungsbau',
         'text': 'Der Stadtrat erteilt dem Erweiterungsbau mit Tiefgarage einstimmig das gemeindliche Einvernehmen — der bauliche Startschuss nach der Kostenrunde im März.',
         'sessionId': 'sr_20260420', 'voteId': 'sr_20260420_04'},
    ],
    't7': [
        {'date': D4, 'type': 'vote', 'title': 'Jahresrechnung 2024 festgestellt',
         'text': 'Der Stadtrat stellt die Jahresrechnung 2024 fest und erteilt die Entlastung. Bürgermeister Dollinger war wegen persönlicher Beteiligung nicht stimmberechtigt.',
         'sessionId': 'sr_20260420', 'voteId': 'sr_20260420_09'},
    ],
}


def main():
    sessions, votes, topics = load('sessions.json'), load('votes.json'), load('topics.json')

    vorhanden = {s['id'] for s in sessions}
    assert not vorhanden & {s['id'] for s in sessions_neu}, 'Sitzung schon erfasst'

    sessions.extend(sessions_neu)
    sessions.sort(key=lambda s: (s['date'], s['id']))
    votes.extend(votes_neu)
    votes.sort(key=lambda v: (v['date'], v['id']))

    for t in topics:
        for h in historie.get(t['id'], []):
            t['history'].append(h)
        if t['id'] in historie:
            t['history'].sort(key=lambda h: h['date'])

    save('sessions.json', sessions)
    save('votes.json', votes)
    save('topics.json', topics)
    print(f'+{len(sessions_neu)} Sitzungen, +{len(votes_neu)} Voten, '
          f'+{sum(len(v) for v in historie.values())} Historien-Einträge')


if __name__ == '__main__':
    main()
