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


def produits(articles: list[dict]) -> list[dict]:
    sys.path.insert(0, str(SITE / "outils"))
    from photos_illustration import sorte_de
    illustrations = lire_json(DONNEES / "illustrations.json", {})   # Wikimedia Commons, par sorte de produit
    fiches = lire_json(DONNEES / "fiches.json", {})          # saisies du propriétaire, par ID Clover
    off = lire_json(DONNEES / "off_cache.json", {})          # Open Food Facts, par code-barres
    sortie = []
    for a in articles:
        nom = (a.get("name") or "").strip()
        if (a.get("deleted") or a.get("hidden") or not a.get("isRevenue", True) or not nom
                or nom.lower() in EXCLUS or a.get("priceType") == "VARIABLE" or not a.get("price")):
            continue
        code = (a.get("code") or "").strip()
        f = fiches.get(a["id"], {})
        o = off.get(code) or {} if code else {}
        if not o.get("trouve"):
            o = {}
        propre = SITE / "images" / "produits" / f"{a['id']}.jpg"      # photo du marché, nommée par l'ID Clover
        photo = f.get("photo") or (f"images/produits/{a['id']}.jpg" if propre.exists() else "") or (
            f"images/produits/{code}.jpg" if code and (SITE / "images" / "produits" / f"{code}.jpg").exists() else "")
        a_nous = bool(f.get("photo") or propre.exists())
        source = "" if a_nous or not photo else (o.get("base") or "Open Food Facts") + " (CC BY-SA)"
        lien = "" if a_nous or not photo else f"https://world.openfoodfacts.org/product/{code}"
        illustration = False
        if not photo and rayon_de(a) in RAYONS_FRAIS:
            ill = illustrations.get(sorte_de(nom) or "")
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
            "description": f.get("description") or o.get("nom_complet", ""),
            "caracteristiques": carac,
            "slug": slug(nom),
        })
    sortie.sort(key=lambda p: (ORDRE.index(p["rayon"]) if p["rayon"] in ORDRE else 99, p["nom"].lower()))
    return sortie


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
                                        "isRevenue", "categories")} for a in articles]
        (DONNEES / "clover_articles.json").write_text(json.dumps(garde, ensure_ascii=False), encoding="utf-8")
    liste = produits(articles)
    DONNEES.mkdir(exist_ok=True)
    rayons = [r for r in ORDRE if any(x["rayon"] == r for x in liste)]
    (DONNEES / "produits.json").write_text(
        json.dumps({"rayons": rayons, "produits": liste}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8")
    avec_photo = sum(1 for x in liste if x["photo"] and not x["illustration"])
    illustres = sum(1 for x in liste if x["illustration"])
    print(f"{len(liste)} produits publiés : {avec_photo} avec photo du produit, {illustres} avec photo d'illustration,"
          f" sur {len(articles)} articles Clover.")


if __name__ == "__main__":
    main()
