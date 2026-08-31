// Abstimmungsähnlichkeit: das Paar-Maß über geteilte Beschlüsse, die
// Profil-Rubrik "Wer ähnlich stimmt" sowie Nähe-Matrix und Nähe-Netz.
import {
  members, votes, memberMap, partyMap, seatOrder, sessionMap,
} from "../daten.js";
import { navigate } from "../routing.js";

// -- Abstimmungsähnlichkeit --
//
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

// Endet ein Mandat an dem Tag, an dem ein anderes beginnt, teilen sich die
// beiden einen Sitz: bis zum Wechselbeschluss stimmt der Alte, danach der
// Neue. Gemeinsam abgestimmt haben sie nie — auch nicht an diesem einen Tag.
const seatSwap = new Set();

// Ehemals frei laufende Verdrahtung aus app.js, unverändert.
export function initNaehe() {
  members.forEach(a => members.forEach(b => {
    if (a === b) return;
    const pa = a.periods && a.periods.length ? a.periods : [{ from: a.from, to: a.to }];
    const pb = b.periods && b.periods.length ? b.periods : [{ from: b.from, to: b.to }];
    if (pa.some(x => x.to && pb.some(y => y.from === x.to)))
      seatSwap.add(a.id < b.id ? a.id + "|" + b.id : b.id + "|" + a.id);
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

function renderSimilarity(m) {
  // Die jüngste Periode, in der diese Person genug Vergleiche hat. Für
  // amtierende Mitglieder ist die laufende Periode noch zu dünn — dann steht
  // hier die vorige, mit Jahreszahl, statt gar nichts.
  let per = null, list = [];
  for (let i = PERIODS.length - 1; i >= 0; i--) {
    const p = PERIODS[i];
    if (simThin(p.id)) continue;
    const l = similarFor(m.id, p.id);
    if (l.length >= 4) { per = p; list = l; break; }
  }
  if (!per) return null;
  const top = list.slice(0, 3);
  const bottom = list.slice(-3).reverse();

  const line = e => {
    const o = memberMap[e.other];
    const p = o && partyMap[o.party];
    const pct = Math.round(Math.abs(e.score) * 100);
    return `<a class="sim-row" href="#/member/${e.other}">
      <span class="member-dot" style="background:${p ? p.color : "#ccc"}"></span>
      <span class="sim-name">${o ? o.name : e.other}</span>
      <span class="sim-bar"><span style="width:${pct}%;background:${e.score >= 0 ? "var(--yes)" : "var(--no)"}"></span></span>
      <span class="sim-val">${e.score >= 0 ? "+" : "−"}${pct}</span>
      <span class="sim-n" title="${e.n} von ${e.joint} gemeinsamen geteilten Beschlüssen">${e.n}<i>/${e.joint}</i></span></a>`;
  };

  const box = document.createElement("details");
  box.className = "profile-section sim-box";
  box.innerHTML = `
    <summary>Wer ähnlich stimmt <span class="sim-period">${per.label}</span></summary>
    <p class="sim-note">Nur geteilte Abstimmungen, bei denen von beiden eine Stimme
      bekannt ist. Die letzte Spalte nennt die Zahl dieser Vergleiche und dahinter,
      bei wie vielen geteilten Beschlüssen beide überhaupt im Saal saßen — je
      weiter die zwei Zahlen auseinanderliegen, desto vorsichtiger ist der Wert
      zu lesen.</p>
    <div class="sim-group">Stimmt am ehesten mit</div>${top.map(line).join("")}
    <div class="sim-group">Stimmt am seltensten mit</div>${bottom.map(line).join("")}`;
  return box;
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

function partyAtDate(m, date) {
  const h = m.partyHistory;
  if (!h || !h.length) return m.party;
  const at = h.find(p => (p.from || "0") <= date && (!p.to || p.to > date));
  return at ? at.party : m.party;
}

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

// Grün = stimmt zusammen, Rot = stimmt gegeneinander, Grau = zu wenig Daten
function simColor(s, max) {
  const a = Math.min(1, Math.abs(s) / max);
  return s >= 0 ? `rgba(79,138,22,${0.12 + a * 0.8})` : `rgba(155,0,0,${0.12 + a * 0.8})`;
}

function drawSimMatrix(el, periodId) {
  const nodes = simNodes(periodId);
  const pairs = similarity(periodId);
  if (nodes.length < 3) {
    el.innerHTML = '<p class="chart-foot">Für diese Wahlperiode liegen noch zu wenige Einzelstimmen vor.</p>';
    return;
  }
  const W = el.clientWidth || 640;
  const spread = simSpread(pairs);
  // Zeilennamen links, dieselben Namen gekippt an der Unterkante als
  // Spaltenbeschriftung. Die Hypotenuse bleibt frei.
  const label = 92, foot = 78;
  const cell = Math.max(9, Math.min(22, (W - label - 4) / nodes.length));
  const size = cell * nodes.length;

  let cells = "", ticks = "";
  nodes.forEach((a, i) => {
    const color = a.party ? a.party.color : "#999";
    ticks += `<text class="hm-name" x="${label - 6}" y="${i * cell + cell / 2 + 3}"
                text-anchor="end" fill="${color}">${a.m.lastName}</text>`
           + `<text class="hm-name" text-anchor="end" fill="${color}"
                transform="rotate(-90 ${label + i * cell + cell / 2 + 3} ${size + 6})"
                x="${label + i * cell + cell / 2 + 3}" y="${size + 6}">${a.m.lastName}</text>`;

    // Nur die untere Hälfte: die obere sagte dasselbe noch einmal
    for (let j = 0; j < i; j++) {
      const b = nodes[j];
      const p = pairs[a.m.id < b.m.id ? a.m.id + "|" + b.m.id : b.m.id + "|" + a.m.id];
      const r = simScore(pairs, a.m.id, b.m.id);
      const never = !p || !p.joint;
      const x = label + j * cell, y = i * cell;
      const fill = r ? simColor(r.s, spread) : never ? "url(#hm-gap-hatch)" : "var(--bg)";
      const title = r
        ? `${a.m.name} / ${b.m.name}: ${r.s >= 0 ? "+" : "−"}${Math.round(Math.abs(r.s) * 100)} `
          + `aus ${r.n} bekannten von ${r.joint} gemeinsamen Beschlüssen`
        : never
          ? `${a.m.name} / ${b.m.name}: saßen nie gleichzeitig im Rat`
          : `${a.m.name} / ${b.m.name}: nur ${(p && p.n) || 0} von ${p.joint} gemeinsamen Beschlüssen bekannt`;
      cells += `<rect x="${x}" y="${y}" width="${cell}" height="${cell}"
                  ${never ? 'class="hm-gap" ' : ""}fill="${fill}"><title>${title}</title></rect>`;
    }
  });

  // In der leeren Hälfte spiegelt je Fraktion ein Winkel ihren eigenen Block
  // an der Diagonale. Wo viel Grün in einem Winkel steckt, hält die Fraktion
  // zusammen — das sieht man, ohne die Namen zu lesen.
  let frames = "";
  let s0 = 0;
  nodes.forEach((n, i) => {
    const last = i === nodes.length - 1;
    const pid = n.party ? n.party.id : "";
    const next = last ? null : (nodes[i + 1].party ? nodes[i + 1].party.id : "");
    if (!last && next === pid) return;
    if (i > s0) {                       // Einerfraktionen haben keinen Block
      const x0 = label + s0 * cell, x1 = label + (i + 1) * cell;
      const y0 = s0 * cell, y1 = (i + 1) * cell;
      frames += `<path class="hm-frame" d="M${x0} ${y0} H${x1} V${y1}"
                   stroke="${n.party ? n.party.color : "#999"}"/>`
              + `<text class="hm-frame-label" x="${x1 - 3}" y="${y0 - 4}"
                   text-anchor="end" fill="${n.party ? n.party.color : "#999"}"
                 >${n.party ? n.party.name : ""}</text>`;
    }
    s0 = i + 1;
  });

  const defs = `<defs><pattern id="hm-gap-hatch" width="5" height="5"
      patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect width="5" height="5" fill="#fff"/>
      <rect width="2.2" height="5" fill="var(--accent)" opacity="0.7"/>
    </pattern></defs>`;
  el.innerHTML = `<svg class="chart heatmap" width="${label + size}" height="${size + foot}"
      viewBox="0 0 ${label + size} ${size + foot}" role="img" aria-label="Ähnlichkeitsmatrix">
      ${defs}${cells}${frames}${ticks}</svg>`
    + `<div class="hm-legend">
         <span><i class="hm-key-scale"></i>stimmt gegeneinander … zusammen</span>
         <span><i class="hm-key-gap"></i>saßen nie gleichzeitig im Rat</span>
         <span><i class="hm-key-none"></i>zu wenig bekannt</span>
         <span><i class="hm-key-frame"></i>Fraktionsblock, an der Diagonale gespiegelt</span>
       </div>`;
}

// Kräftebasierte Anordnung, Fruchterman-Reingold. Positive Nähe zieht
// zusammen, negative drückt auseinander. Kein Schwellenwert: schwache Kanten
// verschwinden über die Deckkraft, nicht über einen Filter.
function drawSimGraph(el, periodId) {
  const nodes = simNodes(periodId).map(n => ({ ...n, x: 0, y: 0, dx: 0, dy: 0 }));
  const pairs = similarity(periodId);
  if (nodes.length < 3) {
    el.innerHTML = '<p class="chart-foot">Für diese Wahlperiode liegen noch zu wenige Einzelstimmen vor.</p>';
    return;
  }
  const idx = {};
  nodes.forEach((n, i) => { idx[n.m.id] = i; });
  const edges = [];
  Object.entries(pairs).forEach(([k, p]) => {
    if (p.n < SIM_MIN) return;
    const [a, b] = k.split("|");
    if (!(a in idx) || !(b in idx)) return;
    edges.push({ a: nodes[idx[a]], b: nodes[idx[b]], s: p.raw / (p.n + SIM_K), n: p.n });
  });

  // Zwei Knoten auf demselben Punkt haben keine Richtung, in die man sie
  // schieben könnte — dx/d wäre null. Dann gibt der Index eine her, immer
  // dieselbe, damit das Bild reproduzierbar bleibt.
  const apart = (a, b, i, j) => {
    const dx = a.x - b.x, dy = a.y - b.y;
    const d = Math.hypot(dx, dy);
    if (d > 1e-6) return [dx, dy, d];
    const t = ((i * 7 + j * 13) % 360) * Math.PI / 180;
    return [Math.cos(t), Math.sin(t), 1];
  };

  const W = el.clientWidth || 640, H = 420;
  nodes.forEach((n, i) => {
    const a = 2 * Math.PI * i / nodes.length;
    n.x = W / 2 + Math.cos(a) * W / 5;
    n.y = H / 2 + Math.sin(a) * H / 5;
  });
  const k = Math.sqrt(W * H / nodes.length) * 0.55;
  const STEPS = 400;
  for (let it = 0; it < STEPS; it++) {
    const temp = (1 - it / STEPS) * k * 0.4;
    nodes.forEach(n => { n.dx = 0; n.dy = 0; });
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const [dx, dy, d] = apart(nodes[i], nodes[j], i, j);
        const f = k * k / d;
        nodes[i].dx += dx / d * f; nodes[i].dy += dy / d * f;
        nodes[j].dx -= dx / d * f; nodes[j].dy -= dy / d * f;
      }
    }
    edges.forEach(e => {
      const dx = e.a.x - e.b.x, dy = e.a.y - e.b.y;
      const d = Math.hypot(dx, dy) || 0.01;
      const f = e.s * d * d / k;
      e.a.dx -= dx / d * f; e.a.dy -= dy / d * f;
      e.b.dx += dx / d * f; e.b.dy += dy / d * f;
    });
    nodes.forEach(n => {
      const d = Math.hypot(n.dx, n.dy) || 0.01;
      n.x = Math.max(28, Math.min(W - 28, n.x + n.dx / d * Math.min(d, temp)));
      n.y = Math.max(22, Math.min(H - 22, n.y + n.dy / d * Math.min(d, temp)));
    });
  }

  // Die Kräfte allein schieben Knoten übereinander, sobald eine Fraktion eng
  // zusammenhält. Ein paar Entzerrungsschritte am Ende drücken sie auf
  // Lesbarkeitsabstand, ohne die Anordnung zu verwerfen.
  const MIN = 26;
  for (let it = 0; it < 240; it++) {
    let moved = false;
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i], b = nodes[j];
        const [dx, dy, d] = apart(a, b, i, j);
        if (d >= MIN) continue;
        const push = (MIN - d) / 2;
        a.x += dx / d * push; a.y += dy / d * push;
        b.x -= dx / d * push; b.y -= dy / d * push;
        moved = true;
      }
    }
    nodes.forEach(n => {
      n.x = Math.max(28, Math.min(W - 28, n.x));
      n.y = Math.max(22, Math.min(H - 22, n.y));
    });
    if (!moved) break;
  }

  const spread = simSpread(pairs);
  const lines = edges
    .slice().sort((p, q) => Math.abs(p.s) - Math.abs(q.s))
    .map(e => {
      const a = Math.min(1, Math.abs(e.s) / spread);
      return `<line x1="${e.a.x.toFixed(1)}" y1="${e.a.y.toFixed(1)}"
               x2="${e.b.x.toFixed(1)}" y2="${e.b.y.toFixed(1)}"
               stroke="${e.s >= 0 ? "#4F8A16" : "#9B0000"}"
               stroke-opacity="${(a * a * 0.5).toFixed(3)}"
               stroke-width="${(0.4 + a * 2).toFixed(2)}"/>`;
    }).join("");
  const dots = nodes.map(n => `
    <g class="sg-node" transform="translate(${n.x.toFixed(1)},${n.y.toFixed(1)})">
      <circle r="7" fill="${n.party ? n.party.color : "#999"}"/>
      <text y="-11" text-anchor="middle">${n.m.lastName}</text>
      <title>${n.m.name}${n.party ? " · " + n.party.name : ""}</title>
    </g>`).join("");

  el.innerHTML = `<svg class="chart simgraph" width="${W}" height="${H}"
      viewBox="0 0 ${W} ${H}" role="img" aria-label="Nähe-Netz">${lines}${dots}</svg>`;
  el.querySelectorAll(".sg-node").forEach((g, i) => {
    g.addEventListener("click", () => navigate("/member/" + nodes[i].m.id));
  });
}

export { PERIODS, stances, partyAtDate, renderSimilarity, drawSimMatrix, drawSimGraph };
