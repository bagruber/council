// D3-based vote visualisations: stacked bar (anonymous) and parliament arc (named).

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
    const left = Math.min(x, window.innerWidth - r.width - 16);
    const top = Math.max(4, y - r.height);
    tooltip.style.left = left + "px";
    tooltip.style.top = top + "px";
  }

  function hideTip() {
    tooltip.classList.add("hidden");
  }

  // -- Stacked bar for anonymous votes --
  // absent shown as thinner bar above, main bar below, 50% mark

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

    // absent bar (top, thinner)
    if (results.absent > 0) {
      const absentW = (results.absent / total) * w;
      svg.append("rect")
        .attr("x", 0).attr("y", 0)
        .attr("width", absentW).attr("height", absentH)
        .attr("rx", 3)
        .attr("fill", "var(--absent)");
    }

    // main bar (yes + no)
    const mainY = absentH + gap;
    if (voting > 0) {
      const yesW = (results.yes / voting) * w;
      const noW = w - yesW;

      // yes portion
      svg.append("rect")
        .attr("x", 0).attr("y", mainY)
        .attr("width", yesW).attr("height", barH)
        .attr("rx", 4)
        .attr("fill", "var(--yes)");

      // no portion (overlaps the rounded yes corner)
      if (results.no > 0) {
        svg.append("rect")
          .attr("x", yesW).attr("y", mainY)
          .attr("width", noW).attr("height", barH)
          .attr("rx", 4)
          .attr("fill", "var(--no)");
      }

      // 50% majority mark
      const halfX = w * 0.5;
      svg.append("line")
        .attr("x1", halfX).attr("x2", halfX)
        .attr("y1", mainY - 2).attr("y2", mainY + barH + 2)
        .attr("stroke", "#fff")
        .attr("stroke-width", 2)
        .attr("stroke-dasharray", "3 2")
        .attr("opacity", 0.8);
    }

    const wrap = container.querySelector(".vote-bar-wrap");

    function barTip(evt) {
      const pctYes = voting > 0 ? ((results.yes / voting) * 100).toFixed(1) : 0;
      const pctNo  = voting > 0 ? ((results.no / voting) * 100).toFixed(1) : 0;
      const html = `
        <div><strong>Ja:</strong> ${results.yes} (${pctYes} %)</div>
        <div><strong>Nein:</strong> ${results.no} (${pctNo} %)</div>
        <div><strong>Abwesend:</strong> ${results.absent}</div>
        <div style="margin-top:4px;opacity:.7">${total} Mitglieder gesamt</div>`;
      showTip(evt, html);
    }

    wrap.addEventListener("mouseenter", barTip);
    wrap.addEventListener("mousemove", moveTip);
    wrap.addEventListener("mouseleave", hideTip);
    wrap.addEventListener("touchstart", barTip, { passive: true });
    wrap.addEventListener("touchend", hideTip);
  }

  // -- Parliament arc for named votes --
  // fill = party color, stroke = vote color, small badge circle

  function drawParliament(container, vote, members, parties) {
    const partyMap = {};
    parties.forEach(p => { partyMap[p.id] = p; });
    const memberMap = {};
    members.forEach(m => { memberMap[m.id] = m; });

    const voteMap = {};
    vote.results.yes.forEach(id => { voteMap[id] = "yes"; });
    vote.results.no.forEach(id => { voteMap[id] = "no"; });
    vote.results.absent.forEach(id => { voteMap[id] = "absent"; });

    const seats = [];
    const mayor = [];

    members.forEach(m => {
      const entry = { member: m, vote: voteMap[m.id] || "absent", party: partyMap[m.party] };
      if (m.role === "mayor") mayor.push(entry);
      else seats.push(entry);
    });

    // sort by party for visual grouping
    const partyOrder = parties.map(p => p.id);
    seats.sort((a, b) => partyOrder.indexOf(a.member.party) - partyOrder.indexOf(b.member.party));

    const n = seats.length;
    let rows;
    if (n <= 16) rows = 1;
    else if (n <= 50) rows = 2;
    else rows = 3;

    const r = 10;
    const gap = 4;
    const rowSpacing = r * 2 + gap;

    // arc: ~3/5 of a circle
    const arcSpan = (3 / 5) * 2 * Math.PI;
    const startAngle = Math.PI / 2 + (Math.PI - arcSpan) / 2 + Math.PI;
    const endAngle = startAngle + arcSpan;

    const seatsPerRow = [];
    let remaining = n;
    for (let ri = rows - 1; ri >= 0; ri--) {
      const count = Math.round(remaining / (ri + 1));
      seatsPerRow.push(count);
      remaining -= count;
    }

    const baseRadius = Math.max(60, seatsPerRow[seatsPerRow.length - 1] * (r * 2 + gap) / arcSpan);

    const allPositions = [];
    let seatIdx = 0;
    for (let ri = 0; ri < rows; ri++) {
      const rowR = baseRadius + ri * rowSpacing;
      const count = seatsPerRow[ri];
      for (let si = 0; si < count; si++) {
        const angle = count === 1
          ? (startAngle + endAngle) / 2
          : startAngle + (endAngle - startAngle) * si / (count - 1);
        const x = Math.cos(angle) * rowR;
        const y = Math.sin(angle) * rowR;
        allPositions.push({ x, y, seat: seats[seatIdx] });
        seatIdx++;
      }
    }

    const xs = allPositions.map(p => p.x);
    const ys = allPositions.map(p => p.y);
    let minX = Math.min(...xs) - r - 6;
    let maxX = Math.max(...xs) + r + 6;
    let minY = Math.min(...ys) - r - 6;
    let maxY = Math.max(...ys) + r + 6;

    const mayorX = maxX + r * 2 + 20;
    const mayorY = (minY + maxY) / 2;
    if (mayor.length) {
      maxX = mayorX + r + 6;
    }

    const svgW = maxX - minX;
    const svgH = maxY - minY;

    const svg = d3.select(container)
      .append("div").attr("class", "parliament-wrap")
      .append("svg")
      .attr("viewBox", `${minX} ${minY} ${svgW} ${svgH}`)
      .attr("width", Math.min(svgW, container.clientWidth || 500))
      .attr("preserveAspectRatio", "xMidYMid meet");

    function voteStrokeColor(v) {
      if (v === "yes") return "var(--yes)";
      if (v === "no") return "var(--no)";
      return "var(--absent)";
    }

    function partyFill(entry) {
      return entry.party ? entry.party.color : "#ccc";
    }

    function seatTip(evt, entry) {
      const voteLabel = entry.vote === "yes" ? "Ja" : entry.vote === "no" ? "Nein" : "Abwesend";
      const title = entry.member.title ? ` (${entry.member.title})` : "";
      const html = `
        <div class="tt-name">${entry.member.name}${title}</div>
        <div class="tt-party">${entry.party ? entry.party.name : ""}</div>
        <div class="tt-vote">${voteLabel}</div>`;
      showTip(evt, html);
    }

    // badge symbols
    const badgeSymbol = { yes: "✓", no: "✗", absent: "–" };
    const badgeR = 5;

    function drawSeat(cx, cy, entry) {
      const g = svg.append("g").attr("class", "seat");

      // main circle: party fill, vote stroke
      g.append("circle")
        .attr("cx", cx).attr("cy", cy).attr("r", r)
        .attr("fill", partyFill(entry))
        .attr("stroke", voteStrokeColor(entry.vote))
        .attr("stroke-width", 2.5)
        .attr("opacity", entry.vote === "absent" ? 0.45 : 1);

      // small badge circle at bottom-right
      const bx = cx + r * 0.6;
      const by = cy + r * 0.6;
      g.append("circle")
        .attr("cx", bx).attr("cy", by).attr("r", badgeR)
        .attr("fill", voteStrokeColor(entry.vote))
        .attr("stroke", "#fff")
        .attr("stroke-width", 1);

      g.append("text")
        .attr("x", bx).attr("y", by + 1)
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "middle")
        .attr("font-size", 7)
        .attr("fill", "#fff")
        .attr("font-weight", "bold")
        .text(badgeSymbol[entry.vote] || "");

      g.on("mouseenter", evt => seatTip(evt, entry))
        .on("mousemove", moveTip)
        .on("mouseleave", hideTip)
        .on("touchstart", evt => seatTip(evt, entry));
    }

    allPositions.forEach(pos => drawSeat(pos.x, pos.y, pos.seat));

    // mayor
    mayor.forEach(m => {
      drawSeat(mayorX, mayorY, m);
      svg.append("text")
        .attr("x", mayorX).attr("y", mayorY + r + 16)
        .attr("text-anchor", "middle")
        .attr("font-size", 9)
        .attr("fill", "var(--text-muted)")
        .text("BM");
    });
  }

  return { drawBar, drawParliament };
})();
