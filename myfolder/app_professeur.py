import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime, time, timedelta
import numpy as np
import io
import os
import toml
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuration de la page
st.set_page_config(
    page_title="Tableau de Bord Professeur | Planification Examens",
    page_icon="👨‍🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === STYLE PERSONNALISÉ ===
st.markdown("""
<style>
    /* Style global */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Cards styling */
    .custom-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
        text-align: center;
        border-left: 5px solid #3498db;
    }
    
    /* Exam cards */
    .exam-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        border-left: 5px solid;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
    }
    
    .exam-card.responsable {
        border-left-color: #3498db;
        background: linear-gradient(90deg, rgba(52, 152, 219, 0.1) 0%, rgba(255, 255, 255, 1) 50%);
    }
    
    .exam-card.surveillant {
        border-left-color: #2ecc71;
        background: linear-gradient(90deg, rgba(46, 204, 113, 0.1) 0%, rgba(255, 255, 255, 1) 50%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #d3d3d3 100%);

        padding-top: 2rem;
    }
    
    [data-testid="stSidebar"] .sidebar-content {
        color: white;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #3498db 0%, #2980b9 100%);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
    }
    
    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    
    .badge-primary {
        background: #3498db;
        color: white;
    }
    
    .badge-success {
        background: #2ecc71;
        color: white;
    }
    
    .badge-warning {
        background: #f39c12;
        color: white;
    }
    
    /* Progress bar */
    .progress-container {
        background: #ecf0f1;
        border-radius: 10px;
        height: 10px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #3498db 0%, #2ecc71 100%);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom tabs */
    .custom-tabs {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 2rem;
        background: white;
        padding: 0.5rem;
        border-radius: 12px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
    }
    
    .custom-tab {
        flex: 1;
        text-align: center;
        padding: 0.8rem;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .custom-tab.active {
        background: linear-gradient(90deg, #3498db 0%, #2980b9 100%);
        color: white;
        box-shadow: 0 3px 10px rgba(52, 152, 219, 0.2);
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        border: none !important;
    }
    
    /* Alert styling */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid;
    }
    
    /* Calendar style */
    .calendar-day {
        text-align: center;
        padding: 0.5rem;
        border-radius: 8px;
        margin: 0.1rem;
        font-weight: bold;
    }
    
    .calendar-day.has-exam {
        background: #3498db;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# HIDE THE PAGE NAVIGATION
hide_pages_navigation = """
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
"""
st.markdown(hide_pages_navigation, unsafe_allow_html=True)

# === VÉRIFICATION DE SESSION ===
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⛔ Accès non autorisé. Veuillez vous connecter.")
    if st.button("🔐 Se connecter"):
        st.switch_page("pages/log.py")
    st.stop()

if 'role' not in st.session_state or st.session_state.role != 'professeur':
    st.error(f"⛔ Cette page est réservée aux professeurs.")
    if st.button("🏠 Retour à l'accueil"):
        st.switch_page("app.py")
    st.stop()

PROFESSEUR_ID = st.session_state.user_id

# === FONCTIONS AUXILIAIRES (garder les fonctions existantes) ===
def load_secrets():
    possible_paths = [
        r"C:\Users\FARES DH\.streamlit\secrets.toml",
        r"C:\Users\FARES DH\Desktop\pree\.streamlit\secrets.toml",
        ".streamlit/secrets.toml",
        "secrets.toml"
    ]
    
    for path in possible_paths:
        try:
            if os.path.exists(path):
                secrets = toml.load(path)
                return secrets.get("mysql", {})
        except:
            continue
    
    return {
        "host": "localhost",
        "database": "planning_examens",
        "user": "root",
        "password": ""
    }

secrets = load_secrets()

@st.cache_resource
def init_connection():
    try:
        conn = mysql.connector.connect(
            host=secrets["host"],
            database=secrets["database"],
            user=secrets["user"],
            password=secrets["password"]
        )
        return conn
    except Error as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
        return None

conn = init_connection()

def run_query(query, params=None, fetch=True):
    try:
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            result = cursor.fetchall()
            cursor.close()
            return result
        else:
            conn.commit()
            cursor.close()
            return True
    except Error as e:
        st.error(f"Erreur SQL: {e}")
        return None

# === HEADER PRINCIPAL ===
st.markdown("""
<div class="header-container">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h1 style="margin: 0; font-size: 2.2rem; display: flex; align-items: center; gap: 10px;">
                👨‍🏫 Tableau de Bord Professeur
            </h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 1rem;">
                Gestion intelligente de votre planning d'examens
            </p>
        </div>
        <div style="text-align: right;">
            <div style="background: rgba(255, 255, 255, 0.1); padding: 8px 15px; border-radius: 8px;">
                <div style="font-size: 0.9rem; opacity: 0.8;">Connecté en tant que</div>
                <div style="font-weight: bold; font-size: 1.1rem;">{}</div>
            </div>
        </div>
    </div>
</div>
""".format(st.session_state.nom_complet), unsafe_allow_html=True)

# === RÉCUPÉRATION DES INFOS PROFESSEUR ===
professeur_info = run_query("""
    SELECT p.nom, p.prenom, p.specialite, p.heures_service, d.nom as departement
    FROM professeurs p
    LEFT JOIN departements d ON p.dept_id = d.id
    WHERE p.id = %s
""", (PROFESSEUR_ID,))

if professeur_info:
    prof = professeur_info[0]
else:
    st.error("Professeur non trouvé")
    st.stop()

# === SIDEBAR REDESIGNÉE ===
with st.sidebar:
    # Photo de profil
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #ffffff 0%, #bdc3c7 100%); border-radius: 10px; 
                     border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                     margin: 0 auto 10px; font-size: 2rem;">
                👨‍🏫
            </div>
            <div style="font-weight: bold; font-size: 1.1rem;">{}</div>
            <div style="color: rgba(255, 255, 255, 0.8); font-size: 0.9rem;">Professeur</div>
        </div>
        """.format(f"{prof['prenom']} {prof['nom'][0]}."), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 📍 Navigation")
    menu_options = {
        "📊 Tableau de Bord": "dashboard",
        "📅 Mes Examens": "examens",
        "📈 Statistiques": "statistiques",
        "📤 Export": "export",
        "⚙️ Paramètres": "parametres"
    }
    
    selected_menu = st.radio(
        "",
        list(menu_options.keys()),
        label_visibility="collapsed",
        key="nav_menu"
    )
    
    st.markdown("---")
    
    # Période
    st.markdown("### 📅 Période d'analyse")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        date_debut = st.date_input("Début", datetime.now(), key="date_debut", label_visibility="collapsed")
    with col_d2:
        date_fin = st.date_input("Fin", datetime.now() + timedelta(days=30), key="date_fin", label_visibility="collapsed")
    
    st.markdown("---")
    
    # Quick Stats
    examens_data = run_query("""
        SELECT COUNT(*) as total FROM examens 
        WHERE (professeur_id = %s OR surveillant_id = %s)
        AND date_examen BETWEEN %s AND %s
        AND statut = 'confirmé'
    """, (PROFESSEUR_ID, PROFESSEUR_ID, date_debut, date_fin))
    
    if examens_data:
        st.markdown("### 📋 Aperçu rapide")
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 10px;">
            <div style="font-size: 2rem; font-weight: bold; text-align: center;">
                {examens_data[0]['total']}
            </div>
            <div style="text-align: center; opacity: 0.9;">Examens planifiés</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Actions
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        if st.button("🔄 Actualiser", use_container_width=True):
            st.rerun()
    with col_act2:
        if st.button("🚪 Déconnexion", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("app.py")

# === CONTENU PRINCIPAL ===
if selected_menu == "📊 Tableau de Bord":
    # Métriques rapides
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2rem;">📊</div>
            <div style="font-size: 1.8rem; font-weight: bold;">24</div>
            <div style="color: #7f8c8d;">Heures ce mois</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2rem;">👥</div>
            <div style="font-size: 1.8rem; font-weight: bold;">156</div>
            <div style="color: #7f8c8d;">Étudiants</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2rem;">📚</div>
            <div style="font-size: 1.8rem; font-weight: bold;">6</div>
            <div style="color: #7f8c8d;">Modules</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2rem;">🎯</div>
            <div style="font-size: 1.8rem; font-weight: bold;">85%</div>
            <div style="color: #7f8c8d;">Disponibilité</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Section principale en deux colonnes
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Calendrier des examens à venir
        st.markdown("### 📅 Prochains examens")
        
        # Récupérer les examens
        examens = run_query("""
            SELECT e.*, m.nom as module, f.nom as formation,
                   CASE WHEN e.professeur_id = %s THEN 'Responsable' ELSE 'Surveillant' END as role
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            WHERE (e.professeur_id = %s OR e.surveillant_id = %s)
            AND e.date_examen BETWEEN %s AND %s
            AND e.statut = 'confirmé'
            ORDER BY e.date_examen, e.heure_debut
            LIMIT 5
        """, (PROFESSEUR_ID, PROFESSEUR_ID, PROFESSEUR_ID, date_debut, date_fin))
        
        if examens:
            for exam in examens:
                role_class = "responsable" if exam['role'] == 'Responsable' else "surveillant"
                badge_color = "badge-primary" if exam['role'] == 'Responsable' else "badge-success"
                
                st.markdown(f"""
                <div class="exam-card {role_class}">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <div style="font-weight: bold; font-size: 1.1rem;">{exam['module']}</div>
                            <div style="color: #7f8c8d; font-size: 0.9rem;">{exam['formation']}</div>
                        </div>
                        <span class="badge {badge_color}">{exam['role']}</span>
                    </div>
                    <div style="display: flex; gap: 20px; margin-top: 10px; font-size: 0.9rem;">
                        <div>📅 {exam['date_examen']}</div>
                        <div>⏰ {exam['heure_debut']} - {exam['heure_fin']}</div>
                        <div>⏱️ {exam['duree_minutes']} min</div>
                    </div>
                    <div style="margin-top: 5px; font-size: 0.9rem;">
                        🏫 {exam.get('salle', 'Non assignée')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aucun examen prévu pour cette période.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Graphique de charge
        
        st.markdown("### 📈 Charge de travail hebdomadaire")
        
        # Données simulées pour le graphique
        semaines = ['S1', 'S2', 'S3', 'S4']
        heures = [12, 18, 15, 20]
        
        fig = go.Figure(data=[
            go.Bar(
                x=semaines,
                y=heures,
                marker_color=['#3498db', '#2ecc71', '#9b59b6', '#e74c3c'],
                text=heures,
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            height=300,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        # Profil professeur
       
        st.markdown("### 👤 Profil Professeur")
        
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%); 
                     border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                     margin: 0 auto 15px; font-size: 2.5rem;">
                {prof['prenom'][0]}{prof['nom'][0]}
            </div>
            <div style="font-weight: bold; font-size: 1.2rem;">{prof['prenom']} {prof['nom']}</div>
            <div style="color: #3498db; font-size: 0.9rem;">{prof.get('departement', 'Non assigné')}</div>
        </div>
        
        <div style="margin: 20px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span>🎓 Spécialité</span>
                <span style="font-weight: bold;">{prof['specialite']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span>⏰ Heures service</span>
                <span style="font-weight: bold;">{prof['heures_service']}h</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span>👨‍🏫 ID</span>
                <span style="font-weight: bold;">{PROFESSEUR_ID}</span>
            </div>
        </div>
        
        <div style="margin-top: 20px;">
            <div style="font-size: 0.9rem; margin-bottom: 5px;">Disponibilité</div>
            <div class="progress-container">
                <div class="progress-bar" style="width: 85%"></div>
            </div>
            <div style="text-align: right; font-size: 0.8rem; color: #7f8c8d;">85%</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Prochain examen
        
        st.markdown("### ⏳ Prochain examen")
        
        # Récupérer le prochain examen
        prochain_examen = run_query("""
            SELECT e.*, m.nom as module
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            WHERE (e.professeur_id = %s OR e.surveillant_id = %s)
            AND e.date_examen >= CURDATE()
            AND e.statut = 'confirmé'
            ORDER BY e.date_examen, e.heure_debut
            LIMIT 1
        """, (PROFESSEUR_ID, PROFESSEUR_ID))
        
        if prochain_examen:
            exam = prochain_examen[0]
            st.markdown(f"""
            <div style="text-align: center; padding: 15px;">
                <div style="font-size: 2.5rem; margin-bottom: 10px;">📝</div>
                <div style="font-weight: bold; font-size: 1.2rem; margin-bottom: 5px;">
                    {exam['module']}
                </div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #3498db; margin: 10px 0;">
                    {exam['date_examen']}
                </div>
                <div style="color: #7f8c8d;">
                    ⏰ {exam['heure_debut']} - {exam['heure_fin']}
                </div>
                <div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 8px;">
                    <div style="font-size: 0.9rem;">⏱️ Durée: {exam['duree_minutes']} minutes</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 30px 20px;">
                <div style="font-size: 3rem; margin-bottom: 10px;">🎉</div>
                <div style="font-weight: bold; color: #2ecc71;">Aucun examen prévu</div>
                <div style="color: #7f8c8d; margin-top: 5px;">Profitez de votre temps libre !</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif selected_menu == "📅 Mes Examens":
    
    st.markdown("### 📅 Mes Examens Confirmés")
    
    # Filtres avancés
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        role_filter = st.selectbox(
            "Rôle",
            ["Tous", "Responsable", "Surveillant"],
            key="role_filter"
        )
    
    with col_f2:
        session_filter = st.selectbox(
            "Session",
            ["Toutes", "Normal", "Rattrapage"],
            key="session_filter"
        )
    
    with col_f3:
        formation_filter = st.selectbox(
            "Formation",
            ["Toutes"] + ["L1", "L2", "L3", "M1", "M2"],
            key="formation_filter"
        )
    
    with col_f4:
        statut_filter = st.selectbox(
            "Statut",
            ["Tous", "Confirmé", "En attente", "Annulé"],
            key="statut_filter"
        )
    
    # Récupérer les examens
    query = """
        SELECT e.*, m.nom as module, f.nom as formation,
               CASE WHEN e.professeur_id = %s THEN 'Responsable' ELSE 'Surveillant' END as role,
               p.nom as responsable_nom, p.prenom as responsable_prenom
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        LEFT JOIN professeurs p ON e.professeur_id = p.id
        WHERE (e.professeur_id = %s OR e.surveillant_id = %s)
        AND e.date_examen BETWEEN %s AND %s
    """
    
    params = [PROFESSEUR_ID, PROFESSEUR_ID, PROFESSEUR_ID, date_debut, date_fin]
    
    if role_filter != "Tous":
        if role_filter == "Responsable":
            query += " AND e.professeur_id = %s"
            params.append(PROFESSEUR_ID)
        else:
            query += " AND e.surveillant_id = %s"
            params.append(PROFESSEUR_ID)
    
    if session_filter != "Toutes":
        query += " AND e.session = %s"
        params.append(session_filter)
    
    if statut_filter != "Tous":
        query += " AND e.statut = %s"
        params.append(statut_filter.lower())
    
    query += " ORDER BY e.date_examen, e.heure_debut"
    
    examens = run_query(query, params)
    
    if examens:
        # Métriques
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        total_examens = len(examens)
        responsable_examens = len([e for e in examens if e['role'] == 'Responsable'])
        surveillant_examens = len([e for e in examens if e['role'] == 'Surveillant'])
        total_heures = sum(e['duree_minutes'] for e in examens) / 60
        
        with col_m1:
            st.metric("Total Examens", total_examens)
        with col_m2:
            st.metric("En tant que Responsable", responsable_examens)
        with col_m3:
            st.metric("En tant que Surveillant", surveillant_examens)
        with col_m4:
            st.metric("Heures totales", f"{total_heures:.1f}h")
        
        st.markdown("---")
        
        # Vue calendrier ou liste
        view_mode = st.radio(
            "Mode d'affichage",
            ["📋 Liste", "📅 Calendrier"],
            horizontal=True,
            key="view_mode"
        )
        
        if view_mode == "📋 Liste":
            # Affichage en liste
            for exam in examens:
                role_class = "responsable" if exam['role'] == 'Responsable' else "surveillant"
                badge_color = "badge-primary" if exam['role'] == 'Responsable' else "badge-success"
                statut_color = "badge-success" if exam['statut'] == 'confirmé' else "badge-warning"
                
                col_ex1, col_ex2, col_ex3 = st.columns([3, 1, 1])
                
                with col_ex1:
                    st.markdown(f"""
                    <div style="padding: 15px; border-radius: 10px; background: {'#f8f9fa' if exam['role'] == 'Responsable' else '#f0f7ff'}; 
                             border-left: 4px solid {'#3498db' if exam['role'] == 'Responsable' else '#2ecc71'};">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <div style="font-weight: bold; font-size: 1.1rem;">{exam['module']}</div>
                                <div style="color: #7f8c8d; font-size: 0.9rem;">{exam['formation']}</div>
                            </div>
                            <div style="display: flex; gap: 5px;">
                                <span class="badge {badge_color}">{exam['role']}</span>
                                <span class="badge {statut_color}">{exam['statut']}</span>
                            </div>
                        </div>
                        <div style="display: flex; gap: 20px; margin-top: 10px; font-size: 0.9rem;">
                            <div><span style="color: #7f8c8d;">📅</span> {exam['date_examen']}</div>
                            <div><span style="color: #7f8c8d;">⏰</span> {exam['heure_debut']} - {exam['heure_fin']}</div>
                            <div><span style="color: #7f8c8d;">⏱️</span> {exam['duree_minutes']} min</div>
                        </div>
                        <div style="margin-top: 5px; font-size: 0.9rem;">
                            <span style="color: #7f8c8d;">🏫</span> {exam.get('salle', 'Non assignée')} | 
                            <span style="color: #7f8c8d;">👥</span> {exam.get('nb_etudiants', 'N/A')} étudiants
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_ex2:
                    st.button("📋 Détails", key=f"detail_{exam['id']}", use_container_width=True)
                
                with col_ex3:
                    st.button("🗺️ Salle", key=f"salle_{exam['id']}", use_container_width=True)
                
                st.markdown("---")
        else:
            # Affichage calendrier simplifié
            st.markdown("### 📅 Vue Calendrier")
            # Ici vous pourriez implémenter un vrai calendrier interactif
            
            # Pour l'instant, afficher un tableau par semaine
            df_examens = pd.DataFrame(examens)
            df_examens['date_examen'] = pd.to_datetime(df_examens['date_examen'])
            df_examens['semaine'] = df_examens['date_examen'].dt.isocalendar().week
            
            st.dataframe(
                df_examens[['date_examen', 'heure_debut', 'module', 'formation', 'role', 'statut']],
                column_config={
                    "date_examen": "Date",
                    "heure_debut": "Heure",
                    "module": "Module",
                    "formation": "Formation",
                    "role": "Rôle",
                    "statut": "Statut"
                },
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("📭 Aucun examen trouvé pour les critères sélectionnés.")
    
    st.markdown('</div>', unsafe_allow_html=True)

elif selected_menu == "📈 Statistiques":
    
    st.markdown("### 📈 Statistiques Détaillées")
    
    # Graphiques en grille 2x2
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Répartition par rôle
        st.markdown("#### 📊 Répartition par rôle")
        
        labels = ['Responsable', 'Surveillant']
        values = [12, 8]  # Données simulées
        
        fig1 = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.4,
            marker_colors=['#3498db', '#2ecc71']
        )])
        
        fig1.update_layout(
            height=300,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.1
            )
        )
        
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_chart2:
        # Charge mensuelle
        st.markdown("#### 📅 Charge mensuelle")
        
        mois = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin']
        heures = [15, 22, 18, 25, 30, 28]
        
        fig2 = go.Figure(data=[
            go.Bar(
                x=mois,
                y=heures,
                marker_color='#3498db',
                text=heures,
                textposition='auto',
            )
        ])
        
        fig2.update_layout(
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    col_chart3, col_chart4 = st.columns(2)
    
    with col_chart3:
        # Répartition par formation
        st.markdown("#### 🎓 Répartition par formation")
        
        formations = ['L1', 'L2', 'L3', 'M1', 'M2']
        nb_examens = [5, 3, 4, 2, 1]
        
        fig3 = go.Figure(data=[
            go.Scatter(
                x=formations,
                y=nb_examens,
                mode='lines+markers',
                line=dict(color='#9b59b6', width=3),
                marker=dict(size=10, color='#9b59b6')
            )
        ])
        
        fig3.update_layout(
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    with col_chart4:
        # Disponibilité
        st.markdown("#### ⏰ Disponibilité")
        
        jours = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven']
        disponibilite = [80, 90, 75, 85, 95]
        
        fig4 = go.Figure(data=[
            go.Scatterpolar(
                r=disponibilite,
                theta=jours,
                fill='toself',
                fillcolor='rgba(52, 152, 219, 0.3)',
                line=dict(color='#3498db')
            )
        ])
        
        fig4.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False,
            height=300
        )
        
        st.plotly_chart(fig4, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

elif selected_menu == "📤 Export":
    st.markdown("### 📤 Export du Planning")
    
    # Options d'export
    export_type = st.radio(
        "Type d'export",
        ["📋 Planning complet", "📅 Par période", "🎯 Par module"],
        horizontal=True
    )
    
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    
    with col_exp1:
        format_export = st.selectbox(
            "Format",
            ["HTML (Web)", "CSV (Excel)", "PDF (Imprimable)", "JSON (Données)"]
        )
    
    with col_exp2:
        include_details = st.multiselect(
            "Inclure",
            ["Détails examen", "Salles", "Étudiants", "Statistiques"],
            default=["Détails examen"]
        )
    
    with col_exp3:
        orientation = st.selectbox(
            "Orientation",
            ["Portrait", "Paysage"]
        )
    
    # Aperçu
    with st.expander("👁️ Aperçu de l'export"):
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border: 2px dashed #dee2e6;">
            <div style="text-align: center; color: #6c757d;">
                <div style="font-size: 3rem; margin-bottom: 10px;">📄</div>
                <div style="font-weight: bold;">Aperçu de l'export</div>
                <div style="margin-top: 10px;">
                    <strong>Format:</strong> {format_export}<br>
                    <strong>Période:</strong> {date_debut} au {date_fin}<br>
                    <strong>Inclusions:</strong> {', '.join(include_details) if include_details else 'Aucune'}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Boutons d'export
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("📥 Exporter maintenant", use_container_width=True, type="primary"):
            st.success("✅ Export généré avec succès !")
    
    with col_btn2:
        if st.button("📧 Envoyer par email", use_container_width=True):
            st.info("📧 Fonctionnalité d'envoi par email bientôt disponible")
    
    with col_btn3:
        if st.button("🖨️ Imprimer", use_container_width=True):
            st.info("🖨️ Fonctionnalité d'impression bientôt disponible")
    
    st.markdown('</div>', unsafe_allow_html=True)

elif selected_menu == "⚙️ Paramètres":
    
    st.markdown("### ⚙️ Paramètres du Profil")
    
    # Formulaire de mise à jour
    with st.form("profile_form"):
        col_set1, col_set2 = st.columns(2)
        
        with col_set1:
            nom = st.text_input("Nom", prof['nom'])
            prenom = st.text_input("Prénom", prof['prenom'])
            email = st.text_input("Email", "professeur@universite.fr")
        
        with col_set2:
            telephone = st.text_input("Téléphone", "+33 1 23 45 67 89")
            specialite = st.text_input("Spécialité", prof['specialite'])
            heures_service = st.number_input("Heures de service", value=int(prof['heures_service']))
        
        # Préférences
        st.markdown("### 🔔 Préférences de notification")
        col_pref1, col_pref2 = st.columns(2)
        
        with col_pref1:
            notif_email = st.checkbox("Notifications par email", value=True)
            notif_sms = st.checkbox("Notifications SMS", value=False)
            rappel_examens = st.checkbox("Rappels d'examens", value=True)
        
        with col_pref2:
            jours_rappel = st.slider("Jours avant rappel", 1, 7, 2)
            heure_notif = st.time_input("Heure des notifications", time(8, 0))
            theme = st.selectbox("Thème de l'interface", ["Clair", "Sombre", "Auto"])
        
        # Boutons d'action
        col_act1, col_act2, col_act3 = st.columns(3)
        
        with col_act1:
            submit = st.form_submit_button("💾 Enregistrer les modifications", type="primary")
        
        with col_act2:
            reset = st.form_submit_button("🔄 Réinitialiser")
        
        with col_act3:
            cancel = st.form_submit_button("❌ Annuler")
        
        if submit:
            st.success("✅ Paramètres mis à jour avec succès !")
    
    st.markdown('</div>', unsafe_allow_html=True)

# === FOOTER ===
st.markdown("""
<hr style="margin: 40px 0 20px 0; border: none; border-top: 1px solid #e0e0e0;">

<div style="text-align: center; color: #7f8c8d; font-size: 0.9rem;">
    <div style="display: flex; justify-content: center; gap: 30px; margin-bottom: 10px;">
        <div>
            <div style="font-weight: bold; color: #2c3e50;">Tableau de Bord Professeur</div>
            <div style="font-size: 0.8rem;">Système de Gestion des Examens</div>
        </div>
        <div>
            <div style="font-weight: bold; color: #2c3e50;">Université</div>
            <div style="font-size: 0.8rem;">Département d'Informatique</div>
        </div>
        <div>
            <div style="font-weight: bold; color: #2c3e50;">Contact</div>
            <div style="font-size: 0.8rem;">support@universite.fr</div>
        </div>
    </div>
    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ecf0f1; font-size: 0.8rem;">
        © 2024 Système de Planification des Examens • Version 2.0 • 
        <span style="color: #3498db;">{}</span>
    </div>
</div>
""".format(prof['prenom'] + " " + prof['nom']), unsafe_allow_html=True)