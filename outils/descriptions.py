"""Description de chaque produit du site.

La description assemble : ce qu'est le produit et comment on le cuisine (d'après sa sorte, reconnue dans son
nom), puis ce que l'on sait de l'article lui-même (marque et origine d'Open Food Facts, conditionnements, couleurs).
Rien n'est inventé sur l'article : les phrases générales décrivent la sorte de produit.
Une description écrite par le propriétaire dans data/fiches.json passe toujours avant.
"""
from __future__ import annotations

import re
import unicodedata

# (motif dans le nom normalisé, description de la sorte, recettes liées) — du plus précis au plus général
SORTES = [
    (r"\barome|essence de|extrait de", "Arôme ou essence pour parfumer les gâteaux, les beignets, les crèmes et les boissons. Quelques gouttes suffisent.", []),
    (r"nouille|noodle|ramen|indomie|buldak|samyang|mi goreng", "Nouilles instantanées prêtes en quelques minutes, à préparer en soupe ou sautées, avec leur sachet d’assaisonnement.", []),
    (r"jus de (citron|lime)|lemon juice|lime juice", "Jus de citron ou de lime pour les marinades, les sauces, les vinaigrettes et les boissons.", ["attieke-poisson"]),
    (r"spaghetti|penne|fettuc|macaroni|coquillage|rigate|lasagn|vermicell|linguin|fusilli|pates alimentaires", "Pâtes alimentaires pour les plats du quotidien : en sauce tomate, à la viande, en gratin ou en salade.", []),
    (r"\bsel\b|salt", "Sel pour la cuisine et la table.", []),
    (r"levure|yeast", "Levure pour faire lever le pain, les beignets (puff-puff) et les pâtisseries.", []),
    (r"beurre|margarine|blue band|jadida|butter", "Beurre ou margarine pour les tartines, la cuisson et la pâtisserie.", []),
    (r"pierre a ecraser|caillou a ecraser|mortier|pilon", "Pierre à écraser traditionnelle pour moudre les épices, le piment, l’ail et le gingembre comme au pays.", []),
    (r"balai|peigne|sac reutilisable|glue|colle", "Article utile pour la maison, en vente au magasin.", []),
    (r"saumon|salmon", "Saumon pour les salades, les sandwichs ou un repas vite préparé.", []),
    (r"tamal|sancocho|pupusa|empanada", "Spécialité d’Amérique latine prête à réchauffer : tamales, empanadas, sancocho…", []),
    (r"nacho|tortilla chips|doritos|takis|yupi|rizadas|taquerito|jalapeno", "Croustilles et grignotines aux saveurs d’Amérique latine, parfaites pour l’apéritif ou la collation.", []),
    (r"poivre africain|4 cote|pepe|soumara|soumbala", "Épice traditionnelle d’Afrique de l’Ouest et centrale (pèbè, 4 côtés, soumbala), qui donne aux sauces et aux soupes leur goût profond.", []),
    (r"assouplis|downy|fabric softener", "Assouplissant pour un linge doux et parfumé.", []),
    (r"menthol|baume|balm", "Baume ou produit mentholé pour le soin et le bien-être.", []),
    (r"attieke", "L’attiéké est une semoule de manioc fermenté cuite à la vapeur, spécialité de la Côte d’Ivoire. Légèrement acidulé et moelleux, il se réchauffe en quelques minutes et accompagne le poisson braisé, le poulet ou une sauce pimentée.", ["attieke-poisson"]),
    (r"gari|garri", "Le gari est une semoule de manioc râpé, fermenté puis torréfié, très répandue en Afrique de l’Ouest et au Cameroun. On le mange trempé dans de l’eau fraîche avec du sucre et des arachides, ou en « eba », pâte ferme qui accompagne les sauces.", ["eba-sauce-gombo"]),
    (r"pounded yam|iyan|igname pil", "Farine d’igname pilée qui permet de préparer en quelques minutes une pâte lisse et élastique, comme l’igname pilée au mortier. Elle accompagne la soupe egusi, la sauce gombo et toutes les sauces africaines.", ["egusi-foufou"]),
    (r"fufu|foufou|kokonte|banku|kenkey|khom", "Farine pour préparer le foufou, la pâte qui accompagne les sauces d’Afrique de l’Ouest et centrale. Il suffit de la mélanger à l’eau bouillante en remuant jusqu’à obtenir une pâte lisse.", ["egusi-foufou"]),
    (r"tapioca", "Le tapioca est une fécule de manioc en perles ou en grains. Il se prépare en bouillie sucrée au lait, en dessert ou pour épaissir les sauces.", []),
    (r"farine de manioc|cassava flour|farine manioc", "Farine de manioc finement moulue, sans gluten. Elle sert à préparer le foufou de manioc, des galettes et des beignets, et à épaissir les sauces.", ["egusi-foufou"]),
    (r"farine de mais|farine mais|maize|semoule de mais|mais granule|mais blanc gran|mais jaune gran|ugali|polenta", "Farine ou semoule de maïs pour préparer l’ugali, le sadza, la bouillie, le couscous de maïs ou la polenta. Un aliment de base nourrissant dans toute l’Afrique et en Amérique latine.", []),
    (r"farine de riz", "Farine de riz fine, sans gluten, pour les galettes, les beignets, les bouillies et les pâtisseries.", []),
    (r"semoule de ble|semoule de durum|semoule farine de ble|boulgour|bulgur", "Semoule de blé pour le couscous, les galettes, les gâteaux de semoule et les bouillies. Elle se prépare en quelques minutes à l’eau bouillante ou à la vapeur.", []),
    (r"couscous", "Couscous à cuire à la vapeur ou à l’eau bouillante, prêt en quelques minutes. Il accompagne les légumes, les viandes en sauce et les ragoûts.", []),
    (r"plantain chips|chips plantain|plantain chip|chifles|platanitos|mariquitas", "Croustilles de plantain tranchées finement et frites, croquantes et légèrement salées ou épicées. Une collation appréciée partout en Afrique, dans les Caraïbes et en Amérique latine.", []),
    (r"farine de plantain|plantain flour|fufu plantain", "Farine de plantain pour préparer un foufou au goût doux ou des galettes. Riche en fibres et naturellement sans gluten.", ["egusi-foufou"]),
    (r"plantain", "Le plantain est une grosse banane à cuire, incontournable en Afrique et dans les Caraïbes. Vert, il se fait bouillir ou frire en « bananes pesées » ; mûr et jaune, il donne l’alloco ou le plantain frit sucré.", ["alloco", "griot-bananes-pesees"]),
    (r"banane", "Bananes fraîches, à manger nature, en dessert, en smoothie ou en beignets.", []),
    (r"manioc|cassava|yuca|yucca", "Le manioc est un tubercule riche en amidon, base de nombreuses cuisines d’Afrique et d’Amérique latine. On le fait bouillir, frire ou piler ; il ne se mange jamais cru.", ["pondu"]),
    (r"igname|\byam\b", "L’igname est un gros tubercule à la chair blanche ou jaune, ferme et farineuse. Bouillie, frite ou pilée, elle accompagne les sauces et les ragoûts.", ["egusi-foufou"]),
    (r"macabo|malanga|taro|eddo", "Tubercule tropical à la chair douce et légèrement collante. Bouilli, il accompagne les sauces ; râpé, il sert à préparer des mets traditionnels comme le « ekwang ».", []),
    (r"patate douce|sweet potato", "La patate douce a une chair sucrée et fondante. Bouillie, frite, rôtie au four ou en purée, elle accompagne viandes et poissons.", []),
    (r"ndole", "Le ndolé est un plat national du Cameroun préparé avec les feuilles amères du même nom, des arachides, des crevettes et de la viande ou du poisson. Ces feuilles sont prêtes à cuisiner.", ["ndole"]),
    (r"pondu|saka saka|feuilles? de manioc|cassava leaves|kwanga", "Feuilles de manioc pilées, prêtes à cuisiner, pour le pondu congolais ou le saka-saka. Elles mijotent longuement avec de l’huile de palme, de l’oignon et du poisson salé.", ["pondu"]),
    (r"eru|okok|fumbwa|gnetum", "Feuilles d’eru (okok, fumbwa), finement tranchées, pour préparer le plat d’eru camerounais ou le fumbwa congolais avec de l’huile de palme, des feuilles d’eau et de la viande ou du poisson fumé.", []),
    (r"bobolo|miondo|chikwangue|baton de manioc|kwanga", "Bâton de manioc fermenté, cuit dans des feuilles. Il se mange en accompagnement du ndolé, du poisson braisé ou des sauces, tiède ou réchauffé à la vapeur.", ["ndole"]),
    (r"placali", "Le placali est une pâte de manioc fermenté de Côte d’Ivoire, servie avec la sauce graine, la sauce gombo ou la sauce kplala.", []),
    (r"egusi|pistache|graines? de courge|melon seed", "Les graines de courge (egusi, pistache) moulues épaississent et parfument les sauces. Elles sont la base de la soupe egusi nigériane et de nombreux plats camerounais.", ["egusi-foufou"]),
    (r"huile de palme|palm oil", "Huile de palme rouge non raffinée, au goût prononcé et à la couleur vive. Elle est indispensable au pondu, à l’eru, à la sauce graine et à de nombreux plats d’Afrique de l’Ouest et centrale.", ["pondu", "egusi-foufou"]),
    (r"huile d.arachide|peanut oil|groundnut oil", "Huile d’arachide au goût doux, qui supporte bien la chaleur : idéale pour les fritures, les plantains et les beignets.", ["alloco"]),
    (r"huile", "Huile de cuisson pour les fritures, les sauces et les marinades.", []),
    (r"pate d.arachide|beurre d.arachide|peanut butter", "Pâte d’arachide pure, base de la sauce arachide (mafé), du poulet à l’arachide et de nombreux plats d’Afrique de l’Ouest et centrale.", ["mafe"]),
    (r"arachide|peanut|groundnut|cacahuete", "Arachides à griller, à moudre ou à cuisiner : en collation, dans le ndolé, la sauce arachide ou les bonbons de pays.", ["ndole", "mafe"]),
    (r"haricot|bean|niebe|koki|pois", "Légumineuses riches en protéines et en fibres. Elles se cuisinent en ragoût, en purée, en beignets (akara) ou en gâteau vapeur comme le koki.", []),
    (r"lentille", "Lentilles riches en protéines, rapides à cuire, pour les soupes, les ragoûts et les salades.", []),
    (r"\briz\b|rice|basmati|jasmin", "Riz pour accompagner les sauces, le poulet DG, le poisson ou pour préparer le riz jollof et le riz gras.", ["poulet-dg"]),
    (r"poivre de penja|poivre blanc|poivre noir", "Poivre au parfum intense, pour relever viandes, poissons et sauces.", []),
    (r"njansang|djansang|djansan", "Le njansang (djansan) est une graine d’Afrique centrale au goût de noisette, moulue pour épaissir et parfumer les sauces et les grillades.", []),
    (r"rondelle|jansang|ndjansang|bush pepper|poivre de guinee|graine de selim|kieng|mbongo|pebe|4 cotes|esese", "Épice traditionnelle d’Afrique centrale et de l’Ouest, qui donne leur goût aux sauces noires, aux soupes et aux bouillons comme le mbongo ou le pepper soup.", []),
    (r"cube|maggi|jumbo|bouillon|onga|knorr|adja", "Cubes et assaisonnements pour donner du goût aux sauces, aux riz et aux bouillons.", []),
    (r"piment|pepper|chili|habanero", "Piment pour relever les sauces, les marinades et les grillades. À doser selon votre goût.", ["attieke-poisson"]),
    (r"epice|spice|curry|soumbala|dawadawa|iru", "Épices et condiments pour parfumer les plats d’Afrique, des Caraïbes et d’ailleurs.", []),
    (r"tomate", "Tomates pour les sauces, les ragoûts et le riz jollof.", ["poulet-dg"]),
    (r"oignon|onion", "Oignons pour les sauces, les marinades et les fritures : la base de presque tous les plats.", []),
    (r"\bail\b|garlic", "Ail pour parfumer les sauces, les marinades et les grillades.", []),
    (r"gingembre|ginger", "Gingembre frais ou sec pour les marinades, les sauces et le jus de gingembre (gnamakoudji).", []),
    (r"gombo|okra", "Le gombo donne aux sauces leur texture onctueuse. On le cuisine en sauce gombo, en soupe ou sauté.", ["eba-sauce-gombo"]),
    (r"safou|safour", "Le safou (prune d’Afrique) se mange légèrement cuit à l’eau ou braisé, souvent avec du bâton de manioc ou du maïs grillé.", []),
    (r"mangue|mango", "Mangues juteuses et parfumées, à manger nature, en jus ou en salade de fruits.", []),
    (r"ananas|pineapple", "Ananas frais, sucré et acidulé, à manger nature ou en jus.", []),
    (r"avocat|avocado", "Avocats à la chair fondante, en salade, en tartine ou en guacamole.", []),
    (r"aubergine|garden egg", "Aubergines pour les sauces, les ragoûts et les grillades.", []),
    (r"crevette|shrimp|prawn|crayfish", "Crevettes séchées ou fumées qui donnent un goût marin profond au ndolé, aux sauces et aux soupes.", ["ndole"]),
    (r"poisson.*fume|fume.*poisson|smoked fish|machoiron|kobapot|konkoe|bounga|catfish fume|brochet fume|capitaine fume", "Poisson fumé au goût intense, qui parfume les sauces gombo, les soupes et les légumes-feuilles.", ["eba-sauce-gombo"]),
    (r"stockfish|morue|bacalao|salted fish|poisson sale", "Poisson séché ou salé à faire tremper avant la cuisson, pour les sauces, les légumes-feuilles et les ragoûts.", ["pondu"]),
    (r"tilapia|capitaine|bar |sole|dorade|bream|snapper|vivaneau|redfish|bonito|thon|maquereau|chinchard|mackerel|croaker|merlu|basa|pangasius|poisson", "Poisson à braiser, frire ou cuisiner en sauce. Bien assaisonné, il accompagne l’attiéké, les plantains ou le riz.", ["attieke-poisson"]),
    (r"escargot", "Escargots africains à cuisiner en sauce pimentée ou en ragoût, une spécialité appréciée d’Afrique centrale et de l’Ouest.", []),
    (r"poulet|poule|chicken|gesier", "Volaille à griller, braiser ou cuisiner en sauce, pour le poulet DG, le poulet braisé ou le yassa.", ["poulet-dg", "mafe"]),
    (r"dinde|turkey", "Dinde (ailes, pilons, croupion) à griller, à fumer ou à cuisiner en sauce, très appréciée dans les cuisines africaines et caribéennes.", []),
    (r"chevre|goat|mouton|agneau|lamb", "Viande de chèvre ou de mouton au goût prononcé, pour les ragoûts, le pepper soup et les grillades.", []),
    (r"boeuf|beef|tripe|rognon|langue|queue de boeuf|peau", "Viande de bœuf pour les sauces, les ragoûts, les soupes et les grillades.", ["mafe"]),
    (r"porc|pork", "Viande de porc à mariner, frire ou braiser : pour le griot haïtien ou les ragoûts.", ["griot-bananes-pesees"]),
    (r"lapin|rabbit", "Viande de lapin tendre et maigre, à braiser ou cuisiner en sauce.", []),
    (r"malta|malt", "Boisson maltée non alcoolisée, douce et rafraîchissante, très populaire en Afrique et dans les Caraïbes.", []),
    (r"biere|beer|guinness|33 export|castel|leffe", "Bière à servir bien fraîche, avec modération. Vente aux personnes majeures seulement.", []),
    (r"bissap|hibiscus|oseille|sorrel", "Fleurs d’hibiscus (bissap, oseille) pour préparer une boisson rafraîchissante et acidulée, servie froide avec de la menthe ou du gingembre.", []),
    (r"jus|juice|nectar|soda|boisson|drink", "Boisson à servir bien fraîche.", []),
    (r"milo|ovaltine|cacao|chocolat chaud", "Boisson chocolatée en poudre, à préparer au lait chaud ou froid au petit-déjeuner.", []),
    (r"the |the$|\bthe\b|tea|infusion|cafe|coffee|kinkeliba", "Thé, café ou infusion à préparer chaud ou glacé.", []),
    (r"chocopain|tartina|nutella|chocolat|pate a tartiner", "Pâte à tartiner chocolatée, sur le pain, les crêpes ou les beignets.", []),
    (r"sardine|thon en conserve|conserve|canned", "Conserve pratique à garder au garde-manger, pour un repas vite préparé.", []),
    (r"pate de tomate|tomato paste|concentre de tomate", "Concentré de tomate pour donner couleur et goût aux sauces, au riz jollof et aux ragoûts.", ["poulet-dg"]),
    (r"biscuit|cookie|parle|croustille|chips|bonbon|candy|snack", "Une collation à grignoter ou à glisser dans la boîte à lunch.", []),
    (r"perruque|wig", "Perruque prête à porter, pour changer de coiffure en quelques minutes.", []),
    (r"leaves of haiti|feuilles? de (cafe|mangue|corossol|citronnelle|bois|arang|the)|bois dine|haiti(en)?.*(feuille|the)", "Feuilles séchées venues d’Haïti, utilisées en infusion selon la tradition caribéenne : on les laisse infuser quelques minutes dans l’eau bouillante.", []),
    (r"epis|pikliz|haitien|haiti", "Produit de la cuisine haïtienne, pour retrouver les saveurs d’Haïti à la maison : épis, pikliz, griot, diri ak pwa…", ["griot-bananes-pesees"]),
    (r"jerk|grace|jamaica|caribbean|caraibe", "Assaisonnement ou produit de la cuisine jamaïcaine et caribéenne, pour le poulet jerk, le riz aux pois et les marinades épicées.", []),
    (r"feuilles?|leaves|matembele|ademe|kwi|massep|ngai|water leaf|bitekuteku|djama|amaranth|lumba|basilic africain", "Légumes-feuilles africains, prêts à cuisiner, pour les sauces vertes, les soupes et les plats mijotés à l’huile de palme ou à l’arachide.", []),
    (r"sorgho|petit mil|mil|fonio|millet|degue|thiacry|monikrou|araw", "Céréale traditionnelle d’Afrique de l’Ouest (mil, sorgho, fonio), sans gluten, pour les bouillies, le couscous de mil, le dêguê ou le thiacry.", []),
    (r"bouillie|akassa|ogi|pap\b|koko|ema", "Préparation pour bouillie traditionnelle, servie chaude au petit-déjeuner, sucrée ou nature, avec des beignets ou des arachides.", []),
    (r"noix de coco|coco|coconut", "Produit à la noix de coco : lait, crème, eau ou pulpe pour les sauces, les desserts et les boissons.", []),
    (r"noix de kola|kola|bitter kola|garcinia", "Noix de kola ou kola amère, partagée en signe d’accueil et d’amitié dans de nombreuses cultures d’Afrique de l’Ouest.", []),
    (r"noix|nuts|cajou|cashew|amande|almond", "Fruits à coque pour grignoter ou cuisiner, riches en bonnes graisses.", []),
    (r"queso|fromage|cheese", "Fromage à cuisiner ou à déguster, pour les arepas, les pupusas, les sandwichs et les plats gratinés.", []),
    (r"mayonnaise|vinaigrette|vinaigre|moutarde|mustard|ketchup|hot sauce|salsa", "Condiment pour accompagner les salades, les sandwichs, les grillades et les fritures.", []),
    (r"sauce", "Sauce prête à l’emploi pour relever les plats, les grillades, le riz et les pâtes.", []),
    (r"cumin|seasoning|assaisonnement|adobo|sazon|curcuma|paprika|thym|laurier|cannelle|muscade|clou de girofle|anis", "Épice ou mélange d’assaisonnement pour parfumer les viandes, les poissons, le riz et les sauces.", []),
    (r"sucre|sugar|panela|piloncillo|cassonade", "Sucre pour les boissons, les desserts et la pâtisserie.", []),
    (r"miel|honey", "Miel pour sucrer naturellement les boissons chaudes, les tartines et les desserts.", []),
    (r"caramel|vanill|arome|essence|levure|baking|gelatine|natilla|flan|pudding|custard", "Ingrédient de pâtisserie pour les desserts, les gâteaux, les crèmes et les flans.", []),
    (r"lait|milk|evaporated|condense|peak|nido|laicran", "Lait en poudre, concentré ou évaporé, pour le café, le thé, les bouillies et les desserts.", []),
    (r"soja|soy|tofu", "Produit à base de soja pour la cuisine du quotidien et les plats asiatiques.", []),
    (r"olive", "Produit à l’olive (huile ou olives) pour les salades, les marinades et la cuisine méditerranéenne.", []),
    (r"tortilla|tostada|taco", "Tortillas de maïs ou de blé pour les tacos, les quesadillas, les enchiladas et les burritos.", []),
    (r"arepa|harina pan|masa|harina", "Farine de maïs précuite pour préparer les arepas, les empanadas, les tamales et les pupusas d’Amérique latine.", []),
    (r"frijol|feves?|refried|black beans|garbanzo|chiche", "Légumineuses de la cuisine latine et méditerranéenne : frijoles, fèves et pois chiches, en ragoût, en purée ou en salade.", []),
    (r"gatorade|powerade|electrolyte|sport", "Boisson pour sportifs, pour se réhydrater après l’effort.", []),
    (r"labatt|budweiser|corona|busch|heineken|stella|molson|coors|bud light|presidente|smirnoff|ice", "Bière à servir bien fraîche, avec modération. Vente aux personnes majeures seulement.", []),
    (r"punch|sirop|syrup|grenadine|cordial", "Sirop ou punch à allonger d’eau ou à servir sur glace.", []),
    (r"croquette|galleta|biscuit|wafer|gaufrette|cracker|crakena", "Biscuits et croquants pour la collation, le café ou la boîte à lunch.", []),
    (r"marmite|chaudron|aluminium|casserole|pot\b|mortier|pilon|cuisine|ustensile", "Article de cuisine pour préparer vos plats comme au pays : marmites en aluminium, mortiers et ustensiles.", []),
    (r"vaisselle|lave|dish|savon|soap|desinfect|eau de javel|bleach|eponge", "Produit d’entretien pour la vaisselle et la maison.", []),
    (r"maillot|jersey|drapeau|flag", "Article aux couleurs des équipes et des pays, pour encourager les siens.", []),
    (r"pomme|apple|raisin|grape|orange|citron|lemon|lime|fraise|strawberry|melon|papaye|papaya|goyave|guava|corossol|tamarin|passion", "Fruits ou produits aux fruits, pour croquer, presser ou cuisiner.", []),
    (r"carotte|chou|celeri|concombre|betterave|poivron|haricot vert|courge|chayot|choyot|epinard|laitue", "Légumes frais pour les salades, les ragoûts et les plats sautés.", []),
    (r"meche|braid|twist|curl|locs?|crochet|bulk|x-pression|expression|kanekalon|kankalon", "Mèches synthétiques pour tresses, vanilles, nattes collées et crochet braids, douces et faciles à coiffer.", []),
    (r"creme|lotion|lait corporel|body|savon|soap|shampo|huile capillaire|hair|cheveux|gel|pommade|beurre de karite|karite|shea|cosmet", "Soin pour le corps ou les cheveux, sélectionné pour les peaux et les cheveux afro.", []),
    (r"detergent|lessive|savon en poudre|viva|tide|javel|nettoy", "Produit d’entretien pour la lessive et la maison.", []),
]

RAYONS = {
    "Fruits & légumes": "Produit frais du rayon fruits et légumes, choisi pour la cuisine d’Afrique, des Caraïbes et d’ailleurs.",
    "Féculents": "Tubercule frais pour accompagner les sauces et les ragoûts.",
    "Farines": "Farine pour préparer les pâtes, bouillies et accompagnements traditionnels.",
    "Riz, graines & pâtes": "Produit sec de base pour accompagner les plats du quotidien.",
    "Épices & sauces": "Épice, sauce ou condiment pour donner du goût à vos plats.",
    "Huiles": "Huile pour la cuisson et l’assaisonnement.",
    "Conserves": "Conserve pratique à garder au garde-manger.",
    "Produits de la mer": "Produit de la mer pour les sauces, les grillades et les soupes.",
    "Viandes & volailles": "Viande ou volaille pour vos sauces, ragoûts et grillades.",
    "Légumes congelés": "Produit congelé, prêt à cuisiner, qui garde le goût du frais.",
    "Boissons": "Boisson à servir bien fraîche.",
    "Thés & cafés": "À préparer chaud ou glacé.",
    "Collations": "Une collation à grignoter.",
    "Tartinades": "À tartiner sur le pain, les crêpes ou les beignets.",
    "Produits latinos": "Un produit d’Amérique latine pour cuisiner les saveurs du Mexique, d’Amérique centrale et du Sud.",
    "Beauté": "Soin pour le corps ou les cheveux.",
    "Mèches & accessoires": "Pour vos coiffures : mèches, perruques et accessoires.",
    "Entretien": "Produit d’entretien pour la maison.",
    "Autres produits": "Un produit de notre sélection d’épicerie fine d’Afrique, des Caraïbes et d’Amérique latine, en vente au Marché Mvog-Mbi.",
}


def normal(t: str) -> str:
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t)


def sorte(nom: str) -> tuple[str, list[str]] | None:
    n = normal(nom)
    for motif, texte, recettes in SORTES:
        if re.search(motif, n):
            return texte, recettes
    return None


def decrire(p: dict) -> tuple[str, list[str]]:
    """(description, recettes liées) d'un produit du catalogue."""
    trouve = sorte(p["nom"])
    texte, recettes = trouve if trouve else (RAYONS.get(p["rayon"], RAYONS["Autres produits"]), [])
    phrases = [texte]
    car = p.get("caracteristiques", {})
    if car.get("Marque") and normal(car["Marque"]) not in normal(texte):
        phrases.append(f"Marque : {car['Marque']}.")
    if car.get("Origine"):
        phrases.append(f"Origine : {car['Origine']}.")
    if p.get("conditionnements"):
        phrases.append("Offert en " + str(len(p["conditionnements"])) + " formats : " + ", ".join(p["conditionnements"]) + ".")
    if p.get("couleurs"):
        n = len(p["couleurs"])
        phrases.append(f"Offert en {n} couleur{'s' if n > 1 else ''} : voir la liste ci-dessous.")
    if p.get("unite"):
        phrases.append("Vendu au poids, pesé en magasin selon la quantité voulue.")
    return " ".join(phrases), recettes
