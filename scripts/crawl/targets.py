"""Waehlt Abstimmungen aus, fuer die eine Presserecherche etwas bringen kann,
und baut daraus Suchanfragen.

Presse nennt Namen fast nur dort, wo es strittig war: die eine Gegenstimme,
das knappe Ergebnis, der abgelehnte Antrag. Einstimmiges steht als Randnotiz
in der Zeitung, wenn ueberhaupt. Entsprechend wird sortiert.

Aufruf:
    python scripts/crawl/targets.py            # Top 40 auf die Konsole
    python scripts/crawl/targets.py --json     # data/crawl/targets.json
    python scripts/crawl/targets.py --limit 80 --since 2023-01-01
"""
import json, os, re, sys, argparse

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(BASE, 'data')

# Woerter, die in jeder zweiten Beschlussvorlage stehen und als Suchbegriff
# nichts eingrenzen.
NOISE = set("""
der die das den dem des ein eine einer eines einem einen und oder aber auch
fuer für von vom zu zum zur mit nach bei bis aus auf in im an am als ist sind
wird werden wurde wurden hat haben nicht kein keine sowie sich es er sie ueber
über gegen ohne durch um vor unter zwischen dass beschliesst beschließt
beschluss beschlussfassung stadtrat stadtrates stadtrat's gremium antrag
antrags antraege anträge vorlage sitzung tagesordnungspunkt top erteilt
erteilung stimmt zustimmung zugestimmt kenntnis genommen billigt billigung
gemaess gemäß abs art nr bzw ggf ca weiteren weitere weiterer folgende
folgenden jeweils sowohl bereits dazu hierzu davon daran wegen mehr neue neuen
neuer neues stadt moosburg moosburger stadtverwaltung verwaltung
""".split())

# Sachbegriffe, die eine Suche wirklich traegt. Wird aus Titel + Text gezogen.
WORD = re.compile(r'[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß0-9\-]{3,}')


def keywords(vote, limit=5):
    """Substantive aus Titel zuerst, dann aus dem Beschlusstext auffuellen."""
    out, seen = [], set()
    for field, cap in (('title', limit), ('text', limit + 2)):
        for w in WORD.findall(vote.get(field) or ''):
            low = w.lower().strip('-')
            if low in NOISE or low in seen or len(low) < 4:
                continue
            # Eigennamen und Grossgeschriebenes sind die brauchbaren Anker
            if not w[0].isupper():
                continue
            seen.add(low)
            out.append(w.strip('-'))
            if len(out) >= cap:
                break
        if len(out) >= limit:
            break
    return out[:limit]


def score(vote, session):
    """Wie wahrscheinlich ist es, dass die Zeitung hier Namen genannt hat."""
    r = vote.get('results') or {}
    yes, no = r.get('yes') or 0, r.get('no') or 0
    if no == 0:
        return 0
    total = yes + no
    s = 40 * (min(yes, no) / total if total else 0)
    if no <= 2:
        s += 25          # "einzige Gegenstimme" ist die haeufigste Presseform
    if yes <= 2:
        s += 25          # abgelehnter Antrag, die Ja-Seite wird genannt
    if vote.get('topicId'):
        s += 10
    if (session or {}).get('type') == 'stadtrat':
        s += 15          # Ausschuesse werden selten besetzt berichtet
    if not vote.get('voters'):
        s += 10
    return round(s, 1)


# Wonach in den drei Blaettern gesucht wird. Die Sitesuche von merkur.de ist
# per robots.txt gesperrt, deshalb laeuft merkur ueber die Suchmaschine.
OUTLETS = {
    'mz':     {'name': 'Moosburger Zeitung (idowa)', 'site': 'idowa.de'},
    'merkur': {'name': 'Freisinger Tagblatt (merkur)', 'site': 'merkur.de'},
    'sz':     {'name': 'Süddeutsche Zeitung', 'site': 'sueddeutsche.de'},
}


def queries(vote, kws):
    """Pro Blatt zwei Anfragen: eng am Beschluss, und breiter auf die Sitzung."""
    date = vote['date']
    tight = ' '.join(kws[:3])
    wide = ' '.join(kws[:2])
    out = []
    for media, o in OUTLETS.items():
        out.append({'media': media,
                    'q': f'site:{o["site"]} Moosburg {tight}'})
        out.append({'media': media,
                    'q': f'site:{o["site"]} Moosburg Stadtrat {wide} {date[:4]}'})
    return out


def load():
    votes = json.load(open(os.path.join(DATA, 'votes.json'), encoding='utf-8'))
    sess = {s['id']: s for s in json.load(open(os.path.join(DATA, 'sessions.json'), encoding='utf-8'))}
    press = json.load(open(os.path.join(DATA, 'press.json'), encoding='utf-8'))
    return votes, sess, press


def build(limit=40, since=None, until=None):
    votes, sess, press = load()
    # Tage, zu denen schon ein Artikel im Bestand liegt - dort ist die Lage
    # bekannt, das muss die Recherche nicht nochmal aufrollen.
    covered = {p['date'] for p in press}

    rows = []
    for v in votes:
        if v['type'] == 'named' or v.get('voters'):
            continue
        if since and v['date'] < since:
            continue
        if until and v['date'] > until:
            continue
        s = sess.get(v['sessionId'])
        sc = score(v, s)
        if sc <= 0:
            continue
        kws = keywords(v)
        if not kws:
            continue
        rows.append({
            'voteId': v['id'],
            'sessionId': v['sessionId'],
            'date': v['date'],
            'body': (s or {}).get('type'),
            'title': v['title'],
            'results': v.get('results'),
            'topicId': v.get('topicId'),
            'score': sc,
            'alreadyCovered': v['date'] in covered,
            'keywords': kws,
            'queries': queries(v, kws),
        })
    rows.sort(key=lambda r: -r['score'])
    return rows[:limit]


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=40)
    ap.add_argument('--since')
    ap.add_argument('--until')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    rows = build(a.limit, a.since, a.until)
    if a.json:
        out = os.path.join(DATA, 'crawl', 'targets.json')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        json.dump(rows, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f'{len(rows)} Ziele -> {out}')
    else:
        for r in rows:
            res = r['results'] or {}
            mark = ' [Tag schon belegt]' if r['alreadyCovered'] else ''
            print(f"{r['score']:5.1f}  {r['date']}  {r['body'] or '?':8s} "
                  f"{res.get('yes')}:{res.get('no')}  {r['voteId']}{mark}")
            print(f"        {r['title'][:88]}")
            print(f"        Begriffe: {', '.join(r['keywords'])}")
