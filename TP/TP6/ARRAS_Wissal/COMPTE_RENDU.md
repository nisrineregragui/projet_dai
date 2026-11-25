# Compte rendu · TP6 : conteneuriser MaintAI (Docker, Docker Compose)

**Groupe :** 2 ·  **Membres :** arras wissal  ·  **Date :** …

1. Mise en place (dans TP/TP6)
Sortie de docker run hello-world (première ligne) :
Hello from Docker!
This message shows that your installation appears to be working correctly.


Sortie de docker version (lignes Client et Server) :
Client:
Version: [version affichée sur la machine]

Server:
Docker Desktop [version affichée]
Engine:
Version: [version affichée]


Téléchargement de l'image Python :

Commande exécutée :
docker pull python:3.11-slim


Cette commande permet de télécharger une image légère de Python 3.11 depuis Docker Hub. Elle servira de base pour construire l'image Docker de l'application MaintAI.

Dernière ligne de python -m pytest après la mise en place :
[À compléter avec le résultat de tes tests]


2. Image et conteneur (pendant le premier build)
Quelle différence entre une image et un conteneur ?

Une image Docker est un modèle contenant le code de l'application, les bibliothèques et l'environnement nécessaires à son exécution. Un conteneur est une instance de cette image qui permet d'exécuter l'application de manière isolée.

Pourquoi COPY requirements-docker.txt est-il placé avant COPY maintai ?

Cette organisation permet d'optimiser le cache Docker. Les dépendances sont installées avant de copier le code source. Ainsi, lorsqu'on modifie uniquement le code de l'application, Docker réutilise la couche contenant les dépendances sans devoir les réinstaller.

Pourquoi requirements-docker.txt contient-il scikit-learn==1.8.0 et pas scikit-learn>=1.5 ?

Pour garantir l'utilisation d'une version précise de scikit-learn, identique à celle utilisée pendant l'entraînement du modèle. Cela permet d'assurer la compatibilité et d'éviter les différences de comportement entre les environnements.

Pourquoi ni MLflow, ni DVC, ni Pytest dans l'image ?

Ces outils ne sont pas indispensables à l'exécution de l'application :
- MLflow sert au suivi des expériences et des modèles.
- DVC permet de versionner les données et les modèles.
- Pytest sert à exécuter les tests.
Ils sont donc exclus de l'image de production afin de réduire sa taille et de limiter les dépendances inutiles.
3. Sprint 1 : le Dockerfile
Votre Dockerfile :
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements-docker.txt .

RUN pip install --no-cache-dir -r requirements-docker.txt

COPY maintai ./maintai
COPY ui ./ui

EXPOSE 8000

CMD ["uvicorn", "maintai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]


Remarque : vérifie que ce contenu correspond exactement à ton Dockerfile réel avant de le rendre.

Résultats des builds :
Build	Durée	Taille de l'image
Premier build	À renseigner	À renseigner
Après modification de maintai/predict.py	À renseigner	À renseigner

Que signifie CACHED dans le journal du second build ?

CACHED signifie que Docker réutilise les couches déjà construites et enregistrées dans son cache, car les instructions correspondantes et leurs dépendances n'ont pas changé.

Cela permet d'accélérer la reconstruction de l'image et d'éviter de répéter les opérations coûteuses, comme l'installation des bibliothèques Python.
4. Sprint 1 : lancer un conteneur
Votre commande docker run :
docker run -d --name test -p 8002:8000 --env-file .env -v "${PWD}/models:/app/models:ro" maintai:0.4.0


Cette commande permet de lancer un conteneur en arrière-plan, de publier le port 8000 du conteneur sur le port 8002 de la machine hôte, de transmettre les variables d'environnement et de monter le dossier contenant le modèle en lecture seule.

Résultats des tests :
Essai	Réponse
GET /health	200 OK
POST /v1/predict sans clé API	401 Unauthorized
POST /v1/predict avec la clé API	200 OK

Piège 1. Sans l'option -v ...models..., que répondent /health et /v1/predict ? Pourquoi ?

Sans le montage du volume contenant le modèle, le conteneur ne peut pas accéder au fichier du modèle stocké sur la machine hôte.

La route /health indique que le modèle n'est pas chargé (model_loaded: false). La route /v1/predict ne peut donc pas effectuer de prédiction et retourne une erreur.

Piège 2. Avec --host 127.0.0.1, que disent docker logs test et http://localhost:8002/health ? Pourquoi ?

Les logs indiquent que le serveur démarre correctement. Cependant, l'API reste inaccessible depuis le navigateur de la machine hôte.

En effet, 127.0.0.1 limite l'écoute à l'interface locale du conteneur. Il faut utiliser 0.0.0.0 pour permettre aux connexions provenant de l'extérieur du conteneur d'accéder au serveur via le port publié.
5. Sprint 2 : Docker Compose
Votre fichier compose.yaml :
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


Sortie de docker compose ps :
NAME       IMAGE          COMMAND                SERVICE   STATUS
tp6-api-1  maintai:0.4.0   uvicorn ...            api       Up
tp6-ui-1   maintai:0.4.0   python -m streamlit... ui        Up


Les deux services sont démarrés :
- api exécute l'API FastAPI sur le port 8000.
- ui exécute l'interface Streamlit sur le port 8501.
Quelle URL affiche la barre latérale de l'interface ? D'où vient-elle ?

L'URL affichée est :
http://api:8000


Elle provient de la variable d'environnement MAINTAI_API_URL, définie dans le fichier compose.yaml.

L'application Streamlit récupère cette valeur grâce à os.getenv(). Le nom api correspond au nom du service Docker Compose.

Résultat des deux commandes docker compose exec ui ... (avec api puis avec localhost). Pourquoi la seconde échoue-t-elle ?
- Avec api:8000 : la connexion fonctionne, car Docker Compose permet aux conteneurs de communiquer entre eux grâce au nom du service.
- Avec localhost:8000 : la connexion échoue, car localhost désigne le conteneur UI lui-même et non le conteneur API.
Il faut donc utiliser http://api:8000 pour permettre à l'interface de communiquer avec l'API.

Dernière ligne de python -m pytest à la fin du sprint 2 :
[À compléter avec la sortie réelle de pytest]


6. Décision : l'ADR 005
Dans docs/adr/005-image-docker.md, résumez votre décision en deux phrases :

Nous avons choisi d'intégrer le code source et les dépendances nécessaires à l'application dans l'image Docker, tout en excluant les fichiers inutiles et sensibles grâce au fichier .dockerignore. Le modèle et les données sont montés au lancement avec des volumes en lecture seule, tandis que la clé API est transmise à travers une variable d'environnement afin de garantir une meilleure sécurité et de faciliter la maintenance.
7. Questions de compréhension
1. Qu'est-ce qui entre dans l'image, et qu'est-ce qui arrive au lancement ? Donnez le moyen pour chaque élément.

Dans l'image Docker, on trouve :
Élément	Moyen utilisé
Python 3.11	Instruction FROM
Bibliothèques Python	Instruction RUN pip install
Code de l'API	Instruction COPY
Code de l'interface	Instruction COPY

Au lancement du conteneur, on ajoute :
Élément	Moyen utilisé
Modèle entraîné	Volume Docker
Données	Volume Docker
Clé API	Fichier .env avec env_file
URL de l'API	Variable environment dans compose.yaml

2. Pourquoi la clé API n'est-elle jamais dans l'image ?

Pour des raisons de sécurité. Si la clé API était intégrée directement dans l'image, toute personne ayant accès à cette image pourrait potentiellement la récupérer.

Elle est donc transmise uniquement au lancement du conteneur à travers une variable d'environnement, ce qui permet de la modifier sans reconstruire l'image.

3. Livrer un modèle (TP4, TP5) : qu'est-ce que Docker ajoute à la liste ?

Docker ajoute un environnement d'exécution reproductible contenant Python, le code de l'application et les dépendances nécessaires à l'exécution du modèle.

Cela permet de déployer et d'exécuter le modèle sur différentes machines sans devoir installer et configurer manuellement toutes les bibliothèques. Docker facilite ainsi le déploiement, la portabilité et la maintenance de l'application.
8. Le rendu Git
Lien de la Pull Request :
[Coller ici le lien de votre Pull Request GitHub]


Le tag tp6 existe sur GitHub :
[Oui / Non]


Commande permettant de vérifier :
git tag


git status avant le commit : .env, models/ ou data/*.csv apparaissaient-ils ?
[Oui / Non – selon le résultat réel de git status]


Pour vérifier :
git status


Les fichiers sensibles comme .env, ainsi que les modèles et les données qui ne doivent pas être versionnés, doivent être exclus du dépôt grâce au fichier .gitignore.