"""Backlog-Import: 38 Niederschriften (2020-01 bis 2026-05) in sessions/votes/members.

Liest die Parser-Ausgabe (scratchpad/parsed.json) und schreibt sessions.json,
votes.json und die drei abgestimmten members.json-Korrekturen.

Einmalig gedacht — nach dem Lauf bleibt das Skript als Dokumentation liegen.
"""
import json, os, re, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
PARSED = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'parsed.json')

MONTHS = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
          'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']


def load(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f:
        return json.load(f)


def save(name, obj):
    with open(os.path.join(DATA, name), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


# ── 1. members.json — die drei abgestimmten Korrekturen ──────────────────────

def fix_members(members):
    by = {m['id']: m for m in members['members']}
    # Marschoun: Mandatspause 2020–2026 (in keiner Niederschrift dieser Periode)
    by['marschoun']['periods'] = [
        {'from': '2014-05-01', 'to': '2020-04-30'},
        {'from': '2026-05-01'},
    ]
    # Nachrücken Gruber für Neumayr: laut Niederschrift 10.10.2022, nicht 24.10.
    by['neumayr']['to'] = '2022-10-10'
    by['gruber']['from'] = '2022-10-10'
    # Dollinger war am 20.01.2020 Zweiter Bürgermeister — Mandat vor seiner
    # Amtszeit als Erster Bürgermeister (2020-05-01).
    by['dollinger']['from'] = '2014-05-01'
    # Vor- und Nachname waren vertauscht; Niederschriften führen ihn als
    # „Daoud Ghadieh, Moutasem, Dr."
    by['ghadieh']['lastName'] = 'Daoud Ghadieh'
    by['ghadieh']['firstName'] = 'Moutasem'
    return members


def active_ids(members, date):
    out = []
    for m in members['members']:
        spans = m.get('periods') or [{'from': m.get('from'), 'to': m.get('to')}]
        if any((s.get('from') or '0') <= date and (not s.get('to') or s['to'] >= date)
               for s in spans):
            out.append(m['id'])
    return out


# ── 2. Votes zusammenfassen ──────────────────────────────────────────────────

def parent_top(top):
    return (top or '').split('.')[0]


def shorten(s, n=95):
    s = re.sub(r'\s+', ' ', (s or '')).strip()
    return s if len(s) <= n else s[:n - 1].rsplit(' ', 1)[0] + '…'


def collapse(votes):
    """Aufeinanderfolgende Stellungnahme-Voten mit identischem Ergebnis unter
    demselben Haupt-TOP zu einem Sammelvote verdichten."""
    out, i = [], 0
    while i < len(votes):
        j = i
        while (j + 1 < len(votes)
               and parent_top(votes[j + 1]['top']) == parent_top(votes[i]['top'])
               and votes[j + 1]['yes'] == votes[i]['yes']
               and votes[j + 1]['no'] == votes[i]['no']
               and votes[j + 1]['outcome'] == votes[i]['outcome']):
            j += 1
        n = j - i + 1
        if n >= 6:
            v = dict(votes[i])
            v['sammel'] = n
            out.append(v)
        else:
            out.extend(votes[i:j + 1])
        i = j + 1
    return out


# ── 3. Aufbau ────────────────────────────────────────────────────────────────

def build(sess, members):
    date = sess['date']
    sid = 'sr_' + date.replace('-', '')
    roster = active_ids(members, date)
    absent = [a for a in sess['absent'] if a in roster]
    voting_pool = [m for m in roster if m not in absent]

    y, mo = int(date[:4]), int(date[5:7])
    title = f"{sess['nr']}. Stadtratssitzung – {MONTHS[mo - 1]} {y}"
    if sess.get('konstituierend'):
        title += ' (konstituierend)'

    votes, agenda_votes = [], {}
    for n, v in enumerate(collapse(sess['votes']), 1):
        vid = f"{sid}_{n:02d}"
        total = v['yes'] + v['no']
        unanimous = v['no'] == 0 or v['yes'] == 0
        text = shorten(v['text'], 400)
        # im Protokoll vermerkte Nichtteilnahme (kurzfristig abwesend oder
        # persönlich beteiligt nach Art. 49 GO) — zählt nicht zum Stimmenpool
        excl = [e for e in v.get('excluded', [])
                if e.get('id') and not str(e['id']).startswith('?') and e['id'] in voting_pool]
        pool = [m for m in voting_pool if m not in {e['id'] for e in excl}]
        if v.get('sammel'):
            text = f"Sammelvote: {v['sammel']} Einzelbeschlüsse mit identischem Ergebnis ({v['yes']}:{v['no']}). " + text

        entry = {
            'id': vid, 'sessionId': sid, 'topicId': None, 'date': date,
            'title': shorten(v['top_title'] or text, 95),
            'text': text,
        }
        # Einstimmig und alle Stimmberechtigten beteiligt → Einzelstimmen ableitbar
        if unanimous and total == len(pool):
            side = 'yes' if v['no'] == 0 else 'no'
            entry['type'] = 'named'
            entry['results'] = {'yes': pool if side == 'yes' else [],
                                'no': pool if side == 'no' else [],
                                'absent': absent + [e['id'] for e in excl]}
            entry['source'] = {'tier': 'protocol-implicit'}
        else:
            entry['type'] = 'anonymous'
            entry['results'] = {'yes': v['yes'], 'no': v['no'],
                                'absent': len(roster) - total}
            # einstimmig, aber Teilnehmerzahl passt nicht exakt: core.js leitet
            # trotzdem 'yes-inferred' ab — Herkunft ist dieselbe wie bei named
            if unanimous:
                entry['source'] = {'tier': 'protocol-implicit'}
        if excl:
            entry['excluded'] = [{'member': e['id'],
                                  'reason': 'beteiligung' if e['reason'] == 'beteiligung'
                                            else 'kurzfristig abwesend'} for e in excl]
        if v['outcome'] == 'abgelehnt' or v['no'] > v['yes']:
            entry['result'] = 'rejected'
        votes.append(entry)
        agenda_votes.setdefault(v['top'], []).append(vid)

    agenda = []
    for a in sess['agenda']:
        item = {'number': a['number'], 'title': shorten(a['title'], 160)}
        vids = agenda_votes.get(a['number'])
        if vids:
            item['voteId'] = vids[0]
            if len(vids) > 1:
                item['voteIds'] = vids
        elif re.match(r'Mitteilungen|Bürgerfragen|Anfragen|Vereidigung|Wahl ',
                      a['title']):
            item['type'] = 'formal'
        agenda.append(item)

    session = {'id': sid, 'date': date, 'type': 'stadtrat', 'title': title,
               'absent': absent, 'agenda': agenda}
    if sess.get('partial'):
        session['notes'] = [shorten(p, 200) for p in sess['partial']]
    return session, votes


def main():
    parsed = json.load(open(PARSED, encoding='utf-8'))
    members = fix_members(load('members.json'))
    sessions = load('sessions.json')
    votes = load('votes.json')
    have = {s['id'] for s in sessions}

    new_s, new_v = [], []
    for p in sorted(parsed, key=lambda x: x['date']):
        sid = 'sr_' + p['date'].replace('-', '')
        if sid in have:
            print('skip (exists):', sid)
            continue
        s, vs = build(p, members)
        new_s.append(s)
        new_v.extend(vs)

    sessions = sorted(sessions + new_s, key=lambda s: (s['date'], s['id']))
    votes = sorted(votes + new_v, key=lambda v: (v['date'], v['id']))
    save('members.json', members)
    save('sessions.json', sessions)
    save('votes.json', votes)

    named = sum(1 for v in new_v if v['type'] == 'named')
    print(f"\n+{len(new_s)} Sitzungen, +{len(new_v)} Votes "
          f"({named} named / {len(new_v) - named} anonymous)")
    print(f"Gesamt: {len(sessions)} Sitzungen, {len(votes)} Votes")


if __name__ == '__main__':
    main()
