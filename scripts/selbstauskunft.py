"""Übernimmt die Antwort eines Mitglieds auf die Liste der offenen Stimmen.

Eingabe ist die zurückgeschickte Nachricht, so wie sie aus
`offene_stimmen.py` herausging — nur dass ⬜ durch ✅ ❌ ➖ ❔ ersetzt wurde.
Das Skript liest die Sitzungszeile (⏰ Datum · Gremium), sucht den Beschluss
über den Titel und trägt die Stimme ein.

Gleiche Titel in einer Sitzung trennt die 📊-Zeile unter dem Punkt. In der
konstituierenden Sitzung vom 11.05.2026 heißen vier Abstimmungen "Entscheidung
über die nummerische Besetzung der Ausschüsse" und unterscheiden sich nur im
Ergebnis — der Titel allein fände dort vier Treffer.

Eingetragen wird zweierlei:
  * `voters[<id>]`      — die Stimme selbst
  * `voterSource[<id>]` — Liste der Belege für diese eine Stimme. Stand sie
                          schon in der Mitschrift oder in der Zeitung, kommt
                          `selbstauskunft` dazu statt sie zu ersetzen: die
                          stärkere Quelle bleibt maßgeblich, die schwächere
                          erhöht nur das Gewicht.

Die vote-weite `source` bleibt unberührt, solange sie schon gesetzt ist.

Aufruf:
    python scripts/selbstauskunft.py hobmaier docs/selbstauskuenfte/hobmaier.txt
    python scripts/selbstauskunft.py hobmaier <datei> --dry
"""
import json, os, re, sys, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')

STIMME = {'✅': 'yes', '❌': 'no', '➖': 'absent'}
UNKLAR = {'❔', '❓', '⬜'}          # nicht beantwortet — überspringen
GREMIUM = {'Stadtrat': 'stadtrat', 'BPU': 'bpu', 'HVFA': 'hvfa'}

SITZUNG = re.compile(r'^[⏰📅]\s*(\d{2})\.(\d{2})\.(\d{4})\s*·\s*(\S+)')
PUNKT = re.compile(r'^(\S)\s*\*(.+?)\*\s*$')
STAND = re.compile(r'^📊\s*(\d+)\s*:\s*(\d+)')


def load(n):
    return json.load(open(os.path.join(DATA, n), encoding='utf-8'))


def lies(pfad):
    """Je beantwortetem Punkt: Datum, Gremium, Stimme, Titel und das Ergebnis
    aus der 📊-Zeile darunter, soweit vorhanden."""
    punkte, letzter = [], None
    datum = gremium = None
    for zeile in open(pfad, encoding='utf-8'):
        zeile = zeile.strip()
        m = SITZUNG.match(zeile)
        if m:
            t, mo, j, g = m.groups()
            datum, gremium = f'{j}-{mo}-{t}', GREMIUM.get(g)
            if not gremium:
                sys.exit(f'Unbekanntes Gremium: {g}')
            continue
        m = PUNKT.match(zeile)
        if m and datum:
            zeichen, titel = m.groups()
            if zeichen in UNKLAR:
                # Die 📊-Zeile darunter gehört zu diesem Punkt, nicht zum
                # vorigen beantworteten.
                letzter = None
                continue
            if zeichen not in STIMME:
                sys.exit(f'Unbekanntes Zeichen "{zeichen}" bei: {titel}')
            letzter = {'datum': datum, 'gremium': gremium, 'stimme': STIMME[zeichen],
                       'titel': titel, 'stand': None}
            punkte.append(letzter)
            continue
        m = STAND.match(zeile)
        if m and letzter and letzter['stand'] is None:
            letzter['stand'] = (int(m.group(1)), int(m.group(2)))
    return punkte


def stand(v):
    r = v['results']
    if isinstance(r['yes'], list):
        return len(r['yes']), len(r['no'])
    return r['yes'], r['no']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('member')
    ap.add_argument('datei')
    ap.add_argument('--dry', action='store_true')
    args = ap.parse_args()

    members = {m['id'] for m in load('members.json')['members']}
    if args.member not in members:
        sys.exit('Unbekannte member-id: ' + args.member)

    sessions = load('sessions.json')
    pfad = os.path.join(DATA, 'votes.json')
    votes = json.load(open(pfad, encoding='utf-8'))
    nach_sitzung = {}
    for v in votes:
        nach_sitzung.setdefault(v['sessionId'], []).append(v)

    sitzung_von = {(s['date'], s.get('type') or 'stadtrat'): s['id'] for s in sessions}

    n = 0
    for p in lies(os.path.join(ROOT, args.datei)):
        stimme, titel = p['stimme'], p['titel']
        sid = sitzung_von.get((p['datum'], p['gremium']))
        if not sid:
            sys.exit(f'Keine Sitzung am {p["datum"]} ({p["gremium"]})')
        treffer = [v for v in nach_sitzung.get(sid, []) if v['title'] == titel]
        if len(treffer) > 1 and p['stand']:
            treffer = [v for v in treffer if stand(v) == p['stand']]
        if len(treffer) != 1:
            sys.exit(f'{len(treffer)} Treffer für "{titel}" in {sid}')
        v = treffer[0]

        alt = (v.get('voters') or {}).get(args.member)
        if alt and alt != stimme:
            print(f'  ! {v["id"]}: bisher {alt}, laut Selbstauskunft {stimme}')

        belege = (v.get('voterSource') or {}).get(args.member)
        if belege is None:
            # Ohne eigenen Eintrag galt bisher die Quelle des Beschlusses. War
            # die Stimme daraus schon bekannt, bleibt dieser Beleg erhalten.
            vorher = (v.get('source') or {}).get('tier')
            belege = [vorher] if (alt and vorher) else []
        if 'selbstauskunft' not in belege:
            belege.append('selbstauskunft')

        v.setdefault('voters', {})[args.member] = stimme
        v.setdefault('voterSource', {})[args.member] = belege
        # Beschlüsse ohne jede Herkunft bekommen sie jetzt von hier
        v.setdefault('source', {'tier': 'selbstauskunft'})
        print(f'  {v["id"]:18s} {stimme:6s} {"+".join(belege):28s} {titel[:40]}')
        n += 1

    print(f'{n} Stimmen' + (' (dry run)' if args.dry else ''))
    if not args.dry:
        with open(pfad, 'w', encoding='utf-8') as f:
            json.dump(votes, f, ensure_ascii=False, indent=2)
            f.write('\n')


if __name__ == '__main__':
    main()
