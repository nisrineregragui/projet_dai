# Compte rendu · TP6 : conteneuriser MaintAI (Docker, Docker Compose)

**Groupe :** G2 ·  **Membres :** Regragui Nisrine  ·  **Date :** 24/11/2026 17:30

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP6.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP6`)

Sortie de `docker run hello-world` (première ligne) et de `docker version` (lignes Client et Server) :

docker run hello-world

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/

(TP6) PS C:\Users\nisri\Downloads\S8-tp6\TP6> docker version
Client:
 Version:           29.8.2
 API version:       1.56
 Go version:        go1.26.8
 Git commit:        7fc2dff
 Built:             Wed Sep 30 19:35:42 2026
 OS/Arch:           windows/amd64
 Context:           desktop-linux

Server: Docker Desktop 4.94.0 (241994)
 Engine:
  Version:          29.8.2
  API version:      1.56 (minimum version 1.40)
  Go version:       go1.26.8
  Git commit:       8af9fe3
  Built:            Wed Sep 30 19:32:25 2026
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          v2.3.6
  GitCommit:        ee2735368117d2eb259779949d5e75cdafec9761
 runc:
  Version:          1.5.1
  GitCommit:        v1.5.1-0-g8f2685a4
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0
(TP6) PS C:\Users\nisri\Downloads\S8-tp6\TP6> docker pull python:3.11-slim
3.11-slim: Pulling from library/python
7cb68d39cd28: Pull complete 
ac4f3e55c849: Pull complete 
40748add9f4f: Pull complete 
03bf319e97a9: Pull complete 
f6984b1a9430: Download complete 
e4c916ade7df: Download complete 
Digest: sha256:61e01f72680f86a5279ad510818ab7b2ee9f049822589d4e34e33e044360356c
Status: Downloaded newer image for python:3.11-slim
docker.io/library/python:3.11-slim

Dernière ligne de `python -m pytest` après la mise en place :

```
============= 5 failed, 33 passed, 4 warnings in 40.86s =============
```

## 2. Image et conteneur (pendant le premier build)

1. Quelle différence entre une image et un conteneur ?
  Une image contient le code, les bibliothèques et l'environnement nécessaires à l'application. Un conteneur est une instance de cette image.
2. Pourquoi `COPY requirements-docker.txt` est-il placé avant `COPY maintai` ?
   Pour utiliser le cache Docker et éviter de réinstaller les bibliothèques chaque fois qu'on modifie le code
3. Pourquoi `requirements-docker.txt` contient-il `scikit-learn==1.8.0` et pas `scikit-learn>=1.5` ?
  Pour garantir l'utilisation de la même version de scikit-learn que celle utilisée pendant l'entraînement du modèle et éviter les problèmes de compatibilité.
4. Pourquoi ni `mlflow`, ni `dvc`, ni `pytest` dans l'image ?
Parce qu'on utilise l'image pour exécuter l'application, pas pour entraîner le modèle, versionner les données ou effectuer les tests. Cela permet aussi de réduire la taille de l'image.

## 3. Sprint 1 : le Dockerfile

Votre `Dockerfile` :

```dockerfile
(collez ici)
```

| Build | Durée | Taille de l'image (`docker images`) |
|---|---|---|
| premier build | 151,4 s|1,13GB |
| après une modification de `maintai/predict.py` | 0,7 s| 1,13GB |

Que signifie `CACHED` dans le journal du second build ?

CACHED signifie que Docker réutilise les couches qui n'ont pas changé. Dans notre cas, les bibliothèques n'ont pas été réinstallées, ce qui a permis de passer de 151,4 secondes à 0,7 seconde

## 4. Sprint 1 : lancer un conteneur

Votre commande `docker run` :

```
(collez ici)
```

| Essai | Réponse |
|---|---|
| `GET /health` | 200 ok  |
| `POST /v1/predict` sans clé |401 unauthorized |
| `POST /v1/predict` avec la clé | 200 ok|

**Piège 1.** Sans l'option `-v ...models...`, que répondent `/health` et `/v1/predict` ? Pourquoi ?
Sans le volume, le modèle n'est pas accessible depuis le conteneur. La route /health retourne model_loaded: false et la prédiction retourne une erreur 50
…

**Piège 2.** Avec `--host 127.0.0.1`, que disent `docker logs test` et `http://localhost:8002/health` ? Pourquoi ?
Le serveur démarre correctement mais l'API est inaccessible depuis mon navigateur, car 127.0.0.1 limite l'écoute à l'interface locale du conteneur. Il faut utiliser 0.0.0.0 pour permettre l'accès depuis le PC via le port publié.

## 5. Sprint 2 : Docker Compose

Votre `compose.yaml` :

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

Sortie de `docker compose ps` :

 docker compose ps
NAME        IMAGE           COMMAND                  SERVICE   CREATED         STATUS         PORTS
tp6-api-1   maintai:0.4.0   "uvicorn maintai.api…"   api       6 seconds ago   Up 4 seconds   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
tp6-ui-1    maintai:0.4.0   "python -m streamlit…"   ui        6 seconds ago   Up 4 seconds   0.0.0.0:8501->8501/tcp, [::]:8501->8501/tcp
(TP6) PS C:\Users\nisri\Downloads\S8-tp6\TP6> 

Quelle URL affiche la barre latérale de l'interface ? D'où vient-elle ?
L'URL http://api:8000 est récupérée depuis la variable d'environnement MAINTAI_API_URL définie dans compose.yaml grâce à os.getenv().
Résultat des deux commandes `docker compose exec ui ...` (avec `api` puis avec `localhost`). Pourquoi la seconde échoue-t-elle ?

```
(collez ici)
```

…

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

============================== 38 passed, 4 warnings in 47.91s =============================

## 6. Décision : l'ADR 005

Dans `docs/adr/005-image-docker.md`. Résumez ici votre décision en deux phrases :

Nous avons choisi d'intégrer le code et les dépendances dans
l'image Docker, tout en excluant les fichiers inutiles et
sensibles grâce à .dockerignore.
Le modèle et les données sont montés au lancement avec des
volumes en lecture seule, ce qui permet de les modifier sans
reconstruire l'image, tandis que la clé API est transmise
par une variable d'environnement.

## 7. Questions de compréhension

1. Qu'est-ce qui entre dans l'image, et qu'est-ce qui arrive au lancement ? Donnez le moyen pour chaque élément.

   Dans l'image, on trouve :
   - Python 3.11 grâce à FROM.
   - Les bibliothèques grâce à RUN pip install.
   - Le code de l'API et de l'interface grâce à COPY.

   Au lancement du conteneur, on ajoute :
   - Le modèle et les données grâce aux volumes.
   - La clé API grâce à env_file (.env).
   - L'URL de l'API grâce à environment dans compose.yaml.

2. Pourquoi la clé API n'est-elle jamais dans l'image ?

   Pour des raisons de sécurité. Si la clé était dans l'image,
   toute personne ayant accès à cette image pourrait la récupérer.
   Elle est donc transmise uniquement au lancement du conteneur.

3. Livrer un modèle (TP4, TP5) : qu'est-ce que Docker ajoute à la liste ?

   Docker ajoute un environnement d'exécution reproductible
   contenant le code, Python et les dépendances nécessaires.
   Cela permet de déployer et d'exécuter le modèle sur différentes
   machines sans installer manuellement les bibliothèques.

## 8. Le rendu Git

- Lien de la pull request : …
- Le tag `tp6` existe sur GitHub : oui / non
- `git status` avant le commit : `.env`, `models/` ou `data/*.csv` apparaissaient-ils ? oui / non

## 9. Ce qui reste flou

…
