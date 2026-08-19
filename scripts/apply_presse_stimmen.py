"""Traegt Stimmverhalten aus Presseberichten ein und legt die Artikel an.

Zeitungen nennen selten das ganze Abstimmungsbild, aber oft die eine
Gegenstimme. Wo die Zahlen der Niederschrift damit aufgehen — Ja + Nein +
Abwesende = Sitzzahl — ist die Abstimmung vollstaendig und wird auf `named`
umgestellt. Sonst bleibt sie anonym und bekommt die bekannten Positionen
als `voters`.

Herkunftsstufe ist in beiden Faellen `press`: ohne den Artikel waere die
Gegenstimme unbekannt, auch wenn die Ja-Seite aus der Anwesenheitsliste kommt.

Aufruf ohne Argument = Probelauf, --apply schreibt.
"""
import json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')

ARTICLES = [
    ('sz_2021-10-25_hundesteuer', 'sz', '2021-10-25',
     'Neue Satzung mit zusätzlichen Reinigungskosten',
     'https://www.sueddeutsche.de/muenchen/freising/neue-satzung-in-moosburg-zusaetzliche-reinigungskosten-1.5451743'),
    ('mz_2021-02-08_ganztagsbetreuung', 'mz', '2021-02-08',
     'Stadtrat beschließt offene Ganztagsbetreuung für Grundschule Süd',
     'https://www.idowa.de/regionen/moosburg/stadtrat-beschliesst-offene-ganztagsbetreuung-fuer-grundschule-sued-art-151274'),
    ('mz_2020-10-26_plan-tiefgarage', 'mz', '2020-10-26',
     'Es geht weiter mit der Plan-Neugestaltung',
     'https://www.idowa.de/regionen/moosburg/es-geht-weiter-mit-plan-neugestaltung-art-136108'),
    ('merkur_2020-10-26_plan-tiefgarage', 'merkur', '2020-10-26',
     'Jetzt steht fest, wann Moosburgs Plan umgebaut wird',
     'https://www.merkur.de/lokales/freising/moosburg-ort29088/jetzt-steht-fest-wann-moosburgs-plan-umgebaut-wird-tiefgarage-neu-diskutiert-90082163.html'),
    ('sz_2023-01-12_granitpflaster', 'sz', '2023-01-12',
     'Kompromiss beim Pflaster: gebunden und offen verfugt',
     'https://www.sueddeutsche.de/muenchen/freising/moosburg-stadtrat-plan-neugestaltung-pflaster-kompromiss-verfugung-gebunden-offen-1.5777812'),
    ('merkur_2023-04-17_schloss-aschwiese', 'merkur', '2023-04-17',
     'Was passiert mit Schloss-Asch-Wiese und altem Sportplatz?',
     'https://www.merkur.de/lokales/freising/moosburg-ort29088/gedankenspiele-fuer-moosburgs-filetstueck-was-passiert-mit-schloss-asch-wiese-und-altem-sportplatz-92221907.html'),
    ('merkur_2024-11-04_hallenbad-kinder', 'merkur', '2024-11-04',
     'Kinder in den Ferien gratis ins Hallenbad – geteilte Meinungen',
     'https://www.merkur.de/lokales/freising/moosburg-ort29088/moosburg-kinder-in-den-ferien-gratis-ins-neue-hallenbad-geteilte-meinungen-im-stadtrat-93394613.html'),
    ('mz_2024-11-04_hallenbad-kinder', 'mz', '2024-11-04',
     'Gratis Badespaß für Kinder vertagt',
     'https://www.idowa.de/regionen/moosburg/gratis-badespass-fuer-kinder-in-moosburg-vertagt-art-307180'),
    ('merkur_2026-02-23_bplan-aich', 'merkur', '2026-02-23',
     'Bauvorhaben im Villenviertel stößt auf Ablehnung',
     'https://www.merkur.de/lokales/freising/moosburg-ort29088/sorge-vor-vierkantbolzen-im-quartier-bauvorhaben-im-moosburger-villenviertel-stoesst-auf-ablehnung-94196267.html'),
]

# voteId -> (Artikel, bekannte Positionen, vollstaendig). "Vollstaendig" heisst:
# die Zahlen gehen auf, alle uebrigen Anwesenden standen auf der anderen Seite.
FINDINGS = {
    'sr_20211025_04': ('sz_2021-10-25_hundesteuer',
                       {'pschorr': 'no', 'becher_j': 'yes'}, False),
    'sr_20210208_02': ('mz_2021-02-08_ganztagsbetreuung',
                       {'kaestl': 'no'}, True),
    'sr_20230112_02': ('sz_2023-01-12_granitpflaster',
                       {'dollinger': 'yes'}, False),
    'sr_20230417_01': ('merkur_2023-04-17_schloss-aschwiese',
                       {'becher_j': 'yes', 'dollinger': 'no'}, False),
    'sr_20241104_05': ('merkur_2024-11-04_hallenbad-kinder',
                       {'beibl': 'no', 'dollinger': 'yes'}, False),
    'sr_20260223_01': ('merkur_2026-02-23_schulweg',
                       {'strobl': 'no'}, True),
    'sr_20260223_04': ('merkur_2026-02-23_bplan-aich',
                       {'tristl': 'yes', 'pschorr': 'yes', 'beibl': 'no'}, False),
}

# Weitere Artikel zur selben Abstimmung — ohne auswertbares Stimmverhalten
LINK_ONLY = {
    'sr_20201026_03': ['mz_2020-10-26_plan-tiefgarage',
                       'merkur_2020-10-26_plan-tiefgarage'],
    'sr_20241104_05': ['mz_2024-11-04_hallenbad-kinder'],
}

# Die Timeline haengt am Hauptbeschluss, das Stimmverhalten am Aenderungsantrag
TOPIC_ONLY = {
    'sr_20230417_02': ['merkur_2023-04-17_schloss-aschwiese'],
}


def active(m, d):
    sp = m.get('periods') or [{'from': m.get('from'), 'to': m.get('to')}]
    return any((s.get('from') or '0') <= d and (not s.get('to') or s['to'] >= d)
               for s in sp)


def main():
    do_apply = '--apply' in sys.argv
    load = lambda n: json.load(open(os.path.join(DATA, n), encoding='utf-8'))
    press, votes, sessions, topics = (load('press.json'), load('votes.json'),
                                      load('sessions.json'), load('topics.json'))
    members = load('members.json')['members']
    vmap = {v['id']: v for v in votes}
    smap = {s['id']: s for s in sessions}

    known = {a['id'] for a in press}
    for pid, media, date, title, url in ARTICLES:
        if pid in known:
            print('  schon vorhanden: ' + pid)
            continue
        press.append({'id': pid, 'media': media, 'date': date,
                      'title': title, 'url': url})
        print('  + Artikel ' + pid)

    for vid, (pid, stances, expand) in FINDINGS.items():
        v = vmap[vid]
        s = smap[v['sessionId']]
        v['source'] = {'tier': 'press', 'pressId': pid}
        if not expand:
            v.setdefault('voters', {}).update(stances)
            print('  ~ ' + vid + ' ' + str(stances))
            continue

        live = [m['id'] for m in members if active(m, v['date'])]
        absent = list(s.get('absent') or [])
        r = v['results']
        if r['yes'] + r['no'] + r['absent'] != len(live):
            print('  ! ' + vid + ': Zahlen gehen nicht auf, uebersprungen')
            continue
        rest = [i for i in live if i not in absent and i not in stances]
        side = 'yes' if r['no'] == len(stances) else 'no'
        v['type'] = 'named'
        v['results'] = {'yes': rest if side == 'yes' else list(stances),
                        'no': list(stances) if side == 'yes' else rest,
                        'absent': absent}
        v.pop('voters', None)
        print('  = ' + vid + ' vollstaendig: ' + str(len(v['results']['yes']))
              + ':' + str(len(v['results']['no'])) + ' + '
              + str(len(absent)) + ' abwesend')

    # Presselinks an Tagesordnungspunkt und Themen-Timeline
    refs = {vid: [p] for vid, (p, _, _) in FINDINGS.items()}
    for vid, ps in LINK_ONLY.items():
        refs.setdefault(vid, []).extend(ps)
    for coll, rows, extra in (
            ('sessions', [i for s in sessions for i in s['agenda']], {}),
            ('topics', [h for t in topics for h in t.get('history', [])], TOPIC_ONLY)):
        for row in rows:
            for pid in refs.get(row.get('voteId'), []) + extra.get(row.get('voteId'), []):
                lst = row.setdefault('press', [])
                if pid not in lst:
                    lst.append(pid)
                    print('  > ' + coll + ' ' + row['voteId'] + ' -> ' + pid)

    if do_apply:
        for name, obj in (('press.json', press), ('votes.json', votes),
                          ('sessions.json', sessions), ('topics.json', topics)):
            with open(os.path.join(DATA, name), 'w', encoding='utf-8') as f:
                json.dump(obj, f, ensure_ascii=False, indent=2)
                f.write('\n')
        print('\ngeschrieben')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
