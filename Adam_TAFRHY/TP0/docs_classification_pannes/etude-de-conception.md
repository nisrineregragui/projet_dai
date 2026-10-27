# Étude de conception — Prédiction de pannes d'équipements

Groupe : TAFRHY Adam · Version : finale · Date : 26/10/2026

## 1. Contexte et utilisateurs

- utilisateur principal : responsable de maintenance industrielle.

## 2. Problème et décision

- decision que l'utilisateur prend avec le systeme : savoir les equipements a inspecter avant une panne.
- frequence : a chaque nouvelle mesure disponible.
- cout d'une erreur, et pour qui : un faux negatif peut provoquer une panne non anticipee, un arret de production et une erreur grave pour l'equipe et l'entreprise. un faux positif declenche une inspection inutile, moins couteuse mais qui prend du temps.

## 3. Approche par sous-problème

| Sous-problème                                                | Approche                               | Pourquoi pas une approche plus simple                                                                                                              |
| ------------------------------------------------------------ | -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| estimer le risque de panne a partir des mesures des capteurs | ml supervise de classification binaire | une regle a seuil fixe sur une seule mesure ne voit pas les liens entre la temperature, les vibrations, la charge et les heures de fonctionnement. |

## 4. Données

| Jeu de données | Source et licence | Volume | Données personnelles ? | exemple_pannes.csv | source et licence non documentees | 5 000 lignes | non |

## 5. Métriques, baseline et critères d'acceptation

- baseline et son score : dummyclassifier(strategy="most_frequent") ; recall = 0,000 sur le jeu de test.
- metrique principale, et pourquoi : recall de la classe `failure`.
- criteres d'acceptation : recall superieur ou egal a 0,55 et precision superieure ou egale a 0,50 sur un jeu de test stratifie, distinct des donnees d'entrainement. l'arbre de decision atteint un recall de 0,597 et une precision de 0,538.

## 6. Architecture prévue

1. charger les donnees csv et retirer les lignes dont la cible est manquante.
2. repartir les donnees entre un jeu d'entrainement de 80 % et un jeu de test de 20 %, de facon stratifiee.
3. preparer les variables numeriques avec une imputation par la mediane puis une mise a l'echelle.
4. entrainer et comparer une baseline, une regression logistique, un arbre de decision et une foret aleatoire.
5. sauvegarder le meilleur pipeline dans `models/model.joblib` et les metriques dans `models/metrics.json`.

## 7. Choix technologiques

- python 3 et pandas pour le chargement et la preparation des donnees.
- scikit-learn pour les pipelines, les modeles et les metriques.
- joblib pour sauvegarder le pipeline choisi.
- pytest pour verifier le comportement du code.

## 8. Risques, éthique, confidentialité

- une prediction est une aide a la decision : elle ne doit pas remplacer une inspection de securite.
- les faux negatifs peuvent mettre en danger la disponibilite des equipements et le personnel. les faux positifs peuvent augmenter la charge de maintenance.

## 9. Limites et hors périmètre

- les donnees sont un jeu d'exemple et ne font pas office de validation en conditions reelles.
- le projet predit un risque de panne, sans expliquer la cause technique ni la date exacte de la panne.
- la maintenance planifiee, la collecte des capteurs en temps reel et une interface utilisateur sont hors perimetre.
