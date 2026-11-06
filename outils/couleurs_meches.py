"""Regroupe les mèches vendues en plusieurs couleurs : une seule fiche par modèle, avec la liste des couleurs.

Dans Clover, chaque couleur est un article (« MECHE X-PRESSION PRES STRETCHED 3X 1B 52'' », « … 27 52'' »…).
Le code de couleur est le dernier mot du nom, ou celui juste avant la longueur (52'', 24"). Les codes suivent
la convention des fabricants de mèches : 1B = noir naturel, 27 = blond miel, T… = ombré, FS… = mélange…
"""
from __future__ import annotations

import re

LONGUEUR = re.compile(r"^\d+(''|\"|”|″)$")
COULEUR = re.compile(
    r"^(?:(?:T|FS|F)?(?:1B|\d{1,3}[JB]?)(?:[/-](?:1B|\d{1,3}J?|BUG|RED|BROWN))?|T?(?:BUG|RED|BLUE|GREEN|PURPLE)"
    r"|GINGER|NOIR|C\d|A\d|DYX/BROWN)#?$", re.I)
NOMS = {
    "1": "noir de jais", "1B": "noir naturel", "2": "brun très foncé", "4": "brun moyen", "6": "châtain",
    "27": "blond miel", "30": "châtain cuivré", "33": "auburn foncé", "350": "cuivre", "613": "blond platine",
    "99J": "bordeaux prune", "BUG": "bourgogne", "RED": "rouge", "BLUE": "bleu", "GREEN": "vert",
    "PURPLE": "violet", "GINGER": "roux gingembre", "NOIR": "noir", "BROWN": "brun", "14": "blond foncé",
}


def separer(nom: str) -> list[str]:
    nom = re.sub(r"(''|\"|”|″)(?=[0-9A-Za-z])", r"\1 ", nom)      # « 18''30 » -> « 18'' 30 »
    nom = re.sub(r"\b(PVC)(\d)", r"\1 \2", nom, flags=re.I)         # « PVC27 » -> « PVC 27 »
    return nom.split()


def couleur_du_nom(nom: str) -> tuple[str, str] | None:
    """(nom du modèle sans la couleur, code de couleur), ou None si le nom n'a pas de couleur."""
    mots = separer(nom)
    for i in range(len(mots) - 1, 0, -1):
        if LONGUEUR.match(mots[i]):
            continue
        if COULEUR.match(mots[i]) and not re.match(r"^\d+X$", mots[i], re.I):
            modele = " ".join(mots[:i] + mots[i + 1:])
            code = mots[i].rstrip("#").upper()
            return modele, re.sub(r"^0(\d)$", r"\1", code)
        return None
    return None


def decrire(code: str) -> str:
    """« T1B/30 » -> « ombré noir naturel vers châtain cuivré »."""
    c = code.upper()
    if c.startswith("FS") and re.search(r"[/-]", c):
        a, b = re.split(r"[/-]", c[2:], maxsplit=1)
        return f"mélange {NOMS.get(a, a)} et {NOMS.get(b, b)}"
    if c.startswith("F") and re.search(r"[/-]", c):
        a, b = re.split(r"[/-]", c[1:], maxsplit=1)
        return f"mélange {NOMS.get(a, a)} et {NOMS.get(b, b)}"
    if c.startswith("T") and re.search(r"[/-]", c):
        a, b = re.split(r"[/-]", c[1:], maxsplit=1)
        return f"ombré {NOMS.get(a, a)} vers {NOMS.get(b, b)}"
    if "/" in c or "-" in c:
        a, b = re.split(r"[/-]", c, maxsplit=1)
        return f"{NOMS.get(a, a)} et {NOMS.get(b, b)}"
    if c.startswith("T") and c[1:] in NOMS:
        return f"ombré noir vers {NOMS[c[1:]]}"
    return NOMS.get(c, "")


def ordre(code: str) -> tuple:
    c = code.upper()
    return (c.startswith(("T", "F")), not c[:1].isdigit(), int(re.match(r"\d*", c).group() or 999), c)


def regrouper(produits: list[dict], rayon: str = "Mèches & accessoires") -> list[dict]:
    groupes: dict[str, list[tuple[str, dict]]] = {}
    for p in produits:
        if p["rayon"] != rayon:
            continue
        trouve = couleur_du_nom(p["nom"])
        if trouve:
            groupes.setdefault(re.sub(r"\s+", "", trouve[0].lower()), []).append((trouve[1], p))
    retires, remplacants = set(), {}
    for cle, variantes in groupes.items():
        if len(variantes) < 2:
            continue
        variantes.sort(key=lambda v: ordre(v[0]))
        modele = couleur_du_nom(variantes[0][1]["nom"])[0]
        tete = next((p for c, p in variantes if c == "1B"), variantes[0][1])
        prix = [p["prix"] for _, p in variantes]
        couleurs = []
        for code, p in variantes:
            if code not in [c["code"] for c in couleurs]:
                couleurs.append({"code": code, "description": decrire(code), "prix": p["prix"]})
        fiche = dict(tete)
        fiche.update({
            "nom": modele, "prix": min(prix), "prix_max": max(prix), "ids": [p["id"] for _, p in variantes],
            "couleurs": couleurs,
            "photo": tete["photo"] or next((p["photo"] for _, p in variantes if p["photo"]), ""),
        })
        car = {k: v for k, v in tete.get("caracteristiques", {}).items() if k != "Code-barres"}
        car["Couleurs disponibles"] = (f"{len(couleurs)} couleurs" if len(couleurs) > 1 else "1 couleur") + " : " + ", ".join(
            c["code"] for c in couleurs)
        fiche["caracteristiques"] = car
        for _, p in variantes:
            retires.add(p["id"])
        remplacants[tete["id"]] = fiche
    sortie = []
    for p in produits:
        if p["id"] in remplacants:
            sortie.append(remplacants[p["id"]])
        elif p["id"] not in retires:
            sortie.append(p)
    return sortie
