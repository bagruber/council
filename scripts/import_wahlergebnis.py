"""Traegt die Stimmenzahlen der Kommunalwahl in members.json ein.

Quelle: `data/knowledge/member_intake.txt`, Spalten
    Listenplatz · Name · Platz nach Auszaehlung · Stimmen · Gewaehlt/Nachruecker

Der Abstand zwischen Listenplatz und Platz nach Auszaehlung ist die eigentliche
Aussage: Haberl stand auf Platz 24 und landete auf Platz 9. Beides wird
gespeichert, das Profil zeigt "Liste 24 -> Platz 9".

Nachruecker sind nicht direkt gewaehlt. Dass Haberl trotzdem im Rat sitzt,
liegt daran, dass Mader als Erster Buergermeister den Vorsitz einnimmt und
seinen Listensitz freigibt.
"""
import json, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')
SRC = os.path.join(DATA, 'knowledge', 'member_intake.txt')

ROW = re.compile(r'^(\d+)\t(.+?)\t(\d+)\t([\d.]+)\t(Gewählt|Nachrücker)\s*$')
YEAR = re.compile(r'^(\d{4})\s*$')

# Die Auszuege nennen den Klarnamen, nicht die ID.
ALIAS = {
    'Mader Maximilian': 'mader', 'Heinz Rudolf': 'heinz',
    'Hadersdorfer Georg': 'hadersdorfer', 'Dr. Reither Dominikus': 'reither',
    'Tristl Manfred': 'tristl', 'Schweiger Christian': 'schweiger',
    'Linz Karin': 'linz_karin', 'Kehlringer Lorena': 'kehlringer',
    'Haberl Ludwig': 'haberl', 'Lauterbach Reinhard': 'lauterbach',
    'Meier Christian': 'meier', 'Grundner Thomas': 'grundner',
    'Sixt Josef': 'sixt', 'Kieninger Ludwig': 'kieninger',
    'Welter Gerhard-Michael': 'welter', 'Dr. Daoud Ghadieh Moutasem': 'ghadieh',
    'Dr. Stanglmaier Michael': 'stanglmaier', 'Beibl Verena': 'beibl',
    'Rümelin Ramona': 'ruemelin', 'Linz Kilian': 'linz_kilian',
    'Röck Matthias': 'roeck', 'von Pressentin Nathalie': 'von_pressentin',
    'Becher Alexandra': 'becher_a', 'Marcus Gunnar': 'marcus',
    'Marschoun Christoph': 'marschoun', 'Šabanović Benjamin': 'sabanovic',
    'Dick Johanna': 'dick', 'Grübl Julian': 'gruebl',
    'Hobmaier Michael': 'hobmaier', 'Wittmann Thomas': 'wittmann',
    'Strobl Alexander': 'strobl',
}


def main():
    path = os.path.join(DATA, 'members.json')
    data = json.load(open(path, encoding='utf-8'))
    by = {m['id']: m for m in data['members']}

    year, added, unknown = None, 0, []
    for line in open(SRC, encoding='utf-8'):
        y = YEAR.match(line.strip())
        if y:
            year = int(y.group(1))
            continue
        r = ROW.match(line.rstrip('\n'))
        if not r or not year:
            continue
        name = r.group(2).strip()
        mid = ALIAS.get(name)
        if not mid or mid not in by:
            unknown.append(name)
            continue
        entry = {'year': year,
                 'listRank': int(r.group(1)),
                 'resultRank': int(r.group(3)),
                 'votes': int(r.group(4).replace('.', '')),
                 'elected': r.group(5) == 'Gewählt'}
        el = by[mid].setdefault('profile', {}).setdefault('elections', [])
        el[:] = [e for e in el if e['year'] != year] + [entry]
        el.sort(key=lambda e: -e['year'])
        added += 1

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

    print(f'  {added} Ergebnisse eingetragen')
    if unknown:
        print(f'  nicht zugeordnet: {unknown}')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
