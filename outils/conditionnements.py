"""Une seule fiche pour un produit vendu en plusieurs formats (« Clic Farine de maïs blanc 907g / 2kg / 5kg »).

Le format (poids ou volume) est retiré du nom ; les articles qui ont alors le même nom, dans le même rayon,
deviennent une fiche avec la liste « Conditionnements disponibles », du plus petit au plus grand.
"""
from __future__ import annotations

import re
import unicodedata

FORMAT = re.compile(r"(?<![\w#])((?:\d+\s*[xX]\s*)?\d+(?:[.,]\d+)?)\s*(kg|g|gr|mg|lbs?|oz|ml|cl|l|litres?)\b\.?", re.I)
EN_FIN = re.compile(r"[\s\-–/(]*\b(en|de)\s*$", re.I)
GRAMMES = {"kg": 1000, "g": 1, "gr": 1, "mg": .001, "lb": 453.6, "lbs": 453.6, "oz": 28.35,
           "l": 1000, "litre": 1000, "litres": 1000, "ml": 1, "cl": 10}


def sans_accents(t: str) -> str:
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()


def format_et_base(nom: str) -> tuple[str, str] | None:
    m = FORMAT.search(nom)
    if not m:
        return None
    base = (nom[:m.start()] + " " + nom[m.end():]).strip()
    base = EN_FIN.sub("", re.sub(r"\s+", " ", base)).strip(" -–/(")
    unite = m.group(2).lower()
    unite = {"gr": "g", "lbs": "lb", "litre": "L", "litres": "L", "l": "L"}.get(unite, unite)
    quantite = re.sub(r"\s*[xX]\s*", " × ", m.group(1)).replace(".", ",")
    return base, f"{quantite} {unite}"


def poids(fmt: str) -> float:
    m = re.match(r"(?:(\d+) × )?(\d+(?:,\d+)?) (\S+)", fmt)
    if not m:
        return 0
    n = int(m.group(1) or 1)
    return n * float(m.group(2).replace(",", ".")) * GRAMMES.get(m.group(3).lower(), 1)


def regrouper(produits: list[dict]) -> list[dict]:
    groupes: dict[tuple, list[tuple[str, dict]]] = {}
    for p in produits:
        if p.get("couleurs"):
            continue
        fb = format_et_base(p["nom"])
        if fb:
            cle = (p["rayon"], re.sub(r"\W+", "", sans_accents(fb[0]).lower()))
            groupes.setdefault(cle, []).append((fb[1], p))
    retires, remplacants = set(), {}
    for variantes in groupes.values():
        if len(variantes) < 2:
            continue
        variantes.sort(key=lambda v: poids(v[0]))
        formats = list(dict.fromkeys(f for f, _ in variantes))
        tete = next((p for _, p in variantes if p["photo"] and not p.get("illustration")),
                    next((p for _, p in variantes if p["photo"]), variantes[0][1]))
        fiche = dict(tete)
        base = format_et_base(variantes[0][1]["nom"])[0]
        fiche.update({"nom": base, "ids": [p["id"] for _, p in variantes], "conditionnements": formats})
        car = {k: v for k, v in tete.get("caracteristiques", {}).items() if k not in ("Code-barres", "Format")}
        car["Conditionnements disponibles"] = ", ".join(formats)
        fiche["caracteristiques"] = car
        for _, p in variantes:
            retires.add(p["id"])
        remplacants[tete["id"]] = fiche
    return [remplacants.get(p["id"], p) for p in produits if p["id"] in remplacants or p["id"] not in retires]
