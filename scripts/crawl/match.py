"""Ordnet Artikel aus dem Archivindex den Zielabstimmungen zu.

Der Slug einer Lokalzeitungs-URL ist die Schlagzeile in Kleinbuchstaben.
Damit laesst sich ohne einen einzigen Seitenabruf entscheiden, welche
Artikel ueberhaupt in Frage kommen - das spart Traffic und haelt die
Zahl der spaeter geholten Seiten klein.

Zwei Eigenheiten des Deutschen muessen dafuer weg:

  Umlaute   Slugs schreiben "gebuehren", die Beschlussvorlage "Gebühren".
  Komposita "Badegebuehren" im Beschluss, "freibad-preise" im Slug. Ein
            Vergleich ganzer Woerter findet das nie, deshalb wird auch
            auf Wortstaemmen ab fuenf Zeichen verglichen.

Das Datum kommt bei merkur aus der Artikelnummer: sie laeuft monoton mit
der Zeit, und press.json liefert genug Stuetzstellen, um zwischen ihnen
zu interpolieren. Bei den anderen Blaettern bleibt der erste Archivabruf
die Obergrenze - genauer wird es erst in extract.py am Artikel selbst.

Aufruf:
    python scripts/crawl/match.py
    python scripts/crawl/match.py --window 30 --min-score 2
"""
import json, os, re, argparse, datetime

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(BASE, 'data')
CRAWL = os.path.join(DATA, 'crawl')

UML = str.maketrans({'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
                     'Ä': 'ae', 'Ö': 'oe', 'Ü': 'ue'})


def fold(s):
    return s.translate(UML).lower()


def tokens(s):
    return [t for t in re.split(r'[^a-z0-9]+', fold(s)) if len(t) > 2]


def overlap(kw, slug_tokens):
    """Wie viele Beschluss-Schlagworte stecken im Slug. Treffer auf dem
    Wortstamm zaehlen halb, ganze Woerter voll."""
    score, hit = 0.0, []
    for k in kw:
        f = fold(k)
        if f in slug_tokens:
            score += 1.0
            hit.append(k)
            continue
        stem = f[:6] if len(f) >= 6 else f
        if len(stem) >= 5 and any(stem in t or t[:6] == stem for t in slug_tokens):
            score += 0.5
            hit.append(k + '~')
    return score, hit


def merkur_dater(press):
    """Stuetzstellen Artikelnummer -> Datum, linear dazwischen."""
    pts = []
    for p in press:
        if p['media'] != 'merkur':
            continue
        m = re.search(r'-(\d{7,9})\.html', p['url'])
        if m:
            pts.append((int(m.group(1)),
                        datetime.date.fromisoformat(p['date']).toordinal()))
    pts.sort()

    def est(url):
        m = re.search(r'-(\d{7,9})\.html', url)
        if not m or not pts:
            return None
        i = int(m.group(1))
        if i < pts[0][0] or i > pts[-1][0]:
            return None
        for (a, da), (b, db) in zip(pts, pts[1:]):
            if a <= i <= b:
                frac = (i - a) / (b - a) if b > a else 0
                return datetime.date.fromordinal(round(da + frac * (db - da))).isoformat()
        return None
    return est


def run(window=28, min_score=1.5, per_vote=6):
    targets = json.load(open(os.path.join(CRAWL, 'targets.json'), encoding='utf-8'))
    index = json.load(open(os.path.join(CRAWL, 'index.json'), encoding='utf-8'))
    press = json.load(open(os.path.join(DATA, 'press.json'), encoding='utf-8'))
    known = {p['url'] for p in press}
    est_merkur = merkur_dater(press)

    pool = []
    for media, items in index.items():
        for a in items:
            pool.append({'media': media, 'url': a['url'],
                         'tokens': set(tokens(a['slug'])),
                         'slug': a['slug'], 'firstSeen': a['firstSeen'],
                         'estDate': est_merkur(a['url']) if media == 'merkur' else None})

    out = []
    for t in targets:
        vd = datetime.date.fromisoformat(t['date'])
        found = []
        for a in pool:
            s, hits = overlap(t['keywords'], a['tokens'])
            if s < min_score:
                continue
            # Datum: geschaetzt wo moeglich, sonst nur die Obergrenze aus
            # dem ersten Archivabruf pruefen.
            d = a['estDate']
            if d:
                delta = (datetime.date.fromisoformat(d) - vd).days
                if not (-4 <= delta <= window):
                    continue
                s += 2.0 if 0 <= delta <= 10 else 0.5
            else:
                fs = datetime.date(int(a['firstSeen'][:4]), int(a['firstSeen'][4:6]),
                                   int(a['firstSeen'][6:8]))
                if fs < vd:
                    continue        # archiviert bevor abgestimmt wurde
            if a['url'] in known:
                s += 0.25           # schon im Bestand, taugt als Kontrolle
            found.append({'media': a['media'], 'url': a['url'], 'slug': a['slug'],
                          'estDate': d, 'firstSeen': a['firstSeen'],
                          'score': round(s, 2), 'matched': hits,
                          'inPress': a['url'] in known})
        found.sort(key=lambda x: -x['score'])
        if found:
            out.append({'voteId': t['voteId'], 'date': t['date'], 'body': t['body'],
                        'title': t['title'], 'results': t['results'],
                        'keywords': t['keywords'], 'voteScore': t['score'],
                        'articles': found[:per_vote]})
    out.sort(key=lambda r: -(r['articles'][0]['score'] + r['voteScore'] / 20))
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--window', type=int, default=28, help='Tage nach der Sitzung')
    ap.add_argument('--min-score', type=float, default=1.5)
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()

    rows = run(a.window, a.min_score)
    dest = os.path.join(CRAWL, 'candidates.json')
    json.dump(rows, open(dest, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('%d Abstimmungen mit Artikelkandidaten -> %s' % (len(rows), dest))
    if not a.quiet:
        for r in rows[:20]:
            res = r['results'] or {}
            print('\n%s  %s  %s:%s  %s' % (r['date'], r['voteId'],
                                           res.get('yes'), res.get('no'), r['title'][:64]))
            for x in r['articles'][:3]:
                print('   %-6s %4.1f  %s  %s' % (x['media'], x['score'],
                                                 x['estDate'] or ('~' + x['firstSeen']),
                                                 x['slug'][:74]))
