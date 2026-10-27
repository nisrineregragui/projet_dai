
# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** G2 · **Membres :** Assiya MARZAK · **Date :** 28/10/2026

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place (rien n'est encore écrit) :

```text
3 failed, 10 passed
```

Les 4 tests de `tests/test_api.py` qui passent déjà : `test_health`, `test_out_of_range_value_is_rejected`, `test_missing_field_is_rejected` et `test_openapi_documents_predict`.

Les deux tests qui attendent un 422 passent « pour une mauvaise raison » : `SensorReading` n'a aucun champ et `extra="forbid"` refuse tout champ inconnu. Toute requête reçoit donc un 422, même une requête correcte. Ils passent parce que le schéma est vide, pas parce qu'une valeur est hors bornes ou qu'un champ manque.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique |
|---|---|---:|---:|---|
| `temperature_c` | `float` | -40 | 150 | Plage de fonctionnement choisie pour un moteur industriel, du grand froid à une surchauffe sévère. |
| `vibration_mm_s` | `float` | 0 | 50 | Une vibration ne peut pas être négative. La limite supérieure permet de rejeter les valeurs excessives ou aberrantes. |
| `load_pct` | `float` | 0 | 120 | C'est un pourcentage de charge, avec une marge de surcharge jusqu'à 120 %. |
| `runtime_hours` | `float` | 0 | 100000 | Les heures de fonctionnement ne peuvent pas être négatives. 100 000 h correspondent à environ 11,4 années de marche continue. |

Après avoir écrit `schemas.py` seul, `python -m pytest` donne encore 3 échecs, mais l'erreur devient `NotImplementedError` :

```text
FAILED tests/test_api.py::test_predict_returns_probability - NotImplementedError
FAILED tests/test_api.py::test_high_risk_reading_raises_alert - NotImplementedError
FAILED tests/test_api.py::test_503_when_model_missing - NotImplementedError
3 failed, 10 passed
```

C'est un bon signe : les relevés valides passent maintenant la validation et arrivent jusqu'à `predict()`, qui n'est pas encore écrite. Le schéma fonctionne.

Je n'ai pas choisi les bornes à partir des valeurs minimales et maximales du CSV : une machine plus chaude ou qui vibre davantage que dans les données d'entraînement pourrait être refusée, alors que c'est justement celle qui risque la panne. Les champs sont de type `float` pour accepter également les valeurs décimales, par exemple 15000,5 heures.

## 3. La fonction `predict()` (`maintai/api/main.py`)

Le code utilisé :

```python
predictor = state.get("predictor")

if predictor is None:
    raise HTTPException(
        status_code=503,
        detail="Modèle non chargé : lancez python -m maintai.train, puis relancez l'API.",
    )

return PredictionOut(**predictor.predict(reading.model_dump()))
```

**Pourquoi répondre 503 et pas 500 quand le modèle manque ?**

500 signale une erreur interne inattendue du serveur. Ici, le modèle est indisponible : le code 503 signifie « service indisponible » et indique que l'API ne peut pas traiter la requête pour le moment. Le message explique comment résoudre le problème.

**Pourquoi le modèle est-il chargé une seule fois, au démarrage, et pas à chaque requête ?**

Lire le fichier du modèle sur le disque à chaque requête rendrait l'API plus lente. On le charge une fois dans `state` au démarrage (`lifespan`) et on le garde en mémoire pour les prédictions suivantes.

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```text
13 passed in 1.63s
```

Les 13 tests passent désormais avec succès.

## 5. L'API en marche

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---:|---|
| `GET /health` | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` avec `{"temperature_c":72.5,"vibration_mm_s":6.1,"load_pct":85,"runtime_hours":15000}` | 200 | `{"failure_probability": ..., "alert": ..., "threshold": 0.3, "model_version": "..."}` |
| `POST /v1/predict` avec une température de 500 | 422 | `{"detail":[{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150.0}}]}` |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | 404 | `{"detail":"Not Found"}` |

Dans `/docs`, les bornes se voient dans la section **Schemas**, en ouvrant `SensorReading` : chaque champ affiche son minimum, son maximum et sa description. L'exemple de relevé apparaît aussi dans `POST /v1/predict`.

Remarque : les valeurs exactes de `failure_probability`, `alert` et `model_version` doivent être remplacées par celles de la réponse réelle obtenue dans `/docs`.

## 6. Questions de compréhension

**1. REST et FastAPI : quelle est la différence ?**

REST est un ensemble de principes pour concevoir une API web (URL claires, méthodes HTTP, codes de statut, JSON et version). FastAPI est la bibliothèque Python avec laquelle on écrit une API qui suit ces principes.

**2. Le schéma Pydantic sert à trois choses. Lesquelles ?**

Valider les requêtes et rejeter les valeurs invalides avec une réponse 422, documenter l'API dans `/docs` et fournir un objet Python typé dans la fonction.

**3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?**

`localhost` est ma propre machine, `8000` est le port où Uvicorn écoute, et `/v1/predict` est la route définie dans le code Python, pas un dossier du disque.

**4. Pourquoi `/v1` dans l'adresse ?**

C'est la version de l'API : le contrat peut évoluer (`/v2`) sans casser les clients qui utilisent encore `/v1`.

**5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?**

`maintai.api.main` est le module correspondant au fichier `maintai/api/main.py`, écrit avec des points, et `app` est la variable de ce module qui contient l'application `FastAPI()`.

## 7. Le rendu Git

- **Lien de la pull request :** aucune pull request créée. Le compte rendu est poussé sur le dépôt https://github.com/nisrineregragui/projet_dai, dans le dossier `TP/TP1`.
- **Le tag `tp1` existe sur GitHub :** oui.
- **Qui a relu la pull request, et quel commentaire a-t-il laissé ?** Aucune relecture, puisqu'il n'y a pas eu de pull request.

## 8. Ce qui reste flou

Pendant le TP, mes 4 champs étaient écrits dans `schemas.py`, mais sans indentation, donc en dehors de la classe `SensorReading`. Python n'a affiché aucune erreur de syntaxe, car du code peut être valide en dehors d'une classe. Cependant, les champs n'appartenaient alors pas au schéma Pydantic, et les tests donnaient seulement des réponses 422.

Je ne comprends pas encore pourquoi Python accepte du code en dehors de la classe sans prévenir, ni comment repérer ce genre d'erreur plus rapidement.
