/* Formulaire « Envoyez-nous un message » : message de retour, contrôle de la pièce jointe. */
(function () {
  "use strict";
  const f = document.getElementById("formulaire");
  if (!f) return;
  f.elements.debut.value = Math.floor(Date.now() / 1000);       // un robot envoie en moins de 3 s
  const p = new URLSearchParams(location.search);
  if (p.get("envoye")) f.querySelector("[data-ok]").hidden = false;
  if (p.get("erreur")) {
    const e = f.querySelector(`[data-erreur="${CSS.escape(p.get("erreur"))}"]`);
    if (e) e.hidden = false;
  }
  const fichier = f.elements.piece;
  const nom = f.querySelector(".fichier em");
  fichier.addEventListener("change", () => {
    const x = fichier.files[0];
    nom.textContent = x ? x.name : nom.dataset.aucun;
    f.querySelectorAll("[data-erreur]").forEach((e) => { e.hidden = true; });
    if (x && x.size > 10 * 1024 * 1024) {
      f.querySelector('[data-erreur="taille"]').hidden = false;
      fichier.value = "";
      nom.textContent = nom.dataset.aucun;
    } else if (x && !/\.(pdf|docx?)$/i.test(x.name)) {
      f.querySelector('[data-erreur="format"]').hidden = false;
      fichier.value = "";
      nom.textContent = nom.dataset.aucun;
    }
  });
  f.addEventListener("submit", () => { f.querySelector("button[type=submit]").disabled = true; });
})();
