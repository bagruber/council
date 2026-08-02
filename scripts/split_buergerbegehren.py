"""Loest das Sammel-Dossier "Buergerbegehren und Buergerentscheide" auf.

Die beiden Buergerbegehren haben inhaltlich nichts miteinander zu tun.
ACKERLAND IN BAUERNHAND ist das entscheidende Kapitel des Bebauungsplans
Nr. 70 "Containerbau ELA" — 46 Beschluesse zwischen 2020 und 2024, von denen
bisher nur die vier Buergerbegehren-Beschluesse einem Thema zugeordnet waren.
"Lebenswertes Moosburg" zielt dagegen auf kein einzelnes Vorhaben, sondern auf
die staedtebauliche Entwicklung insgesamt und bekommt ein eigenes Dossier.
"""
import json, os, re

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
ELA = re.compile(r'Containerbau ELA|ACKERLAND|Gewerbefl(ae|ä)chen Pfrombach', re.I)

T28 = {
    "id": "t28",
    "title": "Gewerbegebiet Pfrombach – Containerbau ELA",
    "field": "economy",
    "type": "konflikt",
    "status": "abgeschlossen",
    "tags": ["economy", "building", "environment"],
    "image": None,
    "summary": "Die Erweiterung der Firma ELA in Pfrombach zog sich über fünf Jahre und "
               "46 Beschlüsse. Zwischen Aufstellungsbeschluss und Satzungsbeschluss lag ein "
               "Bürgerbegehren, dessen Zielen der Stadtrat in namentlicher Abstimmung nicht "
               "folgte — und ein Bürgerentscheid, den er selbst ansetzte. Kaum ein anderes "
               "Verfahren zeigt die Lager im Rat so deutlich: bei den privaten Einwendungen "
               "steht es über zwanzig Abstimmungen hinweg immer wieder 14:8.",
    "history": [
        {"date": "2020-02-10", "type": "vote", "key": True,
         "title": "Aufstellungsbeschluss für den vorhabenbezogenen Bebauungsplan",
         "text": "Der Stadtrat beschließt die Aufstellung eines vorhabenbezogenen Bebauungsplans "
                 "nach § 12 BauGB für die Erweiterung der Firma ELA. Schon dieser erste Schritt "
                 "fällt mit 16:8 gegen eine große Minderheit.",
         "sessionId": "sr_20200210", "voteId": "sr_20200210_01"},
        {"date": "2020-02-10", "type": "vote",
         "title": "Streuobstwiese als Ausgleichsfläche",
         "text": "Einstimmig legt der Rat fest, dass die Streuobstwiese wesentlicher Bestandteil "
                 "der Ausgleichsfläche sein muss — die Untere Naturschutzbehörde ist entsprechend "
                 "zu beteiligen.",
         "sessionId": "sr_20200210", "voteId": "sr_20200210_04"},
        {"date": "2021-02-22", "type": "vote",
         "title": "37 Stellungnahmen abgewogen — die Bruchlinie wird sichtbar",
         "text": "Behörden und Träger öffentlicher Belange werden fast durchweg einstimmig "
                 "abgehandelt. Bei den privaten Einwendungen zu Flächenverbrauch, Verkehr und "
                 "Immissionsschutz kippt das Bild: dort steht es Abstimmung für Abstimmung "
                 "14:8, bei zwei Beschlüssen sogar 12:7.",
         "sessionId": "sr_20210222", "voteId": "sr_20210222_30"},
        {"date": "2021-08-09", "type": "milestone",
         "title": "Bürgerbegehren „ACKERLAND IN BAUERNHAND“ eingereicht",
         "text": "Unter dem Titel „keine Flächenversiegelung durch neue Gewerbeflächen“ wird ein "
                 "Bürgerbegehren gegen das Vorhaben eingereicht."},
        {"date": "2021-09-06", "type": "vote",
         "title": "Bürgerbegehren für zulässig erklärt",
         "text": "Der Stadtrat erklärt das Bürgerbegehren einstimmig formell für zulässig.",
         "sessionId": "sr_20210906", "voteId": "sr_20210906_02"},
        {"date": "2021-09-06", "type": "vote", "key": True,
         "title": "Namentliche Abstimmung: der Rat folgt den Zielen nicht",
         "text": "Der Antrag, den Zielen des Bürgerbegehrens zuzustimmen und die Planungen "
                 "einzustellen, wird namentlich abgestimmt und mit 10:12 abgelehnt. Es ist eine "
                 "der wenigen Abstimmungen dieser Wahlperiode, bei der die Niederschrift jeden "
                 "Namen nennt.",
         "sessionId": "sr_20210906", "voteId": "sr_20210906_03"},
        {"date": "2021-09-06", "type": "vote",
         "title": "Bürgerentscheid beschlossen",
         "text": "Einstimmig setzt der Rat den Bürgerentscheid an. Ein Antrag, ihn ausschließlich "
                 "als Briefwahl durchzuführen, scheitert anschließend mit 9:13.",
         "sessionId": "sr_20210906", "voteId": "sr_20210906_04"},
        {"date": "2021-10-11", "type": "vote",
         "title": "Termin und Stimmzettel festgelegt",
         "text": "Der Bürgerentscheid findet am 21. November 2021 statt. Die Fragestellung "
                 "entspricht dem Bürgerbegehren.",
         "sessionId": "sr_20211011", "voteId": "sr_20211011_01"},
        {"date": "2021-11-21", "type": "milestone",
         "title": "Bürgerentscheid „Gewerbeflächen Pfrombach“",
         "text": "Das Ergebnis ist in den vorliegenden Niederschriften nicht festgehalten. Der "
                 "Bebauungsplan wurde drei Jahre später als Satzung beschlossen."},
        {"date": "2024-12-09", "type": "vote", "key": True,
         "title": "Satzungsbeschluss",
         "text": "Nach 21 weiteren Einzelabstimmungen über Stellungnahmen beschließt der Stadtrat "
                 "den Bebauungsplan Nr. 70 als Satzung — mit 11:7 so knapp wie am Anfang.",
         "sessionId": "sr_20241209", "voteId": "sr_20241209_05"},
    ],
}

T29 = {
    "id": "t29",
    "title": "Bürgerbegehren „Lebenswertes Moosburg“",
    "field": "building",
    "type": "konflikt",
    "status": "abgeschlossen",
    "tags": ["building", "social"],
    "image": None,
    "summary": "Mehr als 1.500 Unterschriften gegen die Wachstumsgeschwindigkeit der Stadt: "
               "Baurecht, Zahl der Wohneinheiten, maximale Flächenversiegelung. Der Stadtrat "
               "bescheinigte dem Begehren die nötigen Unterschriften und erklärte es zugleich "
               "für materiell-rechtlich unzulässig.",
    "history": [
        {"date": "2020-10-02", "type": "milestone",
         "title": "Bürgerbegehren eingereicht",
         "text": "Mehr als 1.500 Moosburgerinnen und Moosburger unterschreiben für eine "
                 "maßvollere städtebauliche Entwicklung."},
        {"date": "2020-10-26", "type": "vote", "key": True,
         "title": "Formell erfüllt, materiell unzulässig",
         "text": "Der Stadtrat stellt fest, dass die erforderlichen Unterschriften vorliegen, "
                 "erklärt das Bürgerbegehren aber für materiell-rechtlich unzulässig.",
         "sessionId": "sr_20201026", "voteId": "sr_20201026_05"},
        {"date": "2020-10-26", "type": "vote",
         "title": "Anregungen zur Kenntnis genommen",
         "text": "Der Rat nimmt die Bedenken zu Verkehrsaufkommen und Infrastruktur ausdrücklich "
                 "ernst und behält sich vor, einzelne Punkte — Baurecht, Wohneinheiten, maximale "
                 "Flächenversiegelung — bei künftigen Bebauungsplänen zu berücksichtigen. Auch "
                 "die Stellplatzsatzung wird als überarbeitungsbedürftig benannt.",
         "sessionId": "sr_20201026", "voteId": "sr_20201026_06"},
    ],
}


def main():
    tp = os.path.join(DATA, 'topics.json')
    vp = os.path.join(DATA, 'votes.json')
    sp = os.path.join(DATA, 'sessions.json')
    topics = json.load(open(tp, encoding='utf-8'))
    votes = json.load(open(vp, encoding='utf-8'))
    sessions = json.load(open(sp, encoding='utf-8'))

    topics = [t for t in topics if t['id'] != 't27'] + [T28, T29]

    ela = {v['id'] for v in votes
           if ELA.search(v['title'] + ' ' + (v.get('text') or ''))}
    lm = {'sr_20201026_05', 'sr_20201026_06'}
    for v in votes:
        if v['id'] in ela:
            v['topicId'] = 't28'
        elif v['id'] in lm:
            v['topicId'] = 't29'
        elif v.get('topicId') == 't27':
            v['topicId'] = None

    for s in sessions:
        for a in s.get('agenda', []):
            if a.get('voteId') in ela:
                a['topicId'] = 't28'
            elif a.get('voteId') in lm:
                a['topicId'] = 't29'
            elif a.get('topicId') == 't27':
                a.pop('topicId')

    for path, obj in ((tp, topics), (vp, votes), (sp, sessions)):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.write('\n')

    print(f'  t28 ELA         {len(ela)} Abstimmungen')
    print(f'  t29 Lebenswert  {len(lm)} Abstimmungen')


if __name__ == '__main__':
    main()
