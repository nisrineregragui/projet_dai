# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** G2 · **Membres :** Wissal ARRAS · **Date :** 10/11/2026 · **Temps :** 18:22

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP3. Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```text
======================================= 5 failed, 18 passed, 1 warning in 1.30s =======================================
```

Quels fichiers de tests échouent, et quelle erreur donnent-ils ?

Deux fichiers de test échouent : `test_client.py` avec l'erreur `NotImplementedError: TP3 sprint 2 : MaintaiClient.predict` et `test_ui.py` qui donne l'erreur `IndexError: list index out of range`.

---

## 2. Lancer Streamlit

Lancez d'abord `streamlit run ui/app.py`. Que s'affiche-t-il dans le navigateur ?

```text
ModuleNotFoundError: No module named 'maintai'
Traceback:
File "/Users/adam/Documents/DAI/Session_6/TP3/maintai-starter-tp3 2/ui/app.py", line 9, in <module>
    from maintai.client import APIError, MaintaiClient
```

Lancez ensuite `python -m streamlit run ui/app.py`. Pourquoi cette commande fonctionne-t-elle et pas la première ?

Car la première s'exécute à partir du dossier `/ui` et ne peut pas accéder aux autres dossiers.

---

## 3. Sprint 1 : l'onglet « Données »

Votre code de l'onglet « Données » (de `c1, c2, c3 = ...` jusqu'au nuage de points) :

```python
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Nombre de relevés", f"{len(df)}")

with col2:
    taux_panne = df["failure"].mean() * 100
    st.metric("Taux de panne", f"{taux_panne:.1f} %")

with col3:
    temp_moy = df["temperature_c"].mean()
    st.metric("Température moyenne", f"{temp_moy:.1f} °C")

st.divider()

var_choisie = st.selectbox("Choisir une variable à analyser", FEATURES)

if var_choisie:
    df_temp = df.copy()
    df_temp["tranche"] = pd.cut(df_temp[var_choisie], bins=10)

    stats_tranche = (
        df_temp.groupby("tranche", observed=False)
        .agg(
            failure=("failure", "mean"),
            val_moyenne=(var_choisie, "mean")
        )
        .reset_index()
    )
    stats_tranche["failure"] = stats_tranche["failure"].mul(100)
    stats_tranche = stats_tranche[stats_tranche["failure"] > 0].copy()
    stats_tranche["Moyenne"] = stats_tranche["val_moyenne"].round(1).astype(str)

    st.subheader(f"Taux de panne par valeur moyenne de {var_choisie}")
    st.bar_chart(
        stats_tranche,
        x="Moyenne",
        y="failure",
        x_label=f"Moyenne de {var_choisie}",
        y_label="Taux de panne (%)"
    )

st.divider()

st.subheader("Température vs Vibration (par statut de panne)")
st.scatter_chart(
    df,
    x="temperature_c",
    y="vibration_mm_s",
    color="failure",
)
```

| **Indicateur** | **Valeur affichée** |
|---|---:|
| Relevés | 5000 |
| Taux de panne | 13.6 |
| Température moyenne | 59.8 |

Choisissez `vibration_mm_s` dans la liste. Comment évolue le taux de panne quand la vibration augmente ?

Le taux de panne augmente.

Ajoutez un `print("relance")` en haut de `ui/app.py`, puis déplacez un curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre sur le fonctionnement de Streamlit ?

« relance » s'affiche dans le terminal quand on déplace le curseur. Cela montre que Streamlit réexécute tout le code à chaque interaction.

À quoi sert `@st.cache_data` sur la fonction `charger` ?

Il permet de mémoriser le résultat de la fonction `charger(path)` pour éviter de tout relire le fichier.

---

## 4. Sprint 2 : l'onglet « Prédiction »

Votre méthode `predict` (`maintai/client.py`) :

```python
def predict(self, reading: dict) -> dict:
    """Envoie un relevé ; lève APIError si l'API refuse, httpx.HTTPError si elle est injoignable."""
    headers = {}
    if self.api_key:
        headers["X-API-Key"] = self.api_key

    r = self.http.post("/v1/predict", json=reading, headers=headers)

    if r.status_code != 200:
        try:
            detail = r.json().get("detail")
        except Exception:
            detail = r.text
        raise APIError(r.status_code, detail)

    return r.json()
```

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```text
========================== 23 passed, 1 warning in 1.31s ==========================
```

Avec l'API lancée (`uvicorn maintai.api.main:app --reload --env-file .env`) :

| **Essai** | **Ce qu'affiche Streamlit** |
|---|---|
| Valeurs par défaut, bonne clé | 95 % avec message ⚠️ ALERTE : Risque de panne élevé ! |
| Valeurs par défaut, fausse clé | Erreur API 401 : Clé API absente ou invalide |
| API arrêtée (Ctrl+C dans le terminal d'uvicorn) | API injoignable ... |

Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la prédiction fonctionne. Pourquoi ?

Car la requête vient du côté serveur et pas du côté navigateur.

---

## 5. Questions de compréhension

**1. Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?**

Dans le TP2, c'est le navigateur web client via JavaScript. Dans le TP3, c'est le serveur Python de l'application via `httpx`.

**2. Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'uvicorn ?**

L'application s'exécute en mémoire dans le même processus Python, sans nécessiter un serveur web Uvicorn actif.

**3. Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?**

Pour un client, Streamlit est plus adapté car nous pouvons créer une interface interactive. Pour un technicien de maintenance, HTML et JavaScript sont plus adaptés car cela évite de recharger tout le code à chaque interaction.

---

## 6. Le rendu Git

- **Lien de la pull request :** https://github.com/nisrineregragui/projet_dai/
- **Le tag `tp3` existe sur GitHub :** non
- **`git status` avant le commit :** `.env`, `data/` ou `models/` apparaissaient-ils ? Non.

---

## 7. Ce qui reste flou

Tout est clair.