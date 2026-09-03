"""Traegt die Presserecherche vom 02.09.2026 ein, nach Durchsicht durch den
Betreiber.

Drei Arten von Eintrag, die auseinandergehalten werden muessen:

COMPLETE  Die Zeitung nennt eine Seite vollstaendig, und die Zahlen der
          Niederschrift gehen auf. Dann ist die Gegenseite keine Vermutung,
          sondern eine Rechnung - das Votum wird `named`.

PARTIAL   Einzelne Positionen sind belegt, der Rest bleibt offen. Mit
          `evidence` wird unterschieden, worauf der Eintrag beruht:
          "hart" = die Zeitung berichtet eine Abstimmung, "weich" = sie
          berichtet eine Wortmeldung. Wer etwas befuerwortet hat, muss nicht
          dafuer gestimmt haben; das steht als `voterEvidence` am Votum und
          wird in der Oberflaeche als Hinweis ausgewiesen.

AGENDA    Der Artikel gehoert zum Tagesordnungspunkt, liefert aber keine
          Stimmdaten - oder das Votum ist ohnehin schon namentlich. Dann
          haengt er am Agenda-Eintrag, nicht an `source`. Ein namentliches
          Votum aus der Niederschrift wird durch einen Zeitungsbericht
          nicht zu einem Pressebeleg.

Aufruf ohne Argument = Probelauf, --apply schreibt.
"""
import json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')

M = 'https://www.merkur.de/lokales/freising/moosburg-ort29088/'
SZ = 'https://www.sueddeutsche.de/muenchen/freising/'

ARTICLES = [
    ('merkur_2020-06-19_waermenetz-schulzentrum', 'merkur', '2020-06-19',
     'Nahwärme soll Schulen heizen',
     M + 'nahwaerme-soll-schulen-heizen-moosburg-setzt-auf-erneuerbare-energien-kritik-an-kostenvergleich-13804394.html'),
    ('merkur_2020-12-16_haushalt-2021', 'merkur', '2020-12-16',
     'Moosburg schnürt Rekord-Haushalt für 2021',
     M + 'unaufschiebbare-grossprojekte-moosburg-schnuert-rekord-haushalt-fuer-2021-90133042.html'),
    ('merkur_2021-02-27_moria-aufnahme', 'merkur', '2021-02-27',
     'Stadtrat erklärt sich gegen den Willen des Bürgermeisters zur Aufnahme bereit',
     M + 'moosburgs-buergermeister-wir-sind-nicht-zustaendig-stadtrat-erklaert-sich-gegen-seinen-willen-bereit-fluechtlinge-aufzunehmen-90218795.html'),
    ('merkur_2021-03-15_planetenviertel', 'merkur', '2021-03-15',
     'Debatte um Nachverdichtung im Planetenviertel – Grünen-Antrag gescheitert',
     M + 'debatte-um-nachverdichtung-im-moosburger-planetenviertel-gruenen-antrag-gescheitert-90242829.html'),
    ('merkur_2023-03-21_kreuzung-westerberg', 'merkur', '2023-03-21',
     'Umstrittene Kreuzung: Rückbau abgelehnt, jetzt sollen neue Ideen her',
     M + 'umstrittene-kreuzung-in-moosburg-rueckbau-abgelehnt-jetzt-sollen-neue-ideen-her-92161449.html'),
    ('merkur_2023-05-23_unterreit', 'merkur', '2023-05-23',
     'Stadträte sagen Ja zum Planungsverfahren, Grüne üben Kritik',
     M + 'umstrittenes-gewerbegebiet-in-moosburg-stadtraete-sagen-ja-zum-planungsverfahren-gruene-ueben-kritik-92296039.html'),
    ('sz_2024-07-16_rockermaier-bauantraege', 'sz', '2024-07-16',
     'Bauanträge fürs Rockermaier-Areal',
     SZ + 'moosburg-neubaugebiet-rockermaier-areal-bauantraege-bebauungsplan-staedtebaulicher-vertrag-erschliessung-nachfolgekosten-lux.2FDMzAGVyhZL6VBrZMdfQZ'),
    ('merkur_2025-02-18_wohnanlage-stadtwaldstrasse', 'merkur', '2025-02-18',
     'Stadträte lehnen Wohnanlage ab – Bauträger wirbt trotzdem bereits dafür',
     M + 'moosburgs-stadtraete-lehnen-wohnanlage-ab-bautraeger-wirbt-trotzdem-bereits-dafuer-93577197.html'),
    ('merkur_2025-04-30_badegebuehren', 'merkur', '2025-04-30',
     'Badespaß wird teurer: Moosburg erhöht Freibad-Preise',
     M + 'badespass-wird-teuer-moosburg-erhoeht-freibad-preise-und-denkt-laut-ueber-parkgebuehren-nach-93706810.html'),
    ('sz_2026-05-13_buergermeister-stellvertreter', 'sz', '2026-05-13',
     'Wahl der Bürgermeister-Stellvertreter',
     SZ + 'moosburg-stadtrat-wahl-buergermeister-stellvertreter-li.3479031'),
    ('merkur_2026-05-27_bahnhofstrasse-mfh', 'merkur', '2026-05-27',
     'Stadtrat gibt Widerstand gegen Zwölf-Parteien-Haus auf',
     M + 'umstrittener-bauantrag-moosburgs-stadtrat-gibt-widerstand-gegen-zwoelf-parteien-haus-auf-94323101.html'),
]

# Eine Seite vollstaendig belegt -> Votum wird namentlich.
COMPLETE = {
    # "Mit der Gegenstimme von Pschorr beschloss das Gremium ..."
    'sr_20200615_08': ('merkur_2020-06-19_waermenetz-schulzentrum', {'pschorr': 'no'}),
    # "Ein kategorisches Nein zu Preiserhoehungen kam nur von Alexander Strobl"
    'sr_20250428_06': ('merkur_2025-04-30_badegebuehren', {'strobl': 'no'}),
}

# Einzelne Positionen belegt. evidence: "hart" = berichtete Abstimmung,
# "weich" = Wortmeldung in der Debatte.
PARTIAL = {
    # "gegen die Stimmen von Verena Beibl, Gerd Beubl, Julian Gruebl (Fresh)
    #  und Kilian Linz (Gruene) angenommen" - gilt fuer alle 7:4 der Sitzung
    'bpu_20240715_05': ('sz_2024-07-16_rockermaier-bauantraege', {
        'beibl': 'no', 'beubl': 'no', 'gruebl': 'no', 'linz_kilian': 'no'}, 'hart'),
    'bpu_20240715_06': ('sz_2024-07-16_rockermaier-bauantraege', {
        'beibl': 'no', 'beubl': 'no', 'gruebl': 'no', 'linz_kilian': 'no'}, 'hart'),
    'bpu_20240715_07': ('sz_2024-07-16_rockermaier-bauantraege', {
        'beibl': 'no', 'beubl': 'no', 'gruebl': 'no', 'linz_kilian': 'no'}, 'hart'),
    'bpu_20240715_08': ('sz_2024-07-16_rockermaier-bauantraege', {
        'beibl': 'no', 'beubl': 'no', 'gruebl': 'no', 'linz_kilian': 'no'}, 'hart'),
    'bpu_20240715_09': ('sz_2024-07-16_rockermaier-bauantraege', {
        'beibl': 'no', 'beubl': 'no', 'gruebl': 'no', 'linz_kilian': 'no'}, 'hart'),

    # Moria: Dollinger wollte gar nicht abstimmen lassen, die drei anderen
    # sprachen im Antragssinn. Keine Abstimmungssaetze - alles weich.
    'sr_20210208_07': ('merkur_2021-02-27_moria-aufnahme', {
        'dollinger': 'no', 'becher_j': 'yes', 'beibl': 'yes', 'beubl': 'yes'}, 'weich'),

    # Planetenviertel. ACHTUNG, der Beschluss ist invertiert formuliert:
    # _16 beschliesst, VON der Aufstellung eines Bebauungsplans ABZUSEHEN.
    # Wer den Bebauungsplan wollte, stimmt hier also mit Nein.
    'sr_20210308_16': ('merkur_2021-03-15_planetenviertel', {
        'wagner': 'no', 'kaestl': 'no', 'beubl': 'yes', 'heinz': 'yes'}, 'weich'),
    # _17 beauftragt das Plangutachten - Heinz' Gegenantrag.
    'sr_20210308_17': ('merkur_2021-03-15_planetenviertel', {'heinz': 'yes'}, 'weich'),

    # Ausschussgroesse: Unterzeichner des Antrags, soweit anwesend.
    # Kaestl und Gruebl stehen schon drin, John fehlte an dem Abend.
    'sr_20230424_04': ('merkur_2023-04-24_ausschussgroesse', {
        'fincke': 'yes', 'stanglmaier': 'yes'}, 'weich'),

    'sr_20250428_04': ('merkur_2025-04-30_badegebuehren', {'marcus': 'yes'}, 'weich'),
    'sr_20250428_05': ('merkur_2025-04-30_badegebuehren', {'stanglmaier': 'yes'}, 'weich'),
}

# Artikel gehoert zum TOP, liefert aber keine Stimmdaten - oder das Votum ist
# schon namentlich aus der Niederschrift und der Artikel bestaetigt es nur.
AGENDA = {
    'merkur_2020-12-16_haushalt-2021': ['sr_20201214_03', 'sr_20201214_04'],
    'merkur_2023-03-21_kreuzung-westerberg': ['bpu_20230320_09', 'bpu_20230320_10'],
    'merkur_2023-05-23_unterreit': ['sr_20230522_02', 'sr_20230522_03'],
    'merkur_2025-02-18_wohnanlage-stadtwaldstrasse': ['bpu_20250116_03', 'bpu_20250116_04'],
    'sz_2026-05-13_buergermeister-stellvertreter': ['sr_20260511_01'],
    'merkur_2026-05-27_bahnhofstrasse-mfh': ['sr_20260518_04'],
}
# Artikel, die zu einem TOP ohne eigenes Votum gehoeren: (sessionId, TOP-Nummer)
AGENDA_TOP = {
    'merkur_2025-02-18_wohnanlage-stadtwaldstrasse': [('sr_20250210', 'Anfragen')],
}


def active(m, d):
    sp = m.get('periods') or [{'from': m.get('from'), 'to': m.get('to')}]
    return any((s.get('from') or '0') <= d and (not s.get('to') or s['to'] >= d)
               for s in sp)


def main():
    do_apply = '--apply' in sys.argv
    load = lambda n: json.load(open(os.path.join(DATA, n), encoding='utf-8'))
    press, votes, sessions = load('press.json'), load('votes.json'), load('sessions.json')
    members = load('members.json')['members']
    vmap = {v['id']: v for v in votes}
    smap = {s['id']: s for s in sessions}

    known = {a['id'] for a in press}
    for pid, media, date, title, url in ARTICLES:
        if pid in known:
            print('  = Artikel schon vorhanden: ' + pid)
            continue
        press.append({'id': pid, 'media': media, 'date': date, 'title': title, 'url': url})
        print('  + Artikel ' + pid)

    for vid, (pid, stances) in COMPLETE.items():
        v, s = vmap[vid], smap[vmap[vid]['sessionId']]
        live = [m['id'] for m in members if active(m, v['date'])]
        absent = list(s.get('absent') or [])
        r = v['results']
        if r['yes'] + r['no'] + r['absent'] != len(live):
            print('  ! %s: %s+%s+%s != %d Stimmberechtigte, uebersprungen'
                  % (vid, r['yes'], r['no'], r['absent'], len(live)))
            continue
        rest = [i for i in live if i not in absent and i not in stances]
        side = 'yes' if r['no'] == len(stances) else 'no'
        v['type'] = 'named'
        v['results'] = {'yes': rest if side == 'yes' else list(stances),
                        'no': list(stances) if side == 'yes' else rest,
                        'absent': absent}
        v['source'] = {'tier': 'press', 'pressId': pid}
        v.pop('voters', None)
        print('  = %s vollstaendig: %d:%d + %d abwesend'
              % (vid, len(v['results']['yes']), len(v['results']['no']), len(absent)))

    for vid, (pid, stances, evidence) in PARTIAL.items():
        v = vmap[vid]
        v.setdefault('voters', {}).update(stances)
        if evidence == 'weich':
            v.setdefault('voterEvidence', {}).update({k: 'weich' for k in stances})
        if not v.get('source') or v['source'].get('tier') == 'press':
            v['source'] = {'tier': 'press', 'pressId': pid}
        print('  ~ %s [%s] %s' % (vid, evidence, stances))

    for pid, vids in AGENDA.items():
        for vid in vids:
            v = vmap.get(vid)
            if not v:
                print('  ! unbekanntes Votum ' + vid)
                continue
            for a in smap[v['sessionId']].get('agenda', []):
                if a.get('voteId') == vid or vid in (a.get('voteIds') or []):
                    lst = a.setdefault('press', [])
                    if pid not in lst:
                        lst.append(pid)
                        print('  > %s an TOP %s (%s)' % (pid, a.get('number'), vid))
                    break

    for pid, refs in AGENDA_TOP.items():
        for sid, needle in refs:
            for a in smap[sid].get('agenda', []):
                if needle.lower() in a['title'].lower():
                    lst = a.setdefault('press', [])
                    if pid not in lst:
                        lst.append(pid)
                        print('  > %s an TOP %s "%s"' % (pid, a.get('number'), a['title'][:40]))
                    break

    if not do_apply:
        print('\nProbelauf - nichts geschrieben. Mit --apply ausfuehren.')
        return
    for name, obj in (('press.json', press), ('votes.json', votes),
                      ('sessions.json', sessions)):
        with open(os.path.join(DATA, name), 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.write('\n')
    print('\ngeschrieben.')


if __name__ == '__main__':
    main()
