// Die drei Übersichtsseiten samt ihrer Diagramme: Sitzungsstatistik
// (Dauer-Punkte, Jahresstunden, Mediane), Datenlage (Register mit
// Herkunftsstufen) und Presseschau.
import {
  sessions, topics, members, pressData, sessionLengths, mediaMap,
  sessionByDateBody, sessionRegister, tierCounts, lengthMin,
  protocolUrl, isWebauszug,
} from "../daten.js";
import { formatDate, formatDuration } from "../hilfen.js";
import { navigate, setChrome, route } from "../routing.js";
import { breadcrumb } from "./themen.js";
import { PERIODS, drawSimMatrix, drawSimGraph } from "./naehe.js";

const main = document.getElementById("main");

// -- Statistik --

// Farben je Gremium: an die Kalender-Punkte angelehnt, aber dunkler
// abgestuft, damit Gold/Blau auf hellem Grund und für Farbenblinde
// unterscheidbar bleiben.
const CHART_BODIES = [
  { id: "stadtrat", label: "Stadtrat", color: "#E6001E" },
  { id: "bpu",      label: "BPU",      color: "#8a6d1e" },
  { id: "hvfa",     label: "HVFA",     color: "#3d7fc1" },
];
const chartColor = {};
CHART_BODIES.forEach(b => { chartColor[b.id] = b.color; });

function median(arr) {
  const s = [...arr].sort((a, b) => a - b);
  const mid = s.length >> 1;
  return s.length % 2 ? s[mid] : Math.round((s[mid - 1] + s[mid]) / 2);
}

const chartTip = document.getElementById("tooltip");

function chartTipShow(evt, html) {
  chartTip.innerHTML = html;
  chartTip.classList.remove("hidden");
  chartTipMove(evt);
}
function chartTipMove(evt) {
  const cx = evt.clientX + 14, cy = evt.clientY - 10;
  const r = chartTip.getBoundingClientRect();
  chartTip.style.left = Math.min(cx, window.innerWidth - r.width - 8) + "px";
  chartTip.style.top = Math.max(4, cy - r.height) + "px";
}
function chartTipHide() {
  chartTip.classList.add("hidden");
}

function chartLegend() {
  return `<div class="chart-legend">` + CHART_BODIES.map(b =>
    `<span><span class="chart-dot" style="background:${b.color}"></span>${b.label}</span>`).join("") + `</div>`;
}

function chartCard(title, foot, drawFn, data, withLegend) {
  const card = document.createElement("div");
  card.className = "chart-card";
  card.innerHTML = `<h3>${title}</h3>${withLegend ? chartLegend() : ""}`;
  const chartEl = document.createElement("div");
  card.appendChild(chartEl);
  if (foot) {
    const f = document.createElement("div");
    f.className = "chart-foot";
    f.textContent = foot;
    card.appendChild(f);
  }
  // Breite erst nach dem Einhängen messbar
  requestAnimationFrame(() => drawFn(chartEl, data));
  return card;
}

function renderStatistik() {
  const back = document.createElement("a");
  back.className = "back-link";
  back.href = "#/";
  back.innerHTML = '<svg class="icon"><use href="#i-arrow_back"/></svg> Übersicht';
  back.addEventListener("click", e => {
    if (window.history.length > 1) { e.preventDefault(); window.history.back(); }
  });
  main.appendChild(back);

  const entries = [...sessionLengths]
    .map(l => ({ date: l.date, body: l.body, start: l.start, end: l.end, min: lengthMin(l) }))
    .sort((a, b) => a.date.localeCompare(b.date));
  const timed = entries.filter(e => e.min !== null);
  const totalMin = timed.reduce((s, e) => s + e.min, 0);
  const srMins = timed.filter(e => e.body === "stadtrat").map(e => e.min);

  const header = document.createElement("div");
  header.className = "topic-header";
  header.innerHTML = `
    <h1>Sitzungsstatistik</h1>
    <div class="topic-summary">Dauer der öffentlichen Sitzungen von Stadtrat, Bau-, Planungs- und Umweltausschuss (BPU) und Hauptverwaltungs- und Finanzausschuss (HVFA) in der Wahlperiode 2020–2026.</div>`;
  main.appendChild(header);

  const tiles = document.createElement("div");
  tiles.className = "stat-tiles";
  tiles.innerHTML = `
    <div class="stat-tile"><div class="stat-tile-value">${entries.length}</div><div class="stat-tile-label">Sitzungen</div></div>
    <div class="stat-tile"><div class="stat-tile-value">${Math.round(totalMin / 60)} Std.</div><div class="stat-tile-label">Gesamtdauer</div></div>
    <div class="stat-tile"><div class="stat-tile-value">${formatDuration(median(srMins))}</div><div class="stat-tile-label">Stadtratssitzung im Median</div></div>`;
  main.appendChild(tiles);

  main.appendChild(chartCard("Jede Sitzung nach Dauer",
    "Jeder Punkt ist eine Sitzung. Klick öffnet die Sitzungsseite, sofern sie erfasst ist.",
    drawDurationDots, timed, true));
  main.appendChild(chartCard("Sitzungsstunden pro Jahr",
    "2020 ab Mai, 2026 bis April (Wahlperiode).",
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
  intro.innerHTML = "Verglichen werden nur <strong>geteilte</strong> Beschlüsse — bei "
    + "Einstimmigkeit stimmen alle gleich, das sagt nichts. Gezählt wird je Paar "
    + "+1 bei gleicher, −1 bei verschiedener Stimme; wer fehlt, zählt nicht mit. "
    + "Die Summe wird durch (Vergleiche + 5) geteilt, damit dünne Grundlagen zur "
    + "Mitte gezogen werden — vier gleiche Stimmen ergeben 0,44, fünfundzwanzig 0,83.";
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
  card.innerHTML = `<h3>${title}</h3>
    <div class="period-switch">${PERIODS.map((p, i) =>
      `<button data-p="${p.id}"${i === 0 ? ' class="on"' : ""}>${p.label}</button>`).join("")}</div>`;
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

// -- Datenlage: was liegt zu welcher Sitzung vor --

const TIERS = [
  { key: "explicit", label: "namentlich",    hint: "Die Niederschrift nennt jeden Namen." },
  { key: "implicit", label: "abgeleitet",    hint: "Einstimmig, aus der Anwesenheit erschlossen." },
  { key: "tracked",  label: "mitgeschrieben", hint: "Von einer benannten Person im Saal erfasst." },
  { key: "press",    label: "aus Presse",    hint: "Aus einem Zeitungsartikel rekonstruiert." },
  { key: "sum",      label: "nur Ergebnis",  hint: "Nur die Gesamtzahlen sind bekannt." },
];

// `filter` schränkt auf eine Herkunftsstufe (explicit/implicit/tracked/press/
// sum) oder eine Erfassungsstufe (protokoll/auszug/keine) ein.
function renderDatenlage(filter) {
  setChrome("sitzung");
  main.appendChild(breadcrumb([{ label: "Übersicht", href: "#/" }]));

  const reg = sessionRegister();
  const erfasst = reg.filter(r => r.session);
  const protokoll = erfasst.filter(r => !isWebauszug(r.session));
  const auszug = erfasst.filter(r => isWebauszug(r.session));
  const totalVotes = erfasst.reduce((n, r) => n + r.votes.length, 0);
  const all = tierCounts(erfasst.flatMap(r => r.votes));
  const traceable = totalVotes - all.sum;

  const header = document.createElement("div");
  header.className = "topic-header";
  header.innerHTML = `
    <h1>Datenlage</h1>
    <div class="topic-summary">Jede öffentliche Sitzung seit Mai 2020, und was von ihr vorliegt.
      Sitzungen ohne Niederschrift sind hier bewusst mit aufgeführt — die Lücke gehört zur
      Auskunft dazu.</div>`;
  main.appendChild(header);

  const tiles = document.createElement("div");
  tiles.className = "stat-tiles";
  tiles.innerHTML = `
    <div class="stat-tile"><div class="stat-tile-value">${protokoll.length} <small>/ ${reg.length}</small></div><div class="stat-tile-label">Sitzungen mit Niederschrift</div></div>
    <div class="stat-tile"><div class="stat-tile-value">${totalVotes}</div><div class="stat-tile-label">erfasste Abstimmungen</div></div>
    <div class="stat-tile"><div class="stat-tile-value">${Math.round(traceable / totalVotes * 100)} %</div><div class="stat-tile-label">Stimmverhalten nachvollziehbar</div></div>`;
  main.appendChild(tiles);

  // Jede Kennzahl ist ein Filter auf sich selbst. Nochmal draufklicken hebt auf.
  const chip = (key, cls, label, n, hint) =>
    `<a class="tier-chip ${cls}${filter === key ? " on" : ""}"
        href="#/datenlage${filter === key ? "" : "/" + key}" title="${hint}">${label} <b>${n}</b></a>`;

  const levels = document.createElement("div");
  levels.className = "tier-legend";
  levels.innerHTML =
    chip("protokoll", "level-protokoll", "Niederschrift", protokoll.length,
         "Niederschrift mit Anwesenheitsliste")
    + chip("auszug", "level-auszug", "nur Beschlussauszug", auszug.length,
           "Beschlussauszug der Stadt, ohne Anwesenheitsliste")
    + chip("keine", "level-keine", "nichts veröffentlicht", reg.length - erfasst.length,
           "Weder Niederschrift noch Auszug veröffentlicht");
  main.appendChild(levels);

  const legend = document.createElement("div");
  legend.className = "tier-legend";
  legend.innerHTML = TIERS.map(t =>
    chip(t.key, "tier-" + t.key, t.label, all[t.key], t.hint)).join("");
  main.appendChild(legend);

  // Herkunftsstufe: die Abstimmungen selbst auflisten, nicht die Sitzungen —
  // "elf namentliche Abstimmungen" will man lesen, nicht suchen.
  const tier = TIERS.find(t => t.key === filter);
  if (tier) {
    main.appendChild(tierVoteList(tier, erfasst));
    return;
  }
  const rows = filter === "protokoll" ? protokoll
             : filter === "auszug"    ? auszug
             : filter === "keine"     ? reg.filter(r => !r.session)
             : reg;
  if (filter && rows !== reg) {
    const note = document.createElement("p");
    note.className = "chart-foot";
    note.textContent = rows.length + " von " + reg.length + " Sitzungen.";
    main.appendChild(note);
  }

  let year = null;
  const table = document.createElement("table");
  table.className = "register";
  const body = document.createElement("tbody");
  rows.forEach(r => {
    if (r.date.slice(0, 4) !== year) {
      year = r.date.slice(0, 4);
      const head = document.createElement("tr");
      head.className = "register-year";
      head.innerHTML = `<th colspan="4">${year}</th>`;
      body.appendChild(head);
    }
    const label = CHART_BODIES.find(b => b.id === r.body).label;
    const dur = r.min ? formatDuration(r.min) : r.start ? r.start + " Uhr" : "";
    const c = tierCounts(r.votes);
    const bar = r.votes.length
      ? `<span class="tier-bar">${TIERS.filter(t => c[t.key])
          .map(t => `<span class="tier-${t.key}" style="flex:${c[t.key]}" title="${c[t.key]}× ${t.label}"></span>`)
          .join("")}</span>`
      : "";

    const web = r.session && isWebauszug(r.session);
    const doc = !r.session ? ""
      : web
        ? (r.session.source.url
            ? `<a class="reg-pdf" href="${r.session.source.url}" target="_blank" rel="noopener"
                  title="Beschlussauszug der Stadt, ohne Anwesenheitsliste"><svg class="icon"><use href="#i-language"/></svg></a>`
            : "")
        : `<a class="reg-pdf" href="${protocolUrl(r.session)}" target="_blank" rel="noopener"
              title="Niederschrift als PDF"><svg class="icon"><use href="#i-description"/></svg></a>`;

    const tr = document.createElement("tr");
    tr.className = r.session ? (web ? "register-partial" : "") : "register-gap";
    tr.innerHTML = `
      <td class="reg-date">${formatDate(r.date)}</td>
      <td class="reg-body"><span class="reg-dot" style="background:${chartColor[r.body]}"></span>${label}</td>
      <td class="reg-dur">${dur}</td>
      <td class="reg-data">${r.session
        ? `<a href="#/session/${r.session.id}">${r.votes.length} Abstimmung${r.votes.length === 1 ? "" : "en"}</a>`
          + (web ? `<span class="reg-flag">ohne Anwesenheitsliste</span>` : "")
          + bar + doc
        : `<span class="reg-none">nichts veröffentlicht</span>`}</td>`;
    body.appendChild(tr);
  });
  table.appendChild(body);
  main.appendChild(table);
}

// Alle Abstimmungen einer Herkunftsstufe, nach Sitzung gruppiert
function tierVoteList(tier, erfasst) {
  const wrap = document.createElement("div");
  const hit = r => r.votes.filter(v => {
    const t = (v.source || {}).tier;
    return tier.key === "sum" ? !t
         : tier.key === "explicit" ? t === "protocol-explicit"
         : tier.key === "implicit" ? t === "protocol-implicit"
         : t === tier.key;
  });
  const groups = erfasst.map(r => [r, hit(r)]).filter(([, v]) => v.length);
  const n = groups.reduce((a, [, v]) => a + v.length, 0);

  const note = document.createElement("p");
  note.className = "chart-foot";
  note.textContent = n + " Abstimmung" + (n === 1 ? "" : "en") + " in "
    + groups.length + " Sitzung" + (groups.length === 1 ? "" : "en") + ". " + tier.hint;
  wrap.appendChild(note);

  const table = document.createElement("table");
  table.className = "register";
  const body = document.createElement("tbody");
  groups.forEach(([r, list]) => {
    const label = CHART_BODIES.find(b => b.id === r.body).label;
    const head = document.createElement("tr");
    head.className = "register-year";
    head.innerHTML = `<th colspan="2"><a href="#/session/${r.session.id}">${formatDate(r.date)}
      · ${label}</a></th>`;
    body.appendChild(head);
    list.forEach(v => {
      const res = v.type === "named"
        ? `${v.results.yes.length}:${v.results.no.length}`
        : `${v.results.yes}:${v.results.no}`;
      const tr = document.createElement("tr");
      tr.innerHTML = `<td class="reg-data"><a href="#/session/${r.session.id}">${v.title}</a></td>
                      <td class="reg-dur">${res}</td>`;
      body.appendChild(tr);
    });
  });
  table.appendChild(body);
  wrap.appendChild(table);
  return wrap;
}

// -- Presseschau --

// Presseartikel hängen an Sitzungen, Dossiers und Anträgen. Für die Übersicht
// wird der Weg umgedreht: je Artikel, woran er hängt.
function pressContext() {
  const ctx = {};
  const add = (ids, entry) => (ids || []).forEach(id => (ctx[id] || (ctx[id] = [])).push(entry));
  sessions.forEach(s => s.agenda.forEach(a =>
    add(a.press, { kind: "Sitzung", label: s.title, href: "#/session/" + s.id })));
  topics.forEach(t => (t.history || []).forEach(h =>
    add(h.press, { kind: "Dossier", label: t.title, href: "#/topic/" + t.id })));
  members.forEach(m => ((m.profile || {}).motions || []).forEach(mo =>
    add(mo.press, { kind: "Antrag", label: mo.title, href: "#/member/" + m.id })));
  return ctx;
}

function renderPresse() {
  main.appendChild(breadcrumb([{ label: "Übersicht", href: "#/" }]));

  const ctx = pressContext();
  const arts = [...pressData].sort((a, b) => b.date.localeCompare(a.date));

  const header = document.createElement("div");
  header.className = "topic-header";
  header.innerHTML = `
    <h1>Presseschau</h1>
    <div class="topic-summary">Alle Zeitungsartikel, die in dieser App verlinkt sind — zu Sitzungen,
      Dossiers und Anträgen. Die Artikel bleiben bei ihren Häusern, hier steht nur der Verweis.</div>`;
  main.appendChild(header);

  let year = null;
  const list = document.createElement("div");
  list.className = "press-list";
  arts.forEach(p => {
    if (p.date.slice(0, 4) !== year) {
      year = p.date.slice(0, 4);
      const h = document.createElement("h2");
      h.className = "section-label";
      h.textContent = year;
      list.appendChild(h);
    }
    const src = mediaMap[p.media] || { name: p.media, color: "#999" };
    const row = document.createElement("div");
    row.className = "press-row";
    row.innerHTML = `
      <span class="press-medium" style="background:${src.color}">${src.logo
        ? `<img src="${src.logo}" alt="${src.name}">` : src.name}</span>
      <div>
        <a class="press-title" href="${p.url}" target="_blank" rel="noopener">${p.title}
          <svg class="icon"><use href="#i-open_in_new"/></svg></a>
        <div class="press-meta">${formatDate(p.date)} · ${src.name}</div>
        <div class="press-refs">${(ctx[p.id] || [])
          .map(c => `<a href="${c.href}"><span class="press-ref-kind">${c.kind}</span>${c.label}</a>`)
          .join("")}</div>
      </div>`;
    list.appendChild(row);
  });
  main.appendChild(list);
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

  let grid = "", ticks = "";
  for (let h = 60; h <= maxMin; h += 60) {
    grid += `<line x1="${left}" x2="${W - right}" y1="${y(h).toFixed(1)}" y2="${y(h).toFixed(1)}"/>`;
    ticks += `<text class="chart-tick" x="${left - 6}" y="${(y(h) + 3).toFixed(1)}" text-anchor="end">${h / 60} h</text>`;
  }
  const firstYear = +entries[0].date.slice(0, 4);
  // Startjahr nur beschriften, wenn es nicht mit dem ersten Jahres-Tick kollidiert
  if (x(firstYear + 1 + "-01-01") - left > 44) {
    ticks += `<text class="chart-tick" x="${left}" y="${H - 6}" text-anchor="start">${firstYear}</text>`;
  }
  for (let yr = firstYear + 1; Date.parse(yr + "-01-01") <= t1; yr++) {
    ticks += `<text class="chart-tick" x="${x(yr + "-01-01").toFixed(1)}" y="${H - 6}" text-anchor="middle">${yr}</text>`;
  }

  const dots = entries.map((e, i) => {
    const linked = sessionByDateBody[e.date + "|" + e.body] ? " linked" : "";
    return `<circle class="dt-dot${linked}" data-i="${i}" cx="${x(e.date).toFixed(1)}" cy="${y(e.min).toFixed(1)}" r="4" fill="${chartColor[e.body]}"/>`;
  }).join("");

  el.innerHTML = `<svg class="chart" width="${W}" height="${H}" role="img" aria-label="Sitzungsdauer im Zeitverlauf">
    <g class="chart-grid">${grid}</g>${ticks}${dots}</svg>`;

  el.querySelectorAll(".dt-dot").forEach(dot => {
    const e = entries[dot.dataset.i];
    const session = sessionByDateBody[e.date + "|" + e.body];
    const label = CHART_BODIES.find(b => b.id === e.body).label;
    dot.addEventListener("mouseenter", evt => chartTipShow(evt,
      `<strong>${label} · ${formatDate(e.date)}</strong><br>${e.start}–${e.end} Uhr · ${formatDuration(e.min)}`));
    dot.addEventListener("mousemove", chartTipMove);
    dot.addEventListener("mouseleave", chartTipHide);
    if (session) dot.addEventListener("click", () => {
      chartTipHide();
      navigate("/session/" + session.id);
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
  years.forEach(yr => { sums[yr] = { stadtrat: 0, bpu: 0, hvfa: 0 }; });
  entries.forEach(e => { sums[e.date.slice(0, 4)][e.body] += e.min; });
  const totalOf = yr => sums[yr].stadtrat + sums[yr].bpu + sums[yr].hvfa;

  const W = el.clientWidth || 640;
  const H = 220, top = 20, right = 8, bottom = 22, left = 36;
  const plotW = W - left - right, plotH = H - top - bottom;
  const maxH = Math.ceil(Math.max(...years.map(totalOf)) / 60 / 20) * 20;
  const scale = min => min / 60 / maxH * plotH;
  const slot = plotW / years.length;
  const barW = Math.min(24, Math.round(slot * 0.55));

  let grid = "", ticks = "";
  for (let h = 20; h <= maxH; h += 20) {
    const gy = (top + plotH - scale(h * 60)).toFixed(1);
    grid += `<line x1="${left}" x2="${W - right}" y1="${gy}" y2="${gy}"/>`;
    ticks += `<text class="chart-tick" x="${left - 6}" y="${+gy + 3}" text-anchor="end">${h} h</text>`;
  }

  let bars = "", hover = [];
  years.forEach((yr, yi) => {
    const cx = left + slot * (yi + 0.5);
    const bx = Math.round(cx - barW / 2);
    let base = top + plotH;
    let gaps = "";
    const segs = CHART_BODIES.filter(b => sums[yr][b.id] > 0);
    segs.forEach((b, si) => {
      const h = scale(sums[yr][b.id]);
      const sy = base - h;
      if (si === segs.length - 1) {
        bars += `<path class="yh-seg" data-yr="${yr}" data-b="${b.id}" d="${capRect(bx, sy, barW, h)}" fill="${b.color}"/>`;
      } else {
        bars += `<rect class="yh-seg" data-yr="${yr}" data-b="${b.id}" x="${bx}" y="${sy.toFixed(1)}" width="${barW}" height="${h.toFixed(1)}" fill="${b.color}"/>`;
        // 2px Lücke in Flächenfarbe zwischen den Segmenten
        gaps += `<line x1="${bx}" x2="${bx + barW}" y1="${sy.toFixed(1)}" y2="${sy.toFixed(1)}" stroke="var(--surface)" stroke-width="2"/>`;
      }
      base = sy;
    });
    bars += gaps;
    bars += `<text class="chart-cap" x="${cx.toFixed(1)}" y="${(base - 5).toFixed(1)}" text-anchor="middle">${Math.round(totalOf(yr) / 60)}</text>`;
    ticks += `<text class="chart-tick" x="${cx.toFixed(1)}" y="${H - 6}" text-anchor="middle">${yr}</text>`;
  });

  el.innerHTML = `<svg class="chart" width="${W}" height="${H}" role="img" aria-label="Sitzungsstunden pro Jahr">
    <g class="chart-grid">${grid}</g>${ticks}${bars}</svg>`;

  el.querySelectorAll(".yh-seg").forEach(seg => {
    const b = CHART_BODIES.find(cb => cb.id === seg.dataset.b);
    const minutes = sums[seg.dataset.yr][seg.dataset.b];
    seg.addEventListener("mouseenter", evt => chartTipShow(evt,
      `<strong>${b.label} ${seg.dataset.yr}</strong><br>${Math.round(minutes / 60)} Std. in ${entries.filter(e => e.date.slice(0, 4) === seg.dataset.yr && e.body === seg.dataset.b).length} Sitzungen`));
    seg.addEventListener("mousemove", chartTipMove);
    seg.addEventListener("mouseleave", chartTipHide);
  });
}

function drawMedianByBody(el, entries) {
  const years = [...new Set(entries.map(e => e.date.slice(0, 4)))].sort();
  const med = {}, counts = {};
  years.forEach(yr => {
    med[yr] = {}; counts[yr] = {};
    CHART_BODIES.forEach(b => {
      const mins = entries.filter(e => e.date.slice(0, 4) === yr && e.body === b.id).map(e => e.min);
      if (mins.length) { med[yr][b.id] = median(mins); counts[yr][b.id] = mins.length; }
    });
  });

  const W = el.clientWidth || 640;
  const H = 200, top = 12, right = 8, bottom = 22, left = 36;
  const plotW = W - left - right, plotH = H - top - bottom;
  const maxMin = Math.ceil(Math.max(...years.map(yr => Math.max(...Object.values(med[yr])))) / 60) * 60;
  const scale = m => m / maxMin * plotH;
  const slot = plotW / years.length;
  const barW = Math.min(16, Math.floor((slot * 0.7 - 4) / CHART_BODIES.length));

  let grid = "", ticks = "";
  for (let h = 60; h <= maxMin; h += 60) {
    const gy = (top + plotH - scale(h)).toFixed(1);
    grid += `<line x1="${left}" x2="${W - right}" y1="${gy}" y2="${gy}"/>`;
    ticks += `<text class="chart-tick" x="${left - 6}" y="${+gy + 3}" text-anchor="end">${h / 60} h</text>`;
  }

  let bars = "";
  years.forEach((yr, yi) => {
    const cx = left + slot * (yi + 0.5);
    const present = CHART_BODIES.filter(b => med[yr][b.id] !== undefined);
    const groupW = present.length * barW + (present.length - 1) * 2;
    present.forEach((b, bi) => {
      const bx = Math.round(cx - groupW / 2 + bi * (barW + 2));
      const h = scale(med[yr][b.id]);
      bars += `<path class="mb-bar" data-yr="${yr}" data-b="${b.id}" d="${capRect(bx, top + plotH - h, barW, h)}" fill="${b.color}"/>`;
    });
    ticks += `<text class="chart-tick" x="${cx.toFixed(1)}" y="${H - 6}" text-anchor="middle">${yr}</text>`;
  });

  el.innerHTML = `<svg class="chart" width="${W}" height="${H}" role="img" aria-label="Mediandauer der Sitzungen pro Jahr und Gremium">
    <g class="chart-grid">${grid}</g>${ticks}${bars}</svg>`;

  el.querySelectorAll(".mb-bar").forEach(bar => {
    const yr = bar.dataset.yr, bid = bar.dataset.b;
    const b = CHART_BODIES.find(cb => cb.id === bid);
    bar.addEventListener("mouseenter", evt => chartTipShow(evt,
      `<strong>${b.label} ${yr}</strong><br>Median ${formatDuration(med[yr][bid])} (${counts[yr][bid]} Sitzung${counts[yr][bid] > 1 ? "en" : ""})`));
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
    return `<tr>
      <td>${yr}</td>
      <td>${inYear.length}</td>
      <td>${Math.round(timed.reduce((s, e) => s + e.min, 0) / 60)} Std.</td>
      <td>${srMins.length ? formatDuration(median(srMins)) : "–"}</td>
    </tr>`;
  }).join("");

  const open = entries.filter(e => e.min === null).length;
  const details = document.createElement("details");
  details.className = "stats-table";
  details.innerHTML = `
    <summary><svg class="icon"><use href="#i-table_rows"/></svg> Daten als Tabelle</summary>
    <table>
      <thead><tr><th>Jahr</th><th>Sitzungen</th><th>Gesamtdauer</th><th>Stadtrat im Median</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
    ${open ? `<div class="chart-foot">${open} Sitzung${open > 1 ? "en" : ""} ohne erfasste Endzeit, nicht in den Dauern enthalten.</div>` : ""}`;
  return details;
}

// Charts sind auf Containerbreite gezeichnet, bei Größenänderung neu aufbauen
let statsResizeTimer;
// Ehemals frei laufende Verdrahtung aus app.js, unverändert.
export function initStatistik() {
  window.addEventListener("resize", () => {
    const path = (window.location.hash.slice(1) || "/").split("?")[0];
    if (path !== "/statistik") return;
    clearTimeout(statsResizeTimer);
    statsResizeTimer = setTimeout(route, 150);
  });
}

export { renderStatistik, renderDatenlage, renderPresse };
