"""Met une photo de produit sur fond blanc : le décor est retiré (rembg, modèle isnet-general-use, sur l'ordinateur),
le produit est recadré, centré avec une marge, en carré de 800 px.

    python outils/fond_blanc.py photo.jpg images/produits/<ID Clover>.jpg
Installation une fois : pip install "rembg[cpu]"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps

SITE = Path(__file__).resolve().parent.parent
COTE = 800
MARGE = 0.08
_SESSION = None


def detourer(image: Image.Image) -> Image.Image:
    """Produit seul sur blanc, carré de 800 px."""
    global _SESSION
    from rembg import new_session, remove
    if _SESSION is None:
        _SESSION = new_session("isnet-general-use")
    image = ImageOps.exif_transpose(image).convert("RGB")
    decoupe = remove(image, session=_SESSION)                 # RGBA : décor transparent
    alpha = decoupe.getchannel("A").point(lambda v: 255 if v > 24 else 0)
    boite = alpha.getbbox() or (0, 0, *decoupe.size)
    decoupe = decoupe.crop(boite)
    fond = Image.new("RGBA", decoupe.size, (255, 255, 255, 255))
    fond.alpha_composite(decoupe)
    produit = fond.convert("RGB")
    w, h = produit.size
    c = int(max(w, h) / (1 - 2 * MARGE))
    carre = Image.new("RGB", (c, c), (255, 255, 255))
    carre.paste(produit, ((c - w) // 2, (c - h) // 2))
    return carre.resize((COTE, COTE), Image.LANCZOS)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", nargs="?")
    ap.add_argument("cible", nargs="?")
    args = ap.parse_args()
    if not (args.source and args.cible):
        ap.error("donner la photo et le fichier à écrire")
    detourer(Image.open(args.source)).save(args.cible, quality=88)
    print(args.cible)


if __name__ == "__main__":
    sys.exit(main())
