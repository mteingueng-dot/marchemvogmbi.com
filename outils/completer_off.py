"""Complète les produits par leur code-barres avec les banques libres Open Food Facts, Open Beauty Facts et
Open Products Facts (photo, marque, format, origine, ingrédients).

Données et photos : licence ODbL / CC BY-SA, source citée sur le site. Jamais de photo prise ailleurs (sites de
marques, magasins, moteurs de recherche) : elles appartiennent à leurs auteurs.

Lit data/clover_articles.json (écrit par exporter_catalogue.py --garder-articles), garde chaque réponse dans
data/off_cache.json et les photos dans images/produits/<code>.jpg. Seuls les vrais codes-barres (chiffre de
contrôle GTIN juste) sont demandés, 100 par demande (recherche groupée : quelques demandes en tout).

    python outils/completer_off.py
"""
from __future__ import annotations

import io
import json
import time
from pathlib import Path

import requests
from PIL import Image

SITE = Path(__file__).resolve().parent.parent
CACHE = SITE / "data" / "off_cache.json"
PHOTOS = SITE / "images" / "produits"
BASES = [
    ("Open Food Facts", "https://world.openfoodfacts.org"),
    ("Open Beauty Facts", "https://world.openbeautyfacts.org"),
    ("Open Products Facts", "https://world.openproductsfacts.org"),
]
CHAMPS = ("code,product_name_fr,product_name,generic_name_fr,brands,quantity,origins,"
          "ingredients_text_fr,ingredients_text,image_front_url,image_url")
ENTETES = {"User-Agent": "MarcheMvogmbiCatalogue/1.0 (site du Marche MVOG-MBI Sherbrooke)"}
LOT = 100
PAUSE_RECHERCHE = 7      # recherche : 10 demandes par minute au plus
PAUSE_IMAGE = 0.3


def gtin_valide(code: str) -> bool:
    if not code.isdigit() or len(code) not in (8, 12, 13, 14):
        return False
    chiffres = [int(c) for c in code[:-1]][::-1]
    somme = sum(c * (3 if i % 2 == 0 else 1) for i, c in enumerate(chiffres))
    return (10 - somme % 10) % 10 == int(code[-1])


def variantes(code: str) -> list[str]:
    """Clover garde souvent l'UPC à 12 chiffres, les banques l'EAN à 13 (un 0 devant)."""
    v = {code, code.lstrip("0")}
    if len(code) == 12:
        v.add("0" + code)
    if len(code) == 13 and code.startswith("0"):
        v.add(code[1:])
    return [x for x in v if x]


def charger() -> dict:
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def enregistrer(cache: dict) -> None:
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")


def demander(session: requests.Session, url: str, params: dict) -> requests.Response:
    for essai in range(6):
        r = session.get(url, params=params, timeout=90)
        if r.status_code == 429 or r.status_code >= 500:
            attente = int(r.headers.get("Retry-After") or 0) or 30 * (essai + 1)
            print(f"  serveur occupé ({r.status_code}), attente {attente} s", flush=True)
            time.sleep(attente)
            continue
        r.raise_for_status()
        return r
    raise RuntimeError("serveur toujours occupé")


def fiche(p: dict, base: str) -> dict:
    ingredients = (p.get("ingredients_text_fr") or p.get("ingredients_text") or "").strip()
    return {
        "trouve": True,
        "base": base,
        "nom_complet": (p.get("generic_name_fr") or "").strip(),
        "marque": (p.get("brands") or "").split(",")[0].strip(),
        "quantite": (p.get("quantity") or "").strip(),
        "origine": (p.get("origins") or "").strip(),
        "ingredients": ingredients[:600],
        "image": p.get("image_front_url") or p.get("image_url") or "",
    }


def photo(session: requests.Session, code: str, url: str) -> bool:
    cible = PHOTOS / f"{code}.jpg"
    if cible.exists():
        return True
    try:
        r = session.get(url, timeout=30)
    except requests.RequestException:
        return False
    if r.status_code != 200:
        return False
    try:
        img = Image.open(io.BytesIO(r.content)).convert("RGB")
    except OSError:
        return False
    img.thumbnail((480, 480))
    fond = Image.new("RGB", (480, 480), "white")
    fond.paste(img, ((480 - img.width) // 2, (480 - img.height) // 2))
    fond.save(cible, "JPEG", quality=82, optimize=True)
    return True


def main() -> None:
    articles = json.loads((SITE / "data" / "clover_articles.json").read_text(encoding="utf-8"))
    codes = sorted({(a.get("code") or "").strip() for a in articles if gtin_valide((a.get("code") or "").strip())})
    PHOTOS.mkdir(parents=True, exist_ok=True)
    cache = charger()
    session = requests.Session()
    session.headers.update(ENTETES)
    for nom_base, url in BASES:
        restants = [c for c in codes if not cache.get(c, {}).get("trouve")
                    and nom_base not in cache.get(c, {}).get("cherche", [])]
        print(f"{nom_base} : {len(restants)} codes à chercher", flush=True)
        for i in range(0, len(restants), LOT):
            lot = restants[i:i + LOT]
            demande = {v: c for c in lot for v in variantes(c)}
            r = demander(session, f"{url}/api/v2/search",
                         {"code": ",".join(demande), "fields": CHAMPS, "page_size": 300})
            trouves = 0
            for p in r.json().get("products", []):
                c = demande.get(str(p.get("code", "")))
                if c and not cache.get(c, {}).get("trouve"):
                    cache[c] = fiche(p, nom_base)
                    trouves += 1
            for c in lot:
                if not cache.get(c, {}).get("trouve"):
                    cache.setdefault(c, {"trouve": False}).setdefault("cherche", []).append(nom_base)
            enregistrer(cache)
            print(f"  {min(i + LOT, len(restants))}/{len(restants)} : {trouves} trouvés", flush=True)
            time.sleep(PAUSE_RECHERCHE)
    a_telecharger = [c for c, v in cache.items() if v.get("trouve") and v.get("image") and not v.get("photo")]
    print(f"Photos à télécharger : {len(a_telecharger)}", flush=True)
    for n, c in enumerate(a_telecharger, 1):
        cache[c]["photo"] = photo(session, c, cache[c]["image"])
        if n % 50 == 0:
            enregistrer(cache)
            print(f"  {n}/{len(a_telecharger)}", flush=True)
        time.sleep(PAUSE_IMAGE)
    enregistrer(cache)
    trouves = sum(1 for v in cache.values() if v.get("trouve"))
    photos = sum(1 for v in cache.values() if v.get("photo"))
    print(f"Terminé : {trouves} produits trouvés, {photos} photos.", flush=True)


if __name__ == "__main__":
    main()
