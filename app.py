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
    .rcp-warning {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 10px;
        border-left: 4px solid #F59E0B;
        font-weight: bold;
        border-radius: 4px;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Nomogramme Expert : Ostéosarcome des Membres")
st.subheader("Modèle Prédictif Calibré & Aide à la Décision (RCP)")
st.markdown("---")

# --- DICTIONNAIRES DES VARIABLES ET COEFFICIENTS ---

age_options = ["0 à 10 ans", "11 à 18 ans", "> 18 ans"]
dict_sex = {"Masculin": 0.0, "Féminin": -0.100}

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
if "Parostéal" in histo or "Périosté" in histo:
    score_age = 0.0  
else:
    if age == "0 à 10 ans":
        score_age = 0.0
    elif age == "11 à 18 ans":
        score_age = 0.150
    else:
        score_age = 0.300  

vol_effect = min(vol, 400) * 0.0008  
crp_effect = min(crp, 50) * 0.004    

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
    
    if prob_recidive <= 12:
        st.success("🟢 **GROUPE 1 (~6% de risque)** : Risque très faible.")
    elif prob_recidive <= 28:
        st.info("🔵 **GROUPE 2 (~18% de risque)** : Risque modéré.")
    elif prob_recidive <= 50:
        st.warning("🟡 **GROUPE 3 (~38% de risque)** : Haut risque.")
    else:
        st.error("🔴 **GROUPE 4 (~65% de risque)** : Très haut risque.")

    # --- GÉNÉRATEUR DYNAMIQUE DE CONDUITE À TENIR ---
    st.markdown("### 📋 Conduite à Tenir Recommandée (Guidelines ESMO/NCCN)")
    st.markdown('<div class="rcp-warning">⚠️ Ces recommandations issues de la littérature récente doivent impérativement être validées et individualisées en Réunion de Concertation Pluridisciplinaire (RCP).</div>', unsafe_allow_html=True)
    
    # 1. Stratégie Chirurgicale
    st.markdown("#### 🔪 Chirurgie")
    if "R2" in marge:
        st.write("🔴 **Envahissement / Résidu Macroscopique (R2) :** Reprise chirurgicale impérative si techniquement réalisable. **Indication formelle d'amputation d'emblée ou de désarticulation** en cas d'envahissement du paquet vasculo-nerveux majeur non reconstructible, de contamination compartimentale massive (fracture pathologique) ou de tumeur inopérable.")
    elif "R1" in marge:
        st.write("🟡 **Marges Limites (R1) :** Reprise chirurgicale pour élargissement fortement recommandée si elle est anatomiquement faisable sans morbidité fonctionnelle extrême.")
    else:
        st.write("🟢 **Marges Saines (R0) :** Chirurgie conservatrice validée. Poursuite de la surveillance de la reconstruction (prothèse/allogreffe) et du plan de rééducation.")

    # 2. Stratégie Médicale (Chimio/Radio)
    st.markdown("#### 💉 Oncologie Médicale & Radiothérapie")
    if "Parostéal" in histo:
        st.write("**Chimiothérapie :** Abstention thérapeutique stricte. La chirurgie R0 est curative pour ce bas grade de surface.")
        st.write("**Radiothérapie :** Formellement non indiquée.")
    elif "Secondaire" in histo:
        st.write("**Chimiothérapie :** Tumeurs souvent chimio-résistantes avec un terrain fragile. Protocole à adapter strictement à l'âge et aux comorbidités. Envisager l'inclusion dans des essais cliniques.")
        st.write("**Radiothérapie :** Ostéosarcome radio-résistant. Réservée aux lésions inopérables (SBRT) ou traitement antalgique palliatif (Samarium-153).")
    else:
        if "Grade III" in huvos or "Grade IV" in huvos:
            st.write("**Chimiothérapie :** Bon répondeur. Poursuite du protocole adjuvant standard de 1ère ligne (MAP : Méthotrexate, Doxorubicine, Cisplatine).")
        else:
            st.write("**Chimiothérapie :** Mauvais répondeur histologique. Discussion en RCP pour l'adjonction d'une ligne de rattrapage (**Ifosfamide / Étoposide**). Considérer l'adjonction d'immunomodulateurs (**Mifamurtide / Mepact**) post-opératoires. En cas de progression, recours aux Inhibiteurs de Tyrosine Kinase (**Cabozantinib, Regorafenib**).")
        
        if "R1" in marge or "R2" in marge:
            st.write("**Radiothérapie :** Les ostéosarcomes sont intrinsèquement radio-résistants. À discuter *exclusivement* sur le lit tumoral en cas de résidu R1/R2 formellement inopérable (doses massives > 60 Gy requises) ou en stéréotaxie sur oligométastases.")
        else:
            st.write("**Radiothérapie :** Non indiquée.")

    # 3. Surveillance
    st.markdown("#### 🔍 Explorations & Suivi")
    if prob_recidive <= 28:
        st.write("Examen clinique, Radiographie locale et **TDM Thoracique (sans injection) tous les 3 mois** pendant 2 ans. Puis tous les 4 mois la 3ème année, et tous les 6 mois les 4ème et 5ème années.")
    else:
        st.write("⚠️ Surveillance intensifiée. **IRM locale et TDM Thoracique stricts tous les 2 mois** pendant 2 ans. Bilan d'extension systémique immédiat (**TEP-Scan 18F-FDG +/- Scintigraphie osseuse**) justifié face au risque métastatique précoce élevé.")

st.markdown("---")
st.caption("Outil de démonstration clinique (SICOT 2026). Ne remplace pas le jugement médical. Basé sur la cohorte d'étude et les consensus internationaux.")
