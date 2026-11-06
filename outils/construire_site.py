"""Assemble les pages du site en français (racine) et dans les autres langues (dossiers en/, es/, pt/, it/, de/) :
même bandeau, même en-tête (avec le choix de la langue) et même pied de page partout.

Le contenu de chaque page est dans sources/<page>.html (français) et sources/<langue>/<page>.html, seulement
le <main>. Les textes communs des langues autres que le français et l'anglais sont dans outils/langue_<code>.py,
les recettes traduites dans data/recettes_<code>.json. La page Rayons est fabriquée d'après data/produits.json, la page Recettes d'après data/recettes.json.
Après une modification :

    python outils/construire_site.py
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from urllib.parse import quote_plus

SITE = Path(__file__).resolve().parent.parent
SOURCES = SITE / "sources"
URL = "https://www.marchemvogmbi.com"
sys.path.insert(0, str(SITE / "outils"))
from langues import RAYONS_EN, TEXTE_RAYON  # noqa: E402
import importlib  # noqa: E402

LANGUES = ["fr", "en", "es", "pt", "it", "de"]
NOMS_LANGUES = {"fr": "Français", "en": "English", "es": "Español", "pt": "Português", "it": "Italiano", "de": "Deutsch"}
AUTRES = {c: importlib.import_module(f"langue_{c}") for c in LANGUES[2:]}   # textes des langues ajoutées


def racine_de(langue: str) -> str:
    return "" if langue == "fr" else "../"

FICHIERS = ["index.html", "nouveautes.html", "boutique.html", "rayons.html", "recettes.html", "a-propos.html", "carriere.html",
            "contact.html", "produit.html"]
SOURCE = {"index.html": "accueil"}                      # nom du fichier de sources/ quand il diffère
AVEC_BOUTIQUE = {"index.html", "boutique.html", "produit.html", "rayons.html"}   # pages qui lisent le catalogue

L = {
    "fr": {
        "lang": "fr-CA", "dossier": "", "menu": ["Accueil", "Nouveautés", "Boutique", "Rayons", "Recettes", "À propos de nous", "Carrière", "Contact"],
        "pages": {
            "index.html": ("Marché Mvog-Mbi Sherbrooke – Le carrefour où toutes les cultures se rencontrent",
                           "Épicerie africaine, caribéenne et latine à Sherbrooke : plus de 2 000 produits, prix imbattables, livraison gratuite dès 100 $. Ouvert tous les jours de 9 h à 21 h."),
            "nouveautes.html": ("Nouveautés – Marché Mvog-Mbi Sherbrooke", "Les derniers arrivages et les offres du moment au Marché Mvog-Mbi, à Sherbrooke."),
            "boutique.html": ("Boutique – Marché Mvog-Mbi Sherbrooke", "Tous les produits du Marché Mvog-Mbi avec leurs photos, descriptions, formats et couleurs."),
            "produit.html": ("Produit – Marché Mvog-Mbi Sherbrooke", "Fiche produit du Marché Mvog-Mbi, épicerie africaine, caribéenne et latine à Sherbrooke."),
            "rayons.html": ("Nos rayons – Marché Mvog-Mbi Sherbrooke", "Tous les rayons du Marché Mvog-Mbi : fruits et légumes, féculents, farines, épices, poissons, viandes, boissons, beauté…"),
            "recettes.html": ("Recettes – Marché Mvog-Mbi Sherbrooke", "Recettes d’Afrique, des Caraïbes et d’Amérique latine pas à pas : ndolé, jollof, thiéboudienne, yassa, moambé, eru, koki, attiéké poisson, mafé…"),
            "a-propos.html": ("À propos de nous – Marché Mvog-Mbi Sherbrooke", "Le Marché Mvog-Mbi, le carrefour où toutes les cultures se rencontrent, à Sherbrooke."),
            "carriere.html": ("Carrière – Marché Mvog-Mbi Sherbrooke", "Travailler au Marché Mvog-Mbi à Sherbrooke : envoyez votre candidature."),
            "contact.html": ("Contact – Marché Mvog-Mbi Sherbrooke", "Adresse, heures, téléphone et courriel du Marché Mvog-Mbi, 3071 boulevard Portland, Sherbrooke."),
        },
        "slogan": "Le carrefour des cultures", "ville": "Sherbrooke",
        "bandeau": ["<strong>Ouvert tous les jours</strong> de 9 h à 21 h", "<strong>Livraison gratuite</strong> dès 100 $ (5 km)",
                    "<strong>Prix imbattables</strong> : 1 ¢ de moins qu’ailleurs"],
        "pied_texte": "Le carrefour où toutes les cultures se rencontrent.<br>Épicerie africaine, caribéenne &amp; latine.",
        "pied_titres": ["Le site", "Magasin", "Heures", "Livraison"],
        "heures": "Tous les jours<br>9 h à 21 h", "livraison": "Gratuite dès 100 $<br>dans un rayon de 5 km",
        "droits": "© 2026 Concept Informatique Inc. Tous droits réservés.", "menu_ouvrir": "Ouvrir le menu",
        "autre": "EN", "autre_titre": "Langue", "produits": "produits", "produit": "produit",
        "barre": ["Appeler", "Itinéraire", "Boutique", "Discuter"], "haut": "Haut de page", "chercher": "Rechercher un produit",
        "pied_chat": "Une question&nbsp;? <button type=\"button\" class=\"lien-chat\" data-assistant>Discutez avec notre assistant</button>",
    },
    "en": {
        "lang": "en-CA", "dossier": "en/", "menu": ["Home", "New", "Shop", "Aisles", "Recipes", "About us", "Careers", "Contact"],
        "pages": {
            "index.html": ("Marché Mvog-Mbi Sherbrooke – Where all cultures meet",
                           "African, Caribbean and Latin American grocery in Sherbrooke: over 2,000 products, unbeatable prices, free delivery from $100. Open every day from 9 a.m. to 9 p.m."),
            "nouveautes.html": ("New arrivals – Marché Mvog-Mbi Sherbrooke", "The latest arrivals and current offers at Marché Mvog-Mbi in Sherbrooke."),
            "boutique.html": ("Shop – Marché Mvog-Mbi Sherbrooke", "All Marché Mvog-Mbi products with photos, descriptions, sizes and colours."),
            "produit.html": ("Product – Marché Mvog-Mbi Sherbrooke", "Product page of Marché Mvog-Mbi, African, Caribbean and Latin American grocery in Sherbrooke."),
            "rayons.html": ("Our aisles – Marché Mvog-Mbi Sherbrooke", "Every aisle at Marché Mvog-Mbi: produce, roots and tubers, flours, spices, fish, meat, drinks, beauty…"),
            "recettes.html": ("Recipes – Marché Mvog-Mbi Sherbrooke", "Step-by-step African, Caribbean and Latin American recipes: ndolé, jollof, thieboudienne, yassa, moambe, eru, koki, attiéké with fish, mafé…"),
            "a-propos.html": ("About us – Marché Mvog-Mbi Sherbrooke", "Marché Mvog-Mbi, where all cultures meet, in Sherbrooke."),
            "carriere.html": ("Careers – Marché Mvog-Mbi Sherbrooke", "Work at Marché Mvog-Mbi in Sherbrooke: send us your application."),
            "contact.html": ("Contact – Marché Mvog-Mbi Sherbrooke", "Address, hours, phone and email of Marché Mvog-Mbi, 3071 boulevard Portland, Sherbrooke."),
        },
        "slogan": "Where cultures meet", "ville": "Sherbrooke",
        "bandeau": ["<strong>Open every day</strong> 9 a.m. – 9 p.m.", "<strong>Free delivery</strong> from $100 (5 km)",
                    "<strong>Unbeatable prices</strong>: 1¢ less than elsewhere"],
        "pied_texte": "Where all cultures meet.<br>African, Caribbean &amp; Latin American grocery.",
        "pied_titres": ["Site", "Store", "Hours", "Delivery"],
        "heures": "Every day<br>9 a.m. – 9 p.m.", "livraison": "Free from $100<br>within 5 km",
        "droits": "© 2026 Concept Informatique Inc. All rights reserved.", "menu_ouvrir": "Open the menu",
        "autre": "FR", "autre_titre": "Language", "produits": "products", "produit": "product",
        "barre": ["Call", "Directions", "Shop", "Chat"], "haut": "Back to top", "chercher": "Search for a product",
        "pied_chat": "A question? <button type=\"button\" class=\"lien-chat\" data-assistant>Chat with our assistant</button>",
    },
}
for _c, _m in AUTRES.items():
    L[_c] = _m.SITE
MENU_FICHIERS = ["index.html", "nouveautes.html", "boutique.html", "rayons.html", "recettes.html", "a-propos.html", "carriere.html", "contact.html"]

# Photo de la tuile de chaque rayon (photos prises au magasin)
PHOTO_RAYON = {
    "Fruits & légumes": "piment-jaune", "Féculents": "igname", "Farines": "foufou", "Riz, graines & pâtes": "riz",
    "Épices & sauces": "egusi", "Huiles": "huile-palme", "Conserves": "sardines", "Produits de la mer": "maquereau",
    "Viandes & volailles": "viande", "Légumes congelés": "congeles", "Boissons": "boissons", "Thés & cafés": "milo",
    "Collations": "chips-plantain", "Tartinades": "chocopain", "Produits latinos": "latinos", "Beauté": "beaute",
    "Mèches & accessoires": "meches", "Entretien": "entretien", "Autres produits": "marmites",
}

FICHE_COMMERCE = {
    "@context": "https://schema.org", "@type": "GroceryStore", "name": "Marché Mvog-Mbi Sherbrooke",
    "description": "Épicerie africaine, caribéenne et latine", "url": URL, "telephone": "+1-819-239-9864",
    "email": "contact@marchemvogmbi.com", "image": f"{URL}/images/logo.png",
    "address": {"@type": "PostalAddress", "streetAddress": "3071 boulevard Portland", "addressLocality": "Sherbrooke",
                "addressRegion": "QC", "postalCode": "J1L 2Y7", "addressCountry": "CA"},
    "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                   "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                   "opens": "09:00", "closes": "21:00"}],
}


FORMULAIRE = {
    "fr": {"titre": "Envoyez-nous un message", "nom": "Prénom et nom", "nom_ex": "ex. Marie Tremblay",
           "courriel": "Courriel", "courriel_ex": "vous@exemple.com", "sujet": "Sujet", "message": "Message",
           "message_ex": "Écrivez votre question ou votre demande…", "piece": "Pièce jointe (facultatif)",
           "formats": "Formats acceptés : PDF et Word (.pdf, .doc, .docx), 10 Mo au maximum.",
           "parcourir": "Parcourir", "aucun": "Aucun fichier sélectionné", "envoyer": "Envoyer la demande",
           "ok": "Merci ! Votre message est bien envoyé. Nous vous répondons rapidement.",
           "erreurs": {"champs": "Remplissez votre nom, un courriel valide et votre message.",
                       "taille": "La pièce jointe dépasse 10 Mo.", "format": "La pièce jointe doit être un fichier PDF ou Word.",
                       "envoi": "Le message n’a pas pu partir. Appelez-nous au 819 239-9864 ou écrivez à contact@marchemvogmbi.com."},
           "sujets": [("produit", "Question sur un produit"), ("commande", "Commande ou livraison"),
                      ("prix", "Garantie du meilleur prix"), ("candidature", "Candidature (CV)"),
                      ("fournisseur", "Fournisseur ou partenariat"), ("autre", "Autre demande")]},
    "en": {"titre": "Send us a message", "nom": "Full name", "nom_ex": "e.g. Mary Smith",
           "courriel": "Email", "courriel_ex": "you@example.com", "sujet": "Subject", "message": "Message",
           "message_ex": "Write your question or request…", "piece": "Attachment (optional)",
           "formats": "Accepted formats: PDF and Word (.pdf, .doc, .docx), 10 MB maximum.",
           "parcourir": "Browse", "aucun": "No file selected", "envoyer": "Send the request",
           "ok": "Thank you! Your message has been sent. We will get back to you shortly.",
           "erreurs": {"champs": "Please enter your name, a valid email and your message.",
                       "taille": "The attachment is larger than 10 MB.", "format": "The attachment must be a PDF or Word file.",
                       "envoi": "The message could not be sent. Call us at 819 239-9864 or email contact@marchemvogmbi.com."},
           "sujets": [("produit", "Question about a product"), ("commande", "Order or delivery"),
                      ("prix", "Best price guarantee"), ("candidature", "Job application (résumé)"),
                      ("fournisseur", "Supplier or partnership"), ("autre", "Other request")]},
}
for _c, _m in AUTRES.items():
    FORMULAIRE[_c] = _m.FORMULAIRE


def credit_photo(r: dict, en: bool) -> str:
    """Mention de la source d'une photo de plat trouvée en ligne (aucune pour les photos du magasin)."""
    if not r.get("photo_source"):
        return ""
    lien = html.escape(r.get("photo_lien", ""))
    nom = html.escape(r["photo_source"])
    texte = f'<a href="{lien}" rel="noopener" target="_blank">{nom}</a>' if lien else nom
    return f'<figcaption>{"Photo" if en else "Photo"} : {texte}</figcaption>'

def formulaire(langue: str, page: str, sujet: str) -> str:
    f = FORMULAIRE[langue]
    options = "".join(f'<option value="{v}"{" selected" if v == sujet else ""}>{html.escape(n)}</option>' for v, n in f["sujets"])
    erreurs = "".join(f'\n          <p class="form-message erreur" data-erreur="{k}" hidden>{html.escape(v)}</p>'
                      for k, v in f["erreurs"].items())
    action = racine_de(langue) + "contact.php"
    accepte = ".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return f"""<form id="formulaire" class="formulaire" action="{action}" method="post" enctype="multipart/form-data">
          <h2>{f["titre"]}</h2>
          <p class="form-message ok" data-ok hidden>{html.escape(f["ok"])}</p>{erreurs}
          <input type="hidden" name="page" value="{page}">
          <input type="hidden" name="debut" value="">
          <div class="champ-cache" aria-hidden="true"><label>Site web <input type="text" name="site_web" tabindex="-1" autocomplete="off"></label></div>
          <div class="form-ligne">
            <label class="champ"><span>{f["nom"]}</span><input type="text" name="nom" required maxlength="120" autocomplete="name" placeholder="{f["nom_ex"]}"></label>
            <label class="champ"><span>{f["courriel"]}</span><input type="email" name="courriel" required maxlength="160" autocomplete="email" placeholder="{f["courriel_ex"]}"></label>
          </div>
          <label class="champ"><span>{f["sujet"]}</span><select name="sujet">{options}</select></label>
          <label class="champ"><span>{f["message"]}</span><textarea name="message" required rows="6" maxlength="8000" placeholder="{f["message_ex"]}"></textarea></label>
          <div class="champ">
            <span>{f["piece"]}</span>
            <small>{f["formats"]}</small>
            <label class="fichier"><input type="file" name="piece" accept="{accepte}"><b>{f["parcourir"]}</b><em data-aucun="{html.escape(f["aucun"])}">{html.escape(f["aucun"])}</em></label>
          </div>
          <button type="submit" class="bouton bouton-plein">{f["envoyer"]}</button>
        </form>"""


def bandeau(t: dict) -> str:
    morceaux = [f'<span><span class="point-ouvert" aria-hidden="true"></span>{t["bandeau"][0]}</span>',
                f'<span>{t["bandeau"][1]}</span>', f'<span>{t["bandeau"][2]}</span>',
                '<a href="tel:+18192399864">819 239-9864</a>']
    return '  <div class="bandeau">\n    <div class="conteneur">\n      ' + "\n      ".join(morceaux) + "\n    </div>\n  </div>\n"


def entete(t: dict, actif: str, fichier: str, langue: str) -> str:
    liens = "\n".join(f'        <a href="{f}"{" aria-current=\"page\"" if f == actif else ""}>{n}</a>'
                      for f, n in zip(MENU_FICHIERS, t["menu"]))
    choix = []
    for c in LANGUES:
        lien = racine_de(langue) + ("" if c == "fr" else f"{c}/") + fichier
        actuel = ' aria-current="true"' if c == langue else ""
        choix.append(f'<a href="{lien}" hreflang="{c}" lang="{c}"{actuel} data-garder-recherche>'
                     f'<b>{c.upper()}</b> {NOMS_LANGUES[c]}</a>')
    langues = (f'<details class="langues"><summary title="{t["autre_titre"]}" aria-label="{t["autre_titre"]}">'
               f'{langue.upper()}</summary><div class="langues-liste">{"".join(choix)}</div></details>')
    return f'''  <header class="entete">
    <div class="conteneur entete-ligne">
      <a href="index.html" class="marque">
        <img src="{racine_de(langue)}images/icone.png" alt="" width="42" height="42">
        <span>Marché Mvog-Mbi<small>{t["slogan"]}</small></span>
      </a>
      <input type="checkbox" id="menu-ouvert" class="menu-case" aria-label="{t["menu_ouvrir"]}">
      <label for="menu-ouvert" class="menu-bouton" aria-hidden="true"><i></i><i></i><i></i></label>
      <nav class="menu">
{liens}
        <span class="menu-actions">
          <a href="boutique.html#recherche" class="icone-rond" title="{t["chercher"]}" aria-label="{t["chercher"]}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg></a>
          {langues}
          <a href="tel:+18192399864" class="bouton bouton-petit"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>819 239-9864</a>
        </span>
      </nav>
    </div>
  </header>
'''


def pied(t: dict, langue: str) -> str:
    liens = "<br>".join(f'<a href="{f}">{n}</a>' for f, n in zip(MENU_FICHIERS, t["menu"]))
    racine = racine_de(langue)
    ti = t["pied_titres"]
    return f'''  <footer class="pied">
    <div class="conteneur">
      <div class="pied-grille">
        <div>
          <a href="index.html" class="marque"><img src="{racine}images/icone.png" alt="" width="42" height="42"><span>Marché Mvog-Mbi<small>Sherbrooke</small></span></a>
          <p>{t["pied_texte"]}</p>
          <p class="pied-chat">{t["pied_chat"]}</p>
        </div>
        <div>
          <h3>{ti[0]}</h3>
          <p>{liens}</p>
        </div>
        <div>
          <h3>{ti[1]}</h3>
          <p>3071 boulevard Portland<br>Sherbrooke (QC) J1L 2Y7<br><a href="tel:+18192399864">819 239-9864</a><br><a href="mailto:contact@marchemvogmbi.com">contact@marchemvogmbi.com</a></p>
        </div>
        <div>
          <h3>{ti[2]}</h3>
          <p>{t["heures"]}</p>
          <h3 class="pied-h3-espace">{ti[3]}</h3>
          <p>{t["livraison"]}</p>
        </div>
      </div>
      <p class="droits">{t["droits"]}</p>
    </div>
  </footer>
'''


def barre_mobile(t: dict) -> str:
    b = t["barre"]
    ic = {
        "tel": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
        "carte": '<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
        "panier": '<path d="M3 4h2l2.4 11.2a2 2 0 0 0 2 1.6h7.7a2 2 0 0 0 2-1.5L21 8H6.2"/><circle cx="10" cy="20.5" r="1.2"/><circle cx="17" cy="20.5" r="1.2"/>',
        "chat": '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/>',
    }
    svg = lambda k: f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ic[k]}</svg>'
    carte = "https://www.google.com/maps/dir/?api=1&amp;destination=3071+boulevard+Portland+Sherbrooke+QC+J1L+2Y7"
    return f'''  <nav class="barre-mobile" aria-label="Actions">
    <a href="tel:+18192399864">{svg("tel")}<span>{b[0]}</span></a>
    <a href="{carte}" target="_blank" rel="noopener">{svg("carte")}<span>{b[1]}</span></a>
    <a href="boutique.html">{svg("panier")}<span>{b[2]}</span></a>
    <button type="button" data-assistant>{svg("chat")}<span>{b[3]}</span></button>
  </nav>
  <button type="button" class="haut-de-page" aria-label="{t["haut"]}" title="{t["haut"]}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M6 11l6-6 6 6"/></svg></button>
'''


def page_rayons(source: str, langue: str) -> str:
    d = json.loads((SITE / "data" / "produits.json").read_text(encoding="utf-8"))
    t = L[langue]
    racine = racine_de(langue)
    tuiles = []
    for r in d["rayons"]:
        n = sum(1 for p in d["produits"] if p["rayon"] == r)
        cle = PHOTO_RAYON.get(r)
        photo = f"images/magasin/{cle}.jpg" if cle and (SITE / "images" / "magasin" / f"{cle}.jpg").exists() else ""
        if langue in AUTRES:
            nom, texte = AUTRES[langue].RAYONS.get(r, r), html.escape(AUTRES[langue].TEXTE_RAYON.get(r, ""))
        else:
            nom = RAYONS_EN.get(r, r) if langue == "en" else r
            texte = html.escape(TEXTE_RAYON.get(r, ("", ""))[1 if langue == "en" else 0])
        nb = f"{n} {t['produits'] if n > 1 else t['produit']}"
        img = f'<img src="{racine}{photo}" alt="" loading="lazy">' if photo else ""
        tuiles.append(f'          <a class="tuile{"" if photo else " sans-image"}" href="boutique.html?rayon={quote_plus(r)}">{img}'
                      f'<em class="tuile-nombre">{nb}</em><strong>{html.escape(nom)}</strong><span>{texte}</span></a>')
    total = f"{len(d['produits']):,}".replace(",", t.get("milliers", " " if langue == "fr" else ","))
    return source.replace("<!--TUILES-->", "\n".join(tuiles)).replace("<!--NOMBRE-->", total)


def page_recettes(source: str, langue: str) -> str:
    recettes = json.loads((SITE / "data" / "recettes.json").read_text(encoding="utf-8"))
    en = langue == "en"
    racine = racine_de(langue)
    if langue in AUTRES:                                 # data/recettes_<code>.json : {id: {titre, pays, …, ingredients, etapes}}
        chemin = SITE / "data" / f"recettes_{langue}.json"
        trad = json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else {}
        for r in recettes:
            x = trad.get(r["id"], {})
            for k in ("titre", "pays", "temps", "portions", "resume"):
                r[k + "_x"] = x.get(k) or r.get(k + "_en") or r[k]
            r["etapes_x"] = x.get("etapes") or r.get("etapes_en") or r["etapes"]
            for i, ing in zip(r["ingredients"], x.get("ingredients") or [i.get("texte_en") for i in r["ingredients"]]):
                i["texte_x"] = ing or i.get("texte_en") or i["texte"]
        v = lambda r, k: r[k + "_x"]
        lib = AUTRES[langue].RECETTES
    else:
        v = (lambda r, k: r.get(k + "_en") or r[k]) if en else (lambda r, k: r[k])
        lib = {"ing": "Ingredients" if en else "Ingrédients", "prep": "Method" if en else "Préparation",
               "temps": "Time" if en else "Temps", "pour": "Serves" if en else "Pour", "trouver": "Find in the shop" if en else "Trouver à la boutique",
               "retour": "Back to recipes" if en else "Retour aux recettes", "autres": "Other recipes" if en else "Autres recettes"}
    if langue in AUTRES:
        texte_ing, etapes_de = (lambda i: i["texte_x"]), (lambda r: r["etapes_x"])
    else:
        texte_ing = lambda i: i.get("texte_en") if en and i.get("texte_en") else i["texte"]
        etapes_de = lambda r: r.get("etapes_en") if en and r.get("etapes_en") else r["etapes"]
    import filtre_pays
    filtre, pays_tuile = filtre_pays.barre(recettes, langue, lambda r: v(r, "pays"))
    sommaire, fiches = [], []
    for r in recettes:
        sommaire.append(f'          <a class="tuile" href="recette-{r["id"]}.html" data-pays="{pays_tuile[r["id"]]}"><img src="{racine}{r["photo"]}" alt="" loading="lazy">'
                        f'<em class="tuile-nombre">{html.escape(v(r, "pays"))}</em><strong>{html.escape(v(r, "titre"))}</strong>'
                        f'<span>{html.escape(v(r, "temps"))}</span></a>')
        ingredients = "\n".join(
            f'              <li><span>{html.escape(texte_ing(i))}</span>'
            f'<a href="boutique.html?q={quote_plus(i["cherche"])}" title="{lib["trouver"]}">{lib["trouver"]} →</a></li>'
            for i in r["ingredients"])
        etapes = "\n".join(f"              <li>{html.escape(e)}</li>" for e in etapes_de(r))
        fiches.append(f'''    <section id="{r["id"]}" class="section recette recette-seule">
      <div class="conteneur recette-grille">
        <a class="retour" href="recettes.html" data-retour>← {lib["retour"]}</a>
        <div class="recette-tete">
          <figure class="recette-photo"><img src="{racine}{r["photo"]}" alt="" loading="lazy"></figure>
          <div>
            <p class="surtitre">{html.escape(v(r, "pays"))}</p>
            <h1>{html.escape(v(r, "titre"))}</h1>
            <p class="intro">{html.escape(v(r, "resume"))}</p>
            <ul class="pastilles"><li>{lib["temps"]}{lib.get("deux_points", " : ")}{html.escape(v(r, "temps"))}</li><li>{lib["pour"]}{lib.get("deux_points", " : ")}{html.escape(v(r, "portions"))}</li></ul>
          </div>
        </div>
        <div class="recette-corps">
          <div>
            <h3>{lib["ing"]}</h3>
            <ul class="ingredients">
{ingredients}
            </ul>
          </div>
          <div>
            <h3>{lib["prep"]}</h3>
            <ol class="etapes-recette">
{etapes}
            </ol>
          </div>
        </div>
      </div>
    </section>
''')
    pages = {}
    for rang, (r, fiche) in enumerate(zip(recettes, fiches)):   # une page par recette, 4 autres recettes en bas
        suivantes = [sommaire[(rang + k) % len(recettes)] for k in range(1, 5)]
        pages[r["id"]] = (fiche + f'''    <section class="section autres-recettes">
      <div class="conteneur">
        <h2>{lib["autres"]}</h2>
        <div class="tuiles">
{chr(10).join(suivantes)}
        </div>
        <p class="centre"><a class="retour retour-bas" href="recettes.html" data-retour>← {lib["retour"]}</a></p>
      </div>
    </section>
''', v(r, "titre"), v(r, "resume"), r["photo"])
    source = source.replace('<div class="tuiles">\n<!--SOMMAIRE-->',
                            '<div class="recettes-mise">\n' + filtre + '\n        <div class="tuiles tuiles-recettes">\n<!--SOMMAIRE-->')
    source = source.replace("<!--SOMMAIRE-->\n        </div>", "<!--SOMMAIRE-->\n        </div>\n        </div>", 1)   # ferme .recettes-mise
    return source.replace("<!--SOMMAIRE-->", "\n".join(sommaire)).replace("<!--RECETTES-->", ""), pages


def construire(fichier: str, langue: str, impose: tuple | None = None) -> int:
    """Écrit une page ; rend le nombre de pages écrites (la page Recettes écrit aussi une page par recette)."""
    t = L[langue]
    n = 1
    if impose:                                          # page d'une recette : (contenu, titre, description, photo)
        contenu, titre_r, description, photo = impose
        titre = f"{titre_r} – {t['pages']['recettes.html'][0]}"
    else:
        titre, description = t["pages"][fichier]
        photo = "images/logo.png"
        dossier = SOURCES if langue == "fr" else SOURCES / langue
        contenu = (dossier / f"{SOURCE.get(fichier, fichier[:-5])}.html").read_text(encoding="utf-8")
    if fichier == "rayons.html":
        contenu = page_rayons(contenu, langue)
    elif fichier == "recettes.html":
        contenu, pages = page_recettes(contenu, langue)
        for rid, (corps, titre_r, resume, photo_r) in pages.items():
            n += construire(f"recette-{rid}.html", langue, (corps, titre_r, resume, photo_r))
    if "<!--FORMULAIRE-->" in contenu:
        sujet = "candidature" if fichier == "carriere.html" else "produit"
        contenu = contenu.replace("<!--FORMULAIRE-->", formulaire(langue, t["dossier"] + fichier, sujet))
    racine = racine_de(langue)
    if langue != "fr":                                  # images et fichiers communs à la racine du site
        contenu = contenu.replace('src="images/', 'src="../images/')
    css = f'  <link rel="stylesheet" href="{racine}boutique.css">\n' if fichier in AVEC_BOUTIQUE else ""
    script = f'  <script src="{racine}boutique.js"></script>\n' if fichier in AVEC_BOUTIQUE else ""
    script += (f'  <script src="{racine}langue.js"></script>\n  <script src="{racine}site.js"></script>\n'
               f'  <script src="{racine}assistant.js"></script>\n')
    if fichier in ("contact.html", "carriere.html"):
        script += f'  <script src="{racine}formulaire.js"></script>\n'
    fiche = ""
    if fichier in ("index.html", "contact.html"):
        fiche = '  <script type="application/ld+json">\n  ' + json.dumps(FICHE_COMMERCE, ensure_ascii=False) + "\n  </script>\n"
    actif = {"produit.html": "boutique.html"}.get(fichier, "recettes.html" if fichier.startswith("recette-") else fichier)
    alternatives = "".join(f'  <link rel="alternate" hreflang="{L[c]["lang"]}" href="{URL}/{L[c]["dossier"]}{fichier}">\n'
                           for c in LANGUES)
    page = f'''<!doctype html>
<html lang="{t["lang"]}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(titre)}</title>
  <meta name="description" content="{html.escape(description)}">
  <meta name="theme-color" content="#0f5f25">
  <link rel="icon" href="{racine}favicon.ico">
  <link rel="apple-touch-icon" href="{racine}images/icone.png">
{alternatives}  <meta property="og:title" content="{html.escape(titre)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:image" content="{URL}/{photo}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,700;1,9..144,700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{racine}style.css">
{css}{fiche}</head>
<body>
{bandeau(t)}
{entete(t, actif, fichier, langue)}
{contenu.rstrip()}

{pied(t, langue)}{barre_mobile(t)}{script}</body>
</html>
'''
    sortie = SITE / t["dossier"] / fichier
    sortie.parent.mkdir(exist_ok=True)
    sortie.write_text(page, encoding="utf-8")
    return n


def main() -> None:
    n = 0
    for langue in LANGUES:
        for fichier in FICHIERS:
            if (SOURCES if langue == "fr" else SOURCES / langue).joinpath(f"{SOURCE.get(fichier, fichier[:-5])}.html").exists():
                n += construire(fichier, langue)
            else:
                print(f"{langue} : sources manquantes pour {fichier}")
    print(f"{n} pages construites.")


if __name__ == "__main__":
    main()
