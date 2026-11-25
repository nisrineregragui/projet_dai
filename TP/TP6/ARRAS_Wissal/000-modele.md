# ADR 005 – Choix de l'architecture Docker pour MaintAI

## Statut

Accepté.

## Contexte

Nous souhaitons faciliter le déploiement de l'application MaintAI et garantir un environnement d'exécution reproductible sur différentes machines.

Pour cela, il est nécessaire de séparer le code source, les dépendances, le modèle entraîné, les données et les secrets afin de simplifier la maintenance et d'améliorer la sécurité de l'application.

## Décision

Nous avons choisi de construire une image Docker basée sur Python 3.11 contenant :

- Les dépendances définies dans `requirements-docker.txt`.
- Le code de l'API FastAPI.
- Le code de l'interface utilisateur Streamlit.

Le modèle entraîné n'est pas intégré dans l'image Docker. Il est monté au lancement du conteneur avec un volume en lecture seule :

`./models:/app/models:ro`

Les données sont également montées avec un volume en lecture seule :

`./data:/app/data:ro`

La clé API est transmise au lancement à travers le fichier `.env`, grâce à la directive `env_file` de Docker Compose.

Le fichier `.dockerignore` permet d'exclure les fichiers inutiles ou sensibles du contexte de construction, notamment :

- `.env`
- `.venv/`
- `models/`
- `data/`
- `mlruns/`
- `mlflow.db`
- `.dvc/`

Enfin, nous utilisons Docker Compose pour orchestrer les deux services `api` et `ui`, qui utilisent la même image Docker `maintai:0.4.0`, avec des configurations et des commandes différentes.

## Alternatives envisagées

### 1. Intégrer le modèle dans l'image Docker

Cette solution consiste à copier directement le modèle entraîné dans l'image pendant sa construction.

**Avantages :**
- Le modèle est directement disponible dans le conteneur.
- Le déploiement est autonome.

**Inconvénients :**
- Augmentation de la taille de l'image.
- Obligation de reconstruire l'image à chaque modification du modèle.
- Moins de flexibilité dans la gestion des versions du modèle.

### 2. Monter le modèle avec un volume Docker

Cette solution consiste à conserver le modèle à l'extérieur de l'image et à le monter au lancement du conteneur.

**Avantages :**
- Possibilité de remplacer le modèle sans reconstruire l'image.
- Réduction de la taille de l'image.
- Séparation entre le code et les artefacts du modèle.

**Inconvénients :**
- Le modèle doit être disponible sur la machine de déploiement.
- Une mauvaise configuration du volume peut empêcher le chargement du modèle.

**Choix retenu :** Nous avons choisi la deuxième solution, car elle offre davantage de flexibilité et facilite la maintenance de l'application.

## Conséquences

### Avantages

- Environnement d'exécution reproductible grâce à Docker.
- Séparation du code, des dépendances, du modèle et des données.
- Réduction de la taille de l'image Docker.
- Possibilité de mettre à jour le modèle sans reconstruire l'image.
- Meilleure protection des secrets grâce à leur transmission au lancement.
- Optimisation du temps de construction grâce au cache Docker.
- Déploiement simplifié et orchestration des services grâce à Docker Compose.

### Inconvénients

- Le modèle et les données doivent être disponibles sur la machine de déploiement.
- Docker doit être installé et correctement configuré.
- Une mauvaise configuration des volumes ou des variables d'environnement peut empêcher le fonctionnement de l'application.
- La gestion des secrets nécessite une attention particulière afin d'éviter leur exposition.

## Conclusion

Cette architecture permet de conteneuriser MaintAI tout en séparant les éléments nécessaires à son exécution. Elle garantit un déploiement plus reproductible, flexible et maintenable, tout en facilitant la gestion du modèle, des données et des informations sensibles.