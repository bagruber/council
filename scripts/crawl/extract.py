"""Liest die Archivkopien und zieht heraus, was ueber Abstimmungen drinsteht.

Der Weg geht ueber die Sitzung, nicht ueber den einzelnen Beschluss. Ein
Lokalartikel berichtet fast immer von einem ganzen Sitzungsabend und
handelt darin drei, vier Tagesordnungspunkte ab. Wer je Beschluss sucht,
findet deshalb wenig; wer das Erscheinungsdatum an die Sitzungsdaten
haelt, findet den Artikel und ordnet die Fundstellen anschliessend den
TOPs zu.

Gesucht wird nicht "irgendwo ein Name", sondern ein Name im Umfeld einer
Abstimmungsformulierung. Lokalzeitungen schreiben das in wenigen immer
gleichen Wendungen: "gegen die Stimmen von", "einzige Gegenstimme",
"X stimmte dagegen", "bei zwei Enthaltungen". Der Beleg-Satz wird
mitgeschrieben, damit die Zuordnung nachpruefbar bleibt.

Nichts hiervon wird eingetragen. Ausgabe ist ein Vorschlag mit Beleg.

Aufruf:
    python scripts/crawl/extract.py --report
    python scripts/crawl/extract.py --window 10 --report
"""
import json, os, re, argparse, html, datetime, gzip, zlib

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(BASE, 'data')
CRAWL = os.path.join(DATA, 'crawl')
CACHE = os.path.join(CRAWL, 'cache')

UML = str.maketrans({'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
                     'Ä': 'ae', 'Ö': 'oe', 'Ü': 'ue'})


def fold(s):
    return s.translate(UML).lower()


# Wendungen, die im Lokalteil eine Abstimmung markieren. Die Gruppe
# entscheidet, wie ein danebenstehender Name gelesen wird.
CUES = [
    ('no',      r'einzige[nr]? Gegenstimme|Gegenstimmen? (?:kam|kamen|von)|'
                r'stimmten? (?:allein |als einzige[rs]? )?dagegen|votierten? dagegen|'
                r'gegen die Stimmen? (?:von|des|der)|dagegen stimmten?|'
                r'waren? dagegen|Nein-Stimmen?|sprachen? sich .{0,30}dagegen aus'),
    ('yes',     r'stimmten? (?:daf[üu]r|zu)|votierten? daf[üu]r|'
                r'mit den Stimmen (?:von|der)|sprachen? sich .{0,25}daf[üu]r aus|'
                r'bef[üu]rworteten?|unterst[üu]tzten?'),
    ('abstain', r'enthielt sich|enthielten sich|Enthaltung(?:en)?|enth[äa]lt sich'),
]
CUE_RE = [(k, re.compile(p, re.I)) for k, p in CUES]

# Der Unterschied, auf den es beim Nachpruefen ankommt: "gegen die Stimmen
# von X" ist ein Abstimmungsergebnis, "X befuerwortete" ist eine Wortmeldung.
# Beides steht im selben Artikel, nur das erste traegt einen Eintrag.
HART = re.compile(r'Gegenstimmen?|stimmten? (?:dagegen|daf[üu]r|zu)|votierten?|'
                  r'gegen die Stimmen|enthielt sich|enthielten sich|Enthaltung|'
                  r'mit den Stimmen|Nein-Stimmen?|Ja-Stimmen?', re.I)

# Ergebniszahlen im Fliesstext: "mit 12:8 Stimmen", "mit 15 zu 3"
TALLY = re.compile(r'(\d{1,2})\s*:\s*(\d{1,2})\s*Stimmen|'
                   r'mit\s+(\d{1,2})\s+zu\s+(\d{1,2})\s*(?:Stimmen)?', re.I)

# Woerter, an denen ein Artikel nach Ratsarbeit aussieht
RAT = re.compile(r'stadtrat|gremium|beschlo|abgelehnt|abgestimmt|abstimmung|'
                 r'mehrheit|gegenstimme|einstimmig|sitzung|b[üu]rgermeister', re.I)


def strip_html(raw):
    # Das Archiv gibt unter id_ die Originalantwort zurueck, also auch
    # deren Kompression.
    if raw[:2] == b'\x1f\x8b':
        try:
            raw = gzip.decompress(raw)
        except Exception:
            pass
    elif raw[:1] == b'\x78':
        try:
            raw = zlib.decompressobj().decompress(raw)
        except Exception:
            pass
    s = raw.decode('utf-8', 'replace')
    s = re.sub(r'(?is)<(script|style|noscript|nav|footer|aside)[^>]*>.*?</\1>', ' ', s)
    date = meta_date(s)
    s = re.sub(r'(?is)<div id="wm-ipp.*?</div>\s*</div>', ' ', s)   # Archiv-Leiste
    s = re.sub(r'(?s)<[^>]+>', ' ', s)
    s = html.unescape(s)
    return re.sub(r'\s+', ' ', s), date


def meta_date(s):
    for pat in (r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})',
                r'property="article:published_time"\s+content="(\d{4}-\d{2}-\d{2})',
                r'name="date"\s+content="(\d{4}-\d{2}-\d{2})',
                r'<meta[^>]+content="(\d{4}-\d{2}-\d{2})[^"]*"[^>]+itemprop="datePublished"',
                r'<time[^>]+datetime="(\d{4}-\d{2}-\d{2})'):
        m = re.search(pat, s, re.I)
        if m:
            return m.group(1)
    return None


def sentences(text):
    return re.split(r'(?<=[.!?])\s+(?=[A-ZÄÖÜ„])', text)


def find_names(sentence, members):
    """Nachnamen im Satz. Mehrdeutige (zwei Becher, zwei Linz) werden
    markiert statt geraten."""
    by_last = {}
    for m in members:
        # Aeltere Artikel fuehren den Geburtsnamen. Verena Beibl steht 2021
        # als Verena Kuch in der Zeitung - ohne `nee` faellt sie durch.
        for ln in filter(None, (m['lastName'], m.get('nee'))):
            if re.search(r'(?<![A-Za-zÄÖÜäöüß])' + re.escape(ln) + r'(?![A-Za-zäöüß])', sentence):
                by_last.setdefault(m['lastName'], []).append(m)
                break
    out = []
    for ln, group in by_last.items():
        if len(group) == 1:
            g = group[0]
            out.append({'id': g['id'], 'name': ln, 'party': g.get('party'),
                        'ambiguous': False})
            continue
        named = [g for g in group if g.get('firstName') and g['firstName'] in sentence]
        if len(named) == 1:
            g = named[0]
            out.append({'id': g['id'], 'name': ln, 'party': g.get('party'),
                        'ambiguous': False})
        else:
            out.append({'id': None, 'name': ln, 'ambiguous': True,
                        'candidates': [g['id'] for g in group]})
    return out


def scan(text, members):
    out = []
    for s in sentences(text):
        if len(s) > 700:
            continue
        cues = [k for k, r in CUE_RE if r.search(s)]
        if not cues:
            continue
        names = find_names(s, members)
        if not names:
            continue
        out.append({'position': cues[0], 'allCues': cues, 'names': names,
                    'evidence': 'hart' if HART.search(s) else 'weich',
                    'sentence': s.strip()})
    return out


def tallies(text):
    out = []
    for m in TALLY.finditer(text):
        g = [x for x in m.groups() if x]
        if len(g) == 2 and int(g[0]) <= 30 and int(g[1]) <= 30:
            out.append('%s:%s' % (g[0], g[1]))
    return sorted(set(out))


def keywords_of(vote):
    """Substantive aus Titel und Beschlusstext, gefaltet."""
    ws = re.findall(r'[A-ZÄÖÜ][A-Za-zÄÖÜäöüß\-]{4,}', (vote['title'] or '') + ' ' + (vote.get('text') or ''))
    return {fold(w) for w in ws} - {
        'stadtrat', 'moosburg', 'beschluss', 'antrag', 'stadt', 'beschlussfassung'}


def tally_of(vote):
    """Bei namentlichen Voten stehen in results Listen, bei anonymen Zahlen."""
    r = vote.get('results') or {}
    y, n = r.get('yes'), r.get('no')
    if isinstance(y, list):
        return len(y), len(n or [])
    return y, n


def best_votes(text, votes, top=3):
    """Welche TOPs dieser Sitzung kommen im Artikel vor."""
    ft = fold(text)
    scored = []
    for v in votes:
        kws = keywords_of(v)
        hit = [k for k in kws if len(k) >= 6 and k[:8] in ft]
        if hit:
            scored.append((len(hit), v, hit))
    scored.sort(key=lambda x: -x[0])
    out = []
    for n, v, h in scored[:top]:
        y, no = tally_of(v)
        out.append({'voteId': v['id'], 'title': v['title'], 'yes': y, 'no': no,
                    'type': v['type'], 'hasVoters': bool(v.get('voters')),
                    'open': v['type'] == 'anonymous' and not v.get('voters'),
                    'matched': sorted(h)[:6], 'score': n})
    return out


def article_id(url):
    """Die Nummer am Ende der URL. Sie ueberlebt jede Schlagzeilenaenderung
    und ist damit die einzige stabile Kennung eines Artikels."""
    m = re.search(r'(?:art-|-)(\d{5,9})(?:\.html)?$|li\.(\d+)$|lux\.(\w+)$', url)
    return next((g for g in m.groups() if g), url) if m else url


def cachefile(url):
    return os.path.join(CACHE, re.sub(r'\W+', '_', url)[-120:] + '.html')


def load():
    votes = json.load(open(os.path.join(DATA, 'votes.json'), encoding='utf-8'))
    sess = json.load(open(os.path.join(DATA, 'sessions.json'), encoding='utf-8'))
    mem = json.load(open(os.path.join(DATA, 'members.json'), encoding='utf-8'))['members']
    press = json.load(open(os.path.join(DATA, 'press.json'), encoding='utf-8'))
    index = json.load(open(os.path.join(CRAWL, 'index.json'), encoding='utf-8'))
    url_media = {}
    for media, items in index.items():
        for a in items:
            url_media[cachefile(a['url'])] = (media, a['url'])
    return votes, sess, mem, press, url_media


def members_at(members, date):
    return [m for m in members
            if not (m.get('from') and m['from'] > date)
            and not (m.get('to') and m['to'] < date)]


def run(window=14):
    votes, sessions, members, press, url_media = load()
    by_session = {}
    for v in votes:
        by_session.setdefault(v['sessionId'], []).append(v)
    known_urls = {p['url'] for p in press}

    results = []
    for fn in sorted(os.listdir(CACHE)):
        path = os.path.join(CACHE, fn)
        media, url = url_media.get(path, (None, None))
        if not url:
            continue
        text, pub = strip_html(open(path, 'rb').read())
        if len(text) < 500 or not RAT.search(text):
            continue
        if not pub:
            continue
        pd = datetime.date.fromisoformat(pub)
        # Welche Sitzung liegt kurz davor?
        near = []
        for s in sessions:
            d = (pd - datetime.date.fromisoformat(s['date'])).days
            if 0 <= d <= window:
                near.append((d, s))
        if not near:
            continue
        near.sort()
        stmts = scan(text, members_at(members, near[0][1]['date']))
        entry = {'media': media, 'url': url, 'published': pub,
                 'inPress': url in known_urls,
                 'headline': re.sub(r'-', ' ', url.rstrip('/').rsplit('/', 1)[-1])[:120],
                 'tallies': tallies(text), 'chars': len(text),
                 'sessions': [], 'statements': stmts}
        for d, s in near[:2]:
            entry['sessions'].append({
                'sessionId': s['id'], 'date': s['date'], 'type': s['type'],
                'daysAfter': d,
                'votes': best_votes(text, by_session.get(s['id'], []))})
        results.append(entry)

    # Dieselbe Meldung steht im Archiv oft mehrfach: die Zeitung aendert die
    # Schlagzeile, der Slug aendert sich mit, die Artikelnummer bleibt. Ohne
    # das hier taucht ein Fund zweimal im Bericht auf.
    best = {}
    for r in results:
        key = (r['media'], article_id(r['url']))
        if key not in best or r['chars'] > best[key]['chars']:
            best[key] = r
    out = list(best.values())
    out.sort(key=lambda r: (not r['statements'], r['published']))
    return out


def report(rows):
    # Aussortiertes bleibt aussortiert - siehe data/knowledge/presse-verworfen.md
    vpath = os.path.join(CRAWL, 'verworfen.json')
    if os.path.exists(vpath):
        weg = {x['url'] for x in json.load(open(vpath, encoding='utf-8'))}
        rows = [r for r in rows if r['url'] not in weg]
    L = ['# Presserecherche: Fundstellen zum Stimmverhalten\n',
         'Erzeugt %s aus Archivkopien (Internet Archive). '
         'Nichts davon ist in die Daten eingetragen.\n' % datetime.date.today().isoformat()]

    def hard(r):
        return any(s['evidence'] == 'hart' for s in r['statements'])

    belegt = [r for r in rows if hard(r)]
    wortmeldung = [r for r in rows if r['statements'] and not hard(r)]
    linkonly = [r for r in rows if not r['statements']]

    L.append('\n%d Artikel mit Abstimmungssatz und Namen, %d nur mit Wortmeldung, '
             '%d weitere zu einer Sitzung ohne Namen.\n'
             % (len(belegt), len(wortmeldung), len(linkonly)))

    def head(r):
        L.append('\n### %s · %s%s' % (r['published'], r['media'],
                                      ' · schon in press.json' if r['inPress'] else ''))
        L.append('%s' % r['url'])
        for s in r['sessions']:
            L.append('- Sitzung %s (%s, +%d Tage)' % (s['sessionId'], s['type'], s['daysAfter']))
            for v in s['votes']:
                flag = 'offen' if v['open'] else ('namentlich' if v['type'] == 'named'
                                                  else 'teilbekannt')
                L.append('  - `%s` %s:%s [%s] — %s' % (v['voteId'], v['yes'], v['no'],
                                                       flag, v['title'][:70]))
        if r['tallies']:
            L.append('- Zahlen im Text: %s' % ', '.join(r['tallies']))

    def says(r, limit=420):
        for st in sorted(r['statements'], key=lambda x: x['evidence'] != 'hart'):
            who = ', '.join(n['name'] + ('(?)' if n['ambiguous'] else '') for n in st['names'])
            L.append('- [%s] **%s** → %s\n  > %s'
                     % (st['evidence'], st['position'], who, st['sentence'][:limit]))

    L.append('\n---\n\n## Stimmverhalten belegt\n')
    L.append('Der Satz nennt eine Abstimmung, nicht nur eine Wortmeldung.\n')
    for r in belegt:
        head(r)
        says(r)

    L.append('\n---\n\n## Nur Wortmeldung\n')
    L.append('Wer etwas befuerwortet hat, muss nicht dafuer gestimmt haben. '
             'Als Beleg fuer eine Position taugt das nicht, als Hinweis schon.\n')
    for r in wortmeldung:
        head(r)
        says(r, 300)

    L.append('\n---\n\n## Nur Sitzungsbezug, kein Name im Text\n')
    L.append('Kandidaten fuer press.json und die Themen-Timeline, ohne Stimmverhalten.\n')
    for r in linkonly:
        s = r['sessions'][0]
        vs = ', '.join(v['voteId'] for v in s['votes']) or '-'
        L.append('- %s %s +%dT · %s\n  %s\n  TOPs: %s'
                 % (r['published'], r['media'], s['daysAfter'], s['sessionId'], r['url'], vs))
    return '\n'.join(L)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--window', type=int, default=14, help='Tage zwischen Sitzung und Artikel')
    ap.add_argument('--report', action='store_true')
    a = ap.parse_args()

    rows = run(a.window)
    dest = os.path.join(CRAWL, 'findings.json')
    json.dump(rows, open(dest, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n = sum(len(r['statements']) for r in rows)
    print('%d Artikel einer Sitzung zugeordnet, %d Fundstellen -> %s' % (len(rows), n, dest))
    if a.report:
        rp = os.path.join(CRAWL, 'BERICHT.md')
        open(rp, 'w', encoding='utf-8').write(report(rows))
        print('->', rp)
