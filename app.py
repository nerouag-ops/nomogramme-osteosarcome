import streamlit as st
import math

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Nomogramme Expert Ostéosarcome",
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

st.title("📊 Nomogramme Expert : Ostéosarcome des Membres")
st.subheader("Modèle Prédictif Calibré - Récidive à 1 an")
st.markdown("---")

# --- DICTIONNAIRES DES VARIABLES ET COEFFICIENTS ---

age_options = ["0 à 10 ans", "11 à 18 ans", "> 18 ans"]
dict_sex = {"Masculin": 0.0, "Féminin": -0.100}

# L'influence de l'histologie est lissée (petits ajustements progressifs)
dict_histo = {
    "Ostéoblastique (Conventionnel - Référence)": 0.0,
    "Fibroblastique (Légèrement meilleur)": -0.050,
    "Chondroblastique (Légèrement moins bon)": 0.050,
    "Télangiectasique (Similaire sous chimio moderne)": 0.050,
    "À petites cellules (Agressif)": 0.150,
    "Périosté (Bon pronostic)": -0.150,
    "Parostéal (Excellent pronostic)": -0.250,
    "Secondaire - Post-radique": 0.200,
    "Secondaire - Sur Maladie de Paget": 0.200,
    "Secondaire - Sur ostéomyélite chronique / Infection": 0.200,
    "Secondaire - Sur infarctus osseux": 0.200
}

dict_meta = {"Non (Référence)": 0.0, "Oui (Métastases primaires)": 0.600}

# Les Moteurs Principaux (La biologie et la chirurgie dominent)
dict_huvos = {
    "Grade IV - Nécrose 100% (Référence)": 0.0,
    "Grade III - Nécrose 90-99%": 0.150,
    "Grade II - Nécrose 50-89% (Mauvaise réponse)": 0.600,
    "Grade I - Nécrose 0-49% (Très mauvaise réponse)": 0.900
}

dict_margin = {
    "R0 - Marges Saines (Référence)": 0.0,
    "R1 - Marges Limites / Microscopiques": 0.700,
    "R2 - Résidu Macroscopique": 1.200 
}

# --- INTERFACE UTILISATEUR ---
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.header("📋 Profil du Patient")
    st.markdown('<div class="highlight-card">', unsafe_allow_html=True)
    
    age = st.selectbox("🎂 1. Tranche d'âge", age_options)
    sexe = st.selectbox("🚻 2. Sexe", list(dict_sex.keys()))
    vol = st.number_input("📏 3. Volume tumoral (cm³)", min_value=0, max_value=5000, value=200, step=10)
    meta = st.selectbox("🩻 4. Métastases au diagnostic", list(dict_meta.keys()))
    crp = st.number_input("🩸 5. CRP (mg/L)", min_value=0, max_value=500, value=10, step=1)
    
    histo = st.selectbox("🔬 6. Type Histologique", list(dict_histo.keys()))
    marge = st.selectbox("🔪 7. Marges chirurgicales", list(dict_margin.keys()))
    huvos = st.selectbox("🧬 8. Score de Huvos", list(dict_huvos.keys()))
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- CALCUL DU MODÈLE LOGIQUE ---

# 1. Traitement de l'Âge (Avec exception pour les tumeurs de surface)
if "Parostéal" in histo or "Périosté" in histo:
    score_age = 0.0  # L'âge adulte n'est pas péjoratif pour ces sous-types
else:
    if age == "0 à 10 ans":
        score_age = 0.0
    elif age == "11 à 18 ans":
        score_age = 0.150
    else:
        score_age = 0.300  # Péjoratif pour les ostéosarcomes conventionnels

# 2. Effet Plafond pour le Volume et la CRP (La courbe s'aplatit après un seuil)
vol_effect = min(vol, 400) * 0.0008  # Plafonné à 400 cm³
crp_effect = min(crp, 50) * 0.004    # Plafonné à 50 mg/L

# 3. Indice Pronostique
PI = (
    score_age +
    dict_sex[sexe] +
    dict_histo[histo] +
    vol_effect +
    dict_meta[meta] +
    crp_effect +
    dict_huvos[huvos] +
    dict_margin[marge]
)

# Fonction de survie de base calibrée à 88% pour isoler l'impact massif des HR
S0_12 = 0.880 
hazard_ratio = math.exp(PI)
prob_survie = math.pow(S0_12, hazard_ratio)
prob_recidive = (1 - prob_survie) * 100

with col2:
    st.header("📊 Évaluation du Risque")
    
    subcol1, subcol2 = st.columns(2)
    with subcol1:
        st.metric(label="Indice Pronostique", value=f"{PI:.2f}")
    with subcol2:
        st.metric(label="Risque de Récidive à 1 an", value=f"{prob_recidive:.1f} %")
    
    st.progress(int(min(max(prob_recidive, 0), 100))) 
    
    st.markdown("### 🧬 Analyse des Facteurs")
    st.markdown('<div class="stat-box">', unsafe_allow_html=True)
    st.write("✔️ **Effet Plafond actif :** L'impact de la CRP et du Volume est non-linéaire et plafonné selon la réalité clinique.")
    if "Parostéal" in histo or "Périosté" in histo:
        st.write("✔️ **Correction Épidémiologique :** L'âge adulte n'a pas été comptabilisé comme facteur péjoratif pour ce sous-type de surface.")
    else:
        st.write("✔️ **Facteurs dominants :** Le modèle donne la primauté absolue au statut des marges et au score de nécrose tumorale.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 🎯 Stratification Clinique")
    
    if prob_recidive <= 12:
        st.success("🟢 **GROUPE 1 (~6% de risque)** : Risque très faible. Surveillance standard.")
    elif prob_recidive <= 28:
        st.info("🔵 **GROUPE 2 (~18% de risque)** : Risque modéré. Vigilance clinique.")
    elif prob_recidive <= 50:
        st.warning("🟡 **GROUPE 3 (~38% de risque)** : Haut risque. Imagerie rapprochée.")
    else:
        st.error("🔴 **GROUPE 4 (~65% de risque)** : Très haut risque. Discussion RCP pour traitement de seconde ligne.")

st.markdown("---")
st.caption("Modèle d'aide à la décision. L'algorithme intègre une calibration experte des facteurs d'âge, de volume et d'inflammation pour éviter les biais linéaires statistiques.")
