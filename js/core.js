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

  // Member's mandate is active on `date`. Honours both top-level from/to and
  // optional `periods: [...]` for split mandates.
  function memberActiveAt(member, date) {
    const periods = (member.periods && member.periods.length)
      ? member.periods
      : [{ from: member.from, to: member.to }];
    return periods.some(p => withinPeriod(p, date));
  }

  // ── Body composition ──────────────────────────────────────────────────────

  // Returns the seatConfig active on `date`. For bodies without seatConfigs
  // (e.g. plenum), the body itself is returned as the "config".
  function bodyConfigAt(body, date) {
    const configs = body && body.seatConfigs;
    if (!configs || !configs.length) return body || {};
    return configs.find(c => withinPeriod(c, date)) || body;
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
  //   5. Explicit `vote.voters[id]`              → that status
  //   6. Per-vote temporary absence (rare)       → 'absent'
  //   7. Unanimous anonymous (yes>0, no===0)     → 'yes-inferred'
  //                          (no>0,  yes===0)    → 'no-inferred'
  //   8. Anonymous split, no per-voter info      → 'unknown'

  function voteStatus(memberId, vote, session, member) {
    if (member && !memberActiveAt(member, vote.date)) return null;

    // Vor der Sitzungsabwesenheit prüfen: wer befangen ist, war ja da.
    const ex = (vote.excluded || []).find(e => e.member === memberId);
    if (ex) {
      if (ex.reason === "beteiligung") return "excluded";
      if (ex.reason === "enthaltung")   return "abstained";
      return "absent";                  // kurzfristig abwesend
    }

    if (session && session.absent && session.absent.includes(memberId)) return "absent";

    if (vote.type === "named") {
      if (vote.results.yes.includes(memberId))    return "yes";
      if (vote.results.no.includes(memberId))     return "no";
      if (vote.results.absent.includes(memberId)) return "absent";
      return null;
    }

    if (vote.voters && vote.voters[memberId]) {
      return vote.voters[memberId];                // already 'yes'|'no'|'absent'
    }
    if (vote.results.absent_ids && vote.results.absent_ids.includes(memberId)) {
      return "absent";
    }

    // Einstimmig heißt nur dann "alle Anwesenden dafür", wenn auch alle
    // mitgestimmt haben. Wo die Niederschrift weniger Stimmen ausweist als
    // Stimmberechtigte da waren, setzt der Import `inferable: false` —
    // dann bleibt es beim ehrlichen Fragezeichen.
    const { yes, no } = vote.results;
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
                   excluded: "bef.", abstained: "enth.",
                   unknown: "?" }[status] || "?";
    return withMarker && status.endsWith("-inferred") ? base + "*" : base;
  }

  // Ausgeschriebene Fassung für Tooltips und Legende.
  function voteStatusTitle(status) {
    return { yes: "Ja", no: "Nein", absent: "Abwesend",
             "yes-inferred": "Ja (aus Anwesenheit abgeleitet)",
             "no-inferred": "Nein (aus Anwesenheit abgeleitet)",
             excluded: "Wegen persönlicher Beteiligung ausgeschlossen (Art. 49 GO)",
             abstained: "Enthalten",
             unknown: "Nicht überliefert" }[status] || "Nicht überliefert";
  }

  // Herkunft der Einzelstimmen — vier Stufen, siehe data/knowledge.
  function sourceLabel(vote) {
    const s = vote.source;
    if (!s) return null;
    return {
      "protocol-explicit": "Namentlich in der Niederschrift",
      "protocol-implicit": "Aus der Anwesenheit abgeleitet",
      press: "Aus Presseberichten",
      tracked: "In der Sitzung mitgeschrieben",
    }[s.tier] || null;
  }

  return {
    withinPeriod, endOfPeriod,
    memberActiveAt,
    bodyConfigAt, isRegularOf,
    voteStatus, voteStatusLabel, voteStatusTitle, sourceLabel, isUnanimous,
  };
})();
