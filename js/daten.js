// Datenbestand und Nachschlagewerke. Lädt die sieben JSON-Dateien und baut
// daraus die Maps, die alle Views teilen. Die Exporte sind live bindings:
// sie stehen erst nach ladeDaten() — der Einstieg (app.js) wartet darauf,
// bevor er rendert.

let topics, sessions, votes, tags, membersData, pressData, sessionLengths;
let members, parties, bodies, seatOrder, mediaSources;
const mediaMap = {};
const pressMap = {};
const topicMap = {};
const sessionMap = {};
const voteMap = {};
const tagMap = {};
const memberMap = {};
const partyMap = {};
const bodyMap = {};
let sessionsSorted;
const lengthMap = {};
const sessionByDateBody = {};
const votesBySession = {};

async function ladeDaten() {
  [topics, sessions, votes, tags, membersData, pressData, sessionLengths] = await Promise.all([
    fetch("data/topics.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
    fetch("data/sessions.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
    fetch("data/votes.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
    fetch("data/tags.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
    fetch("data/members.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
    fetch("data/press.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
    fetch("data/sessionlengths.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
  ]);

  members = membersData.members;
  members.forEach(m => { if (!m.name) m.name = m.firstName + " " + m.lastName; });
  parties = membersData.parties;
  bodies = membersData.bodies || [];
  seatOrder = membersData.seatOrder || parties.map(p => p.id);
  mediaSources = membersData.media || [];
  mediaSources.forEach(m => { mediaMap[m.id] = m; });
  pressData.forEach(p => { pressMap[p.id] = p; });

  topics.forEach(t => { topicMap[t.id] = t; });
  sessions.forEach(s => { sessionMap[s.id] = s; });
  votes.forEach(v => { voteMap[v.id] = v; });
  tags.forEach(t => { tagMap[t.id] = t; });
  members.forEach(m => { memberMap[m.id] = m; });
  parties.forEach(p => { partyMap[p.id] = p; });
  bodies.forEach(b => { bodyMap[b.id] = b; });

  sessionsSorted = [...sessions].sort((a, b) => b.date.localeCompare(a.date));

  // Sitzungsdauern aus den Niederschriften, Zuordnung über Datum + Gremium.
  // Nicht jede Sitzung ist in sessions.json erfasst — die Statistik nutzt
  // alle Einträge, die Sitzungsseite nur den passenden.
  sessionLengths.forEach(l => { lengthMap[l.date + "|" + l.body] = l; });
  sessions.forEach(s => { sessionByDateBody[s.date + "|" + (s.type || "stadtrat")] = s; });

  votes.forEach(v => { (votesBySession[v.sessionId] || (votesBySession[v.sessionId] = [])).push(v); });
}

const PDF_PREFIX = { stadtrat: "SR", bpu: "BPU", hvfa: "HVF" };
function protocolUrl(s) {
  return "data/niederschriften/" + PDF_PREFIX[s.type || "stadtrat"]
       + "_" + s.date.replace(/-/g, "") + ".pdf";
}

// Manche Sitzungen erscheinen nie als Niederschrift, sondern nur als
// Beschlussauszug auf der Website der Stadt. Die Beschlüsse stehen dort, die
// Anwesenheitsliste nicht — deshalb eine eigene Stufe, nicht bloß eine
// andere Quellenangabe.
function isWebauszug(s) {
  return !!(s.source && s.source.kind === "webauszug");
}

// Ein Eintrag je Sitzung, die stattgefunden hat — unabhängig davon, ob eine
// Niederschrift vorliegt. Die Dauern reichen weiter als die erfassten
// Sitzungen, die erfassten Sitzungen weiter zurück als die Dauern.
function sessionRegister() {
  const rows = new Map();
  const put = (date, body) => {
    const key = date + "|" + body;
    if (!rows.has(key)) rows.set(key, { date, body, votes: [] });
    return rows.get(key);
  };
  sessionLengths.forEach(l => {
    const r = put(l.date, l.body);
    r.start = l.start; r.end = l.end; r.min = lengthMin(l);
  });
  sessions.forEach(s => {
    const r = put(s.date, s.type || "stadtrat");
    r.session = s;
    r.votes = votesBySession[s.id] || [];
  });
  return [...rows.values()].sort((a, b) => b.date.localeCompare(a.date));
}

// Wie belastbar ist das Stimmverhalten dieser Sitzung? Zählt die vier
// Herkunftsstufen aus vote.source.tier durch; ohne Stufe ist nur das
// Gesamtergebnis bekannt.
function tierCounts(votes) {
  const c = { explicit: 0, implicit: 0, tracked: 0, press: 0, sum: 0 };
  votes.forEach(v => {
    const t = (v.source || {}).tier;
    if (t === "protocol-explicit")      c.explicit++;
    else if (t === "protocol-implicit") c.implicit++;
    else if (t === "tracked")           c.tracked++;
    else if (t === "press")             c.press++;
    else                                c.sum++;
  });
  return c;
}

function timeToMin(t) {
  const p = t.split(":");
  return p[0] * 60 + +p[1];
}

function lengthMin(l) {
  return l.end ? timeToMin(l.end) - timeToMin(l.start) : null;
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

function bodyIdForSession(s) {
  if (!s) return null;
  if (s.type === "stadtrat") return "plenum";
  if (s.type === "bpu")      return "bpu";
  if (s.type === "hvfa")     return "hvfa";
  return null;
}

export {
  ladeDaten,
  topics, sessions, votes, tags, membersData, pressData, sessionLengths,
  members, parties, bodies, seatOrder, mediaSources, mediaMap, pressMap,
  topicMap, sessionMap, voteMap, tagMap, memberMap, partyMap, bodyMap,
  sessionsSorted, lengthMap, sessionByDateBody, votesBySession,
  protocolUrl, isWebauszug, sessionRegister, tierCounts, lengthMin,
  nowStr, memberActiveAt, isActive, bodyIdForSession,
};
