"""Photos d'illustration des produits frais (sans code-barres) prises dans Wikimedia Commons, licences libres
seulement (CC0, domaine public, CC BY, CC BY-SA), avec auteur et licence gardés pour la mention sur le site.

Une photo par sorte de produit (plantain, igname, tilapia…) : data/illustrations.json + images/illustrations/.
Le produit montre « Photo d'illustration » : ce n'est pas la photo du produit vendu.

    python outils/photos_illustration.py            # télécharge ce qui manque
    python outils/photos_illustration.py --refaire plantain   # choisit une autre photo pour ce mot
"""
from __future__ import annotations

import argparse
import html
import io
import json
import re
import time
from pathlib import Path

import requests
from PIL import Image

SITE = Path(__file__).resolve().parent.parent
FICHIER = SITE / "data" / "illustrations.json"
DOSSIER = SITE / "images" / "illustrations"
API = "https://commons.wikimedia.org/w/api.php"
ENTETES = {"User-Agent": "MarcheMvogmbiCatalogue/1.0 (site du Marche MVOG-MBI Sherbrooke)"}
LICENCES = ("cc0", "public domain", "pdm", "cc by", "cc-by")

# (clé, motif cherché dans le nom normalisé, recherche dans Commons) — du plus précis au plus général
SORTES = [
    ("fruit-passion", r"fruit de la passion", "Passion fruit cut"),
    ("patate-douce", r"patate douce|sweet potato", "Sweet potatoes tubers raw"),
    ("pomme-de-terre", r"pomme(s)? de terre|patate congel", "Raw potatoes tubers"),
    ("citronnelle", r"citronel", "Cymbopogon citratus stalks"),
    ("citron", r"\bcitron\b|lemon", "Lemons fruit"),
    ("lime", r"\blime\b", "Limes fruit"),
    ("ail", r"\bail\b|\bails\b|garlic", "Garlic bulbs"),
    ("ananas", r"ananas", "Pineapple fruit"),
    ("aubergine", r"aubergine", "Eggplants"),
    ("avocat", r"avocat", "Avocados"),
    ("banane-verte", r"banane vert", "Unripe green bananas"),
    ("banane", r"banane", "Bananas bunch"),
    ("betterave", r"bet(t)?erave", "Beetroots"),
    ("cantaloup", r"cantaloup", "Cantaloupe halved"),
    ("melon-miel", r"melon miel", "Honeydew melon"),
    ("pasteque", r"pasteque|melon d.eau", "Watermelon slice"),
    ("carotte", r"carotte", "Carrots"),
    ("celeri", r"celeri", "Celery bunch vegetable"),
    ("chou", r"\bchou\b", "Green cabbage"),
    ("chayotte", r"cho(y|i)otte|chayot", "Chayote"),
    ("concombre", r"co(n|m)combre", "Cucumbers"),
    ("corossol", r"coro(s)?sol", "Soursop fruit"),
    ("fraise", r"fraise", "Strawberries"),
    ("gingembre", r"ging(e|a)(m|n)bre|ginger", "Ginger rhizome root"),
    ("gombo", r"gombo|okra", "Okra vegetable pods"),
    ("mais", r"\bmais frais|mais congel", "Corn cobs husked"),
    ("mandarine", r"mandarine", "Mandarin oranges"),
    ("mangue", r"mangue", "Mangoes"),
    ("manioc", r"manioc|cassava|yucca", "Cassava tubers peeled"),
    ("oignon", r"oignon", "Onions"),
    ("orange", r"\borange\b", "Oranges fruit"),
    ("piment", r"piment", "Scotch bonnet peppers"),
    ("plantain", r"plantain", "Plantain bananas bunch"),
    ("poivron", r"poivron", "Bell peppers red yellow green"),
    ("pomme", r"\bpomme\b", "Red apples"),
    ("raisin", r"raisin", "Red grapes bunch"),
    ("safou", r"safou", "Dacryodes edulis fruits"),
    ("tomate", r"tomate", "Red tomatoes vegetables"),
    ("igname", r"igname|\byam\b", "Yam tubers market"),
    ("macabo", r"macabo|malanga", "Cocoyam tubers"),
    ("taro", r"\btaro\b|eddo", "Taro roots"),
    ("epinard", r"epinard", "Spinach leaves"),
    ("ndole", r"ndole", "Vernonia amygdalina leaves"),
    ("molokhia", r"molokhia", "Jute mallow leaves bunch"),
    ("eru", r"\beru\b|fumbwa", "Gnetum africanum"),
    ("attieke", r"attieke", "Attieke cassava couscous"),
    ("bobolo", r"bobolo|miondo", "Bobolo cassava stick"),
    ("gesier", r"gesier", "Chicken gizzards"),
    ("dinde", r"dinde|turkey", "Raw turkey drumsticks"),
    ("poulet", r"poulet|\bpoule\b|chicken", "Raw chicken meat"),
    ("chevre", r"chevre", "Goat meat raw butcher"),
    ("mouton", r"mouton", "Raw lamb meat"),
    ("lapin", r"lapin", "Rabbit meat raw"),
    ("porc", r"\bporc\b", "Raw pork meat"),
    ("boeuf", r"boeuf|bœuf|beef", "Raw beef cuts butcher"),
    ("escargot", r"escargot", "Achatina fulica"),
    ("crevette", r"crevette|prawn|shrimp", "Dried shrimp"),
    ("tilapia", r"tilapia", "Tilapia fish fresh market"),
    ("maquereau", r"maquereau|chinchard", "Horse mackerel fish"),
    ("sardine", r"sardine", "Fresh sardines fish"),
    ("vivaneau", r"red snapper|redfish|sebaste", "Red snapper fish"),
    ("dorade", r"dorade|sea bream", "Sea bream whole fish"),
    ("thon", r"\bthon\b|bonito", "Tuna fish market"),
    ("poisson-fume", r"(poisson|catfish|capitaine|brochet|kobapot|konkoe|bounga|machoiron).*fum|fum.*poisson", "Smoked fish market"),
    ("poisson-chat", r"poisson chat|catfish|pangasius|basa", "Smoked catfish"),
    ("poisson", r"poisson", "Fresh fish market stall"),
]


def normal(texte: str) -> str:
    import unicodedata
    t = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t)


def sorte_de(nom: str) -> str | None:
    n = normal(nom)
    for cle, motif, _ in SORTES:
        if re.search(motif, n):
            return cle
    return None


def texte(meta: dict, champ: str) -> str:
    v = (meta.get(champ) or {}).get("value", "")
    return html.unescape(re.sub(r"<[^>]+>", "", str(v))).strip()


def lire(session: requests.Session, url: str, **options) -> requests.Response:
    for essai in range(6):
        r = session.get(url, timeout=60, **options)
        if r.status_code == 429 or r.status_code >= 500:
            attente = int(r.headers.get("Retry-After") or 0) or 20 * (essai + 1)
            print(f"  occupé ({r.status_code}), attente {attente} s", flush=True)
            time.sleep(attente)
            continue
        return r
    return r


def chercher(session: requests.Session, recherche: str, exclus: set[str]) -> dict | None:
    r = lire(session, API, params={
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6, "gsrlimit": 20,
        "gsrsearch": f"{recherche} filetype:bitmap", "prop": "imageinfo",
        "iiprop": "url|extmetadata|size", "iiurlwidth": 600})
    r.raise_for_status()
    pages = sorted((r.json().get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    for p in pages:
        if p["title"] in exclus:
            continue
        info = (p.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata") or {}
        licence = texte(meta, "LicenseShortName")
        if not any(l in licence.lower() for l in LICENCES) or "nc" in licence.lower().split("-"):
            continue
        if min(info.get("width", 0), info.get("height", 0)) < 400 or not info.get("thumburl"):
            continue
        return {"titre": p["title"], "image": info["thumburl"], "page": info.get("descriptionurl", ""),
                "auteur": texte(meta, "Artist")[:80] or "Wikimedia Commons", "licence": licence}
    return None


def enregistrer_photo(session: requests.Session, url: str, cible: Path) -> bool:
    r = lire(session, url)
    if r.status_code != 200:
        return False
    img = Image.open(io.BytesIO(r.content)).convert("RGB")
    c = min(img.size)                                      # carré centré
    img = img.crop(((img.width - c) // 2, (img.height - c) // 2, (img.width + c) // 2, (img.height + c) // 2))
    img.resize((480, 480), Image.LANCZOS).save(cible, "JPEG", quality=82, optimize=True)
    return True


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--refaire", nargs="*", default=[], help="clés dont on veut une autre photo")
    args = p.parse_args()
    DOSSIER.mkdir(parents=True, exist_ok=True)
    try:
        faites = json.loads(FICHIER.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        faites = {}
    session = requests.Session()
    session.headers.update(ENTETES)
    try:      # sortes dont aucune photo convenable n'existe : « Photo à venir », jamais redemandées
        refusees = set(json.loads((SITE / "data" / "illustrations_refusees.json").read_text(encoding="utf-8")))
    except (OSError, ValueError):
        refusees = set()
    for cle, _, recherche in SORTES:
        if cle in refusees and cle not in args.refaire:
            continue
        ancienne = faites.get(cle)
        if ancienne and cle not in args.refaire and (DOSSIER / f"{cle}.jpg").exists():
            continue
        exclus = set((ancienne or {}).get("rejetees", [])) | ({ancienne["titre"]} if ancienne else set())
        trouve = chercher(session, recherche, exclus)
        if not trouve or not enregistrer_photo(session, trouve["image"], DOSSIER / f"{cle}.jpg"):
            print(f"{cle} : aucune photo libre trouvée", flush=True)
            continue
        trouve["rejetees"] = sorted(exclus)
        trouve["fichier"] = f"images/illustrations/{cle}.jpg"
        faites[cle] = trouve
        FICHIER.write_text(json.dumps(faites, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{cle} : {trouve['titre']} ({trouve['licence']})", flush=True)
        time.sleep(3)


if __name__ == "__main__":
    main()
