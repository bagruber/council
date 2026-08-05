"""Liest die Beschlussauszüge der Stadt (Textfassung) und baut Sessions + Votes.

Diese Sitzungen erscheinen nie als Niederschrift. Der Auszug nennt Tagesordnung,
Beschluss und Stimmenzahlen — aber keine Anwesenheitsliste. Deshalb:

  * 12 Stimmen (= alle Sitze des BPU) -> named, volle Besetzung
  * weniger -> anonymous ohne `absent`; wer gefehlt hat, steht nirgends
  * "Mehrfachbeschluss" -> mehrere Einzelbeschlüsse ohne ausgewiesene Zahlen,
    also gar kein Vote, nur ein Tagesordnungspunkt

"Beschluss: Abgelehnt" heißt, dass der Bauantrag abgelehnt wurde — nicht, dass
die Abstimmung gescheitert ist. Bei 11:0 ist der Beschluss zur Ablehnung
einstimmig durchgegangen. `result: rejected` wird deshalb nur gesetzt, wenn die
Abstimmung selbst verloren ging.
"""
import json, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')
SRC = os.path.join(DATA, 'niederschriften', 'bpu intake.txt')

HEAD = re.compile(r'^\s*(?P<body>[^\n]*?) - (?P<d>\d{2})\.(?P<m>\d{2})\.(?P<y>\d{4}) - '
                  r'(?P<start>\d{1,2}:\d{2})-(?P<end>\d{1,2}:\d{2}) Uhr\s*$')
TOP = re.compile(r'^\s*Ö\s*(?P<nr>\d+(?:\.\d+)*)\s*$')
BESCHLUSS = re.compile(r'^\s*Beschluss:\s*(?P<kind>.+?)\s*$')
STIMMEN = re.compile(r'^\s*Abstimmung:\s*Ja:\s*(?P<ja>\d+),\s*Nein:\s*(?P<nein>\d+)\s*$')
SKIP = re.compile(r'^\s*(Tagesordnung|TOP-Liste|BM|Öffentliche Bekanntmachung|Öffentlicher Teil.*)\s*$')


def parse(text):
    sessions, cur, top = [], None, None
    url = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith('http'):
            url = line
            continue
        h = HEAD.match(line)
        if h:
            cur = {'date': f"{h['y']}-{h['m']}-{h['d']}", 'start': h['start'], 'end': h['end'],
                   'url': url, 'items': []}
            sessions.append(cur)
            url = top = None
            continue
        if cur is None or SKIP.match(line):
            continue
        t = TOP.match(line)
        if t:
            top = {'number': t['nr'], 'title': [], 'kind': None, 'ja': None, 'nein': None}
            cur['items'].append(top)
            continue
        if top is None:
            continue
        b = BESCHLUSS.match(line)
        if b:
            top['kind'] = b['kind']
            continue
        s = STIMMEN.match(line)
        if s:
            top['ja'], top['nein'] = int(s['ja']), int(s['nein'])
            continue
        top['title'].append(line)

    for s in sessions:
        for it in s['items']:
            # "Nachtrag: <Datum>" steht als eigene Zeile vor dem Titel
            parts = [p for p in it['title'] if not p.startswith('Nachtrag:')]
            it['note'] = next((p for p in it['title'] if p.startswith('Nachtrag:')), None)
            it['title'] = ' '.join(parts).strip()
    return sessions


def main():
    sessions = parse(open(SRC, encoding='utf-8').read())
    known = {s['id'] for s in json.load(open(os.path.join(DATA, 'sessions.json'), encoding='utf-8'))}
    lengths = {(l['date'], l['body']) for l in
               json.load(open(os.path.join(DATA, 'sessionlengths.json'), encoding='utf-8'))}

    total_votes = 0
    for s in sessions:
        sid = 'bpu_' + s['date'].replace('-', '')
        votes = [i for i in s['items'] if i['ja'] is not None]
        full = [i for i in votes if i['ja'] + i['nein'] == 12]
        total_votes += len(votes)
        flags = []
        if sid in known: flags.append('SESSION EXISTIERT')
        if (s['date'], 'bpu') not in lengths: flags.append('neue Dauer')
        if not s['url']: flags.append('KEINE URL')
        print(f"{s['date']}  {s['start']}-{s['end']}  TOPs {len(s['items']):2}  "
              f"Voten {len(votes):2}  davon 12er {len(full):2}  {' · '.join(flags)}")
        for i in s['items']:
            mark = '' if i['ja'] is None else f"{i['ja']}:{i['nein']}"
            print(f"    {i['number']:>5}  {(i['kind'] or '—'):18} {mark:>6}  {i['title'][:64]}")
    print(f"\n{len(sessions)} Sitzungen, {total_votes} Abstimmungen")


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
