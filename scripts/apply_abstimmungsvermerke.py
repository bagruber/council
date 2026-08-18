"""Traegt die "Abstimmungsvermerke" der Niederschriften als excluded-Eintraege ein.

Unter dem Ergebnis halten die Protokolle gelegentlich fest, wer bei genau dieser
Abstimmung nicht mitgestimmt hat — wegen kurzfristiger Abwesenheit oder
persoenlicher Beteiligung nach Art. 49 GO. Der Import hat diese Bloecke bisher
als Fliesstext verworfen.

Uebernommen wird nur, wo die Zuordnung abzaehlbar ist: in 31 der 42 Protokolle
mit Vermerken stimmt die Zahl der Ergebnisbloecke im PDF mit der Zahl der
gespeicherten Abstimmungen ueberein. Dann ist der k-te Block die k-te
Abstimmung. Die uebrigen Protokolle enthalten Sammelvoten, in denen mehrere
Protokollbeschluesse zu einem Eintrag zusammengefasst sind — dort verrutscht
die Zaehlung.

Die Textfassungen der PDFs erwartet das Skript in $VERMERK_TXT.
Aufruf ohne Argument = Probelauf, --apply schreibt.
"""
import re, glob, json, os, sys, collections

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')
TXT = os.environ.get('VERMERK_TXT')
PRE = {'SR': 'sr', 'BPU': 'bpu', 'HVF': 'hvfa'}

REASON = [(re.compile(r'persönlich', re.I), 'beteiligung'),
          (re.compile(r'kurz(fristig|zeitig|er)', re.I), 'kurzfristig abwesend')]

# Vermerke ohne Personenbezug oder anderweitig schon erfasst
SKIP = re.compile(r'2/3 Mehrheit|Namentliche Abstimmung|enthalten')

# Gleiche Nachnamen: der Titel traegt das Geschlecht, sonst der Vorname
AMBIG = {'becher': {'in': 'becher_a', '': 'becher_j',
                    'alexandra': 'becher_a', 'johannes': 'becher_j'},
         'linz':   {'in': 'linz_karin', '': 'linz_kilian',
                    'karin': 'linz_karin', 'kilian': 'linz_kilian'}}


def active(m, d):
    sp = m.get('periods') or [{'from': m.get('from'), 'to': m.get('to')}]
    return any((s.get('from') or '0') <= d and (not s.get('to') or s['to'] >= d) for s in sp)


def _add(token, hint, surnames, found, seen, problems, body):
    key = token.lower().replace('von ', '')
    cands = surnames.get(key)
    if not cands:
        return
    if len(cands) > 1 or key in AMBIG:
        table = AMBIG.get(key)
        pick = None
        if table:
            for first, mid in table.items():
                if first not in ('in', '') and re.search(token + r'\s+' + first, body, re.I):
                    pick = mid
                    break
            if not pick:
                pick = table.get(hint)
        if not pick:
            problems.append('unklar: ' + token + ' in "' + body[:60] + '"')
            return
        mid = pick
    else:
        mid = cands[0]['id']
    if mid not in seen:
        seen.add(mid)
        found.append(mid)


def resolve(text, members, date, problems):
    live = [m for m in members if active(m, date)]
    surnames = collections.defaultdict(list)
    for m in live:
        for key in {m['lastName'].lower(), m['lastName'].lower().replace('von ', '')}:
            surnames[key].append(m)
        if m.get('nee'):
            surnames[m['nee'].lower()].append(m)

    found, seen, done = [], set(), set()
    body = re.sub(r'\s+', ' ', text)
    # Weibliche Anrede zuerst — sie entscheidet bei gleichen Nachnamen
    for m in re.finditer(r'(?:StRin|Bürgermeisterin)\s+(?:Dr\.\s+)?((?:von\s+)?[A-ZÄÖÜ][\wäöüß-]+)', body):
        _add(m.group(1), 'in', surnames, found, seen, problems, body)
        done.add(m.group(1).lower().replace('von ', ''))
    for token in re.findall(r'(?:von\s+)?(?:Dr\.\s+)?\b[A-ZÄÖÜ][\wäöüß-]+\b', body):
        # Per Anrede bereits aufgeloest — sonst kippt "StRin Linz" zusaetzlich
        # auf den gleichnamigen Kollegen
        if token.lower().replace('von ', '') in done:
            continue
        _add(token, '', surnames, found, seen, problems, body)
    return found


def scope(text):
    """Wie viele Beschluesse deckt der Vermerk, rueckwaerts gezaehlt."""
    m = re.search(r'Beschlüssen\s+1\s+bis\s+(\d+)', text)
    if m:
        return int(m.group(1))
    if re.search(r'beiden Beschlüssen|beide Beschlüsse', text):
        return 2
    if re.search(r'bei Beschluss \d', text):
        return 0          # Bezug unklar, wird uebersprungen
    return 1


def blocks(path):
    """Ergebnisbloecke einer Niederschrift, jeder mit den ihm folgenden Vermerken."""
    t = open(path, encoding='utf-8', errors='replace').read()
    t = re.sub(r'\n\s*\d+\..{0,80}Sitzung.{0,80}vom \d\d\.\d\d\.\d{4}\s+Seite \d+\s*\n', '\n', t)
    seq, cur = [], None
    for m in re.finditer(r'(Abstimmungsvermerke?:\s*(?:.+?)(?=\n\s*\n))|'
                         r'((?:Beschlossen|Abgelehnt)\s*:?\s*Ja:\s*\d+\s+Nein:\s*\d+)', t, re.S):
        if m.group(2):
            if cur is not None:
                seq.append(cur)
            cur = []
        elif cur is not None:
            cur.append(' '.join(m.group(1).split()).replace('- ', '').split(':', 1)[1].strip())
    if cur is not None:
        seq.append(cur)
    return seq


def main():
    do_apply = '--apply' in sys.argv
    md = json.load(open(os.path.join(DATA, 'members.json'), encoding='utf-8'))
    vpath = os.path.join(DATA, 'votes.json')
    votes = json.load(open(vpath, encoding='utf-8'))
    by = collections.defaultdict(list)
    for v in votes:
        by[v['sessionId']].append(v)

    problems, hits, corrections = [], [], []
    for f in sorted(glob.glob(os.path.join(TXT, '*.txt'))):
        p, d = os.path.basename(f)[:-4].split('_')
        sess = by.get(PRE[p] + '_' + d)
        if not sess:
            continue
        seq = blocks(f)
        if len(seq) != len(sess):
            continue

        for i, (blk, v) in enumerate(zip(seq, sess)):
            for raw in blk:
                # Am Satzende abschneiden, sonst laeuft der naechste TOP mit
                cut = re.split(r'(?<=teilgenommen\.)|(?<=beteiligt\.)|(?<=anwesend\.)', raw)[0]
                if SKIP.search(cut) or v.get('excluded'):
                    continue
                reason = next((r for rx, r in REASON if rx.search(cut)), None)
                if not reason:
                    problems.append(v['id'] + ': kein Grund erkannt — ' + cut[:70])
                    continue
                span = scope(cut)
                if span == 0:
                    problems.append(v['id'] + ': Bezug auf einzelnen Beschluss unklar — ' + cut[:70])
                    continue
                ids = resolve(cut, md['members'], v['date'], problems)
                if not ids:
                    problems.append(v['id'] + ': keine Person erkannt — ' + cut[:70])
                    continue
                for target in sess[max(0, i - span + 1): i + 1]:
                    ex = target.setdefault('excluded', [])
                    for mid in ids:
                        if any(e['member'] == mid for e in ex):
                            continue
                        ex.append({'member': mid, 'reason': reason})
                        r = target['results']
                        # Benannte Voten wurden aus der Anwesenheit erzeugt und
                        # zaehlen den Vermerkten faelschlich als Ja-Stimme
                        if target['type'] == 'named':
                            for side in ('yes', 'no'):
                                if mid in r[side]:
                                    r[side].remove(mid)
                                    r['absent'].append(mid)
                                    corrections.append(target['id'] + ': ' + mid + ' ' + side + ' -> absent')
                    hits.append((target['id'], reason, ','.join(ids)))

    print(str(len(hits)) + ' Zuordnungen in ' + str(len({h[0] for h in hits})) + ' Abstimmungen')
    print('  ' + str(dict(collections.Counter(h[1] for h in hits))))
    if corrections:
        print('\n' + str(len(corrections)) + ' Korrekturen an benannten Voten:')
        for c in corrections:
            print('   ' + c)
    if problems:
        print('\n' + str(len(problems)) + ' ungeklaert:')
        for p in problems:
            print('   ' + p)
    if do_apply:
        with open(vpath, 'w', encoding='utf-8') as fh:
            json.dump(votes, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print('\ngeschrieben')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
