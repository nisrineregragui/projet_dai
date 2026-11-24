# Compte rendu · TP6 : conteneuriser MaintAI (Docker, Docker Compose)

**Groupe :** G2 ·  **Membres :** Bouthaina Bouargane  ·  **Date :** 24/11/2026 .**Heure :**19:48

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP6.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP6`)

Sortie de `docker run hello-world` (première ligne) et de `docker version` (lignes Client et Server) :

```
Hello from Docker!

Client:
 Version:           29.4.1

Server: Docker Desktop 4.71.0 (225177)
```

Dernière ligne de `python -m pytest` après la mise en place :

```
=================== 5 failed, 33 passed, 4 warnings in 58.08s ====================
```

## 2. Image et conteneur (pendant le premier build)

1. Quelle différence entre une image et un conteneur ?
   
Une image Docker est un modèle contenant le code de l'application et ses dépendances. Un conteneur est une instance de cette image qui s'exécute de manière isolée.

2. Pourquoi `COPY requirements-docker.txt` est-il placé avant `COPY maintai` ?

Pour profiter du cache Docker. Les dépendances sont installées dans une couche séparée et ne sont pas réinstallées lorsque seul le code source change. Cela accélère les reconstructions de l'image.

3. Pourquoi `requirements-docker.txt` contient-il `scikit-learn==1.8.0` et pas `scikit-learn>=1.5` ?

Pour fixer une version précise de scikit-learn et garantir des installations reproductibles. Avec >=1.5, une version différente pourrait être installée selon le moment de la construction.

4. Pourquoi ni `mlflow`, ni `dvc`, ni `pytest` dans l'image ?

Ces outils ne sont pas nécessaires à l'exécution de l'API en production. MLflow et DVC servent au suivi et à la gestion du cycle de vie du modèle, tandis que pytest sert aux tests. Les inclure augmenterait inutilement la taille de l'image.

## 3. Sprint 1 : le Dockerfile

Votre `Dockerfile` :

```dockerfile
# Image de MaintAI
FROM python:3.11-slim

WORKDIR /app

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY maintai ./maintai
COPY ui ./ui

ENV MAINTAI_MODELS_DIR=/app/models
ENV MAINTAI_DATA_PATH=/app/data/sensors.csv

EXPOSE 8000

CMD ["uvicorn", "maintai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

| Build | Durée | Taille de l'image (`docker images`) |
|---|---|---|
| premier build | 107,7 s  | 1,13 GB |
| après une modification de `maintai/predict.py` | 0,8 s | 1,13 GB  |

Deux reconstructions supplémentaires ont été effectuées :

- Deuxième build : 0,8 seconde.
- Troisième build : 0,5 seconde.

La taille de l'image reste de 1,13 GB (DISK USAGE), avec un CONTENT SIZE de 259 MB.

Que signifie `CACHED` dans le journal du second build ?

CACHED signifie que Docker réutilise une couche déjà construite lors d'un précédent build, sans réexécuter l'instruction correspondante. Cela permet de réduire considérablement le temps de reconstruction de l'image.

## 4. Sprint 1 : lancer un conteneur

Votre commande `docker run` :

```
docker run -d --name maintai-api -p 8000:8000 --env-file .env -v "${PWD}/models:/app/models:ro" maintai:0.4.0
```

| Essai | Réponse |
|---|---|
| `GET /health` | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` sans clé | `401 Unauthorized` : `{"detail": "Clé API absente ou invalide"}` |
| `POST /v1/predict` avec la clé | `200 OK` : `{"failure_probability": 0.9553, "alert": true, "threshold": 0.3, "model_version": "2026-11-24T15:55:10Z"}` |

**Piège 1.** Sans l'option `-v ...models...`, que répondent `/health` et `/v1/predict` ? Pourquoi ?

Sans `-v`, `/health` répond `{"status":"ok","model_loaded":false}` : l'API démarre mais ne trouve pas de modèle. `/v1/predict` répond `503` (`{"detail": "Modèle non chargé : lancez python -m maintai.train puis redémarrez l'API"}`). Le dossier `models/` est exclu de l'image par `.dockerignore`, donc le modèle n'existe dans le conteneur que si le volume le fournit au lancement.

**Piège 2.** Avec `--host 127.0.0.1`, que disent `docker logs test` et `http://localhost:8002/health` ? Pourquoi ?

`docker logs test` affiche « Uvicorn running on http://127.0.0.1:8000 ». `curl http://localhost:8002/health` donne « Recv failure: Connection was aborted » et le navigateur donne ERR_CONNECTION_REFUSED. Dans un conteneur, `127.0.0.1` veut dire « ce conteneur seulement ». Le trafic venant du PC arrive par une autre interface du conteneur, que uvicorn n'écoute pas. Il faut écouter partout avec `--host 0.0.0.0`.

## 5. Sprint 2 : Docker Compose

Votre `compose.yaml` :

```yaml
services:
  api:
    build: .
    image: maintai:0.4.0
    env_file: .env
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models:ro

  ui:
    image: maintai:0.4.0
    command:
      - python
      - -m
      - streamlit
      - run
      - ui/app.py
      - --server.address=0.0.0.0
      - --server.port=8501
      - --server.headless=true
    environment:
      MAINTAI_API_URL: http://api:8000
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data:ro
    depends_on:
      - api
```

Sortie de `docker compose ps` :

```
NAME        IMAGE           COMMAND                  SERVICE   CREATED         STATUS         PORTS
tp6-api-1   maintai:0.4.0   "uvicorn maintai.api…"   api       4 seconds ago   Up 3 seconds   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
tp6-ui-1    maintai:0.4.0   "python -m streamlit…"   ui        4 seconds ago   Up 3 seconds   0.0.0.0:8501->8501/tcp, [::]:8501->8501/tcp
```

Quelle URL affiche la barre latérale de l'interface ? D'où vient-elle ?

La barre latérale affiche `http://api:8000` dans Docker Compose (ou `http://localhost:8000` par défaut sans la variable). Elle vient de `os.getenv("MAINTAI_API_URL", "http://localhost:8000")` dans `ui/app.py`, alimentée par `MAINTAI_API_URL: http://api:8000` dans `compose.yaml`.

Résultat des deux commandes `docker compose exec ui ...` (avec `api` puis avec `localhost`). Pourquoi la seconde échoue-t-elle ?

```
# Avec api :
{"status":"ok","model_loaded":true}

# Avec localhost :
httpcore.ConnectError: [Errno 111] Connection refused
```

La seconde échoue parce que dans le conteneur `ui`, `localhost` désigne le conteneur `ui` lui-même (où l'API ne tourne pas), alors que sur le réseau Docker Compose (`tp6_default`), les services communiquent par leur nom de service (`http://api:8000`).

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
======================== 38 passed, 4 warnings in 42.33s =========================
```

## 6. Décision : l'ADR 005

Dans `docs/adr/005-image-docker.md`. Résumez ici votre décision en deux phrases :

Nous avons choisi d'inclure le code et les dépendances Python dans l'image Docker tout en excluant `.venv/`, `data/`, `models/`, `.env` et `mlflow.db` via `.dockerignore`. Le modèle et les données sont fournis au lancement par des volumes (et la clé API via `--env-file .env`), ce qui permet de mettre à jour le modèle sans reconstruire l'image et sans exposer de secrets.

## 7. Questions de compréhension

1. Qu'est-ce qui entre dans l'image, et qu'est-ce qui arrive au lancement ? Donnez le moyen pour chaque élément.

- Dans l'image : le code (`maintai/`, `ui/`) et les bibliothèques (`requirements-docker.txt`) via `COPY` et `RUN` dans le `Dockerfile` (sur la base `python:3.11-slim`).

- Au lancement : le modèle (`models/`) et les données (`data/`) via des volumes (`-v ...:ro` ou `volumes:` dans `compose.yaml`), et les secrets/variables (`.env`) via `--env-file .env` / `env_file`.

2. Pourquoi la clé API n'est-elle jamais dans l'image ?
   
Parce qu'un secret ne doit jamais entrer dans une image qui peut être partagée ou poussée sur un registre ; elle est fournie au lancement via `.env`.

3. Livrer un modèle (TP4, TP5) : qu'est-ce que Docker ajoute à la liste ?
   
Docker emballe le système, Python et les bibliothèques figées dans une image reproductible afin que l'application tourne de la même façon sans préparer manuellement un `.venv` sur le serveur, tout en gardant le modèle séparé via un volume.

## 8. Le rendu Git

- Lien de la pull request : 
- Le tag `tp6` existe sur GitHub : oui 
- `git status` avant le commit : `.env`, `models/` ou `data/*.csv` apparaissaient-ils ? non 

## 9. Ce qui reste flou

Aucun point bloquant ne reste flou : la séparation entre l'image (code + dépendances) et les volumes/secrets au lancement, ainsi que la résolution DNS entre services Compose (`api` vs `localhost`), sont claires.