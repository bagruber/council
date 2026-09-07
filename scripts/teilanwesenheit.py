"""Trägt die Zeitvermerke der Anwesenheitslisten in sessions.json ein.

Die Niederschriften notieren neben einzelnen Namen "ab 18:15 Uhr" oder "bis
20:30 Uhr". Bisher fiel das beim Einarbeiten weg — übrig blieb die Liste der
ganz Abwesenden. Genau diese Vermerke erklären aber, warum bei einstimmigen
Beschlüssen weniger Stimmen ausgewiesen sind als Anwesende: wer später kam
oder früher ging, hat einen Teil der Beschlüsse nicht miterlebt.

`partial` je Sitzung: [{member, from?, to?}] — Uhrzeit oder TOP, wörtlich aus
der Niederschrift. Welcher Beschluss vor und welcher nach der Uhrzeit lag,
steht dort nicht; die Angabe benennt nur, wessen Stimme unsicher ist.

Aufruf:  python scripts/teilanwesenheit.py
"""
import json, os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# Wörtlich aus den Anwesenheitslisten der Niederschriften
VERMERKE = {
    'sr_20230327': [
        {'member': 'stanglmaier',    'from': '18:20'},
        {'member': 'becher_j',       'from': '18:45'},
        {'member': 'gruber',         'from': '20:45'},
        {'member': 'kaestl',         'from': '18:15'},
        {'member': 'von_pressentin', 'to':   '20:30'},
    ],
    'sr_20230515': [
        {'member': 'gruber',         'from': '18:10'},
        {'member': 'von_pressentin', 'from': '18:10'},
        {'member': 'linz_karin',     'to':   '19:10'},
    ],
    'sr_20231214': [
        {'member': 'beibl',          'from': '18:10', 'to': '19:30'},
        {'member': 'fincke',         'to':   '19:30'},
        {'member': 'gruebl',         'from': '18:15'},
        {'member': 'von_pressentin', 'from': '18:15'},
    ],
    'sr_20231218': [
        {'member': 'becher_a',       'from': '18:20'},
        {'member': 'becher_j',       'from': '19:10'},
        {'member': 'fincke',         'from': '18:05'},
        {'member': 'kaestl',         'from': '18:15'},
        {'member': 'von_pressentin', 'from': '18:10'},
    ],
    'sr_20240304': [
        {'member': 'hadersdorfer',   'to':   '20:15'},
    ],
    'sr_20241021': [
        {'member': 'stanglmaier',    'from': '20:10'},
        {'member': 'becher_j',       'from': '20:10'},
        {'member': 'kaestl',         'from': '19:30'},
        {'member': 'linz_karin',     'to':   '21:00'},
    ],
    # 07.10.2024 und 28.07.2025 führen keine Zeitvermerke — dort bleibt die
    # Lücke ohne Träger. Bewusst als leere Liste, damit klar ist: geprüft.
    'sr_20241007': [],
    'sr_20250728': [],
}


def main():
    pfad = os.path.join(DATA, 'sessions.json')
    sessions = json.load(open(pfad, encoding='utf-8'))
    members = {m['id'] for m in json.load(
        open(os.path.join(DATA, 'members.json'), encoding='utf-8'))['members']}

    nach_id = {s['id']: s for s in sessions}
    for sid, eintraege in VERMERKE.items():
        s = nach_id[sid]
        for e in eintraege:
            assert e['member'] in members, e
            assert e['member'] not in (s.get('absent') or []), (sid, e)
        # Reihenfolge im Sitzungsobjekt: partial gehört zu absent
        if eintraege:
            s['partial'] = eintraege
        elif 'partial' in s:
            del s['partial']
        print(f'  {sid}: {len(eintraege)} Zeitvermerke')

    with open(pfad, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)
        f.write('\n')


if __name__ == '__main__':
    main()
