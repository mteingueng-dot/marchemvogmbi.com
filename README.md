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
