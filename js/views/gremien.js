// Gremien-Tab: Plenum, Ausschüsse und besondere Gremien als Karten,
// darunter Fraktionen samt der Rubrik "Nicht mehr im Rat".
import {
  members, bodies, seatOrder, partyMap, memberMap, isActive, nowStr,
} from "../daten.js";
import { formatMonthPeriod, formatPeriod } from "../hilfen.js";
import { factionHistory, renderFraktion } from "./fraktion.js";
import { renderMemberProfile } from "./profil.js";

const gremienMain = document.getElementById("gremien-main");

// -- Gremien tab --

function renderGremien() {
  const hash = window.location.hash.slice(1) || "/";
  if (hash.startsWith("/member/")) {
    renderMemberProfile(hash.split("/member/")[1]);
    return;
  }
  if (hash.startsWith("/fraktion/")) {
    renderFraktion(hash.split("/fraktion/")[1]);
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
    const fh = document.createElement("a");
    fh.className = "faction-head";
    fh.href = "#/fraktion/" + pid;
    fh.innerHTML = `<span class="member-dot" style="background:${party.color}"></span><span class="faction-name">${party.name}</span><span class="faction-count">${group.length}</span><svg class="icon faction-go"><use href="#i-chevron_right"/></svg>`;
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

  // Fraktionen, die es im Rat nicht mehr gibt. "parteilos" bleibt draußen —
  // das ist keine Fraktion, sondern deren Fehlen.
  const hist = factionHistory();
  const gone = Object.keys(hist)
    .filter(pid => pid !== "parteilos" && partyMap[pid] && !(grouped[pid] || []).length)
    .sort((a, b) => (hist[b].to || "9999").localeCompare(hist[a].to || "9999"));

  if (gone.length) {
    const sec = makeSection("Nicht mehr im Rat");
    gone.forEach(pid => {
      const party = partyMap[pid];
      const h = hist[pid];
      const n = h.people.size;
      const row = document.createElement("a");
      row.className = "faction-head faction-gone";
      row.href = "#/fraktion/" + pid;
      row.innerHTML = `
        <span class="member-dot" style="background:${party.color}"></span>
        <span class="faction-name">${party.name}</span>
        <span class="faction-count">${formatMonthPeriod(h.from, h.to)} · ${n} ${n === 1 ? "Person" : "Personen"}</span>
        <svg class="icon faction-go"><use href="#i-chevron_right"/></svg>`;
      sec.appendChild(row);
    });
    wrap.appendChild(sec);
  }

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

export { renderGremien };
