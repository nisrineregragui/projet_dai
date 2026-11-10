# Étude de conception - Détection de pannes et maintenance prédictive multi-modèles (AI4I 2020)

## 1. Contexte et utilisateurs

- **Organisation ou situation :** Site industriel d'usinage de précision exploitant des machines-outils à commande numérique (CNC). Les équipements sont équipés de capteurs télémétriques IoT mesurant en continu la température, la vitesse de rotation, le couple et l'usure de l'outil.
- **Utilisateur principal (un rôle précis) :** Ingénieur ou technicien supérieur de maintenance prédictive industrielle.

## 2. Problème et décision

- **Décision que l'utilisateur prend avec le système :**
  1. Interrompre préventivement la machine pour remplacer l'outil avant la casse mécanique.
  2. Planifier une intervention ciblée selon le mode de défaillance identifié (surchauffe, problème électrique, surcharge).
  3. Ajuster les paramètres d'usinage (réduire le couple ou la vitesse) pour prolonger la durée de vie utile restante ($\text{RUL}$).
- **Fréquence :** Continu / Temps réel (analyse télémétrique cycle par cycle d'usinage).
- **Conséquence d'une erreur, et pour qui :**
  - **Faux négatif (panne non détectée) :** Casse d'outil ou défaillance moteur en plein usinage, entraînant la destruction de la pièce en cours de fabrication, des dégâts matériels sur la broche et un arrêt de production non planifié (coût très élevé pour l'entreprise et risque de sécurité pour les opérateurs).
  - **Faux positif (fausse alerte) :** Arrêt injustifié de la ligne de fabrication et remplacement prématuré d'outils encore fonctionnels (perte de productivité et surcoûts matériels).

## 3. Approche par sous-problème

| Sous-problème                                                                      | Approche (règles / ML / DL / LLM / RAG)          | Pourquoi pas une approche plus simple                                                                                                                                                                       |
| ---------------------------------------------------------------------------------- | ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Détection d'anomalies (Classification binaire : `Machine failure`)**          | ML (ex: Random Forest / XGBoost)                 | Les pannes résultent d'interactions complexes et non linéaires entre plusieurs capteurs (usure, vitesse, couple, température). Des règles de seuils fixes génèrent un taux inacceptable de fausses alertes. |
| **2. Diagnostic du type de panne (Classification multi-classes : `Failure_Type`)** | ML Multi-classes (ex: Random Forest / LightGBM)  | Une règle déterministe ne permet pas d'isoler efficacement les 5 modes de défaillance (`TWF`, `HDF`, `PWF`, `OSF`, `RNF`) lorsqu'ils présentent des signatures thermiques et mécaniques combinées.          |
| **3. Estimation du temps restant avant panne (Régression : `RUL`)**                | ML Régression (ex: Gradient Boosting / CatBoost) | Une règle linéaire simple basée uniquement sur l'horloge ne prend pas en compte les variations d'usure accélérée provoquées par un couple élevé ou des régimes de rotation extrêmes.                        |

## 4. Données

| Jeu de données                               | Source et licence                                                        | Volume                                                                                                                       | Données personnelles ? |
| -------------------------------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| **AI4I 2020 Predictive Maintenance Dataset** | UCI Machine Learning Repository / Kaggle (Licence CC BY 4.0 Open Source) | 10 000 instances / relevés de procédés d'usinage, 14 attributs (températures, vitesse, couple, usure, indicateurs de pannes) | Non                    |

## 5. Métriques, baseline et critères d'acceptation

- **Baseline et ses résultats :**
  - _Modèle 1 (Binaire) :_ Seuil fixe sur l'usure ou le couple ($\text{Tool wear} > 200\text{ min}$ ou $\text{Torque} > 60\text{ Nm}$).
  - _Modèle 2 (Multi-classes) :_ Règles conditionnelles si-alors déterministes.
  - _Modèle 3 (RUL) :_ Estimation linéaire naïve ($\text{RUL} = 240 - \text{Tool wear}$).
- **Métrique principale et pourquoi :**
  - _Modèle 1 :_ **Rappel (Recall)** sur la classe `Machine failure` ($=1$), sous contrainte de Précision. L'objectif absolu est d'éviter les pannes non détectées pour la sécurité et la sauvegarde du matériel.
  - _Modèle 2 :_ **F1-score macro** afin d'accorder le même poids à tous les modes de pannes, y compris les plus rares (`RNF`, `TWF`).
  - _Modèle 3 :_ **MAE (Mean Absolute Error)** mesurée en minutes pour évaluer la précision directe du temps restant.
- **Critères d'acceptation :**
  - _Modèle 1 :_ $\text{Rappel} \ge 90\%$ avec une $\text{Précision} \ge 80\%$.
  - _Modèle 2 :_ $\text{F1-score macro} \ge 0,82$.
  - _Modèle 3 :_ $\text{MAE} \le 8\text{ minutes}$ et $R^2 \ge 0,88$.

## 8. Risques, éthique, confidentialité : répondre aux huit questions ci-dessous

1. **Les données contiennent-elles des données personnelles ? Lesquelles ?**
   Non, uniquement des grandeurs physiques (températures en Kelvin, vitesse de rotation en rpm, couple en Nm, usure en minutes) et des identifiants d'équipement (`UDI`, `Product ID`).

2. **Peut-on s'en passer ou les anonymiser ?**
   Aucune donnée à caractère personnel n'étant enregistrée, l'anonymisation n'est pas requise.

3. **Qui peut être lésé par une erreur ?**
   Les opérateurs de machines en cas de faux négatif (exposition aux risques de casse d'outil ou d'éclats). L'équipe de production en cas de fausses alertes répétées (perte de productivité et baisse de confiance envers le système).

4. **Les données couvrent-elles tous les cas d'usage (lieux, périodes, populations) ?**
   Elles couvrent trois gammes de produits (Low, Medium, High) et une variété de contraintes mécaniques. Elles ne prennent pas en compte les variations extrêmes de températures environnementales extérieures à l'usine.

5. **Quelle erreur coûte le plus, et à qui ?**
   Le faux négatif coûte le plus cher : casse irréversible de la broche, destruction de la pièce usinée et arrêt de chaîne prolongé pour l'entreprise.

6. **Qui valide les décisions, et peut les corriger ?**
   L'ingénieur ou le technicien de maintenance. L'application produit des alertes et prédictions, mais l'interruption physique reste une décision humaine.

7. **Des données sortent-elles de l'organisation (API externe) ?**
   Non. Le traitement s'effectue en local (Edge AI ou serveur interne) pour garantir une latence minimale et protéger la confidentialité des données de production.

8. **Comment le système pourrait-il être détourné ?**
   Un opérateur pourrait faire tourner artificiellement la machine à des régimes extrêmes pour provoquer une fausse alerte et interrompre l'activité.

## 9. Limites et hors périmètre

- **Hors périmètre :**
  - Arrêt automatique d'urgence sans validation humaine.
  - Commande et gestion automatisée des stocks de pièces de rechange.
- **Limites :**
  - Incapacité à anticiper les pannes provoquées par des micro-défauts internes invisibles dans le matériau de la pièce usinée.
  - L'estimation de la RUL est calée sur une usure critique maximale fixée à 240 minutes ; tout changement de modèle d'outil nécessite un ajustement de cette baseline ($\text{RUL} = \text{Seuil} - \text{Tool wear}$).
