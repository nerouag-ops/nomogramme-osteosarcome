import streamlit as st
import math

st.set_page_config(page_title="Nomogramme Osteosarcome 2026", page_icon="🦴", layout="centered")

st.title("🦴 Score Prédictif & Nomogramme Dynamique (V3)")
st.subheader("Prédiction du risque de récidive précoce à 1 an dans l'ostéosarcome des membres")
st.markdown("---")

st.sidebar.header("🔬 Paramètres Patient")

volume_tumoral = st.sidebar.selectbox(
    "1. Volume tumoral initial estimé",
    options=["Inférieur ou égal à 90 cm³ (0 point)", "Supérieur à 90 cm³ (2 points)"]
)

marges_chir = st.sidebar.selectbox(
    "2. Qualité des marges de résection chirurgicale",
    options=["Marges saines R0 (0 point)", "Marges infiltrées microscopiques R1 (1 point)", "Marges infiltrées macroscopiques R2 (2 points)"]
)

reponse_huvos = st.sidebar.selectbox(
    "3. Réponse histologique (Classification de Huvos)",
    options=[
        "Grade IV : Nécrose à 100% / Aucune tumeur viable (1 point)", 
        "Grade III : Nécrose à 90-99% / Rares foyers viables (2 points)", 
        "Grade II : Nécrose à 50-89% / Zones viables importantes (3 points)", 
        "Grade I : Nécrose à 0-49% / Tumeur quasi intacte ou peu altérée (4 points)"
    ]
)

score_total = 0

if "Supérieur à 90" in volume_tumoral:
    score_total += 2

if "R1" in marges_chir:
    score_total += 1
elif "R2" in marges_chir:
    score_total += 2

if "Grade IV" in reponse_huvos:
    score_total += 1
elif "Grade III" in reponse_huvos:
    score_total += 2
elif "Grade II" in reponse_huvos:
    score_total += 3
elif "Grade I" in reponse_huvos:
    score_total += 4

intercept = -4.2
beta_score = 0.92
log_odds = intercept + (beta_score * score_total)
probabilite_exacte = (1 / (1 + math.exp(-log_odds))) * 100

st.header("📊 Évaluation Individualisée du Risque")
col1, col2 = st.columns(2)

with col1:
    st.metric(label="Score Total du Patient", value=f"{score_total} / 8 Points")
with col2:
    st.metric(label="Probabilité de Récidive à 1 an", value=f"{probabilite_exacte:.1f} %")

st.markdown("---")
st.header("📋 Orientation Thérapeutique & Suivi Imagerie")

if score_total <= 2:
    st.success(f"### PROFIL : FAIBLE RISQUE ({probabilite_exacte:.1f} %)\nSurveillance standardisée (TDM thoracique et radiographie locale tous les 3 à 4 mois).")
elif 3 <= score_total <= 5:
    st.warning(f"### PROFIL : RISQUE INTERMÉDIAIRE ({probabilite_exacte:.1f} %)\nSuivi impératif par TDM thoracique et IRM locale stricte tous les 3 mois au cours de la première année. Discussion en RCP.")
else:
    st.error(f"### PROFIL : HAUT RISQUE ({probabilite_exacte:.1f} %)\nAlternance TDM thoracique Haute Résolution et IRM/TEP tous les 2 mois pour intercepter les métastases pulmonaires.")

st.markdown("---")
st.caption("⚠️ Outil d'aide à la décision clinique recalibré en 2026.")