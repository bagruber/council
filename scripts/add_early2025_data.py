import json

BASE = "c:/Users/bened/Documents/GitHub/bagruber/council/data"

# ── Member helpers ────────────────────────────────────────────────────────────
# Feb 2025: beubl still active (until late March), marcus not yet in council
ALL_FEB2025 = [
    "dollinger", "hadersdorfer", "tristl", "weber", "haberl",
    "linz_karin", "heinz",
    "beibl", "stanglmaier", "von_pressentin", "becher_j", "becher_a", "linz_kilian",
    "grundner", "lauterbach", "reif", "kieninger",
    "beubl", "pschorr",
    "gruber", "hobmaier",
    "welter", "kaestl", "fincke", "strobl",
]

# From late March 2025: beubl out, marcus in
ALL_2025 = [
    "dollinger", "hadersdorfer", "tristl", "weber", "haberl",
    "linz_karin", "heinz",
    "beibl", "stanglmaier", "von_pressentin", "becher_j", "becher_a", "linz_kilian",
    "grundner", "lauterbach", "reif", "kieninger",
    "pschorr", "marcus",
    "gruber", "hobmaier",
    "welter", "kaestl", "fincke", "strobl",
]

# BPU members at March 2025 (beubl still on BPU)
BPU_MAR2025_REGULARS = [
    "dollinger", "hadersdorfer", "stanglmaier",
    "beibl", "beubl", "hobmaier", "kieninger", "linz_karin",
    "linz_kilian", "reif", "tristl", "welter",
]

def yes_list(all_members, absent):
    return [m for m in all_members if m not in absent]

# ── Sessions ──────────────────────────────────────────────────────────────────
new_sessions = [
    {
        "id": "sr_20250210",
        "date": "2025-02-10",
        "type": "stadtrat",
        "title": "2. Stadtratssitzung – Februar 2025",
        "absent": ["dollinger", "beubl", "fincke", "linz_kilian", "reif"],
        "agenda": [
            {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
            {"number": 2, "title": "Bürgerfragen gem. § 27 Abs. 2 GeschO/StR", "type": "formal"},
            {"number": 3, "title": "Genehmigung der öffentlichen Niederschriften (StR 16.12.2024, BPU 16.01.2025)",
             "voteId": "sr_20250210_01"},
            {"number": "4.1", "title": "Bestätigung Erster Kommandant FFW Pfrombach-Aich (Rainer Göbl)",
             "voteId": "sr_20250210_02"},
            {"number": "4.2", "title": "Bestätigung Stellv. Kommandant FFW Pfrombach-Aich (Tobias Tristl)",
             "voteId": "sr_20250210_03"},
            {"number": "5.1", "title": "Aufstellungsbeschluss B-Plan „SO Freiflächen-PV-Anlage Kuttenweide“",
             "topicId": "t15", "voteId": "sr_20250210_04"},
            {"number": "5.2", "title": "Städtebaulicher Vertrag PV-Anlage Kuttenweide",
             "topicId": "t15", "voteId": "sr_20250210_05"},
            {"number": 6, "title": "Anfragen", "type": "formal"},
        ]
    },
    {
        "id": "sr_20250224",
        "date": "2025-02-24",
        "type": "stadtrat",
        "title": "3. Stadtratssitzung – Februar 2025",
        "absent": ["grundner", "haberl", "heinz", "kaestl", "von_pressentin"],
        "agenda": [
            {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
            {"number": 2, "title": "Bürgerfragen gem. § 27 Abs. 2 GeschO/StR", "type": "formal"},
            {"number": 3, "title": "Kostenloser Hallenbadeintritt für Kinder (Antrag StRin Beibl)",
             "voteId": "sr_20250224_01"},
            {"number": "4.1", "title": "Dienstleistungsvertrag enPORTAL – Bündelausschreibungen Strom/Gas",
             "voteId": "sr_20250224_02"},
            {"number": "4.2", "title": "Ermächtigung BGT Kommunal-GmbH Strombündelung",
             "voteId": "sr_20250224_03"},
            {"number": "4.3a", "title": "Strom-Ausschreibung Variante 1 – 100% Ökostrom mit Neuanlagenquote (abgelehnt)",
             "voteId": "sr_20250224_04"},
            {"number": "4.3b", "title": "Strom-Ausschreibung Variante 2 – 100% Ökostrom ohne Neuanlagenquote",
             "voteId": "sr_20250224_05"},
            {"number": "4.4", "title": "Ermächtigung Bürgermeister – Beschaffungskonzept",
             "voteId": "sr_20250224_06"},
            {"number": "4.5", "title": "Vergabe an wirtschaftlichsten Bieter",
             "voteId": "sr_20250224_07"},
            {"number": "4.6", "title": "Ermächtigung enPORTAL Verbrauchsdatenabfrage",
             "voteId": "sr_20250224_08"},
            {"number": 5, "title": "Anfragen", "type": "formal"},
        ]
    },
    {
        "id": "bpu_20250317",
        "date": "2025-03-17",
        "type": "bpu",
        "title": "2. Sitzung Bau-, Planungs- und Umweltausschuss",
        "substitutes": [{"member": "tristl", "substitute": "haberl"}],
        "agenda": [
            {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
            {"number": 2, "title": "Bürgerfragen gem. § 27 Abs. 2 / § 36 Abs. 1 GeschO/StR", "type": "formal"},
            {"number": "3.1", "title": "Wohn- und Geschäftshaus Bahnhofstr. 12",
             "voteId": "bpu_20250317_01"},
            {"number": "3.2", "title": "Ersatzneubau AWO Küche und Einzelwohnen Krankenhausweg 10",
             "voteId": "bpu_20250317_02"},
            {"number": "3.3", "title": "Vorbescheid MFH Moosstr. 15b, Aich – Einvernehmen verweigert",
             "voteId": "bpu_20250317_03"},
            {"number": "3.4a", "title": "MFH Neustadtstr. 17 – Einvernehmen erteilt (abgelehnt 3:9)",
             "voteId": "bpu_20250317_04"},
            {"number": "3.4b", "title": "MFH Neustadtstr. 17 – Einvernehmen verweigert",
             "voteId": "bpu_20250317_05"},
            {"number": 4, "title": "Anfragen und Sonstiges", "type": "formal"},
        ]
    },
    {
        "id": "sr_20250602",
        "date": "2025-06-02",
        "type": "stadtrat",
        "title": "8. Stadtratssitzung – Juni 2025",
        "absent": ["hadersdorfer", "stanglmaier", "heinz", "hobmaier", "strobl", "welter"],
        "agenda": [
            {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
            {"number": 2, "title": "Bürgerfragen gem. § 27 Abs. 2 GeschO/StR", "type": "formal"},
            {"number": 3, "title": "Genehmigung der öffentlichen Niederschriften (StR 10.04. und 28.04.2025)",
             "voteId": "sr_20250602_01"},
            {"number": 4, "title": "Information Hebesätze Grundsteuer A und B ab 2025",
             "type": "discussion"},
            {"number": "5.1", "title": "Feststellung Jahresrechnung 2023",
             "voteId": "sr_20250602_02"},
            {"number": "5.2", "title": "Entlastung Bürgermeister zur Jahresrechnung 2023",
             "voteId": "sr_20250602_03"},
            {"number": "5.3", "title": "Verwendung Gewinne 2023 (BgA Photovoltaik)",
             "voteId": "sr_20250602_04"},
            {"number": 6, "title": "Badegebühren Freibad – Redaktionelle Anpassung",
             "topicId": "t12", "voteId": "sr_20250602_05"},
            {"number": 7, "title": "Anfragen", "type": "formal"},
        ]
    },
    {
        "id": "sr_20250623",
        "date": "2025-06-23",
        "type": "stadtrat",
        "title": "9. Stadtratssitzung – Juni 2025",
        "absent": ["hadersdorfer", "stanglmaier", "becher_a", "kieninger", "von_pressentin", "weber"],
        "agenda": [
            {"number": 1, "title": "Mitteilungen des Ersten Bürgermeisters", "type": "formal"},
            {"number": 2, "title": "Bürgerfragen gem. § 27 Abs. 2 GeschO/StR", "type": "formal"},
            {"number": 3, "title": "Kommunale Wärmeplanung – Kenntnisnahme und Roadmap",
             "voteId": "sr_20250623_01"},
            {"number": 4, "title": "Vorlage Jahresrechnung 2024", "type": "discussion"},
            {"number": 5, "title": "Sanierung Bahnhof – Antrag Freie Wähler (vertagt)",
             "topicId": "t2", "type": "discussion"},
            {"number": 6, "title": "Sanierung Parkplatz Alte Polizei (zurückgestellt)",
             "voteId": "sr_20250623_02"},
            {"number": 7, "title": "Kostenloses Parken während Stadtplatzsanierung – Antrag Freie Wähler (abgelehnt)",
             "voteId": "sr_20250623_03"},
            {"number": 8, "title": "Anfragen", "type": "formal"},
        ]
    },
]

# ── Votes ─────────────────────────────────────────────────────────────────────
# sr_20250210: kaestl arrived 19:30, all votes were before that
_absent_0210 = ["dollinger", "beubl", "fincke", "linz_kilian", "reif", "kaestl"]
_absent_0224_session = ["grundner", "haberl", "heinz", "kaestl", "von_pressentin"]
_absent_0602 = ["hadersdorfer", "stanglmaier", "heinz", "hobmaier", "strobl", "welter"]
_absent_0623 = ["hadersdorfer", "stanglmaier", "becher_a", "kieninger", "von_pressentin", "weber"]

new_votes = [
    # ── sr_20250210 ──────────────────────────────────────────────────────────
    {
        "id": "sr_20250210_01",
        "sessionId": "sr_20250210", "topicId": None, "date": "2025-02-10",
        "title": "Genehmigung Niederschriften (StR 16.12.2024, BPU 16.01.2025)",
        "text": "Der Stadtrat genehmigt die öffentlichen Teile der Niederschriften der Stadtratssitzung vom 16.12.2024 und der BPU-Sitzung vom 16.01.2025.",
        "type": "named",
        "results": {"yes": yes_list(ALL_FEB2025, _absent_0210), "no": [], "absent": list(_absent_0210)}
    },
    {
        "id": "sr_20250210_02",
        "sessionId": "sr_20250210", "topicId": None, "date": "2025-02-10",
        "title": "Bestätigung Erster Kommandant FFW Pfrombach-Aich",
        "text": "Der Stadtrat bestätigt Rainer Göbl als Ersten Kommandanten der Freiwilligen Feuerwehr Pfrombach-Aich gemäß Art. 8 BayFwG.",
        "type": "named",
        "results": {"yes": yes_list(ALL_FEB2025, _absent_0210), "no": [], "absent": list(_absent_0210)}
    },
    {
        "id": "sr_20250210_03",
        "sessionId": "sr_20250210", "topicId": None, "date": "2025-02-10",
        "title": "Bestätigung Stellv. Kommandant FFW Pfrombach-Aich",
        "text": "Der Stadtrat bestätigt Tobias Tristl als stellvertretenden Kommandanten der Freiwilligen Feuerwehr Pfrombach-Aich gemäß Art. 8 BayFwG.",
        "type": "named",
        "results": {"yes": yes_list(ALL_FEB2025, _absent_0210), "no": [], "absent": list(_absent_0210)}
    },
    {
        "id": "sr_20250210_04",
        "sessionId": "sr_20250210", "topicId": "t15", "date": "2025-02-10",
        "title": "Aufstellungsbeschluss B-Plan PV Kuttenweide",
        "text": "Der Stadtrat beschließt die Aufstellung eines Bebauungsplans „SO Freiflächen-PV-Anlage Kuttenweide“ gem. § 2 BauGB im Parallelverfahren mit der Änderung des Flächennutzungsplans.",
        "type": "named",
        "results": {"yes": yes_list(ALL_FEB2025, _absent_0210), "no": [], "absent": list(_absent_0210)}
    },
    {
        "id": "sr_20250210_05",
        "sessionId": "sr_20250210", "topicId": "t15", "date": "2025-02-10",
        "title": "Städtebaulicher Vertrag PV Kuttenweide",
        "text": "Der Bürgermeister wird ermächtigt, mit dem Vorhabenträger einen städtebaulichen Vertrag zur Freiflächen-PV-Anlage Kuttenweide abzuschließen. Der Vorhabenträger trägt sämtliche Planungskosten.",
        "type": "named",
        "results": {"yes": yes_list(ALL_FEB2025, _absent_0210), "no": [], "absent": list(_absent_0210)}
    },

    # ── sr_20250224 ──────────────────────────────────────────────────────────
    {
        "id": "sr_20250224_01",
        "sessionId": "sr_20250224", "topicId": None, "date": "2025-02-24",
        "title": "Kostenloser Hallenbadeintritt für Kinder (abgelehnt)",
        "text": "Der Antrag der Sportreferentin Beibl auf kostenlosen Hallenbadeintritt für Kinder in den Faschingsferien 2025 (im Verlauf geändert auf Osterferien) wird abgelehnt.",
        "type": "anonymous",
        "result": "rejected",
        "results": {"yes": 9, "no": 10, "absent": 6}
    },
    {
        "id": "sr_20250224_02",
        "sessionId": "sr_20250224", "topicId": None, "date": "2025-02-24",
        "title": "Dienstleistungsvertrag enPORTAL – Strom-/Gasausschreibung",
        "text": "Der Stadtrat beschließt den Abschluss eines Dienstleistungsvertrags mit der enPORTAL GmbH zur Durchführung von Bündelausschreibungen für Strom- und Gasbeschaffung.",
        "type": "named",
        "results": {"yes": yes_list(ALL_FEB2025, _absent_0224_session), "no": [], "absent": list(_absent_0224_session)}
    },
    {
        "id": "sr_20250224_03",
        "sessionId": "sr_20250224", "topicId": None, "date": "2025-02-24",
        "title": "Ermächtigung BGT Kommunal-GmbH",
        "text": "Der Stadtrat ermächtigt die Kommunal-GmbH des Bayerischen Gemeindetags zur Entscheidungsfindung bei der Strombündelausschreibung ab 01.01.2026.",
        "type": "named",
        "results": {"yes": yes_list(ALL_FEB2025, _absent_0224_session), "no": [], "absent": list(_absent_0224_session)}
    },
    {
        "id": "sr_20250224_04",
        "sessionId": "sr_20250224", "topicId": None, "date": "2025-02-24",
        "title": "Stromqualität Variante 1 – Mit Neuanlagenquote (abgelehnt)",
        "text": "Variante 1 mit 100% Ökostrom inklusive Neuanlagenquote wird abgelehnt.",
        "type": "anonymous",
        "result": "rejected",
        "results": {"yes": 8, "no": 12, "absent": 5}
    },
    {
        "id": "sr_20250224_05",
        "sessionId": "sr_20250224", "topicId": None, "date": "2025-02-24",
        "title": "Stromqualität Variante 2 – Ohne Neuanlagenquote",
        "text": "Variante 2 mit 100% Ökostrom ohne Neuanlagenquote wird beschlossen.",
        "type": "named",
        "results": {"yes": yes_list(ALL_FEB2025, _absent_0224_session), "no": [], "absent": list(_absent_0224_session)}
    },
    {
        "id": "sr_20250224_06",
        "sessionId": "sr_20250224", "topicId": None, "date": "2025-02-24",
        "title": "Ermächtigung Bürgermeister – Beschaffungskonzept",
        "text": "Der Bürgermeister wird ermächtigt, das Beschaffungskonzept innerhalb der vertraglichen Fristen zu genehmigen.",
        "type": "named",
        "results": {"yes": yes_list(ALL_FEB2025, _absent_0224_session), "no": [], "absent": list(_absent_0224_session)}
    },
    {
        "id": "sr_20250224_07",
        "sessionId": "sr_20250224", "topicId": None, "date": "2025-02-24",
        "title": "Vergabe an wirtschaftlichsten Bieter",
        "text": "Der Auftrag wird vorbehaltlich der Beschaffungsvorgaben an den wirtschaftlichsten Bieter vergeben.",
        "type": "named",
        "results": {"yes": yes_list(ALL_FEB2025, _absent_0224_session), "no": [], "absent": list(_absent_0224_session)}
    },
    {
        "id": "sr_20250224_08",
        "sessionId": "sr_20250224", "topicId": None, "date": "2025-02-24",
        "title": "Vollmacht enPORTAL – Verbrauchsdatenabfrage",
        "text": "Die enPORTAL GmbH wird bevollmächtigt, Verbrauchsdaten von Energieversorgern und Netzbetreibern abzurufen.",
        "type": "named",
        "results": {"yes": yes_list(ALL_FEB2025, _absent_0224_session), "no": [], "absent": list(_absent_0224_session)}
    },

    # ── bpu_20250317 ─────────────────────────────────────────────────────────
    # 12 voters: BPU regulars (beubl still on BPU at this date) with haberl substituting tristl
    {
        "id": "bpu_20250317_01",
        "sessionId": "bpu_20250317", "topicId": None, "date": "2025-03-17",
        "title": "Wohn- und Geschäftshaus Bahnhofstr. 12",
        "text": "Der Bauausschuss erteilt das gemeindliche Einvernehmen zum Neubau eines Wohn- und Geschäftshauses mit Stellplätzen an der Bahnhofstraße 12. Befreiungen werden zugestimmt.",
        "type": "anonymous",
        "results": {"yes": 8, "no": 4, "absent": 0}
    },
    {
        "id": "bpu_20250317_02",
        "sessionId": "bpu_20250317", "topicId": None, "date": "2025-03-17",
        "title": "Ersatzneubau AWO Küche und Einzelwohnen Krankenhausweg 10",
        "text": "Der Bauausschuss erteilt einstimmig das gemeindliche Einvernehmen zum Ersatzneubau der AWO Küche und des Einzelwohnens (STE) am Krankenhausweg 10.",
        "type": "named",
        "results": {
            "yes": ["dollinger", "hadersdorfer", "stanglmaier", "beibl", "beubl", "hobmaier",
                    "kieninger", "linz_karin", "linz_kilian", "reif", "welter", "haberl"],
            "no": [], "absent": []
        }
    },
    {
        "id": "bpu_20250317_03",
        "sessionId": "bpu_20250317", "topicId": None, "date": "2025-03-17",
        "title": "Vorbescheid MFH Moosstr. 15b – Einvernehmen verweigert",
        "text": "Der Bauausschuss verweigert einstimmig das gemeindliche Einvernehmen für den Vorbescheid zum Neubau eines Mehrfamilienhauses an der Moosstr. 15b in Aich. Das Maß der baulichen Nutzung fügt sich nicht in den Umgebungscharakter ein.",
        "type": "named",
        "results": {
            "yes": ["dollinger", "hadersdorfer", "stanglmaier", "beibl", "beubl", "hobmaier",
                    "kieninger", "linz_karin", "linz_kilian", "reif", "welter", "haberl"],
            "no": [], "absent": []
        }
    },
    {
        "id": "bpu_20250317_04",
        "sessionId": "bpu_20250317", "topicId": None, "date": "2025-03-17",
        "title": "MFH Neustadtstr. 17 – Einvernehmen erteilt (abgelehnt)",
        "text": "Der Antrag, das gemeindliche Einvernehmen zum Neubau eines Mehrfamilienhauses an der Neustadtstr. 17 zu erteilen, wird abgelehnt.",
        "type": "anonymous",
        "result": "rejected",
        "results": {"yes": 3, "no": 9, "absent": 0}
    },
    {
        "id": "bpu_20250317_05",
        "sessionId": "bpu_20250317", "topicId": None, "date": "2025-03-17",
        "title": "MFH Neustadtstr. 17 – Einvernehmen verweigert",
        "text": "Der Bauausschuss verweigert das gemeindliche Einvernehmen zum Neubau eines Mehrfamilienhauses an der Neustadtstr. 17. Probleme bei Dichte, Versiegelung, Stellplatzpflicht und Spielplatznachweis.",
        "type": "anonymous",
        "results": {"yes": 9, "no": 3, "absent": 0}
    },

    # ── sr_20250602 ──────────────────────────────────────────────────────────
    # vote 3 (18 yes): 1 brief absent unknown – leave anonymous
    {
        "id": "sr_20250602_01",
        "sessionId": "sr_20250602", "topicId": None, "date": "2025-06-02",
        "title": "Genehmigung Niederschriften (StR 10.04. und 28.04.2025)",
        "text": "Der Stadtrat genehmigt die öffentlichen Teile der Niederschriften der Stadtratssitzungen vom 10.04.2025 und 28.04.2025.",
        "type": "anonymous",
        "results": {"yes": 18, "no": 0, "absent": 7}
    },
    {
        "id": "sr_20250602_02",
        "sessionId": "sr_20250602", "topicId": None, "date": "2025-06-02",
        "title": "Feststellung Jahresrechnung 2023",
        "text": "Der Stadtrat beschließt die Feststellung der Jahresrechnung 2023 gemäß Art. 102 Abs. 3 Satz 1 GO.",
        "type": "named",
        "results": {"yes": yes_list(ALL_2025, _absent_0602), "no": [], "absent": list(_absent_0602)}
    },
    {
        "id": "sr_20250602_03",
        "sessionId": "sr_20250602", "topicId": None, "date": "2025-06-02",
        "title": "Entlastung Bürgermeister – Jahresrechnung 2023",
        "text": "Der Stadtrat erteilt dem Ersten Bürgermeister Entlastung für die Jahresrechnung 2023. Bürgermeister Dollinger nimmt wegen persönlicher Beteiligung an der Abstimmung nicht teil.",
        "type": "named",
        "results": {"yes": yes_list(ALL_2025, _absent_0602 + ["dollinger"]), "no": [],
                    "absent": list(_absent_0602) + ["dollinger"]}
    },
    {
        "id": "sr_20250602_04",
        "sessionId": "sr_20250602", "topicId": None, "date": "2025-06-02",
        "title": "Verwendung Gewinne 2023 – BgA Photovoltaik",
        "text": "Die Gewinne aus dem Jahr 2023 der Betriebe gewerblicher Art (Photovoltaikanlagen, 26.101 €) werden den Rücklagen zugeführt.",
        "type": "named",
        "results": {"yes": yes_list(ALL_2025, _absent_0602), "no": [], "absent": list(_absent_0602)}
    },
    {
        "id": "sr_20250602_05",
        "sessionId": "sr_20250602", "topicId": "t12", "date": "2025-06-02",
        "title": "Badegebühren Freibad – Redaktionelle Anpassung",
        "text": "Der Stadtrat beschließt die redaktionelle Anpassung der Badegebührenordnung mit Wirkung zur Saison 2025.",
        "type": "named",
        "results": {"yes": yes_list(ALL_2025, _absent_0602), "no": [], "absent": list(_absent_0602)}
    },

    # ── sr_20250623 ──────────────────────────────────────────────────────────
    {
        "id": "sr_20250623_01",
        "sessionId": "sr_20250623", "topicId": None, "date": "2025-06-23",
        "title": "Kommunale Wärmeplanung – Kenntnisnahme",
        "text": "Der Stadtrat nimmt den Abschlussbericht der kommunalen Wärmeplanung zur Kenntnis und anerkennt ihn als strategische Grundlage für künftige Energie- und Infrastrukturentscheidungen. Die Verwaltung wird beauftragt, Maßnahmen zu priorisieren, Fördermöglichkeiten zu prüfen und die Stakeholder-Beteiligung fortzuführen.",
        "type": "named",
        "results": {"yes": yes_list(ALL_2025, _absent_0623), "no": [], "absent": list(_absent_0623)}
    },
    {
        "id": "sr_20250623_02",
        "sessionId": "sr_20250623", "topicId": None, "date": "2025-06-23",
        "title": "Sanierung Parkplatz Alte Polizei – zurückgestellt",
        "text": "Über den Antrag der Freien Wähler zur Sanierung des Parkplatzes Alte Polizei wird zunächst nicht entschieden – der Punkt wird zurückgestellt.",
        "type": "anonymous",
        "results": {"yes": 12, "no": 7, "absent": 6}
    },
    {
        "id": "sr_20250623_03",
        "sessionId": "sr_20250623", "topicId": None, "date": "2025-06-23",
        "title": "Kostenloses Parken während Stadtplatzsanierung (abgelehnt)",
        "text": "Der Antrag der Freien Wähler, während der Stadtplatzsanierung kostenloses Parken auf den Parkplätzen Zehentstadel und Alte Polizei (mit Parkscheibe, max. 2 Std., bis 31.07.2025) zu ermöglichen, wird abgelehnt.",
        "type": "anonymous",
        "result": "rejected",
        "results": {"yes": 9, "no": 10, "absent": 6}
    },
]

# ── Topics ────────────────────────────────────────────────────────────────────
new_topics = [
    {
        "id": "t15",
        "title": "Photovoltaik-Freiflächenanlage Kuttenweide",
        "tags": ["energy", "infrastructure", "building"],
        "image": None,
        "summary": "Die Stadt stellt einen Bebauungsplan für eine Freiflächen-Photovoltaikanlage am Standort Kuttenweide auf. Im Parallelverfahren wird der Flächennutzungsplan angepasst. Der Vorhabenträger trägt die Planungskosten via städtebaulichem Vertrag.",
        "history": [
            {
                "date": "2025-02-10",
                "type": "vote",
                "title": "Aufstellungsbeschluss B-Plan",
                "text": "Der Stadtrat beschließt einstimmig die Aufstellung des Bebauungsplans „SO Freiflächen-PV-Anlage Kuttenweide“ im Parallelverfahren mit der Änderung des Flächennutzungsplans.",
                "sessionId": "sr_20250210",
                "voteId": "sr_20250210_04"
            },
            {
                "date": "2025-02-10",
                "type": "vote",
                "title": "Städtebaulicher Vertrag",
                "text": "Der Bürgermeister wird ermächtigt, mit dem Vorhabenträger einen städtebaulichen Vertrag abzuschließen. Der Investor trägt sämtliche Planungskosten.",
                "sessionId": "sr_20250210",
                "voteId": "sr_20250210_05"
            }
        ]
    }
]

# ── Apply ─────────────────────────────────────────────────────────────────────
with open(f"{BASE}/sessions.json", "r", encoding="utf-8") as f:
    sessions = json.load(f)
existing = {s["id"] for s in sessions}
for s in new_sessions:
    if s["id"] not in existing:
        sessions.append(s)
        print(f"session added: {s['id']}")
with open(f"{BASE}/sessions.json", "w", encoding="utf-8") as f:
    json.dump(sessions, f, ensure_ascii=False, indent=2)

with open(f"{BASE}/votes.json", "r", encoding="utf-8") as f:
    votes = json.load(f)
existing_v = {v["id"] for v in votes}
added_v = 0
for v in new_votes:
    if v["id"] not in existing_v:
        votes.append(v)
        added_v += 1
with open(f"{BASE}/votes.json", "w", encoding="utf-8") as f:
    json.dump(votes, f, ensure_ascii=False, indent=2)
print(f"votes added: {added_v}")

with open(f"{BASE}/topics.json", "r", encoding="utf-8") as f:
    topics = json.load(f)
existing_t = {t["id"] for t in topics}
for t in new_topics:
    if t["id"] not in existing_t:
        topics.append(t)
        print(f"topic added: {t['id']}")
with open(f"{BASE}/topics.json", "w", encoding="utf-8") as f:
    json.dump(topics, f, ensure_ascii=False, indent=2)

print("\nDone.")
