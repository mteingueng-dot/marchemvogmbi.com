"""Exporte le catalogue Clover vers data/produits.json pour la boutique en ligne.

Lancer depuis le poste ou le serveur où MVOGMBI_Sync est configuré (jeton Clover dans le coffre-fort) :

    python outils/exporter_catalogue.py --sync "E:/claude code/MVOGMBI_Sync_2026.1"

Ce qui est publié : nom, prix de vente, unité (au lb), catégorie, code-barres, et les compléments
(photo, description, caractéristiques) de data/fiches.json et de data/off_cache.json.
Jamais publié : coût, stock, fournisseur.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import urllib.parse
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
DONNEES = SITE / "data"

# Catégories Clover -> rayon affiché sur le site (ordre d'affichage)
RAYONS = {
    "Fruits & Légumes": "Fruits & légumes",
    "Féculents": "Féculents",
    "Farines": "Farines",
    "Produits Moulus": "Farines",
    "Riz": "Riz, graines & pâtes",
    "Graines": "Riz, graines & pâtes",
    "Pâtes Alimentaires": "Riz, graines & pâtes",
    "Epices": "Épices & sauces",
    "Vinaigrettes et Sauces": "Épices & sauces",
    "Huiles": "Huiles",
    "Conserves": "Conserves",
    "Produits de Mer": "Produits de la mer",
    "Viandes & Volailles": "Viandes & volailles",
    "Légumes Congelés": "Légumes congelés",
    "Jus & Bières": "Boissons",
    "Thés & Cafés": "Thés & cafés",
    "Croustilles & Bonbons": "Collations",
    "Tartines": "Tartinades",
    "Latinos": "Produits latinos",
    "Cosmétiques": "Beauté",
    "Mèches & Accessoires": "Mèches & accessoires",
    "Produits d'entretien": "Entretien",
    "Divers": "Autres produits",
}
ORDRE = list(dict.fromkeys(list(RAYONS.values()) + ["Autres produits"]))
PHOTOS_MECHES = [("TWISTED UP", "images/magasin/meches-twisted-up.jpg"),
                 ("X-PRESSION PRES STRETCHED", "images/magasin/meches-xpression.jpg")]
RAYONS_FRAIS = {"Fruits & légumes", "Féculents", "Viandes & volailles", "Produits de la mer", "Légumes congelés"}
EXCLUS = {"article personnalisé", "custom item"}


def slug(texte: str) -> str:
    t = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def format_du_nom(nom: str) -> str:
    """Format lu dans le nom : « 1kg », « 6x99g », « 500 ml », « 2 lb »."""
    m = re.search(r"(\d+\s*[xX]\s*)?\d+(?:[.,]\d+)?\s*(kg|g|mg|lb|lbs|oz|ml|l|cl)\b", nom, re.I)
    return m.group(0).replace(" ", "") if m else ""


def lire_json(chemin: Path, defaut):
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return defaut


def rayon_de(article: dict) -> str:
    for c in (article.get("categories") or {}).get("elements", []):
        if c.get("name") in RAYONS:
            return RAYONS[c["name"]]
    return "Autres produits"


def photo_pro(code: str) -> str:
    """Photo des banques libres, détourée sur fond blanc (outils/photos_pro.py), seulement si elle est réussie :
    produit entier (pas coupé par plus d'un bord de la photo), assez grand dans la photo d'origine, net."""
    if not code:
        return ""
    chemin = f"images/pro/off/{code}.jpg"
    note = NOTES_PRO.get(chemin)
    if not note or not (SITE / chemin).exists() or code in PHOTOS_REFUSEES:
        return ""
    if note.get("bords", 0) >= 2 or note.get("part", 0) < 0.06 or min(note.get("source", [0, 0])) < 300:
        return ""
    return chemin


NOTES_PRO = lire_json(DONNEES / "photos_pro.json", {})
PHOTOS_REFUSEES = set(lire_json(DONNEES / "photos_refusees.json", []))   # écartées à l'œil


def produits(articles: list[dict]) -> list[dict]:
    sys.path.insert(0, str(SITE / "outils"))
    from photos_illustration import sorte_de
    illustrations = lire_json(DONNEES / "illustrations.json", {})   # Wikimedia Commons, par sorte de produit
    magasin = lire_json(DONNEES / "photos_magasin.json", {})        # photos prises au magasin, par sorte
    fiches = lire_json(DONNEES / "fiches.json", {})          # saisies du propriétaire, par ID Clover
    off = lire_json(DONNEES / "off_cache.json", {})          # Open Food Facts, par code-barres
    sortie = []
    for a in articles:
        nom = re.sub(r"^copy of\s+", "", (a.get("name") or "").strip(), flags=re.I)
        if (a.get("deleted") or a.get("hidden") or not a.get("isRevenue", True) or not nom
                or nom.lower() in EXCLUS or a.get("priceType") == "VARIABLE" or not a.get("price")):
            continue
        code = (a.get("code") or "").strip()
        f = fiches.get(a["id"], {})
        o = off.get(code) or {} if code else {}
        if not o.get("trouve"):
            o = {}
        propre = SITE / "images" / "produits" / f"{a['id']}.jpg"      # photo du marché, nommée par l'ID Clover
        photo = f.get("photo") or (f"images/produits/{a['id']}.jpg" if propre.exists() else "") or photo_pro(code)
        a_nous = bool(f.get("photo") or propre.exists())
        source = "" if a_nous or not photo else (o.get("base") or "Open Food Facts") + " (CC BY-SA)"
        lien = "" if a_nous or not photo else f"https://world.openfoodfacts.org/product/{code}"
        illustration = False
        sorte = sorte_de(nom) if rayon_de(a) in RAYONS_FRAIS else None
        if not photo and sorte and magasin.get(sorte) and (SITE / magasin[sorte]).exists():
            photo, illustration, lien = magasin[sorte], True, ""
            source = "Photo prise au Marché Mvog-Mbi"
        if not photo and sorte:
            ill = illustrations.get(sorte)
            if ill and ill.get("fichier") and (SITE / ill["fichier"]).exists():
                photo, illustration = ill["fichier"], True
                source = f"{ill.get('auteur', 'Wikimedia Commons')}, {ill.get('licence', '')}, Wikimedia Commons"
                lien = ill.get("page", "")
        carac = {}
        if o.get("marque"):
            carac["Marque"] = o["marque"]
        fmt = o.get("quantite") or format_du_nom(nom)
        if fmt:
            carac["Format"] = fmt
        if a.get("priceType") == "PER_UNIT":
            carac["Vente"] = "Au poids (prix au lb)"
        if o.get("origine"):
            carac["Origine"] = o["origine"]
        if o.get("ingredients"):
            carac["Ingrédients"] = o["ingredients"]
        if code:
            carac["Code-barres"] = code
        carac.update(f.get("caracteristiques", {}))
        sortie.append({
            "id": a["id"],
            "nom": f.get("nom") or nom,
            "prix": a["price"] / 100,
            "unite": "lb" if a.get("priceType") == "PER_UNIT" else "",
            "rayon": rayon_de(a),
            "photo": photo,
            "photo_source": source,
            "photo_lien": lien,
            "illustration": illustration,
            "description": "",
            "caracteristiques": carac,
            "slug": slug(nom),
        })
    from couleurs_meches import regrouper
    import conditionnements
    from descriptions import decrire
    from descriptions_en import decrire_en
    from langues import RAYONS_EN, CARACTERISTIQUES_EN, VALEURS_EN, couleur_en
    sortie = regrouper(sortie)                 # une fiche par modèle de mèche, avec ses couleurs
    sortie = conditionnements.regrouper(sortie)   # une fiche par produit, avec ses formats
    for p in sortie:                           # photos des paquets prises au magasin
        if p["rayon"] == "Mèches & accessoires" and (not p["photo"] or p["illustration"]):
            for motif, fichier in PHOTOS_MECHES:
                if motif in p["nom"].upper() and (SITE / fichier).exists():
                    p.update(photo=fichier, illustration=False, photo_source="Photo prise au Marché Mvog-Mbi", photo_lien="")
                    break
    web = lire_json(DONNEES / "photos_web.json", {})
    refusees_web = set(lire_json(DONNEES / "photos_web_refusees.json", []))
    for p in sortie:
        w = web.get(p["id"]) or {}             # photo trouvée en ligne (outils/photos_web.py), sauf photo du magasin
        a_nous = p["photo_source"].startswith("Photo prise") and not p["illustration"]
        if (w.get("fichier") and (SITE / w["fichier"]).exists() and p["id"] not in refusees_web
                and not a_nous and not p["photo"].startswith("images/produits/")):
            domaine = urllib.parse.urlsplit(w.get("page") or w.get("image", "")).netloc.removeprefix("www.")
            p.update(photo=w["fichier"], illustration=False, photo_source=domaine, photo_lien=w.get("page", ""))
        propre = fiches.get(p["id"], {}).get("description")
        texte, recettes = decrire(p)
        p["description"] = propre or texte
        p["description_en"] = fiches.get(p["id"], {}).get("description_en") or decrire_en(p)
        p["recettes"] = recettes
        p["rayon_en"] = RAYONS_EN.get(p["rayon"], p["rayon"])
        p["caracteristiques_en"] = {CARACTERISTIQUES_EN.get(k, k): VALEURS_EN.get(v, v)
                                    for k, v in p.get("caracteristiques", {}).items()}
        for c in p.get("couleurs", []):
            c["description_en"] = couleur_en(c["description"])
        # Règle du propriétaire (2026-11-06) : aucun prix sur le site
        for cle in ("prix", "prix_max"):
            p.pop(cle, None)
        for c in p.get("couleurs", []):
            c.pop("prix", None)
    sortie.sort(key=lambda p: (ORDRE.index(p["rayon"]) if p["rayon"] in ORDRE else 99, p["nom"].lower()))
    return sortie


def en_stock(article: dict) -> bool:
    """Vrai si Clover compte du stock (itemStock) ; garde la valeur notée dans clover_articles.json si on relit ce fichier."""
    if "en_stock" in article:
        return bool(article["en_stock"])
    return ((article.get("itemStock") or {}).get("quantity") or 0) > 0


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sync", default=r"E:\claude code\MVOGMBI_Sync_2026.1", help="dossier de MVOGMBI_Sync")
    p.add_argument("--depuis", help="fichier JSON d'articles Clover déjà lus (au lieu de lire Clover)")
    p.add_argument("--garder-articles", action="store_true", help="écrire aussi data/clover_articles.json (non publié)")
    args = p.parse_args()
    if args.depuis:
        articles = lire_json(Path(args.depuis), [])
    else:
        sys.path.insert(0, args.sync)
        from mvogmbi_sync import points_vente
        articles = points_vente.client(Path(args.sync)).inventaire()
    if args.garder_articles:
        garde = [{k: a.get(k) for k in ("id", "name", "code", "price", "priceType", "hidden", "deleted",
                                        "isRevenue", "categories")} | {"en_stock": en_stock(a)} for a in articles]
        (DONNEES / "clover_articles.json").write_text(json.dumps(garde, ensure_ascii=False), encoding="utf-8")
    liste = produits(articles)
    # vitrine de l'accueil : produits en stock avec une vraie photo (identifiants seulement, jamais de quantité)
    stock = {a["id"] for a in articles if en_stock(a)}
    vitrine = [x["id"] for x in liste if x["photo"] and not x["illustration"]
               and any(i in stock for i in (x.get("ids") or [x["id"]]))]
    (DONNEES / "vitrine.json").write_text(json.dumps(vitrine), encoding="utf-8")
    print(f"Vitrine de l'accueil : {len(vitrine)} produits en stock avec photo.")
    DONNEES.mkdir(exist_ok=True)
    rayons = [r for r in ORDRE if any(x["rayon"] == r for x in liste)]
    sys.path.insert(0, str(SITE / "outils"))
    from langues import RAYONS_EN as RAYONS_EN_NOMS
    (DONNEES / "produits.json").write_text(
        json.dumps({"rayons": rayons, "rayons_en": [RAYONS_EN_NOMS.get(r, r) for r in rayons], "produits": liste},
                   ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8")
    # espagnol, portugais, italien, allemand : rayons, caractéristiques et descriptions dans data/produits_<code>.json
    import descriptions_autres
    fiches = lire_json(DONNEES / "fiches.json", {})
    for code in descriptions_autres.CODES:
        (DONNEES / f"produits_{code}.json").write_text(
            json.dumps(descriptions_autres.fichier_langue(liste, code, fiches), ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8")
    avec_photo = sum(1 for x in liste if x["photo"] and not x["illustration"])
    illustres = sum(1 for x in liste if x["illustration"])
    print(f"{len(liste)} produits publiés : {avec_photo} avec photo du produit, {illustres} avec photo d'illustration,"
          f" sur {len(articles)} articles Clover.")


if __name__ == "__main__":
    main()
