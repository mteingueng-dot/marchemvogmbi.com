# Recettes écrites, en attente d'une photo

`lot1_fr_en.py`, `lot2_fr_en.py`, `lot3_fr_en.py` : 45 recettes (français, anglais), traduites dans `lot*_es/pt/it/de.py`.
29 sont déjà sur le site. Les 16 qui attendent une photo : nnam-owondo, placali-kope, red-red, legim, colombo-poulet,
kwacoco-bible, sauce-feuille-patate, matapa, chakchouka, diri-ak-pwa, festival, sauce-djansang, attieke-aubergine,
tassot-cabri, pain-patate, run-down.

Pour en ajouter une : mettre sa photo dans `images/recettes/<id>.jpg`, puis l'ajouter à `data/recettes.json` et aux
`outils/recettes_<langue>.py` comme le fait `ajouter.py` (écrit pour des photos choisies sur planche), et lancer
`python outils/recettes_langues.py` puis `python outils/construire_site.py`.
