"""Ajoute les 45 recettes (3 lots) avec la photo choisie : python -I appliquer.py "1A 2C …" (numéros 1 à 45)."""
import importlib.util, json, re, sys, urllib.parse
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
ICI = Path(__file__).parent
SITE = Path(r"E:\claude code\marchemvogmbi.com")


def charger(nom):
    s = importlib.util.spec_from_file_location(nom, ICI / f"{nom}.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


cand = json.load(open(ICI / "cand.json", encoding="utf-8"))
ordre = cand["ordre"]
choix = {ordre[int(n) - 1]: "ABCD".index(l.upper()) for n, l in re.findall(r"(\d+)\s*([A-Da-d])", sys.argv[1])}
recettes = json.loads((SITE / "data" / "recettes.json").read_text(encoding="utf-8"))
ajout = {c: {} for c in ("es", "pt", "it", "de")}
manque = []
for lot in (1, 2, 3):
    N = charger(f"lot{lot}_fr_en").N
    T = {c: charger(f"lot{lot}_{c}").R for c in ajout}
    for rid, apres, temps, portions, cherche, fr, en in N:
        if any(r["id"] == rid for r in recettes):
            continue
        if rid not in choix:
            manque.append(rid)
            continue
        c = cand["cand"][rid][choix[rid]]
        im = Image.open(ICI / "cand" / f"{rid}_{choix[rid]}.jpg").convert("RGB")
        im.thumbnail((1200, 1200))
        im.save(SITE / "images" / "recettes" / f"{rid}.jpg", quality=86, optimize=True, progressive=True)
        temps_en = temps.replace("de marinade", "marinating").replace("1 nuit", "overnight")
        r = {"id": rid, "titre": fr[0], "pays": fr[1], "temps": temps, "portions": f"{portions} personnes",
             "titre_en": en[0], "pays_en": en[1], "temps_en": temps_en, "portions_en": f"{portions} people",
             "resume": fr[2], "resume_en": en[2],
             "ingredients": [{"texte": t, "cherche": k, "texte_en": e} for t, k, e in zip(fr[3], cherche, en[3])],
             "etapes": fr[4], "etapes_en": en[4], "photo": f"images/recettes/{rid}.jpg",
             "photo_source": c.get("source") or urllib.parse.urlparse(c["page"]).netloc.removeprefix("www."),
             "photo_lien": c["page"]}
        if c.get("licence"):
            r["photo_licence"] = c["licence"]
            r["photo_auteur"] = c.get("auteur", "")
        ids = [x["id"] for x in recettes]
        recettes.insert(ids.index(apres) + 1 if apres in ids else len(recettes), r)
        for code in ajout:
            ajout[code][rid] = T[code][rid]
(SITE / "data" / "recettes.json").write_text(json.dumps(recettes, ensure_ascii=False, indent=1), encoding="utf-8")
for code, nouv in ajout.items():
    chemin = SITE / "outils" / f"recettes_{code}.py"
    texte = chemin.read_text(encoding="utf-8").rstrip()
    assert texte.endswith("}")
    lignes = "".join(f"    {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)},\n" for k, v in nouv.items() if f'"{k}":' not in texte)
    chemin.write_text(texte[:-1] + lignes + "}\n", encoding="utf-8")
print(len(recettes), "recettes ; sans photo choisie :", manque)
