// Sitzungsseite: Kopf mit Dauer und Niederschrift, Vertretungen,
// Tagesordnung mit eingebetteten Abstimmungen.
import {
  sessionMap, bodyMap, memberMap, topicMap, voteMap, lengthMap,
  lengthMin, protocolUrl, isWebauszug,
} from "../daten.js";
import { formatDate, formatDuration } from "../hilfen.js";
import { navigate, setChrome } from "../routing.js";
import { renderPressLinks } from "./themen.js";
import { renderVoteBlock } from "./voten.js";

const main = document.getElementById("main");

// -- Session detail --

function renderSession(id) {
  setChrome("sitzung");
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
  const src = isWebauszug(session)
    ? (session.source.url
        ? `<a class="session-pdf" href="${session.source.url}" target="_blank" rel="noopener">
             <svg class="icon"><use href="#i-language"/></svg> Beschlussauszug der Stadt Moosburg</a>`
        : "")
    : `<a class="session-pdf" href="${protocolUrl(session)}" target="_blank" rel="noopener">
         <svg class="icon"><use href="#i-description"/></svg> Niederschrift (PDF)</a>`;
  header.innerHTML = `<h1>${session.title}</h1><div class="session-date">${formatDate(session.date)}</div>${timeLine}${badge}${src}`;
  main.appendChild(header);

  if (isWebauszug(session)) {
    const note = document.createElement("div");
    note.className = "source-note";
    note.innerHTML = `
      <svg class="icon"><use href="#i-info"/></svg>
      <div><strong>Keine Niederschrift veröffentlicht.</strong>
      Beschlüsse und Ergebnisse dieser Sitzung stammen aus dem Beschlussauszug auf der
      Website der Stadt. Eine Anwesenheitsliste wird dort nicht veröffentlicht — wer
      gefehlt hat, ist deshalb unbekannt. Nur wenn alle regulären Sitze mitgestimmt haben,
      lässt sich das Stimmverhalten den Personen zuordnen.</div>`;
    main.appendChild(note);
  }

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

  // Presse zum Abend als Ganzes. Ein Lokalbericht handelt meist mehrere
  // Punkte ab; die Kopfzeile zeigt, was über die Sitzung geschrieben wurde,
  // die Artikel stehen zusätzlich an den Punkten, die sie wirklich behandeln.
  const sessionPress = renderPressLinks(session.press);
  if (sessionPress) {
    const wrap = document.createElement("div");
    wrap.className = "session-press";
    wrap.innerHTML = "<span>Presse zur Sitzung</span>";
    wrap.appendChild(sessionPress);
    main.appendChild(wrap);
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
    if (item.note) el.innerHTML += `<p class="ai-note">${item.note}</p>`;

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

export { renderSession };
