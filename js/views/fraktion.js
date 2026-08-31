// Fraktionsseite: Besetzung über die Zeit, Wechsel mit Richtung und die
// Geschlossenheit bei geteilten Beschlüssen.
import { members, votes, memberMap, partyMap } from "../daten.js";
import { formatMonthPeriod } from "../hilfen.js";
import { stances, partyAtDate } from "./naehe.js";

const gremienMain = document.getElementById("gremien-main");

// -- Fraktionszugehörigkeit --

// Ein Mandat kann die Fraktion wechseln; `partyHistory` hält das fest. Ohne
// Historie gilt die aktuelle Partei für das ganze Mandat.
function partySpans(m) {
  const mandate = m.periods && m.periods.length ? m.periods : [{ from: m.from, to: m.to }];
  const first = mandate[0].from, last = mandate[mandate.length - 1].to;
  if (!m.partyHistory || !m.partyHistory.length) {
    return [{ party: m.party, from: first, to: last }];
  }
  return m.partyHistory.map(p => ({
    party: p.party,
    from: p.from && p.from > first ? p.from : first,
    to: p.to && (!last || p.to < last) ? p.to : last,
  }));
}

function factionRoster(pid) {
  const today = new Date().toISOString().slice(0, 10);
  const out = [];
  members.forEach(m => {
    const spans = partySpans(m);
    spans.forEach((s, i) => {
      if (s.party !== pid) return;
      const current = (!s.to || s.to >= today) && Council.memberActiveAt(m, today);
      // Nachbarn in der Parteibiografie — sie geben dem Wechsel die Richtung
      out.push({ member: m, span: s, current,
                 from: i > 0 ? spans[i - 1].party : null,
                 to: i < spans.length - 1 ? spans[i + 1].party : null });
    });
  });
  return out;
}

// Alle Parteien, die im Rat vertreten waren, mit Zeitraum und Kopfzahl
function factionHistory() {
  const out = {};
  members.forEach(m => {
    partySpans(m).forEach(s => {
      const e = out[s.party] || (out[s.party] = { people: new Set(), from: s.from, to: s.to });
      e.people.add(m.id);
      if (s.from && s.from < e.from) e.from = s.from;
      if (e.to && (!s.to || s.to > e.to)) e.to = s.to;
    });
  });
  return out;
}

function renderFraktion(pid) {
  const party = partyMap[pid];
  if (!party) { gremienMain.innerHTML = "<p style='padding:40px 24px'>Fraktion nicht gefunden.</p>"; return; }
  gremienMain.innerHTML = "";

  const wrap = document.createElement("div");
  wrap.className = "page-wrap";

  const back = document.createElement("a");
  back.className = "back-link";
  back.href = "#/gremien";
  back.innerHTML = '<svg class="icon"><use href="#i-arrow_back"/></svg> Gremien';
  wrap.appendChild(back);

  const roster = factionRoster(pid);
  const now = roster.filter(r => r.current);
  const past = roster.filter(r => !r.current)
    .sort((a, b) => (b.span.to || "").localeCompare(a.span.to || ""));

  const head = document.createElement("div");
  head.className = "faction-header";
  head.innerHTML = `
    <span class="faction-badge" style="background:${party.color}"></span>
    <div>
      <h1>${party.name}</h1>
      <div class="faction-sub">${now.length} ${now.length === 1 ? "Sitz" : "Sitze"} im Stadtrat
        · ${roster.length} Personen seit ${roster.reduce((a, r) => r.span.from < a ? r.span.from : a, "9999").slice(0, 4)}</div>
    </div>`;
  wrap.appendChild(head);

  const rows = (list, title) => {
    if (!list.length) return;
    const h = document.createElement("p");
    h.className = "section-heading";
    h.textContent = title;
    wrap.appendChild(h);
    list.sort((a, b) => a.member.name.localeCompare(b.member.name));
    list.forEach(r => {
      const row = document.createElement("a");
      row.className = "member-row";
      row.href = "#/member/" + r.member.id;
      // Wechsel mit Richtung: woher jemand kam, wohin er ging
      const chip = (other, dir) => {
        const p = partyMap[other];
        const label = p ? p.name : other;
        return `<span class="faction-move ${dir}" style="--from:${p ? p.color : "#999"}"
          title="${dir === "in" ? "vorher" : "danach"} ${label}"
          >${dir === "in" ? label + " →" : "→ " + label}</span>`;
      };
      const move = (r.from ? chip(r.from, "in") : "") + (r.to ? chip(r.to, "out") : "");
      // Der Bürgermeister sitzt kraft Amtes im Rat, nicht über die Liste
      const office = r.member.role === "mayor"
        ? `<span class="faction-office">Bürgermeister</span>` : "";
      row.innerHTML = `
        <span class="member-dot" style="background:${party.color}"></span>
        <span class="member-row-name">${r.member.name}</span>
        ${office}${move}
        <span class="member-row-meta">${formatMonthPeriod(r.span.from, r.span.to)}</span>`;
      wrap.appendChild(row);
    });
  };
  const coh = factionCohesion(pid);
  if (coh) wrap.appendChild(coh);

  rows(now, "Aktuell");
  rows(past, "Ehemals");

  gremienMain.appendChild(wrap);
}

// Wie oft zieht die Fraktion an einem Strang, wenn der Rat sich teilt — und
// wer schert am häufigsten aus. Gezählt werden nur geteilte Beschlüsse, bei
// denen von mindestens zwei Fraktionsmitgliedern die Stimme bekannt ist.
function factionCohesion(pid) {
  if (pid === "parteilos") return null;      // keine Fraktion, keine Geschlossenheit
  let total = 0, united = 0;
  const dev = {};
  votes.forEach(v => {
    if (Council.isUnanimous(v)) return;
    const st = stances(v);
    const group = Object.entries(st).filter(([id]) =>
      memberMap[id] && partyAtDate(memberMap[id], v.date) === pid);
    if (group.length < 2) return;
    total++;
    const counts = {};
    group.forEach(([, s]) => counts[s] = (counts[s] || 0) + 1);
    if (Object.keys(counts).length === 1) united++;
    // Wer abweicht, weicht von einer Mehrheit ab. Bei zwei Stimmen gibt es
    // keine — dort steht Aussage gegen Aussage.
    if (group.length < 3) return;
    const majority = Object.keys(counts).sort((a, b) => counts[b] - counts[a])[0];
    group.forEach(([id, s]) => {
      const d = dev[id] || (dev[id] = { n: 0, off: 0 });
      d.n++;
      if (s !== majority) d.off++;
    });
  });
  if (total < 5) return null;

  const ranked = Object.entries(dev)
    .filter(([, d]) => d.n >= 5)
    .map(([id, d]) => ({ id, n: d.n, off: d.off, share: d.off / d.n }))
    .sort((a, b) => b.share - a.share)
    .filter(r => r.off > 0)
    .slice(0, 3);

  const box = document.createElement("div");
  box.className = "cohesion";
  box.innerHTML = `
    <div class="cohesion-value">${Math.round(united / total * 100)} %</div>
    <div class="cohesion-label">geschlossen bei geteilten Beschlüssen
      <span>${united} von ${total} Abstimmungen, bei denen der Rat sich nicht einig war
      und mindestens zwei Stimmen aus der Fraktion bekannt sind</span></div>
    ${ranked.length ? `<div class="cohesion-dev">${ranked.map(r => {
      const m = memberMap[r.id];
      const office = m && m.role === "mayor"
        ? ` <span class="faction-office">Bürgermeister</span>` : "";
      return `<a href="#/member/${r.id}"><span>${m ? m.name : r.id}</span>${office}
                <b>${Math.round(r.share * 100)} %</b>
                <small>${r.off} von ${r.n}</small></a>`;
    }).join("")}<p>weicht am häufigsten von der Mehrheit der eigenen Fraktion ab —
      gezählt bei Beschlüssen mit mindestens drei bekannten Stimmen aus der Fraktion</p></div>` : ""}`;
  return box;
}

export { factionHistory, renderFraktion };
