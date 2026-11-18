Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

Groupe : G22 · Membres : ARRAS Wissal · Date : 17/11/2026 · Heure : 20:30

1. Mise en place (dans TP/TP5)

Dernière ligne de python -m pytest après pip install -r requirements.txt et pip install -e . :

================== 5 failed, 27 passed, 2 warnings in 26.81s ===================

Quels tests échouent, et pourquoi ?

Les 5 tests de tests/test_tracking.py :

test_training_creates_a_run
test_run_records_metrics
test_run_records_data_version
test_run_stores_the_model
test_options_change_the_run

Ils échouent parce que log_run n'est pas encore écrite : elle renvoie "" sans rien enregistrer, donc aucun run MLflow n'existe (message des tests : « aucun run MLflow : log_run n'a rien enregistré »). Les 27 autres tests (API, CLI, client, données, package, sécurité, entraînement, UI) viennent du TP4 et passent toujours.

Avant pip install -e ., où pointait le package maintai installé dans l'environnement ? Et après ?

Avec l'environnement du TP4, maintai pointait vers le dossier TP4 (installation éditable du TP4) : Python aurait exécuté le code du TP4 en croyant lancer celui du TP5. J'ai utilisé un environnement .venv propre au TP5, dans lequel il fallait de toute façon installer le package. Après pip install -e ., il pointe vers le TP5 :

 ~ maintai==0.3.0 (from file:///C:/Users/user/Downloads/TP5/TP5)
2. Sprint 1 : MLflow

Votre fonction log_run (maintai/tracking.py) :

python
def log_run(params: dict, metrics: dict, model, X_example, data_path: Path) -> str:
    """Enregistre un entraînement : paramètres, version des données, métriques et modèle. Renvoie l'id du run."""
    mlflow.set_experiment(EXPERIMENT)
    with mlflow.start_run() as run:
        mlflow.log_params(params)
        mlflow.log_param("data_md5", file_md5(data_path))
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(
            model,
            name="model",
            input_example=X_example,
            skops_trusted_types=TRUSTED_TYPES,
        )
    return run.info.run_id

Dernière ligne de python -m pytest à la fin du sprint 1 :

======================= 32 passed, 4 warnings in 30.83s ========================

Vos runs (au moins quatre), relevés dans mlflow ui (mode « Model training ») :

Commande	recall	precision	accuracy	Run ID
python -m maintai.train	0.750	0.622	0.904	b18f8babfc1d42a78ed63f789850b52b
python -m maintai.train --C 0.01	0.691	0.653	0.908	fb93329215a2404a93680a7cc3ec1dfe
python -m maintai.train --threshold 0.2	0.838	0.543	0.882	ba091eac7a6a4d2880e1830ae23202ce
python -m maintai.train --model forest	0.728	0.562	0.886	ade14e7e0a784026b2fa4e4910fd785c
Référence : baseline « jamais de panne »	0.000	–	0.864	–

Quel run choisiriez-vous pour MaintAI, et pourquoi ?

Le run --threshold 0.2 (ba091eac…). Une panne manquée coûte plus cher qu'une fausse alerte, donc le critère principal est le recall : ce run détecte environ 84 % des pannes réelles, contre 75 % pour le réglage par défaut. En échange, la precision baisse à 0.543 (un peu moins d'une alerte sur deux est fausse) et l'accuracy passe de 0.904 à 0.882, ce qui est acceptable vu la contrainte.

--C 0.01 : plus de régularisation, la precision monte légèrement mais le recall est le plus bas, à l'opposé de ce qu'on cherche.
La forêt aléatoire n'est pas meilleure : au même seuil (0.3), elle a un recall (0.728) et une precision (0.562) inférieurs à la régression logistique, pour un modèle plus lourd et moins interprétable.
L'accuracy n'est pas un bon critère ici : la baseline qui ne prédit jamais de panne obtient déjà 0.864, avec un recall nul.

Dans mlflow ui, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son requirements.txt ? Quel problème du TP4 cela règle-t-il ?

scikit-learn==1.8.0. Au TP4, on ne livrait que model.joblib : ce fichier ne se recharge correctement qu'avec la même version de scikit-learn que celle de l'entraînement, et rien n'enregistrait cette version. Maintenant, MLflow range à côté de chaque modèle un requirements.txt (ainsi que conda.yaml et python_env.yaml) avec les versions exactes : on sait toujours dans quel environnement recharger le modèle.

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

Dans mlflow.db (base SQLite : expériences, runs, paramètres, métriques) et dans le dossier mlruns/ (les artefacts, dont les modèles). Ils ne vont pas dans Git : ce sont des fichiers générés, souvent binaires et lourds (un modèle par run), qui changent à chaque entraînement et sont propres à chaque machine. Le .gitignore les exclut. Git garde le code qui produit les runs ; pour partager les runs eux-mêmes, on utiliserait un serveur MLflow commun.

3. Sprint 2 : DVC

Contenu de data/sensors.csv.dvc après dvc add data/sensors.csv :

outs:
- md5: 73e0b7cb3c6f795c70c3ddf970b99c15
  size: 126815
  hash: md5
  path: sensors.csv

Comparez la valeur md5 de ce fichier au paramètre data_md5 de votre dernier run MLflow. Que constatez-vous ?

Les deux valeurs sont identiques : file_md5 calcule la même empreinte que DVC. C'est ce qui relie les deux outils : à partir d'un run MLflow, le data_md5 désigne exactement la version des données suivie par DVC, et donc le commit Git dont le reçu porte ce md5.

Pourquoi data/sensors.csv ne va pas dans Git, alors que data/sensors.csv.dvc y va ?

sensors.csv est un fichier de données qui peut devenir très lourd. Git le gère mal et garderait chaque version pour toujours dans l'historique, ce qui gonflerait le dépôt (et un diff ligne à ligne n'a pas de sens pour des données). DVC stocke le fichier dans son cache puis dans le stockage, et ne met dans Git qu'un reçu de quelques lignes (md5 et taille). Ce reçu suffit pour retrouver la bonne version avec dvc checkout ou dvc pull. dvc add écrit aussi data/.gitignore pour que Git ignore le CSV.

Après python -m maintai.dataset --n 8000 --seed 7, que dit dvc status ?

data/sensors.csv.dvc:
        changed outs:
                modified:           data/sensors.csv

DVC voit que le fichier ne correspond plus au md5 du reçu : il faut faire dvc add pour enregistrer la nouvelle version.

Version	Commit Git (git log --oneline)	md5 (8 premiers caractères)	Nombre de lignes
v1	6d73365	73e0b7cb	5000
v2	142131a	93fdeef2	8000

Revenez à la v1 (git checkout <commit> -- data/sensors.csv.dvc, puis dvc checkout). Combien de lignes contient data/sensors.csv ? Puis revenez à la v2.

Sur la v1, le fichier contient 5000 lignes. Après git checkout HEAD -- data/sensors.csv.dvc et dvc checkout, on retrouve 8000 lignes :

Building workspace index                        |2.00 [00:00,  175entry/s]
Comparing indexes                              |3.00 [00:00, 1.15kentry/s]
Applying changes                                |1.00 [00:00,   203file/s]
M       data\sensors.csv
8000

git checkout ne change que le reçu ; c'est dvc checkout qui remplace le fichier par la version du cache correspondant au md5 du reçu.

Supprimez data/sensors.csv et le dossier .dvc/cache, puis lancez dvc pull. Que se passe-t-il ?

Collecting                                      |1.00 [00:00,  182entry/s]
Fetching
Building workspace index                        |1.00 [00:00, 77.1entry/s]
Comparing indexes                              |3.00 [00:00, 1.38kentry/s]
Applying changes                                |1.00 [00:00,  51.2file/s]
A       data\sensors.csv
1 file fetched and 1 file added
8000

DVC lit le md5 dans data/sensors.csv.dvc, ne le trouve pas dans le cache local (supprimé), télécharge le fichier depuis le stockage (dvc-stockage) dans le cache, puis recrée data/sensors.csv : on retrouve les 8000 lignes de la v2. C'est exactement ce que fait un coéquipier qui clone le dépôt : git pull lui apporte le reçu, dvc pull lui apporte les données.

4. Relier modèle et données

Entraînez un modèle sur la v2. Dans mlflow ui, comparez ce run à celui de la v1 avec les mêmes réglages :

Run	data_md5 (8 caractères)	n_train	recall	precision
v1 (b18f8bab…)	73e0b7cb	4000	0.750	0.622
v2 (92d721a2…)	93fdeef2	6400	0.741	0.650

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

Non. Le recall baisse légèrement (0.750 → 0.741) et la precision monte (0.622 → 0.650) : aucun des deux n'est clairement meilleur, et surtout la comparaison n'est pas valable. Les deux modèles ne sont pas évalués sur le même jeu de test : 1000 lignes tirées de la v1 d'un côté, 1600 lignes de la v2 (générée avec une autre graine) de l'autre. Les métriques mesurent donc deux « examens » différents, qui peuvent ne pas avoir la même proportion de pannes ni la même difficulté. Un écart de quelques centièmes peut venir du jeu de test plutôt que du modèle. Pour comparer honnêtement, il faudrait évaluer les deux modèles sur un même jeu de test fixe, ou faire une validation croisée. C'est justement pour ça que le data_md5 est enregistré dans chaque run : on ne compare que des runs qui ont le même.

5. Décision : l'ADR 004

Voir docs/adr/004-choix-du-modele.md : régression logistique, C = 1.0, seuil 0.2, run ba091eac7a6a4d2880e1830ae23202ce, data_md5 = 73e0b7cb3c6f795c70c3ddf970b99c15 (données v1).

6. Questions de compréhension

Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?

Git versionne le code source et les petits fichiers texte, dont les reçus .dvc.
DVC versionne les fichiers de données : il les garde hors de Git (cache local et stockage partagé) et les identifie par leur md5.
MLflow garde la trace de chaque entraînement : paramètres, data_md5, métriques, modèle et versions exactes des bibliothèques.

Ensemble, ils couvrent les trois choses qui changent en MLOps : le code, les données et le modèle.

Pourquoi le stockage DVC est-il ajouté avec --local dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?

Le stockage est un dossier de mon PC (%USERPROFILE%\dvc-stockage) : ce chemin n'existe que chez moi. Avec --local, il est écrit dans .dvc/config.local, ignoré par Git, donc il n'est pas imposé aux autres membres. Pour partager les données, il faudrait un stockage accessible à tous (S3, Google Drive, Azure, un serveur SSH…), ajouté sans --local pour qu'il soit écrit dans .dvc/config et commité. Chacun ferait alors git pull puis dvc pull, avec ses propres identifiants.

Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?

Le code : dans Git (et dans le wheel du TP4).
Le modèle entraîné : dans MLflow, comme artefact d'un run identifié par son Run ID (dans mlruns/).
Les versions exactes des bibliothèques : dans MLflow, avec le requirements.txt enregistré à côté du modèle.

Le TP5 ajoute une quatrième pièce : les données, versionnées par DVC (le reçu dans Git, le fichier dans le stockage), et reliées au run par data_md5.

7. Le rendu Git
Lien de la pull request : ⟨à compléter après le push⟩
Le tag tp5 existe sur GitHub : ⟨oui / non⟩
git status avant le commit : mlflow.db, mlruns/, data/sensors.csv ou .dvc/cache apparaissaient-ils ? Non : le .gitignore exclut mlflow.db, mlruns/, .dvc/cache et .dvc/config.local, et data/.gitignore (créé par dvc add) exclut data/sensors.csv.
8. Ce qui reste flou

Rien de bloquant.