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
    [data-testid="stFileUploader"] label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
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
        width: 200% !important;
        height: auto !important;
        object-fit: contain !important;
        display: block;
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
        padding: 1.6rem 2rem;
        color: #a8a8b0 !important;
        font-size: 0.78rem;
        border-top: 1px solid var(--gold-25);
        margin-top: 3rem;
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
                delta = (datetime.utcnow() - last).total_seconds() / 60
                if delta > cfg.SESSION_TIMEOUT_MINUTES:
                    logout()
                    st.warning("⏰ Sesión expirada por inactividad. Volvé a ingresar.")
                    return False
            st.session_state["last_activity"] = datetime.utcnow()
            return True
        session = supabase.auth.get_session()
        if session:
            st.session_state["session"] = session
            st.session_state["user_id"] = session.user.id
            st.session_state["last_activity"] = datetime.utcnow()
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
        remaining = (locked_until - datetime.utcnow()).total_seconds()
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
            datetime.utcnow() + timedelta(minutes=cfg.LOGIN_LOCKOUT_MINUTES)
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


def subir_remito_pdf(archivo_pdf, movimiento_id, usuario_id, establecimiento_id):
    """Sube PDF a Supabase Storage con ruta organizada por establecimiento/año/mes."""
    if archivo_pdf is None:
        return None

    ok, msg = _validar_pdf(archivo_pdf)
    if not ok:
        st.error(f"❌ {msg}")
        return None

    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
        nombre_archivo = f"remito_{movimiento_id}_{uuid.uuid4().hex[:8]}.pdf"
        # Organización por carpetas: estab_id/año/mes/archivo
        ruta_completa = f"{establecimiento_id}/{now.year}/{now.month:02d}/{nombre_archivo}"
        archivo_bytes = archivo_pdf.getvalue()

        supabase.storage.from_(cfg.SUPABASE_STORAGE_BUCKET).upload(
            path=ruta_completa,
            file=archivo_bytes,
            file_options={"content-type": "application/pdf"}
        )

        # Guardar ruta interna (no URL pública) en la tabla
        supabase.table("movimientos").update({
            "remito_url": ruta_completa,
            "remito_filename": nombre_archivo
        }).eq("id", movimiento_id).execute()

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
                        st.session_state["last_activity"] = datetime.utcnow()
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
        q = supabase.table("movimientos").select("*").limit(limit)
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
        for pid, qty in stock.items() if qty != 0
    ]

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
        supabase.table("audit_log").insert({
            "usuario_id": st.session_state.get("user_id"),
            "accion": accion,
            "datos": str(datos) if datos else None,
            "timestamp": datetime.utcnow().isoformat(),
        }).execute()
    except Exception:
        pass  # La tabla puede no existir; no interrumpe el flujo


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

    df_filtrado = stock_productos.copy()
    if cat_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["categoria"] == cat_sel]
    if es_agro_dash and subcat_sel != "Todos":
        prods_subcat = get_productos(subcategoria=subcat_sel)
        nombres_subcat = [p["nombre"] for p in prods_subcat]
        df_filtrado = df_filtrado[df_filtrado["producto"].isin(nombres_subcat)]
    if prod_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["producto"] == prod_sel]

    total_stock = df_filtrado["stock"].sum()
    total_productos = len(df_filtrado)
    stock_bajo = len(df_filtrado[df_filtrado["stock"] < cfg.STOCK_CRITICO_DEFAULT])

    # KPI extra: productos con movimiento este mes
    movs_mes = get_movimientos(estab_filter(), limit=1000)
    movs_este_mes = 0
    if movs_mes:
        df_m = pd.DataFrame(movs_mes)
        df_m["fecha"] = pd.to_datetime(df_m["fecha"])
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

    with st.form("form_ingreso", clear_on_submit=False):
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
            archivo_remito = None
            st.caption("ℹ️ Como administrador, no es obligatorio adjuntar remito.")

        submitted = st.form_submit_button("✅ Registrar Ingreso", use_container_width=True)

        if submitted:
            if cantidad <= 0:
                st.error("❌ La cantidad debe ser mayor a 0.")
                return

            if not es_admin and archivo_remito is None:
                st.error("❌ Es obligatorio adjuntar el remito en PDF.")
                return

            try:
                with st.spinner("Registrando ingreso..."):
                    observaciones_full = f"[{tipo_ingreso}] {observaciones}" if observaciones else f"[{tipo_ingreso}]"
                    now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).replace(tzinfo=None)

                    payload = {
                        "tipo": "ingreso",
                        "producto_id": producto_id,
                        "establecimiento_id": establecimiento_id,
                        "cantidad": float(cantidad),
                        "fecha": now.isoformat(),
                        "proveedor_id": proveedor_id,
                        "observaciones": observaciones_full,
                        "usuario_id": st.session_state.get("user_id"),
                    }

                    resultado = supabase.table("movimientos").insert(payload).execute()
                    movimiento_id = resultado.data[0]["id"] if resultado.data else None

                    remito_subido = False
                    if movimiento_id and archivo_remito is not None:
                        url = subir_remito_pdf(archivo_remito, movimiento_id, st.session_state.get("user_id"), establecimiento_id)
                        remito_subido = url is not None

                    registrar_auditoria("ingreso_registrado", {"movimiento_id": movimiento_id, "producto": prod_sel})
                    get_movimientos.clear() if hasattr(get_movimientos, "clear") else None

                    msg = "✅ Ingreso registrado exitosamente!" + (" — Remito adjuntado" if remito_subido else "")
                    st.toast(msg)
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

    rol = st.session_state.get("rol", "")
    es_admin = (rol == "admin")

    establecimientos = get_establecimientos()
    categorias = get_categorias()

    if not establecimientos:
        st.warning("⚠️ No hay establecimientos cargados.")
        return

    if es_admin:
        estab_options = {e["nombre"]: e["id"] for e in establecimientos}
        estab_sel = st.selectbox("🏢 Establecimiento *", list(estab_options.keys()), key="eg_estab")
        establecimiento_id = estab_options[estab_sel]
        establecimiento_nombre = estab_sel
    else:
        establecimiento_id = st.session_state.get("establecimiento_id")
        establecimiento_nombre = st.session_state.get("establecimiento_nombre", "")
        st.info(f"📍 Establecimiento: {establecimiento_nombre}")

    col1, col2 = st.columns(2)
    with col1:
        if not categorias:
            st.warning("⚠️ No hay categorías cargadas.")
            return
        cat_options = {c["nombre"]: c["id"] for c in categorias}
        cat_sel = st.selectbox("📁 Categoría *", list(cat_options.keys()), key="eg_cat")
        cat_id = cat_options[cat_sel]

    es_agroquimico_eg = "agroquimico" in cat_sel.lower() or "agroquímico" in cat_sel.lower()
    subcategoria_eg = None
    if es_agroquimico_eg:
        subcategoria_eg = st.selectbox(
            "🌿 Tipo de Agroquímico *",
            ["Herbicidas", "Insecticidas", "Coadyuvantes"],
            key="eg_subcategoria"
        )

    with col2:
        productos = get_productos(cat_id, subcategoria_eg if es_agroquimico_eg else None)
        if not productos:
            st.warning("⚠️ No hay productos en esta categoría.")
            return
        prod_options = {p["nombre"]: p["id"] for p in productos}
        prod_sel = st.selectbox("🏷️ Producto *", list(prod_options.keys()), key="eg_prod")
        producto_id = prod_options[prod_sel]

    from zoneinfo import ZoneInfo
    _now_arg = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).replace(tzinfo=None)
    st.caption(f"🕐 Fecha y hora del registro: **{_now_arg.strftime('%d/%m/%Y %H:%M')}**")

    with st.form("form_egreso", clear_on_submit=False):
        cantidad = st.number_input("📦 Cantidad *", min_value=0.001, step=0.5, format="%.3f")
        tipo_egreso = st.selectbox("📌 Tipo de Egreso", ["Uso", "Venta", "Traslado", "Merma", "Otro"])
        observaciones = st.text_area("📝 Observaciones", placeholder="Motivo del egreso, destino, responsable, etc.")

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
        else:
            archivo_remito = None

        submitted = st.form_submit_button("✅ Registrar Egreso", use_container_width=True)

        if submitted:
            if cantidad <= 0:
                st.error("❌ La cantidad debe ser mayor a 0.")
                return

            if not es_admin and archivo_remito is None:
                st.error("❌ Es obligatorio adjuntar el remito en PDF.")
                return

            # Validar stock disponible
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

                    registrar_auditoria("egreso_registrado", {"movimiento_id": movimiento_id, "producto": prod_sel})

                    st.toast("✅ Egreso registrado exitosamente!" + (" — Remito adjuntado" if remito_subido else ""))
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
        df["fecha"] = pd.to_datetime(df["fecha"])
        df = df.sort_values("fecha", ascending=False)

    df["producto_nombre"] = df["productos"].apply(lambda x: x.get("nombre", "") if isinstance(x, dict) else "")
    df["categoria_nombre"] = df["productos"].apply(
        lambda x: x.get("categorias", {}).get("nombre", "") if isinstance(x, dict) and x.get("categorias") else ""
    )
    df["establecimiento_nombre"] = df["establecimientos"].apply(lambda x: x.get("nombre", "") if isinstance(x, dict) else "")
    df["fecha_str"] = df["fecha"].dt.strftime("%d/%m/%Y %H:%M")

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

    # Botón de exportación
    col_exp1, col_exp2 = st.columns([4, 1])
    with col_exp2:
        export_df = df[["fecha_str", "tipo", "establecimiento_nombre", "producto_nombre", "cantidad", "observaciones"]].copy()
        export_df.columns = ["Fecha", "Tipo", "Establecimiento", "Producto", "Cantidad", "Observaciones"]
        csv_data = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Exportar CSV",
            data=csv_data,
            file_name=f"historial_{date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )

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

        obs_raw = row["Observaciones"]
        obs = html.escape(str(obs_raw)) if obs_raw and str(obs_raw) not in ["nan", "None", ""] else "—"
        remito_val = row["Remito"]
        remito = str(remito_val) if remito_val and str(remito_val) not in ["nan", "None", "", "—"] else '<span style="color:#666;font-size:0.8rem;">—</span>'
        try:
            cantidad_fmt = f"{float(row['Cantidad']):,.2f}"
        except Exception:
            cantidad_fmt = html.escape(str(row["Cantidad"]))

        filas_html += f"""
        <tr style="background-color:{row_bg};border-bottom:1px solid rgba(212,160,23,0.15);"
            onmouseover="this.style.backgroundColor='rgba(212,160,23,0.12)'"
            onmouseout="this.style.backgroundColor='{row_bg}'">
            <td style="padding:9px 13px;color:#e8e8f0;font-size:0.84rem;white-space:nowrap;">{html.escape(str(row['Fecha']))}</td>
            <td style="padding:9px 13px;text-align:center;">{tipo_badge}</td>
            <td style="padding:9px 13px;color:#d4c8a8;font-size:0.84rem;">{html.escape(str(row['Establecimiento']))}</td>
            <td style="padding:9px 13px;color:#f0f0f5;font-size:0.84rem;font-weight:600;">{html.escape(str(row['Producto']))}</td>
            <td style="padding:9px 13px;color:#d4a017;font-size:0.9rem;font-weight:700;text-align:right;">{cantidad_fmt}</td>
            <td style="padding:9px 13px;text-align:center;">{remito}</td>
            <td style="padding:9px 13px;color:#a0a0b0;font-size:0.82rem;">{obs}</td>
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
    <th style="text-align:center;">📄 Remito</th>
    <th style="text-align:left;">📝 Observaciones</th>
  </tr></thead>
  <tbody>{filas_html}</tbody>
</table></div>"""

    st.markdown(tabla_html, unsafe_allow_html=True)


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
    df["fecha"] = pd.to_datetime(df["fecha"])
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
            with st.form("nuevo_producto"):
                nombre = st.text_input("Nombre del producto *")
                presentacion = st.text_input("Presentación (ej: 20L, 50kg)")
                if st.form_submit_button("💾 Guardar producto global") and nombre:
                    supabase.table("productos").insert({
                        "categoria_id": cat_options[cat_sel],
                        "nombre": nombre.strip(),
                        "presentacion": presentacion.strip(),
                        "unidad_medida": unidad,
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
    SUBCATS_AGRO = ["Herbicidas", "Insecticidas", "Coadyuvantes", "Fungicidas", "Fertilizantes foliares"]

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
            df_hist["fecha"] = pd.to_datetime(df_hist["fecha"])
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
        <p>🌾 Sistema de Control de Stock Agrícola | 📍 {html.escape(str(estab_nombre))}</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
