# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :** …  ·  **Membres :** …  ·  **Date :** …

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP2.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Activité 1 : casser son API (dans `TP/TP1`)

Vos cinq requêtes, le code que vous aviez **prévu**, puis le code **obtenu** dans `/docs` :

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---|---|
| 1 | champ manquant | supprimer runtime hours | 422|422
| 2 | valeur absurde |temperature_c: 500 |422 |422
| 3 | texte au lieu d'un nombre |temperatUre_c:"chaud" |422 |422
| 4 | champ en trop |Ajouter "humidité" :10| 422|422
| 5 | mauvaise route |/v2/predict |404 |404

Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ?

non

Dernière ligne de `python -m pytest` avec `tests/test_casser.py` (dans `TP/TP1`) :
============================================ 19 passed, 1 warning in 1.93s =============================================
```
```

À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

@pytest.mark.parametrize sert à exécuter une même fonction de test plusieurs fois avec différents jeux de données, sans devoir créer plusieurs fonctions. Dans notre exemple, pytest compte 5 tests indépendants, car la liste CAS_REFUSES contient 5 scénarios différents : valeur absurde, champ manquant, texte au lieu d'un nombre, champ supplémentaire et mauvaise route. Chaque scénario est donc exécuté séparément avec ses propres paramètres et son code HTTP attendu.

## 2. ruff

Sortie de `ruff check .` dans `TP/TP1` :
ruff check .
UP017 [*] Use `datetime.UTC` alias
  --> maintai\train.py:58:36
   |
56 |         "target": TARGET,
57 |         "threshold": settings.threshold,
58 |         "trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
   |                                    ^^^^^^^^^^^^
59 |         "sklearn_version": sklearn.__version__,
60 |     }
   |
help: Convert to `datetime.UTC` alias
5  | import json
6  + from datetime import datetime, timezone, UTC
--------------------------------------------------------------------------------
   -         "trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
58 +         "trained_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
59 |         "sklearn_version": sklearn.__version__,
   |

Found 1 error.
[*] 1 fixable with `--fix`.
(.venv) PS C:\Users\user\Downloads\S4_maintai-starter-tp1\maintai-starter-tp1> ruff check . --fix
Found 3 errors (3 fixed, 0 remaining).
(.venv) PS C:\Users\user\Downloads\S4_maintai-starter-tp1\maintai-starter-tp1> ruff check .      
All checks passed!
(.venv) PS C:\Users\user\Downloads\S4_maintai-starter-tp1\maintai-starter-tp1> ruff format .                        
11 files reformatted, 7 files left unchanged
(.venv) PS C:\Users\user\Downloads\S4_maintai-starter-tp1\maintai-starter-tp1> python -m pytest                     
================================================= test session starts ==================================================
platform win32 -- Python 3.13.2, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\user\Downloads\S4_maintai-starter-tp1\maintai-starter-tp1
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collected 19 items                                                                                                      

tests\test_api.py .......                                                                                         [ 36%]
tests\test_casser.py .....                                                                                        [ 63%]
tests\test_data.py ...                                                                                            [ 78%]
tests\test_fourteen.py .                                                                                          [ 84%]
tests\test_train.py ...                                                                                           [100%]

=================================================== warnings summary ===================================================
.venv\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\user\Downloads\S4_maintai-starter-tp1\maintai-starter-tp1\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html

```

Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?
vérifie chacun ?
ruff check . et python -m pytest servent à vérifier la qualité du code, mais ils n'ont pas le même objectif. ruff check . analyse statiquement le code Python pour détecter les erreurs de syntaxe potentielles, les imports inutilisés, les variables non utilisées et les problèmes de style ou de bonnes pratiques. En revanche, python -m pytest exécute les tests automatisés pour vérifier que le programme fonctionne correctement, que les fonctionnalités répondent aux attentes et que les erreurs sont bien gérées. En résumé, Ruff vérifie la qualité du code sans l'exécuter, tandis que Pytest vérifie son comportement en exécutant les tests.
…

## 3. Mise en place du TP2 (dans `TP/TP2`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
============================== 18passed in 1.63s ==============================
```

…

## 4. La clé API (sprint 1)

Votre fonction `require_api_key()` (`maintai/api/security.py`) :

```python
def require_api_key(
    x_api_key: str | None = Header(default=None)
) -> None:
    """Refuse la requête si la clé est absente ou fausse."""

    api_key = get_settings().api_key

    # Vérifier que le serveur possède une clé API configurée
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API non configurée sur le serveur"
        )

    # Vérifier que le client a fourni une clé valide
    if x_api_key is None or not secrets.compare_digest(x_api_key, api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide ou absente"
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

…============================================================== 7 failed, 11 passed, 1 warning in 3.46s ===============================================================

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
============================== 18 passed in 1.59s ==============================
```

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health`, sans clé | 200|{"status": "ok", "model_loaded": true}|
| `POST /v1/predict`, relevé normal, sans clé |401 | {"detail":"Clé API invalide ou absente"}|
| `POST /v1/predict`, relevé normal, fausse clé |401 |{"detail":"Clé API invalide ou absente"} |
| `POST /v1/predict`, relevé normal, bonne clé | 200|{"failure_probability": 0.0027, "alert": false, "threshold": 0.3, "model_version": "2026-11-03T19:52:21Z"} |
| `POST /v1/predict`, 500 °C, sans clé |401 | {"detail":"Clé API invalide ou absente"}|
| `POST /v1/predict`, 500 °C, bonne clé |422 |{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": [
        "body",
        "temperature_c"
      ],
      "msg": "Input should be less than or equal to 150",
      "input": 500,
      "ctx": {
        "le": 150
      }
    }
  ]
} |

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

ans clé, l'API répond 401 ; avec la bonne clé, elle répond 422. Les contrôles
s'exécutent dans l'ordre et le premier qui échoue donne la réponse : la clé est
vérifiée avant les données. Sans clé, le contrôle de la clé échoue en premier
(401) et l'API ne regarde même pas le corps de la requête, donc la valeur
absurde de 500 °C n'est jamais examinée. Avec la bonne clé, le contrôle de la
clé passe, puis le schéma Pydantic refuse temperature_c = 500 : 422.

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

…
J'obtiens 500 (« Clé API non configurée sur le serveur »). Sans --env-file,
le fichier .env n'est pas chargé Ce n'est pas un
401, car 401 signifie « le client s'est mal authentifié » (clé absente ou
fausse). Ici, le client a envoyé la bonne clé : c'est le serveur qui est mal
configuré, donc l'erreur est côté serveur  pas côté client
## 5. La page web (sprint 2)

Votre code `fetch` (le contenu du `addEventListener` dans `web/index.html`) :

```javascript
document.getElementById("go").addEventListener("click", async () => {

  const reading = Object.fromEntries(
    FEATURES.map(f => [
      f,
      Number(document.getElementById(f).value)
    ])
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
      show("err", `Erreur ${response.status} : ${JSON.stringify(data.detail)}`);
      return;
    }

    show(
      data.alert ? "alert" : "ok",
      `${data.alert ? "ALERTE" : "OK"} : probabilité de panne = ${data.failure_probability}`
    );

  } catch (error) {
    show("err", "API injoignable ou bloquée (CORS) : " + error.message);
  }

});
```

Ce qu'affiche la page (servie sur le port 5600) :

| Essai | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé | OK : probabilité de panne = 0.9475(fond vert) |
| 500 °C, bonne clé | Erreur 422 : Erreur 422 : [{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150}}] |
| relevé normal, fausse clé | Erreur 401 : "Clé API invalide ou absente" |

**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?

…API injoignable ou bloquée (CORS) : Failed to fetch
Access to fetch at 'http://localhost:8000/v1/predict' from origin 'http://localhost:5601' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource.
:8000/v1/predict:1  Failed to load resource: net::ERR_FAILED
Le port 5500 étant occupé sur mon poste (WinError 10013), j'ai utilisé 5600
comme origine autorisée (ajoutée à MAINTAI_CORS_ORIGINS dans .env) et 5601
comme origine non autorisée.

La page du port 5601 affiche : « API injoignable ou bloquée (CORS) : Failed to
fetch ». La console (F12) affiche que l'accès à
http://localhost:8000/v1/predict depuis l'origine http://localhost:5601 a été
bloqué par la politique CORS : l'en-tête Access-Control-Allow-Origin est absent
de la réponse à la requête preflight (OPTIONS).

Cause : 5601 n'est pas dans MAINTAI_CORS_ORIGINS, donc l'API refuse le
preflight et le navigateur bloque le POST.

Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?
CORS est une règle appliquée par le navigateur pour protéger l'utilisateur
(une page ne peut appeler une autre origine que si l'API l'autorise). curl.exe
n'est pas un navigateur : il n'envoie pas de preflight et n'applique aucune
politique CORS, il envoie directement la requête. Seule la clé API compte pour
lui. CORS n'est donc pas une protection de l'API : la clé reste indispensable.

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

==================================== 4 failed, 19 passed, 1 warning in 4.30s =====================================
Sans `headers=HEADERS`, 4 tests échouent avec le code 401 au lieu de 422
(valeur absurde, champ manquant, texte au lieu d'un nombre, champ en trop).
La clé API est vérifiée avant les données : sans clé, la requête est refusée
dès le premier contrôle et le schéma n'est jamais examiné.

Le cas qui passe quand même est la mauvaise route (/v2/predict) : la route
n'existe pas, donc l'API répond 404 avant même d'arriver au contrôle de la
clé, qui ne protège que les routes /v1
Dernière ligne de `python -m pytest` avec `headers=HEADERS` :

```
========================================= 23 passed, 1 warning in 3.67s ==========================================
```

## 7. Questions de compréhension

1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?

   401 (Unauthorized) signifie que l'API ne sait pas qui appelle : la clé est
   absente ou fausse (authentification échouée). 422 (Unprocessable Entity)
   signifie que le client est accepté mais que les données envoyées sont
   invalides (champ manquant, valeur hors bornes, mauvais type). Comme la clé
   est vérifiée avant les données, une requête sans clé reçoit 401 même si son
   corps est aussi invalide.

   401 et 403 : avec 401, l'identité n'est pas établie (« qui es-tu ? »). Avec
   403 (Forbidden), l'identité est connue mais le client n'a pas le droit
   d'accéder à cette ressource (« je sais qui tu es, mais tu n'as pas
   l'autorisation »). 401 relève de l'authentification, 403 de l'autorisation.

2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent
   `.env` et `.env.example`, et lequel est commité ?

   Ce qui est dans le code finit sur GitHub, et une clé commitée une seule fois
   reste dans l'historique de Git même si on supprime le fichier ensuite : il
   faut alors changer la clé. La clé est donc lue au démarrage depuis un
   fichier hors Git.
   `.env` contient la vraie clé et les vraies valeurs de configuration de mon
   poste (MAINTAI_API_KEY, MAINTAI_CORS_ORIGINS) ; il est ignoré par Git via
   `.gitignore` et n'est jamais commité. `.env.example` contient une fausse
   valeur (changez-moi) : il documente quoi configurer, et c'est lui qui est
   commité.

3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?

   Une URL est enregistrée partout : journaux du serveur, historique du
   navigateur, outils intermédiaires, liens partagés. Une clé placée dans l'URL
   serait donc exposée et conservée en clair. Un en-tête (X-API-Key) n'est pas
   enregistré de cette façon.

4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?

   `==` s'arrête au premier caractère différent : la durée de la réponse
   dépend du nombre de caractères corrects, ce qui permet à un attaquant de
   deviner la clé caractère par caractère en mesurant les temps de réponse
   (attaque par chronométrage). `secrets.compare_digest` compare en temps
   constant, quel que soit l'endroit où les chaînes diffèrent, et ne révèle
   donc rien par la durée.

5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et
   `http://localhost:8000` sont-elles la même origine ?

   Une origine est la combinaison d'un schéma (http), d'un domaine (localhost)
   et d'un port. Deux URL ont la même origine seulement si ces trois éléments
   sont identiques. `http://localhost:5500` et `http://localhost:8000` ont le
   même schéma et le même domaine mais des ports différents : ce sont deux
   origines différentes. C'est pourquoi le navigateur applique CORS quand la
   page (5500) appelle l'API (8000).

## 8. Le rendu Git

- Lien de la pull request : …
- Le tag `tp2` existe sur GitHub : oui / non
- `git status` avant le commit : le fichier `.env` apparaissait-il ? oui / non
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  …

## 9. Ce qui reste flou

…
