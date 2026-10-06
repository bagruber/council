// Presseschau: alle verlinkten Zeitungsartikel, und woran sie hängen.
import {
  sessions, topics, members, pressData, mediaMap,
} from "../daten.js";
import { formatDate } from "../hilfen.js";
import { backLink } from "../routing.js";
import { html } from "../html.js";

const main = document.getElementById("main");

// -- Presseschau --

// Presseartikel hängen an Sitzungen, Dossiers und Anträgen. Für die Übersicht
// wird der Weg umgedreht: je Artikel, woran er hängt.
function pressContext() {
  const ctx = {};
  // Ein Artikel hängt oft an der Sitzung und zusätzlich an einem ihrer Punkte.
  // In der Presseschau ist das derselbe Verweis und soll nur einmal stehen.
  const add = (ids, entry) => (ids || []).forEach(id => {
    const list = ctx[id] || (ctx[id] = []);
    if (!list.some(e => e.href === entry.href && e.kind === entry.kind)) list.push(entry);
  });
  sessions.forEach(s => {
    add(s.press, { kind: "Sitzung", label: s.title, href: "#/session/" + s.id });
    (s.agenda || []).forEach(a =>
      add(a.press, { kind: "Sitzung", label: s.title, href: "#/session/" + s.id }));
  });
  topics.forEach(t => (t.history || []).forEach(h =>
    add(h.press, { kind: "Dossier", label: t.title, href: "#/topic/" + t.id })));
  members.forEach(m => ((m.profile || {}).motions || []).forEach(mo =>
    add(mo.press, { kind: "Antrag", label: mo.title, href: "#/member/" + m.id })));
  return ctx;
}

function renderPresse() {
  main.appendChild(backLink("Übersicht", "#/"));

  const ctx = pressContext();
  const arts = [...pressData].sort((a, b) => b.date.localeCompare(a.date));

  const header = document.createElement("div");
  header.className = "topic-header";
  header.innerHTML = html`
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
    row.innerHTML = html`
      <span class="press-medium" style="background:${src.color}">${src.logo
        ? html`<img src="${src.logo}" alt="${src.name}">` : src.name}</span>
      <div>
        <a class="press-title" href="${p.url}" target="_blank" rel="noopener">${p.title}
          <svg class="icon"><use href="#i-open_in_new"/></svg></a>
        <div class="press-meta">${formatDate(p.date)} · ${src.name}</div>
        <div class="press-refs">${(ctx[p.id] || [])
          .map(c => html`<a href="${c.href}"><span class="press-ref-kind">${c.kind}</span>${c.label}</a>`)}</div>
      </div>`;
    list.appendChild(row);
  });
  main.appendChild(list);
}

export { renderPresse };
