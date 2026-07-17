import streamlit as st
import math

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Nomogramme Ostéosarcome Calibré",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {background-color: #f4f8fb;}
    h1 {color: #1E3A8A; font-weight: 800;}
    h2, h3 {color: #047857;}
    .stProgress > div > div > div > div {background-color: #EF4444;}
    .highlight-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .stat-box {
        font-family: monospace;
        font-size: 0.9em;
        color: #555;
        background-color: #eee;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Nomogramme Statistique : Ostéosarcome des Membres")
st.subheader("Modèle de Cox Calibré sur la Littérature - Récidive à 1 an")
st.markdown("---")

# --- COEFFICIENTS B CALIBRÉS (LITTÉRATURE + ABSTRACT) ---
# L'indice pronostique (PI) utilise la formule ln(Hazard Ratio)

B_AGE = 0.005
B_VOL = 0.002  # Le volume augmente progressivement le risque
B_CRP = 0.008  # Une CRP qui flambe influence désormais significativement le risque

dict_sex = {"Masculin": 0.0, "Féminin": -0.150}

# Calibration stricte selon la littérature oncologique
dict_histo = {
    "Ostéoblastique (Conventionnel - Référence)": 0.0,
    "Fibroblastique (Similaire à la référence)": 0.0,
    "Télangiectasique (Similaire sous chimio moderne)": 0.100,
    "Chondroblastique (Légèrement moins bon)": 0.300,
    "Périosté (Bon pronostic)": -0.700,
    "Parostéal (Excellent pronostic)": -1.200,
    "À petites cellules (Mauvais pronostic)": 0.900,
    "Secondaire - Post-radique (Très mauvais)": 1.500,
    "Secondaire - Sur Maladie de Paget (Très mauvais)": 1.500,
    "Secondaire - Sur ostéomyélite chronique / Infection (Très mauvais)": 1.500,
    "Secondaire - Sur infarctus osseux (Très mauvais)": 1.500
}

# Ancré sur le résumé de l'étude (HR 3.5)
dict_meta = {"Non (Référence)": 0.0, "Oui (Métastases primaires)": 1.252}

# Ancré sur le résumé de l'étude (HR 3.0 pour mauvaise réponse)
dict_huvos = {
    "Grade IV - Nécrose 100% (Référence)": 0.0,
    "Grade III - Nécrose 90-99%": 0.200,
    "Grade II - Nécrose 50-89% (Mauvaise réponse)": 0.800,
    "Grade I - Nécrose 0-49% (Très mauvaise réponse)": 1.100
}

# Ancré sur le résumé de l'étude (HR 2.4 pour R1)
dict_margin = {
    "R0 - Marges Saines (Référence)": 0.0,
    "R1 - Marges Limites / Microscopiques": 0.875,
    "R2 - Résidu Macroscopique": 1.600 
}

# --- INTERFACE UTILISATEUR ---
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.header("📋 Profil du Patient")
    st.markdown('<div class="highlight-card">', unsafe_allow_html=True)
    
    age = st.number_input("🎂 1. Âge (années)", min_value=0, max_value=100, value=21, step=1)
    sexe = st.selectbox("🚻 2. Sexe", list(dict_sex.keys()))
    vol = st.number_input("📏 3. Volume tumoral (cm³)", min_value=0, max_value=5000, value=250, step=10)
    meta = st.selectbox("🩻 4. Métastases au diagnostic", list(dict_meta.keys()))
    crp = st.number_input("🩸 5. CRP (mg/L)", min_value=0, max_value=500, value=10, step=1)
    
    histo = st.selectbox("🔬 6. Type Histologique", list(dict_histo.keys()))
    marge = st.selectbox("🔪 7. Marges chirurgicales", list(dict_margin.keys()))
    huvos = st.selectbox("🧬 8. Score de Huvos", list(dict_huvos.keys()))
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- CALCUL DU MODÈLE DE COX ---
PI = (
    (age * B_AGE) +
    (dict_sex[sexe]) +
    (dict_histo[histo]) +
    (vol * B_VOL) +
    (dict_meta[meta]) +
    (crp * B_CRP) +
    (dict_huvos[huvos]) +
    (dict_margin[marge])
)

# Calibration de la survie de base (S0)
S0_12 = 0.760 
hazard_ratio = math.exp(PI)
prob_survie = math.pow(S0_12, hazard_ratio)

prob_recidive = (1 - prob_survie) * 100

with col2:
    st.header("📊 Calcul de Probabilité")
    
    subcol1, subcol2 = st.columns(2)
    with subcol1:
        st.metric(label="Indice Pronostique (PI)", value=f"{PI:.3f}")
    with subcol2:
        st.metric(label="Risque de Récidive à 1 an", value=f"{prob_recidive:.1f} %")
    
    st.progress(int(min(max(prob_recidive, 0), 100))) 
    
    st.markdown("### 🧬 Analyse Statistique du Patient")
    st.markdown('<div class="stat-box">', unsafe_allow_html=True)
    st.write(f"**Hazard Ratio (HR) cumulé pour ce patient :** {hazard_ratio:.2f}")
    st.write("Ce modèle intègre les Hazard Ratios validés par votre analyse multivariée (N=214) et la littérature internationale.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 🎯 Classement (Basé sur la cohorte)")
    
    # Stratification alignée sur votre présentation orale
    if prob_recidive <= 12:
        st.success("🟢 **GROUPE 1 (~6% de risque moyen)** : Risque très faible. Surveillance standard.")
    elif prob_recidive <= 28:
        st.info("🔵 **GROUPE 2 (~18% de risque moyen)** : Risque modéré. Vigilance clinique.")
    elif prob_recidive <= 50:
        st.warning("🟡 **GROUPE 3 (~38% de risque moyen)** : Haut risque. Surveillance radiologique rapprochée.")
    else:
        st.error("🔴 **GROUPE 4 (~65% de risque moyen)** : Très haut risque. Candidat pour stratégies de seconde ligne ou essais cliniques.")

st.markdown("---")
st.caption("Modèle clinico-statistique. Les poids des variables ont été calibrés pour refléter la cohorte d'étude et les consensus de la littérature oncologique.")
