"""Filtre par pays de la page Recettes : une rangée de boutons par région, un bouton par pays (avec le nombre de recettes).

Le pays d'une recette (« Bénin et Togo ») est coupé en pays (« Bénin », « Togo ») : la recette est sous chacun.
Le nom affiché vient du pays traduit de la recette, coupé de la même façon (« Benin and Togo »).
Le choix se fait dans la page (site.js) et reste dans l'adresse : recettes.html#pays=haiti.
"""
from __future__ import annotations

import html
import re
import unicodedata

JOINTS = {"fr": " et ", "en": " and ", "es": " y ", "pt": " e ", "it": " e ", "de": " und "}

REGIONS = [
    ("centrale", ["Cameroun", "RD Congo", "Congo", "Congo-Brazzaville", "Gabon"]),
    ("ouest", ["Côte d’Ivoire", "Nigeria", "Ghana", "Sénégal", "Mali", "Burkina Faso", "Bénin", "Togo", "Guinée",
               "Gambie", "Cap-Vert", "Afrique de l’Ouest"]),
    ("est", ["Rwanda", "Burundi", "Kenya", "Tanzanie", "Ouganda", "Éthiopie", "Afrique du Sud", "Mozambique"]),
    ("nord", ["Maroc", "Algérie", "Tunisie", "Égypte"]),
    ("caraibes", ["Haïti", "Jamaïque", "Guadeloupe", "Martinique", "Antilles", "Trinidad", "Cuba", "Porto Rico",
                  "République dominicaine"]),
    ("latine", ["Mexique", "Colombie", "Venezuela", "Salvador", "Costa Rica", "Nicaragua", "Équateur", "Pérou", "Bolivie", "Brésil"]),
]
NOMS_REGIONS = {
    "fr": {"centrale": "Afrique centrale", "ouest": "Afrique de l’Ouest", "est": "Afrique de l’Est et australe",
           "nord": "Afrique du Nord", "caraibes": "Caraïbes", "latine": "Amérique latine", "tous": "Toutes les recettes",
           "titre": "Filtrer par pays"},
    "en": {"centrale": "Central Africa", "ouest": "West Africa", "est": "East and Southern Africa",
           "nord": "North Africa", "caraibes": "Caribbean", "latine": "Latin America", "tous": "All recipes",
           "titre": "Filter by country"},
    "es": {"centrale": "África central", "ouest": "África occidental", "est": "África oriental y austral",
           "nord": "Norte de África", "caraibes": "Caribe", "latine": "América Latina", "tous": "Todas las recetas",
           "titre": "Filtrar por país"},
    "pt": {"centrale": "África Central", "ouest": "África Ocidental", "est": "África Oriental e Austral",
           "nord": "Norte da África", "caraibes": "Caribe", "latine": "América Latina", "tous": "Todas as receitas",
           "titre": "Filtrar por país"},
    "it": {"centrale": "Africa centrale", "ouest": "Africa occidentale", "est": "Africa orientale e australe",
           "nord": "Nordafrica", "caraibes": "Caraibi", "latine": "America Latina", "tous": "Tutte le ricette",
           "titre": "Filtra per paese"},
    "de": {"centrale": "Zentralafrika", "ouest": "Westafrika", "est": "Ost- und Südafrika",
           "nord": "Nordafrika", "caraibes": "Karibik", "latine": "Lateinamerika", "tous": "Alle Rezepte",
           "titre": "Nach Land filtern"},
}
REGION_DE = {p: r for r, pays in REGIONS for p in pays}


def cle(pays: str) -> str:
    t = unicodedata.normalize("NFKD", pays).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def couper(texte: str, langue: str) -> list[str]:
    return [p.strip() for p in texte.split(JOINTS[langue]) if p.strip()]


def pays_de(recette: dict, langue: str, traduit: str) -> list[tuple[str, str]]:
    """[(clé, nom affiché)] des pays d'une recette."""
    fr = couper(recette["pays"], "fr")
    noms = couper(traduit, langue)
    if len(noms) != len(fr):
        noms = fr
    return [(cle(f), n) for f, n in zip(fr, noms)]


def barre(recettes: list[dict], langue: str, traduit) -> tuple[str, dict[str, str]]:
    """HTML de la barre de filtres et {id de recette: "clé1 clé2"}."""
    noms, compte, par_recette = {}, {}, {}
    for r in recettes:
        liste = pays_de(r, langue, traduit(r))
        par_recette[r["id"]] = " ".join(k for k, _ in liste)
        for (k, n), f in zip(liste, couper(r["pays"], "fr")):
            noms.setdefault(k, (n, f))
            compte[k] = compte.get(k, 0) + 1
    t = NOMS_REGIONS[langue]
    lignes = [f'        <div class="filtre-pays" role="group" aria-label="{t["titre"]}">',
              f'          <button type="button" class="pays-bouton actif" data-pays="">{t["tous"]} <em>{len(recettes)}</em></button>']
    for region, liste_fr in REGIONS:
        boutons = [(cle(f), noms[cle(f)][0]) for f in liste_fr if cle(f) in noms]
        if not boutons:
            continue
        lignes.append(f'          <div class="pays-region"><span>{t[region]}</span>')
        lignes += [f'            <button type="button" class="pays-bouton" data-pays="{k}">{html.escape(n)} <em>{compte[k]}</em></button>'
                   for k, n in boutons]
        lignes.append("          </div>")
    oublies = [k for k, (_, f) in noms.items() if f not in REGION_DE]
    if oublies:
        raise SystemExit(f"Pays sans région dans outils/filtre_pays.py : {', '.join(oublies)}")
    lignes.append("        </div>")
    return "\n".join(lignes), par_recette
