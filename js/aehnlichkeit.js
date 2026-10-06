// Das Abstimmungs-Ähnlichkeitsmaß: wie oft haben zwei Personen bei geteilten
// Beschlüssen gleich gestimmt. Gezeichnet wird das in views/naehe.js; hier
// steht nur gerechnet, damit es ohne Browser prüfbar bleibt.
import {
  members, votes, memberMap, partyMap, seatOrder, sessionMap,
} from "./daten.js";
import { Council } from "./core.js";

// Verglichen wird nur, wo der Rat geteilt war: bei einstimmigen Beschlüssen
// stimmen alle gleich, das trägt keine Information. Je Paar und geteiltem
// Votum, bei dem von beiden eine Stimme bekannt ist: +1 gleich, −1 ungleich.
// Fehlt von einer Seite die Stimme — abwesend, befangen, unbekannt — zählt
// das Votum gar nicht.
//
// Die Summe wird nicht durch n geteilt, sondern durch (n + K). Damit zieht
// eine dünne Grundlage das Ergebnis zur Mitte: zehn von zehn übereinstimmenden
// Stimmen ergeben 0,67, fünf von fünf nur 0,50. Genau das ist gewollt —
// Abwesenheit schwächt das Maß, statt es zu verzerren.
const SIM_K = 5;
// Eine einzige gemeinsame Abstimmung ist ein Münzwurf, ab zweien zeigt sich
// ein Muster. Höher muss die Schwelle nicht sein: die Dämpfung durch (n + K)
// hält dünne Paare ohnehin in der Mitte — vier übereinstimmende Stimmen
// ergeben 0,44, während die dichten Paare 0,83 erreichen.
const SIM_MIN = 2;

// Verglichen wird immer innerhalb einer Wahlperiode — über den Wechsel hinweg
// säßen Personen im selben Bild, die nie zusammen abgestimmt haben.
const PERIODS = [
  { id: "p2020", label: "2020–2026", from: "2020-05-01", to: "2026-04-30" },
  { id: "p2026", label: "seit 2026", from: "2026-05-01", to: "9999-12-31" },
];
const periodOf = date => PERIODS.find(p => date >= p.from && date <= p.to);

// Wer bei diesem Votum eine bekannte Ja/Nein-Stimme hat. Die Auswertung geht
// über voteStatus, damit hier dieselben Regeln gelten wie in der Anzeige —
// eine Mitschrift, die jemandem eine Stimme gibt, den die Niederschrift als
// abwesend führt, zählt sonst nur in der Statistik mit.
function stances(v) {
  const session = sessionMap[v.sessionId];
  const st = {};
  members.forEach(m => {
    const s = Council.voteStatus(m.id, v, session, m);
    if (s === "yes" || s === "no") st[m.id] = s;
  });
  return st;
}

// Wer nachrückt, teilt sich den Sitz mit der Vorgängerin: bis zum
// Wechselbeschluss stimmt die eine, danach die andere. Gemeinsam abgestimmt
// haben sie nie, also wird das Paar nicht verglichen. Die Nachfolge steht als
// `succeeds` am Mitglied; vorher wurde sie aus Fraktion und Abstand geraten,
// und das traf über den Wahlwechsel hinweg jede Fraktionskollegin.
const seatSwap = new Set();
const paarKey = (a, b) => a < b ? a + "|" + b : b + "|" + a;

// Ehemals frei laufende Verdrahtung aus app.js.
function initNaehe() {
  members.forEach(m => (m.succeeds || []).forEach(vorher => {
    if (memberMap[vorher]) seatSwap.add(paarKey(m.id, vorher));
  }));
}

const simCaches = {};
const simVoteCount = {};

// Unter dieser Zahl streitiger Beschlüsse mit Einzelstimmen wird gar nichts
// gezeigt. Bei zweien bekäme jedes Paar denselben Betrag — eine Landkarte,
// die nur abbildet, welche Handvoll Beschlüsse zufällig dokumentiert ist.
const SIM_FLOOR = 10;

function similarity(periodId) {
  const per = PERIODS.find(p => p.id === periodId) || PERIODS[0];
  if (simCaches[per.id]) return simCaches[per.id];
  const pairs = {};
  let counted = 0;
  const key = (a, b) => a < b ? a + "|" + b : b + "|" + a;
  const bucket = k => pairs[k] || (pairs[k] = { n: 0, raw: 0, joint: 0 });
  votes.forEach(v => {
    if (Council.isUnanimous(v)) return;
    if (v.date < per.from || v.date > per.to) return;
    const session = sessionMap[v.sessionId];

    // Gelegenheit: beide saßen im Saal und waren stimmberechtigt. Das ist der
    // Nenner, der zeigt, wie dünn die Kenntnis ist — 19 Vergleiche aus 144
    // gemeinsamen Beschlüssen liest sich anders als 19 aus 25.
    const part = members.filter(m => {
      const s = Council.voteStatus(m.id, v, session, m);
      return s && s !== "absent" && s !== "excluded"
               && s !== "abstained" && s !== "restricted";
    }).map(m => m.id);
    for (let i = 0; i < part.length; i++)
      for (let j = i + 1; j < part.length; j++) {
        const k = key(part[i], part[j]);
        if (!seatSwap.has(k)) bucket(k).joint++;
      }

    const st = stances(v);
    const ids = Object.keys(st);
    if (ids.length > 1) counted++;
    for (let i = 0; i < ids.length; i++) {
      for (let j = i + 1; j < ids.length; j++) {
        const p = bucket(key(ids[i], ids[j]));
        p.n++;
        p.raw += st[ids[i]] === st[ids[j]] ? 1 : -1;
      }
    }
  });
  simCaches[per.id] = pairs;
  simVoteCount[per.id] = counted;
  return pairs;
}

function similarFor(id, periodId) {
  const pairs = similarity(periodId);
  const out = [];
  Object.entries(pairs).forEach(([key, p]) => {
    const [a, b] = key.split("|");
    if (a !== id && b !== id) return;
    if (p.n < SIM_MIN) return;
    out.push({ other: a === id ? b : a, n: p.n, joint: p.joint, score: p.raw / (p.n + SIM_K) });
  });
  out.sort((x, y) => y.score - x.score);
  return out;
}

// -- Nähe-Diagramme --

// Wer in dieser Periode überhaupt vergleichbar ist, nach Fraktion sortiert —
// damit die Blöcke in der Matrix den Fraktionen entsprechen.
// Zu dünn, um irgendetwas zu zeigen?
function simThin(periodId) {
  similarity(periodId);
  return (simVoteCount[periodId] || 0) < SIM_FLOOR;
}

function simNodes(periodId) {
  const per = PERIODS.find(p => p.id === periodId);
  const pairs = similarity(periodId);
  if (simThin(periodId)) return [];
  const ids = new Set();
  Object.entries(pairs).forEach(([k, p]) => {
    if (p.n >= SIM_MIN) k.split("|").forEach(i => ids.add(i));
  });
  return [...ids]
    .map(id => memberMap[id])
    .filter(Boolean)
    .map(m => ({ m, party: partyMap[partyAtDate(m, per.to === "9999-12-31" ? per.from : per.to)] }))
    .sort((a, b) => {
      const d = seatOrder.indexOf(a.party ? a.party.id : "") - seatOrder.indexOf(b.party ? b.party.id : "");
      return d || a.m.name.localeCompare(b.m.name);
    });
}

const partyAtDate = (m, date) => Council.partyAt(m, date) || m.party;

function simScore(pairs, a, b) {
  const p = pairs[a < b ? a + "|" + b : b + "|" + a];
  return p && p.n >= SIM_MIN
    ? { s: p.raw / (p.n + SIM_K), n: p.n, joint: p.joint } : null;
}

// Die Farbe reizt den tatsächlich vorkommenden Bereich aus, statt gegen eine
// feste Obergrenze zu laufen. Untergrenze 0,5, damit eine dünn besetzte
// Periode nicht drei Werte zu Vollton aufbläst.
function simSpread(pairs) {
  let max = 0.5;
  Object.values(pairs).forEach(p => {
    if (p.n >= SIM_MIN) max = Math.max(max, Math.abs(p.raw / (p.n + SIM_K)));
  });
  return max;
}

export {
  PERIODS, SIM_K, SIM_MIN,
  initNaehe, stances, similarity, similarFor, simScore, simSpread,
  simThin, simNodes, partyAtDate,
};
