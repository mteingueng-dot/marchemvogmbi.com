"""Fichier .zip à déposer dans cPanel (Gestionnaire de fichiers > public_html > Téléverser, puis Extraire).

Contenu : les pages, les styles et scripts, contact.php, les données lues par le site (produits, recettes, vitrine)
et seulement les images utilisées. Jamais : outils/, sources/, .git, README, data/clover_articles.json
ni les fichiers de travail des outils (caches, photos refusées…).
    python outils/preparer_deploiement.py
"""
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
LANGUES = ["en", "es", "pt", "it", "de"]
DONNEES = re.compile(r"^(produits(_\w+)?|recettes(_\w+)?|vitrine)\.json$")
EXTENSIONS = {".html", ".css", ".js", ".php", ".ico"}


def fichiers() -> list[Path]:
    liste = [p for p in SITE.iterdir() if p.is_file() and p.suffix in EXTENSIONS]
    for code in LANGUES:
        liste += [p for p in (SITE / code).iterdir() if p.is_file() and p.suffix in EXTENSIONS]
    liste += [p for p in (SITE / "data").iterdir() if DONNEES.match(p.name)]
    # images : celles que citent les pages, les scripts et les données publiées
    textes = "".join(p.read_text(encoding="utf-8", errors="ignore") for p in liste)
    utilisees = set(re.findall(r"images/[\w\-./]+?\.(?:jpe?g|png|webp|svg|gif|ico)", textes))
    for chemin in sorted(utilisees):
        p = SITE / chemin
        if p.exists():
            liste.append(p)
    return liste


def main() -> None:
    liste = fichiers()
    sortie = SITE / "deploiement" / f"marchemvogmbi_{datetime.now():%Y-%m-%d_%H%M}.zip"
    sortie.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(sortie, "w", zipfile.ZIP_DEFLATED) as z:
        for p in liste:
            z.write(p, p.relative_to(SITE).as_posix())
        z.write(SITE / "deploiement_htaccess.txt", ".htaccess")      # remplace le .htaccess de WordPress
    taille = sortie.stat().st_size / 1e6
    images = sum(1 for p in liste if p.parts[len(SITE.parts)] == "images")
    print(f"{sortie} : {len(liste)} fichiers dont {images} images, {taille:.1f} Mo")


if __name__ == "__main__":
    sys.exit(main())
