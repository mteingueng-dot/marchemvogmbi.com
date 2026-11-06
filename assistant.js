/* Assistant du Marché Mvog-Mbi : petite fenêtre de discussion qui répond tout de suite, sans service externe.
   Réponses écrites d'avance (heures, adresse, livraison, garantie du prix, paiement, emploi, contact…),
   recherche dans le catalogue (data/produits.json) et dans les recettes (data/recettes.json).
   Six langues : français, anglais, espagnol, portugais, italien, allemand (langue de la page).
   Aucun prix n'est donné (règle du propriétaire) ; rien n'est envoyé ailleurs. */
(function () {
  "use strict";
  const LANG = (document.documentElement.lang || "fr").slice(0, 2);
  const EN = LANG === "en";
  const AUTRE = !["fr", "en"].includes(LANG);           // es, pt, it, de
  const RACINE = LANG === "fr" ? "" : "../";
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
    if (AUTRE) return ouvert ? AUTRES[LANG].ouvert : AUTRES[LANG].ferme;
    if (EN) return ouvert ? `We are <strong>open right now</strong>, until 9 p.m.` : `We are <strong>closed right now</strong>. We open at 9 a.m.`;
    return ouvert ? `Nous sommes <strong>ouverts en ce moment</strong>, jusqu’à 21 h.` : `Nous sommes <strong>fermés en ce moment</strong>. Nous ouvrons à 9 h.`;
  }

  /* Espagnol, portugais, italien, allemand : textes de la fenêtre (T) et réponses écrites d'avance (R) */
  const AUTRES = {
    es: {
      ouvert: "Estamos <strong>abiertos ahora</strong>, hasta las 21 h.", ferme: "Estamos <strong>cerrados ahora</strong>. Abrimos a las 9 h.",
      T: {
        titre: "Asistente Mvog-Mbi", sous: "Responde al instante", ouvrir: "¿Una pregunta? Hablemos", fermer: "Cerrar el chat",
        place: "Escribe tu pregunta…", envoyer: "Enviar", vider: "Nueva conversación",
        bonjour: "¡Hola! 👋 Soy el asistente del Marché Mvog-Mbi. Pregúntame por un producto, el horario, la entrega o una receta.",
        rapides: { heures: "Horario", adresse: "Dirección", livraison: "Entrega", prix: "Mejor precio", produit: "Buscar un producto", recettes: "Recetas", humain: "Hablar con alguien" },
        produitQ: "¡Con gusto! Escribe el nombre de un producto: <em>plátano, gari, attiéké, aceite de palma, extensiones…</em>",
        trouve: (n, q) => `Esto es lo que encontré para «${q}»${n > 5 ? ` (${n} productos)` : ""}:`,
        tousResultats: "Ver todos los resultados en la tienda →", rien: (q) => `No encuentro «${q}» en nuestro catálogo en línea. Quizá esté en la tienda: llámanos al ${TEL} y lo comprobamos enseguida.`,
        pasCompris: `No estoy seguro de haber entendido. Puedes preguntarme el <strong>horario</strong>, la <strong>entrega</strong>, un <strong>producto</strong> o una <strong>receta</strong>, o llamar al equipo al ${TEL}.`,
        ingredients: "Los ingredientes están en la tienda:", voirRecette: "Ver la receta completa →", recettesListe: "Nuestras recetas paso a paso:",
        prixAbsent: "Los precios solo se muestran en la tienda.", dispo: "La disponibilidad cambia según las llegadas:", motRecettes: "recetas",
      },
      R: {
        heures: () => `🕘 Abrimos <strong>todos los días, de 9 a 21 h</strong>, de lunes a domingo.<br>${etatOuverture()}`,
        adresse: () => `📍 <strong>3071 boulevard Portland, Sherbrooke (QC) J1L 2Y7</strong>.<br><a href="${CARTE}" target="_blank" rel="noopener">Cómo llegar →</a>`,
        livraison: () => `🚚 La entrega es <strong>gratuita desde 100 $ de compra</strong>, en un radio de <strong>5 km</strong> de la tienda. Para pedir, llámanos al ${TEL}.`,
        prix: () => `💰 <strong>Garantía del mejor precio</strong>: ¿encuentras el mismo producto, mismo formato, más barato en otro sitio? Te lo vendemos <strong>1 ¢ más barato</strong> y te acreditamos la diferencia en tu compra anterior. Trae el ticket o el folleto de la otra tienda.<br><small>${T.prixAbsent} Llama al ${TEL} para un precio.</small>`,
        paiement: () => `💳 El pago se hace <strong>en la tienda o en la entrega</strong>. Aún no se puede pagar en línea: la tienda en línea sirve para descubrir nuestros productos.`,
        commande: () => `🛒 Para pedir, llámanos al ${TEL} (todos los días, de 9 a 21 h) o <a href="contact.html#ecrire">escríbenos</a> con tu lista. Entrega gratuita desde 100 $ en un radio de 5 km.`,
        emploi: () => `👋 ¡Recibimos candidaturas en todo momento! Envía tu CV desde la <a href="carriere.html#ecrire">página de empleo</a> o tráelo a la tienda.`,
        humain: () => `☎️ El equipo te atiende con gusto: ${TEL} (9 a 21 h), ${COURRIEL} o el <a href="contact.html#ecrire">formulario de contacto</a>.`,
        nouveautes: () => `✨ Descubre las últimas llegadas y las ofertas de la tienda en la <a href="nouveautes.html">página de novedades</a>.`,
        rayons: () => `🧺 Más de 2000 productos en 19 secciones: frutas y verduras, tubérculos, harinas, especias, pescados, carnes, hojas congeladas, bebidas, belleza, extensiones… <a href="rayons.html">Ver todas las secciones →</a>`,
        dispo: () => `📦 ${T.dispo} llámanos al ${TEL} antes de venir por un producto concreto y lo comprobamos.`,
        merci: () => `¡Con gusto! 😊 Hasta pronto en el Marché Mvog-Mbi.`, salut: () => `¡Hola! 😊 ¿En qué puedo ayudarte?`,
      },
    },
    pt: {
      ouvert: "Estamos <strong>abertos agora</strong>, até às 21h.", ferme: "Estamos <strong>fechados agora</strong>. Abrimos às 9h.",
      T: {
        titre: "Assistente Mvog-Mbi", sous: "Responde na hora", ouvrir: "Uma pergunta? Vamos conversar", fermer: "Fechar a conversa",
        place: "Escreva a sua pergunta…", envoyer: "Enviar", vider: "Nova conversa",
        bonjour: "Olá! 👋 Sou o assistente do Marché Mvog-Mbi. Pergunte-me sobre um produto, o horário, a entrega ou uma receita.",
        rapides: { heures: "Horário", adresse: "Endereço", livraison: "Entrega", prix: "Melhor preço", produit: "Procurar um produto", recettes: "Receitas", humain: "Falar com alguém" },
        produitQ: "Com prazer! Escreva o nome de um produto: <em>banana-da-terra, gari, attiéké, dendê, extensões…</em>",
        trouve: (n, q) => `Eis o que encontrei para «${q}»${n > 5 ? ` (${n} produtos)` : ""}:`,
        tousResultats: "Ver todos os resultados na loja →", rien: (q) => `Não encontro «${q}» no nosso catálogo online. Talvez esteja na loja: ligue-nos para ${TEL} e verificamos logo.`,
        pasCompris: `Não tenho a certeza de ter entendido. Pode perguntar-me o <strong>horário</strong>, a <strong>entrega</strong>, um <strong>produto</strong> ou uma <strong>receita</strong>, ou ligar para a equipe: ${TEL}.`,
        ingredients: "Os ingredientes estão na loja:", voirRecette: "Ver a receita completa →", recettesListe: "As nossas receitas passo a passo:",
        prixAbsent: "Os preços só estão afixados na loja.", dispo: "A disponibilidade muda conforme as chegadas:", motRecettes: "receitas",
      },
      R: {
        heures: () => `🕘 Estamos abertos <strong>todos os dias, das 9h às 21h</strong>, de segunda a domingo.<br>${etatOuverture()}`,
        adresse: () => `📍 <strong>3071 boulevard Portland, Sherbrooke (QC) J1L 2Y7</strong>.<br><a href="${CARTE}" target="_blank" rel="noopener">Como chegar →</a>`,
        livraison: () => `🚚 A entrega é <strong>grátis a partir de 100 $ de compras</strong>, num raio de <strong>5 km</strong> da loja. Para encomendar, ligue-nos para ${TEL}.`,
        prix: () => `💰 <strong>Garantia do melhor preço</strong>: encontrou o mesmo produto, mesmo formato, mais barato noutro lugar? Vendemos-lho por <strong>1 ¢ a menos</strong> e creditamos-lhe a diferença na compra anterior. Traga o recibo ou o folheto da outra loja.<br><small>${T.prixAbsent} Ligue para ${TEL} para saber um preço.</small>`,
        paiement: () => `💳 O pagamento é feito <strong>na loja ou na entrega</strong>. Ainda não é possível pagar online: a loja online serve para descobrir os nossos produtos.`,
        commande: () => `🛒 Para encomendar, ligue-nos para ${TEL} (todos os dias, das 9h às 21h) ou <a href="contact.html#ecrire">escreva-nos</a> com a sua lista. Entrega grátis a partir de 100 $ num raio de 5 km.`,
        emploi: () => `👋 Recebemos candidaturas a qualquer momento! Envie o seu currículo pela <a href="carriere.html#ecrire">página Carreira</a> ou deixe-o na loja.`,
        humain: () => `☎️ A equipe atende com prazer: ${TEL} (9h às 21h), ${COURRIEL} ou o <a href="contact.html#ecrire">formulário de contato</a>.`,
        nouveautes: () => `✨ Descubra as últimas chegadas e as ofertas da loja na <a href="nouveautes.html">página Novidades</a>.`,
        rayons: () => `🧺 Mais de 2000 produtos em 19 seções: frutas e legumes, tubérculos, farinhas, especiarias, peixes, carnes, folhas congeladas, bebidas, beleza, extensões… <a href="rayons.html">Ver todas as seções →</a>`,
        dispo: () => `📦 ${T.dispo} ligue-nos para ${TEL} antes de vir por um produto específico, nós verificamos.`,
        merci: () => `Com prazer! 😊 Até breve no Marché Mvog-Mbi.`, salut: () => `Olá! 😊 Como posso ajudar?`,
      },
    },
    it: {
      ouvert: "Siamo <strong>aperti adesso</strong>, fino alle 21.", ferme: "Siamo <strong>chiusi adesso</strong>. Apriamo alle 9.",
      T: {
        titre: "Assistente Mvog-Mbi", sous: "Risponde subito", ouvrir: "Una domanda? Parliamone", fermer: "Chiudi la chat",
        place: "Scrivi la tua domanda…", envoyer: "Invia", vider: "Nuova conversazione",
        bonjour: "Ciao! 👋 Sono l'assistente del Marché Mvog-Mbi. Chiedimi di un prodotto, degli orari, della consegna o di una ricetta.",
        rapides: { heures: "Orari", adresse: "Indirizzo", livraison: "Consegna", prix: "Miglior prezzo", produit: "Trova un prodotto", recettes: "Ricette", humain: "Parla con qualcuno" },
        produitQ: "Volentieri! Scrivi il nome di un prodotto: <em>platano, gari, attiéké, olio di palma, extension…</em>",
        trouve: (n, q) => `Ecco cosa ho trovato per «${q}»${n > 5 ? ` (${n} prodotti)` : ""}:`,
        tousResultats: "Vedi tutti i risultati nel negozio →", rien: (q) => `Non trovo «${q}» nel nostro catalogo online. Forse è comunque in negozio: chiamaci allo ${TEL} e verifichiamo subito.`,
        pasCompris: `Non sono sicuro di aver capito. Puoi chiedermi gli <strong>orari</strong>, la <strong>consegna</strong>, un <strong>prodotto</strong> o una <strong>ricetta</strong>, oppure chiamare la squadra allo ${TEL}.`,
        ingredients: "Gli ingredienti sono in negozio:", voirRecette: "Vedi la ricetta completa →", recettesListe: "Le nostre ricette passo dopo passo:",
        prixAbsent: "I prezzi sono esposti solo in negozio.", dispo: "La disponibilità cambia secondo gli arrivi:", motRecettes: "ricette",
      },
      R: {
        heures: () => `🕘 Siamo aperti <strong>tutti i giorni, dalle 9 alle 21</strong>, dal lunedì alla domenica.<br>${etatOuverture()}`,
        adresse: () => `📍 <strong>3071 boulevard Portland, Sherbrooke (QC) J1L 2Y7</strong>.<br><a href="${CARTE}" target="_blank" rel="noopener">Indicazioni stradali →</a>`,
        livraison: () => `🚚 La consegna è <strong>gratuita da 100 $ di spesa</strong>, entro <strong>5 km</strong> dal negozio. Per ordinare, chiamaci allo ${TEL}.`,
        prix: () => `💰 <strong>Garanzia del miglior prezzo</strong>: trovi lo stesso prodotto, stesso formato, a meno altrove? Te lo vendiamo a <strong>1 ¢ in meno</strong> e ti accreditiamo la differenza sull'acquisto precedente. Porta lo scontrino o il volantino dell'altro negozio.<br><small>${T.prixAbsent} Chiama lo ${TEL} per un prezzo.</small>`,
        paiement: () => `💳 Il pagamento si fa <strong>in negozio o alla consegna</strong>. Il pagamento online non è ancora disponibile: il negozio online serve a scoprire i nostri prodotti.`,
        commande: () => `🛒 Per ordinare, chiamaci allo ${TEL} (tutti i giorni, dalle 9 alle 21) o <a href="contact.html#ecrire">scrivici</a> con la tua lista. Consegna gratuita da 100 $ entro 5 km.`,
        emploi: () => `👋 Riceviamo candidature in ogni momento! Invia il tuo CV dalla <a href="carriere.html#ecrire">pagina Lavora con noi</a> o portalo in negozio.`,
        humain: () => `☎️ La squadra ti risponde volentieri: ${TEL} (dalle 9 alle 21), ${COURRIEL} o il <a href="contact.html#ecrire">modulo di contatto</a>.`,
        nouveautes: () => `✨ Scopri gli ultimi arrivi e le offerte del negozio nella <a href="nouveautes.html">pagina Novità</a>.`,
        rayons: () => `🧺 Oltre 2000 prodotti in 19 reparti: frutta e verdura, tuberi, farine, spezie, pesce, carne, foglie surgelate, bevande, bellezza, extension… <a href="rayons.html">Vedi tutti i reparti →</a>`,
        dispo: () => `📦 ${T.dispo} chiamaci allo ${TEL} prima di venire per un prodotto specifico, verifichiamo per te.`,
        merci: () => `Con piacere! 😊 A presto al Marché Mvog-Mbi.`, salut: () => `Ciao! 😊 Come posso aiutarti?`,
      },
    },
    de: {
      ouvert: "Wir haben <strong>jetzt geöffnet</strong>, bis 21 Uhr.", ferme: "Wir haben <strong>jetzt geschlossen</strong>. Wir öffnen um 9 Uhr.",
      T: {
        titre: "Mvog-Mbi-Assistent", sous: "Antwortet sofort", ouvrir: "Eine Frage? Chatten Sie mit uns", fermer: "Chat schließen",
        place: "Schreiben Sie Ihre Frage…", envoyer: "Senden", vider: "Neues Gespräch",
        bonjour: "Hallo! 👋 Ich bin der Assistent des Marché Mvog-Mbi. Fragen Sie mich nach einem Produkt, den Öffnungszeiten, der Lieferung oder einem Rezept.",
        rapides: { heures: "Öffnungszeiten", adresse: "Adresse", livraison: "Lieferung", prix: "Bester Preis", produit: "Produkt finden", recettes: "Rezepte", humain: "Mit jemandem sprechen" },
        produitQ: "Gern! Schreiben Sie den Namen eines Produkts: <em>Kochbanane, Gari, Attiéké, Palmöl, Flechthaar…</em>",
        trouve: (n, q) => `Das habe ich für „${q}“ gefunden${n > 5 ? ` (${n} Produkte)` : ""}:`,
        tousResultats: "Alle Ergebnisse im Shop ansehen →", rien: (q) => `Ich finde „${q}“ nicht in unserem Online-Katalog. Vielleicht ist es trotzdem im Laden: Rufen Sie uns an unter ${TEL}, wir prüfen es sofort.`,
        pasCompris: `Ich bin nicht sicher, ob ich Sie verstanden habe. Fragen Sie mich nach den <strong>Öffnungszeiten</strong>, der <strong>Lieferung</strong>, einem <strong>Produkt</strong> oder einem <strong>Rezept</strong>, oder erreichen Sie das Team unter ${TEL}.`,
        ingredients: "Die Zutaten gibt es im Laden:", voirRecette: "Zum vollständigen Rezept →", recettesListe: "Unsere Rezepte Schritt für Schritt:",
        prixAbsent: "Die Preise stehen nur im Laden.", dispo: "Die Verfügbarkeit ändert sich mit den Lieferungen:", motRecettes: "rezepte",
      },
      R: {
        heures: () => `🕘 Wir haben <strong>täglich von 9 bis 21 Uhr</strong> geöffnet, von Montag bis Sonntag.<br>${etatOuverture()}`,
        adresse: () => `📍 <strong>3071 boulevard Portland, Sherbrooke (QC) J1L 2Y7</strong>.<br><a href="${CARTE}" target="_blank" rel="noopener">Route anzeigen →</a>`,
        livraison: () => `🚚 Die Lieferung ist <strong>ab 100 $ Einkaufswert kostenlos</strong>, im Umkreis von <strong>5 km</strong> um den Laden. Zum Bestellen rufen Sie uns an unter ${TEL}.`,
        prix: () => `💰 <strong>Bestpreisgarantie</strong>: Sie finden dasselbe Produkt in derselben Größe anderswo günstiger? Wir verkaufen es Ihnen <strong>1 ¢ billiger</strong> und schreiben Ihnen die Differenz auf Ihren letzten Einkauf gut. Bringen Sie den Kassenbon oder Prospekt des anderen Geschäfts mit.<br><small>${T.prixAbsent} Rufen Sie ${TEL} an, um einen Preis zu erfahren.</small>`,
        paiement: () => `💳 Bezahlt wird <strong>im Laden oder bei der Lieferung</strong>. Online-Zahlung gibt es noch nicht: Der Online-Shop dient zum Entdecken unserer Produkte.`,
        commande: () => `🛒 Zum Bestellen rufen Sie uns an unter ${TEL} (täglich 9 bis 21 Uhr) oder <a href="contact.html#ecrire">schreiben Sie uns</a> Ihre Liste. Kostenlose Lieferung ab 100 $ im Umkreis von 5 km.`,
        emploi: () => `👋 Wir nehmen jederzeit Bewerbungen an! Schicken Sie Ihren Lebenslauf über die <a href="carriere.html#ecrire">Karriereseite</a> oder geben Sie ihn im Laden ab.`,
        humain: () => `☎️ Das Team hilft Ihnen gern: ${TEL} (9 bis 21 Uhr), ${COURRIEL} oder das <a href="contact.html#ecrire">Kontaktformular</a>.`,
        nouveautes: () => `✨ Entdecken Sie die neuesten Lieferungen und Angebote auf der <a href="nouveautes.html">Seite Neuheiten</a>.`,
        rayons: () => `🧺 Über 2000 Produkte in 19 Abteilungen: Obst und Gemüse, Knollen, Mehle, Gewürze, Fisch, Fleisch, Tiefkühlblätter, Getränke, Schönheit, Flechthaar… <a href="rayons.html">Alle Abteilungen ansehen →</a>`,
        dispo: () => `📦 ${T.dispo} Rufen Sie uns an unter ${TEL}, bevor Sie für ein bestimmtes Produkt kommen; wir prüfen es für Sie.`,
        merci: () => `Gern geschehen! 😊 Bis bald im Marché Mvog-Mbi.`, salut: () => `Hallo! 😊 Wie kann ich Ihnen helfen?`,
      },
    },
  };
  const T = AUTRE ? AUTRES[LANG].T : EN ? {
    titre: "Mvog-Mbi assistant", sous: "Replies instantly", ouvrir: "Questions? Chat with us", fermer: "Close the chat",
    place: "Type your question…", envoyer: "Send", vider: "New conversation",
    bonjour: "Hello! 👋 I’m the Marché Mvog-Mbi assistant. Ask me about a product, our hours, delivery or a recipe.",
    rapides: { heures: "Hours", adresse: "Address", livraison: "Delivery", prix: "Best price", produit: "Find a product", recettes: "Recipes", humain: "Talk to someone" },
    produitQ: "Sure! Type the name of a product: <em>plantain, gari, attiéké, palm oil, braids…</em>",
    trouve: (n, q) => `Here is what I found for “${q}”${n > 5 ? ` (${n} products)` : ""}:`,
    tousResultats: "See all results in the shop →", rien: (q) => `I can’t find “${q}” in our online catalogue. It may still be in store: call us at ${TEL} and we will check right away.`,
    pasCompris: `I’m not sure I understood. You can ask about our <strong>hours</strong>, <strong>delivery</strong>, a <strong>product</strong> or a <strong>recipe</strong>, or reach the team at ${TEL}.`,
    ingredients: "Ingredients available at the store:", voirRecette: "See the full recipe →", recettesListe: "Our step-by-step recipes:",
    prixAbsent: "Prices are shown in store only.", dispo: "Availability changes with arrivals:", motRecettes: "recipes",
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
    prixAbsent: "Les prix sont affichés en magasin seulement.", dispo: "La disponibilité change selon les arrivages :", motRecettes: "recettes",
  };

  /* Réponses écrites d'avance : mots reconnus (sans accents, en minuscules) -> réponse */
  const R = AUTRE ? AUTRES[LANG].R : EN ? {
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
    ["heures", /\b(heure|heures|horaire|ouvert|ouverte|ouvrez|ouvre|ferme|fermez|fermeture|dimanche|ferie|open|close|closing|hours|horario|horarios|abierto|abren|cierran|domingo|aberto|abrem|fecham|orari|orario|aperto|aprite|chiudete|domenica|offnungszeit\w*|geoffnet|offnen|schliessen|sonntag)\b/],
    ["livraison", /\b(livr\w*|domicile|deliver\w*|5 ?km|entrega\w*|envio|domicilio|consegn\w*|lieferung|liefern|liefert)\b/],
    ["prix", /\b(prix|cher|combien|coute|cout|tarif|garantie|sou|price|prices|cost|cheap\w*|guarantee|expensive|precio|precios|cuanto|cuesta|barato|caro|preco|precos|quanto|custa|prezzo|prezzi|costa|economico|preis|preise|kostet|teuer|billig)\b/],
    ["paiement", /\b(payer|paiement|paye|carte|interac|comptant|debit|pay|payment|cash|card|pagar|pago|tarjeta|efectivo|pagamento|cartao|dinheiro|pagare|carta|contanti|bezahlen|zahlung)\b/],
    ["commande", /\b(commande|commander|reserver|order|ordering|pedido|pedir|encomenda\w*|ordine|ordinare|bestell\w*)\b/],
    ["emploi", /\b(emploi|travail|travailler|job|jobs|cv|candidature|postuler|embauche\w*|career\w*|hiring|resume|work|empleo|trabajo|trabajar|candidatura|curriculo|emprego|trabalho|trabalhar|lavoro|lavorare|bewerb\w*|arbeit|arbeiten|lebenslauf|stelle)\b/],
    ["adresse", /\b(adresse|situe|situes|trouve|itineraire|venir|stationnement|parking|address|where|directions?|located|location|map|direccion|donde|ubicacion|llegar|endereco|onde|chegar|indirizzo|dove|arrivare|wo|anfahrt|route|karte)\b|\bou (etes|est|se trouve)/],
    ["humain", /\b(contact\w*|telephone|tel|appeler|joindre|courriel|email|mail|parler|humain|personne|conseiller|phone|call|human|someone|telefono|llamar|hablar|persona|contato|ligar|falar|pessoa|chiamare|parlare|telefon|anrufen|sprechen|mensch)\b/],
    ["nouveautes", /\b(nouveau|nouveaux|nouveaute\w*|arrivage\w*|promo\w*|special|speciaux|rabais|new|arrivals?|deals?|offers?|novedad\w*|oferta\w*|novidade\w*|novita|offerta\w*|neuheit\w*|angebot\w*|neu)\b/],
    ["dispo", /\b(dispo|disponible|disponibilite|stock|rupture|available|availability|disponibilidad|disponivel|disponibilidade|disponibile|disponibilita|verfugbar\w*|vorratig)\b/],
    ["rayons", /\b(rayon|rayons|categorie\w*|aisles?|categor\w*|departments?|seccion\w*|secao|secoes|reparto|reparti|abteilung\w*)\b/],
    ["merci", /\b(merci|thanks|thank|super|parfait|genial|gracias|obrigad\w*|grazie|danke)\b/],
    ["salut", /^(bonjour|salut|allo|hello|hi|hey|bonsoir|coucou|yo|hola|buenas|ola|oi|bom dia|ciao|buongiorno|salve|hallo|guten tag|servus)\b/],
  ];
  // Mots à retirer avant de chercher un produit (« avez-vous du gari ? » -> « gari »)
  const VIDES = new Set(("avez vous avez-vous est ce que qu il y a t il je cherche cherche voudrais veux aimerais acheter trouver " +
    "du de la le les des un une au aux en pour avec sans svp s il vous plait vendez vend vendre est-ce chez " +
    "do you have any sell selling looking for i want need buy where find the a an some please is there " +
    "tienen tiene teneis busco quiero comprar venden hay el los las unos por favor con " +
    "tem voces vende procuro quero comprar os as uns umas por favor " +
    "avete avete ha cerco vorrei voglio comprare vendete il lo gli lui di del della per favore c e " +
    "haben habt gibt es ich suche mochte will kaufen verkaufen der die das ein eine einen bitte").split(" "));

  let catalogue = null, recettes = null, recettesLangue = null;
  const lire = (f) => fetch(RACINE + f).then((r) => (r.ok ? r.json() : Promise.reject(r.status)));
  function produits() {
    if (!catalogue) {
      const textes = AUTRE ? lire(`data/produits_${LANG}.json`).catch(() => null) : Promise.resolve(null);
      catalogue = Promise.all([lire("data/produits.json"), textes]).then(([d, x]) => {
        d.produits.forEach((p) => {
          if (x) { p._rayon = x.rayons[p.rayon]; p._d = x.d[p.id]; }
          p._nom = " " + mots_de(p.nom);
          p._cle = " " + mots_de([p.nom, p.rayon, p.rayon_en, p._rayon || "", p._d || "", (p.conditionnements || []).join(" ")].join(" "));
          p._debut = " " + mots_de(p._d || (EN ? p.description_en : p.description) || "").slice(0, 60);
        });
        return d.produits;
      }).catch(() => []);
    }
    return catalogue;
  }
  function lesRecettes() {
    if (!recettes) {
      const rx = AUTRE ? lire(`data/recettes_${LANG}.json`).catch(() => ({})) : Promise.resolve({});
      recettes = Promise.all([lire("data/recettes.json"), rx]).then(([liste, x]) => {
        recettesLangue = x;
        return liste;
      }).catch(() => []);
    }
    return recettes;
  }
  // texte d'une recette dans la langue de la page
  const rv = (r, k) => (AUTRE && recettesLangue && recettesLangue[r.id] && recettesLangue[r.id][k]) || (!(EN || AUTRE) ? r[k] : r[k + "_en"] || r[k]);

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

  const CLE = "assistant-mvogmbi-" + LANG;
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
    const rayon = (AUTRE && p._rayon) || (EN && p.rayon_en) || p.rayon;
    return `<a class="assistant-produit" href="produit.html?id=${encodeURIComponent(p.id)}">${img}<span><strong>${echapper(p.nom)}</strong><small>${echapper(rayon)}</small></span></a>`;
  }
  function chercherProduits(texte) {
    const mots = mots_de(texte).split(" ").filter((m) => m.length > 1 && !VIDES.has(m));
    if (!mots.length) return Promise.resolve(null);
    return produits().then((liste) => {
      let trouves = liste.filter((p) => mots.every((m) => p._cle.includes(" " + m)));
      if (!trouves.length && mots.length > 1) trouves = liste.filter((p) => mots.some((m) => m.length > 3 && p._nom.includes(" " + m)));
      const note = (x) => (mots.every((m) => x._nom.includes(" " + m)) ? 4 : mots.every((m) => x._debut.includes(" " + m)) ? 2 : 0) + (x.photo ? 1 : 0);
      trouves.sort((a, b) => note(b) - note(a));
      return { mots: mots.join(" "), trouves };
    });
  }
  function reponseRecette(r) {
    const titre = rv(r, "titre"), pays = rv(r, "pays");
    const ingx = (AUTRE && recettesLangue && recettesLangue[r.id] && recettesLangue[r.id].ingredients) || [];
    const ing = r.ingredients.slice(0, 6).map((i, k) =>
      `<li><a href="boutique.html?q=${encodeURIComponent(i.cherche)}">${echapper(ingx[k] || (!(EN || AUTRE) ? i.texte : i.texte_en || i.texte))}</a></li>`).join("");
    return `🍲 <strong>${echapper(titre)}</strong> (${echapper(pays)}) · ${echapper(rv(r, "temps"))}<br>${echapper(rv(r, "resume"))}
      <br><small>${T.ingredients}</small><ul>${ing}</ul><a href="recette-${r.id}.html">${T.voirRecette}</a>`;
  }
  function comprendre(texte) {
    const n = normal(texte).replace(/[^a-z0-9 ]+/g, " ").replace(/\s+/g, " ").trim();
    return lesRecettes().then((liste) => {
      // Une recette nommée ? (« ndolé », « poulet DG », « mafé »)
      const r = liste.find((x) => mots_de(x.titre).split(" ").filter((m) => m.length > 3 && !["sauce", "soupe", "poisson", "poulet", "bananes", "salsa", "sopa", "pollo", "frango", "molho", "zuppa", "suppe", "huhn", "with", "con", "com", "mit", "aux"].includes(m))
        .some((m) => (" " + n + " ").includes(" " + m + " ")) || (" " + n + " ").includes(" " + mots_de(x.titre) + " ") || (" " + n + " ").includes(" " + mots_de(rv(x, "titre")) + " "));
      if (r) return [reponseRecette(r), ["recettes", "produit", "humain"]];
      if (/\b(recette|recettes|cuisiner|cuisine|plat|plats|preparer|recipe|recipes|cook|cooking|dish|receta|recetas|cocinar|plato|platos|receita|receitas|cozinhar|prato|pratos|ricetta|ricette|cucinare|piatto|piatti|rezept|rezepte|kochen|gericht\w*)\b/.test(n)) {
        return [`${T.recettesListe}<ul>${liste.map((x) => `<li><a href="recette-${x.id}.html">${echapper(rv(x, "titre"))}</a> · ${echapper(rv(x, "pays"))}</li>`).join("")}</ul>`,
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
    else if (k === "recettes") comprendre(T.motRecettes).then(([h, s]) => repondre(h, s));
    else repondre(R[k](), null);
  });
})();
