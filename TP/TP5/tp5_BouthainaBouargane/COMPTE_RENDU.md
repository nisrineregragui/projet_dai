# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :** G2 ·  **Membres :** Bouthaina bouargane  ·  **Date :** …

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP5.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```
=========== 5 failed, 27 passed, 2 warnings in 66.50s (0:01:06) ============
```

Quels tests échouent, et pourquoi ?

Les 5 tests de `tests/test_tracking.py` échouent :
- `test_training_creates_a_run`
- `test_run_records_metrics`
- `test_run_records_data_version`
- `test_run_stores_the_model`
- `test_options_change_the_run`

Ils échouent tous pour la même raison : la fonction `log_run` de `maintai/tracking.py` n'est pas encore écrite (TODO du sprint 1). Elle renvoie `""` sans rien enregistrer dans MLflow. Les tests cherchent le dernier run de l'expérience `maintai` et n'en trouvent aucun : « aucun run MLflow : log_run n'a rien enregistré ». On le voit aussi à la fin de l'entraînement : la ligne « Run MLflow : » n'a pas d'identifiant. Les 27 autres tests portent sur le code du TP4 et passent.

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

L'environnement utilisé n'est pas celui du TP4, mais un `.venv` propre au TP5 (`TP5\TP5\.venv`).

**Avant :** avec l'environnement du TP4 comme le prévoit le polycopié, `maintai` aurait pointé vers le dossier `TP/TP4`, où il avait été installé en mode éditable. Dans notre `.venv`, `maintai` pointait déjà vers le TP5 : lancé depuis un autre dossier, `python -c "import maintai; print(maintai.__file__)"` affiche `...\TP5\TP5\maintai\__init__.py`.

Le premier `pip install -e .` n'a pas modifié l'environnement. Le `.venv` n'avait pas de pip, donc la commande `pip` était celle du Python global (3.14). Elle a été relancée dans l'environnement avec `python -m ensurepip --upgrade` puis `python -m pip install -e .`.

**Après :** `maintai` est installé en mode éditable dans l'environnement (« Building editable for maintai ») et pointe vers `TP5\TP5`. `import maintai` charge le code du TP5, et chaque modification du code est prise en compte sans réinstaller le package.

## 2. Sprint 1 : MLflow

Votre fonction `log_run` (`maintai/tracking.py`) :

```python
def log_run(params: dict, metrics: dict, model, X_example, data_path: Path) -> str:
    """Enregistre un entraînement : paramètres, version des données, métriques et modèle. Renvoie l'id du run."""
    # Range le run dans l'expérience "maintai" (MLflow la crée si elle n'existe pas)
    mlflow.set_experiment(EXPERIMENT)

    # Ouvre un run : tout ce qui est enregistré dans ce bloc appartient à cet entraînement
    with mlflow.start_run() as run:
        # Les réglages de l'entraînement : model, C, threshold, n_train
        mlflow.log_params(params)

        # L'empreinte md5 du fichier de données : elle dit sur quelles données le modèle a été entraîné
        mlflow.log_param("data_md5", file_md5(data_path))

        # Les résultats : recall, precision, accuracy, baseline_recall
        mlflow.log_metrics(metrics)

        # Le modèle lui-même, avec un exemple d'entrée et les versions exactes des bibliothèques
        # skops_trusted_types autorise l'arbre de décision, nécessaire pour --model forest
        mlflow.sklearn.log_model(model, name="model", input_example=X_example,
                                 skops_trusted_types=TRUSTED_TYPES)

    # Renvoie l'identifiant du run, affiché à la fin par "Run MLflow : ..."
    return run.info.run_id
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
===================== 32 passed, 4 warnings in 37.42s ======================
```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training ») :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` | 0.75 | 0.622 | 0.904 |
| `python -m maintai.train --C 0.01` | 0.691 | 0.653 | 0.908 |
| `python -m maintai.train --threshold 0.2` | 0.838 | 0.543 | 0.882 |
| `python -m maintai.train --model forest` | 0.728 | 0.562 | 0.886 |
| `python -m maintai.train --model forest --threshold 0.2` | 0.831 | 0.479 | 0.854 |


Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)

Nous choisissons la régression logistique avec le seuil 0.2 (`--threshold 0.2`, run `26c9249a4f684945b61f8c986d6da1ea`). C'est le run qui a le meilleur recall (0.838) : il détecte environ 84 % des pannes, contre 75 % avec le seuil par défaut 0.3. En échange, la precision baisse à 0.543 : près d'une alerte sur deux est une fausse alerte. Nous l'acceptons, car une panne manquée coûte plus cher qu'une fausse alerte.

La forêt aléatoire n'est pas meilleure. Au seuil 0.3, elle a un recall plus faible (0.728 contre 0.75) et une precision plus faible (0.562 contre 0.622). Au seuil 0.2, son recall est presque le même (0.831 contre 0.838), mais sa precision est nettement plus basse (0.479 contre 0.543), et son accuracy (0.854) passe même sous celle de la baseline (0.864). Elle est aussi plus lourde, pour aucun gain.


Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

Le `requirements.txt` du modèle indique `scikit-learn==1.8.0`, la même version que celle installée dans l'environnement. Ici, MLflow a détecté un projet uv et a repris les versions du fichier `uv.lock`.

Au TP4, le modèle était sauvegardé seul avec joblib, et la version de scikit-learn n'était notée qu'à titre d'information dans `model_info.json`. Rien ne garantissait qu'on recharge le modèle avec la même version, alors qu'un modèle joblib peut refuser de se charger ou changer de comportement avec une autre version. MLflow enregistre avec chaque modèle les versions exactes des bibliothèques : on peut recréer le même environnement pour le recharger.


Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

MLflow enregistre les runs dans le dossier d'où on lance l'entraînement (`TP5\TP5`). La base `mlflow.db` (SQLite) garde les paramètres et les métriques de chaque run. Le dossier `mlruns/` garde les artefacts, dont le modèle de chaque run.

Ces fichiers ne vont pas dans Git : le `.gitignore` exclut `mlflow.db` et `mlruns/`. Ils sont binaires et lourds (un modèle par run) et propres à chaque PC, alors que Git est fait pour le code. Un run se retrouve par son identifiant, et on peut le refaire à partir du code et des données.

## 3. Sprint 2 : DVC

Contenu de `data/sensors.csv.dvc` après `dvc add data/sensors.csv` :

```
outs:
- md5: 73e0b7cb3c6f795c70c3ddf970b99c15
  size: 126815
  hash: md5
  path: sensors.csv
```

Comparez la valeur `md5` de ce fichier au paramètre `data_md5` de votre dernier run MLflow. Que constatez-vous ?

Les deux valeurs sont identiques (`73e0b7cb`). Le `data_md5` enregistré par MLflow est la même empreinte que celle que DVC écrit dans le reçu. À partir d'un run, on sait donc exactement sur quelle version des données le modèle a été entraîné, et on peut retrouver cette version avec DVC.


Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

`data/sensors.csv` est un fichier de données qui peut devenir lourd. Git le gère mal et garderait chaque version pour toujours. DVC le garde hors de Git, dans son cache puis dans le stockage. Dans Git, on ne met que le reçu `data/sensors.csv.dvc` : quelques lignes avec le md5 et la taille du fichier. Ce reçu suffit pour retrouver la bonne version avec `dvc checkout` ou `dvc pull`. D'ailleurs, le `.gitignore` exclut `data/*.csv`.


Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data\sensors.csv.dvc:
        changed outs:
                modified:           data\sensors.csv
```

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 | `0e2c1ae` | `73e0b7cb` | 5000 |
| v2 | `180c458` | `93fdeef2` | 8000 |

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

Après `git checkout 0e2c1ae -- data/sensors.csv.dvc`, puis `dvc checkout` (qui affiche `M data\sensors.csv`), `data/sensors.csv` contient 5000 lignes : c'est bien la v1. Git a remis l'ancien reçu, et DVC a remis le fichier qui lui correspond, depuis son cache, sans rien télécharger. On revient ensuite à la v2 avec `git checkout HEAD -- data/sensors.csv.dvc`, puis `dvc checkout` : le fichier contient de nouveau 8000 lignes.

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

`dvc pull` affiche `A data\sensors.csv` puis `1 file fetched and 1 file added`. DVC lit le reçu `data/sensors.csv.dvc` dans Git (md5 de la v2), télécharge le fichier qui correspond depuis le stockage (`dvc-stockage`) vers son cache (« fetched »), puis le remet dans `data/` (« added »). Le fichier contient de nouveau 8000 lignes. C'est ce que vit un coéquipier qui récupère le dépôt sans les données : avec le reçu dans Git et l'accès au stockage, il retrouve exactement la même version.

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 (`e567844c`) | `73e0b7cb` | 4000 | 0.75 | 0.622 |
| v2 (`d53edf9b`) | `93fdeef2` | 6400 | 0.741 | 0.65 |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

Non. Avec les mêmes réglages (régression logistique, C = 1.0, seuil 0.3), le run v2 a un recall un peu plus faible (0.741 contre 0.75) et une precision un peu plus élevée (0.65 contre 0.622). Aucun des deux ne gagne sur les deux métriques.

Surtout, ces chiffres ne sont pas comparables. Chaque run est évalué sur le jeu de test de ses propres données : 1000 lignes de la v1 d'un côté, 1600 lignes de la v2 de l'autre. Les deux versions sont générées avec des graines différentes et n'ont pas le même taux de panne (13,6 % contre 12,8 %), comme le montre aussi la baseline (accuracy 0.864 contre 0.872). Un écart de métrique peut donc venir des données de test, et non du modèle. Pour dire qu'un modèle est meilleur, il faut les évaluer tous les deux sur le même jeu de test. C'est pour ça que le run enregistre `data_md5` : il dit sur quelles données chaque chiffre a été obtenu.

## 5. Décision : l'ADR 004

Dans `docs/adr/004-choix-du-modele.md` : le modèle et le seuil retenus, à partir de votre tableau MLflow. Indiquez l'identifiant du run et le `data_md5` de la version des données utilisée.

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   
Git versionne le code et les petits fichiers texte, dont les reçus `.dvc` de quelques lignes. DVC versionne les fichiers de données : il les garde hors de Git, dans son cache puis dans le stockage, et les retrouve grâce à leur md5. MLflow garde la trace de chaque entraînement : ses paramètres, le `data_md5` des données, ses métriques et le modèle avec les versions exactes de ses bibliothèques. Les trois sont reliés : le `data_md5` d'un run MLflow est le même que le md5 du reçu DVC, et ce reçu est dans un commit Git.


2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?

Le stockage est ici un dossier de mon PC (`%USERPROFILE%\dvc-stockage`). Ce chemin n'existe que chez moi : avec `--local`, il est écrit dans `.dvc/config.local`, que Git ignore, et ne gêne donc pas les autres membres. Pour partager les mêmes données, il faudrait un stockage accessible à tout le groupe (S3, Google Drive, un serveur), ajouté sans `--local` pour que sa configuration aille dans Git. Chacun pourrait alors faire `dvc push` et `dvc pull` vers le même endroit.


3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?

D'après le tableau « Livrer un modèle » du polycopié, ce sont le code, le modèle et les versions exactes des bibliothèques. Le code est dans Git. Le modèle est dans MLflow : un run, retrouvé par son identifiant. Les versions exactes sont dans le `requirements.txt` du modèle, enregistré par MLflow. Le TP5 y ajoute les données : le reçu est dans Git, le fichier dans le stockage DVC.

## 7. Le rendu Git

- Lien de la pull request : pas de pull request, les fichiers ont été poussés directement sur `master` (commit `0a8054f`) : https://github.com/nisrineregragui/projet_dai/tree/master/TP/TP5/tp5_BouthainaBouargane
- Le tag `tp5` existe sur GitHub : oui
- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ? non : le `.gitignore` les exclut, et `git status` ne listait que le code, le compte rendu, l'ADR et les fichiers de configuration.

## 8. Ce qui reste flou

- Le lien entre DVC et Git quand le TP n'est pas à la racine du dépôt : je n'ai pas bien compris dans quels cas il faut `dvc init --subdir` plutôt que `dvc init`.
- MLflow a repris les versions du fichier `uv.lock` au lieu de celles de l'environnement : je ne sais pas encore laquelle des deux sources est la plus fiable pour livrer un modèle.
- Comment comparer proprement deux modèles entraînés sur des versions différentes des données, avec un même jeu de test.

