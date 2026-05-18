---
name: antrag-einarbeiten
description: Trägt einen Stadtrats-Antrag in das profile.motions[]-Array des einbringenden Mitglieds in members.json ein. Verlinkt zu Sitzung, Abstimmung und ggf. Presseartikel. Nutze dies wenn jemand erwähnt „X hat einen Antrag zu Y eingebracht" und es nicht ohnehin schon Teil einer Niederschriften-Integration ist.
---

# Antrag in Member-Profil einarbeiten

## Auslöser

- User berichtet von einem konkreten Antrag, der von einem Stadtratsmitglied oder einer Fraktion eingebracht wurde.
- Eine Niederschrift erwähnt explizit „Antrag von …" — `niederschrift-einarbeiten` legt die Sitzung+Abstimmung an, dieser Skill ergänzt die Antragstellerin-Seite.
- Ein Presseartikel hebt einen bestimmten Antrag hervor → vorzugsweise gleich nach `presseartikel-einarbeiten` ausführen.

Nicht für: jede einzelne Beschluss-Vorlage. Nur für Anträge, die ein:e Stadträt:in *eigeninitiativ* gestellt hat (oder eine Fraktion).

## Inputs

- **Antragsteller:in**: Member-ID (z.B. `gruber`) oder Fraktion (z.B. „Fresh-Fraktion"). Falls Fraktion: in `motions[]` jedes betroffenen Mitglieds eintragen, oder den/die Initiator:in als primären.
- **Datum**: YYYY-MM-DD (Einbringung).
- **Titel**: kurz, was beantragt wird.
- **Beschreibung**: 1–3 Sätze.
- **Verknüpfungen** (optional): `sessionId`, `voteId`, `press: [pressId, …]`, `topicId`.
- **Status**: `"pending" | "approved" | "rejected" | "withdrawn"`.

## Datenmodell

```jsonc
// data/members.json → members[].profile.motions[]
{
  "date": "2024-06-12",
  "title": "Antrag auf verkehrsberuhigten Bereich Auf dem Plan",
  "text":  "Fresh fordert die Ausweisung des Platzes Auf dem Plan als verkehrsberuhigten Bereich gemäß § 42 StVO …",
  "status": "approved",
  "topicId": "t3",
  "sessionId": "sr_20240612",
  "voteId": "sr_20240612_03",
  "press": ["merkur_2024-06-13_plan"]
}
```

## Vorgehen

1. Member finden in `data/members.json`. Falls Antrag von Fraktion: meist nur Initiator:in als Eintrag, oder mit Vermerk „im Namen der Fraktion".
2. `profile.motions` finden oder anlegen (`{ "motions": [] }` falls nicht da).
3. Eintrag anhängen. Liste nach `date` sortiert halten.
4. Wenn `voteId` referenziert wird, im entsprechenden Vote-Objekt prüfen, ob `topicId` und das `agenda`-Item zur Topic passen.
5. Wenn ein Presseartikel verknüpft wird, prüfen ob die Press-ID existiert. Sonst zuerst `presseartikel-einarbeiten` aufrufen.
6. **`validate-data`** ausführen.
7. Commit: `motion: gruber – verkehrsberuhigter Bereich auf dem Plan (12.06.2024)`.

## Edge Cases

- **Antrag wurde später zurückgezogen**: `status: "withdrawn"` + Notiz im `text`.
- **Mehrere Anträge zum gleichen Thema**: jeden einzeln, mit eigenem Datum.
- **Antrag ohne Abstimmung** (Antrag wurde gar nicht behandelt, abgeschmettert in einer Vorbesprechung): `status: "pending"`, kein `voteId`.
- **Sammelantrag** (z.B. Fresh + SPD gemeinsam): in beiden Profilen eintragen, im `text` die Co-Antragsteller:innen nennen.
