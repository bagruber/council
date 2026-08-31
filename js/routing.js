// Hash-Routing, Tab-Umschaltung und Seiten-Chrome. route() verteilt auf die
// Views; die Views setzen ihrerseits Chrome und navigieren — die zirkulären
// Importe sind gewollt und unkritisch, weil alle Aufrufe erst nach der
// Initialisierung passieren.
import { tagMap } from "./daten.js";
import { renderHome, renderFilteredTopics, renderTopic, renderField } from "./views/themen.js";
import { renderSession } from "./views/sitzungen.js";
import { renderStatistik, renderDatenlage, renderPresse } from "./views/statistik.js";
import { renderCalendar } from "./views/kalender.js";
import { renderGremien } from "./views/gremien.js";
import { renderMemberProfile } from "./views/profil.js";
import { renderFraktion } from "./views/fraktion.js";

const main = document.getElementById("main");

const tabBtns = document.querySelectorAll(".tab-btn");
const tabPanes = {
  themen: document.getElementById("tab-themen"),
  kalender: document.getElementById("tab-kalender"),
  gremien: document.getElementById("tab-gremien"),
  einstellungen: document.getElementById("tab-einstellungen"),
};

let activeTab = "themen";

function switchTab(name) {
  activeTab = name;
  tabBtns.forEach(b => b.classList.toggle("active", b.dataset.tab === name));
  Object.entries(tabPanes).forEach(([k, el]) => el.classList.toggle("hidden", k !== name));
  if (name === "kalender") renderCalendar();
  if (name === "gremien") renderGremien();
  setChrome(name === "themen" ? "themen" : name);
}

// Farbe von Navbar und Hero. Wird von den Detailseiten überschrieben,
// damit ein Themenfeld anders aussieht als ein Dossier.
function setChrome(kind) {
  document.body.dataset.chrome = kind;
}

// -- Routing --

function navigate(path) {
  window.location.hash = path;
}

function route() {
  const hash = window.location.hash.slice(1) || "/";
  const [path, query] = hash.split("?");
  if (path === "/kalender") {
    switchTab("kalender");
    return;
  }
  if (path === "/einstellungen") {
    switchTab("einstellungen");
    return;
  }
  if (path === "/gremien") {
    switchTab("gremien");
    return;
  }
  if (path.startsWith("/member/")) {
    switchTab("gremien");
    renderMemberProfile(path.split("/member/")[1]);
    return;
  }
  if (path.startsWith("/fraktion/")) {
    switchTab("gremien");
    renderFraktion(path.split("/fraktion/")[1]);
    return;
  }
  switchTab("themen");
  main.innerHTML = "";
  if (path.startsWith("/topic/")) {
    renderTopic(path.split("/topic/")[1]);
  } else if (path.startsWith("/feld/")) {
    renderField(path.split("/feld/")[1]);
  } else if (path.startsWith("/session/")) {
    renderSession(path.split("/session/")[1]);
  } else if (path === "/statistik") {
    renderStatistik();
  } else if (path.startsWith("/datenlage")) {
    renderDatenlage(path.split("/datenlage/")[1] || null);
  } else if (path === "/presse") {
    renderPresse();
  } else {
    const tagIds = (new URLSearchParams(query).get("tags") || "")
      .split(",").filter(id => tagMap[id]);
    if (tagIds.length) renderFilteredTopics(tagIds);
    else renderHome();
  }
}

// Track the most recent non-member hash so the back-link on a member profile
// can return to where the user actually came from (Gremien, Topic, Session, …).
let lastListHash = "/";

// Ehemals frei laufende Verdrahtung aus app.js, unverändert.
export function initRouting() {
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const tab = btn.dataset.tab;
      if (tab === "themen") navigate("/");
      else navigate("/" + tab);
    });
  });

  window.addEventListener("hashchange", route);

  window.addEventListener("hashchange", () => {
    const h = window.location.hash.slice(1) || "/";
    if (!h.startsWith("/member/")) lastListHash = h;
  });

  // Besuchszähler der Domain: Routenwechsel selbst melden, sonst steht in
  // der Auswertung nur der Einstieg (siehe moosburg.eu/assets/zaehler.js).
  window.addEventListener("hashchange", () => {
    if (window.zaehl) window.zaehl(location.pathname + location.hash);
  });
}

export { switchTab, setChrome, navigate, route, lastListHash };
