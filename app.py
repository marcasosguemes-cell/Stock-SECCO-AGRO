"""
SISTEMA DE CONTROL DE STOCK AGRÍCOLA
App principal Streamlit — La Sonia / San Guillermo / Camba Pora
Versión mejorada: seguridad, infraestructura, estética, información y almacenamiento.
"""

import html
import logging
import streamlit as st
from supabase import create_client, Client
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

def now_arg():
    """Retorna la hora actual de Buenos Aires sin tzinfo (naive)."""
    return datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).replace(tzinfo=None)

def parse_fecha(series):
    """Convierte columna fecha a datetime naive en hora Argentina.
    - Si viene con timezone (ej: +00:00 UTC de Supabase): convierte a Argentina.
    - Si viene sin timezone (naive): asume que ya está en hora Argentina, no convierte.
    """
    try:
        parsed = pd.to_datetime(series, errors="coerce")
        # Si tiene timezone info → convertir a Argentina
        if parsed.dt.tz is not None:
            return parsed.dt.tz_convert("America/Argentina/Buenos_Aires").dt.tz_localize(None)
        # Sin timezone → ya está en hora Argentina (guardado con now_arg())
        return parsed
    except Exception:
        return pd.to_datetime(series, errors="coerce")
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import uuid
import base64

# ── Logging estructurado ──────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("stock_agricola")

# ── Configuración de página ───────────────────────────────────
st.set_page_config(
    page_title="Stock Agrícola - SECCO AGRO",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Configuración central (Settings) ─────────────────────────
class Settings:
    SUPABASE_URL: str = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY: str = st.secrets["SUPABASE_ANON_KEY"]
    SUPABASE_STORAGE_BUCKET: str = st.secrets.get("SUPABASE_STORAGE_BUCKET", "remitos")
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15
    SESSION_TIMEOUT_MINUTES: int = 120
    MAX_PDF_SIZE_MB: int = 10
    PASSWORD_MIN_LENGTH: int = 8
    STOCK_CRITICO_DEFAULT: int = 50

cfg = Settings()

# ── Cliente Supabase ──────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    return create_client(cfg.SUPABASE_URL, cfg.SUPABASE_KEY)

supabase = get_supabase()


# ══════════════════════════════════════════════════════════════
# CSS — variables de token + estilos
# ══════════════════════════════════════════════════════════════

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

    :root {
        --gold: #d4a017;
        --gold-light: #e5b52a;
        --gold-dark: #b87a0c;
        --gold-05: rgba(212,160,23,0.05);
        --gold-10: rgba(212,160,23,0.10);
        --gold-15: rgba(212,160,23,0.15);
        --gold-18: rgba(212,160,23,0.18);
        --gold-25: rgba(212,160,23,0.25);
        --gold-30: rgba(212,160,23,0.30);
        --gold-35: rgba(212,160,23,0.35);
        --gold-40: rgba(212,160,23,0.40);
        --gold-60: rgba(212,160,23,0.60);
        --gold-75: rgba(212,160,23,0.75);
        --gold-85: rgba(212,160,23,0.85);
        --bg-main: #0e0e14;
        --bg-card: rgba(45,45,52,0.85);
        --bg-surface: rgba(40,40,50,0.70);
        --bg-dark: rgba(22,22,28,0.97);
        --text-primary: #f0f0f5;
        --text-secondary: #c8c8d4;
        --text-muted: #a0a0b0;
        --text-gold: #d4c8a8;
        --green: #22c55e;
        --red: #ef4444;
        --amber: #f59e0b;
    }

    [data-testid="stHeader"], header[data-testid="stHeader"], .stAppHeader,
    [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
    }
    [data-testid="collapsedControl"],
    button[data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    button[data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    html, body { background: var(--bg-main) !important; }

    .stApp {
        background: var(--bg-main) !important;
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
        background: rgba(6,6,10,0.55) !important;
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
        border-right: 1px solid rgba(100,100,120,0.3) !important;
        box-shadow: 4px 0 24px rgba(0,0,0,0.4) !important;
    }

    .sidebar-toggle-wrap > div > button {
        width: 42px !important;
        height: 42px !important;
        padding: 0 !important;
        font-size: 20px !important;
        background: var(--gold-85) !important;
        color: #1a1a1f !important;
        border: none !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.5) !important;
        cursor: pointer !important;
        min-height: unset !important;
        line-height: 1 !important;
    }
    .sidebar-toggle-wrap > div > button:hover {
        background: var(--gold) !important;
        transform: scale(1.06) !important;
        color: #000 !important;
    }

    [data-testid="stSelectbox"] label,
    div[data-testid="stSelectbox"] > label,
    .stSelectbox label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    [data-testid="stSelectbox"] > div > div,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: rgba(55,55,65,0.95) !important;
        border: 1px solid var(--gold-40) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] span,
    [data-testid="stSelectbox"] [data-baseweb="select"] div {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    [data-testid="stDateInput"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stTextInput"] label,
    [data-testid="stTextArea"] label,
    [data-testid="stFileUploader"] label,
    [data-testid="stMultiSelect"] label,
    [data-testid="stCheckbox"] label,
    [data-testid="stCheckbox"] span,
    [data-testid="stRadio"] label,
    [data-testid="stRadio"] span {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* Tabs blancos y visibles */
    [data-testid="stTabs"] [data-baseweb="tab"] {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
        color: var(--gold) !important;
        border-bottom-color: var(--gold) !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid rgba(255,255,255,0.2) !important;
    }

    /* Multiselect etiquetas y tags */
    [data-testid="stMultiSelect"] [data-baseweb="select"] span,
    [data-testid="stMultiSelect"] [data-baseweb="select"] div,
    [data-testid="stMultiSelect"] [data-baseweb="tag"] span {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] .stButton button {
        background: var(--bg-surface) !important;
        border: 1px solid var(--gold-25) !important;
        width: 100% !important;
        text-align: left !important;
        padding: 0.6rem 1rem !important;
        border-radius: 10px !important;
        margin: 3px 0 !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        color: var(--text-secondary) !important;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background: var(--gold-18) !important;
        border-color: var(--gold-60) !important;
        transform: translateX(4px) !important;
        color: #f0e8c8 !important;
    }

    .sidebar-header {
        text-align: center;
        padding: 1.6rem 0 1.2rem 0;
        border-bottom: 1px solid var(--gold-40);
        margin-bottom: 1.4rem;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .sidebar-logo-oval {
        background: #f7f3e8;
        border: 2px solid var(--gold-60);
        border-radius: 50%;
        width: 185px;
        height: 185px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        margin-bottom: 12px;
    }

    .sidebar-logo {
        width: 100% !important;
        height: auto !important;
        display: block;
        transform: scale(1.9);
        transform-origin: center center;
    }

    .sidebar-header h1 {
        font-family: 'Playfair Display', serif !important;
        font-size: 1.4rem !important;
        margin: 0;
        color: var(--gold) !important;
        letter-spacing: 0.04em;
        font-weight: 700;
    }

    .profile-card {
        text-align: center;
        padding: 0.9rem 1rem;
        margin: 0.5rem 0 1rem 0;
        background: var(--bg-surface) !important;
        border: 1px solid var(--gold-25);
        border-radius: 16px;
        backdrop-filter: blur(8px);
    }

    .profile-name {
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text-primary) !important;
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
        border: 2px solid var(--gold-50, rgba(212,160,23,0.5));
        border-radius: 50%;
        width: 420px;
        height: 252px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }

    .title-logo {
        width: 100% !important;
        height: 100% !important;
        object-fit: contain !important;
        display: block;
        padding: 15px;
    }

    .title-bubble-login {
        background: rgba(0,0,0,0.65);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255,215,120,0.6);
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
        background: linear-gradient(135deg,rgba(200,160,96,0.95) 0%,rgba(184,144,90,0.95) 100%);
        border-radius: 20px;
        padding: 1rem 2.2rem;
        display: inline-block;
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
        text-align: center;
        margin-bottom: 1.4rem;
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
        background: linear-gradient(145deg,rgba(55,55,62,0.9) 0%,rgba(45,45,52,0.95) 100%) !important;
        border: 1px solid var(--gold-35);
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
        border-color: var(--gold-60);
    }

    .metric-value {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.6rem !important;
        font-weight: 700;
        color: var(--text-primary) !important;
        margin: 0.4rem 0;
    }

    .metric-label {
        font-size: 0.75rem !important;
        color: var(--gold) !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 700;
    }

    .stButton > button {
        background: linear-gradient(135deg,var(--gold),var(--gold-dark)) !important;
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
        background: linear-gradient(135deg,var(--gold-light),#c98a1a) !important;
        color: #000000 !important;
    }

    [data-testid="stForm"] {
        background: var(--bg-card) !important;
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid var(--gold-30);
    }



    .footer {
        text-align: center;
        padding: 0.3rem 1rem;
        color: #a8a8b0 !important;
        font-size: 0.72rem;
        border-top: 1px solid var(--gold-25);
        margin-top: 0.5rem;
    }

    .password-warning {
        background: linear-gradient(135deg,rgba(212,160,23,0.2),rgba(180,120,10,0.15));
        border: 1px solid var(--gold-60);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }
    .password-warning p,
    .password-warning strong,
    .password-warning span {
        color: var(--text-primary) !important;
    }

    .pdf-miniatura {
        background: var(--gold-15);
        border-radius: 8px;
        padding: 4px 8px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.8rem;
        text-decoration: none;
        color: var(--gold) !important;
        transition: all 0.2s ease;
    }
    .pdf-miniatura:hover {
        background: var(--gold-30);
        color: var(--text-primary) !important;
    }

    .password-strength { height: 6px; border-radius: 4px; margin-top: 6px; transition: width 0.3s ease; }

    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] h3,
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
    }

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

    [data-testid="stAppViewContainer"] h3,
    [data-testid="stAppViewContainer"] div[data-testid="stMarkdownContainer"] h3 {
        color: #FFFFFF !important;
        text-shadow: 0 1px 4px rgba(0,0,0,0.6);
    }

    [data-testid="stForm"] .stButton > button,
    [data-testid="stForm"] [data-testid="stFormSubmitButton"] > button,
    [data-testid="stFormSubmitButton"] > button,
    [data-testid="stFormSubmitButton"] > button > div,
    [data-testid="stFormSubmitButton"] button * {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    [data-testid="stForm"] h3,
    [data-testid="stForm"] label,
    [data-testid="stForm"] .stTextInput label,
    [data-testid="stForm"] p,
    [data-testid="stForm"] span,
    [data-testid="stForm"] div[data-testid="stMarkdownContainer"] h3,
    [data-testid="stForm"] div[data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
    }

    /* Responsive: tablas en móvil */
    @media (max-width: 768px) {
        .logo-oval-wrap { width: 260px !important; height: 156px !important; }
        .main-title-with-logo { font-size: 1.5rem !important; }
        .title-bubble h1 { font-size: 1.3rem !important; }
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# AUTENTICACIÓN
# ══════════════════════════════════════════════════════════════

def _login_attempts_key():
    return "login_attempts"

def _login_locked_until_key():
    return "login_locked_until"

def check_auth():
    """Verifica sesión activa y timeout de inactividad."""
    try:
        if "session" in st.session_state and st.session_state["session"]:
            # Timeout de inactividad
            last = st.session_state.get("last_activity")
            if last:
                delta = (now_arg() - last).total_seconds() / 60
                if delta > cfg.SESSION_TIMEOUT_MINUTES:
                    logout()
                    st.warning("⏰ Sesión expirada por inactividad. Volvé a ingresar.")
                    return False
            st.session_state["last_activity"] = now_arg()
            return True
        session = supabase.auth.get_session()
        if session:
            st.session_state["session"] = session
            st.session_state["user_id"] = session.user.id
            st.session_state["last_activity"] = now_arg()
            return True
        return False
    except Exception:
        return False


def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    keys_to_clear = [
        "session", "user_id", "perfil", "rol", "establecimiento_id",
        "establecimiento_nombre", "pagina", "password_changed",
        "skip_password_check", "last_activity", "estab_seleccionado",
        "estab_activo_id", "estab_activo_nombre",
    ]
    for key in keys_to_clear:
        st.session_state.pop(key, None)
    st.rerun()


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
                    st.error("Perfil no encontrado.")
                    logout()
                    return False
            except Exception as e:
                logger.error(f"Error al cargar perfil: {e}")
                st.error("Error al cargar el perfil.")
                return False
        return False
    return True


def _check_login_lockout():
    """Retorna (bloqueado: bool, segundos_restantes: int)"""
    locked_until = st.session_state.get(_login_locked_until_key())
    if locked_until:
        remaining = (locked_until - now_arg()).total_seconds()
        if remaining > 0:
            return True, int(remaining)
        else:
            st.session_state.pop(_login_locked_until_key(), None)
            st.session_state[_login_attempts_key()] = 0
    return False, 0


def _register_failed_attempt():
    attempts = st.session_state.get(_login_attempts_key(), 0) + 1
    st.session_state[_login_attempts_key()] = attempts
    if attempts >= cfg.MAX_LOGIN_ATTEMPTS:
        st.session_state[_login_locked_until_key()] = (
            now_arg() + timedelta(minutes=cfg.LOGIN_LOCKOUT_MINUTES)
        )
    return attempts


def _password_strength(pwd: str) -> tuple[int, str, str]:
    """Retorna (score 0-4, label, color)."""
    score = 0
    if len(pwd) >= cfg.PASSWORD_MIN_LENGTH:
        score += 1
    if any(c.isdigit() for c in pwd):
        score += 1
    if any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in pwd):
        score += 1
    if len(pwd) >= 12:
        score += 1
    labels = ["Muy débil", "Débil", "Regular", "Buena", "Fuerte"]
    colors = ["#ef4444", "#f97316", "#f59e0b", "#22c55e", "#16a34a"]
    return score, labels[score], colors[score]


# ══════════════════════════════════════════════════════════════
# ALMACENAMIENTO: REMITOS PDF
# ══════════════════════════════════════════════════════════════

def _validar_pdf(archivo_pdf) -> tuple[bool, str]:
    """Valida magic number y tamaño del PDF."""
    MAX_BYTES = cfg.MAX_PDF_SIZE_MB * 1024 * 1024
    data = archivo_pdf.getvalue()
    if len(data) > MAX_BYTES:
        return False, f"El archivo supera el límite de {cfg.MAX_PDF_SIZE_MB}MB."
    if not data.startswith(b"%PDF"):
        return False, "El archivo no es un PDF válido."
    return True, ""


def subir_remito_pdf(archivo_pdf, movimiento_ids, usuario_id, establecimiento_id):
    """Sube PDF a Supabase Storage y lo asocia a uno o varios movimientos.

    movimiento_ids puede ser un UUID (str) o una lista de UUIDs.
    El archivo se sube una sola vez y la misma ruta queda registrada en todos
    los movimientos del lote, de modo que el botón PDF aparezca en cada fila
    del historial.
    """
    if archivo_pdf is None:
        return None

    ok, msg = _validar_pdf(archivo_pdf)
    if not ok:
        st.error(f"❌ {msg}")
        return None

    # Normalizar a lista
    if isinstance(movimiento_ids, (str, int)):
        movimiento_ids = [movimiento_ids]

    try:
        now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
        # Nombre del archivo basado en el primer ID del lote
        primer_id = movimiento_ids[0]
        nombre_archivo = f"remito_{primer_id}_{uuid.uuid4().hex[:8]}.pdf"
        # Organización por carpetas: estab_id/año/mes/archivo
        ruta_completa = f"{establecimiento_id}/{now.year}/{now.month:02d}/{nombre_archivo}"
        archivo_bytes = archivo_pdf.getvalue()

        supabase.storage.from_(cfg.SUPABASE_STORAGE_BUCKET).upload(
            path=ruta_completa,
            file=archivo_bytes,
            file_options={"content-type": "application/pdf"}
        )

        # Asociar la misma ruta a TODOS los movimientos del lote
        for mov_id in movimiento_ids:
            supabase.table("movimientos").update({
                "remito_url": ruta_completa,
                "remito_filename": nombre_archivo
            }).eq("id", mov_id).execute()

        return ruta_completa

    except Exception as e:
        logger.error(f"Error al subir remito: {type(e).__name__}: {e}")
        st.error(f"❌ Error al subir el remito: {e}")
        return None


def get_signed_url(ruta: str) -> str | None:
    """Genera una URL firmada con 1 hora de expiración."""
    if not ruta or ruta == "—":
        return None
    try:
        res = supabase.storage.from_(cfg.SUPABASE_STORAGE_BUCKET).create_signed_url(
            path=ruta,
            expires_in=3600
        )
        return res.get("signedURL") or res.get("signed_url")
    except Exception as e:
        logger.warning(f"No se pudo generar URL firmada para {ruta}: {e}")
        return None


def generar_link_pdf(ruta_pdf):
    """Genera link HTML con URL firmada (temporal 1h)."""
    if not ruta_pdf or ruta_pdf == "—":
        return "—"
    url = get_signed_url(ruta_pdf)
    if not url:
        return "—"
    return (
        f'<a href="{html.escape(url)}" target="_blank" title="Ver remito PDF" '
        f'style="display:inline-flex;align-items:center;gap:5px;text-decoration:none;'
        f'background:linear-gradient(135deg,#c0392b,#e74c3c);color:#fff;'
        f'padding:4px 10px;border-radius:6px;font-size:0.78rem;font-weight:700;'
        f'letter-spacing:0.04em;box-shadow:0 2px 6px rgba(0,0,0,0.35);" '
        f'onmouseover="this.style.opacity=\'0.82\'" onmouseout="this.style.opacity=\'1\'">'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
        f'<polyline points="14 2 14 8 20 8"/>'
        f'<line x1="16" y1="13" x2="8" y2="13"/>'
        f'<line x1="16" y1="17" x2="8" y2="17"/>'
        f'<polyline points="10 9 9 9 8 9"/>'
        f'</svg>\u00a0PDF</a>'
    )


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

        bloqueado, segundos = _check_login_lockout()
        if bloqueado:
            minutos = segundos // 60
            st.error(f"🔒 Demasiados intentos fallidos. Intentá de nuevo en {minutos} min {segundos % 60} seg.")
            return

        with st.form("login_form"):
            st.markdown("### Bienvenido")
            email = st.text_input("Email", placeholder="usuario@ejemplo.com")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("🚀 Ingresar", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("❌ Completá email y contraseña.")
                    return
                try:
                    with st.spinner("Verificando credenciales..."):
                        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state["session"] = res.session
                        st.session_state["user_id"] = res.user.id
                        st.session_state["user_email"] = email
                        st.session_state["last_activity"] = now_arg()
                        st.session_state.pop(_login_attempts_key(), None)
                        st.session_state.pop(_login_locked_until_key(), None)

                        perfil = supabase.table("usuarios").select("*").eq("id", res.user.id).execute()
                        if perfil.data:
                            p = perfil.data[0]
                            st.session_state["perfil"] = p
                            st.session_state["rol"] = p["rol"]
                            st.session_state["establecimiento_id"] = p.get("establecimiento_id")
                            st.session_state["establecimiento_nombre"] = p.get("establecimiento_nombre")
                            st.session_state["password_changed"] = p.get("password_changed", False)
                            st.session_state["pagina"] = "Dashboard"
                            st.session_state.pop("skip_password_check", None)
                            # Log de acceso
                            try:
                                supabase.table("audit_log").insert({
                                    "accion": "login",
                                    "usuario": email,
                                    "datos": {"rol": p.get("rol", ""), "establecimiento": p.get("establecimiento_nombre", "")},
                                    "timestamp": now_arg().isoformat()
                                }).execute()
                            except Exception:
                                pass
                            st.toast("✅ ¡Bienvenido!")
                            st.rerun()
                        else:
                            st.error("❌ No se encontró tu perfil.")
                except Exception as e:
                    intentos = _register_failed_attempt()
                    restantes = cfg.MAX_LOGIN_ATTEMPTS - intentos
                    if restantes > 0:
                        st.error(f"❌ Credenciales incorrectas. {restantes} intento(s) restantes.")
                    else:
                        st.error(f"🔒 Cuenta bloqueada por {cfg.LOGIN_LOCKOUT_MINUTES} minutos.")
                    logger.warning(f"Intento de login fallido para {email}: {e}")


# ══════════════════════════════════════════════════════════════
# CAMBIO DE CONTRASEÑA
# ══════════════════════════════════════════════════════════════

def mostrar_cambio_password():
    st.markdown("""
    <div class="password-warning">
        <h3>🔐 Cambio de Contraseña Obligatorio</h3>
        <p>Por razones de seguridad, debés cambiar tu contraseña antes de continuar.</p>
        <p><strong>Importante:</strong> Usá al menos 8 caracteres, incluyendo números o símbolos.</p>
        <p>Si elegís "Más Tarde", el sistema te recordará en cada ingreso.</p>
    </div>
    """, unsafe_allow_html=True)

    nueva_password = st.text_input("Nueva Contraseña", type="password", placeholder="Mínimo 8 caracteres", key="np_main")

    if nueva_password:
        score, label, color = _password_strength(nueva_password)
        pct = int((score + 1) / 5 * 100)
        st.markdown(f"""
        <div style="font-size:0.8rem;color:{color};margin-top:2px;">Fortaleza: <strong>{label}</strong></div>
        <div style="background:rgba(255,255,255,0.1);border-radius:4px;height:6px;margin-top:4px;">
            <div style="width:{pct}%;background:{color};height:6px;border-radius:4px;transition:width 0.3s;"></div>
        </div>
        """, unsafe_allow_html=True)

    with st.form("cambiar_password_form_main"):
        confirmar_password = st.text_input("Confirmar Contraseña", type="password", placeholder="Repetí tu nueva contraseña")

        col1, col2 = st.columns(2)
        with col1:
            cambiar_btn = st.form_submit_button("✅ Cambiar Contraseña", use_container_width=True)
        with col2:
            mas_tarde_btn = st.form_submit_button("⏰ Más Tarde", use_container_width=True)

        if cambiar_btn:
            if not nueva_password:
                st.error("❌ Ingresá una nueva contraseña.")
            elif len(nueva_password) < cfg.PASSWORD_MIN_LENGTH:
                st.error(f"❌ La contraseña debe tener al menos {cfg.PASSWORD_MIN_LENGTH} caracteres.")
            elif nueva_password != confirmar_password:
                st.error("❌ Las contraseñas no coinciden.")
            else:
                score, _, _ = _password_strength(nueva_password)
                if score < 1:
                    st.error("❌ La contraseña es demasiado débil. Agregá números o símbolos.")
                else:
                    try:
                        with st.spinner("Actualizando contraseña..."):
                            supabase.auth.update_user({"password": nueva_password})
                            supabase.table("usuarios").update({"password_changed": True}).eq(
                                "id", st.session_state["user_id"]
                            ).execute()
                            st.session_state["password_changed"] = True
                            st.session_state.pop("skip_password_check", None)
                            st.toast("✅ Contraseña actualizada correctamente.")
                            st.balloons()
                            st.rerun()
                    except Exception as e:
                        logger.error(f"Error al actualizar contraseña: {e}")
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
                st.error("⚠️ Sin establecimiento asignado. Contactá al administrador.")
                st.markdown("---")
                if st.button("🚪 Cerrar sesión"):
                    logout()
                return

            opciones_estab = [mi_estab_nombre]
            st.session_state["estab_seleccionado"] = mi_estab_nombre
            st.session_state["estab_activo_id"] = mi_estab_id
            st.session_state["estab_activo_nombre"] = mi_estab_nombre
            st.markdown(f"""
            <div style="background:var(--gold-15);border-radius:10px;padding:0.5rem;text-align:center;margin-bottom:0.8rem;">
                <span style="color:var(--gold);">📍 {html.escape(mi_estab_nombre)}</span>
            </div>
            """, unsafe_allow_html=True)

        if rol == "admin":
            if "estab_seleccionado" not in st.session_state:
                st.session_state["estab_seleccionado"] = "🌐 Consolidado"

            estab_sel = st.selectbox(
                "Seleccionar",
                opciones_estab,
                index=opciones_estab.index(st.session_state["estab_seleccionado"])
                if st.session_state["estab_seleccionado"] in opciones_estab else 0,
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

        estab_activo = st.session_state.get(
            "estab_activo_nombre",
            "Consolidado" if rol == "admin" else st.session_state.get("establecimiento_nombre", "")
        )
        es_consolidado = (estab_activo == "Consolidado")

        st.markdown(f"""
        <div class="profile-card">
            <div class="profile-name">👤 {html.escape(perfil.get('nombre', 'Usuario'))}</div>
            <div class="profile-role"><span class="{badge_class}">{badge_text}</span></div>
            <div class="profile-location">📍 {'🌐 Todos los establecimientos' if es_consolidado else html.escape(estab_activo)}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📌 MENÚ")

        if rol != "admin":
            st.info("📎 **Importante:** Al registrar ingresos o egresos debés adjuntar el remito en PDF.")

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
            st.error("⚠️ Configuración incompleta. Contactá al administrador.")
            st.markdown("---")
            if st.button("🚪 Cerrar sesión"):
                logout()
            return

        pagina_actual = st.session_state.get("pagina", "Dashboard")
        nombres_menu = [n for _, n in paginas_menu]
        if pagina_actual not in nombres_menu:
            st.session_state["pagina"] = nombres_menu[0]

        for emoji, nombre in paginas_menu:
            es_activo = (nombre == pagina_actual)
            if es_activo:
                st.markdown(f"""<style>
                [data-testid="stSidebar"] div[data-testid="stButton"]:has(button[key="nav_{nombre}"]) button {{
                    background: linear-gradient(90deg,rgba(212,160,23,0.38) 0%,rgba(212,160,23,0.10) 100%) !important;
                    border-left: 3px solid var(--gold) !important;
                    border-color: var(--gold-75) !important;
                    color: #f5e6b0 !important;
                    font-weight: 700 !important;
                }}</style>""", unsafe_allow_html=True)
            if st.button(f"{emoji}  {nombre}", key=f"nav_{nombre}"):
                st.session_state["pagina"] = nombre
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Cerrar sesión"):
            logout()


# ══════════════════════════════════════════════════════════════
# HELPERS DE DATOS — con caché
# ══════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def get_establecimientos():
    try:
        res = supabase.table("establecimientos").select("*").execute()
        return res.data
    except Exception as e:
        logger.error(f"get_establecimientos error: {e}")
        return []


@st.cache_data(ttl=300)
def get_categorias():
    try:
        res = supabase.table("categorias").select("*").execute()
        return res.data
    except Exception as e:
        logger.error(f"get_categorias error: {e}")
        return []


@st.cache_data(ttl=300)
def get_productos(categoria_id=None, subcategoria=None):
    try:
        q = supabase.table("productos").select("*,categorias(nombre)").eq("activo", True)
        if categoria_id:
            q = q.eq("categoria_id", categoria_id)
        if subcategoria:
            q = q.eq("subcategoria", subcategoria)
        return q.execute().data
    except Exception as e:
        logger.error(f"get_productos error: {e}")
        return []


@st.cache_data(ttl=120)
def get_proveedores():
    try:
        res = supabase.table("proveedores").select("*").eq("activo", True).execute()
        return res.data
    except Exception as e:
        logger.error(f"get_proveedores error: {e}")
        return []


def get_movimientos(establecimiento_id=None, limit=5000):
    try:
        q = supabase.table("movimientos").select("*").order("fecha", desc=True).limit(limit)
        if establecimiento_id:
            q = q.eq("establecimiento_id", establecimiento_id)
        movimientos = q.execute().data

        if not movimientos:
            return []

        producto_ids = list(set(m.get("producto_id") for m in movimientos if m.get("producto_id")))
        establecimiento_ids = list(set(m.get("establecimiento_id") for m in movimientos if m.get("establecimiento_id")))

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
        logger.error(f"get_movimientos error: {e}")
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
    categoria_map = {
        p["id"]: p.get("categorias", {}).get("nombre", "Sin categoría") if p.get("categorias") else "Sin categoría"
        for p in productos
    }
    presentacion_map = {p["id"]: p.get("presentacion", "") for p in productos}
    unidad_map = {p["id"]: p.get("unidad_medida", "unidad") for p in productos}

    stock = {
        prod_id: ingresos.get(prod_id, 0) - egresos.get(prod_id, 0)
        for prod_id in set(ingresos.index) | set(egresos.index)
    }

    result = [
        {
            "producto_id": pid,
            "producto": nombre_map.get(pid, "Desconocido"),
            "categoria": categoria_map.get(pid, "Sin categoría"),
            "presentacion": presentacion_map.get(pid, ""),
            "unidad": unidad_map.get(pid, "unidad"),
            "stock": qty,
        }
        for pid, qty in stock.items() if qty != 0 and pid in nombre_map
    ]

    return pd.DataFrame(result).sort_values("stock", ascending=False)


def get_movimientos_con_filtros(establecimiento_id=None, fecha_desde=None, fecha_hasta=None, tipo=None, producto_id=None, categoria_id=None):
    movimientos = get_movimientos(establecimiento_id, limit=5000)
    if not movimientos:
        return []

    df = pd.DataFrame(movimientos)
    if "fecha" in df.columns:
        df["fecha"] = parse_fecha(df["fecha"])
        if fecha_desde:
            df = df[df["fecha"] >= pd.Timestamp(fecha_desde)]
        if fecha_hasta:
            df = df[df["fecha"] <= pd.Timestamp(fecha_hasta) + pd.Timedelta(days=1)]

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
        logger.error(f"get_stock_por_establecimiento error: {e}")
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

    ingresos = df[df["tipo"] == "ingreso"].groupby(
        ["producto_nombre", "producto_presentacion", "producto_unidad", "categoria_nombre", "establecimiento_nombre"]
    )["cantidad"].sum()
    egresos = df[df["tipo"] == "egreso"].groupby(
        ["producto_nombre", "producto_presentacion", "producto_unidad", "categoria_nombre", "establecimiento_nombre"]
    )["cantidad"].sum()

    stock_df = (ingresos - egresos.reindex(ingresos.index, fill_value=0)).reset_index()
    stock_df.columns = ["producto", "presentacion", "unidad", "categoria", "establecimiento", "stock"]
    return stock_df[stock_df["stock"] != 0].sort_values(["establecimiento", "producto"])


# ══════════════════════════════════════════════════════════════
# RENDER TABLA HTML (con escape XSS)
# ══════════════════════════════════════════════════════════════

def render_tabla_html(df, height=500):
    import streamlit.components.v1 as components
    cols = list(df.columns)
    filas_html = ""
    for _, row in df.iterrows():
        filas_html += '<tr onmouseover="this.style.backgroundColor=\'rgba(212,160,23,0.10)\'" onmouseout="this.style.backgroundColor=\'transparent\'">'
        for col in cols:
            val = row[col]
            style = "color:#f0f0f5;font-size:0.85rem;"
            display_val = ""
            if col in ("stock", "Stock", "cantidad", "Cantidad"):
                try:
                    v = float(val)
                    color = "#ef4444" if v < 50 else "#f59e0b" if v < 200 else "#22c55e"
                    style = f"color:{color};font-weight:700;font-size:0.88rem;text-align:right;"
                    display_val = f"{v:,.2f}"
                except Exception:
                    display_val = html.escape(str(val))
            elif str(val) in ("True", "False"):
                display_val = "✅" if val else "❌"
                style = "text-align:center;"
            else:
                display_val = html.escape(str(val)) if val not in (None, "nan", "None") else "—"
            filas_html += f'<td style="padding:8px 12px;border-bottom:1px solid rgba(212,160,23,0.12);{style}">{display_val}</td>'
        filas_html += "</tr>"

    headers = "".join([
        f'<th style="padding:10px 12px;color:#1a1a1f;font-weight:700;font-size:0.78rem;'
        f'text-transform:uppercase;letter-spacing:0.07em;white-space:nowrap;text-align:left;">'
        f'{html.escape(str(c))}</th>'
        for c in cols
    ])

    tabla_html = f"""<!DOCTYPE html><html><head><style>
    body{{margin:0;padding:0;background:transparent;font-family:'DM Sans',sans-serif;}}
    .wrap{{overflow-x:auto;border-radius:14px;border:1px solid rgba(212,160,23,0.35);box-shadow:0 6px 24px rgba(0,0,0,0.4);}}
    table{{width:100%;border-collapse:collapse;background:rgba(22,22,28,0.97);}}
    thead tr{{background:linear-gradient(135deg,#d4a017 0%,#b87a0c 100%);}}
    tbody tr{{transition:background 0.15s;}}
    </style></head><body>
    <div class="wrap"><table>
    <thead><tr>{headers}</tr></thead>
    <tbody>{filas_html}</tbody>
    </table></div></body></html>"""
    altura = min(height, 80 + len(df) * 38)
    components.html(tabla_html, height=altura, scrolling=True)


# ══════════════════════════════════════════════════════════════
# AUDITORÍA
# ══════════════════════════════════════════════════════════════

def registrar_auditoria(accion: str, datos: dict = None):
    """Registra acciones de admin en la tabla audit_log (si existe)."""
    try:
        import json
        usuario_nombre = (
            st.session_state.get("perfil", {}).get("nombre", "")
            or st.session_state.get("user_email", "")
            or "Admin"
        )
        payload = {
            "usuario_id": st.session_state.get("user_id"),
            "usuario_nombre": usuario_nombre,
            "accion": accion,
            "datos": json.dumps(datos, ensure_ascii=False, default=str) if datos else None,
            "timestamp": now_arg().isoformat(),
        }
        try:
            supabase.table("audit_log").insert(payload).execute()
        except Exception:
            # Si falla (ej: columna usuario_nombre no existe aún), reintentar sin ella
            payload_mini = {k: v for k, v in payload.items() if k != "usuario_nombre"}
            supabase.table("audit_log").insert(payload_mini).execute()
    except Exception:
        pass  # La tabla puede no existir; no interrumpe el flujo


def es_super_admin() -> bool:
    """Retorna True si el usuario logueado es el superadmin de SECCO Agro."""
    try:
        session = st.session_state.get("session")
        if session and hasattr(session, "user") and session.user:
            return session.user.email.lower() == "admin@seccoagro.com.ar"
    except Exception:
        pass
    return False


# ══════════════════════════════════════════════════════════════
# DASHBOARD
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

    SUBCATS_AGRO = ["Herbicidas", "Insecticidas", "Fungicidas", "Coadyuvantes", "Fertilizantes foliares"]
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

    busqueda_rapida = st.text_input(
        "🔍 Búsqueda rápida de producto",
        placeholder="Escribí el nombre del producto...",
        key="dash_busqueda"
    )

    df_filtrado = stock_productos.copy()
    if cat_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["categoria"] == cat_sel]
    if es_agro_dash and subcat_sel != "Todos":
        prods_subcat = get_productos(subcategoria=subcat_sel)
        nombres_subcat = [p["nombre"] for p in prods_subcat]
        df_filtrado = df_filtrado[df_filtrado["producto"].isin(nombres_subcat)]
    if prod_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["producto"] == prod_sel]
    if busqueda_rapida:
        df_filtrado = df_filtrado[df_filtrado["producto"].str.contains(busqueda_rapida, case=False, na=False)]

    total_stock = df_filtrado["stock"].sum()
    total_productos = len(df_filtrado)
    stock_bajo = len(df_filtrado[df_filtrado["stock"] < cfg.STOCK_CRITICO_DEFAULT])

    # KPI extra: productos con movimiento este mes
    movs_mes = get_movimientos(estab_filter(), limit=1000)
    movs_este_mes = 0
    if movs_mes:
        df_m = pd.DataFrame(movs_mes)
        df_m["fecha"] = parse_fecha(df_m["fecha"])
        hoy = datetime.now()
        movs_este_mes = len(df_m[
            (df_m["fecha"].dt.month == hoy.month) & (df_m["fecha"].dt.year == hoy.year)
        ])

    st.markdown(f"""
    <div style="display:flex;gap:1.2rem;margin:1.2rem 0 1.8rem 0;flex-wrap:wrap;">
        <div style="flex:1;min-width:180px;background:linear-gradient(135deg,rgba(212,160,23,0.25),rgba(212,160,23,0.12));
                    border:1px solid rgba(212,160,23,0.6);border-radius:20px;padding:1.4rem 1.6rem;
                    box-shadow:0 6px 24px rgba(0,0,0,0.35);text-align:center;backdrop-filter:blur(8px);">
            <div style="font-size:2rem;margin-bottom:4px;">📦</div>
            <div style="font-size:2.4rem;font-weight:800;color:#d4a017;font-family:'Playfair Display',serif;
                        text-shadow:0 2px 8px rgba(0,0,0,0.4);line-height:1.1;">{total_stock:,.0f}</div>
            <div style="font-size:0.8rem;color:#fff;font-weight:600;text-transform:uppercase;
                        letter-spacing:0.1em;margin-top:6px;opacity:0.85;">Stock Total (unidades)</div>
        </div>
        <div style="flex:1;min-width:180px;background:linear-gradient(135deg,rgba(34,197,94,0.25),rgba(34,197,94,0.12));
                    border:1px solid rgba(34,197,94,0.6);border-radius:20px;padding:1.4rem 1.6rem;
                    box-shadow:0 6px 24px rgba(0,0,0,0.35);text-align:center;backdrop-filter:blur(8px);">
            <div style="font-size:2rem;margin-bottom:4px;">🏷️</div>
            <div style="font-size:2.4rem;font-weight:800;color:#22c55e;font-family:'Playfair Display',serif;
                        text-shadow:0 2px 8px rgba(0,0,0,0.4);line-height:1.1;">{total_productos}</div>
            <div style="font-size:0.8rem;color:#fff;font-weight:600;text-transform:uppercase;
                        letter-spacing:0.1em;margin-top:6px;opacity:0.85;">Productos en Stock</div>
        </div>
        <div style="flex:1;min-width:180px;background:linear-gradient(135deg,rgba(239,68,68,0.25),rgba(239,68,68,0.12));
                    border:1px solid rgba(239,68,68,0.6);border-radius:20px;padding:1.4rem 1.6rem;
                    box-shadow:0 6px 24px rgba(0,0,0,0.35);text-align:center;backdrop-filter:blur(8px);">
            <div style="font-size:2rem;margin-bottom:4px;">⚠️</div>
            <div style="font-size:2.4rem;font-weight:800;color:#ef4444;font-family:'Playfair Display',serif;
                        text-shadow:0 2px 8px rgba(0,0,0,0.4);line-height:1.1;">{stock_bajo}</div>
            <div style="font-size:0.8rem;color:#fff;font-weight:600;text-transform:uppercase;
                        letter-spacing:0.1em;margin-top:6px;opacity:0.85;">Stock Crítico (&lt;{cfg.STOCK_CRITICO_DEFAULT})</div>
        </div>
        <div style="flex:1;min-width:180px;background:linear-gradient(135deg,rgba(59,130,246,0.25),rgba(59,130,246,0.12));
                    border:1px solid rgba(59,130,246,0.6);border-radius:20px;padding:1.4rem 1.6rem;
                    box-shadow:0 6px 24px rgba(0,0,0,0.35);text-align:center;backdrop-filter:blur(8px);">
            <div style="font-size:2rem;margin-bottom:4px;">📅</div>
            <div style="font-size:2.4rem;font-weight:800;color:#3b82f6;font-family:'Playfair Display',serif;
                        text-shadow:0 2px 8px rgba(0,0,0,0.4);line-height:1.1;">{movs_este_mes}</div>
            <div style="font-size:0.8rem;color:#fff;font-weight:600;text-transform:uppercase;
                        letter-spacing:0.1em;margin-top:6px;opacity:0.85;">Movimientos este mes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── RESUMEN DEL DÍA ─────────────────────────────────────────
    hoy_str = now_arg().date()
    movs_hoy_ing = 0
    movs_hoy_eg = 0
    cant_hoy_ing = 0.0
    cant_hoy_eg = 0.0
    if movs_mes:
        df_hoy = pd.DataFrame(movs_mes)
        df_hoy["fecha"] = parse_fecha(df_hoy["fecha"])
        df_hoy_filt = df_hoy[df_hoy["fecha"].dt.date == hoy_str]
        movs_hoy_ing = len(df_hoy_filt[df_hoy_filt["tipo"] == "ingreso"])
        movs_hoy_eg = len(df_hoy_filt[df_hoy_filt["tipo"] == "egreso"])
        cant_hoy_ing = float(df_hoy_filt[df_hoy_filt["tipo"] == "ingreso"]["cantidad"].sum()) if movs_hoy_ing > 0 else 0.0
        cant_hoy_eg = float(df_hoy_filt[df_hoy_filt["tipo"] == "egreso"]["cantidad"].sum()) if movs_hoy_eg > 0 else 0.0

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(212,160,23,0.08),rgba(40,40,50,0.6));
                border:1px solid rgba(212,160,23,0.25);border-radius:16px;padding:0.9rem 1.4rem;
                margin:0 0 1.4rem 0;display:flex;align-items:center;gap:2rem;flex-wrap:wrap;">
        <div style="font-size:0.78rem;font-weight:700;color:#d4a017;text-transform:uppercase;letter-spacing:0.1em;min-width:80px;">
            📅 Hoy
        </div>
        <div style="display:flex;gap:1.8rem;flex-wrap:wrap;">
            <span style="font-size:0.88rem;color:#22c55e;font-weight:600;">
                ▲ {movs_hoy_ing} ingresos
                <span style="color:#a0a0b0;font-weight:400;font-size:0.8rem;"> ({cant_hoy_ing:,.1f} un.)</span>
            </span>
            <span style="font-size:0.88rem;color:#ef4444;font-weight:600;">
                ▼ {movs_hoy_eg} egresos
                <span style="color:#a0a0b0;font-weight:400;font-size:0.8rem;"> ({cant_hoy_eg:,.1f} un.)</span>
            </span>
            <span style="font-size:0.82rem;color:#a0a0b0;">
                Total movimientos hoy: <strong style="color:#f0f0f5;">{movs_hoy_ing + movs_hoy_eg}</strong>
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── GRÁFICO DE BARRAS ────────────────────────────────────────
    if len(df_filtrado) > 0:
        df_chart = df_filtrado.sort_values("stock", ascending=True).tail(20).copy()
        df_chart["color_stock"] = df_chart["stock"].apply(
            lambda s: "#ef4444" if s < cfg.STOCK_CRITICO_DEFAULT else ("#f59e0b" if s < 200 else "#22c55e")
        )
        fig = go.Figure(go.Bar(
            x=df_chart["stock"],
            y=df_chart["producto"],
            orientation="h",
            marker=dict(
                color=df_chart["color_stock"],
                line=dict(color="rgba(212,160,23,0.3)", width=0.5)
            ),
            text=df_chart["stock"].apply(lambda v: f"{v:,.1f}"),
            textposition="outside",
            textfont=dict(color="#d4c8a8", size=11),
            hovertemplate="<b>%{y}</b><br>Stock: %{x:,.2f}<extra></extra>"
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(22,22,28,0.6)",
            font=dict(family="DM Sans", color="#c8c8d4", size=12),
            margin=dict(l=10, r=60, t=30, b=10),
            height=max(220, len(df_chart) * 32 + 50),
            xaxis=dict(
                gridcolor="rgba(212,160,23,0.15)",
                zerolinecolor="rgba(212,160,23,0.3)",
                tickfont=dict(color="#a0a0b0", size=10),
                title=dict(text="Stock", font=dict(color="#d4a017", size=11))
            ),
            yaxis=dict(
                gridcolor="rgba(0,0,0,0)",
                tickfont=dict(color="#f0f0f5", size=11),
                title=None
            ),
            hoverlabel=dict(bgcolor="rgba(22,22,28,0.95)", font_color="#f0f0f5"),
            bargap=0.25,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("""
    <div style="font-size:1.3rem;font-weight:700;color:#fff;margin:0.5rem 0 0.8rem 0;
                text-shadow:0 1px 4px rgba(0,0,0,0.5);">📋 Stock Actual por Producto</div>
    """, unsafe_allow_html=True)

    df_tabla = df_filtrado[["producto", "categoria", "presentacion", "stock", "unidad"]].copy()
    df_tabla = df_tabla.sort_values("stock", ascending=False)

    filas_html = ""
    for _, row in df_tabla.iterrows():
        stock_val = float(row["stock"])
        if stock_val < cfg.STOCK_CRITICO_DEFAULT:
            stock_color = "#ef4444"
        elif stock_val < 200:
            stock_color = "#f59e0b"
        else:
            stock_color = "#22c55e"

        filas_html += f"""
        <tr onmouseover="this.style.backgroundColor='rgba(212,160,23,0.12)'"
            onmouseout="this.style.backgroundColor='transparent'">
            <td style="padding:9px 13px;color:#f0f0f5;font-size:0.88rem;font-weight:600;">{html.escape(str(row['producto']))}</td>
            <td style="padding:9px 13px;color:#d4c8a8;font-size:0.84rem;">{html.escape(str(row['categoria']))}</td>
            <td style="padding:9px 13px;color:#b0b0c0;font-size:0.84rem;">{html.escape(str(row['presentacion']))}</td>
            <td style="padding:9px 13px;color:{stock_color};font-size:0.95rem;font-weight:800;text-align:right;">{stock_val:,.2f}</td>
            <td style="padding:9px 13px;color:#a0a0b0;font-size:0.82rem;">{html.escape(str(row['unidad']))}</td>
        </tr>"""

    estab_label = st.session_state.get("estab_activo_nombre", "Todos los establecimientos")
    filtros_label = f"Categoría: {cat_sel}"
    if es_agro_dash and subcat_sel != "Todos":
        filtros_label += f" | Tipo: {subcat_sel}"
    if prod_sel != "Todos":
        filtros_label += f" | Producto: {prod_sel}"
    fecha_impresion = now_arg().strftime("%d/%m/%Y %H:%M")

    tabla_html = f"""<!DOCTYPE html>
<html><head><style>
  body {{ margin:0; padding:0; background:transparent; font-family:'DM Sans',sans-serif; }}
  .wrap {{ overflow-x:auto; border-radius:14px; border:1px solid rgba(212,160,23,0.35); box-shadow:0 6px 24px rgba(0,0,0,0.4); }}
  table {{ width:100%; border-collapse:collapse; background:rgba(22,22,28,0.97); }}
  thead tr {{ background:linear-gradient(135deg,#d4a017 0%,#b87a0c 100%); }}
  th {{ padding:11px 13px; color:#1a1a1f; font-weight:700; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.07em; white-space:nowrap; }}
  tbody tr {{ border-bottom:1px solid rgba(212,160,23,0.15); transition:background 0.2s; }}
  .print-btn {{
    display:inline-flex; align-items:center; gap:6px;
    margin-bottom:10px; padding:7px 18px;
    background:linear-gradient(135deg,#d4a017,#b87a0c);
    color:#1a1a1f; font-weight:700; font-size:0.85rem;
    border:none; border-radius:8px; cursor:pointer;
    box-shadow:0 3px 10px rgba(0,0,0,0.3);
    font-family:'DM Sans',sans-serif;
  }}
  .print-btn:hover {{ background:linear-gradient(135deg,#e6b520,#c98a10); }}
  @media print {{
    .print-btn {{ display:none !important; }}
    body {{ background:#fff !important; }}
    .wrap {{ border:1px solid #ccc !important; box-shadow:none !important; border-radius:4px !important; }}
    table {{ background:#fff !important; }}
    thead tr {{ background:#d4a017 !important; -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
    th {{ color:#1a1a1f !important; }}
    tbody tr {{ border-bottom:1px solid #ddd !important; }}
    td {{ color:#111 !important; font-size:0.82rem !important; }}
    .print-header {{ display:block !important; }}
  }}
  .print-header {{
    display:none;
    margin-bottom:12px;
    font-family:'DM Sans',sans-serif;
  }}
  .print-header h2 {{ margin:0 0 4px 0; font-size:1.1rem; color:#333; }}
  .print-header p {{ margin:2px 0; font-size:0.8rem; color:#555; }}
</style></head>
<body>
  <div class="print-header">
    <h2>📊 Stock Actual — SECCO Agro</h2>
    <p><strong>Establecimiento:</strong> {html.escape(str(estab_label))}</p>
    <p><strong>Filtros:</strong> {html.escape(str(filtros_label))}</p>
    <p><strong>Generado:</strong> {fecha_impresion}</p>
  </div>
  <button class="print-btn" onclick="window.print()">🖨️ Imprimir / Exportar PDF</button>
  <div class="wrap"><table>
    <thead><tr>
      <th style="text-align:left;">📦 Producto</th>
      <th style="text-align:left;">📁 Categoría</th>
      <th style="text-align:left;">Presentación</th>
      <th style="text-align:right;">Stock</th>
      <th style="text-align:left;">Unidad</th>
    </tr></thead>
    <tbody>{filas_html}</tbody>
  </table></div>
</body></html>"""

    import streamlit.components.v1 as components
    altura = min(750, 160 + len(df_tabla) * 42)
    components.html(tabla_html, height=altura, scrolling=True)


# ══════════════════════════════════════════════════════════════
# NUEVO INGRESO
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

    # Banner de éxito
    if st.session_state.pop("ingreso_ok", None):
        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(34,197,94,0.25),rgba(34,197,94,0.10));
                    border:1px solid rgba(34,197,94,0.6);border-radius:14px;padding:1rem 1.5rem;
                    margin-bottom:1rem;display:flex;align-items:center;gap:12px;">
            <span style="font-size:1.8rem;">✅</span>
            <div>
                <div style="color:#22c55e;font-weight:700;font-size:1rem;">¡Ingreso registrado exitosamente!</div>
                <div style="color:#a0a0b0;font-size:0.82rem;">El movimiento quedó guardado en el historial.</div>
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
        estab_activo_id = st.session_state.get("estab_activo_id")
        estab_activo_nombre = st.session_state.get("estab_activo_nombre", "Consolidado")
        if estab_activo_id:
            establecimiento_id = estab_activo_id
            establecimiento_nombre = estab_activo_nombre
            st.info(f"📍 Establecimiento: **{establecimiento_nombre}**")
        else:
            estab_options = {e["nombre"]: e["id"] for e in establecimientos}
            estab_sel = st.selectbox("🏢 Establecimiento *", list(estab_options.keys()), key="ing_estab")
            establecimiento_id = estab_options[estab_sel]
            establecimiento_nombre = estab_sel
    else:
        establecimiento_id = st.session_state.get("establecimiento_id")
        establecimiento_nombre = st.session_state.get("establecimiento_nombre", "")
        st.info(f"📍 Establecimiento: {establecimiento_nombre}")

    # ── Inicializar lista de líneas de ingreso ──────────────────
    MAX_LINEAS = 5
    if "ing_lineas" not in st.session_state or st.session_state.get("ing_reset"):
        st.session_state["ing_lineas"] = 1
        st.session_state.pop("ing_reset", None)

    num_lineas = st.session_state["ing_lineas"]

    # ── Campos globales (proveedor, tipo, observaciones, remito) ─
    _now_arg = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).replace(tzinfo=None)
    st.caption(f"🕐 Fecha y hora del registro: **{_now_arg.strftime('%d/%m/%Y %H:%M')}**")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        prov_options = {p["nombre"]: p["id"] for p in proveedores}
        if prov_options:
            prov_sel = st.selectbox("🏭 Proveedor", ["Sin proveedor"] + list(prov_options.keys()), key="ing_proveedor")
            proveedor_id = prov_options[prov_sel] if prov_sel != "Sin proveedor" else None
        else:
            proveedor_id = None
    with col_g2:
        tipo_ingreso = st.selectbox("📌 Tipo de Ingreso", ["Compra", "Devolución", "Traslado", "Otro"], key="ing_tipo")

    observaciones = st.text_area("📝 Observaciones", placeholder="N° factura, lote, detalles adicionales...", key="ing_obs")

    # ── Líneas de productos ─────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📦 Productos a ingresar")

    cat_options = {c["nombre"]: c["id"] for c in categorias}
    todos_los_productos = get_productos()
    prod_nombre_a_obj = {p["nombre"]: p for p in todos_los_productos}

    lineas_validas = []
    for i in range(num_lineas):
        with st.container():
            st.markdown(f"**Producto {i+1}**")
            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                cat_sel_i = st.selectbox(
                    f"Categoría", list(cat_options.keys()),
                    key=f"ing_cat_{i}"
                )
                cat_id_i = cat_options[cat_sel_i]
                es_agro_i = "agroquimico" in cat_sel_i.lower() or "agroquímico" in cat_sel_i.lower()
                subcat_i = None
                if es_agro_i:
                    subcat_i = st.selectbox(
                        "Tipo Agroquímico",
                        ["Herbicidas", "Insecticidas", "Fungicidas", "Coadyuvantes", "Fertilizantes foliares"],
                        key=f"ing_subcat_{i}"
                    )
                productos_i = get_productos(cat_id_i, subcat_i if es_agro_i else None)
                prod_options_i = {p["nombre"]: p["id"] for p in productos_i} if productos_i else {}
                if not prod_options_i:
                    st.warning("Sin productos en esta categoría.")
                    continue
                prod_sel_i = st.selectbox("Producto", list(prod_options_i.keys()), key=f"ing_prod_{i}")
                producto_id_i = prod_options_i[prod_sel_i]
                prod_obj_i = next((p for p in productos_i if p["id"] == producto_id_i), {})

            with col_b:
                cantidad_i = st.number_input(
                    "Cantidad *", min_value=0.001, step=0.5, format="%.3f",
                    key=f"ing_cant_{i}"
                )
                fecha_venc_i = st.date_input(
                    "Vencimiento", value=None, format="DD/MM/YYYY",
                    key=f"ing_fvenc_{i}", help="Opcional"
                )

            with col_c:
                marca_i = st.text_input(
                    "Marca", value=prod_obj_i.get("marca", "") or "",
                    placeholder="Ej: Bayer...", key=f"ing_marca_{i}"
                )
                concentracion_i = st.text_input(
                    "Concentración", value=prod_obj_i.get("concentracion", "") or "",
                    placeholder="Ej: 48%", key=f"ing_conc_{i}"
                )

            lineas_validas.append({
                "producto_id": producto_id_i,
                "prod_sel": prod_sel_i,
                "prod_obj": prod_obj_i,
                "cantidad": cantidad_i,
                "fecha_vencimiento": fecha_venc_i,
                "marca": marca_i,
                "concentracion": concentracion_i,
            })

        if i < num_lineas - 1:
            st.markdown("<hr style='border-color:rgba(212,160,23,0.2);margin:0.5rem 0'>", unsafe_allow_html=True)

    # ── Botones agregar / quitar línea ──────────────────────────
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if num_lineas < MAX_LINEAS:
            if st.button(f"➕ Agregar producto ({num_lineas}/{MAX_LINEAS})", key="ing_add"):
                st.session_state["ing_lineas"] += 1
                st.rerun()
    with col_btn2:
        if num_lineas > 1:
            if st.button("➖ Quitar último producto", key="ing_rm"):
                st.session_state["ing_lineas"] -= 1
                st.rerun()

    st.markdown("---")

    # ── Remito ──────────────────────────────────────────────────
    archivo_remito = None
    if not es_admin:
        st.markdown("### 📎 Remito obligatorio")
        st.info(f"Debés adjuntar el remito en PDF (máx. {cfg.MAX_PDF_SIZE_MB}MB).")
        archivo_remito = st.file_uploader(
            "Seleccionar archivo PDF del remito *",
            type=["pdf"],
            key="remito_ingreso"
        )
        if archivo_remito is not None:
            ok, msg = _validar_pdf(archivo_remito)
            if ok:
                st.success(f"✅ Archivo válido: {archivo_remito.name} ({len(archivo_remito.getvalue()) // 1024} KB)")
            else:
                st.error(f"❌ {msg}")
                archivo_remito = None
    else:
        st.caption("ℹ️ Como administrador, no es obligatorio adjuntar remito.")

    # ── Botón registrar ─────────────────────────────────────────
    if st.button("✅ Registrar Ingreso", use_container_width=True, key="ing_submit"):
        if not lineas_validas:
            st.error("❌ Agregá al menos un producto.")
            return
        if not es_admin and archivo_remito is None:
            st.error("❌ Es obligatorio adjuntar el remito en PDF.")
            return
        errores = [f"Producto {i+1}: la cantidad debe ser mayor a 0." for i, l in enumerate(lineas_validas) if l["cantidad"] <= 0]
        if errores:
            for e in errores:
                st.error(f"❌ {e}")
            return

        try:
            with st.spinner(f"Registrando {len(lineas_validas)} producto(s)..."):
                now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).replace(tzinfo=None)
                observaciones_full = f"[{tipo_ingreso}] {observaciones}" if observaciones else f"[{tipo_ingreso}]"
                usuario_id = st.session_state.get("user_id")
                usuario_nombre = st.session_state.get("perfil", {}).get("nombre", "")

                ids_movimientos = []
                for linea in lineas_validas:
                    payload = {
                        "tipo": "ingreso",
                        "producto_id": linea["producto_id"],
                        "establecimiento_id": establecimiento_id,
                        "cantidad": float(linea["cantidad"]),
                        "fecha": now.isoformat(),
                        "proveedor_id": proveedor_id,
                        "observaciones": observaciones_full,
                        "usuario_id": usuario_id,
                        "usuario_nombre": usuario_nombre,
                        "fecha_vencimiento": linea["fecha_vencimiento"].isoformat() if linea["fecha_vencimiento"] else None,
                    }
                    prod_obj = linea["prod_obj"]
                    if linea["marca"].strip() != (prod_obj.get("marca") or "") or \
                       linea["concentracion"].strip() != (prod_obj.get("concentracion") or ""):
                        supabase.table("productos").update({
                            "marca": linea["marca"].strip() or None,
                            "concentracion": linea["concentracion"].strip() or None
                        }).eq("id", linea["producto_id"]).execute()
                        get_productos.clear()

                    resultado = supabase.table("movimientos").insert(payload).execute()
                    mov_id = resultado.data[0]["id"] if resultado.data else None
                    if mov_id:
                        ids_movimientos.append(mov_id)
                    registrar_auditoria("ingreso_registrado", {"movimiento_id": mov_id, "producto": linea["prod_sel"]})

                # Subir el PDF una sola vez y asociarlo a TODOS los movimientos del lote
                if ids_movimientos and archivo_remito is not None:
                    subir_remito_pdf(archivo_remito, ids_movimientos, usuario_id, establecimiento_id)

                get_movimientos.clear() if hasattr(get_movimientos, "clear") else None
                st.session_state["ing_reset"] = True
                st.session_state["ingreso_ok"] = True
                st.rerun()
        except Exception as e:
            logger.error(f"Error al registrar ingreso: {e}")
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

    # Banner de éxito
    if st.session_state.pop("egreso_ok", None):
        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(239,68,68,0.25),rgba(239,68,68,0.10));
                    border:1px solid rgba(239,68,68,0.6);border-radius:14px;padding:1rem 1.5rem;
                    margin-bottom:1rem;display:flex;align-items:center;gap:12px;">
            <span style="font-size:1.8rem;">✅</span>
            <div>
                <div style="color:#ef4444;font-weight:700;font-size:1rem;">¡Egreso registrado exitosamente!</div>
                <div style="color:#a0a0b0;font-size:0.82rem;">El movimiento quedó guardado en el historial.</div>
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
        estab_activo_id = st.session_state.get("estab_activo_id")
        estab_activo_nombre = st.session_state.get("estab_activo_nombre", "Consolidado")
        if estab_activo_id:
            establecimiento_id = estab_activo_id
            establecimiento_nombre = estab_activo_nombre
            st.info(f"📍 Establecimiento: **{establecimiento_nombre}**")
        else:
            estab_options = {e["nombre"]: e["id"] for e in establecimientos}
            estab_sel = st.selectbox("🏢 Establecimiento *", list(estab_options.keys()), key="eg_estab")
            establecimiento_id = estab_options[estab_sel]
            establecimiento_nombre = estab_sel
    else:
        establecimiento_id = st.session_state.get("establecimiento_id")
        establecimiento_nombre = st.session_state.get("establecimiento_nombre", "")
        st.info(f"📍 Establecimiento: {establecimiento_nombre}")

    # ── Inicializar lista de líneas de egreso ───────────────────
    MAX_LINEAS = 5
    if "eg_lineas" not in st.session_state or st.session_state.get("eg_reset"):
        st.session_state["eg_lineas"] = 1
        st.session_state.pop("eg_reset", None)

    num_lineas = st.session_state["eg_lineas"]

    # ── Campos globales ─────────────────────────────────────────
    _now_arg = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).replace(tzinfo=None)
    st.caption(f"🕐 Fecha y hora del registro: **{_now_arg.strftime('%d/%m/%Y %H:%M')}**")

    tipo_egreso = st.selectbox("📌 Tipo de Egreso", ["Uso", "Venta", "Traslado", "Merma", "Otro"], key="eg_tipo")
    observaciones = st.text_area("📝 Observaciones", placeholder="Motivo del egreso, destino, responsable, etc.", key="eg_obs")

    # ── Líneas de productos ─────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📦 Productos a egresar")

    if not categorias:
        st.warning("⚠️ No hay categorías cargadas.")
        return

    cat_options = {c["nombre"]: c["id"] for c in categorias}
    stock_actual_df = get_stock_por_producto(establecimiento_id)

    lineas_validas = []
    for i in range(num_lineas):
        with st.container():
            st.markdown(f"**Producto {i+1}**")
            col_a, col_b = st.columns([3, 1])
            with col_a:
                cat_sel_i = st.selectbox(
                    "Categoría", list(cat_options.keys()),
                    key=f"eg_cat_{i}"
                )
                cat_id_i = cat_options[cat_sel_i]
                es_agro_i = "agroquimico" in cat_sel_i.lower() or "agroquímico" in cat_sel_i.lower()
                subcat_i = None
                if es_agro_i:
                    subcat_i = st.selectbox(
                        "Tipo Agroquímico",
                        ["Herbicidas", "Insecticidas", "Fungicidas", "Coadyuvantes", "Fertilizantes foliares"],
                        key=f"eg_subcat_{i}"
                    )
                productos_i = get_productos(cat_id_i, subcat_i if es_agro_i else None)
                prod_options_i = {p["nombre"]: p["id"] for p in productos_i} if productos_i else {}
                if not prod_options_i:
                    st.warning("Sin productos en esta categoría.")
                    continue
                prod_sel_i = st.selectbox("Producto", list(prod_options_i.keys()), key=f"eg_prod_{i}")
                producto_id_i = prod_options_i[prod_sel_i]

                # Mostrar stock disponible
                if not stock_actual_df.empty:
                    fila_stock = stock_actual_df[stock_actual_df["producto_id"] == producto_id_i]
                    stock_disp = fila_stock.iloc[0]["stock"] if not fila_stock.empty else 0
                    color_stock = "#22c55e" if stock_disp >= 50 else ("#f59e0b" if stock_disp > 0 else "#ef4444")
                    st.markdown(
                        f"<small style='color:{color_stock}'>Stock disponible: <b>{stock_disp:.2f}</b></small>",
                        unsafe_allow_html=True
                    )
                else:
                    stock_disp = 0

            with col_b:
                cantidad_i = st.number_input(
                    "Cantidad *", min_value=0.001, step=0.5, format="%.3f",
                    key=f"eg_cant_{i}"
                )

            lineas_validas.append({
                "producto_id": producto_id_i,
                "prod_sel": prod_sel_i,
                "cantidad": cantidad_i,
                "stock_disp": stock_disp,
            })

        if i < num_lineas - 1:
            st.markdown("<hr style='border-color:rgba(212,160,23,0.2);margin:0.5rem 0'>", unsafe_allow_html=True)

    # ── Botones agregar / quitar línea ──────────────────────────
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if num_lineas < MAX_LINEAS:
            if st.button(f"➕ Agregar producto ({num_lineas}/{MAX_LINEAS})", key="eg_add"):
                st.session_state["eg_lineas"] += 1
                st.rerun()
    with col_btn2:
        if num_lineas > 1:
            if st.button("➖ Quitar último producto", key="eg_rm"):
                st.session_state["eg_lineas"] -= 1
                st.rerun()

    st.markdown("---")

    # ── Remito ──────────────────────────────────────────────────
    archivo_remito = None
    if not es_admin:
        st.markdown("### 📎 Remito obligatorio")
        st.info(f"Debés adjuntar el remito en PDF (máx. {cfg.MAX_PDF_SIZE_MB}MB).")
        archivo_remito = st.file_uploader(
            "Seleccionar archivo PDF del remito *",
            type=["pdf"],
            key="remito_egreso"
        )
        if archivo_remito is not None:
            ok, msg = _validar_pdf(archivo_remito)
            if ok:
                st.success(f"✅ Archivo válido: {archivo_remito.name} ({len(archivo_remito.getvalue()) // 1024} KB)")
            else:
                st.error(f"❌ {msg}")
                archivo_remito = None

    # ── Botón registrar ─────────────────────────────────────────
    if st.button("✅ Registrar Egreso", use_container_width=True, key="eg_submit"):
        if not lineas_validas:
            st.error("❌ Agregá al menos un producto.")
            return
        if not es_admin and archivo_remito is None:
            st.error("❌ Es obligatorio adjuntar el remito en PDF.")
            return

        errores = []
        for i, l in enumerate(lineas_validas):
            if l["cantidad"] <= 0:
                errores.append(f"Producto {i+1}: la cantidad debe ser mayor a 0.")
            elif l["stock_disp"] < l["cantidad"]:
                errores.append(f"Producto {i+1} ({l['prod_sel']}): stock insuficiente. Disponible: {l['stock_disp']:.2f}")
        if errores:
            for e in errores:
                st.error(f"❌ {e}")
            return

        try:
            with st.spinner(f"Registrando {len(lineas_validas)} producto(s)..."):
                now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).replace(tzinfo=None)
                observaciones_full = f"[{tipo_egreso}] {observaciones}" if observaciones else f"[{tipo_egreso}]"
                usuario_id = st.session_state.get("user_id")
                usuario_nombre = st.session_state.get("perfil", {}).get("nombre", "")

                ids_movimientos = []
                for linea in lineas_validas:
                    payload = {
                        "tipo": "egreso",
                        "producto_id": linea["producto_id"],
                        "establecimiento_id": establecimiento_id,
                        "cantidad": float(linea["cantidad"]),
                        "fecha": now.isoformat(),
                        "observaciones": observaciones_full,
                        "usuario_id": usuario_id,
                        "usuario_nombre": usuario_nombre,
                    }
                    resultado = supabase.table("movimientos").insert(payload).execute()
                    mov_id = resultado.data[0]["id"] if resultado.data else None
                    if mov_id:
                        ids_movimientos.append(mov_id)
                    registrar_auditoria("egreso_registrado", {"movimiento_id": mov_id, "producto": linea["prod_sel"]})

                # Subir el PDF una sola vez y asociarlo a TODOS los movimientos del lote
                if ids_movimientos and archivo_remito is not None:
                    subir_remito_pdf(archivo_remito, ids_movimientos, usuario_id, establecimiento_id)

                get_movimientos.clear() if hasattr(get_movimientos, "clear") else None
                st.session_state["eg_reset"] = True
                st.session_state["egreso_ok"] = True
                st.rerun()
        except Exception as e:
            logger.error(f"Error al registrar egreso: {e}")
            st.error(f"❌ Error al guardar: {e}")


# ══════════════════════════════════════════════════════════════
# HISTORIAL
# ══════════════════════════════════════════════════════════════

def pagina_historial():
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>📋 Historial de Movimientos</h1>
            <p>📋 Consultá y filtrá todos los movimientos de stock</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        tipo_filtro = st.selectbox("🔄 Tipo", ["Todos", "ingreso", "egreso"], key="hist_tipo")
    with col_f2:
        fecha_desde = st.date_input("📅 Desde", value=date.today() - timedelta(days=30), key="hist_desde")
    with col_f3:
        fecha_hasta = st.date_input("📅 Hasta", value=date.today(), key="hist_hasta")

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
        df["fecha"] = parse_fecha(df["fecha"])
        df = df.sort_values("fecha", ascending=False)

    df["producto_nombre"] = df["productos"].apply(lambda x: x.get("nombre", "") if isinstance(x, dict) else "")
    df["categoria_nombre"] = df["productos"].apply(
        lambda x: x.get("categorias", {}).get("nombre", "") if isinstance(x, dict) and x.get("categorias") else ""
    )
    df["establecimiento_nombre"] = df["establecimientos"].apply(lambda x: x.get("nombre", "") if isinstance(x, dict) else "")
    df["fecha_str"] = df["fecha"].dt.strftime("%d/%m/%Y %H:%M")
    df["usuario_nombre"] = df.get("usuario_nombre", pd.Series([""] * len(df))).fillna("").astype(str)
    df["usuario_nombre"] = df["usuario_nombre"].replace("", "—")

    SUBCATS_AGRO = ["Herbicidas", "Insecticidas", "Fungicidas", "Coadyuvantes", "Fertilizantes foliares"]
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

    if cat_sel != "Todas":
        df = df[df["categoria_nombre"] == cat_sel]
    if es_agro_hist and subcat_sel != "Todos":
        prods_subcat = get_productos(subcategoria=subcat_sel)
        nombres_subcat = [p["nombre"] for p in prods_subcat]
        df = df[df["producto_nombre"].isin(nombres_subcat)]
    if prod_sel != "Todos":
        df = df[df["producto_nombre"] == prod_sel]

    # Generar links firmados para remitos
    df["remito_link"] = df.apply(
        lambda r: generar_link_pdf(r.get("remito_url")) if r.get("remito_url") else "—",
        axis=1
    )

    st.markdown(f"### 📊 Resultados: **{len(df)}** movimientos")

    # Botones de exportación
    export_df = df[["fecha_str", "tipo", "establecimiento_nombre", "producto_nombre", "cantidad", "observaciones"]].copy()
    export_df.columns = ["Fecha", "Tipo", "Establecimiento", "Producto", "Cantidad", "Observaciones"]

    col_exp1, col_exp2, col_exp3 = st.columns([3, 1, 1])
    with col_exp2:
        csv_data = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 CSV",
            data=csv_data,
            file_name=f"historial_{date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_exp3:
        buf_excel = BytesIO()
        with pd.ExcelWriter(buf_excel, engine="openpyxl") as writer:
            export_df.to_excel(writer, index=False, sheet_name="Historial")
        buf_excel.seek(0)
        st.download_button(
            "📊 Excel",
            data=buf_excel.getvalue(),
            file_name=f"historial_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # Agregar columnas de modificación si existen en el df
    for col_mod in ["modificado_por", "modificado_en", "motivo_modificacion"]:
        if col_mod not in df.columns:
            df[col_mod] = ""
        else:
            df[col_mod] = df[col_mod].fillna("").astype(str).replace("None", "").replace("nan", "")

    display_df = df[["fecha_str", "tipo", "establecimiento_nombre", "producto_nombre", "cantidad", "usuario_nombre", "remito_link", "observaciones", "modificado_por", "modificado_en", "motivo_modificacion"]].copy()
    display_df.columns = ["Fecha", "Tipo", "Establecimiento", "Producto", "Cantidad", "Usuario", "Remito", "Observaciones", "ModPor", "ModEn", "ModMotivo"]

    filas_html = ""
    for _, row in display_df.iterrows():
        if row["Tipo"] == "ingreso":
            row_bg = "rgba(34,197,94,0.10)"
            tipo_badge = '<span style="background:#22c55e;color:#000;padding:2px 10px;border-radius:20px;font-size:0.78rem;font-weight:700;">▲ ingreso</span>'
        else:
            row_bg = "rgba(239,68,68,0.10)"
            tipo_badge = '<span style="background:#ef4444;color:#fff;padding:2px 10px;border-radius:20px;font-size:0.78rem;font-weight:700;">▼ egreso</span>'

        obs_raw = row["Observaciones"]
        obs = html.escape(str(obs_raw)) if obs_raw and str(obs_raw) not in ["nan", "None", ""] else "—"
        usr_raw = row.get("Usuario", "—")
        usuario_cell = html.escape(str(usr_raw)) if usr_raw and str(usr_raw) not in ["nan", "None", ""] else "—"
        remito_val = row["Remito"]
        remito = str(remito_val) if remito_val and str(remito_val) not in ["nan", "None", "", "—"] else '<span style="color:#666;font-size:0.8rem;">—</span>'
        try:
            cantidad_fmt = f"{float(row['Cantidad']):,.2f}"
        except Exception:
            cantidad_fmt = html.escape(str(row["Cantidad"]))

        # Badge y detalle de modificación
        mod_por = str(row.get("ModPor", "") or "").strip()
        mod_en = str(row.get("ModEn", "") or "").strip()
        mod_motivo = str(row.get("ModMotivo", "") or "").strip()
        fue_modificado = bool(mod_por and mod_por not in ["nan", "None", ""])
        if fue_modificado:
            try:
                from datetime import datetime as _dt
                mod_en_fmt = _dt.fromisoformat(mod_en).strftime("%d/%m/%Y %H:%M") if mod_en else ""
            except Exception:
                mod_en_fmt = mod_en
            mod_badge = f'''<span style="background:#7c3aed;color:#fff;padding:2px 8px;border-radius:20px;font-size:0.72rem;font-weight:700;margin-left:6px;">✏️ Modificado</span>'''
            mod_tooltip = html.escape(f"Por: {mod_por} | {mod_en_fmt} | Motivo: {mod_motivo}")
            mod_info = f'''<div style="font-size:0.75rem;color:#c4b5fd;margin-top:3px;" title="{mod_tooltip}">✏️ {html.escape(mod_por)} · {mod_en_fmt}</div>'''
            if mod_motivo:
                mod_info += f'''<div style="font-size:0.72rem;color:#a78bfa;font-style:italic;">"{html.escape(mod_motivo)}"</div>'''
        else:
            mod_badge = ""
            mod_info = ""

        fecha_cell = html.escape(str(row["Fecha"])) + ('<br><span style="font-size:0.72rem;color:#c4b5fd;">✏️ editado</span>' if fue_modificado else "")

        filas_html += f"""
        <tr style="background-color:{row_bg};border-bottom:1px solid rgba(212,160,23,0.15);{'border-left:3px solid #7c3aed;' if fue_modificado else ''}"
            onmouseover="this.style.backgroundColor='rgba(212,160,23,0.12)'"
            onmouseout="this.style.backgroundColor='{row_bg}'">
            <td style="padding:9px 13px;color:#e8e8f0;font-size:0.84rem;white-space:nowrap;">{fecha_cell}</td>
            <td style="padding:9px 13px;text-align:center;">{tipo_badge}</td>
            <td style="padding:9px 13px;color:#d4c8a8;font-size:0.84rem;">{html.escape(str(row['Establecimiento']))}</td>
            <td style="padding:9px 13px;color:#f0f0f5;font-size:0.84rem;font-weight:600;">{html.escape(str(row['Producto']))}</td>
            <td style="padding:9px 13px;color:#d4a017;font-size:0.9rem;font-weight:700;text-align:right;">{cantidad_fmt}</td>
            <td style="padding:9px 13px;color:#90cdf4;font-size:0.82rem;">{usuario_cell}</td>
            <td style="padding:9px 13px;text-align:center;">{remito}</td>
            <td style="padding:9px 13px;color:#a0a0b0;font-size:0.82rem;">{obs}{mod_info}</td>
        </tr>"""

    tabla_html = f"""
<style>
  .hist-wrap {{ overflow-x:auto; border-radius:14px; border:1px solid rgba(212,160,23,0.35); box-shadow:0 6px 24px rgba(0,0,0,0.4); margin-top:8px; }}
  .hist-wrap table {{ width:100%; border-collapse:collapse; background:rgba(22,22,28,0.97); font-family:'DM Sans',sans-serif; }}
  .hist-wrap thead tr {{ background:linear-gradient(135deg,#d4a017 0%,#b87a0c 100%); }}
  .hist-wrap th {{ padding:11px 13px; color:#1a1a1f; font-weight:700; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.07em; white-space:nowrap; }}
</style>
<div class="hist-wrap"><table>
  <thead><tr>
    <th style="text-align:left;">📅 Fecha</th>
    <th style="text-align:center;">Tipo</th>
    <th style="text-align:left;">🏢 Establecimiento</th>
    <th style="text-align:left;">📦 Producto</th>
    <th style="text-align:right;">Cantidad</th>
    <th style="text-align:left;">👤 Usuario</th>
    <th style="text-align:center;">📄 Remito</th>
    <th style="text-align:left;">📝 Observaciones</th>
  </tr></thead>
  <tbody>{filas_html}</tbody>
</table></div>"""

    st.markdown(tabla_html, unsafe_allow_html=True)

    # ── PANEL ADMINISTRACIÓN (solo superadmin) ──────────────────
    if es_super_admin():
        st.markdown("---")
        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(212,160,23,0.15),rgba(180,60,60,0.10));
                    border:1px solid rgba(212,160,23,0.4);border-radius:12px;padding:12px 18px;margin-bottom:10px;">
            <span style="font-size:1.1rem;font-weight:700;color:#d4a017;">⚙️ Panel de Administración</span>
            <span style="color:#a0a0b0;font-size:0.82rem;margin-left:10px;">Solo visible para el administrador</span>
        </div>
        """, unsafe_allow_html=True)

        tab_edit, tab_del, tab_audit, tab_assign = st.tabs(["✏️ Modificar Registro", "🗑️ Eliminar Registro", "🔍 Auditoría de Cambios", "👤 Asignar Usuario"])

        # Construir opciones usando el df filtrado con id
        if "id" in df.columns:
            opciones_dict = {
                f"{row['fecha_str']}  |  {row['tipo'].upper()}  |  {row['producto_nombre']}  |  cant: {row['cantidad']}": row["id"]
                for _, row in df.iterrows()
            }
        else:
            opciones_dict = {}

        # ── TAB: MODIFICAR ─────────────────────────────────────
        with tab_audit:
            st.markdown("##### 🔍 Registro de modificaciones del Administrador")
            try:
                # Seleccionar columnas explícitas para evitar que Supabase resuelva
                # la FK usuario_id → auth.users (permission denied code 42501)
                audit_data = supabase.table("audit_log").select(
                    "id, timestamp, accion, datos, usuario_nombre"
                ).order("timestamp", desc=True).limit(200).execute()
                if audit_data.data:
                    df_audit = pd.DataFrame(audit_data.data)
                    df_audit["timestamp"] = pd.to_datetime(df_audit["timestamp"], errors="coerce").dt.strftime("%d/%m/%Y %H:%M")
                    audit_filas = ""
                    for _, ar in df_audit.iterrows():
                        accion = html.escape(str(ar.get("accion", "") or ""))
                        datos_raw = ar.get("datos", "") or ""
                        # Intentar parsear JSON para mostrarlo más legible
                        try:
                            import json as _json
                            datos_dict = _json.loads(datos_raw) if isinstance(datos_raw, str) else datos_raw
                            if isinstance(datos_dict, dict):
                                datos_str = " | ".join(f"{k}: {v}" for k, v in datos_dict.items() if k not in ("antes", "despues"))
                                antes = datos_dict.get("antes", {})
                                despues = datos_dict.get("despues", {})
                                if antes or despues:
                                    datos_str += f" → antes: {antes} | después: {despues}"
                            else:
                                datos_str = str(datos_raw)
                        except Exception:
                            datos_str = str(datos_raw)
                        datos = html.escape(datos_str[:300])
                        ts = html.escape(str(ar.get("timestamp", "") or ""))
                        usuario = html.escape(str(ar.get("usuario_nombre", "") or "Admin"))
                        audit_filas += f"""<tr style="border-bottom:1px solid rgba(212,160,23,0.15);">
                            <td style="padding:8px 12px;color:#e8e8f0;font-size:0.82rem;white-space:nowrap;">{ts}</td>
                            <td style="padding:8px 12px;color:#d4a017;font-size:0.82rem;font-weight:600;">{accion}</td>
                            <td style="padding:8px 12px;color:#a0a0b0;font-size:0.78rem;word-break:break-word;max-width:420px;">{datos}</td>
                            <td style="padding:8px 12px;color:#90cdf4;font-size:0.82rem;font-weight:500;">{usuario}</td>
                        </tr>"""
                    audit_html = f"""<div style="overflow-x:auto;border-radius:12px;border:1px solid rgba(212,160,23,0.3);margin-top:8px;">
                    <table style="width:100%;border-collapse:collapse;background:rgba(22,22,28,0.97);font-family:sans-serif;">
                    <thead><tr style="background:linear-gradient(135deg,#7c3aed,#4c1d95);">
                        <th style="padding:10px 12px;color:#fff;font-size:0.78rem;text-align:left;">📅 Fecha</th>
                        <th style="padding:10px 12px;color:#fff;font-size:0.78rem;text-align:left;">⚡ Acción</th>
                        <th style="padding:10px 12px;color:#fff;font-size:0.78rem;text-align:left;">📋 Detalle</th>
                        <th style="padding:10px 12px;color:#fff;font-size:0.78rem;text-align:left;">👤 Usuario</th>
                    </tr></thead>
                    <tbody>{audit_filas}</tbody></table></div>"""
                    st.markdown(audit_html, unsafe_allow_html=True)
                else:
                    st.info("No hay registros de auditoría aún.")
            except Exception as e:
                # Si la columna usuario_nombre no existe, reintentar sin ella
                try:
                    audit_data2 = supabase.table("audit_log").select(
                        "id, timestamp, accion, datos"
                    ).order("timestamp", desc=True).limit(200).execute()
                    if audit_data2.data:
                        df_audit = pd.DataFrame(audit_data2.data)
                        df_audit["timestamp"] = pd.to_datetime(df_audit["timestamp"], errors="coerce").dt.strftime("%d/%m/%Y %H:%M")
                        audit_filas = ""
                        for _, ar in df_audit.iterrows():
                            accion = html.escape(str(ar.get("accion", "") or ""))
                            datos = html.escape(str(ar.get("datos", "") or "")[:300])
                            ts = html.escape(str(ar.get("timestamp", "") or ""))
                            audit_filas += f"""<tr style="border-bottom:1px solid rgba(212,160,23,0.15);">
                                <td style="padding:8px 12px;color:#e8e8f0;font-size:0.82rem;white-space:nowrap;">{ts}</td>
                                <td style="padding:8px 12px;color:#d4a017;font-size:0.82rem;font-weight:600;">{accion}</td>
                                <td style="padding:8px 12px;color:#a0a0b0;font-size:0.78rem;word-break:break-word;max-width:500px;">{datos}</td>
                                <td style="padding:8px 12px;color:#90cdf4;font-size:0.82rem;">Admin</td>
                            </tr>"""
                        audit_html = f"""<div style="overflow-x:auto;border-radius:12px;border:1px solid rgba(212,160,23,0.3);margin-top:8px;">
                        <table style="width:100%;border-collapse:collapse;background:rgba(22,22,28,0.97);font-family:sans-serif;">
                        <thead><tr style="background:linear-gradient(135deg,#7c3aed,#4c1d95);">
                            <th style="padding:10px 12px;color:#fff;font-size:0.78rem;text-align:left;">📅 Fecha</th>
                            <th style="padding:10px 12px;color:#fff;font-size:0.78rem;text-align:left;">⚡ Acción</th>
                            <th style="padding:10px 12px;color:#fff;font-size:0.78rem;text-align:left;">📋 Detalle</th>
                            <th style="padding:10px 12px;color:#fff;font-size:0.78rem;text-align:left;">👤 Usuario</th>
                        </tr></thead>
                        <tbody>{audit_filas}</tbody></table></div>"""
                        st.markdown(audit_html, unsafe_allow_html=True)
                    else:
                        st.info("No hay registros de auditoría aún.")
                except Exception as e2:
                    st.warning(f"No se pudo cargar el log de auditoría: {e2}")

        with tab_edit:
            if not opciones_dict:
                st.info("Sin registros para modificar en el filtro actual.")
            else:
                sel_edit = st.selectbox(
                    "📋 Seleccioná el registro a modificar",
                    list(opciones_dict.keys()),
                    key="admin_edit_sel"
                )
                mov_id_edit = opciones_dict.get(sel_edit)
                if mov_id_edit:
                    mov_orig = next((m for m in movimientos if m.get("id") == mov_id_edit), None)
                    if mov_orig:
                        with st.form("form_modificar_registro"):
                            st.markdown(f"**Registro seleccionado:** `{sel_edit}`")
                            col_e1, col_e2 = st.columns(2)
                            with col_e1:
                                nueva_cantidad = st.number_input(
                                    "📦 Nueva Cantidad",
                                    value=float(mov_orig.get("cantidad") or 0),
                                    min_value=0.0,
                                    step=0.01,
                                    key="edit_nueva_cantidad"
                                )
                            with col_e2:
                                nueva_obs = st.text_area(
                                    "📝 Observaciones",
                                    value=mov_orig.get("observaciones") or "",
                                    key="edit_nueva_obs"
                                )
                            motivo_edit = st.text_input(
                                "⚠️ Motivo de la modificación (requerido)",
                                placeholder="Ej: Corrección de error de carga",
                                key="edit_motivo"
                            )
                            submitted_edit = st.form_submit_button("💾 Guardar cambios", type="primary")

                        if submitted_edit:
                            if not motivo_edit.strip():
                                st.error("❌ Debés indicar el motivo de la modificación.")
                            else:
                                try:
                                    datos_antes = {
                                        "cantidad": mov_orig.get("cantidad"),
                                        "observaciones": mov_orig.get("observaciones"),
                                    }
                                    datos_despues = {
                                        "cantidad": nueva_cantidad,
                                        "observaciones": nueva_obs,
                                    }
                                    usuario_nombre_mod = (
                                        st.session_state.get("perfil", {}).get("nombre", "")
                                        or st.session_state.get("user_email", "")
                                        or "Admin"
                                    )
                                    update_payload = {
                                        "cantidad": nueva_cantidad,
                                        "observaciones": nueva_obs,
                                        "modificado_por": usuario_nombre_mod,
                                        "modificado_en": now_arg().isoformat(),
                                        "motivo_modificacion": motivo_edit.strip(),
                                    }
                                    try:
                                        supabase.table("movimientos").update(update_payload).eq("id", mov_id_edit).execute()
                                    except Exception:
                                        supabase.table("movimientos").update({
                                            "cantidad": nueva_cantidad,
                                            "observaciones": nueva_obs,
                                        }).eq("id", mov_id_edit).execute()
                                    registrar_auditoria("modificacion_registro", {
                                        "movimiento_id": mov_id_edit,
                                        "registro": sel_edit,
                                        "motivo": motivo_edit.strip(),
                                        "antes": datos_antes,
                                        "despues": datos_despues,
                                    })
                                    get_movimientos.clear() if hasattr(get_movimientos, "clear") else None
                                    st.success("✅ Registro modificado correctamente.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error al modificar: {e}")

        # ── TAB: ELIMINAR ──────────────────────────────────────
        with tab_del:
            if not opciones_dict:
                st.info("Sin registros para eliminar en el filtro actual.")
            else:
                sel_del = st.selectbox(
                    "📋 Seleccioná el registro a eliminar",
                    list(opciones_dict.keys()),
                    key="admin_del_sel"
                )
                mov_id_del = opciones_dict.get(sel_del)
                if mov_id_del:
                    mov_del = next((m for m in movimientos if m.get("id") == mov_id_del), None)
                    if mov_del:
                        st.warning(f"⚠️ Estás por **eliminar permanentemente** este registro:\n\n`{sel_del}`")
                        motivo_del = st.text_input(
                            "⚠️ Motivo de eliminación (requerido)",
                            placeholder="Ej: Registro duplicado / Error de carga",
                            key="del_motivo"
                        )
                        confirmar_del = st.checkbox(
                            "✅ Confirmo que quiero eliminar este registro de forma permanente",
                            key="del_confirm"
                        )
                        btn_disabled = not confirmar_del or not motivo_del.strip()
                        if st.button("🗑️ Eliminar registro", type="primary", disabled=btn_disabled, key="btn_eliminar"):
                            try:
                                datos_eliminados = {
                                    k: v for k, v in mov_del.items()
                                    if k not in ["productos", "establecimientos"]
                                }
                                registrar_auditoria("eliminacion_registro", {
                                    "movimiento_id": mov_id_del,
                                    "registro": sel_del,
                                    "motivo": motivo_del.strip(),
                                    "datos_eliminados": datos_eliminados,
                                })
                                supabase.table("movimientos").delete().eq("id", mov_id_del).execute()
                                st.success("✅ Registro eliminado. El evento quedó registrado en el log de auditoría.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al eliminar: {e}")

        # ── TAB: ASIGNAR USUARIO ───────────────────────────────
        with tab_assign:
            st.markdown("##### 👤 Asignar usuario a movimientos")

            # ── Sección 1: Asignar todos los sin usuario al Admin ──
            st.markdown("---")
            st.markdown("**🔁 Asignar movimientos sin usuario al Admin**")
            st.caption("Todos los movimientos que no tienen usuario asignado serán atribuidos al usuario Admin.")
            col_aa1, col_aa2 = st.columns([2, 1])
            with col_aa1:
                nombre_admin_input = st.text_input(
                    "Nombre del Admin a asignar",
                    value="Admin",
                    key="assign_admin_nombre"
                )
            with col_aa2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✅ Asignar todos al Admin", key="btn_asignar_admin", type="primary"):
                    try:
                        resp = supabase.table("movimientos").update({
                            "usuario_nombre": nombre_admin_input.strip() or "Admin"
                        }).is_("usuario_nombre", "null").execute()
                        # También los que tienen string vacío
                        supabase.table("movimientos").update({
                            "usuario_nombre": nombre_admin_input.strip() or "Admin"
                        }).eq("usuario_nombre", "").execute()
                        registrar_auditoria("asignacion_masiva_usuario", {
                            "usuario_asignado": nombre_admin_input.strip() or "Admin",
                            "descripcion": "Se asignaron todos los movimientos sin usuario al Admin"
                        })
                        st.success(f"✅ Movimientos sin usuario asignados a '{nombre_admin_input.strip() or 'Admin'}'. Recargando...")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

            # ── Sección 2: Reasignar movimientos filtrados ──
            st.markdown("---")
            st.markdown("**🎯 Reasignar movimientos a un usuario específico**")
            st.caption("Filtrá los movimientos que querés reasignar y elegí el usuario destino.")

            try:
                usuarios_lista = supabase.table("usuarios").select("id, nombre, rol").execute().data or []
                if not usuarios_lista:
                    st.warning("No se encontraron usuarios.")
                else:
                    col_r1, col_r2, col_r3 = st.columns(3)
                    with col_r1:
                        establ_opts = ["Todos"] + sorted(list(set(
                            m.get("establecimientos", {}).get("nombre", "") if isinstance(m.get("establecimientos"), dict) else ""
                            for m in movimientos if m.get("establecimientos")
                        )))
                        filtro_estab = st.selectbox("🏢 Establecimiento", establ_opts, key="assign_estab")
                    with col_r2:
                        usuario_actual_opts = ["Todos"] + sorted(list(set(
                            m.get("usuario_nombre", "") or "—"
                            for m in movimientos
                        )))
                        filtro_usr_actual = st.selectbox("👤 Usuario actual", usuario_actual_opts, key="assign_usr_actual")
                    with col_r3:
                        usuario_destino_opts = {u["nombre"]: u["id"] for u in usuarios_lista}
                        usuario_destino_sel = st.selectbox(
                            "🎯 Asignar a",
                            list(usuario_destino_opts.keys()),
                            key="assign_usr_destino"
                        )

                    # Filtrar movimientos según selección
                    movs_filtrados = movimientos.copy()
                    if filtro_estab != "Todos":
                        movs_filtrados = [
                            m for m in movs_filtrados
                            if isinstance(m.get("establecimientos"), dict)
                            and m["establecimientos"].get("nombre") == filtro_estab
                        ]
                    if filtro_usr_actual != "Todos":
                        val_filtro = None if filtro_usr_actual == "—" else filtro_usr_actual
                        movs_filtrados = [
                            m for m in movs_filtrados
                            if (m.get("usuario_nombre") or "—") == (filtro_usr_actual)
                        ]

                    st.caption(f"📦 Movimientos a reasignar: **{len(movs_filtrados)}**")

                    if movs_filtrados:
                        if st.button(
                            f"🔁 Reasignar {len(movs_filtrados)} movimientos a '{usuario_destino_sel}'",
                            key="btn_reasignar",
                            type="primary"
                        ):
                            try:
                                ids_a_reasignar = [m["id"] for m in movs_filtrados if m.get("id")]
                                # Actualizar en lotes
                                for mid in ids_a_reasignar:
                                    supabase.table("movimientos").update({
                                        "usuario_nombre": usuario_destino_sel,
                                        "usuario_id": usuario_destino_opts[usuario_destino_sel]
                                    }).eq("id", mid).execute()
                                registrar_auditoria("reasignacion_usuario", {
                                    "usuario_destino": usuario_destino_sel,
                                    "cantidad_movimientos": len(ids_a_reasignar),
                                    "filtro_estab": filtro_estab,
                                    "filtro_usr_anterior": filtro_usr_actual,
                                })
                                st.success(f"✅ {len(ids_a_reasignar)} movimientos reasignados a '{usuario_destino_sel}'.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al reasignar: {e}")
                    else:
                        st.info("No hay movimientos que coincidan con el filtro.")
            except Exception as e:
                st.error(f"❌ Error al cargar usuarios: {e}")


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

    umbral = st.number_input(
        "⚠️ Umbral de alerta (unidades)",
        min_value=0,
        value=cfg.STOCK_CRITICO_DEFAULT,
        step=10,
        help="Podés ajustar este valor para ver más o menos alertas según tu criterio."
    )

    stock_productos = get_stock_por_producto(estab_filter())

    if stock_productos.empty:
        st.info("💡 Sin datos para mostrar alertas.")
        return

    stock_bajo = stock_productos[stock_productos["stock"] < umbral]

    if not stock_bajo.empty:
        st.warning(f"⚠️ {len(stock_bajo)} productos con stock menor a {umbral} unidades.")

        # Exportar alertas
        csv_alertas = stock_bajo[["producto", "categoria", "stock", "unidad"]].to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Exportar alertas CSV",
            data=csv_alertas,
            file_name=f"alertas_stock_{date.today()}.csv",
            mime="text/csv"
        )
        render_tabla_html(stock_bajo[["producto", "categoria", "stock", "unidad"]])
    else:
        st.success(f"✅ Todos los productos tienen stock ≥ {umbral} unidades.")


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
    df["fecha"] = parse_fecha(df["fecha"])
    df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    df["producto_nombre"] = df["productos"].apply(lambda x: x.get("nombre", "") if isinstance(x, dict) else "")

    ingresos = df[df["tipo"] == "ingreso"]["cantidad"].sum() if "ingreso" in df["tipo"].values else 0
    egresos_total = df[df["tipo"] == "egreso"]["cantidad"].sum() if "egreso" in df["tipo"].values else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📥 Total Ingresos", f"{ingresos:,.0f}")
    with col2:
        st.metric("📤 Total Egresos", f"{egresos_total:,.0f}")
    with col3:
        st.metric("⚖️ Balance neto", f"{ingresos - egresos_total:,.0f}")

    # Construir resumen con columnas explícitas para evitar KeyError
    resumen = (
        df.groupby(["mes", "tipo"], as_index=False)["cantidad"]
        .sum()
        .rename(columns={"cantidad": "cantidad"})
    )
    # Asegurar que las columnas necesarias existen
    for col in ["mes", "tipo", "cantidad"]:
        if col not in resumen.columns:
            resumen[col] = ""

    col_exp1, col_exp2 = st.columns([4, 1])
    with col_exp2:
        csv_rep = resumen.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Exportar CSV",
            data=csv_rep,
            file_name=f"reporte_{date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )

    render_tabla_html(resumen)

    # Gráfico evolución mensual
    if not resumen.empty and "mes" in resumen.columns and "tipo" in resumen.columns:
        try:
            fig = px.bar(
                resumen, x="mes", y="cantidad", color="tipo",
                color_discrete_map={"ingreso": "#22c55e", "egreso": "#ef4444"},
                barmode="group",
                template="plotly_dark",
                labels={"mes": "Mes", "cantidad": "Cantidad", "tipo": "Tipo"}
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(20,20,28,0.85)",
                font_color="#f0f0f5", height=380, margin=dict(t=20, b=40),
                xaxis_tickangle=-30
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            logger.warning(f"No se pudo graficar reporte: {e}")
            st.info("ℹ️ No hay suficientes datos para generar el gráfico.")


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
                supabase.table("proveedores").insert({"nombre": nombre.strip(), "activo": True}).execute()
                registrar_auditoria("proveedor_creado", {"nombre": nombre})
                get_proveedores.clear()
                st.toast(f"✅ Proveedor '{nombre}' creado.")
                st.rerun()

    if proveedores:
        render_tabla_html(pd.DataFrame(proveedores)[["nombre", "activo"]])


def pagina_productos():
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>📦 Productos Globales</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

    rol = st.session_state.get("rol", "")
    es_admin = (rol == "admin")

    if es_admin:
        st.info("ℹ️ Los productos creados aquí están disponibles para **todos los establecimientos**.")
        categorias = get_categorias()
        cat_options = {c["nombre"]: c["id"] for c in categorias}

        with st.expander("➕ Agregar nuevo producto global"):
            col_a, col_b = st.columns(2)
            with col_a:
                cat_sel = st.selectbox("Categoría", list(cat_options.keys()), key="prod_cat_nueva")
            with col_b:
                unidad = st.selectbox("Unidad", ["litros", "kg", "unidades"], key="prod_unidad_nueva")

            # Selector de subcategoría para Agroquímicos
            SUBCATS_AGRO_PROD = ["Herbicidas", "Insecticidas", "Fungicidas", "Coadyuvantes", "Fertilizantes foliares"]
            es_agroquimico_prod = "agroquimico" in cat_sel.lower() or "agroquímico" in cat_sel.lower()
            subcategoria_prod_sel = None
            if es_agroquimico_prod:
                subcategoria_prod_sel = st.selectbox("🌿 Tipo de Agroquímico *", SUBCATS_AGRO_PROD, key="prod_subcategoria_nueva")

            with st.form("nuevo_producto"):
                nombre = st.text_input("Nombre del producto *")
                presentacion = st.text_input("Presentación (ej: 20L, 50kg)")
                col_mc1, col_mc2 = st.columns(2)
                with col_mc1:
                    marca_nueva = st.text_input("🏷️ Marca", placeholder="Ej: Monsanto, Bayer...")
                with col_mc2:
                    concentracion_nueva = st.text_input("⚗️ Concentración", placeholder="Ej: 48%, 500g/L")
                if st.form_submit_button("💾 Guardar producto global") and nombre:
                    # Verificar si ya existe un producto con el mismo nombre y categoría
                    existente = supabase.table("productos").select("id").ilike("nombre", nombre.strip()).eq("categoria_id", cat_options[cat_sel]).execute()
                    if existente.data:
                        st.warning(f"⚠️ Ya existe un producto llamado **'{nombre.strip()}'** en la categoría **'{cat_sel}'**. No se guardó.")
                    else:
                        supabase.table("productos").insert({
                            "categoria_id": cat_options[cat_sel],
                            "nombre": nombre.strip(),
                            "presentacion": presentacion.strip(),
                            "unidad_medida": unidad,
                            "subcategoria": subcategoria_prod_sel,
                            "marca": marca_nueva.strip() or None,
                            "concentracion": concentracion_nueva.strip() or None,
                            "activo": True
                        }).execute()
                        registrar_auditoria("producto_creado", {"nombre": nombre})
                        get_productos.clear()
                        st.toast(f"✅ Producto '{nombre}' creado.")
                        st.rerun()
    else:
        st.info("📋 Lista de productos disponibles. Solo el administrador puede agregar nuevos.")

    productos = get_productos()
    if productos:
        df = pd.DataFrame(productos)
        df["categoria"] = df["categorias"].apply(lambda x: x["nombre"] if x else "N/A")
        buscar_prod = st.text_input("🔎 Buscar producto", key="prod_buscar", placeholder="Escribí para filtrar...")
        if buscar_prod:
            df = df[df["nombre"].str.contains(buscar_prod, case=False, na=False)]

        if es_admin:
            st.markdown("---")
            st.markdown("### ✏️ Editar producto existente")
            opciones_prod = {f"{r['nombre']} ({r['categoria']})": r for _, r in df.iterrows()}
            prod_sel_edit = st.selectbox("Seleccioná un producto para editar", list(opciones_prod.keys()), key="prod_editar_sel")
            if prod_sel_edit:
                p = opciones_prod[prod_sel_edit]
                categorias_edit = get_categorias()
                cat_opts_edit = {c["nombre"]: c["id"] for c in categorias_edit}
                cat_actual_edit = p["categoria"]

                with st.form("form_editar_producto"):
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        nombre_edit = st.text_input("Nombre *", value=p.get("nombre", ""))
                        marca_edit = st.text_input("🏷️ Marca", value=p.get("marca") or "")
                        presentacion_edit = st.text_input("Presentación", value=p.get("presentacion") or "")
                    with col_e2:
                        cat_edit_sel = st.selectbox("Categoría", list(cat_opts_edit.keys()),
                                                     index=list(cat_opts_edit.keys()).index(cat_actual_edit) if cat_actual_edit in cat_opts_edit else 0,
                                                     key="prod_cat_edit")
                        concentracion_edit = st.text_input("⚗️ Concentración", value=p.get("concentracion") or "")
                        unidad_edit = st.selectbox("Unidad", ["litros", "kg", "unidades"],
                                                    index=["litros", "kg", "unidades"].index(p.get("unidad_medida", "litros")) if p.get("unidad_medida") in ["litros", "kg", "unidades"] else 0,
                                                    key="prod_unidad_edit")

                    SUBCATS_AGRO_EDIT = ["Herbicidas", "Insecticidas", "Fungicidas", "Coadyuvantes", "Fertilizantes foliares"]
                    es_agro_edit = "agroquimico" in cat_edit_sel.lower() or "agroquímico" in cat_edit_sel.lower()
                    subcateg_edit = None
                    if es_agro_edit:
                        subcat_actual = p.get("subcategoria") or SUBCATS_AGRO_EDIT[0]
                        idx_sub = SUBCATS_AGRO_EDIT.index(subcat_actual) if subcat_actual in SUBCATS_AGRO_EDIT else 0
                        subcateg_edit = st.selectbox("🌿 Tipo de Agroquímico", SUBCATS_AGRO_EDIT, index=idx_sub, key="prod_subcateg_edit")

                    activo_edit = st.checkbox("✅ Producto activo", value=bool(p.get("activo", True)))

                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        guardar_edit = st.form_submit_button("💾 Guardar cambios", use_container_width=True)
                    with col_btn2:
                        eliminar_edit = st.form_submit_button("🗑️ Desactivar producto", use_container_width=True)

                    if guardar_edit and nombre_edit:
                        supabase.table("productos").update({
                            "nombre": nombre_edit.strip(),
                            "categoria_id": cat_opts_edit[cat_edit_sel],
                            "marca": marca_edit.strip() or None,
                            "concentracion": concentracion_edit.strip() or None,
                            "presentacion": presentacion_edit.strip() or None,
                            "unidad_medida": unidad_edit,
                            "subcategoria": subcateg_edit,
                            "activo": activo_edit,
                        }).eq("id", p["id"]).execute()
                        registrar_auditoria("producto_editado", {"nombre": nombre_edit})
                        get_productos.clear()
                        st.toast(f"✅ Producto '{nombre_edit}' actualizado.")
                        st.rerun()

                    if eliminar_edit:
                        supabase.table("productos").update({"activo": False}).eq("id", p["id"]).execute()
                        registrar_auditoria("producto_desactivado", {"nombre": p.get("nombre")})
                        get_productos.clear()
                        st.warning(f"⚠️ Producto '{p.get('nombre')}' desactivado.")
                        st.rerun()
        else:
            render_tabla_html(df[["nombre", "categoria", "presentacion", "unidad_medida", "activo"]])


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
            available = [c for c in display_cols if c in df.columns]
            render_tabla_html(df[available])
    except Exception as e:
        logger.error(f"pagina_usuarios error: {e}")
        st.error(f"Error: {e}")


# ══════════════════════════════════════════════════════════════
# CONSOLIDADO
# ══════════════════════════════════════════════════════════════

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

    establecimientos_disp = sorted(stock_df["establecimiento"].dropna().unique().tolist())
    categorias_disp = sorted(stock_df["categoria"].dropna().unique().tolist())
    SUBCATS_AGRO = ["Herbicidas", "Insecticidas", "Fungicidas", "Coadyuvantes", "Fertilizantes foliares"]

    st.markdown("#### 🔍 Filtros")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        estabs_sel = st.multiselect("🏢 Establecimientos", options=establecimientos_disp, default=establecimientos_disp, key="cons_estabs")
    with col2:
        cat_sel = st.selectbox("📁 Categoría", ["Todas"] + categorias_disp, key="cons_cat")
    with col3:
        es_agro = cat_sel != "Todas" and ("agroqui" in cat_sel.lower() or "agroquí" in cat_sel.lower())
        if es_agro:
            subcat_sel = st.selectbox("🌿 Subcategoría", ["Todas"] + SUBCATS_AGRO, key="cons_subcat")
        else:
            subcat_sel = "Todas"
            st.selectbox("🌿 Subcategoría", ["—"], key="cons_subcat_dis", disabled=True)
    with col4:
        buscar = st.text_input("🔎 Buscar producto", key="cons_buscar", placeholder="Nombre...")

    df_f = stock_df.copy()
    if estabs_sel:
        df_f = df_f[df_f["establecimiento"].isin(estabs_sel)]
    if cat_sel != "Todas":
        df_f = df_f[df_f["categoria"] == cat_sel]
    if es_agro and subcat_sel != "Todas":
        if "subcategoria" in df_f.columns:
            df_f = df_f[df_f["subcategoria"] == subcat_sel]
    if buscar:
        df_f = df_f[df_f["producto"].str.contains(buscar, case=False, na=False)]

    if df_f.empty:
        st.warning("Sin datos para los filtros seleccionados.")
        return

    tab1, tab2 = st.tabs(["📋 Tabla de Stock", "📊 Gráficos"])

    with tab1:
        col_ord1, col_ord2 = st.columns([3, 1])
        with col_ord2:
            orden = st.selectbox("Ordenar por", ["producto", "establecimiento", "categoria", "stock"], key="cons_orden")
            asc = st.checkbox("Ascendente", value=True, key="cons_asc")
        df_show = df_f.sort_values(orden, ascending=asc)

        # Exportar consolidado
        csv_con = df_show.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Exportar CSV",
            data=csv_con,
            file_name=f"consolidado_{date.today()}.csv",
            mime="text/csv"
        )
        render_tabla_html(df_show[["producto", "presentacion", "unidad", "categoria", "establecimiento", "stock"]], height=600)

    with tab2:
        st.markdown("##### 📊 Stock por Producto y Establecimiento")
        top_n = st.slider("Mostrar top N productos", 5, 50, 20, key="cons_topn")
        df_top = df_f.groupby("producto")["stock"].sum().nlargest(top_n).index
        df_bar = df_f[df_f["producto"].isin(df_top)]

        fig_bar = px.bar(
            df_bar, x="producto", y="stock", color="establecimiento",
            barmode="group",
            color_discrete_sequence=["#d4a017", "#22c55e", "#3b82f6"],
            template="plotly_dark",
            labels={"producto": "Producto", "stock": "Stock", "establecimiento": "Establecimiento"}
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(20,20,28,0.85)",
            font_color="#f0f0f5", legend_font_color="#f0f0f5",
            xaxis_tickangle=-40, height=420, margin=dict(t=30, b=80)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        col_g2, col_g3 = st.columns(2)

        with col_g2:
            st.markdown("##### 🥧 Distribución por Categoría")
            df_pie = df_f.groupby("categoria")["stock"].sum().reset_index()
            df_pie = df_pie[df_pie["stock"] > 0]
            fig_pie = px.pie(
                df_pie, names="categoria", values="stock",
                color_discrete_sequence=px.colors.sequential.Oranges_r,
                template="plotly_dark"
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", font_color="#f0f0f5",
                legend_font_color="#f0f0f5", height=340, margin=dict(t=20, b=20)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_g3:
            st.markdown(f"##### ⚠️ Stock Bajo (< {cfg.STOCK_CRITICO_DEFAULT} unidades)")
            df_bajo = df_f[df_f["stock"] < cfg.STOCK_CRITICO_DEFAULT].sort_values("stock")
            if df_bajo.empty:
                st.success("✅ Sin productos con stock crítico en la selección actual.")
            else:
                fig_bajo = px.bar(
                    df_bajo, x="stock", y="producto", orientation="h",
                    color="establecimiento",
                    color_discrete_sequence=["#ef4444", "#f59e0b", "#f97316"],
                    template="plotly_dark",
                    labels={"stock": "Stock", "producto": "Producto"}
                )
                fig_bajo.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(20,20,28,0.85)",
                    font_color="#f0f0f5", height=340, margin=dict(t=10, b=20)
                )
                st.plotly_chart(fig_bajo, use_container_width=True)

        st.markdown("##### 📈 Evolución Histórica de Movimientos")
        movs_hist = get_movimientos(None, limit=10000)
        if movs_hist:
            df_hist = pd.DataFrame(movs_hist)
            df_hist["fecha"] = parse_fecha(df_hist["fecha"])
            df_hist["mes"] = df_hist["fecha"].dt.to_period("M").dt.to_timestamp()
            df_hist["establecimiento_nombre"] = df_hist["establecimientos"].apply(
                lambda x: x.get("nombre", "") if isinstance(x, dict) else ""
            )
            if estabs_sel:
                df_hist = df_hist[df_hist["establecimiento_nombre"].isin(estabs_sel)]
            df_evo = df_hist.groupby(["mes", "tipo", "establecimiento_nombre"])["cantidad"].sum().reset_index()
            fig_evo = px.line(
                df_evo, x="mes", y="cantidad", color="establecimiento_nombre",
                line_dash="tipo",
                color_discrete_sequence=["#d4a017", "#22c55e", "#3b82f6"],
                template="plotly_dark",
                labels={"mes": "Mes", "cantidad": "Cantidad", "establecimiento_nombre": "Establecimiento", "tipo": "Tipo"}
            )
            fig_evo.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(20,20,28,0.85)",
                font_color="#f0f0f5", legend_font_color="#f0f0f5",
                height=380, margin=dict(t=20, b=40)
            )
            st.plotly_chart(fig_evo, use_container_width=True)

        st.markdown("##### 🔀 Comparativa de Producto entre Establecimientos")
        productos_disp = sorted(df_f["producto"].dropna().unique().tolist())
        prod_comp = st.selectbox("Seleccionar producto a comparar", productos_disp, key="cons_prod_comp")
        df_comp = df_f[df_f["producto"] == prod_comp]
        if not df_comp.empty:
            fig_comp = px.bar(
                df_comp, x="establecimiento", y="stock",
                color="establecimiento",
                color_discrete_sequence=["#d4a017", "#22c55e", "#3b82f6"],
                template="plotly_dark",
                text="stock",
                labels={"establecimiento": "Establecimiento", "stock": "Stock"}
            )
            fig_comp.update_traces(textposition="outside", textfont_color="#f0f0f5")
            fig_comp.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(20,20,28,0.85)",
                font_color="#f0f0f5", showlegend=False,
                height=320, margin=dict(t=20, b=40)
            )
            st.plotly_chart(fig_comp, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    if not check_auth():
        login()
        return

    if not verificar_perfil():
        return

    if (
        st.session_state.get("rol") != "admin"
        and not st.session_state.get("password_changed", False)
        and not st.session_state.get("skip_password_check", False)
    ):
        mostrar_cambio_password()
        return

    # Toggle sidebar
    if "sidebar_open" not in st.session_state:
        st.session_state["sidebar_open"] = True

    st.markdown('<div class="sidebar-toggle-wrap">', unsafe_allow_html=True)
    icono = "✕" if st.session_state["sidebar_open"] else "☰"
    if st.button(icono, key="btn_toggle_sidebar"):
        st.session_state["sidebar_open"] = not st.session_state["sidebar_open"]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state["sidebar_open"]:
        st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: flex !important;
                width: 21rem !important;
                min-width: 21rem !important;
                transform: translateX(0) !important;
                visibility: visible !important;
            }
        </style>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none !important;
                width: 0 !important;
                min-width: 0 !important;
                visibility: hidden !important;
            }
        </style>""", unsafe_allow_html=True)

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

    estab_nombre = st.session_state.get(
        "estab_activo_nombre",
        st.session_state.get("establecimiento_nombre", "Consolidado")
    )
    st.markdown(f"""
    <div class="footer">
        🌾 Sistema de Control de Stock Agrícola &nbsp;|&nbsp; 📍 {html.escape(str(estab_nombre))}
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
