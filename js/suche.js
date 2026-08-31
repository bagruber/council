// Globale Suche über alle Inhaltsarten, Tag-Pillen und die zweite Suche im
// Gremien-Tab. Beide Eingabefelder teilen sich Index und Trefferliste.
import {
  tags, topics, votes, sessions, members, parties, partyMap, isActive,
} from "./daten.js";
import { navigate } from "./routing.js";
import { formatDate } from "./hilfen.js";
import { DOSSIER_TYPE } from "./views/themen.js";
import { factionHistory } from "./views/fraktion.js";

const searchInput = document.getElementById("search");
const dropdown = document.getElementById("search-dropdown");
const tagBar = document.getElementById("tag-bar");

// -- Gremien search --

const gremienSearchInput = document.getElementById("gremien-search");
const gremienDropdown = document.getElementById("gremien-search-dropdown");

function syncTagPills(ids) {
  tagBar.querySelectorAll(".tag-pill").forEach(p =>
    p.classList.toggle("active", ids.includes(p.dataset.tagId)));
}

// Normalise Umlaute & accents so "Ru" matches "Rümelin", "Stoss" matches "Stoß".
// NFD + Diakritika-Strip erledigt ä→a etc., nur ß braucht den Sonderfall.
function searchNorm(s) {
  return (s || "")
    .toLowerCase()
    .replace(/ß/g, "ss")
    .normalize("NFD").replace(/[̀-ͯ]/g, "");
}

// ── Globale Suche ────────────────────────────────────────────────────────
//
// Ein Index über alle fünf Inhaltsarten. Die Abstimmungen waren bisher gar
// nicht durchsuchbar, obwohl sie den Grossteil des Bestands ausmachen.
// Ergebnisse werden nach Art gruppiert: bei gemischten Treffern ist die Art
// die erste Frage, nicht die Reihenfolge.

const SEARCH_KINDS = [
  { id: "feld",       label: "Themenfelder",  icon: "table_rows" },
  { id: "dossier",    label: "Dossiers",      icon: "description" },
  { id: "abstimmung", label: "Abstimmungen",  icon: "how_to_vote" },
  { id: "sitzung",    label: "Sitzungen",     icon: "calendar_month" },
  { id: "person",     label: "Personen",      icon: "person" },
  { id: "fraktion",   label: "Fraktionen",    icon: "groups" },
  { id: "seite",      label: "Seiten",        icon: "fact_check" },
];

// Übersichtsseiten ohne eigenen Datensatz. Sie über die Suche erreichbar zu
// machen ist billiger, als sie irgendwo in die Navigation zu quetschen.
const SEARCH_PAGES = [
  { href: "#/statistik", title: "Statistik",  meta: "Abstimmungsverhalten, Nähe-Matrix, Nähe-Netz" },
  { href: "#/datenlage", title: "Datenlage",  meta: "Was zu welcher Sitzung vorliegt" },
  { href: "#/presse",    title: "Presseschau", meta: "Berichte über Sitzungen und Beschlüsse" },
  { href: "#/gremien",   title: "Gremien",    meta: "Stadtrat, Ausschüsse, Fraktionen" },
];

function globalSearch(q) {
  const hits = { feld: [], dossier: [], abstimmung: [], sitzung: [], person: [],
                 fraktion: [], seite: [] };

  tags.forEach(t => {
    if (searchNorm(t.name).includes(q))
      hits.feld.push({ href: "#/feld/" + t.id, title: t.name,
                       meta: topics.filter(x => x.field === t.id).length + " Dossiers",
                       color: t.color });
  });
  topics.forEach(t => {
    if (!searchNorm(t.title).includes(q)) return;
    const kind = DOSSIER_TYPE[t.type];
    const years = t.history.map(h => h.date.slice(0, 4));
    hits.dossier.push({
      href: "#/topic/" + t.id, title: t.title,
      meta: [kind && kind.label, years.length &&
             (years[0] === years[years.length - 1] ? years[0]
              : years[0] + "–" + years[years.length - 1])].filter(Boolean).join(" · "),
    });
  });
  votes.forEach(v => {
    if (!searchNorm(v.title).includes(q)) return;
    const r = v.results;
    const tally = v.type === "named" ? `${r.yes.length}:${r.no.length}` : `${r.yes}:${r.no}`;
    hits.abstimmung.push({
      href: "#/session/" + v.sessionId, title: v.title,
      meta: `${formatDate(v.date)} · ${tally}`,
      rejected: v.result === "rejected",
    });
  });
  sessions.forEach(s => {
    if (searchNorm(s.title).includes(q))
      hits.sitzung.push({ href: "#/session/" + s.id, title: s.title,
                          meta: formatDate(s.date) });
  });
  members.forEach(m => {
    if (!searchNorm(m.name).includes(q)) return;
    const p = partyMap[m.party];
    hits.person.push({ href: "#/member/" + m.id, title: m.name,
                       meta: [p && p.name, isActive(m) ? null : "ehemalig"]
                             .filter(Boolean).join(" · "),
                       color: p && p.color });
  });
  const hist = factionHistory();
  parties.forEach(p => {
    if (p.id === "parteilos" || !hist[p.id]) return;
    if (!searchNorm(p.name).includes(q)) return;
    const n = members.filter(m => isActive(m) && m.party === p.id).length;
    hits.fraktion.push({
      href: "#/fraktion/" + p.id, title: p.name, color: p.color,
      meta: n ? n + (n === 1 ? " Sitz" : " Sitze")
              : "nicht mehr im Rat · " + hist[p.id].people.size + " Personen",
    });
  });
  SEARCH_PAGES.forEach(pg => {
    if (searchNorm(pg.title + " " + pg.meta).includes(q)) hits.seite.push(pg);
  });
  return hits;
}

function renderSearchResults(box, hits, onPick) {
  const total = Object.values(hits).reduce((n, a) => n + a.length, 0);
  if (!total) { box.classList.add("hidden"); return; }

  box.innerHTML = "";
  // Bei vielen Treffern bekommt jede Art ein Kontingent, damit eine
  // Kategorie mit hundert Treffern die anderen nicht verdrängt.
  const perKind = total > 14 ? 4 : 8;
  SEARCH_KINDS.forEach(kind => {
    const rows = hits[kind.id];
    if (!rows.length) return;
    const head = document.createElement("div");
    head.className = "dd-group";
    head.innerHTML = `<svg class="icon"><use href="#i-${kind.icon}"/></svg>${kind.label}`
                   + (rows.length > perKind ? `<span>${rows.length}</span>` : "");
    box.appendChild(head);

    rows.slice(0, perKind).forEach(r => {
      const a = document.createElement("a");
      a.className = "dd-item dd-" + kind.id;
      a.href = r.href;
      a.innerHTML =
        (r.color ? `<span class="dd-dot" style="background:${r.color}"></span>` : "")
        + `<span class="dd-title">${r.title}</span>`
        + (r.meta ? `<span class="dd-meta">${r.meta}</span>` : "");
      if (r.rejected) a.classList.add("dd-rejected");
      a.addEventListener("click", () => { box.classList.add("hidden"); onPick(); });
      box.appendChild(a);
    });
  });
  box.classList.remove("hidden");
}

// Ehemals frei laufende Verdrahtung aus app.js, unverändert.
export function initSuche() {
  tags.forEach(tag => {
    const pill = document.createElement("button");
    pill.className = "tag-pill";
    pill.dataset.tagId = tag.id;
    if (tag.color) pill.style.setProperty("--cat-color", tag.color);
    pill.innerHTML = (tag.icon ? `<svg class="icon"><use href="#i-${tag.icon}"/></svg>` : "")
                   + `<span>${tag.name}</span>`;
    pill.addEventListener("click", () => {
      pill.classList.toggle("active");
      const active = tagBar.querySelectorAll(".tag-pill.active");
      const activeIds = Array.from(active).map(el => el.dataset.tagId);
      navigate(activeIds.length ? "/?tags=" + activeIds.join(",") : "/");
    });
    tagBar.appendChild(pill);
  });

  searchInput.addEventListener("input", () => {
    const q = searchNorm(searchInput.value.trim());
    if (q.length < 1) { dropdown.classList.add("hidden"); return; }

    renderSearchResults(dropdown, globalSearch(q), () => { searchInput.value = ""; });
  });

  document.addEventListener("click", evt => {
    if (!evt.target.closest(".search-container")) {
      dropdown.classList.add("hidden");
      gremienDropdown.classList.add("hidden");
    }
  });

  document.addEventListener("keydown", evt => {
    if (evt.key !== "Escape") return;
    document.querySelectorAll(".modal-overlay:not(.hidden), .bottom-sheet:not(.hidden)")
      .forEach(el => el.classList.add("hidden"));
    dropdown.classList.add("hidden");
    gremienDropdown.classList.add("hidden");
  });

  gremienSearchInput.addEventListener("input", () => {
    const q = searchNorm(gremienSearchInput.value.trim());
    if (q.length < 1) { gremienDropdown.classList.add("hidden"); return; }
    renderSearchResults(gremienDropdown, globalSearch(q),
                        () => { gremienSearchInput.value = ""; });
  });
}

export { syncTagPills };
