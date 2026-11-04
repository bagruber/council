"""Arbeitet die Niederschriften vom 15.06. und 28.09.2026 ein.

Der 15.06. stand als Beschlussauszug im Register, der 28.09. nur als leerer
Eintrag. Die Vote-IDs vom 15.06. bleiben, neu sind die beiden Beschluesse, die
der Auszug nicht fuehrte (Vertagung der Farbwahl, Fairtrade-Lenkungsgruppe).

Dazu ein neues Dossier zum Bebauungsplan Nr. 3 (zweite Sitzung, siehe
feedback_bebauungsplan_dossier) und der Vorsitz im Rechnungspruefungsausschuss.

Einmal laufen lassen:
    python scripts/sr_niederschriften_2026_herbst.py
    python scripts/mark_inferable.py
"""
import json, os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def load(n):
    return json.load(open(os.path.join(DATA, n), encoding='utf-8'))


def save(n, obj):
    with open(os.path.join(DATA, n), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def rat_am(members, datum):
    rat = [m['id'] for m in members
           if any((s.get('from') or '0') <= datum <= (s.get('to') or '9999') for s in m['mandates'])]
    assert len(rat) == 25, (datum, len(rat))
    return rat


STROBL = {'tiers': ['selbstauskunft'], 'by': 'strobl'}
MERKUR = 'https://www.merkur.de/lokales/freising/moosburg-ort29088/'
PRESSE = [
    ('merkur_2026-04-28_neues-bauland-neustadt', 'merkur', '2026-04-28',
     'Neues Bauland für die Neustadt – und auch ein Spielplatz? Debatte im Moosburger Stadtrat',
     MERKUR + 'neues-bauland-fuer-die-neustadt-und-auch-ein-spielplatz-debatte-im-moosburger-stadtrat-94281394.html'),
    ('mz_2026-09-29_falschparker', 'mz', '2026-09-29', 'Für Falschparker wird’s in Moosburg ungemütlich',
     'https://www.idowa.de/regionen/moosburg/fuer-falschparker-wirds-in-moosburg-ungemuetlich-art-417857'),
    ('merkur_2026-10-07_parkkontrolle', 'merkur', '2026-10-07', 'Stadt Moosburg lagert Kontrolle der parkenden Autos aus',
     MERKUR + 'stadt-moosburg-lagert-kontrolle-der-parkenden-autos-aus-94528114.html'),
    ('merkur_2026-10-09_schulwegplaene', 'merkur', '2026-10-09',
     'Mehr Verkehrssicherheit für Moosburgs Schüler: Stadtrat beschließt Einführung von digitalen Schulwegplänen',
     MERKUR + 'mehr-verkehrssicherheit-fuer-moosburgs-schueler-stadtrat-beschliesst-einfuehrung-von-digitalen-schulwegplaenen-94531692.html'),
]

T_BP3 = 't36'
DOSSIER = {
    'id': T_BP3, 'title': 'Bebauungsplan Nr. 3 „Thalbacher Au Süd-Ost“', 'tags': ['building'], 'image': None,
    'summary': 'Im Dreieck zwischen Neustadt-, Birken- und Schillerstraße will die Stadt auf eigenen Grundstücken verdichten: 16 Parzellen mit Doppelhäusern und einem Einfamilienhaus, für 50 bis 60 neue Anwohner. Der Plan stammt von 1963 und wird dafür ein zweites Mal geändert.',
    'field': 'building', 'type': 'gebiet', 'status': 'laufend',
    'history': [],
}


def main():
    members = load('members.json')
    sessions = load('sessions.json')
    votes = load('votes.json')
    topics = load('topics.json')
    press = load('press.json')
    bodies = load('bodies.json')
    by_s = {s['id']: s for s in sessions}
    by_v = {v['id']: v for v in votes}

    vorhanden = {p['id'] for p in press}
    for pid, media, datum, titel, url in PRESSE:
        if pid not in vorhanden:
            press.append({'id': pid, 'media': media, 'date': datum, 'title': titel, 'url': url})

    # ── 15.06.2026 ──────────────────────────────────────────────────────────
    s = by_s['sr_20260615']
    assert s['niederschrift'] == 'auszug'
    s['niederschrift'] = 'vollständig'
    s.pop('source')
    s['absent'] = ['welter']
    rat = rat_am(members, s['date'])
    da = [m for m in rat if m != 'welter']
    assert len(da) == 24

    def setze(vid, titel=None, text=None, **felder):
        v = by_v[vid]
        for k in ('inferable', 'note', 'excluded', 'voters', 'result'):
            v.pop(k, None)
        if titel:
            v['title'] = titel
        if text:
            v['text'] = text
        v.update(felder)

    def named(ohne=(), nein=()):
        stimmen = [m for m in da if m not in ohne]
        return {'yes': [m for m in stimmen if m not in nein], 'no': list(nein),
                'absent': [m for m in rat if m not in stimmen]}

    setze('sr_20260615_01', text='Der Stadtrat genehmigt den öffentlichen Teil der Niederschriften vom 11.05. und 18.05.2026.',
          type='anonymous', results={'yes': 23, 'no': 0, 'absent': 2}, source={'tier': 'protocol-implicit'})
    setze('sr_20260615_02', text='Der Flächennutzungsplan wird für den Bereich „Degernpoint Nord“ geändert, im Parallelverfahren mit dem Bebauungsplan Nr. 82.',
          type='anonymous', results={'yes': 23, 'no': 0, 'absent': 2}, source={'tier': 'protocol-implicit'})
    setze('sr_20260615_03', text='Einvernehmen zum Vorbescheid erteilt.',
          type='named', results=named(), source={'tier': 'protocol-implicit'})
    setze('sr_20260615_04', text='Der Stadtrat beschließt, gegen den Vorbescheid für die Sternstraße 12 zu klagen.',
          type='named', results=named(ohne=['heinz']), source={'tier': 'protocol-implicit'},
          excluded=[{'member': 'heinz', 'reason': 'beteiligung'}])
    setze('sr_20260615_05', text='Verena Beibl wird Vorsitzende des Rechnungsprüfungsausschusses, Manfred Tristl ihr Stellvertreter.',
          type='named', results=named(), source={'tier': 'protocol-implicit'})
    setze('sr_20260615_06', text='Die monatliche Dienstaufwandsentschädigung des Ersten Bürgermeisters wird auf 878,10 € festgesetzt; der Betrag liegt innerhalb des gesetzlichen Rahmens.',
          type='anonymous', results={'yes': 21, 'no': 2, 'absent': 2}, source={'tier': 'result-only'},
          excluded=[{'member': 'mader', 'reason': 'beteiligung'}],
          voters={'strobl': dict(STROBL, vote='no', note='Beantragte 50 % und wurde überstimmt')})
    # Strobl beantragte auch hier die Kuerzung; die eine Gegenstimme ist seine,
    # die uebrigen 21 sind Rechnung.
    setze('sr_20260615_07', text='Die Aufwandsentschädigung bleibt unverändert: 1.337,91 € monatlich für den Zweiten, 538,00 € für den Dritten Bürgermeister.',
          type='named', results=named(ohne=['lauterbach', 'stanglmaier'], nein=['strobl']),
          source={'tier': 'selbstauskunft', 'by': 'strobl'},
          excluded=[{'member': 'lauterbach', 'reason': 'beteiligung'}, {'member': 'stanglmaier', 'reason': 'beteiligung'}],
          voters={'strobl': dict(STROBL, note='Beantragte die Kürzung um 50 %')})
    setze('sr_20260615_08', titel='Besetzung des Energiebeirates',
          text='In den Energiebeirat gehen Mader, Stanglmaier, Heinz, Kilian Linz, Sixt und Marcus.',
          type='named', results=named(), source={'tier': 'protocol-implicit'})
    setze('sr_20260615_09', titel='Rathaus 3. BA – Farbkonzept der Fassade: Variante 1 (Grauton)',
          text='Der Stadtrat wählt für die Fassade Variante 1 (Grauton); die Umsetzung folgt den Vorgaben des Landesamts für Denkmalpflege und der Planung des Architekten.',
          type='anonymous', results={'yes': 12, 'no': 11, 'absent': 2}, source={'tier': 'result-only'},
          voters={'strobl': dict(STROBL, vote='yes')})

    neu = [
        {'id': 'sr_20260615_10', 'sessionId': 'sr_20260615', 'topicIds': ['t17'],
         'title': 'Rathaus 3. BA – Farbwahl vertagen',
         'text': 'Antrag, die Entscheidung über die Farbe bis zur Sitzung am 29.06. zu vertagen, abgelehnt.',
         'type': 'anonymous', 'result': 'rejected', 'results': {'yes': 4, 'no': 19, 'absent': 2},
         'source': {'tier': 'result-only'},
         'voters': {'dick': dict(STROBL, vote='yes', note='Antragstellerin; wollte die Bürger befragen'),
                    'strobl': dict(STROBL, vote='yes')}},
        {'id': 'sr_20260615_11', 'sessionId': 'sr_20260615',
         'title': 'Fairtrade-Lenkungsgruppe vertagt',
         'text': 'Die Neubesetzung der Fairtrade-Lenkungsgruppe wird vertagt, bis die Referenten bestellt sind.',
         'type': 'named', 'results': named(), 'source': {'tier': 'protocol-implicit'}},
    ]
    i = next(n for n, v in enumerate(votes) if v['id'] == 'sr_20260615_09') + 1
    votes[i:i] = neu

    for a in s['agenda']:
        if a['number'] in ('5', '6', '7'):
            a['type'] = 'formal'
        if a['number'] == '7.1':
            a['type'] = 'discussion'
        if a['number'] == '6.4':
            a['voteIds'] = ['sr_20260615_08', 'sr_20260615_11']
        if a['number'] == '7.2':
            a['voteIds'] = ['sr_20260615_10', 'sr_20260615_09']

    # ── 28.09.2026 ──────────────────────────────────────────────────────────
    s = by_s['sr_20260928']
    assert s['niederschrift'] == 'keine'
    fehlt = ['beibl', 'dick', 'heinz', 'linz_karin', 'marschoun', 'strobl']
    rat = rat_am(members, s['date'])
    da = [m for m in rat if m not in fehlt]
    assert len(da) == 19
    t26, t8 = ['t26'], ['t8']

    def voll(nr, titel, text, thema=None):
        v = {'id': f'sr_20260928_{nr:02d}', 'sessionId': 'sr_20260928'}
        if thema:
            v['topicIds'] = thema
        v.update(title=titel, text=text, type='named',
                 results={'yes': list(da), 'no': [], 'absent': list(fehlt)},
                 source={'tier': 'protocol-implicit'})
        return v

    def v_id(nr, titel, text, ja, nein, thema=None, **rest):
        v = {'id': f'sr_20260928_{nr:02d}', 'sessionId': 'sr_20260928'}
        if thema:
            v['topicIds'] = thema
        v.update(title=titel, text=text, type='anonymous')
        if ja < nein:
            v['result'] = 'rejected'
        v['results'] = {'yes': ja, 'no': nein, 'absent': 25 - ja - nein}
        v.update(rest)
        return v

    neue = [
        voll(1, 'Beitritt zum Zweckverband Verkehrsüberwachung',
             'Die Stadt tritt dem Zweckverband „Kommunale Verkehrsüberwachung Südostbayern“ bei und überträgt ihm die Überwachung des ruhenden Verkehrs samt Bußgeldstelle.'),
        voll(2, 'B-Plan Nr. 3 „Thalbacher Au Süd-Ost“, 2. Änderung – Billigung',
             'Der Entwurf in der Fassung vom 15.09.2026 wird gebilligt und öffentlich ausgelegt.', [T_BP3]),
        v_id(3, 'Digitaler Schulwegplan auf Probe (Antrag Grüne)',
             'Eine Fachfirma erstellt für ein Jahr probeweise einen digitalen Schulwegplan; danach kommen Ergebnisse und Rückmeldungen wieder in den Stadtrat.',
             12, 7, t8, source={'tier': 'press', 'pressId': 'merkur_2026-10-09_schulwegplaene'},
             voters={'sixt': {'vote': 'yes', 'tiers': ['press']},
                     'stanglmaier': {'vote': 'yes', 'evidence': 'soft'}}),
        voll(4, '27. Änderung des Regionalplans München',
             'Der Fortschreibungsentwurf zu den Kapiteln Siedlung und Freiraum sowie Verkehr wird zustimmend zur Kenntnis genommen.'),
        v_id(5, 'Flächennutzungsplan der Gemeinde Mauern – keine Bedenken',
             'Die Belange der Stadt sind durch die Neuaufstellung nicht berührt.', 18, 0,
             source={'tier': 'protocol-implicit'}),
        voll(6, 'Bündelausschreibung Strom und Gas ab 2028 – Vollmacht',
             'Der Bürgermeister erteilt der Bayerischer Gemeindetag Kommunal-GmbH die Vollmacht für die Bündelausschreibung; den Zuschlag erhält das preisgünstigste Angebot.', t26),
        v_id(7, 'Strom ab 2028 – 100 % Ökostrom mit Neuanlagenquote',
             'Vorschlag, Ökostrom mit Neuanlagenquote zu beschaffen, abgelehnt.', 6, 12, t26,
             source={'tier': 'result-only'},
             note='Die Niederschrift schreibt „Beschlossen“ bei 6:12; nach der Zahl ist der Vorschlag abgelehnt.'),
        voll(8, 'Strom ab 2028 – 100 % Ökostrom ohne Neuanlagenquote',
             'Beschafft wird 100 % Ökostrom ohne Neuanlagenquote.', t26),
        voll(9, 'Gas ab 2028', 'Die enPORTAL GmbH beschafft ab 01.01.2028 Erdgas.', t26),
        voll(10, 'Bündelausschreibung – Freigabe', 'Der Bürgermeister gibt die Ausschreibung innerhalb von 14 Tagen nach Bereitstellung des Vergabekonzepts frei.', t26),
        voll(11, 'Bündelausschreibung – Verbrauchsdaten', 'Der Bürgermeister erteilt der enPORTAL GmbH die Vollmacht, Abnahmestellen und Verbrauchsdaten abzufragen.', t26),
    ]
    datum_von = {x['id']: x['date'] for x in sessions}
    i = next((n for n, v in enumerate(votes) if datum_von.get(v['sessionId'], '') > s['date']), len(votes))
    votes[i:i] = neue

    s['niederschrift'] = 'vollständig'
    s['start'] = '19:00'
    s['title'] = '13. Stadtratssitzung – September 2026'
    s['absent'] = fehlt
    s['agenda'] = [
        {'number': '1', 'title': 'Mitteilungen des Ersten Bürgermeisters', 'type': 'formal'},
        {'number': '2', 'title': 'Bürgerfragen gem. § 27 Abs. 2 GeschO/StR', 'type': 'formal'},
        {'number': '3', 'title': 'Beitritt zum Zweckverband kommunale Verkehrsüberwachung Südostbayern (ruhender Verkehr)',
         'voteIds': ['sr_20260928_01'], 'press': ['mz_2026-09-29_falschparker', 'merkur_2026-10-07_parkkontrolle']},
        {'number': '4', 'title': 'Bebauungsplan Nr. 3 „Thalbacher Au Südost“, 2. Änderung – Vorstellung und Billigung',
         'topicId': T_BP3, 'voteIds': ['sr_20260928_02']},
        {'number': '5', 'title': '18. Änderung Flächennutzungsplan „Windkraft Lohberg“ – Vorstellung und weiteres Vorgehen',
         'type': 'discussion', 'note': 'Keine Beschlussfassung.'},
        {'number': '6', 'title': 'Antrag Bündnis 90/Die Grünen: Sichere Straßen für alle – digitale Schulwegpläne',
         'topicId': 't8', 'voteIds': ['sr_20260928_03'], 'press': ['merkur_2026-10-09_schulwegplaene']},
        {'number': '7', 'title': '27. Änderung des Regionalplans München – Beteiligung', 'voteIds': ['sr_20260928_04']},
        {'number': '8', 'title': 'Neuaufstellung des Flächennutzungsplans der Gemeinde Mauern – Beteiligung', 'voteIds': ['sr_20260928_05']},
        {'number': '9', 'title': 'Bündelausschreibungen für die Strom- und Gasbeschaffung ab 01.01.2028', 'topicId': 't26',
         'voteIds': [f'sr_20260928_{n:02d}' for n in range(6, 12)]},
        {'number': '10', 'title': 'Anfragen', 'type': 'formal'},
    ]

    # ── Dossiers ────────────────────────────────────────────────────────────
    by_t = {t['id']: t for t in topics}
    assert T_BP3 not in by_t
    topics.append(DOSSIER)
    by_t[T_BP3] = DOSSIER
    v = by_v['sr_20260420_06']
    kopf = {k: v[k] for k in ('id', 'sessionId')}
    rest = {k: x for k, x in v.items() if k not in ('id', 'sessionId', 'topicIds')}
    v.clear()
    v.update(kopf, topicIds=[T_BP3], **rest)
    for a in by_s['sr_20260420']['agenda']:
        if 'sr_20260420_06' in a.get('voteIds', []):
            a['topicId'] = T_BP3
            a['press'] = sorted(set(a.get('press', [])) | {'merkur_2026-04-28_neues-bauland-neustadt'})
    DOSSIER['history'] = [
        {'date': '2026-04-20', 'type': 'vote', 'title': 'Entwurf zur Kenntnis, 2. Änderung beschlossen',
         'text': 'Einstimmig: 2. Änderung im vereinfachten Verfahren auf Grundlage der Variante 3. Die Grünen wünschen mehr Grün und einen Spielplatz.',
         'sessionId': 'sr_20260420', 'voteId': 'sr_20260420_06', 'press': ['merkur_2026-04-28_neues-bauland-neustadt']},
        {'date': '2026-09-28', 'type': 'vote', 'title': 'Billigung und Auslegung',
         'text': 'Einstimmig (19:0): Der Entwurf vom 15.09.2026 geht in die öffentliche Auslegung.',
         'sessionId': 'sr_20260928', 'voteId': 'sr_20260928_02'},
    ]
    for h in by_t['t17']['history']:
        if h.get('voteId') == 'sr_20260615_09':
            h['title'] = 'Rathaus 3. BA – Grau für die Fassade'
            h['text'] = 'Nach einer Ortseinsicht mit Farbmustern lehnt der Stadtrat eine Vertagung ab (4:19) und wählt mit 12:11 den Grauton. Die knappste Abstimmung des Abends.'
    by_t['t8']['history'].append({
        'date': '2026-09-28', 'type': 'vote', 'title': 'Digitaler Schulwegplan auf Probe',
        'text': 'Mit 12:7 beschließt der Stadtrat, einen digitalen Schulwegplan ein Jahr lang zu testen.',
        'sessionId': 'sr_20260928', 'voteId': 'sr_20260928_03', 'press': ['merkur_2026-10-09_schulwegplaene']})
    by_t['t26']['history'].append({
        'date': '2026-09-28', 'type': 'vote', 'title': 'Ausschreibung ab 2028: Ökostrom ohne Neuanlagenquote',
        'text': 'Der Vorschlag mit Neuanlagenquote scheitert mit 6:12, einstimmig wird 100 % Ökostrom ohne Quote beschafft. Gas läuft weiter über enPORTAL.',
        'sessionId': 'sr_20260928', 'voteId': 'sr_20260928_08'})

    # ── Rechnungspruefungsausschuss seit 15.06.2026 ─────────────────────────
    rpa = next(b for b in bodies if b['id'] == 'rpa')
    for ort in [rpa, next(c for c in rpa['seatConfigs'] if c.get('from') == '2026-05-01')]:
        sitz = next(x for x in ort['seats'] if x['member'] == 'beibl')
        ort['chair'] = 'beibl'
        ort['chairSub'] = sitz['sub']
        ort['seats'] = [x for x in ort['seats'] if x['member'] != 'beibl']
        next(x for x in ort['seats'] if x['member'] == 'tristl')['role'] = 'Stellv. Vorsitzender'

    for n, obj in (('sessions.json', sessions), ('votes.json', votes), ('topics.json', topics),
                   ('press.json', press), ('bodies.json', bodies)):
        save(n, obj)


if __name__ == '__main__':
    main()
