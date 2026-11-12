# Recettes écrites, en attente d'une photo

`lot1_fr_en.py` à `lot4_fr_en.py` : 65 recettes (français, anglais), traduites dans `lot*_es/pt/it/de.py`.
57 sont sur le site (2026-11-12). Les 8 qui attendent une photo : legim, matapa, sauce-djansang, tassot-cabri,
salade-fonio, gboma-dessi, ngai-ngai, mayi-moulen. `lot4_fr_en.py` : `TEMPS_EN` = temps en anglais quand il ne se
recopie pas tel quel.

Pour en ajouter une : mettre sa photo dans `images/recettes/<id>.jpg`, puis l'ajouter à `data/recettes.json` et aux
`outils/recettes_<langue>.py` comme le fait `ajouter.py` (écrit pour des photos choisies sur planche), et lancer
`python outils/recettes_langues.py` puis `python outils/construire_site.py`.
