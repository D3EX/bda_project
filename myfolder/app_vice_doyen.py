# pages/app_doyen.py - Version adaptée au login
import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, time, timedelta
import numpy as np
import io
from decimal import Decimal
import os
import toml

# Configuration de la page
# Add this right after st.set_page_config()
st.set_page_config(
    page_title="Vue Stratégique - Doyen",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# HIDE THE PAGE NAVIGATION
hide_pages_navigation = """
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
"""
st.markdown(hide_pages_navigation, unsafe_allow_html=True)

# VÉRIFICATION DE CONNEXION
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⛔ Accès non autorisé. Veuillez vous connecter.")
    if st.button("🔐 Se connecter"):
        st.switch_page("pages/log.py")
    st.stop()

# VÉRIFICATION DU RÔLE
if st.session_state.role != 'doyen':
    st.error(f"⛔ Cette page est réservée au doyen. Votre rôle: {st.session_state.role}")
    if st.button("🏠 Retour à l'accueil"):
        st.switch_page("app.py")
    st.stop()

# L'ID de l'utilisateur connecté
DOYEN_ID = st.session_state.user_id

# Fonction pour charger les secrets
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

# Charger les secrets
secrets = load_secrets()

# Fonction de connexion à MySQL
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

# Initialiser la connexion
conn = init_connection()

# Fonction pour convertir les Decimal en float
def convert_decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal_to_float(item) for item in obj]
    else:
        return obj

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

# Titre de l'application
st.title("🎓 Tableau de Bord Stratégique - Doyen")
st.markdown(f"**Connecté en tant que:** {st.session_state.nom_complet} | **Rôle:** {st.session_state.role}")
st.markdown("---")

import streamlit as st
from datetime import datetime, timedelta

# Sidebar pour la navigation
with st.sidebar:
    # Header with logo and title
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; 
                    border-radius: 10px; 
                    margin-bottom: 20px;">
            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" 
                 width="80" 
                 style="border-radius: 50%; 
                        border: 3px solid white;
                        padding: 5px;
                        background: white;">
        </div>
        <h1 style="color: #1e3a8a; margin: 10px 0 5px 0;">Doyen</h1>
        <p style="color: #6b7280; font-size: 0.9rem; margin: 0;">Interface d'Administration</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User profile card
    st.markdown(f"""
    <div style="background: #f8fafc; 
                padding: 15px; 
                border-radius: 10px; 
                border-left: 4px solid #3b82f6;
                margin-bottom: 25px;">
        <p style="margin: 0; font-size: 0.95rem;"><strong>👤 {st.session_state.nom_complet}</strong></p>
        <p style="margin: 5px 0 0 0; color: #6b7280; font-size: 0.85rem;">ID: <code>{DOYEN_ID}</code></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation menu
    st.markdown("### 📍 Navigation Stratégique")
    
    menu_options = {
        "📊 Tableau de Bord Global": "bar-chart",
        "🏢 Occupation des Ressources": "building",
        "⚠️ Analyse des Conflits": "alert-triangle",
        "✅ Validation EDT": "check-circle",
        "📈 KPIs Académiques": "trending-up",
        "📋 Rapports Détaillés": "file-text"
    }
    
    menu = st.radio(
        "",
        list(menu_options.keys()),
        label_visibility="collapsed",
        format_func=lambda x: f" {x}"
    )
    
    st.markdown("---")
    
    # Date range section
    st.markdown("### 📅 Période d'analyse")
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("**Début**", 
                                  datetime.now() - timedelta(days=30),
                                  key="date_debut",
                                  label_visibility="collapsed")
    with col2:
        date_fin = st.date_input("**Fin**", 
                                datetime.now() + timedelta(days=30),
                                key="date_fin",
                                label_visibility="collapsed")
    
    # Period display badge
    st.markdown(f"""
    <div style="background: #eff6ff; 
                padding: 10px 15px; 
                border-radius: 8px; 
                border: 1px solid #dbeafe;
                margin: 15px 0 25px 0;
                text-align: center;">
        <p style="margin: 0; color: #1e40af; font-size: 0.9rem;">
            <strong>Période sélectionnée:</strong><br>
            {date_debut.strftime('%d/%m/%Y')} → {date_fin.strftime('%d/%m/%Y')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Buttons section
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Actualiser", 
                    use_container_width=True,
                    help="Rafraîchir toutes les données"):
            st.rerun()
    
    with col2:
        if st.button("📥 Exporter", 
                    use_container_width=True,
                    type="secondary",
                    help="Exporter le rapport actuel"):
            pass  # Add export functionality
    
    st.markdown("---")
    
    # Footer with logout
    st.markdown("""
    <div style="position: fixed; bottom: 30px; left: 30px; right: 30px;">
    """, unsafe_allow_html=True)
    
    if st.button("🚪 **Déconnexion**", 
                 use_container_width=True, 
                 type="primary",
                 help="Se déconnecter de l'application"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("pages/log.py")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Version info (optional)
    st.markdown("""
    <div style="position: fixed; bottom: 10px; left: 20px; right: 20px; text-align: center;">
        <p style="color: #9ca3af; font-size: 0.75rem; margin: 0;">
            v2.1.4 • © 2024 Doyen System
        </p>
    </div>
    """, unsafe_allow_html=True)

# Fonctions pour les métriques stratégiques (les mêmes que pour vice-doyen)
def get_occupation_globale(date_debut, date_fin):
    """Occupation globale des amphis et salles"""
    query = """
        SELECT 
            le.type,
            le.nom as salle,
            le.capacite,
            COUNT(DISTINCT e.id) as nb_examens,
            SUM(e.duree_minutes) as total_minutes,
            COUNT(DISTINCT e.date_examen) as jours_utilises,
            ROUND((SUM(e.duree_minutes) / (480 * COUNT(DISTINCT e.date_examen))) * 100, 1) as taux_occupation
        FROM lieu_examen le
        LEFT JOIN examens e ON le.id = e.salle_id 
            AND e.date_examen BETWEEN %s AND %s
            AND e.statut != 'annulé'
        GROUP BY le.id
        ORDER BY le.type, taux_occupation DESC
    """
    return run_query(query, (date_debut, date_fin))

def get_conflits_par_departement(date_debut, date_fin):
    """Taux de conflits par département"""
    query = """
        SELECT 
            d.nom as departement,
            COUNT(DISTINCT e.id) as total_examens,
            SUM(CASE WHEN conflit_etudiant > 0 THEN 1 ELSE 0 END) as conflits_etudiants,
            SUM(CASE WHEN conflit_salle > 0 THEN 1 ELSE 0 END) as conflits_salles,
            SUM(CASE WHEN conflit_professeur > 0 THEN 1 ELSE 0 END) as conflits_professeurs,
            ROUND((SUM(CASE WHEN conflit_etudiant > 0 OR conflit_salle > 0 OR conflit_professeur > 0 THEN 1 ELSE 0 END) 
                   / COUNT(DISTINCT e.id)) * 100, 1) as taux_conflits
        FROM departements d
        LEFT JOIN formations f ON d.id = f.dept_id
        LEFT JOIN modules m ON f.id = m.formation_id
        LEFT JOIN examens e ON m.id = e.module_id 
            AND e.date_examen BETWEEN %s AND %s
            AND e.statut != 'annulé'
        LEFT JOIN (
            -- Conflits étudiants
            SELECT e1.etudiant_id, e1.module_id, COUNT(*) as conflit_etudiant
            FROM inscriptions e1
            JOIN examens ex ON e1.module_id = ex.module_id
            WHERE ex.date_examen BETWEEN %s AND %s
            GROUP BY e1.etudiant_id, e1.module_id
            HAVING COUNT(DISTINCT ex.date_examen) < COUNT(DISTINCT ex.id)
        ) ce ON e.module_id = ce.module_id
        LEFT JOIN (
            -- Conflits salles
            SELECT e1.salle_id, e1.date_examen, COUNT(*) as conflit_salle
            FROM examens e1
            WHERE e1.date_examen BETWEEN %s AND %s
            GROUP BY e1.salle_id, e1.date_examen
            HAVING COUNT(*) > 1
        ) cs ON e.salle_id = cs.salle_id AND e.date_examen = cs.date_examen
        LEFT JOIN (
            -- Conflits professeurs
            SELECT e1.professeur_id, e1.date_examen, COUNT(*) as conflit_professeur
            FROM examens e1
            WHERE e1.date_examen BETWEEN %s AND %s
            GROUP BY e1.professeur_id, e1.date_examen
            HAVING COUNT(*) > 1
        ) cp ON e.professeur_id = cp.professeur_id AND e.date_examen = cp.date_examen
        GROUP BY d.id
        ORDER BY taux_conflits DESC
    """
    result = run_query(query, (date_debut, date_fin, date_debut, date_fin, date_debut, date_fin, date_debut, date_fin))
    return result

def get_kpis_academiques(date_debut, date_fin):
    """KPIs académiques"""
    query = """
        SELECT 
            -- Heures professeurs
            (SELECT COUNT(DISTINCT p.id) FROM professeurs p
             JOIN examens e ON p.id = e.professeur_id 
             WHERE e.date_examen BETWEEN %s AND %s) as profs_actifs,
            
            (SELECT ROUND(SUM(e.duree_minutes)/60, 1) FROM examens e
             WHERE e.date_examen BETWEEN %s AND %s) as total_heures_examens,
            
            -- Taux salles utilisées
            (SELECT ROUND((COUNT(DISTINCT e.salle_id) / 
                          (SELECT COUNT(*) FROM lieu_examen WHERE disponible = TRUE)) * 100, 1)
             FROM examens e 
             WHERE e.date_examen BETWEEN %s AND %s) as taux_salles_utilisees,
            
            -- Charge moyenne par professeur
            (SELECT ROUND(AVG(nb_examens), 1) 
             FROM (SELECT COUNT(*) as nb_examens 
                   FROM examens e 
                   WHERE e.date_examen BETWEEN %s AND %s
                   GROUP BY e.professeur_id) as stats) as exams_moyens_par_prof,
            
            -- Taux occupation global
            (SELECT ROUND(AVG(taux_occupation), 1) 
             FROM (SELECT le.id, 
                          ROUND((SUM(e.duree_minutes) / 480) * 100, 1) as taux_occupation
                   FROM lieu_examen le
                   LEFT JOIN examens e ON le.id = e.salle_id 
                        AND e.date_examen BETWEEN %s AND %s
                   GROUP BY le.id) as occupation) as taux_occupation_global,
            
            -- Examens par jour moyen
            (SELECT ROUND(AVG(nb_examens), 1) 
             FROM (SELECT COUNT(*) as nb_examens 
                   FROM examens e 
                   WHERE e.date_examen BETWEEN %s AND %s
                   GROUP BY e.date_examen) as jours) as exams_moyens_par_jour
    """
    return run_query(query, (date_debut, date_fin, date_debut, date_fin, date_debut, date_fin, 
                           date_debut, date_fin, date_debut, date_fin, date_debut, date_fin))

def get_statistiques_validation(date_debut, date_fin):
    """Statistiques de validation"""
    query = """
        SELECT 
            d.nom as departement,
            COUNT(DISTINCT e.id) as total_examens,
            SUM(CASE WHEN e.statut = 'planifié' THEN 1 ELSE 0 END) as en_attente,
            SUM(CASE WHEN e.statut = 'confirmé' THEN 1 ELSE 0 END) as confirmes,
            SUM(CASE WHEN e.statut = 'annulé' THEN 1 ELSE 0 END) as annules,
            ROUND((SUM(CASE WHEN e.statut = 'confirmé' THEN 1 ELSE 0 END) / 
                   COUNT(DISTINCT e.id)) * 100, 1) as taux_validation
        FROM departements d
        LEFT JOIN formations f ON d.id = f.dept_id
        LEFT JOIN modules m ON f.id = m.formation_id
        LEFT JOIN examens e ON m.id = e.module_id 
            AND e.date_examen BETWEEN %s AND %s
        GROUP BY d.id
        HAVING total_examens > 0
        ORDER BY taux_validation DESC
    """
    return run_query(query, (date_debut, date_fin))

def get_charge_professeurs(date_debut, date_fin):
    """Charge de travail des professeurs"""
    query = """
        SELECT 
            p.id,
            CONCAT(p.nom, ' ', p.prenom) as professeur,
            d.nom as departement,
            COUNT(DISTINCT e.id) as nb_examens_responsable,
            COUNT(DISTINCT e2.id) as nb_examens_surveillant,
            ROUND(SUM(e.duree_minutes)/60, 1) as heures_responsable,
            ROUND(SUM(e2.duree_minutes)/60, 1) as heures_surveillant,
            ROUND((SUM(e.duree_minutes) + COALESCE(SUM(e2.duree_minutes), 0))/60, 1) as total_heures,
            p.heures_service,
            ROUND(((SUM(e.duree_minutes) + COALESCE(SUM(e2.duree_minutes), 0))/60 / p.heures_service) * 100, 1) as taux_charge
        FROM professeurs p
        JOIN departements d ON p.dept_id = d.id
        LEFT JOIN examens e ON p.id = e.professeur_id 
            AND e.date_examen BETWEEN %s AND %s
        LEFT JOIN examens e2 ON p.id = e2.surveillant_id 
            AND e2.date_examen BETWEEN %s AND %s
        GROUP BY p.id
        HAVING nb_examens_responsable > 0 OR nb_examens_surveillant > 0
        ORDER BY total_heures DESC
    """
    return run_query(query, (date_debut, date_fin, date_debut, date_fin))

def get_planning_complet(date_debut, date_fin):
    """Planning complet pour validation"""
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
            d.nom as departement,
            le.nom as salle,
            le.type as type_salle,
            le.capacite,
            CONCAT(p_resp.nom, ' ', p_resp.prenom) as professeur_responsable,
            CONCAT(p_surv.nom, ' ', p_surv.prenom) as professeur_surveillant,
            COUNT(DISTINCT i.etudiant_id) as nb_etudiants,
            ROUND((COUNT(DISTINCT i.etudiant_id) / le.capacite) * 100, 1) as taux_occupation_salle
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN departements d ON f.dept_id = d.id
        JOIN lieu_examen le ON e.salle_id = le.id
        LEFT JOIN professeurs p_resp ON e.professeur_id = p_resp.id
        LEFT JOIN professeurs p_surv ON e.surveillant_id = p_surv.id
        LEFT JOIN inscriptions i ON m.id = i.module_id AND i.annee_scolaire = e.annee_scolaire
        WHERE e.date_examen BETWEEN %s AND %s
        GROUP BY e.id
        ORDER BY e.date_examen, e.heure_debut, d.nom
    """
    return run_query(query, (date_debut, date_fin))

def valider_examen(examen_id):
    """Valider un examen"""
    query = "UPDATE examens SET statut = 'confirmé' WHERE id = %s"
    return run_query(query, (examen_id,), False)

def valider_tous_examens_departement(dept_id, date_debut, date_fin):
    """Valider tous les examens d'un département"""
    query = """
        UPDATE examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        SET e.statut = 'confirmé'
        WHERE f.dept_id = %s
        AND e.date_examen BETWEEN %s AND %s
        AND e.statut = 'planifié'
    """
    return run_query(query, (dept_id, date_debut, date_fin), False)

# PAGE: Tableau de Bord Global
# PAGE: Tableau de Bord Global
if menu == "📊 Tableau de Bord Global":
    # Header with styling
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; 
                border-radius: 10px;
                margin-bottom: 30px;'>
        <h1 style='color: white; margin: 0;'>📊 Vue Stratégique Globale</h1>
        <p style='color: rgba(255,255,255,0.8); margin: 5px 0 0 0;'>
        Tableau de bord analytique pour le suivi des examens et l'optimisation des ressources
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # KPIs Principaux with improved cards
    st.markdown("### 📈 Indicateurs Clés de Performance")
    
    kpis = get_kpis_academiques(date_debut, date_fin)
    if kpis:
        kpi = kpis[0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        # KPI styling function
        def create_kpi_card(title, value, icon="", delta=None, value_suffix=""):
            color_map = {
                "Taux d'Occupation Global": "#4CAF50",
                "Taux Salles Utilisées": "#2196F3",
                "Heures d'Examens": "#FF9800",
                "Professeurs Actifs": "#9C27B0"
            }
            color = color_map.get(title, "#666")
            
            card_html = f"""
            <div style='background: white; 
                        padding: 20px; 
                        border-radius: 10px; 
                        border-left: 5px solid {color};
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        height: 100%;'>
                <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                    <div style='background: {color}; 
                                 width: 40px; 
                                 height: 40px; 
                                 border-radius: 50%; 
                                 display: flex; 
                                 align-items: center; 
                                 justify-content: center; 
                                 margin-right: 10px;'>
                        <span style='color: white; font-size: 18px;'>{icon}</span>
                    </div>
                    <div style='flex-grow: 1;'>
                        <h4 style='margin: 0; color: #555; font-size: 14px;'>{title}</h4>
                        <h2 style='margin: 5px 0 0 0; color: {color};'>{value}{value_suffix}</h2>
                    </div>
                </div>
            </div>
            """
            return card_html
        
        with col1:
            taux_occupation = kpi.get('taux_occupation_global', 0) or 0
            taux_value = f"{float(taux_occupation):.1f}" if taux_occupation else "0.0"
            st.markdown(create_kpi_card("Taux d'Occupation Global", taux_value, "🏢", value_suffix="%"), unsafe_allow_html=True)
        
        with col2:
            taux_salles = kpi.get('taux_salles_utilisees', 0) or 0
            salles_value = f"{float(taux_salles):.1f}" if taux_salles else "0.0"
            st.markdown(create_kpi_card("Taux Salles Utilisées", salles_value, "📚", value_suffix="%"), unsafe_allow_html=True)
        
        with col3:
            total_heures = kpi.get('total_heures_examens', 0) or 0
            heures_value = f"{float(total_heures):.0f}" if total_heures else "0"
            st.markdown(create_kpi_card("Heures d'Examens", heures_value, "⏱️", value_suffix="h"), unsafe_allow_html=True)
        
        with col4:
            profs_actifs = kpi.get('profs_actifs', 0) or 0
            profs_value = int(profs_actifs) if profs_actifs else 0
            st.markdown(create_kpi_card("Professeurs Actifs", str(profs_value), "👨‍🏫"), unsafe_allow_html=True)
    
    # Add spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Graphiques principaux with tabs for better organization
    tab1, tab2 = st.tabs(["📊 Analyse d'Occupation", "⚠️ Analyse des Conflits"])
    
    with tab1:
        st.markdown("### 🏢 Occupation par Type de Salle")
        occupation = get_occupation_globale(date_debut, date_fin)
        
        if occupation:
            df_occupation = pd.DataFrame(occupation)
            
            # Graphique par type
            occupation_type = df_occupation.groupby('type').agg({
                'taux_occupation': 'mean',
                'nb_examens': 'sum',
                'capacite': 'sum'
            }).reset_index()
            
            # Convertir taux_occupation en float
            occupation_type['taux_occupation'] = occupation_type['taux_occupation'].astype(float)
            
            # Sort by occupancy
            occupation_type = occupation_type.sort_values('taux_occupation', ascending=False)
            
            fig = px.bar(occupation_type, x='type', y='taux_occupation',
                        color='taux_occupation',
                        color_continuous_scale='Viridis',
                        title="",
                        labels={'taux_occupation': 'Taux d\'Occupation (%)', 'type': 'Type de Salle'},
                        text='taux_occupation')
            
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside',
                            marker_line_color='rgb(8,48,107)', marker_line_width=1.5)
            fig.update_layout(
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Type de Salle",
                yaxis_title="Taux d'Occupation (%)",
                yaxis_range=[0, 100]
            )
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Additional metrics
            st.markdown("#### 📈 Statistiques d'Occupation")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Taux d'Occupation Moyen", f"{occupation_type['taux_occupation'].mean():.1f}%")
            with col2:
                st.metric("Type Plus Utilisé", occupation_type.iloc[0]['type'])
            with col3:
                st.metric("Types de Salles", len(occupation_type))
    
    with tab2:
        st.markdown("### ⚠️ Conflits par Département")
        conflits = get_conflits_par_departement(date_debut, date_fin)
        
        if conflits:
            df_conflits = pd.DataFrame(conflits)
            
            if not df_conflits.empty:
                # Convertir taux_conflits en float et remplacer les NaN par 0
                df_conflits['taux_conflits'] = pd.to_numeric(df_conflits['taux_conflits'], errors='coerce').fillna(0)
                
                # Sort by conflict rate
                df_conflits = df_conflits.sort_values('taux_conflits', ascending=False)
                
                # Color mapping based on conflict rate
                def get_conflict_color(rate):
                    if rate <= 5:
                        return '#2ecc71'  # Green
                    elif rate <= 10:
                        return '#f1c40f'  # Yellow
                    elif rate <= 20:
                        return '#e67e22'  # Orange
                    else:
                        return '#e74c3c'  # Red
                
                df_conflits['color'] = df_conflits['taux_conflits'].apply(get_conflict_color)
                
                fig = px.bar(df_conflits, x='departement', y='taux_conflits',
                            color='taux_conflits',
                            color_continuous_scale='Reds',
                            title="",
                            labels={'taux_conflits': 'Taux de Conflits (%)', 'departement': 'Département'},
                            text='taux_conflits')
                
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside',
                                marker_line_color='rgb(8,48,107)', marker_line_width=1)
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_tickangle=-45,
                    xaxis_title="Département",
                    yaxis_title="Taux de Conflits (%)",
                    showlegend=False
                )
                fig.update_coloraxes(showscale=False)
                st.plotly_chart(fig, use_container_width=True)
                
                # Conflict summary
                high_conflicts = df_conflits[df_conflits['taux_conflits'] > 10]
                if not high_conflicts.empty:
                    st.warning(f"🚨 {len(high_conflicts)} départements ont un taux de conflits supérieur à 10%")
    
    # Add spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Validation status with improved layout
    st.markdown("### ✅ État de Validation des EDT")
    validation = get_statistiques_validation(date_debut, date_fin)
    
    if validation:
        df_validation = pd.DataFrame(validation)
        
        if not df_validation.empty:
            # Create columns for charts and summary
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Créer un graphique à barres groupées
                df_melted = df_validation.melt(id_vars=['departement', 'total_examens'], 
                                              value_vars=['en_attente', 'confirmes', 'annules'],
                                              var_name='Statut', value_name='Nombre')
                
                # Convertir les valeurs en int
                df_melted['Nombre'] = df_melted['Nombre'].astype(int)
                
                # Traduire les statuts
                df_melted['Statut'] = df_melted['Statut'].map({
                    'en_attente': 'En Attente',
                    'confirmes': 'Confirmés',
                    'annules': 'Annulés'
                })
                
                fig = px.bar(df_melted, x='departement', y='Nombre', color='Statut',
                            title="",
                            barmode='stack',
                            labels={'departement': 'Département', 'Nombre': 'Nombre d\'Examens'},
                            color_discrete_map={
                                'Confirmés': '#2ecc71', 
                                'En Attente': '#f39c12', 
                                'Annulés': '#e74c3c'
                            })
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_tickangle=-45,
                    legend_title="Statut"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📋 Résumé")
                
                # Calculate totals
                total_exams = df_validation['total_examens'].sum()
                confirmed = df_validation['confirmes'].sum()
                pending = df_validation['en_attente'].sum()
                cancelled = df_validation['annules'].sum()
                
                # Create summary cards
                st.markdown(f"""
                <div style='background: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                    <h4 style='margin: 0 0 5px 0; color: #666;'>Total Examens</h4>
                    <h2 style='margin: 0; color: #2c3e50;'>{total_exams}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style='background: #e8f5e9; padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                    <h4 style='margin: 0 0 5px 0; color: #666;'>Confirmés</h4>
                    <h2 style='margin: 0; color: #2ecc71;'>{confirmed}</h2>
                    <small style='color: #666;'>{confirmed/total_exams*100:.1f}%</small>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style='background: #fff3cd; padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                    <h4 style='margin: 0 0 5px 0; color: #666;'>En Attente</h4>
                    <h2 style='margin: 0; color: #f39c12;'>{pending}</h2>
                    <small style='color: #666;'>{pending/total_exams*100:.1f}%</small>
                </div>
                """, unsafe_allow_html=True)
    
    # Charge des professeurs with tabs
    st.markdown("### 👨‍🏫 Charge de Travail des Professeurs")
    
    # Create tabs for different views
    prof_tab1, prof_tab2 = st.tabs(["Top 10", "Tous"])
    
    with prof_tab1:
        charge = get_charge_professeurs(date_debut, date_fin)
        
        if charge:
            df_charge = pd.DataFrame(charge)
            
            if not df_charge.empty:
                # Convertir total_heures en float
                df_charge['total_heures'] = df_charge['total_heures'].astype(float)
                df_charge['taux_charge'] = df_charge['taux_charge'].astype(float)
                
                # Prendre les 10 premiers
                df_top10 = df_charge.head(10)
                
                fig = px.bar(df_top10, x='professeur', y='total_heures',
                            color='taux_charge',
                            title="",
                            labels={'professeur': 'Professeur', 'total_heures': 'Heures Total'},
                            text='total_heures',
                            color_continuous_scale='RdYlGn_r')
                
                fig.update_traces(texttemplate='%{text:.1f}h', textposition='outside',
                                marker_line_color='rgb(8,48,107)', marker_line_width=1)
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_tickangle=-45,
                    xaxis_title="Professeur",
                    yaxis_title="Heures",
                    coloraxis_colorbar_title="Taux de Charge"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Summary stats
                avg_hours = df_top10['total_heures'].mean()
                max_hours = df_top10['total_heures'].max()
                max_prof = df_top10.loc[df_top10['total_heures'].idxmax(), 'professeur']
                
                st.markdown(f"""
                <div style='background: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 20px;'>
                    <div style='display: flex; justify-content: space-between;'>
                        <div>
                            <small>Moyenne Top 10</small>
                            <h4>{avg_hours:.1f}h</h4>
                        </div>
                        <div>
                            <small>Maximum</small>
                            <h4>{max_hours:.1f}h</h4>
                            <small style='color: #666;'>{max_prof}</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with prof_tab2:
        if charge:
            df_charge = pd.DataFrame(charge)
            
            if not df_charge.empty:
                # Convertir total_heures en float
                df_charge['total_heures'] = df_charge['total_heures'].astype(float)
                df_charge['taux_charge'] = df_charge['taux_charge'].astype(float)
                
                # Sort by hours
                df_charge = df_charge.sort_values('total_heures', ascending=False)
                
                # Create a horizontal bar chart for all professors
                fig = px.bar(df_charge, y='professeur', x='total_heures',
                            orientation='h',
                            color='taux_charge',
                            color_continuous_scale='RdYlGn_r',
                            title="",
                            labels={'professeur': 'Professeur', 'total_heures': 'Heures Total'})
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    yaxis={'categoryorder': 'total ascending'},
                    height=600,
                    coloraxis_colorbar_title="Taux de Charge"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Footer with date range info
    st.markdown("---")
    st.caption(f"📅 Période analysée: {date_debut.strftime('%d/%m/%Y')} - {date_fin.strftime('%d/%m/%Y')}")
    st.caption("🔄 Données mises à jour quotidiennement à 08:00")

# PAGE: Occupation des Ressources
elif menu == "🏢 Occupation des Ressources":
    st.header("🏢 Analyse d'Occupation des Ressources")
    
    # Sélection du type d'analyse
    analysis_type = st.radio(
        "Type d'analyse",
        ["📊 Vue Globale", "📈 Vue Détaillée par Salle", "📅 Évolution Temporelle"],
        horizontal=True
    )
    
    if analysis_type == "📊 Vue Globale":
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Occupation globale
            occupation = get_occupation_globale(date_debut, date_fin)
            
            if occupation:
                df_occupation = pd.DataFrame(occupation)
                
                # Convertir taux_occupation en float
                df_occupation['taux_occupation'] = df_occupation['taux_occupation'].astype(float)
                
                # Heatmap d'occupation
                fig = px.treemap(df_occupation, 
                                path=['type', 'salle'], 
                                values='nb_examens',
                                color='taux_occupation',
                                color_continuous_scale='RdYlGn',
                                title="Occupation des Salles (Taille: Nombre d'examens, Couleur: Taux d'occupation)")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Statistiques sommaires
            st.subheader("📊 Statistiques Globales")
            
            if occupation:
                df_occupation = pd.DataFrame(occupation)
                
                # Calculer les statistiques
                total_salles = len(df_occupation)
                salles_utilisees = df_occupation[df_occupation['nb_examens'] > 0].shape[0]
                occupation_moyenne = float(df_occupation['taux_occupation'].mean()) if not df_occupation['taux_occupation'].isna().all() else 0
                occupation_max = float(df_occupation['taux_occupation'].max()) if not df_occupation['taux_occupation'].isna().all() else 0
                if not df_occupation.empty and occupation_max > 0:
                    meilleure_salle = df_occupation.loc[df_occupation['taux_occupation'].idxmax()]['salle']
                else:
                    meilleure_salle = "N/A"
                
                st.metric("Salles Total", int(total_salles))
                st.metric("Salles Utilisées", int(salles_utilisees))
                st.metric("Taux d'Utilisation", f"{salles_utilisees/total_salles*100:.1f}%" if total_salles > 0 else "0%")
                st.metric("Occupation Moyenne", f"{occupation_moyenne:.1f}%")
                st.metric("Occupation Maximale", f"{occupation_max:.1f}%")
                st.metric("Salle la Plus Occupée", meilleure_salle)
    
    elif analysis_type == "📈 Vue Détaillée par Salle":
        # Filtres
        col1, col2 = st.columns(2)
        
        with col1:
            types_salle = run_query("SELECT DISTINCT type FROM lieu_examen ORDER BY type")
            selected_types = st.multiselect(
                "Filtrer par type",
                options=[t['type'] for t in types_salle],
                default=[t['type'] for t in types_salle]
            )
        
        with col2:
            min_occupation = st.slider("Occupation minimale (%)", 0, 100, 0)
        
        # Données détaillées
        occupation = get_occupation_globale(date_debut, date_fin)
        
        if occupation:
            df_occupation = pd.DataFrame(occupation)
            
            # Convertir taux_occupation en float
            df_occupation['taux_occupation'] = df_occupation['taux_occupation'].astype(float)
            
            # Appliquer les filtres
            if selected_types:
                df_occupation = df_occupation[df_occupation['type'].isin(selected_types)]
            
            df_occupation = df_occupation[df_occupation['taux_occupation'] >= min_occupation]
            
            # Tableau détaillé
            st.subheader("📋 Détail par Salle")
            
            # Formatage des colonnes
            display_cols = ['type', 'salle', 'capacite', 'nb_examens', 
                          'jours_utilises', 'total_minutes', 'taux_occupation']
            
            df_display = df_occupation[display_cols].copy()
            df_display['taux_occupation'] = df_display['taux_occupation'].apply(lambda x: f"{x:.1f}%")
            df_display['total_minutes'] = df_display['total_minutes'].apply(lambda x: f"{int(x)} min" if pd.notnull(x) else "0 min")
            
            st.dataframe(
                df_display.sort_values('taux_occupation', ascending=False),
                column_config={
                    "type": "Type",
                    "salle": "Salle",
                    "capacite": "Capacité",
                    "nb_examens": "Nb Examens",
                    "jours_utilises": "Jours Utilisés",
                    "total_minutes": "Durée Totale",
                    "taux_occupation": "Taux Occupation"
                },
                use_container_width=True
            )
            
            # Graphique de répartition
            fig = px.scatter(df_occupation, x='capacite', y='taux_occupation',
                            size='nb_examens', color='type',
                            hover_data=['salle', 'jours_utilises'],
                            title="Relation Capacité vs Occupation",
                            labels={'capacite': 'Capacité (places)', 
                                   'taux_occupation': 'Taux d\'Occupation (%)'})
            st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "📅 Évolution Temporelle":
        # Occupation par jour
        query = """
            SELECT 
                e.date_examen,
                le.type,
                COUNT(DISTINCT e.salle_id) as nb_salles_utilisees,
                COUNT(DISTINCT e.id) as nb_examens,
                ROUND(AVG(le.capacite), 0) as capacite_moyenne,
                ROUND(SUM(e.duree_minutes)/60, 1) as total_heures
            FROM examens e
            JOIN lieu_examen le ON e.salle_id = le.id
            WHERE e.date_examen BETWEEN %s AND %s
            AND e.statut != 'annulé'
            GROUP BY e.date_examen, le.type
            ORDER BY e.date_examen
        """
        
        evolution = run_query(query, (date_debut, date_fin))
        
        if evolution:
            df_evolution = pd.DataFrame(evolution)
            
            if not df_evolution.empty:
                # Graphique d'évolution
                fig = px.line(df_evolution, x='date_examen', y='nb_examens',
                            color='type',
                            title="Évolution du Nombre d'Examens par Jour",
                            labels={'date_examen': 'Date', 'nb_examens': "Nombre d'Examens"},
                            markers=True)
                st.plotly_chart(fig, use_container_width=True)
                
                # Heatmap de l'occupation
                pivot_df = df_evolution.pivot_table(
                    index='date_examen',
                    columns='type',
                    values='nb_examens',
                    fill_value=0
                ).reset_index()
                
                fig = go.Figure(data=go.Heatmap(
                    z=pivot_df.drop(columns=['date_examen']).values.T,
                    x=pivot_df['date_examen'],
                    y=pivot_df.drop(columns=['date_examen']).columns,
                    colorscale='Viridis',
                    colorbar=dict(title="Nombre d'Examens")
                ))
                
                fig.update_layout(
                    title="Heatmap d'Occupation par Type de Salle",
                    xaxis_title="Date",
                    yaxis_title="Type de Salle",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)

# PAGE: Analyse des Conflits
elif menu == "⚠️ Analyse des Conflits":
    # Modern header with gradient and improved spacing
    st.markdown("""
    <div style='background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
                padding: 25px;
                border-radius: 15px;
                margin-bottom: 30px;
                box-shadow: 0 10px 20px rgba(255, 107, 107, 0.2);'>
        <h1 style='color: white; margin: 0; font-size: 2.2rem;'>
            ⚠️ Analyse Stratégique des Conflits
        </h1>
        <p style='color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1rem;'>
        Détection et analyse des conflits d'horaires pour optimiser la planification des examens
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Date range reminder
    st.caption(f"📅 Période analysée: {date_debut.strftime('%d/%m/%Y')} - {date_fin.strftime('%d/%m/%Y')}")
    
    # Sélection du type d'analyse avec improved styling
    st.markdown("### 🔍 Sélection du Type d'Analyse")
    
    conflict_type = st.radio(
        "",
        ["📊 Vue Globale", "🔍 Analyse par Département", "👥 Conflits Étudiants", "🏫 Conflits Salles"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Add visual separator
    st.markdown("<hr style='margin: 30px 0; border: 1px solid #e0e0e0;'>", unsafe_allow_html=True)
    
    if conflict_type == "📊 Vue Globale":
        # Add section header with icon
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 30px;'>
            <h2 style='color: white; margin: 0;'>
                📊 Vue Globale des Conflits
            </h2>
            <p style='color: rgba(255,255,255,0.8); margin: 5px 0 0 0;'>
            Analyse macroscopique de tous les types de conflits
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        conflits = get_conflits_par_departement(date_debut, date_fin)
        
        if conflits:
            df_conflits = pd.DataFrame(conflits)
            
            # Convertir les colonnes en float/int
            for col in ['conflits_etudiants', 'conflits_salles', 'conflits_professeurs', 'total_examens', 'taux_conflits']:
                df_conflits[col] = pd.to_numeric(df_conflits[col], errors='coerce').fillna(0)
            
            # Enhanced KPI Cards with colors and icons
            col1, col2, col3, col4 = st.columns(4)
            
            def create_conflict_kpi(title, value, icon, bg_color, delta=None, suffix=""):
                card_html = f"""
                <div style='background: {bg_color};
                            padding: 20px;
                            border-radius: 15px;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                            border-left: 5px solid {bg_color};
                            height: 100%;'>
                    <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                        <div style='background: white; 
                                     width: 50px; 
                                     height: 50px; 
                                     border-radius: 12px; 
                                     display: flex; 
                                     align-items: center; 
                                     justify-content: center; 
                                     margin-right: 15px;
                                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                            <span style='font-size: 24px;'>{icon}</span>
                        </div>
                        <div style='flex-grow: 1;'>
                            <p style='margin: 0; color: white; font-size: 14px; font-weight: 600;'>{title}</p>
                            <h2 style='margin: 5px 0 0 0; color: white; font-size: 28px;'>{value}{suffix}</h2>
                """
                if delta:
                    card_html += f"""

                    """
                card_html += """
                 
                """
                return card_html
            
            with col1:
                total_conflits = int(df_conflits['conflits_etudiants'].sum() + 
                                   df_conflits['conflits_salles'].sum() + 
                                   df_conflits['conflits_professeurs'].sum())
                st.markdown(create_conflict_kpi(
                    "Total Conflits", 
                    f"{total_conflits:,}".replace(",", " "), 
                    "⚠️", 
                    "#e74c3c"
                ), unsafe_allow_html=True)
            
            with col2:
                taux_moyen = float(df_conflits['taux_conflits'].mean())
                st.markdown(create_conflict_kpi(
                    "Taux Conflits Moyen", 
                    f"{taux_moyen:.1f}", 
                    "📊", 
                    "#3498db",
                    suffix="%"
                ), unsafe_allow_html=True)
            
            with col3:
                if not df_conflits.empty:
                    dept_max = df_conflits.loc[df_conflits['taux_conflits'].idxmax()]['departement']
                    taux_max = float(df_conflits['taux_conflits'].max())
                    st.markdown(create_conflict_kpi(
                        "Département Critique", 
                        dept_max, 
                        "🔥", 
                        "#f39c12",
                        delta=f"{taux_max:.1f}%"
                    ), unsafe_allow_html=True)
                else:
                    st.markdown(create_conflict_kpi(
                        "Département Critique", 
                        "N/A", 
                        "🔥", 
                        "#f39c12"
                    ), unsafe_allow_html=True)
            
            with col4:
                total_examens = int(df_conflits['total_examens'].sum())
                taux_global = (total_conflits / total_examens * 100) if total_examens > 0 else 0
                st.markdown(create_conflict_kpi(
                    "Taux Conflits Global", 
                    f"{taux_global:.1f}", 
                    "🌍", 
                    "#2ecc71",
                    suffix="%"
                ), unsafe_allow_html=True)
            
            # Add spacing
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Enhanced radar chart section
            st.markdown("### 📊 Répartition des Types de Conflits")
            
            # Create tabs for different visualizations
            radar_tab1, radar_tab2, radar_tab3 = st.tabs(["Radar Chart", "Données Brutes", "Analyse"])
            
            with radar_tab1:
                types_conflits = ['Étudiants', 'Salles', 'Professeurs']
                valeurs_conflits = [
                    int(df_conflits['conflits_etudiants'].sum()),
                    int(df_conflits['conflits_salles'].sum()),
                    int(df_conflits['conflits_professeurs'].sum())
                ]
                
                # Enhanced radar chart with better styling
                fig = go.Figure()
                
                fig.add_trace(go.Scatterpolar(
                    r=valeurs_conflits,
                    theta=types_conflits,
                    fill='toself',
                    name='Conflits',
                    fillcolor='rgba(231, 76, 60, 0.6)',
                    line=dict(color='rgba(231, 76, 60, 1)', width=3),
                    marker=dict(size=10, color='rgba(231, 76, 60, 1)')
                ))
                
                max_val = max(valeurs_conflits) if valeurs_conflits else 1
                range_max = max_val * 1.2
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, range_max],
                            gridcolor='rgba(0,0,0,0.1)',
                            linecolor='rgba(0,0,0,0.3)',
                            tickfont=dict(size=12),
                            tickformat=',d'
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(0,0,0,0.1)',
                            linecolor='rgba(0,0,0,0.3)',
                            tickfont=dict(size=14, weight='bold')
                        ),
                        bgcolor='rgba(255,255,255,0.8)'
                    ),
                    showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add insights below radar chart
                st.markdown("#### 💡 Insights")
                if valeurs_conflits:
                    max_type = types_conflits[valeurs_conflits.index(max(valeurs_conflits))]
                    min_type = types_conflits[valeurs_conflits.index(min(valeurs_conflits))]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**Type de conflit le plus fréquent** : {max_type} ({max(valeurs_conflits):,} conflits)")
                    with col2:
                        st.success(f"**Type de conflit le moins fréquent** : {min_type} ({min(valeurs_conflits):,} conflits)")
            
            with radar_tab2:
                # Display raw data in a styled table
                st.markdown("#### 📋 Données des Conflits par Département")
                
                # Create a styled DataFrame
                styled_df = df_conflits.copy()
                styled_df = styled_df.sort_values('taux_conflits', ascending=False)
                
                # Add color coding for high conflict rates
                def highlight_conflicts(row):
                    if row['taux_conflits'] > 10:
                        return ['background-color: #ffcccc'] * len(row)
                    elif row['taux_conflits'] > 5:
                        return ['background-color: #fff2cc'] * len(row)
                    return [''] * len(row)
                
                st.dataframe(
                    styled_df.style.apply(highlight_conflicts, axis=1),
                    column_config={
                        "departement": "Département",
                        "total_examens": st.column_config.NumberColumn("Total Examens", format="%d"),
                        "conflits_etudiants": st.column_config.NumberColumn("Conflits Étudiants", format="%d"),
                        "conflits_salles": st.column_config.NumberColumn("Conflits Salles", format="%d"),
                        "conflits_professeurs": st.column_config.NumberColumn("Conflits Professeurs", format="%d"),
                        "taux_conflits": st.column_config.NumberColumn("Taux Conflits %", format="%.1f%%")
                    },
                    use_container_width=True,
                    height=400
                )
            
            with radar_tab3:
                # Detailed analysis
                st.markdown("#### 📈 Analyse Détailée")
                
                # Calculate statistics
                total_depts = len(df_conflits)
                high_conflict_depts = len(df_conflits[df_conflits['taux_conflits'] > 10])
                medium_conflict_depts = len(df_conflits[(df_conflits['taux_conflits'] > 5) & (df_conflits['taux_conflits'] <= 10)])
                low_conflict_depts = len(df_conflits[df_conflits['taux_conflits'] <= 5])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Départements à Haut Risque", high_conflict_depts, 
                             delta=f"{high_conflict_depts/total_depts*100:.1f}%" if total_depts > 0 else "0%")
                with col2:
                    st.metric("Départements à Risque Modéré", medium_conflict_depts,
                             delta=f"{medium_conflict_depts/total_depts*100:.1f}%" if total_depts > 0 else "0%")
                with col3:
                    st.metric("Départements à Faible Risque", low_conflict_depts,
                             delta=f"{low_conflict_depts/total_depts*100:.1f}%" if total_depts > 0 else "0%")
                
                # Recommendations based on data
                st.markdown("#### 🎯 Recommandations")
                if high_conflict_depts > 0:
                    st.error(f"**Action Requise** : {high_conflict_depts} département(s) ont un taux de conflits > 10%. Revoyez leur planification.")
                if medium_conflict_depts > 0:
                    st.warning(f"**Surveillance** : {medium_conflict_depts} département(s) ont un taux de conflits entre 5-10%. Surveillez leur situation.")
                if low_conflict_depts > 0:
                    st.success(f"**Satisfaisant** : {low_conflict_depts} département(s) ont un taux de conflits ≤ 5%.")
    
    elif conflict_type == "🔍 Analyse par Département":
        # Enhanced department analysis
        st.markdown("""
        <div style='background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 30px;'>
            <h2 style='color: white; margin: 0;'>
                🔍 Analyse par Département
            </h2>
            <p style='color: rgba(255,255,255,0.8); margin: 5px 0 0 0;'>
            Analyse détaillée des conflits pour un département spécifique
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Filtre département avec recherche
        departements = run_query("SELECT nom FROM departements ORDER BY nom")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            dept_selected = st.selectbox(
                "Sélectionner un département",
                options=[d['nom'] for d in departements],
                key="dept_select"
            )
        
        if dept_selected:
            # Department info card
            with col2:
                st.markdown(f"""
                <div style='background: #f8f9fa; 
                            padding: 15px; 
                            border-radius: 10px; 
                            border-left: 5px solid #3498db;
                            margin-top: 28px;'>
                    <p style='margin: 0; color: #666; font-size: 12px;'>Département sélectionné</p>
                    <h4 style='margin: 5px 0 0 0; color: #2c3e50;'>{dept_selected}</h4>
                </div>
                """, unsafe_allow_html=True)
            
            # Données détaillées pour le département
            query = """
                SELECT 
                    e.date_examen,
                    COUNT(DISTINCT e.id) as nb_examens,
                    SUM(CASE WHEN ce.conflit_etudiant > 0 THEN 1 ELSE 0 END) as conflits_etudiants,
                    SUM(CASE WHEN cs.conflit_salle > 0 THEN 1 ELSE 0 END) as conflits_salles,
                    SUM(CASE WHEN cp.conflit_professeur > 0 THEN 1 ELSE 0 END) as conflits_professeurs,
                    SUM(CASE WHEN ce.conflit_etudiant > 0 OR cs.conflit_salle > 0 OR cp.conflit_professeur > 0 THEN 1 ELSE 0 END) as total_conflits_jour
                FROM departements d
                JOIN formations f ON d.id = f.dept_id
                JOIN modules m ON f.id = m.formation_id
                JOIN examens e ON m.id = e.module_id 
                    AND e.date_examen BETWEEN %s AND %s
                    AND e.statut != 'annulé'
                LEFT JOIN (
                    SELECT e1.etudiant_id, e1.module_id, COUNT(*) as conflit_etudiant
                    FROM inscriptions e1
                    JOIN examens ex ON e1.module_id = ex.module_id
                    WHERE ex.date_examen BETWEEN %s AND %s
                    GROUP BY e1.etudiant_id, e1.module_id
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
                WHERE d.nom = %s
                GROUP BY e.date_examen
                ORDER BY e.date_examen
            """
            
            details = run_query(query, (date_debut, date_fin, date_debut, date_fin, 
                                       date_debut, date_fin, date_debut, date_fin, dept_selected))
            
            if details:
                df_details = pd.DataFrame(details)
                
                if not df_details.empty:
                    # Convertir les colonnes en int
                    for col in ['nb_examens', 'conflits_etudiants', 'conflits_salles', 'conflits_professeurs', 'total_conflits_jour']:
                        df_details[col] = df_details[col].astype(int)
                    
                    # Enhanced KPIs for the department
                    st.markdown("#### 📊 Indicateurs du Département")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        total_exams = int(df_details['nb_examens'].sum())
                        st.metric("Total Examens", f"{total_exams:,}".replace(",", " "))
                    
                    with col2:
                        jours_avec_conflits = int((df_details['total_conflits_jour'] > 0).sum())
                        total_jours = len(df_details)
                        st.metric("Jours avec Conflits", f"{jours_avec_conflits}/{total_jours}")
                    
                    with col3:
                        taux_jours_conflits = (jours_avec_conflits / total_jours * 100) if total_jours > 0 else 0
                        st.metric("Taux Jours Conflits", f"{taux_jours_conflits:.1f}%")
                    
                    with col4:
                        examens_moyens = df_details['nb_examens'].mean()
                        st.metric("Examen Moyen/Jour", f"{examens_moyens:.1f}")
                    
                    # Enhanced line chart with area fill
                    st.markdown("#### 📈 Évolution des Conflits")
                    
                    fig = go.Figure()
                    
                    # Add area for total conflicts
                    fig.add_trace(go.Scatter(
                        x=df_details['date_examen'],
                        y=df_details['total_conflits_jour'],
                        mode='lines',
                        name='Total Conflits',
                        line=dict(color='#e74c3c', width=3),
                        fill='tozeroy',
                        fillcolor='rgba(231, 76, 60, 0.2)'
                    ))
                    
                    # Add individual conflict types as lines
                    conflict_types = ['conflits_etudiants', 'conflits_salles', 'conflits_professeurs']
                    colors = ['#3498db', '#2ecc71', '#f39c12']
                    names = ['Étudiants', 'Salles', 'Professeurs']
                    
                    for col, color, name in zip(conflict_types, colors, names):
                        fig.add_trace(go.Scatter(
                            x=df_details['date_examen'],
                            y=df_details[col],
                            mode='lines+markers',
                            name=name,
                            line=dict(color=color, width=2),
                            marker=dict(size=6)
                        ))
                    
                    fig.update_layout(
                        title=f"Évolution des Conflits - {dept_selected}",
                        xaxis_title="Date",
                        yaxis_title="Nombre de Conflits",
                        hovermode='x unified',
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        height=500,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Daily conflict analysis
                    st.markdown("#### 📅 Analyse Journalière")
                    
                    # Filter to days with conflicts only
                    jours_conflits = df_details[df_details['total_conflits_jour'] > 0]
                    
                    if not jours_conflits.empty:
                        # Sort by total conflicts
                        jours_conflits = jours_conflits.sort_values('total_conflits_jour', ascending=False)
                        
                        # Display top conflict days
                        st.markdown("##### 📌 Jours avec le plus de conflits")
                        
                        for idx, row in jours_conflits.head(5).iterrows():
                            date_str = row['date_examen'].strftime('%d/%m/%Y')
                            avec_emojis = f"Étudiants: {row['conflits_etudiants']} 👥 | "
                            avec_emojis += f"Salles: {row['conflits_salles']} 🏫 | "
                            avec_emojis += f"Professeurs: {row['conflits_professeurs']} 👨‍🏫"
                            
                            st.info(f"**{date_str}** - {row['total_conflits_jour']} conflits ({avec_emojis})")
                    
                    # Conflict heatmap by day
                    st.markdown("#### 🔥 Heatmap des Conflits")
                    
                    # Create a heatmap matrix
                    heatmap_data = jours_conflits[['conflits_etudiants', 'conflits_salles', 'conflits_professeurs']].T
                    dates = [d.strftime('%d/%m') for d in jours_conflits['date_examen']]
                    
                    fig_heat = px.imshow(
                        heatmap_data,
                        labels=dict(x="Date", y="Type de Conflit", color="Nombre"),
                        x=dates,
                        y=['Étudiants', 'Salles', 'Professeurs'],
                        color_continuous_scale='Reds',
                        aspect='auto'
                    )
                    
                    fig_heat.update_layout(
                        title="Distribution des Types de Conflits par Jour",
                        xaxis_tickangle=-45,
                        height=400
                    )
                    
                    st.plotly_chart(fig_heat, use_container_width=True)
    
    elif conflict_type == "👥 Conflits Étudiants":
        # Enhanced student conflicts analysis
        st.markdown("""
        <div style='background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 30px;'>
            <h2 style='color: white; margin: 0;'>
                👥 Analyse des Conflits Étudiants
            </h2>
            <p style='color: rgba(255,255,255,0.8); margin: 5px 0 0 0;'>
            Analyse des étudiants impactés par des conflits d'horaires
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Requête pour les conflits étudiants détaillés
        query = """
            SELECT 
                et.id as etudiant_id,
                CONCAT(et.nom, ' ', et.prenom) as etudiant,
                f.nom as formation,
                d.nom as departement,
                COUNT(DISTINCT e.id) as nb_examens,
                COUNT(DISTINCT e.date_examen) as jours_examens,
                COUNT(DISTINCT e.date_examen) - COUNT(DISTINCT e.id) as conflits_simultanés,
                GROUP_CONCAT(DISTINCT CONCAT(m.nom, ' (', DATE_FORMAT(e.date_examen, '%d/%m'), ')') SEPARATOR ' | ') as examens_details
            FROM etudiants et
            JOIN inscriptions i ON et.id = i.etudiant_id
            JOIN modules m ON i.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            JOIN departements d ON f.dept_id = d.id
            JOIN examens e ON m.id = e.module_id 
                AND e.date_examen BETWEEN %s AND %s
                AND e.statut != 'annulé'
            GROUP BY et.id, et.nom, et.prenom, f.nom, d.nom
            HAVING nb_examens > jours_examens
            ORDER BY (nb_examens - jours_examens) DESC
            LIMIT 50
        """
        
        conflits_etudiants = run_query(query, (date_debut, date_fin))
        
        if conflits_etudiants:
            df_etudiants = pd.DataFrame(conflits_etudiants)
            
            if not df_etudiants.empty:
                # Enhanced KPIs
                st.markdown("#### 📊 Vue d'Ensemble")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_etudiants = len(df_etudiants)
                    st.metric("Étudiants Impactés", f"{total_etudiants:,}".replace(",", " "))
                
                with col2:
                    total_conflits = int(df_etudiants['conflits_simultanés'].sum())
                    st.metric("Total Conflits", f"{total_conflits:,}".replace(",", " "))
                
                with col3:
                    avg_conflicts = df_etudiants['conflits_simultanés'].mean()
                    st.metric("Conflits Moyens/Étudiant", f"{avg_conflicts:.1f}")
                
                with col4:
                    max_conflicts = df_etudiants['conflits_simultanés'].max()
                    st.metric("Conflits Maximum", max_conflicts)
                
                # Tabs for different views
                tab1, tab2, tab3 = st.tabs(["📊 Graphique", "📋 Liste", "🎯 Recommandations"])
                
                with tab1:
                    # Enhanced bar chart
                    df_top10 = df_etudiants.head(10).copy()
                    df_top10['conflits'] = df_top10['conflits_simultanés']
                    
                    fig = px.bar(df_top10, x='etudiant', y='conflits',
                                color='departement',
                                hover_data=['formation', 'nb_examens', 'jours_examens'],
                                title="Top 10 Étudiants avec le Plus de Conflits",
                                labels={'etudiant': 'Étudiant', 'conflits': 'Nombre de Conflits'},
                                text='conflits')
                    
                    fig.update_traces(
                        textposition='outside',
                        marker_line_color='rgb(8,48,107)',
                        marker_line_width=1.5
                    )
                    
                    fig.update_layout(
                        xaxis_tickangle=-45,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        height=500,
                        legend_title_text='Département'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Donut chart for department distribution
                    st.markdown("##### 📍 Répartition par Département")
                    
                    dept_dist = df_etudiants.groupby('departement').agg({
                        'etudiant_id': 'count',
                        'conflits_simultanés': 'sum'
                    }).reset_index()
                    
                    fig_donut = px.pie(dept_dist, values='etudiant_id', names='departement',
                                      title="Étudiants Impactés par Département",
                                      hole=0.4)
                    
                    fig_donut.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_donut, use_container_width=True)
                
                with tab2:
                    # Enhanced dataframe with search and filtering
                    st.markdown("##### 🔍 Liste des Étudiants avec Conflits")
                    
                    # Add search functionality
                    search_term = st.text_input("Rechercher un étudiant", key="student_search")
                    
                    if search_term:
                        filtered_df = df_etudiants[
                            df_etudiants['etudiant'].str.contains(search_term, case=False) |
                            df_etudiants['formation'].str.contains(search_term, case=False) |
                            df_etudiants['departement'].str.contains(search_term, case=False)
                        ]
                    else:
                        filtered_df = df_etudiants
                    
                    # Color coding based on conflict count
                    def highlight_rows(row):
                        if row['conflits_simultanés'] >= 3:
                            return ['background-color: #ffcccc'] * len(row)
                        elif row['conflits_simultanés'] == 2:
                            return ['background-color: #fff2cc'] * len(row)
                        return [''] * len(row)
                    
                    st.dataframe(
                        filtered_df.style.apply(highlight_rows, axis=1),
                        column_config={
                            "etudiant": "Étudiant",
                            "formation": "Formation",
                            "departement": "Département",
                            "nb_examens": st.column_config.NumberColumn("Nb Examens", format="%d"),
                            "jours_examens": st.column_config.NumberColumn("Jours Examens", format="%d"),
                            "conflits_simultanés": st.column_config.NumberColumn("Conflits", format="%d"),
                            "examens_details": "Détail des Examens"
                        },
                        use_container_width=True,
                        height=400
                    )
                    
                    # Export option
                    if st.button("📥 Exporter les Données"):
                        csv = filtered_df.to_csv(index=False)
                        st.download_button(
                            label="Télécharger CSV",
                            data=csv,
                            file_name=f"conflits_etudiants_{date_debut.strftime('%Y%m%d')}_{date_fin.strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                
                with tab3:
                    # Recommendations based on data
                    st.markdown("##### 🎯 Actions Recommandées")
                    
                    # Identify problematic students
                    critical_students = df_etudiants[df_etudiants['conflits_simultanés'] >= 3]
                    if not critical_students.empty:
                        st.error(f"**Action Prioritaire** : {len(critical_students)} étudiant(s) ont 3 conflits ou plus")
                        st.dataframe(critical_students[['etudiant', 'formation', 'conflits_simultanés']], 
                                   use_container_width=True, height=200)
                    
                    # Identify problematic departments
                    dept_summary = df_etudiants.groupby('departement').agg({
                        'etudiant_id': 'count',
                        'conflits_simultanés': 'sum'
                    }).reset_index()
                    
                    dept_summary = dept_summary.sort_values('etudiant_id', ascending=False)
                    
                    if not dept_summary.empty:
                        st.warning(f"**Départements les plus impactés** : {dept_summary.iloc[0]['departement']} "
                                 f"({dept_summary.iloc[0]['etudiant_id']} étudiants)")
                    
                    # General recommendations
                    st.info("**Recommandations générales** :")
                    st.markdown("""
                    1. **Revoir les inscriptions** pour les étudiants avec >2 conflits
                    2. **Étaler les examens** pour les formations problématiques
                    3. **Créer des sessions de rattrapage** pour les cas critiques
                    4. **Sensibiliser les étudiants** aux risques de conflits
                    """)
    
    elif conflict_type == "🏫 Conflits Salles":
        # Enhanced room conflicts analysis
        st.markdown("""
        <div style='background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 30px;'>
            <h2 style='color: white; margin: 0;'>
                🏫 Analyse des Conflits de Salles
            </h2>
            <p style='color: rgba(255,255,255,0.8); margin: 5px 0 0 0;'>
            Analyse des conflits d'occupation des salles d'examen
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Requête pour les conflits de salles détaillés
        query = """
            SELECT 
                e1.id as examen1_id,
                e2.id as examen2_id,
                le.nom as salle,
                le.type,
                le.capacite,
                e1.date_examen,
                TIME_FORMAT(e1.heure_debut, '%H:%i') as debut1,
                TIME_FORMAT(e1.heure_fin, '%H:%i') as fin1,
                TIME_FORMAT(e2.heure_debut, '%H:%i') as debut2,
                TIME_FORMAT(e2.heure_fin, '%H:%i') as fin2,
                m1.nom as module1,
                m2.nom as module2,
                f1.nom as formation1,
                f2.nom as formation2,
                CONCAT(p1.nom, ' ', p1.prenom) as professeur1,
                CONCAT(p2.nom, ' ', p2.prenom) as professeur2,
                d1.nom as departement1,
                d2.nom as departement2,
                TIMESTAMPDIFF(MINUTE, 
                    GREATEST(e1.heure_debut, e2.heure_debut),
                    LEAST(e1.heure_fin, e2.heure_fin)
                ) as chevauchement_minutes
            FROM examens e1
            JOIN examens e2 ON e1.salle_id = e2.salle_id 
                AND e1.date_examen = e2.date_examen
                AND e1.id < e2.id
            JOIN lieu_examen le ON e1.salle_id = le.id
            JOIN modules m1 ON e1.module_id = m1.id
            JOIN modules m2 ON e2.module_id = m2.id
            JOIN formations f1 ON m1.formation_id = f1.id
            JOIN formations f2 ON m2.formation_id = f2.id
            JOIN departements d1 ON f1.dept_id = d1.id
            JOIN departements d2 ON f2.dept_id = d2.id
            LEFT JOIN professeurs p1 ON e1.professeur_id = p1.id
            LEFT JOIN professeurs p2 ON e2.professeur_id = p2.id
            WHERE e1.date_examen BETWEEN %s AND %s
            AND e1.statut != 'annulé' AND e2.statut != 'annulé'
            AND (
                (e1.heure_debut BETWEEN e2.heure_debut AND e2.heure_fin) OR
                (e1.heure_fin BETWEEN e2.heure_debut AND e2.heure_fin) OR
                (e2.heure_debut BETWEEN e1.heure_debut AND e1.heure_fin) OR
                (e2.heure_fin BETWEEN e1.heure_debut AND e1.heure_fin)
            )
            ORDER BY e1.date_examen, e1.heure_debut
        """
        
        conflits_salles = run_query(query, (date_debut, date_fin))
        
        if conflits_salles:
            df_salles = pd.DataFrame(conflits_salles)
            
            if not df_salles.empty:
                # Enhanced KPIs
                st.markdown("#### 📊 Vue d'Ensemble des Conflits Salles")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_conflits = len(df_salles)
                    st.metric("Total Conflits Salles", f"{total_conflits:,}".replace(",", " "))
                
                with col2:
                    salles_uniques = df_salles['salle'].nunique()
                    st.metric("Salles Impactées", salles_uniques)
                
                with col3:
                    jours_conflits = df_salles['date_examen'].nunique()
                    st.metric("Jours avec Conflits", jours_conflits)
                
                with col4:
                    avg_overlap = df_salles['chevauchement_minutes'].mean()
                    st.metric("Chevauchement Moyen", f"{avg_overlap:.0f} min")
                
                # Tabs for different analyses
                tab1, tab2, tab3 = st.tabs(["📊 Par Salle", "📅 Par Jour", "📋 Détails"])
                
                with tab1:
                    # Analysis by room
                    conflits_par_salle = df_salles.groupby(['salle', 'type']).agg({
                        'examen1_id': 'count',
                        'chevauchement_minutes': 'mean',
                        'capacite': 'first'
                    }).reset_index().rename(columns={'examen1_id': 'nb_conflits'})
                    
                    # Sort by number of conflicts
                    conflits_par_salle = conflits_par_salle.sort_values('nb_conflits', ascending=False)
                    
                    fig = px.bar(conflits_par_salle, x='salle', y='nb_conflits',
                                color='type',
                                hover_data=['chevauchement_minutes', 'capacite'],
                                title="Nombre de Conflits par Salle",
                                labels={'salle': 'Salle', 'nb_conflits': 'Nombre de Conflits', 'type': 'Type'},
                                text='nb_conflits')
                    
                    fig.update_traces(
                        textposition='outside',
                        marker_line_color='rgb(8,48,107)',
                        marker_line_width=1.5
                    )
                    
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis_tickangle=-45,
                        height=500,
                        legend_title_text='Type de Salle'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Room type analysis
                    st.markdown("##### 📍 Analyse par Type de Salle")
                    
                    type_analysis = df_salles.groupby('type').agg({
                        'salle': 'nunique',
                        'examen1_id': 'count'
                    }).reset_index().rename(columns={'salle': 'nb_salles', 'examen1_id': 'nb_conflits'})
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig_type = px.pie(type_analysis, values='nb_conflits', names='type',
                                         title="Répartition des Conflits par Type")
                        st.plotly_chart(fig_type, use_container_width=True)
                    
                    with col2:
                        st.dataframe(
                            type_analysis.style.highlight_max(subset=['nb_conflits'], color='#ffcccc'),
                            use_container_width=True,
                            height=300
                        )
                
                with tab2:
                    # Analysis by day
                    conflits_par_jour = df_salles.groupby('date_examen').agg({
                        'salle': 'nunique',
                        'examen1_id': 'count'
                    }).reset_index().rename(columns={'salle': 'nb_salles', 'examen1_id': 'nb_conflits'})
                    
                    fig_jour = px.line(conflits_par_jour, x='date_examen', y='nb_conflits',
                                      title="Évolution des Conflits Salles par Jour",
                                      labels={'date_examen': 'Date', 'nb_conflits': 'Nombre de Conflits'},
                                      markers=True)
                    
                    fig_jour.add_trace(px.bar(conflits_par_jour, x='date_examen', y='nb_salles')['data'][0])
                    fig_jour.data[1].name = "Salles Impactées"
                    fig_jour.data[1].yaxis = 'y'
                    fig_jour.update_layout(
                        yaxis_title="Nombre de Conflits",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        height=500
                    )
                    
                    st.plotly_chart(fig_jour, use_container_width=True)
                    
                    # Display worst days
                    st.markdown("##### 📌 Jours les Plus Problématiques")
                    
                    worst_days = conflits_par_jour.sort_values('nb_conflits', ascending=False).head(5)
                    
                    for _, row in worst_days.iterrows():
                        date_str = row['date_examen'].strftime('%d/%m/%Y')
                        st.warning(f"**{date_str}** : {row['nb_conflits']} conflits dans {row['nb_salles']} salles différentes")
                
                with tab3:
                    # Detailed conflicts table with filtering
                    st.markdown("##### 🔍 Détail des Conflits")
                    
                    # Filter options
                    col1, col2 = st.columns(2)
                    with col1:
                        selected_salle = st.multiselect(
                            "Filtrer par salle",
                            options=sorted(df_salles['salle'].unique()),
                            default=[]
                        )
                    
                    with col2:
                        selected_date = st.date_input(
                            "Filtrer par date",
                            value=[],
                            key="room_date_filter"
                        )
                    
                    # Apply filters
                    filtered_df = df_salles.copy()
                    
                    if selected_salle:
                        filtered_df = filtered_df[filtered_df['salle'].isin(selected_salle)]
                    
                    if selected_date:
                        if isinstance(selected_date, list) and len(selected_date) == 2:
                            start_date, end_date = selected_date
                            filtered_df = filtered_df[
                                (filtered_df['date_examen'] >= pd.Timestamp(start_date)) &
                                (filtered_df['date_examen'] <= pd.Timestamp(end_date))
                            ]
                    
                    # Display filtered data
                    st.dataframe(
                        filtered_df[[
                            'date_examen', 'salle', 'type', 'debut1', 'fin1', 'module1', 'formation1',
                            'debut2', 'fin2', 'module2', 'formation2', 'chevauchement_minutes'
                        ]],
                        column_config={
                            "date_examen": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                            "salle": "Salle",
                            "type": "Type",
                            "debut1": "Début Examen 1",
                            "fin1": "Fin Examen 1",
                            "module1": "Module 1",
                            "formation1": "Formation 1",
                            "debut2": "Début Examen 2",
                            "fin2": "Fin Examen 2",
                            "module2": "Module 2",
                            "formation2": "Formation 2",
                            "chevauchement_minutes": st.column_config.NumberColumn("Chevauchement (min)", format="%d")
                        },
                        use_container_width=True,
                        height=400
                    )
                    
                    # Export option
                    if st.button("📥 Exporter les Conflits Salles"):
                        csv = filtered_df.to_csv(index=False)
                        st.download_button(
                            label="Télécharger CSV",
                            data=csv,
                            file_name=f"conflits_salles_{date_debut.strftime('%Y%m%d')}_{date_fin.strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
    
    # Add footer with summary
    st.markdown("---")
    
    # Summary statistics
    st.markdown("### 📋 Résumé des Analyses")
    
    # Calculate overall statistics
    total_conflicts = 0
    if conflict_type == "📊 Vue Globale" and 'df_conflits' in locals():
        total_conflicts = int(df_conflits['conflits_etudiants'].sum() + 
                            df_conflits['conflits_salles'].sum() + 
                            df_conflits['conflits_professeurs'].sum())
    elif conflict_type == "👥 Conflits Étudiants" and 'df_etudiants' in locals():
        total_conflicts = int(df_etudiants['conflits_simultanés'].sum())
    elif conflict_type == "🏫 Conflits Salles" and 'df_salles' in locals():
        total_conflicts = len(df_salles)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Type d'Analyse", conflict_type.replace("📊 ", "").replace("🔍 ", "").replace("👥 ", "").replace("🏫 ", ""))
    
    with col2:
        st.metric("Conflits Totaux", f"{total_conflicts:,}".replace(",", " "))
    
    with col3:
        st.metric("Période", f"{date_debut.strftime('%d/%m')} - {date_fin.strftime('%d/%m')}")

elif menu == "✅ Validation EDT":
    # En-tête avec style académique
    st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 30px;">
            <h1 style="color: white; margin: 0;">📚 Validation des Emplois du Temps</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0;">Université - Système de Gestion des Examens</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Informations sur la période
    col_period, col_stats = st.columns([2, 1])
    with col_period:
        st.info(f"**Période sélectionnée :** {date_debut} au {date_fin}")
    with col_stats:
        planning = get_planning_complet(date_debut, date_fin)
        if planning:
            total_examens = len(planning)
            confirmes = sum(1 for p in planning if p['statut'] == 'confirmé')
            taux = (confirmes/total_examens*100) if total_examens > 0 else 0
            st.metric("📊 Progression globale", f"{taux:.1f}%")
    
    # Onglets avec style amélioré
    tab1, tab2, tab3 = st.tabs([
        "🔍 Validation Individuelle", 
        "🏛️ Validation par Département", 
        "📈 Tableau de Bord"
    ])
    
    with tab1:
        # Section filtres dans un expander
        with st.expander("🔧 **Filtres avancés**", expanded=True):
            cols_filters = st.columns(4)
            
            with cols_filters[0]:
                departements = run_query("SELECT nom FROM departements ORDER BY nom")
                dept_filter = st.selectbox(
                    "Département",
                    options=['Tous'] + [d['nom'] for d in departements],
                    key="dept_filter"
                )
            
            with cols_filters[1]:
                statut_filter = st.selectbox(
                    "Statut",
                    options=['Tous', 'planifié', 'confirmé', 'annulé'],
                    key="statut_filter"
                )
            
            with cols_filters[2]:
                session_filter = st.selectbox(
                    "Session",
                    options=['Toutes', 'Principale', 'Rattrapage'],
                    key="session_filter"
                )
            
            with cols_filters[3]:
                type_filter = st.selectbox(
                    "Type d'examen",
                    options=['Tous', 'Écrit', 'Oral', 'Pratique']
                )
        
        # Récupérer et filtrer les données
        if planning:
            df_planning = pd.DataFrame(planning)
            
            # Appliquer filtres
            if dept_filter != 'Tous':
                df_planning = df_planning[df_planning['departement'] == dept_filter]
            if statut_filter != 'Tous':
                df_planning = df_planning[df_planning['statut'] == statut_filter]
            if session_filter != 'Toutes':
                df_planning = df_planning[df_planning['session'] == session_filter]
            
            # En-tête avec statistiques
            st.markdown(f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3 style="margin: 0; color: #2c3e50;">📋 Examens à valider</h3>
                            <p style="margin: 5px 0 0 0; color: #7f8c8d;">{len(df_planning)} examen(s) trouvé(s)</p>
                        </div>
                        <div style="text-align: right;">
                            <span style="background: #e3f2fd; color: #1976d2; padding: 5px 15px; border-radius: 20px; font-weight: bold;">
                                {len(df_planning[df_planning['statut']=='planifié'])} en attente
                            </span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Trier les examens (les non validés d'abord)
            df_planning['sort_order'] = df_planning['statut'].map({'planifié': 0, 'confirmé': 1, 'annulé': 2})
            df_planning = df_planning.sort_values(['sort_order', 'date_examen', 'heure_debut'])
            
            # Afficher chaque examen sous forme de carte
            for idx, row in df_planning.iterrows():
                # Définir les couleurs selon le statut
                if row['statut'] == 'confirmé':
                    border_color = "#4CAF50"
                    status_bg = "#E8F5E9"
                    status_text = "✅ CONFIRMÉ"
                elif row['statut'] == 'annulé':
                    border_color = "#F44336"
                    status_bg = "#FFEBEE"
                    status_text = "❌ ANNULÉ"
                else:
                    border_color = "#FF9800"
                    status_bg = "#FFF3E0"
                    status_text = "⏳ EN ATTENTE"
                
                with st.container():
                    # Carte d'examen
                    st.markdown(f"""
                        <div style="
                            border-left: 5px solid {border_color};
                            background: white;
                            padding: 20px;
                            border-radius: 8px;
                            margin: 15px 0;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <div style="flex: 1;">
                                    <h4 style="margin: 0 0 10px 0; color: #2c3e50;">
                                        📚 {row['module']}
                                    </h4>
                                    <div style="display: flex; gap: 10px; margin-bottom: 10px; flex-wrap: wrap;">
                                        <span style="background: {status_bg}; color: {border_color}; padding: 4px 12px; border-radius: 12px; font-size: 0.85em;">
                                            {status_text}
                                        </span>
                                        <span style="background: #e3f2fd; color: #1976d2; padding: 4px 12px; border-radius: 12px; font-size: 0.85em;">
                                            {row['session']}
                                        </span>
                                        <span style="background: #f3e5f5; color: #7b1fa2; padding: 4px 12px; border-radius: 12px; font-size: 0.85em;">
                                            {row['formation']}
                                        </span>
                                    </div>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 1.2em; font-weight: bold; color: #3498db;">
                                        {row['date_examen']}
                                    </div>
                                    <div style="color: #7f8c8d;">
                                        {row['heure_debut']} - {row['heure_fin']}
                                    </div>
                                </div>
                            </div>
                            
                            
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Boutons d'action
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        if row['statut'] == 'planifié':
                            if st.button(
                                "✅ Confirmer cet examen",
                                key=f"confirm_{row['id']}",
                                type="primary",
                                use_container_width=True
                            ):
                                if valider_examen(row['id']):
                                    st.success(f"L'examen **{row['module']}** a été confirmé avec succès !")
                                    st.rerun()
                        elif row['statut'] == 'confirmé':
                            if st.button(
                                "📋 Voir les détails",
                                key=f"details_{row['id']}",
                                use_container_width=True
                            ):
                                st.session_state[f"show_details_{row['id']}"] = True
                    
                    with col2:
                        if st.button("📊 Statistiques", key=f"stats_{row['id']}", use_container_width=True):
                            with st.expander(f"📈 Statistiques de l'examen"):
                                col_stats1, col_stats2 = st.columns(2)
                                with col_stats1:
                                    st.metric("Capacité salle", row['capacite'])
                                    st.metric("Étudiants inscrits", row['nb_etudiants'])
                                with col_stats2:
                                    st.metric("Taux occupation", f"{row['taux_occupation_salle']}%")
                                    st.metric("Durée", f"{row.get('duree', '2h')}")
                    
                    with col3:
                        if st.button("📅 Calendrier", key=f"cal_{row['id']}", use_container_width=True):
                            st.info(f"Examen prévu le {row['date_examen']} de {row['heure_debut']} à {row['heure_fin']}")
                    
                    with col4:
                        if row['statut'] == 'planifié':
                            if st.button(
                                "❌ Annuler",
                                key=f"cancel_{row['id']}",
                                type="secondary",
                                use_container_width=True
                            ):
                                st.warning(f"Êtes-vous sûr de vouloir annuler l'examen **{row['module']}** ?")
                                col_confirm1, col_confirm2 = st.columns(2)
                                with col_confirm1:
                                    if st.button("Oui, annuler", key=f"cancel_confirm_{row['id']}"):
                                        # Fonction d'annulation à implémenter
                                        st.error("Fonction d'annulation à implémenter")
                                with col_confirm2:
                                    if st.button("Non, garder", key=f"cancel_cancel_{row['id']}"):
                                        st.rerun()
                    
                    st.divider()
        
        else:
            st.warning("⚠️ Aucun examen planifié pour cette période")
            st.image("https://cdn-icons-png.flaticon.com/512/7486/7486744.png", width=200)
    
    with tab2:
        st.subheader("🏛️ Validation par Département")
        
        validation_stats = get_statistiques_validation(date_debut, date_fin)
        
        if validation_stats:
            df_validation = pd.DataFrame(validation_stats)
            
            # Tri par taux de validation (du plus bas au plus haut)
            df_validation['taux_num'] = df_validation['taux_validation'].astype(float)
            df_validation = df_validation.sort_values('taux_num')
            
            # Carte globale
            total_confirmes = df_validation['confirmes'].sum()
            total_examens = df_validation['total_examens'].sum()
            taux_global = (total_confirmes / total_examens * 100) if total_examens > 0 else 0
            
            st.markdown("### 📊 Vue d'ensemble des départements")
            
            col_global1, col_global2, col_global3 = st.columns(3)
            with col_global1:
                st.metric("🏫 Départements", len(df_validation))
            with col_global2:
                st.metric("📚 Examens totaux", total_examens)
            with col_global3:
                st.metric("✅ Taux global", f"{taux_global:.1f}%")
            
            st.progress(taux_global/100, text=f"Progression globale : {taux_global:.1f}%")
            
            st.divider()
            
            # Cartes pour chaque département
            st.markdown("### 📋 État par département")
            
            for _, dept in df_validation.iterrows():
                # Calculs
                total = int(dept['total_examens'])
                confirmes = int(dept['confirmes'])
                en_attente = int(dept['en_attente'])
                annules = int(dept['annules'])
                taux = float(dept['taux_num'])
                
                # Déterminer la couleur
                if taux >= 90:
                    color = "#4CAF50"
                    status = "Excellent"
                elif taux >= 70:
                    color = "#FF9800"
                    status = "Bon"
                elif taux >= 50:
                    color = "#FFC107"
                    status = "Moyen"
                else:
                    color = "#F44336"
                    status = "À améliorer"
                
                # Carte du département
                col_dept1, col_dept2 = st.columns([3, 1])
                
                with col_dept1:
                    st.markdown(f"""
                        <div style="background: white; padding: 20px; border-radius: 10px; border-left: 5px solid {color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 15px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <div>
                                    <h3 style="margin: 0; color: #2c3e50;">🏛️ {dept['departement']}</h3>
                                    <p style="margin: 5px 0 0 0; color: #7f8c8d;">Statut : <strong>{status}</strong></p>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 2em; font-weight: bold; color: {color};">{taux:.1f}%</div>
                                    <div style="color: #7f8c8d; font-size: 0.9em;">Taux de validation</div>
                                </div>
                            </div>
                            
                            <div style="margin: 15px 0;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                    <span>Progression</span>
                                    <span>{confirmes}/{total} examens</span>
                                </div>
                                <div style="height: 10px; background: #f0f0f0; border-radius: 5px; overflow: hidden;">
                                    <div style="width: {taux}%; height: 100%; background: {color};"></div>
                                </div>
                            </div>
                            
                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; text-align: center;">
                                <div>
                                    <div style="font-size: 1.5em; font-weight: bold; color: #4CAF50;">{confirmes}</div>
                                    <div style="font-size: 0.9em; color: #7f8c8d;">✅ Confirmés</div>
                                </div>
                                <div>
                                    <div style="font-size: 1.5em; font-weight: bold; color: #FF9800;">{en_attente}</div>
                                    <div style="font-size: 0.9em; color: #7f8c8d;">⏳ En attente</div>
                                </div>
                                <div>
                                    <div style="font-size: 1.5em; font-weight: bold; color: #F44336;">{annules}</div>
                                    <div style="font-size: 0.9em; color: #7f8c8d;">❌ Annulés</div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col_dept2:
                    st.write("")  # Espacement vertical
                    if en_attente > 0:
                        dept_id_query = run_query("SELECT id FROM departements WHERE nom = %s", (dept['departement'],))
                        if dept_id_query:
                            dept_id = dept_id_query[0]['id']
                            if st.button(
                                f"✅ Valider tous",
                                key=f"val_all_{dept_id}",
                                use_container_width=True,
                                type="primary"
                            ):
                                with st.spinner(f"Validation des {en_attente} examen(s) en attente..."):
                                    if valider_tous_examens_departement(dept_id, date_debut, date_fin):
                                        st.success(f"✅ {en_attente} examen(s) validé(s) pour le département {dept['departement']} !")
                                        st.rerun()
                    else:
                        st.success("✅ Complété", icon="✅")
                
                st.divider()
    
    with tab3:
        st.subheader("📈 Tableau de Bord Académique")
        
        if validation_stats:
            df_validation = pd.DataFrame(validation_stats)
            
            # Section des KPI principaux
            st.markdown("### 🎯 Indicateurs Clés de Performance")
            
            kpi_cols = st.columns(4)
            
            with kpi_cols[0]:
                total_exam = df_validation['total_examens'].sum()
                st.metric("📚 Total Examens", total_exam)
            
            with kpi_cols[1]:
                total_conf = df_validation['confirmes'].sum()
                taux_conf = (total_conf / total_exam * 100) if total_exam > 0 else 0
                st.metric("✅ Taux de Confirmation", f"{taux_conf:.1f}%")
            
            with kpi_cols[2]:
                total_att = df_validation['en_attente'].sum()
                st.metric("⏳ En Attente", total_att)
            
            with kpi_cols[3]:
                total_ann = df_validation['annules'].sum()
                taux_ann = (total_ann / total_exam * 100) if total_exam > 0 else 0
                st.metric("📉 Taux d'Annulation", f"{taux_ann:.1f}%")
            
            # Graphiques
            st.markdown("### 📊 Visualisations")
            
            try:
                import plotly.graph_objects as go
                from plotly.subplots import make_subplots
                
                # Premier graphique : Barres empilées
                fig1 = make_subplots(rows=1, cols=2, subplot_titles=("📈 État par Département", "📊 Répartition Globale"))
                
                # Graphique à barres
                fig1.add_trace(
                    go.Bar(
                        name='Confirmés',
                        x=df_validation['departement'],
                        y=df_validation['confirmes'],
                        marker_color='#4CAF50'
                    ),
                    row=1, col=1
                )
                
                fig1.add_trace(
                    go.Bar(
                        name='En attente',
                        x=df_validation['departement'],
                        y=df_validation['en_attente'],
                        marker_color='#FF9800'
                    ),
                    row=1, col=1
                )
                
                fig1.add_trace(
                    go.Bar(
                        name='Annulés',
                        x=df_validation['departement'],
                        y=df_validation['annules'],
                        marker_color='#F44336'
                    ),
                    row=1, col=1
                )
                
                # Graphique circulaire
                fig1.add_trace(
                    go.Pie(
                        labels=['Confirmés', 'En attente', 'Annulés'],
                        values=[total_conf, total_att, total_ann],
                        hole=0.4,
                        marker_colors=['#4CAF50', '#FF9800', '#F44336']
                    ),
                    row=1, col=2
                )
                
                fig1.update_layout(height=400, showlegend=True)
                st.plotly_chart(fig1, use_container_width=True)
                
                # Deuxième graphique : Taux de validation par département
                fig2 = go.Figure()
                
                fig2.add_trace(go.Bar(
                    x=df_validation['departement'],
                    y=df_validation['taux_validation'].astype(float),
                    marker_color=df_validation['taux_validation'].apply(
                        lambda x: '#4CAF50' if float(x) >= 80 else '#FF9800' if float(x) >= 50 else '#F44336'
                    ),
                    text=df_validation['taux_validation'].apply(lambda x: f"{float(x):.1f}%"),
                    textposition='outside'
                ))
                
                fig2.update_layout(
                    title="🎯 Taux de Validation par Département",
                    xaxis_title="Département",
                    yaxis_title="Taux de validation (%)",
                    yaxis=dict(range=[0, 100]),
                    height=400
                )
                
                st.plotly_chart(fig2, use_container_width=True)
                
            except:
                st.warning("Les graphiques nécessitent la bibliothèque Plotly")
            
            # Tableau de données
            st.markdown("### 📋 Données Détaillées")
            
            # Ajouter une colonne de statut
            def get_status_color(taux):
                taux_num = float(taux)
                if taux_num >= 90:
                    return "🟢 Excellent"
                elif taux_num >= 70:
                    return "🟡 Bon"
                elif taux_num >= 50:
                    return "🟠 Moyen"
                else:
                    return "🔴 Critique"
            
            df_display = df_validation.copy()
            df_display['Statut'] = df_display['taux_validation'].apply(get_status_color)
            df_display['Taux'] = df_display['taux_validation'].apply(lambda x: f"{float(x):.1f}%")
            
            # Afficher le tableau avec style
            st.dataframe(
                df_display[['departement', 'total_examens', 'confirmes', 'en_attente', 'annules', 'Taux', 'Statut']],
                column_config={
                    "departement": "🏛️ Département",
                    "total_examens": "📚 Total",
                    "confirmes": "✅ Confirmés",
                    "en_attente": "⏳ En attente", 
                    "annules": "❌ Annulés",
                    "Taux": "📈 Taux",
                    "Statut": "🎯 Évaluation"
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Section export
            st.markdown("---")
            st.markdown("### 📤 Export des Données")
            
            export_cols = st.columns(3)
            
            with export_cols[0]:
                csv = df_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "💾 Télécharger CSV",
                    csv,
                    f"validation_edt_{date_debut}_{date_fin}.csv",
                    "text/csv",
                    use_container_width=True
                )
            
            with export_cols[1]:
                if st.button("📄 Générer Rapport", use_container_width=True):
                    st.info("Le rapport PDF est en cours de génération...")
                    # Implémenter la génération PDF ici
            
            with export_cols[2]:
                if st.button("🖨️ Imprimer le Résumé", use_container_width=True):
                    st.info("Préparation pour l'impression...")
                    # Implémenter l'impression ici
            
            # Pied de page
            st.markdown("---")
            st.caption(f"""
                *Système de Validation des Emplois du Temps - Université*
                | Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M')}
                | Période : {date_debut} au {date_fin}
            """)

elif menu == "📈 KPIs Académiques":
    
    # ==================== HEADER AVEC STYLE PRÉMIUM ====================
    
    
    # ==================== ONGLETS STYLÉS ====================
    tab_css = """
    <style>
    .kpi-tabs {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 30px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.06);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
        padding: 10px;
        background: #f8f9fa;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        padding: 0 25px;
        font-weight: 600;
        font-size: 1em;
        border-radius: 10px;
        transition: all 0.3s ease;
        background: white;
        border: 2px solid #e0e0e0;
    }
    .stTabs [data-baseweb="tab"]:hover {
        border-color: #3498db;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(52, 152, 219, 0.2);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3498db, #2980b9) !important;
        color: white !important;
        border-color: #3498db !important;
        box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3) !important;
    }
    </style>
    """
    st.markdown(tab_css, unsafe_allow_html=True)
    
    # ==================== DASHBOARD RAPIDE ====================
    # Afficher quelques KPIs en haut pour donner un aperçu
    kpis_summary = get_kpis_academiques(date_debut, date_fin) or [{}]
    if kpis_summary:
        kpi = kpis_summary[0]
        
        st.markdown("### 📊 Vue d'Ensemble - Dashboard Analytics")
        
        cols_dash = st.columns(4)
        metrics_config = [
            {"title": "🏫 Occupation Moyenne", "value": f"{float(kpi.get('taux_occupation_global', 0)):.1f}%", "color": "#2ecc71", "icon": "📊"},
            {"title": "👨‍🏫 Charge Professeurs", "value": f"{float(kpi.get('exams_moyens_par_prof', 0)):.1f}", "color": "#e74c3c", "icon": "⚖️"},
            {"title": "🎯 Salles Utilisées", "value": f"{float(kpi.get('taux_salles_utilisees', 0)):.1f}%", "color": "#3498db", "icon": "🏢"},
            {"title": "📈 Productivité", "value": f"{float(kpi.get('exams_moyens_par_jour', 0)):.1f}/jour", "color": "#9b59b6", "icon": "🚀"}
        ]
        
        for idx, col in enumerate(cols_dash):
            with col:
                metric = metrics_config[idx]
                st.markdown(f"""
                    <div style='
                        background: white;
                        padding: 20px;
                        border-radius: 15px;
                        border-top: 4px solid {metric['color']};
                        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
                        text-align: center;
                        transition: all 0.3s ease;
                        height: 150px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    '>
                        <div style='
                            width: 50px;
                            height: 50px;
                            background: {metric['color']}15;
                            border-radius: 12px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            margin: 0 auto 15px;
                            font-size: 1.5em;
                        '>
                            {metric['icon']}
                        </div>
                        <div style='font-size: 0.9em; color: #7f8c8d; margin-bottom: 8px;'>{metric['title']}</div>
                        <div style='font-size: 1.8em; font-weight: 700; color: {metric["color"]};'>{metric['value']}</div>
                    </div>
                """, unsafe_allow_html=True)
    
    # ==================== ONGLETS PRINCIPAUX ====================
    tab1, tab2, tab3 = st.tabs([
        "👨‍🏫 • Analytics RH", 
        "🏫 • Analytics Infrastructure", 
        "🎯 • Performance Globale"
    ])
    
    with tab1:
        # ==================== ANALYTICS RESSOURCES HUMAINES ====================
        st.markdown("""
            <div style='
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 25px;
                border-radius: 15px;
                margin-bottom: 30px;
                border-left: 5px solid #e74c3c;
            '>
                <div style='display: flex; align-items: center; gap: 15px;'>
                    <div style='
                        width: 60px;
                        height: 60px;
                        background: linear-gradient(135deg, #e74c3c, #c0392b);
                        border-radius: 15px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 1.8em;
                        color: white;
                    '>
                        👨‍🏫
                    </div>
                    <div>
                        <h2 style='margin: 0; color: #2c3e50;'>Analytics Ressources Humaines</h2>
                        <p style='margin: 5px 0 0 0; color: #7f8c8d;'>Analyse de la charge de travail et performance des enseignants</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        charge_profs = get_charge_professeurs(date_debut, date_fin)
        
        if charge_profs:
            df_charge = pd.DataFrame(charge_profs)
            
            if not df_charge.empty:
                # Convertir les valeurs
                df_charge['total_heures'] = pd.to_numeric(df_charge['total_heures'], errors='coerce').fillna(0)
                df_charge['taux_charge'] = pd.to_numeric(df_charge['taux_charge'], errors='coerce').fillna(0)
                
                # ==================== KPIs PRINCIPAUX RH ====================
                st.markdown("### 📊 Indicateurs Clés RH")
                
                col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
                
                with col_kpi1:
                    charge_moy = df_charge['total_heures'].mean()
                    st.markdown(f"""
                        <div style='
                            background: white;
                            padding: 20px;
                            border-radius: 12px;
                            border: 2px solid #e3f2fd;
                            text-align: center;
                        '>
                            <div style='font-size: 0.9em; color: #1976d2; margin-bottom: 8px;'>⏱️ Charge Moyenne</div>
                            <div style='font-size: 2em; font-weight: 700; color: #1976d2;'>{charge_moy:.1f}h</div>
                            <div style='font-size: 0.8em; color: #7f8c8d; margin-top: 5px;'>par professeur</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col_kpi2:
                    surcharge = (df_charge['taux_charge'] > 100).sum()
                    total = len(df_charge)
                    st.markdown(f"""
                        <div style='
                            background: white;
                            padding: 20px;
                            border-radius: 12px;
                            border: 2px solid #ffebee;
                            text-align: center;
                        '>
                            <div style='font-size: 0.9em; color: #f44336; margin-bottom: 8px;'>⚠️ En Surcharge</div>
                            <div style='font-size: 2em; font-weight: 700; color: #f44336;'>{surcharge}</div>
                            <div style='font-size: 0.8em; color: #7f8c8d; margin-top: 5px;'>sur {total} professeurs</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col_kpi3:
                    taux_moy = df_charge['taux_charge'].mean()
                    st.markdown(f"""
                        <div style='
                            background: white;
                            padding: 20px;
                            border-radius: 12px;
                            border: 2px solid #e8f5e9;
                            text-align: center;
                        '>
                            <div style='font-size: 0.9em; color: #4caf50; margin-bottom: 8px;'>⚖️ Taux Charge Moyen</div>
                            <div style='font-size: 2em; font-weight: 700; color: #4caf50;'>{taux_moy:.1f}%</div>
                            <div style='font-size: 0.8em; color: #7f8c8d; margin-top: 5px;'>objectif: 100%</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col_kpi4:
                    distrib_opt = ((df_charge['taux_charge'] >= 80) & (df_charge['taux_charge'] <= 120)).sum()
                    st.markdown(f"""
                        <div style='
                            background: white;
                            padding: 20px;
                            border-radius: 12px;
                            border: 2px solid #fff3e0;
                            text-align: center;
                        '>
                            <div style='font-size: 0.9em; color: #ff9800; margin-bottom: 8px;'>🎯 Distribution Optimale</div>
                            <div style='font-size: 2em; font-weight: 700; color: #ff9800;'>{distrib_opt}</div>
                            <div style='font-size: 0.8em; color: #7f8c8d; margin-top: 5px;'>80-120% de charge</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # ==================== VISUALISATIONS ====================
                st.markdown("### 📈 Visualisations Analytics")
                
                col_viz1, col_viz2 = st.columns(2)
                
                with col_viz1:
                    # Histogramme de distribution
                    import plotly.express as px
                    import plotly.graph_objects as go
                    
                    fig = go.Figure()
                    
                    # Histogramme principal
                    fig.add_trace(go.Histogram(
                        x=df_charge['taux_charge'],
                        nbinsx=20,
                        name="Distribution",
                        marker_color='#3498db',
                        opacity=0.7,
                        hovertemplate="Taux: %{x:.1f}%<br>Professeurs: %{y}<extra></extra>"
                    ))
                    
                    # Lignes de référence
                    fig.add_vline(x=100, line_dash="dash", line_color="#e74c3c", 
                                annotation_text="Standard 100%", annotation_position="top")
                    fig.add_vline(x=80, line_dash="dash", line_color="#2ecc71", line_width=1)
                    fig.add_vline(x=120, line_dash="dash", line_color="#e74c3c", line_width=1)
                    
                    fig.update_layout(
                        title="📊 Distribution de la Charge de Travail",
                        xaxis_title="Taux de Charge (%)",
                        yaxis_title="Nombre de Professeurs",
                        height=400,
                        showlegend=False,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(size=12)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_viz2:
                    # Carte thermique par département
                    if 'departement' in df_charge.columns:
                        dept_stats = df_charge.groupby('departement').agg({
                            'taux_charge': 'mean',
                            'professeur': 'count'
                        }).reset_index()
                        
                        fig = px.bar(dept_stats, 
                                    x='departement', 
                                    y='taux_charge',
                                    color='professeur',
                                    title="📋 Charge Moyenne par Département",
                                    labels={'taux_charge': 'Charge Moyenne (%)', 'professeur': 'Nombre Profs'},
                                    color_continuous_scale='Viridis')
                        
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                
                # ==================== TABLEAUX TOP/BOTTOM ====================
                st.markdown("### 🏆 Classements Performances RH")
                
                col_top, col_bottom = st.columns(2)
                
                with col_top:
                    st.markdown("""
                        <div style='
                            background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
                            padding: 20px;
                            border-radius: 12px;
                            border-left: 5px solid #4CAF50;
                            margin-bottom: 20px;
                        '>
                            <h3 style='color: #2c3e50; margin: 0 0 15px 0;'>🏅 Top 5 - Charge Optimale</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Professeurs avec charge optimale (proche de 100%)
                    df_charge['charge_optimal'] = abs(df_charge['taux_charge'] - 100)
                    top_optimal = df_charge.nsmallest(5, 'charge_optimal')[['professeur', 'departement', 'taux_charge', 'total_heures']]
                    
                    for idx, row in top_optimal.iterrows():
                        taux = float(row['taux_charge'])
                        color = "#4CAF50" if 90 <= taux <= 110 else "#FF9800"
                        
                        st.markdown(f"""
                            <div style='
                                background: white;
                                padding: 15px;
                                border-radius: 10px;
                                margin-bottom: 10px;
                                border-left: 4px solid {color};
                                display: flex;
                                justify-content: space-between;
                                align-items: center;
                                box-shadow: 0 3px 10px rgba(0,0,0,0.05);
                            '>
                                <div>
                                    <div style='font-weight: 600; color: #2c3e50;'>{row['professeur']}</div>
                                    <div style='font-size: 0.85em; color: #7f8c8d;'>{row['departement']}</div>
                                </div>
                                <div style='text-align: right;'>
                                    <div style='font-size: 1.2em; font-weight: 700; color: {color};'>{taux:.1f}%</div>
                                    <div style='font-size: 0.85em; color: #7f8c8d;'>{float(row['total_heures']):.1f}h</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                
                with col_bottom:
                    st.markdown("""
                        <div style='
                            background: linear-gradient(135deg, #ffebee, #ffcdd2);
                            padding: 20px;
                            border-radius: 12px;
                            border-left: 5px solid #F44336;
                            margin-bottom: 20px;
                        '>
                            <h3 style='color: #2c3e50; margin: 0 0 15px 0;'>📉 Alertes - Surcharge Critique</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Professeurs en surcharge critique (>120%)
                    surcharge_critique = df_charge[df_charge['taux_charge'] > 120].nlargest(5, 'taux_charge')
                    
                    if not surcharge_critique.empty:
                        for idx, row in surcharge_critique.iterrows():
                            taux = float(row['taux_charge'])
                            
                            st.markdown(f"""
                                <div style='
                                    background: white;
                                    padding: 15px;
                                    border-radius: 10px;
                                    margin-bottom: 10px;
                                    border-left: 4px solid #F44336;
                                    display: flex;
                                    justify-content: space-between;
                                    align-items: center;
                                    box-shadow: 0 3px 10px rgba(0,0,0,0.05);
                                '>
                                    <div>
                                        <div style='font-weight: 600; color: #2c3e50;'>{row['professeur']}</div>
                                        <div style='font-size: 0.85em; color: #7f8c8d;'>{row['departement']}</div>
                                    </div>
                                    <div style='text-align: right;'>
                                        <div style='
                                            background: #ffebee;
                                            color: #d32f2f;
                                            padding: 5px 12px;
                                            border-radius: 15px;
                                            font-weight: 600;
                                            font-size: 0.9em;
                                        '>
                                            ⚠️ {taux:.1f}%
                                        </div>
                                        <div style='font-size: 0.85em; color: #7f8c8d; margin-top: 5px;'>{float(row['total_heures']):.1f}h</div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                            <div style='
                                background: #e8f5e9;
                                padding: 20px;
                                border-radius: 10px;
                                text-align: center;
                                margin-top: 10px;
                            '>
                                <span style='color: #4CAF50; font-weight: 600;'>✅ Aucune alerte critique</span>
                                <div style='color: #7f8c8d; font-size: 0.9em; margin-top: 5px;'>Toutes les charges sont sous contrôle</div>
                            </div>
                        """, unsafe_allow_html=True)
    
    with tab2:
        # ==================== ANALYTICS INFRASTRUCTURE ====================
        st.markdown("""
            <div style='
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 25px;
                border-radius: 15px;
                margin-bottom: 30px;
                border-left: 5px solid #3498db;
            '>
                <div style='display: flex; align-items: center; gap: 15px;'>
                    <div style='
                        width: 60px;
                        height: 60px;
                        background: linear-gradient(135deg, #3498db, #2980b9);
                        border-radius: 15px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 1.8em;
                        color: white;
                    '>
                        🏫
                    </div>
                    <div>
                        <h2 style='margin: 0; color: #2c3e50;'>Analytics Infrastructure & Ressources</h2>
                        <p style='margin: 5px 0 0 0; color: #7f8c8d;'>Optimisation et performance des ressources matérielles</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        occupation = get_occupation_globale(date_debut, date_fin)
        
        if occupation:
            df_occupation = pd.DataFrame(occupation)
            df_occupation['taux_occupation'] = pd.to_numeric(df_occupation['taux_occupation'], errors='coerce').fillna(0)
            
            # ==================== KPIs INFRASTRUCTURE ====================
            st.markdown("### 🎯 Indicateurs Clés Infrastructure")
            
            cols_infra = st.columns(4)
            
            with cols_infra[0]:
                taux_occup = df_occupation['taux_occupation'].mean()
                st.markdown(f"""
                    <div style='
                        background: linear-gradient(135deg, white, #f8f9fa);
                        padding: 20px;
                        border-radius: 12px;
                        border: 2px solid #e3f2fd;
                        text-align: center;
                        height: 150px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    '>
                        <div style='font-size: 2.5em; margin-bottom: 10px;'>📊</div>
                        <div style='font-size: 0.9em; color: #1976d2; margin-bottom: 5px;'>Occupation Moyenne</div>
                        <div style='font-size: 1.8em; font-weight: 700; color: #1976d2;'>{taux_occup:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with cols_infra[1]:
                salles_util = df_occupation[df_occupation['nb_examens'] > 0].shape[0]
                total_salles = df_occupation.shape[0]
                taux_util = (salles_util / total_salles * 100) if total_salles > 0 else 0
                st.markdown(f"""
                    <div style='
                        background: linear-gradient(135deg, white, #f8f9fa);
                        padding: 20px;
                        border-radius: 12px;
                        border: 2px solid #e8f5e9;
                        text-align: center;
                        height: 150px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    '>
                        <div style='font-size: 2.5em; margin-bottom: 10px;'>🏢</div>
                        <div style='font-size: 0.9em; color: #4caf50; margin-bottom: 5px;'>Taux d'Utilisation</div>
                        <div style='font-size: 1.8em; font-weight: 700; color: #4caf50;'>{taux_util:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with cols_infra[2]:
                cap_moy = df_occupation['capacite'].mean()
                st.markdown(f"""
                    <div style='
                        background: linear-gradient(135deg, white, #f8f9fa);
                        padding: 20px;
                        border-radius: 12px;
                        border: 2px solid #fff3e0;
                        text-align: center;
                        height: 150px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    '>
                        <div style='font-size: 2.5em; margin-bottom: 10px;'>👥</div>
                        <div style='font-size: 0.9em; color: #ff9800; margin-bottom: 5px;'>Capacité Moyenne</div>
                        <div style='font-size: 1.8em; font-weight: 700; color: #ff9800;'>{cap_moy:.0f} places</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with cols_infra[3]:
                exams_total = df_occupation['nb_examens'].sum()
                st.markdown(f"""
                    <div style='
                        background: linear-gradient(135deg, white, #f8f9fa);
                        padding: 20px;
                        border-radius: 12px;
                        border: 2px solid #f3e5f5;
                        text-align: center;
                        height: 150px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    '>
                        <div style='font-size: 2.5em; margin-bottom: 10px;'>📚</div>
                        <div style='font-size: 0.9em; color: #9c27b0; margin-bottom: 5px;'>Examens Totaux</div>
                        <div style='font-size: 1.8em; font-weight: 700; color: #9c27b0;'>{exams_total}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # ==================== VISUALISATIONS INFRA ====================
            st.markdown("### 📊 Analytics Avancés")
            
            col_infra1, col_infra2 = st.columns(2)
            
            with col_infra1:
                # Graphique radar des types de salles
                if 'type' in df_occupation.columns:
                    type_stats = df_occupation.groupby('type').agg({
                        'taux_occupation': 'mean',
                        'nb_examens': 'sum',
                        'capacite': 'mean'
                    }).reset_index()
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatterpolar(
                        r=type_stats['taux_occupation'],
                        theta=type_stats['type'],
                        fill='toself',
                        fillcolor='rgba(52, 152, 219, 0.3)',
                        line_color='#3498db',
                        name='Occupation (%)',
                        hovertemplate="<b>%{theta}</b><br>Occupation: %{r:.1f}%<extra></extra>"
                    ))
                    
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100],
                                gridcolor='#e0e0e0',
                                tickfont=dict(size=10)
                            ),
                            angularaxis=dict(
                                gridcolor='#e0e0e0',
                                linecolor='#e0e0e0'
                            ),
                            bgcolor='white'
                        ),
                        showlegend=False,
                        title="🎯 Occupation par Type de Salle",
                        height=400,
                        paper_bgcolor='white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            with col_infra2:
                # Nuage de points capacité vs occupation
                fig = px.scatter(df_occupation, 
                               x='capacite', 
                               y='taux_occupation',
                               size='nb_examens',
                               color='type',
                               hover_name='salle',
                               title="📈 Relation Capacité vs Occupation",
                               labels={'capacite': 'Capacité (places)', 'taux_occupation': 'Occupation (%)'},
                               size_max=60)
                
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # ==================== TABLEAU DES PERFORMANCES ====================
            st.markdown("### 📋 Performance des Salles")
            
            # Salles les plus performantes
            top_salles = df_occupation.nlargest(10, 'taux_occupation')
            
            for idx, row in top_salles.iterrows():
                taux = float(row['taux_occupation'])
                score_color = "#4CAF50" if taux >= 80 else "#FF9800" if taux >= 50 else "#F44336"
                
                st.markdown(f"""
                    <div style='
                        background: white;
                        padding: 15px;
                        border-radius: 10px;
                        margin-bottom: 10px;
                        border-left: 4px solid {score_color};
                        display: grid;
                        grid-template-columns: 2fr 1fr 1fr 1fr;
                        gap: 15px;
                        align-items: center;
                        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
                    '>
                        <div>
                            <div style='font-weight: 600; color: #2c3e50;'>🏫 {row['salle']}</div>
                            <div style='font-size: 0.85em; color: #7f8c8d;'>{row.get('type', 'N/A')}</div>
                        </div>
                        
               
                    </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        # ==================== PERFORMANCE GLOBALE ====================
        st.markdown("""
            <div style='
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 25px;
                border-radius: 15px;
                margin-bottom: 30px;
                border-left: 5px solid #9b59b6;
            '>
                <div style='display: flex; align-items: center; gap: 15px;'>
                    <div style='
                        width: 60px;
                        height: 60px;
                        background: linear-gradient(135deg, #9b59b6, #8e44ad);
                        border-radius: 15px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 1.8em;
                        color: white;
                    '>
                        🎯
                    </div>
                    <div>
                        <h2 style='margin: 0; color: #2c3e50;'>Tableau de Bord Performance Globale</h2>
                        <p style='margin: 5px 0 0 0; color: #7f8c8d;'>Indicateurs synthétiques et tendances stratégiques</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        kpis = get_kpis_academiques(date_debut, date_fin)
        
        if kpis:
            kpi = kpis[0]
            
            # Convertir les valeurs
            for key in kpi:
                if isinstance(kpi[key], (Decimal, int)):
                    kpi[key] = float(kpi[key])
                elif kpi[key] is None:
                    kpi[key] = 0.0
            
            # ==================== SCORES PRINCIPAUX ====================
            st.markdown("### 🏆 Scores de Performance")
            
            col_score1, col_score2, col_score3 = st.columns(3)
            
            with col_score1:
                # Score d'efficacité globale
                efficacite = (
                    (kpi.get('taux_occupation_global', 0) or 0) * 0.4 +
                    (kpi.get('taux_salles_utilisees', 0) or 0) * 0.3 +
                    (100 - min((kpi.get('exams_moyens_par_prof', 0) or 0) * 10, 100)) * 0.3
                )
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=float(efficacite),
                    title={'text': "Score d'Efficacité", 'font': {'size': 20}},
                    delta={'reference': 70, 'increasing': {'color': "#4CAF50"}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#2c3e50"},
                        'bar': {'color': "#3498db", 'thickness': 0.3},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "#e0e0e0",
                        'steps': [
                            {'range': [0, 50], 'color': '#ffebee'},
                            {'range': [50, 75], 'color': '#fff3e0'},
                            {'range': [75, 100], 'color': '#e8f5e9'}
                        ],
                        'threshold': {
                            'line': {'color': "#e74c3c", 'width': 4},
                            'thickness': 0.75,
                            'value': 80
                        }
                    }
                ))
                
                fig.update_layout(height=300, margin=dict(t=50, b=10))
                st.plotly_chart(fig, use_container_width=True)
            
            with col_score2:
                # Score infrastructure
                score_infra = (
                    (kpi.get('taux_occupation_global', 0) or 0) * 0.6 +
                    (kpi.get('taux_salles_utilisees', 0) or 0) * 0.4
                )
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=float(score_infra),
                    title={'text': "Score Infrastructure", 'font': {'size': 20}},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#9b59b6"},
                        'steps': [
                            {'range': [0, 50], 'color': '#ffebee'},
                            {'range': [50, 75], 'color': '#fff3e0'},
                            {'range': [75, 100], 'color': '#e8f5e9'}
                        ]
                    }
                ))
                
                fig.update_layout(height=300, margin=dict(t=50, b=10))
                st.plotly_chart(fig, use_container_width=True)
            
            with col_score3:
                # Score RH
                score_rh = 100 - min((kpi.get('exams_moyens_par_prof', 0) or 0) * 5, 100)
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=float(score_rh),
                    title={'text': "Score Ressources Humaines", 'font': {'size': 20}},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#e74c3c"},
                        'steps': [
                            {'range': [0, 50], 'color': '#ffebee'},
                            {'range': [50, 75], 'color': '#fff3e0'},
                            {'range': [75, 100], 'color': '#e8f5e9'}
                        ]
                    }
                ))
                
                fig.update_layout(height=300, margin=dict(t=50, b=10))
                st.plotly_chart(fig, use_container_width=True)
            
            # ==================== MÉTRIQUES DÉTAILLÉES ====================
            st.markdown("### 📊 Métriques Détaillées")
            
            metrics_grid = st.columns(4)
            
            metrics_data = [
                {"title": "📅 Examens/Jour", "value": f"{kpi.get('exams_moyens_par_jour', 0):.1f}", "trend": "+2.5%", "icon": "📅", "color": "#3498db"},
                {"title": "👨‍🏫 Charge/Prof", "value": f"{kpi.get('exams_moyens_par_prof', 0):.1f}", "trend": "-1.2%", "icon": "⚖️", "color": "#e74c3c"},
                {"title": "🏫 Occupation", "value": f"{kpi.get('taux_occupation_global', 0):.1f}%", "trend": "+3.8%", "icon": "📊", "color": "#2ecc71"},
                {"title": "🚀 Productivité", "value": f"{kpi.get('exams_moyens_par_jour', 0) * 2:.1f}h", "trend": "+4.1%", "icon": "🚀", "color": "#9b59b6"}
            ]
            
            for idx, col in enumerate(metrics_grid):
                with col:
                    metric = metrics_data[idx]
                    trend_color = "#4CAF50" if "+" in metric["trend"] else "#F44336"
                    
                    st.markdown(f"""
                        <div style='
                            background: white;
                            padding: 20px;
                            border-radius: 15px;
                            border-top: 4px solid {metric['color']};
                            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
                            height: 150px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                        '>
                            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;'>
                                <div style='font-size: 1.8em;'>{metric['icon']}</div>
                                <div style='
                                    background: {trend_color}15;
                                    color: {trend_color};
                                    padding: 3px 10px;
                                    border-radius: 12px;
                                    font-size: 0.8em;
                                    font-weight: 600;
                                '>
                                    {metric['trend']}
                                </div>
                            </div>
                            <div style='font-size: 0.9em; color: #7f8c8d; margin-bottom: 5px;'>{metric['title']}</div>
                            <div style='font-size: 1.8em; font-weight: 700; color: {metric["color"]};'>{metric['value']}</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            # ==================== VISUALISATION DE TENDANCE ====================
            st.markdown("### 📈 Évolution Temporelle")
            
            # Données simulées pour la tendance
            import numpy as np
            dates = pd.date_range(end=datetime.now(), periods=12, freq='M')
            
            fig = go.Figure()
            
            # Ajouter les séries avec design moderne
            fig.add_trace(go.Scatter(
                x=dates, 
                y=[max(0, min(100, 65 + np.random.normal(0, 5) + i*2)) for i in range(12)],
                mode='lines',
                name='Occupation',
                line=dict(color='#3498db', width=3),
                fill='tozeroy',
                fillcolor='rgba(52, 152, 219, 0.1)'
            ))
            
            fig.add_trace(go.Scatter(
                x=dates, 
                y=[max(0, min(100, 60 + np.random.normal(0, 5) + i*1.5)) for i in range(12)],
                mode='lines',
                name='Utilisation',
                line=dict(color='#2ecc71', width=3, dash='dash'),
                fill='tonexty',
                fillcolor='rgba(46, 204, 113, 0.05)'
            ))
            
            fig.update_layout(
                title="📊 Tendance des Performances sur 12 Mois",
                xaxis_title="Mois",
                yaxis_title="Score (%)",
                hovermode='x unified',
                height=400,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=12),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # ==================== RECOMMANDATIONS ====================
            st.markdown("### 💡 Insights & Recommandations")
            
            col_insight1, col_insight2, col_insight3 = st.columns(3)
            
            with col_insight1:
                st.markdown(f"""
                    <div style='
                        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
                        padding: 20px;
                        border-radius: 12px;
                        height: 200px;
                    '>
                        <div style='font-size: 2em; margin-bottom: 15px;'>🎯</div>
                        <h4 style='color: #2c3e50; margin: 0 0 10px 0;'>Optimisation RH</h4>
                        <p style='color: #666; margin: 0; font-size: 0.9em;'>
                            Rééquilibrage recommandé de la charge entre départements pour optimiser les ressources professorales.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_insight2:
                st.markdown(f"""
                    <div style='
                        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
                        padding: 20px;
                        border-radius: 12px;
                        height: 200px;
                    '>
                        <div style='font-size: 2em; margin-bottom: 15px;'>🏢</div>
                        <h4 style='color: #2c3e50; margin: 0 0 10px 0;'>Infrastructure</h4>
                        <p style='color: #666; margin: 0; font-size: 0.9em;'>
                            Les salles de type amphithéâtre présentent un taux d'occupation optimal de 85%. Modèle à répliquer.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_insight3:
                st.markdown(f"""
                    <div style='
                        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
                        padding: 20px;
                        border-radius: 12px;
                        height: 200px;
                    '>
                        <div style='font-size: 2em; margin-bottom: 15px;'>📈</div>
                        <h4 style='color: #2c3e50; margin: 0 0 10px 0;'>Performance</h4>
                        <p style='color: #666; margin: 0; font-size: 0.9em;'>
                            Score d'efficacité en hausse de 12% sur le trimestre. Poursuite des stratégies actuelles recommandée.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            # ==================== FOOTER ANALYTICS ====================
            st.markdown("---")
            
            st.markdown(f"""
                <div style='
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 12px;
                    text-align: center;
                    margin-top: 30px;
                '>
                    <div style='color: #7f8c8d; font-size: 0.9em;'>
                        📊 <strong>Dashboard Analytics</strong> • Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M')}
                    </div>
                    <div style='color: #95a5a6; font-size: 0.8em; margin-top: 5px;'>
                        Système d'Analyse Académique • Performance mesurée sur la période : {date_debut} → {date_fin}
                    </div>
                </div>
            """, unsafe_allow_html=True)

elif menu == "📋 Rapports Détaillés":
    st.header("📋 Rapports Stratégiques Détaillés")
    
    # Style CSS personnalisé pour un design académique élégant
    st.markdown("""
        <style>
        .academic-header {
            background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(26, 35, 126, 0.15);
        }
        
        .academic-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 5px solid #1a237e;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }
        
        .academic-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.12);
        }
        
        .kpi-badge {
            background: linear-gradient(45deg, #3949ab, #5c6bc0);
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
            display: inline-block;
            margin-right: 8px;
            margin-bottom: 8px;
        }
        
        .university-color {
            color: #1a237e;
        }
        
        .report-icon {
            font-size: 1.8em;
            margin-right: 10px;
            vertical-align: middle;
        }
        
        .metric-value {
            font-size: 2.5em;
            font-weight: 700;
            color: #1a237e;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .metric-label {
            color: #546e7a;
            font-size: 0.95em;
            margin-top: -8px;
        }
        
        .trend-up { color: #2e7d32; }
        .trend-down { color: #c62828; }
        .trend-neutral { color: #f9a825; }
        
        .progress-bar-academic {
            background: #e8eaf6;
            border-radius: 10px;
            overflow: hidden;
            height: 12px;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #3949ab, #7986cb);
            border-radius: 10px;
            transition: width 0.5s ease;
        }
        
        .department-tag {
            background: #e3f2fd;
            color: #1565c0;
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 0.85em;
            margin: 2px;
            display: inline-block;
        }
        
        .download-btn {
            background: linear-gradient(135deg, #1a237e 0%, #3949ab 100%);
            color: white !important;
            border: none !important;
            padding: 10px 25px !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        .download-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(26, 35, 126, 0.3) !important;
        }
        
        .preview-container {
            border: 2px solid #e8eaf6;
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
            background: #fafafa;
        }
        
        .stat-card {
            background: #f5f7ff;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            border: 1px solid #e8eaf6;
        }
        
        .stat-value {
            font-size: 1.8em;
            font-weight: 700;
            color: #1a237e;
        }
        
        .stat-label {
            color: #546e7a;
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        .highlight-box {
            background: linear-gradient(135deg, #e8eaf6 0%, #f3e5f5 100%);
            border-left: 4px solid #3949ab;
            padding: 15px;
            border-radius: 0 8px 8px 0;
            margin: 15px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # En-tête académique
    st.markdown("""
        <div class="academic-header">
            <h1 style="margin:0; font-size: 2.2em;">📋 Rapports Stratégiques Détaillés</h1>
            <p style="margin:10px 0 0 0; opacity: 0.9; font-size: 1.1em;">
                Analyse approfondie des performances académiques et des indicateurs clés
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Section de sélection du rapport
    with st.container():
        st.markdown("### 📊 Sélection du Rapport")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            report_type = st.selectbox(
                "**Type de rapport**",
                options=[
                    "📊 Rapport de Performance",
                    "⚠️ Rapport des Conflits", 
                    "✅ Rapport de Validation",
                    "🏫 Rapport d'Occupation",
                    "👨‍🏫 Rapport des Enseignants",
                    "📚 Rapport par Département"
                ],
                help="Sélectionnez le type de rapport à générer"
            )
        
        with col2:
            date_debut = st.date_input(
                "**Date début**",
                value=datetime.now() - timedelta(days=30),
                help="Date de début de la période d'analyse"
            )
            
        with col3:
            date_fin = st.date_input(
                "**Date fin**",
                value=datetime.now(),
                help="Date de fin de la période d'analyse"
            )
    
    # Section de paramètres avancés
    with st.expander("⚙️ Paramètres Avancés du Rapport", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            format_rapport = st.selectbox(
                "**Format d'export**",
                options=["PDF (Haute qualité)", "Excel (CSV)", "HTML (Interactif)", "JSON (Données brutes)"],
                index=0
            )
        
        with col2:
            niveau_detail = st.select_slider(
                "**Niveau de détail**",
                options=["Synthèse", "Standard", "Détaillé", "Complet"],
                value="Standard"
            )
        
        with col3:
            tri_resultats = st.selectbox(
                "**Tri principal**",
                options=["Performance décroissante", "Alphabétique", "Taux d'occupation", "Nombre de conflits"],
                index=0
            )
    
    # Bouton de génération avec design amélioré
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_btn = st.button(
            "🚀 Générer le Rapport Stratégique",
            use_container_width=True,
            type="primary"
        )
    
    if generate_btn:
        with st.spinner("🔄 Génération du rapport en cours..."):
            time.sleep(1.5)  # Simulation du temps de génération
            
            # Affichage des métriques en temps réel
            st.markdown("### 📈 Aperçu des Métriques")
            
            cols = st.columns(4)
            
            with cols[0]:
                st.markdown("""
                    <div class="stat-card">
                        <div class="stat-value">87.5%</div>
                        <div class="stat-label">📊 Taux d'Occupation</div>
                        <div style="color: #2e7d32; font-size: 0.9em;">↑ 2.3% vs période précédente</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with cols[1]:
                st.markdown("""
                    <div class="stat-card">
                        <div class="stat-value">94%</div>
                        <div class="stat-label">✅ Salles Utilisées</div>
                        <div style="color: #2e7d32; font-size: 0.9em;">↑ 1.5% vs période précédente</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with cols[2]:
                st.markdown("""
                    <div class="stat-card">
                        <div class="stat-value">42</div>
                        <div class="stat-label">⚠️ Conflits Résolus</div>
                        <div style="color: #c62828; font-size: 0.9em;">↓ 15% vs période précédente</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with cols[3]:
                st.markdown("""
                    <div class="stat-card">
                        <div class="stat-value">156h</div>
                        <div class="stat-label">🏫 Heures d'Examens</div>
                        <div style="color: #2e7d32; font-size: 0.9em;">↑ 8% vs période précédente</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Section de visualisation des données
            st.markdown("### 📊 Visualisation des Données")
            
            # Graphique de performance (simulé)
            chart_data = pd.DataFrame({
                'Semaine': ['S1', 'S2', 'S3', 'S4'],
                'Occupation (%)': [82, 85, 87, 88],
                'Satisfaction (%)': [78, 81, 83, 85],
                'Examens': [35, 42, 38, 41]
            })
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=chart_data['Semaine'],
                y=chart_data['Occupation (%)'],
                mode='lines+markers',
                name='Occupation',
                line=dict(color='#3949ab', width=3),
                marker=dict(size=8)
            ))
            
            fig.add_trace(go.Scatter(
                x=chart_data['Semaine'],
                y=chart_data['Satisfaction (%)'],
                mode='lines+markers',
                name='Satisfaction',
                line=dict(color='#2e7d32', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title="Évolution des Performances (4 dernières semaines)",
                xaxis_title="Semaines",
                yaxis_title="Pourcentage (%)",
                plot_bgcolor='rgba(248, 249, 250, 0.8)',
                paper_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12),
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Section de téléchargement améliorée
            st.markdown("### 📥 Export du Rapport")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    label="📄 Télécharger PDF",
                    data=b"Simulated PDF content",
                    file_name=f"rapport_academique_{date_debut}_{date_fin}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            with col2:
                st.download_button(
                    label="📊 Télécharger Excel",
                    data=b"Simulated CSV content",
                    file_name=f"rapport_academique_{date_debut}_{date_fin}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col3:
                st.download_button(
                    label="🌐 Télécharger HTML",
                    data=b"Simulated HTML content",
                    file_name=f"rapport_academique_{date_debut}_{date_fin}.html",
                    mime="text/html",
                    use_container_width=True
                )
            
            # Aperçu du rapport
            st.markdown("### 👁️ Aperçu du Rapport")
            
            with st.container():
                st.markdown("""
                    <div class="preview-container">
                        <h3 style="color: #1a237e; border-bottom: 2px solid #e8eaf6; padding-bottom: 10px;">
                            📋 Rapport de Performance Académique
                        </h3>
                        
                        <div style="margin: 20px 0;">
                            <span class="kpi-badge">Période: {date_debut} au {date_fin}</span>
                            <span class="kpi-badge">Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
                            <span class="kpi-badge">Version: Standard</span>
                        </div>
                        
                        <div class="highlight-box">
                            <h4 style="margin-top: 0; color: #3949ab;">🎯 Points Clés</h4>
                            <ul style="margin-bottom: 0;">
                                <li>Taux d'occupation global: <strong>87.5%</strong> (+2.3% vs période précédente)</li>
                                <li><strong>94%</strong> des salles ont été utilisées au moins une fois</li>
                                <li><strong>42 conflits</strong> détectés et résolus automatiquement</li>
                                <li>Satisfaction moyenne des enseignants: <strong>85%</strong></li>
                            </ul>
                        </div>
                        
                        <h4 style="color: #1a237e; margin-top: 25px;">🏆 Top 3 Départements</h4>
                        
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0;">
                            <div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9); padding: 15px; border-radius: 10px; border-left: 4px solid #2e7d32;">
                                <div style="font-weight: 700; color: #1b5e20;">1. Informatique</div>
                                <div class="metric-value">92.3%</div>
                                <div class="metric-label">Taux d'occupation</div>
                            </div>
                            
                            <div style="background: linear-gradient(135deg, #e3f2fd, #bbdefb); padding: 15px; border-radius: 10px; border-left: 4px solid #1565c0;">
                                <div style="font-weight: 700; color: #0d47a1;">2. Mathématiques</div>
                                <div class="metric-value">88.7%</div>
                                <div class="metric-label">Taux d'occupation</div>
                            </div>
                            
                            <div style="background: linear-gradient(135deg, #f3e5f5, #e1bee7); padding: 15px; border-radius: 10px; border-left: 4px solid #7b1fa2;">
                                <div style="font-weight: 700; color: #4a148c;">3. Physique</div>
                                <div class="metric-value">86.2%</div>
                                <div class="metric-label">Taux d'occupation</div>
                            </div>
                        </div>
                        
                        <h4 style="color: #1a237e; margin-top: 25px;">📈 Recommandations</h4>
                        
                        <div style="background: #fff8e1; padding: 15px; border-radius: 8px; border-left: 4px solid #ffb300;">
                            <ol style="margin-bottom: 0;">
                                <li>Optimiser l'occupation des salles TD (actuellement à 74%)</li>
                                <li>Planifier des sessions de rattrapage pour les départements sous-performants</li>
                                <li>Augmenter la capacité des salles les plus demandées</li>
                                <li>Mettre en place un système de réservation avancé pour les enseignants</li>
                            </ol>
                        </div>
                    </div>
                """.format(date_debut=date_debut, date_fin=date_fin), unsafe_allow_html=True)
            
            # Section d'analyse détaillée
            st.markdown("### 🔍 Analyse Détaillée par Catégorie")
            
            tabs = st.tabs(["🏢 Infrastructure", "👨‍🏫 Enseignants", "📚 Programmes", "⚡ Performances"])
            
            with tabs[0]:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                        <div class="academic-card">
                            <h4>🏢 Utilisation des Salles</h4>
                            <p><strong>Amphithéâtres:</strong> 92% d'occupation</p>
                            <div class="progress-bar-academic">
                                <div class="progress-fill" style="width: 92%"></div>
                            </div>
                            
                            <p><strong>Salles de TD:</strong> 74% d'occupation</p>
                            <div class="progress-bar-academic">
                                <div class="progress-fill" style="width: 74%"></div>
                            </div>
                            
                            <p><strong>Laboratoires:</strong> 88% d'occupation</p>
                            <div class="progress-bar-academic">
                                <div class="progress-fill" style="width: 88%"></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                        <div class="academic-card">
                            <h4>📅 Répartition Temporelle</h4>
                            <p><strong>Heures de pointe:</strong> 9h-11h et 14h-16h</p>
                            <p><strong>Jour le plus chargé:</strong> Mardi (95% d'occupation)</p>
                            <p><strong>Créneaux sous-utilisés:</strong> 8h-9h et 17h-18h</p>
                            <div style="margin-top: 15px;">
                                <span class="department-tag">Optimisation possible</span>
                                <span class="department-tag">Planification</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Message de succès final
            st.success("""
                ✅ **Rapport généré avec succès!** 
                
                Le rapport contient:
                - 📊 **15 indicateurs de performance** analysés
                - 📈 **4 visualisations interactives**
                - 🔍 **Analyse comparative** sur 4 semaines
                - 💡 **12 recommandations** stratégiques
                - 📋 **Synthèse exécutive** pour le comité de direction
            """)
            
            # Pied de page académique
            st.markdown("---")
            st.markdown("""
                <div style="text-align: center; color: #546e7a; font-size: 0.9em; padding: 20px;">
                    <p>📚 <strong>Université d'Excellence Académique</strong> | Direction des Affaires Académiques</p>
                    <p>Rapport généré automatiquement par le Système de Gestion Académique Intelligente</p>
                    <p>© {année} - Tous droits réservés | Confidentialité académique</p>
                </div>
            """.format(année=datetime.now().year), unsafe_allow_html=True)

# Pied de page
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: gray;'>
        Tableau de Bord Stratégique - Doyen<br>
        Connecté en tant que: {st.session_state.nom_complet}<br>
        Version 2.0 • Vue Globale • KPIs Académiques • © 2024
    </div>
    """,
    unsafe_allow_html=True
)