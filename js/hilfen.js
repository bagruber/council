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

// Probe Formsprache, vorläufig (14.09.2026): Töne einer Themenfarbe aus
// tags.json. Als Text sind die Farben zu hell, deshalb ein dunkler Ton für
// Icon und Name und ein heller für die Fläche des Kleckses, nach der Formel
// aus dem Haushalt. Reicht der dunkle Ton auf Creme nicht für 4,5:1 (Wirtschaft),
// wird weiter abgedunkelt. Gerechnet wird hier, nicht im Datenbestand.
function mischen(hex, ziel, t) {
  return "#" + [1, 3, 5].map(i => {
    const v = parseInt(hex.slice(i, i + 2), 16);
    return Math.round(v + (ziel - v) * t).toString(16).padStart(2, "0");
  }).join("");
}

function luminanz(hex) {
  const [r, g, b] = [1, 3, 5].map(i => {
    const c = parseInt(hex.slice(i, i + 2), 16) / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function kategorieTon(farbe) {
  const creme = luminanz("#faf7f2");
  let t = 0.35, text = mischen(farbe, 0, t);
  while ((creme + 0.05) / (luminanz(text) + 0.05) < 4.5 && t < 0.9) {
    t += 0.05;
    text = mischen(farbe, 0, t);
  }
  // tief: Band im Kopf des Themenfelds (15.09.2026), Creme darauf mindestens 8,4:1
  return { text, flaeche: mischen(farbe, 255, 0.78), tief: mischen(farbe, 0, 0.6) };
}

// Probe Formsprache (15.09.2026): Steht das Gremium schon als Kategoriezeile
// darüber, reicht vom Titel die Nummer. „12. Stadtratssitzung – September 2026“
// wird „12. Sitzung“; ein Zusatz in Klammern bleibt stehen.
function sitzungKurz(s) {
  const nr = s.title.match(/^(\d+)\./);
  const zusatz = s.title.match(/\(([^)]+)\)\s*$/);
  return (nr ? nr[1] + ". Sitzung" : "Sitzung") + (zusatz ? " (" + zusatz[1] + ")" : "");
}

export { formatDuration, formatDate, monthNames, monthLabel, formatMonthPeriod, formatPeriod, kategorieTon, sitzungKurz };
