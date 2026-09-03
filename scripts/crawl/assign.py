"""Ordnet Artikel ohne Namensnennung den Sitzungen und den TOPs zu, die sie
tatsaechlich behandeln.

Der naive Weg - zaehle, wie viele Woerter aus dem Beschluss im Artikel
vorkommen - taugt dafuer nicht. Er verbindet ein Abschiedsinterview mit
einem Radverkehrskonzept, weil beide "Freising" und "Landratsamt" enthalten,
und er zaehlt "Mehrfamilienhaus" und "Mehrfamilienhauses" als zwei Treffer.

Deshalb zwei Korrekturen:

Seltenheit  Ein Wort, das in 300 von 961 Beschluessen steht, sagt nichts
            darueber, welcher gemeint ist. Jeder Wortstamm wird mit
            log(N/df) gewichtet, wie bei einer Suchmaschine. "Bauleitplanung"
            faellt damit fast heraus, "Rockermaier" traegt.

Stammform   Vor dem Zaehlen werden Wortformen auf acht Zeichen gekuerzt und
            dedupliziert, sonst zaehlt jede Beugung einzeln.

Die Sitzungszuordnung ist die sichere: sie haengt nur am Erscheinungsdatum.
Die TOP-Zuordnung ist die riskante und bekommt deshalb eine Schwelle.

Aufruf:
    python scripts/crawl/assign.py                 # Probelauf mit Stichprobe
    python scripts/crawl/assign.py --min 3.5
    python scripts/crawl/assign.py --apply
"""
import json, os, re, math, gzip, html, argparse, collections

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(BASE, 'data')
CRAWL = os.path.join(DATA, 'crawl')

UML = str.maketrans({'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
                     'Ä': 'ae', 'Ö': 'oe', 'Ü': 'ue'})

# Woerter, die in jedem zweiten Lokalartikel stehen und deshalb nie ein
# Zuordnungsgrund sind - auch dann nicht, wenn sie im Beschluss vorkommen.
STOP = {'moosburg', 'freising', 'stadtrat', 'stadtraet', 'buergerm', 'landrats',
        'gemeinde', 'beschlus', 'sitzung', 'antrag', 'antraege', 'verwaltu',
        'gremium', 'ausschus', 'mitglied', 'vorsitze', 'gruenen', 'muenchen',
        'euro', 'jahr', 'jahre', 'stadt', 'bereich', 'rahmen', 'zukunft'}


def fold(s):
    return s.translate(UML).lower()


def stems(text, n=8):
    """Wortstaemme, gekuerzt und dedupliziert."""
    out = set()
    for w in re.findall(r'[a-zäöüß][a-zäöüß0-9\-]{4,}', fold(text)):
        s = w.replace('-', '')[:n]
        if len(s) >= 6 and s not in STOP:
            out.add(s)
    return out


def vote_stems(v):
    return stems((v['title'] or '') + ' ' + (v.get('text') or ''))


def build_idf(votes):
    df = collections.Counter()
    for v in votes:
        df.update(vote_stems(v))
    n = len(votes)
    return {s: math.log(n / c) for s, c in df.items()}, n


def name_stems(members):
    """Nachnamen taugen nicht zur Themenzuordnung. Ein Sitzungsbericht nennt
    ein Dutzend Raete, und in den Bestellungs-TOPs stehen dieselben Namen -
    danach passt der Artikel auf jeden Punkt des Abends."""
    out = set()
    for m in members:
        for n in filter(None, (m['lastName'], m.get('firstName'), m.get('nee'))):
            out |= stems(n, 8) | {fold(n)[:8]}
    return out


def headline(path):
    raw = open(path, 'rb').read()
    if raw[:2] == b'\x1f\x8b':
        try:
            raw = gzip.decompress(raw)
        except Exception:
            pass
    s = raw.decode('utf-8', 'replace')
    for pat in (r'<meta[^>]+property="og:title"[^>]+content="([^"]{6,200})"',
                r'<meta[^>]+content="([^"]{6,200})"[^>]+property="og:title"',
                r'<title[^>]*>([^<]{6,200})</title>'):
        m = re.search(pat, s, re.I)
        if m:
            t = html.unescape(m.group(1)).strip()
            # merkur und idowa haengen den Blattnamen an, das braucht die Liste nicht
            return re.sub(r'\s*[-|]\s*(Merkur|idowa|S[üu]ddeutsche)[^-|]*$', '', t)
    return None


def press_id(media, date, url):
    """{media}_{YYYY-MM-DD}_{slug} nach der Konvention aus CLAUDE.md."""
    tail = url.rstrip('/').rsplit('/', 1)[-1]
    # Zweimal: erst faellt ".html", danach erst steht die Nummer am Ende.
    for _ in range(2):
        tail = re.sub(r'\.html$|-\d{5,}$|-?li\.\d+$|-?lux\.\w+$', '', tail)
    words = [w for w in fold(tail).split('-')
             if len(w) > 3 and w not in STOP and not w.isdigit()][:3]
    return '%s_%s_%s' % (media, date, '-'.join(words) or 'artikel')


# Beim Durchsehen als falsch erkannt. Der Anker steht zwar in der Schlagzeile,
# meint dort aber etwas anderes: "Oeffnungszeiten" der Geschaefte trifft auf
# das "Oeffnen" einer Imbisshuette, und der Bericht ueber die Wahl der
# Buergermeister-Stellvertreter trifft auf Bestellungen zu ganz anderen Gremien.
AUSGESCHLOSSEN = {
    ('13791824', 'sr_20200525_11'),
    ('13750251', 'sr_20200504_14'),
    ('13750251', 'sr_20200504_08'),
}


def excluded(url, vid):
    return any(k in url and v == vid for k, v in AUSGESCHLOSSEN)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min', type=float, default=4.0,
                    help='Mindestgewicht fuer eine TOP-Zuordnung')
    ap.add_argument('--min-stems', type=int, default=2)
    ap.add_argument('--min-idf', type=float, default=2.0,
                    help='Woerter, die haeufiger als e^-x vorkommen, zaehlen nicht')
    ap.add_argument('--need-idf', type=float, default=4.0,
                    help='mindestens ein Wort muss so selten sein')
    ap.add_argument('--max-share', type=float, default=0.34,
                    help='Woerter in mehr als diesem Anteil der TOPs des Abends zaehlen nicht')
    ap.add_argument('--loose', action='store_true',
                    help='auch Artikel ohne TOP-Anker an die Sitzung haengen')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--sample', type=int, default=14)
    a = ap.parse_args()

    load = lambda n: json.load(open(os.path.join(DATA, n), encoding='utf-8'))
    votes, sessions, press = load('votes.json'), load('sessions.json'), load('press.json')
    members = load('members.json')['members']
    findings = json.load(open(os.path.join(CRAWL, 'findings.json'), encoding='utf-8'))
    idf, _ = build_idf(votes)
    names = name_stems(members)
    # Je Sitzung: in welchem Anteil ihrer TOPs kommt ein Wortstamm vor?
    share = {}
    by_sess = collections.defaultdict(list)
    for v in votes:
        by_sess[v['sessionId']].append(v)
    for sid, vs in by_sess.items():
        c = collections.Counter()
        for v in vs:
            c.update(vote_stems(v))
        share[sid] = {k: n / len(vs) for k, n in c.items()}
    vmap = {v['id']: v for v in votes}
    smap = {s['id']: s for s in sessions}
    known_url = {p['url']: p['id'] for p in press}

    # Artikeltexte einmal einlesen
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from extract import strip_html, cachefile

    # Was ein Mensch schon aussortiert hat, wird nicht wieder vorgelegt.
    vpath = os.path.join(CRAWL, 'verworfen.json')
    verworfen = {x['url'] for x in json.load(open(vpath, encoding='utf-8'))}         if os.path.exists(vpath) else set()

    plan = []
    for r in findings:
        if r['statements'] or r['url'] in verworfen:
            continue                    # von Hand durch oder verworfen
        path = cachefile(r['url'])
        if not os.path.exists(path):
            continue
        text, _ = strip_html(open(path, 'rb').read())
        art = stems(text)
        sess = r['sessions'][0]
        # Nicht jeder Artikel, der kurz nach einer Sitzung erscheint, handelt
        # von ihr. Wahlkampfberichte und Portraets nennen den Stadtrat auch.
        # Verlangt wird deshalb ein Sachbegriff, der die Schlagzeile mit der
        # Tagesordnung dieses Abends verbindet.
        agenda_stems = set()
        for v in vmap.values():
            if v['sessionId'] == sess['sessionId']:
                agenda_stems |= vote_stems(v)
        head = stems(r['url'].rsplit('/', 1)[-1].replace('-', ' ')) - names
        if not any(idf.get(s, 0) >= a.need_idf
                   for s in (agenda_stems & (head | art)) - names):
            continue
        tops = []
        for v in vmap.values():
            if v['sessionId'] != sess['sessionId']:
                continue
            hit = (vote_stems(v) & art) - names
            # Haeufige Woerter summieren sich sonst zu einem Treffer auf, den
            # kein einzelnes von ihnen traegt. Wer unter der Grenze liegt,
            # zaehlt gar nicht mit.
            hit = {s for s in hit if idf.get(s, 0) >= a.min_idf}
            # Und was in der halben Tagesordnung dieses Abends steht, sagt
            # nichts darueber, welcher Punkt gemeint ist. "Stellvertreter" ist
            # ueber alle Sitzungen selten und in der konstituierenden Sitzung
            # trotzdem wertlos, weil es dort in jedem zweiten TOP vorkommt.
            hit = {s for s in hit if share[sess['sessionId']].get(s, 0) <= a.max_share}
            if len(hit) < a.min_stems:
                continue
            # Der Anker muss aus der Schlagzeile kommen. Statistik allein
            # trennt im Deutschen den Sachbegriff nicht vom Verfahrenswort:
            # "Entscheidung", "Stellvertreter", "Aufstellung" sind ueber die
            # Beschluesse genauso selten wie "Gaertnerstrasse". Der Slug ist
            # dagegen die Schlagzeile - was dort steht, behandelt der Artikel
            # wirklich, und zwar als Thema und nicht als Floskel.
            anchor = hit & head
            if not any(idf.get(s, 0) >= a.need_idf for s in anchor):
                continue
            w = sum(idf.get(s, 0) for s in hit)
            if w >= a.min:
                tops.append((round(w, 1), v['id'], v['title'],
                             sorted(anchor, key=lambda s: -idf.get(s, 0))[:4]))
        tops = [t for t in tops if not excluded(r['url'], t[1])]
        tops.sort(reverse=True)
        plan.append({'url': r['url'], 'media': r['media'], 'date': r['published'],
                     'pressId': known_url.get(r['url']),
                     'sessionId': sess['sessionId'], 'daysAfter': sess['daysAfter'],
                     'tops': tops})

    n_top = sum(len(p['tops']) for p in plan)
    print('%d Artikel -> Sitzung, davon %d mit mindestens einem TOP (%d TOP-Links)'
          % (len(plan), sum(1 for p in plan if p['tops']), n_top))
    print('Schwelle: Gewicht >= %.1f und >= %d Stammtreffer\n' % (a.min, a.min_stems))

    print('Stichprobe der TOP-Zuordnungen:')
    shown = 0
    for p in plan:
        for w, vid, title, hit in p['tops']:
            if shown >= a.sample:
                break
            print('  %.1f  %s' % (w, p['url'].rsplit('/', 1)[-1][:66]))
            print('        -> %s  %s' % (vid, title[:52]))
            print('        Stichworte: %s' % ', '.join(hit))
            shown += 1
        if shown >= a.sample:
            break

    # Presseeintraege anlegen, wo der Artikel noch nicht im Bestand ist.
    known_id = {x['id'] for x in press}
    # idowa hat sein URL-Schema gewechselt: derselbe Text liegt einmal unter
    # "...-2158437.html" und einmal unter "...-art-151274". Die Artikelnummern
    # sind verschieden, der Titel ist es nicht - deshalb wird darueber geprueft.
    known_title = {(x['media'], re.sub(r'[^a-z0-9]', '', fold(x['title']))[:60])
                   for x in press}
    neu = 0
    for p in plan:
        # Nur wo die Schlagzeile einen Tagesordnungspunkt benennt, ist die
        # Zuordnung belastbar. Ein Artikel, der bloss im richtigen Zeitfenster
        # erschien, kann alles sein - eine Bilanz, ein Nachruf, die Vorschau
        # auf die uebernaechste Sitzung. Solche bleiben im Bericht liegen.
        if not p['tops'] and not a.loose:
            continue
        if p['pressId']:
            continue
        h = headline(cachefile(p['url']))
        if not h:
            continue                      # ohne Schlagzeile kein Eintrag
        key = (p['media'], re.sub(r'[^a-z0-9]', '', fold(h))[:60])
        if key in known_title:
            continue                      # steht schon unter einer alten URL drin
        known_title.add(key)
        pid = base = press_id(p['media'], p['date'], p['url'])
        n = 2
        while pid in known_id:
            pid, n = '%s-%d' % (base, n), n + 1
        known_id.add(pid)
        p['pressId'], p['headline'] = pid, h
        press.append({'id': pid, 'media': p['media'], 'date': p['date'],
                      'title': h[:120], 'url': p['url']})
        neu += 1

    n_sess = n_top = 0
    for p in plan:
        if not p['pressId'] or (not p['tops'] and not a.loose):
            continue
        sess = smap[p['sessionId']]
        lst = sess.setdefault('press', [])
        if p['pressId'] not in lst:
            lst.append(p['pressId'])
            n_sess += 1
        for _, vid, _, _ in p['tops']:
            for ag in sess.get('agenda', []):
                if ag.get('voteId') == vid or vid in (ag.get('voteIds') or []):
                    al = ag.setdefault('press', [])
                    if p['pressId'] not in al:
                        al.append(p['pressId'])
                        n_top += 1
                    break

    print('\n%d neue Presseeintraege, %d Sitzungs-Links, %d TOP-Links'
          % (neu, n_sess, n_top))

    out = os.path.join(CRAWL, 'zuordnung.json')
    json.dump(plan, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('Plan -> %s' % out)
    if not a.apply:
        print('Probelauf - nichts geschrieben. Mit --apply ausfuehren.')
        return
    for name, obj in (('press.json', press), ('sessions.json', sessions)):
        with open(os.path.join(DATA, name), 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.write('\n')
    print('geschrieben.')


if __name__ == '__main__':
    main()
