# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** G2·  **Membres :** …  ·  **Date :** 27/10/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP1.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place (rien n'est encore écrit) :

```
4 passed, 3 failed in 0.81s
```

Dans `tests/test_api.py`, 4 tests sur 7 passent déjà alors que rien n'est écrit. Lesquels ?

- `test_health`
- `test_out_of_range_value_is_rejected`
- `test_missing_field_is_rejected`
- `test_openapi_documents_predict`

Pour les deux tests qui attendent un code 422, ils passent « pour une mauvaise raison » parce que le modèle `SensorReading` n'a pas encore de champs déclarés. Comme on a mis `extra="forbid"` dans `model_config`, FastAPI/Pydantic rejette automatiquement tout champ non attendu, même avant qu'on ait vérifié les valeurs réelles. Donc une requête avec un champ extra ou un champ manquant est refusée, mais uniquement parce que le schéma est vide, pas parce que la logique métier est correcte.

---

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min / max des données) |
|---|---|---:|---:|---|
| `temperature_c` | `float` | -40 | 150 | La température d'un moteur peut fortement varier selon le contexte, mais on exclut les valeurs impossibles ou dangereusement extrêmes pour éviter des données incohérentes. |
| `vibration_mm_s` | `float` | 0 | 25 | Une vibration négative n'a pas de sens physique ; au-delà de 25 mm/s, on entre dans une zone de dysfonctionnement mécanique évident. |
| `load_pct` | `float` | 0 | 100 | La charge d'un moteur est exprimée en pourcentage de sa puissance nominale, donc elle doit rester dans l'intervalle standard 0–100 %. |
| `runtime_hours` | `float` | 0 | 20000 | Les heures de fonctionnement sont toujours positives ; 20 000 h est un ordre de grandeur réaliste pour des machines industrielles. |

Après avoir écrit `schemas.py` seul, que donne `python -m pytest`, et quel est le message d'erreur des tests qui échouent ? Pourquoi est-ce un bon signe ?

```
4 passed, 3 failed in 0.70s
```

Les tests qui échouent remontent une erreur de type `NotImplementedError` / `500 Internal Server Error` sur `/v1/predict`. C'est un bon signe parce que cela montre que le schéma de validation fonctionne bien : les règles de saisie sont en place, et le seul point restant à corriger est la logique métier de la prédiction elle-même.

---

## 3. La fonction `predict()` (`maintai/api/main.py`)

Votre code :

```python
def predict(reading: SensorReading) -> PredictionOut:
    predictor = state.get("predictor")
    if predictor is None:
        raise HTTPException(status_code=503, detail="Prediction model not available")
    prediction = predictor.predict(reading.model_dump())
    return PredictionOut(**prediction)
```

Pourquoi répondre **503** et pas 500 quand le modèle manque ?

Parce que le modèle est une dépendance externe de l'API. Si le fichier n'est pas présent ou pas encore entraîné, la requête ne peut pas être traitée correctement, mais le serveur lui-même n'est pas cassé. Le code HTTP 503 signifie « Service Unavailable » : le service est prêt, mais il ne peut pas fournir la réponse demandée faute de ressource essentielle.

Pourquoi le modèle est-il chargé **une seule fois**, au démarrage, et pas à chaque requête ?

Parce que le chargement du modèle est coûteux en temps et en mémoire, et qu'il ne change pas tant que l'application tourne. Le `lifespan` du FastAPI le charge au démarrage et le stocke dans `state`, ce qui permet de le réutiliser pour toutes les requêtes sans relire le fichier ou recharger les poids à chaque appel.

---

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```
13 passed in 3.64s
```

---

## 5. L'API en marche

Après `python -m maintai.dataset` et `python -m maintai.train`, lancez `uvicorn maintai.api.main:app --reload`, puis envoyez ces requêtes depuis `/docs` (ou avec `curl.exe`).

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---:|---|
| `GET /health` | 200 | `{"status": "ok", "model_loaded": true}` |
| `POST /v1/predict` avec `{"temperature_c": 72.5, "vibration_mm_s": 6.1, "load_pct": 85, "runtime_hours": 15000}` | 200 | `{"failure_probability": 0.9553, "alert": true, "threshold": 0.3, "model_version": "2026-10-27T18:13:54Z"}` |
| `POST /v1/predict` avec une température de 500 | 422 | `{"detail": [{"type": "less_than_equal", "loc": ["body", "temperature_c"], "msg": "Input should be less than or equal to 150", "input": 500, "ctx": {"le": 150.0}}]}` |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | 404 | erreur de route, la ressource demandée n'existe pas |

Dans `/docs`, où voit-on les bornes que vous avons choisies ?

On les voit directement dans le schéma `SensorReading`, dans la section des paramètres de l'endpoint `/v1/predict`. Chaque champ affiche sa description et la contrainte `ge` / `le`, ce qui rend la documentation interactive et explicite les limites acceptées.

---

## 6. Questions de compréhension

1. REST et FastAPI : quelle est la différence ?
   Le REST est un style d'architecture pour concevoir des APIs, avec des principes comme le découpage ressource/verbes HTTP. FastAPI est un framework Python qui permet de créer très simplement des endpoints REST, avec validation, génération de docs OpenAPI, etc.

2. Le schéma Pydantic sert à trois choses. Lesquelles ?
   - valider les données entrantes ;
   - générer une documentation automatique (OpenAPI / Swagger) ;
   - sérialiser et typer les objets de sortie.

3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?
   - `localhost` = l'adresse locale de la machine sur laquelle l'API tourne ;
   - `8000` = le port réseau de l'application ;
   - `/v1/predict` = le chemin de l'endpoint de prédiction, dans la version 1 de l'API.

4. Pourquoi `/v1` dans l'adresse ?
   Pour versionner l'API. Cela permet de garder des évolutions compatibles sans casser les clients qui utilisent une ancienne version.

5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?
   - `maintai.api.main` = le module Python contenant l'application FastAPI ;
   - `app` = l'instance FastAPI créée dans ce module et servie par uvicorn.

---

## 7. Le rendu Git

- Lien de la pull request : …
- Le tag `tp1` existe sur GitHub : oui / non
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  …

---

## 8. Ce qui reste flou

Au départ, le point le plus difficile a été de distinguer la validation Pydantic de la logique métier. Une fois le schéma bien défini, il restait à faire le lien entre les données entrantes et le modèle entraîné. En pratique, il s'agissait surtout de comprendre que les tests de validation et les tests de prédiction ne relèvent pas de la même étape : d'abord un contrat clair sur les données, puis l'appel au modèle proprement dit.
