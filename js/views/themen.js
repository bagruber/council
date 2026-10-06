// Themen-Tab: Startseite, Themenfelder, Dossiers mit Zeitstrahl — und die
// Bausteine (Brotkrumen, Presse-Links, Kategorie-Chips), die auch andere
// Views einbetten.
import {
  topics, votes, tagMap, topicMap, voteMap,
  sessionMap, pressMap, mediaMap, bestand,
} from "../daten.js";
import { formatDate, kategorieTon } from "../hilfen.js";
import { syncTagPills } from "../suche.js";
import { renderVoteBlock } from "./voten.js";
import { Council } from "../core.js";
import { html, roh } from "../html.js";

const main = document.getElementById("main");

function bestandZeile(b) {
  document.getElementById("themen-bestand").textContent =
    `${b.sitzungen} Sitzungen, ${b.vollstaendig} davon mit Niederschrift`;
}

function renderHome() {
  syncTagPills([]);
  const b = bestand();
  bestandZeile(b);

  const stunden = Math.round(b.minuten / 60);

  // Die Zahlen zum Bestand stehen oben, aber zugeklappt. Sie ordnen ein,
  // was folgt — dafür muessen sie vor den Themen stehen. Aufgeklappt
  // wuerden sie die Themen unter die Falz druecken, und die sind der
  // eigentliche Einstieg.
  const meta = document.createElement("details");
  meta.className = "home-meta";
  meta.innerHTML = html`
    <summary>
      <svg class="icon"><use href="#i-insights"/></svg>
      <span class="home-meta-title">Zahlen zum Bestand</span>
      <span class="home-meta-hint">${b.sitzungen} Sitzungen · ${b.vollstaendig} mit Niederschrift · ${b.presse} Artikel</span>
    </summary>`;

  [
    { href: "#/statistik", icon: "insights", title: "Sitzungsstatistik",
      sub: `${b.sitzungen} Sitzungen · ${stunden} Stunden seit Mai 2020` },
    { href: "#/datenlage", icon: "fact_check", title: "Datenlage",
      sub: `${b.vollstaendig} von ${b.sitzungen} Sitzungen mit Niederschrift` },
    { href: "#/presse", icon: "description", title: "Presseschau",
      sub: `${b.presse} verlinkte Zeitungsartikel` },
  ].forEach(t => {
    const teaser = document.createElement("a");
    teaser.className = "stats-teaser";
    teaser.href = t.href;
    teaser.innerHTML = html`
      <svg class="icon"><use href="#i-${t.icon}"/></svg>
      <div>
        <div class="stats-teaser-title">${t.title}</div>
        <div class="stats-teaser-sub">${t.sub}</div>
      </div>
      <svg class="icon"><use href="#i-chevron_right"/></svg>`;
    meta.appendChild(teaser);
  });
  main.appendChild(meta);

  const heading = document.createElement("p");
  heading.className = "section-heading";
  heading.textContent = "Alle Themen";
  main.appendChild(heading);
  renderTopicList(topics);
}

function renderFilteredTopics(tagIds) {
  syncTagPills(tagIds);
  bestandZeile(bestand());
  const filtered = topics.filter(t => tagIds.some(id => t.tags.includes(id)));
  const label = tagIds.map(id => tagMap[id].name).join(", ");
  const heading = document.createElement("p");
  heading.className = "section-heading";
  heading.textContent = "Themen: " + label;
  main.appendChild(heading);

  // Bei genau einem Filter führt der Weg weiter aufs Feld — dort stehen auch
  // die Beschlüsse, die es zu keinem Dossier gebracht haben. Der Weg steht
  // über der Liste, nicht darunter (16.09.2026).
  if (tagIds.length === 1) {
    const t = tagMap[tagIds[0]];
    const ton = kategorieTon(t.color || "#888888");
    const knopf = document.createElement("a");
    knopf.className = "feld-knopf";
    knopf.href = "#/feld/" + tagIds[0];
    knopf.style.setProperty("--feld-hell", ton.flaeche);
    knopf.style.setProperty("--feld-text", ton.text);
    knopf.innerHTML = html`${klecks(tagIds[0])}<span><b>Zum Themenfeld ${
      t.name}</b><small>Dossiers und einzelne Beschlüsse</small></span><svg class="icon" aria-hidden="true"><use href="#i-chevron_right"/></svg>`;
    main.appendChild(knopf);
  }

  renderTopicList(filtered);

}

function categoryChip(tid, asLink) {
  const t = tagMap[tid];
  if (!t) return html`<span class="cat-line">${tid}</span>`;
  const color = kategorieTon(t.color || "#888888").text;
  const inner = html`${t.icon && html`<svg class="icon" aria-hidden="true"><use href="#i-${t.icon}"/></svg>`}<span>${t.name}</span>`;
  // In Karten muss die Zeile ein span bleiben, verschachtelte Links sind ungültig.
  return asLink
    ? html`<a class="cat-line" href="#/feld/${tid}" style="--cat-color:${color}">${inner}</a>`
    : html`<span class="cat-line" style="--cat-color:${color}">${inner}</span>`;
}

// Klecks nur in den Köpfen von Themenfeld und Dossier, nie in Listen.
const KLECKS = "M25 3.5c8.6.3 17.8 5.2 19.2 14.6 1.5 9.8-4 21.5-14.4 24.9C19.7 46.3 6.6 41.5 4.3 30.7 2 19.6 12.2 3 25 3.5z";

function klecks(tid) {
  const t = tagMap[tid];
  if (!t || !t.icon) return "";
  const ton = kategorieTon(t.color || "#888888");
  return html`<span class="klecks" style="--klecks-flaeche:${ton.flaeche};--klecks-ton:${
    ton.text}" aria-hidden="true"><svg viewBox="0 0 48 48"><path d="${KLECKS}"/></svg><svg class="icon"><use href="#i-${t.icon}"/></svg></span>`;
}

function renderTopicList(list) {
  const wrap = document.createElement("div");
  wrap.className = "topic-list";
  list.forEach(topic => {
    const card = document.createElement("a");
    card.className = "topic-card";
    card.href = "#/topic/" + topic.id;
    card.innerHTML = html`
      <div class="topic-categories">${(topic.tags || []).map(t => categoryChip(t))}</div>
      <h3>${topic.title}</h3>
      <div class="topic-summary">${topic.summary}</div>`;
    wrap.appendChild(card);
  });
  main.appendChild(wrap);
}

// -- Topic detail --

// Pfad statt Zurück-Pfeil: er sagt nicht nur, wo es zurückgeht, sondern
// auch, wo man gerade ist. Der letzte Eintrag ist die aktuelle Seite.
// Nur Feld und Dossier tragen ihn — sie sind die einzigen Seiten mit einem
// festen Platz in einer Hierarchie. Alles andere ist aus mehreren Richtungen
// erreichbar und bekommt den Zurück-Pfeil (backLink in routing.js).
function breadcrumb(items) {
  const nav = document.createElement("nav");
  nav.className = "crumbs";
  nav.setAttribute("aria-label", "Pfad");
  nav.innerHTML = html`${items.filter(Boolean).map((c, i) =>
    html`${i ? roh('<span aria-hidden="true">›</span>') : ""}<a href="${c.href}">${c.label}</a>`)}`;
  return nav;
}

const tlIcons = {
  proposal: "description",
  committee: "groups",
  milestone: "flag",
};

function renderPressLinks(pressArr) {
  if (!pressArr || !pressArr.length) return null;
  const wrap = document.createElement("div");
  wrap.className = "press-links";
  pressArr.forEach(ref => {
    const p = typeof ref === "string" ? pressMap[ref] : ref;
    if (!p) return;
    const src = mediaMap[p.media];
    if (!src) return;
    const a = document.createElement("a");
    a.className = "press-link";
    a.href = p.url;
    a.target = "_blank";
    a.rel = "noopener";
    a.title = p.title || src.name;
    a.setAttribute("aria-label", p.title || ("Artikel bei " + src.name));
    a.style.background = src.color;
    a.innerHTML = html`<img src="${src.logo}" alt="${src.name}">`;
    wrap.appendChild(a);
  });
  return wrap;
}

// Feldseite — die zehn Kategorien aus tags.json als Einstieg. Sie sammelt,
// sie erzählt nicht: die Dossiers des Felds und darunter die Einzelbeschlüsse,
// die es nie zu einem Dossier gebracht haben. Ohne diese Ebene wären das
// hunderte Abstimmungen, die nirgends auftauchen.
function renderField(fieldId) {
  const field = tagMap[fieldId];
  if (!field) { main.innerHTML = html`<p>Feld nicht gefunden.</p>`; return; }


  const dossiers = topics.filter(t => t.field === fieldId || (t.tags || []).includes(fieldId));
  const ids = new Set(dossiers.map(t => t.id));
  const loose = votes
    .filter(v => !(v.topicIds || []).length)
    .filter(v => voteInField(v, fieldId))
    .sort((a, b) => b.date.localeCompare(a.date));

  // Feldseiten tragen ein Band im tiefen Ton ihrer Themenfarbe, Dossiers den
  // hellen Grund. So ist auf einen Blick klar, ob man in einer Übersicht steht
  // oder in einer Sache.
  const header = document.createElement("div");
  header.className = "topic-header topic-header--field band";
  header.style.setProperty("--band-flaeche", kategorieTon(field.color || "#888888").tief);
  header.innerHTML = html`
    <div class="dossier-meta">
      <span class="dossier-type"><svg class="icon"><use href="#i-${field.icon}"/></svg>Themenfeld</span>
      <span class="dossier-count">${dossiers.length} Dossiers · ${loose.length} einzelne Beschlüsse</span>
    </div>
    <div class="topic-title">${klecks(fieldId)}<h1>${field.name}</h1></div>`;
  header.prepend(breadcrumb([{ label: "Themen", href: "#/" }]));
  main.appendChild(header);

  if (dossiers.length) {
    const sec = document.createElement("div");
    sec.innerHTML = html`<h2 class="section-label">Dossiers</h2>`;
    main.appendChild(sec);
    renderTopicList(dossiers);
  }

  if (loose.length) {
    const box = document.createElement("div");
    box.className = "field-loose";
    box.innerHTML = html`<h2 class="section-label">Einzelne Beschlüsse</h2><p class="figures-note">Entscheidungen in diesem Feld, die für sich stehen
         und (noch) zu keinem Dossier gehören.</p>${loose.slice(0, 60).map(v => html`
          <a class="field-vote" href="#/session/${v.sessionId}">
            <span class="fv-date">${formatDate(v.date)}</span>
            <span class="fv-title">${v.title}</span>
          </a>`)}${loose.length > 60 && html`<p class="figures-note">… und ${loose.length - 60} weitere.</p>`}`;
    main.appendChild(box);
  }
}

// Ein loses Votum gehört zu einem Feld, wenn eine Sitzung es einem Dossier
// dieses Felds zugeordnet hat oder der Titel die Feld-Stichwörter trifft.
const FIELD_WORDS = {
  mobility:       /verkehr|park|straße|radweg|fahrrad|tempo|bus|bahn|kreisverkehr|fußgänger|stellplatz/i,
  building:       /bebauungsplan|b-plan|einvernehmen|bauvorhaben|neubau|anbau|wohnein|vorbescheid|flächennutzung|sanierung/i,
  sports:         /sport|verein|bad\b|schwimm|eisstadion|halle|turn/i,
  culture:        /kultur|museum|denkmal|stalag|baracke|bücherei|musikschule|jazz/i,
  environment:    /umwelt|natur|klima|energie|photovoltaik|pv |wind|wärme|grün|baum|wasser|abwasser|kläranlage/i,
  education:      /schule|kita|kindergarten|kinderkrippe|kinderhaus|bildung|jugend/i,
  social:         /sozial|senior|asyl|integration|gesundheit|pflege/i,
  budget:         /haushalt|gebühr|steuer|kredit|zuschuss|hebesatz|jahresabschluss|entlastung/i,
  economy:        /gewerbe|wirtschaft|markt|verkaufsoffen|firma|gmbh/i,
  infrastructure: /kanal|leitung|beleuchtung|strom|breitband|gigabit|feuerwehr|bauhof|friedhof/i,
};

function voteInField(vote, fieldId) {
  const rx = FIELD_WORDS[fieldId];
  return rx ? rx.test(vote.title) : false;
}

// Dossier-Typen. Sie steuern nur den Kopf — die Timeline darunter ist für
// alle gleich, weil sie in allen Fällen dasselbe zeigt: was wann entschieden
// wurde. Was sich unterscheidet, ist die Frage, die man oben beantwortet haben
// will: bei einem Vorhaben „wie weit ist das", bei einer Einrichtung „was gilt
// gerade", bei einem Gebiet „was gehört dazu".
const DOSSIER_TYPE = {
  vorhaben:    { label: "Vorhaben",    icon: "flag" },
  konflikt:    { label: "Streitfall",  icon: "swap_horiz" },
  einrichtung: { label: "Einrichtung", icon: "account_balance" },
  regelwerk:   { label: "Regelwerk",   icon: "description" },
  gebiet:      { label: "Gebiet",      icon: "architecture" },
  zyklus:      { label: "Wiederkehrend", icon: "schedule" },
};

function renderDossierHead(topic) {
  const t = DOSSIER_TYPE[topic.type];
  if (!t) return "";
  const bits = [html`<span class="dossier-type"><svg class="icon"><use href="#i-${t.icon}"/></svg>${t.label}</span>`];

  const dates = topic.history.map(h => h.date).sort();
  if (dates.length) {
    const from = dates[0].slice(0, 4);
    const to = dates[dates.length - 1].slice(0, 4);
    const span = from === to ? from : `${from}–${to}`;
    bits.push(topic.status === "abgeschlossen"
      ? html`<span class="dossier-status done">abgeschlossen ${to}</span>`
      : topic.status === "laufend"
        ? html`<span class="dossier-status open">läuft seit ${from}</span>`
        : html`<span class="dossier-status">${span}</span>`);
  }

  // Die Zuordnung steht an zwei Stellen: als Feld am Votum und als voteId in
  // der Historie. Das Feld ist die vollstaendige Zuordnung, die Historie die
  // kuratierte Auswahl -- aber ein Votum kann in zwei Dossiers vorkommen, und
  // das Feld ist einwertig. Gezaehlt wird deshalb die Vereinigung.
  const n = new Set([
    ...votes.filter(v => (v.topicIds || []).includes(topic.id)).map(v => v.id),
    ...(topic.history || []).map(h => h.voteId).filter(Boolean),
  ]).size;
  if (n) bits.push(html`<span class="dossier-count">${n} Abstimmung${n === 1 ? "" : "en"}</span>`);

  const parent = topic.partOf && topicMap[topic.partOf];
  if (parent) bits.push(html`<a class="dossier-parent" href="#/topic/${parent.id}">Teil von ${parent.title}</a>`);

  return html`<div class="dossier-meta">${bits}</div>`;
}

// Kompakte Übersicht für Größen, die sich regelmäßig ändern — Gebühren,
// Tarife, Förderhöhen. Steht im Kopf, damit nicht die jüngste Anpassung
// die ganze Geschichte anführt.
function renderFigures(topic) {
  const f = topic.figures;
  if (!f || !f.rows || !f.rows.length) return null;
  const box = document.createElement("div");
  box.className = "figures";
  const rows = f.rows.slice().sort((a, b) => b.date.localeCompare(a.date));
  box.innerHTML = html`
    <h2 class="section-label">${f.title}</h2>
    <table class="figures-table"><tbody>${rows.map((r, i) => html`
      <tr${i === 0 ? roh(' class="current"') : ""}${r.voteId ? html` data-vote="${r.voteId}" tabindex="0"` : ""}>
        <td class="fig-date">${formatDate(r.date)}</td>
        <td class="fig-label">${r.label}</td>
        ${r.value && html`<td class="fig-value">${r.value}</td>`}
      </tr>`)}</tbody></table>
    ${f.note && html`<p class="figures-note">${f.note}</p>`}`;

  // Die Zeilen zeigen auf Beschlüsse, die weiter unten im Zeitstrahl stehen.
  // Ein Hash-Anker geht nicht — der Hash trägt hier die Route.
  const jump = e => {
    const tr = e.target.closest("tr[data-vote]");
    if (!tr || (e.key && e.key !== "Enter")) return;
    const target = document.getElementById("e-" + tr.dataset.vote);
    if (!target) return;
    target.scrollIntoView({ block: "center" });
    target.classList.remove("tl-flash");
    void target.offsetWidth;
    target.classList.add("tl-flash");
  };
  box.addEventListener("click", jump);
  box.addEventListener("keydown", jump);
  return box;
}

function renderTopic(id) {
  const topic = topicMap[id];
  if (!topic) { main.innerHTML = html`<p>Thema nicht gefunden.</p>`; return; }

  main.appendChild(breadcrumb([
    { label: "Themen", href: "#/" },
    topic.field && tagMap[topic.field]
      ? { label: tagMap[topic.field].name, href: "#/feld/" + topic.field }
      : null,
  ]));

  const header = document.createElement("div");
  header.className = "topic-header";
  header.innerHTML = html`
    ${renderDossierHead(topic)}
    <div class="topic-title">${klecks((topic.tags || [])[0])}<h1>${topic.title}</h1></div>
    <div class="topic-summary">${topic.summary}</div>
    <div class="topic-tags">${(topic.tags || []).map(t => categoryChip(t, true))}</div>`;
  main.appendChild(header);

  const figures = renderFigures(topic);
  if (figures) main.appendChild(figures);

  // Gebiete führen die Vorhaben auf, die in ihnen liegen
  const children = topics.filter(t => t.partOf === topic.id);
  if (children.length) {
    const box = document.createElement("div");
    box.className = "dossier-children";
    box.innerHTML = html`<h2 class="section-label">Vorhaben in diesem Gebiet</h2>${
      children.map(c => html`<a href="#/topic/${c.id}">${c.title}</a>`)}`;
    main.appendChild(box);
  }

  if (topic.image) {
    const img = document.createElement("img");
    img.className = "topic-image";
    img.src = topic.image;
    img.alt = topic.title;
    main.appendChild(img);
  }

  const timeline = document.createElement("div");
  timeline.className = "timeline";

  topic.history.forEach(entry => {
    const el = document.createElement("div");
    el.className = "tl-entry";
    if (entry.voteId) el.id = "e-" + entry.voteId;

    // Hervorgehoben wird, was tatsächlich eine Weggabelung war: Meilensteine,
    // abgelehnte Anträge und Abstimmungen, die nicht einstimmig durchgingen.
    // `key: true` im Datensatz übersteuert das.
    const v = entry.voteId && voteMap[entry.voteId];
    const pivotal = entry.key === true
      || entry.type === "milestone"
      || (v && (v.result === "rejected" || !Council.isUnanimous(v)));
    if (pivotal) el.classList.add("tl-key");

    let dotClass = entry.type;
    let iconName = tlIcons[entry.type];
    if (entry.type === "vote" && entry.voteId && voteMap[entry.voteId]) {
      const rejected = voteMap[entry.voteId].result === "rejected";
      dotClass = rejected ? "vote-rejected" : "vote-approved";
      iconName = rejected ? "cancel" : "check_circle";
    } else if (entry.type === "vote") {
      dotClass = "vote-approved";
      iconName = "check_circle";
    }

    const dot = document.createElement("div");
    dot.className = "tl-dot " + dotClass;
    if (iconName) dot.innerHTML = html`<svg class="icon"><use href="#i-${iconName}"/></svg>`;
    el.appendChild(dot);

    const dateEl = document.createElement("div");
    dateEl.className = "tl-date";
    dateEl.textContent = formatDate(entry.date);
    el.appendChild(dateEl);

    const h3 = document.createElement("h3");
    h3.textContent = entry.title;
    el.appendChild(h3);

    const p = document.createElement("p");
    p.textContent = entry.text;
    el.appendChild(p);

    if (entry.image) {
      const img = document.createElement("img");
      img.className = "tl-image";
      img.src = entry.image.includes("/") ? entry.image : "img/topics/" + entry.image;
      img.alt = entry.title;
      img.loading = "lazy";
      el.appendChild(img);
    }

    if (entry.voteId && voteMap[entry.voteId]) {
      const voteEl = document.createElement("div");
      voteEl.className = "tl-vote-inline";
      renderVoteBlock(voteEl, voteMap[entry.voteId]);
      el.appendChild(voteEl);
    }

    if (entry.sessionId && sessionMap[entry.sessionId]) {
      const link = document.createElement("a");
      link.className = "tl-session-link";
      link.href = "#/session/" + entry.sessionId;
      link.innerHTML = html`<svg class="icon"><use href="#i-open_in_new"/></svg> ${sessionMap[entry.sessionId].title}`;
      el.appendChild(link);
    }

    const pressEl = renderPressLinks(entry.press);
    if (pressEl) el.appendChild(pressEl);

    timeline.appendChild(el);
  });

  main.appendChild(timeline);
}

export { renderHome, renderFilteredTopics, renderField, renderTopic,
         renderPressLinks, DOSSIER_TYPE };
