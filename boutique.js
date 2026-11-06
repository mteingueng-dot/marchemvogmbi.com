/* Boutique du Marché Mvog-Mbi : catalogue lu dans data/produits.json (exporté de Clover).
   Règle du propriétaire : aucun prix sur le site. Langue de la page : <html lang="fr-CA"> ou "en-CA". */
(function () {
  "use strict";
  const PAR_PAGE = 48;
  const EN = (document.documentElement.lang || "fr").startsWith("en");
  const RACINE = EN ? "../" : "";                      // les pages anglaises sont dans /en/
  const T = EN ? {
    tous: "All products", aucun: "no product matches your search.", produit: "product", produits: "products",
    format: "size", formats: "sizes", couleurs: "colours", couleur: "colour", aVenir: "Photo coming soon",
    introuvable: "This product is no longer listed.", voirTout: "See all products",
    erreur: "The catalogue could not be loaded. Call us at 819 239-9864.",
    carac: "Details", conditionnements: "Available sizes", couleursDispo: "Available colours", recettes: "Recipe ideas",
    aussi: (r) => `Also in “${r}”`, boutique: "Shop", photo: "Photo", illustration: "Illustration photo",
    poids: "Sold by weight: weighed in store to the quantity you want.",
    enVente: "Available in store", magasin: "3071 boulevard Portland, Sherbrooke. Availability depends on arrivals.",
    appeler: "Check availability: 819 239-9864", voirRecette: "See the recipe", deuxPoints: ": ",
  } : {
    tous: "Tous les produits", aucun: "aucun produit ne correspond à la recherche.", produit: "produit", produits: "produits",
    format: "format", formats: "formats", couleurs: "couleurs", couleur: "couleur", aVenir: "Photo à venir",
    introuvable: "Ce produit n’est plus au catalogue.", voirTout: "Voir tous les produits",
    erreur: "Le catalogue n’a pas pu être chargé. Appelez-nous au 819 239-9864.",
    carac: "Caractéristiques", conditionnements: "Conditionnements disponibles", couleursDispo: "Couleurs disponibles",
    recettes: "Idées recettes", aussi: (r) => `Aussi dans « ${r} »`, boutique: "Boutique", photo: "Photo",
    illustration: "Photo d’illustration", poids: "Vendu au poids : pesé en magasin selon la quantité voulue.",
    enVente: "En vente au magasin", magasin: "3071 boulevard Portland, Sherbrooke. Disponibilité selon les arrivages.",
    appeler: "Vérifier la disponibilité : 819 239-9864", voirRecette: "Voir la recette", deuxPoints: " : ",
  };

  const echapper = (t) => String(t ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const mots_de = (t) => normal(t).replace(/[^a-z0-9]+/g, " ").trim();   // début de mot : « gari » ne trouve pas « bulgarie »
  const normal = (t) => String(t || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  const champ = (p, nom) => (EN && p[nom + "_en"]) || p[nom];          // texte anglais s'il existe
  const rayonDe = (p) => champ(p, "rayon");
  const chemin = (f) => (f && !/^https?:/.test(f) ? RACINE + f : f);
  const sansPhoto = (grand) => `<span class="sans-photo${grand ? " grand" : ""}" aria-hidden="true"><img src="${RACINE}images/icone.png" alt="" width="140" height="140"><em>${T.aVenir}</em></span>`;
  const pluriel = (n, un, plusieurs) => `${n} ${n > 1 ? plusieurs : un}`;

  // Photo qui ne se charge pas : la vignette « Photo à venir » prend sa place
  document.addEventListener("error", (e) => {
    const img = e.target;
    if (img.tagName === "IMG" && img.closest(".carte-image, .fiche-image")) img.outerHTML = sansPhoto(!!img.closest(".fiche-image"));
  }, true);

  let catalogue = null;
  function charger() {
    if (!catalogue) {
      catalogue = fetch(RACINE + "data/produits.json", { cache: "no-cache" }).then((r) => {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      });
    }
    return catalogue;
  }

  function details(p) {
    if (p.couleurs && p.couleurs.length > 1) return pluriel(p.couleurs.length, T.couleur, T.couleurs);
    if (p.conditionnements) return pluriel(p.conditionnements.length, T.format, T.formats);
    return "";
  }

  function vignette(p) {
    const image = p.photo
      ? `<img src="${echapper(chemin(p.photo))}" alt="" loading="lazy" width="240" height="240"${p.illustration ? ' class="illustration"' : ""}>`
      : sansPhoto(false);
    const d = details(p);
    return `<a class="carte-produit" href="produit.html?id=${encodeURIComponent(p.id)}">
      <span class="carte-image">${image}</span>
      <span class="carte-corps">
        <span class="carte-rayon">${echapper(rayonDe(p))}</span>
        <span class="carte-nom">${echapper(p.nom)}</span>
        ${d ? `<span class="carte-details">${echapper(d)}</span>` : ""}
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
      const rayons = d.rayons.map((r, i) => ({ fr: r, nom: EN && d.rayons_en ? d.rayons_en[i] : r }));
      d.produits.forEach((p) => {
        const couleurs = (p.couleurs || []).map((c) => [c.code, c.description, c.description_en].join(" ")).join(" ");
        p._cle = " " + mots_de([p.nom, p.rayon, p.rayon_en, p.description, p.description_en, couleurs,
          (p.conditionnements || []).join(" "), Object.values(p.caracteristiques || {}).join(" ")].join(" "));
        p._nom = " " + mots_de(p.nom);
      });
      const nb = {};
      d.produits.forEach((p) => { nb[p.rayon] = (nb[p.rayon] || 0) + 1; });
      listeRayons.innerHTML = `<li><button data-rayon="">${T.tous} <span>${d.produits.length}</span></button></li>` +
        rayons.map((r) => `<li><button data-rayon="${echapper(r.fr)}">${echapper(r.nom)} <span>${nb[r.fr] || 0}</span></button></li>`).join("");

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
        const mots = mots_de(recherche.value).split(" ").filter(Boolean);
        filtres = d.produits.filter((p) => (!rayon || p.rayon === rayon)
          && (!avecPhoto.checked || p.photo)
          && mots.every((m) => p._cle.includes(" " + m)));
        if (mots.length) {                    // le nom qui correspond passe avant la description
          const dansNom = (x) => (mots.every((m) => x._nom.includes(" " + m)) ? 0 : 1);
          filtres.sort((a, b) => dansNom(a) - dansNom(b));
        }
        if (tri.value === "nom") filtres.sort((a, b) => a.nom.localeCompare(b.nom, EN ? "en" : "fr"));
        else if (tri.value === "photo") {
          const note = (x) => (x.photo && !x.illustration ? 2 : x.photo ? 1 : 0);
          filtres.sort((a, b) => note(b) - note(a));
        }
        montres = PAR_PAGE;
        afficher();
      }
      function afficher() {
        const r = rayons.find((x) => x.fr === rayon);
        const quoi = r ? r.nom : T.tous;
        compte.textContent = filtres.length
          ? `${quoi}${T.deuxPoints}${pluriel(filtres.length, T.produit, T.produits)}`
          : `${quoi}${T.deuxPoints}${T.aucun}`;
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
    }).catch(() => { compte.textContent = T.erreur; });
  }

  /* ---------- Page Produit ---------- */
  function produit() {
    const id = new URLSearchParams(location.search).get("id");
    const fiche = document.getElementById("fiche");
    const lesRecettes = fetch(RACINE + "data/recettes.json").then((r) => r.json()).catch(() => []);
    Promise.all([charger(), lesRecettes]).then(([d, recettes]) => {
      const p = d.produits.find((x) => x.id === id || (x.ids || []).includes(id));
      if (!p) {
        fiche.innerHTML = `<p>${T.introuvable} <a href="boutique.html">${T.voirTout}</a></p>`;
        return;
      }
      const rayon = rayonDe(p);
      document.title = `${p.nom} – Marché Mvog-Mbi Sherbrooke`;
      document.getElementById("fil").innerHTML = `<a href="boutique.html">${T.boutique}</a> › ` +
        `<a href="boutique.html?rayon=${encodeURIComponent(p.rayon)}">${echapper(rayon)}</a> › <span>${echapper(p.nom)}</span>`;
      const image = p.photo
        ? `<img src="${echapper(chemin(p.photo))}" alt="${echapper(p.nom)}" width="480" height="480"${p.illustration ? ' class="illustration"' : ""}>`
        : sansPhoto(true);
      const carac = (EN && p.caracteristiques_en) || p.caracteristiques || {};
      const lignes = Object.entries(carac)
        .filter(([k]) => !/^(Conditionnements|Couleurs|Available)/.test(k))
        .map(([k, v]) => `<tr><th scope="row">${echapper(k)}</th><td>${echapper(v)}</td></tr>`).join("");
      const formats = p.conditionnements
        ? `<h2>${T.conditionnements}</h2><ul class="pastilles">${p.conditionnements.map((f) => `<li>${echapper(f)}</li>`).join("")}</ul>` : "";
      const couleurs = p.couleurs
        ? `<h2>${T.couleursDispo}</h2><ul class="couleurs">${p.couleurs.map((c) => {
            const desc = (EN && c.description_en) || c.description;
            return `<li><strong>${echapper(c.code)}</strong>${desc ? `<span>${echapper(desc)}</span>` : ""}</li>`;
          }).join("")}</ul>` : "";
      const liees = recettes.filter((r) => (p.recettes || []).includes(r.id));
      const blocRecettes = liees.length
        ? `<h2>${T.recettes}</h2><div class="recettes-liees">${liees.map((r) =>
            `<a href="recette-${r.id}.html"><strong>${echapper((EN && r.titre_en) || r.titre)}</strong><span>${echapper((EN && r.pays_en) || r.pays)} · ${T.voirRecette} →</span></a>`).join("")}</div>` : "";
      const source = p.photo_source
        ? `<p class="source">${p.illustration ? T.illustration : T.photo}${T.deuxPoints}${p.photo_lien ? `<a href="${echapper(p.photo_lien)}" rel="noopener" target="_blank">${echapper(p.photo_source)}</a>` : echapper(p.photo_source)}</p>` : "";
      fiche.innerHTML = `
        <div class="fiche-image">${image}${source}</div>
        <div class="fiche-texte">
          <p class="surtitre">${echapper(rayon)}</p>
          <h1>${echapper(p.nom)}</h1>
          <p class="fiche-description">${echapper(champ(p, "description"))}</p>
          ${p.unite ? `<p class="note">${T.poids}</p>` : ""}
          ${formats}${couleurs}
          ${lignes ? `<h2>${T.carac}</h2><table class="caracteristiques"><tbody>${lignes}</tbody></table>` : ""}
          ${blocRecettes}
          <div class="dispo">
            <strong>${T.enVente}</strong>
            <span>${T.magasin}</span>
            <a class="bouton" href="tel:+18192399864">${T.appeler}</a>
          </div>
        </div>`;
      const note = (x) => (x.photo && !x.illustration ? 2 : x.photo ? 1 : 0);
      const voisins = d.produits.filter((x) => x.rayon === p.rayon && x.id !== p.id)
        .sort((a, b) => note(b) - note(a)).slice(0, 10);
      if (voisins.length) {
        document.getElementById("voisins-titre").textContent = T.aussi(rayon);
        document.getElementById("voisins").innerHTML = voisins.map(vignette).join("");
      }
    }).catch(() => { fiche.innerHTML = `<p>${T.erreur}</p>`; });
  }

  if (document.getElementById("produits") && document.getElementById("recherche")) boutique();
  if (document.getElementById("fiche")) produit();
  if (document.getElementById("vedettes")) vedettes();
})();
