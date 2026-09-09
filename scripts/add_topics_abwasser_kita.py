"""Legt die Dossiers t30 (Abwasser) und t31 (Kinderbetreuung) an.

Beide sind bewusst breit geschnitten. Die Klaeranlage ist eine staedtische
Liegenschaft, die den Rat seit 2020 in vier Rollen beschaeftigt: als
Gesellschaft (Satzung, Aufsichtsrat), als Rechnungswerk (Jahresabschluss,
Entlastung), als Gebuehrenschuldner (Kalkulation, Entwaesserungssatzung) und
als Bauwerk (Kanal, Absperrbauwerk). Vierundvierzig Beschluesse verteilten sich
bisher auf kein Dossier -- und die Entlastung des Aufsichtsrats erklaert
nebenbei eine ganze Klasse von Abstimmungsluecken, weil dessen Mitglieder ueber
die eigene Entlastung nicht mitstimmen.

Kinderbetreuung genauso: Bau, Personal, Gebuehren gehoeren zusammen. Wer wissen
will, wie die Stadt es mit ihren Kitas haelt, will nicht drei Suchen machen.

Nicht aufgenommen sind Sammelvoten, die das Thema nur streifen -- die
Haushaltssatzungen, die Ausschussbesetzungen, in denen der Aufsichtsrat neben
sechs anderen Gremien steht, und Bauantraege, deren Adresse zufaellig "Am
Kanal" heisst.

Zwei Voten wechseln das Dossier: der Klaeranlagen-Jahresabschluss 2022 samt
Entlastung stand unter t7 (Haushalt), die Kreditermaechtigung fuer die Kita
Sonnensiedlung ebenfalls. Beide sind vom Gegenstand her hier richtiger; der
Haushalt behaelt, was den Haushalt als Ganzes betrifft.
"""
import json, os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

ABWASSER = [
    'sr_20200504_07', 'sr_20200504_09', 'sr_20200504_10', 'sr_20200706_10',
    'sr_20200722_01', 'sr_20200722_02',
    'sr_20210726_02', 'sr_20210726_03',
    'sr_20211213_02', 'sr_20211213_03', 'sr_20211213_04', 'sr_20211213_05', 'sr_20211213_06',
    'sr_20221121_03',
    'sr_20230724_03', 'sr_20230724_04',
    'sr_20240701_02', 'sr_20240701_03',
    'sr_20241118_05',
    'sr_20250324_05',
    'sr_20250728_04', 'sr_20250728_05',
    'sr_20250922_01', 'sr_20250922_03', 'sr_20250922_05',
    'sr_20251110_02', 'sr_20251110_06',
    'bpu_20251208_01',
    'sr_20260511_11', 'sr_20260511_13',
    'sr_20260720_06',
]

KITA = [
    'sr_20200525_02', 'sr_20200525_03',
    'sr_20200914_03',
    'sr_20210906_05',
    'sr_20211206_01', 'sr_20211206_06',
    'sr_20220905_07',
    'sr_20221219_04',
    'sr_20230612_02',
    'sr_20231218_02',
    'sr_20240610_02', 'sr_20240610_03', 'sr_20240610_04', 'sr_20240610_07',
    'bpu_20240715_03',
    'sr_20241209_08',
    'sr_20260720_07', 'sr_20260720_08', 'sr_20260720_09',
]

T30 = {
    'id': 't30',
    'title': 'Kläranlage und Abwasser',
    'tags': ['infrastructure', 'environment'],
    'image': None,
    'summary': 'Die Kläranlage Moosburg GmbH gehört der Stadt, und der Stadtrat ist ihr '
               'Gesellschafter, ihr Rechnungsprüfer und der Gesetzgeber ihrer Gebühren in '
               'einem. Das Dossier führt alles zusammen, was am Abwasser hängt: die '
               'Gesellschaftssatzung und den Aufsichtsrat, die jährlichen Jahresabschlüsse '
               'und Entlastungen, die Gebührenkalkulation und die Entwässerungssatzung, dazu '
               'das Kanalnetz selbst. Bei der Entlastung des Aufsichtsrats stimmen dessen '
               'Mitglieder nicht mit — deshalb gehen dort die Zahlen nicht auf.',
    'history': [
        {'date': '2020-05-04', 'type': 'committee',
         'title': 'Aufsichtsrat neu besetzt, Satzung geändert',
         'text': 'Die konstituierende Sitzung legt den Aufsichtsrat auf den Ersten '
                 'Bürgermeister und sieben Stadtratsmitglieder fest und besetzt ihn.',
         'sessionId': 'sr_20200504', 'voteId': 'sr_20200504_09'},
        {'date': '2020-07-06', 'type': 'milestone',
         'title': 'Neufassung der Gesellschaftssatzung',
         'text': 'Der Stadtrat beschließt die Gesellschaftssatzung der Kläranlage Moosburg '
                 'GmbH neu.',
         'sessionId': 'sr_20200706', 'voteId': 'sr_20200706_10'},
        {'date': '2021-12-13', 'type': 'vote',
         'title': 'Gebührenkalkulation 2022–2025 und neue Entwässerungssatzung',
         'text': 'Fünf Beschlüsse an einem Abend: die Abwassergebühren für vier Jahre und '
                 'der Neuerlass der Entwässerungssatzung samt Beitrags- und Gebührensatzung.',
         'sessionId': 'sr_20211213', 'voteId': 'sr_20211213_05'},
        {'date': '2024-11-18', 'type': 'milestone',
         'title': 'Satzungsänderung: Nachhaltigkeitsbericht',
         'text': 'Die Gesellschaftssatzung wird um den Nachhaltigkeitsbericht ergänzt.',
         'sessionId': 'sr_20241118', 'voteId': 'sr_20241118_05'},
        {'date': '2025-09-22', 'type': 'vote',
         'title': 'Gebührensatz 2026–2029 und neue Benutzungsordnung',
         'text': 'Der Gebührensatz für die Abwasserentsorgung wird für vier Jahre '
                 'festgelegt, der Zinssatz auf 3 % gesetzt und die '
                 'Kläranlagenbenutzungsordnung neu erlassen.',
         'sessionId': 'sr_20250922', 'voteId': 'sr_20250922_03'},
        {'date': '2026-05-11', 'type': 'committee',
         'title': 'Aufsichtsrat der neuen Wahlperiode',
         'text': 'Der neue Stadtrat legt Größe und Besetzung des Aufsichtsrats fest.',
         'sessionId': 'sr_20260511', 'voteId': 'sr_20260511_13'},
        {'date': '2026-07-20', 'type': 'vote',
         'title': 'Jahresabschluss 2025',
         'text': 'Jahresüberschuss 187.840,76 €, zusammen mit dem Vortrag 2.333.922,21 € '
                 'auf neue Rechnung. Einstimmig.',
         'sessionId': 'sr_20260720', 'voteId': 'sr_20260720_06'},
    ],
    'field': 'infrastructure',
    'type': 'vorhaben',
    'status': 'laufend',
}

T31 = {
    'id': 't31',
    'title': 'Kinderbetreuung',
    'tags': ['education', 'social'],
    'image': None,
    'summary': 'Kitas, Krippen und Kindergärten von drei Seiten: was gebaut wird, wer dort '
               'arbeitet und was die Betreuung kostet. Seit 2020 hat der Rat einen '
               'Waldkindergarten aufgestellt, zwei Krippen in Auftrag gegeben und dafür '
               'Kredite bewilligt, eine Arbeitsmarktzulage für Erzieher und Kinderpfleger '
               'eingeführt und zweimal über ihre Höhe gestritten — und die '
               'Kindergartengebühren erhöht.',
    'history': [
        {'date': '2020-05-25', 'type': 'vote',
         'title': 'Waldkindergarten für 40 Kinder',
         'text': 'Standort festgelegt und Mittel bereitgestellt; der Neubau erfolgt mit '
                 'vorgefertigten Einrichtungen.',
         'sessionId': 'sr_20200525', 'voteId': 'sr_20200525_03'},
        {'date': '2021-12-06', 'type': 'vote',
         'title': 'Kinderkrippe in städtischer Trägerschaft',
         'text': 'Die Stadt errichtet selbst eine Kindertageseinrichtung. Am selben Abend '
                 'wird eine Fachbereichsleitung für Kindergarten, Hort und Krippe gefordert.',
         'sessionId': 'sr_20211206', 'voteId': 'sr_20211206_01'},
        {'date': '2023-06-12', 'type': 'vote',
         'title': 'Kita Sonnensiedlung – drei Gruppen mit Wohnungen darüber',
         'text': 'Dreigruppige Kita mit fünf Wohnungen im Obergeschoss.',
         'sessionId': 'sr_20230612', 'voteId': 'sr_20230612_02'},
        {'date': '2024-06-10', 'type': 'vote',
         'title': 'Arbeitsmarktzulage eingeführt, Gebühren erhöht',
         'text': 'Zulage für Erzieher und Kinderpfleger, ein Zuschuss dafür auch an freie '
                 'Träger — und im selben Zug 30 € mehr Kindergartengebühr.',
         'sessionId': 'sr_20240610', 'voteId': 'sr_20240610_02'},
        {'date': '2024-12-09', 'type': 'milestone',
         'title': 'Kredit für die Krippe Sonnensiedlung',
         'text': 'Die Kreditaufnahme für den Bau wird beschlossen.',
         'sessionId': 'sr_20241209', 'voteId': 'sr_20241209_08'},
        {'date': '2026-07-20', 'type': 'vote',
         'title': 'Zulage auf 125 € — 130 € waren knapp nicht drin',
         'text': 'Erst scheitert der Antrag auf 130 € mit 10:13, dann geht die Erhöhung auf '
                 '125 € mit 13:10 durch. Der Gesamtbeschluss danach ist einstimmig.',
         'sessionId': 'sr_20260720', 'voteId': 'sr_20260720_08'},
    ],
    'field': 'education',
    'type': 'vorhaben',
    'status': 'laufend',
}


def load(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f:
        return json.load(f)


def save(name, obj):
    with open(os.path.join(DATA, name), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    topics, votes = load('topics.json'), load('votes.json')
    by_id = {v['id']: v for v in votes}
    have = {t['id'] for t in topics}
    for t in (T30, T31):
        if t['id'] in have:
            raise SystemExit(t['id'] + ' existiert schon')

    for tid, ids in (('t30', ABWASSER), ('t31', KITA)):
        for vid in ids:
            v = by_id[vid]
            v['topicId'] = tid

    # Der Klaeranlagen-Jahresabschluss 2022 stand in der Haushalts-Historie.
    t7 = next(t for t in topics if t['id'] == 't7')
    weg = [h for h in t7['history'] if h.get('voteId') == 'sr_20230724_03']
    for h in weg:
        t7['history'].remove(h)
        h['title'] = 'Jahresabschluss 2022 und Entlastung des Aufsichtsrats'
        T30['history'].append(h)
    T30['history'].sort(key=lambda h: h['date'])

    topics += [T30, T31]
    save('topics.json', topics)
    save('votes.json', votes)
    print('t30: %d Voten, %d Historieneinträge' % (len(ABWASSER), len(T30['history'])))
    print('t31: %d Voten, %d Historieneinträge' % (len(KITA), len(T31['history'])))
    print('aus t7 verschoben: %d' % len(weg))


if __name__ == '__main__':
    main()
