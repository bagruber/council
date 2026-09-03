"""Baut einen Artikelindex fuer die drei Blaetter und holt Artikeltexte.

Zwei Wege, aus einem Grund: merkur.de sperrt in robots.txt alles ausser
einer Handvoll benannter Crawler (`User-agent: *` / `Disallow: /`). Ein
eigenes Skript gehoert nicht dazu. idowa und sueddeutsche.de erlauben den
Zugriff, ihre Archive sind aber nur wenige Wochen tief oder liegen hinter
JavaScript.

Deshalb laeuft die Suche ueber zwei oeffentliche, maschinell gedachte
Schnittstellen:

  CDX  - der URL-Index des Internet Archive. Liefert vollstaendige
         Artikel-URLs seit 2016, und die Slugs tragen die Schlagworte.
  GN   - der RSS-Ausgang von Google News. Liefert Schlagzeile und exaktes
         Erscheinungsdatum, auch fuer merkur.

Artikeltexte kommen aus den Archivkopien, nie vom Server des Verlags.

Aufruf:
    python scripts/crawl/fetch.py index
    python scripts/crawl/fetch.py news --limit 25
    python scripts/crawl/fetch.py text --limit 30
"""
import json, os, re, sys, time, argparse, urllib.parse, urllib.request, html
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CRAWL = os.path.join(BASE, 'data', 'crawl')
CACHE = os.path.join(CRAWL, 'cache')
UA = 'Mozilla/5.0 (compatible; council-research/1.0; lokale Recherche Stadtrat Moosburg)'

# Praefix im Archivindex je Blatt. merkur und idowa haben eigene
# Ortsressorts, die SZ nur ein Landkreisressort - dort wird auf
# "moosburg" im Slug gefiltert.
OUTLETS = {
    'merkur': ['merkur.de/lokales/freising/moosburg-ort29088*'],
    'mz':     ['idowa.de/regionen/moosburg*'],
    # Die SZ hat kein Ortsressort, nur den Landkreis, und drei
    # URL-Generationen (1.NNN, li.NNN, lux.XXX) nebeneinander.
    'sz':     ['sueddeutsche.de/muenchen/freising/moosburg*',
               'sueddeutsche.de/muenchen/freising/*moosburg*'],
}


def get(url, timeout=60, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': UA, 'Accept-Language': 'de-DE,de;q=0.9'})
            return urllib.request.urlopen(req, timeout=timeout).read()
        except Exception as e:
            if i == tries - 1:
                print('  ! %s %s' % (type(e).__name__, url[:90]), file=sys.stderr)
                return None
            time.sleep(2 + 3 * i)


def slug_of(url):
    tail = url.rstrip('/').rsplit('/', 1)[-1]
    tail = re.sub(r'\.html$', '', tail)
    tail = re.sub(r'-\d{5,}$|-?li\.\d+$|-?lux\.\w+$|-\d+\.\d+$', '', tail)
    return tail


def cmd_index(args):
    """CDX abfragen und die Artikel-URLs je Blatt ablegen."""
    os.makedirs(CRAWL, exist_ok=True)
    index = {}
    for media, patterns in OUTLETS.items():
        rows = []
        for pattern in patterns:
            url = ('http://web.archive.org/cdx/search/cdx?url=' + urllib.parse.quote(pattern)
                   + '&output=json&fl=original,timestamp&collapse=urlkey'
                   + '&filter=statuscode:200&limit=' + str(args.limit))
            raw = get(url, timeout=180)
            time.sleep(1)
            if raw and raw.strip().startswith(b'['):
                rows += json.loads(raw)[1:]
        seen, items = set(), []
        for original, ts in rows:
            u = original.split('?')[0].replace('http://', 'https://')
            u = u.replace(':80/', '/').replace('.amp.html', '.html')
            if not re.search(r'-\d{5,}(\.html)?$|li\.\d+$|lux\.\w+$', u):
                continue          # Ressort- und Blaetterseiten raus
            if media == 'sz' and 'moosburg' not in u.lower():
                continue
            if u in seen:
                continue
            seen.add(u)
            items.append({'url': u, 'slug': slug_of(u), 'firstSeen': ts[:8]})
        index[media] = items
        print('%s: %d Artikel im Archivindex' % (media, len(items)))
    out = os.path.join(CRAWL, 'index.json')
    json.dump(index, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('->', out)


MONTHS = dict(zip('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(),
                  ['%02d' % i for i in range(1, 13)]))


def rfc_date(s):
    m = re.search(r'(\d{1,2}) (\w{3}) (\d{4})', s or '')
    if not m:
        return ''
    return '%s-%s-%02d' % (m.group(3), MONTHS.get(m.group(2), '01'), int(m.group(1)))


def cmd_news(args):
    """Google News je Zielabstimmung: Schlagzeile und exaktes Datum."""
    targets = json.load(open(os.path.join(CRAWL, 'targets.json'), encoding='utf-8'))
    hits, seen = [], set()
    for t in targets[:args.limit]:
        for q in t['queries']:
            url = ('https://news.google.com/rss/search?q='
                   + urllib.parse.quote(q) + '&hl=de&gl=DE&ceid=DE:de')
            raw = get(url, timeout=40)
            time.sleep(args.delay)
            if not raw:
                continue
            body = raw.decode('utf-8', 'replace')
            for item in re.findall(r'<item>(.*?)</item>', body, re.S):
                def f(tag):
                    m = re.search(r'<' + tag + r'[^>]*>(.*?)</' + tag + r'>', item, re.S)
                    return html.unescape(m.group(1)).strip() if m else ''
                title, pub = f('title'), f('pubDate')
                if not title:
                    continue
                key = (t['voteId'], title)
                if key in seen:
                    continue
                seen.add(key)
                hits.append({'voteId': t['voteId'], 'voteDate': t['date'],
                             'media': q.split('site:')[1].split()[0],
                             'headline': re.sub(r'\s+-\s+[^-]+$', '', title),
                             'published': rfc_date(pub), 'query': q})
        n = sum(1 for h in hits if h['voteId'] == t['voteId'])
        print('%s: %d Treffer' % (t['voteId'], n))
    out = os.path.join(CRAWL, 'news.json')
    json.dump(hits, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(hits), '->', out)


# Slug-Woerter, an denen ein Artikel ueberhaupt erst nach Ratsarbeit
# aussieht. Ohne diesen Filter holt der Sweep auch Vereinsjubilaeen.
RAT = re.compile(r'stadtrat|stadtraet|stadtraetin|gremium|beschluss|beschliesst|'
                 r'beschlossen|abgelehnt|abgestimmt|abstimmung|mehrheit|gegenstimme|'
                 r'einstimmig|votum|votier|sitzung|antrag|antraege|debatt|streit|'
                 r'kritik|knapp|buergermeister|haushalt|gebuehren|satzung', re.I)


STREIT = re.compile(r'abgelehnt|gegenstimme|dagegen|knapp|mehrheit|einstimmig|'
                    r'umstritten|kontrovers|streit|kritik|debatt|zoff|aerger|'
                    r'aufregung|beschlossen|votum|entscheidung|kippt|scheitert|'
                    r'lehnt|stimmt', re.I)


def cmd_sweep(args):
    """Alle ratsbezogenen Artikel aus dem Index holen, nicht nur die zu
    einer bestimmten Abstimmung. Ein Artikel deckt meist eine ganze
    Sitzung ab - das findet mehr als die Suche je Beschluss."""
    os.makedirs(CACHE, exist_ok=True)
    index = json.load(open(os.path.join(CRAWL, 'index.json'), encoding='utf-8'))
    urls = []
    for media, items in index.items():
        if args.media and media != args.media:
            continue
        for a in items:
            if RAT.search(a['slug']):
                urls.append((a['url'], a['firstSeen']))
    todo = [x for x in urls if not os.path.exists(cachefile(x[0]))]
    # Die Archivkopien kommen langsam (Bandspeicher), deshalb zuerst das,
    # was nach Streit klingt - dort stehen die Namen.
    todo.sort(key=lambda x: -len(STREIT.findall(x[0])))
    print('%d ratsbezogen, %d noch zu holen' % (len(urls), len(todo)), flush=True)
    # Das Archiv antwortet je Seite in Sekunden, nicht Millisekunden.
    # Ein paar parallele Abrufe machen aus einer Stunde eine Viertelstunde,
    # mehr als eine Handvoll waere dem Archiv gegenueber unfein.
    todo = todo[:args.limit]
    done = [0, 0]

    def one(job):
        u, ts = job
        raw = snapshot(u, ts, args.delay)
        if raw:
            open(cachefile(u), 'wb').write(raw)
            done[1] += 1
        done[0] += 1
        if done[0] % 25 == 0:
            print('  %d/%d, %d geholt' % (done[0], len(todo), done[1]), flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(one, todo))
    print('fertig, %d geholt' % done[1])


def snapshot(url, timestamp, delay=0.7):
    """Rohfassung aus dem Archiv. Der Zeitstempel muss echt sein - eine
    Platzhalterangabe liefert 404 statt der naechstgelegenen Kopie.

    Haengt der Rechner an einem WLAN mit Anmeldeseite, antwortet nicht das
    Archiv, sondern das Portal - mit Status 200. Ungeprueft landen solche
    Seiten als Artikel im Cache."""
    raw = get('https://web.archive.org/web/%sid_/%s' % (timestamp, url), timeout=90, tries=2)
    time.sleep(delay)
    if raw and (b'hotsplots' in raw[:4000] or b'Hotspot Login' in raw[:4000]):
        print('  ! Anmeldeseite statt Archiv - WLAN pruefen', file=sys.stderr)
        return None
    return raw


def cachefile(url):
    return os.path.join(CACHE, re.sub(r'\W+', '_', url)[-120:] + '.html')


def cmd_text(args):
    """Archivkopien der Kandidatenartikel holen und ablegen."""
    os.makedirs(CACHE, exist_ok=True)
    cands = json.load(open(os.path.join(CRAWL, 'candidates.json'), encoding='utf-8'))
    urls = []
    for c in cands[:args.limit]:
        for a in c['articles']:
            if a['url'] not in urls:
                urls.append(a['url'])
    index = json.load(open(os.path.join(CRAWL, 'index.json'), encoding='utf-8'))
    stamp = {a['url']: a['firstSeen'] for items in index.values() for a in items}
    for i, u in enumerate(urls, 1):
        fn = cachefile(u)
        if os.path.exists(fn):
            continue
        raw = snapshot(u, stamp.get(u, '2024'), args.delay)
        if not raw:
            continue
        open(fn, 'wb').write(raw)
        print('%d/%d %s' % (i, len(urls), os.path.basename(fn)[:70]))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('index')
    p.add_argument('--limit', type=int, default=20000)
    p.set_defaults(fn=cmd_index)
    p = sub.add_parser('news')
    p.add_argument('--limit', type=int, default=25)
    p.add_argument('--delay', type=float, default=1.5)
    p.set_defaults(fn=cmd_news)
    p = sub.add_parser('sweep')
    p.add_argument('--limit', type=int, default=600)
    p.add_argument('--delay', type=float, default=1.0)
    p.add_argument('--media')
    p.add_argument('--workers', type=int, default=6)
    p.set_defaults(fn=cmd_sweep)
    p = sub.add_parser('text')
    p.add_argument('--limit', type=int, default=40)
    p.add_argument('--delay', type=float, default=1.5)
    p.set_defaults(fn=cmd_text)
    a = ap.parse_args()
    a.fn(a)
