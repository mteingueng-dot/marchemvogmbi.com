"""Fichier .zip à déposer dans cPanel (Gestionnaire de fichiers > public_html > Téléverser, puis Extraire).

Contenu : les pages, les styles et scripts, contact.php, les données lues par le site (produits, recettes, vitrine)
et seulement les images utilisées. Jamais : outils/, sources/, .git, README, data/clover_articles.json
ni les fichiers de travail des outils (caches, photos refusées…).
    python outils/preparer_deploiement.py
    python outils/preparer_deploiement.py --dossier publication   (mise en ligne automatique : .github/workflows)
"""
import json
import re
import shutil
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
    for nom in ("robots.txt", "sitemap.xml"):             # écrits par outils/generer_sitemap.py
        if (SITE / nom).exists():
            liste.append(SITE / nom)
    # clé IndexNow (Bing, Yandex…) : fichier <clé>.txt à la racine, lu par outils/mise_a_jour_auto.py
    liste += [p for p in SITE.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}\.txt", p.name)]
    return liste


def htaccess() -> str:
    """.htaccess du site + redirections permanentes des anciennes adresses des fiches (d'après le nom) vers produit-<ID>.html."""
    texte = (SITE / "deploiement_htaccess.txt").read_text(encoding="utf-8")
    fichier = SITE / "data" / "anciennes_adresses.json"
    if fichier.exists():
        regles = [rf"RewriteRule ^((?:[a-z]{{2}}/)?)produit-{re.escape(ancien)}\.html$ /$1produit-{nouveau}.html [R=301,L]"
                  for ancien, nouveau in sorted(json.loads(fichier.read_text(encoding="utf-8")).items())]
        texte += ("\n# Anciennes adresses des fiches produits (d'après le nom) -> produit-<ID Clover>.html\n"
                  + "\n".join(regles) + "\n")
    return texte


def copier(dossier: Path) -> None:
    """Mêmes fichiers que le .zip, copiés dans un dossier (envoyé ensuite par FTP par GitHub Actions)."""
    liste = fichiers()
    if dossier.exists():
        shutil.rmtree(dossier)
    for p in liste:
        cible = dossier / p.relative_to(SITE)
        cible.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, cible)
    (dossier / ".htaccess").write_text(htaccess(), encoding="utf-8")
    print(f"{dossier} : {len(liste) + 1} fichiers")


def main() -> None:
    if len(sys.argv) == 3 and sys.argv[1] == "--dossier":
        return copier(Path(sys.argv[2]).resolve())
    liste = fichiers()
    sortie = SITE / "deploiement" / f"marchemvogmbi_{datetime.now():%Y-%m-%d_%H%M}.zip"
    sortie.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(sortie, "w", zipfile.ZIP_DEFLATED) as z:
        for p in liste:
            z.write(p, p.relative_to(SITE).as_posix())
        z.writestr(".htaccess", htaccess())      # remplace le .htaccess de WordPress
    taille = sortie.stat().st_size / 1e6
    images = sum(1 for p in liste if p.parts[len(SITE.parts)] == "images")
    print(f"{sortie} : {len(liste)} fichiers dont {images} images, {taille:.1f} Mo")


if __name__ == "__main__":
    sys.exit(main())
