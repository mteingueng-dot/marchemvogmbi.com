"""Écrit sitemap.xml et robots.txt à la racine du site (Google, Bing).

Chaque page dans les 6 langues, avec ses autres langues (hreflang) ; les fiches produit.html?id=… en français.
    python outils/generer_sitemap.py      (après construire_site.py, avant preparer_deploiement.py)
"""
import json
from pathlib import Path
from xml.sax.saxutils import escape

SITE = Path(__file__).resolve().parent.parent
URL = "https://www.marchemvogmbi.com"
LANGUES = {"fr": "fr-CA", "en": "en-CA", "es": "es", "pt": "pt", "it": "it", "de": "de"}
EXCLURE = {"produit.html"}            # page vide sans ?id= ; les fiches sont ajoutées plus bas


def adresse(langue: str, fichier: str) -> str:
    dossier = "" if langue == "fr" else f"{langue}/"
    return f"{URL}/{dossier}{'' if fichier == 'index.html' else fichier}"


def main() -> None:
    pages = sorted(p.name for p in SITE.glob("*.html") if p.name not in EXCLURE)
    pages.sort(key=lambda f: (f != "index.html", f.startswith("recette-"), f))
    lignes = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    nb = 0
    for fichier in pages:
        presentes = [c for c in LANGUES if (SITE / ("" if c == "fr" else c) / fichier).exists()]
        alt = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{LANGUES[c]}" href="{escape(adresse(c, fichier))}"/>' for c in presentes)
        alt += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{escape(adresse("fr", fichier))}"/>'
        for c in presentes:
            lignes.append(f"  <url>\n    <loc>{escape(adresse(c, fichier))}</loc>{alt}\n  </url>")
            nb += 1
    for p in json.loads((SITE / "data" / "produits.json").read_text(encoding="utf-8"))["produits"]:
        lignes.append(f"  <url><loc>{escape(URL + '/produit.html?id=' + str(p['id']))}</loc></url>")
        nb += 1
    lignes.append("</urlset>\n")
    (SITE / "sitemap.xml").write_text("\n".join(lignes), encoding="utf-8")
    (SITE / "robots.txt").write_text("User-agent: *\nDisallow: /contact.php\n\nSitemap: " + URL + "/sitemap.xml\n",
                                     encoding="utf-8")
    print(f"sitemap.xml : {nb} adresses ; robots.txt écrit")


if __name__ == "__main__":
    main()
