import streamlit as st
import math

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Nomogramme SICOT 2026 - Ostéosarcome",
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
st.subheader("Prédiction de la Récidive à 1 An - Modèle Multivarié")
st.markdown("---")

# --- COEFFICIENTS DU MODÈLE DE COX (B = ln(HR)) ---
# Basé sur la cohorte N=214 de l'Hôpital Salim Zemirli (HR extraits de l'Abstract SICOT 2026)

dict_meta = {"Non": 0.0, "Oui (HR 3.5)": 1.253}
dict_huvos = {"Bonne réponse (Nécrose ≥ 90%, Grades III-IV)": 0.0, "Mauvaise réponse (Nécrose < 90%, Grades I-II) (HR 3.0)": 1.099}
dict_margin = {"Saines (R0)": 0.0, "Limites / Infiltrées (R1/R2) (HR 2.4)": 0.875}
dict_size = {"≤ 8 cm": 0.0, "> 8 cm (HR 1.8)": 0.588}
dict_location = {"Distale / Diaphysaire": 0.0, "Proximale (HR 1.5)": 0.405}

# --- INTERFACE UTILISATEUR ---
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.header("📋 Profil du Patient")
    st.markdown('<div class="highlight-card">', unsafe_allow_html=True)
    
    meta = st.selectbox("🩻 1. Métastases au diagnostic", list(dict_meta.keys()))
    huvos = st.selectbox("🧬 2. Réponse Histologique (Huvos)", list(dict_huvos.keys()))
    marge = st.selectbox("🔪 3. Statut des Marges Chirurgicales", list(dict_margin.keys()))
    taille = st.selectbox("📏 4. Taille Tumorale Maximale", list(dict_size.keys()))
    loc = st.selectbox("🦴 5. Localisation Anatomique", list(dict_location.keys()))
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- CALCUL MATHÉMATIQUE ---
# 1. Indice Pronostique (Somme des Beta)
PI = (
    dict_meta[meta] +
    dict_huvos[huvos] +
    dict_margin[marge] +
    dict_size[taille] +
    dict_location[loc]
)

# 2. Hazard Ratio global du patient
hazard_ratio = math.exp(PI)

# 3. Probabilité de récidive
# Calibrée sur une survie de base (S0) à 1 an de 94% pour reproduire la stratification de la cohorte
S0_12 = 0.940 
prob_survie = math.pow(S0_12, hazard_ratio)
prob_recidive = (1 - prob_survie) * 100

with col2:
    st.header("📊 Évaluation du Risque")
    
    subcol1, subcol2 = st.columns(2)
    with subcol1:
        st.metric(label="Hazard Ratio (HR) Cumulé", value=f"{hazard_ratio:.2f}")
    with subcol2:
        st.metric(label="Risque de Récidive à 1 an", value=f"{prob_recidive:.1f} %")
    
    st.progress(int(min(max(prob_recidive, 0), 100))) 
    
    st.markdown("### 🎯 Stratification Clinique Validée")
    
    # Stratification alignée exactement sur les résultats de votre cohorte (6%, 18%, 38%, 65%)
    if prob_recidive <= 12:
        st.success("🟢 **GROUPE 1 (~6% de risque)** : Bas risque. Surveillance radiologique standard trimestrielle.")
    elif prob_recidive <= 28:
        st.info("🔵 **GROUPE 2 (~18% de risque)** : Risque modéré. Vigilance clinique et maintien du protocole adjuvant.")
    elif prob_recidive <= 50:
        st.warning("🟡 **GROUPE 3 (~38% de risque)** : Haut risque. Intensification de la surveillance (IRM/TDM tous les 2 mois).")
    else:
        st.error("🔴 **GROUPE 4 (~65% de risque)** : Très haut risque. Candidat prioritaire pour évaluation de thérapies de seconde ligne et RCP élargie.")

    # --- GÉNÉRATEUR DYNAMIQUE DE CONDUITE À TENIR ---
    st.markdown("### 📋 Orientation Décisionnelle")
    st.markdown('<div class="rcp-warning">⚠️ Résultat à intégrer au jugement clinique en Réunion de Concertation Pluridisciplinaire (RCP).</div>', unsafe_allow_html=True)
    
    if dict_margin[marge] > 0:
        st.write("🔪 **Alerte Chirurgicale :** Les marges R1/R2 majorent le risque de récidive locale de 2.4 fois. Une reprise chirurgicale pour élargissement, voire une chirurgie radicale de sauvetage, doit être discutée si anatomiquement faisable.")
    else:
        st.write("🔪 **Chirurgie :** Marges R0 (Saines). Validation de la conservation du membre. Suivi de l'intégration du montage orthopédique.")

    if dict_huvos[huvos] > 0:
        st.write("💉 **Alerte Oncologique :** Mauvaise réponse à la chimiothérapie d'induction (Huvos I-II). Le protocole MAP standard est insuffisant. Discuter l'introduction d'une chimiothérapie de rattrapage (ex: Ifosfamide/Étoposide) ou de thérapies ciblées.")
    else:
        st.write("💉 **Oncologie :** Bonne réponse histologique (Nécrose ≥ 90%). Poursuite du traitement adjuvant tel qu'initié.")
        
    if dict_meta[meta] > 0:
        st.write("☢️ **Surveillance :** Présence de métastases au diagnostic. Bilan d'extension systémique systématique par TEP-Scan 18F-FDG. Risque de progression majeur imposant un suivi strict tous les 2 mois.")

st.markdown("---")
st.caption("Modèle développé à partir de la cohorte (N=214). Index de concordance (C-index) : 0.81. Présenté au 46th SICOT Orthopaedic World Congress, Kyoto 2026.")
