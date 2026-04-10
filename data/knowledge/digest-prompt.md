# LLM Digest Prompt

Verwende diesen Prompt, um neue Presseartikel oder Sitzungsniederschriften aufzubereiten und strukturiert für die App zu erfassen.

---

## Prompt

Du bekommst eine Quelle (Presseartikel oder Sitzungsniederschrift) aus dem Stadtrat Moosburg a.d. Isar. Extrahiere die folgenden Informationen und gib sie als strukturiertes JSON aus.

### Bei Presseartikeln

Erstelle einen Eintrag für `data/press.json`:

```json
{
  "id": "{medium}_{YYYY-MM-DD}_{slug}",
  "media": "{medium}",
  "date": "YYYY-MM-DD",
  "title": "Kurztitel des Artikels",
  "url": "URL des Artikels"
}
```

- `media`: Kürzel des Mediums (`merkur`, `sz`, `br`, `mz`, etc.)
- `slug`: kurzer, beschreibender Slug in Kebab-Case (z.B. `kreisverkehr`, `parken-plan`)
- `title`: Kurztitel ohne Medienname-Prefix

Prüfe außerdem, zu welchem bestehenden Topic (`t1`–`t10` etc.) der Artikel passt, und gib an, in welchem History-Eintrag die Press-ID referenziert werden soll. Falls kein passendes Topic existiert, schlage ein neues vor.

### Bei Sitzungsniederschriften

Extrahiere pro Tagesordnungspunkt:

```json
{
  "session": {
    "id": "s{N}",
    "date": "YYYY-MM-DD",
    "title": "Sitzung des Stadtrats / Ausschussname",
    "body": "stadtrat | bpu | hvfa | pa | rpa",
    "absent": ["member_id_1", "member_id_2"]
  },
  "agendaItems": [
    {
      "title": "Titel des TOP",
      "summary": "1-2 Sätze Zusammenfassung",
      "topicId": "t{N} oder null",
      "vote": {
        "id": "v{N}",
        "title": "Beschlusstext kurz",
        "type": "named | anonymous",
        "results": {}
      }
    }
  ]
}
```

Für Abstimmungen:
- `type: "named"` wenn Einzelstimmen bekannt: `{ "ja": ["id1"], "nein": ["id2"], "enthaltung": ["id3"] }`
- `type: "anonymous"` wenn nur Zahlen: `{ "ja": 18, "nein": 4, "enthaltung": 0 }`
- Bei einstimmigen Beschlüssen ohne Gegenstimmen: `{ "result": "unanimous", "total": 22 }`
- Falls Mitglieder bei einzelnen Abstimmungen kurz abwesend waren: `"absent_ids": ["member_id"]`

### Zusätzlich immer

- **Neue Fakten**: Sachverhalte, die keinem bestehenden Topic zugeordnet sind, aber relevant sein könnten (z.B. neue Anträge, Personalien, Projekte)
- **Verknüpfungen**: Welche Members werden namentlich erwähnt? In welcher Rolle?
- **Zeitangaben**: Alle Daten in absoluter Form (YYYY-MM-DD), relative Angaben wie "nächste Woche" umrechnen
- **Stimmung/Kontroverse**: Kurze Einschätzung, ob der TOP kontrovers diskutiert wurde

### Ausgabeformat

Gib die extrahierten Daten als JSON-Blöcke aus, die direkt in die entsprechenden Dateien eingefügt werden können:
1. Neue Einträge für `data/press.json`
2. Neue/aktualisierte Einträge für `data/sessions.json`
3. Neue/aktualisierte Einträge für `data/votes.json`
4. Neue History-Einträge für bestehende Topics in `data/topics.json`
5. Vorschläge für neue Topics
6. Sonstige relevante Informationen für die Knowledge Base
