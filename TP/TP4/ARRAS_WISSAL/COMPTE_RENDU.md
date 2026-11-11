# Compte rendu · TP4 : MaintAI devient un package Python

**Groupe :** …  ·  **Membres :** ARRAS Wissal  ·  **Date :** 11/11/2026

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :

```
=================== 2 failed, 25 passed, 1 warning in 28.43s ===================
```

Quels sont les deux tests qui échouent, et pourquoi ?

- `tests/test_package.py::test_installed_version_matches_the_code` échoue avec `PackageNotFoundError: No package metadata was found for maintai`. Le test lit la version du package installé, mais `maintai` n'est pas installé dans le `.venv` : il n'existe que comme dossier de travail, donc il n'y a aucune métadonnée à lire.
- `tests/test_package.py::test_command_is_declared` échoue avec `assert 'maintai-predict' in ['pyproject-build', 'normalizer', ...]`. La commande `maintai-predict` n'est pas déclarée dans `[project.scripts]` et n'est donc pas installée : on ne trouve que les commandes d'autres paquets.

Les deux échecs ont la même cause : `pyproject.toml` était incomplet et le package n'était pas installé.

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

Vos sections `dependencies` et `[project.scripts]` :

```toml
dependencies = [
    "numpy>=2.0",
    "pandas>=2.2",
    "scikit-learn>=1.5",
    "joblib>=1.4",
    "httpx>=0.27",
]

[project.scripts]
maintai-predict = "maintai.cli:main"
```

Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?

`dependencies` ne contient que ce dont le code de `maintai/` a besoin pour fonctionner chez tout utilisateur (numpy, pandas, scikit-learn, joblib, et httpx pour `client.py`). `pytest` ne sert qu'aux développeurs qui lancent les tests (groupe `dev`). `fastapi` ne sert qu'à ceux qui lancent l'API (groupe `api`, importé seulement dans `maintai/api/`). Ces dépendances s'installent à la demande, par exemple avec `pip install maintai[api]`.

Sortie de `pip show maintai` (les quatre premières lignes) :

```
Name: maintai
Version: 0.2.0
Summary: Prédiction de panne de machines à partir de relevés de capteurs
Home-page:
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
======================== 27 passed, 1 warning in 7.55s =========================
```

Depuis un autre dossier (`cd $env:TEMP` sous PowerShell), `maintai-predict 72 6 85 15000` puis `python -c "import maintai; print(maintai.__file__)"` :

```
Probabilité de panne : 95 % (ALERTE)
C:\Users\user\Downloads\TP4\maintai-starter-tp4\maintai\__init__.py
```

(Avant d'avoir entraîné le modèle, la commande affichait « Modèle introuvable » : la commande était bien trouvée, mais `models/model.joblib` n'existait pas encore. Après `python -m maintai.dataset` et `python -m maintai.train`, la prédiction fonctionne.)

Où Python trouve-t-il le code de `maintai` ?

Dans mon dossier de sources (`...\maintai-starter-tp4\maintai\`), pas dans `site-packages`. Avec `pip install -e .`, pip ne copie pas le code : il enregistre un lien vers le dossier du projet. La commande fonctionne depuis n'importe quel dossier parce qu'elle est installée dans le `.venv`.

Modification du message de `maintai/cli.py`, puis `maintai-predict` sans réinstaller :

```
Risque de panne : 95 % (ALERTE)
```

Le changement est-il visible ? Pourquoi ?

Oui, il est visible immédiatement, sans réinstaller, parce que le mode éditable fait pointer Python vers mes fichiers sources : chaque exécution relit le fichier modifié. J'ai ensuite remis le message d'origine (`Probabilité de panne`).

## 3. Sprint 2 : construire et installer le wheel

Sortie de `dir dist` après `python -m build` :

```
-a----        11/11/2026     11:11          11622 maintai-0.2.0-py3-none-any.whl
-a----        11/11/2026     11:11          12243 maintai-0.2.0.tar.gz
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

Non, ni le modèle, ni les tests, ni `ui/` ne sont dans le wheel. `include = ["maintai*"]` dans `pyproject.toml` limite le package au dossier `maintai/`. Le modèle (`models/`) est un fichier produit par l'entraînement, pas du code ; les tests et `ui/` sont hors du dossier `maintai/`. (Le `.tar.gz`, lui, est une archive des sources et contient les tests.)

Dans un environnement neuf (`%TEMP%\essai`), installation du wheel et `maintai-predict` :

| Étape | Ce qui s'affiche |
|---|---|
| sans `MAINTAI_MODELS_DIR` | `Modèle introuvable : C:\Users\user\AppData\Local\Temp\essai\Lib\site-packages\models\model.joblib` puis « Entraînez-le (python -m maintai.train) ou indiquez son dossier dans MAINTAI_MODELS_DIR. » |
| avec `MAINTAI_MODELS_DIR` vers vos `models` | 3 `InconsistentVersionWarning` (StandardScaler, LogisticRegression, Pipeline : « from version 1.8.0 when using version 1.9.1 »), puis `Probabilité de panne : 95 % (ALERTE)` |
| après `pip install scikit-learn==1.8.0` | `Probabilité de panne : 95 % (ALERTE)`, sans avertissement |

D'où vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?

Le modèle a été entraîné avec scikit-learn 1.8.0, mais `dependencies` n'impose qu'une version minimale (`scikit-learn>=1.5`). Dans l'environnement neuf, pip a installé la dernière version (1.9.1). Au chargement du fichier, scikit-learn détecte que la version qui l'a sérialisé diffère de la sienne et prévient. La ligne qui l'explique dans `models/model_info.json` :

```
"sklearn_version": "1.8.0"
```

Après `pip install scikit-learn==1.8.0`, les versions coïncident et l'avertissement disparaît. Le résultat est le même ici (95 %), mais avec des versions différentes il pourrait être faux sans prévenir.

## 4. Questions de compréhension

1. Quelle différence entre `requirements.txt` et la liste `dependencies` de `pyproject.toml` ?

   `requirements.txt` fige des versions exactes (`==`) pour reproduire un environnement précis, ici celui avec lequel le modèle a été entraîné. `dependencies` décrit ce dont le package a besoin, avec des versions minimales, pour qu'il s'installe à côté d'autres paquets sans conflit. Le premier sert à reproduire, le second à distribuer.

2. Quelle différence entre `pip install -e .` et `pip install dist\maintai-0.2.0-py3-none-any.whl` ?

   `pip install -e .` installe un lien vers mes sources : toute modification du code est visible immédiatement, ce qui sert au développement. Le wheel est une archive figée dont le code est copié dans `site-packages` : c'est ce qu'on distribue, et il ne suit pas les modifications des sources. Le wheel ne contient pas le modèle, d'où `MAINTAI_MODELS_DIR`.

3. Qu'est-ce qu'un « point d'entrée » (`[project.scripts]`) ? Où pip crée-t-il le fichier `maintai-predict.exe` ?

   Un point d'entrée associe un nom de commande à une fonction Python, au format `nom = "module:fonction"` (ici `maintai.cli:main`). À l'installation, pip génère un petit exécutable qui appelle cette fonction. Il est créé dans le dossier `Scripts` de l'environnement virtuel actif : `.venv\Scripts\maintai-predict.exe`.

## 5. Le rendu Git

- Lien de la pull request : … (à compléter, ou « push direct sur `master`, pas de PR » si c'est la consigne)
- Le tag `tp4` existe sur GitHub : … (j'ai utilisé le tag `tp4-arras-wissal`)
- `git status` avant le commit : `dist/`, `build/` ou `maintai.egg-info/` apparaissaient-ils ? **non** (exclus à la copie avec robocopy, et ignorés par `.gitignore`)

## 6. Ce qui reste flou

- La différence entre le mode éditable et le wheel : j'ai compris qu'elle tient à l'endroit où Python lit le code, mais j'ai dû tester les deux pour en être sûre.
- La gestion des versions : pourquoi `dependencies` accepte des versions minimales alors que le modèle exige scikit-learn 1.8.0, et comment garantir que l'utilisateur installe la bonne version.
- Git : mon dossier utilisateur contenait un dépôt Git créé par erreur, ce qui m'a obligée à cloner le dépôt du cours dans un dossier propre avant de pousser.