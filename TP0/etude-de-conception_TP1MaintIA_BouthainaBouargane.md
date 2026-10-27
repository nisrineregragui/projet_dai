# Étude de conception — MaintAI

Groupe : Bouthaina Bouargane 
· Date : 20/10/2026

## 1. Contexte et utilisateurs
- Utilisateur principal (un rôle précis) : le responsable de l'équipe de maintenance d'une usine, qui choisit les machines à inspecter.

## 2. Problème et décision
- Décision que l'utilisateur prend avec le système : quelles machines inspecter aujourd'hui, en fonction du risque de panne prédit pour chacune.
- Fréquence : chaque matin.
- Coût d'une erreur, et pour qui :
  - **Panne manquée** (le modèle dit « pas de panne » et la machine tombe en panne) : une ligne de production arrêtée pendant une journée. Coût supporté par l'usine (production perdue).
  - **Fausse alerte** (le modèle annonce une panne qui n'arrive pas) : une heure d'inspection inutile. Coût supporté par l'équipe de maintenance.

## 3. Approche par sous-problème
| Sous-problème | Approche (règles / ML / DL / LLM / RAG) | Pourquoi pas une approche plus simple |
|---|---|---|
| Prédire si une machine va tomber en panne (oui ou non) | **ML classique : classification** (régression logistique retenue, comparée à un arbre et à une forêt aléatoire) | La méthode la plus simple (ne jamais prédire de panne) a une accuracy de 0,824 mais détecte 0 panne. Le modèle combine 4 mesures de capteurs et détecte environ 85 % des pannes. Des règles à seuils fixes sur chaque capteur n'ont pas été testées dans ce projet. |

Pourquoi pas plus complexe (deep learning, LLM) : il n'y a que 5 000 lignes de 4 colonnes numériques, et un modèle linéaire atteint déjà le critère d'acceptation.

## 4. Données
| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---|---|
| `data/exemple_pannes.csv` | Relevés de capteurs synthétiques fournis par le cours (Lab 2.1, usage pédagogique ; pas de licence particulière indiquée) | 5 000 relevés, 5 colonnes, 17,56 % de pannes | Non : ce sont des mesures de machines, aucune personne n'est identifiée |

Colonnes : `temperature_c`, `vibration_mm_s`, `load_pct`, `runtime_hours`, et la cible `failure` (1 = panne, 0 = pas de panne). Aucune valeur manquante dans le fichier.

## 5. Métriques, baseline et critères d'acceptation
- **Baseline et son score :** toujours prédire « pas de panne » (`DummyClassifier`, classe la plus fréquente) : accuracy **0,824**, rappel **0**, précision 0, F1 0 sur le jeu de test.
- **Métrique principale, et pourquoi :** le **rappel**, car une panne manquée arrête une ligne pendant une journée : c'est l'erreur la plus coûteuse, il faut donc détecter le plus de pannes possible. La **précision** sert de garde-fou, pour limiter les fausses alertes (une heure d'inspection chacune). L'accuracy est écartée : une baseline qui ne détecte rien a déjà 0,824.
- **Critères d'acceptation :** rappel ≥ 0,75 **et** précision ≥ 0,50 sur le jeu de test (1 000 relevés, soit 20 % tenus à l'écart, découpage aléatoire stratifié, graine 42).
- **Résultat :** le modèle retenu (régression logistique) obtient un rappel de **0,847** et une précision de **0,527** : le critère est **atteint**. L'arbre (rappel 0,722) et la forêt aléatoire (rappel 0,540) ne l'atteignent pas.

## 6. Architecture prévue
Un pipeline en ligne de commande, sans interface :

1. `data/exemple_pannes.csv` est lu par `monprojet/data.py` (pandas).
2. `split()` tire 80 % des relevés pour l'entraînement (4 000) et 20 % pour le test (1 000), de façon stratifiée et reproductible (graine 42).
3. Pour chaque modèle de `monprojet/models.py`, un `Pipeline` scikit-learn applique le pré-traitement (médiane pour les trous, mise à l'échelle des nombres), puis le modèle.
4. `monprojet/train.py` note chaque modèle sur le jeu de test (accuracy, rappel, précision, F1), les classe selon le rappel et garde le meilleur.
5. Sorties dans `models/` : `model.joblib` (le meilleur modèle) et `metrics.json` (les scores de tous les modèles).
6. Tous les réglages (fichier, cible, type de problème, métrique, découpage, graine) sont dans `monprojet/config.py`.

## 7. Choix technologiques
- **Python 3.12** avec **uv** pour l'environnement et les dépendances (`uv run`), ce qui rend le projet reproductible.
- **pandas** (lecture du CSV), **scikit-learn** (modèles, pré-traitement, métriques), **joblib** (sauvegarde du modèle), **json** (sauvegarde des scores).
- **pytest** : 8 tests ; le projet est fini quand ils passent tous.
- Graine fixe (`SEED = 42`) : les résultats sont identiques à chaque lancement.
- `class_weight="balanced"` pour la régression logistique, l'arbre et la forêt : cela donne plus de poids aux pannes, qui sont la classe rare.

## 8. Risques, éthique, confidentialité
- **Panne manquée** : le risque principal. Même avec un rappel de 0,847, environ 15 % des pannes ne sont pas détectées. Le système doit aider à choisir quoi inspecter, pas remplacer les contrôles de sécurité habituels.
- **Fatigue due aux fausses alertes** : avec une précision de 0,527, environ une alerte sur deux est fausse. Si l'équipe finit par ne plus y croire, le système devient inutile.
- **Données synthétiques** : les scores sont probablement meilleurs que sur de vraies mesures d'usine.
- **Dérive dans le temps** : l'usure des machines, un changement de capteur ou de production peuvent dégrader le modèle ; il faudrait le réévaluer régulièrement.
- **Confidentialité** : risque faible, les données ne concernent que des machines. Avec de vraies données, il faudrait vérifier qu'aucun identifiant de personne (opérateur, par exemple) ne s'y trouve.

## 9. Limites et hors périmètre
- **Limites** : environ 176 pannes dans le jeu de test, donc un rappel connu à quelques points près ; le meilleur modèle est choisi d'après son score sur ce même jeu de test, donc ce score est un peu optimiste ; seuil de décision et hyperparamètres non réglés ; les coûts (une journée d'arrêt, une heure d'inspection) ne sont pas chiffrés en argent.
- **Hors périmètre de ce TP** : interface pour l'équipe de maintenance, mise en production, branchement sur de vrais capteurs, et prédiction du type ou de la date de la panne (on prédit seulement « panne ou non »).