// Der Abstimmungsblock: Ergebnisbalken bzw. Halbrund (VoteVis aus
// parliament.js), Status-Pille und Quellenangabe. Wird von Dossier- und
// Sitzungsseiten eingebettet.
import {
  members, parties, seatOrder, sessionMap, bodyMap, pressMap, mediaMap,
  bodyIdForSession,
} from "../daten.js";

// -- Vote block --

function bodyForVote(vote) {
  const bid = bodyIdForSession(sessionMap[vote.sessionId]);
  return bid ? bodyMap[bid] : null;
}

// Woher die Einzelstimmen stammen. Vier Stufen, absteigend belastbar —
// bewusst eine ruhige Fußzeile, kein Siegel: die Herkunft qualifiziert das
// Ergebnis, sie ist nicht die Nachricht.
function renderVoteSource(vote) {
  const label = Council.sourceLabel(vote);
  if (!label) {
    return vote.type === "anonymous" && vote.results.yes && vote.results.no
      ? `<div class="vote-source">Nur das Ergebnis ist überliefert, nicht wer wie gestimmt hat.</div>`
      : "";
  }
  const parts = [label];
  // Wer mitschreibt, sitzt nicht zwangsläufig im Rat: Presseleute haben
  // keine Mitglieds-ID. Für sie trägt source.byName den Namen — sonst
  // stünde „mitgeschrieben“ da, ohne zu sagen von wem, und das ist der
  // halbe Wert der Angabe.
  const m = vote.source.by && members.find(x => x.id === vote.source.by);
  if (m) parts.push(`${m.firstName.charAt(0)}. ${m.lastName}`);
  else if (vote.source.byName) parts.push(vote.source.byName);
  let html = parts.join(" · ");
  // Bei Stufe "press" ist der Artikel die Quelle, nicht die Bestätigung. Wo er
  // zu einer eigenen Erfassung dazukommt, deckt er in aller Regel nur einen
  // Teil der Stimmen ab — "bestätigt" allein verspräche zu viel.
  const confirm = vote.source.tier === "press" ? "zum Artikel"
    : vote.source.pressScope === "full" ? "durch Presse bestätigt"
    : "teilweise durch Presse bestätigt";
  // Eine Abstimmung kann auf mehreren Artikeln ruhen — dann bekommt jeder
  // seinen eigenen Link, mit dem Medium als Beschriftung.
  const ids = [].concat(vote.source.pressId || []);
  const arts = ids.map(id => pressMap[id]).filter(Boolean);
  if (arts.length === 1) {
    html += ` · <a href="${arts[0].url}" target="_blank" rel="noopener">${confirm}</a>`;
  } else if (arts.length > 1) {
    html += " · " + confirm + ": " + arts.map(a =>
      `<a href="${a.url}" target="_blank" rel="noopener">${
        (mediaMap[a.media] || {}).name || a.media}</a>`).join(", ");
  } else if (vote.source.pressVerified) {
    html += " · " + confirm;
  }
  return `<div class="vote-source">${html}</div>`;
}

function renderVoteBlock(container, vote) {
  const block = document.createElement("div");
  block.className = "vote-block";

  // Status-Pille: angenommen / abgelehnt / vertagt / zurückgezogen.
  // Bei Anträgen subtiler, weil der Titel das Antrags-Kontext schon transportiert
  // (und der Antrag perspektivisch verlinkt wird).
  const STATUS = {
    rejected:  { cls: "rejected",  text: "Abgelehnt"     },
    deferred:  { cls: "deferred",  text: "Vertagt"       },
    withdrawn: { cls: "withdrawn", text: "Zurückgezogen" },
  };
  const st = STATUS[vote.result] || { cls: "approved", text: "Angenommen" };
  const isAntrag = /\bAntrag\b|\bAnträge\b/i.test(vote.title);
  const resultTag = `<span class="vote-result-tag ${st.cls}${isAntrag ? " subtle" : ""}">${st.text}</span>`;

  block.innerHTML = `
    <button class="vote-help-btn" aria-label="Legende" title="Was bedeutet was?">
      <svg class="icon"><use href="#i-help_outline"/></svg>
    </button>
    <h4>${vote.title}${resultTag}</h4>
    <div class="vote-text">${vote.text}</div>
    ${vote.note ? `<p class="vote-note">${vote.note}</p>` : ""}
    <div class="vote-legend">
      <span><span class="legend-dot yes"></span> Ja</span>
      <span><span class="legend-dot no"></span> Nein</span>
      <span><span class="legend-dot absent"></span> Abwesend</span>
    </div>
    ${renderVoteSource(vote)}`;

  block.querySelector(".vote-help-btn").addEventListener("click", () => {
    document.getElementById("vote-legend-modal").classList.remove("hidden");
  });

  const chartEl = document.createElement("div");
  block.appendChild(chartEl);
  container.appendChild(block);

  const hasIndividualData = vote.type === "named"
                          || (vote.voters && Object.keys(vote.voters).length > 0);

  // Einstimmig heißt: das Halbrund sagt nichts, was der Balken nicht schon
  // sagt. Es bleibt eingeklappt — außer jemand war befangen oder enthalten,
  // denn dann steht im Halbrund etwas, das die Zahlen nicht zeigen.
  const quiet = hasIndividualData && Council.isUnanimous(vote)
                && !(vote.excluded || []).length;

  // Der Balken und das Halbrund bekommen eigene Flächen. Vorher teilten sie
  // sich eine, und das Ausklappen hat den Balken überschrieben.
  const seatEl = quiet ? document.createElement("div") : chartEl;

  // drawBar rechnet mit Zahlen, benannte Voten führen Listen
  const counts = vote.type === "named"
    ? { yes: vote.results.yes.length, no: vote.results.no.length,
        absent: vote.results.absent.length }
    : vote.results;

  requestAnimationFrame(() => {
    if (!hasIndividualData || quiet) VoteVis.drawBar(chartEl, counts);
    else {
      const body = bodyForVote(vote);
      VoteVis.drawParliament(chartEl, vote, members, parties, seatOrder,
                             { body, session: sessionMap[vote.sessionId] });
    }
  });

  if (quiet) {
    const toggle = document.createElement("button");
    toggle.className = "vote-expand";
    toggle.textContent = "Einzelstimmen";
    let drawn = false;
    toggle.addEventListener("click", () => {
      seatEl.hidden = !seatEl.hidden;
      toggle.classList.toggle("open", !seatEl.hidden);
      if (!seatEl.hidden && !drawn) {
        drawn = true;
        const body = bodyForVote(vote);
        VoteVis.drawParliament(seatEl, vote, members, parties, seatOrder,
                               { body, bar: false, session: sessionMap[vote.sessionId] });
      }
    });
    // Der Knopf steht zwischen Balken und Halbrund, damit er beim Auf- und
    // Zuklappen nicht unter dem Finger wegwandert.
    seatEl.hidden = true;
    block.appendChild(toggle);
    block.appendChild(seatEl);
  }
}

export { renderVoteBlock };
