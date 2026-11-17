# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :** G2 · **Membres :** TAFRHY Adam · **Date :** 17/11/2026 **Heure :**18:07

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP5.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```
========================================= 5 failed, 27 passed, 2 warnings in 33.69s =========================================
```

Quels tests échouent, et pourquoi ?

les tests qui echouent sont:

- test_training_creates_a_run
- test_run_records_metrics
- test_run_records_data_version
- test_run_stores_the_model
- test_options_change_the_run
  Ils echouent car nous avons pas implemente la fonction log_run() donc aucun run mlflow n'est encore enregistre

  Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

le package avant le pip install pointait sur le TP4 et apres il pointe vers le TP5

## 2. Sprint 1 : MLflow

Votre fonction `log_run` (`maintai/tracking.py`) :

```python
def log_run(params: dict, metrics: dict, model, X_example, data_path: Path) -> str:
    """Enregistre un entraînement : paramètres, version des données, métriques et modèle. Renvoie l'id du run."""
    # TODO TP5 sprint 1 : enregistrer le run dans MLflow
    #   1. choisir l'expérience : mlflow.set_experiment(EXPERIMENT)
    #   2. ouvrir un run :        with mlflow.start_run() as run:
    #   3. dans le with :
    #        - les paramètres :   mlflow.log_params(params)
    #        - la version des données : un paramètre "data_md5", calculé par file_md5(data_path)
    #        - les métriques :    mlflow.log_metrics(metrics)
    #        - le modèle :        mlflow.sklearn.log_model(model, name="model", input_example=X_example,
    #                                                      skops_trusted_types=TRUSTED_TYPES)
    #   4. renvoyer l'identifiant : run.info.run_id
    # 1. Sélectionner (ou créer si elle n'existe pas) l'expérience cible dans MLflow
    mlflow.set_experiment(EXPERIMENT)

    # 2. Ouvrir un run : tout ce qui est enregistré dans ce bloc lui est rattaché
    with mlflow.start_run() as run:
        # 3a. Enregistrer les hyperparamètres du modèle
        mlflow.log_params(params)

        # 3b. Enregistrer l'empreinte MD5 des données pour assurer la traçabilité avec DVC
        mlflow.log_param("data_md5", file_md5(data_path))

        # 3c. Enregistrer les métriques de performance
        mlflow.log_metrics(metrics)

        # 3d. Sauvegarder le modèle avec un exemple d'entrée et les types de confiance skops
        mlflow.sklearn.log_model(
            model,
            name="model",
            input_example=X_example,
            skops_trusted_types=TRUSTED_TYPES,
        )

    # 4. Renvoyer l'identifiant unique du run une fois celui-ci clôturé
    return run.info.run_id

```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
============================================== 32 passed, 4 warnings in 11.74s ==============================================
```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training ») :

| Commande                                                 | recall | precision | accuracy |
| -------------------------------------------------------- | ------ | --------- | -------- |
| `python -m maintai.train`                                | 0.75   | 0.622     | 0.904    |
| `python -m maintai.train --C 0.01`                       | 0.691  | 0.653     | 0.908    |
| `python -m maintai.train --threshold 0.2`                | 0.838  | 0.543     | 0.882    |
| `python -m maintai.train --model forest`                 | 0.728  | 0.562     | 0.886    |
| `python -m maintai.train --model forest --threshold 0.2` | 0.831  | 0.479     | 0.854    |

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)

pour maintai je choisirai python -m maintai.train --threshold 0.2 car avec un seuil bas on assure plus de fausses alertes que de pannes manquees. Elle obtient egalement le meilleur recall ce qui signifie qu'elle detecte le plus de pannes reelles.

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

la version de scikit learn indiquee est 1.8.0. Le probleme du Tp4 etait que seulement le fichier joblib du modele etait stocke sans les versions comme celle de sklearn qui sont indiquees maintenant dans mlflow.

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

mlflow enregistre les runs dans mlflow.db et dnas le dossier mlruns. Ces fichiers ne vont pas dans Git car il concerne que le versionnement du code tandis que mlflow concerne le versionnement ml.

## 3. Sprint 2 : DVC

Contenu de `data/sensors.csv.dvc` après `dvc add data/sensors.csv` :

```
outs:
- md5: b7fec4274774842dc1f48202c6013490
  size: 121814
  hash: md5
  path: sensors.csv

```

Comparez la valeur `md5` de ce fichier au paramètre `data_md5` de votre dernier run MLflow. Que constatez-vous ?

les deux valeurs sont identiques car ce sont les memes versions de donnees.

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

le fichier dvc sert a garder une tracabilite des versions des donnees c'est donc pour cela que nous le mettons sur Git.

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data/sensors.csv.dvc:
        changed outs:
                modified:           data/sensors.csv
```

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
| ------- | -------------------------------- | --------------------------- | ---------------- |
| v1      | ec899a9                          | b7fec427                    | 5000             |
| v2      | 299792e                          | 31ef5ebb                    | 8000             |

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

dans la v1 il contient 5000 lignes et quand nous revenons a la v2 nous avons 8000 lignes.

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

dvc lit dans le fichier sensors.csv.dvc et lit le md5 qu'il contient puis pull la version du fichier csv correspondante dans le remote

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
| --- | ----------------------- | ------- | ------ | --------- |
| v1  | b7fec427                | 4000    | 0.75   | 0.622     |
| v2  | 31ef5ebb                | 6400    | 0.741  | 0.65      |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

On ne peut pas dire que le modele v2 est meilleur ou comparer les deux runs car les donnees de test sont differentes

## 5. Décision : l'ADR 004

Dans `docs/adr/004-choix-du-modele.md` : le modèle et le seuil retenus, à partir de votre tableau MLflow. Indiquez l'identifiant du run et le `data_md5` de la version des données utilisée.

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   git versionne le code source et les petits fichiers recus .dvc, dvc versionne les gros fichiers de donnees via leur empreinte md5, et mlflow trace les entrainements en enregistrant les parametres, les metriques et les modeles avec leurs dependances.
2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
   l'option --local ecrit le chemin dans .dvc/config.local (ignore par git) car le dossier de stockage est personnel a chaque machine ; pour partager les donnees dans le groupe, il faudrait configurer un stockage distant commun sans --local pour versionner sa configuration dans git et permettre a chacun de faire dvc pull.
3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
   livrer un modele demande le code source (versionne dans git), le fichier du modele entraine (stocke dans les artefacts mlflow sous mlruns/) et la liste exacte des dependances logicielles (le fichier requirements.txt genere automatiquement par mlflow avec le modele).

## 7. Le rendu Git

- Lien de la pull request : https://github.com/nisrineregragui/projet_dai/tree/master
- Le tag `tp5` existe sur GitHub : non
- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ? non

## 8. Ce qui reste flou

Tout est clair.

## 9. Expérimentation complémentaire : Grid Search

Pour explorer plus finement les hyperparamètres de la régression logistique, nous avons ajouté un script dédié `maintai/grid_search.py` testant **25 combinaisons** (5 valeurs de régularisation `C` : `0.01, 0.1, 1.0, 10.0, 100.0` × 5 seuils de décision `threshold` : `0.15, 0.20, 0.25, 0.30, 0.35`), toutes enregistrées automatiquement dans MLflow.

Top 5 des runs obtenus avec `python -m maintai.grid_search` (triés par `recall`) :

| Run Name               | C     | threshold | recall | precision | accuracy |
| ---------------------- | ----- | --------- | ------ | --------- | -------- |
| `casual-bear-838`      | 0.01  | 0.15      | 0.919  | 0.455     | 0.839    |
| `persistent-shoat-128` | 0.1   | 0.15      | 0.897  | 0.496     | 0.862    |
| `gifted-quail-317`     | 100.0 | 0.15      | 0.875  | 0.500     | 0.864    |
| `thoughtful-rook-880`  | 10.0  | 0.15      | 0.875  | 0.500     | 0.864    |
| `bemused-sow-852`      | 1.0   | 0.15      | 0.875  | 0.500     | 0.864    |

**Analyse des résultats :**

- **Meilleur rappel :** le run `casual-bear-838` (`C = 0.01`, `threshold = 0.15`) atteint un `recall` de **0.919** (près de 92 % des pannes détectées), mais au prix d'une précision qui chute à `0.455` (plus de la moitié des alertes sont de fausses alertes).
- **Compromis intéressant :** `persistent-shoat-128` (`C = 0.1`, `threshold = 0.15`) conserve un rappel très élevé (`0.897`) tout en limitant mieux les fausses alertes (`precision = 0.496`, `accuracy = 0.862`).
- **Effet de `C` :** à partir de `C >= 1.0` (`1.0`, `10.0`, `100.0`), la régularisation devient trop faible pour modifier les poids du modèle et les métriques plafonnent exactement aux mêmes valeurs (`recall = 0.875`, `precision = 0.500`).
