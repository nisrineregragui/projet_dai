"""Suivi des entraînements avec MLflow : chaque entraînement devient un « run » qu'on peut comparer.

Les runs sont enregistrés dans mlflow.db (dossier courant) ; on les regarde avec : mlflow ui
"""
import hashlib
import os
from pathlib import Path

os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")  # coupe un message d'information de MLflow

import mlflow
import mlflow.sklearn

EXPERIMENT = "maintai"
TRUSTED_TYPES = ["sklearn.tree._tree.Tree"]  # nécessaire pour --model forest


def file_md5(path: Path) -> str:
    """Empreinte du fichier de données : la même que celle que DVC écrit dans le fichier .dvc."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


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