"""Une seule fiche pour un produit vendu sous plusieurs noms et en plusieurs conditionnements.

Exemples : « Clic Farine de maïs blanc 907g / 2kg / 5kg », « Plantain Jaune en lb / en caisse / en 1/2 Carton »,
« Haricot Noir Cameroun 2kg » et « Haricot Noir du Cameroun 1kg », « Jus Power Malt 24x330ml » et « 330ml Bouteille ».

Clé du produit : son nom sans le format (poids, volume, nombre), sans les mots de vente (lb, caisse, carton, sac,
spécial, grand, petit…), sans les petits mots (de, du, en…), sans accents, majuscules ni ordre des mots.
Les articles d'un même rayon qui ont la même clé deviennent une fiche : une seule désignation et la liste
« Conditionnements disponibles », du plus petit au plus grand.
"""
from __future__ import annotations

import re
import unicodedata

FORMAT = re.compile(r"(?<![\w#])((?:\d+\s*[xX]\s*)?\d+(?:[.,]\d+)?)\s*(kg|g|gr|mg|lbs?|oz|ml|cl|l|litres?)\b\.?", re.I)
GRAMMES = {"kg": 1000, "g": 1, "gr": 1, "mg": .001, "lb": 453.6, "lbs": 453.6, "oz": 28.35,
           "l": 1000, "litre": 1000, "litres": 1000, "ml": 1, "cl": 10}

# Mots de vente : (expression, libellé, ordre quand il n'y a pas de poids)
MOTS = [
    (r"1/2\s*carton|demi[- ]carton", "½ carton", 5000),
    (r"carton", "carton", 10000),
    (r"caisse", "caisse", 20000),
    (r"sac", "sac", 3000),
    (r"bouteille", "bouteille", 0),
    (r"sp[eé]cial", "spécial", 1),
    (r"petit", "petit", 0),
    (r"grand", "grand", 2000),
    (r"gros", "gros", 2000),
]
AU_LB = re.compile(r"(?<![\d.,\s])\s*\b(?:en\s+)?(lbs?|livres?)\b\.?", re.I)
NOMBRE = re.compile(r"\b(\d+)\s*(?:x|pcs?|pi[eè]ces?|un|unit[eé]s?|ct|pk|pack)\b", re.I)
PETITS_MOTS = {"en", "de", "du", "la", "le", "les", "d", "l", "of", "the", "and", "et", "au", "a"}


def sans_accents(t: str) -> str:
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()


def _format_lu(m: re.Match) -> str:
    unite = m.group(2).lower()
    unite = {"gr": "g", "lbs": "lb", "litre": "L", "litres": "L", "l": "L"}.get(unite, unite)
    quantite = re.sub(r"\s*[xX]\s*", " × ", m.group(1)).replace(".", ",")
    return f"{quantite} {unite}"


def mots_de_vente(nom: str) -> set[str]:
    return {libelle for motif, libelle, _ in MOTS if re.search(r"\b(?:" + motif + r")\b", nom, re.I)}


def _sans_formats(nom: str, garder: set[str] = frozenset()) -> str:
    t = re.sub(r"\([^)]*\)", " ", nom)
    t = FORMAT.sub(" ", t)
    t = NOMBRE.sub(" ", t)
    t = re.sub(r"\b(?:en\s+)?(?:lbs?|livres?)\b\.?", " ", t, flags=re.I)
    for motif, libelle, _ in MOTS:
        if libelle not in garder:
            t = re.sub(r"\b(?:" + motif + r")\b", " ", t, flags=re.I)
    t = re.sub(r"[/\-–]+\s*(?=\s|$)", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def designation(nom: str, garder: set[str] = frozenset()) -> str:
    """Nom sans format ni mot de vente, petits mots de fin retirés (« Plantain Jaune en caisse » -> « Plantain Jaune »).

    `garder` : mots de vente que portent toutes les variantes (« Semoule de blé Gros ») : ils font partie du nom."""
    t = _sans_formats(nom, garder)
    while True:
        u = re.sub(r"\s+\b(?:en|de|du|d|au|et)\s*$", "", t, flags=re.I).strip(" -–/,")
        if u == t:
            return t
        t = u


def cle(nom: str) -> str:
    t = re.sub(r"[^a-z0-9]+", " ", sans_accents(_sans_formats(nom)).lower())
    return " ".join(sorted(set(t.split()) - PETITS_MOTS))


def conditionnement(nom: str, sauf: set[str] = frozenset()) -> str:
    """Libellé du conditionnement d'un article : « Au lb (spécial) », « Carton 33 lb », « 24 × 330 ml », « À l'unité ».

    `sauf` : mots de vente communs à toutes les variantes (ils restent dans le nom du produit)."""
    mots = []
    for motif, libelle, _ in MOTS:
        if libelle in sauf or libelle == "spécial":
            continue
        if re.search(r"\b(?:" + motif + r")\b", nom, re.I) and libelle not in mots:
            if libelle == "carton" and "½ carton" in mots:
                continue
            mots.append(libelle)
    poids = [_format_lu(m) for m in FORMAT.finditer(nom)]
    nombre = NOMBRE.search(re.sub(r"\([^)]*\)", " ", FORMAT.sub(" ", nom)))
    morceaux = mots[:]
    if poids:
        morceaux.append(poids[0] + (f" ({poids[1]})" if len(poids) > 1 else ""))
    elif AU_LB.search(nom):
        morceaux.append("au lb")
    if nombre:
        morceaux.append(f"{nombre.group(1)} unités")
    texte = " ".join(morceaux)
    if "spécial" not in sauf and re.search(r"\bsp[eé]cial\b", nom, re.I):
        texte = texte + " (spécial)" if texte else "spécial"
    texte = texte or "à l'unité"
    return texte[0].upper() + texte[1:]


def poids(fmt: str) -> float:
    m = re.search(r"(?:(\d+) × )?(\d+(?:,\d+)?) (kg|g|mg|lb|oz|ml|cl|L)\b", fmt)
    if m:
        n = int(m.group(1) or 1)
        return n * float(m.group(2).replace(",", ".")) * GRAMMES.get(m.group(3).lower(), 1)
    bas = fmt.lower()
    ordre = max((o for _, libelle, o in MOTS if libelle in bas), default=0)
    if "au lb" in bas:
        ordre = max(ordre, 453.6)
    return ordre + (0.5 if "spécial" in bas else 0)


def regrouper(produits: list[dict]) -> list[dict]:
    groupes: dict[tuple, list[tuple[str, dict]]] = {}
    for p in produits:
        if p.get("couleurs"):
            continue
        k = cle(p["nom"])
        if k:
            groupes.setdefault((p["rayon"], k), []).append(p)
    retires, remplacants = set(), {}
    for articles in groupes.values():
        if len(articles) < 2:
            continue
        communs = set.intersection(*(mots_de_vente(p["nom"]) for p in articles))
        variantes = [(conditionnement(p["nom"], communs), p) for p in articles]
        variantes.sort(key=lambda v: poids(v[0]))
        formats = list(dict.fromkeys(f for f, _ in variantes))
        tete = next((p for _, p in variantes if p["photo"].startswith("images/produits/")),   # photo du marché d'abord
                    None) or next((p for _, p in variantes if p["photo"] and not p.get("illustration")),
                    next((p for _, p in variantes if p["photo"]), variantes[0][1]))
        noms = [designation(p["nom"], communs) for _, p in variantes]
        base = max(noms, key=lambda n: (len(n), n == designation(tete["nom"], communs)))
        fiche = dict(tete)
        fiche.update({"nom": base, "ids": [p["id"] for _, p in variantes]})
        car = {k: v for k, v in tete.get("caracteristiques", {}).items() if k not in ("Code-barres", "Format")}
        if len(formats) > 1:
            fiche["conditionnements"] = formats
            car["Conditionnements disponibles"] = ", ".join(formats)
        else:
            fiche.pop("conditionnements", None)
        fiche["caracteristiques"] = car
        for _, p in variantes:
            retires.add(p["id"])
        remplacants[tete["id"]] = fiche
    return [remplacants.get(p["id"], p) for p in produits if p["id"] in remplacants or p["id"] not in retires]
