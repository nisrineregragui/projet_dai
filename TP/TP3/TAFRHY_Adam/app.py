"""Interface Streamlit de MaintAI : explorer les données, puis demander une prédiction à l'API.

Lancement (depuis la racine du projet) : python -m streamlit run ui/app.py
"""
import httpx
import pandas as pd
import streamlit as st

from maintai.client import APIError, MaintaiClient
from maintai.config import FEATURES, get_settings

st.set_page_config(page_title="MaintAI", page_icon="🔧")
st.title("MaintAI · prédiction de panne")
print("relance")

@st.cache_data
def charger(path) -> pd.DataFrame:
    # Lu une seule fois : Streamlit relance tout le script à chaque clic
    return pd.read_csv(path)


with st.sidebar:
    url = st.text_input("URL de l'API", "http://localhost:8000")
    cle = st.text_input("Clé API", type="password")

onglet_donnees, onglet_prediction = st.tabs(["Données", "Prédiction"])

# Sprint 1 : explorer les données
with onglet_donnees:
    df = charger(get_settings().data_path)
    # TODO TP3 sprint 1 :
    #   1. trois indicateurs côte à côte (st.columns, puis .metric) :
    #      le nombre de relevés, le taux de panne (df.failure.mean()), la température moyenne
    #   2. une liste déroulante (st.selectbox) pour choisir une variable parmi FEATURES
    #   3. le taux de panne par tranche de cette variable (pd.cut, groupby), en barres (st.bar_chart)
    #   4. un nuage de points température / vibration, coloré par panne (st.scatter_chart)
    st.info("Sprint 1 : les indicateurs et les graphiques viendront ici.")
    df = charger(get_settings().data_path)

    # 1. Trois indicateurs côte à côte
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

    # 2. Liste déroulante pour choisir une variable parmi FEATURES
    var_choisie = st.selectbox("Choisir une variable à analyser", FEATURES)

    # 3. Taux de panne par tranche de cette variable, en diagramme en barres
    if var_choisie:
        df_temp = df.copy()
        # Découpage en 10 tranches
        df_temp["tranche"] = pd.cut(df_temp[var_choisie], bins=10)

        # Calcul simultané du taux de panne et de la moyenne de la variable par tranche
        stats_tranche = (
            df_temp.groupby("tranche", observed=False)
            .agg(
                failure=("failure", "mean"),
                val_moyenne=(var_choisie, "mean")
            )
            .reset_index()
        )

        # Conversion du taux de panne en pourcentage
        stats_tranche["failure"] = stats_tranche["failure"].mul(100)

        # 1. Ne garder que les barres dont le taux de panne est supérieur à 0
        stats_tranche = stats_tranche[stats_tranche["failure"] > 0].copy()

        # 2. Utiliser la valeur moyenne arrondie pour l'axe X (au lieu de l'intervalle)
        stats_tranche["Moyenne"] = stats_tranche["val_moyenne"].round(1).astype(str)

        st.subheader(f"Taux de panne par valeur moyenne de {var_choisie}")
        st.bar_chart(
            stats_tranche,
            x="Moyenne",
            y="failure",
            x_label=f"Moyenne de {var_choisie}",
            y_label="Taux de panne (%)"
        )

    # 4. Nuage de points température / vibration, coloré par panne
    st.subheader("Température vs Vibration (par statut de panne)")
    st.scatter_chart(
        df,
        x="temperature_c",
        y="vibration_mm_s",
        color="failure",
    )

# Sprint 2 : demander une prédiction à l'API
with onglet_prediction:
    with st.form("releve"):
        releve = {
            "temperature_c": st.slider("Température (°C)", -40.0, 150.0, 72.0),
            "vibration_mm_s": st.slider("Vibration (mm/s)", 0.0, 50.0, 6.0),
            "load_pct": st.slider("Charge (%)", 0.0, 100.0, 85.0),
            "runtime_hours": st.number_input("Heures de fonctionnement", 0, 100_000, 15000),
        }
        envoye = st.form_submit_button("Prédire")

    
    if envoye:
        # TODO TP3 sprint 2 :
                #   1. créer MaintaiClient(url, api_key=cle) et appeler .predict(releve)
                #   2. APIError → st.warning avec le code et le message ; httpx.HTTPError → st.error("API injoignable ...")
                #   3. sinon : st.metric("Probabilité de panne", f"{pct} %"), puis st.error (alerte) ou st.success (normal)
        st.info("Sprint 2 : la prédiction s'affichera ici.")
        try:
            client = MaintaiClient(url, api_key=cle)
            res = client.predict(releve)

            if isinstance(res, dict):
                proba = res.get("failure_probability", res.get("probability", res.get("proba", 0.0)))
            else:
                proba = getattr(res, "failure_probability", getattr(res, "probability", getattr(res, "proba", 0.0)))

            pct = int(round(proba * 100)) if proba <= 1.0 else int(round(proba))

            st.metric("Probabilité de panne", f"{pct} %")

            if pct >= 50:
                st.error("⚠️ ALERTE : Risque de panne élevé !")
            else:
                st.success("✅ Statut normal.")

        except APIError as e:
            detail = getattr(e, "detail", str(e))
            code = getattr(e, "status_code", "")
            st.warning(f"Erreur API {code} : {detail}")
        except httpx.HTTPError:
            st.error("API injoignable ...")