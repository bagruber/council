"""Traegt fehlende Anwesenheitslisten nach und loest zwei Voten auf.

Achtzehn Sitzungen hatten keine Anwesenheitsliste. Elf davon sind
Beschlussauszuege — dort gibt es keine. Bei den uebrigen liegt die
Niederschrift vor, die Liste wurde beim Import nur nie ausgelesen; ohne sie
zeigt jedes einstimmige Votum ein Fragezeichen statt einer Stimme.

Hier kommen die Faelle dazu, bei denen die Zahlen der Niederschrift die Liste
bestaetigen. Sitzungen mit Vertretungen bleiben vorerst aussen vor.

Aufruf ohne Argument = Probelauf, --apply schreibt.
"""
import json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')

# Sitzung -> (Abwesende, Vertretungen)
ATTEND = {
    'sr_20251110':   (['becher_a', 'beibl', 'grundner', 'hobmaier'], []),
    'bpu_20230123':  ([], []),
    'bpu_20231123':  ([], []),
    'bpu_20250317':  (['tristl'], [{'member': 'tristl', 'substitute': 'haberl'}]),
}

# Presse- und Mitschriftbefunde
MS = {'tier': 'tracked', 'by': 'gruber', 'pressVerified': False}
PRESSE = 'merkur_2025-06-23_alte-polizei'

ARTICLE = (PRESSE, 'merkur', '2025-06-23',
           'Befestigen, Parkhaus oder nichts verändern?',
           'https://www.merkur.de/lokales/freising/moosburg-ort29088/befestigen-parkhaus-oder-nichts-veraendern-der-parkplatz-alte-polizei-in-moosburg-loest-grundsatzdebatte-aus-93800058.html')

# Nein-Seite vollstaendig benannt, der Rest der Anwesenden stimmte dafuer
FULL = [('sr_20211011_05', ['john'], MS)]

PART = [
    ('sr_20220919_03', {'john': 'no'}, MS),
    ('sr_20250623_02', {'grundner': 'no', 'lauterbach': 'no', 'reif': 'no',
                        'beibl': 'yes'},
     {'tier': 'press', 'pressId': PRESSE}),
    # Hobmaier und Reif fuehrt die Niederschrift an diesem Abend als abwesend,
    # ihr Votum bleibt deshalb draussen
    ('sr_20250714_08', {'pschorr': 'yes', 'grundner': 'yes',
                        'lauterbach': 'yes', 'kieninger': 'yes'}, MS),
]

LINK = {'sr_20250623_02': [PRESSE]}


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
    byses = {}
    for v in votes:
        byses.setdefault(v['sessionId'], []).append(v)

    for sid, (absent, subs) in ATTEND.items():
        s = smap[sid]
        s['absent'] = absent
        if subs:
            s['substitutes'] = subs
        # Gegenprobe: bei wie vielen Voten geht die Rechnung jetzt auf?
        ok = bad = 0
        for v in byses[sid]:
            r = v['results']
            cnt = lambda x: len(x) if isinstance(x, list) else x
            gap = cnt(r['absent']) - len(absent) - len(v.get('excluded') or [])
            (ok, bad) = (ok + 1, bad) if gap == 0 else (ok, bad + 1)
        print('  ' + sid + ': ' + str(len(absent)) + ' abwesend — '
              + str(ok) + ' Voten passen, ' + str(bad) + ' mit weiteren Kurzabwesenheiten')

    known = {a['id'] for a in press}
    if ARTICLE[0] not in known:
        pid, media, date, title, url = ARTICLE
        press.append({'id': pid, 'media': media, 'date': date, 'title': title, 'url': url})
        print('  + Artikel ' + pid)

    for vid, nays, src in FULL:
        v, s = vmap[vid], smap[vmap[vid]['sessionId']]
        live = [m['id'] for m in members if active(m, v['date'])]
        absent = list(s.get('absent') or [])
        yes = [i for i in live if i not in absent and i not in nays]
        cnt = lambda x: len(x) if isinstance(x, list) else x
        r = {k: cnt(x) for k, x in v['results'].items()}
        if (r['yes'], r['no'], r['absent']) != (len(yes), len(nays), len(absent)):
            print('  ! ' + vid + ': ' + str(r) + ' vs ' + str(len(yes)) + ':'
                  + str(len(nays)) + ':' + str(len(absent)))
            continue
        v['type'] = 'named'
        v['results'] = {'yes': yes, 'no': list(nays), 'absent': absent}
        v['source'] = dict(src)
        v.pop('voters', None)
        print('  = ' + vid + ' vollstaendig: ' + str(len(yes)) + ':' + str(len(nays))
              + ' + ' + str(len(absent)) + ' abwesend')

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
