"""Zieht die Wechseldaten der Plenumssitze auf die tatsaechlichen Mandatsdaten.

Die geteilten Sitze der Periode 2020-2026 trugen nur monatsgenaue Grenzen
("2022-01"). Wo das Mandat spaeter endete als der Sitz wechselte, zeigte das
Halbrund die falsche Person — sichtbar etwa am 05.09.2022, wo Neumayr noch
Stadtraetin war, der Sitz aber schon auf Gruber stand.

Der Fehler fiel nur deshalb kaum auf, weil `buildSeatsFromBody` bevorzugt die
Person setzt, die im Vote auftaucht. Bei Voten ohne Einzelstimmen greift diese
Rettung nicht.
"""
import json, os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def main():
    path = os.path.join(DATA, 'members.json')
    data = json.load(open(path, encoding='utf-8'))
    by = {m['id']: m for m in data['members']}
    plenum = next(b for b in data['bodies'] if b.get('type') == 'plenum')

    fixed = 0
    for cfg in plenum['seatConfigs']:
        lo, hi = cfg.get('from'), cfg.get('to')
        for s in cfg['seats']:
            if len(s['occupants']) < 2:
                continue
            for o in s['occupants']:
                m = by[o['member']]
                spans = m.get('periods') or [{'from': m.get('from'), 'to': m.get('to')}]
                span = next(sp for sp in spans
                            if (not hi or (sp.get('from') or '0') <= hi)
                            and (not sp.get('to') or not lo or sp['to'] >= lo))
                for key in ('from', 'to'):
                    if key not in o:
                        continue
                    want = span.get(key)
                    # Der Sitz beginnt/endet nie ausserhalb der Konfiguration
                    if key == 'from' and lo and (not want or want < lo):
                        want = lo
                    if key == 'to' and hi and (not want or want > hi):
                        want = hi
                    if want and o[key] != want:
                        print(f"  {o['member']:14} {key:4} {o[key]:12} -> {want}")
                        o[key] = want
                        fixed += 1

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'  {fixed} Datumsangaben korrigiert')


if __name__ == '__main__':
    main()
