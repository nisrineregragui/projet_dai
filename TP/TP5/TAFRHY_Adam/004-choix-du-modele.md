# ADR 000 : [titre de la décision]

Date : [jj/mm/aaaa] · Auteurs : [noms]

## Contexte

Le module de prédiction de MaintAI doit anticiper les pannes des capteurs industriels avant qu'elles ne surviennent. Dans un contexte de maintenance prédictive, une panne manquée (faux négatif) engendre un arrêt de production très coûteux, alors qu'une fausse alerte (faux positif) n'occasionne qu'une vérification préventive ; il faut donc sélectionner un modèle et un seuil de décision qui maximisent le rappel (`recall`).

## Options étudiées

1. **Régression logistique par défaut (`C=1.0`, `threshold=0.3`)** : offre un bon équilibre global (`accuracy = 0,904`, `precision = 0,622`), mais laisse passer 25 % des pannes (`recall = 0,750`).
2. **Régression logistique fortement régularisée (`C=0.01`, `threshold=0.3`)** : obtient la meilleure précision (`0,653`) et la meilleure exactitude (`0,908`), mais dégrade trop la détection des pannes (`recall = 0,691`).
3. **Forêt aléatoire (`--model forest`, aux seuils `0.3` et `0.2`)** : modèle plus complexe et plus lourd, mais systématiquement moins performant que la régression logistique sur nos données (`recall = 0,728` au seuil `0,3` ; `recall = 0,831` et `precision = 0,479` au seuil `0,2`).
4. **Régression logistique avec seuil abaissé (`C=1.0`, `threshold=0.2`)** : permet de détecter 83,8 % des pannes (`recall = 0,838`), au prix d'une augmentation des fausses alertes (`precision = 0,543`, `accuracy = 0,882`).

## Décision

Retenir le modèle de **régression logistique (`C=1.0`) avec un seuil de décision à `0.2`** (`python -m maintai.train --threshold 0.2`).

- **Run MLflow :** `victorious-deer-924` (Run ID : `<run_id_de_victorious-deer-924>`)
- **Version des données (`data_md5`) :** `b7fec4274774842dc1f48202c6013490` (jeu de données v1, 5 000 lignes)

## Conséquences

- **Ce que cette décision facilite :** Réduction forte des pannes non détectées en production, temps d'inférence minimal et traçabilité complète grâce au couplage entre l'identifiant du run MLflow et l'empreinte `data_md5` versionnée par DVC.
- **Ce que cela rend plus difficile :** Augmentation du taux de fausses alertes (`precision = 0.543`, soit environ 46 % d'alertes sans panne réelle), générant davantage de contrôles préventifs pour les équipes de maintenance.
- **Ce qu'il faudra surveiller :** L'acceptabilité du volume de fausses alertes par les opérateurs sur le terrain, ainsi que la réévaluation du modèle sur un jeu de test fixe et identique avant de basculer vers la version v2 des données (`data_md5 = 31ef5ebb63ef2331a31dfe009ef8796a`).
