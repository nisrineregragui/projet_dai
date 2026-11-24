# ADR 005 — Image Docker

## Statut

Accepté.

## Contexte

Nous souhaitons faciliter le déploiement de MaintAI et garantir un environnement d'exécution reproductible sur différentes machines.

Il faut séparer le code, les dépendances, le modèle, les données et les secrets.

## Décision

Nous avons choisi de construire une image Docker contenant :

- Python 3.11.
- Les dépendances définies dans `requirements-docker.txt`.
- Le code de l'API FastAPI.
- Le code de l'interface Streamlit.

Le modèle n'est pas intégré dans l'image. Il est monté au lancement avec un volume en lecture seule (`./models:/app/models:ro`).

Les données sont également montées avec un volume en lecture seule (`./data:/app/data:ro`).

La clé API est transmise au lancement grâce au fichier `.env`.

Le fichier `.dockerignore` permet d'exclure les fichiers inutiles ou sensibles, notamment :

- `.env`
- `.venv/`
- `models/`
- `data/`
- `mlruns/`
- `mlflow.db`
- `.dvc/`

Nous utilisons Docker Compose pour lancer les deux services `api` et `ui` à partir de la même image.

## Alternatives envisagées

### Intégrer le modèle dans l'image

Cette solution facilite le déploiement, mais augmente la taille de l'image et oblige à la reconstruire à chaque changement du modèle.

### Monter le modèle avec un volume

Cette solution permet de remplacer le modèle sans reconstruire l'image. Cependant, le modèle doit être disponible sur la machine de déploiement.

Nous avons retenu cette deuxième solution.

## Conséquences

### Avantages

- Un environnement d'exécution reproductible.
- Une image plus légère.
- La possibilité de changer le modèle sans reconstruire l'image.
- Une meilleure protection des secrets.
- Une construction plus rapide grâce au cache Docker.
- Un déploiement simplifié avec Docker Compose.

### Inconvénients

- Le modèle et les données doivent être disponibles au lancement.
- Docker doit être installé sur la machine.
- Une mauvaise configuration des volumes ou des variables d'environnement peut empêcher le bon fonctionnement de l'application.