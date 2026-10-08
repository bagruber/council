// Prüft die Zählungen, auf denen Datenlage und Methodik-Seite beruhen — am
// echten Bestand, nicht an erfundenen Daten. Beide Seiten nennen dieselben
// Zahlen, weil sie dieselbe Funktion rufen; abgesichert wird hier, dass diese
// Funktion nichts verschluckt.

import { test, before } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

let d;

before(async () => {
  globalThis.fetch = async (pfad) => ({
    ok: true,
    status: 200,
    json: async () => JSON.parse(
      readFileSync(new URL("../" + pfad, import.meta.url), "utf8")),
  });
  d = await import("../js/daten.js");
  await d.ladeDaten();
});

test("Das Register geht in den drei Stufen auf", () => {
  const b = d.bestand();
  assert.equal(b.vollstaendig + b.auszug + b.keine, b.sitzungen);
});

test("Jede gehaltene Sitzung trägt eine bekannte Stufe", () => {
  const erlaubt = new Set(["vollständig", "auszug", "keine"]);
  const fremd = d.sessionRegister().filter(s => !erlaubt.has(s.niederschrift));
  assert.deepEqual(fremd.map(s => s.id), []);
});

test("Die Herkunftsstufen summieren sich auf alle Abstimmungen", () => {
  const c = d.tierCounts(d.sessionRegister().flatMap(d.votenVon));
  const summe = Object.values(c).reduce((n, x) => n + x, 0);
  assert.equal(summe, d.bestand().abstimmungen);
});

test("Keine Abstimmung fällt wegen unbekannter Stufe auf „nur Ergebnis“", () => {
  // tierCounts zählt alles Unbekannte zu `sum`. Stünde dort eine Stufe, die
  // es nicht geben soll, erklärte die Methodik-Seite sie als „nur das
  // Ergebnis bekannt“ — und das wäre gelogen.
  const erlaubt = new Set(["protocol-explicit", "protocol-implicit", "tracked",
                           "press", "selbstauskunft", "result-only"]);
  const fremd = d.votes.filter(v => !erlaubt.has((v.source || {}).tier));
  assert.deepEqual(fremd.map(v => v.id), []);

  const c = d.tierCounts(d.sessionRegister().flatMap(d.votenVon));
  const echte = d.votes.filter(v => v.source.tier === "result-only").length;
  assert.equal(c.sum, echte);
});

test("Die Ausschlussgründe sind der feste Satz", () => {
  // Die Methodik-Seite zählt über `beteiligung` und `kein_mandat`. Ein Grund
  // in Prosa fiele in core.js stillschweigend auf „abwesend“ durch.
  const erlaubt = new Set(["beteiligung", "enthaltung", "nicht_stimmberechtigt",
                           "kein_mandat", "kurz_abwesend"]);
  const fremd = d.votes.flatMap(v => (v.excluded || [])
    .filter(e => !erlaubt.has(e.reason))
    .map(e => v.id + ": " + e.reason));
  assert.deepEqual(fremd, []);
});

test("Jede Abstimmung gehört zu einer Sitzung, die stattgefunden hat", () => {
  const gehalten = new Set(d.sessionRegister().map(s => s.id));
  const fremd = d.votes.filter(v => !gehalten.has(v.sessionId));
  assert.deepEqual(fremd.map(v => v.id), []);
});
