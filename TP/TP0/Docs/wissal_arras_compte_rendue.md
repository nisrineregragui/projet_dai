# TP0 : MaintAI

**Nom :** ARRAS Wissal · **Groupe :** G2

## Le problème

Prédire une panne à partir de 4 capteurs ; une panne manquée arrête une ligne.

## Résultats sur le jeu de test

| Modèle | Accuracy | Rappel | Précision |
|---|---:|---:|---:|
| baseline | 0.824 | 0.000 | 0.000 |
| régression logistique | 0.889 | 0.574 | 0.737 |
| arbre de décision | 0.839 | 0.597 | 0.538 |
| forêt aléatoire | 0.873 | 0.545 | 0.671 |

## Mon choix, et pourquoi

Je choisis l'arbre de décision, car il a le meilleur rappel avec 0.597. Dans ce projet, le plus important est de détecter le plus de pannes possible, car une panne non détectée peut arrêter une ligne de production.

## Le critère (rappel >= 0,75) est-il atteint ?

Non, le meilleur rappel est 0.597. Le modèle fait quand même beaucoup mieux que la baseline, qui ne détecte aucune panne, mais il n'atteint pas encore le rappel de 0.75 demandé.

## Ce qui reste flou

On ne sait pas si les données représentent tous les cas réels. Il faudrait plus de données et tester le modèle sur une autre période. Il faudrait aussi voir pourquoi certaines pannes ne sont pas détectées.

---

# TP0 : CantineAI

**Nom :** ARRAS Wissal · **Groupe :** G2

## Le problème

Prédire le nombre de repas servis à la cantine. Une prédiction trop basse peut créer un manque de repas, et une prédiction trop haute peut créer du gaspillage.

## Résultats sur le jeu de test

| Modèle | MAE | RMSE | R² |
|---|---:|---:|---:|
| baseline | 70.271 | 88.416 | -0.151 |
| régression linéaire | 22.239 | 28.170 | 0.883 |
| arbre de décision | 46.000 | 59.710 | 0.475 |
| forêt aléatoire | 31.845 | 41.540 | 0.746 |

## Mon choix, et pourquoi

Je choisis la régression linéaire, car elle a la plus petite MAE avec 22.239. Cela veut dire qu'elle se trompe en moyenne d'environ 22 repas, ce qui est le meilleur résultat des modèles testés.

## Le critère (rappel >= 0,75) est-il atteint ?

Ce critère parle du rappel, donc il est adapté à la classification des pannes et pas à la régression de la cantine. Pour la cantine, le critère utilisé est une MAE inférieure ou égale à 30 repas. Il est atteint, avec une MAE de 22.239.

## Ce qui reste flou

Les résultats ne portent que sur 68 jours de test. Le nombre de repas peut changer avec des événements inhabituels, un nouveau menu ou une nouvelle organisation. Il faudrait tester le modèle sur plus de jours et avec de nouvelles années. 