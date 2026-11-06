/* Petits gestes communs à toutes les pages : en-tête qui se resserre au défilement, apparition douce des blocs,
   menu qui se referme après un clic, bouton « haut de page ». Sans ce script, tout reste visible et utilisable. */
(function () {
  "use strict";
  const doc = document.documentElement;
  const entete = document.querySelector(".entete");
  const haut = document.querySelector(".haut-de-page");
  const suivre = () => {
    const y = window.scrollY;
    if (entete) entete.classList.toggle("defile", y > 8);
    if (haut) haut.classList.toggle("visible", y > 900);
  };
  window.addEventListener("scroll", suivre, { passive: true });
  suivre();
  if (haut) haut.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

  const caseMenu = document.getElementById("menu-ouvert");
  document.querySelectorAll(".menu a").forEach((a) => a.addEventListener("click", () => { if (caseMenu) caseMenu.checked = false; }));
  if (caseMenu) caseMenu.addEventListener("change", () => doc.classList.toggle("menu-ouvert", caseMenu.checked));

  // Apparition des blocs (jamais si la personne préfère moins d'animations)
  if (!("IntersectionObserver" in window) || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const choix = ".tete-section, .tuiles > *, .plats > *, .etapes > li, .promesse, .affiches > *, .regions > *, " +
    ".atouts > *, .contact-carte, .nouveautes > *, .galerie > *, .histoire > *, .carriere > *, .form-grille > *, .visite-grille > *, .faq-grille > *, .avis > *, .appel-boite";
  const vus = new IntersectionObserver((entrees) => {
    entrees.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add("vu");
      vus.unobserve(e.target);
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
  document.querySelectorAll(choix).forEach((el) => {
    if (el.getBoundingClientRect().top < innerHeight) return;    // déjà à l'écran : rien à animer
    const rang = Array.prototype.indexOf.call(el.parentNode.children, el) % 6;
    el.style.setProperty("--retard", rang * 70 + "ms");
    el.classList.add("revele");
    vus.observe(el);
  });
})();
