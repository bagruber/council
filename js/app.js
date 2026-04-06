// Main application: data loading, routing, search, tabs, calendar.

(async function () {
  const main = document.getElementById("main");

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
    main.innerHTML = `<p style="color:var(--no);padding:40px 0">Daten konnten nicht geladen werden. Bitte mit einem lokalen Webserver öffnen (z.B. <code>npx serve</code>).</p>`;
    console.error("Datenfehler:", err);
    return;
  }

  const members = membersData.members;
  const parties = membersData.parties;
  const committees = membersData.committees || {};
  const seatOrder = membersData.seatOrder || parties.map(p => p.id);

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
    einstellungen: document.getElementById("tab-einstellungen"),
  };

  function switchTab(name) {
    tabBtns.forEach(b => b.classList.toggle("active", b.dataset.tab === name));
    Object.entries(tabPanes).forEach(([k, el]) => el.classList.toggle("hidden", k !== name));
    if (name === "kalender") renderCalendar();
  }

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => switchTab(btn.dataset.tab));
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

  // -- Search & tags --

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

    if (results.length === 0) { dropdown.classList.add("hidden"); return; }

    dropdown.innerHTML = "";
    results.slice(0, 10).forEach(r => {
      const div = document.createElement("div");
      div.className = "dd-item";
      const typeLabel = r.type === "tag" ? "Tag" : r.type === "topic" ? "Thema" : "Sitzung";
      div.innerHTML = `<span class="dd-type">${typeLabel}</span><span>${r.item.title || r.item.name}</span>`;
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
        } else {
          switchTab("themen");
          navigate("/session/" + r.item.id);
        }
      });
      dropdown.appendChild(div);
    });
    dropdown.classList.remove("hidden");
  });

  document.addEventListener("click", evt => {
    if (!evt.target.closest(".search-container")) dropdown.classList.add("hidden");
  });

  // -- Routing --

  function navigate(path) {
    window.location.hash = path;
  }

  function route() {
    const hash = window.location.hash.slice(1) || "/";
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
    vote: "check_circle",
    milestone: "flag",
  };

  function renderTopic(id) {
    const topic = topicMap[id];
    if (!topic) { main.innerHTML = "<p>Thema nicht gefunden.</p>"; return; }

    const back = document.createElement("a");
    back.className = "back-link";
    back.href = "#/";
    back.innerHTML = '<span class="material-icons">arrow_back</span> Übersicht';
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

      const dot = document.createElement("div");
      dot.className = "tl-dot " + entry.type;
      const iconName = tlIcons[entry.type];
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
    back.innerHTML = '<span class="material-icons">arrow_back</span> Übersicht';
    main.appendChild(back);

    const header = document.createElement("div");
    header.className = "session-header";
    let badge = "";
    if (session.type === "bpu") {
      const comm = committees.bpu;
      badge = `<div class="session-badge"><span class="material-icons">groups</span> ${comm ? comm.shortName : "Ausschuss"}</div>`;
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
        row.innerHTML = `<span class="material-icons">swap_horiz</span> ${sub ? sub.name : s.substitute} für ${member ? member.name : s.member}`;
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

    const rejectedTag = vote.result === "rejected" ? '<span class="rejected-tag">Abgelehnt</span>' : "";

    block.innerHTML = `
      <h4>${vote.title}${rejectedTag}</h4>
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
  const monthNames = ["Januar", "Februar", "März", "April", "Mai", "Juni",
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

    // swipe between months
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
    const startDow = (first.getDay() + 6) % 7; // 0=Monday

    const today = new Date();
    const todayStr = isoDate(today.getFullYear(), today.getMonth(), today.getDate());

    // previous month padding
    const prevLast = new Date(calYear, calMonth, 0);
    for (let i = startDow - 1; i >= 0; i--) {
      const day = prevLast.getDate() - i;
      addDay(day, isoDate(calYear, calMonth - 1, day), true, todayStr);
    }

    // current month
    for (let d = 1; d <= last.getDate(); d++) {
      addDay(d, isoDate(calYear, calMonth, d), false, todayStr);
    }

    // next month padding
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
      row.innerHTML = `
        <span class="sheet-event-dot ${s.type || 'stadtrat'}"></span>
        <div><div class="sheet-event-text">${s.title}</div></div>`;
      row.addEventListener("click", () => {
        calSheet.classList.add("hidden");
        switchTab("themen");
        navigate("/session/" + s.id);
      });
      calSheetBody.appendChild(row);
    });

    calSheet.classList.remove("hidden");
  }

  // -- Helpers --

  function formatDate(iso) {
    const d = new Date(iso + "T00:00:00");
    return d.toLocaleDateString("de-DE", { day: "numeric", month: "long", year: "numeric" });
  }

  route();
})();
