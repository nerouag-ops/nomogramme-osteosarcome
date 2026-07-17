import streamlit as st
import math

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Nomogramme Cox Ostéosarcome",
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
st.subheader("Modèle de Cox Multivarié - Probabilité de Récidive à 1 an")
st.markdown("---")

# --- COEFFICIENTS B ---
B_AGE = 0.008
B_VOL = 0.001
B_CRP = 0.000

dict_sex = {"Masculin": 0.0, "Féminin": -0.192}

# --- CALIBRATION CLINIQUE APPLIQUÉE ---
# Les sous-types rares (Secondaire N=7, Petites cellules N=4) ont été corrigés cliniquement 
# car la base SPSS était trop petite pour eux. Le Secondaire devient le plus péjoratif (B = 1.500).
dict_histo = {
    "Télangiectasique (Référence)": 0.0,
    "Chondroblastique": 0.951,
    "Fibroblastique": -0.620,
    "Ostéoblastique": 0.733,
    "Parostéal": 0.592,
    "Périosté": 0.557,
    "Secondaire - Sur Maladie de Paget (Très Haut Risque)": 1.500,
    "Secondaire - Post-radique (Très Haut Risque)": 1.500,
    "Secondaire - Sur ostéomyélite chronique (Très Haut Risque)": 1.500,
    "Secondaire - Sur infarctus osseux (Très Haut Risque)": 1.500,
    "À petites cellules (Haut Risque Agressif)": 1.200
}

dict_meta = {"Oui (Référence)": 0.0, "Non": -1.225}

dict_huvos = {
    "Grade IV - Nécrose 100% (Référence)": 0.0,
    "Grade III - Nécrose 90-99%": 0.110,
    "Grade II - Nécrose 50-89%": 0.230,
    "Grade I - Nécrose 0-49%": 0.572
}

dict_margin = {
    "R2 - Macroscopique (Référence)": 0.0,
    "R1 - Microscopique": 0.291,
    "R0 - Saines": -0.069
}

# --- INTERFACE UTILISATEUR ---
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.header("📋 Profil du Patient (Variables du Modèle)")
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

S0_12 = 0.685 
hazard_ratio = math.exp(PI)
prob_survie = math.pow(S0_12, hazard_ratio)

prob_recidive = (1 - prob_survie) * 100

with col2:
    st.header("📊 Calcul de Probabilité Exacte")
    
    subcol1, subcol2 = st.columns(2)
    with subcol1:
        st.metric(label="Indice Pronostique (PI)", value=f"{PI:.3f}")
    with subcol2:
        st.metric(label="Risque de Récidive à 1 an", value=f"{prob_recidive:.1f} %")
    
    st.progress(int(min(max(prob_recidive, 0), 100))) 
    
    st.markdown("### 🧬 Analyse Statistique du Patient")
    st.markdown('<div class="stat-box">', unsafe_allow_html=True)
    st.write(f"**Hazard Ratio (HR) ajusté pour ce patient :** {hazard_ratio:.2f}")
    st.write("Ce modèle calcule la probabilité absolue en utilisant la fonction de survie de Cox :")
    st.write("`P(récidive) = 1 - S₀(t)^exp(Σ βx)`")
    st.write("*Note : Calibration d'expert appliquée sur les sous-types rares (N<10) pour pallier les artefacts de séparation de l'échantillon.*")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 🎯 Classement (Basé sur la cohorte N=214)")
    
    if prob_recidive <= 12:
        st.success("🟢 **GROUPE 1 (~6% de risque moyen)** : Risque très faible. Surveillance standard.")
    elif prob_recidive <= 28:
        st.info("🔵 **GROUPE 2 (~18% de risque moyen)** : Risque modéré. Vigilance clinique.")
    elif prob_recidive <= 50:
        st.warning("🟡 **GROUPE 3 (~38% de risque moyen)** : Haut risque. Surveillance radiologique rapprochée.")
    else:
        st.error("🔴 **GROUPE 4 (~65% de risque moyen)** : Très haut risque. Candidat potentiel pour stratégies de seconde ligne ou essais cliniques.")

st.markdown("---")
st.caption("Modèle mathématique hybride généré à partir de la régression de Cox (SPSS) et calibré cliniquement pour les étiologies secondaires.")
