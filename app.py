"""
SISTEMA DE CONTROL DE STOCK AGRÍCOLA
App principal Streamlit — La Sonia / San Guillermo / Camba Pora
Versión con gráficos interactivos y filtros dinámicos
Estructura mejorada: Admin con visión global + usuarios por establecimiento
CON CAMBIO DE CONTRASEÑA OBLIGATORIO EN CADA INGRESO HASTA QUE SE CAMBIE
CON OBLIGATORIEDAD DE SUBIR REMITO EN PDF PARA USUARIOS NO ADMIN
"""

import streamlit as st
from supabase import create_client, Client
from datetime import date, datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import uuid
import base64

# ── Configuración de página ────────────────────────────────────
st.set_page_config(
    page_title="Stock Agrícola - SECCO AGRO",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Botón flotante para abrir/cerrar sidebar ───────────────────
import streamlit.components.v1 as _components
_components.html("""
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin:0; padding:0; background:transparent; overflow:hidden; }
  #sb-toggle {
    position: fixed;
    top: 50vh;
    left: 0;
    transform: translateY(-50%);
    z-index: 2147483647;
    width: 30px;
    height: 62px;
    background: rgba(212,160,23,0.95);
    border: none;
    border-radius: 0 12px 12px 0;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 3px 0 16px rgba(0,0,0,0.5);
    font-size: 18px;
    color: #1a1a1f;
    font-weight: bold;
    transition: width 0.2s;
  }
  #sb-toggle:hover { width: 38px; }
</style>
</head>
<body>
<button id="sb-toggle" title="Abrir/cerrar menú">&#9776;</button>
<script>
  var btn = document.getElementById('sb-toggle');

  function getSidebar() {
    try {
      return parent.document.querySelector('[data-testid="stSidebar"]');
    } catch(e) { return null; }
  }

  function getNativeBtn() {
    var selectors = [
      '[data-testid="collapsedControl"]',
      '[data-testid="stSidebarCollapsedControl"]',
      'button[data-testid="collapsedControl"]',
      'button[data-testid="stSidebarCollapsedControl"]',
      'section[data-testid="stSidebarCollapsedControl"]'
    ];
    try {
      for (var i = 0; i < selectors.length; i++) {
        var el = parent.document.querySelector(selectors[i]);
        if (el) return el;
      }
    } catch(e) {}
    return null;
  }

  function toggleSidebar() {
    // Intento 1: click en botón nativo
    var native = getNativeBtn();
    if (native) { native.click(); return; }

    // Intento 2: manipular el sidebar directamente
    var sidebar = getSidebar();
    if (!sidebar) return;
    var isHidden = sidebar.style.display === 'none'
                   || sidebar.getAttribute('aria-hidden') === 'true'
                   || sidebar.offsetWidth < 10;
    if (isHidden) {
      sidebar.style.removeProperty('display');
      sidebar.style.removeProperty('transform');
      sidebar.style.width = '21rem';
      sidebar.setAttribute('aria-expanded', 'true');
    } else {
      sidebar.style.width = '0';
      sidebar.style.overflow = 'hidden';
    }
  }

  btn.addEventListener('click', toggleSidebar);

  // Posicionar el botón correctamente respecto a la ventana padre
  function reposition() {
    try {
      var rect = parent.document.documentElement;
      btn.style.top = (rect.clientHeight / 2) + 'px';
    } catch(e) {}
  }
  reposition();
  setInterval(reposition, 2000);
</script>
</body>
</html>
""", height=0, scrolling=False)

# ── Cliente Supabase ───────────────────────────────────────────
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]
SUPABASE_STORAGE_BUCKET = st.secrets.get("SUPABASE_STORAGE_BUCKET", "remitos")

@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()


# ══════════════════════════════════════════════════════════════
# CSS MEJORADO - Estilo moderno con tonos grises
# ══════════════════════════════════════════════════════════════

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

    [data-testid="stHeader"], header[data-testid="stHeader"], .stAppHeader {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        background: none !important;
    }

    /* ── Botón nativo sidebar: oculto (usamos botón propio via components.html) ── */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    html, body { background: #0e0e14 !important; }

    .stApp {
        background: #0e0e14 !important;
        font-family: 'DM Sans', sans-serif !important;
        position: relative !important;
        isolation: isolate !important;
    }

    .stApp::after {
        content: '' !important;
        position: fixed !important;
        inset: 0 !important;
        background-image: url('https://raw.githubusercontent.com/marcasosguemes-cell/Stock-SECCO-AGRO/main/Fondo.PNG') !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        filter: grayscale(100%) brightness(0.42) !important;
        -webkit-filter: grayscale(100%) brightness(0.42) !important;
        z-index: -2 !important;
        pointer-events: none !important;
    }

    .stApp::before {
        content: '' !important;
        position: fixed !important;
        inset: 0 !important;
        background: rgba(6, 6, 10, 0.55) !important;
        z-index: -1 !important;
        pointer-events: none !important;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stSidebar"],
    .stApp > div {
        position: relative !important;
        z-index: 1 !important;
        background: transparent !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a1f 0%, #0f0f12 60%, #0a0a0c 100%) !important;
        border-right: 1px solid rgba(100, 100, 120, 0.3) !important;
        box-shadow: 4px 0 24px rgba(0,0,0,0.4) !important;
    }

    /* ── Botón colapsar/expandir sidebar ── */
    [data-testid="collapsedControl"],
    button[data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        background: rgba(212,160,23,0.85) !important;
        border-radius: 0 10px 10px 0 !important;
        color: #1a1a1f !important;
    }

    /* ── Selectbox: label blanco ── */
    [data-testid="stSelectbox"] label,
    div[data-testid="stSelectbox"] > label,
    .stSelectbox label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* ── Selectbox: fondo gris oscuro, texto blanco ── */
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: rgba(55, 55, 65, 0.95) !important;
        border: 1px solid rgba(212,160,23,0.4) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] span,
    [data-testid="stSelectbox"] [data-baseweb="select"] div {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* ── Date input: label blanco ── */
    [data-testid="stDateInput"] label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* ── Todos los labels de inputs: blanco ── */
    [data-testid="stNumberInput"] label,
    [data-testid="stTextInput"] label,
    [data-testid="stTextArea"] label,
    [data-testid="stFileUploader"] label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* ── Botón colapsar/expandir sidebar ── */
    [data-testid="collapsedControl"],
    button[data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        background: rgba(212,160,23,0.85) !important;
        border-radius: 0 10px 10px 0 !important;
        color: #1a1a1f !important;
    }

    /* ── Selectbox: label blanco ── */
    [data-testid="stSelectbox"] label,
    div[data-testid="stSelectbox"] > label,
    .stSelectbox label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* ── Selectbox: fondo gris oscuro, texto blanco ── */
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: rgba(55, 55, 65, 0.95) !important;
        border: 1px solid rgba(212,160,23,0.4) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] span,
    [data-testid="stSelectbox"] [data-baseweb="select"] div {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* ── Date input: label blanco ── */
    [data-testid="stDateInput"] label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* ── Todos los labels de inputs: blanco ── */
    [data-testid="stNumberInput"] label,
    [data-testid="stTextInput"] label,
    [data-testid="stTextArea"] label,
    [data-testid="stFileUploader"] label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] .stButton button {
        background: rgba(50, 50, 60, 0.8) !important;
        border: 1px solid rgba(212, 160, 23, 0.5) !important;
        width: 100%;
        text-align: left;
        padding: 0.7rem 1.1rem;
        border-radius: 12px;
        margin: 5px 0;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.25s ease;
        color: #000000 !important;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background: #d4a017 !important;
        border-color: #b87a0c !important;
        transform: translateX(5px);
        color: #1a1a1f !important;
    }

    .sidebar-header {
        text-align: center;
        padding: 1.6rem 0 1.2rem 0;
        border-bottom: 1px solid rgba(212, 160, 23, 0.4);
        margin-bottom: 1.4rem;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .sidebar-logo-oval {
        background: #f7f3e8;
        border: 2px solid rgba(212, 160, 23, 0.6);
        border-radius: 50%;
        width: 120px;
        height: 120px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3), 0 1px 0 rgba(255,255,255,0.3) inset;
        margin-bottom: 12px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .sidebar-logo {
        width: 115% !important;
        height: auto !important;
        object-fit: contain !important;
        display: block;
        padding: 0px;
    }

    .sidebar-header h1 {
        font-family: 'Playfair Display', serif !important;
        font-size: 1.4rem !important;
        margin: 0;
        color: #d4a017 !important;
        letter-spacing: 0.04em;
        font-weight: 700;
    }

    .profile-card {
        text-align: center;
        padding: 0.9rem 1rem;
        margin: 0.5rem 0 1rem 0;
        background: rgba(40, 40, 48, 0.7) !important;
        border: 1px solid rgba(212, 160, 23, 0.25);
        border-radius: 16px;
        backdrop-filter: blur(8px);
    }

    .profile-name {
        font-size: 0.95rem;
        font-weight: 600;
        color: #f0f0f5 !important;
        margin-bottom: 4px;
    }

    .profile-role, .profile-location {
        font-size: 0.78rem;
        color: #b8b8c0 !important;
        margin-top: 3px;
    }

    .title-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.8rem;
    }

    .logo-oval-wrap {
        background: #f7f3e8;
        border: 2px solid rgba(212, 160, 23, 0.5);
        border-radius: 50%;
        width: 420px;
        height: 252px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3), 0 2px 0 rgba(255,255,255,0.6) inset;
        margin-bottom: 20px;
        transition: transform 0.35s ease, box-shadow 0.35s ease;
    }

    .title-logo {
        width: 100% !important;
        height: 100% !important;
        object-fit: contain !important;
        display: block;
        padding: 15px;
    }

    .title-bubble-login {
        background: rgba(0, 0, 0, 0.65);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 215, 120, 0.6);
        border-radius: 20px;
        padding: 1rem 2.2rem 0.9rem 2.2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.35);
        text-align: center;
        margin-bottom: 0.5rem;
        width: 100%;
    }

    .main-title-with-logo {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        text-shadow: 0 2px 8px rgba(0,0,0,0.6) !important;
        margin: 0 0 0.3rem 0 !important;
        letter-spacing: 0.02em !important;
    }

    .login-subtitle {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.9rem !important;
        color: #FFE8B6 !important;
        font-weight: 500 !important;
        letter-spacing: 0.07em !important;
    }

    .title-bubble {
        background: linear-gradient(135deg, rgba(200, 160, 96, 0.95) 0%, rgba(184, 144, 90, 0.95) 100%);
        border-radius: 20px;
        padding: 1rem 2.2rem;
        display: inline-block;
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
        text-align: center;
        margin-bottom: 1.4rem;
        backdrop-filter: blur(4px);
    }

    .title-bubble h1 {
        margin: 0;
        font-family: 'Playfair Display', serif !important;
        font-size: 1.8rem !important;
        color: #FFFFFF !important;
        font-weight: 700;
        letter-spacing: 0.02em;
        text-shadow: 0 2px 6px rgba(0,0,0,0.5) !important;
    }

    .title-bubble p {
        margin: 0.35rem 0 0 0;
        color: #FFE8B6 !important;
        font-size: 0.9rem;
        font-weight: 500;
    }

    .metric-card {
        background: linear-gradient(145deg, rgba(55, 55, 62, 0.9) 0%, rgba(45, 45, 52, 0.95) 100%) !important;
        border: 1px solid rgba(212, 160, 23, 0.35);
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: all 0.3s cubic-bezier(.4,0,.2,1);
        text-align: center !important;
        padding: 1.2rem 1rem;
        cursor: pointer;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 28px rgba(0,0,0,0.4);
        border-color: rgba(212, 160, 23, 0.6);
    }

    .metric-value {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.6rem !important;
        font-weight: 700;
        color: #f0f0f5 !important;
        margin: 0.4rem 0;
    }

    .metric-label {
        font-size: 0.75rem !important;
        color: #d4a017 !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 700;
    }

    .stButton > button {
        background: linear-gradient(135deg, #d4a017, #b87a0c) !important;
        color: #1a1a1f !important;
        border: none !important;
        border-radius: 12px;
        padding: 0.6rem 1.3rem;
        font-weight: 700;
        font-size: 0.9rem;
        transition: all 0.25s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.35);
        background: linear-gradient(135deg, #e5b52a, #c98a1a) !important;
        color: #000000 !important;
    }

    [data-testid="stForm"] {
        background: rgba(45, 45, 52, 0.85) !important;
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(212, 160, 23, 0.3);
    }

    .footer {
        text-align: center;
        padding: 1.6rem 2rem;
        color: #a8a8b0 !important;
        font-size: 0.78rem;
        border-top: 1px solid rgba(212, 160, 23, 0.25);
        margin-top: 2.5rem;
        background: rgba(35, 35, 42, 0.7);
        backdrop-filter: blur(8px);
        border-radius: 16px;
    }

    .password-warning {
        background: linear-gradient(135deg, rgba(212, 160, 23, 0.2), rgba(184, 122, 12, 0.2));
        border-left: 4px solid #d4a017;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .password-warning h3 {
        color: #d4a017 !important;
        margin-top: 0 !important;
    }

    .password-warning p,
    .password-warning strong,
    .password-warning span {
        color: #f0f0f5 !important;
    }
    
    .pdf-miniatura {
        background: rgba(212, 160, 23, 0.15);
        border-radius: 8px;
        padding: 4px 8px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.8rem;
        text-decoration: none;
        color: #d4a017 !important;
        transition: all 0.2s ease;
    }
    .pdf-miniatura:hover {
        background: rgba(212, 160, 23, 0.3);
        color: #f0f0f5 !important;
    }

    /* ── Sidebar: textos de sección en blanco ── */
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] h3,
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
    }

    /* ── Dashboard: métricas en blanco ── */
    [data-testid="stMetric"] label,
    [data-testid="stMetric"] div[data-testid="stMetricLabel"],
    [data-testid="stMetric"] div[data-testid="stMetricValue"],
    [data-testid="stMetric"] div[data-testid="stMetricDelta"],
    [data-testid="metric-container"] label,
    div[data-testid="stMetricLabel"] p,
    div[data-testid="stMetricValue"] div {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* ── Textos generales en el contenido principal ── */
    [data-testid="stAppViewContainer"] h3,
    [data-testid="stAppViewContainer"] div[data-testid="stMarkdownContainer"] h3 {
        color: #FFFFFF !important;
        text-shadow: 0 1px 4px rgba(0,0,0,0.6);
    }

    /* ── Login: botón Ingresar con letras negras ── */
    [data-testid="stForm"] .stButton > button,
    [data-testid="stForm"] [data-testid="stFormSubmitButton"] > button,
    [data-testid="stFormSubmitButton"] > button,
    [data-testid="stFormSubmitButton"] > button > div,
    [data-testid="stFormSubmitButton"] > button p,
    [data-testid="stFormSubmitButton"] button * {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* ── Todos los forms: labels y textos en blanco ── */
    [data-testid="stForm"] h3,
    [data-testid="stForm"] label,
    [data-testid="stForm"] .stTextInput label,
    [data-testid="stForm"] p,
    [data-testid="stForm"] span,
    [data-testid="stForm"] div[data-testid="stMarkdownContainer"] h3,
    [data-testid="stForm"] div[data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# FUNCIONES DE AUTENTICACIÓN
# ══════════════════════════════════════════════════════════════

def check_auth():
    try:
        if "session" in st.session_state and st.session_state["session"]:
            return True
        session = supabase.auth.get_session()
        if session:
            st.session_state["session"] = session
            st.session_state["user_id"] = session.user.id
            return True
        return False
    except Exception:
        return False


def logout():
    try:
        supabase.auth.sign_out()
        keys_to_clear = ["session", "user_id", "perfil", "rol", "establecimiento_id", 
                         "establecimiento_nombre", "pagina", "password_changed", "skip_password_check"]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    except Exception as e:
        st.error(f"Error al cerrar sesión: {e}")


def verificar_perfil():
    if "rol" not in st.session_state or "perfil" not in st.session_state:
        user_id = st.session_state.get("user_id")
        if user_id:
            try:
                perfil = supabase.table("usuarios").select("*").eq("id", user_id).execute()
                if perfil.data:
                    st.session_state["perfil"] = perfil.data[0]
                    st.session_state["rol"] = perfil.data[0]["rol"]
                    st.session_state["establecimiento_id"] = perfil.data[0].get("establecimiento_id")
                    st.session_state["establecimiento_nombre"] = perfil.data[0].get("establecimiento_nombre")
                    st.session_state["password_changed"] = perfil.data[0].get("password_changed", False)
                    return True
                else:
                    st.error("Perfil no encontrado")
                    logout()
                    return False
            except Exception as e:
                st.error(f"Error al cargar perfil: {e}")
                return False
        return False
    return True


# ══════════════════════════════════════════════════════════════
# FUNCIONES PARA MANEJO DE REMITOS (PDF) - VERSIÓN CORREGIDA
# ══════════════════════════════════════════════════════════════

def subir_remito_pdf(archivo_pdf, movimiento_id, usuario_id, establecimiento_id):
    """
    Sube un archivo PDF a Supabase Storage y guarda la referencia en la tabla movimientos.
    Versión con logs para depuración.
    """
    if archivo_pdf is None:
        st.warning("⚠️ No hay archivo PDF para subir")
        return None
    
    try:
        # Mostrar información del archivo
        nombre_original = archivo_pdf.name if hasattr(archivo_pdf, 'name') else 'sin_nombre'
        tamaño = len(archivo_pdf.getvalue())
        st.info(f"📄 Procesando archivo: {nombre_original} - {tamaño} bytes")
        
        # Generar nombre único para el archivo
        nombre_archivo = f"remito_{movimiento_id}_{uuid.uuid4().hex[:8]}.pdf"
        ruta_completa = nombre_archivo  # Ruta simplificada
        
        # Leer el contenido del archivo
        archivo_bytes = archivo_pdf.getvalue()
        
        # Subir a Supabase Storage
        st.info(f"📤 Subiendo a storage: {ruta_completa}")
        
        supabase.storage.from_(SUPABASE_STORAGE_BUCKET).upload(
            path=ruta_completa,
            file=archivo_bytes,
            file_options={"content-type": "application/pdf"}
        )
        
        # Construir URL pública manualmente
        url_publica = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_STORAGE_BUCKET}/{ruta_completa}"
        
        st.success(f"✅ Archivo subido correctamente")
        st.info(f"🔗 URL: {url_publica[:80]}...")
        
        # Actualizar el registro del movimiento
        resultado = supabase.table("movimientos").update({
            "remito_url": url_publica,
            "remito_filename": nombre_archivo
        }).eq("id", movimiento_id).execute()
        
        st.success(f"✅ Base de datos actualizada para movimiento {movimiento_id}")
        return url_publica
        
    except Exception as e:
        st.error(f"❌ Error detallado al subir el remito: {type(e).__name__}: {e}")
        return None


def generar_link_pdf(url_pdf):
    """Genera un link HTML para visualizar/descargar el PDF"""
    if not url_pdf or url_pdf == "—":
        return "—"
    
    # Crear un link con icono de PDF
    link_html = f"""
    <a href="{url_pdf}" target="_blank" class="pdf-miniatura">
        📄 Ver Remito
    </a>
    """
    return link_html


# ══════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════

def login():
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown("""
        <div class="title-container">
            <div class="logo-oval-wrap">
                <img src="https://raw.githubusercontent.com/marcasosguemes-cell/Stock-SECCO-AGRO/main/Logo.png" class="title-logo" alt="Logo">
            </div>
            <div class="title-bubble-login">
                <h1 class="main-title-with-logo">Stock Agrícola</h1>
                <p class="login-subtitle">La Sonia · San Guillermo · Camba Pora</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### Bienvenido")
            email = st.text_input("Email", placeholder="usuario@ejemplo.com")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("🚀 Ingresar", use_container_width=True)
            
            if submitted:
                try:
                    with st.spinner("Verificando credenciales..."):
                        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state["session"] = res.session
                        st.session_state["user_id"] = res.user.id
                        
                        perfil = supabase.table("usuarios").select("*").eq("id", res.user.id).execute()
                        
                        if perfil.data:
                            st.session_state["perfil"] = perfil.data[0]
                            st.session_state["rol"] = perfil.data[0]["rol"]
                            st.session_state["establecimiento_id"] = perfil.data[0].get("establecimiento_id")
                            st.session_state["establecimiento_nombre"] = perfil.data[0].get("establecimiento_nombre")
                            st.session_state["password_changed"] = perfil.data[0].get("password_changed", False)
                            st.session_state["pagina"] = "Dashboard"
                            st.session_state.pop("skip_password_check", None)
                            st.success("✅ Login exitoso!")
                            st.rerun()
                        else:
                            st.error("❌ No se encontró tu perfil.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")


# ══════════════════════════════════════════════════════════════
# FUNCIÓN PARA MOSTRAR CAMBIO DE CONTRASEÑA
# ══════════════════════════════════════════════════════════════

def mostrar_cambio_password():
    st.markdown("""
    <div class="password-warning">
        <h3>🔐 Cambio de Contraseña Obligatorio</h3>
        <p>Por razones de seguridad, debes cambiar tu contraseña.</p>
        <p><strong>Importante:</strong> Esta contraseña temporal caducará pronto. Por favor, establézcala ahora.</p>
        <p>Si eliges "Más Tarde", el sistema te recordará en cada ingreso hasta que la cambies.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("cambiar_password_form_main"):
        nueva_password = st.text_input("Nueva Contraseña", type="password", placeholder="Mínimo 6 caracteres")
        confirmar_password = st.text_input("Confirmar Contraseña", type="password", placeholder="Repite tu nueva contraseña")
        
        col1, col2 = st.columns(2)
        with col1:
            cambiar_btn = st.form_submit_button("✅ Cambiar Contraseña", use_container_width=True)
        with col2:
            mas_tarde_btn = st.form_submit_button("⏰ Más Tarde", use_container_width=True)
        
        if cambiar_btn:
            if not nueva_password:
                st.error("❌ Por favor ingresa una nueva contraseña")
            elif len(nueva_password) < 6:
                st.error("❌ La contraseña debe tener al menos 6 caracteres")
            elif nueva_password != confirmar_password:
                st.error("❌ Las contraseñas no coinciden")
            else:
                try:
                    with st.spinner("Actualizando contraseña..."):
                        supabase.auth.update_user({"password": nueva_password})
                        supabase.table("usuarios").update({"password_changed": True}).eq("id", st.session_state["user_id"]).execute()
                        st.session_state["password_changed"] = True
                        st.session_state.pop("skip_password_check", None)
                        st.success("✅ Contraseña actualizada correctamente!")
                        st.balloons()
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al actualizar contraseña: {e}")
        
        if mas_tarde_btn:
            st.session_state["skip_password_check"] = True
            st.rerun()


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════

def sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <div class="sidebar-logo-oval">
                <img src="https://raw.githubusercontent.com/marcasosguemes-cell/Stock-SECCO-AGRO/main/Logo.png" class="sidebar-logo" alt="Logo">
            </div>
            <h1>Stock Agrícola</h1>
        </div>
        """, unsafe_allow_html=True)
        
        if "perfil" not in st.session_state:
            st.warning("Cargando...")
            return
            
        perfil = st.session_state.get("perfil", {})
        rol = st.session_state.get("rol", "")
        
        badge_class = "badge-admin" if rol == "admin" else "badge-operator"
        badge_text = "Administrador" if rol == "admin" else "Operador"

        st.markdown("### 🏢 ESTABLECIMIENTO")
        
        establecimientos = get_establecimientos()
        
        if rol == "admin":
            opciones_estab = ["🌐 Consolidado"] + [e["nombre"] for e in establecimientos]
        else:
            mi_estab_id = st.session_state.get("establecimiento_id")
            mi_estab_nombre = st.session_state.get("establecimiento_nombre", "")
            
            if not mi_estab_id or not mi_estab_nombre:
                st.error("⚠️ No tienes un establecimiento asignado. Contacta al administrador.")
                st.markdown("---")
                if st.button("🚪 Cerrar sesión"):
                    logout()
                return
            
            opciones_estab = [mi_estab_nombre]
            st.session_state["estab_seleccionado"] = mi_estab_nombre
            st.session_state["estab_activo_id"] = mi_estab_id
            st.session_state["estab_activo_nombre"] = mi_estab_nombre
            st.markdown(f"""
            <div style="background:rgba(212,160,23,0.2); border-radius:10px; padding:0.5rem; text-align:center; margin-bottom:0.8rem;">
                <span style="color:#d4a017;">📍 {mi_estab_nombre}</span>
            </div>
            """, unsafe_allow_html=True)

        if rol == "admin":
            if "estab_seleccionado" not in st.session_state:
                st.session_state["estab_seleccionado"] = "🌐 Consolidado"

            estab_sel = st.selectbox(
                "Seleccionar",
                opciones_estab,
                index=opciones_estab.index(st.session_state["estab_seleccionado"]) if st.session_state["estab_seleccionado"] in opciones_estab else 0,
                key="sb_estab_selector",
                label_visibility="collapsed"
            )
            
            if estab_sel != st.session_state.get("estab_seleccionado"):
                st.session_state["estab_seleccionado"] = estab_sel
                st.session_state["pagina"] = "Dashboard"
                st.rerun()

            if estab_sel == "🌐 Consolidado":
                st.session_state["estab_activo_id"] = None
                st.session_state["estab_activo_nombre"] = "Consolidado"
            else:
                match = next((e for e in establecimientos if e["nombre"] == estab_sel), None)
                if match:
                    st.session_state["estab_activo_id"] = match["id"]
                    st.session_state["estab_activo_nombre"] = match["nombre"]

        estab_activo = st.session_state.get("estab_activo_nombre", "Consolidado" if rol == "admin" else st.session_state.get("establecimiento_nombre", ""))
        es_consolidado = (estab_activo == "Consolidado")

        st.markdown(f"""
        <div class="profile-card">
            <div class="profile-name">👤 {perfil.get('nombre', 'Usuario')}</div>
            <div class="profile-role"><span class="{badge_class}">{badge_text}</span></div>
            <div class="profile-location">📍 {'🌐 Todos los establecimientos' if es_consolidado else estab_activo}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📌 MENÚ")
        
        if rol != "admin":
            st.info("📎 **Importante:** Al registrar ingresos o egresos deberás adjuntar el remito en formato PDF.")

        if es_consolidado and rol == "admin":
            paginas_menu = [
                ("🌐", "Consolidado"),
                ("⚠️", "Alertas"),
                ("📈", "Reportes"),
                ("🏭", "Proveedores"),
                ("📦", "Productos"),
                ("👥", "Usuarios"),
            ]
        elif rol == "admin":
            paginas_menu = [
                ("📊", "Dashboard"),
                ("📥", "Nuevo Ingreso"),
                ("📤", "Nuevo Egreso"),
                ("📋", "Historial"),
                ("⚠️", "Alertas"),
                ("📈", "Reportes"),
                ("🏭", "Proveedores"),
                ("📦", "Productos"),
                ("👥", "Usuarios"),
            ]
        elif rol == "establecimiento" and st.session_state.get("establecimiento_id"):
            paginas_menu = [
                ("📊", "Dashboard"),
                ("📥", "Nuevo Ingreso"),
                ("📤", "Nuevo Egreso"),
                ("📋", "Historial"),
                ("⚠️", "Alertas"),
                ("📈", "Reportes"),
            ]
        else:
            st.error("⚠️ Configuración incompleta. Contacta al administrador.")
            st.markdown("---")
            if st.button("🚪 Cerrar sesión"):
                logout()
            return

        pagina_actual = st.session_state.get("pagina", "Dashboard")
        nombres_menu = [n for _, n in paginas_menu]
        if pagina_actual not in nombres_menu:
            st.session_state["pagina"] = nombres_menu[0]

        for emoji, nombre in paginas_menu:
            if st.button(f"{emoji}  {nombre}", key=f"nav_{nombre}"):
                st.session_state["pagina"] = nombre
        
        st.markdown("---")
        if st.button("🚪 Cerrar sesión"):
            logout()


# ══════════════════════════════════════════════════════════════
# HELPERS DE DATOS
# ══════════════════════════════════════════════════════════════

def get_establecimientos():
    res = supabase.table("establecimientos").select("*").execute()
    return res.data

def get_categorias():
    res = supabase.table("categorias").select("*").execute()
    return res.data

def get_productos(categoria_id=None, subcategoria=None):
    q = supabase.table("productos").select("*,categorias(nombre)").eq("activo", True)
    if categoria_id:
        q = q.eq("categoria_id", categoria_id)
    if subcategoria:
        q = q.eq("subcategoria", subcategoria)
    return q.execute().data

def get_proveedores():
    res = supabase.table("proveedores").select("*").eq("activo", True).execute()
    return res.data

def get_movimientos(establecimiento_id=None, limit=5000):
    try:
        q = supabase.table("movimientos").select("*").limit(limit)
        if establecimiento_id:
            q = q.eq("establecimiento_id", establecimiento_id)
        movimientos = q.execute().data
        
        if not movimientos:
            return []
        
        producto_ids = list(set([m.get("producto_id") for m in movimientos if m.get("producto_id")]))
        establecimiento_ids = list(set([m.get("establecimiento_id") for m in movimientos if m.get("establecimiento_id")]))
        
        productos_data = {}
        if producto_ids:
            productos_res = supabase.table("productos").select("*, categorias(nombre)").in_("id", producto_ids).execute()
            for p in productos_res.data:
                productos_data[p["id"]] = p
        
        establecimientos_data = {}
        if establecimiento_ids:
            establecimientos_res = supabase.table("establecimientos").select("*").in_("id", establecimiento_ids).execute()
            for e in establecimientos_res.data:
                establecimientos_data[e["id"]] = e
        
        for m in movimientos:
            m["productos"] = productos_data.get(m.get("producto_id"), {})
            m["establecimientos"] = establecimientos_data.get(m.get("establecimiento_id"), {})
        
        return movimientos
    except Exception as e:
        st.error(f"Error al obtener movimientos: {e}")
        return []


def get_stock_por_producto(establecimiento_id=None):
    movimientos = get_movimientos(establecimiento_id, limit=10000)
    if not movimientos:
        return pd.DataFrame()
    
    df = pd.DataFrame(movimientos)
    if "producto_id" not in df.columns:
        return pd.DataFrame()
    
    ingresos = df[df["tipo"] == "ingreso"].groupby("producto_id")["cantidad"].sum()
    egresos = df[df["tipo"] == "egreso"].groupby("producto_id")["cantidad"].sum()
    
    productos = get_productos()
    nombre_map = {p["id"]: p["nombre"] for p in productos}
    categoria_map = {p["id"]: p.get("categorias", {}).get("nombre", "Sin categoría") if p.get("categorias") else "Sin categoría" for p in productos}
    presentacion_map = {p["id"]: p.get("presentacion", "") for p in productos}
    unidad_map = {p["id"]: p.get("unidad_medida", "unidad") for p in productos}
    
    stock = {}
    for prod_id in set(ingresos.index) | set(egresos.index):
        stock[prod_id] = ingresos.get(prod_id, 0) - egresos.get(prod_id, 0)
    
    result = []
    for prod_id, cantidad in stock.items():
        if cantidad != 0:
            result.append({
                "producto_id": prod_id,
                "producto": nombre_map.get(prod_id, "Desconocido"),
                "categoria": categoria_map.get(prod_id, "Sin categoría"),
                "presentacion": presentacion_map.get(prod_id, ""),
                "unidad": unidad_map.get(prod_id, "unidad"),
                "stock": cantidad
            })
    
    return pd.DataFrame(result).sort_values("stock", ascending=False)


def get_movimientos_con_filtros(establecimiento_id=None, fecha_desde=None, fecha_hasta=None, tipo=None, producto_id=None, categoria_id=None):
    movimientos = get_movimientos(establecimiento_id, limit=5000)
    if not movimientos:
        return []
    
    df = pd.DataFrame(movimientos)
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"])
        
        if fecha_desde:
            df = df[df["fecha"] >= pd.Timestamp(fecha_desde)]
        if fecha_hasta:
            df = df[df["fecha"] <= pd.Timestamp(fecha_hasta)]
    
    if tipo and tipo != "Todos":
        df = df[df["tipo"] == tipo]
    
    if producto_id:
        df = df[df["producto_id"] == producto_id]
    
    if categoria_id:
        productos_cat = [p["id"] for p in get_productos(categoria_id)]
        df = df[df["producto_id"].isin(productos_cat)]
    
    return df.to_dict("records")


def estab_filter():
    return st.session_state.get("estab_activo_id", None)


def es_vista_consolidado():
    return st.session_state.get("estab_activo_nombre", "Consolidado") == "Consolidado"


def get_stock_por_establecimiento():
    try:
        movimientos = get_movimientos(None, limit=10000)
    except Exception as e:
        st.error(f"Error al obtener movimientos: {e}")
        return pd.DataFrame()

    if not movimientos:
        return pd.DataFrame()

    df = pd.DataFrame(movimientos)
    
    df["producto_nombre"] = df["productos"].apply(lambda x: x.get("nombre", "") if isinstance(x, dict) else "")
    df["producto_presentacion"] = df["productos"].apply(lambda x: x.get("presentacion", "") if isinstance(x, dict) else "")
    df["producto_unidad"] = df["productos"].apply(lambda x: x.get("unidad_medida", "unidad") if isinstance(x, dict) else "unidad")
    df["categoria_nombre"] = df["productos"].apply(
        lambda x: x.get("categorias", {}).get("nombre", "Sin categoría") if isinstance(x, dict) and x.get("categorias") else "Sin categoría"
    )
    df["establecimiento_nombre"] = df["establecimientos"].apply(lambda x: x.get("nombre", "") if isinstance(x, dict) else "")

    ingresos = df[df["tipo"] == "ingreso"].groupby(["producto_nombre", "producto_presentacion", "producto_unidad", "categoria_nombre", "establecimiento_nombre"])["cantidad"].sum()
    egresos = df[df["tipo"] == "egreso"].groupby(["producto_nombre", "producto_presentacion", "producto_unidad", "categoria_nombre", "establecimiento_nombre"])["cantidad"].sum()

    stock_df = (ingresos - egresos.reindex(ingresos.index, fill_value=0)).reset_index()
    stock_df.columns = ["producto", "presentacion", "unidad", "categoria", "establecimiento", "stock"]
    return stock_df[stock_df["stock"] != 0].sort_values(["establecimiento", "producto"])


# ══════════════════════════════════════════════════════════════
# DASHBOARD (VERSIÓN SIMPLIFICADA)
# ══════════════════════════════════════════════════════════════

def pagina_dashboard():
    st.markdown("""
    <div class="main-content">
        <div class="title-bubble">
            <h1>📊 Dashboard de Stock</h1>
            <p>📋 Análisis del inventario agrícola</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    stock_productos = get_stock_por_producto(estab_filter())
    
    if stock_productos.empty:
        st.info("💡 Sin datos de stock. Registrá movimientos para ver el inventario.")
        return

    # ── Filtros de categoría, subcategoría y producto ──
    SUBCATS_AGRO = ["Herbicidas", "Insecticidas", "Coadyuvantes"]
    categorias_disponibles = sorted(stock_productos["categoria"].dropna().unique().tolist())

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        cat_sel = st.selectbox("📁 Categoría", ["Todas"] + categorias_disponibles, key="dash_cat")

    es_agro_dash = cat_sel != "Todas" and ("agroqui" in cat_sel.lower() or "agroquí" in cat_sel.lower())

    with col_f2:
        if es_agro_dash:
            subcat_sel = st.selectbox("🌿 Tipo Agroquímico", ["Todos"] + SUBCATS_AGRO, key="dash_subcat")
        else:
            subcat_sel = "Todos"
            st.selectbox("🌿 Tipo Agroquímico", ["—"], key="dash_subcat", disabled=True)

    with col_f3:
        df_para_prods = stock_productos.copy()
        if cat_sel != "Todas":
            df_para_prods = df_para_prods[df_para_prods["categoria"] == cat_sel]
        prods_filtrados = sorted(df_para_prods["producto"].dropna().unique().tolist())
        prod_sel = st.selectbox("📦 Producto", ["Todos"] + prods_filtrados, key="dash_prod")

    # Aplicar filtros
    df_filtrado = stock_productos.copy()
    if cat_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["categoria"] == cat_sel]
    if es_agro_dash and subcat_sel != "Todos":
        # filtrar por subcategoría usando el campo 'producto' (nombre contiene subcat o filtramos por lista de productos)
        prods_subcat = get_productos(subcategoria=subcat_sel)
        nombres_subcat = [p["nombre"] for p in prods_subcat]
        df_filtrado = df_filtrado[df_filtrado["producto"].isin(nombres_subcat)]
    if prod_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["producto"] == prod_sel]

    total_stock = df_filtrado["stock"].sum()
    total_productos = len(df_filtrado)
    stock_bajo = len(df_filtrado[df_filtrado["stock"] < 50])

    # ── Burbujas métricas ──
    st.markdown(f"""
    <div style="display:flex;gap:1.2rem;margin:1.2rem 0 1.8rem 0;flex-wrap:wrap;">
        <div style="flex:1;min-width:200px;background:linear-gradient(135deg,rgba(212,160,23,0.25),rgba(212,160,23,0.12));
                    border:1px solid rgba(212,160,23,0.6);border-radius:20px;padding:1.4rem 1.6rem;
                    box-shadow:0 6px 24px rgba(0,0,0,0.35);text-align:center;backdrop-filter:blur(8px);">
            <div style="font-size:2rem;margin-bottom:4px;">📦</div>
            <div style="font-size:2.4rem;font-weight:800;color:#d4a017;font-family:'Playfair Display',serif;
                        text-shadow:0 2px 8px rgba(0,0,0,0.4);line-height:1.1;">{total_stock:,.0f}</div>
            <div style="font-size:0.8rem;color:#fff;font-weight:600;text-transform:uppercase;
                        letter-spacing:0.1em;margin-top:6px;opacity:0.85;">Stock Total (unidades)</div>
        </div>
        <div style="flex:1;min-width:200px;background:linear-gradient(135deg,rgba(34,197,94,0.25),rgba(34,197,94,0.12));
                    border:1px solid rgba(34,197,94,0.6);border-radius:20px;padding:1.4rem 1.6rem;
                    box-shadow:0 6px 24px rgba(0,0,0,0.35);text-align:center;backdrop-filter:blur(8px);">
            <div style="font-size:2rem;margin-bottom:4px;">🏷️</div>
            <div style="font-size:2.4rem;font-weight:800;color:#22c55e;font-family:'Playfair Display',serif;
                        text-shadow:0 2px 8px rgba(0,0,0,0.4);line-height:1.1;">{total_productos}</div>
            <div style="font-size:0.8rem;color:#fff;font-weight:600;text-transform:uppercase;
                        letter-spacing:0.1em;margin-top:6px;opacity:0.85;">Productos en Stock</div>
        </div>
        <div style="flex:1;min-width:200px;background:linear-gradient(135deg,rgba(239,68,68,0.25),rgba(239,68,68,0.12));
                    border:1px solid rgba(239,68,68,0.6);border-radius:20px;padding:1.4rem 1.6rem;
                    box-shadow:0 6px 24px rgba(0,0,0,0.35);text-align:center;backdrop-filter:blur(8px);">
            <div style="font-size:2rem;margin-bottom:4px;">⚠️</div>
            <div style="font-size:2.4rem;font-weight:800;color:#ef4444;font-family:'Playfair Display',serif;
                        text-shadow:0 2px 8px rgba(0,0,0,0.4);line-height:1.1;">{stock_bajo}</div>
            <div style="font-size:0.8rem;color:#fff;font-weight:600;text-transform:uppercase;
                        letter-spacing:0.1em;margin-top:6px;opacity:0.85;">Stock Crítico (&lt;50)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabla de stock con components.html ──
    st.markdown("""
    <div style="font-size:1.3rem;font-weight:700;color:#fff;margin:0.5rem 0 0.8rem 0;
                text-shadow:0 1px 4px rgba(0,0,0,0.5);">📋 Stock Actual por Producto</div>
    """, unsafe_allow_html=True)

    df_tabla = df_filtrado[["producto", "categoria", "presentacion", "stock", "unidad"]].copy()
    df_tabla = df_tabla.sort_values("stock", ascending=False)

    filas_html = ""
    for _, row in df_tabla.iterrows():
        stock_val = float(row["stock"])
        if stock_val < 50:
            stock_color = "#ef4444"
        elif stock_val < 200:
            stock_color = "#f59e0b"
        else:
            stock_color = "#22c55e"

        filas_html += f"""
        <tr onmouseover="this.style.backgroundColor='rgba(212,160,23,0.12)'"
            onmouseout="this.style.backgroundColor='transparent'">
            <td style="padding:9px 13px;color:#f0f0f5;font-size:0.88rem;font-weight:600;">{row["producto"]}</td>
            <td style="padding:9px 13px;color:#d4c8a8;font-size:0.84rem;">{row["categoria"]}</td>
            <td style="padding:9px 13px;color:#b0b0c0;font-size:0.84rem;">{row["presentacion"]}</td>
            <td style="padding:9px 13px;color:{stock_color};font-size:0.95rem;font-weight:800;text-align:right;">{stock_val:,.2f}</td>
            <td style="padding:9px 13px;color:#a0a0b0;font-size:0.82rem;">{row["unidad"]}</td>
        </tr>"""

    tabla_html = f"""<!DOCTYPE html>
<html><head><style>
  body {{ margin:0; padding:0; background:transparent; font-family:'DM Sans',sans-serif; }}
  .wrap {{ overflow-x:auto; border-radius:14px; border:1px solid rgba(212,160,23,0.35); box-shadow:0 6px 24px rgba(0,0,0,0.4); }}
  table {{ width:100%; border-collapse:collapse; background:rgba(22,22,28,0.97); }}
  thead tr {{ background:linear-gradient(135deg,#d4a017 0%,#b87a0c 100%); }}
  th {{ padding:11px 13px; color:#1a1a1f; font-weight:700; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.07em; white-space:nowrap; }}
  tbody tr {{ border-bottom:1px solid rgba(212,160,23,0.15); transition:background 0.2s; }}
</style></head>
<body><div class="wrap"><table>
  <thead><tr>
    <th style="text-align:left;">📦 Producto</th>
    <th style="text-align:left;">📁 Categoría</th>
    <th style="text-align:left;">Presentación</th>
    <th style="text-align:right;">Stock</th>
    <th style="text-align:left;">Unidad</th>
  </tr></thead>
  <tbody>{filas_html}</tbody>
</table></div></body></html>"""

    import streamlit.components.v1 as components
    altura = min(700, 100 + len(df_tabla) * 42)
    components.html(tabla_html, height=altura, scrolling=True)


# ══════════════════════════════════════════════════════════════
# NUEVO INGRESO - CON REMITO OBLIGATORIO PARA NO ADMIN
# ══════════════════════════════════════════════════════════════

def pagina_ingreso():
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>📥 Registrar Ingreso</h1>
            <p>📋 Registra la entrada de productos al inventario</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    rol = st.session_state.get("rol", "")
    es_admin = (rol == "admin")
    
    establecimientos = get_establecimientos()
    categorias = get_categorias()
    proveedores = get_proveedores()

    if not establecimientos:
        st.warning("⚠️ No hay establecimientos cargados.")
        return
    
    if not categorias:
        st.warning("⚠️ No hay categorías cargadas.")
        return

    if es_admin:
        estab_options = {e["nombre"]: e["id"] for e in establecimientos}
        estab_sel = st.selectbox("🏢 Establecimiento *", list(estab_options.keys()), key="ing_estab")
        establecimiento_id = estab_options[estab_sel]
        establecimiento_nombre = estab_sel
    else:
        establecimiento_id = st.session_state.get("establecimiento_id")
        establecimiento_nombre = st.session_state.get("establecimiento_nombre", "")
        st.info(f"📍 Establecimiento: {establecimiento_nombre}")

    col1, col2 = st.columns(2)
    with col1:
        cat_options = {c["nombre"]: c["id"] for c in categorias}
        cat_sel = st.selectbox("📁 Categoría *", list(cat_options.keys()), key="ing_cat")
        cat_id = cat_options[cat_sel]

    es_agroquimico_ing = "agroquimico" in cat_sel.lower() or "agroquímico" in cat_sel.lower()
    subcategoria_ing = None
    if es_agroquimico_ing:
        subcategoria_ing = st.selectbox(
            "🌿 Tipo de Agroquímico *",
            ["Herbicidas", "Insecticidas", "Coadyuvantes"],
            key="ing_subcategoria"
        )

    with col2:
        productos = get_productos(cat_id, subcategoria_ing if es_agroquimico_ing else None)
        if not productos:
            st.warning("⚠️ No hay productos en esta categoría.")
            return
        prod_options = {p["nombre"]: p["id"] for p in productos}
        prod_sel = st.selectbox("🏷️ Producto *", list(prod_options.keys()), key="ing_prod")
        producto_id = prod_options[prod_sel]

    from zoneinfo import ZoneInfo
    _now_arg = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).replace(tzinfo=None)
    st.caption(f"🕐 Fecha y hora del registro: **{_now_arg.strftime('%d/%m/%Y %H:%M')}**")

    # ── Campo para subir remito (obligatorio para no admin) ──
    if not es_admin:
        st.markdown("### 📎 Remito obligatorio")
        st.info("Debes adjuntar el remito en formato PDF que respalde este ingreso.")
        archivo_remito = st.file_uploader(
            "Seleccionar archivo PDF del remito *",
            type=["pdf"],
            key="remito_ingreso"
        )
        if archivo_remito is not None:
            st.success(f"✅ Archivo seleccionado: {archivo_remito.name} - {len(archivo_remito.getvalue())} bytes")
    else:
        archivo_remito = None
        st.caption("ℹ️ Como administrador, no es obligatorio adjuntar remito.")

    with st.form("form_ingreso", clear_on_submit=True):
        col3, col4, col5 = st.columns(3)

        with col3:
            cantidad = st.number_input("📦 Cantidad *", min_value=0.001, step=0.5, format="%.3f")

        with col4:
            prov_options = {p["nombre"]: p["id"] for p in proveedores}
            if prov_options:
                prov_sel = st.selectbox("🏭 Proveedor", ["Sin proveedor"] + list(prov_options.keys()))
                proveedor_id = prov_options[prov_sel] if prov_sel != "Sin proveedor" else None
            else:
                proveedor_id = None

        with col5:
            tipo_ingreso = st.selectbox("📌 Tipo de Ingreso", ["Compra", "Devolución", "Traslado", "Otro"])

        observaciones = st.text_area("📝 Observaciones", placeholder="N° factura, lote, detalles adicionales...")

        submitted = st.form_submit_button("✅ Registrar Ingreso", use_container_width=True)

        if submitted:
            if cantidad <= 0:
                st.error("❌ La cantidad debe ser mayor a 0")
                return
            
            if not es_admin and archivo_remito is None:
                st.error("❌ Es obligatorio adjuntar el remito en formato PDF para registrar el ingreso.")
                return

            try:
                with st.spinner("Registrando ingreso..."):
                    observaciones_full = f"[{tipo_ingreso}] {observaciones}" if observaciones else f"[{tipo_ingreso}]"
                    
                    now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).replace(tzinfo=None)
                    fecha_con_hora = now.isoformat()
                    
                    payload = {
                        "tipo": "ingreso",
                        "producto_id": producto_id,
                        "establecimiento_id": establecimiento_id,
                        "cantidad": float(cantidad),
                        "fecha": fecha_con_hora,
                        "proveedor_id": proveedor_id,
                        "observaciones": observaciones_full,
                        "usuario_id": st.session_state.get("user_id"),
                    }
                    
                    resultado = supabase.table("movimientos").insert(payload).execute()
                    movimiento_id = resultado.data[0]["id"] if resultado.data else None
                    
                    # Subir el remito si existe
                    remito_subido = False
                    if movimiento_id and archivo_remito is not None:
                        url = subir_remito_pdf(archivo_remito, movimiento_id, st.session_state.get("user_id"), establecimiento_id)
                        remito_subido = url is not None
                    
                    st.success(f"✅ Ingreso registrado exitosamente!" + (" — Remito adjuntado" if remito_subido else ""))
                    st.balloons()
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error al guardar: {e}")


# ══════════════════════════════════════════════════════════════
# NUEVO EGRESO
# ══════════════════════════════════════════════════════════════

def pagina_egreso():
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>📤 Registrar Egreso</h1>
            <p>📋 Registra la salida de productos del inventario</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    rol = st.session_state.get("rol", "")
    es_admin = (rol == "admin")
    
    establecimientos = get_establecimientos()
    categorias = get_categorias()

    if not establecimientos:
        st.warning("⚠️ No hay establecimientos cargados.")
        return

    if es_admin:
        estab_options = {e["nombre"]: e["id"] for e in establecimientos}
        estab_sel = st.selectbox("🏢 Establecimiento *", list(estab_options.keys()), key="egr_estab")
        establecimiento_id = estab_options[estab_sel]
    else:
        establecimiento_id = st.session_state.get("establecimiento_id")
        st.info(f"📍 Establecimiento: {st.session_state.get('establecimiento_nombre', '')}")

    col1, col2 = st.columns(2)
    with col1:
        cat_options = {c["nombre"]: c["id"] for c in categorias}
        cat_sel = st.selectbox("📁 Categoría *", list(cat_options.keys()), key="egr_cat")
        cat_id = cat_options[cat_sel]

    es_agroquimico_egr = "agroquimico" in cat_sel.lower() or "agroquímico" in cat_sel.lower()
    subcategoria_egr = None
    if es_agroquimico_egr:
        subcategoria_egr = st.selectbox(
            "🌿 Tipo de Agroquímico *",
            ["Herbicidas", "Insecticidas", "Coadyuvantes"],
            key="egr_subcategoria"
        )

    with col2:
        productos = get_productos(cat_id, subcategoria_egr if es_agroquimico_egr else None)
        if not productos:
            st.warning("⚠️ No hay productos en esta categoría.")
            return
        prod_options = {p["nombre"]: p["id"] for p in productos}
        prod_sel = st.selectbox("🏷️ Producto *", list(prod_options.keys()), key="egr_prod")
        producto_id = prod_options[prod_sel]
        
        stock_actual_df = get_stock_por_producto(establecimiento_id)
        if not stock_actual_df.empty:
            prod_stock = stock_actual_df[stock_actual_df["producto_id"] == producto_id]
            if not prod_stock.empty:
                st.caption(f"📊 Stock disponible: {prod_stock.iloc[0]['stock']:.2f}")

    from zoneinfo import ZoneInfo
    st.caption(f"🕐 Fecha y hora del registro: **{datetime.now(ZoneInfo('America/Argentina/Buenos_Aires')).strftime('%d/%m/%Y %H:%M')}**")

    if not es_admin:
        st.markdown("### 📎 Remito obligatorio")
        st.info("Debes adjuntar el remito en formato PDF que respalde este egreso.")
        archivo_remito = st.file_uploader("Seleccionar archivo PDF del remito *", type=["pdf"], key="remito_egreso")
        if archivo_remito is not None:
            st.success(f"✅ Archivo seleccionado: {archivo_remito.name}")
    else:
        archivo_remito = None

    with st.form("form_egreso", clear_on_submit=True):
        cantidad = st.number_input("📦 Cantidad *", min_value=0.001, step=0.5, format="%.3f")
        tipo_egreso = st.selectbox("📌 Tipo de Egreso", ["Uso", "Venta", "Traslado", "Merma", "Otro"])
        observaciones = st.text_area("📝 Observaciones", placeholder="Motivo del egreso, destino, responsable, etc.")

        submitted = st.form_submit_button("✅ Registrar Egreso", use_container_width=True)

        if submitted:
            if cantidad <= 0:
                st.error("❌ La cantidad debe ser mayor a 0")
                return

            if not es_admin and archivo_remito is None:
                st.error("❌ Es obligatorio adjuntar el remito en formato PDF.")
                return

            stock_actual_df = get_stock_por_producto(establecimiento_id)
            if not stock_actual_df.empty:
                prod_stock = stock_actual_df[stock_actual_df["producto_id"] == producto_id]
                if not prod_stock.empty and prod_stock.iloc[0]["stock"] < cantidad:
                    st.error(f"❌ Stock insuficiente. Disponible: {prod_stock.iloc[0]['stock']:.2f}")
                    return

            try:
                with st.spinner("Registrando egreso..."):
                    observaciones_full = f"[{tipo_egreso}] {observaciones}" if observaciones else f"[{tipo_egreso}]"
                    now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).replace(tzinfo=None)
                    
                    payload = {
                        "tipo": "egreso",
                        "producto_id": producto_id,
                        "establecimiento_id": establecimiento_id,
                        "cantidad": float(cantidad),
                        "fecha": now.isoformat(),
                        "observaciones": observaciones_full,
                        "usuario_id": st.session_state.get("user_id"),
                    }
                    resultado = supabase.table("movimientos").insert(payload).execute()
                    movimiento_id = resultado.data[0]["id"] if resultado.data else None
                    
                    remito_subido = False
                    if movimiento_id and archivo_remito is not None:
                        url = subir_remito_pdf(archivo_remito, movimiento_id, st.session_state.get("user_id"), establecimiento_id)
                        remito_subido = url is not None
                    
                    st.success(f"✅ Egreso registrado exitosamente!" + (" — Remito adjuntado" if remito_subido else ""))
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error al guardar: {e}")


# ══════════════════════════════════════════════════════════════
# HISTORIAL
# ══════════════════════════════════════════════════════════════

def pagina_historial():
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>📋 Historial de Movimientos</h1>
            <p>📋 Consulta y filtra todos los movimientos de stock</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Fila 1: Tipo + Fechas ──
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        tipo_filtro = st.selectbox("🔄 Tipo", ["Todos", "ingreso", "egreso"], key="hist_tipo")
    with col_f2:
        fecha_desde = st.date_input("📅 Desde", value=date.today() - timedelta(days=30), key="hist_desde")
    with col_f3:
        fecha_hasta = st.date_input("📅 Hasta", value=date.today(), key="hist_hasta")

    # Cargar todos los movimientos del período para derivar categorías/productos disponibles
    movimientos = get_movimientos_con_filtros(
        establecimiento_id=estab_filter(),
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        tipo=tipo_filtro if tipo_filtro != "Todos" else None
    )

    if not movimientos:
        st.info("💡 Sin movimientos en el período seleccionado.")
        return

    df = pd.DataFrame(movimientos)
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"])
        df = df.sort_values("fecha", ascending=False)

    df["producto_nombre"]      = df["productos"].apply(lambda x: x.get("nombre", "") if isinstance(x, dict) else "")
    df["categoria_nombre"]     = df["productos"].apply(lambda x: x.get("categorias", {}).get("nombre", "") if isinstance(x, dict) and x.get("categorias") else "")
    df["establecimiento_nombre"] = df["establecimientos"].apply(lambda x: x.get("nombre", "") if isinstance(x, dict) else "")
    df["fecha_str"] = df["fecha"].dt.strftime("%d/%m/%Y %H:%M")

    # ── Fila 2: Categoría + Subcategoría + Producto ──
    SUBCATS_AGRO = ["Herbicidas", "Insecticidas", "Coadyuvantes"]
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        cats_disp = sorted([c for c in df["categoria_nombre"].dropna().unique() if c])
        cat_sel = st.selectbox("📁 Categoría", ["Todas"] + cats_disp, key="hist_cat")

    es_agro_hist = cat_sel != "Todas" and ("agroqui" in cat_sel.lower() or "agroquí" in cat_sel.lower())

    with col_c2:
        if es_agro_hist:
            subcat_sel = st.selectbox("🌿 Tipo Agroquímico", ["Todos"] + SUBCATS_AGRO, key="hist_subcat")
        else:
            subcat_sel = "Todos"
            st.selectbox("🌿 Tipo Agroquímico", ["—"], key="hist_subcat", disabled=True)

    with col_c3:
        df_para_prods = df.copy()
        if cat_sel != "Todas":
            df_para_prods = df_para_prods[df_para_prods["categoria_nombre"] == cat_sel]
        prods_disp = sorted([p for p in df_para_prods["producto_nombre"].dropna().unique() if p])
        prod_sel = st.selectbox("📦 Producto", ["Todos"] + prods_disp, key="hist_prod")

    # Aplicar filtros de categoría, subcategoría y producto
    if cat_sel != "Todas":
        df = df[df["categoria_nombre"] == cat_sel]
    if es_agro_hist and subcat_sel != "Todos":
        prods_subcat = get_productos(subcategoria=subcat_sel)
        nombres_subcat = [p["nombre"] for p in prods_subcat]
        df = df[df["producto_nombre"].isin(nombres_subcat)]
    if prod_sel != "Todos":
        df = df[df["producto_nombre"] == prod_sel]

    # Generar link de remito
    df["remito_link"] = df.apply(
        lambda r: generar_link_pdf(r.get("remito_url")) if r.get("remito_url") else "—",
        axis=1
    )

    st.markdown(f"### 📊 Resultados: **{len(df)}** movimientos")

    display_df = df[["fecha_str", "tipo", "establecimiento_nombre", "producto_nombre", "cantidad", "remito_link", "observaciones"]].copy()
    display_df.columns = ["Fecha", "Tipo", "Establecimiento", "Producto", "Cantidad", "Remito", "Observaciones"]

    filas_html = ""
    for _, row in display_df.iterrows():
        if row["Tipo"] == "ingreso":
            row_bg = "rgba(34,197,94,0.10)"
            tipo_badge = '<span style="background:#22c55e;color:#000;padding:2px 10px;border-radius:20px;font-size:0.78rem;font-weight:700;">▲ ingreso</span>'
        else:
            row_bg = "rgba(239,68,68,0.10)"
            tipo_badge = '<span style="background:#ef4444;color:#fff;padding:2px 10px;border-radius:20px;font-size:0.78rem;font-weight:700;">▼ egreso</span>'

        obs = str(row["Observaciones"]) if row["Observaciones"] and str(row["Observaciones"]) not in ["nan", "None", ""] else "—"
        remito = str(row["Remito"]) if row["Remito"] and str(row["Remito"]) not in ["nan", "None", "", "—"] else "—"
        try:
            cantidad_fmt = f"{float(row['Cantidad']):,.2f}"
        except Exception:
            cantidad_fmt = str(row["Cantidad"])

        filas_html += f"""
        <tr style="background-color:{row_bg};border-bottom:1px solid rgba(212,160,23,0.15);"
            onmouseover="this.style.backgroundColor='rgba(212,160,23,0.12)'"
            onmouseout="this.style.backgroundColor='{row_bg}'">
            <td style="padding:9px 13px;color:#e8e8f0;font-size:0.84rem;white-space:nowrap;">{row['Fecha']}</td>
            <td style="padding:9px 13px;text-align:center;">{tipo_badge}</td>
            <td style="padding:9px 13px;color:#d4c8a8;font-size:0.84rem;">{row['Establecimiento']}</td>
            <td style="padding:9px 13px;color:#f0f0f5;font-size:0.84rem;font-weight:600;">{row['Producto']}</td>
            <td style="padding:9px 13px;color:#d4a017;font-size:0.9rem;font-weight:700;text-align:right;">{cantidad_fmt}</td>
            <td style="padding:9px 13px;text-align:center;">{remito}</td>
            <td style="padding:9px 13px;color:#a0a0b0;font-size:0.82rem;">{obs}</td>
        </tr>"""

    tabla_html = f"""<!DOCTYPE html>
<html><head><style>
  body {{ margin:0; padding:0; background:transparent; font-family:'DM Sans',sans-serif; }}
  .wrap {{ overflow-x:auto; border-radius:14px; border:1px solid rgba(212,160,23,0.35); box-shadow:0 6px 24px rgba(0,0,0,0.4); }}
  table {{ width:100%; border-collapse:collapse; background:rgba(22,22,28,0.97); }}
  thead tr {{ background:linear-gradient(135deg,#d4a017 0%,#b87a0c 100%); }}
  th {{ padding:11px 13px; color:#1a1a1f; font-weight:700; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.07em; white-space:nowrap; }}
</style></head>
<body><div class="wrap"><table>
  <thead><tr>
    <th style="text-align:left;">📅 Fecha</th>
    <th style="text-align:center;">Tipo</th>
    <th style="text-align:left;">🏢 Establecimiento</th>
    <th style="text-align:left;">📦 Producto</th>
    <th style="text-align:right;">Cantidad</th>
    <th style="text-align:center;">📄 Remito</th>
    <th style="text-align:left;">📝 Observaciones</th>
  </tr></thead>
  <tbody>{filas_html}</tbody>
</table></div></body></html>"""

    import streamlit.components.v1 as components
    altura = min(700, 100 + len(display_df) * 42)
    components.html(tabla_html, height=altura, scrolling=True)


# ══════════════════════════════════════════════════════════════
# ALERTAS
# ══════════════════════════════════════════════════════════════

def pagina_alertas():
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>⚠️ Alertas de Stock</h1>
            <p>📋 Monitoreo de stock bajo</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    umbral = st.number_input("⚠️ Umbral de alerta (unidades)", min_value=0, value=50, step=10)
    
    stock_productos = get_stock_por_producto(estab_filter())
    
    if stock_productos.empty:
        st.info("💡 Sin datos para mostrar alertas.")
        return
    
    stock_bajo = stock_productos[stock_productos["stock"] < umbral]
    
    if not stock_bajo.empty:
        st.warning(f"⚠️ {len(stock_bajo)} productos con stock menor a {umbral} unidades")
        st.dataframe(stock_bajo[["producto", "categoria", "stock", "unidad"]], use_container_width=True)
    else:
        st.success(f"✅ Todos los productos tienen stock mayor o igual a {umbral} unidades.")


# ══════════════════════════════════════════════════════════════
# REPORTES
# ══════════════════════════════════════════════════════════════

def pagina_reportes():
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>📈 Reportes</h1>
            <p>📋 Análisis de movimientos</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    movimientos = get_movimientos(estab_filter(), limit=5000)
    
    if not movimientos:
        st.info("💡 Sin datos para generar reportes.")
        return
    
    df = pd.DataFrame(movimientos)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    
    ingresos = df[df["tipo"] == "ingreso"]["cantidad"].sum() if "ingreso" in df["tipo"].values else 0
    egresos = df[df["tipo"] == "egreso"]["cantidad"].sum() if "egreso" in df["tipo"].values else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📥 Total Ingresos", f"{ingresos:,.0f}")
    with col2:
        st.metric("📤 Total Egresos", f"{egresos:,.0f}")
    
    resumen = df.groupby(["mes", "tipo"])["cantidad"].sum().reset_index()
    st.dataframe(resumen, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# ADMIN: PROVEEDORES, PRODUCTOS, USUARIOS
# ══════════════════════════════════════════════════════════════

def pagina_proveedores():
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>🏭 Proveedores</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    proveedores = get_proveedores()
    
    with st.expander("➕ Agregar proveedor"):
        with st.form("nuevo_proveedor"):
            nombre = st.text_input("Nombre")
            if st.form_submit_button("Guardar") and nombre:
                supabase.table("proveedores").insert({"nombre": nombre, "activo": True}).execute()
                st.rerun()
    
    if proveedores:
        st.dataframe(pd.DataFrame(proveedores)[["nombre", "activo"]], use_container_width=True)


def pagina_productos():
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>📦 Productos</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    categorias = get_categorias()
    cat_options = {c["nombre"]: c["id"] for c in categorias}
    
    with st.expander("➕ Agregar producto"):
        cat_sel = st.selectbox("Categoría", list(cat_options.keys()))
        with st.form("nuevo_producto"):
            nombre = st.text_input("Nombre")
            presentacion = st.text_input("Presentación")
            unidad = st.selectbox("Unidad", ["litros", "kg", "unidades"])
            if st.form_submit_button("Guardar") and nombre:
                supabase.table("productos").insert({
                    "categoria_id": cat_options[cat_sel],
                    "nombre": nombre,
                    "presentacion": presentacion,
                    "unidad_medida": unidad,
                    "activo": True
                }).execute()
                st.rerun()
    
    productos = get_productos()
    if productos:
        df = pd.DataFrame(productos)
        df["categoria"] = df["categorias"].apply(lambda x: x["nombre"] if x else "N/A")
        st.dataframe(df[["nombre", "categoria", "presentacion", "unidad_medida", "activo"]], use_container_width=True)


def pagina_usuarios():
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>👥 Usuarios</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        usuarios = supabase.table("usuarios").select("*").execute().data
        if usuarios:
            df = pd.DataFrame(usuarios)
            display_cols = ["nombre", "email", "rol", "establecimiento_nombre"]
            st.dataframe(df[display_cols], use_container_width=True)
    except Exception as e:
        st.error(f"Error: {e}")


def pagina_consolidado():
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>🌐 Vista Consolidada</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    stock_df = get_stock_por_establecimiento()
    
    if stock_df.empty:
        st.info("💡 Sin datos consolidados.")
        return
    
    st.dataframe(stock_df, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    if not check_auth():
        login()
        return

    if not verificar_perfil():
        return

    if (st.session_state.get("rol") != "admin" and 
        not st.session_state.get("password_changed", False) and
        not st.session_state.get("skip_password_check", False)):
        mostrar_cambio_password()
        return

    sidebar()

    pagina = st.session_state.get("pagina", "Dashboard")
    rol = st.session_state.get("rol", "establecimiento")
    consolidado = es_vista_consolidado()

    if consolidado and rol == "admin":
        rutas = {
            "Consolidado": pagina_consolidado,
            "Alertas": pagina_alertas,
            "Reportes": pagina_reportes,
            "Proveedores": pagina_proveedores,
            "Productos": pagina_productos,
            "Usuarios": pagina_usuarios,
        }
        rutas.get(pagina, pagina_consolidado)()
    elif rol == "admin":
        rutas = {
            "Dashboard": pagina_dashboard,
            "Nuevo Ingreso": pagina_ingreso,
            "Nuevo Egreso": pagina_egreso,
            "Historial": pagina_historial,
            "Alertas": pagina_alertas,
            "Reportes": pagina_reportes,
            "Proveedores": pagina_proveedores,
            "Productos": pagina_productos,
            "Usuarios": pagina_usuarios,
        }
        rutas.get(pagina, pagina_dashboard)()
    elif rol == "establecimiento" and st.session_state.get("establecimiento_id"):
        rutas = {
            "Dashboard": pagina_dashboard,
            "Nuevo Ingreso": pagina_ingreso,
            "Nuevo Egreso": pagina_egreso,
            "Historial": pagina_historial,
            "Alertas": pagina_alertas,
            "Reportes": pagina_reportes,
        }
        rutas.get(pagina, pagina_dashboard)()
    else:
        st.error("⚠️ Configuración incompleta.")
        if st.button("Cerrar sesión"):
            logout()
        return

    estab_nombre = st.session_state.get("estab_activo_nombre", 
                                         st.session_state.get("establecimiento_nombre", "Consolidado"))
    st.markdown(f"""
    <div class="footer">
        <p>🌾 Sistema de Control de Stock Agrícola | 📍 {estab_nombre}</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
