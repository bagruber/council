"""Arbeitet 14 BPU-Niederschriften ein (21.09.2020 bis 13.04.2026).

Bis auf den 13.04.2026 standen alle Sitzungen schon als Beschlussauszug im
Register. Die Niederschrift bringt die Anwesenheit und die Einzelbeschluesse,
die der Auszug nur als "mehrere Einzelbeschluesse" fuehrte. Die Votes dieser
Sitzungen werden deshalb neu aufgebaut, nicht ergaenzt.

Nebenbei: den BPU-Sitz, den bodies.json Welter zuschrieb, hielt bis zur
Neubesetzung im Stadtrat am 06.03.2023 (nach der gerichtlichen Entscheidung)
Stefan John, vertreten von Kaestl. Welter sitzt erst ab dann, ohne Vertretung.
Die bereits eingearbeiteten Sitzungen 17.11.2022 und 23.01.2023 werden
entsprechend berichtigt.

Einmal laufen lassen:
    python scripts/bpu_niederschriften_2020_2026.py
"""
import json, os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def load(n):
    return json.load(open(os.path.join(DATA, n), encoding='utf-8'))


def save(n, obj):
    with open(os.path.join(DATA, n), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


# Reihenfolge der zwoelf Sitze 2020-2026, wie bodies.json sie fuehrt.
def sitze(datum):
    return ['dollinger', 'linz_karin', 'tristl',
            'beubl' if datum < '2025-03-24' else 'marcus',
            'john' if datum < '2023-03-06' else 'welter',
            'wittmann' if datum < '2021-10-25' else ('gruebl' if datum < '2024-10-22' else 'hobmaier'),
            'kieninger', 'reif', 'beibl',
            'altenbeck' if datum < '2022-06-01' else 'linz_kilian',
            'hadersdorfer', 'stanglmaier']


# ── Die Niederschriften ─────────────────────────────────────────────────────
#
# Je Beschluss: (TOP, Titel, Text, Ja, Nein, Optionen). Optionen:
#   ohne   = wer an diesem Beschluss nicht mitstimmte, obwohl der Sitz besetzt war
#   ja/nein = Namen aus der Niederschrift (namentliche Abstimmung)
#   weich  = {id: 'yes'|'no'} aus einer Wortmeldung im Pressebericht
#   presse = pressId fuer die weichen Belege
#   thema  = topicIds

MZ_LAENDE = 'mz_2021-05-03_verkehrsberuhigung-laende'
MK_HOTEL_VOR = 'merkur_2020-11-05_apartmenthotel-vorbericht'
MK_HOTEL_AB = 'merkur_2020-11-12_apartmenthotel-abgelehnt'
MK_HOTEL_JA = 'merkur_2021-03-20_apartmenthotel-zustimmung'
MK_NACHVERD = 'merkur_2021-06-18_nachverdichtung-kritik'
MK_AERZTE = 'merkur_2022-05-24_aerztehaus-abgelehnt'
MZ_ZWEI_MFH = 'mz_2022-05-24_zwei-mfh-abgelehnt'
MK_HUBERHAUS = 'merkur_2022-05-25_huber-haus-abriss'
MZ_EINBAHN = 'mz_2025-07-29_einbahnregelung-gestoppt'
MZ_EINBAHN_STREIT = 'mz_2025-09-09_einbahnstrasse-streit'
MZ_KLAGEWEG = 'mz_2026-04-14_klageweg-sternstrasse'

PRESSE = [
    (MK_HOTEL_VOR, 'merkur', '2020-11-05', 'Große Pläne für die Neustadt: Bekommt Moosburg ein neues Hotel mit Läden?',
     'https://www.merkur.de/lokales/freising/moosburg-ort29088/grosse-plaene-fuer-die-neustadt-bekommt-moosburg-ein-neues-hotel-mit-laeden-90091542.html'),
    (MK_HOTEL_AB, 'merkur', '2020-11-12', 'Bauausschuss lehnt Apartmenthotel ab – Büro- und Ladenflächen dürfen an Industriestraße entstehen',
     'https://www.merkur.de/lokales/freising/moosburg-ort29088/moosburg-bauausschuss-lehnt-apartmenthotel-ab-buero-und-ladenflaechen-duerfen-an-industriestrasse-entstehen-90098477.html'),
    (MK_HOTEL_JA, 'merkur', '2021-03-20', 'Umstrittenes Projekt: Knappe Zustimmung für neues Apartmenthotel im Moosburger Industriegebiet',
     'https://www.merkur.de/lokales/freising/moosburg-ort29088/umstrittenes-projekt-knappe-zustimmung-fuer-neues-apartmenthotel-im-moosburger-industriegebiet-90254375.html'),
    (MZ_LAENDE, 'mz', '2021-05-03', 'Moosburger Stadträte für Verkehrsberuhigung',
     'https://www.idowa.de/regionen/moosburg/moosburger-stadtraete-fuer-verkehrsberuhigung-1288245.html'),
    (MK_NACHVERD, 'merkur', '2021-06-18', '„Städtebaulicher Fehler“: Intensive Nachverdichtung gerät in die Kritik',
     'https://www.merkur.de/lokales/freising/moosburg-ort29088/staedtebaulicher-fehler-intensive-nachverdichtung-geraet-in-die-kritik-90808020.html'),
    (MK_AERZTE, 'merkur', '2022-05-24', 'Bauausschuss: Ärztehaus abgelehnt – Bauausschuss befürchtet Verkehrschaos',
     'https://www.merkur.de/lokales/freising/moosburg-ort29088/moosburg-bauausschuss-aerztehaus-abgelehnt-bauausschuss-befuerchtet-verkehrschaos-in-moosburg-91569261.html'),
    (MZ_ZWEI_MFH, 'mz', '2022-05-24', 'Zwei Mehrfamilienhäuser in Moosburg abgelehnt',
     'https://www.idowa.de/regionen/moosburg/zwei-mehrfamilienhaeuser-in-moosburg-abgelehnt-1389687.html'),
    (MK_HUBERHAUS, 'merkur', '2022-05-25', 'Mehr Platz fürs Rathaus: Huber-Haus darf abgerissen werden',
     'https://www.merkur.de/lokales/freising/moosburg-ort29088/moosburg-bauausschuss-hudlerhaus-mehr-platz-fuers-rathaus-hudlerhaus-darf-abgerissen-und-erweiterungsbau-geplant-werden-91569298.html'),
    (MZ_EINBAHN, 'mz', '2025-07-29', 'Frische Einbahnregelung in Moosburg wieder gestoppt',
     'https://www.idowa.de/regionen/moosburg/frische-einbahnregelung-in-moosburg-wieder-gestoppt-art-348852'),
    (MZ_EINBAHN_STREIT, 'mz', '2025-09-09', 'Streit um eine Einbahnstraße an einer Schule in Moosburg',
     'https://www.idowa.de/regionen/moosburg/streit-um-eine-einbahnstrasse-an-einer-schule-in-moosburg-art-355111'),
    (MZ_KLAGEWEG, 'mz', '2026-04-14', 'Moosburger Bauausschuss spricht sich erneut für Klageweg aus',
     'https://www.idowa.de/regionen/moosburg/moosburger-bauausschuss-spricht-sich-erneut-fuer-klageweg-aus-art-389873'),
]

NIEDERSCHRIFT = 'Der Bauausschuss nimmt die Niederschrift zur Kenntnis und genehmigt sie.'

SITZUNGEN = [
    dict(id='bpu_20200921', titel='3. Sitzung Bau-, Planungs- und Umweltausschuss – September 2020',
         absent=['hadersdorfer', 'wittmann', 'beubl', 'beibl'],
         vertretung={'beubl': 'pschorr', 'beibl': 'von_pressentin'},
         beschluesse=[
             ('3.1', 'Vorbescheid Anbau EFH Gabelsbergerstr. 16', 'Einvernehmen zum Vorbescheid erteilt.', 10, 0),
             ('3.2', 'Zwei MFH mit je 5 WE und ein MFH mit 3 WE, Schillerstr. 10 / Neustadtstr. 17',
              'Einvernehmen erteilt; die Besucherstellplätze müssen im Gemeinschaftseigentum bleiben.', 7, 3),
             ('3.3', 'Vorbescheid zwei MFH mit je 3 WE, Uppenbornstr. 12 und 14', 'Einvernehmen zur Bauvoranfrage erteilt.', 10, 0),
             ('3.4', 'Tektur Stellplatznachweis Leinbergerstr. 26–28', 'Einvernehmen zur Tektur von Stellplatznachweis und -anordnung erteilt.', 6, 4),
             ('3.5', 'Vorbescheid Stallgebäude und Altenteilhaus Pillhofen 5', 'Einvernehmen zum Vorbescheid erteilt.', 10, 0),
             ('3.6', 'EFH mit Doppelgarage Isarstr. 33', 'Einvernehmen erteilt; das Grundstück ist hochwassergefährdet.', 10, 0),
             ('3.7', 'Vorbescheid Umbau Oberreit 23 1/2', 'Einvernehmen zur Bauvoranfrage erteilt.', 10, 0),
             ('3.8', 'Zusätzliche Grundstückszufahrt Oberreit 23 1/2',
              'Antrag auf eine zusätzliche Zufahrt samt Grunddienstbarkeiten abgelehnt.', 1, 9),
             ('3.9', 'MFH Neustadtstr. 40 – Ausbau auf 5 WE', 'Einvernehmen erteilt.', 10, 0),
         ]),
    dict(id='bpu_20201109', titel='4. Sitzung Bau-, Planungs- und Umweltausschuss – November 2020',
         absent=[],
         beschluesse=[
             ('3.1', 'Fahrradstraße Viehmarktstraße (Antrag Grüne)',
              'Die Viehmarktstraße in voller Länge und das Teilstück der Landshuter Straße von der Blütenstraße bis zur Kulturgrabenbrücke werden als Fahrradstraße ausgewiesen.',
              10, 2, dict(thema=['t4'])),
             ('3.2', 'Fahrradzone Graf-Konrad-Straße und Stadtgraben (Antrag Grüne)',
              'Die Tempo-30-Zone um Rhenobot-, Statzenbach-, Graf-Konrad-, Gutenberg-, Weihmühl-, Gabelsberger-, Geibitz- und Jahnstraße sowie einen Teil des Stadtgrabens wird für zwei Jahre als Fahrradzone mit „Anlieger frei“ ausgeschildert.',
              9, 3, dict(thema=['t4'])),
             ('4.1', 'Vorbescheid Betriebsleiterwohnhaus Stadtbadstr. 25',
              'Einvernehmen erteilt; vor der Baugenehmigung sind Sondervereinbarungen zu Wasser und Abwasser zu treffen.', 12, 0),
             ('4.2', 'LED-Werbeanlage Fischerstr. 1 – verweigert',
              'Einvernehmen verweigert: Wechselwerbung, Ortsbild, Verkehrssicherheit.', 12, 0),
             ('4.3', 'Großtagespflege Rhenobotstr. 9',
              'Einvernehmen zur Nutzungsänderung erteilt; zusätzliche Stellplätze werden nicht verlangt.', 9, 3, dict(thema=['t31'])),
             ('4.4', 'Vorbescheid EFH Niederambach 8 a', 'Einvernehmen zum Vorbescheid erteilt.', 8, 4),
             ('4.5', 'Auf dem Gries 7 – Einvernehmen erteilen', 'Antrag, das Einvernehmen zu erteilen, einstimmig abgelehnt.', 0, 12),
             ('4.5', 'Auf dem Gries 7 – verweigert',
              'Einvernehmen verweigert: Brandschutz und Abstandsflächen, Einwendungen der Nachbarn. Das Landratsamt soll Denkmalpflege und Wohnflächen prüfen.', 12, 0),
             ('4.6', 'Vorbescheid Lärmschutzwand Mainburger Str. 2 und 4', 'Einvernehmen erteilt.', 11, 0, dict(ohne=['altenbeck'])),
             ('4.7', 'Vorbescheid Ersatzhaus Tiefenbachstr. 120', 'Einvernehmen erteilt; das Landratsamt soll die Größe des Baukörpers prüfen.', 11, 1),
             ('4.8', 'Vorbescheid MFH 2 WE Venusstr. 10 – Einvernehmen erteilen', 'Antrag, das Einvernehmen zu erteilen, abgelehnt.', 4, 8),
             ('4.9', 'MFH 9 WE mit Tiefgarage Sudetenlandstr. 6', 'Einvernehmen erteilt.', 10, 2),
             ('4.10', 'Neue Industriestr. 8 – Neubau in den beantragten Abmessungen', 'Einvernehmen für den Baukörper erteilt.', 12, 0),
             ('4.10', 'Neue Industriestr. 8 – Läden im Erdgeschoss', 'Einvernehmen für Läden mit weniger als 600 m² Verkaufsfläche erteilt.', 12, 0),
             ('4.10', 'Neue Industriestr. 8 – Apartmenthotel erteilen', 'Antrag, das Einvernehmen für die Nutzung als Apartmenthotel zu erteilen, abgelehnt.', 5, 7,
              dict(weich={'dollinger': 'no', 'stanglmaier': 'no'}, presse=MK_HOTEL_AB)),
             ('4.10', 'Neue Industriestr. 8 – Apartmenthotel verweigert',
              'Einvernehmen für die Nutzung als Apartmenthotel verweigert; sie entspricht nicht dem Bebauungsplan.', 11, 1),
             ('4.10', 'Neue Industriestr. 8 – Betreutes Wohnen verweigert',
              'Einvernehmen für betreutes Wohnen, Alten- und Pflegewohnheim verweigert; im Industriegebiet unzulässig.', 12, 0),
         ]),
    dict(id='bpu_20201217', titel='5. Sitzung Bau-, Planungs- und Umweltausschuss – Dezember 2020',
         absent=[],
         partial=[{'member': 'wittmann', 'from': '19:45',
                   'note': 'Alle öffentlichen Beschlüsse mit 11 Stimmen, also vor seinem Eintreffen.'}],
         ohne_alle=['wittmann'],
         beschluesse=[
             ('3', 'Genehmigung der Niederschrift vom 09.11.2020', NIEDERSCHRIFT, 11, 0),
             ('4.1', 'Vorbescheid Lagerhalle mit Hackschnitzellager Kirchamper 8', 'Einvernehmen zum Vorbescheid erteilt.', 11, 0),
             ('4.2', 'MFH Banatstr. 25', 'Einvernehmen erteilt, dazu die Befreiungen vom Bebauungsplan.', 11, 0),
             ('4.3', 'Vorbescheid Abbruch und Neubau Am Kanal 7, Aich', 'Einvernehmen zum Vorbescheid erteilt.', 11, 0),
             ('4.4', 'Herrnstr. 2 – verweigert',
              'Einvernehmen verweigert, die Stellplätze sind nicht nachgewiesen. Bestandsschutz für eine Gewerbeeinheit und zwei Wohnungen wird anerkannt.', 11, 0),
             ('4.5', 'Apartmenthotel Neue Industriestr. 8 – Tektur verweigert',
              'Einvernehmen für die Apartmenthotel-Nutzung nach dem Nutzungskonzept vom 27.11.2020 verweigert; sie entspricht nicht dem Bebauungsplan.', 8, 3),
             ('4.6', 'Vorbescheid Landshuter Str. 195 – Variante 1 verweigert', 'Einvernehmen für zwei Doppelhäuser (E+1+D) verweigert.', 11, 0),
             ('4.6', 'Vorbescheid Landshuter Str. 195 – Variante 2 verweigert', 'Einvernehmen für zwei Doppelhäuser (E+D) verweigert.', 11, 0),
             ('4.7', 'Venusstr. 10 – Einvernehmen nach Anhörung erteilt',
              'Nach der Anhörung zur Ersetzung des Einvernehmens durch das Landratsamt erteilt der Ausschuss das im November verweigerte Einvernehmen.', 6, 5),
             ('4.7', 'Bebauungsplan zwischen Bahn, Westerbergstraße und Georg-Schweiger-Straße (Antrag Grüne)',
              'Auf Antrag der Grünen vom 14.12.2020 empfiehlt der Ausschuss dem Stadtrat, für dieses Gebiet einen Bebauungsplan aufzustellen.', 7, 4),
         ]),
    dict(id='bpu_20210201', titel='1. Sitzung Bau-, Planungs- und Umweltausschuss – Februar 2021',
         absent=[],
         beschluesse=[
             ('3', 'Genehmigung der Niederschrift vom 17.12.2020', NIEDERSCHRIFT, 12, 0),
             ('4.1', 'Vorbescheid Landshuter Str. 28/28 a – Einvernehmen erteilen', 'Antrag, das Einvernehmen zu erteilen, abgelehnt.', 4, 8),
             ('4.1', 'Vorbescheid Landshuter Str. 28/28 a – verweigert',
              'Einvernehmen verweigert: Maß der baulichen Nutzung, Gebäudetiefe, Dachneigung.', 8, 4),
             ('4.1', 'Bebauungsplan Landshuter Straße / Gärtnerstraße (Antrag Beubl)',
              'Auf Antrag von StR Beubl empfiehlt der Ausschuss dem Stadtrat einen Bebauungsplan im beschleunigten Verfahren für die Landshuter Str. 28/28 a und die umliegenden Grundstücke bis zur Gärtnerstraße.', 9, 3),
             ('4.2', 'Vorbescheid Dreispänner und Doppelhaus Unterreiterweg 4', 'Einvernehmen zum Vorbescheid erteilt.', 12, 0),
             ('4.3', 'Vorbescheid Sudetenlandstr. 40 – Baukörperlänge verweigert', 'Einvernehmen für einen rund 50 m langen Baukörper verweigert.', 12, 0),
             ('4.3', 'Vorbescheid Sudetenlandstr. 40 – Giebelbreite erteilt', 'Einvernehmen für eine Giebelbreite von rund 12 m erteilt, sofern die Abstandsflächen nachgewiesen werden.', 12, 0),
             ('4.3', 'Vorbescheid Sudetenlandstr. 40 – GRZ verweigert', 'Einvernehmen für eine GRZ I von 0,45 verweigert; sie liegt über der Obergrenze nach § 17 BauNVO.', 12, 0),
             ('4.3', 'Vorbescheid Sudetenlandstr. 40 – Wandhöhe verweigert', 'Einvernehmen für eine Wandhöhe von rund 9 m verweigert.', 12, 0),
             ('4.3', 'Vorbescheid Sudetenlandstr. 40 – Firsthöhe verweigert', 'Einvernehmen für eine Firsthöhe von rund 11 m verweigert.', 12, 0),
             ('4.3', 'Vorbescheid Sudetenlandstr. 40 – Abstandsflächen', 'Keine Zustimmung zur Abweichung von der Abstandsflächensatzung.', 12, 0),
             ('4.4', 'Vorbescheid Doppelhaus Merkurstr. 7', 'Einvernehmen zum Vorbescheid erteilt.', 7, 5),
             ('4.5', 'MFH 4 WE Thonstetten 5 a – Einvernehmen erteilen', 'Antrag, das Einvernehmen zu erteilen, abgelehnt.', 3, 9),
             ('4.5', 'MFH 4 WE Thonstetten 5 a – verweigert',
              'Einvernehmen verweigert: Stellplätze im rückwärtigen Bereich, Rücksichtnahmegebot, Versiegelung, Verkehr.', 10, 2),
             ('4.6', 'Vorbescheid Thonstetten – Verlängerung gewähren', 'Antrag, den Vorbescheid um zwei Jahre zu verlängern, abgelehnt.', 2, 10),
             ('4.6', 'Vorbescheid Thonstetten – Verlängerung verweigert',
              'Einvernehmen zur Verlängerung verweigert: die Erschließung ist nicht gesichert, ein Wendehammer fehlt.', 10, 2),
         ]),
    dict(id='bpu_20210318', titel='2. Sitzung Bau-, Planungs- und Umweltausschuss – März 2021',
         absent=['john', 'reif'], vertretung={'reif': 'grundner'},
         notes=['John und sein Stellvertreter Kästl waren entschuldigt.'],
         beschluesse=[
             ('3', 'Genehmigung der Niederschrift vom 01.02.2021', NIEDERSCHRIFT, 11, 0),
             ('4.1', 'Widmung Verlängerung Egilbertstraße', 'Die Verlängerung der Egilbertstraße Richtung Friedhof wird als Ortsstraße gewidmet.', 11, 0),
             ('4.2', 'Widmung Erschließungsstraße Jungheinrich, Degernpoint', 'Die Erschließungsstraße zum Mitarbeiterparkplatz wird gewidmet.', 11, 0),
             ('4.3', 'Widmung Buchenlandstraße', 'Die Buchenlandstraße zwischen Erzgebirgstraße und Neuer Industriestraße wird gewidmet.', 11, 0),
             ('4.4', 'Widmung Park-and-Ride-Anlage am Bahnhof',
              'Zustimmung zur Freistellung von Bahnbetriebszwecken; die Verwaltung widmet die Grundstücke der P+R-Anlage.', 11, 0),
             ('4.5', 'Widmung Stichstraße an der Waldstraße', 'Die Stichstraße an der Abzweigung Waldstraße wird als Teil der Waldstraße gewidmet.', 11, 0),
             ('4.6', 'Umbenennung Naustraße', 'Die Naustraße wird zur Verlängerung der Waldstraße umbenannt.', 11, 0),
             ('5.1', 'Ersatzteillager und Garage Fürnsbach 2', 'Einvernehmen erteilt.', 11, 0),
             ('5.2', 'Maschinen- und Bergehalle St.-Georg-Str. 60', 'Einvernehmen erteilt.', 11, 0),
             ('5.3', 'Apartmenthotel Neue Industriestr. 8 – verweigern',
              'Nach der Anhörung zur Ersetzung des Einvernehmens: Antrag, das Einvernehmen wegen der Lage im Industriegebiet weiter zu verweigern, abgelehnt.', 5, 6,
              dict(weich={'dollinger': 'yes', 'altenbeck': 'yes', 'beubl': 'no', 'linz_karin': 'no', 'kieninger': 'no'}, presse=MK_HOTEL_JA)),
             ('5.3', 'Apartmenthotel Neue Industriestr. 8 – Einvernehmen erteilt',
              'Der Ausschuss erteilt das Einvernehmen für das Apartmenthotel, nachdem das Landratsamt das Vorhaben für zulässig gehalten hatte.', 6, 5,
              dict(weich={'beubl': 'yes', 'linz_karin': 'yes', 'kieninger': 'yes', 'dollinger': 'no', 'altenbeck': 'no'}, presse=MK_HOTEL_JA)),
             ('5.4', 'Vorbescheid Bürogebäude Degernpoint G 7', 'Einvernehmen zum Vorbescheid erteilt.', 11, 0),
             ('5.4', 'Vorbescheid Bürogebäude Degernpoint G 7 – Befreiung Wandhöhe', 'Befreiung von der Wandhöhe für einen Teil des Dachgeschosses erteilt.', 9, 2),
             ('5.4', 'Vorbescheid Bürogebäude Degernpoint G 7 – Flachdach', 'Flachdach ausnahmsweise zugelassen.', 11, 0),
             ('5.5', 'Vorbescheid Wohnhaus Breslauer Str. 1', 'Einvernehmen erteilt, dazu die Befreiungen.', 11, 0),
             ('5.6', 'EFH mit Doppelgarage Habichtweg 18', 'Einvernehmen erteilt, dazu die Befreiungen.', 11, 0),
         ]),
    dict(id='bpu_20210429', titel='3. Sitzung Bau-, Planungs- und Umweltausschuss – April 2021',
         absent=['john', 'reif'], vertretung={'reif': 'grundner'},
         partial=[{'member': 'wittmann', 'from': '19:10'}],
         notes=['John und sein Stellvertreter Kästl waren entschuldigt.'],
         beschluesse=[
             ('3', 'Genehmigung der Niederschrift vom 18.03.2021', NIEDERSCHRIFT, 10, 0, dict(ohne=['wittmann'])),
             ('4', 'Verkehrsberuhigung in der Lände',
              'Eine Sackgasse an der Einmündung Nelkenstraße wird abgelehnt. Die Verwaltung prüft einen verkehrsberuhigten Bereich, eine Fahrradstraße oder eine Fahrradzone zusammen mit den Blumenstraßen und misst im Sommer die Geschwindigkeit.',
              8, 3, dict(thema=['t4'])),
             ('5', 'Überschwemmungsgebiet Isar – keine Einwendungen', 'Gegen die Festsetzung des Überschwemmungsgebiets werden keine Einwendungen erhoben.', 11, 0),
             ('6.1', 'MFH 7 WE Mainburger Str. 23 – verweigert', 'Einvernehmen verweigert: Bebauungsplan und Belange der Nachbarn.', 11, 0),
             ('6.2', 'Sichtschutzzaun Feuerdornstr. 3 – Einvernehmen erteilen',
              'Antrag, Einvernehmen und Befreiung zu erteilen, abgelehnt; das Vorhaben entspricht nicht dem Bebauungsplan.', 1, 10),
         ]),
    dict(id='bpu_20210614', titel='4. Sitzung Bau-, Planungs- und Umweltausschuss – Juni 2021', ende='20:00',
         absent=['beubl', 'john', 'reif', 'wittmann'],
         vertretung={'reif': 'grundner', 'john': 'kaestl', 'beubl': 'pschorr'},
         partial=[{'member': 'kaestl', 'from': '19:15'}],
         beschluesse=[
             ('3', 'Genehmigung der Niederschrift vom 29.04.2021', NIEDERSCHRIFT, 10, 0, dict(ohne=['kaestl'])),
             ('4', 'Münchener Straße nördlicher Teil – Asphalt statt Pflaster',
              'Zwischen der Kreuzung Bahnhofstraße und der Fußgängerampel am Grabensepperlweg wird das Fahrbahnpflaster durch Asphalt ersetzt.', 10, 0, dict(ohne=['kaestl'])),
             ('5.1', 'Bürogebäude Driescherstr. 3', 'Einvernehmen erteilt.', 10, 0, dict(ohne=['kaestl'])),
             ('5.2', 'Neue Industriestr. 7 – Einzelhandel', 'Einvernehmen für Einzelhandel mit höchstens 2.950 m² Verkaufsfläche erteilt.', 11, 0),
             ('5.2', 'Neue Industriestr. 7 – Maß der Nutzung', 'Einvernehmen für das Gebäude im dargestellten Maß der baulichen Nutzung erteilt.', 11, 0),
             ('5.2', 'Neue Industriestr. 7 – Freiflächen',
              'Freiflächenplanung mit Befreiungen von den Satzungen der Stadt erteilt; verlangt wird ein qualifizierter Freiflächenplan mit Bäumen und genügend Fahrradstellplätzen.', 11, 0),
             ('5.2', 'Neue Industriestr. 7 – Parkdeck', 'Einvernehmen für ein Parkdeck auf dem eingeschossigen Gebäude erteilt.', 11, 0),
             ('5.2', 'Neue Industriestr. 7 – Arztpraxen und weitere Nutzungen', 'Einvernehmen für die beantragten Nutzungen erteilt.', 11, 0),
             ('5.2', 'Neue Industriestr. 7 – Apotheke', 'Eine Apotheke wird ausnahmsweise zugelassen.', 11, 0),
             ('5.3', 'Vorbescheid MFH 6 WE Thalbacher Str. 50 c – Einvernehmen erteilen', 'Antrag, das Einvernehmen zu erteilen, abgelehnt.', 2, 9,
              dict(weich={'altenbeck': 'no'}, presse=MK_NACHVERD)),
             ('5.3', 'Vorbescheid MFH 6 WE Thalbacher Str. 50 c – verweigert',
              'Einvernehmen verweigert: die Anordnung der Stellplätze gefährdet den Verkehr auf der Thalbacher Straße.', 10, 1),
             ('5.4', 'Vorbescheid MFH 5 WE Gärtnerstr. 51 – verweigert', 'Einvernehmen verweigert, die Wandhöhe fügt sich nicht ein.', 11, 0),
             ('5.4', 'Vorbescheid MFH 5 WE Gärtnerstr. 51 – Befreiung Stellplätze', 'Antrag, eine Befreiung von der Stellplatzsatzung in Aussicht zu stellen, einstimmig abgelehnt.', 0, 11),
             ('5.5', 'Dreifamilienhaus Asternstr. 21', 'Einvernehmen zu Abbruch der Doppelhaushälfte und Neubau mit sechs Stellplätzen erteilt.', 7, 4,
              dict(weich={'altenbeck': 'no'}, presse=MK_NACHVERD)),
             ('5.6', 'Zwei MFH mit Tiefgarage Anton-Nagel-Str. 8 und 10',
              'Einvernehmen erteilt, dazu ein verringerter Stauraum vor der Tiefgaragenzufahrt.', 7, 4,
              dict(weich={'kaestl': 'no', 'stanglmaier': 'no', 'dollinger': 'yes', 'pschorr': 'yes', 'kieninger': 'yes'}, presse=MK_NACHVERD)),
         ]),
    dict(id='bpu_20210719', titel='5. Sitzung Bau-, Planungs- und Umweltausschuss – Juli 2021',
         absent=['john'],
         notes=['John und sein Stellvertreter Kästl waren entschuldigt.'],
         beschluesse=[
             ('3', 'Genehmigung der Niederschrift vom 14.06.2021', NIEDERSCHRIFT, 11, 0),
             ('4', 'Ausbau der Lände – keine Einzelstellplätze', 'Die drei geplanten Einzelstellplätze werden nicht gebaut.', 6, 5),
             ('4', 'Ausbau der Lände – Variante 2',
              'Die Lände zwischen dem Wirtschaftsweg an der Landshuter Straße und der Kulturgrabenbrücke wird nach Variante 2 ausgebaut; die Verwaltung vergibt an die Fa. Richard Schulz.', 11, 0),
             ('5.1', 'Tektur MFH Thonstetten 5 a – Einvernehmen erteilen', 'Antrag, das Einvernehmen zu erteilen, abgelehnt.', 2, 9),
             ('5.1', 'Tektur MFH Thonstetten 5 a – verweigert',
              'Einvernehmen verweigert: lange Zufahrt, unnötige Versiegelung, Rücksichtnahmegebot, Verkehr für die Nachbarn.', 9, 2),
             ('5.2', 'Vierfamilienhaus Thonstetten 39', 'Einvernehmen zu Neubau und Abbruch von Verkaufsstätte und Lager erteilt.', 11, 0),
             ('5.3', 'Vorbescheid MFH Breitenbergstr. 4', 'Einvernehmen zum Vorbescheid erteilt.', 7, 4),
             ('5.3', 'Vorbescheid MFH Breitenbergstr. 4 – Befreiung drei Zufahrten', 'Befreiung von der Stellplatzsatzung für drei Zufahrten erteilt.', 6, 5),
             ('5.4', 'Auf dem Gries 7 – verweigert',
              'Einvernehmen verweigert: die Stellplätze sind nicht nutzbar, der Brandschutz nicht gesichert. Das Landratsamt soll Denkmalpflege und Abstandsflächen prüfen.', 11, 0),
             ('5.5', 'Vorbescheid zwei Doppelhäuser mit 8 WE Wiesenstraße', 'Einvernehmen zum Vorbescheid erteilt.', 11, 0),
         ]),
    dict(id='bpu_20210927', titel='6. Sitzung Bau-, Planungs- und Umweltausschuss – September 2021',
         absent=['hadersdorfer', 'stanglmaier', 'beubl', 'john', 'reif'],
         vertretung={'reif': 'grundner', 'beubl': 'pschorr'},
         notes=['Hadersdorfer, Stanglmaier und John waren samt ihren Stellvertretern (Heinz, Wagner, Kästl) entschuldigt.',
                'Die Niederschrift nennt Verena Beibl bei den namentlichen Abstimmungen unter ihrem früheren Namen Kuch.'],
         beschluesse=[
             ('3', 'Genehmigung der Niederschrift vom 19.07.2021', NIEDERSCHRIFT, 9, 0),
             ('4.1', 'Thonstetten – Verlängerung des Vorbescheids gewähren', 'Nach der Anhörung zur Ersetzung des Einvernehmens: Antrag auf Verlängerung abgelehnt.', 1, 8),
             ('4.1', 'Thonstetten – Verlängerung verweigert',
              'Einvernehmen zur Verlängerung weiter verweigert: Erschließung nicht gesichert, kein Wendehammer.', 8, 1),
             ('4.2', 'MFH 4 WE Thonstetten 5 a – Einvernehmen erteilen', 'Nach der Anhörung zur Ersetzung des Einvernehmens: Antrag, das Einvernehmen zu erteilen, abgelehnt.', 1, 8),
             ('4.2', 'MFH 4 WE Thonstetten 5 a – verweigert',
              'Einvernehmen weiter verweigert: Rücksichtnahmegebot, lange Zufahrt, Versiegelung, Verkehr.', 8, 1),
             ('4.3', 'Halle Gartenbaubetrieb Amperstr. 6', 'Einvernehmen zu Halle und Wildschutzzaun erteilt.', 9, 0),
             ('4.4', 'Fachmärkte Degernpoint M 2 – Erweiterung',
              'Einvernehmen zur Erweiterung der Fachmärkte und der Stellplatzanlage erteilt; Fahrradabstellanlagen sind in der Eingabeplanung darzustellen.', 5, 4,
              dict(ja=['dollinger', 'kieninger', 'pschorr', 'tristl', 'linz_karin'], nein=['beibl', 'altenbeck', 'grundner', 'wittmann'], thema=['t18'])),
             ('4.4', 'Fachmärkte Degernpoint M 2 – Non-Food-Discounter', 'Einvernehmen für Laden 01 als Non-Food-Discounter mit höchstens 800 m² Verkaufsfläche erteilt.', 5, 4,
              dict(ja=['dollinger', 'kieninger', 'pschorr', 'tristl', 'linz_karin'], nein=['beibl', 'altenbeck', 'grundner', 'wittmann'], thema=['t18'])),
             ('4.4', 'Fachmärkte Degernpoint M 2 – Sortimentsliste', 'Einvernehmen zur Sortimentsliste des Non-Food-Discounters erteilt.', 5, 4,
              dict(ja=['dollinger', 'kieninger', 'pschorr', 'tristl', 'linz_karin'], nein=['beibl', 'altenbeck', 'grundner', 'wittmann'], thema=['t18'])),
             ('4.4', 'Fachmärkte Degernpoint M 2 – Textil-Discounter verweigert',
              'Einvernehmen für Laden 02 als Textil-Discounter verweigert; der Bebauungsplan schließt dieses Sortiment aus.', 6, 3,
              dict(ja=['beibl', 'altenbeck', 'grundner', 'wittmann', 'pschorr', 'tristl'], nein=['dollinger', 'kieninger', 'linz_karin'], thema=['t18'])),
             ('4.4', 'Fachmärkte Degernpoint M 2 – Schuhladen verweigert', 'Einvernehmen für Laden 02 als Schuhladen verweigert, aus demselben Grund.', 6, 3,
              dict(ja=['beibl', 'altenbeck', 'grundner', 'wittmann', 'pschorr', 'tristl'], nein=['dollinger', 'kieninger', 'linz_karin'], thema=['t18'])),
             ('4.4', 'Fachmärkte Degernpoint M 2 – Backshop verweigert', 'Einvernehmen für Laden 02 als Backshop mit Café verweigert, aus demselben Grund.', 6, 3,
              dict(ja=['beibl', 'altenbeck', 'grundner', 'wittmann', 'pschorr', 'tristl'], nein=['dollinger', 'kieninger', 'linz_karin'], thema=['t18'])),
             ('4.4', 'Fachmärkte Degernpoint M 2 – Erotikmarkt', 'Einvernehmen für Laden 02 als Erotikmarkt erteilt.', 9, 0, dict(thema=['t18'])),
             ('4.5', 'Tektur Vorbescheid MFH Gärtnerstr. 51 b – Einvernehmen erteilen', 'Antrag, das Einvernehmen zum Vorbescheid zu erteilen, abgelehnt.', 4, 5),
             ('4.5', 'Tektur Vorbescheid MFH Gärtnerstr. 51 b – Stellplatznachweis', 'Antrag, das Einvernehmen zum Stellplatznachweis zu erteilen, abgelehnt.', 3, 6),
             ('4.6', 'Vorbescheid Landshuter Str. 101 – Einvernehmen erteilen', 'Antrag, das Einvernehmen zu erteilen, abgelehnt.', 4, 5,
              dict(ja=['beibl', 'altenbeck', 'linz_karin', 'pschorr'], nein=['dollinger', 'kieninger', 'grundner', 'wittmann', 'tristl'])),
             ('4.6', 'Vorbescheid Landshuter Str. 101 – verweigert',
              'Einvernehmen verweigert: Ersatz- und Erweiterungsbauten sind nach Grundfläche und Bauweise überdimensioniert.', 5, 4,
              dict(ja=['dollinger', 'kieninger', 'grundner', 'wittmann', 'tristl'], nein=['beibl', 'altenbeck', 'linz_karin', 'pschorr'])),
         ]),
    dict(id='bpu_20220324', titel='2. Sitzung Bau-, Planungs- und Umweltausschuss – März 2022',
         absent=['beibl'],
         notes=['Beibl und ihre Stellvertreterin von Pressentin waren entschuldigt.'],
         beschluesse=[
             ('3', 'Genehmigung der Niederschrift vom 24.01.2022',
              'Niederschrift genehmigt, ergänzt um den Redebeitrag von Dr. Stanglmaier zur Statzenbachstr. 8: die Kubatur füge sich nicht in die Umgebung ein.', 11, 0),
             ('4', 'Radwegbeleuchtung Münchener Straße',
              'Die Radwegbeleuchtung an der Münchener Straße wird nach dem Projektplan der SW München verlängert, dazu eine Leuchte an der Einmündung in die Reiteraustraße.', 11, 0),
             ('5', 'Widmung Verlängerung Unterreiterweg', 'Die Verlängerung des Unterreiterwegs (Fl.-Nr. 977/128) wird als Ortsstraße gewidmet.', 11, 0),
             ('6.1', 'Ersatzbau Wohnhaus Niederambach 1 a', 'Einvernehmen erteilt.', 11, 0),
             ('6.2', 'Vorbescheid 7 WE Kirchfeldstr. 24, Aich', 'Einvernehmen erteilt; Fahrradstellplätze und Spielplatz sind in der Eingabeplanung darzustellen.', 11, 0),
             ('6.3', 'Vorbescheid Einzel- und Doppelhäuser Uppenbornstr. 12', 'Einvernehmen erteilt; die Überschreitung der hinteren Baulinie gilt als unbedenklich.', 11, 0),
             ('6.4', 'Lagerhalle Pillhofen 4 – Einvernehmen erteilen', 'Antrag, das Einvernehmen zu erteilen, abgelehnt.', 2, 9),
             ('6.4', 'Lagerhalle Pillhofen 4 – verweigert', 'Einvernehmen verweigert, das Vorhaben liegt im Außenbereich.', 9, 2),
             ('6.4', 'Lagerhalle Pillhofen 4 – Situierung', 'Wegen der Einwände der Nachbarn wird die geplante Situierung nicht akzeptiert und ist zu überarbeiten.', 9, 2),
             ('6.5', 'Vorbescheid Doppelhaus und Dreispänner Südmährerweg 2 und 4',
              'Einvernehmen erteilt; versiegelte Flächen sollen wasserdurchlässig ausgeführt werden.', 11, 0),
             ('6.6', 'Vorbescheid fünf Reihenhäuser Burgermühlstr. 13 – verweigert', 'Einvernehmen verweigert: Gesamtlänge und Wandhöhe fügen sich nicht ein.', 11, 0),
             ('6.7', 'Doppelhaus Zanderstr. 3', 'Einvernehmen erteilt, dazu Befreiungen vom Bebauungsplan.', 8, 3),
         ]),
    dict(id='bpu_20220523', titel='3. Sitzung Bau-, Planungs- und Umweltausschuss – Mai 2022',
         absent=['hadersdorfer', 'beibl', 'john'],
         partial=[{'member': 'beubl', 'from': '19:15'}],
         beschluesse=[
             ('3.1', '20-kV-Schalthaus Am Kraftwerk 1, Pfrombach', 'Einvernehmen erteilt.', 8, 0, dict(ohne=['beubl'])),
             ('3.2', 'Vorbescheid MFH 6 WE Statzenbachstr. 8 – Einvernehmen nach Anhörung',
              'Nach der Anhörung zur Ersetzung des Einvernehmens erteilt der Ausschuss das Einvernehmen zum Vorbescheid.', 5, 3, dict(ohne=['beubl'])),
             ('3.3', 'Vorbescheid Anbau Auf dem Plan 14', 'Einvernehmen erteilt.', 7, 1, dict(ohne=['beubl'])),
             ('3.4', 'MFH 5 WE Thalbacher Str. 50 c', 'Einvernehmen erteilt; die Besucherstellplätze bleiben im Gemeinschaftseigentum.', 9, 0),
             ('3.5', 'EFH mit Doppelgarage Troll 1', 'Einvernehmen erteilt.', 9, 0),
             ('3.6', 'Vorbescheid MFH Stellwerkstr. 26 – Einvernehmen erteilen', 'Antrag, das Einvernehmen zu erteilen, abgelehnt.', 1, 8),
             ('3.6', 'Vorbescheid MFH Stellwerkstr. 26 – verweigert',
              'Einvernehmen verweigert wegen der Stellplatzsituation; empfohlen werden Stellplätze in einer Tiefgarage.', 8, 1),
             ('3.7', 'Wohn- und Ärztehaus Landshuter Str. 22 – Einvernehmen erteilen', 'Antrag, das Einvernehmen zu erteilen, abgelehnt.', 4, 5,
              dict(weich={'stanglmaier': 'no', 'beubl': 'no'}, presse=MK_AERZTE)),
             ('3.7', 'Wohn- und Ärztehaus Landshuter Str. 22 – verweigert',
              'Einvernehmen verweigert: oberirdische Stellplätze und Tiefgaragenausfahrt auf die Landshuter Straße machen die Erschließung sehr problematisch.', 5, 4,
              dict(weich={'stanglmaier': 'yes', 'beubl': 'yes'}, presse=MK_AERZTE)),
             ('4', 'Ölfernleitung TAL-IG – keine Einwendungen', 'Gegen die höhere Förderrate der Transalpinen Ölleitung erhebt die Stadt keine Einwendungen.', 9, 0),
         ]),
    dict(id='bpu_20220926', titel='4. Sitzung Bau-, Planungs- und Umweltausschuss – September 2022',
         absent=['john', 'reif'], vertretung={'reif': 'grundner', 'john': 'kaestl'},
         partial=[{'member': 'kaestl', 'from': '19:30'}],
         beschluesse=[
             ('3', 'Verkehrsberuhigung in der Lände', 'An der Lände wird nichts verändert; die Verwaltung beobachtet das Verkehrsaufkommen weiter.', 10, 1,
              dict(ohne=['kaestl'], thema=['t4'])),
             ('4.1', 'Vorbescheid MFH Stellwerkstr. 26 – Einvernehmen erteilen', 'Nach der Anhörung zur Ersetzung des Einvernehmens: Antrag, das Einvernehmen zu erteilen, abgelehnt.', 3, 8,
              dict(ohne=['kaestl'])),
             ('4.1', 'Vorbescheid MFH Stellwerkstr. 26 – verweigert',
              'Einvernehmen weiter verweigert: Stellplatzsituation; entgegen dem Landratsamt fügt sich das Vorhaben nach Art und Maß nicht ein.', 8, 3, dict(ohne=['kaestl'])),
             ('4.2', 'Vorbescheid Thalbacher Str. 108 – verweigert',
              'Einvernehmen verweigert: E + I + DG fügt sich nicht ein, zum Außenbereich hin soll es bei E + DG bleiben.', 11, 0, dict(ohne=['kaestl'])),
             ('4.3', 'Zahnarztpraxis Niederambach 1 b', 'Einvernehmen zur Nutzungsänderung im Erdgeschoss erteilt.', 8, 4),
             ('4.4', 'Wohn- und Ärztehaus Landshuter Str. 22, Neuplanung – Einvernehmen erteilen', 'Antrag, das Einvernehmen zu erteilen, abgelehnt.', 1, 11),
             ('4.4', 'Wohn- und Ärztehaus Landshuter Str. 22, Neuplanung – verweigert', 'Einvernehmen verweigert, die Stellplatzsatzung ist nicht eingehalten.', 11, 1),
             ('4.5', 'Pferdestall Eck 1, Pfrombach', 'Einvernehmen erteilt.', 12, 0),
             ('5', 'Spielplatz Sanddornstraße, Amperauen',
              'Der Spielplatz wird nach dem Konzept von KomPlan vom 13.09.2022 gebaut, ergänzt um eine Nestschaukel.', 12, 0, dict(thema=['t20'])),
         ]),
    dict(id='bpu_20250721', titel='4. Sitzung Bau-, Planungs- und Umweltausschuss – Juli 2025',
         absent=['dollinger', 'beibl', 'hobmaier', 'linz_karin', 'linz_kilian'],
         vertretung={'linz_karin': 'weber', 'linz_kilian': 'becher_a'},
         partial=[{'member': 'becher_a', 'from': '18:55',
                   'note': 'Alle öffentlichen Beschlüsse mit 8 Stimmen, also vor ihrem Eintreffen.'}],
         ohne_alle=['becher_a'],
         notes=['Sitzungsleitung: Zweiter Bürgermeister Hadersdorfer.'],
         beschluesse=[
             ('3', 'Genehmigung der Niederschrift vom 22.05.2025', NIEDERSCHRIFT, 8, 0),
             ('4.1', 'Einbahnregelung am Schulzentrum Süd',
              'Eine Sperrung von Breitenberg- und Vitztumstraße wird abgelehnt. Stattdessen gilt für zwei Jahre eine Einbahnregelung mit „Radfahrer frei“ über Rektor-Weh-, Breitenberg- und Vitztumstraße; die Verwaltung richtet Elternhaltestellen ein.',
              8, 0, dict(thema=['t8'])),
             ('5.1', 'Vorbescheid MFH 8 WE Sternstr. 12 – verweigert',
              'Einvernehmen verweigert: GRZ und GFZ fügen sich nicht ein, für drei Vollgeschosse gibt es keinen Bezugsfall.', 8, 0),
             ('5.2', 'Maschinenhalle Niederambach', 'Einvernehmen erteilt; das Landratsamt soll die Privilegierung prüfen.', 8, 0),
             ('5.4', 'Studentenwohnheim Saliterstr. 8 und 10 – verweigert',
              'Einvernehmen verweigert: kein allgemeines Wohnen im Sinne des Bebauungsplans, eine Bindung an Studierende ist rechtlich nicht möglich, die Stellplatzsatzung ist nicht eingehalten.',
              8, 0, dict(thema=['t5'])),
         ]),
    dict(id='bpu_20260413', titel='1. Sitzung Bau-, Planungs- und Umweltausschuss – April 2026',
         absent=['hobmaier'],
         beschluesse=[
             ('3', 'Teileinziehung Degernpointweg I', 'Der Degernpointweg I wird auf rund 80 m eingezogen.', 11, 0),
             ('4.1', 'Vorbescheid MFH 7 WE Sternstr. 12 – verweigert',
              'Einvernehmen erneut verweigert: der Baukörper fügt sich nicht in die Sternstraße ein, die Bezugsfälle an der Orionstraße tragen nicht, der Stellplatznachweis entspricht nicht der Satzung.', 11, 0),
             ('4.1', 'Vorbescheid MFH 7 WE Sternstr. 12 – Klage empfohlen', 'Der Ausschuss empfiehlt dem Stadtrat, gegen die Genehmigung des Vorbescheids zu klagen.', 11, 0),
             ('4.2', 'Austragshaus Eck 1, Pfrombach', 'Einvernehmen erteilt.', 11, 0),
             ('4.2', 'Austragshaus Eck 1 – § 36a BauGB', 'Keine Zustimmung nach § 36a BauGB, die Hofstelle Eck ist kein siedlungsnaher Außenbereich.', 11, 0),
             ('4.3', 'Anbau Sperberstr. 6 g', 'Einvernehmen erteilt.', 11, 0),
             ('4.4', 'Bahnhofstr. 50 – Wohnungen im Dachgeschoss',
              'Einvernehmen zur Nutzungsänderung des Dachgeschosses in fünf Wohnungen erteilt, dazu die isolierte Befreiung vom Bebauungsplan.', 11, 0),
         ]),
]

# Presse und Dossiers an den Tagesordnungspunkten
AGENDA_PRESSE = {
    ('bpu_20201109', '4.5'): [MK_HOTEL_AB],
    ('bpu_20201109', '4.10'): [MK_HOTEL_VOR, MK_HOTEL_AB],
    ('bpu_20210318', '5.3'): [MK_HOTEL_JA],
    ('bpu_20210429', '4'): [MZ_LAENDE],
    ('bpu_20210614', '4'): [MK_NACHVERD],
    ('bpu_20210614', '5.3'): [MK_NACHVERD],
    ('bpu_20210614', '5.4'): [MK_NACHVERD],
    ('bpu_20210614', '5.5'): [MK_NACHVERD],
    ('bpu_20210614', '5.6'): [MK_NACHVERD],
    ('bpu_20220523', '1'): [MK_HUBERHAUS],
    ('bpu_20220523', '3.6'): [MZ_ZWEI_MFH],
    ('bpu_20220523', '3.7'): [MK_AERZTE, MZ_ZWEI_MFH],
    ('bpu_20250721', '4.1'): [MZ_EINBAHN],
    ('bpu_20260413', '4.1'): [MZ_KLAGEWEG],
    ('sr_20250908', '4'): [MZ_EINBAHN_STREIT],
}
AGENDA_THEMA = {('bpu_20220523', '1'): 't17'}
AGENDA_NOTIZ = {
    ('bpu_20220523', '1'): 'Der Bürgermeister gibt bekannt, dass der Abriss des Huber-Hauses an der Herrnstraße genehmigt ist.',
    ('bpu_20250721', '5.3'): 'Antrag zurückgezogen.',
}

HISTORIE = {
    't4': [
        ('2020-11-09', 'bpu_20201109', '3.1', 0, 'Fahrradstraße Viehmarktstraße',
         'Auf Antrag der Grünen wird die Viehmarktstraße samt einem Stück Landshuter Straße zur Fahrradstraße (10:2).'),
        ('2020-11-09', 'bpu_20201109', '3.2', 0, 'Fahrradzone um die Graf-Konrad-Straße',
         'Auf Antrag der Grünen wird die Tempo-30-Zone für zwei Jahre zur Fahrradzone (9:3).'),
        ('2021-04-29', 'bpu_20210429', '4', 0, 'Lände: Prüfauftrag statt Sackgasse',
         'Anwohner wollten eine Sackgasse; der Ausschuss lässt stattdessen Fahrradstraße oder verkehrsberuhigten Bereich prüfen (8:3).'),
        ('2022-09-26', 'bpu_20220926', '3', 0, 'Lände bleibt, wie sie ist',
         'Keine Änderung an der Lände, die Verwaltung beobachtet das Verkehrsaufkommen (10:1).'),
    ],
    't31': [
        ('2020-11-09', 'bpu_20201109', '4.3', 0, 'Großtagespflege Rhenobotstraße',
         'Einvernehmen für die Umnutzung einer Wohnung in eine Großtagespflege, ohne zusätzliche Stellplätze (9:3).'),
    ],
    't18': [
        ('2021-09-27', 'bpu_20210927', '4.4', 0, 'Fachmärkte Degernpoint M 2 – namentlich',
         'Erweiterung und Non-Food-Discounter mit 5:4 genehmigt, Textil-, Schuh- und Backshop-Nutzung mit 6:3 verweigert; die Niederschrift nennt alle Namen.'),
    ],
    't20': [
        ('2022-09-26', 'bpu_20220926', '5', 0, 'Spielplatz Sanddornstraße',
         'Einstimmig: Spielplatz nach dem Konzept von KomPlan, ergänzt um eine Nestschaukel.'),
    ],
    't8': [
        ('2025-07-21', 'bpu_20250721', '4.1', 0, 'Einbahnregelung am Schulzentrum Süd',
         'Einstimmig (8:0): Einbahnregelung für zwei Jahre und Elternhaltestellen statt Straßensperrung. Nach Protesten der Anwohner ist die Regelung eine Woche später wieder vom Tisch.'),
    ],
    't5': [
        ('2025-07-21', 'bpu_20250721', '5.4', 0, 'Bauausschuss verweigert Einvernehmen zum Studentenwohnheim',
         'Einstimmig (8:0): kein allgemeines Wohnen im Sinne des Bebauungsplans, Stellplatzsatzung nicht eingehalten.'),
    ],
}
HISTORIE_PRESSE = {('t8', '2025-07-21'): [MZ_EINBAHN]}
MEILENSTEINE = {
    't17': [dict(date='2022-05-23', type='milestone', title='Abriss des Huber-Hauses genehmigt',
                 text='Im Bauausschuss gibt der Bürgermeister bekannt, dass die Abrissgenehmigung für das Huber-Haus an der Herrnstraße vorliegt. Damit kann die Erweiterung des Rathauses geplant werden.',
                 sessionId='bpu_20220523', press=[MK_HUBERHAUS])],
}


def baue(sitzung, alte_agenda):
    sid, datum = sitzung['id'], sitzung['id'][4:8] + '-' + sitzung['id'][8:10] + '-' + sitzung['id'][10:12]
    absent = sitzung['absent']
    vertretung = sitzung.get('vertretung', {})
    # Wer den Sitz an diesem Abend hielt: Mitglied, Vertretung oder niemand.
    platz = []
    for m in sitze(datum):
        if m not in absent:
            platz.append((m, True))
        elif m in vertretung:
            platz.append((vertretung[m], True))
        else:
            platz.append((m, False))

    votes, nr, je_top = [], 0, {}
    for b in sitzung['beschluesse']:
        top, titel, text, ja, nein = b[:5]
        opt = b[5] if len(b) > 5 else {}
        nr += 1
        vid = f'{sid}_{nr:02d}'
        je_top.setdefault(top, []).append(vid)
        ohne = set(opt.get('ohne', [])) | set(sitzung.get('ohne_alle', []))
        da = [p for p, besetzt in platz if besetzt and p not in ohne]
        leer = [p for p, besetzt in platz if not besetzt or p in ohne]
        v = {'id': vid, 'sessionId': sid}
        if opt.get('thema'):
            v['topicIds'] = opt['thema']
        v['title'] = titel
        v['text'] = text
        if 'ja' in opt:
            assert len(opt['ja']) == ja and len(opt['nein']) == nein, vid
            assert set(opt['ja'] + opt['nein']) == set(da), (vid, set(da) ^ set(opt['ja'] + opt['nein']))
            v['type'] = 'named'
            if ja < nein:
                v['result'] = 'rejected'
            v['results'] = {'yes': opt['ja'], 'no': opt['nein'], 'absent': leer}
            v['source'] = {'tier': 'protocol-explicit'}
        elif ja + nein == len(da) and (ja == 0 or nein == 0):
            v['type'] = 'named'
            if ja < nein:
                v['result'] = 'rejected'
            v['results'] = {'yes': da if ja else [], 'no': [] if ja else da, 'absent': leer}
            v['source'] = {'tier': 'protocol-implicit'}
        else:
            assert ja + nein == len(da), (vid, ja, nein, len(da))
            v['type'] = 'anonymous'
            if ja < nein:
                v['result'] = 'rejected'
            v['results'] = {'yes': ja, 'no': nein, 'absent': 12 - ja - nein}
            if ohne:
                v['results']['absent_ids'] = sorted(ohne)
            if opt.get('weich'):
                weich = opt['weich']
                assert set(weich) <= set(da), (vid, set(weich) - set(da))
                assert sum(1 for x in weich.values() if x == 'yes') <= ja, vid
                assert sum(1 for x in weich.values() if x == 'no') <= nein, vid
                v['source'] = {'tier': 'press', 'pressId': opt['presse']}
                v['voters'] = {m: {'vote': x, 'evidence': 'soft'} for m, x in weich.items()}
            else:
                v['source'] = {'tier': 'result-only'}
        votes.append(v)

    agenda = []
    nummern = {a['number'] for a in alte_agenda}
    for a in alte_agenda:
        a = {k: x for k, x in a.items() if k not in ('note', 'voteIds')}
        if a['number'] in je_top:
            a['voteIds'] = je_top[a['number']]
        agenda.append(a)
    return votes, agenda, nummern, je_top


def main():
    bodies = load('bodies.json')
    sessions = load('sessions.json')
    votes = load('votes.json')
    topics = load('topics.json')
    press = load('press.json')

    # ── Sitz John/Welter ────────────────────────────────────────────────────
    bpu = next(b for b in bodies if b['id'] == 'bpu')
    cfg = next(c for c in bpu['seatConfigs'] if c.get('from') == '2020-05-01')
    sitz = next(s for s in cfg['seats'] if s.get('member') == 'welter')
    sitz.clear()
    sitz['occupants'] = [{'member': 'john', 'from': '2020-05-01', 'to': '2023-03-05'},
                         {'member': 'welter', 'from': '2023-03-06'}]

    # ── Presse ──────────────────────────────────────────────────────────────
    vorhanden = {p['id'] for p in press}
    for pid, media, datum, titel, url in PRESSE:
        if pid not in vorhanden:
            press.append({'id': pid, 'media': media, 'date': datum, 'title': titel, 'url': url})

    # ── Die 14 Sitzungen ────────────────────────────────────────────────────
    by_id = {s['id']: s for s in sessions}
    neue_votes = {}
    for sitzung in SITZUNGEN:
        sid = sitzung['id']
        s = by_id[sid]
        alte_agenda = s.get('agenda', [])
        if sid == 'bpu_20260413':
            alte_agenda = ([{'number': '1', 'title': 'Mitteilungen des Ersten Bürgermeisters', 'type': 'formal'},
                            {'number': '2', 'title': 'Bürgerfragen gem. § 27 Abs. 2 und § 36 Abs. 1 GeschO/StR', 'type': 'formal'}]
                           + alte_agenda
                           + [{'number': '5', 'title': 'Anfragen und Sonstiges', 'type': 'formal'}])
        vs, agenda, nummern, je_top = baue(sitzung, alte_agenda)
        fehlt = set(je_top) - nummern
        assert not fehlt, (sid, fehlt)
        for a in agenda:
            k = (sid, a['number'])
            if k in AGENDA_PRESSE:
                a['press'] = AGENDA_PRESSE[k]
            if k in AGENDA_THEMA:
                a['topicId'] = AGENDA_THEMA[k]
            if k in AGENDA_NOTIZ:
                a['note'] = AGENDA_NOTIZ[k]
            themen = {t for vid in a.get('voteIds', []) for v in vs if v['id'] == vid for t in v.get('topicIds', [])}
            if len(themen) == 1:
                a['topicId'] = themen.pop()
        s['niederschrift'] = 'vollständig'
        s.pop('source', None)
        s['title'] = sitzung['titel']
        if sitzung.get('ende'):
            s['end'] = sitzung['ende']
        s['absent'] = sitzung['absent']
        if sitzung.get('vertretung'):
            s['substitutes'] = [{'member': m, 'substitute': x} for m, x in sitzung['vertretung'].items()]
        else:
            s.pop('substitutes', None)
        if sitzung.get('partial'):
            s['partial'] = sitzung['partial']
        if sitzung.get('notes'):
            s['notes'] = sitzung['notes']
        s['agenda'] = agenda
        # Feldreihenfolge wie in den übrigen vollständigen Sitzungen
        reihe = ['id', 'date', 'type', 'niederschrift', 'start', 'end', 'location', 'title', 'quellen',
                 'absent', 'partial', 'substitutes', 'notes', 'press', 'agenda']
        geordnet = {k: s[k] for k in reihe if k in s}
        s.clear()
        s.update(geordnet)
        neue_votes[sid] = vs

    # Sitzung vom 08.09.2025: Folgeartikel zur Einbahnregelung
    for a in by_id['sr_20250908']['agenda']:
        k = ('sr_20250908', a['number'])
        if k in AGENDA_PRESSE:
            a['press'] = sorted(set(a.get('press', [])) | set(AGENDA_PRESSE[k]))

    ergebnis, erledigt = [], set()
    for v in votes:
        sid = v['sessionId']
        if sid in neue_votes:
            if sid not in erledigt:
                ergebnis.extend(neue_votes[sid])
                erledigt.add(sid)
            continue
        ergebnis.append(v)
    for sid, vs in neue_votes.items():
        if sid not in erledigt:
            ergebnis.extend(vs)
    votes = ergebnis

    # ── 17.11.2022 und 23.01.2023: John statt Welter ────────────────────────
    s = by_id['bpu_20221117']
    s['absent'] = ['john', 'reif']
    s['partial'] = [{'member': 'gruebl', 'from': '19:10'}, {'member': 'kaestl', 'from': '19:40'}]
    reihe = ['id', 'date', 'type', 'niederschrift', 'start', 'end', 'title', 'absent', 'partial', 'substitutes', 'agenda']
    geordnet = {k: s[k] for k in reihe if k in s}
    s.clear()
    s.update(geordnet)
    elf = ['dollinger', 'hadersdorfer', 'stanglmaier', 'beubl', 'gruebl', 'kieninger',
           'beibl', 'linz_karin', 'linz_kilian', 'grundner', 'tristl']
    for v in votes:
        if v['sessionId'] == 'bpu_20221117':
            n = v['id'][-2:]
            if n == '01':
                v['results']['absent'] = ['gruebl', 'kaestl']
            elif n in ('02', '04'):
                v['results']['absent_ids'] = ['kaestl']
            elif n in ('03', '05'):
                v.pop('voters', None)
                v['type'] = 'named'
                v['results'] = {'yes': elf, 'no': [], 'absent': ['kaestl']}
            elif n in ('06', '11'):
                v.pop('voters', None)
                v['type'] = 'named'
                v['results'] = {'yes': elf + ['kaestl'], 'no': [], 'absent': []}
        if v['sessionId'] == 'bpu_20230123' and v['type'] == 'named':
            for feld in ('yes', 'no', 'absent'):
                v['results'][feld] = ['john' if m == 'welter' else m for m in v['results'][feld]]

    # ── Dossiers ────────────────────────────────────────────────────────────
    by_topic = {t['id']: t for t in topics}
    for tid, eintraege in HISTORIE.items():
        for datum, sid, top, idx, titel, text in eintraege:
            vid = next(a for a in by_id[sid]['agenda'] if a['number'] == top)['voteIds'][idx]
            h = {'date': datum, 'type': 'vote', 'title': titel, 'text': text, 'sessionId': sid, 'voteId': vid}
            if (tid, datum) in HISTORIE_PRESSE:
                h['press'] = HISTORIE_PRESSE[(tid, datum)]
            by_topic[tid]['history'].append(h)
    for tid, eintraege in MEILENSTEINE.items():
        by_topic[tid]['history'].extend(eintraege)
    for tid in set(HISTORIE) | set(MEILENSTEINE):
        by_topic[tid]['history'].sort(key=lambda h: h['date'])

    save('bodies.json', bodies)
    save('sessions.json', sessions)
    save('votes.json', votes)
    save('topics.json', topics)
    save('press.json', press)

    n = sum(len(x) for x in neue_votes.values())
    named = sum(1 for x in neue_votes.values() for v in x if v['type'] == 'named')
    print(f'{len(neue_votes)} Sitzungen, {n} Beschlüsse, davon {named} named, {n - named} anonym')


if __name__ == '__main__':
    main()
