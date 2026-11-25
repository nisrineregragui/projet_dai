import os

import pandas as pd
import streamlit as st

from maintai.client import APIError, MaintaiClient

st.set_page_config(page_title="MaintAI", layout="wide")

DEFAULT_API_URL = os.getenv("MAINTAI_API_URL", "http://localhost:8000")
DEFAULT_DATA_PATH = os.getenv("MAINTAI_DATA_PATH", "data/sensors.csv")

with st.sidebar:
    st.header("Configuration")
    api_url = st.text_input("URL de l'API", value=DEFAULT_API_URL).rstrip("/")
    api_key = st.text_input("Clé API (X-API-Key)", type="password")

st.title("MaintAI — Prédiction de panne")

tab_donnees, tab_prediction = st.tabs(["Données", "Prédiction"])

with tab_donnees:
    st.subheader("Jeu de données capteurs")
    if os.path.exists(DEFAULT_DATA_PATH):
        df = pd.read_csv(DEFAULT_DATA_PATH)
        st.metric("Nombre de relevés", str(len(df)))
        st.dataframe(df, use_container_width=True)
    else:
        st.metric("Nombre de relevés", "0")
        st.info(f"Fichier introuvable : {DEFAULT_DATA_PATH}")

with tab_prediction:
    st.subheader("Nouveau relevé")
    col1, col2 = st.columns(2)
    with col1:
        temperature_c = st.number_input("Température (°C)", value=72.0)
        vibration_mm_s = st.number_input("Vibration (mm/s)", value=6.0)
    with col2:
        load_pct = st.number_input("Charge (%)", value=85.0)
        runtime_hours = st.number_input("Heures de fonctionnement", value=15000.0)

    if st.button("Prédire", type="primary"):
        releve = {
            "temperature_c": temperature_c,
            "vibration_mm_s": vibration_mm_s,
            "load_pct": load_pct,
            "runtime_hours": runtime_hours,
        }
        try:
            client = MaintaiClient(url=api_url, api_key=api_key or None)
            result = client.predict(releve)
            prob = float(result["failure_probability"])
            alert = bool(result.get("alert", False))

            st.metric("Probabilité de panne", f"{round(prob * 100)} %")
            if alert:
                st.error(f"ALERTE : risque de panne élevé ({prob:.4f})")
            else:
                st.success(f"Fonctionnement normal ({prob:.4f})")
            st.json(result)
        except APIError as exc:
            st.error(f"Erreur API ({exc.status_code}) : {exc.detail}")
        except Exception as exc:
            st.error(f"API injoignable ({api_url}) : {exc}")