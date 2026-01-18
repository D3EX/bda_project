# app.py - Page d'accueil principale
import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd

# Configuration de la page
st.set_page_config(
    page_title="Système de Gestion des Examens",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

# Page d'accueil
def main():
    # Style CSS personnalisé
    st.markdown("""
    <style>
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 4rem 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .feature-card {
            padding: 1.5rem;
            border-radius: 10px;
            background: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            height: 100%;
            transition: transform 0.3s;
        }
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
        }
        .user-card {
            padding: 1.5rem;
            border-radius: 10px;
            background: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            margin-bottom: 1rem;
        }
        .btn-login {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.75rem 2rem;
            border-radius: 30px;
            text-decoration: none;
            display: inline-block;
            margin: 1rem 0;
            font-weight: bold;
        }
        .footer {
            text-align: center;
            margin-top: 3rem;
            padding: 2rem;
            background: #f8f9fa;
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Section héro avec image
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="hero-section">
            <h1 style="font-size: 3rem; margin-bottom: 1rem;">🎓 Système de Gestion des Examens</h1>
            <p style="font-size: 1.2rem; margin-bottom: 2rem;">Solution complète pour la planification et la gestion des examens universitaires</p>
            <a href="/login" class="btn-login">🔐 Se connecter</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=200)
    
    # Statistiques principales
    st.subheader("📊 Statistiques Générales")
    
    # Récupérer les statistiques
    try:
        stats = run_query("""
            SELECT 
                (SELECT COUNT(*) FROM departements) as nb_departements,
                (SELECT COUNT(*) FROM formations) as nb_formations,
                (SELECT COUNT(*) FROM professeurs) as nb_professeurs,
                (SELECT COUNT(*) FROM etudiants) as nb_etudiants,
                (SELECT COUNT(*) FROM modules) as nb_modules,
                (SELECT COUNT(*) FROM lieu_examen) as nb_salles
        """)
        
        if stats:
            stat_data = stats[0]
            
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <h3>{stat_data['nb_departements']}</h3>
                    <p>📚 Départements</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <h3>{stat_data['nb_formations']}</h3>
                    <p>🎓 Formations</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="stat-card">
                    <h3>{stat_data['nb_professeurs']}</h3>
                    <p>👨‍🏫 Professeurs</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="stat-card">
                    <h3>{stat_data['nb_etudiants'] or 0}</h3>
                    <p>👥 Étudiants</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                st.markdown(f"""
                <div class="stat-card">
                    <h3>{stat_data['nb_modules']}</h3>
                    <p>📚 Modules</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col6:
                st.markdown(f"""
                <div class="stat-card">
                    <h3>{stat_data['nb_salles']}</h3>
                    <p>🏫 Salles</p>
                </div>
                """, unsafe_allow_html=True)
    except:
        pass
    
    # Fonctionnalités principales
    st.subheader("✨ Fonctionnalités Principales")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📅 Planification Intelligente</h3>
            <p>Générez automatiquement des emplois du temps d'examens sans conflits</p>
            <ul>
                <li>Optimisation des salles</li>
                <li>Gestion des surveillants</li>
                <li>Prévention des conflits</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>👨‍🏫 Tableau de Bord</h3>
            <p>Interface personnalisée pour chaque rôle</p>
            <ul>
                <li>Professeur: suivi des examens</li>
                <li>Admin: gestion complète</li>
                <li>Chef de département: supervision</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Rapports & Export</h3>
            <p>Générez des rapports détaillés</p>
            <ul>
                <li>Statistiques par département</li>
                <li>Export PDF/Excel</li>
                <li>Visualisation des données</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Types d'utilisateurs
    st.subheader("👥 Types d'Utilisateurs")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="user-card">
            <h3>👑 Administrateur</h3>
            <p>Accès complet au système</p>
            <p>Gestion des utilisateurs</p>
            <p>Supervision générale</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="user-card">
            <h3>🎓 Doyen</h3>
            <p>Vue globale de la faculté</p>
            <p>Statistiques avancées</p>
            <p>Validation des plannings</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="user-card">
            <h3>📚 Chef de Département</h3>
            <p>Gestion du département</p>
            <p>Supervision des professeurs</p>
            <p>Planification départementale</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="user-card">
            <h3>👨‍🏫 Professeur</h3>
            <p>Consultation des examens</p>
            <p>Statistiques personnelles</p>
            <p>Export du planning</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Bouton de connexion principal
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔐 Accéder au système de connexion", use_container_width=True, type="primary"):
            st.switch_page("pages/login.py")
    
    # Footer
    st.markdown("""
    <div class="footer">
        <h3>🎓 Université des Sciences et Technologies</h3>
        <p>Système de Gestion des Examens - Version 2.0</p>
        <p>© 2024 Tous droits réservés</p>
        <p>📧 contact@univ-examens.edu | 📞 +33 1 23 45 67 89</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()