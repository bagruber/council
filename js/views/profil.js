// Personenprofil: Kopf mit Pinselstrich und Porträt, Mandate und Gremien,
// Kerndaten, Anträge, Abstimmungsstatistik und persönlicher Zeitstrahl.
import {
  members, votes, bodies, memberMap, partyMap, bodyMap, sessionMap,
  topicMap, voteMap, sessionsSorted, memberActiveAt, bodyIdForSession,
} from "../daten.js";
import { formatDate, formatPeriod, monthNames } from "../hilfen.js";
import { lastListHash } from "../routing.js";
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
    profile.titles.forEach(t => {
      // Referent:innen vertreten ein Sachgebiet nach außen — das Megafon
      // trifft das besser als ein Orden.
      const icon = t.title.includes("rgermeister") ? "star"
                 : /Referent|Beauftragt/i.test(t.title) ? "referent"
                 : "badge";
      rolesSection.appendChild(makeRoleRow(icon, t.title, [{ from: t.from, to: t.to }]));
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
    groups.get(key).spans.push({ from: r.from, to: r.to });
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

  // Ratsjahre über alle Mandate, Wechseltage nicht doppelt gezählt
  const spans = m.periods && m.periods.length ? m.periods : [{ from: m.from, to: m.to }];
  const days = spans.reduce((n, s) => n + (s.from
    ? (Date.parse(s.to || new Date().toISOString().slice(0, 10)) - Date.parse(s.from)) / 864e5
    : 0), 0);
  if (days > 0) rows.push(["Im Rat seit", `${spans[0].from.slice(0, 4)} · ${Math.round(days / 365)} Jahre`]);

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
      const chipClass = ({ yes: "ja", no: "nein", absent: "abwesend",
                          excluded: "sonder", abstained: "sonder",
                          restricted: "sonder" }[base] || "unknown")
                      + (isUnanimous ? " inferred" : "");
      const chipLabel = Council.voteStatusLabel(status);

      const voteRow = document.createElement("div");
      voteRow.className = "mtl-vote";
      voteRow.innerHTML = `
        <span class="mtl-vote-chip ${chipClass}${Council.evidenceNote(vote, member.id) ? " weich" : ""}" title="${Council.statusProvenance(status, vote, member.id)}">${chipLabel}</span>
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

export { renderMemberProfile };
