# Choix du modèle

Date : 26/10/2026 · Groupe : TAFRHY Adam

## Contexte

le systeme predit le risque de panne d'un equipement a partir de la temperature, des vibrations, de la charge et des heures de fonctionnement. il aide l'equipe de maintenance a savoir quels equipements verifier.

la metrique principale est le recall de la classe failure : manquer une panne possible peut causer un arret non prevu et augmenter les couts de maintenance.

## Données et découpage

les donnees viennent de exemple_pannes.csv. elles contiennent 5 000 lignes et les colonnes temperature_c, vibration_mm_s, load_pct, runtime_hours et failure.

la cible est failure. le jeu est decoupe au hasard, de maniere stratifiee, avec 80 % des donnees pour l'entrainement et 20 % pour le test, soit 1 000 lignes. la graine est 42 pour pouvoir retrouver les memes resultats.

## Résultats sur le jeu de test

| Modèle                | Métrique principale | Autres métriques                              |
| --------------------- | ------------------- | --------------------------------------------- |
| baseline              | recall : 0,000      | accuracy : 0,824 precision : 0,000 f1 : 0,000 |
| regression logistique | recall : 0,574      | accuracy : 0,889 precision : 0,737 f1 : 0,645 |
| arbre de decision     | recall : 0,597      | accuracy : 0,839 precision : 0,538 f1 : 0,566 |
| foret aleatoire       | recall : 0,545      | accuracy : 0,873 precision : 0,671 f1 : 0,602 |

## Décision

le modele retenu est l'arbre de decision, car il a le meilleur recall avec 0,597. il detecte donc environ 60 % des pannes du jeu de test.

il fait mieux que la baseline de 0,597, car la baseline ne detecte aucune panne. le critere fixe dans l'etude de conception, recall superieur ou egal a 0,55 et precision superieure ou egale a 0,50, est atteint.

## Limites

les resultats portent sur un seul jeu de test de 1 000 lignes et doivent etre verifies avec de nouvelles donnees. l'arbre de decision produit aussi des faux positifs : sa precision est de 0,538. enfin, les donnees d'exemple ne couvrent pas forcement toutes les conditions reelles de fonctionnement ni l'evolution des equipements dans le temps.
