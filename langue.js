/* Choix de la langue : garde la recherche, le rayon ou le produit affiché (« ?id=… », « #recette »). */
(function () {
  "use strict";
  document.querySelectorAll("a[data-garder-recherche]").forEach((a) => {
    a.addEventListener("click", () => {
      a.href = a.href.split(/[?#]/)[0] + location.search + location.hash;
      try { localStorage.setItem("langue", a.hreflang); } catch (e) { /* stockage indisponible */ }
    });
  });
})();
