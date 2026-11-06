/* Boutique du Marché Mvog-Mbi : catalogue lu dans data/produits.json (exporté de Clover). */
(function () {
  "use strict";
  const PAR_PAGE = 48;
  const argent = new Intl.NumberFormat("fr-CA", { style: "currency", currency: "CAD" });

  const echapper = (t) => String(t ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const normal = (t) => String(t || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const prix = (p) => argent.format(p.prix) + (p.unite ? " / " + p.unite : "");

  let catalogue = null;
  function charger() {
    if (!catalogue) {
      catalogue = fetch("data/produits.json", { cache: "no-cache" }).then((r) => {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      });
    }
    return catalogue;
  }

  const prixHtml = (p) => echapper(argent.format(p.prix)) + (p.unite ? ` <small>/ ${echapper(p.unite)}</small>` : "");
  const sansPhoto = (grand) => `<span class="sans-photo${grand ? " grand" : ""}" aria-hidden="true"><img src="images/icone.png" alt="" width="140" height="140"><em>Photo à venir</em></span>`;

  function vignette(p) {
    const image = p.photo
      ? `<img src="${echapper(p.photo)}" alt="" loading="lazy" width="240" height="240"${p.illustration ? ' class="illustration"' : ""}>`
      : sansPhoto(false);
    return `<a class="carte-produit" href="produit.html?id=${encodeURIComponent(p.id)}">
      <span class="carte-image">${image}</span>
      <span class="carte-corps">
        <span class="carte-rayon">${echapper(p.rayon)}</span>
        <span class="carte-nom">${echapper(p.nom)}</span>
        <span class="carte-prix">${prixHtml(p)}</span>
      </span>
    </a>`;
  }

  /* ---------- Accueil : produits vedettes ---------- */
  function vedettes() {
    const zone = document.getElementById("vedettes");
    charger().then((d) => {
      const avecPhoto = d.produits.filter((p) => p.photo && !p.illustration);
      const jour = Math.floor(Date.now() / 864e5);          // change chaque jour, pareil pour tous
      const choix = [];
      const vus = new Set();
      for (let i = 0; choix.length < 10 && i < avecPhoto.length * 2; i++) {
        const p = avecPhoto[(jour * 37 + i * 97) % avecPhoto.length];
        if (!vus.has(p.id)) { vus.add(p.id); choix.push(p); }
      }
      zone.innerHTML = choix.map(vignette).join("");
    }).catch(() => { zone.closest("section").hidden = true; });
  }

  /* ---------- Page Boutique ---------- */
  function boutique() {
    const zone = document.getElementById("produits");
    const compte = document.getElementById("compte");
    const plus = document.getElementById("plus");
    const recherche = document.getElementById("recherche");
    const tri = document.getElementById("tri");
    const avecPhoto = document.getElementById("avec-photo");
    const listeRayons = document.getElementById("rayons");
    const params = new URLSearchParams(location.search);
    let rayon = params.get("rayon") || "";
    recherche.value = params.get("q") || "";
    let montres = PAR_PAGE;
    let filtres = [];

    charger().then((d) => {
      d.produits.forEach((p) => { p._cle = normal(p.nom + " " + p.rayon + " " + Object.values(p.caracteristiques || {}).join(" ")); });
      const nb = {};
      d.produits.forEach((p) => { nb[p.rayon] = (nb[p.rayon] || 0) + 1; });
      listeRayons.innerHTML = `<li><button data-rayon="">Tous les produits <span>${d.produits.length}</span></button></li>` +
        d.rayons.map((r) => `<li><button data-rayon="${echapper(r)}">${echapper(r)} <span>${nb[r] || 0}</span></button></li>`).join("");

      function marquer() {
        listeRayons.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", b.dataset.rayon === rayon));
      }
      function adresse() {
        const p = new URLSearchParams();
        if (rayon) p.set("rayon", rayon);
        if (recherche.value.trim()) p.set("q", recherche.value.trim());
        history.replaceState(null, "", p.toString() ? "?" + p : location.pathname);
      }
      function calculer() {
        const mots = normal(recherche.value).split(/\s+/).filter(Boolean);
        filtres = d.produits.filter((p) => (!rayon || p.rayon === rayon)
          && (!avecPhoto.checked || p.photo)
          && mots.every((m) => p._cle.includes(m)));
        const t = tri.value;
        if (t === "nom") filtres.sort((a, b) => a.nom.localeCompare(b.nom, "fr"));
        else if (t === "prix") filtres.sort((a, b) => a.prix - b.prix);
        else if (t === "prix-") filtres.sort((a, b) => b.prix - a.prix);
        montres = PAR_PAGE;
        afficher();
      }
      function afficher() {
        const quoi = rayon || "Tous les produits";
        compte.textContent = filtres.length
          ? `${quoi} : ${filtres.length} produit${filtres.length > 1 ? "s" : ""}`
          : `${quoi} : aucun produit ne correspond à la recherche.`;
        zone.innerHTML = filtres.slice(0, montres).map(vignette).join("");
        plus.hidden = montres >= filtres.length;
      }

      listeRayons.addEventListener("click", (e) => {
        const b = e.target.closest("button");
        if (!b) return;
        rayon = b.dataset.rayon;
        marquer(); adresse(); calculer();
        window.scrollTo({ top: zone.getBoundingClientRect().top + scrollY - 160, behavior: "smooth" });
      });
      let attente;
      recherche.addEventListener("input", () => { clearTimeout(attente); attente = setTimeout(() => { adresse(); calculer(); }, 150); });
      tri.addEventListener("change", calculer);
      avecPhoto.addEventListener("change", calculer);
      plus.addEventListener("click", () => { montres += PAR_PAGE; afficher(); });
      marquer(); calculer();
    }).catch(() => {
      compte.textContent = "Le catalogue n'a pas pu être chargé. Appelez-nous au 819 239-9864.";
    });
  }

  /* ---------- Page Produit ---------- */
  function produit() {
    const id = new URLSearchParams(location.search).get("id");
    const fiche = document.getElementById("fiche");
    charger().then((d) => {
      const p = d.produits.find((x) => x.id === id);
      if (!p) {
        fiche.innerHTML = `<p>Ce produit n'est plus au catalogue. <a href="boutique.html">Voir tous les produits</a></p>`;
        return;
      }
      document.title = `${p.nom} – Marché Mvog-Mbi Sherbrooke`;
      document.getElementById("fil").innerHTML = `<a href="boutique.html">Boutique</a> › ` +
        `<a href="boutique.html?rayon=${encodeURIComponent(p.rayon)}">${echapper(p.rayon)}</a> › <span>${echapper(p.nom)}</span>`;
      const image = p.photo
        ? `<img src="${echapper(p.photo)}" alt="${echapper(p.nom)}" width="480" height="480"${p.illustration ? ' class="illustration"' : ""}>`
        : sansPhoto(true);
      const lignes = Object.entries(p.caracteristiques || {})
        .map(([k, v]) => `<tr><th scope="row">${echapper(k)}</th><td>${echapper(v)}</td></tr>`).join("");
      fiche.innerHTML = `
        <div class="fiche-image">${image}
          ${p.photo_source ? `<p class="source">${p.illustration ? "Photo d’illustration" : "Photo"} : ${p.photo_lien ? `<a href="${echapper(p.photo_lien)}" rel="noopener" target="_blank">${echapper(p.photo_source)}</a>` : echapper(p.photo_source)}</p>` : ""}</div>
        <div class="fiche-texte">
          <p class="surtitre">${echapper(p.rayon)}</p>
          <h1>${echapper(p.nom)}</h1>
          <p class="fiche-prix">${prixHtml(p)}</p>
          ${p.unite ? `<p class="note">Vendu au poids : le prix final dépend de la quantité pesée en magasin.</p>` : ""}
          ${p.description ? `<p class="fiche-description">${echapper(p.description)}</p>` : ""}
          ${lignes ? `<h2>Caractéristiques</h2><table class="caracteristiques"><tbody>${lignes}</tbody></table>` : ""}
          <div class="dispo">
            <strong>En vente au magasin</strong>
            <span>3071 boulevard Portland, Sherbrooke. Disponibilité selon les arrivages.</span>
            <a class="bouton" href="tel:+18192399864">Vérifier la disponibilité : 819 239-9864</a>
          </div>
        </div>`;
      const voisins = d.produits.filter((x) => x.rayon === p.rayon && x.id !== p.id)
        .sort((a, b) => (b.photo ? 1 : 0) - (a.photo ? 1 : 0)).slice(0, 8);
      if (voisins.length) {
        document.getElementById("voisins-titre").textContent = `Aussi dans « ${p.rayon} »`;
        document.getElementById("voisins").innerHTML = voisins.map(vignette).join("");
      }
    }).catch(() => {
      fiche.innerHTML = "<p>Le catalogue n'a pas pu être chargé. Appelez-nous au 819 239-9864.</p>";
    });
  }

  if (document.getElementById("produits") && document.getElementById("recherche")) boutique();
  if (document.getElementById("fiche")) produit();
  if (document.getElementById("vedettes")) vedettes();
})();
