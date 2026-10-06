// Prüft das Ähnlichkeitsmaß aus js/views/naehe.js an erfundenen Daten:
// Dämpfung, Mindestzahl, einstimmige Beschlüsse, Gelegenheit, Sitzwechsel.
//
// Die Views greifen beim Laden auf das Dokument zu und daten.js holt die
// Dateien per fetch. Beides wird hier ersetzt, damit das Maß ohne Browser
// prüfbar ist. Mit dem Schnitt aus AP 5 (Maß getrennt vom Zeichnen) fällt
// der Ersatz für das Dokument weg.

import { test, before } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const K = 5;      // SIM_K in naehe.js
let similarity, simScore;

const KNOTEN = {
  classList: { toggle() {}, add() {}, remove() {}, contains: () => false },
  addEventListener() {}, setAttribute() {}, removeAttribute() {},
  appendChild() {}, querySelector: () => null, querySelectorAll: () => [],
  innerHTML: "", textContent: "", dataset: {}, style: {},
};

// Zwei Fraktionen, vier Personen: a und b stimmen zusammen, c dagegen.
// d rückt für a nach.
const mandat = (party, from, to) =>
  [to ? { from, to, party, role: "councillor" } : { from, party, role: "councillor" }];

const MITGLIEDER = [
  { id: "a", firstName: "A", lastName: "Eins", mandates: mandat("csu", "2020-05-01", "2023-06-30") },
  { id: "b", firstName: "B", lastName: "Zwei", mandates: mandat("csu", "2020-05-01") },
  { id: "c", firstName: "C", lastName: "Drei", mandates: mandat("spd", "2020-05-01") },
  { id: "d", firstName: "D", lastName: "Vier", mandates: mandat("csu", "2023-07-01"),
    succeeds: ["a"] },
];

// Jedes Votum braucht seine eigene Sitzung: das Datum steht seit AP 4 dort,
// und daten.js heftet es beim Laden an die Abstimmung.
const SITZUNGEN = [];
const votum = (id, date, yes, no, stimmen) => {
  const sessionId = "s_" + date.replace(/-/g, "");
  if (!SITZUNGEN.some(s => s.id === sessionId)) {
    SITZUNGEN.push({ id: sessionId, date, type: "stadtrat",
                     niederschrift: "vollständig", agenda: [] });
  }
  return {
    id, sessionId, type: "anonymous", results: { yes, no },
    source: { tier: "tracked" },
    voters: Object.fromEntries(Object.entries(stimmen).map(([k, v]) => [k, { vote: v }])),
  };
};

const VOTEN = [
  // Vier geteilte Beschlüsse: a und b immer gleich, c immer dagegen.
  votum("v1", "2021-01-01", 2, 1, { a: "yes", b: "yes", c: "no" }),
  votum("v2", "2021-02-01", 2, 1, { a: "yes", b: "yes", c: "no" }),
  votum("v3", "2021-03-01", 1, 2, { a: "no", b: "no", c: "yes" }),
  votum("v4", "2021-04-01", 2, 1, { a: "yes", b: "yes", c: "no" }),
  // Einstimmig: trägt keine Information und zählt gar nicht mit.
  votum("v5", "2021-05-01", 3, 0, { a: "yes", b: "yes", c: "yes" }),
  // Nach a's Austritt: d und b stimmen gleich, c dagegen.
  votum("v6", "2023-09-01", 2, 1, { b: "yes", d: "yes", c: "no" }),
  votum("v7", "2023-10-01", 2, 1, { b: "yes", d: "yes", c: "no" }),
];

const BESTAND = {
  "data/topics.json": [],
  "data/sessions.json": SITZUNGEN,
  "data/votes.json": VOTEN,
  "data/tags.json": [],
  "data/members.json": MITGLIEDER,
  "data/parties.json": {
    parties: [{ id: "csu", name: "CSU", color: "#111" },
              { id: "spd", name: "SPD", color: "#222" }],
    seatOrder: ["csu", "spd"],
  },
  "data/bodies.json": [],
  "data/media.json": [],
  "data/press.json": [],
};

before(async () => {
  globalThis.document = {
    getElementById: () => KNOTEN, querySelector: () => KNOTEN,
    querySelectorAll: () => [], createElement: () => ({ ...KNOTEN }),
    addEventListener() {}, body: KNOTEN, documentElement: KNOTEN,
  };
  globalThis.window = {
    location: { hash: "" }, addEventListener() {}, history: { length: 1 },
    innerWidth: 1440, matchMedia: () => ({ matches: false, addEventListener() {} }),
  };
  globalThis.localStorage = { getItem: () => null, setItem() {} };

  const quelle = readFileSync(new URL("../js/core.js", import.meta.url), "utf8");
  globalThis.Council = new Function(quelle + "\nreturn Council;")();

  globalThis.fetch = async (pfad) => ({
    ok: true, status: 200, json: async () => BESTAND[pfad],
  });

  const daten = await import("../js/daten.js");
  await daten.ladeDaten();
  const naehe = await import("../js/views/naehe.js");
  naehe.initNaehe();
  similarity = naehe.similarity;
  simScore = naehe.simScore;
});

test("Nur geteilte Beschlüsse zählen, einstimmige nicht", () => {
  const p = similarity("p2020");
  assert.equal(p["a|b"].n, 4, "v5 war einstimmig und bleibt draußen");
});

test("Gleiche Stimme zählt +1, verschiedene −1", () => {
  const p = similarity("p2020");
  assert.equal(p["a|b"].raw, 4);
  assert.equal(p["a|c"].raw, -4);
});

test("Die Summe wird durch (Vergleiche + 5) gedämpft", () => {
  const p = similarity("p2020");
  assert.equal(simScore(p, "a", "b").s, 4 / (4 + K));
  assert.equal(simScore(p, "a", "c").s, -4 / (4 + K));
});

test("Unter zwei Vergleichen gibt es kein Ergebnis", () => {
  const p = similarity("p2020");
  assert.equal(simScore(p, "d", "c") && simScore(p, "d", "c").n, 2);
  const duenn = { "x|y": { n: 1, raw: 1, joint: 1 } };
  assert.equal(simScore(duenn, "x", "y"), null);
});

test("Gelegenheit zählt die geteilten Beschlüsse, bei denen beide dasaßen", () => {
  const p = similarity("p2020");
  assert.equal(p["a|b"].joint, 4, "einstimmige Beschlüsse zählen auch im Nenner nicht");
  assert.equal(p["b|d"].joint, 2, "erst ab v6 saßen beide im Rat");
});

test("Vorgänger und Nachfolger auf einem Sitz werden nicht verglichen", () => {
  const p = similarity("p2020");
  assert.equal(p["a|d"], undefined, "d steht mit succeeds: [\"a\"] im Datensatz");
});

test("Jede Wahlperiode wird für sich gerechnet", () => {
  const p = similarity("p2026");
  assert.deepEqual(Object.keys(p), [], "in der neuen Periode liegt noch nichts vor");
});
