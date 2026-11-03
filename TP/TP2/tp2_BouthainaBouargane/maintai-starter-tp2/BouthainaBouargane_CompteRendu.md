# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :** …  ·  **Membres :** …  ·  **Date :** …

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP2.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Activité 1 : casser son API (dans `TP/TP1`)

Vos cinq requêtes, le code que vous aviez **prévu**, puis le code **obtenu** dans `/docs` :

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---|---|
| 1 | champ manquant (supprimer `runtime_hours`) | 422 | 422 |
| 2 | valeur absurde (`temperature_c`: 600) | 422 | 422 |
| 3 | texte au lieu d'un nombre (`vibration_mm_s`: "abs") | 422 | 422 |
| 4 | champ en trop (ajouter `temp`: 5) | 422 | 422 |
| 5 | mauvaise route (s'adresser à `/predict_v2`) | 404 | 404 |

Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ?

Aucune prévision n'était fausse. Tous les tests ont donné les codes attendus.

Dernière ligne de `python -m pytest` avec `tests/test_casser.py` (dans `TP/TP1`) :

```
========================= 19 passed, 1 warning in 2.79s ==========================
```

À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

`@pytest.mark.parametrize` permet de tester plusieurs cas avec une seule fonction. Pytest compte 5 tests pour notre fonction, car nous avons défini 5 cas différents.

## 2. ruff

Sortie de `ruff check .` dans `TP/TP1` :

```
Found 2 errors.
[*] 2 fixable with `--fix`.
```

Après correction avec `ruff check . --fix` :

```
Found 4 errors (4 fixed, 0 remaining).
```

Puis avec `ruff check .` :

```
All checks passed!
```

Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?

`ruff check .` vérifie le code pour détecter les erreurs de style et de formatage.

`python -m pytest` exécute les tests pour vérifier que le programme fonctionne correctement.

## 3. Mise en place du TP2 (dans `TP/TP2`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
========================= 19 passed, 1 warning in 3.11s ==========================
```

## 4. La clé API (sprint 1)

Votre fonction `require_api_key()` (`maintai/api/security.py`) :

```python
def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Refuse la requête si la clé est absente ou fausse."""
    api_key = get_settings().api_key

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API non configurée sur le serveur",
        )

    if x_api_key is None or not secrets.compare_digest(x_api_key, api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API absente ou invalide",
        )
```

Votre ligne `router = ...` dans `maintai/api/main.py` :

```python
router = APIRouter(
    prefix="/v1",
    dependencies=[Depends(require_api_key)]
)
```

Après avoir écrit `security.py` seul (sans toucher au router), combien de tests échouent ? Pourquoi ?

```
========================= 7 failed , 11 passed, 1 warning in 3.46s ==========================
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
========================= 19 passed, 1 warning in 3.11s ==========================
```

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health`, sans clé | 200 | `{"status": "healthy"}` |
| `POST /v1/predict`, relevé normal, sans clé | 401 | `{"detail": "Clé API absente ou invalide"}` |
| `POST /v1/predict`, relevé normal, fausse clé | 401 | `{"detail": "Clé API absente ou invalide"}` |
| `POST /v1/predict`, relevé normal, bonne clé | 200 | `{"failure_probability": 0.something, "alert": boolean}` |
| `POST /v1/predict`, 500 °C, sans clé | 401 | `{"detail": "Clé API absente ou invalide"}` |
| `POST /v1/predict`, 500 °C, bonne clé | 422 | `{"detail": [{"loc": ["body", "temperature_c"], "msg": "Input should be less than or equal to 100.0", "type": "less_than_equal", "input": 500, "ctx": {"le": 100.0}}]}` |

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

C'est à cause de l'ordre des vérifications dans l'API : l'authentification (la clé) est contrôlée avant la validation des données. Sans clé, l'API bloque immédiatement la requête (401) sans regarder la température. Avec la clé, l'authentification passe, mais l'API analyse les données et rejette la température de 500 °C car elle dépasse les limites autorisées (422).

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

On obtient un code 500 Internal Server Error. Ce n'est pas un 401 car le problème ne vient pas d'une authentification refusée, mais d'une erreur de configuration du serveur : sans le fichier `.env`, l'application n'a pas pu charger la clé secrète au démarrage. Le serveur est donc incapable de fonctionner, ce qui déclenche une erreur 500.

## 5. La page web (sprint 2)

Votre code `fetch` (le contenu du `addEventListener` dans `web/index.html`) :

```javascript
const FEATURES = ["temperature_c", "vibration_mm_s", "load_pct", "runtime_hours"];
const show = (cls, text) => {
  const r = document.getElementById("result");
  r.className = cls;
  r.textContent = text;
};

document.getElementById("go").addEventListener("click", async () => {
  const reading = Object.fromEntries(
    FEATURES.map(f => [f, Number(document.getElementById(f).value)])
  );

  const url = document.getElementById("url").value;
  const key = document.getElementById("key").value;

  try {
    const response = await fetch(`${url}/v1/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": key
      },
      body: JSON.stringify(reading)
    });

    const data = await response.json();

    if (!response.ok) {
      show("err", data.detail || "Erreur lors de la prédiction");
      return;
    }

    show("ok", JSON.stringify(data, null, 2));

  } catch (error) {
    show("err", "Erreur de connexion à l'API : " + error.message);
  }
});
```

Ce qu'affiche la page (servie sur le port 5500) :

| Essai | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé | `{"failure_probability": 0.15, "alert": false}` |
| 500 °C, bonne clé | `[{"loc": ["body", "temperature_c"], "msg": "Input should be less than or equal to 100.0", "type": "less_than_equal", "input": 500, "ctx": {"le": 100.0}}]` |
| relevé normal, fausse clé | `{"detail": "Clé API absente ou invalide"}` |

**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?

La page affiche une erreur (ou reste bloquée) et la console (F12) indique une erreur CORS explicite du type : « has been blocked by CORS policy ». L'origine 5501 n'est pas autorisée par l'API.

Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?

Parce que CORS est une règle de sécurité propre aux navigateurs web. `curl.exe` n'est pas un navigateur, il n'applique pas cette politique et envoie simplement la requête HTTP.

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

Les 5 tests échouent, et ils renvoient tous le code 401 Unauthorized.

C'est le 5e cas (la mauvaise route `/v1/inconnue`) qui passe quand même.

Parce que FastAPI analyse d'abord l'URL avant de vérifier la sécurité. Comme la route `/v1/inconnue` n'existe pas, l'application renvoie directement un code 404 Not Found, ce qui correspond exactement à ce que le test attendait (attendu = 404), avec ou sans clé API.

Dernière ligne de `python -m pytest` avec `headers=HEADERS` :

```
================ 23 passed, 1 warning in 2.02s ================
```

## 7. Questions de compréhension

**1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?**

- 401 (Unauthorized) : L'utilisateur n'est pas authentifié (clé absente ou invalide).
- 403 (Forbidden) : L'utilisateur est authentifié mais n'a pas les droits pour accéder à la ressource.
- 422 (Unprocessable Entity) : L'authentification est valide, mais les données envoyées dans le corps de la requête sont mal formatées ou incorrectes.

**2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?**

Pour des raisons de sécurité afin de ne pas exposer de secret sur un dépôt public.

- `.env` contient la vraie clé secrète (il est gardé secret et jamais commité).
- `.env.example` contient un modèle vide ou fictif (il est commité sur Git pour montrer la structure attendue).

**3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?**

Pour des raisons de confidentialité : les URL sont enregistrées en clair dans les historiques de navigation, les fichiers de logs des serveurs et les proxys, contrairement aux en-têtes HTTP (surtout en HTTPS).

**4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?**

Il effectue une comparaison à temps constant, ce qui protège contre les attaques temporelles (timing attacks) qui permettent à un pirate de deviner la clé en mesurant le temps de réponse du serveur.

**5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même origine ?**

Une origine est la combinaison d'un protocole (`http://`), d'un domaine (`localhost`) et d'un port (5500 / 8000).

Non, ce ne sont pas la même origine car leurs ports sont différents (CORS bloque les requêtes entre les deux).

## 8. Le rendu Git

- Lien de la pull request : https://github.com/nisrineregragui/projet_dai/pull/2
- Le tag `tp2` existe sur GitHub : oui
- `git status` avant le commit : le fichier `.env` apparaissait-il ? non — il est ignoré par le .gitignore (vérifié avec `git check-ignore -v`)

## 9. Ce qui reste flou

Tout est clair, l'ensemble des notions abordées dans ce TP a été bien compris et assimilé.
