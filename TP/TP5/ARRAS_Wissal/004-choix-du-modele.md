ADR 004 : Choix du modèle et du seuil d'alerte de MaintAI

Date : 17/11/2026 · Auteurs : ARRAS Wissal

Contexte

MaintAI doit signaler une panne avant qu'elle n'arrive, et une panne manquée (faux négatif) coûte beaucoup plus cher qu'une fausse alerte (une inspection inutile) : le critère principal est donc le recall, avec une precision qui reste acceptable. Les classes sont déséquilibrées (la baseline « jamais de panne » obtient 0.864 d'accuracy avec un recall nul), donc l'accuracy seule ne permet pas de choisir.

Options étudiées

Toutes entraînées sur les mêmes données (v1 : 5000 lignes, data_md5 = 73e0b7cb3c6f795c70c3ddf970b99c15, test de 1000 lignes) et suivies dans MLflow (expérience maintai) :

Option	recall	precision	accuracy	Run ID
A. Régression logistique, C = 1.0, seuil 0.3	0.750	0.622	0.904	b18f8bab…
B. Régression logistique, C = 0.01, seuil 0.3	0.691	0.653	0.908	fb933292…
C. Régression logistique, C = 1.0, seuil 0.2	0.838	0.543	0.882	ba091eac…
D. Forêt aléatoire, seuil 0.3	0.728	0.562	0.886	ade14e7e…
A (défaut) : bon équilibre et meilleure precision des modèles simples, mais rate une panne sur quatre.
B (plus de régularisation) : precision légèrement meilleure, mais le recall le plus bas : contraire à la contrainte.
C (seuil abaissé à 0.2) : meilleur recall (environ 84 % des pannes détectées) ; inconvénient : plus de fausses alertes.
D (forêt aléatoire) : plus lourde et moins interprétable, et moins bonne que A en recall comme en precision au même seuil.
Décision

On retient l'option C : régression logistique, C = 1.0, seuil d'alerte 0.2, parce qu'elle maximise le recall et que la contrainte du projet est de ne pas manquer de pannes. Le modèle reste simple, rapide et interprétable.

Run MLflow : ba091eac7a6a4d2880e1830ae23202ce
Données : data_md5 = 73e0b7cb3c6f795c70c3ddf970b99c15 (version v1, commit Git 6d73365)
Environnement : scikit-learn==1.8.0 (requirements.txt du modèle dans MLflow)
Conséquences
Ce que ça facilite : environ 84 % des pannes détectées au lieu de 75 %. Le choix est traçable de bout en bout. Le Run ID donne les paramètres, les métriques, le modèle et ses versions exactes. Le data_md5 donne la version des données : git checkout 6d73365 -- data/sensors.csv.dvc puis dvc checkout les restaurent.
Ce qu'on accepte en échange : une precision de 0.543, donc un peu moins d'une alerte sur deux est fausse, et une accuracy qui passe de 0.904 à 0.882. L'équipe de maintenance fera plus d'inspections inutiles.
Ce qu'il faudra surveiller :
la fatigue d'alerte, si les fausses alertes deviennent trop nombreuses ;
le seuil, à affiner avec une courbe precision-recall ;
la dérive des données : ré-entraîner sur une nouvelle version DVC, et ne comparer les runs que sur un même jeu de test (le run sur la v2 n'est pas directement comparable).