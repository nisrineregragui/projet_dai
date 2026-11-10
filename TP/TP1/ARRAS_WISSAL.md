
# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** G2 · **Membres :** ARRAS WISSAL

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place (rien n'est encore écrit) :

```
3 failed, 10 passed
```

Les 4 tests qui passent déjà : `test_health`, `test_out_of_range_value_is_rejected`, `test_missing_field_is_rejected` et `test_openapi_documents_predict`. Les deux tests de 422 passent pour une mauvaise raison : le schéma est vide et `extra="forbid"` refuse tout champ, donc tout relevé est refusé avec 422, même un relevé valide. Aucune borne n'est réellement vérifiée.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique |
|---|---|---|---|---|
| `temperature_c` | float | -40 | 150 | Plage de fonctionnement d'un moteur industriel (limite de l'isolation). |
| `vibration_mm_s` | float | 0 | 50 | Jamais négative ; zone dangereuse ISO 10816 vers 11 mm/s, 50 laisse une marge avant le capteur défaillant. |
| `load_pct` | float | 0 | 120 | De 0 à 100 % de la charge nominale, plus une marge de surcharge. |
| `runtime_hours` | float | 0 | 100000 | Jamais négatif ; 100 000 h (environ 11 ans de marche continue) dépasse la durée de vie d'une machine. |

Après avoir écrit `schemas.py` seul, `python -m pytest` donne :

```
3 failed, 10 passed (NotImplementedError)
```

C'est un bon signe : le schéma accepte maintenant les relevés valides, et la requête arrive jusqu'à `predict()`, qui n'est pas encore écrite. L'erreur ne vient plus du schéma.

## 3. La fonction `predict()` (`maintai/api/main.py`)

Votre code :

```python
predictor = state.get("predictor")
if predictor is None:
    raise HTTPException(
        status_code=503,
        detail="Modèle non chargé : lancez python -m maintai.train, puis relancez l'API.",
    )
return PredictionOut(**predictor.predict(reading.model_dump()))
```

Pourquoi répondre **503** et pas 500 quand le modèle manque ?
Parce que le code est correct et qu'une ressource manque (le modèle) ; 500 signale un bug dans le code.

Pourquoi le modèle est-il chargé **une seule fois**, au démarrage, et pas à chaque requête ?
Lire le fichier à chaque requête serait lent, et on détecte l'absence du modèle dès le démarrage.

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```
13 passed in 1.63s
```

## 5. L'API en marche

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health` | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` (72.5 / 6.1 / 85 / 15000) | 200 | `{"failure_probability": ..., "alert": ..., "threshold": 0.3, "model_version": "..."}` |
| `POST /v1/predict` (température 500) | 422 | `{"detail":[{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150",...}]}` |
| `POST /v1/predicte` | 404 | `{"detail":"Not Found"}` |

Dans `/docs`, où voit-on les bornes que vous avez choisies ?
Dans le schéma `SensorReading` : minimum, maximum, description et exemple de chaque champ.

## 6. Questions de compréhension

1. REST et FastAPI : quelle est la différence ?
   REST est un ensemble de règles pour concevoir une API web (URL claires, méthodes HTTP, codes de statut, JSON, version). FastAPI est la bibliothèque Python qui permet d'écrire une API qui respecte ces règles.
2. Le schéma Pydantic sert à trois choses. Lesquelles ?
   Il valide les entrées (renvoie 422 avant d'appeler la fonction), il génère la documentation `/docs`, et il donne à la fonction un objet Python typé et déjà vérifié.
3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?
   `localhost` est ma propre machine, `8000` est le port où uvicorn écoute, et `/v1/predict` est la route définie dans le code Python (pas un dossier du disque).
4. Pourquoi `/v1` dans l'adresse ?
   C'est la version de l'API : on pourra créer une `/v2` plus tard sans casser les clients qui utilisent encore `/v1`.
5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?
   `maintai.api.main` est le fichier `maintai/api/main.py` écrit avec des points et sans `.py`. `app` est la variable de ce fichier qui contient l'application FastAPI.

## 7. Le rendu Git

- Lien de la pull request : …
- Le tag `tp1` existe sur GitHub : oui / non
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  …

## 8. Ce qui reste flou

Avec le `.venv` activé, `pip install -r requirements.txt` a installé les paquets dans le Python global, et la commande `uvicorn` lançait la version du Python global. J'ai dû utiliser `python -m pip install` et `python -m uvicorn` pour travailler dans le `.venv`. Je ne comprends pas encore pourquoi `pip` et `uvicorn` pointaient vers le mauvais Python.