import streamlit as st
import mysql.connector
from mysql.connector import Error
import time

# Page config
st.set_page_config(
    page_title="Connexion - Système Examens",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit UI
st.markdown("""
<style>
#MainMenu, footer, header, .stDeployButton, [data-testid="stToolbar"] {
    display: none !important;
    visibility: hidden !important;
}
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
html, body, .stApp {
    overflow: hidden !important;
    height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
            background-color: white;
}
</style>
""", unsafe_allow_html=True)

# Database connection
def init_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            database="planning_examens",
            user="root",
            password=""
        )
    except Error:
        return None

conn = init_connection()

def run_query(query, params=None, fetch=True):
    try:
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params) if params else cursor.execute(query)
        if fetch:
            result = cursor.fetchall()
            cursor.close()
            return result
        conn.commit()
        cursor.close()
        return True
    except Error:
        return None

def authenticate_user(user_id, password):
    if conn is None:
        return False
    query = """
        SELECT u.*, p.nom, p.prenom, p.dept_id, d.nom as departement
        FROM utilisateurs u
        LEFT JOIN professeurs p ON u.id = p.id
        LEFT JOIN departements d ON p.dept_id = d.id
        WHERE u.id = %s AND u.mot_de_passe = %s
    """
    result = run_query(query, (user_id, password))
    if result:
        user = result[0]
        st.session_state['logged_in'] = True
        st.session_state['user_id'] = user['id']
        st.session_state['role'] = user['role']
        st.session_state['nom_complet'] = f"{user.get('prenom','')} {user.get('nom','')}".strip()
        st.session_state['departement_id'] = user.get('dept_id')
        st.session_state['departement'] = user.get('departement')
        return True
    return False


def main():
    # Main CSS for the improved design
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --primary-dark: #0a1429;
        --primary-medium: #1e293b;
        --accent-gold: #d4a853;
        --accent-light: #fef3c7;
        --success: #10b981;
        --error: #ef4444;
        --background: #f8fafc;
        --surface: #ffffff;
        --border: #e2e8f0;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
    }

    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        :root {
            --primary-dark: #f1f5f9;
            --primary-medium: #cbd5e1;
            --background: #0f172a;
            --surface: #1e293b;
            --border: #475569;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
        }
        
        .login-card {
            background: var(--surface) !important;
        }
        
        .stTextInput > div > div,
        .stNumberInput > div > div {
            background: #2d3748 !important;
            border-color: #4a5568 !important;
        }
        
        .stTextInput input,
        .stNumberInput input {
            color: var(--text-primary) !important;
            background: transparent !important;
        }
    }

    /* Main container */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f1f5f9 100%) !important;
        font-family: 'Inter', sans-serif;
    }

    @media (prefers-color-scheme: dark) {
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%) !important;
        }
    }

    /* Main container */
    .main-container {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 80vh;
        padding: 20px;
        animation: fadeIn 0.8s ease-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    /* Login card */
    .login-card {
        background: white;
        border-radius: 24px;
        width: 100px;
        max-width: 80vw;
        box-shadow: 0 25px 70px rgba(10, 20, 41, 0.15), 0 10px 35px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.95);
        overflow: hidden;
        display: flex;
        min-height: 650px;
        animation: fadeInUp 0.6s cubic-bezier(0.22, 1, 0.36, 1);
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Hero section */
    .hero-section {
        flex: 1.2;
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-medium) 100%);
        padding: 50px 40px;
        display: flex;
        flex-direction:;
        justify-content: center;
        color: white;
        position: relative;
        overflow: hidden;
        border-radius: 24px 0 0 24px;
        height: 700px;      
                    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 80%, rgba(212, 168, 83, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
    }

    .hero-content {
        position: relative;
        z-index: 1;
        max-width: 90%;
    }

    .hero-icon {
        width: 70px;
        height: 70px;
        background: linear-gradient(135deg, var(--accent-gold) 0%, #f6d365 100%);
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(212, 168, 83, 0.3);
        animation: float 6s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-10px) rotate(5deg); }
    }

    .hero-title {
        font-family: 'Poppins', sans-serif;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 15px;
        line-height: 1.2;
        background: linear-gradient(135deg, #ffffff 0%, #fef3c7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        opacity: 0.9;
        margin-bottom: 40px;
        line-height: 1.6;
    }

    .features-list {
        display: flex;
        flex-direction: column;
        gap: 15px;
        margin-top: 30px;
    }

    .feature-item {
        display: flex;
        align-items: center;
        gap: 12px;
        font-family: 'Inter', sans-serif;
        font-size: 15px;
        padding: 12px 18px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }

    .feature-item:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateX(5px);
    }

    .feature-item::before {
        content: '✓';
        color: var(--accent-gold);
        font-weight: bold;
        font-size: 16px;
    }

    /* Form section */
    .form-section {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        
    }

    /* Header */
    .auth-header {
        margin-bottom: 40px;
        animation: fadeInUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) 0.2s both;
    }

    .branding {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 25px;
    }

    .logo {
        width: 54px;
        height: 54px;
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-medium) 100%);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: white;
        box-shadow: 0 8px 20px rgba(10, 20, 41, 0.2);
    }

    .brand-name {
        font-family: 'Poppins', sans-serif;
        font-size: 26px;
        font-weight: 700;
        color: var(--text-primary);
    }

    .beta-tag {
        background: linear-gradient(135deg, var(--accent-gold) 0%, #f6d365 100%);
        color: var(--primary-dark);
        font-size: 11px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
        margin-left: 10px;
        letter-spacing: 0.5px;
    }

    .page-title {
        font-family: 'Poppins', sans-serif;
        font-size: 32px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 8px;
        line-height: 1.2;
    }

    .page-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 15px;
        color: var(--text-secondary);
        line-height: 1.6;
    }

    /* Form styling */
    .form-group {
       ;
        animation: fadeInUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        opacity: 0;
    }

    .form-group:nth-child(1) { animation-delay: 0.3s; }
    .form-group:nth-child(2) { animation-delay: 0.4s; }

    .custom-label {
        font-family: 'Poppins', sans-serif !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        letter-spacing: 0.5px !important;
        display: block;
        margin-bottom: 8px;
        text-transform: uppercase;
    }

    /* Input fields */
    .stTextInput > div > div,
    .stNumberInput > div > div {
        background: white !important;
        border: 2px solid var(--border) !important;
        border-radius: 14px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stTextInput > div > div:focus-within,
    .stNumberInput > div > div:focus-within {
        border-color: var(--accent-gold) !important;
        box-shadow: 0 0 0 4px rgba(212, 168, 83, 0.15) !important;
        transform: translateY(-2px);
    }

    .stTextInput input,
    .stNumberInput input {
        height: 52px !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        font-size: 15px !important;
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary) !important;
    }

    input:focus-visible {
        outline: none !important;
    }

    /* Checkbox and forgot password */
    .options-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        animation: fadeInUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) 0.5s both;
    }

    .checkbox-container {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .checkbox-container input[type="checkbox"] {
        width: 18px;
        height: 18px;
        accent-color: var(--accent-gold);
        cursor: pointer;
    }

    .checkbox-label {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        color: var(--text-primary);
        cursor: pointer;
        user-select: none;
    }

    .forgot-password {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        color: var(--accent-gold);
        text-decoration: none;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .forgot-password:hover {
        text-decoration: underline;
        color: var(--primary-dark);
    }

    /* Login button */
    .stButton > button {
        width: 100% !important;
        height: 56px !important;
        background: linear-gradient(135deg, var(--accent-gold) 0%, #f6d365 100%) !important;
        color: var(--primary-dark) !important;
        border: none !important;
        border-radius: 14px !important;
        font-family: 'Poppins', sans-serif !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 6px 20px rgba(212, 168, 83, 0.4) !important;
        transition: all 0.3s ease !important;
        position: relative;
        overflow: hidden;
    }

    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 30px rgba(212, 168, 83, 0.5) !important;
    }

    .stButton > button::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 5px;
        height: 5px;
        background: rgba(255, 255, 255, 0.5);
        opacity: 0;
        border-radius: 100%;
        transform: scale(1, 1) translate(-50%);
        transform-origin: 50% 50%;
    }

    .stButton > button:focus:not(:active)::after {
        animation: ripple 1s ease-out;
    }

    @keyframes ripple {
        0% { transform: scale(0, 0); opacity: 0.5; }
        100% { transform: scale(40, 40); opacity: 0; }
    }

    /* Footer */
    .auth-footer {
        margin-top: 30px;
        padding-top: 25px;
        border-top: 1px solid var(--border);
        text-align: center;
        animation: fadeInUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) 0.6s both;
    }

    .footer-links {
        display: flex;
        justify-content: center;
        gap: 25px;
        margin-bottom: 15px;
    }

    .footer-links a {
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        color: var(--text-secondary);
        text-decoration: none;
        transition: color 0.2s ease;
    }

    .footer-links a:hover {
        color: var(--accent-gold);
    }

    .version {
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        color: var(--text-secondary);
        opacity: 0.7;
    }

    /* Language selector */
    .language-selector {
        position: absolute;
        top: 30px;
        right: 30px;
    }

    .language-selector select {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        padding: 8px 12px;
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        cursor: pointer;
    }

    /* Responsive */
    @media (max-width: 992px) {
        .login-card {
            flex-direction: column;
            min-height: auto;
            width: 95%;
        }
        
        .hero-section {
            padding: 40px 30px;
            border-radius: 24px 24px 0 0;
            
            
            
        }
        
        .form-section {
            padding: 40px 30px;
        }
        
        .hero-content {
            max-width: 100%;
        }
    }

    @media (max-width: 480px) {
        .page-title {
            font-size: 26px;
        }
        
        .hero-title {
            font-size: 26px;
        }
        
        .features-list {
            gap: 10px;
        }
        
        .feature-item {
            padding: 10px 15px;
            font-size: 14px;
        }
    }

    /* Hide streamlit labels */
    .stTextInput label,
    .stNumberInput label {
        display: none !important;
    }

    /* Error/Success messages */
    .stAlert {
        border-radius: 12px !important;
        border-left: none !important;
        animation: fadeInUp 0.4s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)

    # Main container
    
    # Login card container
    
    # Create two columns
    col1, col2 = st.columns([1.2, 1])
    
    # HERO SECTION (Left Column)
    with col1:
        st.markdown("""
        <div class="hero-section">
            <div class="hero-content">
                <div class="hero-icon">🎓</div>
                <h1 class="hero-title">Système de Gestion des Examens</h1>
                <p class="hero-subtitle">
                    Plateforme intelligente pour la planification, surveillance et évaluation 
                    des examens universitaires. Accédez à tous vos outils en un seul endroit.
                </p>
                <div class="features-list">
                    <div class="feature-item">Interface intuitive et moderne</div>
                    <div class="feature-item">Sécurité et authentification renforcées</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # FORM SECTION (Right Column)
    with col2:
        st.markdown("""
        <div class="form-section">
            <div class="auth-header">
                <div class="branding">
                    <div class="logo">🔐</div>
                    <div class="brand-name">ExamensPro</div>
                    <div class="beta-tag">BETA</div>
                </div>
                <h1 class="page-title">Connexion Sécurisée</h1>
            </div>
        """, unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form", clear_on_submit=True):
            # User ID field with animation
            st.markdown('<span class="custom-label">IDENTIFIANT UTILISATEUR</span>', unsafe_allow_html=True)
            user_id = st.number_input(
                "ID Utilisateur",
                min_value=1,
                step=1,
                key="user_id_input",
                label_visibility="collapsed",
                placeholder="Entrez votre identifiant unique"
            )
            
            # Password field with animation
            st.markdown('<span class="custom-label">MOT DE PASSE</span>', unsafe_allow_html=True)
            password = st.text_input(
                "Mot de passe",
                type="password",
                key="password",
                label_visibility="collapsed",
                placeholder="••••••••••••"
            )
            
            # Options row
            st.markdown("""
            <div class="options-row">
                <div class="checkbox-container">
                    <input type="checkbox" id="remember" checked>
                    <label for="remember" class="checkbox-label">Se souvenir de moi</label>
                </div>
                <a class="forgot-password" href="#" onclick="alert('Contactez l\\'administrateur système pour réinitialiser votre mot de passe.'); return false;">
                    Mot de passe oublié ?
                </a>
            </div>
            """, unsafe_allow_html=True)
            
            # Login button
            submit = st.form_submit_button("🔐 SE CONNECTER", type="primary", use_container_width=True)
            
            if submit:
                if not user_id or not password:
                    st.error("⛔ Veuillez remplir tous les champs obligatoires")
                else:
                    # Create a progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Simulate loading with progress
                    for percent in range(101):
                        time.sleep(0.01)
                        progress_bar.progress(percent)
                        if percent < 30:
                            status_text.text("🔍 Vérification des identifiants...")
                        elif percent < 70:
                            status_text.text("🔐 Authentification en cours...")
                        elif percent < 90:
                            status_text.text("👤 Chargement du profil...")
                        else:
                            status_text.text("✅ Connexion presque terminée...")
                    
                    # Clear progress elements
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Authenticate
                    if authenticate_user(int(user_id), password):
                        # Success message with balloons
                        st.success("""
                        🎉 **Connexion réussie !**  
                        Bienvenue dans le système de gestion des examens.
                        """)
                        st.balloons()
                        
                        # Show welcome message
                        if 'nom_complet' in st.session_state:
                            st.info(f"**👋 Bienvenue, {st.session_state['nom_complet']} !**")
                        
                        # Short delay before redirect
                        time.sleep(1.5)
                        
                        # Redirect based on role
                        role = st.session_state.get('role', '').lower()
                        if 'professeur' in role:
                            st.switch_page("pages/app_professeur.py")
                        elif 'admin' in role:
                            st.switch_page("pages/app_admin.py")
                        elif 'doyen' in role:
                            st.switch_page("pages/app_vice_doyen.py")
                        elif 'chef' in role:
                            st.switch_page("pages/app_chef_departement.py")
                        else:
                            st.switch_page("app.py")
                    else:
                        st.error("""
                        ❌ **Échec de l'authentification**  
                        Veuillez vérifier vos identifiants et réessayer.
                        """)
        
        # Footer
        st.markdown("""
        </div>
        <div class="auth-footer">
            <div class="footer-links">
                <a href="#" onclick="alert('Support technique: support@examenspro.edu | Tél: +33 1 23 45 67 89'); return false;">
                    💻 Aide & Support
                </a>
                <a href="#" onclick="alert('Politique de confidentialité et traitement des données'); return false;">
                    🔒 Confidentialité
                </a>
                <a href="#" onclick="alert('Conditions générales d\\'utilisation'); return false;">
                    📄 Conditions
                </a>
            </div>
            <div class="version">Version 2.1.4 | © 2024 ExamensPro</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Close containers
    st.markdown('</div>', unsafe_allow_html=True)  # Close login-card
    st.markdown('</div>', unsafe_allow_html=True)  # Close main-container

if __name__ == "__main__":
    main()