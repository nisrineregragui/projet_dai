# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :** G2 · **Membres :** Adam TAFRHY · **Date :** 03/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP2.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Activité 1 : casser son API (dans `TP/TP1`)

Vos cinq requêtes, le code que vous aviez **prévu**, puis le code **obtenu** dans `/docs` :

| Requête | Ce qui ne va pas          | Code prévu | Code obtenu |
| ------- | ------------------------- | ---------- | ----------- |
| 1       | champ manquant            | 422        | 422         |
| 2       | valeur absurde            | 422        | 422         |
| 3       | texte au lieu d'un nombre | 422        | 422         |
| 4       | champ en trop             | 422        | 422         |
| 5       | mauvaise route            | 404        | 404         |

Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ? Aucune des previsions n'etaient fausses

…

Dernière ligne de `python -m pytest` avec `tests/test_casser.py` (dans `TP/TP1`) :

```
========================================== 19 passed, 1 warning in 0.78s ===========================================
```

À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

`@pytest.mark.parametrize sert a parametrer la fonction de test afin qu'elle s'execute plusieurs fois en lui precisant le schema de la liste qu'on lui passe. Pour cette fonction pytest compte 5 tests car elle s'execute plusieurs fois, une fois pour chaque element de la liste CAS_REFUSES.

## 2. ruff

Sortie de `ruff check .` dans `TP/TP1` :

```
All checks passed!
```

Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?

ruff permet de checker la qualite du code tandis que pytest permet une verification des test implementes dans le dossier tests et la bonne execution du code.

## 3. Mise en place du TP2 (dans `TP/TP2`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
========================================= 2 failed, 16 passed, 1 warning in 0.95s =========================================
```

Quels sont les deux tests qui échouent, et que reçoivent-ils au lieu de 401 ?

les deux tests qui echouent sont test_missing_key_is_rejected et test_wrong_key_is_rejected. Ils recoivent 200 au lieu de 401.

## 4. La clé API (sprint 1)

Votre fonction `require_api_key()` (`maintai/api/security.py`) :

```python
def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Refuse la requête si la clé est absente ou fausse."""
    # TODO (TP2) : Comparez x_api_key à get_settings().api_key avec secrets.compare_digest : 401 si la clé est absente ou fausse, 500 si le serveur n'a pas de clé configurée
    if not get_settings().api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API non configurée côté serveur",
        )

    if not x_api_key or not secrets.compare_digest(x_api_key, get_settings().api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide ou manquante",
        )
```

Votre ligne `router = ...` dans `maintai/api/main.py` :

```python
router = APIRouter(prefix="/v1", dependencies= [Depends(require_api_key)])
```

Après avoir écrit `security.py` seul (sans toucher au router), combien de tests échouent ? Pourquoi ?

2 tests echouent car on definit juste la fonction require api key sans l'integrer dans les dependances du router.

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
============================================== 18 passed, 1 warning in 1.03s ==============================================
```

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête                                       | Code obtenu | Réponse (le corps JSON)                                                                                                                                  |
| --------------------------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /health`, sans clé                       | 200         | {"status":"ok","model_loaded":true}                                                                                                                      |
| `POST /v1/predict`, relevé normal, sans clé   | 401         | {"detail":"Clé API invalide ou manquante"}                                                                                                               |
| `POST /v1/predict`, relevé normal, fausse clé | 401         | {"detail":"Clé API invalide ou manquante"}%                                                                                                              |
| `POST /v1/predict`, relevé normal, bonne clé  | 200         | {"failure_probability":0.9475,"alert":true,"threshold":0.3,"model_version":"2026-11-03T18:18:27Z"}%                                                      |
| `POST /v1/predict`, 500 °C, sans clé          | 401         | {"detail":"Clé API invalide ou manquante"}                                                                                                               |
| `POST /v1/predict`, 500 °C, bonne clé         | 422         | {"detail":[{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150.0}}]}% |

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

car une requete renvoie un code pour manque de cle api tandis que la deuxieme requete renvoie un code car la valeur envoyee est superieure a la valeur maximale acceptable par l'api.

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

on obtient le code 500 car le serveur ne trouve pas le .env qui contient la cle api interne au serveur. On obtient pas 401 car il s'agit d'une erreure interne au serveur.

## 5. La page web (sprint 2)

Votre code `fetch` (le contenu du `addEventListener` dans `web/index.html`) :

```javascript
document.getElementById("go").addEventListener("click", async () => {
  const reading = Object.fromEntries(
    FEATURES.map((f) => [f, Number(document.getElementById(f).value)]),
  );
  const url = document.getElementById("url").value.replace(/\/+$/, "");
  const key = document.getElementById("key").value;

  try {
    const response = await fetch(`${url}/v1/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": key,
      },
      body: JSON.stringify(reading),
    });

    const data = await response.json();

    if (!response.ok) {
      show(
        "err",
        `Erreur ${response.status} : ${data.detail || "Erreur de prédiction"}`,
      );
      return;
    }

    if (data.failure_predicted) {
      show("alert", ` Panne prédite (Probabilité : ${data.probability})`);
    } else {
      show("ok", `Équipement OK (Probabilité de panne : ${data.probability})`);
    }
  } catch (error) {
    show("err", `Impossible de contacter l'API : ${error.message}`);
  }
});
```

Ce qu'affiche la page (servie sur le port 5500) :

| Essai                     | Ce qu'affiche la page                            |
| ------------------------- | ------------------------------------------------ |
| relevé normal, bonne clé  | Équipement OK (Probabilité de panne : undefined) |
| 500 °C, bonne clé         | Erreur 422 : [object Object]                     |
| relevé normal, fausse clé | Erreur 401 : Clé API invalide ou manquante       |

**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?
la page dit Impossible de contacter l'API : Failed to fetch la console F12 dis CORS error avec un statut 400

Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?

Car les addresses autorisees a envoyer des requetes sont http://localhost:5500 et http://127.0.0.1:5500. Aussi CORS ne s'applique que cote navigateur donc quand on execute qu'a partir du terminal ca ne fonctionne pas.

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

nous avons 4 tests qui echouent avec les codes 401. Le test qui passe quand meme est le test ("mauvaise route", "v1/pred", {\*\*VALID}, 404) car il renvoie le code 404 sans verifier la cle api

Dernière ligne de `python -m pytest` avec `headers=HEADERS` :

```
===================================================================== 23 passed in 1.29s ======================================================================
```

## 7. Questions de compréhension

1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?
   401 concerne l'authentification(avec la cle inexistante ou invalide). 422 concerne la validation des donnees. 403 concerne une cle api valide mais nous n'avons pas les droits necessaires pour faire la requete.
2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?
   la cle n'est ni dans le code ni dans le git pour eviter une fuite de la cle car elle est confidentielle. .env contient la cle interne du serveur et les addresses qui peuvent interroger le serveur. .env.example contient la structure du .env. c'est le .example qui peut etre commite
3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?
   si la cle voyage dans un URL elle va etre enregistre dans les fichier logs du serveur ce qui peut constituer une fuite de la cle.
4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?
   le == s'arrete a la premiere occurence d'erreur donnant des indices aux attaqueurs qui peuvent deviner la cle tandis que la deuxieme methode verifie avec un temps constant.
5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même origine ?
   une origine est definie par le triplet protocole, hote et port. `http://localhost:5500` et `http://localhost:8000` ne sont pas les memes origine car leurs numeros de ports different.

## 8. Le rendu Git

- Lien de la pull request : https://github.com/nisrineregragui/projet_dai
- Le tag `tp2` existe sur GitHub : non
- `git status` avant le commit : le fichier `.env` apparaissait-il ? non
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  aucune pull request n'a ete effectue

## 9. Ce qui reste flou

rien n'est flou
