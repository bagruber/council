"""Arbeitet die BPU-Niederschrift vom 24.01.2022 ein.

Die Sitzung stand als Beschlussauszug im Register, ohne Anwesenheit und ohne die
Mehrfachbeschluesse zu 6.3, 6.4, 6.12 und 6.13. Die Vote-IDs bleiben, die acht
neuen Beschluesse bekommen _14 bis _21.

Einmal laufen lassen:
    python scripts/bpu_niederschrift_20220124.py
    python scripts/mark_inferable.py
"""
import json, os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
SID = 'bpu_20220124'
DA = ['dollinger', 'linz_karin', 'tristl', 'beubl', 'john', 'gruebl', 'kieninger', 'reif', 'beibl', 'altenbeck', 'stanglmaier']
FEHLT = ['hadersdorfer']
PRESSE = {'id': 'mz_2022-01-26_mehrfamilienhaeuser-abgelehnt', 'media': 'mz', 'date': '2022-01-26',
          'title': 'Mehrfamilienhäuser in Moosburg abgelehnt',
          'url': 'https://www.idowa.de/regionen/moosburg/mehrfamilienhaeuser-in-moosburg-abgelehnt-2172481.html'}
DEGERNPOINT = 't18'

# TOP -> Beschluesse: (Nummer, Titel, Text, Ja, Nein)
BESCHLUESSE = {
    '3': [(1, 'Nassabbau Semptwiesen II – Tektur zur Rekultivierung',
           'Die Stadt stimmt der beantragten Tektur im wasserrechtlichen Verfahren zu.', 11, 0)],
    '4.1': [(2, 'Westerbergstraße – Fahrradschutzstreifen stadtauswärts',
             'Auf Antrag der Frauen Union wird stadtauswärts ein einseitiger Fahrradschutzstreifen markiert, beginnend etwa 70 m nach der Einmündung Münchener Straße.', 10, 1)],
    '4.2': [(3, 'Westerbergstraße – Querungshilfe an der Münchener Straße',
             'Antrag der Frauen Union zur Kenntnis genommen. Die Verwaltung plant beim endgültigen Kreuzungsumbau eine optimale Lösung für den Querungsverkehr ein.', 11, 0)],
    '5': [(4, 'Unterreiterweg – Widmung als Ortsstraße',
           'Die Verlängerung auf Fl.-Nr. 977/128 wird auf 50 m Länge als Ortsstraße gewidmet.', 11, 0)],
    '6.1': [(5, 'MFH 7 WE Mainburger Str. 23 – Einvernehmen verweigert',
             'Anhörung wegen Ersetzung des gemeindlichen Einvernehmens. Das Vorhaben entspricht nicht dem Bebauungsplan, eine Befreiung ist bei Würdigung der nachbarlichen Interessen nicht möglich.', 11, 0)],
    '6.2': [(6, 'Vorbescheid EFH mit Einliegerwohnung Moosstr., Aich', 'Einvernehmen erteilt.', 11, 0)],
    '6.3': [(14, 'Vorbescheid MFH 6 WE Statzenbachstr. 8 – Einvernehmen erteilen', 'Antrag, das Einvernehmen zu erteilen.', 5, 6),
            (15, 'Vorbescheid MFH 6 WE Statzenbachstr. 8 – Einvernehmen verweigert',
             'Das Gebäude fügt sich in der Bauweise (Wandhöhe, Flachdach) nicht in die nähere Umgebung ein.', 6, 5)],
    '6.4': [(16, 'Fachmärkte Degernpoint M 2 – Getränkemarkt',
             'Einvernehmen zur Nutzung als Getränkemarkt mit höchstens 400 m² Verkaufsfläche, samt Befreiung vom Bebauungsplan in der Fassung der 3. Änderung.', 11, 0),
            (17, 'Fachmärkte Degernpoint M 2 – Außenlager',
             'Einvernehmen zum Außenlager, samt Befreiungen vom Bebauungsplan.', 11, 0)],
    '6.5': [(7, 'Aufstockung und Carport Holzlandstr. 22', 'Einvernehmen erteilt.', 11, 0)],
    '6.6': [(8, 'Lagerschuppen für Bienenhaltung, Neustadtstr.',
             'Einvernehmen zum Ersatzbau und zum Abbruch des bestehenden Schuppens erteilt.', 11, 0)],
    '6.7': [(9, 'Vorbescheid Erweiterung HNO-Praxis Münchener Str. 7',
             'Einvernehmen und Befreiungen erteilt. Vor der Baugenehmigung muss für die fehlenden Pkw- und Fahrradstellplätze ein Ablösevertrag geschlossen werden.', 11, 0)],
    '6.8': [(10, 'Vorbescheid Doppelhaus Münchener Str. 9 und 9a',
             'Einvernehmen und Befreiungen erteilt. Mit der Eingabeplanung ist ein qualifizierter Freiflächengestaltungsplan einzureichen.', 11, 0)],
    '6.9': [(11, 'Vorbescheid Überdachung Reitplatz Holzlandstr. 6 a', 'Einvernehmen erteilt.', 11, 0)],
    '6.10': [(12, 'Generationenwohnhaus Nandlstädter Str. 6', 'Einvernehmen und Befreiungen erteilt.', 11, 0)],
    '6.11': [(13, 'Pferdestall und Mitarbeiterwohnungen Amperstr. 24',
              'Einvernehmen zum Erweiterungsbau und zum Umbau von Lagerräumen in drei Mitarbeiterwohnungen erteilt.', 11, 0)],
    '6.12': [(18, 'Vorbescheid Hotel „Zur Länd“, Lände 1 – Variante 2',
              'Einvernehmen zur Erweiterung von Hotel, Restaurant und Wohnhaus in der Ausführung der Variante 2.', 6, 5),
             (19, 'Vorbescheid Hotel „Zur Länd“, Lände 1 – Variante 1', 'Antrag, das Einvernehmen für die Variante 1 zu erteilen.', 0, 11)],
    '6.13': [(20, 'Tektur Freiflächenplan MFH Gärtnerstr. 51 b – Einvernehmen erteilen', 'Antrag, das Einvernehmen zu erteilen.', 5, 6),
             (21, 'Tektur Freiflächenplan MFH Gärtnerstr. 51 b – Einvernehmen verweigert',
              'Das Maß der baulichen Nutzung (Grundflächenzahl) fügt sich nicht in die nähere Umgebung ein.', 9, 2)],
}


def load(n):
    return json.load(open(os.path.join(DATA, n), encoding='utf-8'))


def save(n, obj):
    with open(os.path.join(DATA, n), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def baue(top, nr, titel, text, ja, nein):
    v = {'id': f'{SID}_{nr:02d}', 'sessionId': SID}
    if top == '6.4':
        v['topicIds'] = [DEGERNPOINT]
    v.update(title=titel, text=text)
    einstimmig = ja + nein == len(DA) and (ja == 0 or nein == 0)
    v['type'] = 'named' if einstimmig else 'anonymous'
    assert ja + nein == len(DA), nr
    if ja < nein:
        v['result'] = 'rejected'
    if einstimmig:
        v['results'] = {'yes': list(DA) if ja else [], 'no': [] if ja else list(DA), 'absent': list(FEHLT)}
        v['source'] = {'tier': 'protocol-implicit'}
    else:
        v['results'] = {'yes': ja, 'no': nein, 'absent': len(FEHLT)}
        v['source'] = {'tier': 'result-only'}
    return v


def main():
    sessions = load('sessions.json')
    votes = load('votes.json')
    press = load('press.json')
    topics = load('topics.json')
    s = next(x for x in sessions if x['id'] == SID)
    assert s['niederschrift'] == 'auszug'
    assert PRESSE['id'] not in {p['id'] for p in press}
    press.append(PRESSE)

    neu = []
    for a in s['agenda']:
        a.pop('note', None)
        if a['number'] in ('4', '6'):
            a['type'] = 'formal'
        if a['number'] in BESCHLUESSE:
            eintraege = BESCHLUESSE[a['number']]
            neu += [baue(a['number'], *e) for e in eintraege]
            a['voteIds'] = [f'{SID}_{e[0]:02d}' for e in eintraege]
        if a['number'] == '6.1':
            a['press'] = [PRESSE['id']]
        if a['number'] == '6.4':
            a['topicId'] = DEGERNPOINT
    assert len(neu) == 21

    i = next(n for n, v in enumerate(votes) if v['sessionId'] == SID)
    votes[:] = [v for v in votes if v['sessionId'] != SID]
    votes[i:i] = neu

    s['niederschrift'] = 'vollständig'
    s.pop('source')
    s['location'] = 'Stadthalle Moosburg'
    s['absent'] = list(FEHLT)
    s['notes'] = ['Hadersdorfer und sein Stellvertreter Heinz waren entschuldigt.']
    reihe = ['id', 'date', 'type', 'niederschrift', 'veroeffentlicht', 'veroeffentlichtQuelle', 'genehmigt',
             'start', 'end', 'location', 'title', 'absent', 'notes', 'agenda']
    geordnet = {k: s[k] for k in reihe}
    s.clear()
    s.update(geordnet)

    t18 = next(t for t in topics if t['id'] == DEGERNPOINT)
    j = next(n for n, h in enumerate(t18['history']) if h['date'] > s['date'])
    t18['history'].insert(j, {
        'date': s['date'], 'type': 'vote', 'title': 'Fachmärkte Degernpoint M 2 – Getränkemarkt und Außenlager',
        'text': 'Einstimmig: Einvernehmen zum Getränkemarkt mit höchstens 400 m² Verkaufsfläche und zum Außenlager, samt Befreiungen vom Bebauungsplan.',
        'sessionId': SID, 'voteId': f'{SID}_16'})

    for n, obj in (('sessions.json', sessions), ('votes.json', votes), ('press.json', press), ('topics.json', topics)):
        save(n, obj)


if __name__ == '__main__':
    main()
