// Kalender-Tab: Monatsraster mit Sitzungspunkten und Tages-Sheet.
import { sessions } from "../daten.js";
import { formatDate, monthNames } from "../hilfen.js";

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
    if (s.type && s.type !== "stadtrat") row.classList.add(s.type);
    const icon = s.type === "bpu" ? "engineering"
               : (s.type && s.type !== "stadtrat") ? "groups"
               : "account_balance";
    row.innerHTML = `
      <svg class="icon"><use href="#i-${icon}"/></svg>
      <div class="sheet-event-text">${s.title}</div>
      <svg class="icon"><use href="#i-chevron_right"/></svg>`;
    row.addEventListener("click", () => calSheet.classList.add("hidden"));
    calSheetBody.appendChild(row);
  });

  calSheet.classList.remove("hidden");
}

export { renderCalendar };
