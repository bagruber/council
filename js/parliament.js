// Vote visualisations:
//  – stacked bar (anonymous votes)
//  – parliament chart (named votes, pluggable layout; default = horseshoe)
//
// Pure DOM + SVG (no D3 dependency).
//
// Public API (kept stable for app.js):
//   VoteVis.drawBar(container, results)
//   VoteVis.drawParliament(container, vote, members, parties, seatOrder [, options])

const VoteVis = (() => {
  const NS  = "http://www.w3.org/2000/svg";
  const DEG = Math.PI / 180;

  // ─── Defaults (override via options arg on drawParliament) ───────────────

  const DEFAULTS = {
    layout: "horseshoe",
    rows: null,                   // null = auto-pick
    seatRadius: 14,
    seatGap: 7,
    arcDeg: 270,
    iconPosition: "concentric-outer",   // or "corner-tr"
    iconRatio: 0.46,              // mini-circle / seat radius
    mayorOffsetFactor: 0.55,      // mayor distance from chamber center, in units of R0
    showRowGuides: true,          // subtle arcs behind each row
  };

  // ─── Layout registry ─────────────────────────────────────────────────────

  const LAYOUTS = {
    horseshoe: horseshoeLayout,
    // future: classic, rectangle, etc.
  };

  // Auto pick rows from seat count
  function autoPickRows(n) {
    if (n <= 12) return 1;
    if (n <= 30) return 2;
    if (n <= 60) return 3;
    return 4;
  }

  /**
   * Horseshoe layout.
   * Solves the inner radius R0 such that within-row spacing equals between-row spacing,
   * yielding a visually balanced, dense seating.
   *
   *   seatUnit u = 2*seatRadius + seatGap
   *   Row i radius R_i = R0 + i*u
   *   Arc capacity per row = arc/u * R_i
   *   total = sum_i (arc/u * R_i) = arc/u * (R*R0 + u*(R-1)*R/2)
   *   Solve: R0 = u*(N / (arc*R) - (R-1)/2)
   */
  function horseshoeLayout({ count, rows, seatRadius, seatGap, arcDeg }) {
    const u = 2 * seatRadius + seatGap;
    const arc = arcDeg * DEG;

    let R0 = u * (count / (arc * rows) - (rows - 1) / 2);
    R0 = Math.max(R0, u * 1.2);    // floor so the inner ring isn't crammed

    const radii = Array.from({ length: rows }, (_, i) => R0 + i * u);

    // allocate seats per row proportional to radius (= circumference)
    const sumR = radii.reduce((s, r) => s + r, 0);
    const seatsPerRow = radii.map(r => Math.round(count * r / sumR));

    // patch rounding so we hit exact N – preserve "outer has most" invariant
    let diff = count - seatsPerRow.reduce((a, b) => a + b, 0);
    let cursor = rows - 1;
    while (diff > 0) { seatsPerRow[cursor]++; diff--; cursor = (cursor - 1 + rows) % rows; }
    while (diff < 0) {
      // remove from largest row that still has > 1
      let idx = -1, mx = -1;
      for (let i = 0; i < rows; i++) if (seatsPerRow[i] > 1 && seatsPerRow[i] > mx) { mx = seatsPerRow[i]; idx = i; }
      if (idx === -1) break;
      seatsPerRow[idx]--; diff++;
    }

    // ensure monotone (inner ≤ outer); shuffle if rounding gave a weird shape
    seatsPerRow.sort((a, b) => a - b);

    // generate positions
    const arcStart = 90 * DEG - arc / 2;
    const positions = [];
    let idx = 0;
    for (let r = 0; r < rows; r++) {
      const n = seatsPerRow[r];
      const radius = radii[r];
      for (let j = 0; j < n; j++) {
        const t = n === 1 ? 0.5 : j / (n - 1);
        const angle = arcStart + t * arc;
        positions.push({
          index:  idx++,
          row:    r,
          radius,
          angle,
          x:  Math.cos(angle) * radius,
          y: -Math.sin(angle) * radius,    // SVG y-down: flip
        });
      }
    }

    return { positions, R0, R_outer: radii[rows - 1], radii, seatsPerRow };
  }

  // ─── Vote → colour / icon / label ────────────────────────────────────────

  const VOTE_COLOR = {
    yes:     "var(--yes)",
    no:      "var(--no)",
    absent:  "var(--absent)",
    unknown: "var(--border)",
  };
  const VOTE_ICON  = { yes: "✓", no: "✗", absent: "–", unknown: "?" };
  const VOTE_LABEL = { yes: "Ja", no: "Nein", absent: "Abwesend", unknown: "Unbekannt" };

  // ─── Tooltip (desktop hover) ─────────────────────────────────────────────

  const tooltipEl = document.getElementById("tooltip");

  function showTooltip(evt, html) {
    if (!tooltipEl) return;
    tooltipEl.innerHTML = html;
    tooltipEl.classList.remove("hidden");
    positionTooltip(evt);
  }
  function moveTooltip(evt) {
    if (!tooltipEl || tooltipEl.classList.contains("hidden")) return;
    positionTooltip(evt);
  }
  function hideTooltip() {
    if (tooltipEl) tooltipEl.classList.add("hidden");
  }
  function positionTooltip(evt) {
    const cx = (evt.touches ? evt.touches[0].clientX : evt.clientX) + 14;
    const cy = (evt.touches ? evt.touches[0].clientY : evt.clientY) - 10;
    const r = tooltipEl.getBoundingClientRect();
    tooltipEl.style.left = Math.min(cx, window.innerWidth - r.width - 8) + "px";
    tooltipEl.style.top  = Math.max(4, cy - r.height) + "px";
  }

  // ─── Popover (mobile tap) ────────────────────────────────────────────────

  let popoverEl    = null;
  let activeSeatId = null;
  const isCoarse   = matchMedia("(hover: none)").matches;

  function closePopover() {
    if (popoverEl) { popoverEl.remove(); popoverEl = null; }
    activeSeatId = null;
    document.removeEventListener("click", outsideClickHandler, true);
  }
  function outsideClickHandler(evt) {
    if (!popoverEl) return;
    if (popoverEl.contains(evt.target)) return;
    if (evt.target.closest(".seat")) return;
    closePopover();
  }
  function showPopover(seatG, seat) {
    closePopover();
    const wrap = seatG.closest(".parliament-wrap");
    if (!wrap) return;
    const seatRect = seatG.getBoundingClientRect();
    const wrapRect = wrap.getBoundingClientRect();

    const pop = document.createElement("div");
    pop.className = "seat-popover";
    pop.innerHTML = `
      <button class="seat-popover-close" aria-label="Schließen">&times;</button>
      <div class="seat-popover-body">${seatInfoHTML(seat)}</div>
      <a href="#/member/${seat.id}" class="seat-popover-link">Profil ansehen →</a>`;

    // position above seat; flip below if it would clip top
    const cx = seatRect.left - wrapRect.left + seatRect.width  / 2;
    const cy = seatRect.top  - wrapRect.top  + seatRect.height / 2;
    pop.style.left = cx + "px";
    pop.style.top  = cy + "px";
    pop.dataset.placement = (cy < 120) ? "below" : "above";

    wrap.appendChild(pop);

    pop.querySelector(".seat-popover-close").addEventListener("click", evt => {
      evt.stopPropagation();
      closePopover();
    });

    popoverEl    = pop;
    activeSeatId = seat.id;
    setTimeout(() => document.addEventListener("click", outsideClickHandler, true), 0);
  }

  function seatInfoHTML(seat) {
    const titlePart = seat.title ? ` <span class="seat-title">(${seat.title})</span>` : "";
    return `
      <div class="seat-name">${seat.name}${titlePart}</div>
      <div class="seat-party"><span class="seat-party-dot" style="background:${seat.party?.color || "#aaa"}"></span>${seat.party?.name || ""}</div>
      <div class="seat-vote vote-${seat.vote}">${VOTE_LABEL[seat.vote] || seat.vote}</div>`;
  }

  // ─── Row guides (subtle arcs behind each row) ────────────────────────────

  function drawRowGuides(svg, layout, opts) {
    const arc = opts.arcDeg * DEG;
    const arcStart = 90 * DEG - arc / 2;
    const arcEnd   = 90 * DEG + arc / 2;
    const steps    = 80;
    layout.radii.forEach(r => {
      const pts = [];
      for (let i = 0; i <= steps; i++) {
        const a = arcStart + (arcEnd - arcStart) * (i / steps);
        pts.push(`${(Math.cos(a) * r).toFixed(2)} ${(-Math.sin(a) * r).toFixed(2)}`);
      }
      const path = svgEl("path");
      path.setAttribute("d", "M " + pts.join(" L "));
      path.setAttribute("fill", "none");
      path.setAttribute("stroke", "currentColor");
      path.setAttribute("stroke-width", "0.7");
      path.setAttribute("opacity", "0.18");
      path.setAttribute("class", "row-guide");
      svg.appendChild(path);
    });
  }

  // ─── Seat rendering ──────────────────────────────────────────────────────

  function svgEl(tag) { return document.createElementNS(NS, tag); }

  function drawSeat(svg, pos, seat, opts) {
    const r       = opts.seatRadius;
    const stroke  = VOTE_COLOR[seat.vote] || VOTE_COLOR.unknown;
    const fill    = seat.party?.color || "#aaa";
    const grayed  = seat.vote === "absent";

    const g = svgEl("g");
    g.classList.add("seat");
    if (grayed) g.classList.add("seat-absent");
    if (seat.id) g.dataset.seatId = seat.id;

    const main = svgEl("circle");
    main.setAttribute("cx", pos.x); main.setAttribute("cy", pos.y);
    main.setAttribute("r", r);
    main.setAttribute("fill", fill);
    main.setAttribute("stroke", stroke);
    main.setAttribute("stroke-width", Math.max(2.5, r * 0.18));
    g.appendChild(main);

    // ─── mini indicator ───
    const iconR = r * opts.iconRatio;
    let ix, iy;
    if (opts.iconPosition === "concentric-outer") {
      const d  = Math.hypot(pos.x, pos.y);
      const ux = d > 0 ? pos.x / d : 0;
      const uy = d > 0 ? pos.y / d : 1;
      const iconDist = r * 0.95;
      ix = pos.x + ux * iconDist;
      iy = pos.y + uy * iconDist;
    } else {  // corner-tr
      ix = pos.x + r * 0.7;
      iy = pos.y - r * 0.7;
    }

    const mini = svgEl("circle");
    mini.setAttribute("cx", ix); mini.setAttribute("cy", iy);
    mini.setAttribute("r", iconR);
    mini.setAttribute("fill", stroke);
    mini.setAttribute("stroke", "#fff");
    mini.setAttribute("stroke-width", "1.3");
    g.appendChild(mini);

    const txt = svgEl("text");
    txt.setAttribute("x", ix); txt.setAttribute("y", iy);
    txt.setAttribute("text-anchor", "middle");
    txt.setAttribute("dominant-baseline", "central");
    txt.setAttribute("font-size", iconR * 1.35);
    txt.setAttribute("font-weight", "bold");
    txt.setAttribute("fill", "#fff");
    txt.style.pointerEvents = "none";
    txt.style.userSelect    = "none";
    txt.textContent = VOTE_ICON[seat.vote] || "";
    g.appendChild(txt);

    // ─── interaction ───
    if (isCoarse) {
      g.addEventListener("click", evt => {
        evt.stopPropagation();
        if (activeSeatId === seat.id) {
          closePopover();
          if (seat.id) window.location.hash = "/member/" + seat.id;
        } else {
          showPopover(g, seat);
        }
      });
    } else {
      g.addEventListener("mouseenter", evt => showTooltip(evt, seatInfoHTML(seat)));
      g.addEventListener("mousemove",  moveTooltip);
      g.addEventListener("mouseleave", hideTooltip);
      g.addEventListener("click", () => {
        hideTooltip();
        if (seat.id) window.location.hash = "/member/" + seat.id;
      });
    }

    svg.appendChild(g);
  }

  // ─── Chart renderer (any layout) ─────────────────────────────────────────

  function renderChart(container, opts) {
    const o = { ...DEFAULTS, ...opts };
    if (!o.rows) o.rows = autoPickRows(o.seats.length);

    const layoutFn = LAYOUTS[o.layout];
    if (!layoutFn) throw new Error("Unknown layout: " + o.layout);

    const layout = layoutFn({
      count:      o.seats.length,
      rows:       o.rows,
      seatRadius: o.seatRadius,
      seatGap:    o.seatGap,
      arcDeg:     o.arcDeg,
    });

    // mayor at angle 270° (south, opposite chamber opening of a 270°-horseshoe)
    const hasMayor   = !!o.mayor;
    const mayorAngle = 270 * DEG;
    const mayorDist  = layout.R0 * o.mayorOffsetFactor;
    const mx = Math.cos(mayorAngle) * mayorDist;
    const my = -Math.sin(mayorAngle) * mayorDist;

    // bounding box
    const pad = o.seatRadius * 1.6;
    const minX = -layout.R_outer - pad;
    const maxX =  layout.R_outer + pad;
    const minY = -layout.R_outer - pad;
    const maxY = Math.max(
      ...layout.positions.map(p => p.y + o.seatRadius + 4),
      hasMayor ? my + o.seatRadius * 2.5 : -Infinity
    );

    const wrap = document.createElement("div");
    wrap.className = "parliament-wrap";
    container.appendChild(wrap);

    const svg = svgEl("svg");
    svg.setAttribute("viewBox", `${minX} ${minY} ${maxX - minX} ${maxY - minY}`);
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
    wrap.appendChild(svg);

    // subtle row guides (behind seats)
    if (o.showRowGuides) drawRowGuides(svg, layout, o);

    // seats (order in array = seating order)
    o.seats.forEach((seat, i) => drawSeat(svg, layout.positions[i], seat, o));

    if (hasMayor) {
      drawSeat(svg, { x: mx, y: my, angle: mayorAngle, row: -1, radius: 0 }, o.mayor, o);
      const lbl = svgEl("text");
      lbl.setAttribute("x", mx);
      lbl.setAttribute("y", my + o.seatRadius * 1.4 + 10);
      lbl.setAttribute("text-anchor", "middle");
      lbl.setAttribute("font-size", "11");
      lbl.setAttribute("fill", "var(--text-muted)");
      lbl.textContent = "BM";
      svg.appendChild(lbl);
    }

    return svg;
  }

  // ─── Stacked bar chart (anonymous votes) ────────────────────────────────

  function drawBar(container, results) {
    const capacity = 25;
    const voting   = results.yes + results.no;
    const w        = container.clientWidth || 400;
    const barH     = 28;
    const absentH  = 10;
    const gap      = 4;
    const h        = absentH + gap + barH;

    const wrap = document.createElement("div");
    wrap.className = "vote-bar-wrap";
    container.appendChild(wrap);

    const svg = svgEl("svg");
    svg.setAttribute("width",  w);
    svg.setAttribute("height", h);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    wrap.appendChild(svg);

    const voteW = (voting / capacity) * w;
    const voteX = (w - voteW) / 2;

    if (results.absent > 0) {
      const absentW = (results.absent / capacity) * w;
      const absentX = (w - absentW) / 2;
      const rect = svgEl("rect");
      rect.setAttribute("x", absentX); rect.setAttribute("y", 0);
      rect.setAttribute("width", absentW); rect.setAttribute("height", absentH);
      rect.setAttribute("rx", 3); rect.setAttribute("fill", "var(--absent)");
      svg.appendChild(rect);
    }

    const mainY = absentH + gap;
    if (voting > 0) {
      const yesW = (results.yes / capacity) * w;
      const yesR = svgEl("rect");
      yesR.setAttribute("x", voteX); yesR.setAttribute("y", mainY);
      yesR.setAttribute("width", yesW); yesR.setAttribute("height", barH);
      yesR.setAttribute("rx", 4); yesR.setAttribute("fill", "var(--yes)");
      svg.appendChild(yesR);

      if (results.no > 0) {
        const noW = (results.no / capacity) * w;
        const noR = svgEl("rect");
        noR.setAttribute("x", voteX + yesW); noR.setAttribute("y", mainY);
        noR.setAttribute("width", noW); noR.setAttribute("height", barH);
        noR.setAttribute("rx", 4); noR.setAttribute("fill", "var(--no)");
        svg.appendChild(noR);
      }

      // 50%-Markierung
      const ln = svgEl("line");
      ln.setAttribute("x1", w / 2); ln.setAttribute("x2", w / 2);
      ln.setAttribute("y1", mainY - 2); ln.setAttribute("y2", mainY + barH + 2);
      ln.setAttribute("stroke", "#fff"); ln.setAttribute("stroke-width", 2);
      ln.setAttribute("stroke-dasharray", "3 2"); ln.setAttribute("opacity", 0.8);
      svg.appendChild(ln);
    }

    function barTip(evt) {
      const pctYes = voting > 0 ? ((results.yes / voting) * 100).toFixed(1) : 0;
      const pctNo  = voting > 0 ? ((results.no / voting) * 100).toFixed(1) : 0;
      showTooltip(evt, `
        <div><strong>Ja:</strong> ${results.yes} (${pctYes} %)</div>
        <div><strong>Nein:</strong> ${results.no} (${pctNo} %)</div>
        <div><strong>Abwesend:</strong> ${results.absent}</div>
        <div style="margin-top:4px;opacity:.7">${capacity} Mitglieder gesamt</div>`);
    }
    wrap.addEventListener("mouseenter", barTip);
    wrap.addEventListener("mousemove",  moveTooltip);
    wrap.addEventListener("mouseleave", hideTooltip);
    wrap.addEventListener("touchstart", barTip, { passive: true });
    wrap.addEventListener("touchend",   hideTooltip);
  }

  // ─── Public: drawParliament (compat with existing app.js) ───────────────

  function drawParliament(container, vote, members, parties, seatOrder, options = {}) {
    const partyMap  = Object.fromEntries(parties.map(p => [p.id, p]));
    const memberMap = Object.fromEntries(members.map(m => [m.id, m]));

    const voteRes = {};
    vote.results.yes.forEach(id => voteRes[id] = "yes");
    vote.results.no .forEach(id => voteRes[id] = "no");
    vote.results.absent.forEach(id => voteRes[id] = "absent");

    const seats = [];
    let mayor = null;

    Object.keys(voteRes).forEach(id => {
      const m = memberMap[id];
      if (!m) return;
      const entry = {
        id: m.id,
        name: m.name || `${m.firstName || ""} ${m.lastName || ""}`.trim(),
        title: m.title || "",
        party: partyMap[m.party],
        vote: voteRes[id],
      };
      if (m.role === "mayor") mayor = entry;
      else seats.push(entry);
    });

    if (!seats.length && !mayor) return;

    // sort by seatOrder (party), then by name
    const order = seatOrder || parties.map(p => p.id);
    seats.sort((a, b) => {
      const ia = order.indexOf(a.party?.id ?? "");
      const ib = order.indexOf(b.party?.id ?? "");
      if (ia !== ib) return ia - ib;
      return (a.name || "").localeCompare(b.name || "");
    });

    // summary bar above the parliament chart
    drawBar(container, {
      yes:    vote.results.yes.length,
      no:     vote.results.no.length,
      absent: vote.results.absent.length,
    });

    renderChart(container, { seats, mayor, ...options });
  }

  return { drawBar, drawParliament, renderChart, LAYOUTS };
})();
