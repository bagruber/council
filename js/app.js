// Einstieg: Daten laden, Einstellungen und Verdrahtung, dann den Router
// starten. Der Schnitt in Module: daten.js hält den Bestand, routing.js
// verteilt, suche.js sucht, views/ rendert — siehe docs/MODULE.md.

import { ladeDaten } from "./daten.js";
import { initRouting, route } from "./routing.js";
import { initSuche } from "./suche.js";
import { initStatistik } from "./views/statistik.js";
import { initKalender } from "./views/kalender.js";
import { initNaehe } from "./views/naehe.js";

// Overlays: Impressum, Kontakt, Legende, Kalenderblatt. Früher hingen die
// Handler als onclick im HTML — die Content-Security-Policy von moosburg.eu
// erlaubt kein inline-Skript, und damit ging kein Overlay mehr zu. Ein
// delegierter Listener kommt ohne aus und deckt auch später eingefügte
// Knöpfe ab. Läuft vor dem Laden der Daten, damit Impressum und Kontakt
// auch dann erreichbar bleiben, wenn der Bestand nicht kommt.
document.addEventListener("click", evt => {
  const oeffner = evt.target.closest("[data-modal]");
  if (oeffner) {
    document.getElementById(oeffner.dataset.modal).classList.remove("hidden");
    return;
  }
  const schliessen = evt.target.closest(".modal-close");
  if (schliessen) {
    schliessen.closest(".modal-overlay, .bottom-sheet").classList.add("hidden");
    return;
  }
  // Klick auf den Schleier selbst, nicht auf den Inhalt darin
  if (evt.target.matches(".modal-overlay, .bottom-sheet")) {
    evt.target.classList.add("hidden");
  }
});

(async function () {
  const main = document.getElementById("main");

  try {
    await ladeDaten();
  } catch (err) {
    main.innerHTML = `<p style="color:var(--no);padding:40px 0">Daten konnten nicht geladen werden. Bitte mit einem lokalen Webserver \u00f6ffnen (z.B. <code>npx serve</code>).</p>`;
    console.error("Datenfehler:", err);
    return;
  }

  // -- Settings --

  const largeFontsToggle = document.getElementById("setting-large-fonts");
  const colorblindToggle = document.getElementById("setting-colorblind");

  function applySetting(key, cls, toggle) {
    const val = localStorage.getItem(key) === "1";
    toggle.checked = val;
    document.documentElement.classList.toggle(cls, val);
  }

  applySetting("largeFonts", "large-fonts", largeFontsToggle);
  applySetting("colorblind", "colorblind", colorblindToggle);

  largeFontsToggle.addEventListener("change", () => {
    localStorage.setItem("largeFonts", largeFontsToggle.checked ? "1" : "0");
    document.documentElement.classList.toggle("large-fonts", largeFontsToggle.checked);
  });

  colorblindToggle.addEventListener("change", () => {
    localStorage.setItem("colorblind", colorblindToggle.checked ? "1" : "0");
    document.documentElement.classList.toggle("colorblind", colorblindToggle.checked);
  });

  initRouting();
  initSuche();
  initStatistik();
  initKalender();
  initNaehe();

  route();
})();
