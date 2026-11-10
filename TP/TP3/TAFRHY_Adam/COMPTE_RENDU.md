# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** G2 · **Membres :** Adam TAFRHY · **Date :** 10/11/2026 **Temps**: 18:22

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP3.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
======================================= 5 failed, 18 passed, 1 warning in 1.30s =======================================
```

Quels fichiers de tests échouent, et quelle erreur donnent-ils ?

deux fichiers de test echouent: test_client.py avec ses erreurs NotImplementedError: TP3 sprint 2 : MaintaiClient.predict et test_ui.py qui donne l'erreur IndexError: list index out of range

## 2. Lancer Streamlit

Lancez d'abord `streamlit run ui/app.py`. Que s'affiche-t-il dans le navigateur ?

```
ModuleNotFoundError: No module named 'maintai'
Traceback:
File "/Users/adam/Documents/DAI/Session_6/TP3/maintai-starter-tp3 2/ui/app.py", line 9, in <module>
    from maintai.client import APIError, MaintaiClient
```

Lancez ensuite `python -m streamlit run ui/app.py`. Pourquoi cette commande fonctionne-t-elle et pas la première ?

car la premiere s'execute a partir du dossier /ui et ne peut pas acceder les autres dossiers.

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

| Indicateur          | Valeur affichée |
| ------------------- | --------------- |
| Relevés             | 5000            |
| Taux de panne       | 13.6            |
| Température moyenne | 59.8            |

Choisissez `vibration_mm_s` dans la liste. Comment évolue le taux de panne quand la vibration augmente ?

le taux de panne augmente.

Ajoutez un `print("relance")` en haut de `ui/app.py`, puis déplacez un curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre sur le fonctionnement de Streamlit ?

relance s'affiche dans le terminal quand on deplace le curseur. cela montre que streamlit reexecute tout le code a chaque interaction.

À quoi sert `@st.cache_data` sur la fonction `charger` ?

il permet de memoriser le resultat de la fonction charger(path) pour éviter de tout relire le fichier.

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

```
========================== 23 passed, 1 warning in 1.31s ==========================
```

Avec l'API lancée (`uvicorn maintai.api.main:app --reload --env-file .env`) :

| Essai                                           | Ce qu'affiche Streamlit                               |
| ----------------------------------------------- | ----------------------------------------------------- |
| valeurs par défaut, bonne clé                   | 95 % avec message ⚠️ ALERTE : Risque de panne élevé ! |
| valeurs par défaut, fausse clé                  |
| Erreur API 401 : Clé API absente ou invalide    |
| API arrêtée (Ctrl+C dans le terminal d'uvicorn) | API injoignable ...                                   |

Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la prédiction fonctionne. Pourquoi ?

car la requete vient du cote serveur et pas du cote navigateur.

## 5. Questions de compréhension

1. Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?
   dans le tp2 c'est le navigateur web client via javascript. dans le tp3, c'est le serveur python de l'application via httpx
2. Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'uvicorn ?
   l'application s'execute en memoire dans le meme processus python, sans necessiter un serveur web Uvicorn actif
3. Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?
   pour un client streamlit est plus adapte car nous pouvons creer une interface interactive. pour un technicien technique de maintenance html et javascript est plus adapte car ca evite de recharger tout le code a chaque interaction

## 6. Le rendu Git

- Lien de la pull request : https://github.com/nisrineregragui/projet_dai/
- Le tag `tp3` existe sur GitHub : non
- `git status` avant le commit : `.env`, `data/` ou `models/` apparaissaient-ils ? non

## 7. Ce qui reste flou

Tout est clair
