// Sitzungsstatistik: wie lang die Sitzungen dauern, und wer mit wem stimmt.
import {
  sessionRegister, bestand, dauerMin, sitzungsart, SITZUNGSARTEN,
} from "../daten.js";
import { formatDate, formatDuration } from "../hilfen.js";
import { navigate, route, backLink } from "../routing.js";
import { PERIODS } from "../aehnlichkeit.js";
import { drawSimMatrix, drawSimGraph } from "./naehe.js";
import { html, roh } from "../html.js";
import {
  chartColor, median, monat, monatJahr,
  chartTipShow, chartTipMove, chartTipHide, chartCard,
} from "./diagramme.js";

const main = document.getElementById("main");

function renderStatistik() {
  main.appendChild(backLink("Übersicht", "#/"));

  const b = bestand();
  const entries = sessionRegister()
    .map(s => ({ id: s.id, date: s.date, body: s.type, start: s.start, end: s.end,
                 min: dauerMin(s), erfasst: !!s.agenda }))
    .sort((a, b2) => a.date.localeCompare(b2.date));
  const timed = entries.filter(e => e.min !== null);
  const srMins = timed.filter(e => e.body === "stadtrat").map(e => e.min);

  const header = document.createElement("div");
  header.className = "topic-header";
  header.innerHTML = html`
    <h1>Sitzungsstatistik</h1>
    <div class="topic-summary">Dauer der öffentlichen Sitzungen von Stadtrat, Bau-, Planungs- und Umweltausschuss (BPU) und Hauptverwaltungs- und Finanzausschuss (HVFA) seit ${monatJahr(b.seit)}.
      Gezählt ist jede Sitzung, die stattgefunden hat — auch die, von denen nichts
      veröffentlicht ist. Von ${b.sitzungen - b.mitDauer} ist keine Dauer überliefert.</div>`;
  main.appendChild(header);

  const tiles = document.createElement("div");
  tiles.className = "stat-tiles";
  tiles.innerHTML = html`
    <div class="stat-tile"><div class="stat-tile-value">${b.sitzungen}</div><div class="stat-tile-label">Sitzungen, ${b.mitDauer} davon mit Dauer</div></div>
    <div class="stat-tile"><div class="stat-tile-value">${Math.round(b.minuten / 60)} Std.</div><div class="stat-tile-label">Gesamtdauer</div></div>
    <div class="stat-tile"><div class="stat-tile-value">${formatDuration(median(srMins))}</div><div class="stat-tile-label">Stadtratssitzung im Median</div></div>`;
  main.appendChild(tiles);

  main.appendChild(chartCard("Jede Sitzung nach Dauer",
    "Jeder Punkt ist eine Sitzung. Klick öffnet die Sitzungsseite, sofern sie erfasst ist.",
    drawDurationDots, timed, true));
  main.appendChild(chartCard("Sitzungsstunden pro Jahr",
    `${timed[0].date.slice(0, 4)} ab ${monat(timed[0].date)}, `
      + `${timed[timed.length - 1].date.slice(0, 4)} bis ${monat(timed[timed.length - 1].date)}.`,
    drawYearHours, timed, true));
  main.appendChild(chartCard("Sitzungsdauer im Median",
    "Median pro Jahr und Gremium.",
    drawMedianByBody, timed, true));

  main.appendChild(buildStatsTable(entries));

  const nh = document.createElement("h2");
  nh.className = "section-label";
  nh.style.marginTop = "34px";
  nh.textContent = "Wer stimmt mit wem";
  main.appendChild(nh);

  const intro = document.createElement("p");
  intro.className = "chart-foot";
  intro.innerHTML = html`Verglichen werden nur <strong>geteilte</strong> Beschlüsse — bei
    Einstimmigkeit stimmen alle gleich, das sagt nichts. Gezählt wird je Paar
    +1 bei gleicher, −1 bei verschiedener Stimme; wer fehlt, zählt nicht mit.
    Die Summe wird durch (Vergleiche + 5) geteilt, damit dünne Grundlagen zur
    Mitte gezogen werden — vier gleiche Stimmen ergeben 0,44, fünfundzwanzig 0,83.`;
  main.appendChild(intro);

  periodCard(main, "Nähe-Matrix",
    "Zeilen und Spalten nach Fraktion sortiert — die Blöcke an der Diagonale sind die Fraktionen. "
    + "Nur die untere Hälfte, die obere wäre ihr Spiegelbild.",
    drawSimMatrix);
  periodCard(main, "Nähe-Netz",
    "Alle Kanten, ohne Schwellenwert: schwache Verbindungen verblassen, statt zu verschwinden. "
    + "Grün zieht zusammen, rot drückt auseinander. Klick öffnet das Profil.",
    drawSimGraph);
}

// Kartenrahmen mit Umschalter für die Wahlperiode. Wird sofort eingehängt,
// weil die Breite erst im Dokument messbar ist — und weil ein nachgereichtes
// Diagramm die Seite unter dem Finger wachsen lässt.
function periodCard(parent, title, foot, drawFn) {
  const card = document.createElement("div");
  card.className = "chart-card";
  card.innerHTML = html`<h3>${title}</h3>
    <div class="period-switch">${PERIODS.map((p, i) =>
      html`<button data-p="${p.id}"${i === 0 ? roh(' class="on"') : ""}>${p.label}</button>`)}</div>`;
  const chartEl = document.createElement("div");
  card.appendChild(chartEl);
  if (foot) {
    const f = document.createElement("div");
    f.className = "chart-foot";
    f.textContent = foot;
    card.appendChild(f);
  }
  card.querySelectorAll(".period-switch button").forEach(btn => {
    btn.addEventListener("click", () => {
      card.querySelectorAll(".period-switch button").forEach(b => b.classList.remove("on"));
      btn.classList.add("on");
      drawFn(chartEl, btn.dataset.p);
    });
  });
  parent.appendChild(card);
  drawFn(chartEl, PERIODS[0].id);
  // Höhe festhalten, sonst springt die Seite beim Periodenwechsel
  chartEl.style.minHeight = chartEl.offsetHeight + "px";
}

function drawDurationDots(el, entries) {
  const W = el.clientWidth || 640;
  const H = 250, top = 10, right = 8, bottom = 22, left = 36;
  const plotW = W - left - right, plotH = H - top - bottom;
  const t0 = Date.parse(entries[0].date);
  const t1 = Date.parse(entries[entries.length - 1].date);
  const maxMin = Math.ceil(Math.max(...entries.map(e => e.min)) / 60) * 60;
  const x = d => left + (Date.parse(d) - t0) / (t1 - t0) * plotW;
  const y = m => top + plotH * (1 - m / maxMin);

  const grid = [], ticks = [];
  for (let h = 60; h <= maxMin; h += 60) {
    grid.push(html`<line x1="${left}" x2="${W - right}" y1="${y(h).toFixed(1)}" y2="${y(h).toFixed(1)}"/>`);
    ticks.push(html`<text class="chart-tick" x="${left - 6}" y="${(y(h) + 3).toFixed(1)}" text-anchor="end">${h / 60} h</text>`);
  }
  const firstYear = +entries[0].date.slice(0, 4);
  // Startjahr nur beschriften, wenn es nicht mit dem ersten Jahres-Tick kollidiert
  if (x(firstYear + 1 + "-01-01") - left > 44) {
    ticks.push(html`<text class="chart-tick" x="${left}" y="${H - 6}" text-anchor="start">${firstYear}</text>`);
  }
  for (let yr = firstYear + 1; Date.parse(yr + "-01-01") <= t1; yr++) {
    ticks.push(html`<text class="chart-tick" x="${x(yr + "-01-01").toFixed(1)}" y="${H - 6}" text-anchor="middle">${yr}</text>`);
  }

  const dots = entries.map((e, i) => {
    const linked = e.erfasst ? " linked" : "";
    return html`<circle class="dt-dot${linked}" data-i="${i}" cx="${x(e.date).toFixed(1)}" cy="${y(e.min).toFixed(1)}" r="4" fill="${chartColor[e.body]}"/>`;
  });

  el.innerHTML = html`<svg class="chart" width="${W}" height="${H}" role="img" aria-label="Sitzungsdauer im Zeitverlauf">
    <g class="chart-grid">${grid}</g>${ticks}${dots}</svg>`;

  el.querySelectorAll(".dt-dot").forEach(dot => {
    const e = entries[dot.dataset.i];
    const label = sitzungsart(e.body).label;
    dot.addEventListener("mouseenter", evt => chartTipShow(evt,
      html`<strong>${label} · ${formatDate(e.date)}</strong><br>${e.start}–${e.end} Uhr · ${formatDuration(e.min)}`));
    dot.addEventListener("mousemove", chartTipMove);
    dot.addEventListener("mouseleave", chartTipHide);
    if (e.erfasst) dot.addEventListener("click", () => {
      chartTipHide();
      navigate("/session/" + e.id);
    });
  });
}

// Abgerundete Oberkante (4px), Unterkante gerade auf der Basislinie
function capRect(x, y, w, h) {
  const r = Math.min(4, h);
  return `M${x},${(y + r).toFixed(1)} a${r},${r} 0 0 1 ${r},-${r} h${w - 2 * r} a${r},${r} 0 0 1 ${r},${r} v${(h - r).toFixed(1)} h${-w} Z`;
}

function drawYearHours(el, entries) {
  const years = [...new Set(entries.map(e => e.date.slice(0, 4)))].sort();
  const sums = {};
  years.forEach(yr => { sums[yr] = {}; SITZUNGSARTEN.forEach(a => { sums[yr][a.type] = 0; }); });
  entries.forEach(e => { sums[e.date.slice(0, 4)][e.body] += e.min; });
  const totalOf = yr => SITZUNGSARTEN.reduce((n, a) => n + sums[yr][a.type], 0);

  const W = el.clientWidth || 640;
  const H = 220, top = 20, right = 8, bottom = 22, left = 36;
  const plotW = W - left - right, plotH = H - top - bottom;
  const maxH = Math.ceil(Math.max(...years.map(totalOf)) / 60 / 20) * 20;
  const scale = min => min / 60 / maxH * plotH;
  const slot = plotW / years.length;
  const barW = Math.min(24, Math.round(slot * 0.55));

  const grid = [], ticks = [];
  for (let h = 20; h <= maxH; h += 20) {
    const gy = (top + plotH - scale(h * 60)).toFixed(1);
    grid.push(html`<line x1="${left}" x2="${W - right}" y1="${gy}" y2="${gy}"/>`);
    ticks.push(html`<text class="chart-tick" x="${left - 6}" y="${+gy + 3}" text-anchor="end">${h} h</text>`);
  }

  const bars = [], hover = [];
  years.forEach((yr, yi) => {
    const cx = left + slot * (yi + 0.5);
    const bx = Math.round(cx - barW / 2);
    let base = top + plotH;
    const gaps = [];
    const segs = SITZUNGSARTEN.filter(b => sums[yr][b.type] > 0);
    segs.forEach((b, si) => {
      const h = scale(sums[yr][b.type]);
      const sy = base - h;
      if (si === segs.length - 1) {
        bars.push(html`<path class="yh-seg" data-yr="${yr}" data-b="${b.type}" d="${capRect(bx, sy, barW, h)}" fill="${b.color}"/>`);
      } else {
        bars.push(html`<rect class="yh-seg" data-yr="${yr}" data-b="${b.type}" x="${bx}" y="${sy.toFixed(1)}" width="${barW}" height="${h.toFixed(1)}" fill="${b.color}"/>`);
        // 2px Lücke in Flächenfarbe zwischen den Segmenten
        gaps.push(html`<line x1="${bx}" x2="${bx + barW}" y1="${sy.toFixed(1)}" y2="${sy.toFixed(1)}" stroke="var(--surface)" stroke-width="2"/>`);
      }
      base = sy;
    });
    bars.push(gaps);
    bars.push(html`<text class="chart-cap" x="${cx.toFixed(1)}" y="${(base - 5).toFixed(1)}" text-anchor="middle">${Math.round(totalOf(yr) / 60)}</text>`);
    ticks.push(html`<text class="chart-tick" x="${cx.toFixed(1)}" y="${H - 6}" text-anchor="middle">${yr}</text>`);
  });

  el.innerHTML = html`<svg class="chart" width="${W}" height="${H}" role="img" aria-label="Sitzungsstunden pro Jahr">
    <g class="chart-grid">${grid}</g>${ticks}${bars}</svg>`;

  el.querySelectorAll(".yh-seg").forEach(seg => {
    const b = sitzungsart(seg.dataset.b);
    const minutes = sums[seg.dataset.yr][seg.dataset.b];
    seg.addEventListener("mouseenter", evt => chartTipShow(evt,
      html`<strong>${b.label} ${seg.dataset.yr}</strong><br>${Math.round(minutes / 60)} Std. in ${entries.filter(e => e.date.slice(0, 4) === seg.dataset.yr && e.body === seg.dataset.b).length} Sitzungen`));
    seg.addEventListener("mousemove", chartTipMove);
    seg.addEventListener("mouseleave", chartTipHide);
  });
}

function drawMedianByBody(el, entries) {
  const years = [...new Set(entries.map(e => e.date.slice(0, 4)))].sort();
  const med = {}, counts = {};
  years.forEach(yr => {
    med[yr] = {}; counts[yr] = {};
    SITZUNGSARTEN.forEach(b => {
      const mins = entries.filter(e => e.date.slice(0, 4) === yr && e.body === b.type).map(e => e.min);
      if (mins.length) { med[yr][b.type] = median(mins); counts[yr][b.type] = mins.length; }
    });
  });

  const W = el.clientWidth || 640;
  const H = 200, top = 12, right = 8, bottom = 22, left = 36;
  const plotW = W - left - right, plotH = H - top - bottom;
  const maxMin = Math.ceil(Math.max(...years.map(yr => Math.max(...Object.values(med[yr])))) / 60) * 60;
  const scale = m => m / maxMin * plotH;
  const slot = plotW / years.length;
  const barW = Math.min(16, Math.floor((slot * 0.7 - 4) / SITZUNGSARTEN.length));

  const grid = [], ticks = [];
  for (let h = 60; h <= maxMin; h += 60) {
    const gy = (top + plotH - scale(h)).toFixed(1);
    grid.push(html`<line x1="${left}" x2="${W - right}" y1="${gy}" y2="${gy}"/>`);
    ticks.push(html`<text class="chart-tick" x="${left - 6}" y="${+gy + 3}" text-anchor="end">${h / 60} h</text>`);
  }

  const bars = [];
  years.forEach((yr, yi) => {
    const cx = left + slot * (yi + 0.5);
    const present = SITZUNGSARTEN.filter(b => med[yr][b.type] !== undefined);
    const groupW = present.length * barW + (present.length - 1) * 2;
    present.forEach((b, bi) => {
      const bx = Math.round(cx - groupW / 2 + bi * (barW + 2));
      const h = scale(med[yr][b.type]);
      bars.push(html`<path class="mb-bar" data-yr="${yr}" data-b="${b.type}" d="${capRect(bx, top + plotH - h, barW, h)}" fill="${b.color}"/>`);
    });
    ticks.push(html`<text class="chart-tick" x="${cx.toFixed(1)}" y="${H - 6}" text-anchor="middle">${yr}</text>`);
  });

  el.innerHTML = html`<svg class="chart" width="${W}" height="${H}" role="img" aria-label="Mediandauer der Sitzungen pro Jahr und Gremium">
    <g class="chart-grid">${grid}</g>${ticks}${bars}</svg>`;

  el.querySelectorAll(".mb-bar").forEach(bar => {
    const yr = bar.dataset.yr, bid = bar.dataset.b;
    const b = sitzungsart(bid);
    bar.addEventListener("mouseenter", evt => chartTipShow(evt,
      html`<strong>${b.label} ${yr}</strong><br>Median ${formatDuration(med[yr][bid])} (${counts[yr][bid]} Sitzung${counts[yr][bid] > 1 ? "en" : ""})`));
    bar.addEventListener("mousemove", chartTipMove);
    bar.addEventListener("mouseleave", chartTipHide);
  });
}

function buildStatsTable(entries) {
  const years = [...new Set(entries.map(e => e.date.slice(0, 4)))].sort();
  const rows = years.map(yr => {
    const inYear = entries.filter(e => e.date.slice(0, 4) === yr);
    const timed = inYear.filter(e => e.min !== null);
    const srMins = timed.filter(e => e.body === "stadtrat").map(e => e.min);
    return html`<tr>
      <td>${yr}</td>
      <td>${inYear.length}</td>
      <td>${Math.round(timed.reduce((s, e) => s + e.min, 0) / 60)} Std.</td>
      <td>${srMins.length ? formatDuration(median(srMins)) : "–"}</td>
    </tr>`;
  });

  const open = entries.filter(e => e.min === null).length;
  const details = document.createElement("details");
  details.className = "stats-table";
  details.innerHTML = html`
    <summary><svg class="icon"><use href="#i-table_rows"/></svg> Daten als Tabelle</summary>
    <table>
      <thead><tr><th>Jahr</th><th>Sitzungen</th><th>Gesamtdauer</th><th>Stadtrat im Median</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
    ${open > 0 && html`<div class="chart-foot">${open} Sitzung${open > 1 ? "en" : ""} ohne erfasste Endzeit, nicht in den Dauern enthalten.</div>`}`;
  return details;
}

// Charts sind auf Containerbreite gezeichnet, bei Größenänderung neu aufbauen
let statsResizeTimer;
function initStatistik() {
  window.addEventListener("resize", () => {
    const path = (window.location.hash.slice(1) || "/").split("?")[0];
    if (path !== "/statistik") return;
    clearTimeout(statsResizeTimer);
    statsResizeTimer = setTimeout(route, 150);
  });
}


export { renderStatistik, initStatistik };
