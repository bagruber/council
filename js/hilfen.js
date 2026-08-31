// Format-Helfer für Daten und Zeiträume, von allen Views geteilt.

function formatDuration(min) {
  const h = Math.floor(min / 60), m = min % 60;
  if (!h) return m + " Min.";
  return m ? h + " Std. " + m + " Min." : h + " Std.";
}

function formatDate(iso) {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("de-DE", { day: "numeric", month: "long", year: "numeric" });
}

const monthNames = ["Januar", "Februar", "M\u00e4rz", "April", "Mai", "Juni",
  "Juli", "August", "September", "Oktober", "November", "Dezember"];

// Fraktionszugehörigkeit endet selten zum Jahreswechsel. "2014–2025" liest
// sich, als wäre Dollinger das ganze Jahr 2025 noch bei den FW gewesen —
// tatsächlich war im Januar Schluss.
const MON = ["", "Jan.", "Feb.", "März", "Apr.", "Mai", "Juni",
             "Juli", "Aug.", "Sep.", "Okt.", "Nov.", "Dez."];
function monthLabel(iso) {
  return MON[+iso.slice(5, 7)] + " " + iso.slice(0, 4);
}

function formatMonthPeriod(from, to) {
  if (!from) return to ? "bis " + monthLabel(to) : "";
  if (!to) return "seit " + monthLabel(from);
  return monthLabel(from) + " – " + monthLabel(to);
}

function formatPeriod(from, to) {
  const f = from ? from.substring(0, 4) : "";
  const t = to ? to.substring(0, 4) : "heute";
  return f + "\u2013" + t;
}

export { formatDuration, formatDate, monthNames, monthLabel, formatMonthPeriod, formatPeriod };
