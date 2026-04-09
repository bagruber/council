# OParl 1.1 – API-Referenz

> **Was:** Standardisierte REST/JSON-Webservice-Schnittstelle für parlamentarische Informationssysteme (Ratsinformationssysteme, kurz RIS) in Deutschland.  
> **Zweck:** Anonymer, lesender Zugriff auf öffentliche Sitzungs-, Gremien- und Dokumentendaten von Kommunen.  
> **Spezifikation:** https://dev.oparl.org/spezifikation  
> **Namespace:** `https://schema.oparl.org/1.1/`  
> **Endpunkte:** https://dev.oparl.org/endpunkte

---

## Technische Grundlagen

- **Protokoll:** HTTP/HTTPS (HTTPS empfohlen)
- **Format:** JSON, UTF-8 ohne BOM
- **Authentifizierung:** keine – vollständig anonym
- **Zustandslosigkeit:** Alle Zugriffe müssen ohne Session/Cookies funktionieren
- **CORS:** Server müssen CORS unterstützen

### Datumsformate
| Typ | Format | Beispiel |
|-----|--------|---------|
| `date` | `yyyy-mm-dd` | `1969-07-21` |
| `date-time` | `yyyy-mm-ddThh:mm:ss±hh:mm` | `1969-07-21T02:56:00+00:00` |

### JSON-Datentypen
`object`, `array`, `integer`, `boolean`, `string`, `url`, `date`, `date-time`

- Fehlende Eigenschaften: weglassen statt `null` ausgeben
- Pflichtfelder dürfen **nicht** `null` sein
- Leere Arrays bei Pflichtfeldern: `[]` ausgeben; bei optionalen weglassen

### Anforderungsnomenklatur (angelehnt an RFC2119)
| Deutsch | RFC2119 | Bedeutung |
|---------|---------|-----------|
| **müssen/muss** | MUST | zwingend erforderlich |
| **nicht dürfen** | MUST NOT | absolutes Verbot |
| **sollten/sollte** | SHOULD | empfohlen |
| **sollten nicht** | SHOULD NOT | nicht empfohlen |
| **dürfen/darf** | MAY | optional |

---

## URLs & Kanonisierung

- Jedes Objekt hat exakt eine unveränderliche **kanonische URL**
- Keine IP-Adressen in URLs verwenden → stabiler Hostname
- Server nur über eine Domain erreichbar (nicht-kanonische → 301-Redirect)
- Groß-/Kleinschreibung, Schrägstriche und führende Nullen sind Teil der kanonischen Schreibweise
- Query-String-Parameter immer gleich sortieren
- Clients dürfen URLs **nicht** verändern
- Implementierungsdetails (z. B. `.php`) nicht in URLs sichtbar machen

---

## Objektlisten & Paginierung

Listen werden als externe Referenz-URL oder intern eingebettet ausgegeben – je nach Schema-Definition des Attributs. Große Listen werden paginiert zurückgegeben.

---

## Objektmodell (Schema)

Alle Typen tragen das Präfix `oparl:`, z. B. `oparl:Organization` = `https://schema.oparl.org/1.1/Organization`.

### Übersicht Objekttypen

| Typ | Beschreibung |
|-----|-------------|
| `oparl:System` | Einstiegspunkt der API; beschreibt den Server |
| `oparl:Body` | Gebietskörperschaft / Gremium (z. B. Stadtrat) |
| `oparl:LegislativeTerm` | Wahlperiode |
| `oparl:Organization` | Ausschuss, Fraktion, Partei o. ä. |
| `oparl:Person` | Eine natürliche Person (Ratsmitglied etc.) |
| `oparl:Membership` | Mitgliedschaft einer Person in einer Organization |
| `oparl:Meeting` | Sitzung eines Gremiums |
| `oparl:AgendaItem` | Tagesordnungspunkt einer Sitzung |
| `oparl:Paper` | Drucksache / Vorlage |
| `oparl:Consultation` | Beratung einer Drucksache in einer Sitzung |
| `oparl:File` | Datei/Dokument (PDF, ODT etc.) |
| `oparl:Location` | Geodaten (Punkt, Linie, Polygon via GeoJSON) |

### oparl:System
Einstiegspunkt der gesamten API. Enthält u. a. Links zu allen `Body`-Objekten und Metadaten zum Server (OParl-Version, Name, Kontakt).

### oparl:Body
Repräsentiert eine Gebietskörperschaft. Enthält Listen-URLs für Organizations, Persons, Meetings, Papers, etc.

### oparl:Organization
Gremium, Fraktion oder Ausschuss. Verweist auf Mitgliedschaften (`membership`) und Sitzungen (`meeting`).

### oparl:Person
Natürliche Person. Felder u. a.: `name`, `email`, `phone`, `status`, `gender`. Datenschutz beachten!

### oparl:Membership
Verbindet `Person` mit `Organization`. Enthält Rolle (`role`), Von-/Bis-Datum.

### oparl:Meeting
Sitzung. Enthält `start`/`end` (date-time), Ort (`location`), Tagesordnung (`agendaItem`-Liste), Einladung/Protokoll als `File`.

### oparl:AgendaItem
Tagesordnungspunkt. Verweist auf zugehörige `Paper` und `Consultation`.

### oparl:Paper
Drucksache/Vorlage. Enthält Typ (`paperType`), Datum, Dateien (`mainFile`, `auxiliaryFile`), Beratungen (`consultation`), Geodaten (`location`) optional.

### oparl:Consultation
Beratung einer Drucksache. Verbindet `Paper` ↔ `AgendaItem` ↔ `Organization`.

### oparl:File
Datei. Felder: `accessUrl`, `downloadUrl`, `mimeType`, `size`, optional `text` (Volltext-Plaintext für Indexierung), `fileName`. Kann auf andere Dateien (andere Formate desselben Inhalts) verweisen.

### oparl:Location
Geodaten nach GeoJSON. Kann Punkt, Linie oder Polygon enthalten. Wird in `Paper`, `Meeting`, `Body` etc. eingebettet.

---

## Gelöschte Objekte

Gelöschte Objekte werden nicht einfach entfernt, sondern als gelöscht markiert zurückgegeben (damit Clients ihren Cache aktualisieren können). Relevant beim inkrementellen Abruf über `modified`-Filter.

## Fehlerbehandlung

Server gibt HTTP-Statuscodes zurück. Fehlerhafte Anfragen → 4xx, Serverfehler → 5xx. Clients dürfen bei unbekannten Erweiterungen **nicht** fehlschlagen.

## Erweiterbarkeit

- Server darf eigene (nicht im Schema definierte) Objekttypen und Eigenschaften ausgeben
- Clients müssen unbekannte Felder ignorieren (keine Fehler)
- Mehrere OParl-Versionen können parallel unter verschiedenen URLs angeboten werden

---

## Typische Abfolge beim Datenabruf

```
GET /  →  oparl:System
  └─ bodyList  →  [oparl:Body, ...]
       ├─ organizationList  →  [oparl:Organization, ...]
       │    └─ membership   →  [oparl:Membership → oparl:Person]
       ├─ meetingList  →  [oparl:Meeting, ...]
       │    ├─ agendaItem   →  [oparl:AgendaItem]
       │    │    └─ consultation → oparl:Consultation → oparl:Paper
       │    └─ invitation/resultsProtocol  →  oparl:File
       └─ paperList  →  [oparl:Paper, ...]
            ├─ mainFile      →  oparl:File
            └─ location      →  oparl:Location (optional)
```

---

## Datenschutzhinweis

Personenbezogene Daten (E-Mail, Anschrift, Fotos, Anwesenheitslisten) dürfen nur mit Zustimmung der betroffenen Person veröffentlicht werden. Vor Inbetriebnahme Datenschutzbeauftragten konsultieren.

---

## Weiterführende Links

- Spezifikation: https://dev.oparl.org/spezifikation
- Bekannte Endpunkte: https://dev.oparl.org/endpunkte
- GitHub / Issue Tracker: https://github.com/OParl/spec/issues/
- Schema-Namespace: https://schema.oparl.org/1.1/
