"""Référencement (Google, Bing) : titres et descriptions de chaque page dans les 6 langues, titre et description
des pages recettes, paragraphe « épicerie à Sherbrooke » de l'accueil, données structurées (magasin, recettes).

Titres : 60 caractères environ ; descriptions : 120 à 160 caractères (contrôlés par outils/construire_site.py).
"""
from __future__ import annotations

import json
import re

URL = "https://www.marchemvogmbi.com"

PAGES = {
    "fr": {
        "index.html": ("Épicerie africaine à Sherbrooke | Marché Mvog-Mbi",
                       "Épicerie africaine, caribéenne et latine au 3071 boul. Portland, Sherbrooke : 2 000 produits, ouvert tous les jours de 9 h à 21 h, livraison gratuite dès 100 $."),
        "nouveautes.html": ("Nouveaux arrivages | Marché Mvog-Mbi Sherbrooke",
                            "Les derniers arrivages d’Afrique, des Caraïbes et d’Amérique latine au Marché Mvog-Mbi, à Sherbrooke. Quantités limitées : passez vite ou appelez-nous."),
        "boutique.html": ("Produits africains et antillais | Marché Mvog-Mbi Sherbrooke",
                          "Gari, attiéké, plantain, huile de palme, ndolé, poisson fumé, mèches : parcourez plus de 2 000 produits, puis appelez au 819 239-9864 ou passez au magasin."),
        "produit.html": ("Produit | Marché Mvog-Mbi Sherbrooke",
                         "Fiche produit du Marché Mvog-Mbi, épicerie africaine, caribéenne et latine au 3071 boulevard Portland, à Sherbrooke. Ouvert tous les jours de 9 h à 21 h."),
        "rayons.html": ("Nos rayons : fruits, farines, épices | Marché Mvog-Mbi",
                        "Plantain, igname, macabo, gari, foufou, poivre de Penja, poissons fumés, viandes, boissons et mèches : tous les rayons de l’épicerie Mvog-Mbi à Sherbrooke."),
        "recettes.html": ("Recettes africaines et antillaises | Marché Mvog-Mbi",
                          "Ndolé, jollof, thiéboudienne, poulet yassa, griot, mafé : plus de 80 recettes d’Afrique, des Caraïbes et d’Amérique latine, ingrédients en vente à Sherbrooke."),
        "a-propos.html": ("Notre histoire : de Yaoundé à Sherbrooke | Marché Mvog-Mbi",
                          "Le Marché Mvog-Mbi tire son nom d’un grand marché de Yaoundé. Au 3071 boul. Portland, à Sherbrooke, l’Afrique, les Caraïbes et l’Amérique latine se croisent."),
        "carriere.html": ("Emplois en épicerie à Sherbrooke | Marché Mvog-Mbi",
                          "Le Marché Mvog-Mbi, épicerie africaine, caribéenne et latine de Sherbrooke, recrute. Envoyez votre CV en ligne ou passez nous voir au 3071 boul. Portland."),
        "contact.html": ("Heures, adresse et livraison | Marché Mvog-Mbi Sherbrooke",
                         "3071 boulevard Portland, Sherbrooke. Ouvert tous les jours de 9 h à 21 h. Commandes au 819 239-9864, livraison gratuite dès 100 $ dans un rayon de 5 km."),
    },
    "en": {
        "index.html": ("African & Caribbean Grocery in Sherbrooke | Marché Mvog-Mbi",
                       "African, Caribbean and Latin grocery at 3071 Portland Blvd, Sherbrooke: over 2,000 products, open daily 9 a.m. to 9 p.m., free delivery on orders from $100."),
        "nouveautes.html": ("New Arrivals | Marché Mvog-Mbi Sherbrooke",
                            "The latest arrivals from Africa, the Caribbean and Latin America at Marché Mvog-Mbi in Sherbrooke. Limited quantities: drop by soon or give us a call."),
        "boutique.html": ("African & Caribbean Products in Sherbrooke | Marché Mvog-Mbi",
                          "Gari, attiéké, plantain, palm oil, ndolé, smoked fish, braiding hair: browse over 2,000 products, then call 819 239-9864 or visit the store."),
        "produit.html": ("Product | Marché Mvog-Mbi Sherbrooke",
                         "Product page of Marché Mvog-Mbi, African, Caribbean and Latin grocery at 3071 boulevard Portland, Sherbrooke. Open every day from 9 a.m. to 9 p.m."),
        "rayons.html": ("Our Aisles: Produce, Flours, Spices, Hair | Marché Mvog-Mbi",
                        "Plantain, yam, cocoyam, gari, fufu, Penja pepper, smoked fish, meat, drinks and braiding hair: every aisle of the Mvog-Mbi grocery in Sherbrooke."),
        "recettes.html": ("African & Caribbean Recipes, Step by Step | Marché Mvog-Mbi",
                          "Ndolé, jollof, thieboudienne, chicken yassa, griot, mafé: over 80 recipes from Africa, the Caribbean and Latin America, with ingredients sold in Sherbrooke."),
        "a-propos.html": ("Our Story: From Yaoundé to Sherbrooke | Marché Mvog-Mbi",
                          "Marché Mvog-Mbi is named after a large market in Yaoundé. At 3071 Portland Blvd in Sherbrooke, Africa, the Caribbean and Latin America meet."),
        "carriere.html": ("Grocery Jobs in Sherbrooke | Marché Mvog-Mbi",
                          "Marché Mvog-Mbi, the African, Caribbean and Latin grocery in Sherbrooke, is hiring. Send your résumé online or drop by 3071 Portland Blvd."),
        "contact.html": ("Hours, Address and Delivery | Marché Mvog-Mbi Sherbrooke",
                         "3071 boulevard Portland, Sherbrooke. Open every day from 9 a.m. to 9 p.m. Call 819 239-9864; free delivery from $100 within a 5 km radius."),
    },
    "es": {
        "index.html": ("Tienda africana y caribeña en Sherbrooke | Marché Mvog-Mbi",
                       "Tienda africana, caribeña y latina en el 3071 boul. Portland, Sherbrooke: más de 2000 productos, abierto todos los días de 9 a 21 h, entrega gratis desde 100 $."),
        "nouveautes.html": ("Novedades | Marché Mvog-Mbi Sherbrooke",
                            "Las últimas llegadas de África, el Caribe y América Latina al Marché Mvog-Mbi, en Sherbrooke. Cantidades limitadas: ven pronto o llámanos por teléfono."),
        "boutique.html": ("Productos africanos y caribeños | Marché Mvog-Mbi",
                          "Gari, attiéké, plátano, aceite de palma, ndolé, pescado ahumado, extensiones: más de 2000 productos. Llama al 819 239-9864 o visita la tienda."),
        "produit.html": ("Producto | Marché Mvog-Mbi Sherbrooke",
                         "Ficha de producto del Marché Mvog-Mbi, tienda africana, caribeña y latina en el 3071 boulevard Portland, Sherbrooke. Abierto todos los días de 9 a 21 h."),
        "rayons.html": ("Secciones: frutas, harinas, especias | Marché Mvog-Mbi",
                        "Plátano, ñame, malanga, gari, fufu, pimienta de Penja, pescado ahumado, carnes, bebidas y extensiones: todas las secciones del Marché Mvog-Mbi en Sherbrooke."),
        "recettes.html": ("Recetas africanas y caribeñas paso a paso | Marché Mvog-Mbi",
                          "Ndolé, jollof, thieboudienne, pollo yassa, griot, mafé: más de 80 recetas de África, el Caribe y América Latina, con ingredientes a la venta en Sherbrooke."),
        "a-propos.html": ("Nuestra historia: de Yaundé a Sherbrooke | Marché Mvog-Mbi",
                          "El Marché Mvog-Mbi lleva el nombre de un gran mercado de Yaundé. En el 3071 boul. Portland, en Sherbrooke, se cruzan África, el Caribe y América Latina."),
        "carriere.html": ("Ofertas de empleo en Sherbrooke | Marché Mvog-Mbi",
                          "El Marché Mvog-Mbi, tienda africana, caribeña y latina de Sherbrooke, contrata personal. Envía tu CV en línea o visítanos en el 3071 boul. Portland."),
        "contact.html": ("Horario, dirección y entrega | Marché Mvog-Mbi Sherbrooke",
                         "3071 boulevard Portland, Sherbrooke. Abierto todos los días de 9 a 21 h. Llama al 819 239-9864; entrega gratuita desde 100 $ en un radio de 5 km."),
    },
    "pt": {
        "index.html": ("Mercearia africana em Sherbrooke | Marché Mvog-Mbi",
                       "Mercearia africana, caribenha e latina no 3071 boul. Portland, Sherbrooke: 2000 produtos, aberta todos os dias das 9h às 21h, entrega grátis desde 100 $."),
        "nouveautes.html": ("Novidades | Marché Mvog-Mbi Sherbrooke",
                            "As últimas chegadas da África, do Caribe e da América Latina ao Marché Mvog-Mbi, em Sherbrooke. Quantidades limitadas: venha logo ou ligue para nós."),
        "boutique.html": ("Produtos africanos e caribenhos | Marché Mvog-Mbi",
                          "Gari, attiéké, banana-da-terra, azeite de dendê, ndolé, peixe defumado, apliques: mais de 2000 produtos. Ligue para 819 239-9864 ou visite a loja."),
        "produit.html": ("Produto | Marché Mvog-Mbi Sherbrooke",
                         "Ficha de produto do Marché Mvog-Mbi, mercearia africana, caribenha e latina no 3071 boulevard Portland, Sherbrooke. Aberta todos os dias das 9h às 21h."),
        "rayons.html": ("Seções: frutas, farinhas, especiarias | Marché Mvog-Mbi",
                        "Banana-da-terra, inhame, taioba, gari, fufu, pimenta de Penja, peixe defumado, carnes, bebidas e apliques: todas as seções do Marché Mvog-Mbi em Sherbrooke."),
        "recettes.html": ("Receitas africanas e caribenhas | Marché Mvog-Mbi",
                          "Ndolé, jollof, thieboudienne, frango yassa, griot, mafé: mais de 80 receitas da África, do Caribe e da América Latina, ingredientes à venda em Sherbrooke."),
        "a-propos.html": ("Nossa história: de Iaundé a Sherbrooke | Marché Mvog-Mbi",
                          "O Marché Mvog-Mbi leva o nome de um grande mercado de Iaundé. No 3071 boul. Portland, em Sherbrooke, a África, o Caribe e a América Latina se encontram."),
        "carriere.html": ("Vagas de emprego em Sherbrooke | Marché Mvog-Mbi",
                          "O Marché Mvog-Mbi, mercearia africana, caribenha e latina de Sherbrooke, está contratando. Envie seu currículo on-line ou visite-nos no 3071 boul. Portland."),
        "contact.html": ("Horário, endereço e entrega | Marché Mvog-Mbi Sherbrooke",
                         "3071 boulevard Portland, Sherbrooke. Aberta todos os dias das 9h às 21h. Ligue para 819 239-9864; entrega grátis desde 100 $ num raio de 5 km."),
    },
    "it": {
        "index.html": ("Alimentari africani a Sherbrooke | Marché Mvog-Mbi",
                       "Alimentari africani, caraibici e latini al 3071 boul. Portland, Sherbrooke: oltre 2000 prodotti, aperto ogni giorno dalle 9 alle 21, consegna gratuita da 100 $."),
        "nouveautes.html": ("Novità | Marché Mvog-Mbi Sherbrooke",
                            "Gli ultimi arrivi dall’Africa, dai Caraibi e dall’America Latina al Marché Mvog-Mbi di Sherbrooke. Quantità limitate: passa presto o chiamaci."),
        "boutique.html": ("Prodotti africani e caraibici a Sherbrooke | Marché Mvog-Mbi",
                          "Gari, attiéké, platano, olio di palma, ndolé, pesce affumicato, extension: oltre 2000 prodotti. Chiama il 819 239-9864 o vieni a trovarci in negozio."),
        "produit.html": ("Prodotto | Marché Mvog-Mbi Sherbrooke",
                         "Scheda prodotto del Marché Mvog-Mbi, alimentari africani, caraibici e latini al 3071 boulevard Portland, Sherbrooke. Aperto ogni giorno dalle 9 alle 21."),
        "rayons.html": ("Reparti: frutta, farine, spezie | Marché Mvog-Mbi",
                        "Platano, igname, taro, gari, fufu, pepe di Penja, pesce affumicato, carni, bevande ed extension: tutti i reparti del Marché Mvog-Mbi a Sherbrooke."),
        "recettes.html": ("Ricette africane e caraibiche passo passo | Marché Mvog-Mbi",
                          "Ndolé, jollof, thieboudienne, pollo yassa, griot, mafé: oltre 80 ricette dall’Africa, dai Caraibi e dall’America Latina, ingredienti in vendita a Sherbrooke."),
        "a-propos.html": ("La nostra storia: da Yaoundé a Sherbrooke | Marché Mvog-Mbi",
                          "Il Marché Mvog-Mbi prende il nome da un grande mercato di Yaoundé. Al 3071 boul. Portland, a Sherbrooke, s’incontrano Africa, Caraibi e America Latina."),
        "carriere.html": ("Lavorare in negozio a Sherbrooke | Marché Mvog-Mbi",
                          "Il Marché Mvog-Mbi, alimentari africani, caraibici e latini di Sherbrooke, assume. Invia il tuo curriculum online o vieni a trovarci al 3071 boul. Portland."),
        "contact.html": ("Orari, indirizzo e consegna | Marché Mvog-Mbi Sherbrooke",
                         "3071 boulevard Portland, Sherbrooke. Aperto ogni giorno dalle 9 alle 21. Chiama il 819 239-9864; consegna gratuita da 100 $ entro un raggio di 5 km."),
    },
    "de": {
        "index.html": ("Afrika- & Karibik-Laden in Sherbrooke | Marché Mvog-Mbi",
                       "Afrikanische, karibische und lateinamerikanische Lebensmittel, 3071 boul. Portland, Sherbrooke: über 2000 Produkte, täglich 9–21 Uhr, Lieferung ab 100 $ gratis."),
        "nouveautes.html": ("Neuheiten | Marché Mvog-Mbi Sherbrooke",
                            "Die neuesten Lieferungen aus Afrika, der Karibik und Lateinamerika im Marché Mvog-Mbi in Sherbrooke. Begrenzte Mengen: schnell vorbeikommen oder anrufen."),
        "boutique.html": ("Afrikanische & karibische Produkte | Marché Mvog-Mbi",
                          "Gari, Attiéké, Kochbananen, Palmöl, Ndolé, Räucherfisch, Haarteile: über 2000 Produkte. Rufen Sie 819 239-9864 an oder besuchen Sie den Laden."),
        "produit.html": ("Produkt | Marché Mvog-Mbi Sherbrooke",
                         "Produktseite des Marché Mvog-Mbi, afrikanische, karibische und lateinamerikanische Lebensmittel, 3071 boulevard Portland, Sherbrooke. Täglich 9–21 Uhr."),
        "rayons.html": ("Abteilungen: Obst, Mehle, Gewürze | Marché Mvog-Mbi",
                        "Kochbananen, Yams, Taro, Gari, Fufu, Penja-Pfeffer, Räucherfisch, Fleisch, Getränke und Haarteile: alle Abteilungen des Marché Mvog-Mbi in Sherbrooke."),
        "recettes.html": ("Afrikanische & karibische Rezepte | Marché Mvog-Mbi",
                          "Ndolé, Jollof, Thieboudienne, Yassa-Hähnchen, Griot, Mafé: über 80 Rezepte aus Afrika, der Karibik und Lateinamerika, Zutaten erhältlich in Sherbrooke."),
        "a-propos.html": ("Von Yaoundé nach Sherbrooke | Marché Mvog-Mbi",
                          "Der Marché Mvog-Mbi ist nach einem großen Markt in Yaoundé benannt. Am 3071 boul. Portland in Sherbrooke treffen sich Afrika, die Karibik und Lateinamerika."),
        "carriere.html": ("Jobs im Lebensmittelladen in Sherbrooke | Marché Mvog-Mbi",
                          "Der Marché Mvog-Mbi, afrikanische, karibische und lateinamerikanische Lebensmittel in Sherbrooke, stellt ein. Lebenslauf online senden oder vorbeikommen."),
        "contact.html": ("Öffnungszeiten & Adresse | Marché Mvog-Mbi Sherbrooke",
                         "3071 boulevard Portland, Sherbrooke. Täglich von 9 bis 21 Uhr geöffnet. Rufen Sie 819 239-9864 an; Lieferung ab 100 $ gratis im Umkreis von 5 km."),
    },
}

# Pages recettes : « Recette : Ndolé (Cameroun) | Marché Mvog-Mbi », description = résumé + mention de Sherbrooke
MOT_RECETTE = {"fr": "Recette : ", "en": "Recipe: ", "es": "Receta: ", "pt": "Receita: ", "it": "Ricetta: ", "de": "Rezept: "}
SUITE_LONGUE = {"fr": " Recette pas à pas, ingrédients en vente au Marché Mvog-Mbi, à Sherbrooke.",
                "en": " Step-by-step recipe, ingredients sold at Marché Mvog-Mbi in Sherbrooke.",
                "es": " Receta paso a paso, ingredientes en el Marché Mvog-Mbi de Sherbrooke.",
                "pt": " Receita passo a passo, ingredientes no Marché Mvog-Mbi de Sherbrooke.",
                "it": " Ricetta passo passo, ingredienti in vendita al Marché Mvog-Mbi di Sherbrooke.",
                "de": " Rezept Schritt für Schritt, Zutaten im Marché Mvog-Mbi in Sherbrooke."}
SUITE_RECETTE = {"fr": " Ingrédients en vente à Sherbrooke.", "en": " Ingredients sold in Sherbrooke.",
                 "es": " Ingredientes a la venta en Sherbrooke.", "pt": " Ingredientes à venda em Sherbrooke.",
                 "it": " Ingredienti in vendita a Sherbrooke.", "de": " Zutaten erhältlich in Sherbrooke."}


TITRE_MAX, DESCRIPTION_MIN, DESCRIPTION_MAX = 60, 120, 160


def titre_recette(titre: str, pays: str, langue: str) -> str:
    """La forme la plus complète qui tient en 60 caractères : on retire d'abord le pays, puis « Recette : »,
    puis « Marché » (« | Mvog-Mbi »)."""
    formes = [f"{MOT_RECETTE[langue]}{titre} ({pays}) | Marché Mvog-Mbi",
              f"{MOT_RECETTE[langue]}{titre} | Marché Mvog-Mbi",
              f"{titre} ({pays}) | Marché Mvog-Mbi",
              f"{titre} | Marché Mvog-Mbi",
              f"{titre} | Mvog-Mbi"]
    return next((f for f in formes if len(f) <= TITRE_MAX), formes[-1])


def couper(texte: str, maximum: int) -> str:
    """Coupe à la dernière phrase qui tient, sinon à la dernière virgule (« … »), sinon au dernier mot (« … »)."""
    if len(texte) <= maximum:
        return texte
    debut = texte[:maximum]
    fin = max(debut.rfind(". "), debut.rfind("! "), debut.rfind("? "))
    if fin >= DESCRIPTION_MIN - 20:
        return debut[:fin + 1]
    virgule = debut[:maximum - 1].rfind(", ")
    if virgule >= DESCRIPTION_MIN:
        return debut[:virgule] + "…"
    mots = debut[:maximum - 1].rsplit(" ", 1)[0].split(" ")
    while len(mots) > 1 and len(mots[-1]) <= 3:            # jamais « … et… », « … de… »
        mots.pop()
    return " ".join(mots).rstrip(",;:–- ") + "…"


def description_recette(resume: str, langue: str) -> str:
    """Résumé + mention du magasin à Sherbrooke (la plus longue qui tient en 160 caractères)."""
    texte = resume.strip()
    if not texte.endswith((".", "!", "?", "…")):
        texte += "."
    for suite in (SUITE_LONGUE[langue], SUITE_RECETTE[langue]):   # la plus longue mention qui tient
        if len(texte + suite) <= DESCRIPTION_MAX:
            return texte + suite
    return couper(texte, DESCRIPTION_MAX)


FICHE_COMMERCE = {
    "@context": "https://schema.org", "@type": "GroceryStore", "@id": f"{URL}/#magasin",
    "name": "Marché Mvog-Mbi Sherbrooke",
    "description": "Épicerie africaine, caribéenne et latine à Sherbrooke : plus de 2 000 produits, livraison gratuite dès 100 $ dans un rayon de 5 km.",
    "url": f"{URL}/", "telephone": "+1-819-239-9864", "email": "contact@marchemvogmbi.com",
    "image": f"{URL}/images/logo.png", "logo": f"{URL}/images/logo.png",
    "address": {"@type": "PostalAddress", "streetAddress": "3071 boulevard Portland", "addressLocality": "Sherbrooke",
                "addressRegion": "QC", "postalCode": "J1L 2Y7", "addressCountry": "CA"},
    "hasMap": "https://www.google.com/maps/dir/?api=1&destination=3071+boulevard+Portland+Sherbrooke+QC+J1L+2Y7",
    "geo": {"@type": "GeoCoordinates", "latitude": 45.40392, "longitude": -71.95231},   # OpenStreetMap, nœud du magasin
    "areaServed": {"@type": "City", "name": "Sherbrooke"}, "currenciesAccepted": "CAD",
    "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                   "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                   "opens": "09:00", "closes": "21:00"}],
}


def duree_iso(temps: str) -> str:
    """« 1 h 30 » -> PT1H30M, « 45 min » -> PT45M, « 2 h » -> PT2H ; rien de reconnu -> ''."""
    m = re.match(r"\s*(?:(\d+)\s*h)?\s*(?:(\d+)\s*(?:min)?)?", temps or "")
    h, mn = (m.group(1), m.group(2)) if m else (None, None)
    return ("PT" + (f"{h}H" if h else "") + (f"{mn}M" if mn else "")) if (h or mn) else ""


def recette_json_ld(r: dict, langue: str, adresse: str) -> str:
    """r : {titre, resume, pays, portions, temps (français, pour la durée), photo, ingredients [textes], etapes}."""
    d = {"@context": "https://schema.org", "@type": "Recipe", "name": r["titre"], "description": r["resume"],
         "image": [f"{URL}/{r['photo']}"] if r.get("photo") else [],
         "author": {"@type": "Organization", "name": "Marché Mvog-Mbi Sherbrooke", "url": f"{URL}/"},
         "recipeCuisine": r.get("pays", ""), "recipeYield": r.get("portions", ""),
         "totalTime": duree_iso(r.get("temps", "")), "recipeIngredient": r.get("ingredients", []),
         "recipeInstructions": [{"@type": "HowToStep", "text": e} for e in r.get("etapes", [])],
         "inLanguage": {"fr": "fr-CA", "en": "en-CA"}.get(langue, langue), "url": adresse}
    d = {k: v for k, v in d.items() if v}
    return '  <script type="application/ld+json">\n  ' + json.dumps(d, ensure_ascii=False) + "\n  </script>\n"


# Paragraphe de l'accueil (après les promesses) : seulement des faits déjà publiés sur le site
TEL = '<a href="tel:+18192399864">819 239-9864</a>'
SHERBROOKE = {
    "fr": ("Votre épicerie africaine, antillaise et latino à Sherbrooke",
           ["Vous cherchez du gari, de l’attiéké, des feuilles de ndolé, de l’huile de palme rouge ou du poisson fumé à Sherbrooke&nbsp;? Le Marché Mvog-Mbi, au 3071 boulevard Portland, réunit plus de 2&nbsp;000 produits d’Afrique centrale et de l’Ouest, des Caraïbes et d’Amérique latine&nbsp;: plantains, igname, macabo et taro, farines de foufou et de manioc, épices comme le poivre de Penja, viandes, boissons, soins de beauté et mèches.",
            "Que vous soyez du Cameroun, de la Côte d’Ivoire, du Congo, du Sénégal, d’Haïti, de la Jamaïque, de la Colombie ou du Québec, vous trouverez ici les ingrédients de vos plats préférés, et des <a href=\"recettes.html\">recettes pas à pas</a> pour en découvrir d’autres. Nous sommes ouverts tous les jours, de 9&nbsp;h à 21&nbsp;h. Nous livrons gratuitement dès 100&nbsp;$ d’achat dans un rayon de 5&nbsp;km, et notre garantie du meilleur prix vous assure de payer 1&nbsp;¢ de moins qu’ailleurs pour le même produit.",
            f"Un produit précis&nbsp;? Appelez-nous au {TEL} avant de vous déplacer&nbsp;: les arrivages changent souvent."]),
    "en": ("Your African, Caribbean and Latin grocery in Sherbrooke",
           ["Looking for gari, attiéké, ndolé leaves, red palm oil or smoked fish in Sherbrooke? Marché Mvog-Mbi, at 3071 boulevard Portland, carries over 2,000 products from Central and West Africa, the Caribbean and Latin America: plantains, yam, cocoyam and taro, fufu and cassava flours, spices such as Penja pepper, meat, drinks, beauty care and braiding hair.",
            "Whether you come from Cameroon, Côte d’Ivoire, Congo, Senegal, Haiti, Jamaica, Colombia or Quebec, you will find the ingredients of your favourite dishes here, along with <a href=\"recettes.html\">step-by-step recipes</a> to discover new ones. We are open every day from 9 a.m. to 9 p.m. Delivery is free on orders from $100 within 5 km, and our best price guarantee means you pay 1¢ less than elsewhere for the same product.",
            f"Looking for something specific? Call us at {TEL} before you come: new arrivals change often."]),
    "es": ("Tu tienda africana, caribeña y latina en Sherbrooke",
           ["¿Buscas gari, attiéké, hojas de ndolé, aceite de palma rojo o pescado ahumado en Sherbrooke? El Marché Mvog-Mbi, en el 3071 boulevard Portland, reúne más de 2000 productos de África central y occidental, el Caribe y América Latina: plátanos, ñame, malanga y taro, harinas de fufu y de yuca, especias como la pimienta de Penja, carnes, bebidas, productos de belleza y extensiones.",
            "Seas de Camerún, Costa de Marfil, el Congo, Senegal, Haití, Jamaica, Colombia o Quebec, aquí encontrarás los ingredientes de tus platos preferidos, y <a href=\"recettes.html\">recetas paso a paso</a> para descubrir otros. Abrimos todos los días de 9 a 21 h. La entrega es gratuita desde 100 $ de compra en un radio de 5 km, y nuestra garantía del mejor precio te asegura pagar 1 ¢ menos que en otros sitios por el mismo producto.",
            f"¿Buscas un producto concreto? Llámanos al {TEL} antes de venir: las llegadas cambian a menudo."]),
    "pt": ("Sua mercearia africana, caribenha e latina em Sherbrooke",
           ["Procura gari, attiéké, folhas de ndolé, azeite de dendê ou peixe defumado em Sherbrooke? O Marché Mvog-Mbi, no 3071 boulevard Portland, reúne mais de 2000 produtos da África Central e Ocidental, do Caribe e da América Latina: banana-da-terra, inhame, taioba e taro, farinhas de fufu e de mandioca, especiarias como a pimenta de Penja, carnes, bebidas, produtos de beleza e apliques.",
            "Seja você de Camarões, da Costa do Marfim, do Congo, do Senegal, do Haiti, da Jamaica, da Colômbia ou do Quebec, aqui encontrará os ingredientes dos seus pratos preferidos, e <a href=\"recettes.html\">receitas passo a passo</a> para descobrir outros. Abrimos todos os dias das 9h às 21h. A entrega é grátis a partir de 100 $ num raio de 5 km, e nossa garantia do melhor preço assegura que você paga 1 ¢ a menos do que em outros lugares pelo mesmo produto.",
            f"Procura um produto específico? Ligue para {TEL} antes de vir: as chegadas mudam com frequência."]),
    "it": ("Il tuo negozio africano, caraibico e latino a Sherbrooke",
           ["Cerchi gari, attiéké, foglie di ndolé, olio di palma rosso o pesce affumicato a Sherbrooke? Il Marché Mvog-Mbi, al 3071 boulevard Portland, riunisce oltre 2000 prodotti dell’Africa centrale e occidentale, dei Caraibi e dell’America Latina: platani, igname, macabo e taro, farine di fufu e di manioca, spezie come il pepe di Penja, carni, bevande, prodotti di bellezza ed extension.",
            "Che tu venga dal Camerun, dalla Costa d’Avorio, dal Congo, dal Senegal, da Haiti, dalla Giamaica, dalla Colombia o dal Québec, qui troverai gli ingredienti dei tuoi piatti preferiti, e <a href=\"recettes.html\">ricette passo passo</a> per scoprirne altri. Siamo aperti tutti i giorni dalle 9 alle 21. La consegna è gratuita da 100 $ di spesa entro 5 km, e la nostra garanzia del miglior prezzo ti fa pagare 1 ¢ in meno che altrove per lo stesso prodotto.",
            f"Cerchi un prodotto preciso? Chiamaci al {TEL} prima di venire: gli arrivi cambiano spesso."]),
    "de": ("Ihr afrikanischer, karibischer und lateinamerikanischer Laden in Sherbrooke",
           ["Sie suchen Gari, Attiéké, Ndolé-Blätter, rotes Palmöl oder Räucherfisch in Sherbrooke? Der Marché Mvog-Mbi am 3071 boulevard Portland führt über 2000 Produkte aus Zentral- und Westafrika, der Karibik und Lateinamerika: Kochbananen, Yams, Macabo und Taro, Fufu- und Maniokmehl, Gewürze wie Penja-Pfeffer, Fleisch, Getränke, Schönheitspflege und Haarteile.",
            "Ob Sie aus Kamerun, der Elfenbeinküste, dem Kongo, Senegal, Haiti, Jamaika, Kolumbien oder Québec kommen: Hier finden Sie die Zutaten Ihrer Lieblingsgerichte und <a href=\"recettes.html\">Rezepte Schritt für Schritt</a>, um neue zu entdecken. Wir haben täglich von 9 bis 21 Uhr geöffnet. Ab 100 $ Einkauf liefern wir im Umkreis von 5 km gratis, und dank unserer Bestpreisgarantie zahlen Sie für dasselbe Produkt 1 ¢ weniger als anderswo.",
            f"Sie suchen ein bestimmtes Produkt? Rufen Sie uns unter {TEL} an, bevor Sie kommen: Die Lieferungen wechseln oft."]),
}


def section_sherbrooke(langue: str) -> str:
    titre, paragraphes = SHERBROOKE[langue]
    corps = "\n".join(f"        <p>{p}</p>" for p in paragraphes)
    return (f'    <section class="section section-locale">\n      <div class="conteneur texte-local">\n'
            f"        <h2>{titre}</h2>\n{corps}\n      </div>\n    </section>\n")
