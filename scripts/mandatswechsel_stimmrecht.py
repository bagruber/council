"""Trägt bei Wechselsitzungen ein, wem der Sitz zu welcher Abstimmung gehörte.

An einem Wechseltag stehen zwei Namen in der Anwesenheitsliste, aber es gibt
nur einen Sitz. Ohne Vermerk am einzelnen Votum hält die App beide für
stimmberechtigt — bei einstimmigen Beschlüssen schreibt sie deshalb beiden ein
Ja gut, und bei geteilten steht bei beiden ein Fragezeichen. Beides ist falsch,
denn der Zeitpunkt des Wechsels steht in der Niederschrift.

Die Regel, aus den Niederschriften belegt:
  * vor dem Wechselbeschluss  — der Sitz gehört der ausscheidenden Person
  * beim Wechselbeschluss     — die ausscheidende Person ist nach Art. 49 GO
                                persönlich beteiligt, die nachrückende ist noch
                                nicht vereidigt: der Sitz stimmt nicht mit
  * danach                    — der Sitz gehört der nachrückenden Person

Wer den Sitz gerade nicht hält, bekommt `kein_mandat`. Dieser Grund zählt in
mark_inferable.py bewusst nicht als Ausschluss: der Sitz ist ja besetzt, nur
eben von der anderen Person.

Aufruf:  python scripts/mandatswechsel_stimmrecht.py [--dry]
"""
import json, os, sys

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# Sitzung: (ausscheidend, nachrückend, Votum des Wechselbeschlusses)
WECHSEL = {
    'sr_20211025': ('wittmann', 'gruebl',   'sr_20211025_01'),
    'sr_20221010': ('neumayr',  'gruber',   'sr_20221010_01'),
    'sr_20230724': ('john',     'strobl',   'sr_20230724_01'),
    'sr_20241021': ('gruebl',   'hobmaier', 'sr_20241021_02'),
}


def ergaenze(vote, mid, grund):
    excl = vote.setdefault('excluded', [])
    if any(e['member'] == mid for e in excl):
        return False
    excl.append({'member': mid, 'reason': grund})
    return True


def main():
    trocken = '--dry' in sys.argv
    pfad = os.path.join(DATA, 'votes.json')
    votes = json.load(open(pfad, encoding='utf-8'))

    proSitzung = {}
    for v in votes:
        proSitzung.setdefault(v['sessionId'], []).append(v)

    geaendert = 0
    for sid, (raus, rein, wechselVotum) in WECHSEL.items():
        reihe = sorted(proSitzung.get(sid, []), key=lambda v: v['id'])
        idx = next(i for i, v in enumerate(reihe) if v['id'] == wechselVotum)
        for i, v in enumerate(reihe):
            # Namentliche Voten tragen die Wahrheit schon: wer den Sitz nicht
            # hielt, steht in keinem der drei Arrays.
            if v['type'] == 'named':
                continue
            if i < idx:
                treffer = [(rein, 'kein_mandat')]
            elif i == idx:
                treffer = [(rein, 'kein_mandat'), (raus, 'beteiligung')]
            else:
                treffer = [(raus, 'kein_mandat')]
            for mid, grund in treffer:
                if ergaenze(v, mid, grund):
                    geaendert += 1
                    print(f'  {v["id"]:18s} {mid:12s} {grund}')

        # Auf Wechseltagen war die Zahl der Abwesenden aus 26 statt 25 Sitzen
        # gerechnet — die beiden teilen sich einen Sitz.
        for v in reihe:
            if v['type'] != 'anonymous':
                continue
            r = v['results']
            soll = 25 - r['yes'] - r['no']
            if r['absent'] != soll:
                print(f'  {v["id"]:18s} abwesend {r["absent"]} → {soll}')
                r['absent'] = soll
                geaendert += 1

    print(f'{geaendert} Änderungen' + (' (dry run)' if trocken else ''))
    if not trocken:
        with open(pfad, 'w', encoding='utf-8') as f:
            json.dump(votes, f, ensure_ascii=False, indent=2)
            f.write('\n')


if __name__ == '__main__':
    main()
