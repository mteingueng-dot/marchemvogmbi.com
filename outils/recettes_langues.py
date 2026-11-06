"""Écrit data/recettes_<code>.json (espagnol, portugais, italien, allemand) depuis outils/recettes_<code>.py.

Contrôle : chaque recette de data/recettes.json est traduite, avec autant d'ingrédients et d'étapes que l'originale.
    python outils/recettes_langues.py
"""
import importlib
import json
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SITE / "outils"))

recettes = json.loads((SITE / "data" / "recettes.json").read_text(encoding="utf-8"))
for code in ("es", "pt", "it", "de"):
    try:
        m = importlib.import_module(f"recettes_{code}")
    except ModuleNotFoundError:
        print(f"{code} : pas encore traduit")
        continue
    sortie, problemes = {}, []
    for r in recettes:
        t = m.R.get(r["id"])
        if not t:
            problemes.append(f"{r['id']} absente")
            continue
        titre, pays, temps, portions, resume, ingredients, etapes = t
        if len(ingredients) != len(r["ingredients"]) or len(etapes) != len(r["etapes"]):
            problemes.append(f"{r['id']} : {len(ingredients)}/{len(r['ingredients'])} ingrédients, {len(etapes)}/{len(r['etapes'])} étapes")
        sortie[r["id"]] = {"titre": titre, "pays": pays, "temps": temps, "portions": portions, "resume": resume,
                           "ingredients": ingredients, "etapes": etapes}
    (SITE / "data" / f"recettes_{code}.json").write_text(json.dumps(sortie, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{code} : {len(sortie)} recettes" + (" ; à corriger : " + " ; ".join(problemes) if problemes else ""))
