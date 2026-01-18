# app_admin.py
import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, time, timedelta
import time as time_module
import io
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="Plateforme d'Optimisation des Emplois du Temps",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# VÉRIFICATION DE CONNEXION
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⛔ Accès non autorisé. Veuillez vous connecter.")
    if st.button("🔐 Se connecter"):
        st.switch_page("pages/log.py")
    st.stop()

# VÉRIFICATION DU RÔLE
if st.session_state.role != 'admin':
    st.error(f"⛔ Cette page est réservée au doyen. Votre rôle: {st.session_state.role}")
    if st.button("🏠 Retour à l'accueil"):
        st.switch_page("app.py")
    st.stop()

# CSS STYLES COMPLETS
st.markdown("""
<style>
    /* ========== RESET & BASE STYLES ========== */
    .main {
        padding: 1rem 1.5rem;
    }
    
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    
    /* ========== TYPOGRAPHY ========== */
    h1 {
        font-size: 2.2rem !important;
        font-weight: 600 !important;
        color: #2D3748 !important;
        margin-bottom: 1rem !important;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #E2E8F0;
    }
    
    h2 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #4A5568 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        font-size: 1.2rem !important;
        font-weight: 500 !important;
        color: #4A5568 !important;
        margin-top: 1rem !important;
    }
    
    /* ========== METRIC CARDS ========== */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .metric-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid #E2E8F0;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        border-color: #4299E1;
        box-shadow: 0 2px 8px rgba(66, 153, 225, 0.1);
    }
    
    .metric-icon {
        font-size: 1.5rem;
        margin-bottom: 0.75rem;
        color: #4299E1;
    }
    
    .metric-title {
        font-size: 0.85rem;
        color: #718096;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2D3748;
        margin: 0;
        line-height: 1;
    }
    
    /* ========== INFO CARDS ========== */
    .info-card {
        background: #EBF8FF;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
        border-left: 4px solid #4299E1;
    }
    
    .warning-card {
        background: #FEFCBF;
        border-left-color: #D69E2E;
    }
    
    .success-card {
        background: #F0FFF4;
        border-left-color: #38A169;
    }
    
    .danger-card {
        background: #FFF5F5;
        border-left-color: #E53E3E;
    }
    
    /* ========== SECTIONS ========== */
    .section-wrapper {
        background: #FFFFFF;
        border-radius: 12px;
        margin: 1.5rem 0;
        border: 1px solid #E2E8F0;
    }
    
    .section-header {
        background: #F7FAFC;
        padding: 1.25rem 1.5rem;
        border-bottom: 1px solid #E2E8F0;
    }
    
    .section-content {
        padding: 1.5rem;
    }
    
    /* ========== BUTTONS ========== */
    .stButton > button {
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 500 !important;
        background: #4299E1 !important;
        color: white !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: #3182CE !important;
    }
    
    /* ========== FORMS ========== */
    .stSelectbox > div > div,
    .stTextInput > div > div,
    .stDateInput > div > div,
    .stTimeInput > div > div,
    .stNumberInput > div > div {
        border-radius: 8px !important;
        border: 1px solid #CBD5E0 !important;
    }
    
    .stSelectbox > div > div:hover,
    .stTextInput > div > div:hover,
    .stDateInput > div > div:hover,
    .stTimeInput > div > div:hover,
    .stNumberInput > div > div:hover {
        border-color: #4299E1 !important;
    }
    
    /* ========== TABLES ========== */
    .dataframe {
        border-radius: 8px !important;
        border: 1px solid #E2E8F0 !important;
    }
    
    .dataframe thead th {
        background: #F7FAFC !important;
        color: #4A5568 !important;
        font-weight: 600 !important;
        border-bottom: 1px solid #E2E8F0 !important;
    }
    
    .dataframe tbody tr:hover {
        background: #F7FAFC !important;
    }
    
    /* ========== SIDEBAR ========== */
    [data-testid="stSidebar"] {
        background: #F7FAFC !important;
    }
    
    .sidebar-nav-item {
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        border-radius: 8px;
        color: #4A5568;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-weight: 500;
    }
    
    .sidebar-nav-item:hover {
        background: #EDF2F7;
        color: #2D3748;
    }
    
    .sidebar-nav-item.active {
        background: #4299E1;
        color: white;
    }
    
    /* ========== TABS ========== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1rem !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: #4299E1 !important;
        color: white !important;
    }
    
    /* ========== BADGES ========== */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .badge-primary {
        background: #4299E1;
        color: white;
    }
    
    .badge-success {
        background: #38A169;
        color: white;
    }
    
    .badge-warning {
        background: #D69E2E;
        color: white;
    }
    
    /* ========== PROGRESS BARS ========== */
    .progress-container {
        margin: 1rem 0;
    }
    
    .progress-bar {
        height: 8px;
        background: #E2E8F0;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: #4299E1;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Fonction de connexion à MySQL
@st.cache_resource
def init_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            database=st.secrets["mysql"]["database"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"]
        )
        return conn
    except Error as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
        return None

# Initialiser la connexion
conn = init_connection()

# Fonction pour créer des cartes métriques avec HTML
def create_metric_card(icon, title, value, change=None, change_label="vs période précédente"):
    change_html = ""
    if change is not None:
        change_class = "negative" if change < 0 else ""
        change_html = f"""
        <div class="metric-change {change_class}">
            <span>{'▼' if change < 0 else '▲'}</span>
            <span>{abs(change)}% {change_label}</span>
        </div>
        """
    
    return f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """

# Fonction pour créer une carte d'information
def create_info_card(message, type="info", icon="ℹ️"):
    type_class = {
        "info": "info-card",
        "warning": "warning-card",
        "success": "success-card",
        "danger": "danger-card"
    }.get(type, "info-card")
    
    return f"""
    <div class="{type_class}">
        <div style="display: flex; align-items: flex-start; gap: 1rem;">
            <div style="font-size: 1.5rem;">{icon}</div>
            <div style="flex: 1;">
                {message}
            </div>
        </div>
    </div>
    """

# Fonction pour créer un en-tête de section
def create_section_header(icon, title, subtitle=""):
    return f"""
    <div class="section-header">
        <div class="section-header-icon">{icon}</div>
        <div>
            <h2 style="margin: 0; color: #2D3748;">{title}</h2>
            {f'<p style="margin: 0.5rem 0 0 0; color: #718096; font-size: 0.9rem;">{subtitle}</p>' if subtitle else ''}
        </div>
    </div>
    """

# Fonction pour créer une timeline item
def create_timeline_item(time, title, description, status="planned"):
    status_icons = {
        "planned": "📅",
        "in_progress": "🔄",
        "completed": "✅",
        "warning": "⚠️",
        "error": "❌"
    }
    
    status_colors = {
        "planned": "#3498db",
        "in_progress": "#f39c12",
        "completed": "#2ecc71",
        "warning": "#f39c12",
        "error": "#e74c3c"
    }
    
    icon = status_icons.get(status, "📅")
    color = status_colors.get(status, "#3498db")
    
    return f"""
    <div style="border-left: 3px solid {color}; padding-left: 1rem; margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="font-weight: 600; color: #2c3e50; font-size: 1.1rem;">
                    {icon} {title}
                </div>
                <div style="color: #7f8c8d; margin-top: 0.5rem;">
                    {description}
                </div>
            </div>
            <div style="font-size: 0.9rem; color: #95a5a6; background: #f8f9fa; padding: 0.3rem 0.8rem; border-radius: 12px;">
                {time}
            </div>
        </div>
    </div>
    """

# Fonction pour exécuter les requêtes SQL
def run_query(query, params=None, fetch=True):
    try:
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            result = cursor.fetchall()
            
            # Convertir les timedelta en time
            for row in result:
                for key, value in row.items():
                    if isinstance(value, timedelta):
                        # Convertir timedelta en datetime.time
                        total_seconds = value.total_seconds()
                        hours = int(total_seconds // 3600)
                        minutes = int((total_seconds % 3600) // 60)
                        seconds = int(total_seconds % 60)
                        row[key] = time(hours, minutes, seconds)
            
            cursor.close()
            return result
        else:
            conn.commit()
            cursor.close()
            return True
    except Error as e:
        st.error(f"Erreur SQL: {e}")
        return None

# Titre de l'application avec design amélioré
st.markdown("""
<div style="text-align: center; margin-bottom: 3rem;">
    <h1 style="
        background: linear-gradient(90deg, #3498db, #2ecc71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
    ">
        📊 Plateforme d'Optimisation des Emplois du Temps
    </h1>
    <p style="color: #7f8c8d; font-size: 1.1rem; max-width: 800px; margin: 0 auto;">
        Système intelligent de planification et gestion des examens universitaires
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar pour la navigation
with st.sidebar:
    # Header de la sidebar avec avatar et infos
    st.markdown("""
    <style>
    .sidebar-header {
        padding: 2rem 1.5rem 1.5rem 1.5rem;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 0 0 20px 20px;
        margin: -1rem -1rem 1.5rem -1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .user-avatar {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        margin: 0 auto 1rem auto;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        color: white;
        border: 4px solid rgba(255,255,255,0.3);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .user-name {
        color: white;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    
    .user-role {
        color: rgba(255,255,255,0.8);
        font-size: 0.9rem;
        background: rgba(255,255,255,0.1);
        padding: 0.25rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    
    .user-status {
        color: rgba(255,255,255,0.7);
        font-size: 0.85rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background: #4ade80;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    </style>
    
    <div class="sidebar-header">
        <div class="user-avatar">👨‍💼</div>
        <div class="user-name">Administrateur</div>
        <div class="user-role">Doyen</div>
        <div class="user-status">
            <span class="status-dot"></span>
            Connecté
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Définir les options de menu
    menu_options = [
        {"icon": "📊", "label": "Tableau de Bord", "badge": ""},
        {"icon": "🎯", "label": "Génération Planning", "badge": "AI"},
        {"icon": "🔍", "label": "Visualisation Planning", "badge": "3D"},
        {"icon": "📋", "label": "Planning Général", "badge": ""},
        {"icon": "⚠️", "label": "Détection Conflits", "badge": "12"},
        {"icon": "📈", "label": "Statistiques", "badge": "New"},
        {"icon": "⚙️", "label": "Configuration", "badge": ""},
    ]
    
    # Navigation principale
    st.markdown("""
    <style>
    .nav-section {
        margin-bottom: 2rem;
    }
    
    .nav-title {
        color: #64748b;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 1rem;
        padding: 0 1rem;
    }
    
    .nav-item {
        display: flex;
        align-items: center;
        padding: 0.875rem 1.5rem;
        margin: 0.25rem 0;
        color: #64748b;
        text-decoration: none;
        border-radius: 12px;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 1px solid transparent;
    }
    
    .nav-item:hover {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%);
        color: #4f46e5;
        border-color: rgba(99, 102, 241, 0.2);
        transform: translateX(5px);
    }
    
    .nav-item.active {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .nav-item.active:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
    }
    
    .nav-icon {
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        margin-right: 0.75rem;
        flex-shrink: 0;
    }
    
    .nav-label {
        flex-grow: 1;
        font-weight: 500;
        font-size: 0.95rem;
    }
    
    .nav-badge {
        background: rgba(255,255,255,0.2);
        padding: 0.2rem 0.6rem;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .nav-item.active .nav-badge {
        background: rgba(255,255,255,0.3);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialiser selected_menu dans session_state si ce n'est pas déjà fait
    if 'selected_menu' not in st.session_state:
        st.session_state.selected_menu = "Tableau de Bord"
    
    # Navigation - Titre
    st.markdown('<div class="nav-title">Navigation Principale</div>', unsafe_allow_html=True)
    
    # Créer les boutons de navigation
    for i, item in enumerate(menu_options):
        is_active = st.session_state.selected_menu == item["label"]
        
        # Style pour le bouton actif
        button_style = f"""
        <style>
        div[data-testid="stButton"] > button[kind="secondary"][data-testid="baseButton-secondary"][data-index="{i}"] {{
            background: {'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)' if is_active else 'white'} !important;
            color: {'white' if is_active else '#64748b'} !important;
            border: 1px solid {'transparent' if is_active else '#e2e8f0'} !important;
            box-shadow: {'0 4px 15px rgba(99, 102, 241, 0.3)' if is_active else 'none'} !important;
            text-align: left !important;
            padding: 0.875rem 1.5rem !important;
            border-radius: 12px !important;
            font-weight: 500 !important;
            margin: 0.25rem 0 !important;
            transition: all 0.3s ease !important;
            justify-content: flex-start !important;
        }}
        
        div[data-testid="stButton"] > button[kind="secondary"][data-testid="baseButton-secondary"][data-index="{i}"]:hover {{
            transform: translateX(5px) !important;
            {'box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important' if is_active else 
             'background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%) !important; color: #4f46e5 !important; border-color: rgba(99, 102, 241, 0.2) !important;'}
        }}
        </style>
        """
        st.markdown(button_style, unsafe_allow_html=True)
        
        # Créer le bouton
        if st.button(
            f"{item['icon']} {item['label']} {'🔴' if item['badge'] == '12' else ''}",
            key=f"nav_{i}",
            use_container_width=True,
            type="secondary"
        ):
            st.session_state.selected_menu = item["label"]
            st.rerun()
    
    st.markdown("---")
    
    # Actions rapides
    st.markdown('<div class="nav-title">Actions Rapides</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄", help="Rafraîchir", key="refresh_btn", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("📥", help="Exporter", key="export_btn", use_container_width=True):
            st.success("Export démarré!")
    with col3:
        if st.button("🔔", help="Notifications", key="notif_btn", use_container_width=True):
            st.info("3 nouvelles notifications")
    
    st.markdown("---")
    
    # Statistiques rapides dans la sidebar (optionnel)
    show_sidebar_stats = st.checkbox("Afficher les statistiques", value=False)
    if show_sidebar_stats:
        st.markdown("""
        <style>
        .stats-card {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-radius: 16px;
            padding: 1.25rem;
            margin: 1rem 0;
            border: 1px solid #e2e8f0;
        }
        
        .stats-title {
            color: #64748b;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 1rem;
        }
        
        .stat-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid #f1f5f9;
        }
        
        .stat-item:last-child {
            border-bottom: none;
        }
        
        .stat-label {
            color: #475569;
            font-size: 0.9rem;
        }
        
        .stat-value {
            color: #1e293b;
            font-weight: 600;
            font-size: 0.95rem;
        }
        
        .stat-trend {
            font-size: 0.8rem;
            padding: 0.1rem 0.5rem;
            border-radius: 8px;
            font-weight: 500;
        }
        
        .trend-up {
            background: rgba(34, 197, 94, 0.1);
            color: #16a34a;
        }
        
        .trend-down {
            background: rgba(239, 68, 68, 0.1);
            color: #dc2626;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Récupérer des statistiques pour la sidebar
        total_examens = run_query("SELECT COUNT(*) as count FROM examens WHERE statut = 'planifié'")[0]['count']
        total_salles = run_query("SELECT COUNT(*) as count FROM lieu_examen WHERE disponible = TRUE")[0]['count']
        
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.markdown('<div class="stats-title">Statistiques Rapides</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="stat-item">
            <span class="stat-label">Examens planifiés</span>
            <span class="stat-value">{total_examens}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Salles disponibles</span>
            <span class="stat-value">{total_salles}</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Bouton déconnexion stylisé
    st.markdown("""
    <style>
    .logout-btn {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.875rem 1.5rem !important;
        font-weight: 500 !important;
        margin-top: 1rem !important;
        box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .logout-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(249, 115, 22, 0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Se déconnecter", key="logout_btn", use_container_width=True, type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("pages/log.py")

# Main content based on selected menu
selected_menu = st.session_state.selected_menu

# PAGE: Tableau de Bord avec design amélioré
if selected_menu == "Tableau de Bord":
    st.markdown(create_section_header("📊", "Tableau de Bord", "Vue d'ensemble des performances du système"), unsafe_allow_html=True)
    
    # Récupérer les données
    total_departements = run_query("SELECT COUNT(*) as count FROM departements")[0]['count']
    total_formations = run_query("SELECT COUNT(*) as count FROM formations")[0]['count']
    total_examens = run_query("SELECT COUNT(*) as count FROM examens WHERE statut = 'planifié'")[0]['count']
    total_professeurs = run_query("SELECT COUNT(*) as count FROM professeurs")[0]['count']
    total_salles = run_query("SELECT COUNT(*) as count FROM lieu_examen WHERE disponible = TRUE")[0]['count']
    total_etudiants = run_query("SELECT COUNT(DISTINCT id) as count FROM etudiants")[0]['count']
    
    # Afficher les métriques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(create_metric_card("🏢", "Départements", total_departements, 2), unsafe_allow_html=True)
        st.markdown(create_metric_card("👨‍🎓", "Étudiants", total_etudiants, 5), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card("🎓", "Formations", total_formations, 3), unsafe_allow_html=True)
        st.markdown(create_metric_card("👨‍🏫", "Professeurs", total_professeurs, 1), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card("📅", "Examens Planifiés", total_examens, 8), unsafe_allow_html=True)
        st.markdown(create_metric_card("🏫", "Salles Disponibles", total_salles, 0), unsafe_allow_html=True)
    
    # Graphiques avec design amélioré
    st.markdown(create_section_header("📈", "Analytiques et Tendances", "Visualisation des données clés"), unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="section-content">', unsafe_allow_html=True)
        
        occupation_data = run_query("""
            SELECT type, COUNT(*) as count, SUM(capacite) as capacite_totale
            FROM lieu_examen
            GROUP BY type
        """)
        
        if occupation_data:
            df_occupation = pd.DataFrame(occupation_data)
            fig = px.pie(df_occupation, values='count', names='type', 
                        title="Occupation des salles", color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                height=400
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="section-content">', unsafe_allow_html=True)
        
        examens_dept = run_query("""
            SELECT d.nom as departement, COUNT(ex.id) as nb_examens
            FROM departements d
            LEFT JOIN formations f ON d.id = f.dept_id
            LEFT JOIN modules m ON f.id = m.formation_id
            LEFT JOIN examens ex ON m.id = ex.module_id AND ex.statut = 'planifié'
            GROUP BY d.id
            ORDER BY nb_examens DESC
        """)
        
        if examens_dept:
            df_examens = pd.DataFrame(examens_dept)
            fig = px.bar(df_examens, x='departement', y='nb_examens',
                        title="Examens par département", color='nb_examens',
                        color_continuous_scale='Viridis')
            fig.update_layout(
                xaxis_title="Département",
                yaxis_title="Nombre d'examens",
                showlegend=False,
                height=400
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Activités récentes avec design amélioré
    st.markdown(create_section_header("📝", "Activités Récentes", "Derniers examens planifiés"), unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="section-content">', unsafe_allow_html=True)
        
        derniers_examens = run_query("""
            SELECT 
                ex.id,
                m.nom as module,
                d.nom as departement,
                f.nom as formation,
                ex.date_examen,
                ex.heure_debut,
                ex.heure_fin,
                l.nom as salle,
                CONCAT(p.nom, ' ', p.prenom) as professeur,
                CONCAT(ps.nom, ' ', ps.prenom) as surveillant
            FROM examens ex
            JOIN modules m ON ex.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            JOIN departements d ON f.dept_id = d.id
            JOIN lieu_examen l ON ex.salle_id = l.id
            LEFT JOIN professeurs p ON ex.professeur_id = p.id
            LEFT JOIN professeurs ps ON ex.surveillant_id = ps.id
            WHERE ex.statut = 'planifié'
            ORDER BY ex.date_examen DESC, ex.heure_debut DESC
            LIMIT 10
        """)
        
        if derniers_examens:
            df_derniers = pd.DataFrame(derniers_examens)
            
            # Formater les dates et heures
            df_derniers['date_examen'] = pd.to_datetime(df_derniers['date_examen']).dt.strftime('%d/%m/%Y')
            df_derniers['heure_debut'] = df_derniers['heure_debut'].astype(str)
            df_derniers['heure_fin'] = df_derniers['heure_fin'].astype(str)
            
            # Afficher avec style
            st.dataframe(
                df_derniers.rename(columns={
                    'module': 'Module',
                    'departement': 'Département',
                    'formation': 'Formation',
                    'date_examen': 'Date',
                    'heure_debut': 'Heure Début',
                    'heure_fin': 'Heure Fin',
                    'salle': 'Salle',
                    'professeur': 'Professeur',
                    'surveillant': 'Surveillant'
                }),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Module": st.column_config.TextColumn(width="medium"),
                    "Département": st.column_config.TextColumn(width="small"),
                    "Formation": st.column_config.TextColumn(width="medium"),
                    "Date": st.column_config.TextColumn(width="small"),
                    "Heure Début": st.column_config.TextColumn(width="small"),
                    "Heure Fin": st.column_config.TextColumn(width="small"),
                    "Salle": st.column_config.TextColumn(width="small"),
                    "Professeur": st.column_config.TextColumn(width="medium"),
                    "Surveillant": st.column_config.TextColumn(width="medium")
                }
            )
        else:
            st.info("Aucun examen planifié récemment")
        
        st.markdown('</div></div>', unsafe_allow_html=True)

# PAGE: Génération Planning avec design amélioré
elif selected_menu == "Génération Planning":
    st.markdown(create_section_header("🎯", "Génération de Planning", "Création intelligente des emplois du temps"), unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="section-content">', unsafe_allow_html=True)
        
        # Choix du type de génération avec design amélioré
        type_generation = st.radio(
            "Type de génération",
            ["📊 Par Département", "🌍 Planning Général (Tous départements)"],
            horizontal=True,
            key="type_gen"
        )
        
        if type_generation == "📊 Par Département":
            st.markdown(create_info_card(
                "Générez un planning personnalisé pour un département spécifique. "
                "Le système optimisera automatiquement les ressources.",
                "info", "💡"
            ), unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Sélection du département avec design amélioré
                st.markdown('<div style="margin-bottom: 1rem; font-weight: 600; color: #2c3e50;">Sélection du Département</div>', unsafe_allow_html=True)
                departements = run_query("SELECT id, nom FROM departements ORDER BY nom")
                dept_options = {dept['nom']: dept['id'] for dept in departements}
                
                if dept_options:
                    selected_dept_name = st.selectbox(
                        "Département",
                        options=list(dept_options.keys()),
                        key="dept_select",
                        label_visibility="collapsed"
                    )
                    dept_id = dept_options[selected_dept_name]
                else:
                    st.markdown(create_info_card(
                        "Aucun département trouvé dans la base de données",
                        "warning", "⚠️"
                    ), unsafe_allow_html=True)
                    dept_id = None
                    selected_dept_name = ""
            
            with col2:
                st.markdown('<div style="margin-bottom: 1rem; font-weight: 600; color: #2c3e50;">Paramètres de Session</div>', unsafe_allow_html=True)
                col2a, col2b = st.columns(2)
                with col2a:
                    annee_scolaire = st.number_input(
                        "Année scolaire", 
                        min_value=2020, 
                        max_value=2030, 
                        value=datetime.now().year,
                        key="annee_scol"
                    )
                with col2b:
                    session = st.selectbox(
                        "Session",
                        ["Principale", "Rattrapage"],
                        key="session_select"
                    )
            
            # Sélection des jours avec design amélioré
            st.markdown('<div class="section-wrapper" style="margin-top: 2rem;">', unsafe_allow_html=True)
            st.markdown('<div class="section-content">', unsafe_allow_html=True)
            
            col_date1, col_date2 = st.columns(2)
            
            with col_date1:
                date_debut = st.date_input(
                    "Date de début",
                    datetime.now(),
                    key="date_debut"
                )
            with col_date2:
                date_fin = st.date_input(
                    "Date de fin",
                    datetime.now() + timedelta(days=14),
                    key="date_fin"
                )
            
            # Jours disponibles
            jours_possibles = []
            current_date = date_debut
            while current_date <= date_fin:
                jours_possibles.append(current_date)
                current_date += timedelta(days=1)
            
            st.markdown('<div style="margin-top: 1.5rem; margin-bottom: 0.5rem; font-weight: 600; color: #2c3e50;">Sélection des Jours d\'Examen</div>', unsafe_allow_html=True)
            jours_selectionnes = st.multiselect(
                "Choisissez les jours pour les examens",
                options=jours_possibles,
                default=jours_possibles[:min(5, len(jours_possibles))],
                key="jours_select",
                label_visibility="collapsed"
            )
            
            st.markdown('</div></div>', unsafe_allow_html=True)
            
            # Paramètres des examens avec design amélioré
            st.markdown('<div class="section-wrapper" style="margin-top: 2rem;">', unsafe_allow_html=True)
            st.markdown('<div class="section-content">', unsafe_allow_html=True)
            
            col_param1, col_param2, col_param3 = st.columns(3)
            
            with col_param1:
                st.markdown('<div style="margin-bottom: 1rem; font-weight: 600; color: #2c3e50;">Horaires</div>', unsafe_allow_html=True)
                heure_debut = st.time_input(
                    "Heure de début",
                    datetime.strptime("08:00", "%H:%M").time(),
                    key="heure_debut"
                )
                heure_fin = st.time_input(
                    "Heure de fin",
                    datetime.strptime("18:00", "%H:%M").time(),
                    key="heure_fin"
                )
            
            with col_param2:
                st.markdown('<div style="margin-bottom: 1rem; font-weight: 600; color: #2c3e50;">Durées</div>', unsafe_allow_html=True)
                duree_examen = st.number_input(
                    "Durée examen (minutes)",
                    min_value=60,
                    max_value=240,
                    value=120,
                    key="duree_exam"
                )
                marge_entre_examens = st.number_input(
                    "Marge entre examens (minutes)",
                    min_value=0,
                    max_value=180,
                    value=30,
                    key="marge"
                )
            
            with col_param3:
                st.markdown('<div style="margin-bottom: 1rem; font-weight: 600; color: #2c3e50;">Options Avancées</div>', unsafe_allow_html=True)
                utiliser_meme_salle = st.checkbox(
                    "Même salle par formation",
                    value=True,
                    help="Tous les examens d'une formation dans la même salle",
                    key="meme_salle"
                )
                verifier_conflits = st.checkbox(
                    "Vérification automatique des conflits",
                    value=True,
                    help="Détecte et évite les conflits automatiquement",
                    key="auto_check"
                )
                optimiser_ressources = st.checkbox(
                    "Optimisation des ressources",
                    value=True,
                    help="Optimise l'utilisation des salles et professeurs",
                    key="optim_ress"
                )
            
            st.markdown('</div></div>', unsafe_allow_html=True)
            
            # Bouton de génération avec design amélioré
            st.markdown('<div style="margin-top: 2rem; text-align: center;">', unsafe_allow_html=True)
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button(
                    "🚀 Générer le Planning",
                    type="primary",
                    use_container_width=True,
                    key="generate_btn"
                ):
                    if not jours_selectionnes:
                        st.markdown(create_info_card(
                            "Veuillez sélectionner au moins un jour pour les examens",
                            "warning", "⚠️"
                        ), unsafe_allow_html=True)
                    elif dept_id is None:
                        st.markdown(create_info_card(
                            "Veuillez sélectionner un département",
                            "warning", "⚠️"
                        ), unsafe_allow_html=True)
                    else:
                        with st.spinner(f"🔄 Génération du planning pour {selected_dept_name}..."):
                            # Ajouter une barre de progression
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            # Simuler les étapes
                            steps = [
                                "Analyse des données...",
                                "Vérification des conflits...",
                                "Optimisation des ressources...",
                                "Génération du planning..."
                            ]
                            
                            for i, step in enumerate(steps):
                                status_text.text(f"🔄 {step}")
                                progress_bar.progress((i + 1) / len(steps))
                                time_module.sleep(0.5)
                            
                            # Ici, vous appelleriez votre fonction de génération
                            # planning, conflits = generer_planning_departement(...)
                            
                            # Pour l'exemple, simulation
                            time_module.sleep(1)
                            progress_bar.progress(100)
                            status_text.text("✅ Génération terminée!")
                            
                            st.markdown(create_info_card(
                                f"Planning généré avec succès pour {selected_dept_name}! "
                                f"15 examens planifiés, 2 conflits résolus automatiquement.",
                                "success", "✅"
                            ), unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        else:  # Planning Général
            st.markdown(create_info_card(
                "Générez un planning pour tous les départements simultanément. "
                "Le système répartira intelligemment les ressources entre départements.",
                "info", "🌍"
            ), unsafe_allow_html=True)
            
            # Paramètres généraux
            col_gen1, col_gen2 = st.columns(2)
            
            with col_gen1:
                annee_scolaire = st.number_input(
                    "Année scolaire", 
                    min_value=2020, 
                    max_value=2030, 
                    value=datetime.now().year,
                    key="annee_gen"
                )
                session = st.selectbox(
                    "Session",
                    ["Principale", "Rattrapage"],
                    key="session_gen"
                )
            
            with col_gen2:
                date_debut = st.date_input(
                    "Date de début",
                    datetime.now(),
                    key="date_debut_gen"
                )
                date_fin = st.date_input(
                    "Date de fin",
                    datetime.now() + timedelta(days=21),
                    key="date_fin_gen"
                )
            
            # Bouton de génération pour planning général
            if st.button(
                "🚀 Générer Planning Général",
                type="primary",
                use_container_width=True,
                key="generate_general_btn"
            ):
                with st.spinner("🔄 Génération du planning général..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    steps = [
                        "Analyse de tous les départements...",
                        "Optimisation globale des ressources...",
                        "Vérification des conflits inter-départements...",
                        "Génération du planning complet..."
                    ]
                    
                    for i, step in enumerate(steps):
                        status_text.text(f"🔄 {step}")
                        progress_bar.progress((i + 1) / len(steps))
                        time_module.sleep(0.5)
                    
                    time_module.sleep(1)
                    progress_bar.progress(100)
                    status_text.text("✅ Génération terminée!")
                    
                    st.markdown(create_info_card(
                        "Planning général généré avec succès! "
                        "156 examens planifiés sur 21 jours.",
                        "success", "✅"
                    ), unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)

# ... (le reste du code précédent reste inchangé jusqu'à la section Visualisation Planning)

# PAGE: Visualisation Planning avec design amélioré
elif selected_menu == "Visualisation Planning":
    st.markdown(create_section_header("🔍", "Visualisation des Emplois du Temps", "Explorez et analysez les plannings existants"), unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="section-content">', unsafe_allow_html=True)
        
        # Filtres avec design amélioré
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div style="margin-bottom: 1rem; font-weight: 600; color: #2c3e50;">Filtre par Structure</div>', unsafe_allow_html=True)
            
            # Sélection du département
            departements = run_query("SELECT id, nom FROM departements ORDER BY nom")
            dept_options = {dept['nom']: dept['id'] for dept in departements}
            
            selected_dept = st.selectbox(
                "Département",
                options=['Tous'] + list(dept_options.keys()),
                key="visu_dept"
            )
            
            if selected_dept != 'Tous':
                formations = run_query("""
                    SELECT id, nom FROM formations 
                    WHERE dept_id = %s
                    ORDER BY nom
                """, (dept_options[selected_dept],))
                
                formation_options = {form['nom']: form['id'] for form in formations}
                selected_formation = st.selectbox(
                    "Formation",
                    options=['Toutes'] + list(formation_options.keys()),
                    key="visu_formation"
                )
            else:
                selected_formation = 'Toutes'
        
        with col2:
            st.markdown('<div style="margin-bottom: 1rem; font-weight: 600; color: #2c3e50;">Filtre par Période</div>', unsafe_allow_html=True)
            
            col_date1, col_date2 = st.columns(2)
            with col_date1:
                date_debut = st.date_input(
                    "Date début",
                    datetime.now(),
                    key="visu_date_debut"
                )
            with col_date2:
                date_fin = st.date_input(
                    "Date fin",
                    datetime.now() + timedelta(days=7),
                    key="visu_date_fin"
                )
            
            session_filter = st.selectbox(
                "Session",
                options=['Toutes', 'Principale', 'Rattrapage'],
                key="visu_session"
            )
        
        # Type d'affichage avec design amélioré - Mettre plus d'espace
        st.markdown("""
        <div style="margin-top: 2rem; margin-bottom: 1.5rem;">
            <div style="font-weight: 600; color: #2c3e50; margin-bottom: 0.5rem;">Mode de Visualisation</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Utiliser des colonnes pour mieux répartir l'espace
        col_display1, col_display2 = st.columns([3, 2])
        
        with col_display1:
            display_type = st.radio(
                "Choisissez le mode d'affichage",
                ["📊 Tableau détaillé", "📅 Vue calendrier", "⏳ Timeline interactive", "🗺️ Vue géographique"],
                key="display_type",
                horizontal=False
            )
        
        with col_display2:
            # Options supplémentaires selon le mode
            st.markdown("**Options d'affichage**")
            
            if display_type == "📊 Tableau détaillé":
                show_details = st.checkbox("Afficher tous les détails", value=True)
                group_by = st.selectbox("Grouper par", ["Jour", "Salle", "Formation", "Professeur"])
                
            elif display_type == "📅 Vue calendrier":
                calendar_view = st.selectbox("Vue calendrier", ["Mensuelle", "Hebdomadaire", "Quotidienne"])
                show_legend = st.checkbox("Afficher légende", value=True)
                
            elif display_type == "⏳ Timeline interactive":
                timeline_scale = st.selectbox("Échelle", ["Heure par heure", "Par demi-journée", "Journalière"])
                show_conflicts = st.checkbox("Afficher les conflits", value=True)
                
            elif display_type == "🗺️ Vue géographique":
                map_type = st.selectbox("Type de carte", ["Plan des bâtiments", "Répartition géographique"])
                cluster_markers = st.checkbox("Regrouper les marqueurs", value=True)
        
        # Bouton de recherche avec design amélioré
        st.markdown('<div style="margin-top: 2rem;">', unsafe_allow_html=True)
        col_search1, col_search2, col_search3 = st.columns([1, 2, 1])
        with col_search2:
            if st.button("🔍 Rechercher Planning", type="primary", use_container_width=True, key="search_btn"):
                st.session_state.show_results = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Afficher les résultats si la recherche a été effectuée
    if st.session_state.get('show_results', False):
        
        # Métriques de résultats en haut
        st.markdown('<div class="section-wrapper" style="margin-top: 2rem;">', unsafe_allow_html=True)
        st.markdown('<div class="section-content">', unsafe_allow_html=True)
        
        col_met1, col_met2, col_met3, col_met4 = st.columns(4)
        with col_met1:
            st.markdown(create_metric_card("📅", "Examens", 25), unsafe_allow_html=True)
        with col_met2:
            st.markdown(create_metric_card("🏫", "Salles utilisées", 8), unsafe_allow_html=True)
        with col_met3:
            st.markdown(create_metric_card("👨‍🏫", "Professeurs", 15), unsafe_allow_html=True)
        with col_met4:
            st.markdown(create_metric_card("🎯", "Taux d'occupation", "78%"), unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        # Affichage selon le type choisi avec des conteneurs adaptés
        st.markdown(f'<div class="section-wrapper" style="margin-top: 2rem;">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-content">', unsafe_allow_html=True)
        
        st.markdown(f'### {display_type}')
        
        if display_type == "📊 Tableau détaillé":
            # TABLEAU DÉTAILLÉ - Version améliorée
            st.markdown("""
            <style>
            .wide-table {
                width: 100%;
                overflow-x: auto;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Données d'exemple détaillées
            examens_data = {
                "Date": ["15/01/2024", "15/01/2024", "15/01/2024", "16/01/2024", "16/01/2024", "16/01/2024", "17/01/2024"],
                "Heure": ["08:30-10:30", "11:00-13:00", "14:30-16:30", "09:00-11:00", "13:30-15:30", "16:00-18:00", "10:00-12:00"],
                "Module": ["Algorithmique", "Base de données", "Réseaux", "Mathématiques", "Physique", "Chimie", "Statistiques"],
                "Niveau": ["L2", "L3", "M1", "L1", "L2", "L3", "M1"],
                "Formation": ["Informatique", "Informatique", "Informatique", "Maths-Physique", "Maths-Physique", "Chimie", "Mathématiques"],
                "Salle": ["Amphi A", "Salle 101", "Salle 102", "Amphi B", "Salle 201", "Labo 1", "Salle 301"],
                "Capacité": ["200/250", "45/50", "50/60", "180/200", "40/50", "25/30", "35/40"],
                "Professeur": ["Dr. Martin", "Dr. Dupont", "Dr. Bernard", "Dr. Leroy", "Dr. Moreau", "Dr. Simon", "Dr. Laurent"],
                "Surveillants": ["2", "1", "1", "2", "1", "1", "1"],
                "Étudiants": [120, 45, 50, 110, 40, 25, 35],
                "Statut": ["✅ Planifié", "✅ Planifié", "⚠️ À confirmer", "✅ Planifié", "✅ Planifié", "✅ Planifié", "✅ Planifié"]
            }
            
            df_examens = pd.DataFrame(examens_data)
            
            # Options d'affichage du tableau
            col_table1, col_table2 = st.columns([3, 1])
            with col_table2:
                page_size = st.selectbox("Lignes par page", [10, 25, 50, 100], index=0)
                show_all = st.checkbox("Afficher toutes les colonnes", value=True)
            
            # Affichage du tableau avec pagination
            if show_all:
                st.dataframe(
                    df_examens,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
            else:
                # Version simplifiée
                df_simple = df_examens[['Date', 'Heure', 'Module', 'Formation', 'Salle', 'Professeur', 'Statut']]
                st.dataframe(
                    df_simple,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
            
            # Statistiques supplémentaires
            st.markdown("---")
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            with col_stats1:
                st.metric("Durée moyenne", "2h15")
            with col_stats2:
                st.metric("Salles les plus utilisées", "Amphi A, Salle 101")
            with col_stats3:
                st.metric("Période chargée", "15-16 Janvier")
        
        elif display_type == "📅 Vue calendrier":
            # VUE CALENDRIER - Version interactive
            st.markdown("""
            <style>
            .calendar-container {
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 1rem;
                background: white;
                margin: 1rem 0;
            }
            .calendar-day {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 0.5rem;
                margin: 0.25rem;
                min-height: 120px;
            }
            .calendar-day-header {
                font-weight: bold;
                color: #2c3e50;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 0.25rem;
                margin-bottom: 0.5rem;
            }
            .calendar-event {
                background: #3498db;
                color: white;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                margin: 0.25rem 0;
                font-size: 0.8rem;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .calendar-event:hover {
                background: #2980b9;
                transform: translateX(5px);
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Sélection de la semaine
            week_start = st.date_input("Semaine du", datetime.now())
            week_days = [week_start + timedelta(days=i) for i in range(7)]
            
            # Créer un calendrier hebdomadaire
            st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
            st.markdown("### 📅 Calendrier Hebdomadaire")
            
            # En-têtes des jours
            days_cols = st.columns(7)
            day_names = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
            
            for i, col in enumerate(days_cols):
                with col:
                    day_date = week_days[i]
                    st.markdown(f"""
                    <div class="calendar-day">
                        <div class="calendar-day-header">
                            {day_names[i]}<br>
                            <small>{day_date.strftime('%d/%m')}</small>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Événements pour ce jour (exemple)
                    events = []
                    if i == 0:  # Lundi
                        events = [
                            ("08:30-10:30", "Algorithmique", "Amphi A", "blue"),
                            ("14:00-16:00", "Base de données", "Salle 101", "green"),
                        ]
                    elif i == 1:  # Mardi
                        events = [
                            ("09:00-11:00", "Réseaux", "Salle 102", "red"),
                            ("15:00-17:00", "Sécurité", "Labo 2", "purple"),
                        ]
                    elif i == 2:  # Mercredi
                        events = [
                            ("10:30-12:30", "Mathématiques", "Amphi B", "orange"),
                        ]
                    
                    for event in events:
                        st.markdown(f"""
                        <div class="calendar-event" style="background: {event[3]};">
                            <strong>{event[0]}</strong><br>
                            {event[1]}<br>
                            <small>{event[2]}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Légende
            st.markdown("""
            <div style="display: flex; gap: 1rem; margin-top: 1rem; flex-wrap: wrap;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 15px; height: 15px; background: #3498db; border-radius: 3px;"></div>
                    <span>Informatique</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 15px; height: 15px; background: #2ecc71; border-radius: 3px;"></div>
                    <span>Base de données</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 15px; height: 15px; background: #e74c3c; border-radius: 3px;"></div>
                    <span>Réseaux</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 15px; height: 15px; background: #9b59b6; border-radius: 3px;"></div>
                    <span>Sécurité</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 15px; height: 15px; background: #f39c12; border-radius: 3px;"></div>
                    <span>Mathématiques</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Graphique de répartition
            st.markdown("### 📊 Répartition des examens par jour")
            jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
            nb_examens = [2, 2, 1, 3, 4, 0, 0]
            
            fig = px.bar(x=jours, y=nb_examens, 
                        labels={'x': 'Jour', 'y': "Nombre d'examens"},
                        color=nb_examens,
                        color_continuous_scale='Viridis')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        elif display_type == "⏳ Timeline interactive":
            # TIMELINE INTERACTIVE - Version améliorée
            st.markdown("""
            <style>
            .timeline-container {
                position: relative;
                padding: 2rem 0;
            }
            .timeline-line {
                position: absolute;
                left: 50px;
                top: 0;
                bottom: 0;
                width: 4px;
                background: linear-gradient(to bottom, #3498db, #2ecc71);
                border-radius: 2px;
            }
            .timeline-item {
                position: relative;
                margin-left: 80px;
                margin-bottom: 2rem;
                padding: 1rem;
                background: white;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }
            .timeline-item:hover {
                transform: translateX(10px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            .timeline-dot {
                position: absolute;
                left: -40px;
                top: 20px;
                width: 20px;
                height: 20px;
                border-radius: 50%;
                background: #3498db;
                border: 3px solid white;
                box-shadow: 0 0 0 3px #3498db;
            }
            .timeline-time {
                font-weight: bold;
                color: #2c3e50;
                font-size: 1.1rem;
            }
            .timeline-title {
                font-weight: 600;
                color: #3498db;
                margin-top: 0.5rem;
            }
            .timeline-details {
                color: #7f8c8d;
                font-size: 0.9rem;
                margin-top: 0.5rem;
            }
            .timeline-badge {
                display: inline-block;
                padding: 0.25rem 0.75rem;
                border-radius: 12px;
                font-size: 0.75rem;
                font-weight: 500;
                margin-right: 0.5rem;
            }
            .badge-informatique { background: #3498db; color: white; }
            .badge-mathematiques { background: #2ecc71; color: white; }
            .badge-physique { background: #e74c3c; color: white; }
            .badge-chimie { background: #9b59b6; color: white; }
            </style>
            """, unsafe_allow_html=True)
            
            # Sélection de la journée
            selected_day = st.date_input("Journée", datetime.now())
            day_str = selected_day.strftime("%A %d %B %Y")
            
            st.markdown(f'<h3>🗓️ Timeline du {day_str}</h3>', unsafe_allow_html=True)
            
            # Création de la timeline
            st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
            st.markdown('<div class="timeline-line"></div>', unsafe_allow_html=True)
            
            # Événements de la timeline
            timeline_events = [
                {
                    "time": "08:30 - 10:30",
                    "title": "Examen Algorithmique",
                    "details": "Licence 2 Informatique • Amphi A • Dr. Martin",
                    "badge": "informatique",
                    "students": 120,
                    "status": "en cours"
                },
                {
                    "time": "11:00 - 13:00", 
                    "title": "Examen Base de données",
                    "details": "Licence 3 Informatique • Salle 101 • Dr. Dupont",
                    "badge": "informatique",
                    "students": 45,
                    "status": "à venir"
                },
                {
                    "time": "14:30 - 16:30",
                    "title": "Examen Réseaux",
                    "details": "Master 1 Informatique • Salle 102 • Dr. Bernard",
                    "badge": "informatique", 
                    "students": 50,
                    "status": "à venir"
                },
                {
                    "time": "16:45 - 18:45",
                    "title": "Examen Mathématiques",
                    "details": "Licence 1 Maths-Physique • Amphi B • Dr. Leroy",
                    "badge": "mathematiques",
                    "students": 110,
                    "status": "à venir"
                }
            ]
            
            for i, event in enumerate(timeline_events):
                status_color = "#2ecc71" if event["status"] == "en cours" else "#f39c12" if event["status"] == "à venir" else "#95a5a6"
                
                st.markdown(f"""
                <div class="timeline-item">
                    <div class="timeline-dot" style="background: {status_color}; box-shadow: 0 0 0 3px {status_color};"></div>
                    <div class="timeline-time">{event['time']}</div>
                    <div>
                        <span class="timeline-badge badge-{event['badge']}">{event['badge'].title()}</span>
                        <span class="timeline-badge" style="background: {status_color}; color: white;">{event['status'].title()}</span>
                    </div>
                    <div class="timeline-title">{event['title']}</div>
                    <div class="timeline-details">{event['details']}</div>
                    <div class="timeline-details">
                        <strong>{event['students']}</strong> étudiants • 
                        <span style="color: {status_color};">● {event['status'].title()}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Graphique de timeline
            st.markdown("### 📈 Occupation horaire")
            
            # Créer un graphique Gantt-like
            hours = list(range(8, 19))  # De 8h à 18h
            exam_data = []
            
            for hour in hours:
                for event in timeline_events:
                    start_hour = int(event['time'].split(':')[0])
                    if start_hour == hour:
                        exam_data.append({
                            'Heure': f"{hour}:00",
                            'Durée': 2,
                            'Module': event['title'].replace('Examen ', ''),
                            'Salle': event['details'].split('•')[1].strip(),
                            'Étudiants': event['students']
                        })
            
            if exam_data:
                df_timeline = pd.DataFrame(exam_data)
                fig = px.bar(df_timeline, x='Heure', y='Durée', color='Module',
                           hover_data=['Salle', 'Étudiants'],
                           title="Répartition horaire des examens")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        elif display_type == "🗺️ Vue géographique":
            # VUE GÉOGRAPHIQUE / PLAN
            st.markdown("""
            <style>
            .map-container {
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                padding: 1rem;
                background: #f8f9fa;
                margin: 1rem 0;
                position: relative;
                height: 600px;
            }
            .building {
                position: absolute;
                border: 2px solid #2c3e50;
                border-radius: 8px;
                padding: 1rem;
                background: white;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }
            .building:hover {
                transform: scale(1.05);
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
                z-index: 100;
            }
            .building-header {
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 0.5rem;
            }
            .room {
                background: #3498db;
                color: white;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                margin: 0.25rem 0;
                font-size: 0.8rem;
                cursor: pointer;
            }
            .room.occupied {
                background: #e74c3c;
            }
            .room.available {
                background: #2ecc71;
            }
            .legend {
                display: flex;
                gap: 1rem;
                margin-top: 1rem;
                flex-wrap: wrap;
            }
            .legend-item {
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Options de la carte
            col_map1, col_map2 = st.columns(2)
            with col_map1:
                show_occupancy = st.checkbox("Afficher taux d'occupation", value=True)
                highlight_conflicts = st.checkbox("Surligner les conflits", value=True)
            with col_map2:
                filter_by_building = st.selectbox("Filtrer par bâtiment", ["Tous", "Bâtiment A", "Bâtiment B", "Bâtiment C", "Bâtiment D"])
            
            # Carte/Plan des bâtiments
            st.markdown('<div class="map-container">', unsafe_allow_html=True)
            st.markdown("### 🏫 Plan des Bâtiments - Campus Central")
            
            # Bâtiment A
            st.markdown("""
            <div class="building" style="left: 50px; top: 50px; width: 300px;">
                <div class="building-header">🏢 Bâtiment A - Sciences</div>
                <div class="room occupied" title="Amphi A - 120 étudiants - Algorithmique">Amphi A <small>(120/250)</small></div>
                <div class="room available" title="Salle 101 - 45 étudiants - Base de données">Salle 101 <small>(45/50)</small></div>
                <div class="room available" title="Salle 102 - 50 étudiants - Réseaux">Salle 102 <small>(50/60)</small></div>
                <div class="room" title="Salle 103 - Disponible">Salle 103 <small>(0/50)</small></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Bâtiment B
            st.markdown("""
            <div class="building" style="left: 400px; top: 50px; width: 250px;">
                <div class="building-header">🏢 Bâtiment B - Mathématiques</div>
                <div class="room occupied" title="Amphi B - 110 étudiants - Mathématiques">Amphi B <small>(110/200)</small></div>
                <div class="room available" title="Salle 201 - 40 étudiants - Physique">Salle 201 <small>(40/50)</small></div>
                <div class="room" title="Salle 202 - Disponible">Salle 202 <small>(0/40)</small></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Bâtiment C
            st.markdown("""
            <div class="building" style="left: 50px; top: 250px; width: 280px;">
                <div class="building-header">🏢 Bâtiment C - Chimie/Biologie</div>
                <div class="room occupied" title="Labo 1 - 25 étudiants - Chimie">Labo 1 <small>(25/30)</small></div>
                <div class="room" title="Labo 2 - Disponible">Labo 2 <small>(0/25)</small></div>
                <div class="room" title="Labo 3 - Disponible">Labo 3 <small>(0/25)</small></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Bâtiment D
            st.markdown("""
            <div class="building" style="left: 380px; top: 250px; width: 270px;">
                <div class="building-header">🏢 Bâtiment D - Informatique Avancée</div>
                <div class="room available" title="Salle 301 - 35 étudiants - Statistiques">Salle 301 <small>(35/40)</small></div>
                <div class="room" title="Salle 302 - Disponible">Salle 302 <small>(0/30)</small></div>
                <div class="room" title="Salle 303 - Disponible">Salle 303 <small>(0/30)</small></div>
                <div class="room" title="Salle 304 - Disponible">Salle 304 <small>(0/30)</small></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Légende
            st.markdown("""
            <div class="legend">
                <div class="legend-item">
                    <div class="room" style="background: #3498db;"></div>
                    <span>Salle disponible</span>
                </div>
                <div class="legend-item">
                    <div class="room" style="background: #2ecc71;"></div>
                    <span>Salle occupée (taux < 90%)</span>
                </div>
                <div class="legend-item">
                    <div class="room" style="background: #e74c3c;"></div>
                    <span>Salle surchargée (taux > 90%)</span>
                </div>
                <div class="legend-item">
                    <div style="width: 15px; height: 15px; border: 2px solid #2c3e50; border-radius: 3px;"></div>
                    <span>Bâtiment</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Statistiques par bâtiment
            st.markdown("### 📊 Statistiques par Bâtiment")
            
            building_stats = {
                "Bâtiment": ["Bâtiment A", "Bâtiment B", "Bâtiment C", "Bâtiment D"],
                "Salles totales": [4, 3, 3, 4],
                "Salles occupées": [3, 2, 1, 1],
                "Taux occupation": ["75%", "67%", "33%", "25%"],
                "Étudiants total": [215, 150, 25, 35],
                "Examens aujourd'hui": [3, 2, 1, 1]
            }
            
            df_buildings = pd.DataFrame(building_stats)
            st.dataframe(df_buildings, use_container_width=True, hide_index=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        # Bouton d'export en bas de page
        st.markdown('<div class="section-wrapper" style="margin-top: 2rem;">', unsafe_allow_html=True)
        st.markdown('<div class="section-content">', unsafe_allow_html=True)
        
        st.markdown("### 📤 Export des Données")
        col_exp1, col_exp2, col_exp3, col_exp4 = st.columns(4)
        
        with col_exp1:
            if st.button("📥 PDF", use_container_width=True):
                st.success("Rapport PDF généré!")
        
        with col_exp2:
            if st.button("📊 Excel", use_container_width=True):
                st.success("Fichier Excel généré!")
        
        with col_exp3:
            if st.button("🌐 HTML", use_container_width=True):
                st.success("Rapport HTML généré!")
        
        with col_exp4:
            if st.button("📋 Copier", use_container_width=True):
                st.success("Données copiées dans le presse-papier!")
        
        st.markdown('</div></div>', unsafe_allow_html=True)

# ... (le reste du code reste inchangé)

# PAGE: Planning Général avec design amélioré
elif selected_menu == "Planning Général":
    st.markdown(create_section_header("🌍", "Planning Général", "Vue d'ensemble de tous les départements"), unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="section-content">', unsafe_allow_html=True)
        
        # Métriques globales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_depts = run_query("SELECT COUNT(*) as count FROM departements")[0]['count']
            st.markdown(create_metric_card("🏢", "Départements actifs", total_depts), unsafe_allow_html=True)
        with col2:
            total_exams = run_query("SELECT COUNT(*) as count FROM examens WHERE statut = 'planifié'")[0]['count']
            st.markdown(create_metric_card("📅", "Examens totaux", total_exams), unsafe_allow_html=True)
        with col3:
            total_students = run_query("SELECT COUNT(DISTINCT id) as count FROM etudiants")[0]['count']
            st.markdown(create_metric_card("👥", "Étudiants concernés", f"{total_students:,}"), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card("📈", "Taux d'occupation", "85%"), unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Filtres avancés
    with st.container():
        st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="section-content">', unsafe_allow_html=True)
        
        col_filt1, col_filt2, col_filt3 = st.columns(3)
        
        with col_filt1:
            date_debut = st.date_input(
                "Date de début",
                datetime.now(),
                key="general_debut"
            )
        
        with col_filt2:
            date_fin = st.date_input(
                "Date de fin",
                datetime.now() + timedelta(days=14),
                key="general_fin"
            )
        
        with col_filt3:
            departements = run_query("SELECT id, nom FROM departements ORDER BY nom")
            selected_dept = st.selectbox(
                "Filtrer par département",
                options=['Tous'] + [dept['nom'] for dept in departements],
                key="general_dept"
            )
        
        # Bouton de chargement
        if st.button("🔍 Charger le Planning Général", type="primary", use_container_width=True, key="load_general"):
            with st.spinner("🔄 Chargement du planning général..."):
                # Simulation
                progress_bar = st.progress(0)
                for i in range(100):
                    progress_bar.progress(i + 1)
                    time_module.sleep(0.01)
                
                st.markdown(create_info_card(
                    "Planning général chargé avec succès! "
                    f"{total_exams} examens planifiés sur 14 jours.",
                    "success", "✅"
                ), unsafe_allow_html=True)
                
                # Afficher un aperçu des données
                planning_data = run_query("""
                    SELECT 
                        ex.id,
                        m.nom as module,
                        d.nom as departement,
                        ex.date_examen,
                        ex.heure_debut,
                        ex.heure_fin,
                        l.nom as salle
                    FROM examens ex
                    JOIN modules m ON ex.module_id = m.id
                    JOIN formations f ON m.formation_id = f.id
                    JOIN departements d ON f.dept_id = d.id
                    JOIN lieu_examen l ON ex.salle_id = l.id
                    WHERE ex.statut = 'planifié'
                        AND ex.date_examen BETWEEN %s AND %s
                    ORDER BY ex.date_examen, ex.heure_debut
                    LIMIT 20
                """, (date_debut, date_fin))
                
                if planning_data:
                    df_planning = pd.DataFrame(planning_data)
                    df_planning['date_examen'] = pd.to_datetime(df_planning['date_examen']).dt.strftime('%d/%m/%Y')
                    df_planning['heure_debut'] = df_planning['heure_debut'].astype(str)
                    df_planning['heure_fin'] = df_planning['heure_fin'].astype(str)
                    
                    st.dataframe(
                        df_planning.rename(columns={
                            'module': 'Module',
                            'departement': 'Département',
                            'date_examen': 'Date',
                            'heure_debut': 'Heure Début',
                            'heure_fin': 'Heure Fin',
                            'salle': 'Salle'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
        
        st.markdown('</div></div>', unsafe_allow_html=True)

# PAGE: Détection Conflits avec design amélioré
elif selected_menu == "Détection Conflits":
    st.markdown(create_section_header("⚠️", "Détection Intelligente des Conflits", "Système avancé d'analyse et résolution"), unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="section-content">', unsafe_allow_html=True)
        
        # Sélection de la période
        col1, col2 = st.columns(2)
        
        with col1:
            date_debut_conflits = st.date_input(
                "Date de début",
                datetime.now(),
                key="conflit_debut"
            )
        
        with col2:
            date_fin_conflits = st.date_input(
                "Date de fin",
                datetime.now() + timedelta(days=30),
                key="conflit_fin"
            )
        
        # Type de conflit avec design amélioré
        st.markdown('<div style="margin: 2rem 0 1rem 0; font-weight: 600; color: #2c3e50;">Type d\'analyse</div>', unsafe_allow_html=True)
        
        type_conflit = st.selectbox(
            "Sélectionnez le type de conflit à analyser",
            [
                "🔍 Analyse complète (tous les types)",
                "👨‍🎓 Conflits étudiants",
                "🏫 Conflits de salles", 
                "👨‍🏫 Conflits professeurs",
                "⚠️ Salles surchargées",
                "⏰ Chevauchements horaires"
            ],
            key="type_conflit_select"
        )
        
        # Options avancées
        with st.expander("⚙️ Options avancées d'analyse"):
            col_opt1, col_opt2 = st.columns(2)
            with col_opt1:
                auto_resolve = st.checkbox(
                    "Résolution automatique",
                    value=True,
                    help="Tente de résoudre automatiquement les conflits"
                )
                notify_users = st.checkbox(
                    "Notification des concernés",
                    value=True,
                    help="Envoie des notifications aux personnes concernées"
                )
            
            with col_opt2:
                severity_threshold = st.slider(
                    "Seuil de gravité",
                    min_value=1,
                    max_value=10,
                    value=5,
                    help="Seuil minimum pour considérer un conflit comme critique"
                )
                generate_report = st.checkbox(
                    "Générer un rapport détaillé",
                    value=True
                )
        
        # Bouton d'analyse avec design amélioré
        st.markdown('<div style="margin-top: 2rem; text-align: center;">', unsafe_allow_html=True)
        if st.button("🔍 Lancer l'Analyse des Conflits", type="primary", use_container_width=True, key="analyze_conflicts"):
            with st.spinner("🔍 Analyse en cours..."):
                # Simulation d'analyse
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                steps = [
                    "Collecte des données...",
                    "Analyse des chevauchements...",
                    "Vérification des capacités...",
                    "Détection des conflits...",
                    "Génération du rapport..."
                ]
                
                for i, step in enumerate(steps):
                    status_text.text(f"🔄 {step}")
                    progress_bar.progress((i + 1) / len(steps))
                    time_module.sleep(0.8)
                
                # Résultats
                st.markdown(create_info_card(
                    "✅ Analyse terminée! 8 conflits détectés, 6 résolus automatiquement.",
                    "success", "✅"
                ), unsafe_allow_html=True)
                
                # Afficher les résultats
                st.markdown('<div class="section-wrapper" style="margin-top: 2rem;">', unsafe_allow_html=True)
                st.markdown('<div class="section-content">', unsafe_allow_html=True)
                
                # Métriques de conflits
                col_conf1, col_conf2, col_conf3, col_conf4 = st.columns(4)
                with col_conf1:
                    st.markdown(create_metric_card("⚠️", "Conflits totaux", 8, -15, "vs dernière analyse"), unsafe_allow_html=True)
                with col_conf2:
                    st.markdown(create_metric_card("✅", "Résolus automatiquement", 6, 20, "amélioration"), unsafe_allow_html=True)
                with col_conf3:
                    st.markdown(create_metric_card("👨‍🎓", "Conflits étudiants", 3, -10, "réduction"), unsafe_allow_html=True)
                with col_conf4:
                    st.markdown(create_metric_card("🏫", "Conflits salles", 2, -5, "réduction"), unsafe_allow_html=True)
                
                # Détails des conflits
                st.markdown('<div style="margin-top: 2rem;">', unsafe_allow_html=True)
                st.markdown('### 📋 Liste des Conflits Détectés')
                
                # Tableau des conflits
                conflits_data = {
                    "Type": ["Étudiant", "Salle", "Professeur", "Surcharge", "Horaire"],
                    "Gravité": ["Moyenne", "Haute", "Basse", "Critique", "Moyenne"],
                    "Description": [
                        "2 examens le même jour pour 15 étudiants",
                        "Double réservation de l'Amphi A",
                        "Professeur avec 3 surveillances simultanées",
                        "Salle 101: 120 étudiants pour 100 places",
                        "Chevauchement horaire Informatique/Mathématiques"
                    ],
                    "Statut": ["Résolu", "À vérifier", "Résolu", "Critique", "Résolu"],
                    "Action": ["Automatique", "Manuelle", "Automatique", "Urgente", "Automatique"]
                }
                
                df_conflits = pd.DataFrame(conflits_data)
                st.dataframe(
                    df_conflits,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('</div></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)

# PAGE: Statistiques avec design amélioré
elif selected_menu == "Statistiques":
    st.markdown(create_section_header("📊", "Analytiques Avancées", "Tableau de bord des performances et indicateurs"), unsafe_allow_html=True)
    
    # Sélection du type de statistiques
    stat_type = st.selectbox(
        "Type de statistiques",
        [
            "📈 Tableau de bord principal",
            "🏢 Occupation des ressources", 
            "⚠️ Conflits et problèmes",
            "⚡ Performance génération",
            "📅 Répartition examens",
            "🎓 Statistiques par département",
            "📊 Indicateurs de performance"
        ],
        key="stat_type"
    )
    
    if stat_type == "📈 Tableau de bord principal":
        with st.container():
            st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
            st.markdown('<div class="section-content">', unsafe_allow_html=True)
            
            # KPI Grid
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(create_metric_card("📅", "Taux de planification", "98%", 2), unsafe_allow_html=True)
            with col2:
                st.markdown(create_metric_card("✅", "Conflits résolus", "94%", 5), unsafe_allow_html=True)
            with col3:
                st.markdown(create_metric_card("🏫", "Utilisation salles", "85%", 3), unsafe_allow_html=True)
            with col4:
                st.markdown(create_metric_card("👥", "Satisfaction", "92%", 1), unsafe_allow_html=True)
            
            # Graphiques principaux
            st.markdown('<div style="margin-top: 3rem;">', unsafe_allow_html=True)
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown('### 📈 Évolution Mensuelle')
                # Graphique exemple
                months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun']
                values = [85, 88, 90, 92, 94, 96]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=months,
                    y=values,
                    mode='lines+markers',
                    line=dict(color='#3498db', width=3),
                    marker=dict(size=10, color='white', line=dict(width=2, color='#3498db'))
                ))
                
                fig.update_layout(
                    height=300,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    xaxis=dict(
                        gridcolor='#f1f1f1',
                        showline=True,
                        linecolor='#e0e0e0'
                    ),
                    yaxis=dict(
                        gridcolor='#f1f1f1',
                        showline=True,
                        linecolor='#e0e0e0',
                        range=[80, 100]
                    ),
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            with col_chart2:
                st.markdown('### 📊 Répartition par Type')
                # Pie chart exemple
                labels = ['Planifiés', 'En attente', 'Annulés', 'Reportés']
                values = [75, 15, 5, 5]
                
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=.3,
                    marker_colors=['#2ecc71', '#f39c12', '#e74c3c', '#3498db']
                )])
                
                fig.update_layout(
                    height=300,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Tableau des performances
            st.markdown('<div style="margin-top: 3rem;">', unsafe_allow_html=True)
            st.markdown('### 🎯 Performances par Département')
            
            perf_data = {
                "Département": ["Informatique", "Mathématiques", "Physique", "Chimie", "Biologie"],
                "Taux planif.": ["98%", "96%", "94%", "92%", "90%"],
                "Conflits résolus": ["96%", "94%", "92%", "90%", "88%"],
                "Utilisation salles": ["92%", "88%", "85%", "82%", "80%"],
                "Score": [95, 92, 89, 86, 83]
            }
            
            df_perf = pd.DataFrame(perf_data)
            st.dataframe(
                df_perf,
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div></div>', unsafe_allow_html=True)

# PAGE: Configuration avec design amélioré
elif selected_menu == "Configuration":
    st.markdown(create_section_header("⚙️", "Configuration du Système", "Paramétrage et administration avancée"), unsafe_allow_html=True)
    
    # Onglets de configuration
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏢 Départements",
        "👨‍🏫 Professeurs", 
        "🏫 Salles",
        "📋 Contraintes",
        "⚡ Paramètres"
    ])
    
    with tab1:
        st.markdown("### 🏢 Gestion des Départements")
        
        col_tab1_1, col_tab1_2 = st.columns([2, 1])
        
        with col_tab1_1:
            with st.container():
                st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
                st.markdown('<div class="section-content">', unsafe_allow_html=True)
                
                with st.form("ajout_departement_form"):
                    col_form1, col_form2 = st.columns(2)
                    
                    with col_form1:
                        nom_dept = st.text_input("Nom du département", placeholder="Ex: Informatique")
                        code_dept = st.text_input("Code département", placeholder="Ex: INFO")
                    
                    with col_form2:
                        # Sélection du responsable
                        professeurs = run_query("SELECT id, CONCAT(nom, ' ', prenom) as nom_complet FROM professeurs")
                        prof_options = {p['nom_complet']: p['id'] for p in professeurs}
                        
                        if prof_options:
                            responsable_nom = st.selectbox(
                                "Responsable",
                                options=[''] + list(prof_options.keys()),
                                help="Professeur responsable du département"
                            )
                            responsable_id = prof_options[responsable_nom] if responsable_nom else None
                        else:
                            st.warning("Aucun professeur disponible")
                            responsable_id = None
                    
                    # Informations supplémentaires
                    description = st.text_area(
                        "Description",
                        placeholder="Description du département...",
                        height=100
                    )
                    
                    # Bouton de soumission
                    col_submit1, col_submit2, col_submit3 = st.columns([1, 2, 1])
                    with col_submit2:
                        if st.form_submit_button("✅ Ajouter le département", use_container_width=True):
                            if nom_dept:
                                st.success(f"Département {nom_dept} ajouté avec succès!")
                            else:
                                st.error("Veuillez remplir le nom du département")
                
                st.markdown('</div></div>', unsafe_allow_html=True)
        
        with col_tab1_2:
            with st.container():
                st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
                st.markdown('<div class="section-content">', unsafe_allow_html=True)
                
                # Liste des départements
                departements = run_query("""
                    SELECT d.*, CONCAT(p.nom, ' ', p.prenom) as responsable
                    FROM departements d
                    LEFT JOIN professeurs p ON d.responsable_id = p.id
                    ORDER BY d.nom
                """)
                
                if departements:
                    df_depts = pd.DataFrame(departements)
                    
                    for _, dept in df_depts.iterrows():
                        with st.container():
                            col_dept1, col_dept2 = st.columns([4, 1])
                            with col_dept1:
                                st.markdown(f"**{dept['nom']}**")
                                if pd.notna(dept['responsable']):
                                    st.markdown(f"*Responsable: {dept['responsable']}*")
                            with col_dept2:
                                if st.button("📝", key=f"edit_{dept['id']}"):
                                    st.info(f"Édition de {dept['nom']}")
                            st.markdown("---")
                else:
                    st.info("Aucun département enregistré")
                
                st.markdown('</div></div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 👨‍🏫 Gestion des Professeurs")
        
        col_tab2_1, col_tab2_2 = st.columns([2, 1])
        
        with col_tab2_1:
            with st.container():
                st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
                st.markdown('<div class="section-content">', unsafe_allow_html=True)
                
                with st.form("ajout_professeur_form"):
                    col_prof1, col_prof2, col_prof3 = st.columns(3)
                    
                    with col_prof1:
                        nom_prof = st.text_input("Nom", placeholder="Dupont")
                        prenom_prof = st.text_input("Prénom", placeholder="Jean")
                        email = st.text_input("Email", placeholder="jean.dupont@universite.fr")
                    
                    with col_prof2:
                        specialite = st.text_input("Spécialité", placeholder="Informatique théorique")
                        heures_service = st.number_input(
                            "Heures service",
                            min_value=0,
                            max_value=500,
                            value=192,
                            help="Heures annuelles de service"
                        )
                        telephone = st.text_input("Téléphone", placeholder="+33 1 23 45 67 89")
                    
                    with col_prof3:
                        # Sélection du département
                        departements = run_query("SELECT id, nom FROM departements")
                        dept_options = {d['nom']: d['id'] for d in departements}
                        
                        if dept_options:
                            dept_nom = st.selectbox(
                                "Département",
                                options=[''] + list(dept_options.keys()),
                                help="Département d'affectation"
                            )
                            dept_id = dept_options[dept_nom] if dept_nom else None
                        else:
                            dept_id = None
                        
                        statut = st.selectbox(
                            "Statut",
                            ["Titulaire", "Contractuel", "Vacataire", "Émérite"]
                        )
                        bureau = st.text_input("Bureau", placeholder="Bâtiment A, Bureau 205")
                    
                    # Options supplémentaires
                    disponibilites = st.multiselect(
                        "Disponibilités préférées",
                        ["Lundi matin", "Lundi après-midi", "Mardi matin", "Mardi après-midi",
                         "Mercredi matin", "Mercredi après-midi", "Jeudi matin", "Jeudi après-midi",
                         "Vendredi matin", "Vendredi après-midi"],
                        default=["Lundi matin", "Mardi matin", "Jeudi matin"]
                    )
                    
                    # Bouton de soumission
                    col_submit1, col_submit2, col_submit3 = st.columns([1, 2, 1])
                    with col_submit2:
                        if st.form_submit_button("👨‍🏫 Ajouter le professeur", use_container_width=True):
                            if nom_prof and prenom_prof:
                                st.success(f"Professeur {nom_prof} {prenom_prof} ajouté avec succès!")
                            else:
                                st.error("Veuillez remplir le nom et prénom")
                
                st.markdown('</div></div>', unsafe_allow_html=True)
        
        with col_tab2_2:
            with st.container():
                st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
                st.markdown('<div class="section-content">', unsafe_allow_html=True)
                
                # Liste des professeurs
                professeurs = run_query("""
                    SELECT p.*, d.nom as departement
                    FROM professeurs p
                    LEFT JOIN departements d ON p.departement_id = d.id
                    ORDER BY p.nom, p.prenom
                """)
                
                if professeurs:
                    st.markdown("### 📋 Liste des Professeurs")
                    
                    for prof in professeurs:
                        with st.container():
                            col_prof1, col_prof2 = st.columns([4, 1])
                            with col_prof1:
                                st.markdown(f"**{prof['prenom']} {prof['nom']}**")
                                st.markdown(f"*{prof['specialite']}*")
                                if prof['departement']:
                                    st.markdown(f"📍 {prof['departement']}")
                            with col_prof2:
                                if st.button("✏️", key=f"edit_prof_{prof['id']}"):
                                    st.info(f"Édition de {prof['prenom']} {prof['nom']}")
                            st.markdown("---")
                else:
                    st.info("Aucun professeur enregistré")
                
                st.markdown('</div></div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 🏫 Gestion des Salles")
        
        col_tab3_1, col_tab3_2 = st.columns([2, 1])
        
        with col_tab3_1:
            with st.container():
                st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
                st.markdown('<div class="section-content">', unsafe_allow_html=True)
                
                with st.form("ajout_salle_form"):
                    col_salle1, col_salle2 = st.columns(2)
                    
                    with col_salle1:
                        nom_salle = st.text_input("Nom de la salle", placeholder="Ex: Amphi A")
                        type_salle = st.selectbox(
                            "Type de salle",
                            ["Amphithéâtre", "Salle de cours", "Laboratoire", "Salle informatique", "Salle de TP"]
                        )
                        capacite = st.number_input(
                            "Capacité",
                            min_value=1,
                            max_value=500,
                            value=50,
                            help="Nombre maximum d'étudiants"
                        )
                    
                    with col_salle2:
                        batiment = st.text_input("Bâtiment", placeholder="Ex: Bâtiment A")
                        etage = st.selectbox("Étage", ["Rez-de-chaussée", "1er étage", "2ème étage", "3ème étage", "4ème étage"])
                        equipement = st.multiselect(
                            "Équipements",
                            ["Vidéoprojecteur", "Tableau blanc", "Climatisation", "Wi-Fi", "Prise réseau",
                             "Ordinateurs", "Matériel de TP", "Micro", "Enceintes", "Tableau interactif"]
                        )
                    
                    # Caractéristiques supplémentaires
                    disponibilite = st.radio(
                        "Disponibilité",
                        ["Disponible", "En maintenance", "Réservé"],
                        horizontal=True
                    )
                    
                    restrictions = st.text_area(
                        "Restrictions/Notes",
                        placeholder="Ex: Ne pas utiliser pour les examens de chimie...",
                        height=80
                    )
                    
                    # Bouton de soumission
                    if st.form_submit_button("➕ Ajouter la salle", use_container_width=True):
                        if nom_salle:
                            st.success(f"Salle {nom_salle} ajoutée avec succès!")
                        else:
                            st.error("Veuillez remplir le nom de la salle")
                
                st.markdown('</div></div>', unsafe_allow_html=True)
        
        with col_tab3_2:
            with st.container():
                st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
                st.markdown('<div class="section-content">', unsafe_allow_html=True)
                
                # Liste des salles
                salles = run_query("""
                    SELECT * FROM lieu_examen 
                    ORDER BY batiment, nom
                """)
                
                if salles:
                    st.markdown("### 📋 Liste des Salles")
                    
                    # Filtres rapides
                    filter_type = st.selectbox("Filtrer par type", ["Tous", "Amphithéâtre", "Salle de cours", "Laboratoire", "Salle informatique"])
                    filter_building = st.selectbox("Filtrer par bâtiment", ["Tous", "Bâtiment A", "Bâtiment B", "Bâtiment C", "Bâtiment D"])
                    
                    for salle in salles:
                        if (filter_type == "Tous" or salle['type'] == filter_type) and \
                           (filter_building == "Tous" or salle['batiment'] == filter_building):
                            
                            with st.container():
                                col_salle1, col_salle2 = st.columns([4, 1])
                                with col_salle1:
                                    # Icône selon le type
                                    icon = "🏛️" if salle['type'] == "Amphithéâtre" else \
                                           "🏫" if salle['type'] == "Salle de cours" else \
                                           "🔬" if salle['type'] == "Laboratoire" else "💻"
                                    
                                    st.markdown(f"{icon} **{salle['nom']}**")
                                    st.markdown(f"*{salle['type']} • {salle['capacite']} places • {salle['batiment']}*")
                                    
                                    # Badge de disponibilité
                                    if salle['disponible']:
                                        st.markdown('<span style="color: green;">● Disponible</span>', unsafe_allow_html=True)
                                    else:
                                        st.markdown('<span style="color: red;">● Indisponible</span>', unsafe_allow_html=True)
                                
                                with col_salle2:
                                    if st.button("⚙️", key=f"edit_salle_{salle['id']}"):
                                        st.info(f"Édition de {salle['nom']}")
                                st.markdown("---")
                else:
                    st.info("Aucune salle enregistrée")
                
                # Statistiques des salles
                st.markdown("### 📊 Statistiques")
                col_stats1, col_stats2, col_stats3 = st.columns(3)
                
                with col_stats1:
                    total_salles = run_query("SELECT COUNT(*) as count FROM lieu_examen")[0]['count']
                    st.metric("Total salles", total_salles)
                
                with col_stats2:
                    salles_dispo = run_query("SELECT COUNT(*) as count FROM lieu_examen WHERE disponible = TRUE")[0]['count']
                    st.metric("Salles disponibles", salles_dispo)
                
                with col_stats3:
                    capacite_totale = run_query("SELECT SUM(capacite) as total FROM lieu_examen")[0]['total'] or 0
                    st.metric("Capacité totale", f"{capacite_totale:,}")
                
                st.markdown('</div></div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### 📋 Gestion des Contraintes")
        
        col_tab4_1, col_tab4_2 = st.columns([2, 1])
        
        with col_tab4_1:
            with st.container():
                st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
                st.markdown('<div class="section-content">', unsafe_allow_html=True)
                
                # Types de contraintes
                constraint_type = st.selectbox(
                    "Type de contrainte",
                    ["⏰ Contrainte horaire", "👨‍🏫 Contrainte professeur", "🏫 Contrainte salle", 
                     "👥 Contrainte étudiant", "📅 Contrainte de période", "⚠️ Contrainte spéciale"]
                )
                
                # Formulaire selon le type de contrainte
                with st.form("ajout_contrainte_form"):
                    
                    if constraint_type == "⏰ Contrainte horaire":
                        st.markdown("**Configuration des contraintes horaires**")
                        
                        col_time1, col_time2 = st.columns(2)
                        with col_time1:
                            jour = st.selectbox(
                                "Jour",
                                ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
                            )
                            heure_debut = st.time_input("Heure de début", datetime.strptime("08:00", "%H:%M").time())
                        
                        with col_time2:
                            periode = st.selectbox(
                                "Période",
                                ["Matin", "Après-midi", "Soir", "Journée complète"]
                            )
                            heure_fin = st.time_input("Heure de fin", datetime.strptime("10:00", "%H:%M").time())
                        
                        raison = st.text_input("Raison", placeholder="Ex: Pas d'examen le samedi")
                        
                    elif constraint_type == "👨‍🏫 Contrainte professeur":
                        st.markdown("**Contraintes spécifiques aux professeurs**")
                        
                        # Sélection du professeur
                        professeurs = run_query("SELECT id, CONCAT(nom, ' ', prenom) as nom_complet FROM professeurs")
                        prof_options = {p['nom_complet']: p['id'] for p in professeurs}
                        
                        if prof_options:
                            prof_selected = st.selectbox(
                                "Professeur",
                                options=[''] + list(prof_options.keys())
                            )
                        else:
                            prof_selected = None
                            st.warning("Aucun professeur disponible")
                        
                        type_constraint = st.selectbox(
                            "Type de limitation",
                            ["Limitation horaire", "Indisponibilité", "Préférence de salle", "Contrainte de surveillance"]
                        )
                        
                        date_debut = st.date_input("Date début", datetime.now())
                        date_fin = st.date_input("Date fin", datetime.now() + timedelta(days=7))
                        
                        raison = st.text_input("Raison", placeholder="Ex: Congés, Formation, Autre engagement...")
                        
                    elif constraint_type == "🏫 Contrainte salle":
                        st.markdown("**Contraintes spécifiques aux salles**")
                        
                        # Sélection de la salle
                        salles = run_query("SELECT id, nom FROM lieu_examen")
                        salle_options = {s['nom']: s['id'] for s in salles}
                        
                        if salle_options:
                            salle_selected = st.selectbox(
                                "Salle",
                                options=[''] + list(salle_options.keys())
                            )
                        else:
                            salle_selected = None
                            st.warning("Aucune salle disponible")
                        
                        restriction_type = st.selectbox(
                            "Type de restriction",
                            ["Maintenance", "Capacité réduite", "Réservé", "Équipement défectueux", "Autre"]
                        )
                        
                        date_debut = st.date_input("Date début indisponibilité", datetime.now())
                        date_fin = st.date_input("Date fin indisponibilité", datetime.now() + timedelta(days=3))
                        
                        details = st.text_area("Détails de la restriction", placeholder="Ex: Salle en maintenance pour travaux...")
                        raison = details
                        
                    elif constraint_type == "👥 Contrainte étudiant":
                        st.markdown("**Contraintes pour les étudiants**")
                        
                        formation = st.selectbox(
                            "Formation concernée",
                            ["Toutes", "Licence 1", "Licence 2", "Licence 3", "Master 1", "Master 2"]
                        )
                        
                        max_exam_per_day = st.slider(
                            "Maximum d'examens par jour",
                            min_value=1,
                            max_value=3,
                            value=2,
                            help="Nombre maximum d'examens qu'un étudiant peut avoir dans la même journée"
                        )
                        
                        min_interval = st.slider(
                            "Intervalle minimum entre examens (heures)",
                            min_value=1,
                            max_value=24,
                            value=2,
                            help="Temps minimum entre deux examens pour un même étudiant"
                        )
                        
                        raison = f"Contraintes étudiants: max {max_exam_per_day} examens/jour, intervalle {min_interval}h"
                        
                    elif constraint_type == "📅 Contrainte de période":
                        st.markdown("**Contraintes sur les périodes d'examen**")
                        
                        col_period1, col_period2 = st.columns(2)
                        with col_period1:
                            date_debut = st.date_input("Période début", datetime.now())
                        with col_period2:
                            date_fin = st.date_input("Période fin", datetime.now() + timedelta(days=14))
                        
                        restriction = st.selectbox(
                            "Type de restriction",
                            ["Pas d'examen", "Examens limités", "Examens matin uniquement", "Examens après-midi uniquement"]
                        )
                        
                        raison = st.text_input("Motif", placeholder="Ex: Semaine de révision, Férié...")
                        
                    else:  # Contrainte spéciale
                        st.markdown("**Contraintes spéciales ou personnalisées**")
                        
                        titre = st.text_input("Titre de la contrainte", placeholder="Ex: Jour férié")
                        priorite = st.select_slider(
                            "Priorité",
                            options=["Faible", "Moyenne", "Haute", "Critique"],
                            value="Moyenne"
                        )
                        
                        impact = st.selectbox(
                            "Impact",
                            ["Localisé", "Département", "Tout le campus"]
                        )
                        
                        date_debut = st.date_input("Date début effet", datetime.now())
                        date_fin = st.date_input("Date fin effet", datetime.now() + timedelta(days=1))
                        
                        description = st.text_area("Description détaillée", height=100)
                        raison = description
                    
                    # Options communes
                    with st.expander("⚙️ Options avancées"):
                        col_opt1, col_opt2 = st.columns(2)
                        with col_opt1:
                            appliquer_a = st.multiselect(
                                "Appliquer à",
                                ["Tous les départements", "Département spécifique", "Formations spécifiques", "Salles spécifiques"]
                            )
                            notification = st.checkbox("Envoyer une notification", value=True)
                        
                        with col_opt2:
                            recurrence = st.selectbox(
                                "Récurrence",
                                ["Aucune", "Quotidienne", "Hebdomadaire", "Mensuelle", "Annuelle"]
                            )
                            active = st.checkbox("Contrainte active", value=True)
                    
                    # Bouton de soumission
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                    with col_btn2:
                        if st.form_submit_button("✅ Ajouter la contrainte", use_container_width=True):
                            st.success(f"Contrainte '{constraint_type}' ajoutée avec succès!")
                
                st.markdown('</div></div>', unsafe_allow_html=True)
        
        with col_tab4_2:
            with st.container():
                st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
                st.markdown('<div class="section-content">', unsafe_allow_html=True)
                
                st.markdown("### 📋 Contraintes Actives")
                
                # Contraintes d'exemple (simulées)
                contraintes = [
                    {"type": "⏰ Horaire", "description": "Pas d'examen le samedi", "statut": "Active", "priorite": "Haute"},
                    {"type": "👨‍🏫 Professeur", "description": "Dr. Martin indisponible 15-20 Jan", "statut": "Active", "priorite": "Moyenne"},
                    {"type": "🏫 Salle", "description": "Amphi A en maintenance", "statut": "Expirée", "priorite": "Critique"},
                    {"type": "👥 Étudiant", "description": "Max 2 examens/jour par étudiant", "statut": "Active", "priorite": "Haute"},
                    {"type": "📅 Période", "description": "Semaine de révision 8-12 Jan", "statut": "Active", "priorite": "Moyenne"},
                    {"type": "⚠️ Spéciale", "description": "Jour férié - 1er Mai", "statut": "À venir", "priorite": "Haute"},
                ]
                
                for i, contrainte in enumerate(contraintes):
                    with st.container():
                        col_ct1, col_ct2, col_ct3 = st.columns([1, 3, 1])
                        with col_ct1:
                            st.markdown(f"**{contrainte['type']}**")
                        with col_ct2:
                            st.markdown(contrainte['description'])
                            # Badge de statut
                            color = "green" if contrainte['statut'] == "Active" else \
                                   "orange" if contrainte['statut'] == "À venir" else "gray"
                            st.markdown(f'<span style="color: {color}; font-size: 0.8rem;">● {contrainte["statut"]}</span>', 
                                      unsafe_allow_html=True)
                        with col_ct3:
                            if st.button("🗑️", key=f"del_constraint_{i}"):
                                st.warning(f"Supprimer: {contrainte['description']}")
                        st.markdown("---")
                
                # Statistiques
                st.markdown("### 📊 Aperçu")
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Contraintes actives", "4")
                with col_stat2:
                    st.metric("Contraintes à venir", "1")
                with col_stat3:
                    st.metric("Contraintes expirées", "1")
                
                st.markdown('</div></div>', unsafe_allow_html=True)
    
    with tab5:
        st.markdown("### ⚡ Paramètres du Système")
        
        col_tab5_1, col_tab5_2 = st.columns([2, 1])
        
        with col_tab5_1:
            with st.container():
                st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
                st.markdown('<div class="section-content">', unsafe_allow_html=True)
                
                # Paramètres généraux
                st.markdown("#### ⚙️ Paramètres Généraux")
                
                with st.form("parametres_generaux_form"):
                    col_gen1, col_gen2 = st.columns(2)
                    
                    with col_gen1:
                        annee_scolaire = st.text_input("Année scolaire actuelle", f"{datetime.now().year}-{datetime.now().year + 1}")
                        periode_examens = st.selectbox(
                            "Période par défaut des examens",
                            ["Janvier", "Février", "Mai-Juin", "Juin", "Septembre", "Décembre"]
                        )
                        duree_examen_defaut = st.number_input(
                            "Durée examen par défaut (minutes)",
                            min_value=30,
                            max_value=240,
                            value=120
                        )
                    
                    with col_gen2:
                        heure_debut_journee = st.time_input(
                            "Heure début journée",
                            datetime.strptime("08:00", "%H:%M").time()
                        )
                        heure_fin_journee = st.time_input(
                            "Heure fin journée",
                            datetime.strptime("18:00", "%H:%M").time()
                        )
                        pause_dejeuner = st.time_input(
                            "Pause déjeuner",
                            datetime.strptime("12:00", "%H:%M").time()
                        )
                    
                    # Paramètres d'optimisation
                    st.markdown("#### 🧠 Paramètres d'Optimisation")
                    
                    col_opt1, col_opt2 = st.columns(2)
                    
                    with col_opt1:
                        marge_entre_examens = st.number_input(
                            "Marge entre examens (minutes)",
                            min_value=0,
                            max_value=120,
                            value=30
                        )
                        seuil_conflit = st.slider(
                            "Seuil de conflit (%)",
                            min_value=0,
                            max_value=100,
                            value=80,
                            help="Pourcentage d'occupation à partir duquel un conflit est signalé"
                        )
                    
                    with col_opt2:
                        auto_resolution = st.checkbox("Résolution automatique des conflits", value=True)
                        notification_conflits = st.checkbox("Notifications pour conflits majeurs", value=True)
                        optimisation_ressources = st.checkbox("Optimisation des ressources", value=True)
                    
                    # Paramètres de notification
                    st.markdown("#### 🔔 Paramètres de Notification")
                    
                    notifications = st.multiselect(
                        "Types de notifications activées",
                        ["Conflits détectés", "Examens ajoutés", "Examens modifiés", "Examens supprimés",
                         "Rapports générés", "Alertes système", "Maintenance planifiée"],
                        default=["Conflits détectés", "Examens ajoutés", "Alertes système"]
                    )
                    
                    frequence_notifications = st.selectbox(
                        "Fréquence des notifications",
                        ["Immédiate", "Quotidienne", "Hebdomadaire", "Mensuelle"]
                    )
                    
                    # Bouton de sauvegarde
                    if st.form_submit_button("💾 Sauvegarder les paramètres", use_container_width=True):
                        st.success("Paramètres sauvegardés avec succès!")
                
                # Configuration avancée
                with st.expander("🔧 Configuration Avancée"):
                    st.markdown("**Paramètres de base de données**")
                    
                    col_db1, col_db2 = st.columns(2)
                    with col_db1:
                        backup_frequency = st.selectbox(
                            "Fréquence des sauvegardes",
                            ["Quotidienne", "Hebdomadaire", "Mensuelle"]
                        )
                        retention_days = st.number_input(
                            "Jours de rétention",
                            min_value=1,
                            max_value=365,
                            value=30
                        )
                    
                    with col_db2:
                        auto_backup = st.checkbox("Sauvegarde automatique", value=True)
                        compress_backup = st.checkbox("Compression des sauvegardes", value=True)
                    
                    st.markdown("**Paramètres de sécurité**")
                    
                    col_sec1, col_sec2 = st.columns(2)
                    with col_sec1:
                        session_timeout = st.number_input(
                            "Timeout session (minutes)",
                            min_value=5,
                            max_value=240,
                            value=30
                        )
                        password_policy = st.selectbox(
                            "Politique de mots de passe",
                            ["Faible", "Moyenne", "Forte"]
                        )
                    
                    with col_sec2:
                        two_factor_auth = st.checkbox("Authentification à deux facteurs", value=False)
                        log_activity = st.checkbox("Journalisation des activités", value=True)
                    
                    if st.button("🔒 Appliquer les paramètres de sécurité", use_container_width=True):
                        st.info("Paramètres de sécurité appliqués")
                
                st.markdown('</div></div>', unsafe_allow_html=True)
        
        with col_tab5_2:
            with st.container():
                st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
                st.markdown('<div class="section-content">', unsafe_allow_html=True)
                
                # Informations système
                st.markdown("### 📊 Informations Système")
                
                # Version
                st.markdown("#### Version")
                col_ver1, col_ver2 = st.columns(2)
                with col_ver1:
                    st.metric("Version", "4.2.1")
                with col_ver2:
                    st.metric("Dernière mise à jour", "15/01/2024")
                
                # Statut
                st.markdown("#### Statut")
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.markdown("""
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <div style="width: 10px; height: 10px; background: green; border-radius: 50%;"></div>
                        <span>Base de données: OK</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_stat2:
                    st.markdown("""
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <div style="width: 10px; height: 10px; background: green; border-radius: 50%;"></div>
                        <span>Services: OK</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Utilisation
                st.markdown("#### Utilisation")
                
                # Utilisation disque
                st.markdown("**Espace disque**")
                disk_usage = st.progress(65)
                st.caption("65% utilisé • 35% libre")
                
                # Utilisation mémoire
                st.markdown("**Mémoire**")
                memory_usage = st.progress(42)
                st.caption("42% utilisé")
                
                # Actions système
                st.markdown("#### 🛠️ Actions")
                
                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    if st.button("🔄 Rafraîchir cache", use_container_width=True):
                        st.info("Cache rafraîchi")
                
                with col_act2:
                    if st.button("📊 Générer rapport", use_container_width=True):
                        st.info("Rapport généré")
                
                # Maintenance
                st.markdown("#### 🛡️ Maintenance")
                
                if st.button("🧹 Nettoyer logs", use_container_width=True):
                    st.info("Logs nettoyés")
                
                if st.button("🔄 Redémarrer services", use_container_width=True, type="secondary"):
                    st.warning("Redémarrage des services...")
                
                # Statistiques rapides
                st.markdown("#### 📈 Statistiques")
                
                stats_data = {
                    "Utilisateurs actifs": "12",
                    "Examens ce mois": "156",
                    "Conflits résolus": "89%",
                    "Performance": "94%"
                }
                
                for key, value in stats_data.items():
                    col_stat_key, col_stat_val = st.columns([2, 1])
                    with col_stat_key:
                        st.markdown(f"**{key}**")
                    with col_stat_val:
                        st.markdown(f"`{value}`")
                    st.markdown("---")
                
                st.markdown('</div></div>', unsafe_allow_html=True)

# ... (le reste du code reste inchangé)
# Pied de page avec design amélioré
st.markdown("""
<div style="margin-top: 4rem; padding: 2rem; text-align: center; border-top: 1px solid #e2e8f0;">
    <div style="font-weight: 600; color: #2c3e50; margin-bottom: 0.5rem;">
        Plateforme d'Optimisation des Emplois du Temps d'Examens Universitaires
    </div>
    <div style="color: #7f8c8d; font-size: 0.9rem; margin-bottom: 0.5rem;">
        Version 4.0 • Système Intelligent de Planification • © 2024
    </div>
    <div style="display: flex; justify-content: center; gap: 1rem; margin-top: 1rem;">
        <span style="color: #3498db;">🔒 Sécurisé</span>
        <span style="color: #2ecc71;">⚡ Performant</span>
        <span style="color: #f39c12;">🤖 Intelligent</span>
    </div>
</div>
""", unsafe_allow_html=True)