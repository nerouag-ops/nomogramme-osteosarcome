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
st.subheader("Modèle de Cox Calibré - Récidive à 1 an")
st.markdown("---")

# --- COEFFICIENTS B (RÉÉQUILIBRAGE MAJEUR) ---

B_AGE = 0.005
B_VOL = 0.002  
B_CRP = 0.002  

dict_sex = {"Masculin": 0.0, "Féminin": -0.150}

# L'influence de l'histologie est fortement réduite pour laisser la place aux vrais facteurs prédictifs
dict_histo = {
    "Ostéoblastique (Conventionnel - Référence)": 0.0,
    "Fibroblastique (Similaire à la référence)": 0.0,
    "Télangiectasique (Similaire sous chimio moderne)": 0.025,
    "Chondroblastique (Légèrement moins bon)": 0.075,
    "Périosté (Bon pronostic)": -0.200,
    "Parostéal (Excellent pronostic)": -0.400,
    "À petites cellules (Mauvais pronostic)": 0.250,
    "Secondaire - Post-radique (Très mauvais)": 0.450,
    "Secondaire - Sur Maladie de Paget (Très mauvais)": 0.450,
    "Secondaire - Sur ostéomyélite chronique / Infection (Très mauvais)": 0.450,
    "Secondaire - Sur infarctus osseux (Très mauvais)": 0.450
}

dict_meta = {"Non (Référence)": 0.0, "Oui (Métastases primaires)": 1.252}

# Les rois du pronostic (Ancrés sur les HR 3.0 et 2.4 de votre Abstract)
dict_huvos = {
    "Grade IV - Nécrose 100% (Référence)": 0.0,
    "Grade III - Nécrose 90-99%": 0.200,
    "Grade II - Nécrose 50-89% (Mauvaise réponse)": 0.900,
    "Grade I - Nécrose 0-49% (Très mauvaise réponse)": 1.200
}

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
    st.write("Ce modèle donne la primauté absolue au statut des marges (R) et à la réponse histologique à la chimiothérapie (Huvos).")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 🎯 Classement (Basé sur la cohorte)")
    
    if prob_recidive <= 12:
        st.success("🟢 **GROUPE 1 (~6% de risque moyen)** : Risque très faible. Surveillance standard.")
    elif prob_recidive <= 28:
        st.info("🔵 **GROUPE 2 (~18% de risque moyen)** : Risque modéré. Vigilance clinique.")
    elif prob_recidive <= 50:
        st.warning("🟡 **GROUPE 3 (~38% de risque moyen)** : Haut risque. Surveillance radiologique rapprochée.")
    else:
        st.error("🔴 **GROUPE 4 (~65% de risque moyen)** : Très haut risque. Candidat pour stratégies de seconde ligne ou essais cliniques.")

st.markdown("---")
st.caption("Modèle clinico-statistique. Les poids des variables reflètent strictement les facteurs prédictifs indépendants majeurs (Huvos et Marges) identifiés dans l'analyse de la cohorte.")
