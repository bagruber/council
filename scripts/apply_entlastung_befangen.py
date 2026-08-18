"""Traegt die namentlichen Befangenheiten der Klaeranlage-Entlastungen ein.

Die Niederschriften halten unter "Abstimmungsvermerke:" fest, wer wegen
persoenlicher Beteiligung nicht mitgestimmt hat — bei allen fuenf Entlastungen
des Aufsichtsrats. Das ist verbatim aus dem Protokoll, also protocol-explicit.

Der Vermerk nennt nur die *anwesenden* Aufsichtsratsmitglieder; abwesende
fehlen. Deshalb schwankt die Zahl zwischen fuenf und acht, obwohl der
Aufsichtsrat durchgehend acht Sitze hat.

Wo Anwesende minus Benannte genau die Ja-Stimmen ergibt, ist das Votum
vollstaendig aufgeloest und wird `named`. Wo eine Restluecke bleibt, werden nur
die Befangenen gesetzt; das Votum bleibt anonym und gesperrt.
"""
import json, os, sys

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# Wortlaut der Abstimmungsvermerke, Namen zu IDs aufgeloest
CASES = {
    'sr_20200722_02': ['dollinger', 'stanglmaier', 'weber', 'beubl'],
    'sr_20210726_03': ['dollinger', 'weber', 'haberl', 'wagner',
                       'stanglmaier', 'reif', 'beubl', 'linz_karin'],
    'sr_20230724_04': ['dollinger', 'weber', 'haberl', 'reif', 'beubl', 'gruebl'],
    'sr_20240701_03': ['dollinger', 'weber', 'haberl', 'becher_a',
                       'stanglmaier', 'reif', 'beubl', 'gruebl'],
    'sr_20250728_05': ['dollinger', 'weber', 'haberl', 'reif', 'hobmaier'],
}
# 22.07.2020: der Vermerk nennt zusaetzlich StRin Linz, die Anwesenheitsliste
# fuehrt sie aber als entschuldigt. Sie bleibt abwesend, nicht befangen.

NOTE = ('Die Mitglieder des Aufsichtsrats stimmen über ihre eigene Entlastung '
        'nicht mit. Die Niederschrift nennt sie namentlich.')
NOTE_OPEN = NOTE + (' Die Zahl der Ja-Stimmen liegt zusätzlich um {n} unter der '
                    'Zahl der übrigen Anwesenden; wer nicht mitgestimmt hat, '
                    'hält die Niederschrift nicht fest.')


def active(m, d):
    sp = m.get('periods') or [{'from': m.get('from'), 'to': m.get('to')}]
    return any((s.get('from') or '0') <= d and (not s.get('to') or s['to'] >= d) for s in sp)


def main():
    md = json.load(open(os.path.join(DATA, 'members.json'), encoding='utf-8'))
    sessions = {s['id']: s for s in json.load(open(os.path.join(DATA, 'sessions.json'), encoding='utf-8'))}
    path = os.path.join(DATA, 'votes.json')
    votes = json.load(open(path, encoding='utf-8'))

    for v in votes:
        ex = CASES.get(v['id'])
        if not ex:
            continue
        sess = sessions[v['sessionId']]
        absent = sess.get('absent', [])
        present = [m['id'] for m in md['members']
                   if active(m, v['date']) and m['id'] not in absent]
        rest = [p for p in present if p not in ex]
        ja = v['results']['yes'] if v['type'] == 'anonymous' else len(v['results']['yes'])
        gap = len(rest) - ja

        v['excluded'] = [{'member': m, 'reason': 'beteiligung'} for m in ex]
        v['source'] = {'tier': 'protocol-explicit'}
        if gap == 0:
            v['type'] = 'named'
            # Befangene stehen in absent, damit die Arrays aufgehen; voteStatus
            # liest die Befangenheit vorher aus `excluded` und zeigt "bef."
            v['results'] = {'yes': rest, 'no': [], 'absent': absent + ex}
            v.pop('inferable', None)
            v['note'] = NOTE
            print(f"  {v['id']}  aufgelöst: {len(rest)} Ja, {len(ex)} befangen, {len(absent)} abwesend")
        else:
            v['inferable'] = False
            v['note'] = NOTE_OPEN.format(n=gap)
            print(f"  {v['id']}  {len(ex)} befangen gesetzt, {gap} Stimmen bleiben offen")

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(votes, f, ensure_ascii=False, indent=2)
        f.write('\n')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
