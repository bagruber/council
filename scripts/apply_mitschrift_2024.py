"""Traegt Mitschriften und zwei Presseartikel als Einzelstimmen ein.

Vier Beschluesse vom 10.06.2024 und einer vom 28.07.2025 liegen als
Mitschrift vor. Wo alle Anwesenden benannt sind, wird das Votum auf `named`
umgestellt; kurzfristige Abwesenheiten, die die Sitzungsliste nicht kennt,
kommen als `excluded` dazu und muessen auch in `results.absent` stehen,
damit die Arrays auf die Gremiengroesse aufgehen.

Aufruf ohne Argument = Probelauf, --apply schreibt.
"""
import json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')

ARTICLES = [
    ('sz_2023-01-12_pflaster-mehrkosten', 'sz', '2023-01-12',
     'Feste Verfugung: Streit um die Mehrkosten',
     'https://www.sueddeutsche.de/muenchen/freising/moosburg-stadtrat-plan-umgestaltung-pflaster-feste-verfugung-mehrkosten-1.5732083'),
    ('merkur_2023-04-24_ausschussgroesse', 'merkur', '2023-04-24',
     'Ausschüsse vergrößern? Stadträte sagen Nein',
     'https://www.merkur.de/lokales/freising/moosburg-ort29088/ausschuesse-vergroessern-moosburgs-stadtraete-sagen-nein-und-zwei-parteien-bleiben-draussen-92237949.html'),
]

MS = {'tier': 'tracked', 'by': 'gruber', 'pressVerified': False}

# Vollstaendige Mitschriften: Nein-Seite benannt, der Rest der Anwesenden
# stimmte dafuer. `extra` sind Abwesende, die die Sitzungsliste nicht fuehrt.
FULL = [
    ('sr_20240610_02', ['tristl', 'fincke', 'lauterbach'], [], MS),
    ('sr_20240610_09', ['linz_karin', 'haberl', 'tristl', 'fincke', 'grundner'], [], MS),
    ('sr_20250728_03', ['haberl'], ['linz_karin', 'fincke', 'kaestl'], MS),
]

# Teilbekannt — bei zwei Beschluessen steht Reif doppelt und Lauterbach
# nirgends, das laesst sich nicht aufloesen. Beide bleiben hier offen.
PART = [
    ('sr_20240610_04',
     {'dollinger': 'yes', 'weber': 'yes', 'haberl': 'yes', 'pschorr': 'yes',
      'fincke': 'yes', 'kaestl': 'yes', 'gruebl': 'yes', 'grundner': 'yes',
      'kieninger': 'yes',
      'linz_karin': 'no', 'tristl': 'no', 'strobl': 'no', 'gruber': 'no',
      'von_pressentin': 'no', 'linz_kilian': 'no', 'beibl': 'no'}, MS),
    ('sr_20240610_05',
     {'dollinger': 'yes', 'weber': 'yes', 'haberl': 'yes', 'pschorr': 'yes',
      'grundner': 'yes', 'kieninger': 'yes',
      'linz_karin': 'no', 'tristl': 'no', 'fincke': 'no', 'kaestl': 'no',
      'strobl': 'no', 'gruber': 'no', 'gruebl': 'no',
      'von_pressentin': 'no', 'linz_kilian': 'no', 'beibl': 'no'}, MS),
    # CSU stimmte fuer die gebundene Verlegung, wie der Buergermeister
    ('sr_20230112_02',
     {'heinz': 'yes', 'hadersdorfer': 'yes', 'weber': 'yes', 'haberl': 'yes'},
     {'tier': 'press', 'pressId': ['sz_2023-01-12_granitpflaster',
                                   'sz_2023-01-12_pflaster-mehrkosten']}),
    # John steht in der Sitzungsliste als abwesend — sein Ja fehlt deshalb hier
    ('sr_20230424_04',
     {'weber': 'no', 'pschorr': 'no', 'dollinger': 'no', 'kieninger': 'no',
      'kaestl': 'yes', 'gruebl': 'yes'},
     {'tier': 'press', 'pressId': 'merkur_2023-04-24_ausschussgroesse'}),
]

LINK = {'sr_20230112_02': ['sz_2023-01-12_pflaster-mehrkosten'],
        'sr_20230424_04': ['merkur_2023-04-24_ausschussgroesse']}


def active(m, d):
    sp = m.get('periods') or [{'from': m.get('from'), 'to': m.get('to')}]
    return any((s.get('from') or '0') <= d and (not s.get('to') or s['to'] >= d)
               for s in sp)


def main():
    do_apply = '--apply' in sys.argv
    load = lambda n: json.load(open(os.path.join(DATA, n), encoding='utf-8'))
    press, votes, sessions = load('press.json'), load('votes.json'), load('sessions.json')
    members = load('members.json')['members']
    vmap = {v['id']: v for v in votes}
    smap = {s['id']: s for s in sessions}

    known = {a['id'] for a in press}
    for pid, media, date, title, url in ARTICLES:
        if pid in known:
            continue
        press.append({'id': pid, 'media': media, 'date': date, 'title': title, 'url': url})
        print('  + Artikel ' + pid)

    for vid, nays, extra, src in FULL:
        v, s = vmap[vid], smap[vmap[vid]['sessionId']]
        live = [m['id'] for m in members if active(m, v['date'])]
        absent = list(s.get('absent') or []) + extra
        yes = [i for i in live if i not in absent and i not in nays]
        r = v['results']
        if (r['yes'], r['no'], r['absent']) != (len(yes), len(nays), len(absent)):
            print('  ! ' + vid + ': Protokoll ' + str(r) + ' vs Mitschrift '
                  + str({'yes': len(yes), 'no': len(nays), 'absent': len(absent)}))
            continue
        v['type'] = 'named'
        v['results'] = {'yes': yes, 'no': list(nays), 'absent': absent}
        for mid in extra:
            ex = v.setdefault('excluded', [])
            if not any(e['member'] == mid for e in ex):
                ex.append({'member': mid, 'reason': 'kurzfristig abwesend'})
        v['source'] = dict(src)
        v.pop('voters', None)
        print('  = ' + vid + ' vollstaendig: ' + str(len(yes)) + ':' + str(len(nays))
              + ' + ' + str(len(absent)) + ' abwesend'
              + (' (davon ' + str(len(extra)) + ' kurzfristig)' if extra else ''))

    for vid, stances, src in PART:
        v = vmap[vid]
        v.setdefault('voters', {}).update(stances)
        v['source'] = dict(src)
        r = v['results']
        y = sum(1 for x in v['voters'].values() if x == 'yes')
        n = sum(1 for x in v['voters'].values() if x == 'no')
        print('  ~ ' + vid + ': ' + str(y) + ' von ' + str(r['yes']) + ' Ja, '
              + str(n) + ' von ' + str(r['no']) + ' Nein bekannt')

    for s in sessions:
        for it in s['agenda']:
            for pid in LINK.get(it.get('voteId'), []):
                lst = it.setdefault('press', [])
                if pid not in lst:
                    lst.append(pid)
                    print('  > ' + it['voteId'] + ' -> ' + pid)

    if do_apply:
        for name, obj in (('press.json', press), ('votes.json', votes),
                          ('sessions.json', sessions)):
            with open(os.path.join(DATA, name), 'w', encoding='utf-8') as f:
                json.dump(obj, f, ensure_ascii=False, indent=2)
                f.write('\n')
        print('\ngeschrieben')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
