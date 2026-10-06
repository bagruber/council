// Datenlage: das Sitzungsregister mit dem, was von jeder Sitzung vorliegt,
// und die Herkunftsstufen der Einzelstimmen.
import {
  sessionRegister, bestand, votenVon, tierCounts, dauerMin,
  protocolUrl, isWebauszug, sitzungsart,
} from "../daten.js";
import { formatDate, formatDuration } from "../hilfen.js";
import { backLink } from "../routing.js";
import { html } from "../html.js";
import { chartColor, monatJahr } from "./diagramme.js";

const main = document.getElementById("main");

// -- Datenlage: was liegt zu welcher Sitzung vor --

const TIERS = [
  { key: "explicit", label: "namentlich",    hint: "Die Niederschrift nennt jeden Namen." },
  { key: "implicit", label: "abgeleitet",    hint: "Einstimmig, aus der Anwesenheit erschlossen." },
  { key: "tracked",  label: "mitgeschrieben", hint: "Im Saal vollständig erfasst — Tool oder Mitschrift." },
  { key: "press",    label: "aus Presse",    hint: "Aus einem Zeitungsartikel rekonstruiert." },
  { key: "selbstauskunft", label: "Selbstauskunft", hint: "Aus eigenen Notizen eines Ratsmitglieds rekonstruiert." },
  { key: "sum",      label: "nur Ergebnis",  hint: "Nur die Gesamtzahlen sind bekannt." },
];

// Wie viel Presse liegt zu einer Sitzung vor — am Abend selbst und an
// einzelnen Punkten. Die Zahl ist als Rechercheanzeige gedacht: wo nichts
// steht, lohnt das Nachsehen, wo etwas steht, ist es schon gesichtet.
function pressOfSession(session) {
  if (!session) return { session: 0, tops: 0, total: 0, topsWith: 0, topsVoted: 0 };
  const ids = new Set(session.press || []);
  let topsWith = 0, topsVoted = 0;
  (session.agenda || []).forEach(a => {
    if ((a.voteIds || []).length) topsVoted++;
    if ((a.press || []).length) {
      topsWith++;
      a.press.forEach(id => ids.add(id));
    }
  });
  return { session: (session.press || []).length, tops: topsWith,
           total: ids.size, topsWith, topsVoted };
}

function pressBadge(p) {
  if (!p.total) {
    return html`<span class="reg-presse none" title="Kein Zeitungsartikel verknüpft">–</span>`;
  }
  const anTops = p.topsWith
    ? `, davon ${p.topsWith} von ${p.topsVoted} Punkten zugeordnet`
    : ", noch keinem Punkt zugeordnet";
  return html`<span class="reg-presse" title="${p.total} Artikel${anTops}">${p.total} Presse</span>`;
}

// `filter` schränkt auf eine Herkunftsstufe (explicit/implicit/tracked/press/
// sum) oder eine Erfassungsstufe (protokoll/auszug/keine/presse/ohne-presse) ein.
function renderDatenlage(filter) {
  main.appendChild(backLink("Übersicht", "#/"));

  const b = bestand();
  const reg = sessionRegister();
  const stufe = x => reg.filter(r => r.niederschrift === x);
  const protokoll = stufe("vollständig");
  const auszug = stufe("auszug");
  const erfasst = reg.filter(r => r.niederschrift !== "keine");
  const all = tierCounts(reg.flatMap(votenVon));
  const traceable = b.abstimmungen - all.sum;

  const header = document.createElement("div");
  header.className = "topic-header";
  header.innerHTML = html`
    <h1>Datenlage</h1>
    <div class="topic-summary">Jede öffentliche Sitzung seit ${monatJahr(b.seit)}, und was von ihr vorliegt.
      Gezählt ist, was stattgefunden hat — Sitzungen ohne Niederschrift stehen
      bewusst mit in der Liste, die Lücke gehört zur Auskunft dazu.
      <a href="#/methodik">So entsteht diese Seite</a> erklärt, wie die Angaben
      zustande kommen.</div>`;
  main.appendChild(header);

  const tiles = document.createElement("div");
  tiles.className = "stat-tiles";
  tiles.innerHTML = html`
    <div class="stat-tile"><div class="stat-tile-value">${b.vollstaendig} <small>/ ${b.sitzungen}</small></div><div class="stat-tile-label">Sitzungen mit Niederschrift</div></div>
    <div class="stat-tile"><div class="stat-tile-value">${b.abstimmungen}</div><div class="stat-tile-label">erfasste Abstimmungen</div></div>
    <div class="stat-tile"><div class="stat-tile-value">${Math.round(traceable / b.abstimmungen * 100)} %</div><div class="stat-tile-label">Stimmverhalten nachvollziehbar</div></div>`;
  main.appendChild(tiles);

  // Jede Kennzahl ist ein Filter auf sich selbst. Nochmal draufklicken hebt auf.
  const chip = (key, cls, label, n, hint) =>
    html`<a class="tier-chip ${cls}${filter === key ? " on" : ""}"
        href="#/datenlage${filter === key ? "" : "/" + key}" title="${hint}">${label} <b>${n}</b></a>`;

  const levels = document.createElement("div");
  levels.className = "tier-legend";
  levels.innerHTML = html`${[
    chip("protokoll", "level-protokoll", "Niederschrift", b.vollstaendig,
         "Niederschrift mit Anwesenheitsliste"),
    chip("auszug", "level-auszug", "nur Beschlussauszug", b.auszug,
         "Beschlussauszug der Stadt, ohne Anwesenheitsliste"),
    chip("keine", "level-keine", "nichts veröffentlicht", b.keine,
         "Weder Niederschrift noch Auszug veröffentlicht"),
  ]}`;
  main.appendChild(levels);

  // Presselage getrennt von der Aktenlage: eine Sitzung kann lückenlos
  // protokolliert und trotzdem unbeschrieben sein, und umgekehrt.
  const mitPresse = erfasst.filter(r => pressOfSession(r).total);
  const presse = document.createElement("div");
  presse.className = "tier-legend";
  presse.innerHTML = html`${[
    chip("presse", "level-protokoll", "mit Presseartikel", mitPresse.length,
         "Mindestens ein Zeitungsartikel ist verknüpft"),
    chip("ohne-presse", "level-keine", "ohne Presseartikel",
         erfasst.length - mitPresse.length,
         "Noch kein Artikel verknüpft — hier lohnt die Recherche"),
  ]}`;
  main.appendChild(presse);

  const legend = document.createElement("div");
  legend.className = "tier-legend";
  legend.innerHTML = html`${TIERS.map(t =>
    chip(t.key, "tier-" + t.key, t.label, all[t.key], t.hint))}`;
  main.appendChild(legend);

  // Herkunftsstufe: die Abstimmungen selbst auflisten, nicht die Sitzungen —
  // "elf namentliche Abstimmungen" will man lesen, nicht suchen.
  const tier = TIERS.find(t => t.key === filter);
  if (tier) {
    main.appendChild(tierVoteList(tier, erfasst));
    return;
  }
  const rows = filter === "protokoll"    ? protokoll
             : filter === "auszug"       ? auszug
             : filter === "keine"        ? stufe("keine")
             : filter === "presse"       ? mitPresse
             : filter === "ohne-presse"  ? erfasst.filter(r => !pressOfSession(r).total)
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
      head.innerHTML = html`<th colspan="4">${year}</th>`;
      body.appendChild(head);
    }
    const label = sitzungsart(r.type).label;
    const min = dauerMin(r);
    const dur = min ? formatDuration(min) : r.start ? r.start + " Uhr" : "";
    const voten = votenVon(r);
    const c = tierCounts(voten);
    const bar = voten.length > 0 && html`<span class="tier-bar">${TIERS.filter(t => c[t.key])
          .map(t => html`<span class="tier-${t.key}" style="flex:${c[t.key]}" title="${c[t.key]}× ${t.label}"></span>`)}</span>`;

    const web = isWebauszug(r);
    const doc = r.niederschrift === "keine" ? ""
      : web
        ? ((r.source || {}).url
            ? html`<a class="reg-pdf" href="${r.source.url}" target="_blank" rel="noopener"
                  title="Beschlussauszug der Stadt, ohne Anwesenheitsliste"><svg class="icon"><use href="#i-language"/></svg></a>`
            : "")
        : html`<a class="reg-pdf" href="${protocolUrl(r)}" target="_blank" rel="noopener"
              title="Niederschrift als PDF"><svg class="icon"><use href="#i-description"/></svg></a>`;

    const tr = document.createElement("tr");
    tr.className = r.niederschrift === "keine" ? "register-gap" : web ? "register-partial" : "";
    tr.innerHTML = html`
      <td class="reg-date">${formatDate(r.date)}</td>
      <td class="reg-body"><span class="reg-dot" style="background:${chartColor[r.type]}"></span>${label}</td>
      <td class="reg-dur">${dur}</td>
      <td class="reg-data">${r.agenda
        ? html`<a href="#/session/${r.id}">${voten.length} Abstimmung${
            voten.length === 1 ? "" : "en"}</a>${
            web && html`<span class="reg-flag">ohne Anwesenheitsliste</span>`}${bar}${doc}${pressBadge(pressOfSession(r))}`
        : html`<span class="reg-none">nichts veröffentlicht</span>`}</td>`;
    body.appendChild(tr);
  });
  table.appendChild(body);
  main.appendChild(table);
}

// Alle Abstimmungen einer Herkunftsstufe, nach Sitzung gruppiert
function tierVoteList(tier, erfasst) {
  const wrap = document.createElement("div");
  const hit = r => votenVon(r).filter(v => {
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
    const label = sitzungsart(r.type).label;
    const head = document.createElement("tr");
    head.className = "register-group";
    head.innerHTML = html`<th colspan="2"><a href="#/session/${r.id}"><span class="reg-dot"
      style="background:${chartColor[r.type]}"></span>${formatDate(r.date)} · ${label}</a></th>`;
    body.appendChild(head);
    list.forEach(v => {
      const res = v.type === "named"
        ? `${v.results.yes.length}:${v.results.no.length}`
        : `${v.results.yes}:${v.results.no}`;
      const tr = document.createElement("tr");
      tr.innerHTML = html`<td class="reg-title"><a href="#/session/${r.id}">${v.title}</a></td>
                      <td class="reg-dur">${res}</td>`;
      body.appendChild(tr);
    });
  });
  table.appendChild(body);
  wrap.appendChild(table);
  return wrap;
}

export { renderDatenlage };
