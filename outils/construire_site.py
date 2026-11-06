"""Assemble les pages du site : même bandeau, même en-tête et même pied de page partout.

Le contenu de chaque page est dans sources/<page>.html (seulement le <main>). Après une modification :

    python outils/construire_site.py

La page Rayons est fabriquée d'après data/produits.json (nombre de produits et photo de chaque rayon) :
relancer aussi ce script après exporter_catalogue.py.
"""
from __future__ import annotations

import html
import json
from pathlib import Path
from urllib.parse import quote_plus

SITE = Path(__file__).resolve().parent.parent
SOURCES = SITE / "sources"
URL = "https://www.marchemvogmbi.com"

MENU = [("index.html", "Accueil"), ("boutique.html", "Boutique"), ("rayons.html", "Rayons"),
        ("a-propos.html", "À propos de nous"), ("carriere.html", "Carrière"), ("contact.html", "Contact")]

PAGES = {
    "index.html": ("accueil", "Marché Mvog-Mbi Sherbrooke – Le carrefour où toutes les cultures se rencontrent",
                   "Épicerie africaine, caribéenne et latine à Sherbrooke : plus de 2 500 produits, prix imbattables, "
                   "livraison gratuite dès 100 $. Ouvert tous les jours de 9 h à 21 h."),
    "boutique.html": ("boutique", "Boutique – Marché Mvog-Mbi Sherbrooke",
                      "Tous les produits du Marché Mvog-Mbi avec leurs prix, photos et caractéristiques."),
    "produit.html": ("produit", "Produit – Marché Mvog-Mbi Sherbrooke",
                     "Fiche produit du Marché Mvog-Mbi, épicerie africaine, caribéenne et latine à Sherbrooke."),
    "rayons.html": ("rayons", "Nos rayons – Marché Mvog-Mbi Sherbrooke",
                    "Tous les rayons du Marché Mvog-Mbi : fruits et légumes, féculents, farines, épices, poissons, "
                    "viandes, boissons, beauté…"),
    "a-propos.html": ("a-propos", "À propos de nous – Marché Mvog-Mbi Sherbrooke",
                      "Le Marché Mvog-Mbi, le carrefour où toutes les cultures se rencontrent, à Sherbrooke."),
    "carriere.html": ("carriere", "Carrière – Marché Mvog-Mbi Sherbrooke",
                      "Travailler au Marché Mvog-Mbi à Sherbrooke : envoyez votre candidature."),
    "contact.html": ("contact", "Contact – Marché Mvog-Mbi Sherbrooke",
                     "Adresse, heures, téléphone et courriel du Marché Mvog-Mbi, 3071 boulevard Portland, Sherbrooke."),
}
AVEC_BOUTIQUE = {"index.html", "boutique.html", "produit.html", "rayons.html"}   # pages qui lisent le catalogue

# Photo de la tuile de chaque rayon (photos d'illustration libres), sinon la 1re photo de produit du rayon
PHOTO_RAYON = {
    "Fruits & légumes": "mangue", "Féculents": "igname", "Produits de la mer": "poisson-fume",
    "Viandes & volailles": "poulet", "Légumes congelés": "ndole",
}
TEXTE_RAYON = {
    "Fruits & légumes": "Plantains, mangues, gombo, piments, ananas",
    "Féculents": "Igname, macabo, taro, patate douce",
    "Farines": "Gari, foufou, tapioca, semoule, farines de maïs",
    "Riz, graines & pâtes": "Riz parfumés, haricots, egusi, arachides",
    "Épices & sauces": "Poivre de Penja, cubes, piments, sauces",
    "Huiles": "Huile de palme rouge, arachide, cuisson",
    "Conserves": "Légumes, poissons, sauces en conserve",
    "Produits de la mer": "Poissons fumés, crevettes, tilapia",
    "Viandes & volailles": "Chèvre, bœuf, poulet, dinde, porc",
    "Légumes congelés": "Ndolé, pondu, attiéké, feuilles",
    "Boissons": "Jus, malts, bières, boissons d’ailleurs",
    "Thés & cafés": "Thés, cafés, infusions",
    "Collations": "Croustilles, biscuits, bonbons",
    "Tartinades": "Tartinades et confitures",
    "Produits latinos": "Le meilleur d’Amérique latine",
    "Beauté": "Soins du corps et des cheveux",
    "Mèches & accessoires": "Mèches, perruques, accessoires",
    "Entretien": "Produits ménagers",
    "Autres produits": "Tout le reste du magasin",
}
COULEURS = ["", " r", " j"]

BANDEAU = '''  <div class="bandeau">
    <div class="conteneur">
      <span><span class="point-ouvert" aria-hidden="true"></span><strong>Ouvert tous les jours</strong> de 9 h à 21 h</span>
      <span><strong>Livraison gratuite</strong> dès 100 $ (5 km)</span>
      <span><strong>Prix imbattables</strong> : 1 ¢ de moins qu’ailleurs</span>
      <a href="tel:+18192399864">819 239-9864</a>
    </div>
  </div>
'''

PIED = '''  <footer class="pied">
    <div class="conteneur">
      <div class="pied-grille">
        <div>
          <a href="index.html" class="marque"><img src="images/icone.png" alt="" width="42" height="42"><span>Marché Mvog-Mbi<small>Sherbrooke</small></span></a>
          <p>Le carrefour où toutes les cultures se rencontrent.<br>Épicerie africaine, caribéenne &amp; latine.</p>
        </div>
        <div>
          <h3>Le site</h3>
          <p>{liens}</p>
        </div>
        <div>
          <h3>Magasin</h3>
          <p>3071 boulevard Portland<br>Sherbrooke (QC) J1L 2Y7<br><a href="tel:+18192399864">819 239-9864</a><br><a href="mailto:contact@marchemvogmbi.com">contact@marchemvogmbi.com</a></p>
        </div>
        <div>
          <h3>Heures</h3>
          <p>Tous les jours<br>9 h à 21 h</p>
          <h3 class="pied-h3-espace">Livraison</h3>
          <p>Gratuite dès 100 $<br>dans un rayon de 5 km</p>
        </div>
      </div>
      <p class="droits">© 2026 Concept Informatique Inc. Tous droits réservés.</p>
    </div>
  </footer>
'''

FICHE_COMMERCE = {
    "@context": "https://schema.org", "@type": "GroceryStore", "name": "Marché Mvog-Mbi Sherbrooke",
    "description": "Épicerie africaine, caribéenne et latine", "url": URL, "telephone": "+1-819-239-9864",
    "email": "contact@marchemvogmbi.com", "image": f"{URL}/images/logo.png",
    "address": {"@type": "PostalAddress", "streetAddress": "3071 boulevard Portland", "addressLocality": "Sherbrooke",
                "addressRegion": "QC", "postalCode": "J1L 2Y7", "addressCountry": "CA"},
    "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                   "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                   "opens": "09:00", "closes": "21:00"}],
}


def entete(actif: str) -> str:
    liens = "\n".join(
        f'        <a href="{f}"{" aria-current=\"page\"" if f == actif else ""}>{t}</a>' for f, t in MENU)
    return f'''  <header class="entete">
    <div class="conteneur entete-ligne">
      <a href="index.html" class="marque">
        <img src="images/icone.png" alt="" width="42" height="42">
        <span>Marché Mvog-Mbi<small>Le carrefour des cultures</small></span>
      </a>
      <input type="checkbox" id="menu-ouvert" class="menu-case" aria-label="Ouvrir le menu">
      <label for="menu-ouvert" class="menu-bouton" aria-hidden="true">☰</label>
      <nav class="menu">
{liens}
        <a href="tel:+18192399864" class="bouton bouton-petit">819 239-9864</a>
      </nav>
    </div>
  </header>
'''


def page_rayons() -> str:
    d = json.loads((SITE / "data" / "produits.json").read_text(encoding="utf-8"))
    tuiles = []
    for i, r in enumerate(d["rayons"]):
        produits = [p for p in d["produits"] if p["rayon"] == r]
        cle = PHOTO_RAYON.get(r)
        photo = f"images/illustrations/{cle}.jpg" if cle and (SITE / "images" / "illustrations" / f"{cle}.jpg").exists() else ""
        lien = f"boutique.html?rayon={quote_plus(r)}"
        texte = html.escape(TEXTE_RAYON.get(r, ""))
        nb = f"{len(produits)} produit{'s' if len(produits) > 1 else ''}"
        if photo:
            tuiles.append(f'          <a class="tuile" href="{lien}"><img src="{photo}" alt="" loading="lazy">'
                          f'<em class="tuile-nombre">{nb}</em><strong>{html.escape(r)}</strong><span>{texte}</span></a>')
        else:
            tuiles.append(f'          <a class="tuile sans-image{COULEURS[i % 3]}" href="{lien}">'
                          f'<em class="tuile-nombre">{nb}</em><strong>{html.escape(r)}</strong><span>{texte}</span></a>')
    source = (SOURCES / "rayons.html").read_text(encoding="utf-8")
    return source.replace("<!--TUILES-->", "\n".join(tuiles)).replace(
        "<!--NOMBRE-->", f"{len(d['produits']):,}".replace(",", " "))


def construire(fichier: str) -> None:
    cle, titre, description = PAGES[fichier]
    contenu = page_rayons() if fichier == "rayons.html" else (SOURCES / f"{cle}.html").read_text(encoding="utf-8")
    css = '  <link rel="stylesheet" href="boutique.css">\n' if fichier in AVEC_BOUTIQUE else ""
    script = '  <script src="boutique.js"></script>\n' if fichier in AVEC_BOUTIQUE else ""
    fiche = ""
    if fichier in ("index.html", "contact.html"):
        fiche = ('  <script type="application/ld+json">\n  '
                 + json.dumps(FICHE_COMMERCE, ensure_ascii=False) + "\n  </script>\n")
    actif = fichier if fichier != "produit.html" else "boutique.html"
    pied = PIED.format(liens="<br>".join(f'<a href="{f}">{t}</a>' for f, t in MENU))
    page = f'''<!doctype html>
<html lang="fr-CA">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(titre)}</title>
  <meta name="description" content="{html.escape(description)}">
  <meta name="theme-color" content="#15201a">
  <link rel="icon" href="favicon.ico">
  <link rel="apple-touch-icon" href="images/icone.png">
  <meta property="og:title" content="{html.escape(titre)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:image" content="{URL}/images/logo.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
{css}{fiche}</head>
<body>
{BANDEAU}
{entete(actif)}
{contenu.rstrip()}

{pied}{script}</body>
</html>
'''
    (SITE / fichier).write_text(page, encoding="utf-8")


def main() -> None:
    for fichier in PAGES:
        construire(fichier)
    print(f"{len(PAGES)} pages construites.")


if __name__ == "__main__":
    main()
