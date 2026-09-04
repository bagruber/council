// Erzeugt css/tokens.css als Kopie des Gestaltungs-Kanons aus
// bagruber/moosburg-design (css/tokens.css, Geschwister-Checkout erwartet
// unter ../moosburg-design). Diese App hat keinen Build-Step, kann die Tokens
// also nicht als Dependency importieren; und die Domain-CSP erlaubt
// style-src 'self', ein Nachladen von GitHub Pages wäre still tot. Deshalb
// eine Kopie, aber eine erzeugte statt einer getippten.
//
// Idempotent: der Stand im Herkunftskopf ist das letzte Commit-Datum der
// Quelldatei, nicht das Laufdatum. Ein zweiter Lauf ändert nichts.
//
// Danach `python scripts/stamp_assets.py`, sonst liefert der Browser die alte
// Datei aus.
//
//   node scripts/hole-tokens.mjs

import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const WURZEL = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const DESIGN = path.resolve(WURZEL, "..", "moosburg-design");
const QUELLE = path.join(DESIGN, "css", "tokens.css");
const ZIEL = path.join(WURZEL, "css", "tokens.css");

if (!fs.existsSync(QUELLE)) {
  throw new Error("Quelle fehlt: " + QUELLE + " (moosburg-design danebenklonen)");
}

const stand = execFileSync(
  "git", ["-C", DESIGN, "log", "-1", "--format=%cs", "--", "css/tokens.css"],
  { encoding: "utf8" },
).trim();
if (!/^\d{4}-\d{2}-\d{2}$/.test(stand)) {
  throw new Error("Kein Commit-Datum für die Quelle gefunden: " + stand);
}

// Der Kopf der Quelle wiederholt sich sonst; er sagt dasselbe für das andere Repo.
const inhalt = fs.readFileSync(QUELLE, "utf8").replace(/^\/\*[\s\S]*?\*\/\s*/, "");

const kopf = `/* KOPIE, nicht von Hand ändern.
   Quelle:  bagruber/moosburg-design, css/tokens.css
   Stand:   ${stand}
   Erzeugt: node scripts/hole-tokens.mjs

   Änderungen am Kanon gehören in moosburg-design/css/theme.css, dort
   \`npm run tokens\`, dann hier das Skript laufen lassen. */

`;

const neu = kopf + inhalt;
const alt = fs.existsSync(ZIEL) ? fs.readFileSync(ZIEL, "utf8") : "";
if (alt === neu) {
  console.log("unverändert (Stand " + stand + ")");
} else {
  fs.writeFileSync(ZIEL, neu);
  console.log("css/tokens.css geschrieben, Stand " + stand);
}
