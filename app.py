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

# --- COEFFICIENTS B (Tirés de la sortie SPSS du 17-JUL-2026) ---
B_AGE = 0.008
B_VOL = 0.001
B_CRP = 0.000 # Coefficient nul dans le modèle

dict_sex = {"Masculin": 0.0, "Féminin": -0.192}

dict_histo = {
    "Télangiectasique (Référence)": 0.0,
    "Chondroblastique": 0.951,
    "Fibroblastique": -0.620,
    "Ostéoblastique": 0.733,
    "Parostéal": 0.592,
    "Périosté": 0.557,
    "Secondaire": -0.001,
    "À petites cellules": -10.340 # Exp(B) tend vers 0 dans le modèle
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
    
    age = st.number_input("🎂 1. Âge (années)", min_value=0, max_value=100, value=21)
    sexe = st.selectbox("🚻 2. Sexe", list(dict_sex.keys()))
    vol = st.number_input("📏 3. Volume tumoral (cm³)", min_value=0, max_value=5000, value=250)
    meta = st.selectbox("🩻 4. Métastases au diagnostic", list(dict_meta.keys()))
    crp = st.number_input("🩸 5. CRP (mg/L)", min_value=0.0, value=10.0)
    histo = st.selectbox("🔬 6. Type Histologique", list(dict_histo.keys()))
    marge = st.selectbox("🔪 7. Marges chirurgicales", list(dict_margin.keys()))
    huvos = st.selectbox("🧬 8. Score de Huvos", list(dict_huvos.keys()))
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- CALCUL DU MODÈLE DE COX ---
# 1. Calcul de l'Indice Pronostique (PI = Somme des B*X)
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

# 2. Estimation de la probabilité de survie S(t) = S0(t)^exp(PI)
# La survie de base estimée (S0 à 12 mois) est calibrée sur la moyenne globale de récidive (27%)
S0_12 = 0.685 
hazard_ratio = math.exp(PI)
prob_survie = math.pow(S0_12, hazard_ratio)

# 3. Probabilité de récidive = 1 - Probabilité de survie
prob_recidive = (1 - prob_survie) * 100

with col2:
    st.header("📊 Calcul de Probabilité Exacte")
    
    subcol1, subcol2 = st.columns(2)
    with subcol1:
        st.metric(label="Indice Pronostique (PI)", value=f"{PI:.3f}")
    with subcol2:
        st.metric(label="Risque de Récidive à 1 an", value=f"{prob_recidive:.1f} %")
    
    st.progress(int(min(max(prob_recidive, 0), 100))) # Borne la barre entre 0 et 100
    
    st.markdown("### 🧬 Analyse Statistique du Patient")
    st.markdown('<div class="stat-box">', unsafe_allow_html=True)
    st.write(f"**Hazard Ratio (HR) ajusté pour ce patient :** {hazard_ratio:.2f}")
    st.write("Ce modèle calcule la probabilité absolue en utilisant la fonction de survie de Cox :")
    st.write("`P(récidive) = 1 - S₀(t)^exp(Σ βx)`")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- STRATIFICATION SELON L'ABSTRACT (4 GROUPES) ---
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
st.caption("Modèle mathématique strict généré à partir de la régression de Cox (SPSS - 17 Juillet 2026). N=214 patients. Variables indépendantes : Âge, Sexe, Volume Tumoral, Statut Métastatique, CRP, Type Histologique, Marges, Grade de Huvos.")
