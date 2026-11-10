# Compte rendu · TP4 : MaintAI devient un package Python

**Groupe :** G2 · **Membres :** Adam TAFRHY · **Date :** 10/11/2026 **Temps**: 18:22

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP4.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :

```
============================================ 2 failed, 25 passed in 2.13s =============================================
```

Quels sont les deux tests qui échouent, et pourquoi ?

le premier test est test_installed_version_matches_the_code car maintai n'est pas encore installe dans le venv. le deuxieme test est test_command_is_declared car maintai-predict n'est pas encore declare dans la configuration du projet dans le pyproject.toml

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

car nous en avons pas besoin pour faire une prediction

Sortie de `pip show maintai` (les quatre premières lignes) :

```
Name: maintai
Version: 0.2.0
Summary: TODO : une phrase qui dit ce que fait le package
Home-page:
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
============================================ 27 passed, 1 warning in 1.57s ============================================
```

Placez-vous dans un autre dossier (`cd %TEMP%`) et lancez `maintai-predict 72 6 85 15000`, puis `python -c "import maintai; print(maintai.__file__)"`. Qu'affichent ces deux commandes ? Où Python trouve-t-il le code de `maintai` ?

maintai-predict 72 6 85 15000
Probabilité de panne : 95 % (ALERTE)
/Users/adam/Documents/DAI/Session_6/TP4/maintai-starter-tp4/maintai/**init**.py

Python trouve le code dans le venv

Modifiez le message affiché par `maintai/cli.py`, puis relancez `maintai-predict` sans réinstaller. Le changement est-il visible ? Pourquoi ?

oui le changement est visible sans reinstaller car nous avons installe en mode editable avec l'extension -e

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


on y trouve le modele et les test et ui car setuptools integre que maintai
```

Dans un environnement neuf (`%TEMP%\essai`), installez le wheel et lancez `maintai-predict` :

| Étape                                                                                   | Ce qui s'affiche                                                                                   |
| --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| sans `MAINTAI_MODELS_DIR`                                                               | Modèle introuvable : /private/tmp/essai/venv_test/lib/python3.13/site-packages/models/model.joblib |
| Entraînez-le (python -m maintai.train) ou indiquez son dossier dans MAINTAI_MODELS_DIR. |
| avec `MAINTAI_MODELS_DIR` vers vos `models`                                             | Probabilité de panne : 95 % (ALERTE) avec Warning                                                  |
| après `pip install scikit-learn==1.8.0`                                                 | Modification: Probabilité de panne : 95 % (ALERTE)                                                 |

D'où vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?

l'avertissement vient de la version de scikit learn. la ligne de models/model_info.json qui permet de le comprendre est "sklearn_version": "1.8.0"

## 4. Questions de compréhension

1. Quelle différence entre `requirements.txt` et la liste `dependencies` de `pyproject.toml` ?
   requirements est pour un environnement complet tandis que dependecies de pyproject contient les dependences minimales necessaires au bon fonctionnement.
2. Quelle différence entre `pip install -e .` et `pip install dist\maintai-0.2.0-py3-none-any.whl` ?
   la premiere est une version editable donc toute modification dans le code se voit tandis que la deuxieme est statique.
3. Qu'est-ce qu'un « point d'entrée » (`[project.scripts]`) ? Où pip crée-t-il le fichier `maintai-predict.exe` ?
   un point d'entree associe une commande terminal a une fonction python precise. pip cree le fichier .exe dans l'environnement vituel.

## 5. Le rendu Git

- Lien de la pull request :https://github.com/nisrineregragui/projet_dai/
- Le tag `tp4` existe sur GitHub : non
- `git status` avant le commit : `dist/`, `build/` ou `maintai.egg-info/` apparaissaient-ils ? non

## 6. Ce qui reste flou

Tout est clair.
