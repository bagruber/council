"""Traegt die 16 BPU-Beschlussauszuege in sessions.json und votes.json ein.

Grundlage ist `data/niederschriften/bpu intake.txt` — die Textfassung der
Buergerinfo-Seiten der Stadt. Diese Sitzungen erscheinen nie als Niederschrift.

Was der Auszug hergibt und was nicht:
  * Tagesordnung, Beschlussart und Stimmenzahlen: ja.
  * Anwesenheitsliste: nein. Deshalb `source.kind = webauszug`.

Daraus die Ableitungsregeln:
  * Erreicht *irgendeine* Abstimmung der Sitzung die volle Sitzzahl (BPU: 12),
    war niemand ganztaegig abwesend -> `absent: []`. Einzelne Voten mit weniger
    Stimmen sind dann kurzfristige Abwesenheiten, wer, bleibt offen.
  * Einstimmige Voten mit voller Sitzzahl werden `named`.
  * Alles andere bleibt `anonymous`; `mark_inferable.py` sperrt die Ableitung.
  * Vor Mai 2020 gibt es fuer den BPU gar keine Sitzverteilung. Dort bleibt auch
    ein 12:0 anonym — die zwoelf Namen sind nicht bekannt.

"Beschluss: Abgelehnt" heisst, dass das Vorhaben abgelehnt wurde, nicht dass die
Abstimmung scheiterte: 12:0 bedeutet, der Beschluss zur Ablehnung ging
einstimmig durch. `result: rejected` wird nur gesetzt, wenn Nein ueberwiegt.
"""
import json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_bpu_webauszug import parse, SRC

FORMAL = ('Mitteilungen des Ersten Bürgermeisters', 'Mitteilungen der Ersten Bürgermeisterin',
          'Anfragen und Sonstiges')
MEHRFACH = ('Mehrere Einzelbeschlüsse. Der Beschlussauszug der Stadt weist dafür '
            'keine Stimmenzahlen aus.')

# Sitzungsnummern, soweit die Genehmigungs-TOPs sie belegen. Die beiden Sitzungen
# vor Mai 2020 gehoeren zur alten Wahlperiode und tragen keine bekannte Nummer.
NUMBERS = {
    '2020-09-21': 1, '2020-11-09': 2, '2020-12-17': 3,
    '2021-02-01': 1, '2021-03-18': 2, '2021-04-29': 3,
    '2021-06-14': 4, '2021-07-19': 5, '2021-09-27': 6,
    '2022-01-24': 1, '2022-03-24': 2, '2022-05-23': 3, '2022-09-26': 4,
    '2025-07-21': 4,
}
MONTH = ['', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
         'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']

# Eindeutige Zuordnungen zu bestehenden Dossiers; alles Uebrige bleibt offen.
TOPICS = {
    ('2020-03-02', '4.1'): 't12',   # Interims-Containerbad am Stadtbad
    ('2020-03-02', '3.1'): 't4',    # Fussgaenger- und Radverkehrskonzept
    ('2020-03-02', '3.2'): 't4',
    ('2022-09-26', '5'):   't20',   # Spielplatz Sanddornstrasse, WA Amperauen
    ('2025-07-21', '4.1'): 't8',    # Verkehrsberuhigung Schulzentrum Sued
}


def bpu_seats(members_data, date):
    """Die zwölf Sitze des BPU an diesem Tag, oder None vor Mai 2020."""
    body = next(b for b in members_data['bodies'] if b['id'] == 'bpu')
    cfg = next((c for c in body['seatConfigs']
                if (c.get('from') or '0') <= date and (not c.get('to') or c['to'] >= date)), None)
    if not cfg:
        return None
    out = [cfg['chair']] + [v['member'] for v in cfg.get('vicechairs', [])]
    for s in cfg['seats']:
        if s.get('member'):
            out.append(s['member']); continue
        occ = next((o for o in s.get('occupants', [])
                    if (o.get('from') or '0') <= date and (not o.get('to') or o['to'] >= date)), None)
        if occ:
            out.append(occ['member'])
    return out


def main():
    members_data = json.load(open(os.path.join(DATA, 'members.json'), encoding='utf-8'))
    sessions = json.load(open(os.path.join(DATA, 'sessions.json'), encoding='utf-8'))
    votes = json.load(open(os.path.join(DATA, 'votes.json'), encoding='utf-8'))
    lengths = json.load(open(os.path.join(DATA, 'sessionlengths.json'), encoding='utf-8'))

    known = {s['id'] for s in sessions}
    have_len = {(l['date'], l['body']) for l in lengths}
    stats = {'sessions': 0, 'votes': 0, 'named': 0, 'anonymous': 0,
             'rejected': 0, 'mehrfach': 0, 'voll besetzt': 0}

    for s in parse(open(SRC, encoding='utf-8').read()):
        sid = 'bpu_' + s['date'].replace('-', '')
        if sid in known:
            print(f"  uebersprungen (existiert): {sid}")
            continue

        seats = bpu_seats(members_data, s['date'])
        size = len(seats) if seats else 12
        voted = [i for i in s['items'] if i['ja'] is not None]
        # Volle Sitzzahl in mindestens einem Votum -> niemand ganztaegig abwesend
        complete = any(i['ja'] + i['nein'] == size for i in voted)
        if complete:
            stats['voll besetzt'] += 1

        y, m = int(s['date'][:4]), int(s['date'][5:7])
        nr = NUMBERS.get(s['date'])
        title = (f"{nr}. Sitzung Bau-, Planungs- und Umweltausschuss – {MONTH[m]} {y}"
                 if nr else f"Sitzung Bau-, Planungs- und Umweltausschuss – {MONTH[m]} {y}")

        session = {'id': sid, 'date': s['date'], 'type': 'bpu', 'title': title,
                   'source': {'kind': 'webauszug', 'url': s['url']}, 'agenda': []}
        if complete:
            session['absent'] = []

        n = 0
        for it in s['items']:
            item = {'number': it['number'], 'title': it['title']}
            if it['title'] in FORMAL or it['title'].startswith('Bürgerfragen'):
                item['type'] = 'formal'
            if it['kind'] == 'Mehrfachbeschluss':
                item['note'] = MEHRFACH
                stats['mehrfach'] += 1
            if it['ja'] is not None:
                n += 1
                vid = f'{sid}_{n:02d}'
                item['voteId'] = vid
                total = it['ja'] + it['nein']
                unanimous = it['nein'] == 0 or it['ja'] == 0
                nameable = seats and total == size and unanimous

                if it['kind'] == 'Abgelehnt':
                    text = (f"Das Vorhaben wurde abgelehnt. Der Beschluss dazu ging mit "
                            f"{it['ja']}:{it['nein']} durch." if it['ja'] > it['nein']
                            else f"Abgelehnt: der Beschlussvorschlag fiel mit {it['ja']}:{it['nein']} durch.")
                else:
                    text = f"Beschlossen mit {it['ja']}:{it['nein']}."
                if it['note']:
                    text = it['note'] + ' ' + text

                v = {'id': vid, 'sessionId': sid,
                     'topicId': TOPICS.get((s['date'], it['number'])),
                     'date': s['date'], 'title': it['title'], 'text': text}
                if it['ja'] < it['nein']:
                    v['result'] = 'rejected'
                    stats['rejected'] += 1
                if nameable:
                    side = 'yes' if it['nein'] == 0 else 'no'
                    other = 'no' if side == 'yes' else 'yes'
                    v['type'] = 'named'
                    v['results'] = {side: list(seats), other: [], 'absent': []}
                    stats['named'] += 1
                else:
                    v['type'] = 'anonymous'
                    v['results'] = {'yes': it['ja'], 'no': it['nein'],
                                    'absent': (size - total) if seats else 0}
                    stats['anonymous'] += 1
                v['source'] = {'tier': 'protocol-implicit' if nameable else None}
                if not nameable:
                    del v['source']
                if v['topicId'] is None:
                    del v['topicId']
                votes.append(v)
                stats['votes'] += 1
            session['agenda'].append(item)

        sessions.append(session)
        stats['sessions'] += 1
        if (s['date'], 'bpu') not in have_len:
            lengths.append({'date': s['date'], 'body': 'bpu',
                            'start': s['start'], 'end': s['end']})

    sessions.sort(key=lambda x: (x['date'], x['id']))
    votes.sort(key=lambda x: (x['date'], x['id']))
    lengths.sort(key=lambda x: (x['date'], x['body']))

    for name, obj in (('sessions.json', sessions), ('votes.json', votes),
                      ('sessionlengths.json', lengths)):
        with open(os.path.join(DATA, name), 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.write('\n')

    for k, v in stats.items():
        print(f'  {k:14} {v:4}')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
