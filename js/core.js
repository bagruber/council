// Council Core — Shared period & vote-status helpers.
//
// Single source of truth for "was this person active / a regular committee
// seat-holder / how did they vote" — consumed by app.js (profile, statistics)
// and parliament.js (chamber visualisation).
//
// See docs/CORE.md for a walkthrough.

const Council = (() => {

  // ── Period helpers ────────────────────────────────────────────────────────

  // YYYY-MM end-of-month sentinel ("2024-10" → "2024-10-99" for inclusive compare).
  function endOfPeriod(p) {
    return p && p.length === 7 ? p + "-99" : p;
  }

  // True if `date` falls inside { from?, to? } (inclusive on both ends; absent
  // bound = open-ended).
  function withinPeriod(span, date) {
    if (span.from && date < span.from) return false;
    if (span.to   && date > endOfPeriod(span.to)) return false;
    return true;
  }

  // Mandat, Fraktion und Rolle stehen als eine geordnete Liste von Abschnitten
  // am Mitglied: `mandates: [{from, to, party, role}]`. Eine Lücke zwischen
  // zwei Abschnitten ist eine Unterbrechung des Mandats (Marschoun 2014–2020
  // und seit 2026), kein Abstand heißt Fraktions- oder Rollenwechsel.
  // Überlappen zwei Abschnitte an ihrer Grenze, gilt der spätere — ein
  // Wechsel am 6. Oktober heißt, dass der 6. Oktober schon der neuen Seite
  // gehört.
  function memberActiveAt(member, date) {
    return (member.mandates || []).some(p => withinPeriod(p, date));
  }

  // Fraktion bzw. Rolle an einem Tag. Ohne Mandat an dem Tag null.
  function mandateAt(member, date) {
    let treffer = null;
    (member.mandates || []).forEach(p => { if (withinPeriod(p, date)) treffer = p; });
    return treffer;
  }

  function partyAt(member, date) {
    const m = mandateAt(member, date);
    return m ? m.party : null;
  }

  // Die eigentlichen Mandatszeiten: aufeinanderfolgende Abschnitte sind ein
  // Mandat, eine Lücke dazwischen ist eine Unterbrechung. Fraktions- und
  // Rollenwechsel schneiden die Abschnitte, nicht das Mandat.
  function mandateSpans(member) {
    const out = [];
    (member.mandates || []).forEach(p => {
      const letzte = out[out.length - 1];
      if (letzte && letzte.to === p.from) letzte.to = p.to;
      else out.push({ from: p.from, to: p.to });
    });
    return out;
  }

  // Die Abschnitte zu Zeitspannen je Fraktion zusammengefasst, für die
  // Fraktionszeile im Profil. Aufeinanderfolgende Abschnitte derselben
  // Fraktion sind eine Spanne, auch wenn die Rolle dazwischen wechselt.
  function partySpans(member) {
    const out = [];
    (member.mandates || []).forEach(p => {
      const letzte = out[out.length - 1];
      if (letzte && letzte.party === p.party && letzte.to === p.from) letzte.to = p.to;
      else out.push({ party: p.party, from: p.from, to: p.to });
    });
    return out;
  }

  // ── Body composition ──────────────────────────────────────────────────────

  // Returns the seatConfig active on `date`. For bodies without seatConfigs
  // (e.g. plenum), the body itself is returned as the "config".
  function bodyConfigAt(body, date) {
    const configs = body && body.seatConfigs;
    // Gremien ohne Perioden (Aufsichtsrat, Verbandsrat) tragen ihre Besetzung
    // direkt am Objekt.
    if (!configs || !configs.length) return body || {};
    // Gremien mit Perioden: ausserhalb aller Perioden gibt es keine bekannte
    // Besetzung. Der frühere Rückfall auf die oberste `seats`-Ebene hat für
    // alte Sitzungen die heutige Besetzung ausgewiesen.
    return configs.find(c => withinPeriod(c, date)) || {};
  }

  // Whether `member` holds a regular seat (chair, vice-chair, or seat) in
  // `body` on `date`. Returns true for the regular occupant — NOT for a
  // substitute who happens to step in for a specific vote.
  function isRegularOf(member, body, date) {
    const cfg = bodyConfigAt(body, date);
    if (cfg.chair === member.id) return true;
    if ((cfg.vicechairs || []).some(v => v.member === member.id)) return true;
    return (cfg.seats || []).some(s => {
      if (s.member === member.id) return true;
      if (s.occupants) {
        return s.occupants.some(o => o.member === member.id && withinPeriod(o, date));
      }
      return false;
    });
  }

  // ── Vote status — the heart of the module ─────────────────────────────────
  //
  // Given a member, a vote, and the session it belongs to, returns one of:
  //   'yes' | 'no' | 'absent'
  //   'yes-inferred' | 'no-inferred'   — anonymous vote, status derivable from
  //                                       unanimity-of-present
  //   'excluded'                       — anwesend, aber wegen persönlicher
  //                                       Beteiligung (Art. 49 GO) ausgeschlossen
  //   'abstained'                      — anwesend, enthalten
  //   'restricted'                     — anwesend, aber nicht stimmberechtigt
  //                                      (neu gewählt, Niederschrift nicht miterlebt)
  //   'unknown'                        — anonymous vote, status not derivable
  //   null                             — member was not on council that day
  //
  // 'excluded' und 'abstained' sind Randfälle (zusammen unter 8 % der Stimmen).
  // Sie werden erfasst, weil "befangen" das Gegenteil von "abwesend" ist —
  // aber sie bleiben in der Darstellung hinter Ja/Nein/Unbekannt zurück.
  //
  // Sources, in priority order:
  //   1. Member not active at vote.date          → null
  //   2. Per-vote exclusion (`vote.excluded`)    → 'excluded' | 'abstained'
  //   3. Session-level absence                   → 'absent'
  //   4. Named vote → arrays of ids              → 'yes' | 'no' | 'absent'
  //   5. Explicit `vote.voters[id].vote`         → that status
  //   6. Per-vote temporary absence (rare)       → 'absent'
  //   7. Unanimous anonymous (yes>0, no===0)     → 'yes-inferred'
  //                          (no>0,  yes===0)    → 'no-inferred'
  //   8. Anonymous split, no per-voter info      → 'unknown'

  function voteStatus(memberId, vote, session, member) {
    if (member && !memberActiveAt(member, vote.date)) return null;

    // Vor der Sitzungsabwesenheit prüfen: wer befangen ist, war ja da.
    const ex = (vote.excluded || []).find(e => e.member === memberId);
    if (ex) {
      if (ex.reason === "beteiligung")           return "excluded";
      if (ex.reason === "enthaltung")            return "abstained";
      if (ex.reason === "nicht_stimmberechtigt") return "restricted";
      // Wechseltag: den Sitz hielt zu dieser Abstimmung die andere Person.
      if (ex.reason === "kein_mandat")            return "restricted";
      return "absent";                  // kurz_abwesend
    }

    if (session && session.absent && session.absent.includes(memberId)) return "absent";

    if (vote.type === "named") {
      if (vote.results.yes.includes(memberId))    return "yes";
      if (vote.results.no.includes(memberId))     return "no";
      if (vote.results.absent.includes(memberId)) return "absent";
      return null;
    }

    // Ein voters-Eintrag kann auch nur die Herkunft tragen, ohne eigene
    // Stimme — dann gilt weiter, was die Listen oben hergeben.
    const eigen = (vote.voters || {})[memberId];
    if (eigen && eigen.vote) return eigen.vote;    // 'yes'|'no'|'absent'

    if (vote.results.absent_ids && vote.results.absent_ids.includes(memberId)) {
      return "absent";
    }

    // Einstimmig heißt nur dann "alle Anwesenden dafür", wenn auch alle
    // mitgestimmt haben. Wo die Niederschrift weniger Stimmen ausweist als
    // Stimmberechtigte da waren, setzt der Import `inferable: false` —
    // dann bleibt es beim ehrlichen Fragezeichen.
    const { yes, no } = vote.results;

    // `teilweise`: es haben weniger mitgestimmt als anwesend waren, aber die
    // Niederschrift nennt, wer später kam oder früher ging. Offen bleibt dann
    // nur deren Stimme — für alle anderen im Saal gilt das einstimmige
    // Ergebnis, sonst stünde bei zwanzig Personen ein Fragezeichen, weil eine
    // fehlte.
    if (vote.inferable === "teilweise"
        && ((session && session.partial) || []).some(p => p.member === memberId)) {
      return "unknown";
    }
    if (vote.inferable !== false) {
      if (yes > 0 && no === 0) return "yes-inferred";
      if (no  > 0 && yes === 0) return "no-inferred";
    }
    return "unknown";
  }

  // True if the vote was unanimous — named: leeres Ja- oder Nein-Array,
  // anonymous: null auf einer Seite.
  function isUnanimous(vote) {
    const r = vote.results;
    return vote.type === "named"
      ? (r.no.length === 0 || r.yes.length === 0)
      : (r.no === 0 || r.yes === 0);
  }

  // Compact German label for UI chips ("Ja", "Nein", "–", "?", or empty for unknown).
  // Pass `withMarker: true` to append "*" to inferred values.
  function voteStatusLabel(status, withMarker = false) {
    if (!status) return "";
    const base = { yes: "Ja", no: "Nein", absent: "–",
                   "yes-inferred": "Ja", "no-inferred": "Nein",
                   excluded: "bef.", abstained: "enth.", restricted: "n.b.",
                   unknown: "?" }[status] || "?";
    return withMarker && status.endsWith("-inferred") ? base + "*" : base;
  }

  // Ausgeschriebene Fassung für Tooltips und Legende.
  function voteStatusTitle(status) {
    return { yes: "Ja", no: "Nein", absent: "Abwesend",
             "yes-inferred": "Ja - aus öff. Niederschrift abgeleitet",
             "no-inferred": "Nein - aus öff. Niederschrift abgeleitet",
             excluded: "Wegen persönlicher Beteiligung ausgeschlossen (Art. 49 GO)",
             abstained: "Enthalten",
             restricted: "Bei dieser Abstimmung nicht stimmberechtigt",
             unknown: "Nicht überliefert" }[status] || "Nicht überliefert";
  }

  // Herkunft der Einzelstimmen, absteigend nach Belastbarkeit.
  const TIER_RANK = ["protocol-explicit", "protocol-implicit", "tracked",
                     "press", "selbstauskunft", "result-only"];
  const TIER_LABEL = {
    "protocol-explicit": "Namentlich in der Niederschrift",
    "protocol-implicit": "Aus der öff. Niederschrift abgeleitet",
    tracked: "In der Sitzung mitgeschrieben",
    press: "Aus Presseberichten",
    selbstauskunft: "Aus eigenen Notizen rekonstruiert",
    // Die unterste Stufe hat nichts zu benennen: die Niederschrift nennt Ja
    // und Nein und sonst nichts. Ohne Beschriftung bleibt die Fußzeile leer,
    // und views/voten.js setzt dort seinen eigenen Satz.
    "result-only": null,
  };

  // Alle Belege für die Stimme dieser Person, stärkster zuerst. Mehrere sind
  // möglich: wer in der Mitschrift steht und später selbst antwortet, ist zwei
  // Mal belegt. Für die Anzeige zählt der stärkste, die übrigen erhöhen nur
  // das Gewicht. Ohne eigenen Eintrag gilt die Stufe des Beschlusses.
  function voterTiers(vote, memberId) {
    const eigen = memberId && ((vote.voters || {})[memberId] || {}).tiers;
    const liste = eigen ? [].concat(eigen)
                : (vote.source && vote.source.tier ? [vote.source.tier] : []);
    return liste.slice().sort((a, b) => TIER_RANK.indexOf(a) - TIER_RANK.indexOf(b));
  }

  // Ohne `memberId` die Herkunft des Beschlusses, mit ihr die stärkste dieser
  // einen Stimme.
  function sourceLabel(vote, memberId) {
    const tiers = voterTiers(vote, memberId);
    return tiers.length ? (TIER_LABEL[tiers[0]] || null) : null;
  }

  // Woher die Stimme dieser einen Person kommt. Die Stufe am Votum sagt, wie
  // das Ergebnis insgesamt belegt ist; hier geht es um den Einzelfall — eine
  // Zeitung, die "gegen die Stimmen von X" schreibt, belegt etwas anderes als
  // eine, die X in der Debatte zitiert. Ohne Eintrag gilt die Stufe des Votums.
  function evidenceNote(vote, memberId) {
    const eigen = vote && (vote.voters || {})[memberId];
    if (!eigen || eigen.evidence !== "soft") return null;
    return "aus einer Wortmeldung erschlossen, nicht als Stimme berichtet";
  }

  // Statuszeile plus Herkunft, für Titel-Attribute in den Übersichten.
  // Wo nichts überliefert ist, sagt die Herkunft nichts — dann bleibt sie weg,
  // sonst stünde "Nicht überliefert - Aus Presseberichten" da, was klingt, als
  // stamme die Lücke aus der Zeitung.
  function statusProvenance(status, vote, memberId) {
    if (status === "unknown") return voteStatusTitle(status);
    const tiers = voterTiers(vote, memberId);
    // "Ja - aus öff. Niederschrift abgeleitet - Aus der öff. Niederschrift
    // abgeleitet" sagt dasselbe zwei Mal; die Statuszeile trägt es schon.
    if (status.endsWith("-inferred") && tiers[0] === "protocol-implicit") {
      return voteStatusTitle(status);
    }
    const note = evidenceNote(vote, memberId) || (tiers.length ? TIER_LABEL[tiers[0]] : null);
    if (!note) return voteStatusTitle(status);
    const weitere = tiers.slice(1).map(x => TIER_LABEL[x]).filter(Boolean);
    return voteStatusTitle(status) + " - " + note
         + (weitere.length ? ", dazu " + weitere.join(", ").toLowerCase() : "");
  }

  return {
    withinPeriod, endOfPeriod,
    memberActiveAt, mandateAt, mandateSpans, partyAt, partySpans,
    bodyConfigAt, isRegularOf,
    voteStatus, voteStatusLabel, voteStatusTitle, sourceLabel, isUnanimous,
    evidenceNote, statusProvenance, voterTiers,
  };
})();
