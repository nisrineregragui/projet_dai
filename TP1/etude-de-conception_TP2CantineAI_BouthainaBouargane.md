# Étude de conception — CantineAI

Groupe : Bouthaina Bouargane 
· Date : 26/10/2026

## 1. Contexte et utilisateurs
- Utilisateur principal (un rôle précis) : le gestionnaire de la cantine d'un lycée, qui sert le déjeuner du lundi au vendredi à environ 650 élèves inscrits.

## 2. Problème et décision
- Décision que l'utilisateur prend avec le système : combien de repas commander à la cuisine pour le lendemain.
- Fréquence : chaque jour d'école à 10 h, soit 5 fois par semaine.
- Coût d'une erreur, et pour qui :
  - **Repas en trop** : environ 15 DH de matière première jetés par repas, et du gaspillage alimentaire. Coût supporté par le lycée.
  - **Repas manquant** : un élève sans déjeuner, ou un sandwich de remplacement acheté en urgence, et des plaintes des parents. Coût supporté par les élèves, les parents et le gestionnaire.

## 3. Approche par sous-problème
| Sous-problème | Approche (règles / ML / DL / LLM / RAG) | Pourquoi pas une approche plus simple |
|---|---|---|
| Prévoir le nombre de repas servis le lendemain (un nombre) | **ML classique : régression** (Ridge retenu, comparé à un arbre et à une forêt aléatoire) | Les deux méthodes simples testées sont mauvaises : prédire toujours la moyenne donne une MAE de 70,3 repas, et recopier le chiffre de la semaine précédente (pratique actuelle) donne 76,0. Le menu, le jour, la météo et le calendrier se combinent, ce que des règles fixes couvrent mal. Le ridge descend à 22,6. |

Pourquoi pas plus complexe (deep learning, LLM) : il n'y a que 340 lignes de données tabulaires, ce qui est trop peu pour un réseau de neurones, et un modèle linéaire suffit déjà.

## 4. Données
| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---|---|
| `data/cantine_repas.csv` | Données synthétiques générées pour le cours (usage pédagogique ; pas de licence particulière indiquée) | 340 jours d'école (sept. 2024 → juin 2026), 11 colonnes, une ligne par jour | Non : ce sont des totaux journaliers, aucun élève n'est identifié |

Colonnes : `date`, `jour`, `inscrits`, `menu`, `temperature_c`, `pluie_mm`, `examens`, `sortie_scolaire`, `veille_vacances`, `repas_semaine_precedente`, et la cible `repas_servis`. Particularité : `repas_semaine_precedente` est vide pour 60 jours (première semaine, retours de vacances).

## 5. Métriques, baseline et critères d'acceptation
- **Baseline et son score :**
  - Méthode actuelle du gestionnaire (même jour, semaine précédente) : MAE **75,977** sur le jeu de test (les 10 jours sans valeur de la semaine précédente sont remplis par la moyenne de l'entraînement).
  - Baseline du code (`DummyRegressor`, toujours la moyenne), exigée par les tests : MAE **70,271**.
- **Métrique principale, et pourquoi :** la MAE, en repas par jour. Elle se lit directement par le gestionnaire et se relie au coût : chaque repas en trop coûte 15 DH. Elle est complétée par la RMSE (qui punit davantage les grosses erreurs) et le R².
- **Critères d'acceptation :** MAE au moins 30 % sous celle de la méthode actuelle du gestionnaire (75,977), soit une MAE ≤ 53 repas, mesurée sur le jeu de test (les 68 jours d'école les plus récents, du 25/02/2026 au 19/06/2026), avec un découpage chronologique.
- **Résultat :** le modèle retenu (Ridge) obtient une MAE de **22,623**, soit environ 70 % sous la méthode actuelle : le critère est **atteint** (vérifié par un test automatique, `test_critere_d_acceptation_30_pourcent_sous_le_gestionnaire`).

## 6. Architecture prévue
Un pipeline en ligne de commande, sans interface :

1. `data/cantine_repas.csv` est lu par `monprojet/data.py` (pandas).
2. `split()` range les jours par date : les 272 premiers servent à l'entraînement, les 68 derniers au test.
3. Pour chaque modèle de `monprojet/models.py`, un `Pipeline` scikit-learn applique d'abord le pré-traitement (médiane pour les trous, mise à l'échelle des nombres, encodage 0/1 de `jour` et `menu`), puis le modèle.
4. `monprojet/train.py` note chaque modèle sur le jeu de test (MAE, RMSE, R²), les classe et garde le meilleur.
5. Sorties dans `models/` : `model.joblib` (le meilleur modèle) et `metrics.json` (les scores de tous les modèles).
6. Tous les réglages (fichier, cible, métrique, découpage, graine) sont dans `monprojet/config.py` : aucun chemin ni nom de colonne n'est écrit en dur ailleurs.

## 7. Choix technologiques
- **Python 3.12** avec **uv** pour l'environnement et les dépendances (`uv sync`, `uv run`), ce qui rend le projet reproductible sur une autre machine.
- **pandas** (lecture du CSV, découpage), **scikit-learn** (modèles, pré-traitement, métriques), **joblib** (sauvegarde du modèle), **json** (sauvegarde des scores).
- **pytest** : 12 tests (8 du cours et 4 propres à CantineAI) ; le projet est fini quand ils passent tous.
- Graine fixe (`SEED = 42`) : les résultats sont identiques à chaque lancement.

## 8. Risques, éthique, confidentialité
- **Confidentialité** : risque faible, car les données ne contiennent aucune information sur des élèves, seulement des totaux par jour. Avec de vraies données, il faudrait vérifier qu'aucune donnée personnelle n'est ajoutée.
- **Fuite d'information** : un tirage au hasard du jeu de test ferait « voir le futur » au modèle. On l'évite avec un découpage chronologique.
- **Données synthétiques** : les scores sont probablement meilleurs que ce que l'on obtiendrait sur de vraies données de cantine.
- **Erreurs coûteuses** : un modèle qui sous-estime laisse des élèves sans repas. Le gestionnaire doit pouvoir garder une marge de sécurité et ne pas suivre aveuglément la prédiction.
- **Changements dans le temps** : un nouveau menu, un changement de règlement ou une période inhabituelle peuvent dégrader les prévisions ; il faudrait réévaluer le modèle régulièrement.
- **Données manquantes** : après les vacances, le chiffre de la semaine précédente est absent et remplacé par la médiane. Sur les 10 jours de test concernés, l'erreur n'est pas plus grande (MAE 16,2 contre 23,7), mais c'est trop peu de jours pour conclure ; il faudra le surveiller.

## 9. Limites et hors périmètre
- **Limites** : jeu de test de 68 jours et un seul découpage ; le meilleur modèle est choisi d'après son score sur ce même jeu de test, donc le score est un peu optimiste ; hyperparamètres non réglés ; la MAE traite pareil un repas en trop et un repas manquant.
- **Hors périmètre de ce TP** : interface pour le gestionnaire, mise en production, récupération automatique du menu et de la météo prévue, et prise en compte séparée du coût d'un repas manquant (inconnu).