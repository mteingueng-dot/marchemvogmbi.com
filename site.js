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

/* Recettes : bouton retour (revient à la liste là où on l'avait laissée) et anciens liens « recettes.html#id » */
(function () {
  "use strict";
  document.querySelectorAll("[data-retour]").forEach((a) => a.addEventListener("click", (e) => {
    try {
      if (sessionStorage.getItem("depuis-recettes") === location.pathname && history.length > 1) {
        sessionStorage.removeItem("depuis-recettes");
        e.preventDefault();
        history.back();
      }
    } catch (_) { /* lien normal */ }
  }));
  if (/\/recettes\.html$/.test(location.pathname)) {      // clic sur une recette : le retour revient ici
    document.querySelectorAll("a.tuile[href^='recette-']").forEach((a) => a.addEventListener("click", () => {
      try { sessionStorage.setItem("depuis-recettes", new URL(a.href).pathname); } catch (_) { /* rien */ }
    }));
  }
  if (/\/recettes\.html$/.test(location.pathname) && /^#[a-z0-9-]+$/.test(location.hash)
      && document.querySelector(`a.tuile[href="recette-${location.hash.slice(1)}.html"]`)) {
    location.replace(`recette-${location.hash.slice(1)}.html`);
  }
})();

/* Choix de la langue : la liste se referme d'un clic ailleurs ou avec Échap */
(function () {
  "use strict";
  const d = document.querySelector("details.langues");
  if (!d) return;
  document.addEventListener("click", (e) => { if (d.open && !d.contains(e.target)) d.open = false; });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") d.open = false; });
})();
