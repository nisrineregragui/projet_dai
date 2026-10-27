# TP0 : MaintAI

**Nom :** Assiya MARZAK · **Groupe :** G2

## Le problème

Prédire une panne à partir de 4 capteurs ; une panne manquée arrête une ligne.

## Résultats sur le jeu de test

| Modèle | Accuracy | Rappel | Précision |
|—|—|—|—|
| baseline | 0.824 | 0.000 | 0.000 |
| régression logistique | 0.889 | 0.574 | 0.737 |
| arbre de décision | 0.839 | 0.597 | 0.538 |
| forêt aléatoire | 0.873 | 0.545 | 0.671 |

## Mon choix, et pourquoi

je choisis l'arbre de decision, car il a le meilleur rappel avec 0.597. dans ce projet, le plus important est de detecter le plus de pannes possible car une panne non detectee peut arreter une ligne de production.

## Le critère (rappel >= 0,75) est-il atteint ?

non, le meilleur rappel est 0.597. le modele fait quand meme beaucoup mieux que la baseline qui ne detecte aucune panne, mais il n'atteint pas encore le rappel de 0.75 demande.

## Ce qui reste flou

on ne sait pas si les donnees representent tous les cas reels. il faudrait plus de donnees et tester le modele sur une autre periode. il faudrait aussi voir pourquoi certaines pannes ne sont pas detectees.

# TP0 : CantineAI

**Nom :** Adam TAFRHY · **Groupe :** G2

## Le problème

predire le nombre de repas servis a la cantine. une prediction trop basse peut creer un manque de repas et une prediction trop haute peut creer du gaspillage.

## Résultats sur le jeu de test

| Modèle | MAE | RMSE | R2 |
|—|—|—|—|
| baseline | 70.271 | 88.416 | -0.151 |
| regression lineaire | 22.239 | 28.170 | 0.883 |
| arbre de decision | 46.000 | 59.710 | 0.475 |
| foret aleatoire | 31.845 | 41.540 | 0.746 |

## Mon choix, et pourquoi

je choisis la regression lineaire, car elle a la plus petite mae avec 22.239. cela veut dire qu'elle se trompe en moyenne d'environ 22 repas, ce qui est le meilleur resultat des modeles testes.

## Le critère (rappel >= 0,75) est-il atteint ?

ce critere parle du rappel, donc il est adapte a la classification des pannes et pas a la regression de la cantine. pour la cantine, le critere utilise est une mae inferieure ou egale a 30 repas. il est atteint avec une mae de 22.239.

## Ce qui reste flou

les resultats ne portent que sur 68 jours de test. le nombre de repas peut changer avec des evenements inhabituels, un nouveau menu ou une nouvelle organisation. il faudrait tester le modele sur plus de jours et avec de nouvelles annees.
