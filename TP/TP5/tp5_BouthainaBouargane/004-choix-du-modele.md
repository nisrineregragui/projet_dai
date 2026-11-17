# ADR 004 : Choix du modèle et du seuil de MaintAI

Date : 17/11/2026 · Auteurs : Bouthaina Bouargane

## Contexte
MaintAI doit prédire les pannes à partir des relevés de capteurs. Une panne manquée coûte plus cher qu'une fausse alerte : la métrique principale est donc le recall.

## Options étudiées
Toutes les options ont été entraînées sur la v1 des données (`data_md5` = `73e0b7cb3c6f795c70c3ddf970b99c15`) et comparées dans MLflow :
1. Régression logistique, seuil 0.3 (défaut) : avantages : bon équilibre (recall 0.75, precision 0.622) ; inconvénients : une panne sur quatre est manquée.
2. Régression logistique, C = 0.01 : avantages : moins de fausses alertes (precision 0.653) ; inconvénients : le recall le plus faible (0.691).
3. Régression logistique, seuil 0.2 : avantages : le meilleur recall (0.838), avec un modèle simple ; inconvénients : plus de fausses alertes (precision 0.543).
4. Forêt aléatoire, seuil 0.3 : avantages : aucun par rapport à l'option 1 ; inconvénients : recall (0.728) et precision (0.562) plus faibles que l'option 1 au même seuil, et modèle plus lourd.
5. Forêt aléatoire, seuil 0.2 : avantages : recall élevé (0.831) ; inconvénients : precision plus faible que l'option 3 (0.479 contre 0.543), accuracy (0.854) sous la baseline (0.864), et modèle plus lourd.

## Décision
Nous retenons la régression logistique (C = 1.0) avec le seuil 0.2 : c'est l'option qui détecte le plus de pannes (recall 0.838), ce qui répond à la contrainte principale du projet.

- Run MLflow : `26c9249a4f684945b61f8c986d6da1ea`
- Données : v1, `data_md5` = `73e0b7cb3c6f795c70c3ddf970b99c15` (commit Git `0e2c1ae`, « Données v1 »)

## Conséquences
Cette décision facilite la détection des pannes : environ 84 % sont repérées, contre 75 % avec le seuil par défaut. Elle rend le travail de maintenance plus lourd, car il y a plus de fausses alertes : avec une precision de 0.543, près d'une alerte sur deux est fausse. Le modèle se retrouve par l'identifiant de son run, avec les versions exactes de ses bibliothèques, et ses données avec `git checkout 0e2c1ae -- data/sensors.csv.dvc`, puis `dvc checkout`. À surveiller : ce choix a été fait sur la v1. Si on passe à la v2, il faudra refaire la comparaison sur un même jeu de test avant de garder le seuil 0.2.