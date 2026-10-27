# Choix du modèle

Date : 26/10/2026 · Groupe : Adam TAFRHY

## Contexte

le projet sert a predire le nombre de repas qui seront servis a la cantine. il aide le responsable a preparer une quantite plus proche du besoin reel.

la metrique principale est la mae. elle indique de combien de repas, en moyenne, le modele se trompe.

## Données et découpage

les donnees viennent de cantine_repas.csv. le fichier contient 340 jours et la cible est repas_servis. les colonnes utilisees sont le jour, les inscrits, le menu, la temperature, la pluie, les examens, les sorties scolaires, la veille des vacances et les repas de la semaine precedente.

la date n'est pas utilisee comme variable d'entree. les donnees sont triees par date : les 272 premiers jours servent a l'entrainement et les 68 derniers jours servent au test. ce choix permet de tester le modele sur des jours futurs.

## Résultats sur le jeu de test

| Modèle              |    MAE | Autres résultats          |
| ------------------- | -----: | ------------------------- |
| baseline            | 70,271 | rmse : 88,416 r2 : -0,151 |
| regression lineaire | 22,239 | rmse : 28,170 r2 : 0,883  |
| arbre de decision   | 46,000 | rmse : 59,710 r2 : 0,475  |
| foret aleatoire     | 31,845 | rmse : 41,540 r2 : 0,746  |

## Décision

le modele retenu est la regression lineaire. il a la plus petite mae : il se trompe en moyenne de 22,239 repas par jour.

il fait mieux que la baseline de 48,032 repas en mae. le critere fixe, une mae inferieure ou egale a 30 repas, est atteint.

## Limites

le test ne porte que sur 68 jours. les resultats peuvent changer avec une nouvelle annee, un changement de menu ou des evenements non prevus. il manque aussi 60 valeurs pour la colonne des repas de la semaine precedente : le pipeline les remplace, mais cette information reste moins fiable sur ces jours.
