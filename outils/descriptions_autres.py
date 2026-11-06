"""Descriptions des produits en espagnol, portugais, italien et allemand (textes dans outils/langue_<code>.py).

Même logique que descriptions_en.decrire_en : la sorte du produit (descriptions.SORTES) donne la première phrase,
sinon le texte du rayon ; puis marque, origine, formats, couleurs et vente au poids.
"""
from __future__ import annotations

import importlib

import descriptions as fr

CODES = ["es", "pt", "it", "de"]


def module(code: str):
    m = importlib.import_module(f"langue_{code}")
    assert len(m.SORTES) == len(fr.SORTES), (code, len(m.SORTES), len(fr.SORTES))
    if not hasattr(m, "_TRADUCTION"):
        m._TRADUCTION = {texte: x for (_, texte, _), x in zip(fr.SORTES, m.SORTES)}
        m._TRADUCTION.update({fr.RAYONS[k]: v for k, v in m.RAYONS_DESC.items()})
    return m


def decrire(p: dict, code: str) -> str:
    m = module(code)
    trouve = fr.sorte(p["nom"])
    texte = trouve[0] if trouve else fr.RAYONS.get(p["rayon"], fr.RAYONS["Autres produits"])
    phrases = [m._TRADUCTION.get(texte, "")]
    car = p.get("caracteristiques", {})
    if car.get("Marque") and fr.normal(car["Marque"]) not in fr.normal(texte):
        phrases.append(m.PHRASES["marque"].format(car["Marque"]))
    if car.get("Origine"):
        phrases.append(m.PHRASES["origine"].format(car["Origine"]))
    if p.get("conditionnements"):
        phrases.append(m.PHRASES["formats"].format(n=len(p["conditionnements"]), liste=", ".join(p["conditionnements"])))
    if p.get("couleurs"):
        n = len(p["couleurs"])
        phrases.append(m.PHRASES["couleurs"].format(n=n) if n > 1 else m.PHRASES["couleur"])
    if p.get("unite"):
        phrases.append(m.PHRASES["poids"])
    return " ".join(x for x in phrases if x)


def fichier_langue(produits: list[dict], code: str, fiches: dict) -> dict:
    """Contenu de data/produits_<code>.json : noms des rayons, des caractéristiques et une description par produit."""
    m = module(code)
    return {"rayons": m.RAYONS, "carac": m.CARACTERISTIQUES, "valeurs": m.VALEURS,
            "d": {p["id"]: fiches.get(p["id"], {}).get("description_" + code) or decrire(p, code) for p in produits}}
