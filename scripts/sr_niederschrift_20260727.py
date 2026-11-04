"""Arbeitet die Niederschrift vom 27.07.2026 ein: Satzung, Geschaeftsordnung, Referate.

Die Einzelstimmen der geteilten Beschluesse stammen aus der Mitschrift des
Betreibers. In 29 von 33 Faellen stimmen beide Quellen ueberein. Bei Stalag und
Standesbeamter gilt die Niederschrift gegen die Mitschrift, weil ihr Vermerk
benennt, wer nicht mitstimmte. Zwei Zahlen der Niederschrift gehen nicht auf:

- Angleichung auf 45 EUR: gedruckt 6:18. Karin Linz war laut Mitschrift von 19:12
  bis 19:16 draussen, die Mitschrift zaehlt 5:18. Ihr wird kein Ja zugeschrieben.
- Moosburg Card freiwillig: gedruckt 19:9, das sind 28 Stimmen bei 24 Anwesenden.

Dazu das Dossier t37 ueber beide Wahlperioden und die neuen Referate.

Einmal laufen lassen:
    python scripts/sr_niederschrift_20260727.py
    python scripts/niederschrift_datum.py
    python scripts/mark_inferable.py
"""
import json, os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
SID = 'sr_20260727'
T = 't37'
TRACKED = {'tier': 'tracked', 'by': 'gruber', 'pressVerified': False}
AMTLICH = {'tier': 'protocol-implicit'}

VIERZEHN = ['dick', 'linz_kilian', 'marcus', 'marschoun', 'roeck', 'ruemelin', 'sabanovic', 'stanglmaier', 'strobl']
ZEHN = ['dick', 'ghadieh', 'linz_kilian', 'marcus', 'marschoun', 'roeck', 'ruemelin', 'sabanovic', 'stanglmaier', 'strobl']
FUENFZEHN = ['dick', 'ghadieh', 'linz_kilian', 'roeck', 'ruemelin', 'sabanovic', 'stanglmaier', 'strobl', 'welter']

# Nummer, Titel, Text, Ja, Nein, Minderheit (Seite und Namen), Ohne, Dossier, Zusatz
EINTRAEGE = [
    (1, 'Ersatzbeschaffung LF10 für die Feuerwehr',
     'Die Stadt beschafft ein neues LF10 für die Freiwillige Feuerwehr Moosburg. Die Verwaltung schreibt es gemeinsam mit einem Ingenieurbüro aus.',
     23, 0, None, ['grundner'], False, {}),
    (2, 'Entschädigung – gestaffeltes Sitzungsgeld (Antrag Fresh)',
     'Statt 45 € je Sitzung: eine Grundpauschale bis zwei Stunden und ein Zuschlag für jede weitere angefangene halbe Stunde.',
     3, 21, ('ja', ['dick', 'marcus', 'sabanovic']), [], True, {}),
    (3, 'Entschädigung – Dynamisierung (Antrag Fresh)',
     'Pauschalen, Sitzungsgeld, Fraktionsgelder und Entschädigungen steigen zum 01.05.2029 um die bis dahin festgelegten Erhöhungen der Dienstaufwandsentschädigung nach Art. 46 Abs. 3 KWBG.',
     18, 6, ('nein', ['ghadieh', 'grundner', 'lauterbach', 'meier', 'sixt', 'welter']), [], True, {}),
    (4, 'Entschädigung – Angleichung auf 45 € (Antrag Fresh)',
     'Referenten und Beauftragte bekommen einheitlich 45 €.',
     5, 18, ('ja', ['dick', 'linz_kilian', 'roeck', 'ruemelin', 'sabanovic']), ['linz_karin'], True,
     {'excluded': [{'member': 'linz_karin', 'reason': 'kurz_abwesend'}],
      'note': 'Die Niederschrift druckt 6:18. Karin Linz war in diesem Moment laut Mitschrift kurz draußen; vermutlich wurde das beim Zählen übersehen. Am Ergebnis ändert es nichts.'}),
    (5, 'Entschädigung – Angleichung auf 90 € (Antrag Marschoun)',
     'Referenten und Beauftragte bekommen einheitlich 90 €.',
     9, 15, ('ja', VIERZEHN), [], True, {}),
    (6, 'Entschädigung – keine Moosburg Card (Antrag Strobl)',
     'Die monatliche Pauschale wird nicht in Moosburg Card und Auszahlung geteilt.',
     1, 23, ('ja', ['strobl']), [], True, {}),
    (7, 'Entschädigung – Moosburg Card freiwillig (Antrag Rümelin)',
     'Die Pauschale wird nur mit Zustimmung des jeweiligen Mitglieds geteilt: 50 € Moosburg Card, 75 € Auszahlung.',
     16, 8, ('nein', ['ghadieh', 'haberl', 'hadersdorfer', 'lauterbach', 'marcus', 'marschoun', 'reither', 'welter']), [], True,
     {'note': 'Die Niederschrift druckt 19:9, das wären 28 Stimmen bei 24 Anwesenden. Hier steht die Zählung aus der Mitschrift. Beschlossen ist der Antrag in beiden Fassungen.'}),
    (8, 'Höhe der Aufwandsentschädigungen',
     'Im Monat 125 € Pauschale, 90 € für Referenten, 45 € für Beauftragte, 15 € Technikpauschale; 45 € Sitzungsgeld. Fraktionen: 70 € je Mitglied im Jahr, Vorsitz 40 € im Monat plus 5 € je Mitglied. Ortssprecher: 75 € im Monat und 45 € je Stadtratssitzung.',
     23, 1, ('nein', ['ghadieh']), [], True, {}),
    (9, 'Satzung zum Gemeindeverfassungsrecht erlassen',
     'Die „Satzung zur Regelung von Fragen des örtlichen Gemeindeverfassungsrechtes“ wird mit den beschlossenen Änderungen erlassen.',
     22, 2, ('nein', ['ghadieh', 'welter']), [], True, {}),
    (10, 'Geschäftsordnung – namentlich über die namentliche Abstimmung',
     'Über den Änderungsvorschlag „Namentliche Abstimmung“ wird namentlich abgestimmt.',
     11, 13, ('ja', ['dick', 'ghadieh', 'kehlringer', 'linz_kilian', 'marcus', 'roeck', 'ruemelin', 'sabanovic', 'stanglmaier', 'strobl', 'welter']), [], True, {}),
    (11, 'Geschäftsordnung – Live-Stream und Mediathek (Antrag Fresh)',
     '§ 21: Öffentliche Sitzungen werden als Audio live übertragen und sechs Wochen zum Abruf bereitgestellt, oder bis zum Ende der nächsten Sitzung, falls sie später stattfindet. Wer teilnimmt, muss freiwillig einwilligen.',
     9, 15, ('ja', ['dick', 'kehlringer', 'linz_kilian', 'marcus', 'roeck', 'ruemelin', 'sabanovic', 'stanglmaier', 'strobl']), [], True, {}),
    (12, 'Geschäftsordnung – Themenbeauftragte (Antrag Fresh)',
     '§ 3: Der Stadtrat kann Beauftragte bestimmen, die ihm nicht angehören müssen, etwa für Wirtschaft, Integration, Stalag und Städtepartnerschaften. Die Posten werden öffentlich ausgeschrieben.',
     8, 16, ('ja', ['dick', 'linz_kilian', 'marcus', 'roeck', 'ruemelin', 'sabanovic', 'stanglmaier', 'strobl']), [], True, {}),
    (13, 'Geschäftsordnung – namentliche Abstimmung (Antrag Fresh)',
     '§ 30 Abs. 6: Ist ein Beschluss nicht einstimmig, hält die Niederschrift fest, wer mit Ja und wer mit Nein gestimmt hat.',
     9, 15, ('ja', FUENFZEHN), [], True, {}),
    (14, 'Geschäftsordnung – Veröffentlichung der Niederschriften vertagt (Antrag Heinz)',
     'Die Entscheidung wird vertagt. Die Verwaltung prüft, welche Inhalte der Niederschrift veröffentlicht werden können und in welchem Umfang die Sitzungsunterlagen den Bürgerinnen und Bürgern zugänglich gemacht werden können.',
     24, 0, None, [], True, {}),
    (15, 'Geschäftsordnung – Digitalisierungsreferent (Antrag Marcus)',
     'Die Funktion des Digitalisierungsreferenten kommt in die Geschäftsordnung.',
     9, 15, ('ja', VIERZEHN), [], True, {}),
    (16, 'Geschäftsordnung – sechs Referate',
     'In die Geschäftsordnung kommen: Energie, Mobilität und Umwelt; Verein und Sport; Kultur; Senioren und Soziales einschließlich Inklusion; Schulen und Kindertageseinrichtungen; Jugend.',
     24, 0, None, [], True, {}),
    (17, 'Geschäftsordnung – Einzelabstimmung über die Beauftragten (Antrag Rümelin)',
     'Über die Aufnahme jedes Beauftragten wird einzeln abgestimmt.',
     9, 15, ('ja', ['dick', 'ghadieh', 'linz_kilian', 'marcus', 'roeck', 'ruemelin', 'sabanovic', 'stanglmaier', 'strobl']), [], True, {}),
    (18, 'Geschäftsordnung – vier Beauftragte',
     'Wirtschaft, Migration und Integration, Stalag, Städtepartnerschaften.',
     10, 14, ('ja', ZEHN), [], True, {}),
    (19, 'Geschäftsordnung – drei Beauftragte',
     'Wirtschaft, Migration und Integration, Stalag.',
     10, 14, ('ja', ZEHN), [], True, {}),
    (20, 'Geschäftsordnung – zwei Beauftragte',
     'Wirtschaft und Stalag.',
     22, 2, ('nein', ['ghadieh', 'sabanovic']), [], True, {}),
    (21, 'Geschäftsordnung – Ordnungsgeld',
     'Der neue § 29 führt ein Ordnungsgeld mit den angegebenen Höchstsätzen ein.',
     17, 7, ('nein', ['dick', 'ghadieh', 'sabanovic', 'sixt', 'stanglmaier', 'tristl', 'welter']), [], True, {}),
    (22, 'Geschäftsordnung – Einleitung (Antrag Dick)',
     'Neuer einleitender Satz: „Alle personenbezogenen Bezeichnungen gelten für alle Mitglieder des Stadtrates unabhängig von deren Geschlecht“.',
     23, 1, ('nein', ['ghadieh']), [], True, {}),
    (23, 'Geschäftsordnung – Verhaltenskodex vertagt (Antrag Reither)',
     'Die Entscheidung über einen Verhaltenskodex als Anlage zur Geschäftsordnung wird vertagt.',
     24, 0, None, [], True, {}),
    (24, 'Neue Geschäftsordnung beschlossen',
     'Der Stadtrat beschließt die Geschäftsordnung mit den in der Sitzung beschlossenen Änderungen.',
     24, 0, None, [], True, {}),
    (25, 'Besetzung der sechs Referate (Sammelvote)',
     'Sechs Beschlüsse, jeweils 23:0: Dr. Michael Stanglmaier (Energie, Mobilität, Umwelt), Josef Sixt (Verein, Sport), Matthias Röck (Kultur), Karin Linz (Senioren, Soziales, Inklusion), Lorena Kehlringer (Schulen, Kindertageseinrichtungen), Johanna Dick (Jugend).',
     23, 0, None, ['tristl'], False, {'excluded': [{'member': 'tristl', 'reason': 'kurz_abwesend'}]}),
    (26, 'Beauftragter für Stalag',
     'Dr. Dominik Reither wird Beauftragter für Stalag.',
     21, 0, None, ['tristl', 'schweiger', 'sabanovic'], False,
     {'excluded': [{'member': m, 'reason': 'kurz_abwesend'} for m in ('tristl', 'schweiger', 'sabanovic')]}),
    (27, 'Erster Bürgermeister wird Eheschließungsstandesbeamter',
     'Maximilian Mader wird Standesbeamter für den Standesamtsbezirk Moosburg, beschränkt auf Eheschließungen.',
     21, 0, None, ['tristl', 'sabanovic', 'mader'], False,
     {'excluded': [{'member': 'tristl', 'reason': 'kurz_abwesend'}, {'member': 'sabanovic', 'reason': 'kurz_abwesend'},
                   {'member': 'mader', 'reason': 'beteiligung'}]}),
    (28, 'Gigabitförderung 2.0 – weiteres Verfahren',
     'Der Stadtrat nimmt die Präsentation zur Kenntnis und beschließt die weiteren Verfahrensschritte. Wird der Infrastruktur-Förderantrag bewilligt, plant er den Eigenanteil von voraussichtlich 550.000 € im Haushalt ein.',
     23, 0, None, ['lauterbach'], False, {}),
]

AGENDA = [
    {'number': '1', 'title': 'Mitteilungen des Ersten Bürgermeisters', 'type': 'formal'},
    {'number': '2', 'title': 'Bürgerfragen gem. § 27 Abs. 2 GeschO/StR', 'type': 'formal'},
    {'number': '3', 'title': 'Beschluss zur Ersatzbeschaffung eines LF10 für die Freiwillige Feuerwehr Moosburg', 'voteIds': [f'{SID}_01']},
    {'number': '4', 'title': 'Stadtratsangelegenheiten', 'type': 'formal'},
    {'number': '4.1', 'title': 'Erlass der Satzung zur Regelung von Fragen des örtlichen Gemeindeverfassungsrechtes', 'topicId': T,
     'voteIds': [f'{SID}_{n:02d}' for n in range(2, 10)]},
    {'number': '4.2', 'title': 'Erlass der Geschäftsordnung für den Stadtrat der Stadt Moosburg a.d. Isar', 'topicId': T,
     'voteIds': [f'{SID}_{n:02d}' for n in range(10, 25)]},
    {'number': '4.3', 'title': 'Besetzung der Referenten- und Beauftragtenposten', 'voteIds': [f'{SID}_25', f'{SID}_26']},
    {'number': '5', 'title': 'Bestellung des Ersten Bürgermeisters als Eheschließungsstandesbeamter', 'voteIds': [f'{SID}_27']},
    {'number': '6', 'title': 'Gigabitförderung 2.0 – Vorstellung Ergebnis Markterkundung und Beschluss zum weiteren Verfahren', 'voteIds': [f'{SID}_28']},
    {'number': '7', 'title': 'Anfragen', 'type': 'formal'},
]

PARTIAL = [
    {'member': 'grundner', 'from': '19:10'},
    {'member': 'lauterbach', 'to': '21:00'},
    {'member': 'heinz', 'to': '21:30'},
    {'member': 'strobl', 'to': '22:00'},
    {'member': 'haberl', 'to': '22:20'},
]

# Aeltere Beschluesse, die ins Dossier wandern
FRUEHER = ['sr_20200504_11', 'sr_20200706_03', 'sr_20200706_04', 'sr_20200706_05', 'sr_20200706_06',
           'sr_20200706_11', 'sr_20200706_12', 'sr_20240201_04', 'sr_20241021_05', 'sr_20260325_06',
           'sr_20260511_14', 'sr_20260615_06', 'sr_20260615_07']

# Im Dossier taugt „Stadtratsangelegenheiten“ als Titel nicht
UMBENANNT = {
    'sr_20200706_03': ('Neue Geschäftsordnung',
                       'Der Stadtrat beschließt die Geschäftsordnung in der vorliegenden Fassung mit den in der Sitzung beschlossenen Änderungen.'),
    'sr_20200706_04': ('Entschädigung – 102,50 € Pauschale (Antrag Pschorr)',
                       'Die monatliche Pauschale beträgt 102,50 € statt 110 €, alles Übrige wie im Beschluss zur Höhe der Aufwandsentschädigungen.'),
    'sr_20200706_05': ('Höhe der Aufwandsentschädigungen',
                       'Im Monat 110 € Pauschale, 80 € für Referenten, 5 € Technikpauschale; 40 € Sitzungsgeld. Fraktionen: 70 € je Mitglied im Jahr, Vorsitz 40 € im Monat plus 5 € je Mitglied. Ortssprecher: 70 € im Monat und 40 € je Stadtratssitzung.'),
    'sr_20200706_06': ('Satzung zum Gemeindeverfassungsrecht erlassen',
                       'Die „Satzung zur Regelung von Fragen des örtlichen Gemeindeverfassungsrechtes“ wird mit den beschlossenen Änderungen erlassen.'),
}


def schritt(datum, titel, text, sid, vote):
    return {'date': datum, 'type': 'vote', 'title': titel, 'text': text, 'sessionId': sid, 'voteId': vote}


DOSSIER = {
    'id': T, 'title': 'Geschäftsordnung und Entschädigung', 'tags': ['budget'], 'image': None,
    'summary': 'Wie der Stadtrat arbeitet und was seine Mitglieder dafür bekommen. Zu Beginn einer Wahlperiode beschließt er es neu, zuletzt im Juli 2020 und im Juli 2026: die Geschäftsordnung, die Satzung mit den Aufwandsentschädigungen und die Entschädigung der Bürgermeister.',
    'field': 'budget', 'type': 'zyklus',
    'history': [
        schritt('2020-05-04', 'Alte Geschäftsordnung gilt vorerst weiter',
                'Einstimmig: Die Geschäftsordnung von 2015 bleibt, bis eine neue beschlossen ist.', 'sr_20200504', 'sr_20200504_11'),
        schritt('2020-07-06', 'Neue Geschäftsordnung', 'Einstimmig beschlossen (24:0).', 'sr_20200706', 'sr_20200706_03'),
        schritt('2020-07-06', 'Entschädigung: 110 € Pauschale, 40 € Sitzungsgeld',
                'Ein Änderungsantrag von StR Pschorr für 102,50 € scheitert mit 3:21, beschlossen werden 110 € im Monat und 40 € je Sitzung (22:2).',
                'sr_20200706', 'sr_20200706_05'),
        schritt('2020-07-06', 'Entschädigung der Bürgermeister',
                'Der Erste Bürgermeister bekommt den Höchstbetrag nach KWBG (23:0), Zweiter und Dritter bleiben bei 1.161,31 € und 466,98 € (21:0).',
                'sr_20200706', 'sr_20200706_12'),
        schritt('2024-02-01', 'Ersatzleistungen für ehrenamtliche Stadträte',
                'Die Satzung wird rückwirkend zum 01.01.2024 geändert (19:1).', 'sr_20240201', 'sr_20240201_04'),
        schritt('2024-10-21', 'Entschädigung für den Jugendreferenten',
                'Einstimmig: eine monatliche Entschädigung in Höhe der Referentenpauschale.', 'sr_20241021', 'sr_20241021_05'),
        schritt('2026-03-25', '1. Änderung der Geschäftsordnung: „Bauturbo“',
                'Die Änderung regelt die Zustimmung der Gemeinde nach § 36a BauGB (17:4).', 'sr_20260325', 'sr_20260325_06'),
        schritt('2026-05-11', 'Geschäftsordnung gilt vorerst weiter',
                'Einstimmig: Die Geschäftsordnung von 2020 bleibt, bis eine neue beschlossen ist.', 'sr_20260511', 'sr_20260511_14'),
        schritt('2026-06-15', 'Entschädigung der Bürgermeister',
                'Der Erste Bürgermeister bekommt 878,10 € im Monat (21:2), Zweiter und Dritter bleiben bei 1.337,91 € und 538,00 € (21:1).',
                'sr_20260615', 'sr_20260615_06'),
        schritt('2026-07-27', 'Entschädigung: 125 € Pauschale, 45 € Sitzungsgeld',
                'Mit 23:1 beschlossen, die Satzung mit 22:2. Die Moosburg Card wird freiwillig. Fresh scheitert mit dem gestaffelten Sitzungsgeld, setzt aber die Dynamisierung ab 2029 durch (18:6).',
                SID, f'{SID}_08'),
        schritt('2026-07-27', 'Live-Stream abgelehnt',
                'Fresh beantragt, öffentliche Sitzungen als Audio live zu übertragen und danach eine Zeit lang abrufbar zu halten. Abgelehnt mit 9:15.',
                SID, f'{SID}_11'),
        schritt('2026-07-27', 'Namentliche Abstimmung abgelehnt',
                'Fresh beantragt, dass die Niederschrift bei nicht einstimmigen Beschlüssen festhält, wer wie gestimmt hat. Abgelehnt mit 9:15, schon die namentliche Abstimmung darüber scheitert mit 11:13.',
                SID, f'{SID}_13'),
        schritt('2026-07-27', 'Veröffentlichung der Niederschriften vertagt',
                'Einstimmig auf Antrag von StR Heinz: Die Verwaltung prüft, welche Inhalte der Niederschrift veröffentlicht und wie weit die Sitzungsunterlagen zugänglich gemacht werden können.',
                SID, f'{SID}_14'),
        schritt('2026-07-27', 'Ordnungsgeld eingeführt', 'Der neue § 29 führt ein Ordnungsgeld ein (17:7).', SID, f'{SID}_21'),
        schritt('2026-07-27', 'Neue Geschäftsordnung',
                'Einstimmig beschlossen, mit den Änderungen des Abends. Sechs Referate und zwei Beauftragte kommen hinein, ein Digitalisierungsreferent nicht (9:15). Der Verhaltenskodex wird vertagt.',
                SID, f'{SID}_24'),
    ],
}

# (Mitglied, Titel fuer Profil und Kopf)
NEUE_TITEL = [
    ('stanglmaier', 'Energie-, Mobilitäts- und Umweltreferent'),
    ('sixt', 'Vereins- und Sportreferent'),
    ('roeck', 'Kulturreferent'),
    ('linz_karin', 'Senioren- und Sozialreferentin'),
    ('kehlringer', 'Referentin für Schulen und Kindertageseinrichtungen'),
    ('dick', 'Jugendreferentin'),
    ('reither', 'Beauftragter für Stalag'),
]
# Enden wie die uebrigen Referate der alten Periode
ALTE_TITEL = [('heinz', 'Kulturreferent'), ('beibl', 'Sportreferentin'), ('hadersdorfer', 'Ehrenamtsreferent')]


def load(n):
    return json.load(open(os.path.join(DATA, n), encoding='utf-8'))


def save(n, obj):
    with open(os.path.join(DATA, n), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    members = load('members.json')
    sessions = load('sessions.json')
    votes = load('votes.json')
    topics = load('topics.json')
    by_s = {s['id']: s for s in sessions}
    by_v = {v['id']: v for v in votes}
    by_m = {m['id']: m for m in members}
    assert T not in {t['id'] for t in topics}

    s = by_s[SID]
    assert s['niederschrift'] == 'keine'
    rat = [m['id'] for m in members
           if any((a.get('from') or '0') <= s['date'] <= (a.get('to') or '9999') for a in m['mandates'])]
    assert len(rat) == 25
    fehlt = ['beibl']

    neue = []
    for nr, titel, text, ja, nein, minderheit, ohne, im_dossier, zusatz in EINTRAEGE:
        da = [m for m in rat if m not in fehlt and m not in ohne]
        if minderheit:
            seite, namen = minderheit
            assert set(namen) <= set(da), (nr, set(namen) - set(da))
            rest = [m for m in da if m not in namen]
            yes, no = (namen, rest) if seite == 'ja' else (rest, namen)
        else:
            yes, no = da, []
        assert (len(yes), len(no)) == (ja, nein), (nr, len(yes), len(no))
        v = {'id': f'{SID}_{nr:02d}', 'sessionId': SID}
        if im_dossier:
            v['topicIds'] = [T]
        v.update(title=titel, text=text, type='named')
        if ja < nein:
            v['result'] = 'rejected'
        v['results'] = {'yes': yes, 'no': no, 'absent': [m for m in rat if m not in da]}
        v['source'] = dict(TRACKED if minderheit else AMTLICH)
        v.update(zusatz)
        neue.append(v)

    datum_von = {x['id']: x['date'] for x in sessions}
    i = next((n for n, v in enumerate(votes) if datum_von.get(v['sessionId'], '') > s['date']), len(votes))
    votes[i:i] = neue

    s['niederschrift'] = 'vollständig'
    s['title'] = '11. Stadtratssitzung – Juli 2026'
    s['absent'] = fehlt
    s['partial'] = PARTIAL
    s['agenda'] = AGENDA

    topics.append(DOSSIER)
    for vid in FRUEHER:
        v = by_v[vid]
        assert not v.get('topicIds'), vid
        kopf = {k: v[k] for k in ('id', 'sessionId')}
        rest = {k: x for k, x in v.items() if k not in ('id', 'sessionId')}
        v.clear()
        v.update(kopf, topicIds=[T], **rest)
        if vid in UMBENANNT:
            v['title'], v['text'] = UMBENANNT[vid]
        for a in by_s[v['sessionId']]['agenda']:
            if vid in a.get('voteIds', []) and not a.get('topicId'):
                a['topicId'] = T

    for mid, titel in ALTE_TITEL:
        m = by_m[mid]
        eintrag = next(t for t in m['profile']['titles'] if t['title'] == titel)
        assert eintrag['to'] is None
        eintrag['to'] = '2026-05'
        if m.get('title') == titel:
            del m['title']

    for mid, titel in NEUE_TITEL:
        m = by_m[mid]
        if 'title' not in m:
            kopf = {k: m[k] for k in ('id', 'firstName', 'lastName')}
            rest = {k: x for k, x in m.items() if k not in kopf}
            m.clear()
            m.update(kopf, title=titel, **rest)
        p = m['profile']
        if 'titles' not in p:
            rest = {k: p.pop(k) for k in list(p) if k != 'pronouns'}
            p['titles'] = []
            p.update(rest)
        p['titles'].append({'title': titel, 'from': s['date'], 'to': None})

    for n, obj in (('sessions.json', sessions), ('votes.json', votes), ('topics.json', topics), ('members.json', members)):
        save(n, obj)


if __name__ == '__main__':
    main()
