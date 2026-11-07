"""Pages thématiques (référencement) : produits par origine et rayon beauté, dans les 6 langues.

    produits-afrique-centrale.html, produits-afrique-ouest.html, produits-caraibes.html, meches-beaute-afro.html

Chaque page : un texte d'environ 150 à 250 mots, des produits phares en HTML fixe (liens vers les fiches), des
recherches de la boutique, les recettes de la région et les autres pages thématiques. Seuls des produits vendus
au magasin sont nommés dans les textes (vérifiés dans data/produits.json). Appelé par outils/construire_site.py.
"""
from __future__ import annotations

import html
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import quote_plus

import filtre_pays
import pages_produits

SITE = Path(__file__).resolve().parent.parent
NB_PRODUITS = 20
e = html.escape

TEL = '<a href="tel:+18192399864">819 239-9864</a>'

LIBELLES = {
    "fr": {"selections": "Nos sélections par origine", "surtitre": "Par origine", "phares": "Quelques produits en magasin", "chercher": "Chercher dans la boutique",
           "recettes": "Recettes de la région", "autres": "Nos autres sélections", "tout": "Voir tous les produits",
           "itineraire": "Itinéraire"},
    "en": {"selections": "Our selections by origin", "surtitre": "By origin", "phares": "Some products in store", "chercher": "Search the shop",
           "recettes": "Recipes from the region", "autres": "Our other selections", "tout": "See all products",
           "itineraire": "Directions"},
    "es": {"selections": "Nuestras selecciones por origen", "surtitre": "Por origen", "phares": "Algunos productos en tienda", "chercher": "Buscar en la tienda",
           "recettes": "Recetas de la región", "autres": "Nuestras otras selecciones", "tout": "Ver todos los productos",
           "itineraire": "Cómo llegar"},
    "pt": {"selections": "Nossas seleções por origem", "surtitre": "Por origem", "phares": "Alguns produtos na loja", "chercher": "Pesquisar na loja",
           "recettes": "Receitas da região", "autres": "Nossas outras seleções", "tout": "Ver todos os produtos",
           "itineraire": "Como chegar"},
    "it": {"selections": "Le nostre selezioni per origine", "surtitre": "Per origine", "phares": "Alcuni prodotti in negozio", "chercher": "Cerca nel negozio",
           "recettes": "Ricette della regione", "autres": "Le nostre altre selezioni", "tout": "Vedi tutti i prodotti",
           "itineraire": "Indicazioni"},
    "de": {"selections": "Unsere Auswahl nach Herkunft", "surtitre": "Nach Herkunft", "phares": "Einige Produkte im Laden", "chercher": "Im Shop suchen",
           "recettes": "Rezepte aus der Region", "autres": "Unsere weiteren Auswahlen", "tout": "Alle Produkte ansehen",
           "itineraire": "Route"},
}

FIN = {   # dernier paragraphe commun
    "fr": f"Les arrivages changent souvent : appelez-nous au {TEL} pour vérifier qu’un produit est en magasin. Nous sommes ouverts tous les jours de 9&nbsp;h à 21&nbsp;h, au 3071 boulevard Portland, et la livraison est gratuite dès 100&nbsp;$ d’achat dans un rayon de 5&nbsp;km.",
    "en": f"New arrivals change often: call us at {TEL} to check that a product is in store. We are open every day from 9 a.m. to 9 p.m. at 3071 boulevard Portland, and delivery is free on orders from $100 within 5 km.",
    "es": f"Las llegadas cambian a menudo: llámanos al {TEL} para comprobar que un producto está en tienda. Abrimos todos los días de 9 a 21 h en el 3071 boulevard Portland, y la entrega es gratuita desde 100 $ en un radio de 5 km.",
    "pt": f"As chegadas mudam com frequência: ligue para {TEL} para confirmar que um produto está na loja. Abrimos todos os dias das 9h às 21h, no 3071 boulevard Portland, e a entrega é grátis a partir de 100 $ num raio de 5 km.",
    "it": f"Gli arrivi cambiano spesso: chiamaci al {TEL} per verificare che un prodotto sia in negozio. Siamo aperti tutti i giorni dalle 9 alle 21 al 3071 boulevard Portland, e la consegna è gratuita da 100 $ entro 5 km.",
    "de": f"Die Lieferungen wechseln oft: Rufen Sie uns unter {TEL} an, um zu prüfen, ob ein Produkt vorrätig ist. Wir haben täglich von 9 bis 21 Uhr am 3071 boulevard Portland geöffnet, und ab 100 $ liefern wir im Umkreis von 5 km gratis.",
}

THEMES = [
    {
        "fichier": "produits-afrique-centrale.html", "region": "centrale",
        "mots": ["ndole", "eru", "egusi", "macabo", "bobolo", "chikwangue", "mbongo", "djansang", "penja",
                 "pondu", "miondo", "safou", "plantain", "taro", "manioc", "foufou", "couscous"],
        "recherches": ["ndolé", "eru", "pondu", "macabo", "bobolo", "chikwangue", "penja", "mbongo", "foufou", "plantain"],
        "textes": {
            "fr": ("Produits d’Afrique centrale à Sherbrooke | Marché Mvog-Mbi",
                   "Ndolé, eru, pondu, macabo, bobolo, chikwangue, poivre de Penja, foufou : les produits du Cameroun, du Congo et du Gabon au Marché Mvog-Mbi, à Sherbrooke.",
                   "Produits d’Afrique centrale : Cameroun, Congo, Gabon",
                   ["Le Marché Mvog-Mbi tire son nom d’un grand marché de Yaoundé : l’Afrique centrale est au cœur de nos rayons. À Sherbrooke, vous trouvez chez nous les ingrédients des plats du Cameroun, de la République démocratique du Congo, du Congo-Brazzaville et du Gabon.",
                    "Pour le ndolé, l’eru, le pondu ou le koki : feuilles congelées, graines d’egusi, poissons fumés et séchés. Pour accompagner : plantains, macabo, taro, manioc, miondo, bobolo, chikwangue et farines de foufou. Pour relever : poivre blanc de Penja, mbongo, djansang, piments et cubes d’assaisonnement. Et en saison, le safou."]),
            "en": ("Central African Food in Sherbrooke | Marché Mvog-Mbi",
                   "Ndolé, eru, pondu, cocoyam, bobolo, chikwangue, Penja pepper, fufu: products from Cameroon, Congo and Gabon at Marché Mvog-Mbi in Sherbrooke.",
                   "Central African products: Cameroon, Congo, Gabon",
                   ["Marché Mvog-Mbi is named after a large market in Yaoundé, so Central Africa is at the heart of our aisles. In Sherbrooke, you will find the ingredients of dishes from Cameroon, the Democratic Republic of the Congo, Congo-Brazzaville and Gabon.",
                    "For ndolé, eru, pondu or koki: frozen leaves, egusi seeds, smoked and dried fish. On the side: plantains, cocoyam (macabo), taro, cassava, miondo, bobolo, chikwangue and fufu flours. For flavour: white Penja pepper, mbongo, djansang, chillies and seasoning cubes. And in season, safou (African plum)."]),
            "es": ("Productos de África central en Sherbrooke | Marché Mvog-Mbi",
                   "Ndolé, eru, pondu, malanga, bobolo, chikwangue, pimienta de Penja, fufu: productos de Camerún, el Congo y Gabón en el Marché Mvog-Mbi de Sherbrooke.",
                   "Productos de África central: Camerún, Congo, Gabón",
                   ["El Marché Mvog-Mbi lleva el nombre de un gran mercado de Yaundé: África central está en el corazón de nuestras secciones. En Sherbrooke encontrarás los ingredientes de los platos de Camerún, la República Democrática del Congo, el Congo-Brazzaville y Gabón.",
                    "Para el ndolé, el eru, el pondu o el koki: hojas congeladas, semillas de egusi, pescado ahumado y seco. Para acompañar: plátanos, malanga (macabo), taro, yuca, miondo, bobolo, chikwangue y harinas de fufu. Para dar sabor: pimienta blanca de Penja, mbongo, djansang, chiles y cubitos. Y en temporada, el safou."]),
            "pt": ("Produtos da África Central em Sherbrooke | Marché Mvog-Mbi",
                   "Ndolé, eru, pondu, taioba, bobolo, chikwangue, pimenta de Penja, fufu: produtos de Camarões, do Congo e do Gabão no Marché Mvog-Mbi, em Sherbrooke.",
                   "Produtos da África Central: Camarões, Congo, Gabão",
                   ["O Marché Mvog-Mbi leva o nome de um grande mercado de Iaundé: a África Central está no coração das nossas seções. Em Sherbrooke, você encontra os ingredientes dos pratos de Camarões, da República Democrática do Congo, do Congo-Brazzaville e do Gabão.",
                    "Para o ndolé, o eru, o pondu ou o koki: folhas congeladas, sementes de egusi, peixe defumado e seco. Para acompanhar: banana-da-terra, taioba (macabo), taro, mandioca, miondo, bobolo, chikwangue e farinhas de fufu. Para temperar: pimenta branca de Penja, mbongo, djansang, pimentas e caldos. E, na estação, o safou."]),
            "it": ("Prodotti dell’Africa centrale a Sherbrooke | Marché Mvog-Mbi",
                   "Ndolé, eru, pondu, macabo, bobolo, chikwangue, pepe di Penja, fufu: prodotti del Camerun, del Congo e del Gabon al Marché Mvog-Mbi di Sherbrooke.",
                   "Prodotti dell’Africa centrale: Camerun, Congo, Gabon",
                   ["Il Marché Mvog-Mbi prende il nome da un grande mercato di Yaoundé: l’Africa centrale è al centro dei nostri reparti. A Sherbrooke trovi gli ingredienti dei piatti del Camerun, della Repubblica Democratica del Congo, del Congo-Brazzaville e del Gabon.",
                    "Per il ndolé, l’eru, il pondu o il koki: foglie surgelate, semi di egusi, pesce affumicato ed essiccato. Per accompagnare: platani, macabo, taro, manioca, miondo, bobolo, chikwangue e farine di fufu. Per insaporire: pepe bianco di Penja, mbongo, djansang, peperoncini e dadi. E in stagione, il safou."]),
            "de": ("Zentralafrikanische Produkte | Marché Mvog-Mbi Sherbrooke",
                   "Ndolé, Eru, Pondu, Macabo, Bobolo, Chikwangue, Penja-Pfeffer, Fufu: Produkte aus Kamerun, dem Kongo und Gabun im Marché Mvog-Mbi in Sherbrooke.",
                   "Produkte aus Zentralafrika: Kamerun, Kongo, Gabun",
                   ["Der Marché Mvog-Mbi ist nach einem großen Markt in Yaoundé benannt: Zentralafrika steht im Mittelpunkt unseres Sortiments. In Sherbrooke finden Sie die Zutaten für Gerichte aus Kamerun, der Demokratischen Republik Kongo, Kongo-Brazzaville und Gabun.",
                    "Für Ndolé, Eru, Pondu oder Koki: tiefgekühlte Blätter, Egusi-Samen, Räucher- und Trockenfisch. Als Beilage: Kochbananen, Macabo, Taro, Maniok, Miondo, Bobolo, Chikwangue und Fufu-Mehl. Zum Würzen: weißer Penja-Pfeffer, Mbongo, Djansang, Chilis und Brühwürfel. Und in der Saison Safou."]),
        },
    },
    {
        "fichier": "produits-afrique-ouest.html", "region": "ouest",
        "mots": ["attieke", "gari", "fonio", "bissap", "gombo", "igname", "elubo", "banku", "egusi", "mil", "sorgho",
                 "ijebu", "yam", "plantain", "palme"],
        "recherches": ["attiéké", "gari", "fonio", "bissap", "gombo", "igname", "egusi", "banku", "huile de palme"],
        "textes": {
            "fr": ("Produits d’Afrique de l’Ouest | Marché Mvog-Mbi Sherbrooke",
                   "Attiéké, gari, fonio, bissap, gombo, igname, egusi, huile de palme : les produits de Côte d’Ivoire, du Nigeria, du Ghana et du Sénégal, à Sherbrooke.",
                   "Produits d’Afrique de l’Ouest : Côte d’Ivoire, Nigeria, Ghana, Sénégal",
                   ["Attiéké poisson, riz jollof, thiéboudienne, eba et sauce gombo, mafé, poulet yassa : les plats d’Afrique de l’Ouest se préparent avec des ingrédients que vous trouvez au Marché Mvog-Mbi, à Sherbrooke.",
                    "Semoules et farines : attiéké, gari blanc et jaune, fonio, farine d’igname (elubo), farines de mil et de sorgho, mélanges pour banku. Légumes et tubercules : igname, gombo, plantain. Pour la cuisine : huile de palme, graines d’egusi, poissons fumés et séchés, épices et bouillons. Et pour boire : jus et sirops de bissap."]),
            "en": ("West African Food in Sherbrooke | Marché Mvog-Mbi",
                   "Attiéké, gari, fonio, bissap, okra, yam, egusi, palm oil: products from Côte d’Ivoire, Nigeria, Ghana and Senegal at Marché Mvog-Mbi in Sherbrooke.",
                   "West African products: Côte d’Ivoire, Nigeria, Ghana, Senegal",
                   ["Attiéké with fish, jollof rice, thieboudienne, eba with okra soup, mafé, chicken yassa: West African dishes are made with ingredients you will find at Marché Mvog-Mbi in Sherbrooke.",
                    "Semolinas and flours: attiéké, white and yellow gari, fonio, yam flour (elubo), millet and sorghum flours, banku mixes. Vegetables and tubers: yam, okra, plantain. For cooking: palm oil, egusi seeds, smoked and dried fish, spices and stock cubes. And to drink: bissap (hibiscus) juices and syrups."]),
            "es": ("Productos de África occidental | Marché Mvog-Mbi Sherbrooke",
                   "Attiéké, gari, fonio, bissap, quimbombó, ñame, egusi, aceite de palma: productos de Costa de Marfil, Nigeria, Ghana y Senegal en Sherbrooke.",
                   "Productos de África occidental: Costa de Marfil, Nigeria, Ghana, Senegal",
                   ["Attiéké con pescado, arroz jollof, thieboudienne, eba con salsa de quimbombó, mafé, pollo yassa: los platos de África occidental se preparan con ingredientes que encontrarás en el Marché Mvog-Mbi de Sherbrooke.",
                    "Sémolas y harinas: attiéké, gari blanco y amarillo, fonio, harina de ñame (elubo), harinas de mijo y de sorgo, mezclas para banku. Verduras y tubérculos: ñame, quimbombó, plátano. Para cocinar: aceite de palma, semillas de egusi, pescado ahumado y seco, especias y caldos. Y para beber: jugos y jarabes de bissap."]),
            "pt": ("Produtos da África Ocidental | Marché Mvog-Mbi Sherbrooke",
                   "Attiéké, gari, fonio, bissap, quiabo, inhame, egusi, azeite de dendê: produtos da Costa do Marfim, Nigéria, Gana e Senegal, em Sherbrooke.",
                   "Produtos da África Ocidental: Costa do Marfim, Nigéria, Gana, Senegal",
                   ["Attiéké com peixe, arroz jollof, thieboudienne, eba com molho de quiabo, mafé, frango yassa: os pratos da África Ocidental são feitos com ingredientes que você encontra no Marché Mvog-Mbi, em Sherbrooke.",
                    "Sêmolas e farinhas: attiéké, gari branco e amarelo, fonio, farinha de inhame (elubo), farinhas de milhete e de sorgo, misturas para banku. Legumes e tubérculos: inhame, quiabo, banana-da-terra. Para cozinhar: azeite de dendê, sementes de egusi, peixe defumado e seco, especiarias e caldos. E para beber: sucos e xaropes de bissap."]),
            "it": ("Prodotti dell’Africa occidentale | Marché Mvog-Mbi",
                   "Attiéké, gari, fonio, bissap, gombo, igname, egusi, olio di palma: prodotti di Costa d’Avorio, Nigeria, Ghana e Senegal a Sherbrooke.",
                   "Prodotti dell’Africa occidentale: Costa d’Avorio, Nigeria, Ghana, Senegal",
                   ["Attiéké con pesce, riso jollof, thieboudienne, eba con salsa di gombo, mafé, pollo yassa: i piatti dell’Africa occidentale si preparano con ingredienti che trovi al Marché Mvog-Mbi di Sherbrooke.",
                    "Semole e farine: attiéké, gari bianco e giallo, fonio, farina di igname (elubo), farine di miglio e di sorgo, miscele per banku. Verdure e tuberi: igname, gombo, platano. Per cucinare: olio di palma, semi di egusi, pesce affumicato ed essiccato, spezie e dadi. E da bere: succhi e sciroppi di bissap."]),
            "de": ("Westafrikanische Produkte | Marché Mvog-Mbi Sherbrooke",
                   "Attiéké, Gari, Fonio, Bissap, Okra, Yams, Egusi, Palmöl: Produkte aus der Elfenbeinküste, Nigeria, Ghana und Senegal in Sherbrooke.",
                   "Produkte aus Westafrika: Elfenbeinküste, Nigeria, Ghana, Senegal",
                   ["Attiéké mit Fisch, Jollof-Reis, Thieboudienne, Eba mit Okrasoße, Mafé, Yassa-Hähnchen: Westafrikanische Gerichte gelingen mit Zutaten aus dem Marché Mvog-Mbi in Sherbrooke.",
                    "Grieß und Mehl: Attiéké, weißer und gelber Gari, Fonio, Yamsmehl (Elubo), Hirse- und Sorghummehl, Banku-Mischungen. Gemüse und Knollen: Yams, Okra, Kochbananen. Zum Kochen: Palmöl, Egusi-Samen, Räucher- und Trockenfisch, Gewürze und Brühwürfel. Und zum Trinken: Bissap-Säfte und -Sirupe."]),
        },
    },
    {
        "fichier": "produits-caraibes.html", "region": "caraibes",
        "mots": ["ackee", "djon", "jerk", "scotch", "malta", "grace", "island spice", "jamaica", "haiti", "bigga",
                 "creole", "champagne"],
        "recherches": ["ackee", "djon djon", "jerk", "scotch bonnet", "malta", "kola", "grace"],
        "textes": {
            "fr": ("Produits antillais et haïtiens | Marché Mvog-Mbi Sherbrooke",
                   "Ackee, djon-djon, sauces et marinades jerk, piment scotch bonnet, boissons malta et kola : les produits d’Haïti, de la Jamaïque et des Antilles à Sherbrooke.",
                   "Produits des Caraïbes : Haïti, Jamaïque, Antilles",
                   ["Griot et bananes pesées, diri djon-djon, soup joumou, ackee et morue, poulet jerk, accras de morue : les plats des Caraïbes ont leur place au Marché Mvog-Mbi, à Sherbrooke.",
                    "Vous y trouvez l’ackee en conserve, le djon-djon, les sauces, marinades et assaisonnements jerk, le sel au piment scotch bonnet, les haricots et les conserves des îles, les plantains, ainsi que les boissons malta et kola. De nouveaux arrivages complètent le rayon chaque semaine."]),
            "en": ("Caribbean & Haitian Food in Sherbrooke | Marché Mvog-Mbi",
                   "Ackee, djon djon, jerk sauces and marinades, scotch bonnet salt, malta and kola drinks: products from Haiti, Jamaica and the West Indies in Sherbrooke.",
                   "Caribbean products: Haiti, Jamaica, West Indies",
                   ["Griot with fried plantains, diri djon djon, soup joumou, ackee and saltfish, jerk chicken, salt cod fritters: Caribbean dishes have their place at Marché Mvog-Mbi in Sherbrooke.",
                    "You will find canned ackee, djon djon mushrooms, jerk sauces, marinades and seasonings, scotch bonnet salt, island beans and canned goods, plantains, as well as malta and kola drinks. New arrivals fill the aisle every week."]),
            "es": ("Productos del Caribe y de Haití | Marché Mvog-Mbi Sherbrooke",
                   "Ackee, djon djon, salsas y adobos jerk, sal con ají scotch bonnet, bebidas malta y kola: productos de Haití, Jamaica y las Antillas en Sherbrooke.",
                   "Productos del Caribe: Haití, Jamaica, Antillas",
                   ["Griot con plátanos fritos, diri djon djon, soup joumou, ackee con bacalao, pollo jerk, buñuelos de bacalao: los platos del Caribe tienen su lugar en el Marché Mvog-Mbi de Sherbrooke.",
                    "Encontrarás ackee en conserva, djon djon, salsas, adobos y condimentos jerk, sal con ají scotch bonnet, frijoles y conservas de las islas, plátanos y bebidas malta y kola. Cada semana llegan novedades a la sección."]),
            "pt": ("Produtos do Caribe e do Haiti | Marché Mvog-Mbi Sherbrooke",
                   "Ackee, djon djon, molhos e marinadas jerk, sal com pimenta scotch bonnet, bebidas malta e kola: produtos do Haiti, da Jamaica e das Antilhas em Sherbrooke.",
                   "Produtos do Caribe: Haiti, Jamaica, Antilhas",
                   ["Griot com banana frita, diri djon djon, soup joumou, ackee com bacalhau, frango jerk, bolinhos de bacalhau: os pratos do Caribe têm o seu lugar no Marché Mvog-Mbi, em Sherbrooke.",
                    "Você encontra ackee em conserva, djon djon, molhos, marinadas e temperos jerk, sal com pimenta scotch bonnet, feijões e conservas das ilhas, banana-da-terra e bebidas malta e kola. Novidades chegam à seção toda semana."]),
            "it": ("Prodotti dei Caraibi e di Haiti | Marché Mvog-Mbi Sherbrooke",
                   "Ackee, djon djon, salse e marinate jerk, sale al peperoncino scotch bonnet, bevande malta e kola: prodotti di Haiti, Giamaica e Antille a Sherbrooke.",
                   "Prodotti dei Caraibi: Haiti, Giamaica, Antille",
                   ["Griot con platani fritti, diri djon djon, soup joumou, ackee e baccalà, pollo jerk, frittelle di baccalà: i piatti dei Caraibi hanno il loro posto al Marché Mvog-Mbi di Sherbrooke.",
                    "Trovi ackee in scatola, djon djon, salse, marinate e condimenti jerk, sale al peperoncino scotch bonnet, fagioli e conserve delle isole, platani e bevande malta e kola. Ogni settimana nuovi arrivi completano il reparto."]),
            "de": ("Karibische & haitianische Produkte | Marché Mvog-Mbi",
                   "Ackee, Djon-Djon, Jerk-Soßen und -Marinaden, Scotch-Bonnet-Salz, Malta- und Kola-Getränke: Produkte aus Haiti, Jamaika und den Antillen in Sherbrooke.",
                   "Produkte aus der Karibik: Haiti, Jamaika, Antillen",
                   ["Griot mit gebratenen Kochbananen, Diri Djon-Djon, Soup Joumou, Ackee mit Stockfisch, Jerk-Hähnchen, Stockfisch-Krapfen: Karibische Gerichte haben ihren Platz im Marché Mvog-Mbi in Sherbrooke.",
                    "Sie finden Ackee in Dosen, Djon-Djon-Pilze, Jerk-Soßen, -Marinaden und -Gewürze, Scotch-Bonnet-Salz, Bohnen und Konserven der Inseln, Kochbananen sowie Malta- und Kola-Getränke. Jede Woche kommen neue Produkte hinzu."]),
        },
    },
    {
        "fichier": "meches-beaute-afro.html", "region": None, "rayons": ["Mèches & accessoires", "Beauté"],
        "mots": [], "recherches": [],
        "textes": {
            "fr": ("Mèches et beauté afro à Sherbrooke | Marché Mvog-Mbi",
                   "Mèches pour tresses, vanilles et crochet braids en plusieurs couleurs, soins des cheveux et de la peau : le rayon beauté afro du Marché Mvog-Mbi, à Sherbrooke.",
                   "Mèches et beauté afro",
                   ["Tresses, vanilles, nattes collées, crochet braids : le Marché Mvog-Mbi propose un grand choix de mèches synthétiques, en plusieurs longueurs et couleurs (noir naturel, brun, blond miel, bourgogne, ombrés…). Chaque fiche indique les couleurs offertes.",
                    "Le rayon beauté complète l’offre : soins capillaires, huiles, crèmes et produits pour la peau, ainsi que des accessoires de coiffure."]),
            "en": ("Braiding Hair & Afro Beauty in Sherbrooke | Marché Mvog-Mbi",
                   "Braiding hair for box braids, twists and crochet braids in many colours, hair and skin care: the afro beauty aisle of Marché Mvog-Mbi in Sherbrooke.",
                   "Braiding hair and afro beauty",
                   ["Box braids, twists, cornrows, crochet braids: Marché Mvog-Mbi offers a wide choice of synthetic braiding hair in several lengths and colours (natural black, brown, honey blonde, burgundy, ombré…). Each product page lists the colours available.",
                    "The beauty aisle completes the range: hair care, oils, creams and skin care products, as well as hair accessories."]),
            "es": ("Extensiones y belleza afro en Sherbrooke | Marché Mvog-Mbi",
                   "Extensiones para trenzas, twists y crochet braids en varios colores, cuidado del cabello y de la piel: la belleza afro del Marché Mvog-Mbi en Sherbrooke.",
                   "Extensiones y belleza afro",
                   ["Trenzas, twists, trenzas pegadas, crochet braids: el Marché Mvog-Mbi ofrece una gran variedad de extensiones sintéticas en varios largos y colores (negro natural, castaño, rubio miel, borgoña, ombré…). Cada ficha indica los colores disponibles.",
                    "La sección de belleza completa la oferta: cuidado del cabello, aceites, cremas y productos para la piel, además de accesorios de peinado."]),
            "pt": ("Apliques e beleza afro em Sherbrooke | Marché Mvog-Mbi",
                   "Apliques para tranças, twists e crochet braids em várias cores, cuidados com o cabelo e a pele: a seção de beleza afro do Marché Mvog-Mbi, em Sherbrooke.",
                   "Apliques e beleza afro",
                   ["Tranças, twists, tranças nagô, crochet braids: o Marché Mvog-Mbi oferece uma grande variedade de apliques sintéticos em vários comprimentos e cores (preto natural, castanho, loiro mel, bordô, ombré…). Cada ficha indica as cores disponíveis.",
                    "A seção de beleza completa a oferta: cuidados com o cabelo, óleos, cremes e produtos para a pele, além de acessórios de penteado."]),
            "it": ("Extension e bellezza afro a Sherbrooke | Marché Mvog-Mbi",
                   "Extension per trecce, twist e crochet braids in molti colori, cura dei capelli e della pelle: il reparto bellezza afro del Marché Mvog-Mbi di Sherbrooke.",
                   "Extension e bellezza afro",
                   ["Trecce, twist, cornrows, crochet braids: il Marché Mvog-Mbi offre un’ampia scelta di extension sintetiche in diverse lunghezze e colori (nero naturale, castano, biondo miele, bordeaux, ombré…). Ogni scheda indica i colori disponibili.",
                    "Il reparto bellezza completa l’offerta: cura dei capelli, oli, creme e prodotti per la pelle, oltre ad accessori per acconciature."]),
            "de": ("Haarteile & Afro-Beauty in Sherbrooke | Marché Mvog-Mbi",
                   "Haarteile für Box Braids, Twists und Crochet Braids in vielen Farben, Haar- und Hautpflege: die Afro-Beauty-Abteilung des Marché Mvog-Mbi in Sherbrooke.",
                   "Haarteile und Afro-Beauty",
                   ["Box Braids, Twists, Cornrows, Crochet Braids: Der Marché Mvog-Mbi bietet eine große Auswahl an synthetischen Haarteilen in mehreren Längen und Farben (Naturschwarz, Braun, Honigblond, Burgund, Ombré…). Jede Produktseite nennt die erhältlichen Farben.",
                    "Die Beauty-Abteilung ergänzt das Angebot: Haarpflege, Öle, Cremes und Hautpflegeprodukte sowie Haaraccessoires."]),
        },
    },
]
FICHIERS = [th["fichier"] for th in THEMES]


def normal(t: str) -> str:
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()


def produits_du_theme(theme: dict, produits: list[dict]) -> list[dict]:
    """Produits avec vraie photo ; un par mot-clé à tour de rôle, pour montrer de la variété."""
    avec_photo = [p for p in produits if p.get("photo") and not p.get("illustration")]
    if theme.get("rayons"):
        listes = [[p for p in avec_photo if p["rayon"] == r] for r in theme["rayons"]]
    else:
        listes = [[p for p in avec_photo if re.search(r"\b" + re.escape(m), normal(p["nom"]))] for m in theme["mots"]]
    choisis, vus = [], set()
    while len(choisis) < NB_PRODUITS and any(listes):
        for liste in listes:
            while liste and liste[0]["id"] in vus:
                liste.pop(0)
            if liste:
                p = liste.pop(0)
                vus.add(p["id"])
                choisis.append(p)
                if len(choisis) == NB_PRODUITS:
                    break
    return choisis


def recettes_du_theme(theme: dict, langue: str) -> list[tuple[str, str, str, str]]:
    """(id, titre, pays, photo) des recettes dont un pays est dans la région du thème."""
    if not theme.get("region"):
        return []
    pays_region = dict(filtre_pays.REGIONS)[theme["region"]]
    cat = pages_produits.Catalogue(langue)
    recettes = json.loads((SITE / "data" / "recettes.json").read_text(encoding="utf-8"))
    sortie = []
    for r in recettes:
        if any(p in pays_region for p in filtre_pays.couper(r["pays"], "fr")):
            titre, pays = cat.recettes[r["id"]]
            sortie.append((r["id"], titre, pays, r["photo"]))
    return sortie


def tuiles_themes(langue: str, sauf: str | None = None) -> str:
    """Tuiles vers les pages thématiques (page Rayons, bas de chaque page thématique)."""
    produits = json.loads((SITE / "data" / "produits.json").read_text(encoding="utf-8"))["produits"]
    tuiles = []
    for th in THEMES:
        if th["fichier"] == sauf:
            continue
        titre, _, h1, _ = th["textes"][langue]
        choix = produits_du_theme(th, produits)
        img = f'<img src="{e(choix[0]["photo"])}" alt="{e(h1)}" loading="lazy">' if choix else ""
        nom = h1.split(":")[0].strip()
        detail = h1.split(":", 1)[1].strip() if ":" in h1 else ""
        tuiles.append(f'          <a class="tuile" href="{th["fichier"]}">{img}<strong>{e(nom)}</strong><span>{e(detail)}</span></a>')
    return "\n".join(tuiles)


def pages(langue: str) -> list[dict]:
    lib = LIBELLES[langue]
    t_prod = pages_produits.TEXTES[langue]
    cat = pages_produits.Catalogue(langue)
    d = json.loads((SITE / "data" / "produits.json").read_text(encoding="utf-8"))
    rayons_en = dict(zip(d["rayons"], d["rayons_en"]))
    sortie = []
    for th in THEMES:
        titre, description, h1, paragraphes = th["textes"][langue]
        produits = produits_du_theme(th, cat.produits)
        cartes = "\n".join(pages_produits.vignette(p, cat, t_prod) for p in produits)
        if th.get("rayons"):
            liens = [(f"boutique.html?rayon={quote_plus(r)}", cat.rayon({"rayon": r, "rayon_en": rayons_en.get(r)}))
                     for r in th["rayons"]]
        else:
            liens = [(f"boutique.html?q={quote_plus(q)}", q) for q in th["recherches"]]
        recherches = "".join(f'<li><a href="{e(u)}">{e(n)}</a></li>' for u, n in liens)
        recettes = recettes_du_theme(th, langue)
        bloc_recettes = ""
        if recettes:
            tuiles = "\n".join(f'          <a class="tuile" href="recette-{rid}.html"><img src="{e(photo)}" alt="{e(t)}" loading="lazy">'
                               f'<em class="tuile-nombre">{e(pays)}</em><strong>{e(t)}</strong></a>'
                               for rid, t, pays, photo in recettes[:8])
            bloc_recettes = f'''    <section class="section">
      <div class="conteneur">
        <h2>{lib["recettes"]}</h2>
        <div class="tuiles">
{tuiles}
        </div>
      </div>
    </section>
'''
        texte = "\n".join(f"        <p>{p}</p>" for p in paragraphes + [FIN[langue]])
        contenu = f'''  <main>
    <section class="entete-page">
      <div class="conteneur">
        <p class="surtitre">{lib["surtitre"]}</p>
        <h1>{e(h1)}</h1>
      </div>
    </section>
    <section class="section section-blanche section-locale">
      <div class="conteneur texte-local">
{texte}
        <h2 class="theme-chercher">{lib["chercher"]}</h2>
        <ul class="pastilles pastilles-liens">{recherches}</ul>
      </div>
    </section>
    <section class="section">
      <div class="conteneur">
        <div class="tete-section">
          <div><h2>{lib["phares"]}</h2></div>
          <a href="boutique.html" class="bouton bouton-clair">{lib["tout"]}</a>
        </div>
        <div class="produits">
{cartes}
        </div>
      </div>
    </section>
{bloc_recettes}    <section class="section section-blanche">
      <div class="conteneur">
        <h2>{lib["autres"]}</h2>
        <div class="tuiles">
{tuiles_themes(langue, th["fichier"])}
        </div>
      </div>
    </section>
  </main>
'''
        photo = produits[0]["photo"] if produits else "images/logo.png"
        sortie.append({"fichier": th["fichier"], "contenu": contenu, "titre": titre, "description": description,
                       "photo": photo})
    return sortie


def section_rayons(langue: str) -> str:
    """Bloc ajouté au bas de la page Rayons : liens vers les pages thématiques."""
    return f'''    <section class="section section-blanche">
      <div class="conteneur">
        <p class="surtitre">{LIBELLES[langue]["surtitre"]}</p>
        <h2>{LIBELLES[langue]["selections"]}</h2>
        <div class="tuiles">
{tuiles_themes(langue)}
        </div>
      </div>
    </section>
'''
