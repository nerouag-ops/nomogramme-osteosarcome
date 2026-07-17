import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Nomogramme Ostéosarcome V4",
    page_icon="🦴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1, h2, h3 {color: #1f77b4;}
    .stProgress > div > div > div > div {background-color: #ff4b4b;}
    </style>
""", unsafe_allow_html=True)

# --- EN-TÊTE ---
st.title("🦴 Nomogramme Dynamique : Ostéosarcome des Membres")
st.subheader("Prédiction du risque de récidive précoce à 1 an (V4)")
st.markdown("---")

# --- DICTIONNAIRES DES SCORES ---
age_options = {"≤ 8 ans": 0, "9 à 17 ans": 1, "≥ 18 ans": 2}
volume_options = {"< 50 cm³": 0, "50-90 cm³": 1, "> 90 cm³": 2}
crp_options = {"< 10 mg/L (Normale)": 0, "≥ 10 mg/L (Élevée)": 2}
marge_options = {"Saines (R0)": 0, "Limites (R1)": 1, "Infiltrées (R2)": 2}
huvos_options = {
    "Grade IV (Nécrose 100%)": 0,
    "Grade III (Nécrose 90-99%)": 1,
    "Grade II (Nécrose 50-89%)": 2,
    "Grade I (Nécrose 0-49%)": 3
}

# --- INTERFACE UTILISATEUR (Colonnes) ---
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.header("⚙️ Saisie des Paramètres")
    st.info("Veuillez renseigner les données cliniques et biologiques du patient.")
    
    age = st.selectbox("1. Âge du patient", list(age_options.keys()))
    vol = st.selectbox("2. Volume tumoral initial estimé", list(volume_options.keys()))
    crp = st.selectbox("3. CRP (Marqueur inflammatoire)", list(crp_options.keys()))
    marge = st.selectbox("4. Marges de résection chirurgicale", list(marge_options.keys()))
    huvos = st.selectbox("5. Réponse histologique (Huvos)", list(huvos_options.keys()))

# --- CALCULS ---
score_total = age_options[age] + volume_options[vol] + crp_options[crp] + marge_options[marge] + huvos_options[huvos]
score_max = 11

# Calcul de la probabilité 
probabilite = (score_total / score_max) * 100

# --- AFFICHAGE DES RÉSULTATS ---
with col2:
    st.header("📊 Évaluation Individualisée du Risque")
    st.markdown("<br>", unsafe_allow_html=True)
    
    subcol1, subcol2 = st.columns(2)
    with subcol1:
        st.metric(label="Score Total", value=f"{score_total} / {score_max} pts")
    with subcol2:
        st.metric(label="Probabilité de Récidive (1 an)", value=f"{probabilite:.1f} %")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.write("**Niveau de risque estimé :**")
    st.progress(int(probabilite))
    
    if probabilite < 30:
        st.success("🟢 **Risque Faible** : Suivi clinique standard recommandé.")
    elif probabilite < 70:
        st.warning("🟡 **Risque Intermédiaire** : Surveillance rapprochée nécessaire.")
    else:
        st.error("🔴 **Risque Élevé** : Protocole de rééducation et suivi intensifs requis.")

st.markdown("---")
st.caption("Outil d'aide à la décision clinique. Ne remplace pas le jugement médical. Basé sur les données de la littérature (intégration Âge et CRP).")
