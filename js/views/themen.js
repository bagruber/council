// Themen-Tab: Startseite, Themenfelder, Dossiers mit Zeitstrahl — und die
// Bausteine (Brotkrumen, Presse-Links, Kategorie-Chips), die auch andere
// Views einbetten.
import {
  topics, votes, sessionLengths, pressData, tagMap, topicMap, voteMap,
  sessionMap, pressMap, mediaMap, sessionRegister, lengthMin,
} from "../daten.js";
import { formatDate } from "../hilfen.js";
import { setChrome } from "../routing.js";
import { syncTagPills } from "../suche.js";
import { renderVoteBlock } from "./voten.js";

const main = document.getElementById("main");

function renderHome() {
  syncTagPills([]);

  const totalH = Math.round(sessionLengths.reduce((s, l) => s + (lengthMin(l) || 0), 0) / 60);
  const reg = sessionRegister();
  const withProtocol = reg.filter(r => r.session).length;

  // Die Zahlen zum Bestand stehen oben, aber zugeklappt. Sie ordnen ein,
  // was folgt — dafür muessen sie vor den Themen stehen. Aufgeklappt
  // wuerden sie die Themen unter die Falz druecken, und die sind der
  // eigentliche Einstieg.
  const meta = document.createElement("details");
  meta.className = "home-meta";
  meta.innerHTML = `
    <summary>
      <svg class="icon"><use href="#i-insights"/></svg>
      <span class="home-meta-title">Zahlen zum Bestand</span>
      <span class="home-meta-hint">${sessionLengths.length} Sitzungen · ${withProtocol} von ${reg.length} mit Niederschrift · ${pressData.length} Artikel</span>
    </summary>`;

  [
    { href: "#/statistik", icon: "insights", title: "Sitzungsstatistik",
      sub: `${sessionLengths.length} Sitzungen · ${totalH} Stunden seit Mai 2020` },
    { href: "#/datenlage", icon: "fact_check", title: "Datenlage",
      sub: `${withProtocol} von ${reg.length} Sitzungen mit Niederschrift` },
    { href: "#/presse", icon: "description", title: "Presseschau",
      sub: `${pressData.length} verlinkte Zeitungsartikel` },
  ].forEach(t => {
    const teaser = document.createElement("a");
    teaser.className = "stats-teaser";
    teaser.href = t.href;
    teaser.innerHTML = `
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
  const filtered = topics.filter(t => tagIds.some(id => t.tags.includes(id)));
  const label = tagIds.map(id => tagMap[id].name).join(", ");
  const heading = document.createElement("p");
  heading.className = "section-heading";
  heading.textContent = "Themen: " + label;
  main.appendChild(heading);
  renderTopicList(filtered);

  // Bei genau einem Filter führt der Weg weiter aufs Feld — dort stehen auch
  // die Beschlüsse, die es zu keinem Dossier gebracht haben.
  if (tagIds.length === 1) {
    const more = document.createElement("a");
    more.className = "field-more";
    more.href = "#/feld/" + tagIds[0];
    more.textContent = `Alles zu ${tagMap[tagIds[0]].name} — auch einzelne Beschlüsse`;
    main.appendChild(more);
  }
}

function categoryChip(tid, asLink) {
  const t = tagMap[tid];
  if (!t) return `<span class="cat-chip">${tid}</span>`;
  const color = t.color || "#888";
  const icon = t.icon ? `<svg class="icon cat-chip-icon"><use href="#i-${t.icon}"/></svg>` : "";
  const inner = `${icon}<span>${t.name}</span>`;
  // In Karten muss der Chip ein span bleiben — verschachtelte Links sind ungültig.
  return asLink
    ? `<a class="cat-chip" href="#/feld/${tid}" style="--cat-color:${color}">${inner}</a>`
    : `<span class="cat-chip" style="--cat-color:${color}">${inner}</span>`;
}

function renderTopicList(list) {
  const wrap = document.createElement("div");
  wrap.className = "topic-list";
  list.forEach(topic => {
    const card = document.createElement("a");
    card.className = "topic-card";
    card.href = "#/topic/" + topic.id;
    card.innerHTML = `
      <div class="topic-categories">${(topic.tags || []).map(categoryChip).join("")}</div>
      <h3>${topic.title}</h3>
      <div class="topic-summary">${topic.summary}</div>`;
    wrap.appendChild(card);
  });
  main.appendChild(wrap);
}

// -- Topic detail --

// Pfad statt Zurück-Pfeil: er sagt nicht nur, wo es zurückgeht, sondern
// auch, wo man gerade ist. Der letzte Eintrag ist die aktuelle Seite.
function breadcrumb(items) {
  const nav = document.createElement("nav");
  nav.className = "crumbs";
  nav.setAttribute("aria-label", "Pfad");
  nav.innerHTML = items.filter(Boolean)
    .map(c => `<a href="${c.href}">${c.label}</a>`)
    .join('<span aria-hidden="true">›</span>');
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
    a.innerHTML = `<img src="${src.logo}" alt="${src.name}">`;
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
  if (!field) { main.innerHTML = "<p>Feld nicht gefunden.</p>"; return; }

  setChrome("feld");
  main.appendChild(breadcrumb([{ label: "Themen", href: "#/" }]));

  const dossiers = topics.filter(t => t.field === fieldId || (t.tags || []).includes(fieldId));
  const ids = new Set(dossiers.map(t => t.id));
  const loose = votes
    .filter(v => !v.topicId)
    .filter(v => voteInField(v, fieldId))
    .sort((a, b) => b.date.localeCompare(a.date));

  // Feldseiten tragen das dunkle Wappenrot, Dossiers den hellen Grund.
  // So ist auf einen Blick klar, ob man in einer Übersicht steht oder in
  // einer Sache — ohne dass es irgendwo geschrieben stehen muss.
  const header = document.createElement("div");
  header.className = "topic-header topic-header--field";
  header.innerHTML = `
    <div class="dossier-meta">
      <span class="dossier-type"><svg class="icon"><use href="#i-${field.icon}"/></svg>Themenfeld</span>
      <span class="dossier-count">${dossiers.length} Dossiers · ${loose.length} einzelne Beschlüsse</span>
    </div>
    <h1>${field.name}</h1>
    <div class="rainbow-stripe" aria-hidden="true">${"<span></span>".repeat(9)}</div>`;
  main.appendChild(header);

  if (dossiers.length) {
    const sec = document.createElement("div");
    sec.innerHTML = `<h2 class="section-label">Dossiers</h2>`;
    main.appendChild(sec);
    renderTopicList(dossiers);
  }

  if (loose.length) {
    const box = document.createElement("div");
    box.className = "field-loose";
    box.innerHTML = `<h2 class="section-label">Einzelne Beschlüsse</h2>`
      + `<p class="figures-note">Entscheidungen in diesem Feld, die für sich stehen
         und (noch) zu keinem Dossier gehören.</p>`
      + loose.slice(0, 60).map(v => `
          <a class="field-vote" href="#/session/${v.sessionId}">
            <span class="fv-date">${formatDate(v.date)}</span>
            <span class="fv-title">${v.title}</span>
          </a>`).join("")
      + (loose.length > 60 ? `<p class="figures-note">… und ${loose.length - 60} weitere.</p>` : "");
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
  const bits = [`<span class="dossier-type"><svg class="icon"><use href="#i-${t.icon}"/></svg>${t.label}</span>`];

  const dates = topic.history.map(h => h.date).sort();
  if (dates.length) {
    const from = dates[0].slice(0, 4);
    const to = dates[dates.length - 1].slice(0, 4);
    const span = from === to ? from : `${from}–${to}`;
    bits.push(topic.status === "abgeschlossen"
      ? `<span class="dossier-status done">abgeschlossen ${to}</span>`
      : topic.status === "laufend"
        ? `<span class="dossier-status open">läuft seit ${from}</span>`
        : `<span class="dossier-status">${span}</span>`);
  }

  const n = votes.filter(v => v.topicId === topic.id).length;
  if (n) bits.push(`<span class="dossier-count">${n} Abstimmung${n === 1 ? "" : "en"}</span>`);

  const parent = topic.partOf && topicMap[topic.partOf];
  if (parent) bits.push(`<a class="dossier-parent" href="#/topic/${parent.id}">Teil von ${parent.title}</a>`);

  return `<div class="dossier-meta">${bits.join("")}</div>`;
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
  box.innerHTML = `
    <h2 class="section-label">${f.title}</h2>
    <table class="figures-table"><tbody>${rows.map((r, i) => `
      <tr${i === 0 ? ' class="current"' : ""}${r.voteId ? ` data-vote="${r.voteId}" tabindex="0"` : ""}>
        <td class="fig-date">${formatDate(r.date)}</td>
        <td class="fig-label">${r.label}</td>
        ${r.value ? `<td class="fig-value">${r.value}</td>` : ""}
      </tr>`).join("")}</tbody></table>
    ${f.note ? `<p class="figures-note">${f.note}</p>` : ""}`;

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
  if (!topic) { main.innerHTML = "<p>Thema nicht gefunden.</p>"; return; }

  main.appendChild(breadcrumb([
    { label: "Themen", href: "#/" },
    topic.field && tagMap[topic.field]
      ? { label: tagMap[topic.field].name, href: "#/feld/" + topic.field }
      : null,
  ]));

  const header = document.createElement("div");
  header.className = "topic-header";
  header.innerHTML = `
    ${renderDossierHead(topic)}
    <h1>${topic.title}</h1>
    <div class="topic-summary">${topic.summary}</div>
    <div class="topic-tags">${(topic.tags || []).map(t => categoryChip(t, true)).join("")}</div>`;
  main.appendChild(header);

  const figures = renderFigures(topic);
  if (figures) main.appendChild(figures);

  // Gebiete führen die Vorhaben auf, die in ihnen liegen
  const children = topics.filter(t => t.partOf === topic.id);
  if (children.length) {
    const box = document.createElement("div");
    box.className = "dossier-children";
    box.innerHTML = `<h2 class="section-label">Vorhaben in diesem Gebiet</h2>`
      + children.map(c => `<a href="#/topic/${c.id}">${c.title}</a>`).join("");
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
    if (iconName) dot.innerHTML = `<svg class="icon"><use href="#i-${iconName}"/></svg>`;
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
      link.innerHTML = '<svg class="icon"><use href="#i-open_in_new"/></svg> ' + sessionMap[entry.sessionId].title;
      el.appendChild(link);
    }

    const pressEl = renderPressLinks(entry.press);
    if (pressEl) el.appendChild(pressEl);

    timeline.appendChild(el);
  });

  main.appendChild(timeline);
}

export { renderHome, renderFilteredTopics, renderField, renderTopic,
         breadcrumb, renderPressLinks, DOSSIER_TYPE };
