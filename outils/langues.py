"""Textes communs en français et en anglais (rayons, couleurs de mèches, caractéristiques)."""

RAYONS_EN = {
    "Fruits & légumes": "Fruits & vegetables", "Féculents": "Roots & tubers", "Farines": "Flours",
    "Riz, graines & pâtes": "Rice, seeds & pasta", "Épices & sauces": "Spices & sauces", "Huiles": "Oils",
    "Conserves": "Canned goods", "Produits de la mer": "Seafood", "Viandes & volailles": "Meat & poultry",
    "Légumes congelés": "Frozen vegetables", "Boissons": "Drinks", "Thés & cafés": "Teas & coffees",
    "Collations": "Snacks", "Tartinades": "Spreads", "Produits latinos": "Latin American products",
    "Beauté": "Beauty", "Mèches & accessoires": "Hair extensions & accessories", "Entretien": "Household",
    "Autres produits": "Other products",
}

TEXTE_RAYON = {
    "Fruits & légumes": ("Plantains, mangues, gombo, piments, ananas", "Plantains, mangoes, okra, peppers, pineapples"),
    "Féculents": ("Igname, macabo, taro, patate douce", "Yam, cocoyam, taro, sweet potato"),
    "Farines": ("Gari, foufou, tapioca, semoule, farines de maïs", "Gari, fufu, tapioca, semolina, corn flours"),
    "Riz, graines & pâtes": ("Riz parfumés, haricots, egusi, arachides", "Fragrant rice, beans, egusi, peanuts"),
    "Épices & sauces": ("Poivre de Penja, cubes, piments, sauces", "Penja pepper, stock cubes, chilies, sauces"),
    "Huiles": ("Huile de palme rouge, arachide, cuisson", "Red palm oil, peanut and cooking oils"),
    "Conserves": ("Légumes, poissons, sauces en conserve", "Canned vegetables, fish and sauces"),
    "Produits de la mer": ("Poissons fumés, crevettes, tilapia", "Smoked fish, shrimp, tilapia"),
    "Viandes & volailles": ("Chèvre, bœuf, poulet, dinde, porc", "Goat, beef, chicken, turkey, pork"),
    "Légumes congelés": ("Ndolé, pondu, attiéké, feuilles", "Ndolé, pondu, attiéké, leafy greens"),
    "Boissons": ("Jus, malts, bières, boissons d’ailleurs", "Juices, malts, beers, drinks from abroad"),
    "Thés & cafés": ("Thés, cafés, infusions", "Teas, coffees, herbal teas"),
    "Collations": ("Croustilles, biscuits, bonbons", "Chips, cookies, candy"),
    "Tartinades": ("Tartinades et confitures", "Spreads and jams"),
    "Produits latinos": ("Le meilleur d’Amérique latine", "The best of Latin America"),
    "Beauté": ("Soins du corps et des cheveux", "Body and hair care"),
    "Mèches & accessoires": ("Mèches, perruques, accessoires", "Braiding hair, wigs, accessories"),
    "Entretien": ("Produits ménagers", "Cleaning products"),
    "Autres produits": ("Tout le reste du magasin", "Everything else in the store"),
}

CARACTERISTIQUES_EN = {
    "Marque": "Brand", "Format": "Size", "Vente": "Sold", "Origine": "Origin", "Ingrédients": "Ingredients",
    "Code-barres": "Barcode", "Conditionnements disponibles": "Available sizes", "Couleurs disponibles": "Available colours",
}
VALEURS_EN = {"Au poids (prix au lb)": "By weight", "Au poids": "By weight"}

COULEURS_EN = {
    "noir de jais": "jet black", "noir naturel": "natural black", "brun très foncé": "darkest brown",
    "brun moyen": "medium brown", "châtain": "light brown", "blond miel": "honey blonde",
    "châtain cuivré": "copper auburn", "auburn foncé": "dark auburn", "cuivre": "copper", "blond platine": "platinum blonde",
    "bordeaux prune": "plum burgundy", "bourgogne": "burgundy", "rouge": "red", "bleu": "blue", "vert": "green",
    "violet": "purple", "roux gingembre": "ginger", "noir": "black", "brun": "brown", "blond foncé": "dark blonde",
}


def couleur_en(fr: str) -> str:
    """« ombré noir naturel vers blond miel » -> « natural black to honey blonde ombré »."""
    if not fr:
        return ""
    t = fr
    for prefixe, modele in (("ombré ", "{} ombré"), ("mélange ", "{} blend")):
        if t.startswith(prefixe):
            reste = t[len(prefixe):]
            sep = " vers " if " vers " in reste else " et "
            a, _, b = reste.partition(sep)
            mot = " to " if sep == " vers " else " and "
            return modele.format(COULEURS_EN.get(a, a) + (mot + COULEURS_EN.get(b, b) if b else ""))
    if " et " in t:
        a, b = t.split(" et ", 1)
        return f"{COULEURS_EN.get(a, a)} and {COULEURS_EN.get(b, b)}"
    return COULEURS_EN.get(t, t)
