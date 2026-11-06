"""Prépare les photos prises au magasin (dossier E:/site web, photos WhatsApp) pour le site.

Chaque photo retenue est redressée (EXIF), recadrée et réduite dans images/magasin/<nom>.jpg :
carrée (800 px) pour les tuiles et les fiches, en entier (1200 px de haut) pour les affiches.
data/photos_magasin.json relie chaque sorte de produit frais (voir photos_illustration.SORTES) à sa photo :
elle passe avant les photos d'illustration de Wikimedia.

    python outils/photos_magasin.py "E:/site web"
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

SITE = Path(__file__).resolve().parent.parent
DOSSIER = SITE / "images" / "magasin"

# Nom du fichier dans le dossier -> nom sur le site. Choisies une à une d'après les planches.
CARREES = {
    # produits frais (aussi utilisés pour les fiches des produits frais)
    "WhatsApp Image 2026-11-05 at 22.57.28 (9).jpeg": "plantain", "WhatsApp Image 2026-11-05 at 22.57.28 (7).jpeg": "banane-verte", "WhatsApp Image 2026-11-05 at 22.57.32 (14).jpeg": "banane", "WhatsApp Image 2026-11-05 at 22.57.28 (8).jpeg": "igname", "WhatsApp Image 2026-11-05 at 22.57.33 (7).jpeg": "igname-long", "WhatsApp Image 2026-11-05 at 22.57.33 (6).jpeg": "manioc",
    "WhatsApp Image 2026-11-05 at 22.57.29 (3).jpeg": "gombo", "WhatsApp Image 2026-11-05 at 22.57.30 (1).jpeg": "piment", "WhatsApp Image 2026-11-05 at 22.57.31.jpeg": "piment-vert", "WhatsApp Image 2026-11-05 at 22.57.33 (8).jpeg": "piments-melanges", "WhatsApp Image 2026-11-05 at 22.57.33 (12).jpeg": "tomate", "WhatsApp Image 2026-11-05 at 22.57.31 (3).jpeg": "oignon",
    "WhatsApp Image 2026-11-05 at 22.57.28 (14).jpeg": "ail", "WhatsApp Image 2026-11-05 at 22.57.32 (13).jpeg": "gingembre", "WhatsApp Image 2026-11-05 at 22.57.28 (10).jpeg": "mangue", "WhatsApp Image 2026-11-05 at 22.57.31 (8).jpeg": "patate-douce", "WhatsApp Image 2026-11-05 at 22.57.33 (5).jpeg": "macabo", "WhatsApp Image 2026-11-05 at 22.57.34 (6).jpeg": "safou",
    "WhatsApp Image 2026-11-05 at 22.57.31 (6).jpeg": "aubergine", "WhatsApp Image 2026-11-05 at 22.57.30 (6).jpeg": "arachides", "WhatsApp Image 2026-11-05 at 22.57.31 (15).jpeg": "maquereau", "WhatsApp Image 2026-11-05 at 22.57.27 (10).jpeg": "vivaneau", "WhatsApp Image 2026-11-05 at 22.57.30.jpeg": "piment-jaune", "WhatsApp Image 2026-11-05 at 22.57.31 (4).jpeg": "gombo-2",
    # rayons et galerie
    "WhatsApp Image 2026-11-05 at 22.57.28.jpeg": "farines", "WhatsApp Image 2026-11-05 at 22.57.32 (3).jpeg": "foufou", "WhatsApp Image 2026-11-05 at 22.57.28 (2).jpeg": "riz", "WhatsApp Image 2026-11-05 at 22.57.29 (15).jpeg": "egusi", "WhatsApp Image 2026-11-05 at 22.57.29 (16).jpeg": "huile-palme", "WhatsApp Image 2026-11-05 at 22.57.32 (15).jpeg": "sardines", "WhatsApp Image 2026-11-05 at 22.57.27 (9).jpeg": "viande",
    "WhatsApp Image 2026-11-05 at 22.57.27 (13).jpeg": "congeles", "WhatsApp Image 2026-11-05 at 22.57.27 (12).jpeg": "boissons", "WhatsApp Image 2026-11-05 at 22.57.30 (8).jpeg": "malta", "WhatsApp Image 2026-11-05 at 22.57.32 (1).jpeg": "milo", "WhatsApp Image 2026-11-05 at 22.58.10 (1).jpeg": "chips-plantain", "WhatsApp Image 2026-11-05 at 22.57.32 (2).jpeg": "chocopain",
    "WhatsApp Image 2026-11-05 at 22.58.10 (4).jpeg": "latinos", "WhatsApp Image 2026-11-05 at 22.57.26 (6).jpeg": "beaute", "WhatsApp Image 2026-11-05 at 22.57.26 (8).jpeg": "soins-cheveux", "WhatsApp Image 2026-11-05 at 22.58.07 (1).jpeg": "meches", "WhatsApp Image 2026-11-05 at 22.58.07.jpeg": "meches-2", "WhatsApp Image 2026-11-05 at 22.58.09 (16).jpeg": "entretien",
    "WhatsApp Image 2026-11-05 at 22.57.29 (10).jpeg": "marmites", "WhatsApp Image 2026-11-05 at 22.57.26 (10).jpeg": "rayon-cheveux", "WhatsApp Image 2026-11-05 at 22.57.28 (4).jpeg": "conserves", "WhatsApp Image 2026-11-05 at 22.57.29 (9).jpeg": "allee", "WhatsApp Image 2026-11-05 at 22.57.33 (3).jpeg": "etageres", "WhatsApp Image 2026-11-05 at 22.57.30 (11).jpeg": "bieres",
    "WhatsApp Image 2026-11-05 at 22.58.07 (10).jpeg": "meches-xpression", "WhatsApp Image 2026-11-05 at 22.58.07 (3).jpeg": "meches-twisted-up", "WhatsApp Image 2026-11-05 at 22.58.09 (4).jpeg": "djouka", "WhatsApp Image 2026-11-05 at 22.58.09 (7).jpeg": "degue", "WhatsApp Image 2026-11-05 at 22.58.09 (12).jpeg": "piment-sauce", "WhatsApp Image 2026-11-05 at 22.57.28 (1).jpeg": "meches-3", "WhatsApp Image 2026-11-05 at 22.57.28 (12).jpeg": "maillots",
    # nouveautés (photos du 2026-11-05, 23 h)
    "641677628_122188706804767848_1057815094342699640_n.jpg": "marmites-32l",
    "643352881_122188704590767848_8176234992694435746_n.jpg": "bols-bois",
    "643375769_122188713092767848_5208710800113610630_n.jpg": "marmites-45l",
    "643392248_122188713134767848_5180932262170540212_n.jpg": "marmites-55l",
    "643420844_122188713398767848_3123075706906356119_n.jpg": "marmite-57",
    "641663537_122188704308767848_803654779715530378_n.jpg": "batana",
    "643285180_122188704512767848_626133846949389212_n.jpg": "lotions-vitamines",
    "643686101_122188704356767848_6926719420879262665_n.jpg": "papaya",
    "643309740_122188704176767848_2784456296277755402_n.jpg": "caro-white",
    "642728476_122188704218767848_372241409766641746_n.jpg": "olive-oil",
    "643306021_122188704260767848_5219211814648559816_n.jpg": "lotions-blanches",
    "643319761_122188704470767848_7333262257307940429_n.jpg": "gels-douche",
}
AFFICHES = {"769957385_122210387864767848_5305240656695458404_n.jpg": "arrivage-uccao", "784352984_122211903056767848_5452133294914314349_n.jpg": "arrivage-malta", "784819021_122211903188767848_4544933917351887979_n.jpg": "arrivage-malta-24", "WhatsApp Image 2026-11-05 at 22.57.32 (7).jpeg": "arrivage-chocopain", "WhatsApp Image 2026-11-05 at 22.57.32 (8).jpeg": "arrivage-milo", "WhatsApp Image 2026-11-05 at 22.57.33.jpeg": "arrivage-tartina"}

# Sorte de produit frais -> photo du magasin (clés de photos_illustration.SORTES)
SORTES = {
    "plantain": "plantain", "banane-verte": "banane-verte", "banane": "banane", "igname": "igname",
    "manioc": "manioc", "gombo": "gombo", "piment": "piment", "tomate": "tomate", "oignon": "oignon",
    "ail": "ail", "gingembre": "gingembre", "mangue": "mangue", "patate-douce": "patate-douce",
    "macabo": "macabo", "safou": "safou", "aubergine": "aubergine", "maquereau": "maquereau",
    "vivaneau": "vivaneau",
}


def carree(src: Path, cible: Path, cote: int = 800) -> None:
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    c = min(im.size)
    im = im.crop(((im.width - c) // 2, (im.height - c) // 2, (im.width + c) // 2, (im.height + c) // 2))
    im.resize((cote, cote), Image.LANCZOS).save(cible, "JPEG", quality=80, optimize=True, progressive=True)


def entiere(src: Path, cible: Path, hauteur: int = 1200) -> None:
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    im.thumbnail((hauteur, hauteur), Image.LANCZOS)
    im.save(cible, "JPEG", quality=82, optimize=True, progressive=True)


def main() -> None:
    source = Path(sys.argv[1] if len(sys.argv) > 1 else r"E:\site web")
    DOSSIER.mkdir(parents=True, exist_ok=True)
    for rang, nom in CARREES.items():
        carree(source / rang, DOSSIER / f"{nom}.jpg")
    for rang, nom in AFFICHES.items():
        entiere(source / rang, DOSSIER / f"{nom}.jpg")
    (SITE / "data" / "photos_magasin.json").write_text(
        json.dumps({k: f"images/magasin/{v}.jpg" for k, v in SORTES.items()}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"{len(CARREES) + len(AFFICHES)} photos préparées dans images/magasin/.")


if __name__ == "__main__":
    main()
