"""Themen auf zwei Ebenen umstellen: Felder (tags.json) und Dossiers (topics.json).

Jedes Dossier bekommt
  field   — Primärfeld für die Feld-Landingpage
  type    — bestimmt den Kopf der Seite, die Timeline bleibt für alle gleich
  status  — laufend | abgeschlossen (nur wo es endet)
  partOf  — optional das übergeordnete Dossier (Gebiet)

Ausserdem wird „Energie & Klimawende" (t15) aufgelöst: es war ein Feld,
kein Dossier. Die Inhalte gehen in eigenständige Dossiers.
"""
import json, os, collections

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# id: (field, type, status, partOf)
CLASSIFY = {
    't1':  ('sports',         'vorhaben',    'laufend',       None),
    't2':  ('building',       'vorhaben',    'laufend',       None),
    't3':  ('mobility',       'konflikt',    'laufend',       None),
    't4':  ('mobility',       'vorhaben',    'laufend',       None),
    't5':  ('building',       'konflikt',    'laufend',       None),
    't6':  ('education',      'vorhaben',    'laufend',       None),
    't7':  ('budget',         'zyklus',      None,            None),
    't8':  ('mobility',       'vorhaben',    'laufend',       None),
    't9':  ('mobility',       'vorhaben',    'laufend',       None),
    't10': ('economy',        'vorhaben',    'laufend',       None),
    't11': ('culture',        'vorhaben',    'abgeschlossen', None),
    't12': ('sports',         'einrichtung', None,            None),
    't13': ('building',       'gebiet',      'laufend',       None),
    't14': ('culture',        'konflikt',    'laufend',       None),
    't16': ('sports',         'einrichtung', None,            None),
    't17': ('building',       'vorhaben',    'laufend',       None),
    't18': ('economy',        'gebiet',      'laufend',       None),
    't19': ('sports',         'vorhaben',    'laufend',       None),
    't20': ('building',       'gebiet',      'abgeschlossen', None),
}

# Aus t15 werden eigenständige Dossiers. Zuordnung über Vote-IDs.
SPLIT = [
    {
        'id': 't21', 'title': 'Kommunale Wärmeplanung',
        'field': 'environment', 'type': 'vorhaben', 'status': 'abgeschlossen',
        'tags': ['environment', 'infrastructure'],
        'summary': 'Gesetzlich vorgeschriebene Planung, wie Moosburg künftig heizt. '
                   'Zwischenergebnis 2024, Abschlussbericht im Juni 2025 — die Grundlage '
                   'für alle weiteren Entscheidungen zur Wärmeversorgung.',
        'votes': ['Wärmeplanung'],
    },
    {
        'id': 't22', 'title': 'Windenergie im Regionalplan',
        'field': 'environment', 'type': 'konflikt', 'status': 'laufend',
        'tags': ['environment'],
        'summary': 'Der Regionalplan München weist Vorranggebiete für Windkraft aus. '
                   'Moosburg nahm 2024 dazu Stellung — eine der wenigen Abstimmungen, '
                   'bei denen die Fraktionen sichtbar auseinandergingen.',
        'votes': ['Windenergie'],
    },
    {
        'id': 't23', 'title': 'Photovoltaik-Freiflächenanlage Kuttenweide',
        'field': 'environment', 'type': 'vorhaben', 'status': 'laufend',
        'tags': ['environment', 'building'],
        'summary': 'Bebauungsplan und städtebaulicher Vertrag für eine Freiflächen-'
                   'Photovoltaikanlage an der Kuttenweide, beides im Februar 2025 beschlossen.',
        'votes': ['Kuttenweide'],
    },
    {
        'id': 't24', 'title': 'Straßenbeleuchtung auf LED',
        'field': 'infrastructure', 'type': 'vorhaben', 'status': 'abgeschlossen',
        'tags': ['infrastructure', 'environment'],
        'summary': 'Umrüstung der städtischen Straßenbeleuchtung auf LED, mit einem '
                   'Beleuchtungskonzept als Grundlage. Beides 2023 einstimmig beschlossen.',
        'votes': ['Straßenbeleuchtung'],
    },
    {
        'id': 't25', 'title': 'Städtische Förderprogramme für Energie',
        'field': 'environment', 'type': 'regelwerk', 'status': None,
        'tags': ['environment', 'budget'],
        'summary': 'Zuschüsse, die die Stadt selbst ausreicht: Solarförderung und das '
                   'Förderprogramm „Natürlich Dämmen". Beide wurden seit Auflage mehrfach '
                   'angepasst.',
        'votes': ['Solarförder', 'Natürlich Dämmen'],
    },
    {
        'id': 't26', 'title': 'Stromeinkauf der Stadt',
        'field': 'infrastructure', 'type': 'zyklus', 'status': None,
        'tags': ['infrastructure', 'environment', 'budget'],
        'summary': 'Die Stadt schreibt ihren Strombedarf in mehrjährigen Bündeln aus. '
                   'Seit der Ausschreibung 2025 bezieht sie 100 % Ökostrom.',
        'votes': ['Strom-Bündelausschreibung', 'Strom-/Gasausschreibung'],
    },
]

# Wiederkehrende Groessen, die als kompakte Uebersicht in den Kopf gehoeren
FIGURES = {
    't12': {'title': 'Badegebührenordnung',
            'note': 'Beschlossene Fassungen — die jeweils jüngste gilt.'},
    't16': {'title': 'Gebühren und Öffnungszeiten',
            'note': 'Seit Eröffnung beschlossene Regelungen.'},
    't25': {'title': 'Förderprogramme',
            'note': 'Auflage und Änderungen.'},
}


def load(n):
    return json.load(open(os.path.join(DATA, n), encoding='utf-8'))


def save(n, o):
    with open(os.path.join(DATA, n), 'w', encoding='utf-8') as f:
        json.dump(o, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    topics = load('topics.json')
    votes = load('votes.json')
    by_id = {t['id']: t for t in topics}

    # 1. Bestehende Dossiers einordnen
    for tid, (field, typ, status, parent) in CLASSIFY.items():
        t = by_id[tid]
        t['field'] = field
        t['type'] = typ
        if status:
            t['status'] = status
        if parent:
            t['partOf'] = parent

    # 2. t15 aufloesen
    old = by_id.pop('t15')
    topics = [t for t in topics if t['id'] != 't15']
    hist = {h.get('voteId'): h for h in old['history'] if h.get('voteId')}
    moved = set()

    for spec in SPLIT:
        picked = [v for v in votes
                  if v.get('topicId') in ('t15', None)
                  and any(k.lower() in v['title'].lower() for k in spec['votes'])]
        for v in picked:
            v['topicId'] = spec['id']
            moved.add(v['id'])
        new = {
            'id': spec['id'], 'title': spec['title'],
            'field': spec['field'], 'type': spec['type'],
            'tags': spec['tags'], 'image': None, 'summary': spec['summary'],
            # Für jedes übernommene Votum ein Timeline-Eintrag: den redaktionell
            # gepflegten aus t15, sonst einen aus dem Votum abgeleiteten.
            'history': [
                hist.get(v['id']) or {
                    'date': v['date'], 'type': 'vote', 'title': v['title'],
                    'text': v.get('text', ''), 'sessionId': v['sessionId'],
                    'voteId': v['id'],
                }
                for v in sorted(picked, key=lambda x: x['date'])
            ],
        }
        if spec['status']:
            new['status'] = spec['status']
        topics.append(new)
        print(f"  {spec['id']}  {len(picked):2} Voten  {spec['title']}")

    rest = [v for v in votes if v.get('topicId') == 't15']
    for v in rest:
        v['topicId'] = None
    print(f"\n  {len(rest)} Voten ohne eigenes Dossier -> Feld Umwelt/Infrastruktur:")
    for v in sorted(rest, key=lambda x: x['date']):
        print(f"     {v['date']}  {v['title'][:64]}")

    # 3. Kennwert-Uebersichten: die passenden History-Eintraege als Serie markieren
    for tid, fig in FIGURES.items():
        t = next((x for x in topics if x['id'] == tid), None)
        if not t:
            continue
        keys = ('gebühr', 'tarif', 'öffnungszeit', 'förder', 'ordnung')
        rows = [{'date': h['date'], 'label': h['title'], 'voteId': h.get('voteId')}
                for h in t['history']
                if any(k in h['title'].lower() for k in keys)]
        if rows:
            t['figures'] = {**fig, 'rows': rows}
            print(f"\n  figures {tid}: {len(rows)} Zeilen")

    # 4. Tagesordnungspunkte nachziehen: sie verweisen noch auf t15
    sessions = load('sessions.json')
    vote_topic = {v['id']: v.get('topicId') for v in votes}
    fixed = dropped = 0
    for s in sessions:
        for a in s.get('agenda', []):
            if a.get('topicId') != 't15':
                continue
            new_id = vote_topic.get(a.get('voteId'))
            if new_id:
                a['topicId'] = new_id
                fixed += 1
            else:
                del a['topicId']
                dropped += 1
    print(f"\n  Tagesordnung: {fixed} auf neue Dossiers umgehängt, {dropped} ohne Zuordnung")
    save('sessions.json', sessions)

    topics.sort(key=lambda t: int(t['id'][1:]))
    save('topics.json', topics)
    save('votes.json', votes)

    kinds = collections.Counter(t['type'] for t in topics)
    print(f"\n{len(topics)} Dossiers: {dict(kinds)}")


if __name__ == '__main__':
    main()
