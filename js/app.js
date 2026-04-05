// Main application: data loading, routing, search, views.

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
  const seatOrder = membersData.seatOrder || parties.map(p => p.id);

  // -- Settings modal --
  const settingsBtn = document.querySelector(".nav-settings");
  const settingsOverlay = document.getElementById("settings-overlay");
  const settingsClose = document.getElementById("settings-close");
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

  settingsBtn.addEventListener("click", () => settingsOverlay.classList.remove("hidden"));
  settingsClose.addEventListener("click", () => settingsOverlay.classList.add("hidden"));
  settingsOverlay.addEventListener("click", evt => {
    if (evt.target === settingsOverlay) settingsOverlay.classList.add("hidden");
  });

  const searchInput = document.getElementById("search");
  const dropdown = document.getElementById("search-dropdown");
  const tagBar = document.getElementById("tag-bar");

  // lookup helpers
  const topicMap = {};
  topics.forEach(t => { topicMap[t.id] = t; });
  const sessionMap = {};
  sessions.forEach(s => { sessionMap[s.id] = s; });
  const voteMap = {};
  votes.forEach(v => { voteMap[v.id] = v; });
  const tagMap = {};
  tags.forEach(t => { tagMap[t.id] = t; });

  // -- Render tags in bar --
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
        const activeIds = Array.from(active).map((el, i) => tags.find(t => t.name === el.textContent).id);
        showFilteredTopics(activeIds);
      }
    });
    tagBar.appendChild(pill);
  });

  function clearActiveTags() {
    tagBar.querySelectorAll(".tag-pill.active").forEach(p => p.classList.remove("active"));
  }

  // -- Search --
  searchInput.addEventListener("input", () => {
    const q = searchInput.value.trim().toLowerCase();
    if (q.length < 1) {
      dropdown.classList.add("hidden");
      return;
    }
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

    if (results.length === 0) {
      dropdown.classList.add("hidden");
      return;
    }

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
          navigate("/topic/" + r.item.id);
        } else {
          navigate("/session/" + r.item.id);
        }
      });
      dropdown.appendChild(div);
    });
    dropdown.classList.remove("hidden");
  });

  // close dropdown on outside click
  document.addEventListener("click", evt => {
    if (!evt.target.closest(".search-container")) dropdown.classList.add("hidden");
  });

  // -- Routing via hash --
  function navigate(path) {
    window.location.hash = path;
  }

  function route() {
    const hash = window.location.hash.slice(1) || "/";
    main.innerHTML = "";

    if (hash.startsWith("/topic/")) {
      const id = hash.split("/topic/")[1];
      renderTopic(id);
    } else if (hash.startsWith("/session/")) {
      const id = hash.split("/session/")[1];
      renderSession(id);
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

  // -- Topic detail with timeline --

  const tlIcons = {
    proposal:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
    committee: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    vote:      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>',
    milestone: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/></svg>',
  };

  function renderTopic(id) {
    const topic = topicMap[id];
    if (!topic) { main.innerHTML = "<p>Thema nicht gefunden.</p>"; return; }

    const back = document.createElement("a");
    back.className = "back-link";
    back.href = "#/";
    back.innerHTML = "← Übersicht";
    main.appendChild(back);

    // header
    const header = document.createElement("div");
    header.className = "topic-header";
    header.innerHTML = `
      <h1>${topic.title}</h1>
      <div class="topic-summary">${topic.summary}</div>
      <div class="topic-tags">${topic.tags.map(tid => `<span class="tag-sm">${tagMap[tid] ? tagMap[tid].name : tid}</span>`).join("")}</div>`;
    main.appendChild(header);

    // image
    if (topic.image) {
      const img = document.createElement("img");
      img.className = "topic-image";
      img.src = topic.image;
      img.alt = topic.title;
      main.appendChild(img);
    }

    // timeline
    const timeline = document.createElement("div");
    timeline.className = "timeline";

    topic.history.forEach(entry => {
      const el = document.createElement("div");
      el.className = "tl-entry";

      const dot = document.createElement("div");
      dot.className = "tl-dot " + entry.type;
      dot.innerHTML = tlIcons[entry.type] || "";
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

      // if this entry has a vote, render it inline
      if (entry.voteId && voteMap[entry.voteId]) {
        const voteEl = document.createElement("div");
        voteEl.className = "tl-vote-inline";
        renderVoteBlock(voteEl, voteMap[entry.voteId]);
        el.appendChild(voteEl);
      }

      // link to session
      if (entry.sessionId && sessionMap[entry.sessionId]) {
        const link = document.createElement("a");
        link.className = "tl-session-link";
        link.href = "#/session/" + entry.sessionId;
        link.textContent = "→ " + sessionMap[entry.sessionId].title;
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
    back.innerHTML = "← Übersicht";
    main.appendChild(back);

    const header = document.createElement("div");
    header.className = "session-header";
    header.innerHTML = `<h1>${session.title}</h1><div class="session-date">${formatDate(session.date)}</div>`;
    main.appendChild(header);

    const list = document.createElement("div");
    list.className = "agenda-list";

    session.agenda.forEach(item => {
      const el = document.createElement("div");
      el.className = "agenda-item";

      const hasTopicLink = item.topicId && topicMap[item.topicId];
      if (hasTopicLink) {
        el.classList.add("has-link");
        el.addEventListener("click", () => navigate("/topic/" + item.topicId));
      }

      el.innerHTML = `
        <div class="ai-number">TOP ${item.number}</div>
        <h3>${item.title}</h3>`;

      if (item.type === "formal") {
        el.innerHTML += `<span class="ai-type">Formell</span>`;
      } else if (item.type === "discussion") {
        el.innerHTML += `<span class="ai-type">Beratung</span>`;
      }

      // vote for this agenda item
      if (item.voteId && voteMap[item.voteId]) {
        const voteEl = document.createElement("div");
        renderVoteBlock(voteEl, voteMap[item.voteId]);
        el.appendChild(voteEl);
      }

      list.appendChild(el);
    });

    main.appendChild(list);
  }

  // -- Vote block rendering --

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

    // defer D3 rendering until element is in DOM
    requestAnimationFrame(() => {
      if (vote.type === "anonymous") {
        VoteVis.drawBar(chartEl, vote.results);
      } else {
        VoteVis.drawParliament(chartEl, vote, members, parties, seatOrder);
      }
    });
  }

  // -- Helpers --

  function formatDate(iso) {
    const d = new Date(iso + "T00:00:00");
    return d.toLocaleDateString("de-DE", { day: "numeric", month: "long", year: "numeric" });
  }

  // initial route
  route();
})();
