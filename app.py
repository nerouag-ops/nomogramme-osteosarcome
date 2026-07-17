import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Nomogramme Ostéosarcome V10",
    page_icon="🦴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS PERSONNALISÉ (Pour un rendu très visuel et coloré) ---
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
    </style>
""", unsafe_allow_html=True)

# --- EN-TÊTE ---
st.title("🦴 Nomogramme Dynamique : Ostéosarcome des Membres")
st.subheader("Prédiction du risque à 1 an & Stratégie Thérapeutique Personnalisée")
st.markdown("---")

# --- DICTIONNAIRES DES SCORES ---
type_options = {
    "Bas grade (Parostéal, Central de bas grade)": 1,
    "Grade intermédiaire (Périosté)": 2,
    "Haut grade conventionnel (Ostéoblastique, Chondro-, Fibro-)": 3,
    "Haut grade agressif (Télangiectasique, Petites cellules)": 4,
    "Secondaire (Sur maladie de Paget, Post-radique)": 5
}
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

# --- INTERFACE UTILISATEUR ---
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.header("📋 Profil du Patient")
    st.markdown('<div class="highlight-card">', unsafe_allow_html=True)
    
    type_osteo = st.selectbox("🔬 1. Sous-type histologique", list(type_options.keys()))
    age = st.selectbox("🎂 2. Âge du patient", list(age_options.keys()))
    vol = st.selectbox("📏 3. Volume tumoral initial estimé", list(volume_options.keys()))
    crp = st.selectbox("🩸 4. CRP (Marqueur inflammatoire)", list(crp_options.keys()))
    marge = st.selectbox("🔪 5. Marges de résection chirurgicale", list(marge_options.keys()))
    huvos = st.selectbox("🧬 6. Réponse histologique (Huvos)", list(huvos_options.keys()))
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- CALCULS ---
score_total = type_options[type_osteo] + age_options[age] + volume_options[vol] + crp_options[crp] + marge_options[marge] + huvos_options[huvos]
score_max = 16
probabilite = (score_total / score_max) * 100

with col2:
    st.header("📊 Évaluation & Plan d'Action")
    
    subcol1, subcol2 = st.columns(2)
    with subcol1:
        st.metric(label="Score de Risque", value=f"{score_total} / {score_max}")
    with subcol2:
        st.metric(label="Probabilité de Récidive (1 an)", value=f"{probabilite:.1f} %")
    
    st.progress(int(probabilite))
    
    # --- RECOMMANDATIONS AVEC ICÔNES ---
    st.markdown("### 🎯 Stratégie Recommandée (Guidelines NCCN/ESMO)")
    
    if probabilite < 30:
        st.success("🟢 **RISQUE FAIBLE : Chirurgie conservatrice validée / Histologie favorable.**")
        st.markdown("""
        * **🔍 Exploration :** Examen clinique, Rx locale et TDM thoracique tous les 3 mois (années 1-2).
        * **🔪 Chirurgie :** Conservation du membre (résection R0). Suivi de la reconstruction (prothèse/greffe).
        * **💉 Chimiothérapie :** 
            * *Si bas grade :* 🚫 Abstention thérapeutique (pas de chimio).
            * *Si haut grade :* Poursuite du protocole classique (MAP).
        * **☢️ Radiothérapie :** Non indiquée.
        * **🦴 MPR (Rééducation) :** Reprise progressive de la mise en charge selon l'implant.
        """)
        
    elif probabilite < 70:
        st.warning("🟡 **RISQUE INTERMÉDIAIRE : Vigilance sur les marges (R1) ou nécrose partielle.**")
        st.markdown("""
        * **🔍 Exploration :** Rythme intensifié. IRM locale (dépistage tissulaire) et TDM thoracique tous les 2 à 3 mois.
        * **🔪 Chirurgie :** Si marges R1, **reprise pour élargissement** à discuter en RCP si faisable sans morbidité fonctionnelle extrême.
        * **💉 Chimiothérapie :** Maintien MAP. Discussion en RCP pour ajout Ifosfamide/Étoposide ou introduction de Mifamurtide.
        * **☢️ Radiothérapie :** À discuter sur le lit tumoral uniquement si résidu R1 strictement inopérable.
        * **🦴 MPR (Rééducation) :** Programme prudent. Éviter les contraintes biomécaniques maximales sur le montage.
        """)
        
    else:
        st.error("🔴 **RISQUE ÉLEVÉ : Alerte clinique (Résidu R2, Sous-type péjoratif ou Récidive).**")
        st.markdown("""
        * **🔍 Exploration :** Bilan d'extension immédiat (TEP-Scan 18F-FDG ☢️ +/- Scintigraphie osseuse).
        * **🔪 Chirurgie :** Reprise impérative si R2. **Amputation d'emblée ou désarticulation** formellement indiquée si envahissement vasculo-nerveux ou contamination par fracture pathologique.
        * **💉 Chimiothérapie :** Lignes de rattrapage (Ifosfamide/Étoposide) ou inhibiteurs de tyrosine kinase (TKI).
        * **☢️ Radiothérapie :** SBRT sur oligométastases ou métabolique à visée palliative/antalgique.
        * **🦴 MPR (Rééducation) :** En cas d'amputation : appareillage précoce, gestion du membre fantôme et soutien psychologique.
        """)

st.markdown("---")
st.caption("🌐 Développé pour le 46ème Congrès Mondial SICOT. Basé sur les guidelines internationales 2024-2026.")
