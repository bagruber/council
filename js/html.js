// Markup bauen, ohne dass Daten zu Code werden.
//
// Die Views setzen ihre Ausgabe über innerHTML zusammen. Solange der Bestand
// aus eigenen JSON-Dateien kommt, ist das harmlos — ein Sitzungstitel mit
// einem spitzen Klammerzeichen gibt es dort nicht. Vor OParl und vor allem,
// was eine Verwaltung hochlädt, ist es das nicht mehr: dann steht fremder
// Text in der Seite, und ein <script> darin wäre ausführbar.
//
//   el.innerHTML = html`<h1>${titel}</h1>`;
//
// Eingesetzte Werte werden maskiert. Verschachtelte html``-Stücke und Listen
// davon kommen unverändert durch, denn sie sind schon fertiges Markup:
//
//   html`<ul>${zeilen.map(z => html`<li>${z.titel}</li>`)}</ul>`
//
// Wo wirklich eine Zeichenkette mit Markup eingesetzt werden soll, die nicht
// aus html`` kommt, sagt roh() das ausdrücklich — und macht es damit zu einer
// Stelle, die man beim Lesen sieht.

const ZEICHEN = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };

function maskieren(wert) {
  return String(wert).replace(/[&<>"']/g, z => ZEICHEN[z]);
}

// Fertiges Markup. Eine eigene Klasse, damit sich eine Zeichenkette aus den
// Daten nicht als Markup ausgeben kann.
class Markup {
  constructor(text) { this.text = text; }
  toString() { return this.text; }
}

const roh = text => new Markup(text);

function einsetzen(wert) {
  // null, undefined und false stehen für "nichts" — der haeufigste Fall bei
  // ${bedingung && html`…`}.
  if (wert === null || wert === undefined || wert === false || wert === true) return "";
  if (wert instanceof Markup) return wert.text;
  if (Array.isArray(wert)) return wert.map(einsetzen).join("");
  return maskieren(wert);
}

function html(teile, ...werte) {
  let aus = teile[0];
  for (let i = 0; i < werte.length; i++) aus += einsetzen(werte[i]) + teile[i + 1];
  return new Markup(aus);
}

export { html, roh, maskieren, Markup };
