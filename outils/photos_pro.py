"""Photos de produit « professionnelles » : produit détouré, centré sur fond blanc, ombre douce.

Le détourage se fait sur ce poste avec rembg (modèle isnet-general-use), installé à part :
    python -m venv venv_rembg && venv_rembg/Scripts/python -m pip install "rembg[cpu]" pillow
puis :
    venv_rembg/Scripts/python outils/photos_pro.py images/produits images/pro
    venv_rembg/Scripts/python outils/photos_pro.py "E:/site web" images/pro/magasin --fichiers liste.txt

Pour chaque photo : images/pro/<nom>.jpg (800 × 800) et une note dans data/photos_pro.json
(part de l'image occupée par le produit, netteté) pour écarter les photos ratées.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps, ImageStat

SITE = Path(__file__).resolve().parent.parent
COTE = 800
MARGE = 0.07


def packshot(image: Image.Image, session) -> tuple[Image.Image, dict]:
    from rembg import remove
    image = ImageOps.exif_transpose(image).convert("RGB")
    image.thumbnail((1600, 1600))
    rgba = remove(image, session=session, post_process_mask=True)
    alpha = rgba.getchannel("A").point(lambda v: 0 if v < 128 else v)     # contour net, sans halo
    rgba.putalpha(alpha)
    masque = alpha.point(lambda v: 255 if v else 0)
    boite = masque.getbbox()
    part, bords = 0.0, 0
    if boite:
        part = masque.crop(boite).histogram()[255] / (image.width * image.height)
        g, h, d, b = boite                         # produit coupé par le bord de la photo ?
        bords = sum((g <= 2, h <= 2, d >= image.width - 2, b >= image.height - 2))
        rgba = rgba.crop(boite)
    net = ImageStat.Stat(rgba.convert("L").filter(ImageFilter.FIND_EDGES)).var[0] if boite else 0
    utile = int(COTE * (1 - 2 * MARGE))
    echelle = utile / max(rgba.size)               # agrandir aussi les petits produits
    rgba = rgba.resize((max(1, round(rgba.width * echelle)), max(1, round(rgba.height * echelle))), Image.LANCZOS)
    fond = Image.new("RGB", (COTE, COTE), "white")
    # ombre douce sous le produit
    ombre = Image.new("L", (COTE, COTE), 0)
    w, h = rgba.size
    x, y = (COTE - w) // 2, (COTE - h) // 2
    ellipse = Image.new("L", (w, max(8, h // 12)), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(ellipse).ellipse((0, 0, w - 1, ellipse.height - 1), fill=70)
    ombre.paste(ellipse, (x, min(COTE - ellipse.height, y + h - ellipse.height // 2)))
    ombre = ombre.filter(ImageFilter.GaussianBlur(14))
    fond.paste(Image.new("RGB", (COTE, COTE), (205, 205, 200)), (0, 0), ombre)
    fond.paste(rgba, (x, y), rgba)
    return fond, {"part": round(part, 3), "nettete": round(net), "taille": list(rgba.size), "bords": bords,
                  "source": list(image.size)}


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument("source")
    a.add_argument("cible")
    a.add_argument("--fichiers", help="liste de noms de fichiers à traiter (un par ligne)")
    a.add_argument("--refaire", action="store_true")
    args = a.parse_args()
    from rembg import new_session
    session = new_session("isnet-general-use")
    source, cible = Path(args.source), SITE / args.cible
    cible.mkdir(parents=True, exist_ok=True)
    noms = (Path(args.fichiers).read_text(encoding="utf-8").split("\n") if args.fichiers
            else sorted(f.name for f in source.glob("*.jp*g")))
    noms = [n.strip() for n in noms if n.strip()]
    notes_f = SITE / "data" / "photos_pro.json"
    notes = json.loads(notes_f.read_text(encoding="utf-8")) if notes_f.exists() else {}
    for i, nom in enumerate(noms, 1):
        sortie = cible / (Path(nom).stem + ".jpg")
        if sortie.exists() and not args.refaire:
            continue
        try:
            image, note = packshot(Image.open(source / nom), session)
        except Exception as e:                      # photo illisible : on passe
            print(f"{nom} : {e}", file=sys.stderr)
            continue
        image.save(sortie, "JPEG", quality=86, optimize=True, progressive=True)
        notes[str(sortie.relative_to(SITE)).replace("\\", "/")] = note
        if i % 25 == 0:
            notes_f.write_text(json.dumps(notes, indent=0), encoding="utf-8")
            print(f"{i}/{len(noms)}", flush=True)
    notes_f.write_text(json.dumps(notes, indent=0), encoding="utf-8")
    print(f"Terminé : {len(noms)} photos.", flush=True)


if __name__ == "__main__":
    main()
