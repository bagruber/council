"""Tracking-Exporte des council-voting-tool in sessions/votes überführen.

Nur für Sitzungen, zu denen auch eine Niederschrift vorliegt — das Tracking
liefert die Einzelstimmen (Tier `tracked`), die Niederschrift das Aggregat.

Aufruf:  python scripts/add_tracking_2026.py <zip-oder-ordner> --by <member-id>
"""
import json, os, re, sys, zipfile, argparse, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
BODY_BY_TITLE = {'Bau-, Planungs- und Umweltausschuss': ('bpu', 'bpu'),
                 'Stadtrat': ('sr', 'stadtrat'),
                 'Hauptverwaltungs- und Finanzausschuss': ('hvfa', 'hvfa')}


def load(n):
    return json.load(open(os.path.join(DATA, n), encoding='utf-8'))


def save(n, o):
    with open(os.path.join(DATA, n), 'w', encoding='utf-8') as f:
        json.dump(o, f, ensure_ascii=False, indent=2)
        f.write('\n')


def fold(s):
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return (s.lower().replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue')
             .replace('ß', 'ss').replace('.', '').strip())


def name_index(members):
    idx = {}
    for m in members:
        idx[fold(f"{m['lastName']}, {m['firstName']}")] = m['id']
        for key in [m['lastName']] + m['lastName'].split():
            idx.setdefault(fold(key), m['id'])
    return idx


def resolve(idx, name):
    # Titel entfernen, aber das Komma zwischen Nach- und Vorname erhalten
    n = fold(re.sub(r'\s*\b(Dr\.|Dipl\.[\w.-]*|MdL)\s*', ' ', name).replace(' ,', ',').strip())
    if n in idx:
        return idx[n]
    last = n.split(',')[0].strip()
    return idx.get(last)


def read_export(path):
    if os.path.isdir(path):
        return json.load(open(os.path.join(path, 'oeffentlich.json'), encoding='utf-8'))
    with zipfile.ZipFile(path) as z:
        return json.loads(z.read('oeffentlich.json').decode('utf-8'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('--by', required=True, help='member id der erfassenden Person')
    ap.add_argument('--press-verified', action='store_true')
    args = ap.parse_args()

    exp = read_export(args.source)
    members = load('members.json')
    idx = name_index(members['members'])
    date = exp['sitzung']['datum']
    prefix, stype = BODY_BY_TITLE[exp['sitzung']['gremium']]
    sid = f"{prefix}_{date.replace('-', '')}"

    present = [resolve(idx, a['name']) for a in exp['anwesenheit']
               if a['verlauf'][-1]['status'] == 'anwesend']
    present = [p for p in present if p]

    sessions, votes = load('sessions.json'), load('votes.json')
    sess = next((s for s in sessions if s['id'] == sid), None)
    existing = {v['id']: v for v in votes if v['sessionId'] == sid}

    # Tracking-Abstimmungen in der Reihenfolge des Exports
    tracked = []
    for a in exp['abstimmungen']:
        yes = [resolve(idx, n) for n in a['ja']]
        no = [resolve(idx, n) for n in a['nein']]
        away = [resolve(idx, n) for n in a.get('kurzzeitig_abwesend', [])]
        tracked.append({
            'top': (a.get('top') or '').strip(),
            'title': re.sub(r'\s+', ' ', a['titel']).strip(),
            'comment': re.sub(r'\s+', ' ', a.get('kommentar') or '').strip(),
            'yes': [x for x in yes if x], 'no': [x for x in no if x],
            'away': [x for x in away if x],
        })

    def top_no(s):
        m = re.match(r'Ö?\s*(\d+(?:\.\d+)*)', s)
        return m.group(1) if m else None

    if sess is None:                                   # Sitzung neu anlegen
        # Bei Ausschüssen zählen nur die regulären Sitze als abwesend, nicht
        # der ganze Stadtrat.
        pool = _body_members(members, prefix, date) or [
            m['id'] for m in members['members'] if _active(m, date)]
        absent = [m for m in pool if m not in present]
        agenda, seen = [], set()
        for t in tracked:
            n = top_no(t['top'])
            if n and n not in seen:
                seen.add(n)
                agenda.append({'number': n,
                               'title': re.sub(r'^Ö?\s*[\d.]+\s*', '', t['top'])})
        sess = {'id': sid, 'date': date, 'type': stype,
                'title': _session_title(stype, date, sessions),
                'absent': absent, 'agenda': agenda}
        sessions.append(sess)
        sessions.sort(key=lambda s: (s['date'], s['id']))
        print(f'neue Sitzung {sid} angelegt ({len(agenda)} TOPs)')

    # Zuordnung über TOP-Nummer und Reihenfolge innerhalb des TOP. Die
    # Niederschrift ist die stärkere Quelle: sie wird nie überschrieben.
    pool = _body_members(members, prefix, date) or [
        m['id'] for m in members['members'] if _active(m, date)]

    by_top = {}
    for v in sorted(existing.values(), key=lambda v: v['id']):
        by_top.setdefault(_vote_top(sess, v['id']), []).append(v)

    added = upgraded = kept = 0
    conflicts = []
    for t in tracked:
        n = top_no(t['top'])
        queue = by_top.get(n) or []
        target = queue.pop(0) if queue else None
        t_total = len(t['yes']) + len(t['no'])
        source = {'tier': 'tracked', 'by': args.by,
                  'pressVerified': bool(args.press_verified)}
        results = {'yes': t['yes'], 'no': t['no'],
                   'absent': sorted(set(pool) - set(t['yes']) - set(t['no']))}

        if target is None:
            vid = f"{sid}_{len(existing) + added + 1:02d}"
            nv = {'id': vid, 'sessionId': sid, 'topicId': None, 'date': date,
                  'title': _short(t['title']), 'text': t['title'],
                  'type': 'named', 'results': results, 'source': source}
            if t['comment']:
                nv['note'] = t['comment']
            if len(t['no']) > len(t['yes']):
                nv['result'] = 'rejected'
            votes.append(nv)
            added += 1
            continue

        p_total = (len(target['results']['yes']) + len(target['results']['no'])
                   if target['type'] == 'named'
                   else target['results']['yes'] + target['results']['no'])
        if target['type'] == 'named':
            kept += 1                       # protocol-implicit schlägt tracked
        elif p_total != t_total:
            conflicts.append((target['id'], p_total, t_total))
        else:
            target.update(type='named', results=results, source=source)
            if t['comment']:
                target['note'] = t['comment']
            upgraded += 1

    for cid, p, tt in conflicts:
        print(f'  ! {cid}: Niederschrift {p} Stimmen, Tracking {tt} — '
              f'Niederschrift behalten, Tracking nicht übernommen')
    votes.sort(key=lambda v: (v['date'], v['id']))
    save('sessions.json', sessions)
    save('votes.json', votes)
    print(f'{sid}: +{added} neu, {upgraded} auf named angehoben (Tier tracked, '
          f'by={args.by}), {kept} bei protocol-implicit belassen, '
          f'{len(conflicts)} Konflikt(e)')


def _active(m, d):
    spans = m.get('periods') or [{'from': m.get('from'), 'to': m.get('to')}]
    return any((s.get('from') or '0') <= d and (not s.get('to') or s['to'] >= d)
               for s in spans)


def _vote_top(sess, vid):
    for a in sess.get('agenda', []):
        if a.get('voteId') == vid or vid in (a.get('voteIds') or []):
            return str(a['number'])
    return None


def _short(s, n=95):
    s = re.sub(r'\s+', ' ', s).strip()
    return s if len(s) <= n else s[:n - 1].rsplit(' ', 1)[0] + '…'


def _body_members(members, prefix, date):
    body = next((b for b in members['bodies'] if b.get('id') == prefix), None)
    if not body or body.get('type') == 'plenum':
        return []
    cfg = next((c for c in body.get('seatConfigs', [])
                if (c.get('from') or '0') <= date and (not c.get('to') or c['to'] >= date)),
               None) or body
    out = [cfg.get('chair')] + [v['member'] for v in cfg.get('vicechairs', [])]
    for s in cfg.get('seats', []):
        if s.get('member'):
            out.append(s['member'])
            continue
        # Sitz mit wechselnder Besetzung: den zum Datum passenden Inhaber nehmen
        for o in s.get('occupants', []):
            if (o.get('from') or '0') <= date and (not o.get('to') or o['to'] >= date):
                out.append(o['member'])
                break
    return [x for x in out if x]


def _session_title(stype, date, sessions):
    label = {'stadtrat': 'Stadtratssitzung', 'bpu': 'Sitzung Bau-, Planungs- und Umweltausschuss',
             'hvfa': 'Sitzung Hauptverwaltungs- und Finanzausschuss'}[stype]
    n = sum(1 for s in sessions if s['type'] == stype and s['date'][:4] == date[:4]
            and s['date'] < date) + 1
    return f"{n}. {label}" if stype != 'stadtrat' else f"{n}. {label} – {date[:4]}"


if __name__ == '__main__':
    main()
