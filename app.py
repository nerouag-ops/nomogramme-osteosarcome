import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Nomogramme Ostéosarcome V13",
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
st.subheader("Prédiction du risque à 1 an & Stratégie Thérapeutique Personnalisée (V13)")
st.markdown("---")

# --- DICTIONNAIRES DES SCORES (PONDÉRATION CLINIQUE CORRIGÉE) ---
type_options = {
    "Parostéal (Bas grade)": 0,
    "Central de bas grade": 0,
    "Périosté (Grade intermédiaire)": 1,
    "Fibroblastique (Haut grade - Pronostic intermédiaire)": 2,
    "Chondroblastique (Haut grade)": 3,
    "Ostéoblastique (Haut grade conventionnel - Référence)": 4,
    "Télangiectasique (Haut grade agressif)": 5,
    "À petites cellules (Haut grade agressif)": 5,
    "Secondaire sur maladie de Paget": 6,
    "Secondaire post-radique": 6
}
age_options = {"≤ 8 ans": 0, "9 à 17 ans": 1, "≥ 18 ans": 2}
volume_options = {"< 100 cm³ (Petit volume)": 0, "100 - 200 cm³ (Intermédiaire)": 1, "> 200 cm³ (Massif)": 2}
crp_options = {"< 10 mg/L (Normale)": 0, "≥ 10 mg/L (Élevée)": 2}
marge_options = {"Saines (R0)": 0, "Limites (R1)": 2, "Infiltrées (R2)": 4}

# Le Huvos a désormais un impact MAJEUR sur le score
huvos_options = {
    "Grade IV (Nécrose 100%)": 0,
    "Grade III (Nécrose 90-99%)": 1,
    "Grade II (Nécrose 50-89%)": 4,
    "Grade I (Nécrose 0-49%)": 6
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
score_max = 22 # Nouveau score maximum
probabilite = (score_total / score_max) * 100

with col2:
    st.header("📊 Évaluation & Plan d'Action")
    
    subcol1, subcol2 = st.columns(2)
    with subcol1:
        st.metric(label="Score de Risque", value=f"{score_total} / {score_max}")
    with subcol2:
        st.metric(label="Probabilité de Récidive (1 an)", value=f"{probabilite:.1f} %")
    
    st.progress(int(probabilite))
    
    # --- LOGIQUE DYNAMIQUE DES RECOMMANDATIONS ---
    # La conduite à tenir s'adapte exactement aux choix du chirurgien
    
    # 1. Logique Chirurgicale
    if marge == "Infiltrées (R2)":
        chirurgie_text = "⚠️ **Reprise chirurgicale impérative (R2)**. L'amputation d'emblée ou la désarticulation est formellement indiquée en cas d'envahissement vasculo-nerveux majeur ou de contamination compartimentale."
    elif marge == "Limites (R1)":
        chirurgie_text = "⚠️ **Reprise chirurgicale pour élargissement** si techniquement réalisable sans amputation, suite aux marges limites (R1)."
    else:
        chirurgie_text = "✅ **Conservation du membre validée** (Marges R0). Surveillance clinique de la reconstruction. Pas de reprise chirurgicale indiquée."

    # 2. Logique Médicale (Chimio/Radio)
    if "Parostéal" in type_osteo or "Central" in type_osteo:
        chimio_text = "🚫 **Abstention thérapeutique stricte** (Pas de chimiothérapie ni radiothérapie pour ce bas grade). La chirurgie R0 est curative."
    elif huvos in ["Grade I (Nécrose 0-49%)", "Grade II (Nécrose 50-89%)"]:
        chimio_text = "⚠️ **Mauvais répondeur histologique :** Lignes de rattrapage à discuter en RCP d'emblée (Ifosfamide/Étoposide). Recours aux TKI (Cabozantinib) en cas de progression."
    else:
        chimio_text = "✅ **Bon répondeur histologique :** Poursuite du protocole adjuvant standard (MAP). Radiothérapie formellement non indiquée."

    # 3. Logique d'Exploration
    if probabilite < 30:
        explo_text = "Examen clinique, Radiographie locale et TDM thoracique **tous les 3 mois pendant 2 ans**. Puis tous les 4 mois la 3ème année. Puis tous les 6 mois les 4ème et 5ème années."
    elif probabilite < 70:
        explo_text = "IRM locale (dépistage tissulaire) et TDM thoracique **tous les 2 mois pendant 1 an**. Puis tous les 3 mois la 2ème année."
    else:
        explo_text = "Bilan d'extension systémique immédiat (**TEP-Scan 18F-FDG ☢️ / Scintigraphie osseuse**). TDM thoracique et IRM locale stricts tous les 2 mois pendant 2 ans."

    # --- AFFICHAGE DES RECOMMANDATIONS ---
    st.markdown("### 🎯 Stratégie Recommandée (Guidelines ESMO/NCCN)")
    
    if probabilite < 30:
        st.success("🟢 **RISQUE FAIBLE : Profil très favorable.**")
    elif probabilite < 70:
        st.warning("🟡 **RISQUE INTERMÉDIAIRE : Vigilance clinique requise.**")
    else:
        st.error("🔴 **RISQUE ÉLEVÉ : Alerte clinique majeure.**")

    st.markdown(f"""
    * **🔍 Exploration :** {explo_text}
    * **🔪 Chirurgie :** {chirurgie_text}
    * **💉 Traitement médical :** {chimio_text}
    """)

st.markdown("---")
st.caption("🌐 Développé pour le 46ème Congrès Mondial SICOT. L'algorithme décisionnel s'adapte dynamiquement au score de Huvos, au type histologique précis et à la qualité des marges.")
