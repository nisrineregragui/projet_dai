# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :** g2 ·  **Membres :** regragui nisrine ·  **Date :** 03/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP2.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Activité 1 : casser son API (dans `TP/TP1`)

Vos cinq requêtes, le code que vous aviez **prévu**, puis le code **obtenu** dans `/docs` :

Cas	                             Requête à envoyer	          Code HTTP prévu          obtenu 
Champ manquant                     Supprimer load_pct	                  422                422
Valeur absurde	                    temperature_c :500	                     422                422
Texte au lieu d'un nombre          temperature_c: "chaud"	            422                422 
Champ en trop	                    Ajouter "pressure": 10	            422                422 
Mauvaise route	                    /v2/predict	                        404                404

Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ?
Non

Dernière ligne de `python -m pytest` avec `tests/test_casser.py` (dans `TP/TP1`) :

```
=================== 19 passed in 9.44s ====================
```

À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?
 
 @pytest.mark.parametrize permet d'exécuter une même fonction avec plusieurs jeux de données ; pytest compte donc 5 tests distincts, un pour chaque cas défini dans CAS_REFUSES

…

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
   |
5  | import json
   - from datetime import datetime, timezone
6  + from datetime import datetime, timezone, UTC
7  |
--------------------------------------------------------------------------------
57 |         "threshold": settings.threshold,
   -         "trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
58 +         "trained_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
59 |         "sklearn_version": sklearn.__version__,
   |
   
Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?

ruff check . vérifie la qualité du code (erreurs de syntaxe, style et bonnes pratiques), tandis que python -m pytest exécute les tests pour vérifier que le programme fonctionne correctement

## 3. Mise en place du TP2 (dans `TP/TP2`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
(collez ici)
```

Quels sont les deux tests qui échouent, et que reçoivent-ils au lieu de 401 ?

…

## 4. La clé API (sprint 1)

Votre fonction `require_api_key()` (`maintai/api/security.py`) :

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
            detail="Clé API invalide ou absente",
        )


Votre ligne `router = ...` dans `maintai/api/main.py` :

router = APIRouter(
    prefix="/v1",
    dependencies=[Depends(require_api_key)]
)

Après avoir écrit `security.py` seul (sans toucher au router), combien de tests échouent ? Pourquoi ?

============================================================== 7 failed, 11 passed, 1 warning in 3.46s ===============================================================
(S5_maintai-starter-tp2) PS C:\Users\nisri\Downloads\S5_maintai-starter-tp2\maintai-starter-tp2> 

Dernière ligne de `python -m pytest` à la fin du sprint 1 :
=================================================================== 18 passed, 1 warning in 1.98s ====================================================================

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health`, sans clé | 200|{
  "status": "ok",
  "model_loaded": true
} |
| `POST /v1/predict`, relevé normal, sans clé |401 |{
  "detail": "Clé API invalide ou absente"
} |
| `POST /v1/predict`, relevé normal, fausse clé |401 |{
  "detail": "Clé API invalide ou absente"
} |
| `POST /v1/predict`, relevé normal, bonne clé | 200| {
  "failure_probability": 0.9553,
  "alert": true,
  "threshold": 0.3,
  "model_version": "2026-11-03T21:00:55Z"
}|
| `POST /v1/predict`, 500 °C, sans clé |401 |{
  "detail": "Clé API invalide ou absente"
} |
| `POST /v1/predict`, 500 °C, bonne clé |422 | {
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
}|

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

Sans clé API, la requête est rejetée directement avec 401, tandis qu'avec une clé valide, la température est vérifiée et dépasse la limite de 150 °C, ce qui provoque une erreur 422

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

On obtient 500 car le serveur n'a pas de clé API configurée, contrairement au 401 qui indique une clé absente ou incorrecte envoyée par le client

## 5. La page web (sprint 2)

Votre code `fetch` (le contenu du `addEventListener` dans `web/index.html`) :

<script>
const FEATURES = [
  "temperature_c",
  "vibration_mm_s",
  "load_pct",
  "runtime_hours"
];

const show = (cls, text) => {
  const r = document.getElementById("result");
  r.className = cls;
  r.textContent = text;
};

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
      throw new Error(data.detail || "Erreur API");
    }

    show(
      data.failure_probability >= 0.5 ? "alert" : "ok",
      JSON.stringify(data, null, 2)
    );

  } catch (error) {
    show("err", error.message);
  }
});
</script>

Ce qu'affiche la page (servie sur le port 5500) :

| Essai | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé | { "failure_probability": 0.9475, "alert": true, "threshold": 0.3, "model_version": "2026-11-03T21:00:55Z" }|
| 500 °C, bonne clé | [object Object]|
| relevé normal, fausse clé | Clé API invalide ou absente |

**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?

Failed to fetch
Access to fetch at 'http://localhost:8000/v1/predict' from origin 'http://localhost:5501' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource.



Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?

Parce que curl n'est pas bloqué par CORS, contrairement au navigateur.

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

Quatre tests échouent : ils reçoivent 401 au lieu de 422, car la clé API manque. Le test de mauvaise route passe quand même : cette route n'existe pas, donc l'API répond 404 avant de vérifier la clé.

Dernière ligne de `python -m pytest` avec `headers=HEADERS` :

```
============================= 23 passed in 5.24s ==============================
```

## 7. Questions de compréhension

1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?
   401 signifie que la clé manque ou n'est pas valide. 422 signifie que les données envoyées ne sont pas valides. 403 signifie que l'utilisateur est identifié, mais n'a pas le droit d'accéder à cette ressource.
2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?
   La clé est un secret : il ne faut pas la publier. `.env` contient la vraie clé et n'est pas commité. `.env.example` contient une valeur d'exemple et est commité.
3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?
   L'URL peut être enregistrée dans l'historique ou les journaux. L'en-tête évite d'y exposer la clé.
4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?
   Il compare les clés sans révéler le résultat plus vite selon l'endroit où elles diffèrent. Cela aide à éviter les attaques par mesure du temps.
5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même origine ?
   Une origine est composée du protocole, du nom d'hôte et du port. Ces deux adresses ont des ports différents, donc elles ne sont pas de la même origine.

## 8. Le rendu Git

- Lien de la pull request : https://github.com/nisrineregragui/projet_dai.git
- Le tag `tp2` existe sur GitHub : non
- `git status` avant le commit : le fichier `.env` apparaissait-il ? oui / non
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  …

## 9. Ce qui reste flou

