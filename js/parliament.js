// D3 vote visualisations: stacked bar (anonymous) and parliament arc (named).

const VoteVis = (() => {

  const tooltip = document.getElementById("tooltip");

  function showTip(evt, html) {
    tooltip.innerHTML = html;
    tooltip.classList.remove("hidden");
    positionTip(evt);
  }

  function moveTip(evt) {
    if (tooltip.classList.contains("hidden")) return;
    positionTip(evt);
  }

  function positionTip(evt) {
    const x = (evt.touches ? evt.touches[0].clientX : evt.clientX) + 12;
    const y = (evt.touches ? evt.touches[0].clientY : evt.clientY) - 10;
    const r = tooltip.getBoundingClientRect();
    tooltip.style.left = Math.min(x, window.innerWidth - r.width - 16) + "px";
    tooltip.style.top = Math.max(4, y - r.height) + "px";
  }

  function hideTip() {
    tooltip.classList.add("hidden");
  }

  // -- Stacked bar for anonymous votes --

  function drawBar(container, results) {
    const total = results.yes + results.no + results.absent;
    const voting = results.yes + results.no;
    const w = container.clientWidth || 400;
    const barH = 28;
    const absentH = 10;
    const gap = 4;
    const h = absentH + gap + barH;

    const svg = d3.select(container)
      .append("div").attr("class", "vote-bar-wrap")
      .append("svg").attr("width", w).attr("height", h)
      .attr("viewBox", `0 0 ${w} ${h}`);

    if (results.absent > 0) {
      const absentW = (results.absent / total) * w;
      svg.append("rect")
        .attr("x", 0).attr("y", 0)
        .attr("width", absentW).attr("height", absentH)
        .attr("rx", 3)
        .attr("fill", "var(--absent)");
    }

    const mainY = absentH + gap;
    if (voting > 0) {
      const yesW = (results.yes / voting) * w;
      svg.append("rect")
        .attr("x", 0).attr("y", mainY)
        .attr("width", yesW).attr("height", barH)
        .attr("rx", 4)
        .attr("fill", "var(--yes)");

      if (results.no > 0) {
        svg.append("rect")
          .attr("x", yesW).attr("y", mainY)
          .attr("width", w - yesW).attr("height", barH)
          .attr("rx", 4)
          .attr("fill", "var(--no)");
      }

      // 50% majority mark
      svg.append("line")
        .attr("x1", w / 2).attr("x2", w / 2)
        .attr("y1", mainY - 2).attr("y2", mainY + barH + 2)
        .attr("stroke", "#fff").attr("stroke-width", 2)
        .attr("stroke-dasharray", "3 2").attr("opacity", 0.8);
    }

    const wrap = container.querySelector(".vote-bar-wrap");
    function barTip(evt) {
      const pctYes = voting > 0 ? ((results.yes / voting) * 100).toFixed(1) : 0;
      const pctNo  = voting > 0 ? ((results.no / voting) * 100).toFixed(1) : 0;
      showTip(evt, `
        <div><strong>Ja:</strong> ${results.yes} (${pctYes} %)</div>
        <div><strong>Nein:</strong> ${results.no} (${pctNo} %)</div>
        <div><strong>Abwesend:</strong> ${results.absent}</div>
        <div style="margin-top:4px;opacity:.7">${total} Mitglieder gesamt</div>`);
    }
    wrap.addEventListener("mouseenter", barTip);
    wrap.addEventListener("mousemove", moveTip);
    wrap.addEventListener("mouseleave", hideTip);
    wrap.addEventListener("touchstart", barTip, { passive: true });
    wrap.addEventListener("touchend", hideTip);
  }

  // -- Parliament arc for named votes --

  function drawParliament(container, vote, members, parties, seatOrder) {
    const partyMap = {};
    parties.forEach(p => { partyMap[p.id] = p; });
    const memberMap = {};
    members.forEach(m => { memberMap[m.id] = m; });

    // build seats from vote results only (handles historical composition)
    const voteMap = {};
    vote.results.yes.forEach(id => { voteMap[id] = "yes"; });
    vote.results.no.forEach(id => { voteMap[id] = "no"; });
    vote.results.absent.forEach(id => { voteMap[id] = "absent"; });

    const allIds = Object.keys(voteMap);
    const councillors = [];
    const mayors = [];

    allIds.forEach(id => {
      const m = memberMap[id];
      if (!m) return;
      const entry = { member: m, vote: voteMap[id], party: partyMap[m.party] };
      if (m.role === "mayor") mayors.push(entry);
      else councillors.push(entry);
    });

    // sort by seating order
    const order = seatOrder || parties.map(p => p.id);
    councillors.sort((a, b) => {
      const ia = order.indexOf(a.member.party);
      const ib = order.indexOf(b.member.party);
      return ia - ib;
    });

    const n = councillors.length;
    if (n === 0) return;

    const r = 10;
    const rowGap = 6;
    const rowSpacing = r * 2 + rowGap;

    // arc: ~3/5 of circle
    const arcSpan = (3 / 5) * 2 * Math.PI;
    const startAngle = Math.PI / 2 + (Math.PI - arcSpan) / 2 + Math.PI;
    const endAngle = startAngle + arcSpan;

    // row split: compute so arc-length spacing is similar
    const innerR = Math.max(50, n * 1.8);
    const outerR = innerR + rowSpacing;
    const innerCount = Math.round(n * innerR / (innerR + outerR));
    const outerCount = n - innerCount;

    // distribute parties across rows
    const partyGroups = [];
    let prev = null;
    councillors.forEach(seat => {
      if (!prev || prev.party.id !== seat.party.id) {
        partyGroups.push({ partyId: seat.party.id, seats: [seat] });
      } else {
        partyGroups[partyGroups.length - 1].seats.push(seat);
      }
      prev = seat;
    });

    // allocate inner/outer per party group
    const alloc = partyGroups.map(g => {
      let inner = Math.round(g.seats.length * innerCount / n);
      if (g.seats.length >= 2) {
        inner = Math.max(1, Math.min(inner, g.seats.length - 1));
      } else {
        // single-seat parties: put in outer row by default
        inner = 0;
      }
      return { ...g, inner, outer: g.seats.length - inner };
    });

    // adjust totals to match targets
    let innerSum = alloc.reduce((s, a) => s + a.inner, 0);
    while (innerSum < innerCount) {
      // move a seat from outer to inner in the group with most outer headroom
      const cands = alloc.filter(a => a.outer > 1);
      if (!cands.length) break;
      cands.sort((a, b) => b.outer - a.outer);
      cands[0].inner++;
      cands[0].outer--;
      innerSum++;
    }
    while (innerSum > innerCount) {
      const cands = alloc.filter(a => a.inner > 1 || (a.inner === 1 && a.seats.length === 1));
      if (!cands.length) break;
      cands.sort((a, b) => b.inner - a.inner);
      cands[0].inner--;
      cands[0].outer++;
      innerSum--;
    }

    // build row arrays in seating order
    const innerSeats = [];
    const outerSeats = [];
    alloc.forEach(g => {
      // alternate: first seat outer, second inner, etc.
      for (let i = 0; i < g.seats.length; i++) {
        if (i % 2 === 0 && outerSeats.length < outerCount) {
          outerSeats.push(g.seats[i]);
        } else if (innerSeats.length < innerCount) {
          innerSeats.push(g.seats[i]);
        } else {
          outerSeats.push(g.seats[i]);
        }
      }
    });

    // place seats along arcs
    function arcPositions(count, radius) {
      const positions = [];
      for (let i = 0; i < count; i++) {
        const angle = count === 1
          ? (startAngle + endAngle) / 2
          : startAngle + (endAngle - startAngle) * i / (count - 1);
        positions.push({
          x: Math.cos(angle) * radius,
          y: Math.sin(angle) * radius,
        });
      }
      return positions;
    }

    const innerPositions = arcPositions(innerSeats.length, innerR);
    const outerPositions = arcPositions(outerSeats.length, outerR);

    // compute bounding box
    const all = [...innerPositions, ...outerPositions];
    let minX = Math.min(...all.map(p => p.x)) - r - 8;
    let maxX = Math.max(...all.map(p => p.x)) + r + 8;
    let minY = Math.min(...all.map(p => p.y)) - r - 8;
    let maxY = Math.max(...all.map(p => p.y)) + r + 8;

    // mayor to the right
    const mayorX = maxX + r * 2 + 20;
    const mayorY = (minY + maxY) / 2;
    if (mayors.length) maxX = mayorX + r + 8;

    const svgW = maxX - minX;
    const svgH = maxY - minY;

    const svg = d3.select(container)
      .append("div").attr("class", "parliament-wrap")
      .append("svg")
      .attr("viewBox", `${minX} ${minY} ${svgW} ${svgH}`)
      .attr("width", Math.min(svgW, container.clientWidth || 500))
      .attr("preserveAspectRatio", "xMidYMid meet");

    const voteStroke = { yes: "var(--yes)", no: "var(--no)", absent: "var(--absent)" };
    const voteBadge = { yes: "\u2713", no: "\u2717", absent: "\u2013" };

    function seatTip(evt, entry) {
      const label = entry.vote === "yes" ? "Ja" : entry.vote === "no" ? "Nein" : "Abwesend";
      const title = entry.member.title ? ` (${entry.member.title})` : "";
      showTip(evt, `
        <div class="tt-name">${entry.member.name}${title}</div>
        <div class="tt-party">${entry.party ? entry.party.name : ""}</div>
        <div class="tt-vote">${label}</div>`);
    }

    function drawSeat(cx, cy, entry) {
      const g = svg.append("g").attr("class", "seat");
      const fill = entry.party ? entry.party.color : "#ccc";
      const stroke = voteStroke[entry.vote] || voteStroke.absent;
      const opacity = entry.vote === "absent" ? 0.4 : 1;

      g.append("circle")
        .attr("cx", cx).attr("cy", cy).attr("r", r)
        .attr("fill", fill).attr("stroke", stroke)
        .attr("stroke-width", 2.5).attr("opacity", opacity);

      // badge
      const bx = cx + r * 0.6;
      const by = cy + r * 0.6;
      g.append("circle")
        .attr("cx", bx).attr("cy", by).attr("r", 5)
        .attr("fill", stroke).attr("stroke", "#fff").attr("stroke-width", 1);
      g.append("text")
        .attr("x", bx).attr("y", by + 1)
        .attr("text-anchor", "middle").attr("dominant-baseline", "middle")
        .attr("font-size", 7).attr("fill", "#fff").attr("font-weight", "bold")
        .text(voteBadge[entry.vote] || "");

      g.on("mouseenter", evt => seatTip(evt, entry))
        .on("mousemove", moveTip)
        .on("mouseleave", hideTip)
        .on("touchstart", evt => seatTip(evt, entry));
    }

    innerPositions.forEach((pos, i) => drawSeat(pos.x, pos.y, innerSeats[i]));
    outerPositions.forEach((pos, i) => drawSeat(pos.x, pos.y, outerSeats[i]));

    mayors.forEach(m => {
      drawSeat(mayorX, mayorY, m);
      svg.append("text")
        .attr("x", mayorX).attr("y", mayorY + r + 16)
        .attr("text-anchor", "middle").attr("font-size", 9)
        .attr("fill", "var(--text-muted)").text("BM");
    });
  }

  return { drawBar, drawParliament };
})();
