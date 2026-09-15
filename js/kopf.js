// Probe Formsprache, vorläufig (14.09.2026): „Über das Projekt“ im Kopf. Ab
// 1024 px ein Panel unter dem Knopf, darunter ein Blatt hinter dem
// Rosen-Knopf, das zusätzlich auf moosburg.eu führt. Ein Disclosure, kein
// Menü: aria-expanded an beiden Knöpfen, Esc und ein Klick außerhalb
// schließen, nach Esc kehrt der Fokus zum auslösenden Knopf zurück.

export function initKopf() {
  const bereich = document.querySelector("[data-ueber]");
  const panel = document.getElementById("ueber-panel");
  const knoepfe = bereich.querySelectorAll('[aria-controls="ueber-panel"]');
  let ausloeser = null;

  // Mobil liegt das Panel als Blatt unten; der Schleier dahinter schließt es.
  const schleier = document.createElement("div");
  schleier.className = "ueber-schleier";
  schleier.hidden = true;
  bereich.appendChild(schleier);

  function setze(offen) {
    panel.hidden = !offen;
    schleier.hidden = !offen;
    knoepfe.forEach(k => k.setAttribute("aria-expanded", String(offen)));
  }

  knoepfe.forEach(k => k.addEventListener("click", () => {
    ausloeser = k;
    setze(panel.hidden);
  }));

  document.addEventListener("keydown", e => {
    if (e.key !== "Escape" || panel.hidden) return;
    setze(false);
    if (ausloeser) ausloeser.focus();
  });

  document.addEventListener("mousedown", e => {
    if (panel.hidden) return;
    if (!bereich.contains(e.target) || e.target === schleier) setze(false);
  });

  // Jeder Eintrag führt woandershin (Seite, Modal, extern): das Panel geht zu.
  panel.addEventListener("click", e => {
    if (e.target.closest("a, button")) setze(false);
  });
}
