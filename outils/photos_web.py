"""Photos de produit trouvées par une recherche d'images sur le nom exact du produit (marque, sorte, format).

    python outils/photos_web.py                 # tous les produits sans photo prise au magasin
    python outils/photos_web.py --limite 25     # essai
    python outils/photos_web.py --refaire ID…   # chercher de nouveau ces produits

Pour chaque produit : les résultats de la recherche (titre, image, page d'origine) ; on télécharge les premiers,
on garde celui dont le titre ressemble le plus au nom du produit, assez grand, de préférence sur fond blanc,
puis on le place au centre d'un carré blanc de 800 × 800 : images/web/<id>.jpg.
Les choix sont notés dans data/photos_web.json (page d'origine gardée pour la mention de la source).
Une photo jugée mauvaise à l'œil : ajouter l'ID du produit dans data/photos_web_refusees.json.
"""
from __future__ import annotations

import argparse
import html
import io
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock

from PIL import Image, ImageChops, ImageOps, ImageStat

SITE = Path(__file__).resolve().parent.parent
DOSSIER = SITE / "images" / "web"
NOTES = SITE / "data" / "photos_web.json"
REFUSEES = SITE / "data" / "photos_web_refusees.json"
COTE = 800
MARGE = 0.06
AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
EXCLUS = ("pinterest.", "facebook.", "instagram.", "tiktok.", "youtube.", "shutterstock.", "alamy.",
          "istockphoto.", "gettyimages.", "dreamstime.", "123rf.", "depositphotos.", "freepik.", "vecteezy.",
          "ldplayer.", "pngtree.", "pixabay.", "unsplash.", "pexels.", "wikipedia.", "ebay.", "aliexpress.")
FRAIS = {"Fruits & légumes", "Féculents", "Viandes & volailles", "Produits de la mer", "Légumes congelés"}
VIDES = {"de", "du", "des", "la", "le", "les", "et", "en", "a", "au", "aux", "with", "and", "the", "of", "in", "pour"}


def mots(texte: str) -> set[str]:
    t = unicodedata.normalize("NFKD", texte.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return {m for m in re.findall(r"[a-z0-9]+", t) if m not in VIDES and len(m) > 1}


def lire(url: str, delai: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": AGENT, "Accept-Language": "fr-CA,fr;q=0.9,en;q=0.8",
                                               "Accept": "image/avif,image/webp,image/*,*/*;q=0.8"})
    with urllib.request.urlopen(req, timeout=delai) as r:
        return r.read(12_000_000)


def resultats(requete: str) -> list[dict]:
    url = "https://www.bing.com/images/async?" + urllib.parse.urlencode(
        {"q": requete, "first": "0", "count": "20", "mmasync": "1", "adlt": "strict"})
    page = lire(url).decode("utf-8", "replace")
    sortie = []
    for m in re.findall(r'\bm="(\{.*?\})"', page):
        try:
            d = json.loads(html.unescape(m))
        except ValueError:
            continue
        if d.get("murl") and not any(e in (d.get("purl", "") + d["murl"]) for e in EXCLUS):
            sortie.append({"image": d["murl"], "page": d.get("purl", ""), "titre": d.get("t", "")})
    return sortie


def fond_blanc(image: Image.Image) -> float:
    """Part des coins clairs (0 à 1) : une photo de produit sur fond blanc."""
    g = image.convert("L")
    w, h = g.size
    k = max(4, min(w, h) // 20)
    coins = [g.crop(b) for b in ((0, 0, k, k), (w - k, 0, w, k), (0, h - k, k, h), (w - k, h - k, w, h))]
    return sum(1 for c in coins if ImageStat.Stat(c).mean[0] > 235) / 4


def carre(image: Image.Image) -> Image.Image:
    image = ImageOps.exif_transpose(image)
    if image.mode in ("RGBA", "LA", "P"):
        image = image.convert("RGBA")
        fond = Image.new("RGBA", image.size, "white")
        fond.alpha_composite(image)
        image = fond
    image = image.convert("RGB")
    # retirer les bords blancs autour du produit
    diff = ImageChops.difference(image, Image.new("RGB", image.size, "white")).convert("L").point(lambda v: 255 if v > 18 else 0)
    boite = diff.getbbox()
    if boite:
        image = image.crop(boite)
    utile = int(COTE * (1 - 2 * MARGE))
    echelle = utile / max(image.size)
    image = image.resize((max(1, round(image.width * echelle)), max(1, round(image.height * echelle))), Image.LANCZOS)
    sortie = Image.new("RGB", (COTE, COTE), "white")
    sortie.paste(image, ((COTE - image.width) // 2, (COTE - image.height) // 2))
    return sortie


def requete(p: dict) -> str:
    nom = re.sub(r"\b(en\s+)?(lbs?|kg|pcs?|unit[ée]s?)\b\.?", " ", p["nom"], flags=re.I)
    nom = re.sub(r"\s+", " ", nom).strip()
    return nom + (" frais fruit légume" if p.get("rayon") in FRAIS else "")


def choisir(p: dict) -> dict | None:
    frais = p.get("rayon") in FRAIS
    cible = mots(requete(p).replace(" frais fruit légume", ""))
    candidats = resultats(requete(p))[:8]
    meilleur = None
    for rang, c in enumerate(candidats):
        try:
            image = Image.open(io.BytesIO(lire(c["image"], 15)))
            image.load()
        except Exception:
            continue
        w, h = image.size
        if min(w, h) < 280 or max(w, h) / min(w, h) > 2.2:
            continue
        commun = len(cible & mots(c["titre"] + " " + c["page"])) / max(1, len(cible))
        blanc = fond_blanc(image)
        if frais and blanc < 0.5:
            continue                     # produit frais : seulement une photo détourée, sans décor
        note = commun * 3 + blanc * (2.5 if frais else 1.2) + min(1, min(w, h) / 800) * 0.6 - rang * 0.12
        if not meilleur or note > meilleur["note"]:
            meilleur = dict(c, note=round(note, 2), commun=round(commun, 2), taille=[w, h], _image=image)
        if commun >= 0.8 and fond_blanc(image) >= 0.75 and min(w, h) >= 500:
            break                        # assez bon : inutile de télécharger les suivants
    return meilleur


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--refaire", nargs="*", default=[])
    ap.add_argument("--fils", type=int, default=4)
    ap.add_argument("--ids", nargs="*", default=[])
    args = ap.parse_args()
    DOSSIER.mkdir(parents=True, exist_ok=True)
    notes = json.loads(NOTES.read_text(encoding="utf-8")) if NOTES.exists() else {}
    for i in args.refaire:
        notes.pop(i, None)
    produits = json.loads((SITE / "data" / "produits.json").read_text(encoding="utf-8"))["produits"]
    a_faire = [p for p in produits if p["id"] not in notes
               and not (p.get("photo_source", "").startswith("Photo prise") and not p.get("illustration"))]
    if args.ids:
        a_faire = [p for p in a_faire if p["id"] in set(args.ids)]
    if args.limite:
        a_faire = a_faire[:args.limite]
    print(f"{len(a_faire)} produits à chercher", flush=True)
    verrou, compte = Lock(), [0, 0]

    def traiter(p: dict) -> None:
        try:
            c = choisir(p)
        except Exception as e:                       # recherche refusée ou réseau : on réessaiera
            print(f"  ! {p['nom']} : {e}", flush=True)
            time.sleep(5)
            return
        with verrou:
            compte[0] += 1
            if not c or c["commun"] < 0.4:
                notes[p["id"]] = {"nom": p["nom"], "fichier": "", "raison": "rien de ressemblant"}
            else:
                fichier = f"images/web/{p['id']}.jpg"
                carre(c.pop("_image")).save(SITE / fichier, "JPEG", quality=86, optimize=True, progressive=True)
                notes[p["id"]] = {"nom": p["nom"], "requete": requete(p), "fichier": fichier, **c}
                compte[1] += 1
            if compte[0] % 25 == 0:
                NOTES.write_text(json.dumps(notes, ensure_ascii=False, indent=1), encoding="utf-8")
                print(f"  {compte[0]} / {len(a_faire)} ({compte[1]} photos)", flush=True)
        time.sleep(0.4)

    with ThreadPoolExecutor(args.fils) as ex:
        list(ex.map(traiter, a_faire))
    NOTES.write_text(json.dumps(notes, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Terminé : {compte[1]} photos sur {compte[0]} produits cherchés", flush=True)


if __name__ == "__main__":
    sys.exit(main())
