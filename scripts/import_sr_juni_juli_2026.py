"""Traegt die Niederschriften vom 29.06.2026 und 20.07.2026 ein.

Beide Sitzungen sind vollstaendig protokolliert, mit Anwesenheitsliste. Alle
einstimmigen Beschluesse lassen sich damit auf Namen aufloesen
(`protocol-implicit`); die eine geteilte Abstimmung bleibt anonym, weil die
Niederschrift keine Namen nennt.

Zwei Faelle, die nicht mechanisch sind:

  * 29.06., TOP 5: "StR Hadersdorfer war aufgrund kurzfristiger Abwesenheit
    nicht an der Abstimmung beteiligt." 21 statt 22 Stimmen. Hadersdorfer
    steht deshalb in `results.absent` und zusaetzlich in `excluded` -- das
    unterscheidet die kurze Abwesenheit von der ganztaegigen.
  * 29.06., TOP 4 und 7 sind Zurueckstellungen. Der Beschluss *lautet*, den
    Punkt zurueckzustellen, und er ging mit 22:0 durch -- das ist kein
    abgelehnter Beschluss, sondern ein angenommener. Kein `result: rejected`.

Verena Beibl war laut Liste nur bis 20:30 Uhr da (Sitzungsende 20:47). Alle
drei Abstimmungen zaehlen 22 Stimmen, also die volle Anwesenheit -- sie fielen
vor ihrem Gehen. Die Teilanwesenheit steht trotzdem in `partial`.
"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')

ABWESEND = {
    'sr_20260629': ['heinz', 'linz_karin', 'roeck'],
    'sr_20260720': ['stanglmaier', 'heinz'],
}

SITZUNGEN = [
    {
        'id': 'sr_20260629', 'date': '2026-06-29', 'type': 'stadtrat',
        'title': '9. Stadtratssitzung – Juni 2026',
        'partial': [{'member': 'beibl', 'to': '20:30'}],
        'agenda': [
            ('2', 'Mitteilungen des Ersten Bürgermeisters', 'formal', None),
            ('2.1', 'Vorstellung Projekt "Lange Nacht der Demokratie" durch VHS Moosburg',
             'discussion', None),
            ('3', 'Bürgerfragen gem. § 27 Abs. 2 GeschO/StR', 'formal', None),
            ('4', 'Einbeziehungssatzung "Niederambach Süd"', None, 1),
            ('5', 'Teilfortschreibung des Landesentwicklungsprogramms Bayern zur vorläufigen '
                  'Sicherung der Lärmschutzbereiche der Flugplätze Lechfeld, München und Salzburg',
             None, 2),
            ('6', 'Vorlage der Jahresrechnung 2025 gem. Art. 102 Abs. 2 GO', 'discussion', None),
            ('7', 'Beschluss über die Änderung des Widmungszwecks/der Nutzung der Stadthalle '
                  'Moosburg - Ausschluss von Parteiveranstaltungen', None, 3),
            ('8', 'Anfragen', 'formal', None),
        ],
        'votes': [
            {'title': 'Einbeziehungssatzung „Niederambach Süd" – zurückgestellt',
             'text': 'Der Stadtrat beschließt, den Tagesordnungspunkt zurückzustellen.',
             'yes': 22, 'no': 0},
            {'title': 'Landesentwicklungsprogramm – Lärmschutzbereiche Lechfeld, München, Salzburg',
             'text': 'Der Stadtrat nimmt den Teilfortschreibungsentwurf des '
                     'Landesentwicklungsprogramms Bayern zur vorläufigen Sicherung der '
                     'Lärmschutzbereiche der Flugplätze Lechfeld, München und Salzburg zur '
                     'Kenntnis.',
             'yes': 21, 'no': 0,
             'kurzfristig': ['hadersdorfer'],
             'note': 'StR Hadersdorfer war aufgrund kurzfristiger Abwesenheit nicht an der '
                     'Abstimmung beteiligt.'},
            {'title': 'Stadthalle – Ausschluss von Parteiveranstaltungen – zurückgestellt',
             'text': 'Der Stadtrat beschließt, den Tagesordnungspunkt zurückzustellen.',
             'yes': 22, 'no': 0},
        ],
    },
    {
        'id': 'sr_20260720', 'date': '2026-07-20', 'type': 'stadtrat',
        'title': '10. Stadtratssitzung – Juli 2026',
        'agenda': [
            ('2', 'Mitteilungen des Ersten Bürgermeisters', 'formal', None),
            ('3', 'Bürgerfragen gem. § 27 Abs. 2 GeschO/StR', 'formal', None),
            ('4', 'Genehmigung der öffentlichen Niederschriften (StR 15.06.2026)', None, 1),
            ('5', 'Einbeziehungssatzung "Niederambach Süd"', None, 2),
            ('6', 'Aufstellungsbeschluss Bebauungsplan Nr. 85 nebst 20. Änderung des '
                  'Flächennutzungsplans für die Flurstücke 1277, 1277/1, 1277/3, 1277/4, '
                  '1277/5, 1277/6, 1278 u. 1279 - Gemarkung Pfrombach', None, [3, 4, 5]),
            ('7', 'Haushalt 2026 - Finanzbericht zum 30.06.2026', 'discussion', None),
            ('8', 'Kläranlage Moosburg GmbH - Feststellung des Jahresabschlusses 2025 und '
                  'Beschluss über die Ergebnisverwendung', None, 6),
            ('9', 'Beschluss über Weitergewährung einer Arbeitsmarktzulage für Erzieher/innen '
                  'und Kinderpfleger/innen in den Kindertageseinrichtungen', None, 7),
            ('10', 'Anfragen', 'formal', None),
        ],
        'votes': [
            {'title': 'Genehmigung der öffentlichen Niederschrift (StR 15.06.2026)',
             'text': 'Der Stadtrat genehmigt den öffentlichen Teil der Niederschrift der '
                     'Stadtratssitzung vom 15.06.2026 unter Berücksichtigung der beantragten '
                     'Änderungen und Ergänzungen.',
             'yes': 23, 'no': 0},
            {'title': 'Einbeziehungssatzung „Niederambach Süd" – Aufstellungsbeschluss',
             'text': 'Der Stadtrat beschließt die Aufstellung der Einbeziehungssatzung '
                     '„Niederambach Süd" für eine Teilfläche des Flurstücks 1125 der Gemarkung '
                     'Niederambach. Die Verwaltung wird beauftragt, die nächsten '
                     'Verfahrensschritte sowie die Beteiligung der Öffentlichkeit und der '
                     'Behörden durchzuführen. Vor Verfahrensabschluss soll mit dem Antragsteller '
                     'ein städtebaulicher Vertrag zur genauen Regelung der Nutzung abgeschlossen '
                     'werden.',
             'yes': 23, 'no': 0},
            {'title': 'B-Plan Nr. 85 Pfrombach – Aufstellungsbeschluss mit 20. FNP-Änderung',
             'text': 'Der Stadtrat beschließt die Aufstellung des Bebauungsplans Nr. 85 zur '
                     'Festsetzung eines Gewerbegebiets für die Erweiterung eines bestehenden '
                     'Betriebsstandortes. Der Geltungsbereich umfasst die Flurnummern 1277, '
                     '1277/1, 1277/2, 1277/3, 1277/4, 1277/5, 1277/6, 1278 und 1279 der '
                     'Gemarkung Pfrombach. Mit der Aufstellung erfolgt gleichzeitig die 20. '
                     'Änderung des Flächennutzungsplans im Parallelverfahren.',
             'yes': 23, 'no': 0},
            {'title': 'B-Plan Nr. 85 Pfrombach – städtebaulicher Vertrag',
             'text': 'Die Verwaltung wird beauftragt, mit dem Bauwerber einen städtebaulichen '
                     'Vertrag abzuschließen, der die Durchführung der Bauleitplanung sichert. '
                     'Die gesamten Planungskosten inkl. aller Nebenkosten sind vollumfänglich '
                     'vom Bauwerber zu tragen.',
             'yes': 23, 'no': 0},
            {'title': 'B-Plan Nr. 85 Pfrombach – städtebaulicher Entwurf vor Verfahrenseintritt',
             'text': 'Die Verwaltung wird beauftragt, gemeinsam mit dem Antragsteller einen '
                     'städtebaulichen Entwurf für den Flächennutzungsplan und den Bebauungsplan '
                     'zu erarbeiten. Diese sind dem Stadtrat vor Eintritt in das Verfahren '
                     'vorzustellen.',
             'yes': 23, 'no': 0},
            {'title': 'Kläranlage GmbH – Jahresabschluss 2025',
             'text': 'Der Stadtrat empfiehlt der Gesellschafterversammlung, den Jahresabschluss '
                     '2025 in der vorliegenden Form festzustellen. Der Jahresüberschuss in Höhe '
                     'von 187.840,76 € wird mit dem Vortrag in Höhe von 2.146.081,45 € '
                     'verrechnet und zusammen in Höhe von 2.333.922,21 € auf neue Rechnung '
                     'vorgetragen.',
             'yes': 23, 'no': 0},
            {'title': 'Arbeitsmarktzulage Erzieher/Kinderpfleger – Erhöhung auf 125 €',
             'text': 'Der Stadtrat beschließt, die Arbeitsmarktzulage ab 01.09.2026 auf '
                     '125,00 € zu erhöhen.',
             'yes': 13, 'no': 10},
        ],
    },
]


def load(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f:
        return json.load(f)


def save(name, obj):
    with open(os.path.join(DATA, name), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def roster(members, date):
    return [m['id'] for m in members
            if m.get('from', '9999') <= date and (m.get('to') is None or m['to'] >= date)]


def main():
    sessions, votes = load('sessions.json'), load('votes.json')
    members = load('members.json')['members']
    have = {s['id'] for s in sessions}

    neue_sessions, neue_votes = [], []
    for spec in SITZUNGEN:
        sid, date = spec['id'], spec['date']
        if sid in have:
            raise SystemExit(sid + ' steht schon in sessions.json')

        alle = roster(members, date)
        assert len(alle) == 25, '%s: %d Sitze' % (sid, len(alle))
        abwesend = ABWESEND[sid]
        for mid in abwesend:
            assert mid in alle, mid
        anwesend = [m for m in alle if m not in abwesend]

        for i, spec_v in enumerate(spec['votes'], start=1):
            vid = '%s_%02d' % (sid, i)
            kurz = spec_v.get('kurzfristig', [])
            stimmberechtigt = [m for m in anwesend if m not in kurz]
            assert len(stimmberechtigt) == spec_v['yes'] + spec_v['no'], \
                '%s: %d anwesend, %d Stimmen' % (vid, len(stimmberechtigt),
                                                 spec_v['yes'] + spec_v['no'])
            v = {'id': vid, 'sessionId': sid, 'topicId': None, 'date': date,
                 'title': spec_v['title'], 'text': spec_v['text']}
            if spec_v['no'] == 0:
                # Einstimmig bei bekannter Anwesenheit: jede Stimme ist Rechnung,
                # nicht Vermutung.
                v['type'] = 'named'
                v['results'] = {'yes': stimmberechtigt, 'no': [],
                                'absent': abwesend + kurz}
                v['source'] = {'tier': 'protocol-implicit'}
            else:
                # Geteilt und ohne Namen in der Niederschrift -- nur das Ergebnis.
                v['type'] = 'anonymous'
                v['results'] = {'yes': spec_v['yes'], 'no': spec_v['no'],
                                'absent': len(abwesend)}
            if kurz:
                v['excluded'] = [{'member': m, 'reason': 'kurzfristig abwesend'} for m in kurz]
            if spec_v.get('note'):
                v['note'] = spec_v['note']
            neue_votes.append(v)

        agenda = []
        for number, title, kind, ref in spec['agenda']:
            item = {'number': number, 'title': title}
            if kind:
                item['type'] = kind
            if isinstance(ref, list):
                item['voteId'] = '%s_%02d' % (sid, ref[0])
                item['voteIds'] = ['%s_%02d' % (sid, n) for n in ref]
            elif ref:
                item['voteId'] = '%s_%02d' % (sid, ref)
            agenda.append(item)

        session = {'id': sid, 'date': date, 'type': spec['type'], 'title': spec['title'],
                   'absent': abwesend, 'agenda': agenda}
        if spec.get('partial'):
            session['partial'] = spec['partial']
        neue_sessions.append(session)

    sessions += neue_sessions
    sessions.sort(key=lambda s: (s['date'], s['id']))
    votes += neue_votes
    votes.sort(key=lambda v: (v['date'], v['id']))
    save('sessions.json', sessions)
    save('votes.json', votes)
    print('%d Sitzungen, %d Beschlüsse' % (len(neue_sessions), len(neue_votes)))


if __name__ == '__main__':
    main()
