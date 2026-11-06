/* Assistant du Marché Mvog-Mbi : petite fenêtre de discussion qui répond tout de suite, sans service externe.
   Réponses écrites d'avance (heures, adresse, livraison, garantie du prix, paiement, emploi, contact…),
   recherche dans le catalogue (data/produits.json) et dans les recettes (data/recettes.json).
   Aucun prix n'est donné (règle du propriétaire) ; rien n'est envoyé ailleurs. */
(function () {
  "use strict";
  const EN = (document.documentElement.lang || "fr").startsWith("en");
  const RACINE = EN ? "../" : "";
  const TEL = '<a href="tel:+18192399864">819 239-9864</a>';
  const COURRIEL = '<a href="mailto:contact@marchemvogmbi.com">contact@marchemvogmbi.com</a>';
  const CARTE = "https://www.google.com/maps/dir/?api=1&destination=3071+boulevard+Portland+Sherbrooke+QC+J1L+2Y7";

  const echapper = (t) => String(t ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const normal = (t) => String(t || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const mots_de = (t) => normal(t).replace(/[^a-z0-9]+/g, " ").trim();

  /* Ouvert maintenant ? (heure de Sherbrooke, 9 h à 21 h tous les jours) */
  function etatOuverture() {
    let h = new Date().getHours(), m = new Date().getMinutes();
    try {
      const p = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Toronto", hour: "numeric", minute: "numeric", hourCycle: "h23" })
        .formatToParts(new Date());
      h = +p.find((x) => x.type === "hour").value; m = +p.find((x) => x.type === "minute").value;
    } catch (e) { /* fuseau inconnu : heure du poste */ }
    const ouvert = h >= 9 && h < 21;
    if (EN) return ouvert ? `We are <strong>open right now</strong>, until 9 p.m.` : `We are <strong>closed right now</strong>. We open at 9 a.m.`;
    return ouvert ? `Nous sommes <strong>ouverts en ce moment</strong>, jusqu’à 21 h.` : `Nous sommes <strong>fermés en ce moment</strong>. Nous ouvrons à 9 h.`;
  }

  const T = EN ? {
    titre: "Mvog-Mbi assistant", sous: "Replies instantly", ouvrir: "Questions? Chat with us", fermer: "Close the chat",
    place: "Type your question…", envoyer: "Send", vider: "New conversation",
    bonjour: "Hello! 👋 I’m the Marché Mvog-Mbi assistant. Ask me about a product, our hours, delivery or a recipe.",
    rapides: { heures: "Hours", adresse: "Address", livraison: "Delivery", prix: "Best price", produit: "Find a product", recettes: "Recipes", humain: "Talk to someone" },
    produitQ: "Sure! Type the name of a product: <em>plantain, gari, attiéké, palm oil, braids…</em>",
    trouve: (n, q) => `Here is what I found for “${q}”${n > 5 ? ` (${n} products)` : ""}:`,
    tousResultats: "See all results in the shop →", rien: (q) => `I can’t find “${q}” in our online catalogue. It may still be in store: call us at ${TEL} and we will check right away.`,
    pasCompris: `I’m not sure I understood. You can ask about our <strong>hours</strong>, <strong>delivery</strong>, a <strong>product</strong> or a <strong>recipe</strong>, or reach the team at ${TEL}.`,
    ingredients: "Ingredients available at the store:", voirRecette: "See the full recipe →", recettesListe: "Our step-by-step recipes:",
    prixAbsent: "Prices are shown in store only.", dispo: "Availability changes with arrivals:",
  } : {
    titre: "Assistant Mvog-Mbi", sous: "Répond tout de suite", ouvrir: "Une question ? Discutons", fermer: "Fermer la discussion",
    place: "Écrivez votre question…", envoyer: "Envoyer", vider: "Nouvelle discussion",
    bonjour: "Bonjour ! 👋 Je suis l’assistant du Marché Mvog-Mbi. Posez-moi une question sur un produit, nos heures, la livraison ou une recette.",
    rapides: { heures: "Heures", adresse: "Adresse", livraison: "Livraison", prix: "Meilleur prix", produit: "Trouver un produit", recettes: "Recettes", humain: "Parler à quelqu’un" },
    produitQ: "Avec plaisir ! Écrivez le nom d’un produit : <em>plantain, gari, attiéké, huile de palme, mèches…</em>",
    trouve: (n, q) => `Voici ce que j’ai trouvé pour « ${q} »${n > 5 ? ` (${n} produits)` : ""} :`,
    tousResultats: "Voir tous les résultats dans la boutique →", rien: (q) => `Je ne trouve pas « ${q} » dans notre catalogue en ligne. Il est peut-être quand même en magasin : appelez-nous au ${TEL}, nous vérifions tout de suite.`,
    pasCompris: `Je ne suis pas certain d’avoir compris. Vous pouvez me demander nos <strong>heures</strong>, la <strong>livraison</strong>, un <strong>produit</strong> ou une <strong>recette</strong>, ou joindre l’équipe au ${TEL}.`,
    ingredients: "Les ingrédients se trouvent au magasin :", voirRecette: "Voir la recette complète →", recettesListe: "Nos recettes pas à pas :",
    prixAbsent: "Les prix sont affichés en magasin seulement.", dispo: "La disponibilité change selon les arrivages :",
  };

  /* Réponses écrites d'avance : mots reconnus (sans accents, en minuscules) -> réponse */
  const R = EN ? {
    heures: () => `🕘 We are open <strong>every day, 9 a.m. to 9 p.m.</strong>, Monday to Sunday.<br>${etatOuverture()}`,
    adresse: () => `📍 <strong>3071 boulevard Portland, Sherbrooke (QC) J1L 2Y7</strong>.<br><a href="${CARTE}" target="_blank" rel="noopener">Get directions →</a>`,
    livraison: () => `🚚 Delivery is <strong>free for orders of $100 or more</strong> within <strong>5 km</strong> of the store. To order, call us at ${TEL}.`,
    prix: () => `💰 <strong>Best price guarantee</strong>: if you find the same product, same size, cheaper elsewhere, we sell it to you for <strong>1¢ less</strong>, and we credit you the difference on your previous bill. Bring the other store’s receipt or flyer.<br><small>${T.prixAbsent} Call ${TEL} for a price.</small>`,
    paiement: () => `💳 Payment is made <strong>in store or on delivery</strong>. Online payment is not available yet: the online shop is for discovering our products.`,
    commande: () => `🛒 To order, call us at ${TEL} (every day, 9 a.m. – 9 p.m.) or <a href="contact.html#ecrire">write to us</a> with your list. Free delivery from $100 within 5 km.`,
    emploi: () => `👋 We accept applications at any time! Send your résumé through the <a href="carriere.html#ecrire">careers page</a> or drop it off at the store.`,
    humain: () => `☎️ The team is happy to help: call ${TEL} (9 a.m. – 9 p.m.), email ${COURRIEL} or use the <a href="contact.html#ecrire">contact form</a>.`,
    nouveautes: () => `✨ See our latest arrivals and in-store offers on the <a href="nouveautes.html">New arrivals page</a>.`,
    rayons: () => `🧺 Over 2,000 products in 19 aisles: produce, roots and tubers, flours, spices, fish, meat, frozen leaves, drinks, beauty, braids… <a href="rayons.html">See all aisles →</a>`,
    dispo: () => `📦 ${T.dispo} call us at ${TEL} before coming in for a specific product, we will check for you.`,
    merci: () => `With pleasure! 😊 See you soon at Marché Mvog-Mbi.`,
    salut: () => `Hello! 😊 How can I help you?`,
  } : {
    heures: () => `🕘 Nous sommes ouverts <strong>tous les jours, de 9 h à 21 h</strong>, du lundi au dimanche.<br>${etatOuverture()}`,
    adresse: () => `📍 <strong>3071 boulevard Portland, Sherbrooke (QC) J1L 2Y7</strong>.<br><a href="${CARTE}" target="_blank" rel="noopener">Obtenir l’itinéraire →</a>`,
    livraison: () => `🚚 La livraison est <strong>gratuite dès 100 $ d’achat</strong>, dans un rayon de <strong>5 km</strong> autour du magasin. Pour commander, appelez-nous au ${TEL}.`,
    prix: () => `💰 <strong>Garantie du meilleur prix</strong> : vous trouvez le même produit, même format, moins cher ailleurs ? Nous vous le vendons <strong>1 ¢ de moins</strong>, et nous vous faisons un crédit de la différence sur votre ancienne facture. Apportez la facture ou l’annonce de l’autre magasin.<br><small>${T.prixAbsent} Appelez le ${TEL} pour un prix.</small>`,
    paiement: () => `💳 Le paiement se fait <strong>en magasin ou à la livraison</strong>. Le paiement en ligne n’est pas encore offert : la boutique en ligne sert à découvrir nos produits.`,
    commande: () => `🛒 Pour commander, appelez-nous au ${TEL} (tous les jours, 9 h à 21 h) ou <a href="contact.html#ecrire">écrivez-nous</a> avec votre liste. Livraison gratuite dès 100 $ dans un rayon de 5 km.`,
    emploi: () => `👋 Nous recevons les candidatures en tout temps ! Envoyez votre CV depuis la <a href="carriere.html#ecrire">page Carrière</a> ou déposez-le au magasin.`,
    humain: () => `☎️ L’équipe vous répond avec plaisir : ${TEL} (9 h à 21 h), ${COURRIEL} ou le <a href="contact.html#ecrire">formulaire de contact</a>.`,
    nouveautes: () => `✨ Découvrez nos derniers arrivages et les offres du magasin sur la <a href="nouveautes.html">page Nouveautés</a>.`,
    rayons: () => `🧺 Plus de 2 000 produits dans 19 rayons : fruits et légumes, féculents, farines, épices, poissons, viandes, feuilles congelées, boissons, beauté, mèches… <a href="rayons.html">Voir tous les rayons →</a>`,
    dispo: () => `📦 ${T.dispo} appelez-nous au ${TEL} avant de venir pour un produit précis, nous vérifions pour vous.`,
    merci: () => `Avec plaisir ! 😊 À bientôt au Marché Mvog-Mbi.`,
    salut: () => `Bonjour ! 😊 Comment puis-je vous aider ?`,
  };
  const INTENTIONS = [
    ["heures", /\b(heure|heures|horaire|ouvert|ouverte|ouvrez|ouvre|ferme|fermez|fermeture|dimanche|ferie|open|close|closing|hours)\b/],
    ["livraison", /\b(livr\w*|domicile|deliver\w*|5 ?km)\b/],
    ["prix", /\b(prix|cher|combien|coute|cout|tarif|garantie|sou|price|prices|cost|cheap\w*|guarantee|expensive)\b/],
    ["paiement", /\b(payer|paiement|paye|carte|interac|comptant|debit|pay|payment|cash|card)\b/],
    ["commande", /\b(commande|commander|reserver|order|ordering)\b/],
    ["emploi", /\b(emploi|travail|travailler|job|jobs|cv|candidature|postuler|embauche\w*|career\w*|hiring|resume|work)\b/],
    ["adresse", /\b(adresse|situe|situes|trouve|itineraire|venir|stationnement|parking|address|where|directions?|located|location|map)\b|\bou (etes|est|se trouve)/],
    ["humain", /\b(contact\w*|telephone|tel|appeler|joindre|courriel|email|mail|parler|humain|personne|conseiller|phone|call|human|someone)\b/],
    ["nouveautes", /\b(nouveau|nouveaux|nouveaute\w*|arrivage\w*|promo\w*|special|speciaux|rabais|new|arrivals?|deals?|offers?)\b/],
    ["dispo", /\b(dispo|disponible|disponibilite|stock|rupture|available|availability)\b/],
    ["rayons", /\b(rayon|rayons|categorie\w*|aisles?|categor\w*|departments?)\b/],
    ["merci", /\b(merci|thanks|thank|super|parfait|genial)\b/],
    ["salut", /^(bonjour|salut|allo|hello|hi|hey|bonsoir|coucou|yo)\b/],
  ];
  // Mots à retirer avant de chercher un produit (« avez-vous du gari ? » -> « gari »)
  const VIDES = new Set(("avez vous avez-vous est ce que qu il y a t il je cherche cherche voudrais veux aimerais acheter trouver " +
    "du de la le les des un une au aux en pour avec sans svp s il vous plait vendez vend vendre est-ce chez " +
    "do you have any sell selling looking for i want need buy where find the a an some please is there").split(" "));

  let catalogue = null, recettes = null;
  const lire = (f) => fetch(RACINE + f).then((r) => (r.ok ? r.json() : Promise.reject(r.status)));
  function produits() {
    if (!catalogue) {
      catalogue = lire("data/produits.json").then((d) => {
        d.produits.forEach((p) => {
          p._nom = " " + mots_de(p.nom);
          p._cle = " " + mots_de([p.nom, p.rayon, p.rayon_en, (p.conditionnements || []).join(" ")].join(" "));
        });
        return d.produits;
      }).catch(() => []);
    }
    return catalogue;
  }
  function lesRecettes() { if (!recettes) recettes = lire("data/recettes.json").catch(() => []); return recettes; }

  /* ---------- Fenêtre ---------- */
  const icone = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/><path d="M8.5 11h.01M12 11h.01M15.5 11h.01"/></svg>';
  const racine = document.createElement("div");
  racine.className = "assistant";
  racine.innerHTML = `
    <button type="button" class="assistant-bouton" aria-expanded="false" aria-controls="assistant-fenetre">
      ${icone}<span>${T.ouvrir}</span>
    </button>
    <section id="assistant-fenetre" class="assistant-fenetre" role="dialog" aria-label="${T.titre}" hidden>
      <header class="assistant-tete">
        <img src="${RACINE}images/icone.png" alt="" width="40" height="40">
        <div><strong>${T.titre}</strong><span><i class="point-ouvert" aria-hidden="true"></i>${T.sous}</span></div>
        <button type="button" class="assistant-vider" title="${T.vider}" aria-label="${T.vider}">↺</button>
        <button type="button" class="assistant-fermer" aria-label="${T.fermer}">✕</button>
      </header>
      <div class="assistant-fil" aria-live="polite"></div>
      <div class="assistant-rapides"></div>
      <form class="assistant-saisie" autocomplete="off">
        <input type="text" name="q" maxlength="200" placeholder="${T.place}" aria-label="${T.place}">
        <button type="submit" aria-label="${T.envoyer}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></button>
      </form>
    </section>`;
  document.body.appendChild(racine);
  const bouton = racine.querySelector(".assistant-bouton");
  const fenetre = racine.querySelector(".assistant-fenetre");
  const fil = racine.querySelector(".assistant-fil");
  const rapides = racine.querySelector(".assistant-rapides");
  const saisie = racine.querySelector(".assistant-saisie");
  const champ = saisie.querySelector("input");

  const CLE = "assistant-mvogmbi-" + (EN ? "en" : "fr");
  let historique = [];
  try { historique = JSON.parse(sessionStorage.getItem(CLE) || "[]"); } catch (e) { historique = []; }
  const garder = () => { try { sessionStorage.setItem(CLE, JSON.stringify(historique.slice(-40))); } catch (e) { /* rien */ } };

  function bulle(qui, contenu, enregistrer = true) {
    const b = document.createElement("div");
    b.className = "assistant-msg " + qui;
    b.innerHTML = contenu;
    fil.appendChild(b);
    fil.scrollTop = fil.scrollHeight;
    if (enregistrer) { historique.push([qui, contenu]); garder(); }
  }
  function montrerRapides(liste) {
    rapides.innerHTML = liste.map((k) => `<button type="button" data-k="${k}">${T.rapides[k]}</button>`).join("");
  }
  function repondre(contenu, suite) {
    const attente = document.createElement("div");
    attente.className = "assistant-msg bot attente";
    attente.innerHTML = "<i></i><i></i><i></i>";
    fil.appendChild(attente);
    fil.scrollTop = fil.scrollHeight;
    Promise.resolve(contenu).then((html) => setTimeout(() => {
      attente.remove();
      bulle("bot", html);
      montrerRapides(suite || ["heures", "livraison", "produit", "recettes", "humain"]);
    }, 420));
  }

  /* ---------- Compréhension ---------- */
  function vignette(p) {
    const img = p.photo ? `<img src="${echapper(RACINE + p.photo)}" alt="" loading="lazy" width="44" height="44">`
      : `<img src="${RACINE}images/icone.png" alt="" class="vide" width="44" height="44">`;
    const rayon = (EN && p.rayon_en) || p.rayon;
    return `<a class="assistant-produit" href="produit.html?id=${encodeURIComponent(p.id)}">${img}<span><strong>${echapper(p.nom)}</strong><small>${echapper(rayon)}</small></span></a>`;
  }
  function chercherProduits(texte) {
    const mots = mots_de(texte).split(" ").filter((m) => m.length > 1 && !VIDES.has(m));
    if (!mots.length) return Promise.resolve(null);
    return produits().then((liste) => {
      let trouves = liste.filter((p) => mots.every((m) => p._cle.includes(" " + m)));
      if (!trouves.length && mots.length > 1) trouves = liste.filter((p) => mots.some((m) => m.length > 3 && p._nom.includes(" " + m)));
      const note = (x) => (mots.every((m) => x._nom.includes(" " + m)) ? 2 : 0) + (x.photo ? 1 : 0);
      trouves.sort((a, b) => note(b) - note(a));
      return { mots: mots.join(" "), trouves };
    });
  }
  function reponseRecette(r) {
    const titre = (EN && r.titre_en) || r.titre, pays = (EN && r.pays_en) || r.pays;
    const ing = r.ingredients.slice(0, 6).map((i) =>
      `<li><a href="boutique.html?q=${encodeURIComponent(i.cherche)}">${echapper((EN && i.texte_en) || i.texte)}</a></li>`).join("");
    return `🍲 <strong>${echapper(titre)}</strong> (${echapper(pays)}) · ${echapper((EN && r.temps_en) || r.temps)}<br>${echapper((EN && r.resume_en) || r.resume)}
      <br><small>${T.ingredients}</small><ul>${ing}</ul><a href="recettes.html#${r.id}">${T.voirRecette}</a>`;
  }
  function comprendre(texte) {
    const n = normal(texte).replace(/[^a-z0-9 ]+/g, " ").replace(/\s+/g, " ").trim();
    return lesRecettes().then((liste) => {
      // Une recette nommée ? (« ndolé », « poulet DG », « mafé »)
      const r = liste.find((x) => mots_de(x.titre).split(" ").filter((m) => m.length > 3 && !["sauce", "soupe", "poisson", "poulet", "bananes"].includes(m))
        .some((m) => (" " + n + " ").includes(" " + m + " ")) || (" " + n + " ").includes(" " + mots_de(x.titre) + " "));
      if (r) return [reponseRecette(r), ["recettes", "produit", "humain"]];
      if (/\b(recette|recettes|cuisiner|cuisine|plat|plats|preparer|recipe|recipes|cook|cooking|dish)\b/.test(n)) {
        return [`${T.recettesListe}<ul>${liste.map((x) => `<li><a href="recettes.html#${x.id}">${echapper((EN && x.titre_en) || x.titre)}</a> · ${echapper((EN && x.pays_en) || x.pays)}</li>`).join("")}</ul>`,
          ["produit", "humain"]];
      }
      const intention = INTENTIONS.find(([, re]) => re.test(n));
      // Une question de produit l'emporte sur « prix » ou « dispo » : « avez-vous du gari ? »
      return chercherProduits(n).then((res) => {
        const general = intention && ["heures", "adresse", "livraison", "paiement", "emploi", "humain", "commande", "merci", "salut", "nouveautes", "rayons"].includes(intention[0]);
        if (res && res.trouves.length && !general) {
          const q = echapper(texte.trim());
          const plus = res.trouves.length > 5 ? `<a class="assistant-tout" href="boutique.html?q=${encodeURIComponent(res.mots)}">${T.tousResultats}</a>` : "";
          const extra = intention ? `<p>${R[intention[0]]()}</p>` : "";
          return [`${T.trouve(res.trouves.length, q)}<div class="assistant-produits">${res.trouves.slice(0, 5).map(vignette).join("")}</div>${plus}${extra}`,
            ["produit", "livraison", "humain"]];
        }
        if (intention) return [R[intention[0]](), null];
        if (res && res.mots) return [T.rien(echapper(texte.trim())), ["produit", "recettes", "humain"]];
        return [T.pasCompris, null];
      });
    });
  }

  function demander(texte) {
    if (!texte.trim()) return;
    bulle("moi", echapper(texte));
    rapides.innerHTML = "";
    const resultat = comprendre(texte);
    resultat.then(([html, suite]) => repondre(html, suite)).catch(() => repondre(T.pasCompris));
  }

  /* ---------- Événements ---------- */
  function demarrer() {
    fil.innerHTML = "";
    if (historique.length) historique.forEach(([qui, c]) => bulle(qui, c, false));
    else bulle("bot", T.bonjour);
    montrerRapides(["heures", "adresse", "livraison", "prix", "produit", "recettes", "humain"]);
  }
  let pret = false;
  function ouvrir() {
    if (!pret) { demarrer(); pret = true; produits(); lesRecettes(); }
    fenetre.hidden = false;
    racine.classList.add("ouvert");
    bouton.setAttribute("aria-expanded", "true");
    setTimeout(() => champ.focus(), 50);
  }
  function fermer() {
    fenetre.hidden = true;
    racine.classList.remove("ouvert");
    bouton.setAttribute("aria-expanded", "false");
    bouton.focus();
  }
  window.ouvrirAssistant = ouvrir;
  bouton.addEventListener("click", () => (fenetre.hidden ? ouvrir() : fermer()));
  racine.querySelector(".assistant-fermer").addEventListener("click", fermer);
  racine.querySelector(".assistant-vider").addEventListener("click", () => { historique = []; garder(); demarrer(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !fenetre.hidden) fermer(); });
  document.querySelectorAll("[data-assistant]").forEach((a) => a.addEventListener("click", (e) => { e.preventDefault(); ouvrir(); }));
  saisie.addEventListener("submit", (e) => { e.preventDefault(); const t = champ.value; champ.value = ""; demander(t); });
  rapides.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    const k = b.dataset.k;
    bulle("moi", echapper(b.textContent));
    rapides.innerHTML = "";
    if (k === "produit") repondre(T.produitQ, ["recettes", "humain"]);
    else if (k === "recettes") comprendre(EN ? "recipes" : "recettes").then(([h, s]) => repondre(h, s));
    else repondre(R[k](), null);
  });
})();
