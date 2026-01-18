# app_etudiant.py
import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import calendar

# Configuration de la page
st.set_page_config(
    page_title="UniSchedule - Portail Étudiant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour l'interface moderne
st.markdown("""
<style>
    /* Styles généraux */
    .main {
        background-color: #f9f9fb;
    }
    
    /* Sidebar styles */
    .sidebar .sidebar-content {
        background-color: #1f2c3a;
        color: white;
    }
    
    /* Cacher la navigation des pages */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* Titres */
    h1, h2, h3 {
        color: #1f2c3a;
        font-weight: 600;
    }
    
    /* Cartes de métriques */
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid #3498db;
    }
    
    /* Boutons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Tableaux */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .dataframe th {
        background-color: #3498db;
        color: white;
        font-weight: 600;
    }
    
    .dataframe td {
        border-bottom: 1px solid #eaeaea;
    }
    
    /* Badges de session */
    .badge-normal {
        background-color: #2ecc71;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: 500;
    }
    
    .badge-rattrapage {
        background-color: #e67e22;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: 500;
    }
    
    /* Export buttons */
    .export-btn {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .export-btn:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    /* Améliorations sidebar */
    .sidebar-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .filter-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .info-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin-top: 2rem;
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
            cursor.close()
            return result
        else:
            conn.commit()
            cursor.close()
            return True
    except Error as e:
        st.error(f"Erreur SQL: {e}")
        return None

# Fonctions pour les étudiants
def get_departements():
    """Récupère tous les départements"""
    return run_query("SELECT DISTINCT id, nom FROM departements ORDER BY nom")

def get_formations_par_departement(dept_id):
    """Récupère les formations d'un département spécifique"""
    query = """
        SELECT DISTINCT id, nom 
        FROM formations 
        WHERE dept_id = %s 
        ORDER BY nom
    """
    return run_query(query, (dept_id,))

def get_examens_formation(formation_id, date_debut, date_fin):
    """Récupère tous les examens confirmés d'une formation"""
    query = """
        SELECT DISTINCT
            e.id,
            e.date_examen,
            TIME_FORMAT(e.heure_debut, '%H:%i') as heure_debut,  # ADD THIS
            TIME_FORMAT(e.heure_fin, '%H:%i') as heure_fin,      # ADD THIS
            e.duree_minutes,
            e.session,
            m.nom as module,
            m.credits,
            CONCAT(p.nom, ' ', p.prenom) as professeur,
            le.nom as salle,
            le.type as type_salle,
            le.capacite,
            COUNT(DISTINCT i.etudiant_id) as nb_etudiants,
            ROUND((COUNT(DISTINCT i.etudiant_id) / NULLIF(le.capacite, 0)) * 100, 1) as taux_occupation
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        LEFT JOIN professeurs p ON e.professeur_id = p.id
        JOIN lieu_examen le ON e.salle_id = le.id
        LEFT JOIN inscriptions i ON m.id = i.module_id AND i.annee_scolaire = e.annee_scolaire
        WHERE f.id = %s
        AND e.statut = 'confirmé'
        AND e.date_examen BETWEEN %s AND %s
        GROUP BY e.id, e.date_examen, e.heure_debut, e.heure_fin, m.nom, p.nom, p.prenom, le.nom
        ORDER BY e.date_examen, e.heure_debut
    """
    return run_query(query, (formation_id, date_debut, date_fin))

# Initialisation de session state
if 'selected_dept_id' not in st.session_state:
    st.session_state.selected_dept_id = None
if 'selected_formation_id' not in st.session_state:
    st.session_state.selected_formation_id = None

# Sidebar pour les filtres - VERSION CORRIGÉE
with st.sidebar:
    # En-tête stylée unique
    st.markdown("""
    <div class="sidebar-section">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 2.5rem;">🎓</div>
            <div>
                <h1 style="color: white; margin: 0; font-size: 1.5rem; font-weight: 700;">UniSchedule</h1>
                <p style="color: rgba(255, 255, 255, 0.9); margin: 0.2rem 0 0 0; font-size: 0.9rem;">Portail Étudiant</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Section de filtres
    st.markdown("""
    <div class="filter-card">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
            <span style="font-size: 1.2rem;">🎯</span>
            <h3 style="margin: 0; color: #2d3748; font-weight: 600;">Filtres de Recherche</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Récupérer les départements
    departements = get_departements()
    
    if not departements:
        st.error("⚠️ Aucun département trouvé dans la base de données")
        st.stop()
    
    # Créer dictionnaire département
    dept_options = {}
    for dept in departements:
        if dept['nom'] not in dept_options.values():
            dept_options[dept['id']] = dept['nom']
    
    # Sélection du département
    selected_dept_nom = st.selectbox(
        "**Département**",
        options=list(dept_options.values()),
        key="dept_select",
        help="Sélectionnez votre département"
    )
    
    # Trouver l'ID correspondant
    selected_dept_id = None
    for dept_id, dept_nom in dept_options.items():
        if dept_nom == selected_dept_nom:
            selected_dept_id = dept_id
            break
    
    # Divider stylé
    st.markdown('<hr style="margin: 1.5rem 0; border: none; height: 1px; background: linear-gradient(90deg, transparent, #667eea, transparent);">', unsafe_allow_html=True)
    
    # Récupérer les formations pour le département sélectionné
    if selected_dept_id:
        formations = get_formations_par_departement(selected_dept_id)
        
        if not formations:
            st.warning("Aucune formation disponible pour ce département")
            selected_formation_nom = None
            selected_formation_id = None
        else:
            formation_options = {}
            for formation in formations:
                if formation['nom'] not in formation_options.values():
                    formation_options[formation['id']] = formation['nom']
            
            selected_formation_nom = st.selectbox(
                "**Formation**",
                options=list(formation_options.values()),
                key="formation_select",
                help="Sélectionnez votre formation"
            )
            
            # Trouver l'ID correspondant
            selected_formation_id = None
            for formation_id, formation_nom in formation_options.items():
                if formation_nom == selected_formation_nom:
                    selected_formation_id = formation_id
                    break
    
    # Section période - UNE SEULE FOIS
    st.markdown('<hr style="margin: 1.5rem 0; border: none; height: 1px; background: linear-gradient(90deg, transparent, #667eea, transparent);">', unsafe_allow_html=True)
    
    st.markdown("**📅 Période de Recherche**")
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("Début", 
                                  datetime.now(), 
                                  key="date_debut",
                                  help="Date de début de recherche")
    with col2:
        date_fin = st.date_input("Fin", 
                                datetime.now() + timedelta(days=30), 
                                key="date_fin",
                                help="Date de fin de recherche")
    
    # Mode d'affichage
    st.markdown('<hr style="margin: 1.5rem 0; border: none; height: 1px; background: linear-gradient(90deg, transparent, #667eea, transparent);">', unsafe_allow_html=True)
    
    st.markdown("**📋 Mode d'Affichage**")
    display_mode = st.radio(
        "",
        ["📊 Tableau", "📅 Calendrier"],
        index=0,
        key="display_mode",
        label_visibility="collapsed"
    )
    
    # Fermer le div de section filtres
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Boutons d'action
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔍 Rechercher", 
                    type="primary", 
                    use_container_width=True,
                    help="Rechercher les examens selon les critères"):
            st.session_state.selected_dept_id = selected_dept_id
            st.session_state.selected_formation_id = selected_formation_id
            st.rerun()
    
    with col_btn2:
        if st.button("🔄 Réinitialiser", 
                    use_container_width=True,
                    help="Réinitialiser tous les filtres"):
            st.session_state.clear()
            st.rerun()
    
    # Section d'informations courantes
    if selected_dept_nom and selected_formation_nom:
        st.markdown("""
        <div class="info-card">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                <span style="font-size: 1.1rem;">ℹ️</span>
                <h4 style="margin: 0; color: #2d3748; font-size: 0.95rem; font-weight: 600;">Sélection Actuelle</h4>
            </div>
            <div style="color: #718096; font-size: 0.85rem; line-height: 1.4;">
                <p style="margin: 0.5rem 0;">
                    <span style="color: #667eea; font-weight: 500;">📁 Département :</span><br>
                    {dept}
                </p>
                <p style="margin: 0.5rem 0;">
                    <span style="color: #667eea; font-weight: 500;">🎓 Formation :</span><br>
                    {formation}
                </p>
                <p style="margin: 0.5rem 0;">
                    <span style="color: #667eea; font-weight: 500;">📅 Période :</span><br>
                    {debut} - {fin}
                </p>
            </div>
        </div>
        """.format(
            dept=selected_dept_nom,
            formation=selected_formation_nom,
            debut=date_debut.strftime('%d/%m/%Y'),
            fin=date_fin.strftime('%d/%m/%Y')
        ), unsafe_allow_html=True)
        col_act1, col_act2 = st.columns(2)
    with col_act1:
        if st.button("EXIT", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("app.py")

    # Pied de page
    st.markdown("""
    <div style="margin-top: 2rem; text-align: center; color: #a0aec0; font-size: 0.75rem;">
        <hr style="margin-bottom: 1rem; border: none; height: 1px; background: #e2e8f0;">
        <p style="margin: 0.25rem 0;">UniSchedule v2.0</p>
        <p style="margin: 0.25rem 0;">© 2024 Université</p>
        <p style="margin: 0.25rem 0; font-size: 0.7rem;">Portail Étudiant</p>
    </div>
    """, unsafe_allow_html=True)

# Main content area
st.markdown("## 📅 Consultation des Emplois du Temps")

# Vérifier si une formation est sélectionnée
if not st.session_state.get('selected_formation_id'):
    st.info("👈 Veuillez sélectionner un département et une formation dans la sidebar pour commencer.")
    st.markdown("""
    ### Instructions :
    1. Sélectionnez votre **Département** dans le menu déroulant
    2. Choisissez votre **Formation**
    3. Définissez la **Période** souhaitée
    4. Sélectionnez le **Mode d'affichage** (Tableau ou Calendrier)
    5. Cliquez sur **🔍 Rechercher** pour afficher les résultats
    
    ---
    
    **Fonctionnalités disponibles :**
    - 📊 **Affichage Tableau** : Vue détaillée sous forme de tableau
    - 📅 **Affichage Calendrier** : Vue organisée par jour
    - 📤 **Export** : Téléchargement des données en CSV, HTML
    - 🔍 **Filtrage** : Recherche par période et formation
    """)
    st.stop()

# Utiliser les valeurs de session state
selected_formation_id = st.session_state.selected_formation_id

# Récupérer les informations de la formation
formation_info = run_query("""
    SELECT DISTINCT f.nom as formation, d.nom as departement 
    FROM formations f
    JOIN departements d ON f.dept_id = d.id
    WHERE f.id = %s
""", (selected_formation_id,))

if not formation_info:
    st.error("Formation non trouvée")
    st.stop()

info = formation_info[0]

# En-tête principal
st.markdown(f"""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 30px; 
            border-radius: 15px; 
            color: white; 
            margin-bottom: 30px;'>
    <h1 style='color: white; margin-bottom: 10px;'>{info['formation']}</h1>
    <div style='display: flex; gap: 20px; flex-wrap: wrap;'>
        <div style='display: flex; align-items: center; gap: 8px;'>
            <span>📚</span>
            <span>{info['departement']}</span>
        </div>
        <div style='display: flex; align-items: center; gap: 8px;'>
            <span>📅</span>
            <span>{date_debut.strftime('%d/%m/%Y')} - {date_fin.strftime('%d/%m/%Y')}</span>
        </div>
        <div style='display: flex; align-items: center; gap: 8px;'>
            <span>👥</span>
            <span>Portail Étudiant</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Récupérer les examens
examens = get_examens_formation(selected_formation_id, date_debut, date_fin)

if examens:
    df_examens = pd.DataFrame(examens)
    df_examens = df_examens.drop_duplicates(subset=['id', 'date_examen', 'heure_debut', 'module'])
    
    # Métriques résumées
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("📋", "Examens", len(df_examens)),
        ("📅", "Jours d'examens", df_examens['date_examen'].nunique()),
        ("🏫", "Salles utilisées", df_examens['salle'].nunique()),
        ("👥", "Total étudiants", df_examens['nb_etudiants'].sum())
    ]
    
    for i, (icon, label, value) in enumerate(metrics):
        with [col1, col2, col3, col4][i]:
            st.markdown(f"""
            <div class='metric-card'>
                <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 10px;'>
                    <div style='font-size: 24px;'>{icon}</div>
                    <div>
                        <div style='font-size: 12px; color: #666;'>{label}</div>
                        <div style='font-size: 24px; font-weight: 700; color: #1f2c3a;'>{value}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Afficher selon le mode sélectionné
    if display_mode == "📊 Tableau":
        st.markdown("### 📋 Tableau des Examens")
        
        # Préparer le DataFrame pour l'affichage
        df_display = df_examens.copy()
        df_display['date_examen'] = pd.to_datetime(df_display['date_examen']).dt.strftime('%d/%m/%Y')
        
        # Formater les colonnes
        df_display['Module'] = df_display.apply(
            lambda x: f"**{x['module']}**\n({x['credits']} crédits)", 
            axis=1
        )
        
        df_display['Professeur'] = df_display.apply(
            lambda x: f"👨‍🏫 {x['professeur']}" if pd.notna(x['professeur']) else "👨‍🏫 Non assigné", 
            axis=1
        )
        
        df_display['Salle'] = df_display.apply(
            lambda x: f"🏫 {x['salle']}\n({x['type_salle']})", 
            axis=1
        )
        
        # Fonction de coloration pour la session
        def color_session(session):
            if session == 'Normale':
                return 'background-color: #2ecc71; color: white; padding: 4px 8px; border-radius: 12px;'
            else:
                return 'background-color: #e67e22; color: white; padding: 4px 8px; border-radius: 12px;'
        
        # Afficher le tableau stylisé
        st.dataframe(
            df_display.rename(columns={
                'date_examen': 'Date',
                'heure_debut': 'Heure début',
                'heure_fin': 'Heure fin',
                'session': 'Session'
            })[['Date', 'Heure début', 'Heure fin', 'Module', 'Professeur', 'Salle', 'Session']],
            column_config={
                "Date": st.column_config.TextColumn(width="small"),
                "Heure début": st.column_config.TextColumn(width="small"),
                "Heure fin": st.column_config.TextColumn(width="small"),
                "Module": st.column_config.TextColumn(width="large"),
                "Professeur": st.column_config.TextColumn(width="medium"),
                "Salle": st.column_config.TextColumn(width="medium"),
                "Session": st.column_config.Column(
                    width="small",
                    help="Session normale ou rattrapage"
                )
            },
            use_container_width=True,
            hide_index=True
        )
    
    elif display_mode == "📅 Calendrier":
        st.markdown("### 📅 Vue Calendrier")
        
        if not df_examens.empty:
            df_examens['date_examen'] = pd.to_datetime(df_examens['date_examen'])
            dates_uniques = sorted(df_examens['date_examen'].unique())
            
            for date in dates_uniques:
                df_date = df_examens[df_examens['date_examen'] == date]
                jour_nom = calendar.day_name[date.weekday()]
                jour_num = date.strftime('%d/%m/%Y')
                
                with st.expander(f"📅 {jour_nom} {jour_num} - {len(df_date)} examen(s)", expanded=True):
                    for idx, exam in df_date.iterrows():
                        session_color = "#2ecc71" if exam['session'] == 'Normale' else "#e67e22"
                        session_text = "🟢 Normale" if exam['session'] == 'Normale' else "🟠 Rattrapage"
                        
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.markdown(f"""
                            <div style='border-left: 4px solid {session_color}; padding-left: 15px; margin: 10px 0;'>
                                <div style='line-height: 1.6;'>
                                    <div style='color: #2c3e50; font-weight: bold; font-size: 1.1em;'>
                                        🕐 {exam['heure_debut']} - {exam['heure_fin']} • {exam['module']}
                                    </div>
                                    <div style='color: #666;'>
                                        👨‍🏫 {exam['professeur']} • 🏫 {exam['salle']} ({exam['type_salle']}) • 👥 {exam['nb_etudiants']} étudiants
                                    </div>
                                    <div style='color: #888; font-size: 0.9em;'>
                                        📚 {exam['credits']} crédits • ⏱️ {exam['duree_minutes']} minutes
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_b:
                            st.markdown(f"""
                            <div style='text-align: center; padding: 5px;'>
                                <div style='background-color: {session_color}; 
                                            color: white; 
                                            padding: 5px 10px; 
                                            border-radius: 15px; 
                                            font-size: 0.9em; 
                                            font-weight: 500;'>
                                    {exam['session']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
    
    # Section export
    st.markdown("---")
    st.markdown("### 📤 Export des Données")
    
    col_export1, col_export2, col_export3 = st.columns(3)
    
    export_formats = [
        ("📊", "CSV (Excel)", "Format tableur compatible Excel"),
        ("🌐", "HTML", "Format web avec mise en page"),
        ("📄", "PDF", "Format document (via HTML)")
    ]
    
    for i, (icon, title, description) in enumerate(export_formats):
        with [col_export1, col_export2, col_export3][i]:
            st.markdown(f"""
            <div class='export-btn'>
                <div style='font-size: 24px; margin-bottom: 10px;'>{icon}</div>
                <div style='font-weight: 600; margin-bottom: 5px;'>{title}</div>
                <div style='font-size: 12px; color: #666;'>{description}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Boutons de téléchargement
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    
    with col_dl1:
        csv_data = df_examens.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Télécharger CSV",
            data=csv_data,
            file_name=f"emploi_du_temps_{info['formation'].replace(' ', '_')}_{date_debut.strftime('%Y%m%d')}_{date_fin.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="csv_download"
        )
    
    with col_dl2:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Emploi du Temps - {info['formation']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 30px; 
                    border-radius: 15px; 
                    margin-bottom: 30px; 
                }}
                h1 {{ margin: 0 0 10px 0; color: white; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th {{ background-color: #3498db; color: white; padding: 12px; text-align: left; }}
                td {{ padding: 12px; border-bottom: 1px solid #ddd; vertical-align: top; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .badge {{ 
                    background-color: #2ecc71; 
                    color: white; 
                    padding: 3px 8px; 
                    border-radius: 12px; 
                    font-size: 0.9em; 
                }}
                .badge-rattrapage {{ background-color: #e67e22; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📅 Emploi du Temps - {info['formation']}</h1>
                <p><strong>Département:</strong> {info['departement']}</p>
                <p><strong>Période:</strong> {date_debut.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}</p>
                <p><strong>Généré le:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                <p><strong>Total examens:</strong> {len(df_examens)}</p>
            </div>
            <table>
                <tr>
                    <th>Date</th>
                    <th>Heure début</th>
                    <th>Heure fin</th>
                    <th>Module (Crédits)</th>
                    <th>Professeur</th>
                    <th>Salle (Type)</th>
                    <th>Étudiants</th>
                    <th>Session</th>
                </tr>
        """
        
        for _, exam in df_examens.iterrows():
            session_class = "badge" if exam['session'] == 'Normale' else "badge badge-rattrapage"
            html_content += f"""
                <tr>
                    <td>{exam['date_examen'].strftime('%d/%m/%Y') if hasattr(exam['date_examen'], 'strftime') else exam['date_examen']}</td>
                    <td>{exam['heure_debut']}</td>
                    <td>{exam['heure_fin']}</td>
                    <td><strong>{exam['module']}</strong><br>{exam['credits']} crédits</td>
                    <td>{exam['professeur']}</td>
                    <td>{exam['salle']}<br><small>{exam['type_salle']}</small></td>
                    <td><span class="{session_class}">{exam['session']}</span></td>
                </tr>
            """
        
        html_content += """
            </table>
        </body>
        </html>
        """
        
        st.download_button(
            label="Télécharger HTML",
            data=html_content.encode('utf-8'),
            file_name=f"emploi_du_temps_{info['formation'].replace(' ', '_')}_{date_debut.strftime('%Y%m%d')}_{date_fin.strftime('%Y%m%d')}.html",
            mime="text/html",
            use_container_width=True,
            key="html_download"
        )
    
    with col_dl3:
        st.info("Pour générer un PDF :\n1. Téléchargez le HTML\n2. Ouvrez-le dans votre navigateur\n3. Utilisez l'impression > Enregistrer au format PDF")

else:
    st.info("""
    📭 Aucun examen confirmé trouvé pour cette formation sur la période sélectionnée.
    
    **Suggestions :**
    - Vérifiez la période de recherche
    - Contactez l'administration si vous pensez qu'il devrait y avoir des examens
    - Assurez-vous que les examens sont confirmés par les professeurs
    """)

# Pied de page
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px; font-size: 0.9em;'>
    <strong>📚 Consultation des Emplois du Temps - Portail Étudiant</strong><br>
    Version 2.0 • Accès Public • Données actualisées en temps réel
</div>
""", unsafe_allow_html=True)