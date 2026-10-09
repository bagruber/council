"""Arbeitet 19 Stadtrats-Niederschriften ein (10.05.2021 bis 15.01.2024).

Die Sitzungen standen nur als leere Eintraege im Register. Dazu kommen vier
neue Dossiers (Bebauungsplaene 66 und 74, Wasserversorgung, Sparkasse) und
zwei Presse-Funde zu Sitzungen, die schon im Bestand sind.

Entscheidungen des Betreibers vom 09.10.2026, die hier umgesetzt sind:
  - Fehlt in einer Sitzung bei *allen* Beschluessen dieselbe eine Stimme ohne
    Vermerk (02.05.2022), gilt das als Zaehlfehler: alle Anwesenden, mit
    oeffentlichem Hinweis. Einzelne Luecken bleiben bei der 90-%-Regel.
  - Wer einen Antrag gestellt hat, hat dafuer gestimmt (hart).
  - Ueber Niederschriften aus der Zeit vor dem eigenen Mandat stimmen
    Nachruecker nicht mit (nicht stimmberechtigt).
  - Jeder Bebauungsplan wird ein eigenes Dossier.

Einmal laufen lassen:
    python scripts/sr_niederschriften_2021_2024.py
    python scripts/mark_inferable.py
"""
import json, os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def load(n):
    return json.load(open(os.path.join(DATA, n), encoding='utf-8'))


def save(n, obj):
    with open(os.path.join(DATA, n), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


MERKUR = 'https://www.merkur.de/lokales/freising/moosburg-ort29088/'
P = {
    'unterfuehrung': ('merkur', '2021-05-14', 'Moosburgs Pendler können hoffen: Durchgehender Tunnel am Bahnhof wird konkreter',
                      MERKUR + 'moosburgs-pendler-koennen-hoffen-durchgehender-tunnel-am-bahnhof-wird-konkreter-90576998.html'),
    'parkleitsystem': ('merkur', '2021-04-28', 'Per Sensoren: Moosburger Stadträte wollen lästige Parkplatz-Suche stoppen',
                       MERKUR + 'per-sensoren-moosburger-stadtraete-wollen-laestige-parkplatz-suche-stoppen-idee-stoesst-auf-widerstand-90480014.html'),
    'volksfestplatz': ('merkur', '2022-01-20', 'Debatte um Bebauung am Moosburger Volksfestplatz: Nachverdichtung zähneknirschend akzeptiert',
                       MERKUR + 'debatte-um-bebauung-am-moosburger-volksfestplatz-nachverdichtung-zaehneknirschend-akzeptiert-91246848.html'),
    'aerztehaus-bahnhof': ('merkur', '2022-02-10', 'Ärztehaus am Bahnhof: Moosburgs Stadtrat sagt Nein zu AfD-Antrag',
                           MERKUR + 'aerztehaus-bahnhof-moosburgs-stadtrat-sagt-nein-afd-antrag-autos-muessen-bald-radstaendern-weichen-91310118.html'),
    'kitagebuehren': ('merkur', '2022-02-22', 'Erhöhung der Kindergartengebühren in Moosburg kommt weniger geballt als befürchtet',
                      MERKUR + 'erhoehung-der-kindergartengebuehren-in-moosburg-kommt-weniger-geballt-als-befuerchtet-91365503.html'),
    'sparkassenfusion': ('merkur', '2022-03-15', 'Kritiker überstimmt: Fusion von Sparkassen Freising und Moosburg erhält grünes Licht',
                         MERKUR + 'kritiker-ueberstimmt-fusion-von-sparkassen-freising-und-moosburg-erhaelt-gruenes-licht-91412680.html'),
    'oberes-gereut': ('merkur', '2022-03-17', 'Bebauungsplan Oberes Gereuth Nord-Ost: Räte arbeiten weiter an Lückenschließung – Absage für Grünen-Antrag',
                      MERKUR + 'moosburg-bebauungsplan-oberes-gereuth-nord-ost-raete-arbeiten-weiter-an-lueckenschliessung-absage-fuer-gruenen-antrag-91415038.html'),
    'montessori': ('merkur', '2022-03-29', 'Geplante Montessorischule: Scheitert sie am Grundstückspreis der Stadt?',
                   MERKUR + 'geplante-montessorischule-moosburg-scheitert-sie-am-grundstueckspreis-der-stadt-91443745.html'),
    'sparkasse-vertrag': ('mz', '2022-03-31', 'Klare Mehrheit für künftige Sparkasse Freising Moosburg',
                          'https://www.idowa.de/regionen/moosburg/klare-mehrheit-fuer-kuenftige-sparkasse-freising-moosburg-1819397.html'),
    'freibadgebuehren': ('mz', '2022-04-05', 'Stadtrat erhöht Gebühren für Moosburger Freibad',
                         'https://www.idowa.de/regionen/moosburg/stadtrat-erhoeht-gebuehren-fuer-moosburger-freibad-1074601.html'),
    'pv-schuldach': ('merkur', '2022-05-05', 'Moosburg treibt Energieautarkie voran: Mehr Photovoltaik auf Schuldach beschlossen',
                     MERKUR + 'moosburg-treibt-energieautarkie-voran-mehr-photovoltaik-auf-schuldach-beschlossen-91521869.html'),
    'gruene-legen-nieder': ('merkur', '2022-05-06', 'Zwei Grünen-Stadträte legen Mandat nieder – Umbruch ist keine taktische Idee',
                            MERKUR + 'moosburg-zwei-gruenen-stadtraete-legen-mandat-nieder-umbruch-ist-keine-taktische-idee-91527723.html'),
    'schuelerzahlen': ('merkur', '2022-05-11', 'Steigende Schülerzahlen werden für Stadt Moosburg zur Herausforderung',
                       MERKUR + 'steigende-schuelerzahlen-werden-fuer-stadt-moosburg-zur-herausforderung-91536276.html'),
    'naturfriedhof': ('merkur', '2022-05-19', 'Grünen-Rätin fordert Trauerwald für Moosburg und erntet Kritik von Kirchen-Vertretern',
                      MERKUR + 'gruenen-raetin-fordert-trauerwald-fuer-moosburg-und-erntet-kritik-von-kirchen-vertretern-91558171.html'),
    'gruene-verabschiedet': ('merkur', '2022-05-31', 'Zwei langjährige Grünen-Stadträte verabschiedet – Nachfolger stehen fest',
                             MERKUR + 'moosburg-zwei-langjaehrige-gruenen-stadtraete-verabschiedet-nachfolger-stehen-fest-und-erklaeren-ziele-91583148.html'),
    'vereidigung': ('merkur', '2022-07-05', 'Neue Grünen-Stadträte vom Rathauschef vereidigt',
                    MERKUR + 'moosburg-neue-gruenen-stadtraete-vom-rathauschef-vereidigt-91649579.html'),
    'rasenmaeher': ('merkur', '2022-11-08', '„Absolut komisch“: FC Moosburg werden Rasenmäher geklaut – Stadtrat debattiert über Geld für Ersatz',
                    MERKUR + 'absolut-komisch-fc-moosburg-werden-rasenmaeher-geklaut-stadtrat-debattiert-ueber-geld-fuer-ersatz-91902934.html'),
    'eisstadion': ('merkur', '2022-11-09', 'Starker Tobak bei Eisstadion-Prüfung: Moosburger Stadträte haken bei Ungereimtheiten nach',
                   MERKUR + 'starker-tobak-bei-eisstadion-pruefung-moosburger-stadtraete-haken-bei-ungereimtheiten-nach-91905529.html'),
    'hallenmieten': ('merkur', '2022-11-24', 'Moosburg dreht an der Preisschraube: Städtische Hallen kosten künftig deutlich mehr Miete',
                     MERKUR + 'moosburg-dreht-an-der-preisschraube-staedtische-hallen-kosten-kuenftig-deutlich-mehr-miete-91934352.html'),
    'jungheinrich': ('merkur', '2023-09-26', 'Stadtratsbeschluss: Firma Jungheinrich darf erweitern',
                     MERKUR + 'stadtratsbeschluss-firma-jungheinrich-darf-erweitern-weltkonzern-zieht-moosburg-paris-vor-92543870.html'),
    'bahnhof-sanierung': ('merkur', '2023-09-29', 'Bahnhofsgebäude: Stadtrat trifft Entscheidung',
                          MERKUR + 'moosburg-bahnhofsgebaeude-stadtrat-trifft-entscheidung-92548617.html'),
    'wasserwerk': ('merkur', '2023-10-19', 'Kostenexplosion für Sanierung des Moosburger Wasserwerks',
                   MERKUR + 'mehr-als-eine-halbe-million-euro-teurer-kostenexplosion-fuer-sanierung-des-moosburger-wasserwerks-92585304.html'),
    'wassergebuehren': ('merkur', '2023-12-09', 'Neukalkulation: Wassergebühren steigen deutlich',
                        MERKUR + 'moosburg-neukalkulation-wassergebuehren-steigend-deutlich-92718976.html'),
}


def pid(k):
    return f'{P[k][0]}_{P[k][1]}_{k}'


T_BP66, T_BP74, T_WASSER, T_SPARKASSE = 't32', 't33', 't34', 't35'

NIEDERSCHRIFT = 'Der Stadtrat genehmigt den öffentlichen Teil der Niederschrift.'
ZAEHLFEHLER = ('Die Niederschrift weist 19:0 aus, anwesend waren 20. Weil alle Beschlüsse dieser '
               'Sitzung eine Stimme weniger zählen und keine Abwesenheit vermerkt ist, gehen wir '
               'von einem Zählfehler aus und führen alle Anwesenden.')
NACHRUECKER = ('{wer} hat über Niederschriften aus der Zeit vor dem eigenen Mandat nicht '
               'mitgestimmt. Die Niederschrift vermerkt das nicht; nur so geht die Zahl auf.')
ANTRAG = 'Antragsteller'

# Je Beschluss: (TOP, Titel, Text, Ja, Nein, Optionen). Optionen:
#   ohne      kurzfristig abwesend (Vermerk)  spaet  noch nicht oder nicht mehr da
#   beteiligt persoenliche Beteiligung
#   nsb       nicht stimmberechtigt       alle        Zaehlfehler, alle Anwesenden
#   ja/nein   namentlich laut Niederschrift
#   hart      {id: vote} aus der Presse oder dem Verfahren; ist eine Seite
#             damit voll, wird die andere errechnet
#   weich     {id: vote} aus einer Wortmeldung
#   antrag    [ids], die den Antrag gestellt haben (Ja, hart)
#   verfahren {id: vote}, aus dem Verfahren (etwa Nein zur Ablehnung des eigenen Antrags)
#   presse    pressId fuer hart/weich aus der Presse
#   thema, note
SITZUNGEN = [
    dict(id='sr_20210510', titel='8. Stadtratssitzung – Mai 2021', absent=['kaestl', 'reif', 'wittmann'],
         agenda=[('1', 'Mitteilungen des Ersten Bürgermeisters', 'formal'), ('2', 'Bürgerfragen', 'formal'),
                 ('3', 'Genehmigung der Niederschrift vom 12.04.2021'),
                 ('4', 'Einführung eines digitalen Parktickets / Smart City (Antrag StR Fincke)'),
                 ('4.1', 'Schluss mit dem Parksuchverkehr (Antrag StRe Fincke und John, 2. Teilantrag)'),
                 ('5', 'Voranfrage Aufstockung und Neubau von Wohngebäuden Stadtplatz 12, Georg-Hummel-Str./Rentamtstr.; Anhörung wegen Ersetzung des Einvernehmens'),
                 ('6', 'Verlängerung der Personenunterführung am Bahnhof; Machbarkeitsstudie und weiteres Vorgehen'),
                 ('7', 'Vorlage der Jahresrechnung 2020', None, 'Zur Kenntnis genommen.'), ('8', 'Anfragen', 'formal')],
         beschluesse=[
             ('3', 'Genehmigung der Niederschrift vom 12.04.2021', NIEDERSCHRIFT, 22, 0),
             ('4', 'Digitales Parkticket (Antrag Fincke)', 'Das digitale Parkticket wird über den Anbieter Pay by Phone eingeführt; die Zusatzgebühren tragen die Nutzer.', 22, 0),
             ('4.1', 'Parkbelegung in der App anzeigen (Antrag Fincke/John)', 'Kommt ein Parkleitsystem, prüft die Stadt, ob die Belegung auch über MeinMoosburg.de oder eine App angezeigt werden kann.', 21, 1),
             ('5', 'Stadtplatz 12 – Aufstockung: Einvernehmen verweigern', 'Antrag, das Einvernehmen zur Aufstockung zu verweigern, abgelehnt.', 8, 13, dict(beteiligt=['heinz'])),
             ('5', 'Georg-Hummel-/Rentamtstraße – Einvernehmen erteilen', 'Antrag, das Einvernehmen für die Neubauten zu erteilen (beide Dachvarianten fügen sich ein), abgelehnt.', 9, 12, dict(beteiligt=['heinz'])),
             ('6', 'Personenunterführung Bahnhof – Varianten 3 und 1a', 'Die Machbarkeitsstudie wird zur Kenntnis genommen; die Varianten 3 und 1a werden weiterverfolgt.', 22, 0, dict(thema=['t2'])),
             ('6', 'Personenunterführung Bahnhof – Kosten und Planung', 'Die Stadt übernimmt die Kosten; die Verwaltung wählt mit der Bahn ein Planungsbüro und legt eine Planungsvereinbarung für die Leistungsphasen 1 und 2 vor.', 22, 0, dict(thema=['t2'])),
         ]),
    dict(id='sr_20220117', titel='1. Stadtratssitzung – Januar 2022', absent=['lauterbach', 'von_pressentin'],
         agenda=[('1', 'Mitteilungen des Ersten Bürgermeisters', 'formal'), ('2', 'Bürgerfragen', 'formal'),
                 ('3', 'Genehmigung der Niederschriften (StR 11.10., 08.11., 06.12.2021; HVFA 25.11., 29.11.2021)'),
                 ('4', 'FF Thonstetten – Bestätigung des 1. und 2. Kommandanten'),
                 ('5', 'Bauangelegenheiten', 'formal'),
                 ('5.1', 'Vorbescheid Wohnanlage mit Tiefgarage Landshuter Str. 28/28a; Anhörung wegen Ersetzung des Einvernehmens'),
                 ('6', 'Erlass einer Stadtgrünverordnung – Beschluss über die Variante'),
                 ('7', 'Breitbandförderung Bundesprogramm'), ('8', 'Anfragen', 'formal')],
         beschluesse=[
             ('3', 'Genehmigung der Niederschriften', 'Der Stadtrat genehmigt die öffentlichen Teile der genannten Niederschriften.', 23, 0),
             ('4', 'FF Thonstetten – 1. Kommandant Martin Hörhammer', 'Martin Hörhammer wird als 1. Kommandant bestätigt.', 23, 0),
             ('4', 'FF Thonstetten – 2. Kommandant Reinhard Meilinger', 'Reinhard Meilinger wird als 2. Kommandant bestätigt.', 23, 0),
             ('5.1', 'Landshuter Str. 28 – kein Bebauungsplan', 'Die Empfehlung des Bauausschusses wird zur Kenntnis genommen; für das Gebiet zwischen Gärtnerstraße, Landshuter Straße und Staatsstraße wird kein Bebauungsplan aufgestellt.', 13, 10,
              dict(protokoll={'altenbeck': 'no'})),
             ('5.1', 'Landshuter Str. 28 – Einvernehmen zum Vorbescheid', 'Nach der Anhörung zur Ersetzung erteilt der Stadtrat das Einvernehmen für die Wohnanlage mit Tiefgarage.', 13, 10,
              dict(protokoll={'altenbeck': 'no'}, hart_gruppe='no', presse=pid('volksfestplatz'),
                   hart={m: 'no' for m in ['stanglmaier', 'altenbeck', 'becher_j', 'beibl', 'wagner', 'neumayr', 'gruebl', 'kaestl', 'john', 'beubl']})),
             ('6', 'Stadtgrünverordnung – Stammumfang 100 cm (Antrag Pschorr)', 'Antrag, den geschützten Stammumfang von 80 auf 100 cm anzuheben, abgelehnt.', 2, 21, dict(antrag=['pschorr'])),
             ('6', 'Stadtgrünverordnung – Entwurf 1 (Antrag Neumayr/Becher)', 'Antrag, Verordnungsentwurf 1 zum Verfahrensentwurf zu machen, abgelehnt.', 10, 13, dict(antrag=['neumayr', 'becher_j'])),
             ('6', 'Stadtgrünverordnung – Entwurf 2 (Änderungsantrag CSU)', 'Verordnungsentwurf 2 wird Verfahrensentwurf und öffentlich bekanntgemacht.', 15, 8),
             ('6', 'Stadtgrünverordnung – Ortsteile ausnehmen', 'Antrag, Niederambach, Kirchamper, Pfrombach/Aich und Thonstetten aus dem Geltungsbereich zu nehmen, abgelehnt.', 5, 18),
             ('6', 'Stadtgrünverordnung – Geltungsbereich', 'Der Entwurf des Geltungsbereichs wird gebilligt und mit dem Verordnungsentwurf bekanntgemacht.', 16, 7),
             ('7', 'Breitbandförderung – Teilnahme am Bundesprogramm', 'Die Stadt nimmt am Bundesförderprogramm Breitband und an der Kofinanzierungsrichtlinie teil.', 23, 0),
         ]),
    dict(id='sr_20220207', titel='2. Stadtratssitzung – Februar 2022', absent=['fincke', 'heinz', 'john'],
         partial=[{'member': 'kaestl', 'from': '20:05'}], ohne_alle=['kaestl'],
         agenda=[('1', 'Mitteilungen des Ersten Bürgermeisters', 'formal'),
                 ('2', 'Genehmigung der Niederschriften (StR 22.11.2021, HVFA 02.12.2021)'),
                 ('3', 'Bürgerfragen', 'formal'),
                 ('4', 'Einziehung eines Teilabschnitts der Saliterstraße'),
                 ('5', 'Anträge zum Bahnhof', 'formal'),
                 ('5.1', 'Erweiterung des Bahnhofsgebäudes für ein Ärztehaus (Antrag StR Welter)'),
                 ('5.2', 'Streichen der Außenwände des Bahnhofsgebäudes (Antrag CSU-Fraktion)'),
                 ('6', 'Anfragen', 'formal')],
         beschluesse=[
             ('2', 'Genehmigung der Niederschriften', NIEDERSCHRIFT, 21, 0,
              dict(note='Die Niederschrift druckt 23:0. Stimmberechtigt anwesend waren zu diesem Zeitpunkt 21; vermutlich ein Druckfehler.')),
             ('4', 'Saliterstraße – Teileinziehung einleiten', 'Für rund 140 m der Saliterstraße wird das Verfahren zur Teileinziehung eingeleitet.', 20, 1),
             ('5.1', 'Ärztehaus im Bahnhofsgebäude (Antrag Welter) abgelehnt', 'Der Stadtrat lehnt den Antrag ab, das Bahnhofsgebäude für ein Ärztehaus zu erweitern.', 20, 1,
              dict(hart={'welter': 'no'}, presse=pid('aerztehaus-bahnhof'), thema=['t2'])),
             ('5.2', 'Bahnhof – Außenwände streichen (Antrag CSU)', 'Die Fassade des Bahnhofsgebäudes wird neu gestrichen; 25.000 € werden überplanmäßig bereitgestellt.', 21, 0, dict(thema=['t2'])),
         ]),
    dict(id='sr_20220221', titel='3. Stadtratssitzung – Februar 2022', absent=['heinz', 'john', 'neumayr', 'weber', 'welter'],
         partial=[{'member': 'kaestl', 'from': '19:10'}, {'member': 'beibl', 'to': '21:00'}],
         agenda=[('1', 'Mitteilungen des Ersten Bürgermeisters', 'formal'), ('2', 'Bürgerfragen', 'formal'),
                 ('3', 'Genehmigung der Niederschriften vom 13.12.2021 und 17.01.2022'),
                 ('4', 'Änderung der Kindertageseinrichtungs-Gebührensatzung'), ('5', 'Anfragen', 'formal')],
         beschluesse=[
             ('3', 'Genehmigung der Niederschriften', NIEDERSCHRIFT, 19, 0, dict(spaet=['kaestl'])),
             ('4', 'Kitagebühren: +20 %, +8 %, dann 3 % jährlich', 'Kindergarten- und Hortgebühren steigen zum 01.09.2022 um 20 %, 2023/24 um 8 % und danach jährlich um 3 % bis 2027/28 (Vorschlag des Bürgermeisters).', 13, 7,
              dict(hart={'dollinger': 'yes'}, presse=pid('kitagebuehren'), thema=['t31'])),
             ('4', 'Kitagebühren – Geschwisterermäßigung für alle Einrichtungen', 'Die Geschwisterermäßigung gilt trägerunabhängig in allen Moosburger Einrichtungen.', 20, 0, dict(thema=['t31'])),
             ('4', 'Kitagebühren – Änderungssatzung', 'Die vierte Änderung der Gebührensatzung wird zum 01.09.2022 erlassen.', 20, 0, dict(thema=['t31'])),
         ]),
    dict(id='sr_20220314', titel='4. Stadtratssitzung – März 2022', start='19:00', absent=['dollinger', 'von_pressentin'],
         agenda=[('2', 'Mitteilungen des Ersten Bürgermeisters', 'formal'), ('3', 'Bürgerfragen', 'formal'),
                 ('4', 'Vereinigung der Stadt- und Kreissparkasse Moosburg mit der Sparkasse Freising'),
                 ('5', 'Verordnung für einen verkaufsoffenen Sonntag am 10.04.2022'),
                 ('6', 'Bebauungsplan Nr. 66 „Oberes Gereut Nordost“', 'formal'),
                 ('6.1', 'Vorstellung der Planung (Antrag auf Vertagung)'),
                 ('6.2–6.18', 'Sammelvote: 12 Stellungnahmen aus der Beteiligung (einstimmig)'),
                 ('6.3', 'Stellungnahme LRA Freising, Gesundheitsamt'),
                 ('6.4', 'Stellungnahme Wasserwirtschaftsamt München (Änderungsantrag Grundwassergutachten)'),
                 ('6.7', 'Stellungnahme Regierung von Oberbayern'),
                 ('6.8', 'Stellungnahme Deutsche Telekom'),
                 ('6.12', 'Stellungnahme LRA Freising, Immissionsschutz (Änderungsantrag Immissionsgutachten)'),
                 ('6.14', 'Stellungnahme LRA Freising, Naturschutz'),
                 ('6.19–6.26', 'Private Einwände, Billigung und Auslegung', None, 'Zurückgestellt.'),
                 ('7', 'Anfragen', 'formal')],
         notes=['Sitzungsleitung: Zweiter Bürgermeister Hadersdorfer; Bürgermeister Dollinger war erkrankt.'],
         beschluesse=[
             ('4', 'Sparkassen Moosburg und Freising – Vereinigung', 'Die Stadt stimmt der Auflösung des Zweckverbands zum 01.06.2022 und dem Beitritt zum Trägerzweckverband der Sparkasse Freising zu.', 14, 9,
              dict(weich={'hadersdorfer': 'yes', 'heinz': 'yes', 'pschorr': 'yes', 'wagner': 'no', 'grundner': 'no', 'beubl': 'no', 'kaestl': 'no'},
                   presse=pid('sparkassenfusion'), thema=[T_SPARKASSE])),
             ('4', 'Sparkasse – drei Verbandsräte', 'Moosburg entsendet drei Verbandsräte: den Ersten Bürgermeister und zwei vom Stadtrat gewählte, je mit Vertretung.', 23, 0, dict(thema=[T_SPARKASSE])),
             ('4', 'Sparkasse – Vorbehalt der übrigen Beschlüsse', 'Der Vollzug steht unter dem Vorbehalt gleichlautender Beschlüsse des Landkreises und der Sparkassengremien.', 23, 0, dict(thema=[T_SPARKASSE])),
             ('5', 'Verkaufsoffener Sonntag 10.04.2022', 'Die Verordnung wird erlassen.', 22, 1),
             ('6.1', 'BP 66 – Vertagung der Abwägung', 'Antrag der Grünen, das Verfahren zu vertagen, bis die Infrastruktur für weitere Wohngebiete geschaffen ist, abgelehnt.', 9, 14,
              dict(antrag=['stanglmaier'], weich={'heinz': 'no'}, presse=pid('oberes-gereut'), thema=[T_BP66])),
             ('6.2–6.18', 'BP 66 – 12 Stellungnahmen (Sammelvote)', 'Zwölf Stellungnahmen, jeweils 23:0: gleichlautende (ALE, ADBV), Wasserwirtschaftsamt (Verwaltung fragt nach einem Grundwassergutachten), Staatliches Bauamt, Regionaler Planungsverband, Eisenbahn-Bundesamt, Kläranlage, Vodafone, Altlasten, Kreisbrandrat (Wendehammer für die Drehleiter), AELF Erding, Bauernverband, Wasserwerk.', 23, 0, dict(thema=[T_BP66])),
             ('6.3', 'BP 66 – Gesundheitsamt', 'Alle Gebäude werden an Kanal und Trinkwasser angeschlossen.', 22, 0, dict(ohne=['linz_karin'], thema=[T_BP66])),
             ('6.4', 'BP 66 – Änderungsantrag Grundwasserströmungsgutachten', 'Antrag, ein Grundwasserströmungsgutachten zu verlangen, abgelehnt.', 9, 14, dict(thema=[T_BP66])),
             ('6.7', 'BP 66 – Regierung von Oberbayern', 'Der Plan entspricht den Erfordernissen der Raumordnung.', 22, 0, dict(ohne=['beibl'], thema=[T_BP66])),
             ('6.8', 'BP 66 – Deutsche Telekom', 'Keine Einwände; die Hinweise werden berücksichtigt.', 21, 0, dict(ohne=['beibl', 'altenbeck'], thema=[T_BP66])),
             ('6.12', 'BP 66 – Änderungsantrag Immissionsschutzgutachten', 'Antrag, ein Immissionsschutzgutachten für den Verkehr zum bestehenden Wohngebiet zu empfehlen, abgelehnt.', 9, 14, dict(thema=[T_BP66])),
             ('6.12', 'BP 66 – Immissionsschutzbehörde', 'Hinweise zu Tierhaltung und Flugplatz werden in den Plan aufgenommen.', 14, 9, dict(thema=[T_BP66])),
             ('6.14', 'BP 66 – Naturschutzbehörde', 'FFH-Verträglichkeit und artenschutzrechtliche Prüfung ergeben keine Beeinträchtigung.', 15, 8, dict(thema=[T_BP66])),
         ]),
    dict(id='sr_20220328', titel='5. Stadtratssitzung – März 2022', absent=['beibl', 'fincke', 'john', 'tristl'],
         agenda=[('1', 'Mitteilungen des Ersten Bürgermeisters', 'formal'), ('2', 'Bürgerfragen', 'formal'),
                 ('3', 'Teilfortschreibung des Landesentwicklungsprogramms (LEP)'),
                 ('4', 'Straßenverkehrsangelegenheiten', 'formal'),
                 ('4.1', 'Mitgliedschaft bei der Initiative „Lebenswerte Städte durch angemessene Geschwindigkeit“ (Antrag Stanglmaier, Beubl, Grübl, Reif)'),
                 ('5', 'Bebauungsplan Nr. 71 „Oberreit“ – Einstellung des Verfahrens'),
                 ('6', 'Bebauungsplan Nr. 76 „SO Montessori Moosburg“ – Einstellung des Verfahrens'),
                 ('7', 'Kaltmiete bei Neuvermietung, Sudetenlandstr. 46 und 48'), ('8', 'Anfragen', 'formal')],
         beschluesse=[
             ('3', 'LEP – dritte Startbahn streichen', 'Der Stadtrat fordert, das Ziel einer dritten Startbahn ersatzlos aus dem Landesentwicklungsprogramm zu streichen.', 21, 0),
             ('3', 'LEP – Vorranggebiet Flughafen aufheben', 'Der Stadtrat fordert, das Vorranggebiet Flughafen München aufzuheben, hilfsweise die Flächen für eine dritte Startbahn herauszunehmen.', 13, 8,
              dict(ja=['stanglmaier', 'becher_j', 'altenbeck', 'wagner', 'von_pressentin', 'reif', 'grundner', 'gruebl', 'neumayr', 'kaestl', 'beubl', 'haberl', 'dollinger'],
                   nein=['hadersdorfer', 'kieninger', 'lauterbach', 'heinz', 'pschorr', 'weber', 'welter', 'linz_karin'])),
             ('4.1', 'Beitritt „Lebenswerte Städte durch angemessene Geschwindigkeit“', 'Die Stadt beantragt die Mitgliedschaft in der Initiative.', 16, 5,
              dict(antrag=['stanglmaier', 'beubl', 'gruebl', 'reif'], thema=['t4'])),
             ('5', 'BP 71 „Oberreit“ – Verfahren eingestellt', 'Das Bauleitplanverfahren und die 6. FNP-Änderung werden eingestellt.', 21, 0),
             ('6', 'BP 76 „SO Montessori“ – Verfahren eingestellt', 'Das Bauleitplanverfahren und die 13. FNP-Änderung werden eingestellt.', 21, 0),
             ('7', 'Kaltmiete Sudetenlandstraße 46/48', 'Bei Neuvermietung steigt die Kaltmiete von 7,00 auf 8,00 €/m², die Garagenmiete von 42,50 auf 50,00 €.', 12, 9),
         ]),
    dict(id='sr_20220404', titel='6. Stadtratssitzung – April 2022', absent=['becher_j', 'fincke', 'wagner'],
         agenda=[('1', 'Mitteilungen des Ersten Bürgermeisters', 'formal'), ('2', 'Bürgerfragen', 'formal'),
                 ('3', 'Lehmabbau mit Wiederverfüllung, Abbaugebiet Stießberg'),
                 ('4', 'Verbandsräte des Zweckverbands Sparkasse Freising Moosburg'),
                 ('5', 'Zustandsbericht städtische Bäume', 'discussion'),
                 ('6', 'Neubau eines Abenteuerspielplatzes – Standort'),
                 ('7', 'Neufassung der Badegebührenordnung Freibad'), ('8', 'Anfragen', 'formal')],
         beschluesse=[
             ('3', 'Lehmabbau Stießberg', 'Einvernehmen für Lehmabbau mit Wiederverfüllung und Rekultivierung erteilt.', 20, 1),
             ('4', 'Sparkasse – Verbandsräte Hadersdorfer und Kieninger', 'Verbandsräte werden Georg Hadersdorfer (Vertretung Karin Linz) und Ludwig Kieninger (Vertretung Thomas Grundner).', 13, 8, dict(thema=[T_SPARKASSE])),
             ('6', 'Abenteuerspielplatz – Standort 1', 'Der Abenteuerspielplatz entsteht am Standort 1 (Flurstück 1135, südlicher Teil).', 17, 5),
             ('7', 'Badegebühren – Einzel- und Mehrfachkarten', 'Einzel- und 12er-Karten nach Vorschlag der Verwaltung; die Abendkarte gilt auch am Wochenende.', 21, 1, dict(thema=['t12'])),
             ('7', 'Badegebühren – Saisonkarten nach Verwaltungsvorschlag', 'Saisonkarten nach Vorschlag der Verwaltung abgelehnt.', 8, 14, dict(thema=['t12'])),
             ('7', 'Badegebühren – Saisonkarten (Antrag Stanglmaier)', 'Saisonkarten: Erwachsene 75 €, ermäßigt 55 €, Kinder 40 €, Familien 100/135 €.', 22, 0, dict(antrag=['stanglmaier'], thema=['t12'])),
             ('7', 'Badegebühren – ermäßigte Familienkarten', 'Ermäßigte Familienkarten (75/100 €) abgelehnt.', 8, 14, dict(thema=['t12'])),
             ('7', 'Badegebührenordnung', 'Die Badegebührenordnung wird mit den beschlossenen Sätzen neu gefasst.', 21, 1, dict(thema=['t12'])),
         ]),
    dict(id='sr_20220502', titel='7. Stadtratssitzung – Mai 2022', absent=['dollinger', 'becher_j', 'fincke', 'kaestl', 'lauterbach'],
         agenda=[('7', 'Mitteilungen des Zweiten Bürgermeisters', 'formal'), ('8', 'Bürgerfragen', 'formal'),
                 ('9', 'Genehmigung der Niederschriften (StR 07.02., 21.02.2022; BA 24.03.2022)'),
                 ('10', 'Neubau eines Abenteuerspielplatzes – Vorstellung der Planung', None, 'Zur Kenntnis genommen.'),
                 ('11', 'PV-Anlage mit 99,2 kWp auf dem Neubau der Anton-Vitzthum-Grundschule'), ('12', 'Anfragen', 'formal')],
         notes=['Sitzungsleitung: Zweiter Bürgermeister Hadersdorfer.'],
         beschluesse=[
             ('9', 'Genehmigung der Niederschriften', NIEDERSCHRIFT, 19, 0, dict(alle=True, note=ZAEHLFEHLER)),
             ('11', 'PV-Anlage Anton-Vitzthum-Grundschule', 'Auf dem Neubau entsteht eine PV-Anlage mit 99,2 kWp und 24-kWh-Speicher.', 19, 0, dict(alle=True, note=ZAEHLFEHLER)),
             ('11', 'PV-Anlage – Finanzierung', 'Die überplanmäßige Ausgabe wird genehmigt; 110 T€ kommen aus dem Ansatz für den Schulneubau.', 19, 0, dict(alle=True, note=ZAEHLFEHLER)),
             ('11', 'PV-Anlage – Umsetzung', 'Die Verwaltung setzt das Vorhaben um.', 19, 0, dict(alle=True, note=ZAEHLFEHLER)),
         ]),
    dict(id='sr_20220509', titel='8. Stadtratssitzung – Mai 2022', absent=['stanglmaier', 'fincke', 'heinz', 'john', 'tristl', 'wagner', 'welter'],
         agenda=[('1', 'Mitteilungen des Ersten Bürgermeisters', 'formal'), ('2', 'Bürgerfragen', 'formal'),
                 ('3', 'Genehmigung der Niederschriften vom 14.03. und 28.03.2022'),
                 ('4', 'Ausbau der Lände; Ausweisung als Fahrradstraße', None, 'Zurückgestellt.'),
                 ('5', 'Änderung des Flächennutzungsplans an der Moosstraße, Aich'),
                 ('6', 'Schulsprengel für das Baugebiet Amperauen'),
                 ('7', 'Vorlage der Jahresrechnung 2021', None, 'Zur Kenntnis genommen.'), ('8', 'Anfragen', 'formal')],
         beschluesse=[
             ('3', 'Genehmigung der Niederschriften', NIEDERSCHRIFT, 17, 0),
             ('5', 'FNP-Änderung Moosstraße, Aich', 'Der Flächennutzungsplan wird für einen Teil der Moosstraße geändert; die Verwaltung beauftragt ein Planungsbüro.', 18, 0),
             ('5', 'Moosstraße – Planungskostenvertrag', 'Mit dem Antragsteller wird ein Vertrag über die Planungskosten geschlossen.', 18, 0),
             ('6', 'Schulsprengel Amperauen', 'Das Baugebiet Amperauen wird der Theresia-Gerhardinger-Grundschule zugeordnet.', 18, 0, dict(thema=['t6', 't20'])),
         ]),
    dict(id='sr_20220530', titel='9. Stadtratssitzung – Mai 2022', absent=[],
         agenda=[('1', 'Mitteilungen des Ersten Bürgermeisters', 'formal'), ('2', 'Bürgerfragen', 'formal'),
                 ('3', 'Bebauungsplan Nr. 78 „Dr.-Schels-Straße“ – städtebaulicher Entwurf', 'discussion'),
                 ('4', 'Trauerpark/Naturfriedhof – Grundsatzbeschluss (Antrag StRin Altenbeck)'),
                 ('5', 'Stadtratsangelegenheiten', 'formal'),
                 ('5.1', 'Niederlegung des Mandats durch Evelin Altenbeck; Listennachfolge'),
                 ('5.2', 'Niederlegung des Mandats durch Alfred Wagner; Listennachfolge'), ('6', 'Anfragen', 'formal')],
         beschluesse=[
             ('4', 'Naturfriedhof – Antrag ablehnen', 'Vorschlag, den Antrag mangels Bedarf abzulehnen, abgelehnt.', 11, 14, dict(verfahren={'altenbeck': 'no'})),
             ('4', 'Naturfriedhof – nur Gespräch mit der Kirchenverwaltung', 'Vorschlag, lediglich das Gespräch mit der katholischen Kirchenverwaltung zu suchen, abgelehnt.', 9, 16),
             ('4', 'Naturfriedhof – grundsätzlich unterstützt', 'Der Stadtrat unterstützt einen Naturfriedhof grundsätzlich; die Verwaltung prüft Standort, Genehmigung, Erschließung, Betrieb und Kosten.', 17, 8, dict(antrag=['altenbeck'])),
             ('5.1', 'Niederlegung Altenbeck – A. Becher rückt nach', 'Der Stadtrat stellt das Ausscheiden zum 31.05.2022 fest; Alexandra Becher rückt nach.', 24, 0,
              dict(beteiligt=['altenbeck'], note='Die Niederschrift vermerkt nicht, wer nicht mitgestimmt hat; vermutlich die Ausscheidende selbst.')),
             ('5.2', 'Niederlegung Wagner – K. Linz rückt nach', 'Der Stadtrat stellt das Ausscheiden zum 31.05.2022 fest; Kilian Linz rückt nach.', 24, 0,
              dict(beteiligt=['wagner'], note='Die Niederschrift vermerkt nicht, wer nicht mitgestimmt hat; vermutlich der Ausscheidende selbst.')),
         ]),
    dict(id='sr_20220704', titel='10. Stadtratssitzung – Juli 2022', location='Schäfflerhalle',
         absent=['becher_j', 'fincke', 'john', 'kaestl', 'von_pressentin'],
         agenda=[('1', 'Mitteilungen des Ersten Bürgermeisters', 'formal'), ('2', 'Bürgerfragen', 'formal'),
                 ('3', 'Genehmigung der Niederschrift vom 02.05.2022'),
                 ('4', 'Stadtratsangelegenheiten', 'formal'),
                 ('4.1', 'Vereidigung von Alexandra Becher', 'formal'), ('4.2', 'Vereidigung von Kilian Linz', 'formal'),
                 ('4.3', 'Neubesetzung von Ausschüssen und Aufsichtsrat Kläranlage'),
                 ('5', 'Verkehrskonzept Moosburg – Endbericht'),
                 ('6', 'Bebauungsplan Nr. 51 „Großer Anger West“ (Gemeinde Langenbach) – Beteiligung'),
                 ('7', 'Dreigruppige Kinderkrippe Sonnensiedlung 1', 'formal'),
                 ('7.1', 'Vorplanung und Bauweise (Antrag Stanglmaier)'), ('8', 'Anfragen', 'formal')],
         beschluesse=[
             ('3', 'Genehmigung der Niederschrift vom 02.05.2022', NIEDERSCHRIFT, 17, 0, dict(nsb=['becher_a', 'linz_kilian'])),
             ('4.3', 'Neubesetzung der Ausschüsse', 'Die geänderte Besetzung der Ausschüsse wird bestätigt.', 19, 0),
             ('4.3', 'Aufsichtsrat Kläranlage: A. Becher für Wagner', 'Alexandra Becher wird als Nachfolgerin von Alfred Wagner in den Aufsichtsrat berufen.', 19, 0, dict(thema=['t30'])),
             ('5', 'Verkehrskonzept – Endbericht als Leitlinie', 'Der Endbericht wird zustimmend zur Kenntnis genommen; seine Ziele gelten als Leitlinie.', 19, 0, dict(ohne=['beibl'], thema=['t4'])),
             ('6', 'BP 51 Großer Anger West (Langenbach) – keine Einwände', 'Belange der Stadt sind nicht berührt.', 20, 0),
             ('7.1', 'Kinderkrippe Sonnensiedlung – Variante V2', 'Gebaut wird eine dreigruppige Krippe mit Wohngeschoss; Förderung und Raumprogramm werden mit der Regierung geklärt.', 19, 0, dict(thema=['t31'])),
             ('7.1', 'Kinderkrippe – Holzbauweise (Antrag Stanglmaier)', 'Antrag, die ganze Krippe in Holz zu bauen, abgelehnt.', 7, 12, dict(antrag=['stanglmaier'], thema=['t31'])),
             ('7.1', 'Kinderkrippe – Hybridbauweise', 'Die Krippe wird in Hybridbauweise errichtet: Erdgeschoss massiv, Obergeschoss in Holz.', 19, 0, dict(beteiligt=['heinz'], thema=['t31'])),
         ]),
    dict(id='sr_20220711', titel='11. Stadtratssitzung – Juli 2022', absent=['hadersdorfer', 'becher_j', 'grundner', 'john'],
         agenda=[('2', 'Mitteilungen des Ersten Bürgermeisters', 'formal'), ('3', 'Bürgerfragen', 'formal'),
                 ('4', 'Genehmigung der Niederschrift der Bauausschuss-Sitzung vom 23.05.2022'),
                 ('5', 'Einziehung eines Teilabschnitts der Saliterstraße'),
                 ('6', 'Bauangelegenheiten', 'formal'), ('6.1', 'Lager- und Gerätehaus Sempt 7'),
                 ('7', 'Bebauungsplan Nr. 66 „Oberes Gereut Nordost“ – Abwägung', 'formal'),
                 ('7.1', 'Sachstandsbericht', 'discussion'),
                 ('7.2–7.8', 'Sammelvote: 7 Stellungnahmen (einstimmig)'),
                 ('7.9', 'Billigungs- und Auslegungsbeschluss'),
                 ('8', 'Bebauungsplan Nr. 74 „Feldkirchen“ und 10. FNP-Änderung – Abwägung', 'formal'),
                 ('8.1', 'Sachstandsbericht', 'discussion'),
                 ('8.2–8.25', 'Sammelvote: 16 Stellungnahmen (einstimmig)'),
                 ('8.7–8.10', 'Sammelvote: 4 Stellungnahmen (Beibl kurz abwesend)'),
                 ('8.11–8.12', 'Sammelvote: 2 Stellungnahmen (Beibl und Fincke kurz abwesend)'),
                 ('8.13–8.14', 'Sammelvote: 2 Stellungnahmen (Fincke kurz abwesend)'),
                 ('8.26', 'Billigungs- und Auslegungsbeschluss'),
                 ('9', 'Landschaftsschutzgebiet „Ampertal“ – Anhörung zur 6. Änderungsverordnung'), ('10', 'Anfragen', 'formal')],
         beschluesse=[
             ('4', 'Genehmigung der Niederschrift BA 23.05.2022', NIEDERSCHRIFT, 19, 0),
             ('5', 'Saliterstraße – Teileinziehung', 'Rund 140 m der Saliterstraße werden eingezogen.', 20, 0),
             ('6.1', 'Lager- und Gerätehaus Sempt 7', 'Einvernehmen erteilt.', 20, 0),
             ('7.2–7.8', 'BP 66 – 7 Stellungnahmen (Sammelvote)', 'Sieben Stellungnahmen, jeweils 21:0: Straßenverkehrsbehörde (Wohnwege, Geh- und Radweg über die Wiesenstraße), SWM, Fliegerclub (Emissionen sind hinzunehmen) und vier private Einwände (Wohnhöfe, Grundwasser mit Beweissicherung, Verkehr und Naturschutz).', 21, 0, dict(thema=[T_BP66])),
             ('7.9', 'BP 66 – Billigung und öffentliche Auslegung', 'Der Entwurf in der Fassung vom 14.03.2022 wird gebilligt und öffentlich ausgelegt.', 21, 0, dict(thema=[T_BP66])),
             ('8.2–8.25', 'BP 74 – 16 Stellungnahmen (Sammelvote)', 'Sechzehn Stellungnahmen, jeweils 21:0, darunter Altlasten, Gesundheitsamt, Kreisarchäologie, Wasserwirtschaftsamt, Immissionsschutz, Naturschutz, Regierung von Oberbayern (Sondergebiet „Saatgutbetriebe Feldkirchen“), Denkmalpflege (Baufenster 7a bis 7 m Wandhöhe) und Kreisbrandrat.', 21, 0, dict(thema=[T_BP74])),
             ('8.7–8.10', 'BP 74 – 4 Stellungnahmen (Sammelvote)', 'Staatliches Bauamt, Eisenbahn-Bundesamt, Telekom, Handwerkskammer, jeweils 20:0.', 20, 0, dict(ohne=['beibl'], thema=[T_BP74])),
             ('8.11–8.12', 'BP 74 – 2 Stellungnahmen (Sammelvote)', 'AELF und Energienetze Bayern, jeweils 19:0.', 19, 0, dict(ohne=['beibl', 'fincke'], thema=[T_BP74])),
             ('8.13–8.14', 'BP 74 – 2 Stellungnahmen (Sammelvote)', 'bayernets und gleichlautende Stellungnahmen ohne Äußerung, jeweils 20:0.', 20, 0, dict(ohne=['fincke'], thema=[T_BP74])),
             ('8.26', 'BP 74 – Billigung und öffentliche Auslegung', 'Bebauungsplan mit Grünordnungsplan und 10. FNP-Änderung in der Fassung vom 09.06.2022 werden gebilligt und ausgelegt.', 21, 0, dict(thema=[T_BP74])),
             ('9', 'LSG Ampertal – keine Einwände', 'Gegen die 6. Änderungsverordnung bestehen keine Einwände.', 21, 0),
         ]),
    dict(id='sr_20220718', titel='12. Stadtratssitzung – Juli 2022', absent=['stanglmaier', 'becher_a', 'becher_j', 'heinz', 'tristl'],
         agenda=[('1', 'Mitteilungen des Ersten Bürgermeisters', 'formal'), ('2', 'Bürgerfragen', 'formal'),
                 ('3', 'Globalkalkulation Abwasser, Änderung der BGS-EWS'),
                 ('4', 'Finanzbericht des Kämmerers zum 1. Halbjahr 2022'), ('5', 'Anfragen', 'formal')],
         beschluesse=[
             ('3', 'Kanalherstellungsbeiträge erhöht', 'Die Beiträge steigen auf 1,40 €/m² Grundstücks- und 11,50 €/m² Geschossfläche.', 20, 0, dict(thema=['t30'])),
             ('3', 'Änderung der BGS-EWS', 'Die Änderungssatzung tritt zum 01.08.2022 in Kraft.', 20, 0, dict(thema=['t30'])),
             ('4', 'Halbjahresbericht 2022', 'Der Halbjahresbericht wird zur Kenntnis genommen.', 20, 0, dict(thema=['t7'])),
         ]),
    dict(id='sr_20220725', titel='13. Stadtratssitzung – Juli 2022', absent=['stanglmaier', 'becher_a', 'gruebl', 'heinz', 'john', 'neumayr', 'von_pressentin'],
         agenda=[('1', 'Mitteilungen des Ersten Bürgermeisters', 'formal'), ('2', 'Bürgerfragen', 'formal'),
                 ('3', 'Genehmigung der Niederschriften vom 09.05. und 30.05.2022'),
                 ('4', 'Kläranlage Moosburg GmbH', 'formal'),
                 ('4.1', 'Jahresabschluss 2021 und Ergebnisverwendung'), ('4.2', 'Entlastung des Aufsichtsrats für 2021'),
                 ('5', 'Heizkraftwerk Bader Energie – dritter Biomassekessel (BImSchG)'), ('6', 'Anfragen', 'formal')],
         beschluesse=[
             ('3', 'Genehmigung der Niederschriften', NIEDERSCHRIFT, 17, 0,
              dict(nsb=['linz_kilian'], note=NACHRUECKER.format(wer='Kilian Linz'))),
             ('4.1', 'Kläranlage – Jahresabschluss 2021', 'Empfehlung an die Gesellschafterversammlung, den Jahresabschluss festzustellen; der Überschuss wird vorgetragen.', 18, 0, dict(thema=['t30'])),
             ('4.2', 'Kläranlage – Entlastung des Aufsichtsrats 2021', 'Empfehlung, den Aufsichtsrat zu entlasten.', 13, 0,
              dict(beteiligt=['dollinger', 'weber', 'haberl', 'reif', 'beubl'], thema=['t30'])),
             ('5', 'Heizkraftwerk Bader Energie – keine Einwendungen', 'Gegen die Neugenehmigung mit drittem Biomassekessel bestehen keine Einwendungen.', 18, 0),
         ]),
    dict(id='sr_20221107', titel='18. Stadtratssitzung – November 2022', absent=['beubl', 'john', 'reif'],
         agenda=[('1', 'Mitteilungen des Ersten Bürgermeisters', 'formal'), ('2', 'Bürgerfragen', 'formal'),
                 ('3', 'Genehmigung der Niederschrift vom 19.09.2022'),
                 ('4', 'Zuschuss für den FC Moosburg (Rasenmäher)'),
                 ('5', 'Aufhebungssatzung zur Betriebssatzung des Wasserwerks'),
                 ('6', 'Städtebauliche Vereinbarungen des Wasserzweckverbands Baumgartner Gruppe'),
                 ('7', 'Örtliche Rechnungsprüfung – Jahresrechnung 2020', 'formal'),
                 ('7.1', 'Feststellung der Jahresrechnung 2020'), ('7.2', 'Entlastung zur Jahresrechnung 2020'), ('8', 'Anfragen', 'formal')],
         beschluesse=[
             ('3', 'Genehmigung der Niederschrift vom 19.09.2022', NIEDERSCHRIFT, 22, 0),
             ('4', 'Zuschuss FC Moosburg – 50 % für den Rasenmäher', 'Der FC Moosburg erhält 50 % der Kosten eines Rasenmähertraktors, höchstens 21.250 €.', 13, 9,
              dict(weich={'heinz': 'yes', 'lauterbach': 'yes', 'dollinger': 'no', 'beibl': 'no'}, presse=pid('rasenmaeher'))),
             ('5', 'Wasserwerk – Aufhebungssatzung zur Betriebssatzung', 'Die Betriebssatzung des Eigenbetriebs Wasserwerk wird aufgehoben.', 21, 0, dict(ohne=['hadersdorfer'], thema=[T_WASSER])),
             ('6', 'Wasserzweckverband – städtebauliche Vereinbarung', 'Die Stadt verpflichtet sich, künftige Neubaugebiete im Verbandsgebiet nach der Vereinbarung des Zweckverbands zu erschließen.', 21, 0, dict(ohne=['hadersdorfer'], thema=[T_WASSER])),
             ('7.1', 'Jahresrechnung 2020 festgestellt', 'Die Jahresrechnung 2020 wird festgestellt.', 22, 0, dict(thema=['t7'])),
             ('7.2', 'Entlastung zur Jahresrechnung 2020', 'Entlastung wird erteilt.', 21, 0, dict(beteiligt=['dollinger'], thema=['t7'])),
         ]),
    dict(id='sr_20230925', titel='15. Stadtratssitzung – September 2023', absent=['stanglmaier', 'becher_a', 'beubl', 'linz_karin'],
         partial=[{'member': 'kaestl', 'from': '19:15'}, {'member': 'beibl', 'to': '20:45'}, {'member': 'heinz', 'to': '21:30'},
                  {'member': 'von_pressentin', 'to': '22:00'}, {'member': 'grundner', 'to': '22:20'}],
         agenda=[('1', 'Mitteilungen des Ersten Bürgermeisters', 'formal'), ('2', 'Bürgerfragen', 'formal'),
                 ('3', 'Genehmigung der Niederschrift vom 12.06.2023'),
                 ('4', 'Bebauungsplan Nr. 80 „Degernpoint Nordost“ und 16. FNP-Änderung – Aufstellung'),
                 ('5', '1. Änderung des Bebauungsplans Nr. 52 „WA Amperauen“', 'formal'),
                 ('5.1', 'Stellungnahmen aus der Beteiligung'), ('5.2', 'Satzungsbeschluss'),
                 ('6', 'Empfangsgebäude Bahnhof Moosburg', 'formal'),
                 ('6.1', 'Ergebnisse der Bahnhofsumfrage', 'discussion'),
                 ('6.2', 'Fördermöglichkeiten und Ausbauvariante'),
                 ('7', 'Verkaufsoffener Sonntag am 15.10.2023'), ('8', 'Anfragen', 'formal')],
         beschluesse=[
             ('3', 'Genehmigung der Niederschrift vom 12.06.2023', NIEDERSCHRIFT, 21, 0),
             ('4', 'BP 80 Degernpoint Nordost II – Aufstellung', 'Der Bebauungsplan wird aufgestellt; mit dem Antragsteller wird ein städtebaulicher Vertrag verhandelt.', 21, 0, dict(thema=['t18'])),
             ('4', 'BP 80 – 16. FNP-Änderung', 'Der Flächennutzungsplan wird im Parallelverfahren geändert.', 21, 0, dict(thema=['t18'])),
             ('4', 'BP 80 – frühzeitige Beteiligung', 'Die Verwaltung führt die frühzeitige Beteiligung durch.', 21, 0, dict(thema=['t18'])),
             ('5.1', 'BP 52 Amperauen, 1. Änderung – keine Stellungnahmen', 'Während der Auslegung gingen keine Stellungnahmen ein.', 20, 0, dict(ohne=['weber'], thema=['t20'])),
             ('5.2', 'BP 52 Amperauen, 1. Änderung – Satzungsbeschluss', 'Die 1. Änderung wird als Satzung beschlossen.', 21, 0, dict(thema=['t20'])),
             ('6.2', 'Bahnhof – Generalsanierung', 'Das Empfangsgebäude wird generalsaniert, im Rahmen der Förderbedingungen.', 18, 2,
              dict(weich={'dollinger': 'yes', 'becher_j': 'yes', 'welter': 'no'}, presse=pid('bahnhof-sanierung'), thema=['t2'])),
             ('7', 'Verkaufsoffener Sonntag 15.10.2023', 'Die Verordnung wird erlassen.', 19, 1),
         ]),
    dict(id='sr_20231016', titel='16. Stadtratssitzung – Oktober 2023', absent=['stanglmaier', 'becher_j', 'beibl', 'tristl'],
         agenda=[('2', 'Mitteilungen des Ersten Bürgermeisters', 'formal'), ('3', 'Bürgerfragen', 'formal'),
                 ('4', 'Sanierung der Aufbereitungsanlage des Wasserwerks – Entwurfsplanung'),
                 ('5', 'Theresia-Gerhardinger-Grundschule – 2. Bauabschnitt mit Aufzug'), ('6', 'Anfragen', 'formal')],
         beschluesse=[
             ('4', 'Wasserwerk – Ausführungsplanung und Ausschreibung', 'Die Entwurfsplanung wird zur Ausführungsplanung weiterentwickelt; das Büro Kienlein schreibt aus.', 21, 0, dict(thema=[T_WASSER])),
             ('4', 'Wasserwerk – Netzersatzanlage vorab ausschreiben', 'Die neue Netzersatzanlage wird vorab im Oktober 2023 ausgeschrieben.', 21, 0, dict(thema=[T_WASSER])),
             ('5', 'Grundschule – barrierefreier Umbau mit Aufzug', 'Der 2. Bauabschnitt wird mit geschätzten Kosten von 552.369 € beauftragt.', 20, 0, dict(beteiligt=['heinz'], thema=['t6'])),
         ]),
    dict(id='sr_20231204', titel='19. Stadtratssitzung – Dezember 2023', absent=['lauterbach', 'linz_kilian', 'pschorr', 'von_pressentin'],
         partial=[{'member': 'gruber', 'from': '18:25'}, {'member': 'beibl', 'from': '18:40', 'to': '19:15'}, {'member': 'kaestl', 'from': '18:50'}],
         ohne_alle=['beibl'],
         agenda=[('2', 'Mitteilungen des Ersten Bürgermeisters', 'formal'), ('3', 'Bürgerfragen', 'formal'),
                 ('4', 'Genehmigung der Niederschrift vom 16.10.2023'),
                 ('5', 'Neufestsetzung der Wassergebühren', 'formal'),
                 ('5.1', 'Gebührenkalkulation Wasser 2024 bis 2027'),
                 ('5.2', 'Änderungssatzung zur Wasserabgabesatzung und Neufassung der BGS-WAS'), ('6', 'Anfragen', 'formal')],
         beschluesse=[
             ('4', 'Genehmigung der Niederschrift vom 16.10.2023', NIEDERSCHRIFT, 20, 0),
             ('5.1', 'Wasser – kalkulatorischer Zinssatz 3 %', 'Der kalkulatorische Zinssatz wird auf 3,0 % festgesetzt.', 20, 0, dict(thema=[T_WASSER])),
             ('5.1', 'Wasser – Grundgebühren +50 %', 'Die Grundgebühren steigen um 50 %.', 20, 0, dict(thema=[T_WASSER])),
             ('5.1', 'Wasser – Verbrauchsgebühr', 'Die Verbrauchsgebühr beträgt 1,89 €/m³ für 2024/25 und 2,15 €/m³ für 2026/27.', 20, 0, dict(thema=[T_WASSER])),
             ('5.2', 'Änderungssatzung Wasserabgabesatzung', 'Die Änderungssatzung zum 01.01.2024 wird beschlossen.', 19, 0, dict(ohne=['gruber'], thema=[T_WASSER])),
             ('5.2', 'Neufassung BGS-WAS', 'Die Beitrags- und Gebührensatzung zum 01.01.2024 wird neu gefasst.', 19, 0, dict(ohne=['gruber'], thema=[T_WASSER])),
         ]),
    dict(id='sr_20240115', titel='1. Stadtratssitzung – Januar 2024', absent=['tristl'],
         partial=[{'member': 'stanglmaier', 'from': '19:15'}, {'member': 'gruber', 'from': '19:20'},
                  {'member': 'kaestl', 'from': '19:20'}, {'member': 'beibl', 'to': '19:50'}],
         agenda=[('1', 'Mitteilungen des Ersten Bürgermeisters', 'formal'), ('2', 'Bürgerfragen', 'formal'),
                 ('3', 'Genehmigung der Niederschrift vom 04.12.2023'),
                 ('4', 'Gutachten über Schülerprognosen für die Grund- und Mittelschulen'),
                 ('5', 'Erweiterung der Theresia-Gerhardinger-Grundschule – Planung'),
                 ('6', 'Baugesuche und Anträge', 'formal'),
                 ('6.1', 'Vorbescheid Abbruch des Postgebäudes und Wohn- und Geschäftsgebäude mit Tiefgarage, Bahnhofstr. 12'),
                 ('6.2', 'Vorbescheid zwei Gemeinschaftsunterkünfte nach § 246 BauGB, Degernpoint G7 und G8'),
                 ('7', 'Anfragen', 'formal')],
         beschluesse=[
             ('3', 'Genehmigung der Niederschrift vom 04.12.2023', NIEDERSCHRIFT, 21, 0, dict(spaet=['stanglmaier', 'gruber', 'kaestl'])),
             ('4', 'Schülerprognose zur Kenntnis genommen', 'Die Einwohner- und Schulbedarfsprognose wird zur Kenntnis genommen.', 24, 0, dict(thema=['t6'])),
             ('5', 'Grundschule – Erweiterung auf dem Nachbargrundstück', 'Die Grundschule wird auf dem früheren Rockermaier-Grundstück erweitert, mit einer Brücke zum Bestand.', 23, 0, dict(spaet=['beibl'], thema=['t6'])),
             ('5', 'Grundschule – Vergabe der Planung', 'Die Verwaltung vergibt die Planungsleistungen an Stein und Partner Projektmanagement, München.', 23, 0, dict(spaet=['beibl'], thema=['t6'])),
             ('6.1', 'Postgebäude Bahnhofstr. 12 – Einvernehmen verweigert', 'Die nötige Befreiung vom Bebauungsplan kann mit Rücksicht auf die Nachbarn nicht erteilt werden.', 22, 1, dict(spaet=['beibl'])),
             ('6.2', 'Gemeinschaftsunterkünfte Degernpoint – Einvernehmen verweigert', 'Im Industriegebiet sind die Anforderungen an den Lärmschutz für Wohnnutzung nicht erfüllt.', 23, 0, dict(spaet=['beibl'], thema=['t18'])),
         ]),
]

AGENDA_PRESSE = {
    ('sr_20210510', '6'): ['unterfuehrung'],
    ('sr_20220117', '5.1'): ['volksfestplatz'],
    ('sr_20220207', '5.1'): ['aerztehaus-bahnhof'], ('sr_20220207', '5.2'): ['aerztehaus-bahnhof'],
    ('sr_20220221', '4'): ['kitagebuehren'],
    ('sr_20220314', '4'): ['sparkassenfusion'], ('sr_20220314', '6.1'): ['oberes-gereut'],
    ('sr_20220328', '6'): ['montessori'],
    ('sr_20220404', '7'): ['freibadgebuehren'],
    ('sr_20220502', '11'): ['pv-schuldach'],
    ('sr_20220509', '6'): ['schuelerzahlen'],
    ('sr_20220530', '4'): ['naturfriedhof'],
    ('sr_20220530', '5.1'): ['gruene-legen-nieder', 'gruene-verabschiedet'],
    ('sr_20220530', '5.2'): ['gruene-legen-nieder', 'gruene-verabschiedet'],
    ('sr_20220704', '4.1'): ['vereidigung'], ('sr_20220704', '4.2'): ['vereidigung'],
    ('sr_20221107', '4'): ['rasenmaeher'], ('sr_20221107', '7'): ['eisstadion'],
    ('sr_20230925', '4'): ['jungheinrich'], ('sr_20230925', '6.2'): ['bahnhof-sanierung'],
    ('sr_20231016', '4'): ['wasserwerk'],
    ('sr_20231204', '5'): ['wassergebuehren'],
}

NEUE_DOSSIERS = [
    {'id': T_BP66, 'title': 'Bebauungsplan Nr. 66 „Oberes Gereut Nordost“', 'tags': ['building'], 'image': None,
     'summary': 'Wohngebiet an der Fischerstraße im Südosten Moosburgs, zwischen Isar und Flugplatz, für rund 275 Menschen. Die Grünen wollten das Verfahren 2022 ruhen lassen, bis Schulen und Kinderbetreuung nachkommen; die Mehrheit hat weitergeplant. 2024 wechselte das Verfahren ins Regelverfahren.',
     'field': 'building', 'type': 'gebiet', 'status': 'laufend'},
    {'id': T_BP74, 'title': 'Bebauungsplan Nr. 74 „Feldkirchen“', 'tags': ['building', 'economy'], 'image': None,
     'summary': 'Sondergebiet für die Saatgutbetriebe in Feldkirchen, mit der 10. Änderung des Flächennutzungsplans. Der Stadtrat hat die Stellungnahmen aus zwei Beteiligungsrunden abgewogen und den Plan 2023 abgeschlossen.',
     'field': 'building', 'type': 'gebiet', 'status': 'abgeschlossen'},
    {'id': T_WASSER, 'title': 'Wasserversorgung', 'tags': ['infrastructure'], 'image': None,
     'summary': 'Das städtische Wasserwerk, seine Sanierung und die Gebühren, die sie bezahlen. 2022 wurde der Eigenbetrieb aufgelöst und das Wasserwerk wieder in die Verwaltung geholt; seit 2023 wird die Aufbereitungsanlage saniert, und die Gebühren steigen in zwei Stufen.',
     'field': 'infrastructure', 'type': 'einrichtung', 'status': 'laufend'},
    {'id': T_SPARKASSE, 'title': 'Sparkasse', 'tags': ['economy', 'budget'], 'image': None,
     'summary': 'Die Stadt- und Kreissparkasse Moosburg und ihr Zweckverband. 2022 fusionierte sie mit der Sparkasse Freising; der Stadtrat stimmte knapp zu und stritt über die Besetzung der Verbandsräte.',
     'field': 'economy', 'type': 'einrichtung', 'status': 'laufend'},
]

# Historie: (Dossier, Datum, Sitzung, TOP, Index des Beschlusses im TOP, Titel, Text)
HISTORIE = [
    (T_BP66, '2022-03-14', 'sr_20220314', '6.1', 0, 'Vertagung abgelehnt', 'Die Grünen wollen das Verfahren ruhen lassen, bis die Infrastruktur nachkommt; abgelehnt mit 9:14. Danach wird ein erster Teil der Stellungnahmen abgewogen, zwei Änderungsanträge für Gutachten scheitern ebenfalls mit 9:14.'),
    (T_BP66, '2022-07-11', 'sr_20220711', '7.9', 0, 'Billigung und Auslegung', 'Die restlichen Stellungnahmen werden einstimmig abgewogen, der Entwurf gebilligt und ausgelegt.'),
    (T_BP74, '2022-07-11', 'sr_20220711', '8.26', 0, 'Abwägung und Billigung', 'Gut zwanzig Stellungnahmen werden einstimmig abgewogen, Plan und FNP-Änderung gebilligt und ausgelegt.'),
    (T_WASSER, '2022-11-07', 'sr_20221107', '5', 0, 'Eigenbetrieb aufgelöst', 'Die Betriebssatzung des Wasserwerks wird aufgehoben; dazu eine Vereinbarung mit dem Wasserzweckverband Baumgartner Gruppe über künftige Neubaugebiete.'),
    (T_WASSER, '2023-10-16', 'sr_20231016', '4', 0, 'Sanierung der Aufbereitungsanlage', 'Ausführungsplanung und Ausschreibung beschlossen, die Netzersatzanlage wird vorab ausgeschrieben. Die Kosten liegen über eine halbe Million höher als geplant.'),
    (T_WASSER, '2023-12-04', 'sr_20231204', '5.1', 2, 'Neue Wassergebühren', 'Grundgebühr plus 50 %, Verbrauch 1,89 €/m³ ab 2024 und 2,15 €/m³ ab 2026. Alles einstimmig.'),
    (T_SPARKASSE, '2022-03-14', 'sr_20220314', '4', 0, 'Fusion mit Freising', 'Mit 14:9 stimmt der Stadtrat der Vereinigung mit der Sparkasse Freising zum 1. Juni 2022 zu.'),
    (T_SPARKASSE, '2022-04-04', 'sr_20220404', '4', 0, 'Verbandsräte', 'Die Grünen beanspruchen einen Sitz; mit 13:8 bleibt es bei Hadersdorfer und Kieninger.'),
    ('t2', '2022-02-07', 'sr_20220207', '5.1', 0, 'Ärztehaus im Bahnhof abgelehnt', 'Welters Antrag findet nur seine eigene Stimme (20:1); die CSU setzt den Anstrich der Fassade durch.'),
    ('t2', '2023-09-25', 'sr_20230925', '6.2', 0, 'Generalsanierung statt Neubau', 'Weil nur die Sanierung nennenswert gefördert wird, beschließt der Stadtrat mit 18:2 die Generalsanierung.'),
    ('t18', '2023-09-25', 'sr_20230925', '4', 0, 'B-Plan Nr. 80 aufgestellt', 'Einstimmig: Aufstellung für die Erweiterung von Jungheinrich, mit städtebaulichem Vertrag.'),
    ('t6', '2024-01-15', 'sr_20240115', '5', 0, 'Erweiterung auf dem Nachbargrundstück', 'Einstimmig: Die Grundschule wird auf dem früheren Rockermaier-Grundstück erweitert.'),
    ('t12', '2022-04-04', 'sr_20220404', '7', 2, 'Neue Badegebühren', 'Die Saisonkarten nach dem Antrag Stanglmaier gehen einstimmig durch, der Verwaltungsvorschlag scheitert.'),
    ('t31', '2022-02-21', 'sr_20220221', '4', 0, 'Kitagebühren steigen', 'Mit 13:7 setzt sich der Vorschlag des Bürgermeisters durch: 20 % in diesem, 8 % im nächsten Jahr, danach 3 % jährlich.'),
    ('t31', '2022-07-04', 'sr_20220704', '7.1', 2, 'Krippe Sonnensiedlung in Hybridbauweise', 'Die reine Holzbauweise (Antrag Stanglmaier) scheitert mit 7:12, gebaut wird hybrid.'),
]
BESTEHENDE = {
    T_BP66: ['sr_20241021_07', 'sr_20260325_04'],
    T_BP74: ['sr_20200706_01', 'sr_20230522_10'],
    T_WASSER: ['sr_20221010_04', 'sr_20230522_04', 'bpu_20231123_10', 'sr_20251110_03', 'sr_20251110_04'],
    T_SPARKASSE: ['sr_20200504_14', 'sr_20260511_18', 'sr_20260511_19'],
}
MEILENSTEINE = {
    T_SPARKASSE: [dict(date='2022-03-31', type='milestone', title='Vereinigungsvertrag unterzeichnet',
                       text='Die beiden Sparkassen, die Städte und der Landkreis unterzeichnen den Vertrag; die Fusion gilt ab 1. Juni 2022.',
                       press=[pid('sparkasse-vertrag')])],
}


def aktiv(m, datum):
    return any((s.get('from') or '0') <= datum <= (s.get('to') or '9999') for s in m['mandates'])


def baue(sitzung, members, vid_start=1):
    sid = sitzung['id']
    datum = f'{sid[3:7]}-{sid[7:9]}-{sid[9:11]}'
    rat = [m['id'] for m in members if aktiv(m, datum)]
    assert len(rat) == 25, (sid, len(rat))
    absent = sitzung['absent']
    assert set(absent) <= set(rat), (sid, set(absent) - set(rat))
    da_basis = [m for m in rat if m not in absent]

    votes, je_top = [], {}
    for nr, b in enumerate(sitzung['beschluesse'], vid_start):
        top, titel, text, ja, nein = b[:5]
        opt = b[5] if len(b) > 5 else {}
        vid = f'{sid}_{nr:02d}'
        je_top.setdefault(top, []).append(vid)
        ohne = list(opt.get('ohne', []))
        spaet = list(opt.get('spaet', [])) + [m for m in sitzung.get('ohne_alle', []) if m not in opt.get('spaet', [])]
        excluded = ([{'member': m, 'reason': 'kurz_abwesend'} for m in opt.get('ohne', [])]
                    + [{'member': m, 'reason': 'beteiligung'} for m in opt.get('beteiligt', [])]
                    + [{'member': m, 'reason': 'nicht_stimmberechtigt'} for m in opt.get('nsb', [])])
        weg = set(ohne) | set(spaet) | set(opt.get('beteiligt', [])) | set(opt.get('nsb', []))
        stimmen = [m for m in da_basis if m not in weg]
        abwesend = [m for m in rat if m not in stimmen]

        v = {'id': vid, 'sessionId': sid}
        if opt.get('thema'):
            v['topicIds'] = opt['thema']
        v['title'] = titel
        v['text'] = text
        if ja < nein:
            v['result'] = 'rejected'
        excl_out = excluded

        bekannt = {}
        bekannt.update(opt.get('protokoll', {}))
        bekannt.update(opt.get('hart', {}))
        bekannt.update({m: 'yes' for m in opt.get('antrag', [])})
        bekannt.update(opt.get('verfahren', {}))

        if 'ja' in opt:
            assert len(opt['ja']) == ja and len(opt['nein']) == nein, vid
            assert set(opt['ja'] + opt['nein']) == set(stimmen), (vid, set(stimmen) ^ set(opt['ja'] + opt['nein']))
            v['type'] = 'named'
            v['results'] = {'yes': opt['ja'], 'no': opt['nein'], 'absent': abwesend}
            v['source'] = {'tier': 'protocol-explicit'}
        elif opt.get('alle'):
            v['type'] = 'named'
            v['results'] = {'yes': stimmen, 'no': [], 'absent': abwesend}
            v['source'] = {'tier': 'protocol-implicit'}
        elif ja + nein == len(stimmen) and (ja == 0 or nein == 0):
            v['type'] = 'named'
            v['results'] = {'yes': stimmen if ja else [], 'no': [] if ja else stimmen, 'absent': abwesend}
            v['source'] = {'tier': 'protocol-implicit'}
        elif ja + nein == len(stimmen) and bekannt and (
                sum(1 for x in bekannt.values() if x == 'yes') == ja
                or sum(1 for x in bekannt.values() if x == 'no') == nein):
            # Eine Seite ist voll: die andere ist Rechnung
            seite = 'yes' if sum(1 for x in bekannt.values() if x == 'yes') == ja else 'no'
            andere = [m for m in stimmen if m not in bekannt]
            v['type'] = 'named'
            ja_l = [m for m in stimmen if bekannt.get(m) == 'yes'] + (andere if seite == 'no' else [])
            nein_l = [m for m in stimmen if bekannt.get(m) == 'no'] + (andere if seite == 'yes' else [])
            assert len(ja_l) == ja and len(nein_l) == nein, vid
            v['results'] = {'yes': ja_l, 'no': nein_l, 'absent': abwesend}
            v['source'] = {'tier': 'press', 'pressId': opt['presse']} if opt.get('presse') else {'tier': 'protocol-implicit'}
            herkunft = {}
            for m in opt.get('protokoll', {}):
                herkunft[m] = {'tiers': ['protocol-explicit']}
            for m in list(opt.get('antrag', [])) + list(opt.get('verfahren', {})):
                herkunft[m] = {'tiers': ['protocol-implicit'], 'note': ANTRAG}
            if herkunft:
                v['voters'] = herkunft
        else:
            v['type'] = 'anonymous'
            v['results'] = {'yes': ja, 'no': nein, 'absent': 25 - ja - nein}
            if spaet:
                v['results']['absent_ids'] = sorted(spaet)
            voters = {}
            for m, x in opt.get('protokoll', {}).items():
                voters[m] = {'vote': x, 'tiers': ['protocol-explicit']}
            for m in opt.get('antrag', []):
                voters[m] = {'vote': 'yes', 'tiers': ['protocol-implicit'], 'note': ANTRAG}
            for m, x in opt.get('verfahren', {}).items():
                voters[m] = {'vote': x, 'tiers': ['protocol-implicit'], 'note': ANTRAG}
            for m, x in opt.get('hart', {}).items():
                voters[m] = {'vote': x, 'tiers': ['press']}
            for m, x in opt.get('weich', {}).items():
                assert m in stimmen, (vid, m)
                voters.setdefault(m, {'vote': x, 'evidence': 'soft'})
            assert sum(1 for x in voters.values() if x.get('vote') == 'yes') <= ja, vid
            assert sum(1 for x in voters.values() if x.get('vote') == 'no') <= nein, vid
            if opt.get('presse') and (opt.get('hart') or opt.get('weich')):
                v['source'] = {'tier': 'press', 'pressId': opt['presse']}
            elif ja == 0 or nein == 0:
                v['source'] = {'tier': 'protocol-implicit'}
            else:
                v['source'] = {'tier': 'result-only'}
            if voters:
                v['voters'] = voters
        if excl_out:
            v['excluded'] = excl_out
        if opt.get('note'):
            v['note'] = opt['note']
        votes.append(v)

    agenda = []
    for eintrag in sitzung['agenda']:
        nummer, titel = eintrag[0], eintrag[1]
        art = eintrag[2] if len(eintrag) > 2 else None
        notiz = eintrag[3] if len(eintrag) > 3 else None
        a = {'number': nummer, 'title': titel}
        if art:
            a['type'] = art
        if nummer in je_top:
            a['voteIds'] = je_top[nummer]
            themen = {t for vid in je_top[nummer] for v in votes if v['id'] == vid for t in v.get('topicIds', [])}
            if len(themen) == 1:
                a['topicId'] = themen.pop()
        if (sid, nummer) in AGENDA_PRESSE:
            a['press'] = [pid(k) for k in AGENDA_PRESSE[(sid, nummer)]]
        if notiz:
            a['note'] = notiz
        agenda.append(a)
    fehlt = set(je_top) - {a['number'] for a in agenda}
    assert not fehlt, (sid, fehlt)
    return votes, agenda


def main():
    members = load('members.json')
    sessions = load('sessions.json')
    votes = load('votes.json')
    topics = load('topics.json')
    press = load('press.json')

    vorhanden = {p['id'] for p in press}
    for k, (media, datum, titel, url) in P.items():
        if pid(k) not in vorhanden:
            press.append({'id': pid(k), 'media': media, 'date': datum, 'title': titel, 'url': url})

    by_id = {s['id']: s for s in sessions}
    neue = {}
    for sitzung in SITZUNGEN:
        sid = sitzung['id']
        assert not any(v['sessionId'] == sid for v in votes), sid
        vs, agenda = baue(sitzung, members)
        s = by_id[sid]
        s['niederschrift'] = 'vollständig'
        if sitzung.get('start'):
            s['start'] = sitzung['start']
        if sitzung.get('location'):
            s['location'] = sitzung['location']
        s['title'] = sitzung['titel']
        s['absent'] = sitzung['absent']
        if sitzung.get('partial'):
            s['partial'] = sitzung['partial']
        if sitzung.get('notes'):
            s['notes'] = sitzung['notes']
        s['agenda'] = agenda
        reihe = ['id', 'date', 'type', 'niederschrift', 'start', 'end', 'location', 'title', 'quellen',
                 'absent', 'partial', 'substitutes', 'notes', 'press', 'agenda']
        geordnet = {k: s[k] for k in reihe if k in s}
        s.clear()
        s.update(geordnet)
        neue[sid] = vs

    # Die Stimmen stehen in votes.json in der Reihenfolge der Sitzungen
    datum_von = {s['id']: s['date'] for s in sessions}
    for sid, vs in neue.items():
        i = next((n for n, v in enumerate(votes) if datum_von.get(v['sessionId'], '') > datum_von[sid]), len(votes))
        votes[i:i] = vs

    # Beifang: Hallenmieten 21.11.2022, Fincke als einzige Gegenstimme
    v = next(x for x in votes if x['id'] == 'sr_20221121_06')
    s = by_id['sr_20221121']
    named_vorher = next(x for x in votes if x['id'] == 'sr_20221121_01')
    da = named_vorher['results']['yes']
    assert len(da) == 19 and 'fincke' in da
    v['type'] = 'named'
    v['results'] = {'yes': [m for m in da if m != 'fincke'], 'no': ['fincke'], 'absent': named_vorher['results']['absent']}
    v['source'] = {'tier': 'press', 'pressId': pid('hallenmieten')}
    v['voters'] = {'fincke': {'tiers': ['press']}}
    for a in s['agenda']:
        if 'sr_20221121_06' in a.get('voteIds', []):
            a['press'] = sorted(set(a.get('press', [])) | {pid('hallenmieten')})
    # Beifang: Parkleitsystem 26.04.2021, nur verlinkt
    for a in by_id['sr_20210426']['agenda']:
        if 'sr_20210426_03' in a.get('voteIds', []):
            a['press'] = sorted(set(a.get('press', [])) | {pid('parkleitsystem')})

    # Dossiers
    by_topic = {t['id']: t for t in topics}
    for d in NEUE_DOSSIERS:
        assert d['id'] not in by_topic
        t = dict(d)
        t['history'] = []
        topics.append(t)
        by_topic[t['id']] = t
    vote_by = {x['id']: x for x in votes}
    for tid, vids in BESTEHENDE.items():
        for vid in vids:
            x = vote_by[vid]
            x['topicIds'] = sorted(set(x.get('topicIds', [])) | {tid})
            # topicIds steht vor title
            reihe = ['id', 'sessionId', 'topicIds']
            geordnet = {k: x[k] for k in reihe if k in x}
            geordnet.update({k: w for k, w in x.items() if k not in reihe})
            x.clear()
            x.update(geordnet)
            s = by_id[x['sessionId']]
            by_topic[tid]['history'].append({'date': s['date'], 'type': 'vote', 'title': x['title'],
                                             'text': x.get('text', ''), 'sessionId': s['id'], 'voteId': vid})
    for tid, datum, sid, top, idx, titel, text in HISTORIE:
        vid = next(a for a in by_id[sid]['agenda'] if a['number'] == top)['voteIds'][idx]
        h = {'date': datum, 'type': 'vote', 'title': titel, 'text': text, 'sessionId': sid, 'voteId': vid}
        a = next(a for a in by_id[sid]['agenda'] if a['number'] == top)
        if a.get('press'):
            h['press'] = a['press']
        by_topic[tid]['history'].append(h)
    for tid, eintraege in MEILENSTEINE.items():
        by_topic[tid]['history'].extend(eintraege)
    for tid in {h[0] for h in HISTORIE} | set(BESTEHENDE) | set(MEILENSTEINE):
        by_topic[tid]['history'].sort(key=lambda h: h['date'])

    save('sessions.json', sessions)
    save('votes.json', votes)
    save('topics.json', topics)
    save('press.json', press)

    n = sum(len(x) for x in neue.values())
    named = sum(1 for x in neue.values() for v in x if v['type'] == 'named')
    print(f'{len(neue)} Sitzungen, {n} Beschlüsse, davon {named} named, {n - named} anonym')


if __name__ == '__main__':
    main()
