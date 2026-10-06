// Prüft js/core.js: Perioden, Gremienbesetzung, Vote-Status, Herkunft.
// Läuft mit `node --test tests/`, ohne Abhängigkeit.
//
// core.js ist ein klassisches Skript mit der Globalen `Council`. Bis es ein
// ES-Modul ist, wird es hier ausgewertet statt importiert.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const quelle = readFileSync(new URL("../js/core.js", import.meta.url), "utf8");
const Council = new Function(quelle + "\nreturn Council;")();

const anon = (yes, no, extra = {}) => ({
  id: "v1", date: "2023-07-24", sessionId: "s1", type: "anonymous",
  results: { yes, no }, ...extra,
});
const named = (yes, no, absent = [], extra = {}) => ({
  id: "v1", date: "2023-07-24", sessionId: "s1", type: "named",
  results: { yes, no, absent }, ...extra,
});

test("Zeitraum: beide Enden zählen mit, fehlende Grenze ist offen", () => {
  assert.equal(Council.withinPeriod({ from: "2020-05-01", to: "2026-04-30" }, "2020-05-01"), true);
  assert.equal(Council.withinPeriod({ from: "2020-05-01", to: "2026-04-30" }, "2026-04-30"), true);
  assert.equal(Council.withinPeriod({ from: "2020-05-01", to: "2026-04-30" }, "2026-05-01"), false);
  assert.equal(Council.withinPeriod({ from: "2020-05-01" }, "2099-01-01"), true);
  assert.equal(Council.withinPeriod({ to: "2020-05-01" }, "1999-01-01"), true);
});

test("Monatsangabe als Ende reicht bis zum Monatsletzten", () => {
  assert.equal(Council.endOfPeriod("2024-10"), "2024-10-99");
  assert.equal(Council.endOfPeriod("2024-10-15"), "2024-10-15");
  assert.equal(Council.withinPeriod({ to: "2024-10" }, "2024-10-31"), true);
  assert.equal(Council.withinPeriod({ to: "2024-10" }, "2024-11-01"), false);
});

test("Mandat: einfacher Zeitraum", () => {
  const m = { id: "a", from: "2020-05-01", to: "2026-04-30" };
  assert.equal(Council.memberActiveAt(m, "2023-07-24"), true);
  assert.equal(Council.memberActiveAt(m, "2020-04-30"), false);
  assert.equal(Council.memberActiveAt(m, "2026-05-02"), false);
});

test("Mandat: zwei getrennte Perioden, die Lücke dazwischen zählt nicht", () => {
  const m = { id: "marschoun", from: "2014-05-01", periods: [
    { from: "2014-05-01", to: "2020-04-30" },
    { from: "2026-05-01" },
  ] };
  assert.equal(Council.memberActiveAt(m, "2015-01-01"), true);
  assert.equal(Council.memberActiveAt(m, "2023-07-24"), false);
  assert.equal(Council.memberActiveAt(m, "2026-06-01"), true);
});

const bpu = {
  id: "bpu",
  seatConfigs: [
    { from: "2020-05-01", to: "2026-04-30",
      chair: "dollinger",
      vicechairs: [{ member: "hadersdorfer", sub: "heinz" }],
      seats: [
        { member: "kieninger", sub: "becher_j" },
        { occupants: [{ member: "john", to: "2023-07-23" },
                      { member: "strobl", from: "2023-07-24" }] },
      ] },
    { from: "2026-05-01", chair: "dollinger", seats: [{ member: "gruber" }] },
  ],
};

test("Gremium: die Besetzung zum Datum, außerhalb aller Perioden keine", () => {
  assert.equal(Council.bodyConfigAt(bpu, "2023-07-24").from, "2020-05-01");
  assert.equal(Council.bodyConfigAt(bpu, "2026-06-01").from, "2026-05-01");
  assert.deepEqual(Council.bodyConfigAt(bpu, "2019-01-01"), {});
});

test("Gremium ohne Perioden trägt seine Besetzung direkt", () => {
  const rat = { id: "aufsichtsrat", seats: [{ member: "gruber" }] };
  assert.equal(Council.bodyConfigAt(rat, "2023-07-24"), rat);
});

test("Stammsitz: Vorsitz, Stellvertretung und Sitz zählen, Vertretung nicht", () => {
  const am = d => id => Council.isRegularOf({ id }, bpu, d);
  const bei = am("2023-07-24");
  assert.equal(bei("dollinger"), true);
  assert.equal(bei("hadersdorfer"), true);
  assert.equal(bei("kieninger"), true);
  assert.equal(bei("heinz"), false, "Stellvertreter ist kein Stammsitz");
  assert.equal(bei("becher_j"), false);
});

test("Stammsitz wechselt mit der Nachfolge auf dem Sitz", () => {
  assert.equal(Council.isRegularOf({ id: "john" }, bpu, "2023-07-23"), true);
  assert.equal(Council.isRegularOf({ id: "john" }, bpu, "2023-07-24"), false);
  assert.equal(Council.isRegularOf({ id: "strobl" }, bpu, "2023-07-23"), false);
  assert.equal(Council.isRegularOf({ id: "strobl" }, bpu, "2023-07-24"), true);
});

test("Ohne Mandat am Abstimmungstag gibt es keinen Status", () => {
  const m = { id: "a", from: "2026-05-01" };
  assert.equal(Council.voteStatus("a", anon(10, 0), null, m), null);
});

test("Befangenheit geht der Sitzungsabwesenheit vor", () => {
  const session = { absent: ["a"] };
  const v = anon(10, 0, { excluded: [{ member: "a", reason: "beteiligung" }] });
  assert.equal(Council.voteStatus("a", v, session, null), "excluded");
});

test("Die Gründe der Ausschlussliste führen auf eigene Status", () => {
  const fall = reason =>
    Council.voteStatus("a", anon(10, 0, { excluded: [{ member: "a", reason }] }), null, null);
  assert.equal(fall("beteiligung"), "excluded");
  assert.equal(fall("enthaltung"), "abstained");
  assert.equal(fall("nicht_stimmberechtigt"), "restricted");
  assert.equal(fall("kein_mandat"), "restricted");
  assert.equal(fall("kurz_abwesend"), "absent");
  assert.equal(fall("kurz_weg"), "absent", "unbekannter Grund heißt abwesend");
});

test("Abwesend laut Sitzung", () => {
  assert.equal(Council.voteStatus("a", anon(10, 0), { absent: ["a"] }, null), "absent");
});

test("Namentliche Abstimmung liest aus den Listen", () => {
  const v = named(["a"], ["b"], ["c"]);
  assert.equal(Council.voteStatus("a", v, null, null), "yes");
  assert.equal(Council.voteStatus("b", v, null, null), "no");
  assert.equal(Council.voteStatus("c", v, null, null), "absent");
  assert.equal(Council.voteStatus("d", v, null, null), null, "nicht genannt heißt nicht im Rat");
});

test("Einzelstimme am anonymen Votum schlägt die Ableitung", () => {
  const v = anon(10, 2, { voters: { a: { vote: "no" } } });
  assert.equal(Council.voteStatus("a", v, null, null), "no");
});

test("Ein voters-Eintrag ohne Stimme trägt nur die Herkunft", () => {
  const v = anon(20, 0, { voters: { a: { tiers: ["selbstauskunft"], by: "a" } } });
  assert.equal(Council.voteStatus("a", v, null, null), "yes-inferred",
    "die Ableitung gilt weiter");
  assert.deepEqual(Council.voterTiers(v, "a"), ["selbstauskunft"]);
});

test("Kurze Abwesenheit am Votum selbst", () => {
  const v = anon(10, 0, { results: { yes: 10, no: 0, absent_ids: ["a"] } });
  assert.equal(Council.voteStatus("a", v, null, null), "absent");
});

test("Einstimmig anonym wird abgeleitet, geteilt nicht", () => {
  assert.equal(Council.voteStatus("a", anon(20, 0), null, null), "yes-inferred");
  assert.equal(Council.voteStatus("a", anon(0, 20), null, null), "no-inferred");
  assert.equal(Council.voteStatus("a", anon(12, 8), null, null), "unknown");
});

test("inferable: false unterbindet die Ableitung", () => {
  assert.equal(Council.voteStatus("a", anon(20, 0, { inferable: false }), null, null), "unknown");
});

test("inferable: teilweise lässt nur die Teilanwesenden offen", () => {
  const v = anon(20, 0, { inferable: "teilweise" });
  const session = { partial: [{ member: "a", note: "kam später" }] };
  assert.equal(Council.voteStatus("a", v, session, null), "unknown");
  assert.equal(Council.voteStatus("b", v, session, null), "yes-inferred");
});

test("Einstimmigkeit, namentlich wie anonym", () => {
  assert.equal(Council.isUnanimous(anon(20, 0)), true);
  assert.equal(Council.isUnanimous(anon(12, 8)), false);
  assert.equal(Council.isUnanimous(named(["a", "b"], [])), true);
  assert.equal(Council.isUnanimous(named(["a"], ["b"])), false);
});

test("Kurzlabel, mit und ohne Stern", () => {
  assert.equal(Council.voteStatusLabel("yes"), "Ja");
  assert.equal(Council.voteStatusLabel("yes-inferred"), "Ja");
  assert.equal(Council.voteStatusLabel("yes-inferred", true), "Ja*");
  assert.equal(Council.voteStatusLabel("absent"), "–");
  assert.equal(Council.voteStatusLabel(null), "");
});

test("Herkunft: Stufe des Votums, Einzelbeleg schlägt sie", () => {
  const v = anon(12, 8, {
    source: { tier: "press" },
    voters: { a: { vote: "no", tiers: ["tracked", "selbstauskunft"] } },
  });
  assert.deepEqual(Council.voterTiers(v, "b"), ["press"]);
  assert.deepEqual(Council.voterTiers(v, "a"), ["tracked", "selbstauskunft"],
    "stärkster Beleg zuerst");
  assert.equal(Council.sourceLabel(v), "Aus Presseberichten");
  assert.equal(Council.sourceLabel(v, "a"), "In der Sitzung mitgeschrieben");
});

test("Weicher Beleg wird benannt, nicht als Stimme ausgegeben", () => {
  const v = anon(12, 8, { source: { tier: "press" },
                          voters: { a: { vote: "no", evidence: "soft" } } });
  assert.match(Council.evidenceNote(v, "a"), /Wortmeldung/);
  assert.equal(Council.evidenceNote(v, "b"), null);
  assert.match(Council.statusProvenance("no", v, "a"), /^Nein - aus einer Wortmeldung/);
});

test("Abgeleitet aus der Niederschrift sagt die Herkunft nicht zweimal", () => {
  const v = anon(20, 0, { source: { tier: "protocol-implicit" } });
  assert.equal(Council.statusProvenance("yes-inferred", v, "a"),
    "Ja - aus öff. Niederschrift abgeleitet");
});

test("Nur das Ergebnis bekannt: die Stufe steht da, zu benennen gibt es nichts", () => {
  const v = anon(12, 8, { source: { tier: "result-only" } });
  assert.deepEqual(Council.voterTiers(v, "a"), ["result-only"]);
  assert.equal(Council.sourceLabel(v), null,
    "views/voten.js setzt dort seinen eigenen Satz");
  assert.equal(Council.statusProvenance("unknown", v, "a"), "Nicht überliefert");
});
