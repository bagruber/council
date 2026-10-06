// Datenbestand und Nachschlagewerke. Lädt die sechs JSON-Dateien und baut
// daraus die Maps, die alle Views teilen. Die Exporte sind live bindings:
// sie stehen erst nach ladeDaten() — der Einstieg (app.js) wartet darauf,
// bevor er rendert.

let topics, sessions, votes, tags, membersData, pressData;
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
const votesBySession = {};

async function ladeDaten() {
  [topics, sessions, votes, tags, membersData, pressData] = await Promise.all([
    fetch("data/topics.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
    fetch("data/sessions.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
    fetch("data/votes.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
    fetch("data/tags.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
    fetch("data/members.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
    fetch("data/press.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
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

  votes.forEach(v => { (votesBySession[v.sessionId] || (votesBySession[v.sessionId] = [])).push(v); });
}

// Eine Sitzungsart, zwei Namen: im Gremienteil heisst das Gremium "Plenum",
// weil es dort neben den Ausschuessen steht und die Unterscheidung der Punkt
// ist. In Statistik, Register und Kalender heisst dieselbe Sitzung "Stadtrat",
// weil sie dort neben anderen Sitzungen steht. Beides ist richtig, nur stand
// die Zuordnung bisher dreimal im Code — hier, in bodyIdForSession und als
// CHART_BODIES in statistik.js.
const SITZUNGSARTEN = [
  { type: "stadtrat", body: "plenum", label: "Stadtrat", pdf: "SR",
    color: "var(--body-stadtrat)" },
  { type: "bpu", body: "bpu", label: "BPU", pdf: "BPU",
    color: "var(--body-bpu)" },
  { type: "hvfa", body: "hvfa", label: "HVFA", pdf: "HVF",
    color: "var(--body-hvfa)" },
];
const sitzungsart = type => SITZUNGSARTEN.find(a => a.type === type) || null;

function protocolUrl(s) {
  return "data/niederschriften/" + sitzungsart(s.type).pdf
       + "_" + s.date.replace(/-/g, "") + ".pdf";
}

// Was von einer Sitzung vorliegt. Steht als `niederschrift` am Datensatz:
//   "vollständig" — Niederschrift mit Anwesenheitsliste
//   "auszug"      — Beschlussauszug der Stadt, ohne Anwesenheitsliste
//   "keine"       — nichts veröffentlicht
// Der Beschlussauszug ist eine eigene Stufe und nicht bloß eine andere
// Quellenangabe: die Beschlüsse stehen dort, die Anwesenheit nicht.
const NIEDERSCHRIFT = [
  { stufe: "vollständig", label: "Niederschrift",
    hinweis: "Niederschrift mit Anwesenheitsliste" },
  { stufe: "auszug", label: "nur Beschlussauszug",
    hinweis: "Beschlussauszug der Stadt, ohne Anwesenheitsliste" },
  { stufe: "keine", label: "nichts veröffentlicht",
    hinweis: "Weder Niederschrift noch Auszug veröffentlicht" },
];

function isWebauszug(s) {
  return s.niederschrift === "auszug";
}

// Ob eine Sitzung war, sagt ihr Datum. Ein gepflegtes Statusfeld ginge am Tag
// der Sitzung schief und stünde dann im Widerspruch zur Liste darunter.
function istGehalten(s) {
  return s.date <= nowStr;
}

// Probe Formsprache: das Gremium einer Sitzung oder eines Termins, für
// Kategoriezeile und Flächenfarbe.
function gremium(s) {
  const art = sitzungsart(s.type || "stadtrat");
  const body = art && bodyMap[art.body];
  return {
    art: art ? art.type : "stadtrat",
    name: body ? body.name : (art ? art.label : ""),
    icon: body && body.icon ? body.icon : "account_balance",
  };
}

// Probe Formsprache: die nächste angekündigte Sitzung ab heute. Bestimmt beim
// Rendern, nie fest eingetragen; ohne Termin null.
function naechsteSitzung() {
  return sessions
    .filter(s => s.date >= nowStr)
    .sort((a, b) => (a.date + (a.start || "")).localeCompare(b.date + (b.start || "")))[0] || null;
}

// Das Sitzungsregister: jede Sitzung, die stattgefunden hat, neueste zuerst —
// unabhängig davon, ob etwas von ihr veröffentlicht ist. Seit Oktober 2026 ist
// das schlicht sessions.json; davor standen die Sitzungen in drei Dateien und
// wurden an drei Stellen verschieden gezählt.
function sessionRegister() {
  return sessionsSorted.filter(istGehalten);
}

// Die eine Zählstelle. Startseite, Statistik und Datenlage lesen nur von hier;
// die Seiten nennen die Definition, die hier steht.
function bestand() {
  const reg = sessionRegister();
  const zaehle = stufe => reg.filter(s => s.niederschrift === stufe).length;
  const voten = reg.reduce((n, s) => n + votenVon(s).length, 0);
  return {
    sitzungen: reg.length,
    vollstaendig: zaehle("vollständig"),
    auszug: zaehle("auszug"),
    keine: zaehle("keine"),
    mitDauer: reg.filter(dauerMin).length,
    minuten: reg.reduce((n, s) => n + (dauerMin(s) || 0), 0),
    abstimmungen: voten,
    presse: pressData.length,
    seit: reg.length ? reg[reg.length - 1].date : null,
  };
}

const votenVon = s => votesBySession[s.id] || [];

// Wie belastbar ist das Stimmverhalten dieser Sitzung? Zählt die
// Herkunftsstufen aus vote.source.tier durch; ohne Stufe ist nur das
// Gesamtergebnis bekannt. Gezählt wird je Beschluss nach seiner
// Hauptquelle — einzelne Stimmen können daneben aus `voterSource` stammen.
function tierCounts(votes) {
  const c = { explicit: 0, implicit: 0, tracked: 0, press: 0,
              selbstauskunft: 0, sum: 0 };
  votes.forEach(v => {
    const t = (v.source || {}).tier;
    if (t === "protocol-explicit")      c.explicit++;
    else if (t === "protocol-implicit") c.implicit++;
    else if (t === "tracked")           c.tracked++;
    else if (t === "press")             c.press++;
    else if (t === "selbstauskunft")    c.selbstauskunft++;
    else                                c.sum++;
  });
  return c;
}

function timeToMin(t) {
  const p = t.split(":");
  return p[0] * 60 + +p[1];
}

// Dauer in Minuten, sofern Beginn und Ende überliefert sind.
function dauerMin(s) {
  return s.start && s.end ? timeToMin(s.end) - timeToMin(s.start) : null;
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
  const art = s && sitzungsart(s.type);
  return art ? art.body : null;
}

export {
  ladeDaten,
  topics, sessions, votes, tags, membersData, pressData,
  members, parties, bodies, seatOrder, mediaSources, mediaMap, pressMap,
  topicMap, sessionMap, voteMap, tagMap, memberMap, partyMap, bodyMap,
  sessionsSorted, votesBySession,
  SITZUNGSARTEN, sitzungsart, NIEDERSCHRIFT,
  protocolUrl, isWebauszug, istGehalten, naechsteSitzung, gremium,
  sessionRegister, bestand, votenVon, tierCounts, dauerMin,
  nowStr, memberActiveAt, isActive, bodyIdForSession,
};
