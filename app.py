import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Nomogramme Ostéosarcome V12",
    page_icon="🦴",
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
    </style>
""", unsafe_allow_html=True)

st.title("🦴 Nomogramme Dynamique : Ostéosarcome des Membres")
st.subheader("Prédiction du risque à 1 an & Stratégie Thérapeutique Personnalisée")
st.markdown("---")

# --- DICTIONNAIRES DES SCORES ---
type_options = {
    "Bas grade (Parostéal, Central) - Très faible risque de récidive": 1,
    "Grade intermédiaire (Périosté) - Risque de récidive modéré": 2,
    "Haut grade conventionnel (Ostéoblastique, Chondro-, Fibro-) - Risque standard": 3,
    "Haut grade agressif (Télangiectasique, Petites cellules) - Haut risque de dissémination": 4,
    "Secondaire (Sur Paget, Post-radique) - Risque majeur de récidive précoce": 5
}
age_options = {"≤ 8 ans": 0, "9 à 17 ans": 1, "≥ 18 ans": 2}

# --- NOUVEAUX VOLUMES SELON LA LITTÉRATURE (COSS) ---
volume_options = {
    "< 100 cm³ (Petit volume)": 0,
    "100 - 200 cm³ (Volume intermédiaire)": 1,
    "> 200 cm³ (Volume massif / Péjoratif)": 2
}

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
    vol = st.selectbox("📏 3. Volume tumoral initial (IRM)", list(volume_options.keys()))
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
    
    # --- RECOMMANDATIONS ONCOLOGIQUES STRICTES ---
    st.markdown("### 🎯 Stratégie Recommandée (Guidelines ESMO/NCCN)")
    
    if probabilite < 30:
        st.success("🟢 **RISQUE FAIBLE : Chirurgie conservatrice validée / Histologie favorable.**")
        st.markdown("""
        * **🔍 Exploration (Calendrier strict) :** Examen clinique, Radiographie locale et TDM thoracique tous les 3 mois pendant 2 ans. Puis tous les 4 mois la 3ème année. Puis tous les 6 mois les 4ème et 5ème années. Annuellement par la suite.
        * **🔪 Chirurgie :** Surveillance de la reconstruction. Pas de reprise chirurgicale indiquée.
        * **💉 Chimiothérapie :** 
            * *Tumeur de bas grade :* 🚫 Abstention thérapeutique stricte.
            * *Haut grade conventionnel :* Poursuite du protocole adjuvant standard (MAP).
        * **☢️ Radiothérapie :** Formellement non indiquée.
        """)
        
    elif probabilite < 70:
        st.warning("🟡 **RISQUE INTERMÉDIAIRE : Vigilance sur les marges (R1) ou nécrose partielle.**")
        st.markdown("""
        * **🔍 Exploration (Calendrier strict) :** IRM locale (dépistage de récidive tissulaire) et TDM thoracique tous les 2 mois pendant la 1ère année. Puis tous les 3 mois la 2ème année.
        * **🔪 Chirurgie :** Si marges limites (R1), **reprise chirurgicale pour élargissement** si techniquement réalisable sans amputation.
        * **💉 Chimiothérapie :** Maintien du protocole MAP. RCP nécessaire pour discuter l'ajout de l'Ifosfamide/Étoposide et l'introduction du Mifamurtide (Mepact).
        * **☢️ Radiothérapie :** Indiquée exclusivement sur le lit tumoral en cas de marges R1 inopérables (doses > 60 Gy requises).
        """)
        
    else:
        st.error("🔴 **RISQUE ÉLEVÉ : Alerte clinique (Résidu R2, Sous-type agressif/secondaire).**")
        st.markdown("""
        * **🔍 Exploration (Calendrier strict) :** Bilan d'extension systémique immédiat (TEP-Scan 18F-FDG ☢️ et/ou Scintigraphie osseuse au Technétium). TDM thoracique et IRM locale tous les 2 mois stricts pendant 2 ans.
        * **🔪 Chirurgie :** Reprise chirurgicale impérative si marges R2. L'**amputation d'emblée ou la désarticulation** est formellement indiquée en cas d'envahissement vasculo-nerveux majeur ou de contamination compartimentale massive par fracture pathologique.
        * **💉 Chimiothérapie :** Lignes de rattrapage d'emblée (Ifosfamide/Étoposide). Recours aux inhibiteurs de tyrosine kinase (Cabozantinib, Regorafenib) en cas de progression sous traitement.
        * **☢️ Radiothérapie :** SBRT (Radiothérapie stéréotaxique) sur oligométastases osseuses ou pulmonaires inopérables. Radiothérapie métabolique à visée palliative/antalgique.
        """)

st.markdown("---")
st.caption("🌐 Développé pour le 46ème Congrès Mondial SICOT. Protocoles d'imagerie et de traitement strictement alignés sur les guidelines de l'ESMO et du NCCN (2024-2026).")
