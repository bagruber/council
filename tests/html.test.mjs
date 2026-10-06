// Prüft js/html.js: was maskiert wird und was durchkommt.

import { test } from "node:test";
import assert from "node:assert/strict";
import { html, roh, maskieren } from "../js/html.js";

test("Eingesetzte Werte werden maskiert", () => {
  const titel = 'Plan "A" & <script>alert(1)</script>';
  assert.equal(String(html`<h1>${titel}</h1>`),
    "<h1>Plan &quot;A&quot; &amp; &lt;script&gt;alert(1)&lt;/script&gt;</h1>");
});

test("Das Gerüst selbst bleibt unangetastet", () => {
  assert.equal(String(html`<a href="#/x">y</a>`), '<a href="#/x">y</a>');
});

test("Verschachteltes html`` ist schon fertiges Markup", () => {
  const zeile = t => html`<li>${t}</li>`;
  assert.equal(String(html`<ul>${zeile("a<b")}</ul>`), "<ul><li>a&lt;b</li></ul>");
});

test("Listen werden zusammengefügt, nicht mit Komma", () => {
  assert.equal(String(html`<ul>${[1, 2, 3].map(n => html`<li>${n}</li>`)}</ul>`),
    "<ul><li>1</li><li>2</li><li>3</li></ul>");
});

test("Nichts heißt nichts", () => {
  assert.equal(String(html`<p>${null}${undefined}${false}${""}</p>`), "<p></p>");
  assert.equal(String(html`<p>${0}</p>`), "<p>0</p>", "die Null ist ein Wert");
});

test("roh() setzt Markup ein, das nicht aus html`` kommt", () => {
  assert.equal(String(html`<p>${roh("<b>x</b>")}</p>`), "<p><b>x</b></p>");
});

test("Eine Zeichenkette aus den Daten kann sich nicht als Markup ausgeben", () => {
  const boese = { toString: () => "<b>nein</b>" };
  assert.equal(String(html`<p>${boese}</p>`), "<p>&lt;b&gt;nein&lt;/b&gt;</p>");
});

test("maskieren deckt die fünf Zeichen ab", () => {
  assert.equal(maskieren(`&<>"'`), "&amp;&lt;&gt;&quot;&#39;");
});
