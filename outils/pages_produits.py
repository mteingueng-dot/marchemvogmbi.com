"""Une page HTML fixe par produit, dans les 6 langues : produit-<slug>.html (fr à la racine, en/, es/…).

Google lit la fiche sans attendre le JavaScript (« gari Sherbrooke », « attiéké Sherbrooke »…). Même présentation
que la fiche remplie par boutique.js ; boutique.js ne touche pas une fiche marquée data-fixe.
Aucun prix (règle du propriétaire). Appelé par outils/construire_site.py.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import quote_plus

SITE = Path(__file__).resolve().parent.parent
URL = "https://www.marchemvogmbi.com"
VOISINS = 10

TEXTES = {
    "fr": {"boutique": "Boutique", "carac": "Caractéristiques", "conditionnements": "Conditionnements disponibles",
           "couleursDispo": "Couleurs disponibles", "recettes": "Idées recettes", "aussi": "Aussi dans « {} »",
           "poids": "Vendu au poids : pesé en magasin selon la quantité voulue.", "enVente": "En vente au magasin",
           "magasin": "3071 boulevard Portland, Sherbrooke. Disponibilité selon les arrivages.",
           "appeler": "Vérifier la disponibilité : 819 239-9864", "voirRecette": "Voir la recette", "aVenir": "Photo à venir",
           "photo": "Photo", "illustration": "Photo d’illustration", "dp": " : ",
           "format": "format", "formats": "formats", "couleur": "couleur", "couleurs": "couleurs",
           "ville": "à Sherbrooke", "vente": " En vente au Marché Mvog-Mbi, 3071 boul. Portland, Sherbrooke.",
           "vente_court": " En vente au Marché Mvog-Mbi, à Sherbrooke.",
           "heures": " Ouvert tous les jours de 9 h à 21 h."},
    "en": {"boutique": "Shop", "carac": "Details", "conditionnements": "Available sizes", "couleursDispo": "Available colours",
           "recettes": "Recipe ideas", "aussi": "Also in “{}”", "poids": "Sold by weight: weighed in store to the quantity you want.",
           "enVente": "Available in store", "magasin": "3071 boulevard Portland, Sherbrooke. Availability depends on arrivals.",
           "appeler": "Check availability: 819 239-9864", "voirRecette": "See the recipe", "aVenir": "Photo coming soon",
           "photo": "Photo", "illustration": "Illustration photo", "dp": ": ",
           "format": "size", "formats": "sizes", "couleur": "colour", "couleurs": "colours",
           "ville": "in Sherbrooke", "vente": " Available at Marché Mvog-Mbi, 3071 Portland Blvd, Sherbrooke.",
           "vente_court": " Available at Marché Mvog-Mbi in Sherbrooke.",
           "heures": " Open every day from 9 a.m. to 9 p.m."},
    "es": {"boutique": "Tienda", "carac": "Características", "conditionnements": "Formatos disponibles", "couleursDispo": "Colores disponibles",
           "recettes": "Ideas de recetas", "aussi": "También en «{}»", "poids": "Se vende al peso: pesado en la tienda según la cantidad que quieras.",
           "enVente": "A la venta en la tienda", "magasin": "3071 boulevard Portland, Sherbrooke. Disponibilidad según las llegadas.",
           "appeler": "Consultar disponibilidad: 819 239-9864", "voirRecette": "Ver la receta", "aVenir": "Foto próximamente",
           "photo": "Foto", "illustration": "Foto ilustrativa", "dp": ": ",
           "format": "formato", "formats": "formatos", "couleur": "color", "couleurs": "colores",
           "ville": "en Sherbrooke", "vente": " A la venta en el Marché Mvog-Mbi, 3071 boul. Portland, Sherbrooke.",
           "vente_court": " A la venta en el Marché Mvog-Mbi de Sherbrooke.",
           "heures": " Abierto todos los días de 9 a 21 h."},
    "pt": {"boutique": "Loja", "carac": "Características", "conditionnements": "Formatos disponíveis", "couleursDispo": "Cores disponíveis",
           "recettes": "Ideias de receitas", "aussi": "Também em «{}»", "poids": "Vendido a peso: pesado na loja conforme a quantidade desejada.",
           "enVente": "À venda na loja", "magasin": "3071 boulevard Portland, Sherbrooke. Disponibilidade conforme as chegadas.",
           "appeler": "Verificar disponibilidade: 819 239-9864", "voirRecette": "Ver a receita", "aVenir": "Foto em breve",
           "photo": "Foto", "illustration": "Foto ilustrativa", "dp": ": ",
           "format": "formato", "formats": "formatos", "couleur": "cor", "couleurs": "cores",
           "ville": "em Sherbrooke", "vente": " À venda no Marché Mvog-Mbi, 3071 boul. Portland, Sherbrooke.",
           "vente_court": " À venda no Marché Mvog-Mbi, em Sherbrooke.",
           "heures": " Aberto todos os dias das 9h às 21h."},
    "it": {"boutique": "Negozio", "carac": "Caratteristiche", "conditionnements": "Formati disponibili", "couleursDispo": "Colori disponibili",
           "recettes": "Idee ricetta", "aussi": "Anche in «{}»", "poids": "Venduto a peso: pesato in negozio secondo la quantità desiderata.",
           "enVente": "In vendita in negozio", "magasin": "3071 boulevard Portland, Sherbrooke. Disponibilità secondo gli arrivi.",
           "appeler": "Verifica la disponibilità: 819 239-9864", "voirRecette": "Vedi la ricetta", "aVenir": "Foto in arrivo",
           "photo": "Foto", "illustration": "Foto illustrativa", "dp": ": ",
           "format": "formato", "formats": "formati", "couleur": "colore", "couleurs": "colori",
           "ville": "a Sherbrooke", "vente": " In vendita al Marché Mvog-Mbi, 3071 boul. Portland, Sherbrooke.",
           "vente_court": " In vendita al Marché Mvog-Mbi di Sherbrooke.",
           "heures": " Aperto tutti i giorni dalle 9 alle 21."},
    "de": {"boutique": "Shop", "carac": "Merkmale", "conditionnements": "Erhältliche Größen", "couleursDispo": "Erhältliche Farben",
           "recettes": "Rezeptideen", "aussi": "Auch in „{}“", "poids": "Wird nach Gewicht verkauft: im Laden nach Wunsch abgewogen.",
           "enVente": "Im Laden erhältlich", "magasin": "3071 boulevard Portland, Sherbrooke. Verfügbarkeit je nach Lieferung.",
           "appeler": "Verfügbarkeit prüfen: 819 239-9864", "voirRecette": "Zum Rezept", "aVenir": "Foto folgt",
           "photo": "Foto", "illustration": "Beispielfoto", "dp": ": ",
           "format": "Größe", "formats": "Größen", "couleur": "Farbe", "couleurs": "Farben",
           "ville": "in Sherbrooke", "vente": " Erhältlich im Marché Mvog-Mbi, 3071 boul. Portland, Sherbrooke.",
           "vente_court": " Erhältlich im Marché Mvog-Mbi in Sherbrooke.",
           "heures": " Täglich von 9 bis 21 Uhr geöffnet."},
}

e = html.escape


def nom_de_page(p: dict) -> str:
    return f"produit-{p['slug']}.html"


class Catalogue:
    """Produits et textes d'une langue (rayon, description, caractéristiques, recettes liées)."""

    def __init__(self, langue: str):
        self.langue = langue
        d = json.loads((SITE / "data" / "produits.json").read_text(encoding="utf-8"))
        self.produits = d["produits"]
        self.x = {}
        if langue not in ("fr", "en"):
            chemin = SITE / "data" / f"produits_{langue}.json"
            self.x = json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else {}
        recettes = json.loads((SITE / "data" / "recettes.json").read_text(encoding="utf-8"))
        rx = {}
        if langue not in ("fr", "en"):
            chemin = SITE / "data" / f"recettes_{langue}.json"
            rx = json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else {}
        self.recettes = {}
        for r in recettes:
            if langue == "fr":
                self.recettes[r["id"]] = (r["titre"], r["pays"])
            elif langue == "en":
                self.recettes[r["id"]] = (r.get("titre_en") or r["titre"], r.get("pays_en") or r["pays"])
            else:
                t = rx.get(r["id"], {})
                self.recettes[r["id"]] = (t.get("titre") or r.get("titre_en") or r["titre"], t.get("pays") or r.get("pays_en") or r["pays"])

    def rayon(self, p: dict) -> str:
        if self.langue == "fr":
            return p["rayon"]
        if self.langue == "en":
            return p.get("rayon_en") or p["rayon"]
        return self.x.get("rayons", {}).get(p["rayon"]) or p.get("rayon_en") or p["rayon"]

    def description(self, p: dict) -> str:
        if self.langue == "fr":
            return p.get("description", "")
        if self.langue == "en":
            return p.get("description_en") or p.get("description", "")
        return self.x.get("d", {}).get(p["id"]) or p.get("description_en") or ""

    def caracteristiques(self, p: dict) -> dict:
        if self.langue == "fr":
            c = p.get("caracteristiques", {})
        elif self.langue == "en":
            c = p.get("caracteristiques_en", {})
        else:
            c = {self.x.get("carac", {}).get(k, k): self.x.get("valeurs", {}).get(v, v)
                 for k, v in p.get("caracteristiques", {}).items()}
        return {k: v for k, v in c.items() if not k.startswith(("Conditionnements", "Couleurs", "Available"))}


def details(p: dict, t: dict) -> str:
    if p.get("couleurs") and len(p["couleurs"]) > 1:
        n = len(p["couleurs"])
        return f"{n} {t['couleurs'] if n > 1 else t['couleur']}"
    if p.get("conditionnements"):
        n = len(p["conditionnements"])
        return f"{n} {t['formats'] if n > 1 else t['format']}"
    return ""


def sans_photo(grand: bool, t: dict) -> str:
    return (f'<span class="sans-photo{" grand" if grand else ""}" aria-hidden="true"><img src="images/icone.png" alt="" '
            f'width="140" height="140"><em>{t["aVenir"]}</em></span>')


def vignette(p: dict, cat: Catalogue, t: dict) -> str:
    """Même carte que vignette() de boutique.js."""
    image = (f'<img src="{e(p["photo"])}" alt="{e(p["nom"])}" loading="lazy" width="240" height="240"'
             f'{" class=\"illustration\"" if p.get("illustration") else ""}>') if p.get("photo") else sans_photo(False, t)
    d = details(p, t)
    return (f'<a class="carte-produit" href="{nom_de_page(p)}">\n      <span class="carte-image">{image}</span>\n'
            f'      <span class="carte-corps">\n        <span class="carte-rayon">{e(cat.rayon(p))}</span>\n'
            f'        <span class="carte-nom">{e(p["nom"])}</span>\n'
            + (f'        <span class="carte-details">{e(d)}</span>\n' if d else "")
            + "      </span>\n    </a>")


def titre_page(nom: str, t: dict) -> str:
    for f in (f"{nom} {t['ville']} | Marché Mvog-Mbi", f"{nom} | Marché Mvog-Mbi", f"{nom} | Mvog-Mbi"):
        if len(f) <= 60:
            return f
    return f"{nom[:48].rsplit(' ', 1)[0]} | Mvog-Mbi"


def description_page(texte: str, t: dict, nom: str = "") -> str:
    """Description du produit + où l'acheter, 120 à 160 caractères : un texte court reçoit aussi les heures, puis
    le nom du produit en tête."""
    texte = texte.strip()
    if texte and not texte.endswith((".", "!", "?", "…")):
        texte += "."
    essais = [texte + t["vente"], texte + t["vente_court"], texte + t["vente"] + t["heures"],
              texte + t["vente_court"] + t["heures"]]
    if nom:
        essais += [f"{nom}. {texte}{t['vente']}{t['heures']}", f"{nom}. {texte}{t['vente_court']}{t['heures']}"]
    essais = [x.strip() for x in essais]
    bon = next((x for x in essais if 120 <= len(x) <= 160), None)          # le premier qui a la bonne longueur
    if bon:
        return bon
    tiennent = [x for x in essais if len(x) <= 160]
    if tiennent:
        return max(tiennent, key=len)
    import referencement                               # texte coupé pour garder la mention de Sherbrooke
    debut = referencement.couper(texte, 160 - len(t["vente_court"]))
    if len(debut) >= 60:
        return debut + t["vente_court"]
    return referencement.couper(texte, 160)


def fil_json_ld(langue: str, dossier: str, t: dict, rayon_fr: str, rayon: str, nom: str, fichier: str) -> str:
    base = f"{URL}/{dossier}"
    d = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": t["boutique"], "item": f"{base}boutique.html"},
        {"@type": "ListItem", "position": 2, "name": rayon, "item": f"{base}boutique.html?rayon={quote_plus(rayon_fr)}"},
        {"@type": "ListItem", "position": 3, "name": nom, "item": f"{base}{fichier}"}]}
    return '  <script type="application/ld+json">\n  ' + json.dumps(d, ensure_ascii=False) + "\n  </script>\n"


def pages(langue: str, dossier: str) -> list[dict]:
    """{fichier, contenu, titre, description, photo, ld} pour chaque produit."""
    t = TEXTES[langue]
    cat = Catalogue(langue)
    par_rayon: dict[str, list] = {}
    for p in cat.produits:
        par_rayon.setdefault(p["rayon"], []).append(p)
    sortie = []
    for p in cat.produits:
        fichier = nom_de_page(p)
        rayon = cat.rayon(p)
        nom = p["nom"]
        if p.get("photo"):
            image = (f'<img src="{e(p["photo"])}" alt="{e(nom)}" width="480" height="480"'
                     f'{" class=\"illustration\"" if p.get("illustration") else ""}>')
        else:
            image = sans_photo(True, t)
        source = ""
        if p.get("photo_source") and re.search(r"\bCC\b", p["photo_source"]):
            lib = t["illustration"] if p.get("illustration") else t["photo"]
            lien = (f'<a href="{e(p["photo_lien"])}" rel="noopener" target="_blank">{e(p["photo_source"])}</a>'
                    if p.get("photo_lien") else e(p["photo_source"]))
            source = f'<p class="source">{lib}{t["dp"]}{lien}</p>'
        formats = ""
        if p.get("conditionnements"):
            formats = (f'<h2>{t["conditionnements"]}</h2><ul class="pastilles">'
                       + "".join(f"<li>{e(f)}</li>" for f in p["conditionnements"]) + "</ul>")
        couleurs = ""
        if p.get("couleurs"):
            items = []
            for c in p["couleurs"]:
                desc = c.get("description") if langue == "fr" else (c.get("description_en") or c.get("description"))
                items.append(f"<li><strong>{e(c['code'])}</strong>" + (f"<span>{e(desc)}</span>" if desc else "") + "</li>")
            couleurs = f'<h2>{t["couleursDispo"]}</h2><ul class="couleurs">{"".join(items)}</ul>'
        carac = cat.caracteristiques(p)
        lignes = "".join(f'<tr><th scope="row">{e(k)}</th><td>{e(v)}</td></tr>' for k, v in carac.items())
        tableau = f'<h2>{t["carac"]}</h2><table class="caracteristiques"><tbody>{lignes}</tbody></table>' if lignes else ""
        liees = [r for r in p.get("recettes", []) if r in cat.recettes]
        bloc_recettes = ""
        if liees:
            bloc_recettes = (f'<h2>{t["recettes"]}</h2><div class="recettes-liees">' + "".join(
                f'<a href="recette-{r}.html"><strong>{e(cat.recettes[r][0])}</strong>'
                f'<span>{e(cat.recettes[r][1])} · {t["voirRecette"]} →</span></a>' for r in liees) + "</div>")
        texte = cat.description(p)
        # voisins : les 10 produits qui suivent dans le rayon (chaque fiche reçoit des liens de 10 autres)
        rang = par_rayon[p["rayon"]]
        i = rang.index(p)
        voisins = [rang[(i + k) % len(rang)] for k in range(1, min(VOISINS, len(rang) - 1) + 1)]
        bloc_voisins = ""
        if voisins:
            bloc_voisins = (f'    <section class="voisins">\n      <h2 id="voisins-titre">{e(t["aussi"].format(rayon))}</h2>\n'
                            f'      <div id="voisins" class="produits">\n'
                            + "\n".join(vignette(v, cat, t) for v in voisins) + "\n      </div>\n    </section>\n")
        lien_rayon = f"boutique.html?rayon={quote_plus(p['rayon'])}"
        contenu = f'''  <main class="conteneur fiche-page">
    <nav class="fil" id="fil" aria-label="Fil d’Ariane"><a href="boutique.html">{t["boutique"]}</a> › <a href="{lien_rayon}">{e(rayon)}</a> › <span>{e(nom)}</span></nav>
    <article id="fiche" class="fiche" data-fixe>
        <div class="fiche-image">{image}{source}</div>
        <div class="fiche-texte">
          <p class="surtitre">{e(rayon)}</p>
          <h1>{e(nom)}</h1>
          <p class="fiche-description">{e(texte)}</p>
          {f'<p class="note">{t["poids"]}</p>' if p.get("unite") else ""}
          {formats}{couleurs}
          {tableau}
          {bloc_recettes}
          <div class="dispo">
            <strong>{t["enVente"]}</strong>
            <span>{t["magasin"]}</span>
            <a class="bouton" href="tel:+18192399864">{t["appeler"]}</a>
          </div>
        </div>
    </article>
{bloc_voisins}  </main>
'''
        sortie.append({"fichier": fichier, "contenu": contenu, "titre": titre_page(nom, t),
                       "description": description_page(texte, t, nom), "photo": p.get("photo") or "images/logo.png",
                       "ld": fil_json_ld(langue, dossier, t, p["rayon"], rayon, nom, fichier)})
    return sortie
