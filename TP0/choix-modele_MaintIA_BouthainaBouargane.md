# Choix du modèle

Date : 20/10/2026 · Groupe : Bouthaina Bouargane

## Contexte
MaintAI aide l'équipe de maintenance d'une usine à choisir, chaque matin, les machines à inspecter, en prédisant à partir de relevés de capteurs si une machine va tomber en panne. C'est une classification binaire : panne (1) ou pas de panne (0). Une panne manquée arrête une ligne de production pendant une journée ; une fausse alerte coûte une heure d'inspection.

La métrique principale est le **rappel** (la part des vraies pannes détectées), car une panne manquée est l'erreur la plus coûteuse. La **précision** (la part des alertes qui sont de vraies pannes) sert de garde-fou, pour ne pas noyer l'équipe sous les fausses alertes. L'accuracy n'est pas retenue : avec 17,6 % de pannes, un modèle qui ne prédit jamais de panne a déjà 82,4 % d'accuracy tout en ratant toutes les pannes.

## Données et découpage
- Fichier : `data/exemple_pannes.csv`, **5 000 relevés** de capteurs synthétiques, dont 17,56 % se terminent par une panne.
- Colonnes utilisées (4) : `temperature_c`, `vibration_mm_s`, `load_pct`, `runtime_hours`. La cible est `failure` (0 ou 1).
- Découpage **aléatoire et stratifié** (la proportion de pannes est la même en entraînement et en test), graine 42 : 4 000 relevés pour l'entraînement, **1 000 relevés pour le test** (20 %, tenus à l'écart). Les relevés ne sont pas une série temporelle, donc un tirage au hasard est correct ici.

## Résultats sur le jeu de test

| Modèle | Métrique principale (rappel) | Autres métriques |
|---|---|---|
| Baseline (toujours « pas de panne ») | 0,000 | accuracy 0,824 · précision 0,000 · F1 0,000 |
| Arbre de décision (profondeur 5, classes équilibrées) | 0,722 | accuracy 0,825 · précision 0,502 · F1 0,592 |
| Forêt aléatoire (200 arbres, classes équilibrées) | 0,540 | accuracy 0,882 · précision 0,720 · F1 0,617 |
| **Régression logistique (classes équilibrées)** | **0,847** | **accuracy 0,839 · précision 0,527 · F1 0,649** |

Ordre de grandeur pour le jeu de test (1 000 relevés, soit environ 176 pannes et 824 relevés normaux), reconstitué à partir des scores de la régression logistique : environ 149 pannes détectées sur 176, environ 27 pannes manquées et environ 134 fausses alertes. La baseline, elle, rate les 176 pannes.

## Décision
**Modèle retenu : régression logistique.** Raison principale : c'est le modèle qui détecte le plus de pannes (rappel 0,847), alors que la métrique principale est le rappel.

- **Bat-il la baseline ?** Oui. La baseline a un rappel de 0 (aucune panne détectée) ; la régression logistique en détecte environ 85 %. Son accuracy (0,839) n'est qu'un peu au-dessus de celle de la baseline (0,824) : c'est la preuve que l'accuracy ne mesure pas ce qui compte ici.
- **Critère d'acceptation (section 5 de l'étude) : atteint.** Le critère est rappel ≥ 0,75 et précision ≥ 0,50 sur le jeu de test. La régression logistique obtient 0,847 et 0,527. L'arbre obtient un rappel de 0,722 (sous 0,75) et la forêt de 0,540 : ni l'un ni l'autre n'atteint le critère.
- **Pourquoi pas la forêt, qui a la meilleure accuracy (0,882) et la meilleure précision (0,720) ?** Parce qu'elle rate presque la moitié des pannes (rappel 0,540). Elle est plus prudente : elle déclenche moins d'alertes, mais elle en laisse passer beaucoup, ce qui est l'erreur la plus coûteuse.
- **Compromis à connaître :** avec une précision de 0,527, environ une alerte sur deux est une fausse alerte. C'est le prix d'un rappel élevé : chaque fausse alerte coûte une heure d'inspection, contre une journée d'arrêt de ligne pour une panne manquée.

## Limites
- **Taille du jeu de test** : environ 176 pannes seulement. Le rappel de 0,847 est donc une estimation à quelques points près (de l'ordre de ± 5 points) ; un autre tirage donnerait un autre chiffre.
- **Le test a servi à choisir** : le modèle est retenu d'après son rappel sur le jeu de test. Avec 4 modèles l'effet est faible, mais le score est un peu optimiste ; un jeu de validation séparé serait plus propre.
- **Données synthétiques** : relevés générés pour le cours, probablement plus réguliers que de vraies mesures d'usine. Les résultats ne se transposent pas tels quels à une vraie usine.
- **Seuil de décision non réglé** : le modèle décide « panne » à partir du seuil par défaut. Un seuil plus bas détecterait plus de pannes mais ferait plus de fausses alertes ; ce compromis n'a pas été exploré.
- **Coûts non chiffrés** : on sait qu'une panne manquée coûte une journée d'arrêt et une fausse alerte une heure, mais pas leur coût en argent, donc le meilleur seuil n'est pas calculé.
- **Hyperparamètres non réglés** : l'arbre et la forêt ont été utilisés avec leurs réglages de départ.
- **Données manquantes** : aucune valeur manquante dans `exemple_pannes.csv` (vérifié sur les 5 000 relevés). Avec de vrais capteurs (capteur en panne, relevé perdu), il y en aurait, et ce cas n'a pas été testé.
- **Cas mal couverts** : les 27 pannes manquées ressemblent à des machines normales (vibration médiane 2,7 mm/s, contre 2,2 pour les relevés normaux et 5,8 pour les pannes détectées). Une panne qui ne se voit pas dans les vibrations est donc mal détectée.