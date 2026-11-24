# ADR 000 : [titre de la décision]

Date : 24/11/2026 · Auteurs : Adam TAFRHY

## Contexte

L'image Docker `maintai:0.4.0` doit pouvoir être construite rapidement et partagée sur n'importe quel serveur sans exposer la clé API ni obliger à rebâtir l'image à chaque réentraînement du modèle. Il faut donc décider quels fichiers entrent dans l'image au moment du `docker build` et lesquels sont injectés dynamiquement au lancement du conteneur.

## Options étudiées

1. **Tout embarquer dans l'image (code, modèle `models/`, données `data/` et configuration `.env`)** :
   - _Avantages_ : le conteneur est totalement autonome et se lance d'une seule commande sans volumes externes ni fichier d'environnement.
   - _Inconvénients_ : la clé API (`.env`) est figée dans les couches de l'image et compromise en cas de partage ; chaque réentraînement du modèle ou mise à jour des données impose de reconstruire et redéployer une image volumineuse ; les artefacts de développement (`mlflow.db`, `mlruns/`, `.dvc/`, `.venv/`, `tests/`) alourdissent inutilement le build.
2. **Embarquer uniquement l'OS, Python 3.11-slim, les dépendances figées et le code (`maintai/`, `ui/`), en excluant le reste via `.dockerignore`** :
   - _Avantages_ : aucun secret n'est stocké dans l'image ; le modèle (`models/`) et les données (`data/`) sont montés en lecture seule (`:ro`) au lancement et peuvent être mis à jour sans rebuilder l'image (cycle MLOps) ; l'exclusion des outils de dev (`mlflow`, `dvc`, `pytest`, `.venv/`, `.git/`) réduit la taille de l'image (~1,16 Go) et accélère les builds grâce au cache Docker.
   - _Inconvénients_ : le lancement d'un conteneur exige de monter explicitement les volumes (`-v`) et de passer le fichier `--env-file .env` (ou d'orchestrer le tout avec Docker Compose) ; sans volume `models/`, l'API démarre mais renvoie une erreur `503` sur `/v1/predict`.

## Décision

Retenir l'**option 2** : l'image Docker ne contient que le runtime Python, les bibliothèques de production (`requirements-docker.txt`) et le code source (`maintai/`, `ui/`), tandis que `.dockerignore` exclut `models/`, `data/`, `.env`, `.venv/`, `mlflow.db`, `mlruns/`, `.dvc/`, `tests/` et `.git/`. Ce choix répond à la fois aux contraintes de sécurité (zéro secret dans l'image) et de MLOps (découplage entre le cycle de vie du code et celui du modèle entraîné).

## Conséquences

- **Ce que cela facilite** : le déploiement sécurisé et reproductible sur tout serveur, la mise à jour à chaud des modèles via un simple redémarrage de conteneur, et des reconstructions quasi instantanées (~1,4 s) lors de modifications du code grâce au cache de couches.
- **Ce que cela rend plus difficile** : un `docker run` brut sans options `-v` ni `--env-file` ne suffit plus pour que l'API soit opérationnelle ; l'usage de `compose.yaml` devient indispensable pour fiabiliser le lancement.
- **Ce qu'il faudra surveiller** : la présence effective des fichiers attendus dans `./models` et `./data` sur la machine hôte avant le démarrage, la compatibilité stricte de version entre `scikit-learn==1.8.0` dans l'image et l'environnement d'entraînement, ainsi que la non-publication de `.env`, `models/` et `data/*.csv` dans Git.
