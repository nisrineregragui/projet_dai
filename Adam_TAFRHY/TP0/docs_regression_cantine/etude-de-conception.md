# Étude de conception — Prévision des repas de la cantine

Groupe : Adam TAFRHY · Version : finale · Date : 26/10/2026

## 1. Contexte et utilisateur

- utilisateur principal : le responsable de la cantine.
- le but est de prevoir le nombre de repas qui seront servis chaque jour pour mieux preparer les quantites.

## 2. Problème et décision

- la decision est de choisir combien de repas preparer pour la journee.
- la prediction peut etre faite avant chaque jour de service, des que le menu et les informations du jour sont connus.
- si la prediction est trop basse, des eleves risquent de ne pas avoir de repas. si elle est trop haute, il y a du gaspillage alimentaire et des couts inutiles.

## 3. Approche choisie

| Sous-problème                     | Approche   | Pourquoi pas une règle simple                                                                      |
| --------------------------------- | ---------- | -------------------------------------------------------------------------------------------------- |
| estimer le nombre de repas servis | regression | une simple moyenne ne tient pas compte du jour, du menu, de la meteo, des examens ou des vacances. |

## 4. Données

| Jeu de données    | Source et licence | Volume     | Données personnelles ? |
| ----------------- | ----------------- | ---------- | ---------------------- |
| cantine_repas.csv | jeu fourni        | 340 lignes | non                    |

les donnees contiennent notamment la date, le jour, le nombre d'inscrits, le menu, la temperature, la pluie, les examens, les sorties scolaires, la veille des vacances et le nombre de repas de la semaine precedente. la cible est repas_servis.

## 5. Métriques, baseline et critère

- baseline : dummyregressor(strategy="mean"), avec une mae de 70,271 repas sur le jeu de test.
- metrique principale : la mae, car elle donne directement le nombre moyen de repas d'erreur et elle est facile a comprendre pour la cantine.
- critere d'acceptation : obtenir une mae inferieure ou egale a 30 repas sur les 20 % de jours les plus recents. la regression lineaire obtient 22,239, donc le critere est atteint.

## 6. Architecture prévue

1. charger le fichier csv et retirer les lignes sans cible.
2. trier les jours par date puis utiliser les 80 % premiers pour entrainer et les 20 % derniers pour tester.
3. remplacer les valeurs manquantes, mettre les nombres a l'echelle et encoder les variables comme le jour ou le menu.
4. comparer une baseline, une regression lineaire, un arbre de decision et une foret aleatoire.
5. sauvegarder le meilleur pipeline dans models/model.joblib et les resultats dans models/metrics.json.

## 7. Choix techniques

- python et pandas pour lire et preparer les donnees.
- scikit-learn pour le pretraitement, les modeles et les metriques.
- joblib pour garder le modele choisi.
- pytest pour verifier le code.

## 8. Risques et limites éthiques

- le modele est une aide pour la preparation, il ne remplace pas le jugement du responsable.
- une erreur peut amener soit du gaspillage, soit un manque de repas pour les eleves.
- il n'y a pas de donnees personnelles dans le fichier.

## 9. Hors périmètre

- les resultats viennent d'un seul jeu de donnees et doivent etre verifies avec de nouvelles annees.
- le projet ne gere pas les commandes, les stocks, les allergies ou le cout des ingredients.
- il ne predit pas les situations exceptionnelles qui ne sont pas representees dans les donnees.
