# TP0 : MaintAI

**Nom :** Assiya MARZAK · **Groupe :** G2

## Le problème

Prédire si une machine va tomber en panne à partir de 4 capteurs (température, vibration, charge, heures de fonctionnement). Une panne manquée arrête une ligne de production pendant une journée ; une fausse alerte coûte seulement une heure d'inspection.

## Résultats sur le jeu de test

Jeu de test : 1 000 relevés (20 %), découpage aléatoire stratifié, graine 42.

| Modèle | accuracy | recall | precision | f1 |
|---|---|---|---|---|
| regression_logistique | 0.839 | 0.847 | 0.527 | 0.649 |
| arbre | 0.825 | 0.722 | 0.502 | 0.592 |
| foret_aleatoire | 0.882 | 0.540 | 0.720 | 0.617 |
| baseline | 0.824 | 0.000 | 0.000 | 0.000 |

Meilleur modèle selon recall : regression_logistique

## Mon choix, et pourquoi

Je retiens la régression logistique, car elle a le meilleur rappel : 0.847. Elle détecte 149 pannes sur 176 dans le jeu de test, alors que la baseline n'en détecte aucune.

La forêt aléatoire a la meilleure accuracy (0.882), mais elle rate presque une panne sur deux. Ici, rater une panne coûte beaucoup plus cher qu'une fausse alerte, donc je me base sur le rappel et non sur l'accuracy.

Mes scores sont plus élevés en rappel que ceux de la S3 (0.574) parce que j'ai ajouté `class_weight="balanced"` aux modèles : les pannes, plus rares, comptent davantage pendant l'entraînement.

## Le critère (rappel >= 0,75) est-il atteint ?

Oui. La régression logistique obtient un rappel de 0.847, au-dessus de 0,75, et une précision de 0.527, au-dessus du garde-fou de 0,50. L'arbre (0.722) et la forêt (0.540) n'atteignent pas le critère.

## Ce qui reste flou

- Le prix d'un rappel élevé : environ une alerte sur deux est fausse (134 fausses alertes). Je ne sais pas si l'équipe de maintenance l'accepterait au quotidien.
- Le seuil de décision n'a pas été réglé : un autre seuil changerait l'équilibre entre rappel et précision.
- Les 27 pannes manquées ressemblent à des machines normales (vibration faible). Je ne sais pas encore comment les détecter.
- Les données sont synthétiques : les résultats ne sont pas forcément les mêmes dans une vraie usine.

# TP1 : CantineAI

**Nom :** Bouthaina Bouargane · **Groupe :** G2

## Le problème

Prévoir le nombre de repas servis le lendemain à la cantine d'un lycée (environ 650 élèves inscrits). Une prévision trop haute fait jeter des repas (environ 15 DH chacun) ; une prévision trop basse laisse des élèves sans déjeuner.

## Résultats sur le jeu de test

Jeu de test : les 68 derniers jours d'école (du 25/02/2026 au 19/06/2026), découpage chronologique. MAE et RMSE en nombre de repas : plus petit = meilleur.

| Modèle | mae | rmse | r2 |
|---|---|---|---|
| ridge | 22.623 | 28.545 | 0.880 |
| foret_aleatoire | 31.825 | 41.647 | 0.745 |
| arbre | 42.010 | 54.766 | 0.558 |
| baseline | 70.271 | 88.416 | -0.151 |

Meilleur modèle selon mae : ridge

Méthode actuelle du gestionnaire (semaine précédente), calculée à part sur les mêmes 68 jours : mae 75.977 · rmse 95.592 · r2 -0.346.

## Mon choix, et pourquoi

Je retiens le ridge, car il a la plus petite MAE : 22.623. Il se trompe en moyenne d'environ 23 repas par jour, contre 76 pour la méthode actuelle du gestionnaire, soit environ 70 % d'erreur en moins.

Un modèle linéaire suffit ici : les effets du jour, du menu et des examens semblent s'additionner, et il n'y a que 272 jours pour l'entraînement.

## Le critère (MAE au moins 30 % sous la méthode actuelle, soit MAE <= 53) est-il atteint ?

Oui. Le ridge obtient une MAE de 22.623, bien en dessous de 53 repas. La forêt (31.825) et l'arbre (42.010) atteignent aussi ce seuil, mais le ridge reste le meilleur.

## Ce qui reste flou

- Le modèle prévoit trop bas 45 jours sur 68. Je ne sais pas encore quelle marge ajouter pour éviter les repas manquants.
- La MAE compte de la même façon un repas jeté et un élève sans repas, alors que ces deux erreurs n'ont pas le même coût.
- Le test ne couvre que le printemps 2026 : je ne sais pas comment le modèle se comporte à une rentrée de septembre, où le nombre d'inscrits change.
- Les données sont synthétiques : une vraie cantine aurait des jours plus imprévisibles.
