# Compte rendu · TP4 : MaintAI devient un package Python

**Groupe :** G2 · **Membres :** Wissal ARRAS · **Date :** 10/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP4.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :

```
============================================ 2 failed, 25 passed in 2.13s =============================================
```

Quels sont les deux tests qui échouent, et pourquoi ?

- `test_installed_version_matches_the_code` échoue car `maintai` n'est pas encore installé dans le venv.
- `test_command_is_declared` échoue car la commande `maintai-predict` n'est pas encore déclarée dans le `pyproject.toml`.

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

Vos sections `dependencies` et `[project.scripts]` :

```toml
dependencies = [
    "pandas>=2.0",
    "scikit-learn>=1.4",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "httpx>=0.27",
]

[project.scripts]
maintai-predict = "maintai.cli:main"
```

Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?

Parce que le code de base de `maintai` (faire une prédiction) n'en a pas besoin pour fonctionner. `pytest` sert uniquement au développement (groupe `dev`) et `fastapi` uniquement à l'API (groupe `api`). Ils sont dans les groupes optionnels pour ne pas alourdir l'installation de ceux qui n'en ont pas l'usage.

Sortie de `pip show maintai` (les quatre premières lignes) :

```
Name: maintai
Version: 0.2.0
Summary: Prédiction de pannes de machines à partir de données capteurs (modèle scikit-learn, CLI et API)
Home-page:
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
============================================ 27 passed, 1 warning in 1.57s ============================================
```

Placez-vous dans un autre dossier et lancez `maintai-predict 72 6 85 15000`, puis `python -c "import maintai; print(maintai.__file__)"`. Qu'affichent ces deux commandes ? Où Python trouve-t-il le code de `maintai` ?

```
maintai-predict 72 6 85 15000
Probabilité de panne : 95 % (ALERTE)

/Users/adam/Documents/DAI/Session_6/TP4/maintai-starter-tp4/maintai/__init__.py
```

Avec `pip install -e .`, Python ne copie pas le code : le venv contient seulement un lien vers le dossier du projet. Python trouve donc le code directement dans le dossier source `maintai/`.

Modifiez le message affiché par `maintai/cli.py`, puis relancez `maintai-predict` sans réinstaller. Le changement est-il visible ? Pourquoi ?

Oui, le changement est visible sans réinstaller, car l'installation en mode editable (`-e`) pointe vers les fichiers sources : chaque modification est prise en compte immédiatement.

## 3. Sprint 2 : construire et installer le wheel

Sortie de `dir dist` après `python -m build` :

```
maintai-0.2.0-py3-none-any.whl  maintai-0.2.0.tar.gz
```

Contenu du wheel (`tar -tf dist\maintai-0.2.0-py3-none-any.whl`). Le modèle, les tests et `ui/` y sont-ils ? Pourquoi ?

```
maintai/__init__.py
maintai/cli.py
maintai/client.py
maintai/config.py
maintai/data.py
maintai/dataset.py
maintai/predict.py
maintai/train.py
maintai/api/__init__.py
maintai/api/main.py
maintai/api/schemas.py
maintai/api/security.py
maintai-0.2.0.dist-info/METADATA
maintai-0.2.0.dist-info/WHEEL
maintai-0.2.0.dist-info/entry_points.txt
maintai-0.2.0.dist-info/top_level.txt
maintai-0.2.0.dist-info/RECORD
```

Non : ni le modèle (`models/`), ni les tests, ni `ui/` ne sont dans le wheel. Dans le `pyproject.toml`, `[tool.setuptools.packages.find]` contient `include = ["maintai*"]` : setuptools n'embarque que le dossier `maintai/`. Le modèle `.joblib` est un fichier de données, pas du code, et il est situé hors du package.

Dans un environnement neuf (`%TEMP%\essai`), installez le wheel et lancez `maintai-predict` :

| Étape | Ce qui s'affiche |
| --- | --- |
| sans `MAINTAI_MODELS_DIR` | Modèle introuvable : /private/tmp/essai/venv_test/lib/python3.13/site-packages/models/model.joblib. Entraînez-le (python -m maintai.train) ou indiquez son dossier dans MAINTAI_MODELS_DIR. |
| avec `MAINTAI_MODELS_DIR` vers vos `models` | Probabilité de panne : 95 % (ALERTE), avec un avertissement `InconsistentVersionWarning` |
| après `pip install scikit-learn==1.8.0` | Probabilité de panne : 95 % (ALERTE), sans avertissement |

D'où vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?

Le modèle a été entraîné avec une version de scikit-learn différente de celle installée dans l'environnement neuf. La ligne `"sklearn_version": "1.8.0"` de `models/model_info.json` donne la version d'entraînement. Après installation de `scikit-learn==1.8.0`, l'avertissement disparaît.

## 4. Questions de compréhension

1. Quelle différence entre `requirements.txt` et la liste `dependencies` de `pyproject.toml` ?

   `requirements.txt` décrit un environnement complet à reproduire (outils de dev, tests, etc.), souvent avec des versions précises. `dependencies` ne liste que le minimum nécessaire au fonctionnement du package, avec des versions minimales, et c'est ce que pip installe automatiquement avec le package.

2. Quelle différence entre `pip install -e .` et `pip install dist\maintai-0.2.0-py3-none-any.whl` ?

   La première est une installation éditable : le venv pointe vers le dossier source, donc toute modification du code est visible immédiatement. La seconde installe une copie figée du code, telle qu'elle était au moment du build ; il faut reconstruire et réinstaller pour voir un changement.

3. Qu'est-ce qu'un « point d'entrée » (`[project.scripts]`) ? Où pip crée-t-il le fichier `maintai-predict.exe` ?

   Un point d'entrée associe une commande du terminal à une fonction Python précise (`maintai-predict` → `maintai.cli:main`). pip crée l'exécutable dans le dossier des scripts de l'environnement virtuel (`.venv\Scripts` sous Windows, `.venv/bin` sous macOS/Linux).

## 5. Le rendu Git

- Lien de la pull request : https://github.com/nisrineregragui/projet_dai/
- Le tag `tp4` existe sur GitHub : non
- `git status` avant le commit : `dist/`, `build/` ou `maintai.egg-info/` apparaissaient-ils ? non

## 6. Ce qui reste flou

Tout est clair.
