# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :** …  ·  **Membres :** …  ·  **Date :** 17/11/2026  17:34

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP5.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```

===================== 5 failed, 27 passed, 2 warnings in 32.72s =====================
```

Quels tests échouent, et pourquoi ?

…

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

…

## 2. Sprint 1 : MLflow

Votre fonction `log_run` (`maintai/tracking.py`) :

def log_run(params: dict, metrics: dict, model, X_example, data_path: Path) -> str:
    """Enregistre un entraînement dans MLflow."""

    mlflow.set_experiment(EXPERIMENT)

    with mlflow.start_run() as run:
        mlflow.log_params(params)
        mlflow.log_param("data_md5", file_md5(data_path))
        mlflow.log_metrics(metrics)

        mlflow.sklearn.log_model(
            model,
            name="model",
            input_example=X_example,
            skops_trusted_types=TRUSTED_TYPES
        )

        return run.info.run_id

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
============== 32 passed, 4 warnings in 52.15s ========
```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training ») :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` |0.75 |0.622 |0.904 |
| `python -m maintai.train --C 0.01` | 0.691|0.653 | 0.908|
| `python -m maintai.train --threshold 0.2` |0.838 | 0.543| 0.882|
| `python -m maintai.train --model forest` | 0.728| 0.562|0.886|
| (votre essai) | | | |

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)


Je choisis le modèle avec threshold = 0.2 car il possède
le meilleur recall (0.838).

Dans MaintAI, manquer une panne coûte plus cher que
déclencher une fausse alerte. Il faut donc privilégier
le recall plutôt que la précision.

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?
1.8.0

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

MLflow enregistre les runs dans le fichier `mlflow.db` et les artefacts des modèles dans le dossier `mlartifacts/` (ou `mlruns/` selon la configuration), dans le répertoire du projet.

Ces fichiers ne vont pas dans Git, car ils peuvent être volumineux et sont générés automatiquement. Ils sont exclus grâce au fichier `.gitignore`.

Git sert à versionner le code, tandis que MLflow sert à suivre les entraînements, leurs paramètres, leurs métriques et leurs modèles.

## 3. Sprint 2 : DVC

Contenu de `data/sensors.csv.dvc` après `dvc add data/sensors.csv` :

outs:
- md5: 73e0b7cb3c6f795c70c3ddf970b99c15
  size: 126815
  hash: md5
  path: sensors.csv

Comparez la valeur `md5` de ce fichier au paramètre `data_md5` de votre dernier run MLflow. Que constatez-vous ?
Les deux valeurs MD5 doivent être identiques : 73e0b7cb3c6f795c70c3ddf970b99c15.
Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

le fichier data/sensors.csv contient les données qui peuvent être volumineuses, donc DVC les gère à la place de Git.

Le fichier data/sensors.csv.dvc est léger et contient le MD5 et la taille des données. Il va dans Git pour permettre de suivre les versions et retrouver les données correspondantes.

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?
(TP5) PS C:\Users\nisri\Downloads\TP5\TP5> dvc status
data\sensors.csv.dvc:                                                          
        changed outs:
                modified:           data\sensors.csv
(TP5) PS C:\Users\nisri\Downloads\TP5\TP5> 

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 |	01ba5c5 | 73e0b7cb|	5000 |
| v2 |a8bb41f |93fdeef2 | 8000|

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

…

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

Après avoir restauré le fichier .dvc de la v2, dvc pull permet de récupérer les 8000 lignes depuis le stockage DVC.

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 |73e0b7cb |4000 |0.750 |0.622 |
| v2 | 93fdeef2| 6400|0.741 |0.650 |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

entraînés sur des données différentes ?
Non, le modèle v2 n’est pas forcément meilleur. Sa précision augmente (0.650 contre 0.622), mais son recall diminue légèrement (0.741 contre 0.750).

Il faut être prudent, car les deux modèles ont été entraînés et testés sur des données différentes. Pour les comparer correctement, il faudrait les évaluer sur le même jeu de test.
## 5. Décision : l'ADR 004

Dans `docs/adr/004-choix-du-modele.md` : le modèle et le seuil retenus, à partir de votre tableau MLflow. Indiquez l'identifiant du run et le `data_md5` de la version des données utilisée.

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   Git versionne le code source et les fichiers de configuration.

DVC versionne les données en conservant leur MD5 dans Git et les fichiers dans un stockage séparé.

MLflow suit les entraînements, les paramètres, les métriques et les modèles entraînés.
2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
   On utilise --local car le stockage se trouve sur notre PC et son chemin ne doit pas être partagé dans Git.

Pour que tout le groupe accède aux mêmes données, il faudrait utiliser un stockage commun, comme Google Drive, S3 ou un serveur partagé.
3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
   …

## 7. Le rendu Git

- Lien de la pull request : …
- Le tag `tp5` existe sur GitHub : oui / non
- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ? oui / non

## 8. Ce qui reste flou

…
