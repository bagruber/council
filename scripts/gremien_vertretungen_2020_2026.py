"""Besetzung und Vertretungen der Ausschuesse 2020-2026 nach den Belegen.

Bis hierher trug jedes Gremium fuer die ganze Periode die Besetzung vom Ende
der Periode, und jeder Sitz genau eine Vertretung. Die Vertretung wechselt
aber unabhaengig vom Sitzinhaber; `sub` darf deshalb jetzt eine Liste mit
Zeitraeumen sein (siehe Council.subAt in js/core.js).

Belege:
  BPU          Anwesenheitslisten der Niederschriften 2020-2026
  Aufsichtsrat Stadtrat 04.05.2020 TOP 4.3, 25.10.2021, 10.10.2022,
               21.10.2024 TOP 4.4, 24.03.2025 TOP 4.3
  HVFA         Anwesenheitsliste 28.11.2024; Groesse (11 + Vorsitz) aus
               Stadtrat 04.05.2020 TOP 3.2. Die bisherige Besetzung war eine
               Kopie des Aufsichtsrats.
  PA           Stadtrat 27.03.2023 TOP 9, 26.06.2023 TOP 6, 24.07.2023
  RPA          Stadtrat 06.07.2020 (Vorsitz Beubl, Stellv. Lauterbach),
               26.06.2023 TOP 6, 24.03.2025 TOP 4.4

Die Namenslisten der Neubesetzungen vom 04.05.2020, 06.03.2023, 21.10.2024
und 24.03.2025 stehen in Anlagen, die nicht vorliegen. Was nur daraus
hervorginge, bleibt offen; Annahmen sind unten kommentiert.

Einmal laufen lassen:
    python scripts/gremien_vertretungen_2020_2026.py
"""
import json, os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
PFAD = os.path.join(DATA, 'bodies.json')

# Wer 2022 fuer Wagner und Altenbeck nachrueckte, sass ab der Vereidigung am
# 20.06.2022 im Rat. Wann genau die Gremiensitze uebergingen, ist nicht
# belegt; zwischen Juni und September 2022 lag keine BPU-Sitzung.
GRUENE_NACHRUECKER = '2022-06-20'

BPU_SUBS = {
    'john': [{'member': 'kaestl', 'from': '2020-05-01', 'to': '2023-03-05'}],
    'wittmann': [{'member': 'neumayr', 'to': '2022-10-09'}, {'member': 'gruber', 'from': '2022-10-10'}],
    # Altenbecks Vertretung ist nicht ueberliefert
    'altenbeck': [{'member': 'becher_a', 'from': GRUENE_NACHRUECKER}],
    'stanglmaier': [{'member': 'wagner', 'to': '2022-05-31'}, {'member': 'becher_j', 'from': GRUENE_NACHRUECKER}],
}

FRESH_SITZ = [{'member': 'wittmann', 'to': '2021-10-24'},
              {'member': 'gruebl', 'from': '2021-10-25', 'to': '2024-10-20'},
              {'member': 'hobmaier', 'from': '2024-10-21'}]
FRESH_VERTRETUNG = [{'member': 'neumayr', 'to': '2022-10-09'}, {'member': 'gruber', 'from': '2022-10-10'}]

AUFSICHTSRAT = {
    'from': '2020-05-01', 'to': '2026-04-30', 'chair': 'dollinger',
    'seats': [
        {'member': 'weber', 'sub': 'linz_karin'},
        {'member': 'haberl', 'sub': 'tristl'},
        # Dass A. Becher Wagners Sitz uebernahm, folgt aus der Besetzung von
        # 2025 (gleiche Vertretung), nicht aus einem Beschluss.
        {'occupants': [{'member': 'wagner', 'to': '2022-05-31'},
                       {'member': 'becher_a', 'from': GRUENE_NACHRUECKER}],
         'sub': 'von_pressentin'},
        {'member': 'stanglmaier', 'sub': 'beibl'},
        {'member': 'reif', 'sub': 'grundner'},
        {'occupants': [{'member': 'beubl', 'to': '2025-03-23'},
                       {'member': 'marcus', 'from': '2025-03-24'}],
         'sub': 'pschorr'},
        {'occupants': FRESH_SITZ, 'sub': FRESH_VERTRETUNG},
    ],
}

# Vor der Neubesetzung am 06.03.2023 ist die Besetzung unbekannt. Zwischen
# März 2023 und November 2024 schieden nur Mitglieder aus (John, Gruebl),
# die im November 2024 nicht im HVFA sassen; ab dem 06.03.2023 gilt deshalb
# die belegte Besetzung.
HVFA = {
    'from': '2023-03-06', 'to': '2026-04-30', 'chair': 'dollinger',
    'seats': [
        {'member': 'stanglmaier'},
        {'member': 'fincke'},
        {'member': 'lauterbach'},
        {'member': 'linz_kilian'},
        {'member': 'pschorr'},
        {'member': 'weber'},
        {'member': 'welter'},
        {'member': 'gruber', 'sub': [{'member': 'hobmaier', 'from': '2024-10-21'}]},
        {'member': 'grundner'},
        {'member': 'heinz'},
        {'member': 'von_pressentin'},
    ],
}

PA_SUBS = {
    'pschorr': [{'member': 'beubl', 'from': '2023-03-27', 'to': '2025-03-23'},
                {'member': 'marcus', 'from': '2025-03-24'}],
    'gruber': [{'member': 'john', 'from': '2023-06-26', 'to': '2023-07-23'},
               {'member': 'strobl', 'from': '2023-07-24'}],
}


def rpa(alt):
    """Den Vorsitz hatte bis zum 24.03.2025 Beubl, danach Lauterbach. Die
    uebrigen Sitze entsprechen der Besetzung von 2025; wer vor den Wechseln
    von 2022 und 2023 sass, ist nicht belegt."""
    sitze = {s['member']: s for s in alt['seats']}
    hobmaier_sitz = {'occupants': [{'member': 'gruebl', 'to': '2024-10-20'},
                                   {'member': 'hobmaier', 'from': '2024-10-21'}],
                     'sub': [{'member': 'kaestl', 'from': '2023-06-26'}]}
    vor = {
        'from': '2020-05-01', 'to': '2025-03-23', 'chair': 'beubl',
        # Beubls Vertretung im Vorsitz: wie beim SPD-Sitz danach
        'chairSub': 'pschorr',
        'seats': [sitze['linz_karin'], sitze['tristl'],
                  {'member': 'lauterbach', 'sub': alt['chairSub'], 'role': 'Stellv. Vorsitzender'},
                  dict(hobmaier_sitz), sitze['becher_a'], sitze['beibl']],
    }
    nach = {
        'from': '2025-03-24', 'to': '2026-04-30', 'chair': 'lauterbach', 'chairSub': alt['chairSub'],
        'seats': [sitze['linz_karin'], sitze['tristl'], sitze['marcus'],
                  dict(hobmaier_sitz, role='Stellv. Vorsitzender'), sitze['becher_a'], sitze['beibl']],
    }
    return [vor, nach]


def main():
    bodies = json.load(open(PFAD, encoding='utf-8'))
    by = {b['id']: b for b in bodies}

    def periode(bid):
        return next(c for c in by[bid]['seatConfigs'] if c.get('from') == '2020-05-01')

    for s in periode('bpu')['seats']:
        schluessel = s.get('member') or s['occupants'][0]['member']
        if schluessel in BPU_SUBS:
            s['sub'] = BPU_SUBS[schluessel]

    for bid, neu in (('ar_klaeranlage', [AUFSICHTSRAT]), ('hvfa', [HVFA])):
        cfgs = by[bid]['seatConfigs']
        i = cfgs.index(periode(bid))
        cfgs[i:i + 1] = neu

    for s in periode('pa')['seats']:
        if s['member'] in PA_SUBS:
            s['sub'] = PA_SUBS[s['member']]

    cfgs = by['rpa']['seatConfigs']
    alt = periode('rpa')
    i = cfgs.index(alt)
    cfgs[i:i + 1] = rpa(alt)

    with open(PFAD, 'w', encoding='utf-8') as f:
        json.dump(bodies, f, ensure_ascii=False, indent=2)
        f.write('\n')


if __name__ == '__main__':
    main()
