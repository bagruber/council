// Nähe-Diagramme: die Rubrik "Wer ähnlich stimmt" im Profil, die Nähe-Matrix
// und das Nähe-Netz in Fläche und Raum. Das Maß selbst steht in
// js/aehnlichkeit.js.
import { memberMap, partyMap } from "../daten.js";
import { navigate } from "../routing.js";
import { html, roh } from "../html.js";
import {
  PERIODS, SIM_K, SIM_MIN, similarity, similarFor, simScore, simSpread,
  simThin, simNodes,
} from "../aehnlichkeit.js";

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
    return html`<a class="sim-row" href="#/member/${e.other}">
      <span class="member-dot" style="background:${p ? p.color : "#ccc"}"></span>
      <span class="sim-name">${o ? o.name : e.other}</span>
      <span class="sim-bar"><span style="width:${pct}%;background:${e.score >= 0 ? "var(--yes)" : "var(--no)"}"></span></span>
      <span class="sim-val">${e.score >= 0 ? "+" : "−"}${pct}</span>
      <span class="sim-n" title="${e.n} von ${e.joint} gemeinsamen geteilten Beschlüssen">${e.n}<i>/${e.joint}</i></span></a>`;
  };

  const box = document.createElement("details");
  box.className = "profile-section sim-box";
  box.innerHTML = html`
    <summary>Wer ähnlich stimmt <span class="sim-period">${per.label}</span></summary>
    <p class="sim-note">Nur geteilte Abstimmungen, bei denen von beiden eine Stimme
      bekannt ist. Die letzte Spalte nennt die Zahl dieser Vergleiche und dahinter,
      bei wie vielen geteilten Beschlüssen beide überhaupt im Saal saßen — je
      weiter die zwei Zahlen auseinanderliegen, desto vorsichtiger ist der Wert
      zu lesen.</p>
    <div class="sim-group">Stimmt am ehesten mit</div>${top.map(line)}
    <div class="sim-group">Stimmt am seltensten mit</div>${bottom.map(line)}`;
  return box;
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
    el.innerHTML = html`<p class="chart-foot">Für diese Wahlperiode liegen noch zu wenige Einzelstimmen vor.</p>`;
    return;
  }
  const W = el.clientWidth || 640;
  const spread = simSpread(pairs);
  // Zeilennamen links, dieselben Namen gekippt an der Unterkante als
  // Spaltenbeschriftung. Die Hypotenuse bleibt frei.
  const label = 92, foot = 78;
  const cell = Math.max(9, Math.min(22, (W - label - 4) / nodes.length));
  const size = cell * nodes.length;

  const cells = [], ticks = [];
  nodes.forEach((a, i) => {
    const color = a.party ? a.party.color : "#999";
    ticks.push(html`<text class="hm-name" x="${label - 6}" y="${i * cell + cell / 2 + 3}"
                text-anchor="end" fill="${color}">${a.m.lastName}</text>`,
               html`<text class="hm-name" text-anchor="end" fill="${color}"
                transform="rotate(-90 ${label + i * cell + cell / 2 + 3} ${size + 6})"
                x="${label + i * cell + cell / 2 + 3}" y="${size + 6}">${a.m.lastName}</text>`);

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
      cells.push(html`<rect x="${x}" y="${y}" width="${cell}" height="${cell}"
                  ${never ? roh('class="hm-gap" ') : ""}fill="${fill}"><title>${title}</title></rect>`);
    }
  });

  // In der leeren Hälfte spiegelt je Fraktion ein Winkel ihren eigenen Block
  // an der Diagonale. Wo viel Grün in einem Winkel steckt, hält die Fraktion
  // zusammen — das sieht man, ohne die Namen zu lesen.
  const frames = [];
  let s0 = 0;
  nodes.forEach((n, i) => {
    const last = i === nodes.length - 1;
    const pid = n.party ? n.party.id : "";
    const next = last ? null : (nodes[i + 1].party ? nodes[i + 1].party.id : "");
    if (!last && next === pid) return;
    if (i > s0) {                       // Einerfraktionen haben keinen Block
      const x0 = label + s0 * cell, x1 = label + (i + 1) * cell;
      const y0 = s0 * cell, y1 = (i + 1) * cell;
      frames.push(html`<path class="hm-frame" d="M${x0} ${y0} H${x1} V${y1}"
                   stroke="${n.party ? n.party.color : "#999"}"/>`,
                  html`<text class="hm-frame-label" x="${x1 - 3}" y="${y0 - 4}"
                   text-anchor="end" fill="${n.party ? n.party.color : "#999"}"
                 >${n.party ? n.party.name : ""}</text>`);
    }
    s0 = i + 1;
  });

  const defs = html`<defs><pattern id="hm-gap-hatch" width="5" height="5"
      patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect width="5" height="5" fill="#fff"/>
      <rect width="2.2" height="5" fill="var(--accent)" opacity="0.7"/>
    </pattern></defs>`;
  el.innerHTML = html`<svg class="chart heatmap" width="${label + size}" height="${size + foot}"
      viewBox="0 0 ${label + size} ${size + foot}" role="img" aria-label="Ähnlichkeitsmatrix">
      ${defs}${cells}${frames}${ticks}</svg><div class="hm-legend">
         <span><i class="hm-key-scale"></i>stimmt gegeneinander … zusammen</span>
         <span><i class="hm-key-gap"></i>saßen nie gleichzeitig im Rat</span>
         <span><i class="hm-key-none"></i>zu wenig bekannt</span>
         <span><i class="hm-key-frame"></i>Fraktionsblock, an der Diagonale gespiegelt</span>
       </div>`;
}

// Kräftebasierte Anordnung, Fruchterman-Reingold. Positive Nähe zieht
// zusammen, negative drückt auseinander. Kein Schwellenwert: schwache Kanten
// verschwinden über die Deckkraft, nicht über einen Filter.
// Der Knoten traegt die Initialen, nicht den Namen. Zweiunddreissig Namen
// nebeneinander ueberlagern sich, zweiunddreissig Kreise nicht. Name und
// Fraktion nennt am Rechner der Tooltip; auf dem Handy erscheint der Name nach
// dem ersten Tipp, der zweite oeffnet das Profil.
const SG_R = 13;

// Ob die letzte Eingabe eine Beruehrung war. Auf dem Handy gibt es kein
// Zeigen, also braucht der Name dort einen eigenen Schritt.
//
// Gefragt wird pointerdown, nicht touchstart: nach einer Beruehrung schickt
// der Browser zusaetzlich Maus-Ereignisse hinterher, damit alte Seiten
// funktionieren. Ein touchstart-Merker, den ein mousemove wieder loescht,
// steht beim Klick deshalb schon wieder auf falsch.
let sgFinger = false;
document.addEventListener("pointerdown",
  e => { sgFinger = e.pointerType !== "mouse"; }, { passive: true });

// Zwei Buchstaben reichen fast immer. Karin und Kilian Linz sassen zusammen im
// Rat; dort wird der Vorname zweistellig, sonst stuende zweimal "KL".
function sgInitialen(nodes) {
  // "von Pressentin" faengt klein an, die Initiale nicht.
  const gross = t => t[0].toUpperCase();
  const kurz = n => gross(n.m.firstName) + gross(n.m.lastName);
  const zahl = {};
  nodes.forEach(n => { const k = kurz(n); zahl[k] = (zahl[k] || 0) + 1; });
  return n => zahl[kurz(n)] > 1
    ? n.m.firstName.slice(0, 2) + gross(n.m.lastName)
    : kurz(n);
}

// Schrift auf der Parteifarbe: CSU-Schwarz braucht weisse Initialen, FDP-Gelb
// schwarze. Gerechnet wird der Kontrast zu beiden Kandidaten, und der
// groessere gewinnt -- eine feste Helligkeitsschwelle liegt sonst leicht
// daneben. Bei Gruenen-Gruen etwa traegt Schwarz doppelt so weit wie Weiss.
function sgSchrift(hex) {
  const [r, g, b] = [1, 3, 5]
    .map(i => parseInt(hex.slice(i, i + 2), 16) / 255)
    .map(c => c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
  const L = 0.2126 * r + 0.7152 * g + 0.0722 * b;
  const aufWeiss = 1.05 / (L + 0.05);
  const aufDunkel = (L + 0.05) / (0.0114 + 0.05);   // #1c1c1c
  return aufWeiss > aufDunkel ? "#fff" : "#1c1c1c";
}

function sgFlach(nodes, edges, W, H) {
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
        n.x = Math.max(SG_R + 6, Math.min(W - SG_R - 6, n.x + n.dx / d * Math.min(d, temp)));
        n.y = Math.max(SG_R + 14, Math.min(H - SG_R - 6, n.y + n.dy / d * Math.min(d, temp)));
      });
    }

    // Die Kräfte allein schieben Knoten übereinander, sobald eine Fraktion eng
    // zusammenhält. Ein paar Entzerrungsschritte am Ende drücken sie auf
    // Lesbarkeitsabstand, ohne die Anordnung zu verwerfen.
    // Gerade so viel, dass sich die Kreise nicht ueberlappen. Jeder Pixel mehr
    // verschiebt das Bild gegen die Kraefte, die es eigentlich zeigen soll.
    const MIN = SG_R * 2;
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
        n.x = Math.max(SG_R + 6, Math.min(W - SG_R - 6, n.x));
        n.y = Math.max(SG_R + 14, Math.min(H - SG_R - 6, n.y));
      });
      if (!moved) break;
    }
}

// -- Das Netz im Raum, ein Versuch --
//
// Im Raum nicht das Kräftespiel der Fläche, sondern Stress-Minimierung (MDS):
// Jedes Paar bekommt als Sollabstand seine Unähnlichkeit, 1 − Nähe, und die
// Anordnung sucht die Lage, die diese Abstände am besten trifft. Die Kräfte
// verteilen die Knoten von sich aus gleichmäßig. In der Kugel, ohne Wände,
// wurde daraus ein gleichförmiger Ball, der wenig über die Nähe sagte.
//
// Bei dreißig Leuten trägt die dritte Achse oft wenig, deshalb bleibt die
// Fläche die Vorgabe.
let sgRaum = false;

// Abstand der Kamera vom Kugelmittelpunkt, in Kugelradien. Näher heißt mehr
// Perspektive: vorne bis zu D/(D-1) mal so groß wie in der Mitte.
const SG_D = 4;
// Pixel je Kugelradius, so dass auch die vorderste Seite ins Bild passt
const sgMass = (W, H) => (Math.min(W, H) / 2 - SG_R - 14) * (SG_D - 1) / SG_D;

function sgRaumLage(nodes, edges, MIN) {
  const N = nodes.length;
  // Start auf einer Spirale über die Kugel, damit das Bild reproduzierbar bleibt
  nodes.forEach((n, i) => {
    const y = 1 - 2 * (i + 0.5) / N, r = Math.sqrt(1 - y * y), t = i * 2.39996;
    n.p = [Math.cos(t) * r * 0.4, y * 0.4, Math.sin(t) * r * 0.4];
  });
  const apart = (a, b, i, j) => {
    const v = a.p.map((c, x) => c - b.p[x]);
    const d = Math.hypot(...v);
    if (d > 1e-6) return [v.map(c => c / d), d];
    const t = ((i * 7 + j * 13) % 360) * Math.PI / 180;
    return [[Math.cos(t), Math.sin(t), 0], 1e-3];
  };
  const kugel = n => {
    const r = Math.hypot(...n.p);
    if (r > 1) n.p = n.p.map(c => c / r);
  };

  // Paare ohne genug gemeinsame Stimmen haben keinen Sollabstand und ziehen
  // nicht aneinander. Dass sie sich nicht überdecken, regelt die Entzerrung.
  const soll = nodes.map(() => []);
  edges.forEach(e => {
    const i = nodes.indexOf(e.a), j = nodes.indexOf(e.b);
    soll[i].push([j, 1 - e.s]);
    soll[j].push([i, 1 - e.s]);
  });
  // Jeder Knoten rückt dahin, wo ihn alle Nachbarn im Sollabstand sähen,
  // gemittelt (Gansner, Koren, North 2004)
  for (let it = 0; it < 300; it++) {
    nodes.forEach((n, i) => {
      if (!soll[i].length) return;
      const z = [0, 0, 0];
      soll[i].forEach(([j, d]) => {
        const [u] = apart(n, nodes[j], i, j);
        for (let c = 0; c < 3; c++) z[c] += nodes[j].p[c] + d * u[c];
      });
      n.p = z.map(c => c / soll[i].length);
    });
  }

  // Die Mitte der Ausdehnung, nicht der Schwerpunkt. Der läge in der großen
  // Fraktion, zwei Ausreißer reichten dann bis an den Rand, und das Aufziehen
  // auf die Kugel drückte alle anderen in der Mitte zusammen.
  const mitte = [0, 1, 2].map(c => {
    const v = nodes.map(n => n.p[c]);
    return (Math.min(...v) + Math.max(...v)) / 2;
  });
  nodes.forEach(n => { n.p = n.p.map((c, x) => c - mitte[x]); });
  const rand = Math.max(...nodes.map(n => Math.hypot(...n.p))) || 1;
  nodes.forEach(n => { n.p = n.p.map(c => c / rand); });

  for (let it = 0; it < 240; it++) {
    let moved = false;
    for (let i = 0; i < N; i++) {
      for (let j = i + 1; j < N; j++) {
        const a = nodes[i], b = nodes[j];
        const [u, d] = apart(a, b, i, j);
        if (d >= MIN) continue;
        const push = (MIN - d) / 2;
        a.p = a.p.map((c, x) => c + u[x] * push);
        b.p = b.p.map((c, x) => c - u[x] * push);
        moved = true;
      }
    }
    nodes.forEach(kugel);
    if (!moved) break;
  }
}

// Drehen per Ziehen. Bis zum ersten Griff dreht sich das Netz langsam von
// selbst, erst die Bewegung macht die Tiefe lesbar. Steht der Zeiger auf einem
// Kreis, hält es an, sonst läuft er unter dem Tooltip weg.
function sgDrehen(svg, nodes, edges, knoten, W, H) {
  const S = sgMass(W, H);
  const linien = [...svg.querySelectorAll("line")];
  const namen = knoten.map(g => g.querySelector(".sg-name"));
  let yaw = 0.5, pitch = 0.35, reihe = "";

  const zeichne = () => {
    const cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
    nodes.forEach(n => {
      const [x, y, z] = n.p;
      const x1 = x * cy + z * sy, z1 = z * cy - x * sy;
      n.t = y * sp + z1 * cp;                 // Tiefe, groesser ist naeher
      n.f = SG_D / (SG_D - n.t);
      n.x = W / 2 + x1 * n.f * S;
      n.y = H / 2 + (y * cp - z1 * sp) * n.f * S;
    });
    edges.forEach((e, i) => {
      linien[i].setAttribute("x1", e.a.x.toFixed(1));
      linien[i].setAttribute("y1", e.a.y.toFixed(1));
      linien[i].setAttribute("x2", e.b.x.toFixed(1));
      linien[i].setAttribute("y2", e.b.y.toFixed(1));
    });
    knoten.forEach((g, i) => {
      const n = nodes[i];
      g.setAttribute("transform",
        `translate(${n.x.toFixed(1)},${n.y.toFixed(1)}) scale(${n.f.toFixed(3)})`);
      const anker = n.x < 60 ? "start" : n.x > W - 60 ? "end" : "middle";
      namen[i].setAttribute("x", anker === "start" ? -SG_R : anker === "end" ? SG_R : 0);
      namen[i].setAttribute("text-anchor", anker);
    });
    // Hinten zuerst. Ein angetippter Kreis bleibt vorn, sonst verdeckt ein
    // naeherer seinen Namen.
    const tiefe = i => knoten[i].classList.contains("on") ? Infinity : nodes[i].t;
    const neu = nodes.map((n, i) => i).sort((a, b) => tiefe(a) - tiefe(b));
    if (neu.join() !== reihe) {
      neu.forEach(i => svg.appendChild(knoten[i]));
      reihe = neu.join();
    }
  };
  zeichne();

  let auto = !matchMedia("(prefers-reduced-motion: reduce)").matches;
  let zeigt = false, sichtbar = true, vorher = 0;
  const io = new IntersectionObserver(([e]) => { sichtbar = e.isIntersecting; });
  io.observe(svg);
  const lauf = jetzt => {
    if (!auto || !svg.isConnected) { io.disconnect(); return; }
    if (vorher && sichtbar && !zeigt) {
      yaw += Math.min(jetzt - vorher, 50) * 0.00018;   // eine Runde in gut einer halben Minute
      zeichne();
    }
    vorher = jetzt;
    requestAnimationFrame(lauf);
  };
  requestAnimationFrame(lauf);

  svg.addEventListener("pointerover", e => {
    zeigt = e.pointerType === "mouse" && !!e.target.closest(".sg-node");
  });
  svg.addEventListener("pointerleave", () => { zeigt = false; });

  // Erst ab ein paar Pixeln ist es ein Ziehen. Darunter bleibt es ein Klick,
  // der wie in der Fläche den Namen zeigt oder das Profil oeffnet.
  let start = null, gezogen = false;
  svg.addEventListener("pointerdown", e => {
    auto = false;
    start = [e.clientX, e.clientY, yaw, pitch];
    gezogen = false;
  });
  svg.addEventListener("pointermove", e => {
    if (!start) return;
    const dx = e.clientX - start[0], dy = e.clientY - start[1];
    if (!gezogen && Math.hypot(dx, dy) < 5) return;
    if (!gezogen) svg.setPointerCapture(e.pointerId);
    gezogen = true;
    yaw = start[2] + dx * 0.01;
    pitch = Math.max(-1.4, Math.min(1.4, start[3] - dy * 0.01));
    zeichne();
  });
  svg.addEventListener("pointerup", () => { start = null; });
  svg.addEventListener("pointercancel", () => { start = null; });
  // Vor dem Klick-Zuhoerer in drawSimGraph, der sonst nach dem Loslassen das
  // Profil oeffnet
  svg.addEventListener("click", e => { if (gezogen) e.stopImmediatePropagation(); }, true);
}

function drawSimGraph(el, periodId) {
  const nodes = simNodes(periodId).map(n => ({ ...n, x: 0, y: 0, dx: 0, dy: 0 }));
  const pairs = similarity(periodId);
  if (nodes.length < 3) {
    el.innerHTML = html`<p class="chart-foot">Für diese Wahlperiode liegen noch zu wenige Einzelstimmen vor.</p>`;
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

  const W = el.clientWidth || 640, H = 420;

  // Wer nachrückt, hat mit dem Vorgänger nie abgestimmt, das Paar hat keine
  // Kante, und nichts zieht die beiden zueinander. Im Raum standen John und
  // Strobl so weit auseinander wie das fernste Fünftel aller Paare. Für die
  // Anordnung, nicht im Bild, bekommen sie deshalb die Nähe, die
  // Fraktionskollegen in dieser Periode typischerweise haben (Median).
  //
  // Die Nachfolge steht als `succeeds` am Mitglied. Wagner und Altenbeck
  // schieden am selben Tag aus; wer von Kilian Linz und A. Becher für wen
  // nachrückte, gibt die Liste von 2020 her, und die liegt nicht vor —
  // deshalb nennen beide beide, und es bleibt bei den vier Kreuzpaaren.
  const kollegen = edges
    .filter(e => e.a.party && e.b.party && e.a.party.id === e.b.party.id)
    .map(e => e.s).sort((x, y) => x - y);
  const folgt = (a, b) => (a.succeeds || []).includes(b.id)
                       || (b.succeeds || []).includes(a.id);
  const lage = edges.slice();
  if (kollegen.length) nodes.forEach(a => nodes.forEach(b => {
    if (a !== b && folgt(a.m, b.m)) lage.push({ a, b, s: kollegen[kollegen.length >> 1] });
  }));
  // Im Raum anderthalb Kreise Abstand statt einem: von vorn gesehen rücken
  // die Kreise durch die Tiefe ohnehin zusammen
  if (sgRaum) sgRaumLage(nodes, lage, 3 * SG_R / sgMass(W, H));
  else sgFlach(nodes, lage, W, H);

  const spread = simSpread(pairs);
  // Sortiert an Ort und Stelle: im Raum findet sgDrehen Kante i als i-te Linie
  const lines = edges
    .sort((p, q) => Math.abs(p.s) - Math.abs(q.s))
    .map(e => {
      const a = Math.min(1, Math.abs(e.s) / spread);
      return html`<line x1="${e.a.x.toFixed(1)}" y1="${e.a.y.toFixed(1)}"
               x2="${e.b.x.toFixed(1)}" y2="${e.b.y.toFixed(1)}"
               stroke="${e.s >= 0 ? "#4F8A16" : "#9B0000"}"
               stroke-opacity="${(a * a * 0.5).toFixed(3)}"
               stroke-width="${(0.4 + a * 2).toFixed(2)}"/>`;
    });
  const ini = sgInitialen(nodes);
  const dots = nodes.map(n => {
    const farbe = n.party ? n.party.color : "#999999";
    const k = ini(n);
    // Ein mittig gesetzter Name laeuft am Rand aus dem Bild. Dort haengt er
    // deshalb an der Innenseite des Knotens statt an dessen Mitte.
    const anker = n.x < 60 ? "start" : n.x > W - 60 ? "end" : "middle";
    const nx = anker === "start" ? -SG_R : anker === "end" ? SG_R : 0;
    return html`
    <g class="sg-node" transform="translate(${n.x.toFixed(1)},${n.y.toFixed(1)})">
      <circle r="${SG_R}" fill="${farbe}"/>
      <text class="sg-ini${k.length > 2 ? " lang" : ""}" y="3.6" text-anchor="middle"
            fill="${sgSchrift(farbe)}">${k}</text>
      <text class="sg-name" x="${nx}" y="${-(SG_R + 7)}" text-anchor="${anker}">${n.m.name}</text>
      <title>${n.m.name}${n.party ? " · " + n.party.name : ""}</title>
    </g>`;
  });

  el.innerHTML = html`<div class="sg-ansicht">
      <div class="period-switch">
        <button data-a="flach"${sgRaum ? "" : roh(' class="on"')}>Fläche</button>
        <button data-a="raum"${sgRaum ? roh(' class="on"') : ""}>Raum</button>
      </div>${sgRaum && html`<span class="sg-hinweis">Versuch. Ziehen dreht das Netz.</span>`}
    </div>
    <svg class="chart simgraph${sgRaum ? " raum" : ""}" width="${W}" height="${H}"
      viewBox="0 0 ${W} ${H}" role="img"
      aria-label="Nähe-Netz${sgRaum ? " im Raum" : ""}">${lines}${dots}</svg>`;
  el.querySelectorAll(".sg-ansicht button").forEach(b => b.addEventListener("click", () => {
    sgRaum = b.dataset.a === "raum";
    drawSimGraph(el, periodId);
  }));
  // Am Rechner nennt der Tooltip Namen und Fraktion, der Klick oeffnet sofort.
  // Mit dem Finger gibt es kein Zeigen -- dort nennt der erste Tipp den Namen,
  // der zweite oeffnet das Profil.
  //
  // Beim Zeigen darf sich am Knoten nichts bewegen. Wandert er auf mouseenter
  // ans Ende des SVG, bricht das am Rechner den Tooltip ab, und auf dem Handy,
  // wo der Browser nach dem Tap Mausereignisse nachschiebt, verschluckt es den
  // ersten Klick. Nach vorn geholt wird deshalb erst beim Tippen, wenn der Name
  // erscheint -- sonst deckt ihn ein spaeter gezeichneter Kreis zu.
  const nachVorn = g => g.parentNode.appendChild(g);
  const svg = el.querySelector("svg");
  const knoten = [...svg.querySelectorAll(".sg-node")];

  // Der Klick haengt am SVG, nicht an jedem Knoten: nach einer Beruehrung
  // schickt der Browser den Klick mitunter an das SVG statt an den Kreis
  // darin. Ueber das SVG kommt beides an, und beim Neuzeichnen ist der
  // Zuhoerer mit dem alten SVG weg.
  //
  // Welcher Knoten gemeint war, weiss aber nur pointerdown. Chrome verschiebt
  // den Klick nach einer Beruehrung auf das Element, das es fuer das
  // wahrscheinlichste Ziel haelt -- im dichten Netz eine Kante oder der
  // Nachbarkreis. Gemerkt wird deshalb der Knoten unter dem Finger beim
  // Aufsetzen, und der gilt beim Klick.
  let gedrueckt = null;
  svg.addEventListener("pointerdown", e => {
    gedrueckt = e.target.closest ? e.target.closest(".sg-node") : null;
  });
  svg.addEventListener("click", () => {
    const g = gedrueckt;
    if (!g) return;
    if (sgFinger && !g.classList.contains("on")) {
      knoten.forEach(o => o.classList.remove("on"));
      g.classList.add("on");
      nachVorn(g);
      return;
    }
    navigate("/member/" + nodes[knoten.indexOf(g)].m.id);
  });
  if (sgRaum) sgDrehen(svg, nodes, edges, knoten, W, H);
}

export { renderSimilarity, drawSimMatrix, drawSimGraph };
