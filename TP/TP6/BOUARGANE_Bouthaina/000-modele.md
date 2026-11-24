# ADR 005 : Conteneurisation de MaintAI avec Docker et Docker Compose

- **Statut :** Accepté
- **Date :** 24/11/2026
- **Auteurs :** Bouthaina Bouargane (Groupe G2)

## Contexte

MaintAI doit être packagé dans une image Docker (`maintai:0.4.0`) et orchestré avec Docker Compose (`compose.yaml`) pour l'API FastAPI et l'interface Streamlit, tout en respectant la reproductibilité des dépendances, la maîtrise de la taille de l'image et la sécurité des secrets et modèles.

## Décision

- Inclure dans l'image (`Dockerfile`, base `python:3.11-slim`) uniquement le code applicatif (`maintai/`, `ui/`) et les dépendances de production figées (`requirements-docker.txt`), en omettant `mlflow`, `dvc` et `pytest`.
- Exclure du contexte de build via `.dockerignore` les environnements locaux, modèles, données, secrets et bases locales (`.venv/`, `models/`, `data/`, `.env`, `mlflow.db`).
- Fournir les artefacts et variables au lancement : `./models:/app/models:ro` et `./data:/app/data:ro` en volumes lecture seule, et la configuration / clé API via `--env-file .env` / `env_file`.
- Orchestrer `api` et `ui` via `compose.yaml` sur le réseau Docker Compose, avec `MAINTAI_API_URL: http://api:8000` injectée au service `ui` (et `os.getenv("MAINTAI_API_URL", "http://localhost:8000")` dans `ui/app.py`).

## Conséquences

- **Positives :** image plus légère et reproductible, aucun secret ni artefact lourd ou local intégré à l'image, possibilité de mettre à jour le modèle ou les données sans reconstruire l'image.
- **Négatives :** l'absence du volume `models/` au lancement démarre l'API sans modèle chargé (`/health` renvoie `"model_loaded":false` et `/v1/predict` renvoie `503` une fois la clé API fournie) ; la communication entre services doit passer par le nom de service (`api`) et non `localhost`.