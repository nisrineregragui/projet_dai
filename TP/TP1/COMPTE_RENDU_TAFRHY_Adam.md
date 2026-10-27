# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** G2 · **Membres :** Adam TAFRHY · **Date :** 27/10/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP1.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place (rien n'est encore écrit) :

```
==================================================================== 3 failed, 10 passed, 1 warning in 0.78s ====================================================================
```

Dans `tests/test_api.py`, 4 tests sur 7 passent déjà alors que rien n'est écrit. Lesquels ? Pour les deux tests qui attendent un code 422, expliquez pourquoi ils passent « pour une mauvaise raison » (indice : regardez `extra="forbid"` dans `schemas.py`).

les 4 tests qui passent deja sont test_health, test_out_of_range_value_is_rejected, test_missing_field_is_rejected et test_openapi_documents_predict.

les deux tests qui attendent un code 422 passent pour une mauvaise raison. au debut, le schema ne declare aucun champ mais extra="forbid" refuse tous les champs envoyes. meme un releve normal est donc refuse comme s'il contenait des champs inconnus. le resultat 422 est bon, mais pas la cause du refus.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable         | Type  | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min / max des données)                                                                                      |
| ---------------- | ----- | -------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `temperature_c`  | float | -40            | 150            | un capteur peut mesurer une temperature negative en exterieur, mais une temperature au dessus de 150 c est peu credible pour l'equipement. |
| `vibration_mm_s` | float | 0              | 10             | une vibration ne peut pas etre negative et au dela de 10 mm le niveau est deja tres anormal pour ce type de machine.                       |
| `load_pct`       | float | 0              | 100            | la charge est exprimee en pourcentage donc elle ne peut pas sortir de 0 a 100.                                                             |
| `runtime_hours`  | float | 0              | 100000         | un compteur d'heures ne peut pas etre negatif, 100000 h laisse une marge importante pour une machine ancienne.                             |

Après avoir écrit `schemas.py` seul, que donne `python -m pytest`, et quel est le message d'erreur des tests qui échouent ? Pourquoi est-ce un bon signe ?

```
2 failed, 11 passed in 1.43s
```

les deux echecs concernent seulement la route de prediction : une requete valide recoit 503 au lieu de 200, puis le test ne trouve pas la cle alert. c'est un bon signe car les donnees sont maintenant acceptees par le schema. il reste a recuperer le modele charge dans state avant de faire la prediction.

## 3. La fonction `predict()` (`maintai/api/main.py`)

Votre code :

```python
predictor = state.get("predictor")

if predictor is None:
    raise HTTPException(status_code=503, detail="Modèle non chargé")

return PredictionOut(**predictor.predict(reading.model_dump()))
```

Pourquoi répondre **503** et pas 500 quand le modèle manque ?

503 veut dire que le serveur fonctionne mais qu'il ne peut pas fournir le service demande pour le moment. ici, le modele n'est pas charge. 500 indiquerait plutot une erreur interne non prevue dans le code.

Pourquoi le modèle est-il chargé **une seule fois**, au démarrage, et pas à chaque requête ?

le modele est lu une seule fois depuis models/model.joblib au demarrage puis garde dans state["predictor"]. cela evite de relire le fichier et de recharger le modele a chaque requete ce qui rend l'api plus rapide et plus stable.

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```
========================================================================= 13 passed, 1 warning in 0.78s =========================================================================
```

## 5. L'API en marche

Après `python -m maintai.dataset` et `python -m maintai.train`, lancez `uvicorn maintai.api.main:app --reload`, puis envoyez ces requêtes depuis `/docs` (ou avec `curl.exe`).

| Requête                                                                                                          | Code obtenu | Réponse (le corps JSON)                                                                                                  |
| ---------------------------------------------------------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------ |
| `GET /health`                                                                                                    | 200         | {"status":"ok","model_loaded":true}                                                                                      |
| `POST /v1/predict` avec `{"temperature_c": 72.5, "vibration_mm_s": 6.1, "load_pct": 85, "runtime_hours": 15000}` | 200         | {"failure_probability":0.9553,"alert":true,"threshold":0.3,"model_version":"2026-10-27T17:38:18Z"}                       |
| `POST /v1/predict` avec une température de 500                                                                   | 422         | {"detail":[{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150"}]} |
| `POST /v1/predicte` (faute de frappe dans l'adresse)                                                             | 404         | {"detail":"Not Found"}                                                                                                   |

Dans `/docs`, où voit-on les bornes que vous avez choisies ?

dans /docs, les bornes sont visibles dans le schema de la requete de POST /v1/predict, dans les details de schema. on voit les valeurs minimum et maximum pour chaque champ.

## 6. Questions de compréhension

1. REST et FastAPI : quelle est la différence ?
   REST est un style pour organiser une api autour de ressources, d'url et de methodes http. fastapi est un framework python qui aide a creer cette api et a valider les donnees.
2. Le schéma Pydantic sert à trois choses. Lesquelles ?
   il valide les donnees recues, les convertit dans les bons types et genere automatiquement une partie de la documentation openapi dans /docs.
3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?
   localhost designe mon propre ordinateur, 8000 est le port ecoute par le serveur et /v1/predict est le chemin de la route de prediction.
4. Pourquoi `/v1` dans l'adresse ?
   cela permet de versionner l'api. si une nouvelle version incompatible est faite plus tard, on peut ajouter /v2 sans casser les clients qui utilisent encore /v1.
5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?
   maintai.api.main est le module python qui contient le code de l'api. app est l'objet FastAPI cree dans ce module et donne a uvicorn pour lancer le serveur.

## 7. Le rendu Git

- Lien de la pull request : https://github.com/nisrineregragui/projet_dai
- Le tag `tp1` existe sur GitHub : oui
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  aucune pull request n'a ete effectue

## 8. Ce qui reste flou

il reste a mieux comprendre comment choisir un seuil de panne adapte au cout des faux positifs et des faux negatifs. il faudra aussi apprendre a deployer l'api sur un vrai serveur au lieu de seulement l'utiliser en local.
