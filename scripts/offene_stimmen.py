"""Listet je Person die Abstimmungen, bei denen ihr Verhalten unklar bleibt.

Spiegelt die Statuslogik aus js/core.js (voteStatus, isRegularOf) — unklar
heisst hier genau das, was die App als "?" zeigt: ein geteiltes Ergebnis ohne
Einzelstimmen, oder eine einstimmige Abstimmung, bei der die Ableitung gesperrt
ist. Wo die Niederschrift vermerkt, wer spaeter kam oder frueher ging, bleibt
nur deren Stimme offen (`inferable: "teilweise"`).

Sitzungen ohne veroeffentlichte Anwesenheitsliste (Beschlussauszuege der
Stadt, `source.kind == webauszug`) bleiben aussen vor: dort liegt die
Unklarheit an der fehlenden Liste, nicht am Abstimmungsergebnis.

Ausgabe ist eine Datei je Person, zum Verschicken gedacht: der Beschlusstext
steht dabei, damit sich das mit eigenen Notizen abgleichen laesst, und vor
jedem Punkt ein Kaestchen, das die Person nur austauschen muss.

Aufruf:
    python scripts/offene_stimmen.py --dir docs/offene-stimmen fincke kaestl
    python scripts/offene_stimmen.py fincke          # auf die Konsole
"""
import json, os, re, sys, argparse
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')

BODY_OF_TYPE = {'stadtrat': 'plenum', 'bpu': 'bpu', 'hvfa': 'hvfa'}
BODY_LABEL = {'plenum': 'Stadtrat', 'bpu': 'BPU', 'hvfa': 'HVFA'}


def load(n):
    return json.load(open(os.path.join(DATA, n), encoding='utf-8'))


def within(span, datum):
    von, bis = span.get('from'), span.get('to')
    if bis and len(bis) == 7:
        bis += '-99'
    return not (von and datum < von) and not (bis and datum > bis)


def aktiv_am(m, datum):
    # Geteilte Mandate (Marschoun) liegen in periods; from/to spannt die Lücke.
    perioden = m.get('periods') or [{'from': m.get('from'), 'to': m.get('to')}]
    return any(within(p, datum) for p in perioden)


def config_am(body, datum):
    configs = body.get('seatConfigs')
    if not configs:
        return body
    for c in configs:
        if within(c, datum):
            return c
    return {}


def regulaer(mid, body, datum):
    cfg = config_am(body, datum)
    if cfg.get('chair') == mid:
        return True
    if any(v['member'] == mid for v in cfg.get('vicechairs') or []):
        return True
    for s in cfg.get('seats') or []:
        if s.get('member') == mid:
            return True
        if any(o['member'] == mid and within(o, datum) for o in s.get('occupants') or []):
            return True
    return False


def status(mid, vote, session, member):
    if member and not aktiv_am(member, vote['date']):
        return None
    ex = next((e for e in vote.get('excluded') or [] if e['member'] == mid), None)
    if ex:
        return {'beteiligung': 'excluded', 'enthaltung': 'abstained',
                'nicht_stimmberechtigt': 'restricted',
                'kein_mandat': 'restricted'}.get(ex['reason'], 'absent')
    if session and mid in (session.get('absent') or []):
        return 'absent'

    r = vote['results']
    if vote['type'] == 'named':
        for feld in ('yes', 'no', 'absent'):
            if mid in r[feld]:
                return feld
        return None
    if (vote.get('voters') or {}).get(mid):
        return vote['voters'][mid]
    if mid in (r.get('absent_ids') or []):
        return 'absent'
    if vote.get('inferable') == 'teilweise' and any(
            e['member'] == mid for e in (session or {}).get('partial') or []):
        return 'unknown'
    if vote.get('inferable') is not False:
        if r['yes'] > 0 and r['no'] == 0:
            return 'yes-inferred'
        if r['no'] > 0 and r['yes'] == 0:
            return 'no-inferred'
    return 'unknown'


def datum_kurz(d):
    j, m, t = d.split('-')
    return f'{t}.{m}.{j}'


def kuerzen(text, grenze=260):
    text = re.sub(r'\s+', ' ', (text or '')).strip()
    text = re.sub(r'\s*\(\d+\s*:\s*\d+\)\.?$', '.', text)
    # Aus den Niederschriften geerbte Silbentrennung: "abwei- chende".
    # "Bau- und" ist dagegen ein echter Bindestrich und bleibt.
    text = re.sub(r'([A-Za-zÄÖÜäöüß]*[a-zäöüß])-\s+(?!(?:und|oder|bzw|sowie|wie)\b)([a-zäöüß]{2,})',
                  lambda m: m.group(1) + m.group(2), text)
    if len(text) <= grenze:
        return text
    schnitt = text[:grenze].rsplit('. ', 1)
    return (schnitt[0] + '.') if len(schnitt) > 1 else text[:grenze].rstrip() + ' …'


def einstimmig(v):
    r = v['results']
    return (not r['no'] or not r['yes']) if v['type'] == 'named' \
        else (r['no'] == 0 or r['yes'] == 0)


KOPF = """Offene Abstimmungen – {name}

Hallo {vorname}, bei diesen {n} Beschlüssen ist nicht überliefert, wie du
gestimmt hast. ⬜ ersetzen durch:
✅ dafür · ❌ dagegen · ➖ nicht mitgestimmt · ❔ weiß nicht mehr

Wo „einstimmig" steht, hat niemand dagegen gestimmt — ❌ scheidet dort aus.
Teilantworten helfen auch."""


def text_fuer(member, eintraege):
    nach_sitzung = defaultdict(list)
    for v, s, bid in eintraege:
        nach_sitzung[s['id']].append((v, s, bid))

    name = f"{member['firstName']} {member['lastName']}"
    z = [KOPF.format(name=name, vorname=member['firstName'], n=len(eintraege))]

    reihe = sorted(nach_sitzung, key=lambda k: nach_sitzung[k][0][1]['date'])
    jahre = sorted({nach_sitzung[k][0][1]['date'][:4] for k in reihe})
    jahr_offen = None

    for sid in reihe:
        gruppe = nach_sitzung[sid]
        s, bid = gruppe[0][1], gruppe[0][2]
        if len(jahre) > 1 and s['date'][:4] != jahr_offen:
            jahr_offen = s['date'][:4]
            z.append('')
            z.append(f'📆 {jahr_offen} · {jahre.index(jahr_offen) + 1}/{len(jahre)}')
        z.append('')
        z.append(f'📅 {datum_kurz(s["date"])} · {BODY_LABEL[bid]}')
        for v, _, _ in gruppe:
            r = v['results']
            z.append('')
            z.append(f'⬜ *{v["title"]}*')
            if v.get('text'):
                z.append(kuerzen(v['text']))
            z.append(f'📊 {r["yes"]}:{r["no"]}'
                     + (' · einstimmig' if einstimmig(v) else ''))

    z.append('')
    z.append('moosburg.eu/stadtrat')
    return '\n'.join(z) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ids', nargs='+')
    ap.add_argument('--dir')
    args = ap.parse_args()

    md = load('members.json')
    members = {m['id']: m for m in md['members']}
    bodies = {b['id']: b for b in md['bodies']}
    sessions = {s['id']: s for s in load('sessions.json')}
    votes = load('votes.json')

    fehlt = [i for i in args.ids if i not in members]
    if fehlt:
        sys.exit('Unbekannte ids: ' + ', '.join(fehlt))

    offen = defaultdict(list)
    for v in votes:
        session = sessions.get(v['sessionId'])
        bid = BODY_OF_TYPE.get((session or {}).get('type'))
        if not session or not bid:
            continue
        if (session.get('source') or {}).get('kind') == 'webauszug':
            continue
        body = bodies.get(bid)
        if not body:
            continue
        for mid in args.ids:
            m = members[mid]
            if bid == 'plenum':
                if not aktiv_am(m, v['date']):
                    continue
            elif not regulaer(mid, body, v['date']):
                continue
            if status(mid, v, session, m) == 'unknown':
                offen[mid].append((v, session, bid))

    for mid in args.ids:
        text = text_fuer(members[mid], offen[mid])
        if args.dir:
            ordner = os.path.join(ROOT, args.dir)
            os.makedirs(ordner, exist_ok=True)
            open(os.path.join(ordner, mid + '.txt'), 'w', encoding='utf-8').write(text)
            sitzungen = len({s['id'] for _, s, _ in offen[mid]})
            print(f'  {mid:14s} {len(offen[mid]):4d} Beschlüsse · {sitzungen:2d} Sitzungen'
                  f' · {len(text) // 1000} k Zeichen')
        else:
            print(text)


if __name__ == '__main__':
    main()
