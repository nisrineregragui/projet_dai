# ADR 004 : Choix du modèle de prédiction des pannes

Date : 17/11/2026 · Auteurs : Regragui Nisrine

## Contexte

Dans MaintAI, une panne non détectée coûte plus cher qu'une fausse alerte.
Nous devons donc choisir un modèle qui privilégie le recall pour détecter le maximum de pannes.

## Options étudiées

1. **Régression logistique (seuil = 0.3)**
   - Avantage : bonne précision (0.622).
   - Inconvénient : recall de 0.750, donc davantage de pannes manquées.

2. **Régression logistique (seuil = 0.2)**
   - Avantage : meilleur recall (0.838), donc davantage de pannes détectées.
   - Inconvénient : précision plus faible (0.543), donc plus de fausses alertes.

3. **Random Forest (seuil = 0.3)**
   - Avantage : peut modéliser des relations complexes.
   - Inconvénient : recall inférieur (0.728).

## Décision

Nous retenons la **régression logistique avec un seuil de 0.2**,
car elle possède le meilleur recall (0.838).

Ce choix permet de réduire les pannes non détectées, ce qui est
la priorité du projet MaintAI.

- **Run MLflow :** `f0248028999045d5bb9b351e724dd15c`
- **data_md5 :** `73e0b7cb3c6f795c70c3ddf970b99c15`
- **Version des données :** v1 (5000 lignes)

## Conséquences

Cette décision permet de détecter davantage de pannes.

En revanche, elle génère plus de fausses alertes à cause de la précision
plus faible. Il faudra donc surveiller le recall, la précision et
le nombre de fausses alertes, puis ajuster le seuil si nécessaire.