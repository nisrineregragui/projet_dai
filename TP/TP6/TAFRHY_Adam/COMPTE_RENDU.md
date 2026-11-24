# Compte rendu · TP6 : conteneuriser MaintAI (Docker, Docker Compose)

**Groupe :** G2 · **Membres :** Adam TAFRHY · **Date :** 24/11/2026. **Heure :** 18:02

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP6.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP6`)

Sortie de `docker run hello-world` (première ligne) et de `docker version` (lignes Client et Server) :

```
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
58dee6a49ef1: Pull complete
c3bdf82c34d1: Download complete
Digest: sha256:1e4c05b897a751332ce85c7e9449da2d93514ea2dea6dbb0e2753c9e949b2bfa
Status: Downloaded newer image for hello-world:latest

Hello from Docker!

(venv) adam@MacBook-Pro-2 TP6 % docker version
Client:
 Version:           29.8.1

 Server: Docker Desktop 4.93.0 (240920)
 Engine:
  Version:          29.8.1
```

Dernière ligne de `python -m pytest` après la mise en place :

```
========================================= 5 failed, 33 passed, 4 warnings in 7.96s ==========================================
```

## 2. Image et conteneur (pendant le premier build)

1. Quelle différence entre une image et un conteneur ?
   Une image est un modèle figé en lecture seule (contenant le système, Python, les bibliothèques et le code) construit à partir d'un Dockerfile. Un conteneur est une instance exécutable et isolée de cette image qui tourne en mémoire avec ses propres processus et son propre réseau.
2. Pourquoi `COPY requirements-docker.txt` est-il placé avant `COPY maintai` ?
   Docker met en cache chaque couche d'instructions et réutilise les couches inchangées jusqu'à la première modification. Placer requirements-docker.txt et pip install avant le code évite de retélécharger et réinstaller toutes les bibliothèques (très long) à chaque modification du code Python.
3. Pourquoi `requirements-docker.txt` contient-il `scikit-learn==1.8.0` et pas `scikit-learn>=1.5` ?
   Pour garantir la reproductibilité stricte de l'environnement et éviter les erreurs d'incompatibilité de sérialisation (joblib / skops) entre la version de scikit-learn ayant entraîné le modèle et celle présente dans le conteneur.
4. Pourquoi ni `mlflow`, ni `dvc`, ni `pytest` dans l'image ?
   Ce sont des outils de développement, de suivi d'expériences et de tests, inutiles pour exécuter l'API ou l'interface en production. Les exclure allège considérablement la taille de l'image et réduit le temps de build.

## 3. Sprint 1 : le Dockerfile

Votre `Dockerfile` :

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY maintai ./maintai
COPY ui ./ui

ENV MAINTAI_MODELS_DIR=/app/models

EXPOSE 8000

CMD ["uvicorn", "maintai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

| Build                                          | Durée  | Taille de l'image (`docker images`) |
| ---------------------------------------------- | ------ | ----------------------------------- |
| premier build                                  | 61,5 s | 1.16GB                              |
| après une modification de `maintai/predict.py` | 1,4 s  | 1.16GB                              |

Que signifie `CACHED` dans le journal du second build ?

CACHED signifie que Docker a réutilisé directement la couche issue du build précédent sans réexécuter l'instruction correspondante (comme RUN pip install), car ni cette ligne ni les fichiers qu'elle utilise (requirements-docker.txt) n'ont été modifiés. Docker ne reconstruit ainsi que les couches à partir de la première modification (COPY maintai ./maintai), ce qui rend le second build quasi instantané.

## 4. Sprint 1 : lancer un conteneur

Votre commande `docker run` :

```
docker run -d --name maintai-api -p 8000:8000 --env-file .env -v "$(pwd)/models:/app/models:ro" maintai:0.4.0
```

| Essai                          | Réponse                                                                                            |
| ------------------------------ | -------------------------------------------------------------------------------------------------- |
| `GET /health`                  | {"status":"ok","model_loaded":true}                                                                |
| `POST /v1/predict` sans clé    | HTTP/1.1 401 Unauthorized                                                                          |
| `POST /v1/predict` avec la clé | {"failure_probability":0.7912,"alert":true,"threshold":0.3,"model_version":"2026-11-24T15:35:25Z"} |

**Piège 1.** Sans l'option `-v ...models...`, que répondent `/health` et `/v1/predict` ? Pourquoi ?

GET /health répond {"status":"ok","model_loaded":false} et POST /v1/predict renvoie une erreur 503 Service Unavailable (« Modèle non chargé »). Comme le dossier models/ est ignoré par .dockerignore, le répertoire /app/models du conteneur est vide sans le montage du volume -v, ce qui empêche l'API de charger un modèle.

**Piège 2.** Avec `--host 127.0.0.1`, que disent `docker logs test` et `http://localhost:8002/health` ? Pourquoi ?

docker logs test affiche Uvicorn running on http://127.0.0.1:8000, tandis que l'appel à http://localhost:8002/health depuis le Mac échoue (connexion refusée / réponse vide). Dans un conteneur, 127.0.0.1 restreint l'écoute au conteneur lui-même ; il faut utiliser 0.0.0.0 pour écouter sur toutes les interfaces réseau, y compris celle reliée au port 8002 du Mac par Docker.

## 5. Sprint 2 : Docker Compose

Votre `compose.yaml` :

```yaml
services:
  api:
    build: .
    image: maintai:0.4.0
    env_file: .env # MAINTAI_API_KEY, comme au TP2
    ports:
      - "8000:8000" # PC:conteneur
    volumes:
      - ./models:/app/models:ro
  ui:
    image: maintai:0.4.0
    build: .
    command:
      [
        "python",
        "-m",
        "streamlit",
        "run",
        "ui/app.py",
        "--server.address",
        "0.0.0.0",
        "--server.port",
        "8501",
      ]
    ports:
      - "8501:8501"
    environment:
      - MAINTAI_API_URL=http://api:8000
    volumes:
      - ./data:/app/data:ro
    depends_on:
      - api
```

Sortie de `docker compose ps` :

```
NAME        IMAGE           COMMAND                  SERVICE   CREATED          STATUS          PORTS
tp6-api-1   maintai:0.4.0   "uvicorn maintai.api…"   api       10 seconds ago   Up 10 seconds   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
tp6-ui-1    maintai:0.4.0   "python -m streamlit…"   ui        10 seconds ago   Up 10 seconds   0.0.0.0:8501->8501/tcp, [::]:8501->8501/tcp
```

Quelle URL affiche la barre latérale de l'interface ? D'où vient-elle ?

Elle affiche http://api:8000. Elle provient de la variable d'environnement MAINTAI_API_URL=http://api:8000 injectée au conteneur ui via compose.yaml et lue par défaut au démarrage dans ui/app.py (os.getenv("MAINTAI_API_URL", "http://localhost:8000")).

Résultat des deux commandes `docker compose exec ui ...` (avec `api` puis avec `localhost`). Pourquoi la seconde échoue-t-elle ?

```
(venv) adam@MacBook-Pro-2 TP6 % docker compose exec ui python -c "import httpx; print(httpx.get('http://api:8000/health').text)"
{"status":"ok","model_loaded":true}

(venv) adam@MacBook-Pro-2 TP6 % docker compose exec ui python -c "import httpx; print(httpx.get('http://localhost:8000/health').text)"
httpx.ConnectError: [Errno 111] Connection refused
```

localhost

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
============================================== 38 passed, 4 warnings in 8.13s ===============================================
```

## 6. Décision : l'ADR 005

Dans `docs/adr/005-image-docker.md`. Résumez ici votre décision en deux phrases :

Nous avons décidé de n'embarquer dans l'image Docker que le système, les bibliothèques de production et le code applicatif (maintai/, ui/), tout en excluant via .dockerignore le modèle (models/), les données (data/), les secrets (.env) et les artefacts de développement (mlflow.db, mlruns/, .dvc/, .venv/, tests/). Cette séparation protège la clé API, allège l'image et permet de mettre à jour le modèle par un simple montage de volume en lecture seule au lancement sans devoir reconstruire l'image.

## 7. Questions de compréhension

1. Qu'est-ce qui entre dans l'image, et qu'est-ce qui arrive au lancement ? Donnez le moyen pour chaque élément.
   - Dans l'image (au docker build, via les instructions FROM, COPY et RUN du Dockerfile) : le système Linux de base et Python 3.11 (FROM python:3.11-slim), les bibliothèques figées (COPY requirements-docker.txt puis RUN pip install), ainsi que le code de l'application (COPY maintai ./maintai et COPY ui ./ui).
   - Au lancement du conteneur (au docker run ou docker compose up) : les modèles entraînés (models/ monté par un volume -v ou volumes:), les données (data/ monté par un volume -v ou volumes:), et les variables d'environnement / secrets (.env injecté via --env-file ou env_file:).
2. Pourquoi la clé API n'est-elle jamais dans l'image ?
   Parce qu'une image Docker est figée et destinée à être partagée : y intégrer un secret exposerait la clé à quiconque récupère ou inspecte l'image. De plus, l'injecter au lancement (--env-file .env) permet de changer de clé selon l'environnement sans devoir reconstruire l'image.
3. Livrer un modèle (TP4, TP5) : qu'est-ce que Docker ajoute à la liste ?
   Après le code versionné, le paquet Python (wheel) et le modèle entraîné (TP4/TP5), Docker ajoute l'environnement d'exécution complet (le système Linux, la version exacte de Python et toutes les dépendances figées) dans une image portable qui tourne à l'identique sur n'importe quel PC ou serveur sans avoir à préparer de venv.

## 8. Le rendu Git

- Lien de la pull request : https://github.com/nisrineregragui/projet_dai
- Le tag `tp6` existe sur GitHub : non
- `git status` avant le commit : `.env`, `models/` ou `data/*.csv` apparaissaient-ils ? non

## 9. Ce qui reste flou

Tout est clair.
