# Compte rendu · TP6 : conteneuriser MaintAI (Docker, Docker Compose)

**Groupe :** G2  ·  **Membres :** Assiya MARZAK  ·  **Date :** 24/11/2026

---

## 1. Mise en place (dans `TP/TP6`)

Sortie de `docker run hello-world` (première ligne) et de `docker version` (lignes Client et Server) :

```
Hello from Docker!
This message shows that your installation appears to be working correctly.

Client:
 Version:           29.4.0
 API version:       1.54
 OS/Arch:           windows/amd64
 Context:           desktop-linux

Server: Docker Desktop 4.69.0 (224084)
 Engine:
  Version:          29.4.0
  API version:      1.54 (minimum version 1.40)
  OS/Arch:          linux/amd64
```



## 2. Image et conteneur (pendant le premier build)

1. Quelle différence entre une image et un conteneur ?
   Une image est un modèle figé, en lecture seule (système, Python, bibliothèques, code). Un conteneur est une instance en cours d'exécution de cette image, avec sa propre couche inscriptible, son réseau et ses processus. On peut lancer plusieurs conteneurs à partir d'une même image.
2. Pourquoi `COPY requirements-docker.txt` est-il placé avant `COPY maintai` ?
   Docker met en cache chaque instruction tant que ses entrées n'ont pas changé. Les dépendances changent rarement et leur installation est lente, alors que le code change souvent. En copiant d'abord le fichier de dépendances, une modification de `maintai/` ne relance pas `pip install` : cette couche reste en cache.
3. Pourquoi `requirements-docker.txt` contient-il `scikit-learn==1.8.0` et pas `scikit-learn>=1.5` ?
   Le modèle est sérialisé avec une version précise de scikit-learn. Le charger avec une autre version peut produire des avertissements, des résultats différents ou une erreur. Figer la version rend l'image reproductible : un build fait aujourd'hui ou dans six mois utilise la même bibliothèque.
4. Pourquoi ni `mlflow`, ni `dvc`, ni `pytest` dans l'image ?
   L'image sert uniquement à exécuter l'API et l'interface. MLflow (suivi d'expériences), DVC (versionnement des données) et pytest (tests) sont des outils de développement. Les exclure rend l'image plus légère, plus rapide à construire et à télécharger, et réduit la surface d'attaque.

## 3. Sprint 1 : le Dockerfile

Votre `Dockerfile` :

```dockerfile
# Image de MaintAI : le code et ses bibliothèques, sans les données ni le modèle.
# Construire : docker build -t maintai:0.4.0 .

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
| premier build | À REMPLIR | 1.13 GB (259 MB de contenu compressé) |
| après une modification de `maintai/predict.py` | À REMPLIR (un rebuild entièrement en cache a pris 2,79 s) | 1.13 GB (identique) |

Que signifie `CACHED` dans le journal du second build ?

Docker a réutilisé une couche déjà construite, car l'instruction et les fichiers qu'elle utilise n'ont pas changé. Ici, les étapes jusqu'à `pip install` sont en cache et seule la copie de `maintai/` est refaite. C'est ce qui rend le second build très rapide.

## 4. Sprint 1 : lancer un conteneur

Votre commande `docker run` :

```
docker run -d --name maintai-api -p 8000:8000 --env-file .env -v "${PWD}\models:/app/models:ro" maintai:0.4.0
```

| Essai | Réponse |
|---|---|
| `GET /health` | À REMPLIR (le conteneur Compose répond `{"status":"ok","model_loaded":true}`) |
| `POST /v1/predict` sans clé | À REMPLIR (attendu : 401 ou 403) |
| `POST /v1/predict` avec la clé | À REMPLIR (attendu : 200 avec `failure_probability`) |

(Clé utilisée : la valeur de `MAINTAI_API_KEY` dans `.env`, transmise dans l'en-tête `x-api-key`.)

**Piège 1.** Sans l'option `-v ...models...`, que répondent `/health` et `/v1/predict` ? Pourquoi ?

Observé : À REMPLIR (codes et message de `docker logs`).
Explication : l'image ne contient pas le modèle (exclu par `.dockerignore`, absent du Dockerfile). Sans le volume, `/app/models` est vide dans le conteneur. Le serveur démarre, mais le modèle n'est pas chargé (`model_loaded` à `false` dans `/health`) et `/v1/predict` échoue faute de modèle.

**Piège 2.** Avec `--host 127.0.0.1`, que disent `docker logs test` et `http://localhost:8002/health` ? Pourquoi ?

Observé : À REMPLIR.
Explication : les logs montrent qu'uvicorn démarre normalement, mais sur `http://127.0.0.1:8000`. `localhost:8002/health` ne répond pas (connexion réinitialisée ou refusée). Avec `127.0.0.1`, uvicorn n'écoute que sur l'interface interne du conteneur, alors que le trafic publié par `-p` arrive par l'interface réseau du conteneur. Il faut `--host 0.0.0.0` pour écouter sur toutes les interfaces.

## 5. Sprint 2 : Docker Compose

Votre `compose.yaml` :

```yaml
# MaintAI en deux conteneurs : l'API et l'interface Streamlit.
# Lancer : docker compose up --build      Arrêter : docker compose down

services:
  api:
    build: .
    image: maintai:0.4.0
    env_file: .env                     # MAINTAI_API_KEY, comme au TP2
    ports:
      - "8000:8000"                    # PC:conteneur
    volumes:
      - ./models:/app/models:ro        # modèle du PC, en lecture seule

  ui:
    image: maintai:0.4.0
    command: ["python", "-m", "streamlit", "run", "ui/app.py",
              "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
    environment:
      MAINTAI_API_URL: http://api:8000 # nom du service, port 8000
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data:ro            # données du PC, en lecture seule
    depends_on:
      - api
```

Sortie de `docker compose ps` :

```
NAME        IMAGE           COMMAND                  SERVICE   CREATED         STATUS         PORTS
tp6-api-1   maintai:0.4.0   "uvicorn maintai.api…"   api       5 seconds ago   Up 4 seconds   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
tp6-ui-1    maintai:0.4.0   "python -m streamlit…"   ui        5 seconds ago   Up 3 seconds   0.0.0.0:8501->8501/tcp, [::]:8501->8501/tcp
```

Quelle URL affiche la barre latérale de l'interface ? D'où vient-elle ?

`http://api:8000` (À VÉRIFIER sur votre écran). Elle vient de la variable `MAINTAI_API_URL` définie dans le service `ui` de `compose.yaml`, lue par `ui/app.py` avec `os.getenv("MAINTAI_API_URL", "http://localhost:8000")`. Sans la variable (lancement sur le PC), la valeur par défaut est `http://localhost:8000`.

Résultat des deux commandes `docker compose exec ui ...` (avec `api` puis avec `localhost`). Pourquoi la seconde échoue-t-elle ?

```
> docker compose exec ui python -c "import httpx; print(httpx.get('http://api:8000/health').text)"
{"status":"ok","model_loaded":true}

> docker compose exec ui python -c "import httpx; print(httpx.get('http://localhost:8000/health').text)"
Traceback (most recent call last):
  ...
httpcore.ConnectError: [Errno 111] Connection refused
...
httpx.ConnectError: [Errno 111] Connection refused
```

Chaque conteneur a sa propre pile réseau : `localhost` y désigne le conteneur lui-même. Dans `ui`, seul Streamlit tourne (port 8501) et rien n'écoute sur le 8000, donc la connexion est refusée (`Connection refused`). L'API est dans un autre conteneur, joignable par le nom de service `api` grâce au DNS du réseau Compose. Dans le navigateur, `localhost:8000` fonctionne parce que `localhost` y désigne le PC, où le port de l'API est publié par `-p 8000:8000`.

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
38 passed, 6 warnings in 41.97s
```

## 6. Décision : l'ADR 005

Dans `docs/adr/005-image-docker.md`. Résumez ici votre décision en deux phrases :

À ADAPTER à votre fichier ADR : Nous construisons une image Docker unique contenant uniquement le code et ses bibliothèques aux versions figées, sans les données, le modèle ni le secret. Ceux-ci sont fournis au lancement (volumes en lecture seule et `--env-file`), et Docker Compose orchestre l'API et l'interface sur un réseau commun.

## 7. Questions de compréhension

1. Qu'est-ce qui entre dans l'image, et qu'est-ce qui arrive au lancement ? Donnez le moyen pour chaque élément.
   Dans l'image (`COPY` et `RUN pip install`) : le code (`maintai/`, `ui/`) et les bibliothèques aux versions figées. Au lancement : le modèle (volume `./models:/app/models:ro`), les données (volume `./data:/app/data:ro`), le secret `MAINTAI_API_KEY` (`env_file: .env` ou `--env-file .env`) et l'adresse de l'API pour l'interface (`environment: MAINTAI_API_URL`).
2. Pourquoi la clé API n'est-elle jamais dans l'image ?
   Une image se partage (registre, collègues) et ses couches sont lisibles : un secret copié dedans serait exposé à quiconque la récupère, même supprimé dans une couche ultérieure. `.env` est donc exclu par `.dockerignore` et injecté seulement à l'exécution, ce qui permet aussi de changer la clé sans reconstruire l'image.
3. Livrer un modèle (TP4, TP5) : qu'est-ce que Docker ajoute à la liste ?
   L'environnement d'exécution : version de Python, système et bibliothèques (dont la version exacte de scikit-learn). Le modèle, les données et le code sont déjà versionnés (TP4, TP5), mais Docker garantit qu'ils tournent de la même façon partout : fini le « ça marche sur mon PC ».

## 8. Le rendu Git

- Lien de la pull request : À REMPLIR
- Le tag `tp6` existe sur GitHub : À REMPLIR (oui / non)
- `git status` avant le commit : `.env`, `models/` ou `data/*.csv` apparaissaient-ils ? À REMPLIR (attendu : non, car ils sont ignorés)

## 9. Ce qui reste flou

À REMPLIR avec vos vraies questions. Idées si vous n'avez rien de précis : la différence entre `EXPOSE` et `-p`, ou le fait que `depends_on` n'attend pas que l'API soit prête.