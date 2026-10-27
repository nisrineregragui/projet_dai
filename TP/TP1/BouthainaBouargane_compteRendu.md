# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :**2  ·  **Membres :** Bouthaina Bouargane  ·  **Date :** 27/10/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP1.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place (rien n'est encore écrit) :

```
======= 3 failed, 10 passed, 1 warning  ========
```

Dans `tests/test_api.py`, 4 tests sur 7 passent déjà alors que rien n'est écrit. Lesquels ? Pour les deux tests qui attendent un code 422, expliquez pourquoi ils passent « pour une mauvaise raison » (indice : regardez `extra="forbid"` dans `schemas.py`).

Les tests qui passent : `test_health`, `test_out_of_range_value_is_rejected`, `test_missing_field_is_rejected` et `test_openapi_documents_predict`.

Au début, `SensorReading` n'a aucun champ et `extra="forbid"` refuse les champs inconnus. Donc tous les champs envoyés sont refusés et on a toujours 422, même avec une requête correcte. Les tests passent, mais pas parce que la température est trop grande ou qu'il manque un champ.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min / max des données) |
|---|---|---|---|---|
| `temperature_c` | float | -20 | 150 | Une machine peut être froide à l'arrêt, mais au-delà de 150 °C c'est plutôt une erreur de capteur. |
| `vibration_mm_s` | float | 0 | 50 | Une vibration ne peut pas être négative, et 50 mm/s est déjà très élevé pour une machine. |
| `load_pct` | float | 0 | 100 | C'est un pourcentage. |
| `runtime_hours` | float | 0 | 200000 | Les heures ne peuvent pas être négatives, et 200 000 h font environ 23 ans de marche. |

Après avoir écrit `schemas.py` seul, que donne `python -m pytest`, et quel est le message d'erreur des tests qui échouent ? Pourquoi est-ce un bon signe ?

```
FAILED tests/test_api.py::test_predict_returns_probability - NotImplementedError
FAILED tests/test_api.py::test_high_risk_reading_raises_alert - NotImplementedError
FAILED tests/test_api.py::test_503_when_model_missing - NotImplementedError
======= 3 failed, 10 passed, 1 warning in 4.11s ========
```

Toujours 3 tests en échec, mais maintenant l'erreur est `NotImplementedError`. Ça veut dire que les requêtes passent la validation et arrivent jusqu'à `predict()`, qu'on n'a pas encore écrite. Le schéma marche donc bien.

On n'a pas pris le min / max des données, parce qu'une machine plus chaude ou qui vibre plus que dans les données d'entraînement serait refusée, alors que c'est justement celle qui risque de tomber en panne.

## 3. La fonction `predict()` (`maintai/api/main.py`)

Votre code :

```python
predictor = state.get("predictor")
if predictor is None:
    raise HTTPException(status_code=503, detail="Modèle non chargé")
return predictor.predict(reading.model_dump())
```

Pourquoi répondre **503** et pas 500 quand le modèle manque ?

500 veut dire qu'il y a un bug dans le serveur. Ici ce n'est pas un bug : le modèle n'est juste pas encore disponible. 503 veut dire « service indisponible pour le moment », donc on peut réessayer plus tard.

Pourquoi le modèle est-il chargé **une seule fois**, au démarrage, et pas à chaque requête ?

Charger le modèle depuis le fichier prend du temps. Si on le faisait à chaque requête, l'API serait lente. On le charge une fois au démarrage et on le garde en mémoire.

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```
============ 13 passed, 1 warning in 2.34s =============
```

## 5. L'API en marche

Après `python -m maintai.dataset` et `python -m maintai.train`, lancez `uvicorn maintai.api.main:app --reload`, puis envoyez ces requêtes depuis `/docs` (ou avec `curl.exe`).

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health` | 200 | `{"status": "ok", "model_loaded": true}` |
| `POST /v1/predict` avec `{"temperature_c": 72.5, "vibration_mm_s": 6.1, "load_pct": 85, "runtime_hours": 15000}` | 200 | `{"failure_probability": 0.9553, "alert": true, "threshold": 0.3, "model_version": "2026-10-27T17:49:13Z"}` |
| `POST /v1/predict` avec une température de 500 | 422 | `{"detail": [{"type": "less_than_equal", "loc": ["body", "temperature_c"], "msg": "Input should be less than or equal to 150", "input": 500, "ctx": {"le": 150.0}}]}` |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | 404 | `{"detail": "Not Found"}` |

Dans `/docs`, où voit-on les bornes que vous avez choisies ?

En bas de la page, dans **Schemas**, en ouvrant `SensorReading`. Chaque champ affiche son `minimum` et son `maximum`.

## 6. Questions de compréhension

1. REST et FastAPI : quelle est la différence ?
   REST, c'est une façon d'organiser une API (des URL et des méthodes comme GET et POST). FastAPI, c'est un outil Python qu'on utilise pour créer cette API.
2. Le schéma Pydantic sert à trois choses. Lesquelles ?
   Vérifier les données reçues, les transformer en objet Python, et générer la documentation dans `/docs`.
3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?
   `localhost` c'est notre propre machine, `8000` c'est le port où l'API tourne, et `/v1/predict` c'est la route qu'on appelle.
4. Pourquoi `/v1` dans l'adresse ?
   C'est la version de l'API. Si on la modifie plus tard, on peut créer `/v2` sans casser ceux qui utilisent encore `/v1`.
5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?
   `maintai.api.main` c'est le fichier `maintai/api/main.py`, et `app` c'est l'objet FastAPI défini dans ce fichier.

## 7. Le rendu Git

- Lien de la pull request : pas de pull request, le compte rendu est poussé directement sur la branche `master` du dépôt https://github.com/nisrineregragui/projet_dai (dossier `TP/TP1`).
- Le tag `tp1` existe sur GitHub : oui
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  Pas de relecture, puisqu'il n'y a pas eu de pull request.

## 8. Ce qui reste flou

Je ne comprends pas encore très bien comment fonctionne `lifespan` avec le `yield`. Je ne sais pas non plus ce que vaut la prédiction quand une valeur est acceptée mais très différente des données d'entraînement.