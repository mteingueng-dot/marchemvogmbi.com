# marchemvogmbi.com

Site du Marché Mvog-Mbi Sherbrooke, épicerie africaine et caribéenne : page d'accueil et boutique en ligne avec tous les produits de Clover (prix, rayons, photos, caractéristiques). Pas encore de paiement en ligne : les produits s'achètent au magasin.

Site statique (HTML, CSS, un peu de JavaScript) : il se dépose tel quel chez l'hébergeur (WHC, dossier `public_html`), sans base de données.

## Pages

Six pages au menu, assemblées par `outils/construire_site.py` (même bandeau, en-tête et pied de page partout). Le contenu de chaque page est dans `sources/` :

- `index.html` (`sources/accueil.html`) : accueil, promesses (prix imbattables, livraison gratuite), produits vedettes, rayons, plats du monde.
- `boutique.html` : tous les produits, par rayon, avec recherche, tri et filtre « avec photo ».
- `rayons.html` (`sources/rayons.html`) : tous les rayons, fabriqués d'après `data/produits.json`.
- `a-propos.html`, `carriere.html`, `contact.html`.
- `produit.html?id=<ID Clover>` : fiche du produit (photo, prix, caractéristiques, produits du même rayon).

Après une modification d'un fichier de `sources/` ou du catalogue : `python outils/construire_site.py`.

## Mettre le catalogue à jour depuis Clover

Sur le poste ou le serveur où MVOGMBI_Sync est configuré (jeton Clover dans le coffre-fort de Windows) :

```
python outils/exporter_catalogue.py --sync "E:/claude code/MVOGMBI_Sync_2026.1" --garder-articles
python outils/completer_off.py
python outils/photos_illustration.py
python outils/exporter_catalogue.py --depuis data/clover_articles.json
python outils/construire_site.py
```

1. Le 1er appel lit Clover : articles visibles, avec un prix fixe ou au lb, comptés comme recette. Il ne publie jamais le coût, le stock ni le fournisseur.
2. `completer_off.py` cherche chaque code-barres dans Open Food Facts : photo, marque, format, origine, ingrédients. Chaque réponse est gardée dans `data/off_cache.json`, donc seuls les nouveaux codes sont demandés.
3. Le dernier appel réécrit `data/produits.json`. On dépose ensuite le site chez l'hébergeur.

Les photos et données d'Open Food Facts sont sous licence CC BY-SA / ODbL : la mention est dans le pied de page et sous chaque photo.

## Ajouter vos photos et descriptions

- **Photo :** enregistrez-la sous `images/produits/<ID Clover>.jpg`, au format carré, environ 480 px. Elle remplace celle d'Open Food Facts. L'ID Clover est à la fin de l'adresse de la fiche produit.
- **Description, nom ou caractéristiques :** ajoutez-les dans `data/fiches.json` :

```json
{
  "FGFWRG9VR3RXE": {
    "description": "Huile de palme rouge non raffinée, pour le ndolé, l'okok et les sauces graines.",
    "caracteristiques": { "Origine": "Ghana", "Conservation": "À température ambiante" }
  }
}
```

Relancez ensuite `exporter_catalogue.py`.

## Essayer en local

```
python -m http.server 8811
```

Ouvrez ensuite http://127.0.0.1:8811/. La boutique lit `data/produits.json` : ouverte en double-cliquant sur le fichier, sans ce petit serveur, elle ne peut pas charger les produits.

## Langues, formulaire, photos

- Deux langues : `sources/*.html` (français, racine du site) et `sources/en/*.html` (anglais, dossier `en/`). Le choix FR / EN est dans le menu.
- `contact.php` : formulaire des pages Contact et Carrière, envoyé à contact@marchemvogmbi.com avec la pièce jointe (PDF ou Word, 10 Mo au plus). Il faut un hébergement avec PHP et `mail()` (WHC). Faites un envoi d'essai après la mise en ligne.
- Photos professionnelles : `outils/photos_pro.py` détoure les produits sur fond blanc avec rembg, installé à part (voir l'en-tête du script). Une photo ratée s'écarte en ajoutant son code-barres dans `data/photos_refusees.json`.
- Photos du magasin : `outils/photos_magasin.py "E:/site web"` (photos choisies par nom de fichier).
- Aucun prix n'est publié : règle du propriétaire.

## Assistant et ergonomie

- `assistant.js` : fenêtre de discussion (bouton en bas à droite, « Discuter » dans la barre du téléphone). Elle répond sans aucun service externe : heures (ouvert ou fermé en ce moment, heure de Sherbrooke), adresse, livraison, garantie du meilleur prix, paiement, commande, emploi, contact ; elle cherche aussi les produits dans `data/produits.json` et les recettes dans `data/recettes.json`. Elle ne donne aucun prix. Pour changer une réponse, modifier l'objet `R` du fichier (français et anglais).
- `site.js` : en-tête qui se resserre au défilement, apparition douce des blocs (désactivée si la personne préfère moins d'animations), bouton « haut de page ».
- Téléphone : barre d'actions fixe en bas (Appeler, Itinéraire, Boutique, Discuter).

## Photos des produits trouvées en ligne

`python outils/photos_web.py` cherche une image pour chaque produit d'après son nom exact (marque, sorte, format),
garde celle dont le titre ressemble le plus au produit, de préférence sur fond blanc, et l'enregistre dans
`images/web/<id>.jpg` (carré blanc 700 × 700). Les choix sont dans `data/photos_web.json`, avec la page d'origine
affichée comme source sur la fiche. Une photo mauvaise : ajouter l'ID du produit dans `data/photos_web_refusees.json`,
puis `python outils/photos_web.py --refaire <ID>` et relancer l'export. Les photos prises au magasin restent prioritaires.
