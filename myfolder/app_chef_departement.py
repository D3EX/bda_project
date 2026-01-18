# pages/app_chef_departement.py - Version adaptée au login
import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, time, timedelta
import numpy as np
import io
from decimal import Decimal
import os
import toml

# Configuration de la page
st.set_page_config(
    page_title="Vue Stratégique - Chef Département",
    page_icon="👨‍💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS PERSONNALISÉ PROFESSIONNEL
st.markdown("""
<style>
    /* Cache la navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* En-tête principal */
    .main-header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* Cartes de métriques */
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #3949ab;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #1a237e;
        margin-bottom: 5px;
    }
    
    .metric-label {
        font-size: 13px;
        color: #666;
        font-weight: 500;
    }
    
    /* Badges de statut */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
    }
    
    .status-confirmed {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-pending {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .status-cancelled {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    /* Onglets améliorés */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 8px 8px 0 0;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    /* Boutons améliorés */
    .stButton button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Cartes d'examen */
    .examen-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-left: 4px solid #3949ab;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .examen-card:hover {
        border-color: #3949ab;
        box-shadow: 0 4px 12px rgba(57, 73, 171, 0.1);
    }
    
    /* En-têtes de section */
    .section-header {
        border-bottom: 2px solid #3949ab;
        padding-bottom: 0.8rem;
        margin-bottom: 1.5rem;
        color: #1a237e;
        font-weight: 600;
        font-size: 1.3rem;
    }
    
    /* Barre de progression */
    .progress-container {
        background: #f5f5f5;
        border-radius: 10px;
        padding: 8px;
        margin: 10px 0;
    }
    
    .progress-bar {
        height: 8px;
        background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    /* Tags */
    .tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 500;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    
    .tag-info {
        background: #e3f2fd;
        color: #1565c0;
    }
    
    .tag-success {
        background: #e8f5e9;
        color: #2e7d32;
    }
    
    .tag-warning {
        background: #fff8e1;
        color: #f57c00;
    }
    
    .tag-primary {
        background: #e8eaf6;
        color: #3949ab;
    }
    
    /* Tableaux */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    /* Sidebar améliorée */
    .sidebar-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #3949ab 0%, #283593 100%);
        color: white;
        border-radius: 0 0 10px 10px;
        margin: -1rem -1rem 1rem -1rem;
    }
    
    .user-avatar {
        width: 70px;
        height: 70px;
        border-radius: 50%;
        background: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem;
        color: #3949ab;
        font-size: 1.8rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Pied de page */
    .footer {
        text-align: center;
        color: #666;
        font-size: 12px;
        padding: 1.5rem;
        margin-top: 2rem;
        border-top: 1px solid #e0e0e0;
        background: #f8f9fa;
        border-radius: 8px;
    }
    
    /* Filtres */
    .filter-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin-bottom: 1.5rem;
    }
    
    /* Graphiques */
    .plotly-chart {
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# VÉRIFICATION DE CONNEXION
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⛔ Accès non autorisé. Veuillez vous connecter.")
    if st.button("🔐 Se connecter"):
        st.switch_page("pages/log.py")
    st.stop()

# VÉRIFICATION DU RÔLE
if st.session_state.role != 'chef_departement':
    st.error(f"⛔ Cette page est réservée aux chefs de département. Votre rôle: {st.session_state.role}")
    if st.button("🏠 Retour à l'accueil"):
        st.switch_page("app.py")
    st.stop()

# L'ID de l'utilisateur connecté
CHEF_ID = st.session_state.user_id

# ============================================================================
# FONCTIONS UTILITAIRES (INCHANGÉES)
# ============================================================================

def load_secrets():
    """Charger les secrets de configuration"""
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

@st.cache_resource
def init_connection():
    """Initialiser la connexion MySQL"""
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

def run_query(query, params=None, fetch=True):
    """Exécuter une requête SQL"""
    try:
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            result = cursor.fetchall()
            
            # Convertir les timedelta en time et Decimal en float
            for row in result:
                for key, value in row.items():
                    if isinstance(value, timedelta):
                        total_seconds = value.total_seconds()
                        hours = int(total_seconds // 3600)
                        minutes = int((total_seconds % 3600) // 60)
                        seconds = int(total_seconds % 60)
                        row[key] = time(hours, minutes, seconds)
                    elif isinstance(value, Decimal):
                        row[key] = float(value)
            
            cursor.close()
            return result
        else:
            conn.commit()
            cursor.close()
            return True
    except Error as e:
        st.error(f"Erreur SQL: {e}")
        return None

def get_departement_chef(chef_id):
    """Récupérer le département dont l'utilisateur est responsable"""
    query = """
        SELECT id, nom 
        FROM departements 
        WHERE responsable_id = %s
    """
    result = run_query(query, (chef_id,))
    return result[0] if result else None

# ============================================================================
# FONCTIONS SPÉCIFIQUES AU DÉPARTEMENT (INCHANGÉES)
# ============================================================================

def get_info_departement(dept_id):
    """Informations générales du département"""
    query = """
        SELECT 
            d.nom,
            COUNT(DISTINCT f.id) as nb_formations,
            COUNT(DISTINCT m.id) as nb_modules,
            COUNT(DISTINCT p.id) as nb_professeurs,
            COUNT(DISTINCT et.id) as nb_etudiants,
            COUNT(DISTINCT le.id) as nb_salles,
            (SELECT COUNT(DISTINCT e.id) FROM examens e 
             JOIN modules m ON e.module_id = m.id 
             JOIN formations f ON m.formation_id = f.id 
             WHERE f.dept_id = %s AND e.date_examen BETWEEN %s AND %s) as nb_examens_planifies
        FROM departements d
        LEFT JOIN formations f ON d.id = f.dept_id
        LEFT JOIN modules m ON f.id = m.formation_id
        LEFT JOIN professeurs p ON d.id = p.dept_id
        LEFT JOIN etudiants et ON f.id = et.formation_id
        LEFT JOIN lieu_examen le ON 1=1
        WHERE d.id = %s
        GROUP BY d.id
    """
    return run_query(query, (dept_id, date_debut, date_fin, dept_id))

def get_examens_departement(dept_id, date_debut, date_fin):
    """Tous les examens du département"""
    query = """
        SELECT 
            e.id,
            e.date_examen,
            e.heure_debut,
            e.heure_fin,
            e.duree_minutes,
            e.statut,
            e.session,
            m.nom as module,
            f.nom as formation,
            CONCAT(p.nom, ' ', p.prenom) as professeur,
            CONCAT(ps.nom, ' ', ps.prenom) as surveillant,
            le.nom as salle,
            le.type as type_salle,
            le.capacite,
            COUNT(DISTINCT i.etudiant_id) as nb_etudiants,
            ROUND((COUNT(DISTINCT i.etudiant_id) / le.capacite) * 100, 1) as taux_occupation
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN departements d ON f.dept_id = d.id
        LEFT JOIN professeurs p ON e.professeur_id = p.id
        LEFT JOIN professeurs ps ON e.surveillant_id = ps.id
        JOIN lieu_examen le ON e.salle_id = le.id
        LEFT JOIN inscriptions i ON m.id = i.module_id AND i.annee_scolaire = e.annee_scolaire
        WHERE d.id = %s
        AND e.date_examen BETWEEN %s AND %s
        GROUP BY e.id
        ORDER BY e.date_examen, e.heure_debut
    """
    return run_query(query, (dept_id, date_debut, date_fin))

def get_statistiques_validation_departement(dept_id, date_debut, date_fin):
    """Statistiques de validation pour le département"""
    query = """
        SELECT 
            f.nom as formation,
            COUNT(DISTINCT e.id) as total_examens,
            SUM(CASE WHEN e.statut = 'planifié' THEN 1 ELSE 0 END) as en_attente,
            SUM(CASE WHEN e.statut = 'confirmé' THEN 1 ELSE 0 END) as confirmes,
            SUM(CASE WHEN e.statut = 'annulé' THEN 1 ELSE 0 END) as annules,
            ROUND((SUM(CASE WHEN e.statut = 'confirmé' THEN 1 ELSE 0 END) / 
                   COUNT(DISTINCT e.id)) * 100, 1) as taux_validation
        FROM formations f
        JOIN modules m ON f.id = m.formation_id
        JOIN examens e ON m.id = e.module_id
        WHERE f.dept_id = %s
        AND e.date_examen BETWEEN %s AND %s
        GROUP BY f.id
        HAVING total_examens > 0
        ORDER BY taux_validation DESC
    """
    return run_query(query, (dept_id, date_debut, date_fin))

def get_conflits_par_formation(dept_id, date_debut, date_fin):
    """Conflits détaillés par formation"""
    query = """
        SELECT 
            f.nom as formation,
            COUNT(DISTINCT e.id) as total_examens,
            SUM(CASE WHEN ce.conflit_etudiant > 0 THEN 1 ELSE 0 END) as conflits_etudiants,
            SUM(CASE WHEN cs.conflit_salle > 0 THEN 1 ELSE 0 END) as conflits_salles,
            SUM(CASE WHEN cp.conflit_professeur > 0 THEN 1 ELSE 0 END) as conflits_professeurs,
            SUM(CASE WHEN ce.conflit_etudiant > 0 OR cs.conflit_salle > 0 OR cp.conflit_professeur > 0 THEN 1 ELSE 0 END) as total_conflits,
            ROUND((SUM(CASE WHEN ce.conflit_etudiant > 0 OR cs.conflit_salle > 0 OR cp.conflit_professeur > 0 THEN 1 ELSE 0 END) / 
                   COUNT(DISTINCT e.id)) * 100, 1) as taux_conflits
        FROM formations f
        JOIN modules m ON f.id = m.formation_id
        JOIN examens e ON m.id = e.module_id AND e.date_examen BETWEEN %s AND %s
        LEFT JOIN (
            SELECT e1.module_id, COUNT(*) as conflit_etudiant
            FROM inscriptions e1
            JOIN examens ex ON e1.module_id = ex.module_id
            WHERE ex.date_examen BETWEEN %s AND %s
            GROUP BY e1.module_id, e1.etudiant_id
            HAVING COUNT(DISTINCT ex.date_examen) < COUNT(DISTINCT ex.id)
        ) ce ON e.module_id = ce.module_id
        LEFT JOIN (
            SELECT e1.salle_id, e1.date_examen, COUNT(*) as conflit_salle
            FROM examens e1
            WHERE e1.date_examen BETWEEN %s AND %s
            GROUP BY e1.salle_id, e1.date_examen
            HAVING COUNT(*) > 1
        ) cs ON e.salle_id = cs.salle_id AND e.date_examen = cs.date_examen
        LEFT JOIN (
            SELECT e1.professeur_id, e1.date_examen, COUNT(*) as conflit_professeur
            FROM examens e1
            WHERE e1.date_examen BETWEEN %s AND %s
            GROUP BY e1.professeur_id, e1.date_examen
            HAVING COUNT(*) > 1
        ) cp ON e.professeur_id = cp.professeur_id AND e.date_examen = cp.date_examen
        WHERE f.dept_id = %s
        GROUP BY f.id
        ORDER BY taux_conflits DESC
    """
    return run_query(query, (date_debut, date_fin, date_debut, date_fin, 
                           date_debut, date_fin, date_debut, date_fin, dept_id))

def get_professeurs_departement(dept_id):
    """Liste des professeurs du département"""
    query = """
        SELECT 
            p.id,
            CONCAT(p.nom, ' ', p.prenom) as nom_complet,
            p.specialite,
            p.heures_service,
            COUNT(DISTINCT e.id) as nb_examens_responsable,
            COUNT(DISTINCT e2.id) as nb_examens_surveillant,
            ROUND(SUM(e.duree_minutes)/60, 1) as heures_responsable,
            ROUND(SUM(e2.duree_minutes)/60, 1) as heures_surveillant,
            ROUND((COALESCE(SUM(e.duree_minutes), 0) + COALESCE(SUM(e2.duree_minutes), 0))/60, 1) as total_heures
        FROM professeurs p
        LEFT JOIN examens e ON p.id = e.professeur_id AND e.date_examen BETWEEN %s AND %s
        LEFT JOIN examens e2 ON p.id = e2.surveillant_id AND e2.date_examen BETWEEN %s AND %s
        WHERE p.dept_id = %s
        GROUP BY p.id
        ORDER BY p.nom, p.prenom
    """
    return run_query(query, (date_debut, date_fin, date_debut, date_fin, dept_id))

def get_formations_departement(dept_id):
    """Liste des formations du département"""
    query = """
        SELECT 
            f.id,
            f.nom,
            COUNT(DISTINCT m.id) as nb_modules,
            COUNT(DISTINCT et.id) as nb_etudiants,
            COUNT(DISTINCT e.id) as nb_examens_planifies
        FROM formations f
        LEFT JOIN modules m ON f.id = m.formation_id
        LEFT JOIN etudiants et ON f.id = et.formation_id
        LEFT JOIN examens e ON m.id = e.module_id AND e.date_examen BETWEEN %s AND %s
        WHERE f.dept_id = %s
        GROUP BY f.id
        ORDER BY f.nom
    """
    return run_query(query, (date_debut, date_fin, dept_id))

def valider_examen_departement(examen_id):
    """Valider un examen spécifique"""
    query = "UPDATE examens SET statut = 'confirmé' WHERE id = %s"
    return run_query(query, (examen_id,), False)

def valider_tous_examens_formation(formation_id, date_debut, date_fin):
    """Valider tous les examens d'une formation"""
    query = """
        UPDATE examens e
        JOIN modules m ON e.module_id = m.id
        SET e.statut = 'confirmé'
        WHERE m.formation_id = %s
        AND e.date_examen BETWEEN %s AND %s
        AND e.statut = 'planifié'
    """
    return run_query(query, (formation_id, date_debut, date_fin), False)

def get_occupation_salles_departement(dept_id, date_debut, date_fin):
    """Occupation des salles pour le département"""
    query = """
        SELECT 
            le.type,
            le.nom as salle,
            le.capacite,
            COUNT(DISTINCT e.id) as nb_examens,
            COUNT(DISTINCT e.date_examen) as jours_utilises,
            ROUND((SUM(e.duree_minutes) / (480 * COUNT(DISTINCT e.date_examen))) * 100, 1) as taux_occupation
        FROM lieu_examen le
        JOIN examens e ON le.id = e.salle_id 
            AND e.date_examen BETWEEN %s AND %s
            AND e.statut != 'annulé'
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        WHERE f.dept_id = %s
        GROUP BY le.id
        ORDER BY le.type, taux_occupation DESC
    """
    return run_query(query, (date_debut, date_fin, dept_id))

# ============================================================================
# PAGES AVEC DESIGN AMÉLIORÉ
# ============================================================================

def render_tableau_de_bord():
    """Page: Tableau de Bord Département"""
    # En-tête principal
    col_title, col_stats = st.columns([3, 1])
    with col_title:
        st.title("📊 Tableau de Bord Département")
        st.markdown(f"**Département:** {departement_nom} | **Période:** {date_debut} au {date_fin}")
    with col_stats:
        examens = get_examens_departement(DEPARTEMENT_ID, date_debut, date_fin)
        if examens:
            df_examens = pd.DataFrame(examens)
            total_examens = len(df_examens)
            confirmes = len(df_examens[df_examens['statut'] == 'confirmé'])
            taux_validation = (confirmes/total_examens*100) if total_examens > 0 else 0
            st.markdown(f'<div class="metric-card" style="text-align: center; background: rgba(255,255,255,0.1); border: none;">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value" style="color: white;">{taux_validation:.1f}%</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-label" style="color: rgba(255,255,255,0.9);">Taux Validation</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Informations générales
    info = get_info_departement(DEPARTEMENT_ID)
    
    if info:
        info_data = info[0]
        
        # Métriques principales - Design amélioré
        st.markdown('<div class="section-header">📈 Aperçu du Département</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = [
            ("Formations", "🎓", int(info_data.get('nb_formations', 0)), "#3949ab"),
            ("Modules", "📚", int(info_data.get('nb_modules', 0)), "#2196F3"),
            ("Professeurs", "👨‍🏫", int(info_data.get('nb_professeurs', 0)), "#4CAF50"),
            ("Examens", "📅", int(info_data.get('nb_examens_planifies', 0)), "#FF9800")
        ]
        
        for i, (label, icon, value, color) in enumerate(metrics):
            with [col1, col2, col3, col4][i]:
                st.markdown(f'<div style="display: flex; align-items: center; justify-content: space-between;">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{value}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size: 24px; color: {color};">{icon}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-label">{label}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Deuxième ligne de métriques
        col5, col6, col7, col8 = st.columns(4)
        
        metrics2 = [
            ("Étudiants", "👥", int(info_data.get('nb_etudiants', 0)), "#9C27B0"),
            ("Salles", "🏫", int(info_data.get('nb_salles', 0)), "#00BCD4"),
            ("Formations Actives", "🎯", len(get_formations_departement(DEPARTEMENT_ID)) if get_formations_departement(DEPARTEMENT_ID) else 0, "#FF5722"),
            ("Occupation Moy.", "📊", f"{float(get_occupation_salles_departement(DEPARTEMENT_ID, date_debut, date_fin)[0]['taux_occupation']):.1f}%" if get_occupation_salles_departement(DEPARTEMENT_ID, date_debut, date_fin) else "0%", "#607D8B")
        ]
        
        for i, (label, icon, value, color) in enumerate(metrics2):
            with [col5, col6, col7, col8][i]:
                st.markdown(f'<div style="display: flex; align-items: center; justify-content: space-between;">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{value}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size: 24px; color: {color};">{icon}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-label">{label}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Graphiques rapides
    st.markdown('<div class="section-header">📊 Visualisations</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div style="font-weight: 600; color: #1a237e; margin-bottom: 1rem;">📊 Examens par Formation</div>', unsafe_allow_html=True)
        examens = get_examens_departement(DEPARTEMENT_ID, date_debut, date_fin)
        
        if examens:
            df_examens = pd.DataFrame(examens)
            exams_par_formation = df_examens.groupby('formation').size().reset_index(name='nb_examens')
            
            if not exams_par_formation.empty:
                fig = px.pie(exams_par_formation, values='nb_examens', names='formation',
                            title="", hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
                fig.update_layout(showlegend=True, height=300, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div style="font-weight: 600; color: #1a237e; margin-bottom: 1rem;">📈 Évolution Journalière</div>', unsafe_allow_html=True)
        if examens:
            df_examens = pd.DataFrame(examens)
            df_examens['date_examen'] = pd.to_datetime(df_examens['date_examen'])
            exams_par_jour = df_examens.groupby('date_examen').size().reset_index(name='nb_examens')
            
            if not exams_par_jour.empty:
                fig = px.line(exams_par_jour, x='date_examen', y='nb_examens',
                             title="", markers=True, line_shape='spline',
                             color_discrete_sequence=['#3949ab'])
                fig.update_layout(height=300, xaxis_title="Date", yaxis_title="Examens",
                                margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Derniers examens
    st.markdown('<div class="section-header">📋 Derniers Examens Planifiés</div>', unsafe_allow_html=True)
    if examens:
        df_recent = pd.DataFrame(examens)
        df_recent = df_recent.sort_values('date_examen', ascending=False).head(8)
        
        for _, row in df_recent.iterrows():
            with st.container():
                st.markdown('<div class="examen-card">', unsafe_allow_html=True)
                col_info, col_stat = st.columns([3, 1])
                
                with col_info:
                    # Status badge
                    if row['statut'] == 'confirmé':
                        status_class = "status-confirmed"
                        status_text = "✅ Validé"
                    elif row['statut'] == 'annulé':
                        status_class = "status-cancelled"
                        status_text = "❌ Annulé"
                    else:
                        status_class = "status-pending"
                        status_text = "⏳ En attente"
                    
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                        <div style="font-weight: 600; font-size: 16px; color: #1a237e;">{row['module']}</div>
                        <span class="{status_class}">{status_text}</span>
                    </div>
                    <div style="color: #666; margin-bottom: 12px; font-size: 14px;">{row['formation']}</div>
                    <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px;">
                        <span class="tag tag-primary">📅 {row['date_examen']}</span>
                        <span class="tag tag-warning">⏰ {row['heure_debut']}-{row['heure_fin']}</span>
                        <span class="tag tag-info">🏫 {row['salle']}</span>
                        <span class="tag tag-success">👥 {int(row['nb_etudiants'])} étudiants</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_stat:
                    occupation_rate = float(row['taux_occupation']) if pd.notnull(row['taux_occupation']) else 0
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="font-size: 20px; font-weight: 700; color: #1a237e;">{occupation_rate:.1f}%</div>
                        <div style="font-size: 11px; color: #666; margin-bottom: 8px;">Occupation</div>
                        <div style="height: 6px; background: #e0e0e0; border-radius: 3px; overflow: hidden;">
                            <div style="width: {occupation_rate}%; height: 100%; background: {'#4CAF50' if occupation_rate < 80 else '#FF9800' if occupation_rate < 95 else '#F44336'};"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

def render_validation_edt():
    """Page: Validation des Emplois du Temps"""
    # En-tête principal
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("✅ Validation des Emplois du Temps")
    st.markdown(f"**Validez et gérez les examens planifiés pour le département {departement_nom}**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Validation Individuelle", "🎯 Validation par Formation"])
    
    with tab1:
       
        st.subheader("🔍 Filtres de Recherche")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            statut_filter = st.selectbox(
                "Statut",
                options=['Tous', 'planifié', 'confirmé', 'annulé']
            )
        
        with col2:
            formations = get_formations_departement(DEPARTEMENT_ID)
            formation_options = ['Toutes'] + [f['nom'] for f in formations]
            formation_filter = st.selectbox("Formation", formation_options)
        
        with col3:
            type_options = ['Tous', 'Amphi', 'Salle TD', 'Laboratoire']
            type_filter = st.selectbox("Type de salle", type_options)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Récupérer les examens
        examens = get_examens_departement(DEPARTEMENT_ID, date_debut, date_fin)
        
        if examens:
            df_examens = pd.DataFrame(examens)
            
            # Appliquer les filtres
            if statut_filter != 'Tous':
                df_examens = df_examens[df_examens['statut'] == statut_filter]
            
            if formation_filter != 'Toutes':
                df_examens = df_examens[df_examens['formation'] == formation_filter]
            
            if type_filter != 'Tous':
                df_examens = df_examens[df_examens['type_salle'] == type_filter]
            
            # Métriques de filtrage
            st.markdown('<div style="display: grid; gap: 1rem; margin-bottom: 2rem;">', unsafe_allow_html=True)
            
            metrics_data = [
                ("Examens filtrés", len(df_examens), "#3949ab"),
                ("En attente", len(df_examens[df_examens['statut'] == 'planifié']), "#FF9800"),
                ("Validés", len(df_examens[df_examens['statut'] == 'confirmé']), "#4CAF50"),
                ("Annulés", len(df_examens[df_examens['statut'] == 'annulé']), "#F44336")
            ]
            
            for label, value, color in metrics_data:
                st.markdown(f'''
                <div class="metric-card" style="text-align: center; border-left-color: {color};">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Afficher les examens
            st.markdown('<div class="section-header">📝 Examens à Valider</div>', unsafe_allow_html=True)
            
            for idx, row in df_examens.iterrows():
                with st.container():
                 
                    col_info, col_action = st.columns([4, 1])
                    
                    with col_info:
                        # Définir la couleur selon le statut
                        if row['statut'] == 'confirmé':
                            status_class = "status-confirmed"
                            status_icon = "✅"
                            status_text = "Validé"
                        elif row['statut'] == 'annulé':
                            status_class = "status-cancelled"
                            status_icon = "❌"
                            status_text = "Annulé"
                        else:
                            status_class = "status-pending"
                            status_icon = "⏳"
                            status_text = "En attente"
                        
                        # Occupation bar
                        occupation_rate = float(row['taux_occupation']) if pd.notnull(row['taux_occupation']) else 0
                        
                        st.markdown(f"""
                        <div style="display: flex; align-items: start; justify-content: space-between; margin-bottom: 12px;">
                            <div>
                                <div style="font-weight: 600; font-size: 16px; color: #1a237e;">{row['module']}</div>
                                <div style="color: #666; font-size: 14px;">{row['formation']}</div>
                            </div>
                            <span class="{status_class}">{status_icon} {status_text}</span>
                        </div>
                        
                        <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px;">
                            <span class="tag tag-primary">📅 {row['date_examen']}</span>
                            <span class="tag tag-warning">⏰ {row['heure_debut']}-{row['heure_fin']}</span>
                            <span class="tag tag-info">🏫 {row['salle']} ({row['type_salle']})</span>
                            <span class="tag tag-success">👨‍🏫 {row['professeur'] or 'Non assigné'}</span>
                        </div>
                        
                        <div style="background: #f8f9fa; padding: 10px; border-radius: 6px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                                <span style="font-size: 12px; color: #666;">Occupation de la salle</span>
                                <span style="font-size: 12px; font-weight: 600; color: #333;">{occupation_rate:.1f}%</span>
                            </div>
                            <div style="height: 6px; background: #e0e0e0; border-radius: 3px; overflow: hidden;">
                                <div style="width: {occupation_rate}%; height: 100%; background: {'#4CAF50' if occupation_rate < 80 else '#FF9800' if occupation_rate < 95 else '#F44336'};"></div>
                            </div>
                            <div style="font-size: 11px; color: #666; margin-top: 4px;">{int(row['nb_etudiants'])} étudiants sur {int(row['capacite'])} places</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_action:
                        st.write("")
                        if row['statut'] == 'planifié':
                            if st.button(f"✅ Valider", 
                                        key=f"val_{row['id']}", 
                                        use_container_width=True,
                                        type="primary"):
                                if valider_examen_departement(row['id']):
                                    st.success(f"✓ Examen {row['module']} validé!")
                                    st.rerun()
                        elif row['statut'] == 'confirmé':
                            st.success("✅ Validé")
                        else:
                            st.error("❌ Annulé")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.info("ℹ️ Aucun examen trouvé pour la période sélectionnée.")
    
    with tab2:
        st.markdown('<div class="section-header">🎯 Validation Globale par Formation</div>', unsafe_allow_html=True)
        
        # Statistiques par formation
        stats = get_statistiques_validation_departement(DEPARTEMENT_ID, date_debut, date_fin)
        
        if stats:
            df_stats = pd.DataFrame(stats)
            
            # Convertir les colonnes en float
            for col in ['total_examens', 'confirmes', 'en_attente', 'annules', 'taux_validation']:
                if col in df_stats.columns:
                    df_stats[col] = pd.to_numeric(df_stats[col], errors='coerce').fillna(0)
            
            for _, formation in df_stats.iterrows():
                with st.container():
                    st.markdown('<div class="examen-card">', unsafe_allow_html=True)
                    col_stat, col_action = st.columns([3, 1])
                    
                    with col_stat:
                        # Calculer la progression
                        confirmes_float = float(formation['confirmes'])
                        total_examens_float = float(formation['total_examens'])
                        progress = (confirmes_float / total_examens_float) if total_examens_float > 0 else 0
                        
                        st.markdown(f"""
                        <div style="font-weight: 600; font-size: 16px; color: #1a237e; margin-bottom: 12px;">🎓 {formation['formation']}</div>
                        
                        <div style="margin-bottom: 15px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                                <span style="font-size: 12px; color: #666;">Progression de validation</span>
                                <span style="font-size: 12px; font-weight: 600; color: #1a237e;">{int(formation['confirmes'])}/{int(formation['total_examens'])}</span>
                            </div>
                            <div style="height: 8px; background: #e0e0e0; border-radius: 4px; overflow: hidden;">
                                <div style="width: {progress*100}%; height: 100%; background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);"></div>
                            </div>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                            <div style="text-align: center; padding: 8px; background: #d4edda; border-radius: 6px;">
                                <div style="font-size: 18px; font-weight: 700; color: #2e7d32;">{int(formation['confirmes'])}</div>
                                <div style="font-size: 11px; color: #2e7d32;">Confirmés</div>
                            </div>
                            <div style="text-align: center; padding: 8px; background: #fff3cd; border-radius: 6px;">
                                <div style="font-size: 18px; font-weight: 700; color: #f57c00;">{int(formation['en_attente'])}</div>
                                <div style="font-size: 11px; color: #f57c00;">En attente</div>
                            </div>
                            <div style="text-align: center; padding: 8px; background: #f8d7da; border-radius: 6px;">
                                <div style="font-size: 18px; font-weight: 700; color: #c62828;">{int(formation['annules'])}</div>
                                <div style="font-size: 11px; color: #c62828;">Annulés</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_action:
                        st.write("")
                        if formation['en_attente'] > 0:
                            # Récupérer l'ID de la formation
                            formation_id_query = run_query(
                                "SELECT id FROM formations WHERE nom = %s AND dept_id = %s", 
                                (formation['formation'], DEPARTEMENT_ID)
                            )
                            if formation_id_query:
                                formation_id = formation_id_query[0]['id']
                                if st.button(f"✅ Tout Valider", 
                                           key=f"val_all_{formation_id}", 
                                           use_container_width=True,
                                           type="primary"):
                                    if valider_tous_examens_formation(formation_id, date_debut, date_fin):
                                        st.success(f"✓ Tous les examens de {formation['formation']} validés!")
                                        st.rerun()
                        else:
                            st.markdown('<div style="text-align: center; padding: 10px; background: #d4edda; border-radius: 6px;">', unsafe_allow_html=True)
                            st.markdown("✅ Complètement<br>validé", unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Graphique de synthèse
            st.markdown('<div class="section-header">📊 Synthèse de Validation</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            
            # Convertir les valeurs pour le graphique
            df_stats['confirmes_float'] = df_stats['confirmes'].astype(float)
            df_stats['en_attente_float'] = df_stats['en_attente'].astype(float)
            df_stats['annules_float'] = df_stats['annules'].astype(float)
            
            fig = px.bar(df_stats, x='formation', y=['confirmes_float', 'en_attente_float', 'annules_float'],
                        title="",
                        labels={'value': "Nombre d'examens", 'formation': 'Formation', 'variable': 'Statut'},
                        barmode='stack',
                        color_discrete_sequence=['#4CAF50', '#FFC107', '#F44336'])
            
            fig.update_layout(
                height=400,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#333'),
                xaxis=dict(
                    tickangle=-45,
                    gridcolor='#f0f0f0'
                ),
                yaxis=dict(
                    gridcolor='#f0f0f0'
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            # Renommer les légendes
            fig.for_each_trace(lambda t: t.update(name='Confirmés' if 'confirmes' in t.name else 
                                                'En attente' if 'attente' in t.name else 'Annulés'))
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# FONCTIONS DE RENDU MANQUANTES AJOUTÉES
# ============================================================================

def render_statistiques_departement():
    """Page: Statistiques du Département"""
    # En-tête principal
    st.title("📊 Statistiques du Département")
    st.markdown(f"**Analyse détaillée des performances du département {departement_nom}**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📈 Vue Globale", "👨‍🏫 Ressources Humaines", "🏫 Ressources Matérielles"])
    
    with tab1:
        st.markdown('<div class="section-header">📈 Vue Globale du Département</div>', unsafe_allow_html=True)
        
        # Récupérer les données
        examens = get_examens_departement(DEPARTEMENT_ID, date_debut, date_fin)
        
        if examens:
            df_examens = pd.DataFrame(examens)
            
            # KPIs avec design amélioré
            col1, col2, col3, col4 = st.columns(4)
            
            kpis = [
                ("Total Examens", len(df_examens), "📊", "#3949ab"),
                ("Formations", df_examens['formation'].nunique(), "🎓", "#2196F3"),
                ("Salles utilisées", df_examens['salle'].nunique(), "🏫", "#4CAF50"),
                ("Professeurs", df_examens['professeur'].nunique(), "👨‍🏫", "#FF9800")
            ]
            
            for i, (label, value, icon, color) in enumerate(kpis):
                with [col1, col2, col3, col4][i]:
                    st.markdown(f'<div style="display: flex; align-items: center; justify-content: space-between;">', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-value">{value}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="font-size: 24px; color: {color};">{icon}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-label">{label}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Graphiques
            st.markdown('<div class="section-header">📈 Visualisations</div>', unsafe_allow_html=True)
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown('<div style="font-weight: 600; color: #1a237e; margin-bottom: 1rem;">📊 Répartition par Statut</div>', unsafe_allow_html=True)
                # Répartition par statut
                statuts = df_examens['statut'].value_counts().reset_index()
                statuts.columns = ['statut', 'count']
                
                fig = px.pie(statuts, values='count', names='statut',
                            title="", hole=0.3,
                            color_discrete_map={'planifié': '#FFC107', 'confirmé': '#4CAF50', 'annulé': '#F44336'})
                fig.update_layout(showlegend=True, height=300, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_chart2:
                st.markdown('<div style="font-weight: 600; color: #1a237e; margin-bottom: 1rem;">📈 Charge Journalière</div>', unsafe_allow_html=True)
                # Charge par jour
                df_examens['date_examen'] = pd.to_datetime(df_examens['date_examen'])
                charge_jour = df_examens.groupby('date_examen').agg({
                    'id': 'count',
                    'duree_minutes': 'sum'
                }).reset_index()
                
                fig = px.bar(charge_jour, x='date_examen', y='id',
                            title="",
                            labels={'id': "Nombre d'examens", 'date_examen': 'Date'},
                            color_discrete_sequence=['#3949ab'])
                fig.update_layout(height=300, xaxis_title="Date", yaxis_title="Examens",
                                margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Tableau récapitulatif
            st.markdown('<div class="section-header">📋 Récapitulatif par Formation</div>', unsafe_allow_html=True)
            
            recap = df_examens.groupby('formation').agg({
                'id': 'count',
                'nb_etudiants': 'sum',
                'duree_minutes': 'sum',
                'statut': lambda x: (x == 'confirmé').sum()
            }).reset_index()
            
            recap.columns = ['Formation', 'Nb Examens', 'Total Étudiants', 'Durée Totale (min)', 'Examens Validés']
            
            # Convertir les valeurs en float
            recap['Total Étudiants'] = recap['Total Étudiants'].astype(float)
            recap['Durée Totale (min)'] = recap['Durée Totale (min)'].astype(float)
            recap['Examens Validés'] = recap['Examens Validés'].astype(float)
            recap['Nb Examens'] = recap['Nb Examens'].astype(float)
            
            recap['Taux Validation'] = (recap['Examens Validés'] / recap['Nb Examens'] * 100).round(1)
            recap['Durée Totale (min)'] = recap['Durée Totale (min)'].astype(int)
            recap['Nb Examens'] = recap['Nb Examens'].astype(int)
            recap['Total Étudiants'] = recap['Total Étudiants'].astype(int)
            recap['Examens Validés'] = recap['Examens Validés'].astype(int)
            
            st.dataframe(recap, use_container_width=True)
    
    with tab2:
        render_statistiques_rh()
    
    with tab3:
        render_statistiques_rm()

def render_statistiques_rh():
    """Sous-page: Statistiques des Ressources Humaines"""
    st.markdown('<div class="section-header">👨‍🏫 Statistiques des Ressources Humaines</div>', unsafe_allow_html=True)
    
    # Récupérer les professeurs
    professeurs = get_professeurs_departement(DEPARTEMENT_ID)
    
    if professeurs:
        df_profs = pd.DataFrame(professeurs)
        
        # Convertir les colonnes en float
        for col in ['total_heures', 'heures_responsable', 'heures_surveillant', 'nb_examens_responsable', 'nb_examens_surveillant']:
            if col in df_profs.columns:
                df_profs[col] = pd.to_numeric(df_profs[col], errors='coerce').fillna(0)
            
        # Métriques avec design amélioré
        col1, col2, col3 = st.columns(3)
        
        metrics_rh = [
            ("Charge moyenne", f"{float(df_profs['total_heures'].mean()):.1f}h", "⚖️", "#4CAF50"),
            ("Professeurs surveillants", df_profs[df_profs['nb_examens_surveillant'] > 0].shape[0], "👁️", "#2196F3"),
            ("Professeurs responsables", df_profs[df_profs['nb_examens_responsable'] > 0].shape[0], "🎯", "#FF9800")
        ]
        
        for i, (label, value, icon, color) in enumerate(metrics_rh):
            with [col1, col2, col3][i]:
                st.markdown(f'<div style="display: flex; align-items: center; justify-content: space-between;">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{value}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size: 24px; color: {color};">{icon}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-label">{label}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Graphique de charge
        st.markdown('<div class="section-header">📊 Charge de Travail des Professeurs</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        
        df_profs_sorted = df_profs.sort_values('total_heures', ascending=False).head(10)
        
        fig = px.bar(df_profs_sorted, x='nom_complet', y='total_heures',
                    title="",
                    labels={'nom_complet': 'Professeur', 'total_heures': 'Total Heures'},
                    text='total_heures',
                    color='total_heures',
                    color_continuous_scale='RdYlGn_r')
        
        fig.update_traces(texttemplate='%{text:.1f}h', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tableau détaillé
        st.markdown('<div class="section-header">📋 Détail par Professeur</div>', unsafe_allow_html=True)
        
        df_display = df_profs[['nom_complet', 'specialite', 'nb_examens_responsable', 
                              'nb_examens_surveillant', 'heures_responsable', 
                              'heures_surveillant', 'total_heures']].copy()
        
        # Formater l'affichage
        df_display['total_heures'] = df_display['total_heures'].apply(lambda x: f"{float(x):.1f}h")
        df_display['heures_responsable'] = df_display['heures_responsable'].apply(lambda x: f"{float(x):.1f}h" if x else "0.0h")
        df_display['heures_surveillant'] = df_display['heures_surveillant'].apply(lambda x: f"{float(x):.1f}h" if x else "0.0h")
        
        st.dataframe(
            df_display.sort_values('total_heures', ascending=False, key=lambda col: col.str.replace('h', '').astype(float)),
            column_config={
                "nom_complet": "Professeur",
                "specialite": "Spécialité",
                "nb_examens_responsable": "Nb Examens Responsable",
                "nb_examens_surveillant": "Nb Examens Surveillant",
                "heures_responsable": "Heures Responsable",
                "heures_surveillant": "Heures Surveillant",
                "total_heures": "Total Heures"
            },
            use_container_width=True
        )

def render_statistiques_rm():
    """Sous-page: Statistiques des Ressources Matérielles"""
    st.markdown('<div class="section-header">🏫 Statistiques des Ressources Matérielles</div>', unsafe_allow_html=True)
    
    # Occupation des salles
    occupation = get_occupation_salles_departement(DEPARTEMENT_ID, date_debut, date_fin)
    
    if occupation:
        df_occupation = pd.DataFrame(occupation)
        
        # Convertir les colonnes en float
        for col in ['taux_occupation', 'capacite', 'nb_examens']:
            if col in df_occupation.columns:
                df_occupation[col] = pd.to_numeric(df_occupation[col], errors='coerce').fillna(0)
            
        # Métriques avec design amélioré
        col1, col2, col3 = st.columns(3)
        
        metrics_rm = [
            ("Occupation moyenne", f"{float(df_occupation['taux_occupation'].mean()):.1f}%", "📊", "#4CAF50"),
            (f"Salles utilisées", f"{df_occupation[df_occupation['nb_examens'] > 0].shape[0]}/{df_occupation.shape[0]}", "🏫", "#2196F3"),
            ("Capacité moyenne", f"{float(df_occupation['capacite'].mean()):.0f} places", "👥", "#FF9800")
        ]
        
        for i, (label, value, icon, color) in enumerate(metrics_rm):
            with [col1, col2, col3][i]:
                st.markdown(f'<div class="metric-card" style="border-left-color: {color};">', unsafe_allow_html=True)
                st.markdown(f'<div style="display: flex; align-items: center; justify-content: space-between;">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{value}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size: 24px; color: {color};">{icon}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-label">{label}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Graphique d'occupation
        st.markdown('<div class="section-header">📊 Occupation des Salles</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        
        fig = px.bar(df_occupation, x='salle', y='taux_occupation',
                    color='type',
                    title="",
                    labels={'taux_occupation': "Taux d'occupation (%)", 'salle': 'Salle'},
                    text='taux_occupation')
        
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tableau détaillé
        st.markdown('<div class="section-header">📋 Détail des Salles Utilisées</div>', unsafe_allow_html=True)
        
        df_display = df_occupation[['type', 'salle', 'capacite', 'nb_examens', 'jours_utilises', 'taux_occupation']].copy()
        df_display['taux_occupation'] = df_display['taux_occupation'].apply(lambda x: f"{float(x):.1f}%")
        df_display['capacite'] = df_display['capacite'].apply(lambda x: f"{int(x)} places")
        
        st.dataframe(
            df_display.sort_values('taux_occupation', ascending=False, key=lambda col: col.str.replace('%', '').astype(float)),
            column_config={
                "type": "Type",
                "salle": "Salle",
                "capacite": "Capacité",
                "nb_examens": "Nb Examens",
                "jours_utilises": "Jours Utilisés",
                "taux_occupation": "Taux Occupation"
            },
            use_container_width=True
        )

def render_conflits_formation():
    """Page: Analyse des Conflits par Formation"""
    # En-tête principal
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("⚠️ Analyse des Conflits par Formation")
    st.markdown(f"**Détection et analyse des conflits de planning pour le département {departement_nom}**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Récupérer les conflits
    conflits = get_conflits_par_formation(DEPARTEMENT_ID, date_debut, date_fin)
    
    if conflits:
        df_conflits = pd.DataFrame(conflits)
        
        # Convertir les colonnes en float
        for col in ['total_conflits', 'conflits_etudiants', 'conflits_salles', 
                   'conflits_professeurs', 'total_examens', 'taux_conflits']:
            if col in df_conflits.columns:
                df_conflits[col] = pd.to_numeric(df_conflits[col], errors='coerce').fillna(0)
            
        # KPIs globaux avec design amélioré
        st.markdown('<div class="section-header">📊 Indicateurs de Conflits</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        kpis_conflits = [
            ("Total Conflits", int(float(df_conflits['total_conflits'].sum())), "⚠️", "#F44336"),
            ("Taux Conflits Moyen", f"{float(df_conflits['taux_conflits'].mean()):.1f}%", "📈", "#FF9800"),
            ("Formation Critique", df_conflits.loc[df_conflits['taux_conflits'].idxmax()]['formation'] if not df_conflits.empty else "N/A", "🔥", "#3949ab"),
            ("Taux Conflits Global", f"{(float(df_conflits['total_conflits'].sum()) / float(df_conflits['total_examens'].sum()) * 100) if float(df_conflits['total_examens'].sum()) > 0 else 0:.1f}%", "🌐", "#2196F3")
        ]
        
        for i, (label, value, icon, color) in enumerate(kpis_conflits):
            with [col1, col2, col3, col4][i]:
                st.markdown(f'<div style="display: flex; align-items: center; justify-content: space-between;">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{value}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size: 24px; color: {color};">{icon}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-label">{label}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Graphique des conflits par formation
        st.markdown('<div class="section-header">📊 Répartition des Conflits par Formation</div>', unsafe_allow_html=True)
        
        fig = px.bar(df_conflits, x='formation', y='taux_conflits',
                    color='taux_conflits',
                    title="",
                    labels={'formation': 'Formation', 'taux_conflits': 'Taux de Conflits (%)'},
                    text='taux_conflits',
                    color_continuous_scale='RdYlGn_r')
        
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Graphique radar des types de conflits
        st.markdown('<div class="section-header">🎯 Types de Conflits par Formation</div>', unsafe_allow_html=True)
        
        # Préparer les données pour le radar
        types_conflits = ['Étudiants', 'Salles', 'Professeurs']
        
        fig = go.Figure()
        
        for idx, row in df_conflits.iterrows():
            valeurs = [
                float(row['conflits_etudiants']),
                float(row['conflits_salles']),
                float(row['conflits_professeurs'])
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=valeurs,
                theta=types_conflits,
                fill='toself',
                name=row['formation']
            ))
        
        # Calculer la valeur maximale pour l'échelle
        max_val = max(
            df_conflits[['conflits_etudiants', 'conflits_salles', 'conflits_professeurs']].max().max(),
            1
        )
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, float(max_val) * 1.2]
                )),
            showlegend=True,
            title="",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tableau détaillé
        st.markdown('<div class="section-header">📋 Détail des Conflits par Formation</div>', unsafe_allow_html=True)
        
        df_display = df_conflits.copy()
        df_display['taux_conflits'] = df_display['taux_conflits'].apply(lambda x: f"{float(x):.1f}%")
        
        st.dataframe(
            df_display[['formation', 'total_examens', 'conflits_etudiants', 
                       'conflits_salles', 'conflits_professeurs', 'total_conflits', 'taux_conflits']],
            column_config={
                "formation": "Formation",
                "total_examens": "Total Examens",
                "conflits_etudiants": "Conflits Étudiants",
                "conflits_salles": "Conflits Salles",
                "conflits_professeurs": "Conflits Professeurs",
                "total_conflits": "Total Conflits",
                "taux_conflits": "Taux Conflits"
            },
            use_container_width=True
        )
        
        # Analyse des conflits critiques
        st.markdown('<div class="section-header">🔍 Analyse des Conflits Critiques</div>', unsafe_allow_html=True)
        
        df_critiques = df_conflits[df_conflits['taux_conflits'] > 10].copy()
        
        if not df_critiques.empty:
            for _, formation in df_critiques.iterrows():
                with st.expander(f"⚠️ {formation['formation']} - Taux: {float(formation['taux_conflits']):.1f}%"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f'<div class="metric-value">{int(formation["conflits_etudiants"])}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-label">Conflits Étudiants</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f'<div class="metric-value">{int(formation["conflits_salles"])}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-label">Conflits Salles</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f'<div class="metric-value">{int(formation["conflits_professeurs"])}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-label">Conflits Professeurs</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Recommandations
                    st.info("**Recommandations:**")
                    
                    if formation['conflits_etudiants'] > 0:
                        st.write("• Réorganiser les horaires des examens pour éviter les chevauchements d'étudiants")
                    
                    if formation['conflits_salles'] > 0:
                        st.write("• Attribuer des salles différentes pour les examens qui se chevauchent")
                    
                    if formation['conflits_professeurs'] > 0:
                        st.write("• Redistribuer les surveillances entre les professeurs")
        
        else:
            st.success("✅ Aucune formation avec un taux de conflits critique (>10%)")
    
    else:
        st.info("ℹ️ Aucun conflit détecté pour la période sélectionnée.")

def render_gestion_professeurs():
    """Page: Gestion des Professeurs du Département"""
    # En-tête principal
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("👨‍🏫 Gestion des Professeurs du Département")
    st.markdown(f"**Gestion des ressources humaines pour le département {departement_nom}**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Récupérer les professeurs
    professeurs = get_professeurs_departement(DEPARTEMENT_ID)
    
    if professeurs:
        df_profs = pd.DataFrame(professeurs)
        
        # Convertir les colonnes en float
        for col in ['total_heures', 'heures_responsable', 'heures_surveillant']:
            if col in df_profs.columns:
                df_profs[col] = pd.to_numeric(df_profs[col], errors='coerce').fillna(0)
            
        # Statistiques globales avec design amélioré
        st.markdown('<div class="section-header">📊 Vue ensemble</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        stats_profs = [
            ("Nombre de professeurs", len(df_profs), "👨‍🏫", "#3949ab"),
            ("Professeurs actifs", df_profs[df_profs['total_heures'] > 0].shape[0], "✅", "#4CAF50"),
            ("Charge totale", f"{float(df_profs['total_heures'].sum()):.1f}h", "⚖️", "#FF9800")
        ]
        
        for i, (label, value, icon, color) in enumerate(stats_profs):
            with [col1, col2, col3][i]:
                st.markdown(f'<div style="display: flex; align-items: center; justify-content: space-between;">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{value}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size: 24px; color: {color};">{icon}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-label">{label}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Recherche et filtres
        st.markdown('<div class="section-header">🔍 Recherche et Filtres</div>', unsafe_allow_html=True)
        st.markdown('<div class="filter-card">', unsafe_allow_html=True)
        
        col_search1, col_search2 = st.columns(2)
        
        with col_search1:
            recherche_nom = st.text_input("Rechercher par nom")
        
        with col_search2:
            min_heures = st.slider("Charge minimale (heures)", 0, 100, 0)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Appliquer les filtres
        df_filtre = df_profs.copy()
        
        if recherche_nom:
            df_filtre = df_filtre[df_filtre['nom_complet'].str.contains(recherche_nom, case=False, na=False)]
        
        df_filtre = df_filtre[df_filtre['total_heures'] >= min_heures]
        
        # Tableau des professeurs
        st.markdown('<div class="section-header">📋 Liste des Professeurs</div>', unsafe_allow_html=True)
        
        df_display = df_filtre[['nom_complet', 'specialite', 'nb_examens_responsable', 
                               'nb_examens_surveillant', 'heures_responsable', 
                               'heures_surveillant', 'total_heures']].copy()
        
        # Formater l'affichage
        df_display['total_heures'] = df_display['total_heures'].apply(lambda x: f"{float(x):.1f}h")
        df_display['heures_responsable'] = df_display['heures_responsable'].apply(lambda x: f"{float(x):.1f}h" if pd.notnull(x) else "0.0h")
        df_display['heures_surveillant'] = df_display['heures_surveillant'].apply(lambda x: f"{float(x):.1f}h" if pd.notnull(x) else "0.0h")
        
        # Fonction pour trier par heures
        def sort_by_hours(col):
            return col.str.replace('h', '').astype(float)
        
        st.dataframe(
            df_display.sort_values('total_heures', ascending=False, key=sort_by_hours),
            column_config={
                "nom_complet": "Professeur",
                "specialite": "Spécialité",
                "nb_examens_responsable": "Examens Responsable",
                "nb_examens_surveillant": "Examens Surveillant",
                "heures_responsable": "Heures Responsable",
                "heures_surveillant": "Heures Surveillant",
                "total_heures": "Total Heures"
            },
            use_container_width=True
        )
        
        # Graphique de répartition
        st.markdown('<div class="section-header">📊 Répartition de la Charge</div>', unsafe_allow_html=True)
        
        fig = px.scatter(df_profs, x='nb_examens_responsable', y='nb_examens_surveillant',
                        size='total_heures', color='specialite',
                        hover_data=['nom_complet'],
                        title="",
                        labels={'nb_examens_responsable': 'Examens Responsable',
                               'nb_examens_surveillant': 'Examens Surveillant'})
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Export des données
        st.markdown('<div class="section-header">📤 Export des Données</div>', unsafe_allow_html=True)
        
        csv_data = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger CSV",
            data=csv_data,
            file_name=f"professeurs_departement_{departement_nom}_{date_debut}_{date_fin}.csv",
            mime="text/csv"
        )

def render_planning_departement():
    """Page: Planning Complet du Département"""
    # En-tête principal
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("📅 Planning Complet du Département")
    st.markdown(f"**Consultation du planning global pour le département {departement_nom}**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sélection de l'affichage
    st.markdown('<div class="section-header">🎯 Mode daffichage</div>', unsafe_allow_html=True)
    
    display_mode = st.radio(
        "",
        ["📋 Vue Tableau", "📊 Vue Calendrier", "🎯 Vue Graphique"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Récupérer les examens
    examens = get_examens_departement(DEPARTEMENT_ID, date_debut, date_fin)
    
    if examens:
        df_examens = pd.DataFrame(examens)
        
        if display_mode == "📋 Vue Tableau":
            render_planning_tableau(df_examens)
        
        elif display_mode == "📊 Vue Calendrier":
            render_planning_calendrier(df_examens)
        
        elif display_mode == "🎯 Vue Graphique":
            render_planning_graphique(df_examens)
        
        # Export du planning
        render_planning_export(df_examens)
    
    else:
        st.info("ℹ️ Aucun examen trouvé pour la période sélectionnée.")

def render_planning_tableau(df_examens):
    """Sous-page: Planning Détaillé en Tableau"""
    st.markdown('<div class="section-header">📋 Planning Détaillé</div>', unsafe_allow_html=True)
    
    # Filtres
    st.markdown('<div class="filter-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        formation_filter = st.selectbox(
            "Formation",
            options=['Toutes'] + list(df_examens['formation'].unique())
        )
    
    with col2:
        statut_filter = st.selectbox(
            "Statut",
            options=['Tous'] + list(df_examens['statut'].unique())
        )
    
    with col3:
        salle_filter = st.selectbox(
            "Salle",
            options=['Toutes'] + list(df_examens['salle'].unique())
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Appliquer les filtres
    df_filtered = df_examens.copy()
    
    if formation_filter != 'Toutes':
        df_filtered = df_filtered[df_filtered['formation'] == formation_filter]
    
    if statut_filter != 'Tous':
        df_filtered = df_filtered[df_filtered['statut'] == statut_filter]
    
    if salle_filter != 'Toutes':
        df_filtered = df_filtered[df_filtered['salle'] == salle_filter]
    
    # Afficher le tableau
    st.dataframe(
        df_filtered[['date_examen', 'heure_debut', 'heure_fin', 'module', 'formation', 
                   'professeur', 'salle', 'nb_etudiants', 'taux_occupation', 'statut']],
        column_config={
            "date_examen": "Date",
            "heure_debut": "Heure début",
            "heure_fin": "Heure fin",
            "module": "Module",
            "formation": "Formation",
            "professeur": "Professeur",
            "salle": "Salle",
            "nb_etudiants": "Étudiants",
            "taux_occupation": "Occupation",
            "statut": "Statut"
        },
        use_container_width=True
    )

def render_planning_calendrier(df_examens):
    """Sous-page: Planning en Vue Calendrier"""
    st.markdown('<div class="section-header">📊 Planning Calendrier</div>', unsafe_allow_html=True)
    
    # Grouper par date
    df_examens['date_examen'] = pd.to_datetime(df_examens['date_examen'])
    dates_uniques = sorted(df_examens['date_examen'].unique())
    
    for date in dates_uniques:
        df_date = df_examens[df_examens['date_examen'] == date]
        
        with st.expander(f"📅 {date.strftime('%A %d %B %Y')} ({len(df_date)} examens)"):
            for _, exam in df_date.iterrows():
                st.markdown('<div class="examen-card">', unsafe_allow_html=True)
                col_ex1, col_ex2 = st.columns([3, 1])
                with col_ex1:
                    st.markdown(f"""
                    <div style="font-weight: 600; font-size: 16px; color: #1a237e;">{exam['module']}</div>
                    <div style="color: #666; margin-bottom: 8px;">{exam['formation']}</div>
                    <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                        <span class="tag tag-warning">⏰ {exam['heure_debut']} - {exam['heure_fin']}</span>
                        <span class="tag tag-info">👨‍🏫 {exam['professeur']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_ex2:
                    if exam['statut'] == 'confirmé':
                        status_class = "status-confirmed"
                    elif exam['statut'] == 'annulé':
                        status_class = "status-cancelled"
                    else:
                        status_class = "status-pending"
                    
                    st.markdown(f"""
                    <div style="text-align: right;">
                        <span class="{status_class}" style="display: block; margin-bottom: 8px;">{exam['statut']}</span>
                        <div style="font-size: 12px; color: #666;">🏫 {exam['salle']}</div>
                        <div style="font-size: 12px; color: #666;">👥 {int(exam['nb_etudiants'])}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

def render_planning_graphique(df_examens):
    """Sous-page: Planning en Vue Graphique"""
    st.markdown('<div class="section-header">🎯 Vue Graphique du Planning</div>', unsafe_allow_html=True)
    
    # Préparer les données pour le graphique Gantt
    df_gantt = df_examens.copy()
    df_gantt['date_examen'] = pd.to_datetime(df_gantt['date_examen'])
    df_gantt['datetime_debut'] = pd.to_datetime(
        df_gantt['date_examen'].astype(str) + ' ' + df_gantt['heure_debut'].astype(str)
    )
    df_gantt['datetime_fin'] = pd.to_datetime(
        df_gantt['date_examen'].astype(str) + ' ' + df_gantt['heure_fin'].astype(str)
    )
    
    # Graphique Gantt
    st.markdown('<div style="font-weight: 600; color: #1a237e; margin-bottom: 1rem;">📅 Diagramme de Gantt</div>', unsafe_allow_html=True)
    
    fig = px.timeline(
        df_gantt,
        x_start="datetime_debut",
        x_end="datetime_fin",
        y="formation",
        color="module",
        hover_data=["professeur", "salle", "nb_etudiants", "statut"],
        title=""
    )
    
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Heatmap d'occupation des salles
    st.markdown('<div class="section-header">🔥 Heatmap dOccupation des Salles</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    
    # Créer une heatmap par jour et par salle
    pivot_data = df_examens.pivot_table(
        index='date_examen',
        columns='salle',
        values='id',
        aggfunc='count',
        fill_value=0
    ).reset_index()
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.drop(columns=['date_examen']).values.T,
        x=pivot_data['date_examen'],
        y=pivot_data.drop(columns=['date_examen']).columns,
        colorscale='Viridis',
        colorbar=dict(title="Nombre d'examens")
    ))
    
    fig.update_layout(
        title="",
        xaxis_title="Date",
        yaxis_title="Salle",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_planning_export(df_examens):
    """Sous-page: Export du Planning"""
    st.markdown('<div class="section-header">📤 Export du Planning</div>', unsafe_allow_html=True)
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        csv_data = df_examens.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger CSV",
            data=csv_data,
            file_name=f"planning_{departement_nom}_{date_debut}_{date_fin}.csv",
            mime="text/csv"
        )
    
    with col_exp2:
        # Générer un rapport HTML simple
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Planning {departement_nom}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #3498db; color: white; }}
                .valide {{ background-color: #d4edda; }}
                .attente {{ background-color: #fff3cd; }}
                .annule {{ background-color: #f8d7da; }}
            </style>
        </head>
        <body>
            <h1>📅 Planning d'Examens - {departement_nom}</h1>
            <p>Période: {date_debut} au {date_fin}</p>
            <p>Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            {df_examens.to_html(index=False, classes='table')}
        </body>
        </html>
        """
        
        st.download_button(
            label="📥 Télécharger HTML",
            data=html_content.encode('utf-8'),
            file_name=f"planning_{departement_nom}_{date_debut}_{date_fin}.html",
            mime="text/html"
        )

# ============================================================================
# CONFIGURATION INITIALE
# ============================================================================

# Charger les secrets et initialiser la connexion
secrets = load_secrets()
conn = init_connection()

# Récupérer le département dont l'utilisateur est responsable
departement_info = get_departement_chef(CHEF_ID)

if not departement_info:
    st.error("❌ Vous n'êtes pas responsable d'un département.")
    st.info("Veuillez contacter l'administrateur pour vous assigner un département.")
    if st.button("🏠 Retour à l'accueil"):
        st.switch_page("app.py")
    st.stop()

DEPARTEMENT_ID = departement_info['id']
departement_nom = departement_info['nom']

# ============================================================================
# SIDEBAR AMÉLIORÉE
# ============================================================================

with st.sidebar:
    # En-tête sidebar
    st.markdown('<div class="user-avatar">👨‍💼</div>', unsafe_allow_html=True)
    st.markdown(f'<h3 style="color: black; margin-bottom: 5px;">{st.session_state.nom_complet}</h3>', unsafe_allow_html=True)
    st.markdown(f'<p style="color: black; margin: 0; font-size: 14px;">Chef de Département</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown('<div style="font-weight: 600; color: #1a237e; margin-bottom: 1rem;">📋 Navigation</div>', unsafe_allow_html=True)
    
    menu_options = [
        ("🏠 Tableau de Bord", "📊 Vue d'ensemble du département"),
        ("✅ Validation EDT", "✅ Gestion des validations d'examens"),
        ("📊 Statistiques Département", "📈 Analyse des performances"),
        ("⚠️ Conflits par Formation", "⚠️ Détection et résolution de conflits"),
        ("👨‍🏫 Gestion Professeurs", "👨‍🏫 Gestion des ressources humaines"),
        ("📅 Planning Département", "📅 Consultation du planning global")
    ]
    
    menu = st.radio(
        "",
        [opt[0] for opt in menu_options],
        format_func=lambda x: f"{x}",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Période d'analyse
    st.markdown('<div style="font-weight: 600; color: #1a237e; margin-bottom: 1rem;">📅 Période d\'analyse</div>', unsafe_allow_html=True)
    date_debut = st.date_input("Date début", datetime.now())
    date_fin = st.date_input("Date fin", datetime.now() + timedelta(days=30))
    
    # Afficher la durée
    delta = (date_fin - date_debut).days
    st.caption(f"**Durée:** {delta} jours")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Actions rapides
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Actualiser", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("📥 Exporter", use_container_width=True):
            st.info("Export en développement...")
    
    st.markdown("---")
    
    # Déconnexion
    if st.button("🚪 Déconnexion", use_container_width=True, type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("pages/log.py")

# ============================================================================
# EN-TÊTE PRINCIPAL
# ============================================================================

# Titre principal avec design amélioré
col_title, col_dept = st.columns([3, 1])
with col_title:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 1rem;">
        <div style="font-size: 32px;">👨‍💼</div>
        <div>
            <h1 style="margin: 0; color: #1a237e;">Tableau de Bord Chef de Département</h1>
            <p style="margin: 0; color: #666; font-size: 14px;">Gestion stratégique du département {departement_nom}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_dept:
    st.markdown(f"""
    <div class="metric-card" style="text-align: center;">
        <div class="metric-value" style="color: #3949ab;">{departement_nom}</div>
        <div class="metric-label">Département</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# ROUTAGE DES PAGES
# ============================================================================

if menu == "🏠 Tableau de Bord":
    render_tableau_de_bord()
    
elif menu == "✅ Validation EDT":
    render_validation_edt()
    
elif menu == "📊 Statistiques Département":
    render_statistiques_departement()
    
elif menu == "⚠️ Conflits par Formation":
    render_conflits_formation()
    
elif menu == "👨‍🏫 Gestion Professeurs":
    render_gestion_professeurs()
    
elif menu == "📅 Planning Département":
    render_planning_departement()

# ============================================================================
# PIED DE PAGE AMÉLIORÉ
# ============================================================================

st.markdown("---")
st.markdown(f"""
<div class="footer">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div style="font-weight: 600; color: #1a237e; margin-bottom: 5px;">Tableau de Bord Chef de Département • {departement_nom}</div>
            <div style="color: #666; font-size: 11px;">Version 2.0 • Système de Gestion des Examens</div>
        </div>
        <div style="text-align: right;">
            <div style="color: #666; font-size: 11px;">Connecté en tant que: {st.session_state.nom_complet}</div>
            <div style="color: #666; font-size: 11px;">Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
        </div>
    </div>
    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e0e0e0; color: #999; font-size: 10px;">
        © 2024 - Tous droits réservés • Application développée pour la gestion académique
    </div>
</div>
""", unsafe_allow_html=True)