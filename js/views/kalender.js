// Kalender-Tab: Monatsraster mit Sitzungspunkten und Tages-Sheet.
import { sessions, sessionMap, naechsteSitzung, gremium } from "../daten.js";
import { formatDate, monthNames, sitzungKurz } from "../hilfen.js";

let calYear, calMonth;
const calTitle = document.getElementById("cal-title");
const calGrid = document.getElementById("cal-grid");
const calSheet = document.getElementById("cal-sheet");
const calSheetBody = document.getElementById("cal-sheet-body");

const sessionsByDate = {};

// Ehemals frei laufende Verdrahtung aus app.js, unverändert.
export function initKalender() {
  sessions.forEach(s => {
    if (!sessionsByDate[s.date]) sessionsByDate[s.date] = [];
    sessionsByDate[s.date].push(s);
  });

  const now = new Date();
  calYear = now.getFullYear();
  calMonth = now.getMonth();
  renderNaechsteSitzung();

  document.getElementById("cal-prev").addEventListener("click", () => {
    if (--calMonth < 0) { calMonth = 11; calYear--; }
    renderCalendar();
  });
  document.getElementById("cal-next").addEventListener("click", () => {
    if (++calMonth > 11) { calMonth = 0; calYear++; }
    renderCalendar();
  });

  let startX = 0;
  const pane = document.getElementById("tab-kalender");
  pane.addEventListener("touchstart", e => { startX = e.touches[0].clientX; }, { passive: true });
  pane.addEventListener("touchend", e => {
    const dx = e.changedTouches[0].clientX - startX;
    if (Math.abs(dx) < 60) return;
    if (dx < 0) { if (++calMonth > 11) { calMonth = 0; calYear++; } }
    else { if (--calMonth < 0) { calMonth = 11; calYear--; } }
    renderCalendar();
  });
}

function renderCalendar() {
  calTitle.textContent = monthNames[calMonth] + " " + calYear;
  calGrid.innerHTML = "";

  const first = new Date(calYear, calMonth, 1);
  const last = new Date(calYear, calMonth + 1, 0);
  const startDow = (first.getDay() + 6) % 7;

  const today = new Date();
  const todayStr = isoDate(today.getFullYear(), today.getMonth(), today.getDate());

  const prevLast = new Date(calYear, calMonth, 0);
  for (let i = startDow - 1; i >= 0; i--) {
    addDay(prevLast.getDate() - i, isoDate(calYear, calMonth - 1, prevLast.getDate() - i), true, todayStr);
  }

  for (let d = 1; d <= last.getDate(); d++) {
    addDay(d, isoDate(calYear, calMonth, d), false, todayStr);
  }

  const cells = calGrid.children.length;
  const pad = (7 - (cells % 7)) % 7;
  for (let d = 1; d <= pad; d++) {
    addDay(d, isoDate(calYear, calMonth + 1, d), true, todayStr);
  }
}

function isoDate(y, m, d) {
  const dt = new Date(y, m, d);
  return dt.getFullYear() + "-" +
    String(dt.getMonth() + 1).padStart(2, "0") + "-" +
    String(dt.getDate()).padStart(2, "0");
}

function addDay(num, dateStr, otherMonth, todayStr) {
  const cell = document.createElement("div");
  cell.className = "cal-day";
  if (otherMonth) cell.classList.add("other-month");
  if (dateStr === todayStr) cell.classList.add("today");

  const span = document.createElement("span");
  span.textContent = num;
  cell.appendChild(span);

  const events = sessionsByDate[dateStr];
  if (events) {
    const dots = document.createElement("div");
    dots.className = "cal-dots";
    events.forEach(s => {
      const dot = document.createElement("span");
      dot.className = "cal-dot " + (s.type || "stadtrat");
      dots.appendChild(dot);
    });
    cell.appendChild(dots);
    cell.addEventListener("click", () => openDaySheet(dateStr, events));
  }

  calGrid.appendChild(cell);
}

function openDaySheet(dateStr, events) {
  calSheetBody.innerHTML = "";

  const heading = document.createElement("div");
  heading.className = "sheet-date";
  heading.textContent = formatDate(dateStr);
  calSheetBody.appendChild(heading);

  events.forEach(s => {
    const row = document.createElement("a");
    row.className = "sheet-event";
    row.href = "#/session/" + s.id;
    // Probe Formsprache (15.09.2026): das Gremium als Kategoriezeile, darunter
    // nur Nummer und Datum, ohne den Gremiennamen ein zweites Mal.
    const g = gremium(s);
    row.dataset.gremium = g.art;
    row.innerHTML = `
      <div class="sheet-event-text">
        <span class="gremium-zeile"><svg class="icon" aria-hidden="true"><use href="#i-${g.icon}"/></svg>${g.name}</span>
        ${sitzungKurz(s)}, ${formatDate(s.date)}
      </div>
      <svg class="icon" aria-hidden="true"><use href="#i-chevron_right"/></svg>`;
    row.addEventListener("click", () => calSheet.classList.add("hidden"));
    calSheetBody.appendChild(row);
  });

  calSheet.classList.remove("hidden");
}

// Probe Formsprache, vorläufig (14.09.2026): Farbfläche „nächste Sitzung“ oben
// im Kalender. Ohne Termin ab heute gibt es keine Fläche; den Knopf zur
// Tagesordnung nur, wenn es die Sitzungsseite schon gibt.
function renderNaechsteSitzung() {
  const box = document.getElementById("naechste-sitzung");
  const t = naechsteSitzung();
  if (!t) { box.hidden = true; return; }
  box.dataset.gremium = gremium(t).art;
  const tag = new Date(t.date + "T00:00:00")
    .toLocaleDateString("de-DE", { weekday: "long", day: "numeric", month: "long" });
  const knopf = sessionMap[t.id]
    ? `<a class="flaeche-knopf" href="#/session/${t.id}">Tagesordnung<svg class="icon" aria-hidden="true"><use href="#i-chevron_right"/></svg></a>`
    : "";
  box.innerHTML = `
    <div class="flaeche-inhalt">
      <h2 class="flaeche-etikett" id="naechste-sitzung-titel">Nächste Sitzung</h2>
      <p class="flaeche-gross">${tag}</p>
      <p class="flaeche-text">${t.title}, ${t.time} Uhr<br>${t.location}</p>
      ${knopf}
    </div>`;
}

export { renderCalendar };
