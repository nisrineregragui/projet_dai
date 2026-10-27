# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** G2  ·  **Membres :** Assiya MARZAK  ·  **Date :** 27/10/2026

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place (rien n'est encore écrit) :

```
3 failed, 10 passed, 1 warning in 3.72s
```

Dans `tests/test_api.py`, 4 tests sur 7 passent déjà alors que rien n'est écrit. Ce sont `test_health`, `test_out_of_range_value_is_rejected`, `test_missing_field_is_rejected` et `test_openapi_documents_predict`. Les 3 qui échouent sont `test_predict_returns_probability`, `test_high_risk_reading_raises_alert` et `test_503_when_model_missing`.

Les deux tests qui attendent un 422 (`test_out_of_range_value_is_rejected` et `test_missing_field_is_rejected`) passent « pour une mauvaise raison » : au départ, `SensorReading` n'a aucun champ et `extra="forbid"` refuse tout champ inconnu. Toute requête reçoit donc un 422, même une requête correcte. Ils passent parce que le schéma est vide, pas parce que la température est hors bornes ou qu'un champ manque.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min / max des données) |
|---|---|---|---|---|
| `temperature_c` | float | -40 | 150 | Plage d'un moteur en conditions réelles, du grand froid à une surchauffe sévère. |
| `vibration_mm_s` | float | 0 | 50 | Une vibration est une amplitude, donc jamais négative. Au-delà de 50 mm/s, la machine serait en danger immédiat. |
| `load_pct` | float | 0 | 100 | C'est un pourcentage de charge. |
| `runtime_hours` | float | 0 | 100000 | Des heures de marche ne sont pas négatives. 100 000 h font environ 11 ans de marche continue. |

Après avoir écrit `schemas.py` seul, `python -m pytest` donne encore 3 failed, mais le message d'erreur devient `NotImplementedError` (au lieu de `assert 422 == 200`) :

```
FAILED tests/test_api.py::test_predict_returns_probability - NotImplementedError
FAILED tests/test_api.py::test_high_risk_reading_raises_alert - NotImplementedError
FAILED tests/test_api.py::test_503_when_model_missing - NotImplementedError
3 failed, 10 passed
```

C'est un bon signe : les relevés valides passent maintenant la validation et arrivent jusqu'à `predict()`, qui n'est pas encore écrite. Le schéma fonctionne.

Je n'ai pas pris le min / max du CSV : une machine plus chaude ou qui vibre plus que dans les données d'entraînement serait refusée, alors que c'est justement celle qui risque la panne. Les champs sont des `float` : un `int` refuserait par exemple 15000,5 heures.

## 3. La fonction `predict()` (`maintai/api/main.py`)

Votre code :

```python
predictor = state.get("predictor")
if predictor is None:
    raise HTTPException(
        status_code=503,
        detail="Modèle non chargé : lancez python -m maintai.train puis redémarrez l'API.",
    )
return PredictionOut(**predictor.predict(reading.model_dump()))
```

Pourquoi répondre **503** et pas 500 quand le modèle manque ?

500 signale un bug dans le code du serveur. Ici le code est correct : c'est le modèle qui est indisponible. 503 veut dire « service indisponible », donc le client sait qu'il peut réessayer plus tard, et le message dit quoi faire (entraîner le modèle puis redémarrer).

Pourquoi le modèle est-il chargé **une seule fois**, au démarrage, et pas à chaque requête ?

Lire le fichier du modèle sur le disque prend du temps. Le faire à chaque requête rendrait l'API lente. On le charge une fois dans `state` au démarrage (`lifespan`) et on le garde en mémoire.

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```
13 passed, 1 warning in 4.08s
```

## 5. L'API en marche

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health` | 200 | `{"status": "ok", "model_loaded": true}` |
| `POST /v1/predict` avec `{"temperature_c": 72.5, "vibration_mm_s": 6.1, "load_pct": 85, "runtime_hours": 15000}` | 200 | [À REMPLACER : ton Response body] |
| `POST /v1/predict` avec une température de 500 | 422 | [À REMPLACER : ton Response body, il contient « Input should be less than or equal to 150 »] |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | 404 | `{"detail": "Not Found"}` |

Dans `/docs`, les bornes se voient dans la section **Schemas**, en ouvrant `SensorReading` : chaque champ affiche son minimum, son maximum et sa description. L'exemple de relevé apparaît aussi dans le détail de `POST /v1/predict`.

## 6. Questions de compréhension

1. REST et FastAPI : quelle est la différence ?
   REST est un ensemble de règles pour concevoir une API web (URL claires, méthodes HTTP, codes de statut, JSON, version). FastAPI est la bibliothèque Python avec laquelle on écrit une API qui suit ces règles.
2. Le schéma Pydantic sert à trois choses. Lesquelles ?
   Valider les requêtes (422 si la valeur est invalide), documenter l'API dans `/docs`, et fournir un objet Python typé dans la fonction.
3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?
   `localhost` est ma propre machine, `8000` est le port où uvicorn écoute, et `/v1/predict` est la route définie dans le code Python (pas un dossier du disque).
4. Pourquoi `/v1` dans l'adresse ?
   C'est la version de l'API : le contrat peut évoluer (`/v2`) sans casser les clients qui utilisent encore `/v1`.
5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?
   `maintai.api.main` est le fichier `maintai/api/main.py` écrit avec des points, et `app` est la variable de ce fichier qui contient l'application `FastAPI()`.

## 7. Le rendu Git

- Lien de la pull request : [À REMPLACER : lien de ta PR, ou « pas de pull request, fichier poussé sur la branche ... »]
- Le tag `tp1` existe sur GitHub : [À REMPLACER : oui / non]
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  [À REMPLACER : ou « pas de relecture »]