// Main application: data loading, routing, search, tabs, calendar, gremien.

(async function () {
  const main = document.getElementById("main");
  const gremienMain = document.getElementById("gremien-main");

  let topics, sessions, votes, tags, membersData;
  try {
    [topics, sessions, votes, tags, membersData] = await Promise.all([
      fetch("data/topics.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
      fetch("data/sessions.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
      fetch("data/votes.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
      fetch("data/tags.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
      fetch("data/members.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
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

  const nowStr = (() => {
    const n = new Date();
    return n.getFullYear() + "-" + String(n.getMonth() + 1).padStart(2, "0");
  })();

  function isActive(m) {
    if (m.to && m.to <= nowStr) return false;
    if (m.from > nowStr) return false;
    return true;
  }

  // -- Search (Themen tab) --

  const searchInput = document.getElementById("search");
  const dropdown = document.getElementById("search-dropdown");
  const tagBar = document.getElementById("tag-bar");

  tags.forEach(tag => {
    const pill = document.createElement("button");
    pill.className = "tag-pill";
    pill.textContent = tag.name;
    pill.addEventListener("click", () => {
      pill.classList.toggle("active");
      const active = tagBar.querySelectorAll(".tag-pill.active");
      if (active.length === 0) {
        navigate("/");
      } else {
        const activeIds = Array.from(active).map(el => tags.find(t => t.name === el.textContent).id);
        showFilteredTopics(activeIds);
      }
    });
    tagBar.appendChild(pill);
  });

  function clearActiveTags() {
    tagBar.querySelectorAll(".tag-pill.active").forEach(p => p.classList.remove("active"));
  }

  searchInput.addEventListener("input", () => {
    const q = searchInput.value.trim().toLowerCase();
    if (q.length < 1) { dropdown.classList.add("hidden"); return; }

    const results = [];
    tags.forEach(t => {
      if (t.name.toLowerCase().includes(q)) results.push({ type: "tag", item: t });
    });
    topics.forEach(t => {
      if (t.title.toLowerCase().includes(q)) results.push({ type: "topic", item: t });
    });
    sessions.forEach(s => {
      if (s.title.toLowerCase().includes(q)) results.push({ type: "session", item: s });
    });
    members.forEach(m => {
      if (m.name.toLowerCase().includes(q)) results.push({ type: "member", item: m });
    });

    if (results.length === 0) { dropdown.classList.add("hidden"); return; }

    dropdown.innerHTML = "";
    results.slice(0, 12).forEach(r => {
      const div = document.createElement("div");
      div.className = "dd-item";
      const labels = { tag: "Tag", topic: "Thema", session: "Sitzung", member: "Person" };
      div.innerHTML = `<span class="dd-type">${labels[r.type]}</span><span>${r.item.title || r.item.name}</span>`;
      div.addEventListener("click", () => {
        dropdown.classList.add("hidden");
        searchInput.value = "";
        if (r.type === "tag") {
          clearActiveTags();
          const pill = Array.from(tagBar.children).find(p => p.textContent === r.item.name);
          if (pill) pill.classList.add("active");
          showFilteredTopics([r.item.id]);
        } else if (r.type === "topic") {
          switchTab("themen");
          navigate("/topic/" + r.item.id);
        } else if (r.type === "session") {
          switchTab("themen");
          navigate("/session/" + r.item.id);
        } else {
          switchTab("gremien");
          navigate("/member/" + r.item.id);
        }
      });
      dropdown.appendChild(div);
    });
    dropdown.classList.remove("hidden");
  });

  document.addEventListener("click", evt => {
    if (!evt.target.closest(".search-container")) {
      dropdown.classList.add("hidden");
      gremienDropdown.classList.add("hidden");
    }
  });

  // -- Gremien search --

  const gremienSearchInput = document.getElementById("gremien-search");
  const gremienDropdown = document.getElementById("gremien-search-dropdown");

  gremienSearchInput.addEventListener("input", () => {
    const q = gremienSearchInput.value.trim().toLowerCase();
    if (q.length < 1) { gremienDropdown.classList.add("hidden"); return; }

    const results = members.filter(m => m.name.toLowerCase().includes(q));
    if (!results.length) { gremienDropdown.classList.add("hidden"); return; }

    gremienDropdown.innerHTML = "";
    results.slice(0, 10).forEach(m => {
      const div = document.createElement("div");
      div.className = "dd-item";
      const party = partyMap[m.party];
      const status = isActive(m) ? "" : " (ehem.)";
      div.innerHTML = `<span class="member-dot" style="background:${party ? party.color : '#ccc'}"></span><span>${m.name}${status}</span>`;
      div.addEventListener("click", () => {
        gremienDropdown.classList.add("hidden");
        gremienSearchInput.value = "";
        navigate("/member/" + m.id);
      });
      gremienDropdown.appendChild(div);
    });
    gremienDropdown.classList.remove("hidden");
  });

  // -- Routing --

  function navigate(path) {
    window.location.hash = path;
  }

  function route() {
    const hash = window.location.hash.slice(1) || "/";
    if (hash === "/kalender") {
      switchTab("kalender");
      return;
    }
    if (hash === "/einstellungen") {
      switchTab("einstellungen");
      return;
    }
    if (hash === "/gremien") {
      switchTab("gremien");
      return;
    }
    if (hash.startsWith("/member/")) {
      switchTab("gremien");
      renderMemberProfile(hash.split("/member/")[1]);
      return;
    }
    switchTab("themen");
    main.innerHTML = "";
    if (hash.startsWith("/topic/")) {
      renderTopic(hash.split("/topic/")[1]);
    } else if (hash.startsWith("/session/")) {
      renderSession(hash.split("/session/")[1]);
    } else {
      renderHome();
    }
  }

  window.addEventListener("hashchange", route);

  // -- Views --

  function renderHome() {
    clearActiveTags();
    const heading = document.createElement("p");
    heading.className = "section-heading";
    heading.textContent = "Alle Themen";
    main.appendChild(heading);
    renderTopicList(topics);
  }

  function showFilteredTopics(tagIds) {
    window.location.hash = "/";
    main.innerHTML = "";
    const filtered = topics.filter(t => tagIds.some(id => t.tags.includes(id)));
    const label = tagIds.map(id => tagMap[id].name).join(", ");
    const heading = document.createElement("p");
    heading.className = "section-heading";
    heading.textContent = "Themen: " + label;
    main.appendChild(heading);
    renderTopicList(filtered);
  }

  function renderTopicList(list) {
    const wrap = document.createElement("div");
    wrap.className = "topic-list";
    list.forEach(topic => {
      const card = document.createElement("div");
      card.className = "topic-card";
      card.addEventListener("click", () => navigate("/topic/" + topic.id));
      card.innerHTML = `
        <h3>${topic.title}</h3>
        <div class="topic-summary">${topic.summary}</div>
        <div class="topic-tags">
          ${topic.tags.map(tid => `<span class="tag-sm">${tagMap[tid] ? tagMap[tid].name : tid}</span>`).join("")}
        </div>`;
      wrap.appendChild(card);
    });
    main.appendChild(wrap);
  }

  // -- Topic detail --

  const tlIcons = {
    proposal: "description",
    committee: "groups",
    milestone: "flag",
  };

  function renderPressLinks(pressArr) {
    if (!pressArr || !pressArr.length) return null;
    const wrap = document.createElement("div");
    wrap.className = "press-links";
    pressArr.forEach(p => {
      const src = mediaMap[p.media];
      if (!src) return;
      const a = document.createElement("a");
      a.className = "press-link";
      a.href = p.url;
      a.target = "_blank";
      a.rel = "noopener";
      a.title = p.title || src.name;
      a.style.background = src.color;
      a.innerHTML = `<img src="${src.logo}" alt="${src.name}">`;
      wrap.appendChild(a);
    });
    return wrap;
  }

  function renderTopic(id) {
    const topic = topicMap[id];
    if (!topic) { main.innerHTML = "<p>Thema nicht gefunden.</p>"; return; }

    const back = document.createElement("a");
    back.className = "back-link";
    back.href = "#/";
    back.innerHTML = '<span class="material-icons">arrow_back</span> \u00dcbersicht';
    back.addEventListener("click", e => {
      if (window.history.length > 1) { e.preventDefault(); window.history.back(); }
    });
    main.appendChild(back);

    const header = document.createElement("div");
    header.className = "topic-header";
    header.innerHTML = `
      <h1>${topic.title}</h1>
      <div class="topic-summary">${topic.summary}</div>
      <div class="topic-tags">${topic.tags.map(tid => `<span class="tag-sm">${tagMap[tid] ? tagMap[tid].name : tid}</span>`).join("")}</div>`;
    main.appendChild(header);

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
      if (iconName) dot.innerHTML = `<span class="material-icons">${iconName}</span>`;
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
        link.innerHTML = '<span class="material-icons" style="font-size:14px;vertical-align:-2px">open_in_new</span> ' + sessionMap[entry.sessionId].title;
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
    back.innerHTML = '<span class="material-icons">arrow_back</span> \u00dcbersicht';
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
      badge = `<div class="session-badge"><span class="material-icons">groups</span> ${label}</div>`;
    }
    header.innerHTML = `<h1>${session.title}</h1><div class="session-date">${formatDate(session.date)}</div>${badge}`;
    main.appendChild(header);

    if (session.substitutes && session.substitutes.length) {
      const subs = document.createElement("div");
      subs.className = "session-subs";
      session.substitutes.forEach(s => {
        const member = memberMap[s.member];
        const sub = memberMap[s.substitute];
        const row = document.createElement("div");
        row.className = "sub-row";
        row.innerHTML = `<span class="material-icons">swap_horiz</span> ${sub ? sub.name : s.substitute} f\u00fcr ${member ? member.name : s.member}`;
        subs.appendChild(row);
      });
      main.appendChild(subs);
    }

    const list = document.createElement("div");
    list.className = "agenda-list";

    session.agenda.forEach(item => {
      const el = document.createElement("div");
      el.className = "agenda-item";

      if (item.topicId && topicMap[item.topicId]) {
        el.classList.add("has-link");
        el.addEventListener("click", () => navigate("/topic/" + item.topicId));
      }

      el.innerHTML = `
        <div class="ai-number">TOP ${item.number}</div>
        <h3>${item.title}</h3>`;

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

      list.appendChild(el);
    });

    main.appendChild(list);
  }

  // -- Vote block --

  function renderVoteBlock(container, vote) {
    const block = document.createElement("div");
    block.className = "vote-block";

    const isRejected = vote.result === "rejected";
    const tagClass = isRejected ? "rejected" : "approved";
    const tagText = isRejected ? "Abgelehnt" : "Zugestimmt";
    const resultTag = `<span class="vote-result-tag ${tagClass}">${tagText}</span>`;

    block.innerHTML = `
      <h4>${vote.title}${resultTag}</h4>
      <div class="vote-text">${vote.text}</div>
      <div class="vote-legend">
        <span><span class="legend-dot yes"></span> Ja</span>
        <span><span class="legend-dot no"></span> Nein</span>
        <span><span class="legend-dot absent"></span> Abwesend</span>
      </div>`;

    const chartEl = document.createElement("div");
    block.appendChild(chartEl);
    container.appendChild(block);

    requestAnimationFrame(() => {
      if (vote.type === "anonymous") {
        VoteVis.drawBar(chartEl, vote.results);
      } else {
        VoteVis.drawParliament(chartEl, vote, members, parties, seatOrder);
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
      const row = document.createElement("div");
      row.className = "sheet-event";
      if (s.type && s.type !== "stadtrat") row.classList.add(s.type);
      const icon = s.type === "bpu" ? "engineering" : "account_balance";
      row.innerHTML = `
        <span class="material-icons">${icon}</span>
        <div class="sheet-event-text">${s.title}</div>
        <span class="material-icons">chevron_right</span>`;
      row.addEventListener("click", () => {
        calSheet.classList.add("hidden");
        switchTab("themen");
        navigate("/session/" + s.id);
      });
      calSheetBody.appendChild(row);
    });

    calSheet.classList.remove("hidden");
  }

  // -- Gremien tab --

  let gremienRendered = false;

  function renderGremien() {
    const hash = window.location.hash.slice(1) || "/";
    if (hash.startsWith("/member/")) {
      renderMemberProfile(hash.split("/member/")[1]);
      return;
    }
    if (gremienRendered) return;
    gremienRendered = true;
    gremienMain.innerHTML = "";

    const wrap = document.createElement("div");
    wrap.style.cssText = "max-width:800px;margin:0 auto;padding:24px 24px 64px;";

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
      fh.style.cssText = "display:flex;align-items:center;gap:8px;margin:16px 0 6px;";
      fh.innerHTML = `<span class="member-dot" style="background:${party.color};width:10px;height:10px"></span><span style="font-weight:600;font-size:0.9rem">${party.name}</span><span style="font-size:0.78rem;color:var(--text-muted)">${group.length}</span>`;
      factionSec.appendChild(fh);
      group.sort((a, b) => a.name.localeCompare(b.name));
      group.forEach(m => factionSec.appendChild(makeMemberRow(m)));
    });

    if (activeMayor) {
      const mh = document.createElement("div");
      mh.style.cssText = "display:flex;align-items:center;gap:8px;margin:16px 0 6px;";
      const mp = partyMap[activeMayor.party];
      mh.innerHTML = `<span class="member-dot" style="background:${mp ? mp.color : '#999'};width:10px;height:10px"></span><span style="font-weight:600;font-size:0.9rem">B\u00fcrgermeister</span>`;
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
        <span class="material-icons">${body.icon || 'groups'}</span>
        <div>
          <div class="body-card-title">${body.name}</div>
          ${count ? `<div class="body-card-count">${count} Mitglieder</div>` : ''}
        </div>
        <span class="material-icons expand-icon">expand_more</span>
      </div>
      <div class="body-card-detail"></div>`;

    const detail = card.querySelector(".body-card-detail");

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

      let html = "<thead><tr><th>Mitglied</th>";
      if (hasSubs) html += "<th></th><th>Stellvertretung</th>";
      html += "</tr></thead><tbody>";

      // chair
      if (body.chair && memberMap[body.chair]) {
        const ch = memberMap[body.chair];
        const chp = partyMap[ch.party];
        html += `<tr><td class="seat-name" data-mid="${ch.id}"><span class="member-dot" style="background:${chp ? chp.color : '#ccc'}"></span> ${ch.name} <span style="font-size:0.72rem;color:var(--text-muted)">(Vorsitz)</span></td>`;
        if (hasSubs) {
          if (body.chairSub && memberMap[body.chairSub]) {
            const cs = memberMap[body.chairSub];
            html += `<td><span class="material-icons swap-icon">swap_horiz</span></td><td class="seat-sub" data-mid="${cs.id}">${cs.name}</td>`;
          } else {
            html += "<td></td><td></td>";
          }
        }
        html += "</tr>";
      }

      // vice-chairs
      if (body.vicechairs) {
        body.vicechairs.forEach(vc => {
          const m = memberMap[vc.member];
          if (!m) return;
          const p = partyMap[m.party];
          html += `<tr><td class="seat-name" data-mid="${m.id}"><span class="member-dot" style="background:${p ? p.color : '#ccc'}"></span> ${m.name} <span style="font-size:0.72rem;color:var(--text-muted)">(Stellv. Vorsitz)</span></td>`;
          if (vc.sub && memberMap[vc.sub]) {
            const s = memberMap[vc.sub];
            html += `<td><span class="material-icons swap-icon">swap_horiz</span></td><td class="seat-sub" data-mid="${s.id}">${s.name}</td>`;
          } else {
            html += "<td></td><td></td>";
          }
          html += "</tr>";
        });
      }

      // regular seats
      body.seats.forEach(seat => {
        const m = memberMap[seat.member];
        if (!m) return;
        const p = partyMap[m.party];
        const roleTag = seat.role ? ` <span style="font-size:0.72rem;color:var(--text-muted)">(${seat.role})</span>` : "";
        html += `<tr><td class="seat-name" data-mid="${m.id}"><span class="member-dot" style="background:${p ? p.color : '#ccc'}"></span> ${m.name}${roleTag}</td>`;
        if (hasSubs) {
          if (seat.sub && memberMap[seat.sub]) {
            const s = memberMap[seat.sub];
            html += `<td><span class="material-icons swap-icon">swap_horiz</span></td><td class="seat-sub" data-mid="${s.id}">${s.name}</td>`;
          } else {
            html += "<td></td><td></td>";
          }
        }
        html += "</tr>";
      });

      html += "</tbody>";
      table.innerHTML = html;

      table.querySelectorAll("[data-mid]").forEach(el => {
        el.addEventListener("click", e => {
          e.stopPropagation();
          navigate("/member/" + el.dataset.mid);
        });
      });

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
    const row = document.createElement("div");
    row.className = "member-row";
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
    row.addEventListener("click", e => {
      e.stopPropagation();
      navigate("/member/" + m.id);
    });
    return row;
  }

  // -- Member profile --

  function nameColorFromParty(hex) {
    if (!hex) return "#555";
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    const lum = 0.299 * r + 0.587 * g + 0.114 * b;
    if (lum < 40) return "#666";
    const f = lum > 180 ? 0.4 : lum > 120 ? 0.55 : 0.7;
    return "#" + [r, g, b].map(c => Math.round(c * f).toString(16).padStart(2, "0")).join("");
  }

  function renderMemberProfile(id) {
    const m = memberMap[id];
    if (!m) { gremienMain.innerHTML = "<p style='padding:40px 24px'>Person nicht gefunden.</p>"; return; }

    gremienMain.innerHTML = "";
    const wrap = document.createElement("div");
    wrap.style.cssText = "max-width:800px;margin:0 auto;padding:32px 24px 64px;";

    const back = document.createElement("a");
    back.className = "back-link";
    back.href = "#/";
    back.innerHTML = '<span class="material-icons">arrow_back</span> Gremien';
    back.addEventListener("click", e => {
      e.preventDefault();
      if (window.history.length > 1) {
        gremienRendered = false;
        window.history.back();
      } else {
        gremienRendered = false;
        window.location.hash = "/";
        renderGremien();
      }
    });
    wrap.appendChild(back);

    const party = partyMap[m.party];
    const profile = m.profile || {};

    // header
    const header = document.createElement("div");
    header.className = "profile-header";
    const initial = (m.firstName || m.name).charAt(0);
    const neeSuffix = m.nee ? ` <span class="profile-nee">(geb. ${m.nee})</span>` : "";
    const photoPath = "img/members/" + m.id + ".png";
    const avatarColor = party ? party.color : '#999';
    const nameColor = nameColorFromParty(avatarColor);

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
          <div class="profile-surname" style="color:${nameColor}">${m.lastName || m.name}${neeSuffix}</div>
          ${profile.pronouns ? `<div class="profile-pronouns">${profile.pronouns}</div>` : ""}
          <div class="profile-party"><span class="profile-party-dot" style="background:${avatarColor}"></span>${party ? party.name : ""}${m.title ? " \u2013 " + m.title : ""}</div>
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
        b.innerHTML = (badgeIcons[id] ? `<span class="material-icons">${badgeIcons[id]}</span> ` : "") + (labels[id] || id);
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
      avatarEl.style.backgroundImage = "url('" + photoPath + "')";
      avatarEl.style.backgroundSize = "cover";
      avatarEl.style.backgroundPosition = "center";
      avatarEl.style.backgroundColor = "transparent";
      avatarEl.textContent = "";
    };
    testImg.onerror = () => {};
    testImg.src = photoPath;

    header.addEventListener("contextmenu", e => e.preventDefault());

    // roles & committees
    const rolesSection = document.createElement("div");
    rolesSection.className = "profile-section";
    rolesSection.innerHTML = "<h3>Mandate & Funktionen</h3>";

    const roleLabel = m.role === "mayor" ? "B\u00fcrgermeister" : "Stadtrat";
    rolesSection.appendChild(makeRoleRow("account_balance", roleLabel, m.from, m.to));

    if (m.title) {
      rolesSection.appendChild(makeRoleRow("star", m.title, m.from, m.to));
    }

    if (profile.titles) {
      profile.titles.forEach(t => {
        rolesSection.appendChild(makeRoleRow("badge", t.title, t.from, t.to));
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
          ? `<a href="#/session/${mot.sessionId}" style="display:inline-flex;align-items:center;gap:3px;color:var(--primary);text-decoration:none;font-size:0.78rem;margin-top:2px"><span class="material-icons" style="font-size:13px">open_in_new</span>${sessionMap[mot.sessionId].title}</a>`
          : "";
        el.innerHTML = `
          <span class="material-icons">edit_note</span>
          <div>
            <div class="mtl-motion-title">${mot.title}</div>
            <div class="mtl-motion-meta">${mot.body} \u2013 ${formatDate(mot.date)}</div>
            ${coNames ? `<div class="mtl-motion-meta">gemeinsam mit ${coNames}</div>` : ""}
            ${sessionLink}
          </div>`;
        motionSec.appendChild(el);
      });
      wrap.appendChild(motionSec);
    }

    // personal timeline
    const tlSection = document.createElement("div");
    tlSection.className = "profile-section";
    tlSection.innerHTML = "<h3>Abstimmungsverhalten</h3>";
    wrap.appendChild(tlSection);

    const tlWrap = document.createElement("div");
    renderMemberTimeline(tlWrap, m);
    wrap.appendChild(tlWrap);

    gremienMain.appendChild(wrap);
  }

  function makeContactLink(type, href) {
    const a = document.createElement("a");
    a.className = "contact-link cl-" + type;
    a.href = href;
    a.target = "_blank";
    a.rel = "noopener";
    const icons = {
      email: '<i class="fas fa-envelope"></i>',
      website: '<i class="fas fa-globe"></i>',
      instagram: '<i class="fab fa-instagram"></i>',
      threads: '<i class="fab fa-threads"></i>',
      linkedin: '<i class="fab fa-linkedin-in"></i>',
      facebook: '<i class="fab fa-facebook"></i>',
    };
    a.innerHTML = icons[type] || '<i class="fas fa-link"></i>';
    return a;
  }

  function makeRoleRow(icon, text, from, to) {
    const row = document.createElement("div");
    row.className = "role-row";
    row.innerHTML = `
      <span class="material-icons">${icon}</span>
      <span>${text}</span>
      <span class="role-dates">${formatPeriod(from, to)}</span>`;
    return row;
  }

  // -- Member timeline --

  function renderMemberTimeline(container, member) {
    const from = member.from;
    const to = member.to || "9999-12";

    const relevant = sessionsSorted.filter(s => {
      const ym = s.date.substring(0, 7);
      return ym >= from && ym <= to;
    });

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
      sHeader.innerHTML = `<span class="material-icons">${icon}</span> <a href="#/session/${session.id}">${session.title}</a>`;
      sessionEl.appendChild(sHeader);

      votedItems.forEach(item => {
        const vote = voteMap[item.voteId];
        const voteStatus = getMemberVoteStatus(member.id, vote, session);
        const chipClass = { ja: "ja", nein: "nein", abwesend: "abwesend", "?": "unknown" }[voteStatus];
        const chipLabel = { ja: "Ja", nein: "Nein", abwesend: "\u2013", "?": "?" }[voteStatus];

        const voteRow = document.createElement("div");
        voteRow.className = "mtl-vote";
        voteRow.innerHTML = `
          <span class="mtl-vote-chip ${chipClass}">${chipLabel}</span>
          <span class="mtl-vote-title">${vote.title}</span>`;

        const detail = document.createElement("div");
        detail.className = "mtl-vote-detail hidden";
        let detailHTML = `<p>${vote.text}</p>`;
        if (vote.type === "anonymous") {
          detailHTML += `<p style="margin-top:4px">${vote.results.yes} Ja, ${vote.results.no} Nein, ${vote.results.absent} Abwesend</p>`;
        }
        if (item.topicId && topicMap[item.topicId]) {
          detailHTML += `<a href="#/topic/${item.topicId}"><span class="material-icons" style="font-size:14px">open_in_new</span> ${topicMap[item.topicId].title}</a>`;
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

  function getMemberVoteStatus(memberId, vote, session) {
    if (session && session.absent && session.absent.includes(memberId)) return "abwesend";
    if (vote.type === "named") {
      if (vote.results.yes.includes(memberId)) return "ja";
      if (vote.results.no.includes(memberId)) return "nein";
      if (vote.results.absent.includes(memberId)) return "abwesend";
    }
    if (vote.type === "anonymous" && vote.results.no === 0) {
      return "ja";
    }
    return "?";
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
