// Main application: data loading, routing, search, tabs, calendar, gremien.

const SHOW_PRONOUNS = true;

(async function () {
  const main = document.getElementById("main");
  const gremienMain = document.getElementById("gremien-main");

  let topics, sessions, votes, tags, membersData, pressData, sessionLengths;
  try {
    [topics, sessions, votes, tags, membersData, pressData, sessionLengths] = await Promise.all([
      fetch("data/topics.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
      fetch("data/sessions.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
      fetch("data/votes.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
      fetch("data/tags.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
      fetch("data/members.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
      fetch("data/press.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
      fetch("data/sessionlengths.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
    ]);
  } catch (err) {
    main.innerHTML = `<p style="color:var(--no);padding:40px 0">Daten konnten nicht geladen werden. Bitte mit einem lokalen Webserver \u00f6ffnen (z.B. <code>npx serve</code>).</p>`;
    console.error("Datenfehler:", err);
    return;
  }

  const members = membersData.members;
  members.forEach(m => { if (!m.name) m.name = m.firstName + " " + m.lastName; });
  const parties = membersData.parties;
  const bodies = membersData.bodies || [];
  const seatOrder = membersData.seatOrder || parties.map(p => p.id);
  const mediaSources = membersData.media || [];
  const mediaMap = {};
  mediaSources.forEach(m => { mediaMap[m.id] = m; });
  const pressMap = {};
  pressData.forEach(p => { pressMap[p.id] = p; });

  // -- Settings --

  const largeFontsToggle = document.getElementById("setting-large-fonts");
  const colorblindToggle = document.getElementById("setting-colorblind");

  function applySetting(key, cls, toggle) {
    const val = localStorage.getItem(key) === "1";
    toggle.checked = val;
    document.documentElement.classList.toggle(cls, val);
  }

  applySetting("largeFonts", "large-fonts", largeFontsToggle);
  applySetting("colorblind", "colorblind", colorblindToggle);

  largeFontsToggle.addEventListener("change", () => {
    localStorage.setItem("largeFonts", largeFontsToggle.checked ? "1" : "0");
    document.documentElement.classList.toggle("large-fonts", largeFontsToggle.checked);
  });

  colorblindToggle.addEventListener("change", () => {
    localStorage.setItem("colorblind", colorblindToggle.checked ? "1" : "0");
    document.documentElement.classList.toggle("colorblind", colorblindToggle.checked);
  });

  // -- Tab switching --

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
  }

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const tab = btn.dataset.tab;
      if (tab === "themen") navigate("/");
      else navigate("/" + tab);
    });
  });

  // -- Lookup maps --

  const topicMap = {};
  topics.forEach(t => { topicMap[t.id] = t; });
  const sessionMap = {};
  sessions.forEach(s => { sessionMap[s.id] = s; });
  const voteMap = {};
  votes.forEach(v => { voteMap[v.id] = v; });
  const tagMap = {};
  tags.forEach(t => { tagMap[t.id] = t; });
  const memberMap = {};
  members.forEach(m => { memberMap[m.id] = m; });
  const partyMap = {};
  parties.forEach(p => { partyMap[p.id] = p; });
  const bodyMap = {};
  bodies.forEach(b => { bodyMap[b.id] = b; });

  const sessionsSorted = [...sessions].sort((a, b) => b.date.localeCompare(a.date));

  // Sitzungsdauern aus den Niederschriften, Zuordnung über Datum + Gremium.
  // Nicht jede Sitzung ist in sessions.json erfasst — die Statistik nutzt
  // alle Einträge, die Sitzungsseite nur den passenden.
  const lengthMap = {};
  sessionLengths.forEach(l => { lengthMap[l.date + "|" + l.body] = l; });
  const sessionByDateBody = {};
  sessions.forEach(s => { sessionByDateBody[s.date + "|" + (s.type || "stadtrat")] = s; });

  function timeToMin(t) {
    const p = t.split(":");
    return p[0] * 60 + +p[1];
  }

  function lengthMin(l) {
    return l.end ? timeToMin(l.end) - timeToMin(l.start) : null;
  }

  function formatDuration(min) {
    const h = Math.floor(min / 60), m = min % 60;
    if (!h) return m + " Min.";
    return m ? h + " Std. " + m + " Min." : h + " Std.";
  }

  const nowStr = (() => {
    const n = new Date();
    return n.getFullYear() + "-"
         + String(n.getMonth() + 1).padStart(2, "0") + "-"
         + String(n.getDate()).padStart(2, "0");
  })();

  // A member can have one or multiple non-contiguous mandate periods.
  // Period & active-membership: see js/core.js / docs/CORE.md
  const memberActiveAt = Council.memberActiveAt;
  const isActive = (m) => Council.memberActiveAt(m, nowStr);

  // -- Search (Themen tab) --

  const searchInput = document.getElementById("search");
  const dropdown = document.getElementById("search-dropdown");
  const tagBar = document.getElementById("tag-bar");

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

  searchInput.addEventListener("input", () => {
    const q = searchNorm(searchInput.value.trim());
    if (q.length < 1) { dropdown.classList.add("hidden"); return; }

    const results = [];
    tags.forEach(t => {
      if (searchNorm(t.name).includes(q)) results.push({ type: "tag", item: t });
    });
    topics.forEach(t => {
      if (searchNorm(t.title).includes(q)) results.push({ type: "topic", item: t });
    });
    sessions.forEach(s => {
      if (searchNorm(s.title).includes(q)) results.push({ type: "session", item: s });
    });
    members.forEach(m => {
      if (searchNorm(m.name).includes(q)) results.push({ type: "member", item: m });
    });

    if (results.length === 0) { dropdown.classList.add("hidden"); return; }

    dropdown.innerHTML = "";
    results.slice(0, 12).forEach(r => {
      const item = document.createElement("a");
      item.className = "dd-item";
      item.href = r.type === "tag" ? "#/?tags=" + r.item.id
                : r.type === "topic" ? "#/topic/" + r.item.id
                : r.type === "session" ? "#/session/" + r.item.id
                : "#/member/" + r.item.id;
      const labels = { tag: "Tag", topic: "Thema", session: "Sitzung", member: "Person" };
      const former = r.type === "member" && !isActive(r.item) ? " (ehem.)" : "";
      item.innerHTML = `<span class="dd-type">${labels[r.type]}</span><span>${r.item.title || r.item.name}${former}</span>`;
      item.addEventListener("click", () => {
        dropdown.classList.add("hidden");
        searchInput.value = "";
      });
      dropdown.appendChild(item);
    });
    dropdown.classList.remove("hidden");
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

  // -- Gremien search --

  const gremienSearchInput = document.getElementById("gremien-search");
  const gremienDropdown = document.getElementById("gremien-search-dropdown");

  gremienSearchInput.addEventListener("input", () => {
    const q = searchNorm(gremienSearchInput.value.trim());
    if (q.length < 1) { gremienDropdown.classList.add("hidden"); return; }

    const results = members.filter(m => searchNorm(m.name).includes(q));
    if (!results.length) { gremienDropdown.classList.add("hidden"); return; }

    gremienDropdown.innerHTML = "";
    results.slice(0, 10).forEach(m => {
      const item = document.createElement("a");
      item.className = "dd-item";
      item.href = "#/member/" + m.id;
      const party = partyMap[m.party];
      const status = isActive(m) ? "" : " (ehem.)";
      item.innerHTML = `<span class="member-dot" style="background:${party ? party.color : '#ccc'}"></span><span>${m.name}${status}</span>`;
      item.addEventListener("click", () => {
        gremienDropdown.classList.add("hidden");
        gremienSearchInput.value = "";
      });
      gremienDropdown.appendChild(item);
    });
    gremienDropdown.classList.remove("hidden");
  });

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
    } else {
      const tagIds = (new URLSearchParams(query).get("tags") || "")
        .split(",").filter(id => tagMap[id]);
      if (tagIds.length) renderFilteredTopics(tagIds);
      else renderHome();
    }
  }

  window.addEventListener("hashchange", route);

  // Track the most recent non-member hash so the back-link on a member profile
  // can return to where the user actually came from (Gremien, Topic, Session, …).
  let lastListHash = "/";
  window.addEventListener("hashchange", () => {
    const h = window.location.hash.slice(1) || "/";
    if (!h.startsWith("/member/")) lastListHash = h;
  });

  // -- Views --

  function renderHome() {
    syncTagPills([]);
    const heading = document.createElement("p");
    heading.className = "section-heading";
    heading.textContent = "Alle Themen";
    main.appendChild(heading);
    renderTopicList(topics);

    const totalH = Math.round(sessionLengths.reduce((s, l) => s + (lengthMin(l) || 0), 0) / 60);
    const teaser = document.createElement("a");
    teaser.className = "stats-teaser";
    teaser.href = "#/statistik";
    teaser.innerHTML = `
      <svg class="icon"><use href="#i-insights"/></svg>
      <div>
        <div class="stats-teaser-title">Sitzungsstatistik</div>
        <div class="stats-teaser-sub">${sessionLengths.length} Sitzungen · ${totalH} Stunden seit Mai 2020</div>
      </div>
      <svg class="icon"><use href="#i-chevron_right"/></svg>`;
    main.appendChild(teaser);
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

    main.appendChild(breadcrumb([{ label: "Themen", href: "#/" }]));

    const dossiers = topics.filter(t => t.field === fieldId || (t.tags || []).includes(fieldId));
    const ids = new Set(dossiers.map(t => t.id));
    const loose = votes
      .filter(v => !v.topicId)
      .filter(v => voteInField(v, fieldId))
      .sort((a, b) => b.date.localeCompare(a.date));

    const header = document.createElement("div");
    header.className = "topic-header";
    header.innerHTML = `
      <div class="dossier-meta"><span class="dossier-type" style="color:${field.color}">
        <svg class="icon"><use href="#i-${field.icon}"/></svg>Feld</span>
        <span class="dossier-count">${dossiers.length} Dossiers · ${loose.length} weitere Beschlüsse</span></div>
      <h1>${field.name}</h1>`;
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
        <tr${i === 0 ? ' class="current"' : ""}>
          <td class="fig-date">${formatDate(r.date)}</td>
          <td class="fig-label">${r.voteId ? `<a href="#/topic/${topic.id}">${r.label}</a>` : r.label}</td>
          ${r.value ? `<td class="fig-value">${r.value}</td>` : ""}
        </tr>`).join("")}</tbody></table>
      ${f.note ? `<p class="figures-note">${f.note}</p>` : ""}`;
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

  // -- Session detail --

  function renderSession(id) {
    const session = sessionMap[id];
    if (!session) { main.innerHTML = "<p>Sitzung nicht gefunden.</p>"; return; }

    const back = document.createElement("a");
    back.className = "back-link";
    back.href = "#/";
    back.innerHTML = '<svg class="icon"><use href="#i-arrow_back"/></svg> \u00dcbersicht';
    back.addEventListener("click", e => {
      if (window.history.length > 1) { e.preventDefault(); window.history.back(); }
    });
    main.appendChild(back);

    const header = document.createElement("div");
    header.className = "session-header";
    let badge = "";
    if (session.type && session.type !== "stadtrat") {
      const body = bodyMap[session.type];
      const label = body ? body.shortName : session.type;
      badge = `<div class="session-badge"><svg class="icon"><use href="#i-groups"/></svg> ${label}</div>`;
    }
    const len = lengthMap[session.date + "|" + (session.type || "stadtrat")];
    let timeLine = "";
    if (len) {
      const dur = lengthMin(len);
      timeLine = `<div class="session-time"><svg class="icon"><use href="#i-schedule"/></svg>${len.start}${len.end ? "–" + len.end : ""} Uhr${dur ? " · " + formatDuration(dur) : ""}</div>`;
    }
    header.innerHTML = `<h1>${session.title}</h1><div class="session-date">${formatDate(session.date)}</div>${timeLine}${badge}`;
    main.appendChild(header);

    if (session.substitutes && session.substitutes.length) {
      const subs = document.createElement("div");
      subs.className = "session-subs";
      session.substitutes.forEach(s => {
        const member = memberMap[s.member];
        const sub = memberMap[s.substitute];
        const row = document.createElement("div");
        row.className = "sub-row";
        row.innerHTML = `<svg class="icon"><use href="#i-swap_horiz"/></svg> ${sub ? sub.name : s.substitute} f\u00fcr ${member ? member.name : s.member}`;
        subs.appendChild(row);
      });
      main.appendChild(subs);
    }

    const list = document.createElement("div");
    list.className = "agenda-list";

    session.agenda.forEach(item => {
      const el = document.createElement("div");
      el.className = "agenda-item";

      const hasTopic = item.topicId && topicMap[item.topicId];
      if (hasTopic) {
        el.classList.add("has-link");
        // Großer Klickbereich, aber Vote-Block/Buttons/Links nicht abfangen
        el.addEventListener("click", e => {
          if (e.target.closest("a, button, .vote-block")) return;
          navigate("/topic/" + item.topicId);
        });
      }

      el.innerHTML = `
        <div class="ai-number">TOP ${item.number}</div>
        <h3>${hasTopic ? `<a href="#/topic/${item.topicId}">${item.title}</a>` : item.title}</h3>`;

      if (item.type === "formal") {
        el.innerHTML += '<span class="ai-type">Formell</span>';
      } else if (item.type === "discussion") {
        el.innerHTML += '<span class="ai-type">Beratung</span>';
      }

      if (item.voteId && voteMap[item.voteId]) {
        const voteEl = document.createElement("div");
        renderVoteBlock(voteEl, voteMap[item.voteId]);
        el.appendChild(voteEl);
      }

      const agendaPress = renderPressLinks(item.press);
      if (agendaPress) el.appendChild(agendaPress);

      list.appendChild(el);
    });

    main.appendChild(list);
  }

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
  window.addEventListener("resize", () => {
    const path = (window.location.hash.slice(1) || "/").split("?")[0];
    if (path !== "/statistik") return;
    clearTimeout(statsResizeTimer);
    statsResizeTimer = setTimeout(route, 150);
  });

  // -- Vote block --

  function bodyForVote(vote) {
    const bid = bodyIdForSession(sessionMap[vote.sessionId]);
    return bid ? bodyMap[bid] : null;
  }

  // Woher die Einzelstimmen stammen. Vier Stufen, absteigend belastbar —
  // bewusst eine ruhige Fußzeile, kein Siegel: die Herkunft qualifiziert das
  // Ergebnis, sie ist nicht die Nachricht.
  function renderVoteSource(vote) {
    const label = Council.sourceLabel(vote);
    if (!label) {
      return vote.type === "anonymous" && vote.results.yes && vote.results.no
        ? `<div class="vote-source">Nur das Ergebnis ist überliefert, nicht wer wie gestimmt hat.</div>`
        : "";
    }
    const parts = [label];
    if (vote.source.by) {
      const m = members.find(x => x.id === vote.source.by);
      if (m) parts.push(`${m.firstName.charAt(0)}. ${m.lastName}`);
    }
    let html = parts.join(" · ");
    const art = vote.source.pressId && pressMap[vote.source.pressId];
    if (art) {
      html += ` · <a href="${art.url}" target="_blank" rel="noopener">durch Presse bestätigt</a>`;
    } else if (vote.source.pressVerified) {
      html += " · durch Presse bestätigt";
    }
    return `<div class="vote-source">${html}</div>`;
  }

  function renderVoteBlock(container, vote) {
    const block = document.createElement("div");
    block.className = "vote-block";

    // Status-Pille: angenommen / abgelehnt / vertagt / zurückgezogen.
    // Bei Anträgen subtiler, weil der Titel das Antrags-Kontext schon transportiert
    // (und der Antrag perspektivisch verlinkt wird).
    const STATUS = {
      rejected:  { cls: "rejected",  text: "Abgelehnt"     },
      deferred:  { cls: "deferred",  text: "Vertagt"       },
      withdrawn: { cls: "withdrawn", text: "Zurückgezogen" },
    };
    const st = STATUS[vote.result] || { cls: "approved", text: "Angenommen" };
    const isAntrag = /\bAntrag\b|\bAnträge\b/i.test(vote.title);
    const resultTag = `<span class="vote-result-tag ${st.cls}${isAntrag ? " subtle" : ""}">${st.text}</span>`;

    block.innerHTML = `
      <button class="vote-help-btn" aria-label="Legende" title="Was bedeutet was?">
        <svg class="icon"><use href="#i-help_outline"/></svg>
      </button>
      <h4>${vote.title}${resultTag}</h4>
      <div class="vote-text">${vote.text}</div>
      ${vote.note ? `<p class="vote-note">${vote.note}</p>` : ""}
      <div class="vote-legend">
        <span><span class="legend-dot yes"></span> Ja</span>
        <span><span class="legend-dot no"></span> Nein</span>
        <span><span class="legend-dot absent"></span> Abwesend</span>
      </div>
      ${renderVoteSource(vote)}`;

    block.querySelector(".vote-help-btn").addEventListener("click", () => {
      document.getElementById("vote-legend-modal").classList.remove("hidden");
    });

    const chartEl = document.createElement("div");
    block.appendChild(chartEl);
    container.appendChild(block);

    requestAnimationFrame(() => {
      const hasIndividualData = vote.type === "named"
                              || (vote.voters && Object.keys(vote.voters).length > 0);
      if (!hasIndividualData) {
        VoteVis.drawBar(chartEl, vote.results);
      } else {
        const body = bodyForVote(vote);
        VoteVis.drawParliament(chartEl, vote, members, parties, seatOrder, body ? { body } : {});
      }
    });
  }

  // -- Calendar --

  let calYear, calMonth;
  const calTitle = document.getElementById("cal-title");
  const calGrid = document.getElementById("cal-grid");
  const calSheet = document.getElementById("cal-sheet");
  const calSheetBody = document.getElementById("cal-sheet-body");
  const monthNames = ["Januar", "Februar", "M\u00e4rz", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember"];

  const sessionsByDate = {};
  sessions.forEach(s => {
    if (!sessionsByDate[s.date]) sessionsByDate[s.date] = [];
    sessionsByDate[s.date].push(s);
  });

  (function initCalendar() {
    const now = new Date();
    calYear = now.getFullYear();
    calMonth = now.getMonth();

    document.getElementById("cal-prev").addEventListener("click", () => {
      if (--calMonth < 0) { calMonth = 11; calYear--; }
      renderCalendar();
    });
    document.getElementById("cal-next").addEventListener("click", () => {
      if (++calMonth > 11) { calMonth = 0; calYear++; }
      renderCalendar();
    });

    let startX = 0;
    const pane = document.getElementById("tab-kalender");
    pane.addEventListener("touchstart", e => { startX = e.touches[0].clientX; }, { passive: true });
    pane.addEventListener("touchend", e => {
      const dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) < 60) return;
      if (dx < 0) { if (++calMonth > 11) { calMonth = 0; calYear++; } }
      else { if (--calMonth < 0) { calMonth = 11; calYear--; } }
      renderCalendar();
    });
  })();

  function renderCalendar() {
    calTitle.textContent = monthNames[calMonth] + " " + calYear;
    calGrid.innerHTML = "";

    const first = new Date(calYear, calMonth, 1);
    const last = new Date(calYear, calMonth + 1, 0);
    const startDow = (first.getDay() + 6) % 7;

    const today = new Date();
    const todayStr = isoDate(today.getFullYear(), today.getMonth(), today.getDate());

    const prevLast = new Date(calYear, calMonth, 0);
    for (let i = startDow - 1; i >= 0; i--) {
      addDay(prevLast.getDate() - i, isoDate(calYear, calMonth - 1, prevLast.getDate() - i), true, todayStr);
    }

    for (let d = 1; d <= last.getDate(); d++) {
      addDay(d, isoDate(calYear, calMonth, d), false, todayStr);
    }

    const cells = calGrid.children.length;
    const pad = (7 - (cells % 7)) % 7;
    for (let d = 1; d <= pad; d++) {
      addDay(d, isoDate(calYear, calMonth + 1, d), true, todayStr);
    }
  }

  function isoDate(y, m, d) {
    const dt = new Date(y, m, d);
    return dt.getFullYear() + "-" +
      String(dt.getMonth() + 1).padStart(2, "0") + "-" +
      String(dt.getDate()).padStart(2, "0");
  }

  function addDay(num, dateStr, otherMonth, todayStr) {
    const cell = document.createElement("div");
    cell.className = "cal-day";
    if (otherMonth) cell.classList.add("other-month");
    if (dateStr === todayStr) cell.classList.add("today");

    const span = document.createElement("span");
    span.textContent = num;
    cell.appendChild(span);

    const events = sessionsByDate[dateStr];
    if (events) {
      const dots = document.createElement("div");
      dots.className = "cal-dots";
      events.forEach(s => {
        const dot = document.createElement("span");
        dot.className = "cal-dot " + (s.type || "stadtrat");
        dots.appendChild(dot);
      });
      cell.appendChild(dots);
      cell.addEventListener("click", () => openDaySheet(dateStr, events));
    }

    calGrid.appendChild(cell);
  }

  function openDaySheet(dateStr, events) {
    calSheetBody.innerHTML = "";

    const heading = document.createElement("div");
    heading.className = "sheet-date";
    heading.textContent = formatDate(dateStr);
    calSheetBody.appendChild(heading);

    events.forEach(s => {
      const row = document.createElement("a");
      row.className = "sheet-event";
      row.href = "#/session/" + s.id;
      if (s.type && s.type !== "stadtrat") row.classList.add(s.type);
      const icon = s.type === "bpu" ? "engineering"
                 : (s.type && s.type !== "stadtrat") ? "groups"
                 : "account_balance";
      row.innerHTML = `
        <svg class="icon"><use href="#i-${icon}"/></svg>
        <div class="sheet-event-text">${s.title}</div>
        <svg class="icon"><use href="#i-chevron_right"/></svg>`;
      row.addEventListener("click", () => calSheet.classList.add("hidden"));
      calSheetBody.appendChild(row);
    });

    calSheet.classList.remove("hidden");
  }

  // -- Gremien tab --

  function renderGremien() {
    const hash = window.location.hash.slice(1) || "/";
    if (hash.startsWith("/member/")) {
      renderMemberProfile(hash.split("/member/")[1]);
      return;
    }
    gremienMain.innerHTML = "";

    const wrap = document.createElement("div");
    wrap.className = "page-wrap";

    const plenum = bodies.filter(b => b.type === "plenum");
    const ausschuesse = bodies.filter(b => b.type === "ausschuss");
    const sonstige = bodies.filter(b => b.type === "sonstige");

    // Plenum
    if (plenum.length) {
      const sec = makeSection("");
      const cards = document.createElement("div");
      cards.className = "body-cards full-width";
      plenum.forEach(b => cards.appendChild(makeBodyCard(b)));
      sec.appendChild(cards);
      wrap.appendChild(sec);
    }

    // Ausschuesse
    if (ausschuesse.length) {
      const sec = makeSection("Aussch\u00fcsse");
      const cards = document.createElement("div");
      cards.className = "body-cards";
      ausschuesse.forEach(b => cards.appendChild(makeBodyCard(b)));
      sec.appendChild(cards);
      wrap.appendChild(sec);
    }

    // Sonstige
    if (sonstige.length) {
      const sec = makeSection("Besondere Gremien");
      const cards = document.createElement("div");
      cards.className = "body-cards";
      sonstige.forEach(b => cards.appendChild(makeBodyCard(b)));
      sec.appendChild(cards);
      wrap.appendChild(sec);
    }

    // faction list
    const factionSec = makeSection("Fraktionen");
    const activeMembers = members.filter(m => isActive(m) && m.role !== "mayor");
    const activeMayor = members.find(m => isActive(m) && m.role === "mayor");

    const grouped = {};
    seatOrder.forEach(pid => { grouped[pid] = []; });
    activeMembers.forEach(m => {
      if (!grouped[m.party]) grouped[m.party] = [];
      grouped[m.party].push(m);
    });

    seatOrder.forEach(pid => {
      const group = grouped[pid];
      if (!group || !group.length) return;
      const party = partyMap[pid];
      const fh = document.createElement("div");
      fh.className = "faction-head";
      fh.innerHTML = `<span class="member-dot" style="background:${party.color}"></span><span class="faction-name">${party.name}</span><span class="faction-count">${group.length}</span>`;
      factionSec.appendChild(fh);
      group.sort((a, b) => a.name.localeCompare(b.name));
      group.forEach(m => factionSec.appendChild(makeMemberRow(m)));
    });

    if (activeMayor) {
      const mh = document.createElement("div");
      mh.className = "faction-head";
      const mp = partyMap[activeMayor.party];
      mh.innerHTML = `<span class="member-dot" style="background:${mp ? mp.color : '#999'}"></span><span class="faction-name">B\u00fcrgermeister</span>`;
      factionSec.appendChild(mh);
      factionSec.appendChild(makeMemberRow(activeMayor));
    }

    wrap.appendChild(factionSec);

    gremienMain.appendChild(wrap);
  }

  function makeSection(title) {
    const sec = document.createElement("div");
    sec.className = "gremien-section";
    if (title) {
      const h = document.createElement("p");
      h.className = "section-heading";
      h.textContent = title;
      sec.appendChild(h);
    }
    return sec;
  }

  function makeBodyCard(body) {
    const card = document.createElement("div");
    card.className = "body-card";

    const current = [];
    const former = [];

    if (body.type === "plenum") {
      members.forEach(m => {
        if (isActive(m)) current.push(m);
        else former.push(m);
      });
    } else if (body.seats) {
      const allIds = new Set();
      body.seats.forEach(s => {
        allIds.add(s.member);
        if (s.sub) allIds.add(s.sub);
      });
      if (body.chair) allIds.add(body.chair);
      if (body.chairSub) allIds.add(body.chairSub);
      if (body.vicechairs) body.vicechairs.forEach(v => { allIds.add(v.member); if (v.sub) allIds.add(v.sub); });

      allIds.forEach(id => {
        const m = memberMap[id];
        if (!m) return;
        const period = body.memberPeriod;
        if (period && period.to && period.to <= nowStr) {
          if (!former.find(c => c.id === m.id)) former.push(m);
        } else if (isActive(m)) {
          if (!current.find(c => c.id === m.id)) current.push(m);
        } else {
          if (!former.find(c => c.id === m.id)) former.push(m);
        }
      });
    }

    current.sort((a, b) => a.name.localeCompare(b.name));
    former.sort((a, b) => a.name.localeCompare(b.name));
    const count = body.seats ? body.seats.length + (body.vicechairs ? body.vicechairs.length : 0) + 1 : current.length;

    card.innerHTML = `
      <div class="body-card-header">
        <svg class="icon"><use href="#i-${body.icon || 'groups'}"/></svg>
        <div>
          <div class="body-card-title">${body.name}</div>
          ${count ? `<div class="body-card-count">${count} Mitglieder</div>` : ''}
        </div>
        <svg class="icon expand-icon"><use href="#i-expand_more"/></svg>
      </div>
      <div class="body-card-detail"><div class="body-card-detail-inner"></div></div>`;

    const detail = card.querySelector(".body-card-detail-inner");

    if (body.description) {
      const desc = document.createElement("div");
      desc.className = "body-card-desc";
      desc.textContent = body.description;
      detail.appendChild(desc);
    }

    // seats table with substitutes
    if (body.seats && body.type !== "plenum") {
      const hasSubs = body.seats.some(s => s.sub);
      const table = document.createElement("table");
      table.className = "seat-table";

      const nameCell = (m, role) => {
        const p = partyMap[m.party];
        const roleTag = role ? ` <span class="seat-role">(${role})</span>` : "";
        return `<td class="seat-name"><a href="#/member/${m.id}"><span class="member-dot" style="background:${p ? p.color : '#ccc'}"></span> ${m.name}${roleTag}</a></td>`;
      };
      const subCells = (subId) => {
        if (!hasSubs) return "";
        const s = subId && memberMap[subId];
        return s
          ? `<td><svg class="icon swap-icon"><use href="#i-swap_horiz"/></svg></td><td class="seat-sub"><a href="#/member/${s.id}">${s.name}</a></td>`
          : "<td></td><td></td>";
      };

      let html = "<thead><tr><th>Mitglied</th>";
      if (hasSubs) html += "<th></th><th>Stellvertretung</th>";
      html += "</tr></thead><tbody>";

      if (body.chair && memberMap[body.chair]) {
        html += "<tr>" + nameCell(memberMap[body.chair], "Vorsitz") + subCells(body.chairSub) + "</tr>";
      }
      (body.vicechairs || []).forEach(vc => {
        const m = memberMap[vc.member];
        if (m) html += "<tr>" + nameCell(m, "Stellv. Vorsitz") + subCells(vc.sub) + "</tr>";
      });
      body.seats.forEach(seat => {
        const m = memberMap[seat.member];
        if (m) html += "<tr>" + nameCell(m, seat.role) + subCells(seat.sub) + "</tr>";
      });

      html += "</tbody>";
      table.innerHTML = html;
      detail.appendChild(table);
    } else {
      // plenum: simple member list
      if (current.length) {
        const list = document.createElement("div");
        list.className = "body-member-list";
        const heading = document.createElement("div");
        heading.className = "bml-heading";
        heading.textContent = "Aktuelle Mitglieder";
        list.appendChild(heading);
        current.forEach(m => list.appendChild(makeMemberRow(m)));
        detail.appendChild(list);
      }
      if (former.length) {
        const list = document.createElement("div");
        list.className = "body-member-list";
        const heading = document.createElement("div");
        heading.className = "bml-heading";
        heading.textContent = "Ehemalige";
        list.appendChild(heading);
        former.forEach(m => list.appendChild(makeMemberRow(m, true)));
        detail.appendChild(list);
      }
    }

    card.querySelector(".body-card-header").addEventListener("click", () => {
      card.classList.toggle("expanded");
    });

    return card;
  }

  function makeMemberRow(m, showDates) {
    const row = document.createElement("a");
    row.className = "member-row";
    row.href = "#/member/" + m.id;
    const party = partyMap[m.party];
    const color = party ? party.color : "#ccc";
    let meta = "";
    if (m.title) meta = m.title;
    else if (m.role === "mayor") meta = "BM";
    if (showDates) meta = formatPeriod(m.from, m.to);

    row.innerHTML = `
      <span class="member-dot" style="background:${color}"></span>
      <span class="member-row-name">${m.name}</span>
      <span class="member-row-meta">${meta}</span>`;
    return row;
  }

  // -- Member profile --

  function nameColorFromParty(hex, darker) {
    if (!hex) return darker ? "#333" : "#555";
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    const lum = 0.299 * r + 0.587 * g + 0.114 * b;
    if (lum < 30) {
      const boost = darker ? 80 : 120;
      return "#" + [r, g, b].map(c => Math.min(255, c + boost).toString(16).padStart(2, "0")).join("");
    }
    const f = darker
      ? (lum > 180 ? 0.22 : lum > 120 ? 0.35 : 0.45)
      : (lum > 180 ? 0.45 : lum > 120 ? 0.6 : 0.75);
    return "#" + [r, g, b].map(c => Math.round(c * f).toString(16).padStart(2, "0")).join("");
  }

  function renderMemberProfile(id) {
    const m = memberMap[id];
    if (!m) { gremienMain.innerHTML = "<p style='padding:40px 24px'>Person nicht gefunden.</p>"; return; }

    gremienMain.innerHTML = "";
    const wrap = document.createElement("div");
    wrap.className = "page-wrap";

    const back = document.createElement("a");
    back.className = "back-link";
    // Return to wherever the user came from (Gremien list, Topic, Session, …)
    const backHash = lastListHash || "/gremien";
    back.href = "#" + backHash;
    const backLabel = backHash === "/gremien" ? "Gremien"
                    : backHash.startsWith("/topic/") ? "Thema"
                    : backHash.startsWith("/session/") ? "Sitzung"
                    : "Übersicht";
    back.innerHTML = `<svg class="icon"><use href="#i-arrow_back"/></svg> ${backLabel}`;
    wrap.appendChild(back);

    const currentPartyId = m.partyHistory && m.partyHistory.length
      ? m.partyHistory[m.partyHistory.length - 1].party
      : m.party;
    const party = partyMap[currentPartyId] || partyMap[m.party];
    const profile = m.profile || {};

    // header
    const header = document.createElement("div");
    header.className = "profile-header";
    const initial = (m.firstName || m.name).charAt(0);
    const photoPath = "img/members/" + m.id + ".webp";
    const photoPath2x = "img/members/" + m.id + "@2x.webp";
    const avatarColor = party ? party.color : '#999';
    const nameColor = nameColorFromParty(avatarColor, false);
    const surnameColor = nameColorFromParty(avatarColor, true);

    const brushFiles = ["A1","A2","A3","A4","A6","A7","A8","A9","A10"];
    const memberIdx = members.indexOf(m);
    const brushFile = brushFiles[memberIdx % brushFiles.length];
    const brushRotation = ((memberIdx * 37 + 13) % 360) - 180;

    header.innerHTML = `
      <div class="profile-avatar-wrap">
        <div class="avatar-brush" id="avatar-brush"></div>
        <div class="profile-avatar" id="profile-avatar" style="background:${avatarColor}">${initial}</div>
      </div>
      <div class="profile-info">
        <div class="profile-name-block"><div class="profile-name-inner">
          <div class="profile-given-name" style="color:${nameColor}">${m.firstName || ""}</div>
          <div class="profile-surname${(m.lastName || m.name).length > 10 ? ' long-name' : ''}" style="color:${surnameColor}">${m.lastName || m.name}</div>
          ${m.nee ? `<div class="profile-nee" style="color:${nameColor}">(geb. ${m.nee})</div>` : ""}
          ${SHOW_PRONOUNS && profile.pronouns ? `<div class="profile-pronouns">${profile.pronouns}</div>` : ""}
          <div class="profile-party"><span class="profile-party-dot" style="background:${avatarColor}"></span>${party ? party.name : ""}</div>
          ${m.title ? `<div class="profile-title">${m.title}</div>` : ""}
        </div></div>
        <div class="profile-meta" id="profile-meta"></div>
      </div>`;
    wrap.appendChild(header);

    const metaEl = header.querySelector("#profile-meta");
    if (profile.identity && profile.identity.length) {
      const badges = document.createElement("div");
      badges.className = "identity-badges";
      const labels = { queer: "LGBTQ+", migrant: "Migrantisch", flinta: "FLINTA", disability: "Barrierefrei" };
      const badgeIcons = { queer: "favorite", migrant: "public", flinta: "female", disability: "accessible" };
      profile.identity.forEach(id => {
        const b = document.createElement("span");
        b.className = "id-badge " + id;
        b.innerHTML = (badgeIcons[id] ? `<svg class="icon"><use href="#i-${badgeIcons[id]}"/></svg> ` : "") + (labels[id] || id);
        badges.appendChild(b);
      });
      metaEl.appendChild(badges);
    }
    if (profile.contact) {
      const c = profile.contact;
      const links = document.createElement("div");
      links.className = "profile-contact";
      if (c.email) links.appendChild(makeContactLink("email", "mailto:" + c.email));
      if (c.website) links.appendChild(makeContactLink("website", "https://" + c.website));
      if (c.instagram) links.appendChild(makeContactLink("instagram", "https://instagram.com/" + c.instagram.replace("@", "")));
      if (c.threads) links.appendChild(makeContactLink("threads", "https://threads.net/" + c.threads.replace("@", "")));
      if (c.linkedin) links.appendChild(makeContactLink("linkedin", "https://linkedin.com/in" + c.linkedin));
      if (c.facebook) links.appendChild(makeContactLink("facebook", "https://facebook.com" + c.facebook));
      metaEl.appendChild(links);
    }

    fetch("img/brushstroke" + brushFile + ".svg")
      .then(r => r.text())
      .then(svgText => {
        const brushEl = header.querySelector("#avatar-brush");
        if (!brushEl) return;
        const colored = svgText
          .replace(/fill:\s*#333/g, "fill: " + avatarColor);
        brushEl.innerHTML = colored;
        const svg = brushEl.querySelector("svg");
        if (svg) {
          svg.style.width = "100%";
          svg.style.height = "100%";
          svg.style.transform = "rotate(" + brushRotation + "deg)";
          svg.removeAttribute("id");
        }
      });

    const avatarEl = header.querySelector("#profile-avatar");
    const testImg = new Image();
    testImg.onload = () => {
      // Use image-set so retina screens fetch the 2x variant, others the lighter 1x.
      avatarEl.style.backgroundImage =
        `image-set(url('${photoPath}') 1x, url('${photoPath2x}') 2x)`;
      avatarEl.style.backgroundSize = "cover";
      avatarEl.style.backgroundPosition = "center";
      avatarEl.style.backgroundColor = "transparent";
      avatarEl.textContent = "";
    };
    testImg.onerror = () => {};
    testImg.src = photoPath;

    // roles & committees
    const rolesSection = document.createElement("div");
    rolesSection.className = "profile-section";
    rolesSection.innerHTML = "<h3>Mandate & Funktionen</h3>";

    const roleLabel = m.role === "mayor" ? "B\u00fcrgermeister" : "Stadtrat";
    const periods = (m.periods && m.periods.length)
      ? m.periods
      : [{ from: m.from, to: m.to }];
    periods.forEach(p => {
      rolesSection.appendChild(makeRoleRow("account_balance", roleLabel, p.from, p.to));
    });

    if (m.partyHistory && m.partyHistory.length) {
      const phWrap = document.createElement("div");
      phWrap.className = "party-history";
      m.partyHistory.forEach(ph => {
        const p = partyMap[ph.party];
        const color = p ? p.color : "#999";
        const name = p ? p.name : ph.party;
        const period = formatPeriod(ph.from, ph.to);
        const row = document.createElement("div");
        row.className = "party-history-row";
        row.innerHTML = `<span class="profile-party-dot" style="background:${color}"></span><span>${name}</span><span class="role-dates">${period}</span>`;
        phWrap.appendChild(row);
      });
      rolesSection.appendChild(phWrap);
    }

    if (m.roleHistory) {
      m.roleHistory.forEach(rh => {
        const rl = rh.role === "mayor" ? "B\u00fcrgermeister" : "Stadtrat";
        rolesSection.appendChild(makeRoleRow("account_balance", rl, rh.from, rh.to));
      });
    }

    if (profile.titles) {
      profile.titles.forEach(t => {
        const icon = t.title.includes("rgermeister") ? "star" : "badge";
        rolesSection.appendChild(makeRoleRow(icon, t.title, t.from, t.to));
      });
    }

    // committees from seats data (member or substitute)
    bodies.forEach(b => {
      if (b.type === "plenum" || !b.seats) return;
      const inSeats = b.seats.some(s => s.member === m.id);
      const isSub = b.seats.some(s => s.sub === m.id);
      const isChair = b.chair === m.id;
      const isChairSub = b.chairSub === m.id;
      const isVice = b.vicechairs && b.vicechairs.some(v => v.member === m.id);
      const isViceSub = b.vicechairs && b.vicechairs.some(v => v.sub === m.id);
      if (inSeats || isSub || isChair || isChairSub || isVice || isViceSub) {
        const role = isChair ? " (Vorsitz)" : isVice ? " (Stellv. Vorsitz)" : "";
        rolesSection.appendChild(makeRoleRow("groups", b.name + role, m.from, m.to));
      }
      // past memberships
      if (b.pastSeats) {
        b.pastSeats.forEach(ps => {
          if (ps.member !== m.id) return;
          const suffix = ps.role ? ` (${ps.role})` : ps.sub === true ? " (Stellv.)" : "";
          rolesSection.appendChild(makeRoleRow("history", b.name + suffix, ps.from || m.from, ps.to));
        });
      }
    });

    wrap.appendChild(rolesSection);

    // motions
    if (profile.motions && profile.motions.length) {
      const motionSec = document.createElement("div");
      motionSec.className = "profile-section";
      motionSec.innerHTML = "<h3>Antr\u00e4ge</h3>";
      profile.motions.forEach(mot => {
        const el = document.createElement("div");
        el.className = "mtl-motion";
        const coNames = mot.coSigners
          .map(sid => memberMap[sid] ? memberMap[sid].name : sid)
          .join(", ");
        const sessionLink = mot.sessionId && sessionMap[mot.sessionId]
          ? `<a href="#/session/${mot.sessionId}" class="mtl-motion-link"><svg class="icon"><use href="#i-open_in_new"/></svg>${sessionMap[mot.sessionId].title}</a>`
          : "";
        el.innerHTML = `
          <svg class="icon"><use href="#i-edit_note"/></svg>
          <div>
            <div class="mtl-motion-title">${mot.title}</div>
            <div class="mtl-motion-meta">${mot.body} \u2013 ${formatDate(mot.date)}</div>
            ${coNames ? `<div class="mtl-motion-meta">gemeinsam mit ${coNames}</div>` : ""}
            ${sessionLink}
          </div>`;
        const motPress = renderPressLinks(mot.press);
        if (motPress) el.appendChild(motPress);
        motionSec.appendChild(el);
      });
      wrap.appendChild(motionSec);
    }

    // personal timeline
    const tlSection = document.createElement("div");
    tlSection.className = "profile-section";
    tlSection.innerHTML = "<h3>Abstimmungsverhalten</h3>";
    wrap.appendChild(tlSection);

    // Stats card (collapsed by default)
    const stats = computeVotingStats(m);
    if (stats.total.total > 0) {
      const statsEl = renderVotingStatsCard(stats);
      wrap.appendChild(statsEl);
    }

    const tlWrap = document.createElement("div");
    renderMemberTimeline(tlWrap, m);
    wrap.appendChild(tlWrap);

    gremienMain.appendChild(wrap);
  }

  // ─── Voting statistics ───────────────────────────────────────────────────

  function bodyIdForSession(s) {
    if (!s) return null;
    if (s.type === "stadtrat") return "plenum";
    if (s.type === "bpu")      return "bpu";
    if (s.type === "hvfa")     return "hvfa";
    return null;
  }

  function periodOfDate(d) {
    if (d < "2020-05-01") return "2014–2020";
    if (d < "2026-05-01") return "2020–2026";
    return "2026–2032";
  }

  // Sieben Kategorien: Verhalten (Ja/Nein/Unbekannt/Abwesend) × Einstimmigkeit
  // der Abstimmung. u = einstimmige Abstimmung, s = nicht einstimmige (split).
  // Bei einstimmigen Votes ist die Einzelstimme weniger aussagekräftig,
  // deshalb werden sie blasser dargestellt — egal ob named oder abgeleitet.
  const STAT_ZERO = () =>
    ({ uYes:0, uNo:0, sYes:0, sNo:0, sUnknown:0, absU:0, absS:0, total:0 });

  function statKey(raw, unanimous) {
    const base = raw.replace("-inferred", "");
    // Befangen oder enthalten heißt: anwesend, aber keine Stimme abgegeben.
    // Sie landen in der Nicht-abgestimmt-Spalte — sonst würden sie als Nein
    // gezählt und das Stimmbild verfälschen.
    if (base === "absent" || base === "excluded" || base === "abstained"
        || base === "restricted") {
      return unanimous ? "absU" : "absS";
    }
    if (base === "unknown") return "sUnknown";
    return (unanimous ? "u" : "s") + (base === "yes" ? "Yes" : "No");
  }

  function computeVotingStats(member) {
    const out = { byYear: {}, byPeriod: {}, byBody: {}, total: STAT_ZERO() };
    const inc = (bucket, key, status) => {
      if (!bucket[key]) bucket[key] = STAT_ZERO();
      bucket[key][status]++;
      bucket[key].total++;
      out.total[status]++;
      out.total.total++;
    };

    votes.forEach(v => {
      const session = sessionMap[v.sessionId];
      const bid = bodyIdForSession(session);
      if (!bid) return;
      const body = bodyMap[bid];
      if (!body) return;

      // Relevance: plenum = active member; committee = regular (not sub)
      if (bid === "plenum") {
        if (!Council.memberActiveAt(member, v.date)) return;
      } else {
        if (!Council.isRegularOf(member, body, v.date)) return;
      }

      const raw = Council.voteStatus(member.id, v, session, member);
      if (raw === null) return;
      const status = statKey(raw, Council.isUnanimous(v));

      inc(out.byYear,   v.date.substring(0, 4), status);
      inc(out.byPeriod, periodOfDate(v.date),   status);
      inc(out.byBody,   bid,                    status);
    });

    return out;
  }

  // Bar-Reihenfolge — symmetrisch um die Mitte: links Ablehnung (einstimmig
  // außen, knapp innen), Mitte Unbekannt, rechts Zustimmung; Abwesende ganz
  // außen rechts (einstimmige Abstimmungen blasser).
  const VS_SEGMENTS = [
    { key: "uNo",      cls: "no-inf"   },
    { key: "sNo",      cls: "no"       },
    { key: "sUnknown", cls: "unknown"  },
    { key: "sYes",     cls: "yes"      },
    { key: "uYes",     cls: "yes-inf"  },
    { key: "absU",     cls: "absent-u" },
    { key: "absS",     cls: "absent"   },
  ];

  function barSegments(b, total) {
    return VS_SEGMENTS
      .filter(s => b[s.key] > 0)
      .map(s => `<span class="vs-seg ${s.cls}" style="width:${(b[s.key]/total*100).toFixed(1)}%" title="${b[s.key]}"></span>`)
      .join("");
  }

  function renderVotingStatsCard(stats) {
    const t = stats.total;
    // absolut + relativ, überall gleiches Format
    const fmt = (n) => `${n} (${t.total ? Math.round(n / t.total * 100) : 0}%)`;
    const details = document.createElement("details");
    details.className = "voting-stats";
    details.innerHTML = `
      <summary>
        <svg class="icon"><use href="#i-insights"/></svg>
        <span>Statistik anzeigen</span>
        <span class="vs-total-count">${t.total} Abst.</span>
      </summary>
      <div class="vs-content">
        <div class="vs-summary">
          <div class="vs-bar">${barSegments(t, t.total)}</div>

          <div class="vs-legend">
            <div class="vs-legend-row vs-group">
              <span class="vs-legend-head">Einstimmig</span>
              <span class="vs-legend-share">${fmt(t.uYes + t.uNo)}</span>
            </div>
            <div class="vs-legend-row vs-sub">
              <span class="vs-dot yes-inf"></span>Ja ${fmt(t.uYes)}
              <span class="vs-dot no-inf"></span>Nein ${fmt(t.uNo)}
            </div>

            <div class="vs-legend-row vs-group">
              <span class="vs-legend-head">Nicht einstimmig</span>
              <span class="vs-legend-share">${fmt(t.sYes + t.sNo + t.sUnknown)}</span>
            </div>
            <div class="vs-legend-row vs-sub">
              <span class="vs-dot yes"></span>Ja ${fmt(t.sYes)}
              <span class="vs-dot unknown"></span>Unbekannt ${fmt(t.sUnknown)}
              <span class="vs-dot no"></span>Nein ${fmt(t.sNo)}
            </div>

            <div class="vs-legend-row vs-group">
              <span class="vs-legend-head">Abwesend</span>
              <span class="vs-legend-share">${fmt(t.absU + t.absS)}</span>
            </div>
            <div class="vs-legend-row vs-sub">
              <span class="vs-dot absent-u"></span>bei einstimmigen ${fmt(t.absU)}
              <span class="vs-dot absent"></span>bei nicht einstimmigen ${fmt(t.absS)}
            </div>
          </div>
        </div>
        ${renderStatsBreakdown("Pro Jahr",    stats.byYear,   k => k)}
        ${renderStatsBreakdown("Pro Periode", stats.byPeriod, k => k)}
        ${renderStatsBreakdown("Pro Gremium", stats.byBody,   k => bodyMap[k] ? bodyMap[k].shortName : k)}
      </div>`;
    return details;
  }

  function renderStatsBreakdown(title, bucket, keyLabel) {
    const keys = Object.keys(bucket).sort();
    if (!keys.length) return "";
    const rows = keys.map(k => {
      const b = bucket[k];
      return `
        <div class="vs-row">
          <div class="vs-row-label">${keyLabel(k)}</div>
          <div class="vs-row-bar">${barSegments(b, b.total)}</div>
          <div class="vs-row-count">${b.total}</div>
        </div>`;
    }).join("");
    return `<div class="vs-section"><h4>${title}</h4>${rows}</div>`;
  }

  function makeContactLink(type, href) {
    const a = document.createElement("a");
    a.className = "contact-link cl-" + type;
    a.href = href;
    a.target = "_blank";
    a.rel = "noopener";
    const labels = {
      email: "E-Mail", website: "Website", instagram: "Instagram",
      threads: "Threads", linkedin: "LinkedIn", facebook: "Facebook",
    };
    a.setAttribute("aria-label", labels[type] || type);
    // Brand-Pfade aus Font Awesome Free 6.5.1 (CC BY 4.0), inline statt CDN
    const icons = {
      email: '<svg class="icon"><use href="#i-email"/></svg>',
      website: '<svg class="icon"><use href="#i-language"/></svg>',
      instagram: '<svg viewBox="0 0 448 512"><path d="M224.1 141c-63.6 0-114.9 51.3-114.9 114.9s51.3 114.9 114.9 114.9S339 319.5 339 255.9 287.7 141 224.1 141zm0 189.6c-41.1 0-74.7-33.5-74.7-74.7s33.5-74.7 74.7-74.7 74.7 33.5 74.7 74.7-33.6 74.7-74.7 74.7zm146.4-194.3c0 14.9-12 26.8-26.8 26.8-14.9 0-26.8-12-26.8-26.8s12-26.8 26.8-26.8 26.8 12 26.8 26.8zm76.1 27.2c-1.7-35.9-9.9-67.7-36.2-93.9-26.2-26.2-58-34.4-93.9-36.2-37-2.1-147.9-2.1-184.9 0-35.8 1.7-67.6 9.9-93.9 36.1s-34.4 58-36.2 93.9c-2.1 37-2.1 147.9 0 184.9 1.7 35.9 9.9 67.7 36.2 93.9s58 34.4 93.9 36.2c37 2.1 147.9 2.1 184.9 0 35.9-1.7 67.7-9.9 93.9-36.2 26.2-26.2 34.4-58 36.2-93.9 2.1-37 2.1-147.8 0-184.8zM398.8 388c-7.8 19.6-22.9 34.7-42.6 42.6-29.5 11.7-99.5 9-132.1 9s-102.7 2.6-132.1-9c-19.6-7.8-34.7-22.9-42.6-42.6-11.7-29.5-9-99.5-9-132.1s-2.6-102.7 9-132.1c7.8-19.6 22.9-34.7 42.6-42.6 29.5-11.7 99.5-9 132.1-9s102.7-2.6 132.1 9c19.6 7.8 34.7 22.9 42.6 42.6 11.7 29.5 9 99.5 9 132.1s2.7 102.7-9 132.1z"/></svg>',
      threads: '<svg viewBox="0 0 448 512"><path d="M331.5 235.7c2.2 .9 4.2 1.9 6.3 2.8c29.2 14.1 50.6 35.2 61.8 61.4c15.7 36.5 17.2 95.8-30.3 143.2c-36.2 36.2-80.3 52.5-142.6 53h-.3c-70.2-.5-124.1-24.1-160.4-70.2c-32.3-41-48.9-98.1-49.5-169.6V256v-.2C17 184.3 33.6 127.2 65.9 86.2C102.2 40.1 156.2 16.5 226.4 16h.3c70.3 .5 124.9 24 162.3 69.9c18.4 22.7 32 50 40.6 81.7l-40.4 10.8c-7.1-25.8-17.8-47.8-32.2-65.4c-29.2-35.8-73-54.2-130.5-54.6c-57 .5-100.1 18.8-128.2 54.4C72.1 146.1 58.5 194.3 58 256c.5 61.7 14.1 109.9 40.3 143.3c28 35.6 71.2 53.9 128.2 54.4c51.4-.4 85.4-12.6 113.7-40.9c32.3-32.2 31.7-71.8 21.4-95.9c-6.1-14.2-17.1-26-31.9-34.9c-3.7 26.9-11.8 48.3-24.7 64.8c-17.1 21.8-41.4 33.6-72.7 35.3c-23.6 1.3-46.3-4.4-63.9-16c-20.8-13.8-33-34.8-34.3-59.3c-2.5-48.3 35.7-83 95.2-86.4c21.1-1.2 40.9-.3 59.2 2.8c-2.4-14.8-7.3-26.6-14.6-35.2c-10-11.7-25.6-17.7-46.2-17.8H227c-16.6 0-39 4.6-53.3 26.3l-34.4-23.6c19.2-29.1 50.3-45.1 87.8-45.1h.8c62.6 .4 99.9 39.5 103.7 107.7l-.2 .2zm-156 68.8c1.3 25.1 28.4 36.8 54.6 35.3c25.6-1.4 54.6-11.4 59.5-73.2c-13.2-2.9-27.8-4.4-43.4-4.4c-4.8 0-9.6 .1-14.4 .4c-42.9 2.4-57.2 23.2-56.2 41.8l-.1 .1z"/></svg>',
      linkedin: '<svg viewBox="0 0 448 512"><path d="M100.28 448H7.4V148.9h92.88zM53.79 108.1C24.09 108.1 0 83.5 0 53.8a53.79 53.79 0 0 1 107.58 0c0 29.7-24.1 54.3-53.79 54.3zM447.9 448h-92.68V302.4c0-34.7-.7-79.2-48.29-79.2-48.29 0-55.69 37.7-55.69 76.7V448h-92.78V148.9h89.08v40.8h1.3c12.4-23.5 42.69-48.3 87.88-48.3 94 0 111.28 61.9 111.28 142.3V448z"/></svg>',
      facebook: '<svg viewBox="0 0 320 512"><path d="M80 299.3V512H196V299.3h86.5l18-97.8H196V166.9c0-51.7 20.3-71.5 72.7-71.5c16.3 0 29.4 .4 37 1.2V7.9C291.4 4 256.4 0 236.2 0C129.3 0 80 50.5 80 159.4v42.1H14v97.8H80z"/></svg>',
    };
    a.innerHTML = icons[type] || '<svg class="icon"><use href="#i-link"/></svg>';
    return a;
  }

  function makeRoleRow(icon, text, from, to) {
    const row = document.createElement("div");
    row.className = "role-row";
    row.innerHTML = `
      <svg class="icon"><use href="#i-${icon}"/></svg>
      <span>${text}</span>
      <span class="role-dates">${formatPeriod(from, to)}</span>`;
    return row;
  }

  // -- Member timeline --

  function renderMemberTimeline(container, member) {
    const relevant = sessionsSorted.filter(s => memberActiveAt(member, s.date));

    if (!relevant.length) {
      container.innerHTML = '<p style="color:var(--text-muted);font-size:0.88rem">Keine Sitzungsdaten vorhanden.</p>';
      return;
    }

    let currentMonth = "";

    relevant.forEach(session => {
      const d = new Date(session.date + "T00:00:00");
      const monthKey = monthNames[d.getMonth()] + " " + d.getFullYear();

      if (monthKey !== currentMonth) {
        currentMonth = monthKey;
        const header = document.createElement("div");
        header.className = "mtl-month-header";
        header.textContent = monthKey;
        container.appendChild(header);
      }

      const votedItems = session.agenda.filter(a => a.voteId && voteMap[a.voteId]);
      if (!votedItems.length) return;

      const sessionEl = document.createElement("div");
      sessionEl.className = "mtl-session";

      const icon = (session.type && session.type !== "stadtrat") ? "groups" : "account_balance";
      const sHeader = document.createElement("div");
      sHeader.className = "mtl-session-header";
      sHeader.innerHTML = `<svg class="icon"><use href="#i-${icon}"/></svg> <a href="#/session/${session.id}">${session.title}</a>`;
      sessionEl.appendChild(sHeader);

      votedItems.forEach(item => {
        const vote = voteMap[item.voteId];
        const status = Council.voteStatus(member.id, vote, session, member);
        if (status === null) return;
        // Einstimmig mitgegangen \u2192 blasser Chip (gleiche Logik wie Statistik)
        const isUnanimous = Council.isUnanimous(vote);
        const base = status.replace("-inferred", "");
        const chipClass = ({ yes: "ja", no: "nein", absent: "abwesend",
                            excluded: "sonder", abstained: "sonder",
                            restricted: "sonder" }[base] || "unknown")
                        + (isUnanimous ? " inferred" : "");
        const chipLabel = Council.voteStatusLabel(status);

        const voteRow = document.createElement("div");
        voteRow.className = "mtl-vote";
        voteRow.innerHTML = `
          <span class="mtl-vote-chip ${chipClass}" title="${Council.voteStatusTitle(status)}">${chipLabel}</span>
          <span class="mtl-vote-title">${vote.title}</span>`;

        const detail = document.createElement("div");
        detail.className = "mtl-vote-detail hidden";
        let detailHTML = `<p>${vote.text}</p>`;
        if (vote.type === "anonymous") {
          detailHTML += `<p style="margin-top:4px">${vote.results.yes} Ja, ${vote.results.no} Nein, ${vote.results.absent} Abwesend</p>`;
        }
        if (item.topicId && topicMap[item.topicId]) {
          detailHTML += `<a href="#/topic/${item.topicId}"><svg class="icon"><use href="#i-open_in_new"/></svg> ${topicMap[item.topicId].title}</a>`;
        }
        detail.innerHTML = detailHTML;

        voteRow.querySelector(".mtl-vote-title").addEventListener("click", () => {
          detail.classList.toggle("hidden");
        });

        sessionEl.appendChild(voteRow);
        sessionEl.appendChild(detail);
      });

      container.appendChild(sessionEl);
    });
  }

  // -- Helpers --

  function formatDate(iso) {
    const d = new Date(iso + "T00:00:00");
    return d.toLocaleDateString("de-DE", { day: "numeric", month: "long", year: "numeric" });
  }

  function formatPeriod(from, to) {
    const f = from ? from.substring(0, 4) : "";
    const t = to ? to.substring(0, 4) : "heute";
    return f + "\u2013" + t;
  }

  route();
})();
