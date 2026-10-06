// Werkzeug für die Diagramme der Übersichtsseiten: Farben je Gremium,
// Kartenrahmen, Tooltip, Median.
import { SITZUNGSARTEN } from "../daten.js";
import { monthNames } from "../hilfen.js";
import { html } from "../html.js";

// Diagramme und Register kennen die Sitzung unter ihrer Art (stadtrat/bpu/
// hvfa), nicht unter ihrem Gremium — Label und Farbe kommen aus daten.js.
const chartColor = {};
SITZUNGSARTEN.forEach(a => { chartColor[a.type] = a.color; });

function median(arr) {
  const s = [...arr].sort((a, b) => a - b);
  const mid = s.length >> 1;
  return s.length % 2 ? s[mid] : Math.round((s[mid - 1] + s[mid]) / 2);
}

// Zeitraeume stehen nicht mehr fest im Text. "Wahlperiode 2020-2026" und
// "seit Mai 2020" waren beide falsch, sobald die Daten ueber die Grenzen
// hinausreichten -- und jede neue Sitzung haette sie wieder veralten lassen.
const monat = iso => monthNames[Number(iso.slice(5, 7)) - 1];
const monatJahr = iso => monat(iso) + " " + iso.slice(0, 4);

const chartTip = document.getElementById("tooltip");

function chartTipShow(evt, inhalt) {
  chartTip.innerHTML = inhalt;
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
  return html`<div class="chart-legend">${SITZUNGSARTEN.map(b =>
    html`<span><span class="chart-dot" style="background:${b.color}"></span>${b.label}</span>`)}</div>`;
}

function chartCard(title, foot, drawFn, data, withLegend) {
  const card = document.createElement("div");
  card.className = "chart-card";
  card.innerHTML = html`<h3>${title}</h3>${withLegend && chartLegend()}`;
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

export {
  chartColor, median, monat, monatJahr,
  chartTipShow, chartTipMove, chartTipHide, chartLegend, chartCard,
};
