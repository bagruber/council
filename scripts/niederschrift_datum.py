"""Trägt in sessions.json ein, wann eine Niederschrift genehmigt und wann sie veröffentlicht wurde.

`veroeffentlichtQuelle` sagt, woher das Datum kommt:

- ris: aus dem Ratsinformationssystem, das es öffentlich nicht anzeigt. Wird von
  Hand eingetragen, dieses Skript lässt es stehen.
- pdf: Erstellungsdatum der PDF. Eine Obergrenze, die Datei kann jünger sein als
  die Veröffentlichung. Geprüft im November 2026 an 23 Niederschriften mit beiden
  Daten: neunmal gleich, 14-mal die PDF bis zu 33 Tage später, nie früher.
- unbekannt: Die PDF stammt von einem Tag in NEU_ERZEUGT, das Datum sagt also nichts.

Liegt eine PDF im Ordner, ist aber noch nicht eingearbeitet, bekommt die Sitzung
das Datum trotzdem: Online ist sie ja schon.

`genehmigt` kommt aus der späteren Niederschrift, in der die Genehmigung steht.
"""
import json, os, re

from pypdf import PdfReader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSIONS = os.path.join(ROOT, 'data', 'sessions.json')
PDFS = os.path.join(ROOT, 'data', 'niederschriften')
KUERZEL = {'stadtrat': 'SR', 'bpu': 'BPU', 'hvfa': 'HVF'}

# 55 Stadtrats-Niederschriften von 2020 bis 2024 tragen dieses Datum, stehen im
# Ratsinformationssystem aber nicht unter den Veröffentlichungen ab 07.07.2026.
NEU_ERZEUGT = {'2026-07-27'}

MONATE = {m: i + 1 for i, m in enumerate(
    'Januar Februar März April Mai Juni Juli August September Oktober November Dezember'.split())}
DATUM = re.compile(r'(\d{1,2})\.\s?(?:(\d{1,2})\.\s?|(' + '|'.join(MONATE) + r')\s)(\d{4}|\d{2}(?!\d))?')
GREMIUM = (('hvfa', r'HVF|Hauptverwaltung|Finanzausschuss'),
           ('bpu', r'Bauausschuss|Umwelt\s?-?\s?aus\s?-?\s?schuss'),
           ('stadtrat', r'StR|Stadtrat'))


def pdf_datum(pfad):
    m = re.match(r'D:(\d{4})(\d{2})(\d{2})', PdfReader(pfad).metadata['/CreationDate'])
    return f'{m[1]}-{m[2]}-{m[3]}'


def daten_in(text, sitzung):
    """Daten aus einem Genehmigungssatz. Ohne Jahr ('vom 06.07. und 20.07.2020')
    gilt das nächste genannte Jahr, sonst das der genehmigenden Sitzung."""
    treffer = [(int(m[1]), int(m[2]) if m[2] else MONATE[m[3]], m[4]) for m in DATUM.finditer(text)]
    jahr, aus = None, []
    for tag, monat, j in reversed(treffer):
        jahr = (j if len(j) == 4 else '20' + j) if j else jahr
        iso = f'{jahr or sitzung[:4]}-{monat:02d}-{tag:02d}'
        if not jahr and iso >= sitzung:
            iso = f'{int(sitzung[:4]) - 1}-{monat:02d}-{tag:02d}'
        aus.append(iso)
    return aus


def genehmigungen(text, art, sitzung, register):
    """Liefert die Sitzungen, deren Niederschrift diese Sitzung genehmigt hat."""
    text = ' '.join(text.split())
    stellen = re.finditer(r'genehmigung[^§]{0,220}?(?:niederschrift|protokoll)[^§]{0,200}'
                          r'|genehmigt[^§]{0,120}?(?:niederschrift|protokoll)[^§]{0,160}'
                          r'|(?:niederschrift|protokoll)[^§]{0,160}?genehmigt', text, re.I)
    aus = set()
    for m in stellen:
        # Der Satz endet beim Ergebnis oder beim nächsten Tagesordnungspunkt.
        satz = re.split(r'Beschlossen|Abgelehnt|Vertagt|\s\d{1,2}(?:\.\d{1,2})?\s[A-ZÄÖÜ]', m[0])[0]
        for iso in daten_in(satz, sitzung):
            if iso >= sitzung:
                continue
            kandidaten = [t for t in KUERZEL if (iso, t) in register]
            if not kandidaten:
                continue
            genannt = [t for t, muster in GREMIUM if re.search(muster, satz) and t in kandidaten]
            aus.add(register[iso, genannt[0] if genannt else art if art in kandidaten else kandidaten[0]])
    return aus


def einordnen(s, felder):
    """Setzt die Felder direkt hinter `niederschrift`, der Rest bleibt, wie er ist."""
    rest = [(k, v) for k, v in s.items() if k not in ('veroeffentlicht', 'veroeffentlichtQuelle', 'genehmigt')]
    pos = [k for k, _ in rest].index('niederschrift') + 1
    return dict(rest[:pos] + [(k, v) for k, v in felder if v] + rest[pos:])


with open(SESSIONS, encoding='utf-8') as f:
    sessions = json.load(f)

register = {(s['date'], s['type']): s['id'] for s in sessions}
art_von = {v: k for k, v in KUERZEL.items()}
genehmigt = {}
pdf_daten = {}
for name in sorted(os.listdir(PDFS)):
    m = re.fullmatch(r'(SR|BPU|HVF)_(\d{4})(\d{2})(\d{2})\.pdf', name)
    if not m:
        continue
    sitzung = f'{m[2]}-{m[3]}-{m[4]}'
    pfad = os.path.join(PDFS, name)
    pdf_daten[art_von[m[1]], sitzung] = pdf_datum(pfad)
    text = ' '.join(p.extract_text() or '' for p in PdfReader(pfad).pages)
    for sid in genehmigungen(text, art_von[m[1]], sitzung, register):
        genehmigt[sid] = min(genehmigt.get(sid, sitzung), sitzung)

geaendert = 0
for i, s in enumerate(sessions):
    datum, quelle = s.get('veroeffentlicht'), s.get('veroeffentlichtQuelle')
    if quelle != 'ris' and (s['type'], s['date']) in pdf_daten:
        datum = pdf_daten[s['type'], s['date']]
        quelle = 'pdf'
        if datum in NEU_ERZEUGT:
            datum, quelle = None, 'unbekannt'
    neu = einordnen(s, [('veroeffentlicht', datum), ('veroeffentlichtQuelle', quelle),
                        ('genehmigt', genehmigt.get(s['id']))])
    if list(neu.items()) != list(s.items()):
        geaendert += 1
        sessions[i] = neu

with open(SESSIONS, 'w', encoding='utf-8') as f:
    json.dump(sessions, f, ensure_ascii=False, indent=2)
    f.write('\n')

print(f'{geaendert} Sitzungen geändert')
