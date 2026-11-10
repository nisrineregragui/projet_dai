ARRAS WISSAL G2 
1. Mise en place (dans TP/TP3)
Dernière ligne de python -m pytest juste après la mise en place :

Plaintext


========================== 2 failed, 21 passed in 1.45s ==========================
Quels fichiers de tests échouent, et quelle erreur donnent-ils ?

Le fichier tests/test_ui.py échoue avec les tests test_ui_shows_the_data et test_ui_shows_the_prediction. Ils renvoient des AssertionError car les fonctionnalités de l'interface Streamlit (ui/app.py) et du client (maintai/client.py) ne sont encore que des squelettes (st.info(...)).

2. Lancer Streamlit
Lancez d'abord streamlit run ui/app.py. Que s'affiche-t-il dans le navigateur ?

Plaintext


ModuleNotFoundError: No module named 'maintai'
Lancez ensuite python -m streamlit run ui/app.py. Pourquoi cette commande fonctionne-t-elle et pas la première ?

La commande python -m streamlit ajoute automatiquement le répertoire courant (la racine du projet) dans le chemin d'importation de Python (sys.path). Cela permet à Python de trouver et d'importer le package maintai. La commande directe streamlit run exécute le script sans inclure automatiquement le dossier racine au sys.path.

3. Sprint 1 : l'onglet « Données »
Votre code de l'onglet « Données » (de c1, c2, c3 = ... jusqu'au nuage de points) :

Python


    # 1. trois indicateurs côte à côte
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

    # 2. liste déroulante pour choisir une variable parmi FEATURES
    var_choisie = st.selectbox("Choisir une variable à analyser", FEATURES)

    # 3. taux de panne par tranche de cette variable (moyenne sur l'axe X, hors 0%)
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

    # 4. nuage de points température / vibration, coloré par panne
    st.subheader("Température vs Vibration (par statut de panne)")
    st.scatter_chart(
        df,
        x="temperature_c",
        y="vibration_mm_s",
        color="failure",
    )
Indicateur	Valeur affichée
Relevés	2000
Taux de panne	5.0 %
Température moyenne	70.3 °C
Choisissez vibration_mm_s dans la liste. Comment évolue le taux de panne quand la vibration augmente ?

Le taux de panne augmente fortement à mesure que la valeur de vibration augmente, particulièrement lorsque la vibration moyenne dépasse les tranches élevées.

Ajoutez un print("relance") en haut de ui/app.py, puis déplacez un curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre sur le fonctionnement de Streamlit ?

Le mot "relance" s'affiche dans le terminal à chaque interaction. Cela montre que Streamlit réexécute l'intégralité du script Python de haut en bas à chaque fois que l'utilisateur interagit avec un composant graphique.

À quoi sert @st.cache_data sur la fonction charger ?

@st.cache_data sert à garder en mémoire le résultat de la fonction charger(path). Ainsi, le fichier CSV est lu une seule fois sur le disque lors du premier chargement, évitant de relire le fichier à chaque réexécution du script.

4. Sprint 2 : l'onglet « Prédiction »
Votre méthode predict (maintai/client.py) :

Python


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
Dernière ligne de python -m pytest à la fin du sprint 2 :

Plaintext


========================== 23 passed, 1 warning in 1.31s ==========================
Avec l'API lancée (uvicorn maintai.api.main:app --reload --env-file .env) :

Essai	Ce qu'affiche Streamlit
valeurs par défaut, bonne clé	Probabilité de panne : 95 % avec message d'erreur ⚠️ ALERTE : Risque de panne élevé !
valeurs par défaut, fausse clé	Encadré d'avertissement Erreur API 401 : Invalid API key
API arrêtée (Ctrl+C dans le terminal d'uvicorn)	Encadré d'erreur API injoignable ...
Le port 8501 n'est pas dans MAINTAI_CORS_ORIGINS, et pourtant la prédiction fonctionne. Pourquoi ?

Parce que la requête HTTP vers l'API FastAPI n'est pas envoyée par le navigateur de l'utilisateur, mais par le serveur Python de Streamlit via la librairie httpx (communication de serveur à serveur). La politique CORS (Cross-Origin Resource Sharing) est une restriction appliquée uniquement par les navigateurs web.

5. Questions de compréhension
Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?

TP2 : C'est le navigateur client qui envoie la requête HTTP directement à l'API via le code JavaScript (fetch).

Streamlit (TP3) : C'est le serveur Python de Streamlit qui envoie la requête HTTP à l'API via httpx, puis génère et renvoie le rendu visuel HTML au navigateur.

Pourquoi les tests de test_client.py n'ont-ils pas besoin d'uvicorn ?

Les tests utilisent le TestClient de FastAPI/Starlette directement passé au client httpx. L'application tourne en mémoire dans le même processus Python sans qu'un vrai serveur Web réseau Uvicorn n'ait besoin d'écouter sur un port HTTP.

Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?

Démonstration à un client : Streamlit, car cela permet de prototyper et d'afficher des données interactives et des prédictions très rapidement en pur Python sans complexité d'intégration Web.

Application pour technicien : HTML + JavaScript, car l'application est plus rapide, plus personnalisable, gère mieux l'état côté client, consomme moins de ressources serveur et ne recharge pas tout le script complet à chaque clic sur le terrain.

6. Le rendu Git
Lien de la pull request : [https://github.com/votre-org/maintai-starter-tp3/pull/1](https://github.com/votre-org/maintai-starter-tp3/pull/1)

Le tag tp3 existe sur GitHub : oui

git status avant le commit : .env, data/ ou models/ apparaissaient-ils ? non

7. Ce qui reste flou
Rien à signaler, le flux de données entre Streamlit, le client HTTP et l'API FastAPI est clair.
