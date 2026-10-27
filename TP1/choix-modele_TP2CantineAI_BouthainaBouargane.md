# Choix du modèle

Date : 26/10/2026 · Groupe : Bouthaina Bouargane

## Contexte
CantineAI aide le gestionnaire d'une cantine de lycée (environ 650 élèves inscrits) à décider, chaque jour à 10 h, combien de repas commander à la cuisine pour le lendemain. Un repas en trop est jeté (environ 15 DH de matière première perdus), un repas manquant laisse un élève sans déjeuner. C'est une régression sur une série temporelle : prédire `repas_servis`, un nombre.

La métrique principale est la **MAE**, l'erreur moyenne en nombre de repas par jour. Elle se lit directement par le gestionnaire (« je me trompe de X repas par jour ») et se relie au coût d'une erreur : un repas en trop coûte 15 DH. Elle est à minimiser (plus petit = meilleur).

## Données et découpage
- Fichier : `data/cantine_repas.csv`, 340 jours d'école de septembre 2024 à juin 2026, une ligne par jour, données synthétiques générées pour le cours.
- Colonnes utilisées (9) : `jour`, `inscrits`, `menu`, `temperature_c`, `pluie_mm`, `examens`, `sortie_scolaire`, `veille_vacances`, `repas_semaine_precedente`. La cible est `repas_servis` ; la colonne `date` sert uniquement à ranger les jours dans l'ordre.
- Données manquantes : `repas_semaine_precedente` est vide pour 60 jours (première semaine, retours de vacances). Ces jours sont gardés ; le trou est comblé par la médiane dans le pré-traitement.
- Découpage **chronologique** : entraînement = les 272 premiers jours, test = les **68 derniers jours** (20 %, du 25/02/2026 au 19/06/2026). On entraîne sur le passé et on teste sur le futur, car un tirage au hasard mélangerait des jours voisins des deux côtés et donnerait un score trop beau. Graine fixe : 42 (elle sert aux modèles qui ont du hasard, comme la forêt ; le découpage chronologique, lui, ne dépend pas du hasard).

## Résultats sur le jeu de test

| Modèle | Métrique principale (MAE, en repas) | Autres métriques |
|---|---|---|
| Baseline du code (toujours la moyenne) | 70,271 | RMSE 88,416 · R² -0,151 |
| Référence métier (même jour, semaine précédente) | 75,977 | RMSE 95,592 · R² -0,346 |
| Arbre de décision (profondeur 5) | 42,010 | RMSE 54,766 · R² 0,558 |
| Forêt aléatoire (200 arbres) | 31,825 | RMSE 41,647 · R² 0,745 |
| **Ridge (régression linéaire régularisée)** | **22,623** | **RMSE 28,545 · R² 0,880** |

La référence métier est la méthode actuelle du gestionnaire. Elle est mesurée à part (`monprojet/reference_gestionnaire.py`) sur exactement les mêmes 68 jours ; pour les 10 jours de test où le chiffre de la semaine d'avant est vide, on a pris la moyenne de l'entraînement.

## Décision
**Modèle retenu : Ridge.** Raison principale : c'est celui qui a la plus petite MAE sur le jeu de test (22,6 repas par jour), devant la forêt aléatoire (31,8) et l'arbre (42,0).

- **Bat-il la baseline ?** Oui, nettement. Par rapport à la baseline du code (MAE 70,3), il gagne 47,6 repas par jour, soit environ 68 % d'erreur en moins. Par rapport à la méthode actuelle du gestionnaire (MAE 76,0), il gagne 53,4 repas par jour, soit environ 70 % d'erreur en moins.
- **Critère d'acceptation (section 5 de l'étude) : atteint.** Le critère demandait une MAE au moins 30 % sous celle de la méthode actuelle sur les 68 derniers jours, soit une MAE ≤ 53 repas. Le ridge obtient 22,6.
- **Pourquoi pas la forêt aléatoire, pourtant plus complexe ?** Avec seulement 272 jours d'entraînement, un modèle plus flexible a moins de données pour apprendre, et ici l'effet du menu, du jour et des examens semble s'additionner, ce qui convient bien à un modèle linéaire. C'est une explication probable, pas une preuve : on ne l'a pas testée davantage.
- **En argent :** 22,6 repas × 15 DH donne au plus environ 340 DH de matière par jour si toutes les erreurs étaient des excès, contre environ 1 140 DH pour la méthode actuelle. C'est un majorant grossier : les erreurs vont dans les deux sens.

## Limites
- **Petit jeu de test** : 68 jours seulement, un seul découpage. Avec un autre découpage, les chiffres changeraient. Il faudrait plusieurs découpages dans le temps pour être sûr.
- **Le test a servi à choisir** : le meilleur modèle est choisi d'après son score sur le jeu de test. Avec 4 modèles l'effet est faible, mais le score du ridge est légèrement optimiste ; un jeu de validation séparé serait plus propre.
- **Données synthétiques** : générées pour le cours, donc probablement plus régulières que de vraies données de cantine. Les résultats ne se transposent pas tels quels à un vrai lycée.
- **La MAE traite pareil un repas en trop et un repas manquant**, alors que leurs coûts sont différents (15 DH contre un élève sans déjeuner, dont on ne connaît pas le coût exact).
- **Données manquantes** : après les vacances, le chiffre de la semaine précédente est vide et remplacé par la médiane. Sur les 10 jours de test concernés, l'erreur n'est pas plus grande (MAE 16,2 contre 23,7 les autres jours), mais 10 jours sont trop peu pour conclure.
- **Cas mal couverts** : le test contient peu de jours particuliers (10 jours d'examens, 4 sorties, 2 veilles de vacances) et ne couvre pas de rentrée de septembre, où les inscrits changent beaucoup (de 638 à 680 en 2025). La plus grosse erreur est de 71 repas (vendredi 01/05/2026, couscous : 695 servis, 624 prévus).
- **Le modèle sous-estime plus souvent** : 45 jours sur 68, en moyenne 8,6 repas de moins que la réalité. C'est l'erreur la plus gênante (des élèves sans repas) ; ajouter une petite marge à la prévision serait à étudier.
- **Hyperparamètres non réglés** : l'arbre et la forêt ont été utilisés avec leurs réglages de départ ; ils auraient peut-être progressé avec un réglage.