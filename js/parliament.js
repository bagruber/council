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

    const wrap = container.querySelector(".vote-bar-wrap:last-child");
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

    const voteResults = {};
    vote.results.yes.forEach(id => { voteResults[id] = "yes"; });
    vote.results.no.forEach(id => { voteResults[id] = "no"; });
    vote.results.absent.forEach(id => { voteResults[id] = "absent"; });

    const allIds = Object.keys(voteResults);
    const councillors = [];
    const mayors = [];

    allIds.forEach(id => {
      const m = memberMap[id];
      if (!m) return;
      const entry = { member: m, vote: voteResults[id], party: partyMap[m.party] };
      if (m.role === "mayor") mayors.push(entry);
      else councillors.push(entry);
    });

    // sort by seating order, stable within party
    const order = seatOrder || parties.map(p => p.id);
    councillors.sort((a, b) => {
      const ia = order.indexOf(a.member.party);
      const ib = order.indexOf(b.member.party);
      if (ia !== ib) return ia - ib;
      return a.member.name.localeCompare(b.member.name);
    });

    const n = councillors.length;
    if (n === 0) return;

    // draw stacked bar summary above the arc
    const barResults = {
      yes: vote.results.yes.length,
      no: vote.results.no.length,
      absent: vote.results.absent.length,
    };
    drawBar(container, barResults);

    const r = 10;
    const arcSpan = (3 / 4) * 2 * Math.PI;
    const startAngle = (3 / 4) * Math.PI;
    const endAngle = startAngle + arcSpan;

    // single row for committees / small bodies, two rows for full council
    const singleRow = n <= 12;

    let positioned;
    let mayorY;

    if (singleRow) {
      const radius = Math.max(40, n * 3.5);
      const pos = arcPos(n, radius, startAngle, endAngle);
      positioned = councillors.map((seat, i) => ({ ...seat, x: pos[i].x, y: pos[i].y }));
      mayorY = radius * 0.55;
    } else {
      const rowGap = 6;
      const rowSpacing = r * 2 + rowGap;
      const innerR = Math.max(50, n * 1.8);
      const outerR = innerR + rowSpacing;
      const innerTarget = Math.round(n * innerR / (innerR + outerR));
      const outerTarget = n - innerTarget;

      // group consecutive same-party members
      const groups = [];
      councillors.forEach(seat => {
        const last = groups[groups.length - 1];
        if (last && last[0].party.id === seat.party.id) last.push(seat);
        else groups.push([seat]);
      });

      // allocate inner/outer per party group, keeping blocks together
      const alloc = groups.map(g => {
        let inner = Math.round(g.length * innerTarget / n);
        if (g.length >= 2) inner = Math.max(1, Math.min(inner, g.length - 1));
        else inner = 0;
        return { seats: g, inner, outer: g.length - inner };
      });

      // balance row sizes
      let innerSum = alloc.reduce((s, a) => s + a.inner, 0);
      while (innerSum < innerTarget) {
        const c = alloc.filter(a => a.outer > 1);
        if (!c.length) break;
        c.sort((a, b) => b.outer - a.outer);
        c[0].inner++; c[0].outer--; innerSum++;
      }
      while (innerSum > innerTarget) {
        const c = alloc.filter(a => a.inner > 1 || (a.inner === 1 && a.seats.length === 1));
        if (!c.length) break;
        c.sort((a, b) => b.inner - a.inner);
        c[0].inner--; c[0].outer++; innerSum--;
      }

      // fill rows keeping party groups contiguous
      const innerSeats = [];
      const outerSeats = [];
      alloc.forEach(g => {
        for (let i = 0; i < g.outer; i++) outerSeats.push(g.seats[i]);
        for (let i = g.outer; i < g.seats.length; i++) innerSeats.push(g.seats[i]);
      });

      const innerPos = arcPos(innerSeats.length, innerR, startAngle, endAngle);
      const outerPos = arcPos(outerSeats.length, outerR, startAngle, endAngle);

      positioned = [
        ...innerSeats.map((s, i) => ({ ...s, x: innerPos[i].x, y: innerPos[i].y })),
        ...outerSeats.map((s, i) => ({ ...s, x: outerPos[i].x, y: outerPos[i].y })),
      ];
      mayorY = innerR * 0.6;
    }

    // bounding box
    let minX = Math.min(...positioned.map(p => p.x)) - r - 8;
    let maxX = Math.max(...positioned.map(p => p.x)) + r + 8;
    let minY = Math.min(...positioned.map(p => p.y)) - r - 8;
    let maxY = Math.max(...positioned.map(p => p.y)) + r + 8;
    if (mayors.length) maxY = Math.max(maxY, mayorY + r + 28);

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

      // desktop: hover for tooltip, click navigates to profile
      g.on("mouseenter", evt => seatTip(evt, entry))
        .on("mousemove", moveTip)
        .on("mouseleave", hideTip)
        .on("click", () => {
          hideTip();
          window.location.hash = "/member/" + entry.member.id;
        });

      // mobile: short touch = tooltip, long press = navigate
      let pressTimer = null;
      let didLongPress = false;
      const node = g.node();
      node.addEventListener("touchstart", evt => {
        didLongPress = false;
        seatTip(evt, entry);
        pressTimer = setTimeout(() => {
          didLongPress = true;
          hideTip();
          window.location.hash = "/member/" + entry.member.id;
        }, 500);
      }, { passive: true });
      node.addEventListener("touchend", () => {
        clearTimeout(pressTimer);
        if (!didLongPress) setTimeout(hideTip, 1500);
      });
      node.addEventListener("touchmove", () => {
        clearTimeout(pressTimer);
      }, { passive: true });
    }

    positioned.forEach(s => drawSeat(s.x, s.y, s));

    mayors.forEach(m => {
      drawSeat(0, mayorY, m);
      svg.append("text")
        .attr("x", 0).attr("y", mayorY + r + 16)
        .attr("text-anchor", "middle").attr("font-size", 9)
        .attr("fill", "var(--text-muted)").text("BM");
    });
  }

  function arcPos(count, radius, start, end) {
    const positions = [];
    for (let i = 0; i < count; i++) {
      const angle = count === 1
        ? (start + end) / 2
        : start + (end - start) * i / (count - 1);
      positions.push({ x: Math.cos(angle) * radius, y: Math.sin(angle) * radius });
    }
    return positions;
  }

  return { drawBar, drawParliament };
})();
