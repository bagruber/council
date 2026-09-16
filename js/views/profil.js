// Personenprofil: Kopf mit Pinselstrich und Porträt, Mandate und Gremien,
// Kerndaten, Anträge, Abstimmungsstatistik und persönlicher Zeitstrahl.
import {
  members, votes, bodies, memberMap, partyMap, bodyMap, sessionMap,
  topicMap, voteMap, sessionsSorted, memberActiveAt, bodyIdForSession,
} from "../daten.js";
import { formatDate, formatPeriod, monthNames } from "../hilfen.js";
import { lastListHash, backLink } from "../routing.js";
import { renderPressLinks } from "./themen.js";
import { renderSimilarity } from "./naehe.js";

const gremienMain = document.getElementById("gremien-main");

const SHOW_PRONOUNS = true;

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

  // Das Ziel steht im Label, damit der Pfeil nicht blind ist: von der
  // Gremienliste, aus einem Dossier, aus einer Sitzung.
  const backHash = lastListHash || "/gremien";
  const backLabel = backHash === "/gremien" ? "Gremien"
                  : backHash.startsWith("/topic/") ? "Thema"
                  : backHash.startsWith("/session/") ? "Sitzung"
                  : "Übersicht";
  wrap.appendChild(backLink(backLabel, "#" + backHash));

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
    // Die Namen stammten noch aus der Material-Zeit und liefen ins Leere.
    // FLINTA bewusst nicht mit dem Venus-Zeichen: es umfasst auch inter,
    // nicht-binäre, trans und agender Personen.
    const badgeIcons = { queer: "queer", migrant: "migrant",
                         flinta: "flinta", disability: "disability" };
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

  const roleLabel = r => r === "mayor" ? "B\u00fcrgermeister" : "Stadtrat";
  const mandates = ((m.periods && m.periods.length) ? m.periods : [{ from: m.from, to: m.to }])
    .map(p => ({ icon: "account_balance", label: roleLabel(m.role), from: p.from, to: p.to }))
    .concat((m.roleHistory || []).map(rh =>
      ({ icon: "account_balance", label: roleLabel(rh.role), from: rh.from, to: rh.to })));
  mergeRoles(mandates).forEach(r => {
    rolesSection.appendChild(makeRoleRow(r.icon, r.label, r.spans));
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

  if (profile.titles) {
    // Referent:innen vertreten ein Sachgebiet nach außen — das Megafon
    // trifft das besser als ein Orden. Ämter laufen wie Gremiensitze durch
    // mergeRoles: zwei Wahlperioden nacheinander sind ein Zeitraum.
    const titel = profile.titles.map(t => ({
      icon: t.title.includes("rgermeister") ? "star"
          : /Referent|Beauftragt/i.test(t.title) ? "referent"
          : "badge",
      label: t.title, from: t.from, to: t.to,
    }));
    mergeRoles(titel).forEach(r => {
      rolesSection.appendChild(makeRoleRow(r.icon, r.label, r.spans));
    });
  }

  // Gremien. Die Ausschüsse liegen in `seatConfigs` je Wahlperiode — die
  // alte Fassung las nur ein `seats` auf oberster Ebene und fand deshalb
  // ausschließlich die Gremien ohne Perioden (Aufsichtsrat, Verbandsrat).
  committeeRoles(m).forEach(r => {
    rolesSection.appendChild(makeRoleRow(r.icon, r.label, r.spans));
  });

  wrap.appendChild(rolesSection);

  const facts = renderMemberFacts(m, profile);
  if (facts) wrap.appendChild(facts);

  const sim = renderSimilarity(m);
  if (sim) wrap.appendChild(sim);

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
  ({ uYes:0, uNo:0, uUnknown:0, sYes:0, sNo:0, sUnknown:0, absU:0, absS:0, total:0 });

function statKey(raw, unanimous) {
  const base = raw.replace("-inferred", "");
  // Befangen oder enthalten heißt: anwesend, aber keine Stimme abgegeben.
  // Sie landen in der Nicht-abgestimmt-Spalte — sonst würden sie als Nein
  // gezählt und das Stimmbild verfälschen.
  if (base === "absent" || base === "excluded" || base === "abstained"
      || base === "restricted") {
    return unanimous ? "absU" : "absS";
  }
  // Bei einem einstimmigen Beschluss hat niemand dagegen gestimmt. Wessen
  // Stimme dort nicht überliefert ist, hat mitgetragen oder gefehlt — die
  // offene Frage ist die Anwesenheit, nicht die Richtung. Bei geteilten
  // Beschlüssen ist dagegen die Stimme selbst unbekannt.
  if (base === "unknown") return unanimous ? "uUnknown" : "sUnknown";
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

// Bar-Reihenfolge — links Ablehnung (einstimmig außen, knapp innen), Mitte die
// unbekannte Stimme, rechts Zustimmung. Ganz außen rechts der graue Block: wer
// nicht mitgestimmt hat, und wessen Anwesenheit offen ist.
const VS_SEGMENTS = [
  { key: "uNo",      cls: "no-inf"   },
  { key: "sNo",      cls: "no"       },
  { key: "sUnknown", cls: "unknown"  },
  { key: "sYes",     cls: "yes"      },
  { key: "uYes",     cls: "yes-inf"  },
  { key: "uUnknown", cls: "unknown-u" },
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
            <span class="vs-item"><span class="vs-dot yes-inf"></span>Ja ${fmt(t.uYes)}</span>
            <span class="vs-item"><span class="vs-dot no-inf"></span>Nein ${fmt(t.uNo)}</span>
          </div>

          <div class="vs-legend-row vs-group">
            <span class="vs-legend-head">Nicht einstimmig</span>
            <span class="vs-legend-share">${fmt(t.sYes + t.sNo + t.sUnknown)}</span>
          </div>
          <div class="vs-legend-row vs-sub">
            <span class="vs-item"><span class="vs-dot yes"></span>Ja ${fmt(t.sYes)}</span>
            <span class="vs-item"><span class="vs-dot unknown"></span>Unbekannt ${fmt(t.sUnknown)}</span>
            <span class="vs-item"><span class="vs-dot no"></span>Nein ${fmt(t.sNo)}</span>
          </div>

          <div class="vs-legend-row vs-group">
            <span class="vs-legend-head">Nicht mitgestimmt</span>
            <span class="vs-legend-share">${fmt(t.absU + t.absS + t.uUnknown)}</span>
          </div>
          <div class="vs-legend-row vs-sub">
            <span class="vs-item"><span class="vs-dot unknown-u"></span>Anwesenheit unklar ${fmt(t.uUnknown)}</span>
            <span class="vs-item"><span class="vs-dot absent-u"></span>abwesend bei einstimmigen ${fmt(t.absU)}</span>
            <span class="vs-item"><span class="vs-dot absent"></span>abwesend bei nicht einstimmigen ${fmt(t.absS)}</span>
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
  // Eigene, kräftigere Zeichen für diese Reihe: die Glyphe steht weiß in einer
  // 26 px kleinen farbigen Fläche (16.09.2026).
  const ids = {
    email: "kontakt_email", website: "kontakt_website", instagram: "instagram",
    threads: "threads", linkedin: "linkedin", facebook: "facebook",
  };
  a.innerHTML = `<svg class="icon"><use href="#i-${ids[type] || "link"}"/></svg>`;
  return a;
}

// Alle Gremiensitze einer Person, über alle Wahlperioden hinweg.
// Ein Sitz kann direkt gesetzt sein (`member`), als Vertretung (`sub`) oder
// über `occupants`, wenn er im Lauf der Periode weitergereicht wurde.
function committeeRoles(m) {
  const out = [];
  bodies.forEach(b => {
    if (b.type === "plenum") return;
    const configs = (b.seatConfigs && b.seatConfigs.length) ? b.seatConfigs : [b];
    configs.forEach(cfg => {
      let role = null, from = cfg.from || m.from, to = cfg.to || m.to;

      if (cfg.chair === m.id)          role = "Vorsitz";
      else if (cfg.chairSub === m.id)  role = "Vorsitz, Vertretung";
      else if ((cfg.vicechairs || []).some(v => v.member === m.id))
        role = "Stellv. Vorsitz";
      else if ((cfg.vicechairs || []).some(v => v.sub === m.id))
        role = "Stellv. Vorsitz, Vertretung";
      else {
        for (const s of cfg.seats || []) {
          if (s.member === m.id) { role = ""; break; }
          if (s.sub === m.id)    { role = "Vertretung"; break; }
          const occ = (s.occupants || []).find(o => o.member === m.id);
          if (occ) {
            role = "";
            if (occ.from) from = occ.from;
            if (occ.to)   to = occ.to;
            break;
          }
        }
      }
      if (role === null) return;
      // Der Sitz kann nicht vor dem Mandat beginnen und nicht danach enden.
      const span = (m.periods && m.periods.length ? m.periods : [{ from: m.from, to: m.to }])
        .find(p => (!p.to || !from || p.to >= from) && (!to || !p.from || p.from <= to));
      if (span) {
        if (span.from && (!from || span.from > from)) from = span.from;
        if (span.to   && (!to   || span.to   < to))   to   = span.to;
      }
      const icon = role.startsWith("Vorsitz") || role.startsWith("Stellv.")
        ? "vorsitz"
        : b.type === "sonstige" ? "aufsichtsrat" : "ausschuss";
      out.push({ icon, label: b.name + (role ? ` (${role})` : ""), from, to });
    });

    (b.pastSeats || []).forEach(ps => {
      if (ps.member !== m.id) return;
      const suffix = ps.role ? ` (${ps.role})` : ps.sub === true ? " (Vertretung)" : "";
      out.push({ icon: "history", label: b.name + suffix,
                 from: ps.from || m.from, to: ps.to });
    });
  });
  return mergeRoles(out);
}

// Ein Ausschuss über zwei Wahlperioden hinweg ist eine Zugehörigkeit, keine
// zwei. Nur echte Unterbrechungen bleiben getrennte Zeiträume — bei Marschoun
// etwa liegen sechs Jahre zwischen den Mandaten.
function mergeRoles(rows) {
  const groups = new Map();
  rows.forEach(r => {
    const key = r.icon + "|" + r.label;
    if (!groups.has(key)) groups.set(key, { icon: r.icon, label: r.label, spans: [] });
    groups.get(key).spans.push({ from: vollTag(r.from, false), to: vollTag(r.to, true) });
  });
  return [...groups.values()].map(g => {
    g.spans.sort((a, b) => (a.from || "").localeCompare(b.from || ""));
    g.spans = g.spans.reduce((acc, s) => {
      const prev = acc[acc.length - 1];
      if (prev && (!prev.to || !s.from || dayAfter(prev.to) >= s.from)) {
        if (!s.to || (prev.to && s.to > prev.to)) prev.to = s.to;
      } else acc.push({ ...s });
      return acc;
    }, []);
    return g;
  });
}

// Manche Angaben stehen nur als Monat ("2020-05"). Für den Vergleich zählt
// dann der Monatsanfang, als Ende das Monatsende — sonst stoßen zwei
// lückenlose Zeiträume nicht aneinander und bleiben getrennte Zeilen.
function vollTag(iso, ende) {
  if (!iso || iso.length !== 7) return iso;
  if (!ende) return iso + "-01";
  const [j, m] = iso.split("-").map(Number);
  return new Date(Date.UTC(j, m, 0)).toISOString().slice(0, 10);
}

function dayAfter(iso) {
  const d = new Date(iso + "T12:00:00");
  d.setDate(d.getDate() + 1);
  return d.toISOString().slice(0, 10);
}

// Kerndaten zur Person. Bleibt weg, solange nichts hinterlegt ist — die
// Angaben kommen nach und nach dazu.
function renderMemberFacts(m, profile) {
  const rows = [];
  if (profile.birthYear)  rows.push(["Jahrgang", profile.birthYear]);
  if (profile.occupation) rows.push(["Beruf", profile.occupation]);
  if (profile.district)   rows.push(["Ortsteil", profile.district]);

  // „Im Rat seit“ stand schon in den Mandaten darüber und ist hier raus.
  const el = profile.elections || [];
  if (!rows.length && !el.length) return null;

  const sec = document.createElement("div");
  sec.className = "profile-section";
  sec.innerHTML = "<h3>Zur Person</h3>"
    + rows.map(([k, v]) => `<div class="fact-row"><span>${k}</span><span>${v}</span></div>`).join("");

  if (el.length) {
    // Der Listenplatz sagt, wohin die Partei jemanden gesetzt hat; der Rang
    // nach Auszählung, wohin die Wählerinnen und Wähler ihn gerückt haben.
    const rowsHtml = [...el].sort((a, b) => b.year - a.year).map(e => `
      <tr>
        <td>${e.year}</td>
        <td class="fig-value">${e.votes != null ? e.votes.toLocaleString("de-DE") : "–"}</td>
        <td class="fact-rank">${e.listRank != null && e.resultRank != null
          ? `Liste ${e.listRank} → Platz ${e.resultRank}`
          : e.listRank != null ? `Liste ${e.listRank}` : ""}</td>
      </tr>`).join("");
    const t = document.createElement("table");
    t.className = "figures-table fact-elections";
    t.innerHTML = `<thead><tr><th>Wahl</th><th class="fig-value">Stimmen</th><th></th></tr></thead>
                   <tbody>${rowsHtml}</tbody>`;
    sec.appendChild(t);
  }
  return sec;
}

function makeRoleRow(icon, text, spans) {
  const row = document.createElement("div");
  row.className = "role-row";
  row.innerHTML = `
    <svg class="icon"><use href="#i-${icon}"/></svg>
    <span>${text}</span>
    <span class="role-dates">${spans.map(s => formatPeriod(s.from, s.to)).join("<br>")}</span>`;
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
      // Einstimmig und ohne Eintrag: die Richtung ist klar, offen ist nur, ob
      // die Person überhaupt da war. Das Fragezeichen bleibt, der Chip wird
      // grau — dieselbe Lesart wie in der Statistik.
      const unklar = base === "unknown" && isUnanimous;
      const chipClass = unklar ? "unklar"
        : ({ yes: "ja", no: "nein", absent: "abwesend",
             excluded: "sonder", abstained: "sonder",
             restricted: "sonder" }[base] || "unknown")
          + (isUnanimous ? " inferred" : "");
      const chipLabel = Council.voteStatusLabel(status);

      const voteRow = document.createElement("div");
      voteRow.className = "mtl-vote";
      voteRow.innerHTML = `
        <span class="mtl-vote-chip ${chipClass}${Council.evidenceNote(vote, member.id) ? " weich" : ""}" title="${unklar ? "Anwesenheit nicht überliefert" : Council.statusProvenance(status, vote, member.id)}">${chipLabel}</span>
        <span class="mtl-vote-title">${vote.title}</span>`;

      const detail = document.createElement("div");
      detail.className = "mtl-vote-detail hidden";
      let detailHTML = `<p>${vote.text}</p>`;
      if (vote.type === "anonymous") {
        const abw = vote.results.absent === undefined
          ? "Abwesenheit nicht überliefert" : vote.results.absent + " Abwesend";
        detailHTML += `<p style="margin-top:4px">${vote.results.yes} Ja, ${vote.results.no} Nein, ${abw}</p>`;
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

export { renderMemberProfile };
