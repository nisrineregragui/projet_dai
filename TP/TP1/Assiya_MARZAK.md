
# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** G2  
**Membre :** Assiya MARZAK  
**Date :** 27/10/2026

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place, avant d'écrire le code :

```text
3 failed, 10 passed
```

Les quatre tests qui passent déjà dans `tests/test_api.py` sont :

- `test_health`
- `test_out_of_range_value_is_rejected`
- `test_missing_field_is_rejected`
- `test_openapi_documents_predict`

Les deux tests qui attendent un code HTTP 422 passent pour une mauvaise raison. Au départ, le schéma `SensorReading` ne contient aucun champ et utilise `extra="forbid"`. Cette option interdit les champs supplémentaires qui ne sont pas déclarés dans le schéma. Comme tous les champs envoyés dans la requête sont alors considérés comme inconnus, même une requête valide est rejetée avec un code 422.

Les tests passent donc parce que le schéma est vide, et non parce que les validations des valeurs et des champs fonctionnent correctement.

---

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique |
|---|---|---:|---:|---|
| `temperature_c` | `float` | -40 | 150 | Cette plage représente des températures possibles pour surveiller un moteur industriel, du grand froid jusqu'à une température très élevée. |
| `vibration_mm_s` | `float` | 0 | 50 | Une vibration ne peut pas être négative. La borne supérieure permet de rejeter les valeurs excessives ou aberrantes. |
| `load_pct` | `float` | 0 | 120 | Le pourcentage de charge ne peut pas être négatif. La limite de 120 % permet de prendre en compte une éventuelle surcharge du moteur. |
| `runtime_hours` | `float` | 0 | 100000 | Le nombre d'heures de fonctionnement ne peut pas être négatif. 100 000 heures correspondent à environ 11,4 années de fonctionnement continu. |

Après avoir écrit uniquement `schemas.py`, la commande `python -m pytest` donne encore trois échecs :

```text
FAILED tests/test_api.py::test_predict_returns_probability - NotImplementedError
FAILED tests/test_api.py::test_high_risk_reading_raises_alert - NotImplementedError
FAILED tests/test_api.py::test_503_when_model_missing - NotImplementedError

3 failed, 10 passed
```

C'est un bon signe, car les données sont maintenant correctement validées par le schéma Pydantic. Les requêtes valides peuvent atteindre la fonction `predict()`. Les trois tests échouent parce que cette fonction n'est pas encore implémentée et déclenche une `NotImplementedError`.

Les bornes ont été choisies selon des limites physiques plausibles pour un moteur industriel, et non simplement selon les valeurs minimales et maximales du fichier CSV. Une machine peut présenter une température ou une vibration supérieure à celles observées pendant l'entraînement. Il est donc important de prévoir une plage suffisamment large pour accepter des mesures réalistes.

Les champs sont de type `float` afin d'accepter aussi les nombres décimaux, par exemple `15000.5` heures de fonctionnement.

---

## 3. La fonction `predict()` (`maintai/api/main.py`)

Voici le corps de la fonction utilisé :

```python
predictor = state.get("predictor")

if predictor is None:
    raise HTTPException(
        status_code=503,
        detail="Modèle non chargé : lancez python -m maintai.train, puis relancez l'API.",
    )

return PredictionOut(**predictor.predict(reading.model_dump()))
```

### Pourquoi répondre 503 et non 500 lorsque le modèle manque ?

Le code HTTP 500 signifie qu'une erreur interne du serveur s'est produite. Le code HTTP 503 signifie que le service est temporairement indisponible.

Dans notre cas, si le modèle de prédiction n'est pas chargé, l'API ne peut pas effectuer la prédiction demandée. Le code 503 est donc plus adapté, car il indique que le service ne peut pas traiter la requête pour le moment.

Le message d'erreur précise comment résoudre le problème : entraîner ou charger le modèle avec `python -m maintai.train`, puis relancer l'API si nécessaire.

### Pourquoi le modèle est-il chargé une seule fois au démarrage ?

Charger le modèle à chaque requête serait inefficace et ralentirait les réponses de l'API.

Le modèle est donc chargé une seule fois au démarrage de l'application, dans le mécanisme `lifespan`, puis conservé en mémoire dans `state`. Les requêtes suivantes peuvent ainsi réutiliser le modèle déjà chargé, ce qui améliore les performances.

---

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```text
13 passed in 1.63s
```

Les 13 tests passent désormais avec succès. Cela confirme que les fonctionnalités testées de l'API, notamment la validation des entrées, la prédiction, la gestion des alertes et le cas où le modèle est indisponible, répondent aux attentes des tests.

---

## 5. L'API en marche

Après avoir exécuté les commandes suivantes :

```powershell
python -m maintai.dataset
python -m maintai.train
uvicorn maintai.api.main:app --reload
```

Les requêtes suivantes permettent de vérifier le fonctionnement de l'API depuis `/docs`.

| Requête | Code obtenu | Réponse (corps JSON) |
|---|---:|---|
| `GET /health` | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` avec `{"temperature_c":72.5,"vibration_mm_s":6.1,"load_pct":85,"runtime_hours":15000}` | 200 | `{"failure_probability":...,"alert":...,"threshold":0.3,"model_version":"..."}` |
| `POST /v1/predict` avec une température de 500 °C | 422 | `{"detail":[{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150.0}}]}` |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | 404 | `{"detail":"Not Found"}` |

**Remarque :** pour la requête de prédiction valide, les points de suspension indiquent que les valeurs exactes de `failure_probability`, `alert` et `model_version` doivent être remplacées par celles retournées par votre propre API.

### Où voir les bornes dans `/docs` ?

Dans la documentation interactive `/docs`, la section **Schemas** présente le schéma `SensorReading`. En l'ouvrant, on peut consulter les champs, leurs types, leurs valeurs minimales et maximales, ainsi que leurs descriptions.

Dans la section `POST /v1/predict`, on peut également voir le format attendu pour envoyer une requête de prédiction.

---

## 6. Questions de compréhension

### 1. REST et FastAPI : quelle est la différence ?

REST est un ensemble de principes d'architecture utilisés pour concevoir des API web. Il repose notamment sur des ressources accessibles par des URL, des méthodes HTTP et des codes de statut.

FastAPI est une bibliothèque Python permettant de développer des API web. Elle fournit notamment la validation des données, la génération automatique de documentation et la gestion des requêtes HTTP. On peut utiliser FastAPI pour créer une API respectant les principes REST.

### 2. Le schéma Pydantic sert à trois choses. Lesquelles ?

Le schéma Pydantic remplit trois fonctions principales :

1. **Valider les données entrantes :** il vérifie les types, les champs obligatoires et les limites autorisées. Une requête invalide peut être rejetée avec un code HTTP 422.
2. **Documenter l'API :** il permet de générer automatiquement une documentation décrivant les champs et les contraintes dans `/docs`.
3. **Fournir un objet Python typé :** il permet à la fonction de recevoir des données structurées et validées, plus faciles à utiliser dans le code.

### 3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?

- `localhost` désigne la machine locale sur laquelle l'API est exécutée.
- `8000` est le port utilisé par le serveur Uvicorn pour écouter les requêtes.
- `/v1/predict` est le chemin de la route de prédiction exposée par l'API. Il ne correspond pas à un dossier du disque.

### 4. Pourquoi utiliser `/v1` dans l'adresse ?

`/v1` indique la version 1 de l'API. Si le contrat de l'API évolue de manière incompatible, une nouvelle version `/v2` peut être créée sans obliger immédiatement les clients qui utilisent `/v1` à modifier leur code.

### 5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?

`maintai.api.main` désigne le module Python correspondant au fichier `maintai/api/main.py`. Les points représentent les dossiers et le nom du module.

`app` désigne la variable définie dans ce module qui contient l'instance de l'application FastAPI, généralement créée avec `app = FastAPI()`.

Uvicorn utilise ce chemin pour trouver l'application et la démarrer.

---

## 7. Le rendu Git

- **Lien du dépôt GitHub :** https://github.com/nisrineregragui/projet_dai
- **Dossier du TP :** `TP/TP1`
- **Lien de la pull request :** aucune pull request n'a été créée à ce stade. Le compte rendu a été envoyé sur le dépôt.
- **Le tag `tp1` existe sur GitHub :** oui, selon les vérifications effectuées pendant le TP.
- **Relecture de la pull request :** aucune relecture n'a eu lieu puisqu'aucune pull request n'a été créée.

Pour un rendu nécessitant une pull request, il faudra créer une branche de travail, pousser les modifications, puis ouvrir une pull request vers la branche cible du dépôt.

---

## 8. Ce qui reste flou

Pendant le TP, j'ai rencontré une difficulté liée à l'indentation dans `schemas.py`. Les champs avaient été écrits sans indentation à l'intérieur de la classe `SensorReading`, donc en dehors de celle-ci.

Python n'a pas affiché d'erreur de syntaxe, car du code peut être valide en dehors d'une classe. Cependant, les champs n'appartenaient pas au schéma Pydantic. La validation ne fonctionnait donc pas comme prévu et les requêtes étaient rejetées avec un code 422.

Je ne comprends pas encore complètement pourquoi Python accepte du code placé en dehors d'une classe sans afficher d'erreur. Je souhaite également apprendre à repérer plus rapidement ce type de problème, notamment grâce à l'indentation dans VS Code, aux outils d'analyse du code et aux tests automatisés.

Cette difficulté m'a permis de comprendre que la syntaxe correcte ne garantit pas toujours que le programme réalise le comportement attendu. Il faut aussi vérifier la structure du code et s'assurer que les tests valident réellement le comportement recherché.
