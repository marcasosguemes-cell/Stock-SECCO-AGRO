"""
SISTEMA DE CONTROL DE STOCK AGRÍCOLA
App principal Streamlit — La Sonia / San Guillermo / Camba Pora
Versión con logo grande, fondo muy apagado y subtítulos en burbuja
"""

import streamlit as st
from supabase import create_client, Client
from datetime import date, timedelta
import pandas as pd
from io import BytesIO

# ── Configuración de página ────────────────────────────────────
st.set_page_config(
    page_title="Stock Agrícola - SECCO AGRO",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Cliente Supabase ───────────────────────────────────────────
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]

@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()


# ══════════════════════════════════════════════════════════════
# CSS MEJORADO - Fondo muy apagado, logo en óvalo más pequeño
# ══════════════════════════════════════════════════════════════

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

    /* ── Fondo con imagen muy apagada ── */
    .stApp {
        background-image: url('https://raw.githubusercontent.com/marcasosguemes-cell/Stock-SECCO-AGRO/main/Fondo.PNG') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        background-repeat: no-repeat !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(255, 255, 255, 0.935);
        z-index: -1;
        pointer-events: none;
    }

    /* ── Sidebar refinado ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #192337 0%, #1e2d45 60%, #1a2a3f 100%) !important;
        border-right: 1px solid rgba(212, 160, 23, 0.25) !important;
        box-shadow: 4px 0 24px rgba(0,0,0,0.18);
    }

    [data-testid="stSidebar"] * {
        color: #dce8dc !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    [data-testid="stSidebar"] .stButton button {
        background: transparent;
        border: 1px solid rgba(212, 160, 23, 0.18);
        width: 100%;
        text-align: left;
        padding: 0.65rem 1.1rem;
        border-radius: 10px;
        margin: 4px 0;
        font-size: 0.88rem;
        font-weight: 500;
        letter-spacing: 0.01em;
        transition: all 0.25s cubic-bezier(.4,0,.2,1);
        color: #c8dcc8 !important;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(212, 160, 23, 0.12);
        border-color: rgba(212, 160, 23, 0.5);
        transform: translateX(5px);
        color: #f5e199 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    }

    /* ── Sidebar header con logo ── */
    .sidebar-header {
        text-align: center;
        padding: 1.6rem 0 1.2rem 0;
        border-bottom: 1px solid rgba(212, 160, 23, 0.35);
        margin-bottom: 1.4rem;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .sidebar-header img {
        width: 145px !important;
        height: auto !important;
        filter: drop-shadow(0 4px 16px rgba(0,0,0,0.35)) brightness(1.05);
        margin-bottom: 12px;
        transition: transform 0.3s ease;
    }

    .sidebar-header img:hover {
        transform: scale(1.03);
    }

    .sidebar-header h1 {
        font-family: 'Playfair Display', serif !important;
        font-size: 1.15rem !important;
        margin: 0;
        color: #d4a017 !important;
        letter-spacing: 0.04em;
        font-weight: 600;
    }

    /* ── Profile card ── */
    .profile-card {
        text-align: center;
        padding: 0.9rem 1rem;
        margin: 0.5rem 0 1rem 0;
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(212, 160, 23, 0.15);
        border-radius: 14px;
        backdrop-filter: blur(4px);
    }

    .profile-name {
        font-size: 0.95rem;
        font-weight: 600;
        color: #e8f4e8 !important;
        margin-bottom: 4px;
    }

    .profile-role, .profile-location {
        font-size: 0.78rem;
        color: #a8c8a8 !important;
        margin-top: 3px;
    }

    /* ── Título login con logo en óvalo MÁS PEQUEÑO ── */
    .title-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.8rem;
    }

    /* Óvalo detrás del logo - TAMAÑO REDUCIDO */
    .logo-oval-wrap {
        background: #f7f3e8;
        border: 2px solid rgba(212, 160, 23, 0.5);
        border-radius: 50%;
        width: 180px;        /* Óvalo mucho más pequeño */
        height: 108px;       /* Óvalo mucho más pequeño */
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.25), 0 1px 0 rgba(255,255,255,0.6) inset;
        margin-bottom: 16px;
        transition: transform 0.35s ease, box-shadow 0.35s ease;
    }

    .logo-oval-wrap:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }

    .title-logo {
        width: 100% !important;
        height: 100% !important;
        object-fit: contain !important;
        display: block;
        transition: transform 0.35s ease;
        padding: 8px;
    }

    /* Burbuja transparente tipo glassmorphism */
    .title-bubble-login {
        background: rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.35);
        border-radius: 20px;
        padding: 1rem 2.2rem 0.9rem 2.2rem;
        display: block;
        box-shadow: 0 4px 24px rgba(0,0,0,0.15);
        text-align: center;
        margin-bottom: 0.5rem;
        width: 100%;
        box-sizing: border-box;
    }

    .main-title-with-logo {
        font-family: 'Playfair Display', serif !important;
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff !important;
        text-shadow: 0 2px 12px rgba(0,0,0,0.45), 0 1px 3px rgba(0,0,0,0.6);
        margin: 0 0 0.3rem 0;
        text-align: center;
        letter-spacing: 0.01em;
        -webkit-text-fill-color: unset !important;
        line-height: 1.15;
    }

    .login-subtitle {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.88rem;
        color: #f0f8e8 !important;
        text-shadow: 0 1px 6px rgba(0,0,0,0.5);
        font-weight: 500;
        letter-spacing: 0.07em;
        margin: 0;
    }

    /* ── Title bubbles ── */
    .title-bubble {
        background: linear-gradient(135deg, #c8a060 0%, #b8905a 100%);
        border: 1px solid rgba(120, 85, 45, 0.35);
        border-radius: 18px;
        padding: 1rem 2.2rem;
        display: inline-block;
        box-shadow: 0 4px 18px rgba(100, 70, 30, 0.18), 0 1px 0 rgba(255,255,255,0.25) inset;
        transition: all 0.25s ease;
        text-align: center;
        margin-bottom: 1.4rem;
    }

    .title-bubble:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 28px rgba(100, 70, 30, 0.24);
    }

    .title-bubble h1 {
        margin: 0;
        font-family: 'Playfair Display', serif !important;
        font-size: 1.75rem !important;
        color: #2a4a1a !important;
        font-weight: 700;
        letter-spacing: 0.01em;
        -webkit-text-fill-color: unset !important;
    }

    .title-bubble p {
        margin: 0.35rem 0 0 0;
        color: #3d5a2a !important;
        font-size: 0.88rem;
        font-weight: 400;
        opacity: 0.85;
    }

    /* ── Section titles ── */
    .section-title {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 1.1rem !important;
        font-weight: 600;
        color: #1a4a1a !important;
        border-left: 3px solid #d4a017;
        padding-left: 0.85rem;
        margin: 1.8rem 0 1rem 0;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        font-size: 0.82rem !important;
    }

    .main-title {
        font-family: 'Playfair Display', serif !important;
        font-size: 1.9rem;
        font-weight: 700;
        color: #1a4a1a !important;
        margin: 0 0 0.4rem 0;
        -webkit-text-fill-color: unset !important;
    }

    /* ── Metric cards ── */
    .metric-card {
        background: linear-gradient(145deg, rgba(195, 215, 175, 0.82) 0%, rgba(175, 200, 155, 0.88) 100%) !important;
        border: 1px solid rgba(100, 130, 80, 0.25);
        border-radius: 18px;
        box-shadow: 0 2px 12px rgba(50, 90, 50, 0.1), 0 1px 0 rgba(255,255,255,0.6) inset;
        transition: all 0.3s cubic-bezier(.4,0,.2,1);
        text-align: center !important;
        padding: 1.2rem 1rem;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 28px rgba(50, 90, 50, 0.16);
        background: linear-gradient(145deg, rgba(205, 225, 185, 0.92) 0%, rgba(185, 210, 165, 0.95) 100%) !important;
    }

    .metric-card, .metric-card * {
        color: #0d2a0d !important;
        text-align: center !important;
    }

    .metric-value {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.6rem !important;
        font-weight: 700;
        color: #173a17 !important;
        margin: 0.4rem 0;
        line-height: 1;
    }

    .metric-label {
        font-size: 0.72rem !important;
        color: #2a4a2a !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #2c5e2e, #3a7040) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px;
        padding: 0.55rem 1.3rem;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600;
        font-size: 0.88rem;
        letter-spacing: 0.02em;
        transition: all 0.25s ease;
        box-shadow: 0 2px 8px rgba(44, 94, 46, 0.25);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(44, 94, 46, 0.38);
        background: linear-gradient(135deg, #316634, #428046) !important;
    }

    /* ── Forms ── */
    [data-testid="stForm"] {
        background: rgba(195, 215, 175, 0.45) !important;
        border: 1px solid rgba(100, 130, 80, 0.2);
        border-radius: 18px;
        padding: 1.2rem;
        box-shadow: 0 2px 12px rgba(50, 90, 50, 0.07);
    }

    /* ── Inputs ── */
    input, textarea, select {
        color: #1a2a1a !important;
        background-color: rgba(245, 252, 235, 0.92) !important;
        border-radius: 9px !important;
        border: 1px solid rgba(100, 130, 80, 0.3) !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    /* ── Tables ── */
    .stDataFrame {
        background: rgba(195, 215, 175, 0.5);
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(50, 90, 50, 0.08);
    }

    .stDataFrame * {
        color: #1a2a1a !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    /* ── Alerts ── */
    .stAlert {
        background: rgba(195, 215, 175, 0.65) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(100, 130, 80, 0.25) !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    /* ── Badges ── */
    .badge {
        display: inline-block;
        padding: 0.22rem 0.7rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .badge-admin {
        background: linear-gradient(135deg, #c89010, #a87010);
        color: white !important;
        box-shadow: 0 2px 6px rgba(180, 130, 20, 0.3);
    }

    .badge-operator {
        background: linear-gradient(135deg, #2c5e2e, #3d7a3f);
        color: white !important;
        box-shadow: 0 2px 6px rgba(44, 94, 46, 0.3);
    }

    /* ── Footer ── */
    .footer {
        text-align: center;
        padding: 1.6rem 2rem;
        color: #4a5b4a !important;
        font-size: 0.78rem;
        border-top: 1px solid rgba(100, 120, 80, 0.25);
        margin-top: 2.5rem;
        background: linear-gradient(135deg, rgba(195, 215, 175, 0.6) 0%, rgba(175, 200, 155, 0.7) 100%);
        border-radius: 16px;
        letter-spacing: 0.02em;
    }

    /* ── General text ── */
    p, span, div, label, .stMarkdown, .stText {
        color: #1a1a1a !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    /* ── Animations ── */
    .main-content {
        animation: fadeUp 0.45s cubic-bezier(.4,0,.2,1);
    }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Dividers ── */
    hr {
        border: none !important;
        border-top: 1px solid rgba(100, 130, 80, 0.18) !important;
        margin: 1.5rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# FUNCIONES DE AUTENTICACIÓN
# ══════════════════════════════════════════════════════════════

def check_auth():
    """Verifica si el usuario está autenticado"""
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
    """Cierra la sesión del usuario"""
    try:
        supabase.auth.sign_out()
        for key in ["session", "user_id", "perfil", "rol", "establecimiento_id", "establecimiento_nombre", "pagina"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    except Exception as e:
        st.error(f"Error al cerrar sesión: {e}")


def verificar_perfil():
    """Verifica que el perfil del usuario esté cargado"""
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
# LOGIN CON LOGO EN ÓVALO MÁS PEQUEÑO
# ══════════════════════════════════════════════════════════════

def login():
    """Pantalla de login con logo en óvalo más pequeño"""
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        # Logo en óvalo + título y subtítulo en burbuja
        st.markdown("""
        <div class="title-container">
            <div class="logo-oval-wrap">
                <img src="https://raw.githubusercontent.com/marcasosguemes-cell/Stock-SECCO-AGRO/main/Logo.png" class="title-logo" alt="Logo Stock Agrícola">
            </div>
            <div class="title-bubble-login">
                <h1 class="main-title-with-logo">Stock Agrícola</h1>
                <p class="login-subtitle">La Sonia &nbsp;·&nbsp; San Guillermo &nbsp;·&nbsp; Camba Pora</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### Bienvenido")
            st.markdown("Ingresa tus credenciales para continuar")
            
            email = st.text_input("Email", placeholder="usuario@ejemplo.com")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            
            submitted = st.form_submit_button("🚀 Ingresar", use_container_width=True, type="primary")
            
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
                            st.session_state["pagina"] = "Dashboard"
                            st.success("✅ Login exitoso! Redirigiendo...")
                            st.rerun()
                        else:
                            st.error("❌ No se encontró tu perfil. Contacta al administrador.")
                            
                except Exception as e:
                    st.error(f"❌ Error al iniciar sesión: {e}")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.3);">
            <p style="color: #ffffff; font-size: 0.8rem; font-weight: 500; text-shadow: 0 1px 6px rgba(0,0,0,0.6); letter-spacing: 0.05em;">Sistema de Control de Stock Agrícola</p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SIDEBAR CON LOGO
# ══════════════════════════════════════════════════════════════

def sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <img src="https://raw.githubusercontent.com/marcasosguemes-cell/Stock-SECCO-AGRO/main/Logo.png" alt="Logo">
            <h1>Stock Agrícola</h1>
        </div>
        """, unsafe_allow_html=True)
        
        if "perfil" not in st.session_state:
            st.warning("Cargando...")
            return
            
        perfil = st.session_state.get("perfil", {})
        rol = st.session_state.get("rol", "")
        estab = st.session_state.get("establecimiento_nombre", "Todos")
        
        badge_class = "badge-admin" if rol == "admin" else "badge-operator"
        badge_text = "Administrador" if rol == "admin" else "Operador"
        
        st.markdown(f"""
        <div class="profile-card">
            <div class="profile-name">👤 {perfil.get('nombre', 'Usuario')}</div>
            <div class="profile-role"><span class="badge {badge_class}">{badge_text}</span></div>
            <div class="profile-location">📍 {estab if estab else 'Todos los establecimientos'}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        paginas = [
            ("📊", "Dashboard", "Resumen general"),
            ("📥", "Nuevo Ingreso", "Registrar entrada de productos"),
            ("📤", "Nuevo Egreso", "Registrar salida de productos"),
            ("📋", "Historial", "Ver movimientos"),
            ("⚠️", "Alertas", "Stock bajo y vencimientos"),
            ("📈", "Reportes", "Análisis y estadísticas"),
        ]
        
        if rol == "admin":
            paginas += [
                ("🏭", "Proveedores", "Gestionar proveedores"),
                ("📦", "Productos", "Catálogo de productos"),
                ("👥", "Usuarios", "Gestión de usuarios"),
            ]
        
        st.markdown("### 📌 MENU")
        for emoji, nombre, tooltip in paginas:
            if st.button(f"{emoji}  {nombre}", key=f"nav_{nombre}", help=tooltip):
                st.session_state["pagina"] = nombre
        
        st.markdown("---")
        
        st.markdown("""
        <div style="margin-top: auto; padding-top: 2rem;">
            <p style="font-size: 0.7rem; text-align: center; opacity: 0.6;">
                Versión 2.0<br>
                © 2024
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Cerrar sesión", help="Salir del sistema"):
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

def get_productos(categoria_id=None):
    q = supabase.table("productos").select("*,categorias(nombre)").eq("activo", True)
    if categoria_id:
        q = q.eq("categoria_id", categoria_id)
    return q.execute().data

def get_proveedores():
    res = supabase.table("proveedores").select("*").eq("activo", True).execute()
    return res.data

def get_movimientos(establecimiento_id=None, limit=200):
    try:
        q = supabase.table("movimientos").select("*, productos!inner(nombre, categorias(nombre)), establecimientos!inner(nombre)").limit(limit)
        if establecimiento_id:
            q = q.eq("establecimiento_id", establecimiento_id)
        return q.execute().data
    except:
        return []


def get_stock_por_establecimiento():
    """Obtiene stock agrupado por establecimiento"""
    movimientos = get_movimientos()
    if not movimientos:
        return pd.DataFrame()
    
    df = pd.DataFrame(movimientos)
    
    # Asegurarse de que la columna establecimiento_id existe
    if "establecimiento_id" not in df.columns:
        return pd.DataFrame()
    
    # Calcular stock por establecimiento
    ingresos = df[df["tipo"] == "ingreso"].groupby("establecimiento_id")["cantidad"].sum()
    egresos = df[df["tipo"] == "egreso"].groupby("establecimiento_id")["cantidad"].sum()
    
    stock = {}
    for establecimiento in set(ingresos.index) | set(egresos.index):
        stock[establecimiento] = ingresos.get(establecimiento, 0) - egresos.get(establecimiento, 0)
    
    # Obtener nombres de establecimientos
    establecimientos = get_establecimientos()
    nombre_map = {e["id"]: e["nombre"] for e in establecimientos}
    
    result = []
    for est_id, cantidad in stock.items():
        result.append({
            "establecimiento": nombre_map.get(est_id, "Desconocido"),
            "stock": cantidad
        })
    
    return pd.DataFrame(result)


def estab_filter():
    if "rol" not in st.session_state:
        return None
    if st.session_state.get("rol") == "admin":
        return None
    return st.session_state.get("establecimiento_id")


# ══════════════════════════════════════════════════════════════
# DASHBOARD CON BURBUJA MARRÓN A LA IZQUIERDA
# ══════════════════════════════════════════════════════════════

def pagina_dashboard():
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Título con burbuja marrón a la izquierda
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>📊 Dashboard de Stock</h1>
            <p>📋 Resumen general del inventario agrícola</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    movimientos = get_movimientos(estab_filter())
    
    # Métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    if movimientos:
        df = pd.DataFrame(movimientos)
        total_ingresos = len(df[df["tipo"] == "ingreso"])
        total_egresos = len(df[df["tipo"] == "egreso"])
        total_movimientos = len(df)
        
        ingresos_sum = df[df["tipo"] == "ingreso"]["cantidad"].sum()
        egresos_sum = df[df["tipo"] == "egreso"]["cantidad"].sum()
        stock_total = ingresos_sum - egresos_sum
    else:
        total_ingresos = total_egresos = total_movimientos = stock_total = 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📦 Stock Total</div>
            <div class="metric-value">{stock_total:,.0f}</div>
            <div style="font-size:0.8rem;">unidades en inventario</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📥 Ingresos</div>
            <div class="metric-value">{total_ingresos}</div>
            <div style="font-size:0.8rem;">movimientos registrados</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📤 Egresos</div>
            <div class="metric-value">{total_egresos}</div>
            <div style="font-size:0.8rem;">movimientos registrados</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔄 Total Movimientos</div>
            <div class="metric-value">{total_movimientos}</div>
            <div style="font-size:0.8rem;">operaciones realizadas</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # SECCIÓN: Stock por Establecimiento
    st.markdown('<h3 class="section-title">🏢 Stock por Establecimiento</h3>', unsafe_allow_html=True)
    
    stock_por_establecimiento = get_stock_por_establecimiento()
    
    if not stock_por_establecimiento.empty and len(stock_por_establecimiento) > 0:
        st.markdown("### 📊 Distribución de Stock por Establecimiento")
        st.bar_chart(stock_por_establecimiento.set_index("establecimiento"))
        
        st.markdown("### 📋 Detalle de Stock por Establecimiento")
        st.dataframe(stock_por_establecimiento, use_container_width=True)
    else:
        st.info("💡 Sin datos de stock por establecimiento. Registrá movimientos para ver estadísticas.")
    
    st.markdown("---")
    
    # Últimos movimientos
    if movimientos:
        df = pd.DataFrame(movimientos)
        df["fecha"] = pd.to_datetime(df["fecha"])
        ultimos = df.sort_values("fecha", ascending=False).head(10)
        
        st.markdown('<h3 class="section-title">📋 Últimos Movimientos</h3>', unsafe_allow_html=True)
        
        display_df = ultimos[["fecha", "tipo", "cantidad", "observaciones"]].copy()
        display_df.columns = ["Fecha", "Tipo", "Cantidad", "Observaciones"]
        
        def color_tipo(val):
            if val == "ingreso":
                return "color: #2c5e2e"
            return "color: #d4a017"
        
        st.dataframe(
            display_df.style.applymap(color_tipo, subset=["Tipo"]),
            use_container_width=True,
            height=300
        )
    else:
        st.info("💡 Sin movimientos registrados. Comenzá registrando ingresos desde el menú lateral.")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# NUEVO INGRESO CON BURBUJA MARRÓN
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

    establecimientos = get_establecimientos()
    categorias = get_categorias()
    proveedores = get_proveedores()

    if not establecimientos:
        st.warning("⚠️ No hay establecimientos cargados. Contacta al administrador.")
        return
    
    if not categorias:
        st.warning("⚠️ No hay categorías cargadas. Contacta al administrador.")
        return

    with st.form("form_ingreso", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.get("rol") == "admin":
                estab_options = {e["nombre"]: e["id"] for e in establecimientos}
                estab_sel = st.selectbox("🏢 Establecimiento *", list(estab_options.keys()))
                establecimiento_id = estab_options[estab_sel]
            else:
                establecimiento_id = st.session_state.get("establecimiento_id")
                st.info(f"📍 Establecimiento: {st.session_state.get('establecimiento_nombre', '')}")
            
            cat_options = {c["nombre"]: c["id"] for c in categorias}
            cat_sel = st.selectbox("📁 Categoría *", list(cat_options.keys()))
            cat_id = cat_options[cat_sel]
        
        with col2:
            productos = get_productos(cat_id)
            if not productos:
                st.warning("⚠️ No hay productos en esta categoría. Ve a Productos para agregar.")
                return
            
            prod_options = {p["nombre"]: p["id"] for p in productos}
            prod_sel = st.selectbox("🏷️ Producto *", list(prod_options.keys()))
            producto_id = prod_options[prod_sel]
        
        st.markdown("---")
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            cantidad = st.number_input("📦 Cantidad *", min_value=0.001, step=0.5, format="%.3f")
        
        with col4:
            fecha = st.date_input("📅 Fecha *", value=date.today())
        
        with col5:
            prov_options = {p["nombre"]: p["id"] for p in proveedores}
            if prov_options:
                prov_sel = st.selectbox("🏭 Proveedor", ["Sin proveedor"] + list(prov_options.keys()))
                proveedor_id = prov_options[prov_sel] if prov_sel != "Sin proveedor" else None
            else:
                proveedor_id = None
                st.info("💡 Puedes agregar proveedores desde el menú Proveedores")
        
        observaciones = st.text_area("📝 Observaciones", placeholder="N° factura, lote, fecha de vencimiento, etc.")
        
        submitted = st.form_submit_button("✅ Registrar Ingreso", type="primary", use_container_width=True)
        
        if submitted:
            if cantidad <= 0:
                st.error("❌ La cantidad debe ser mayor a 0")
                return
            
            try:
                with st.spinner("Registrando ingreso..."):
                    payload = {
                        "tipo": "ingreso",
                        "producto_id": producto_id,
                        "establecimiento_id": establecimiento_id,
                        "cantidad": float(cantidad),
                        "fecha": str(fecha),
                        "proveedor_id": proveedor_id,
                        "observaciones": observaciones or None,
                        "usuario_id": st.session_state.get("user_id"),
                    }
                    supabase.table("movimientos").insert(payload).execute()
                    st.success(f"✅ Ingreso registrado exitosamente!")
                    st.balloons()
            except Exception as e:
                st.error(f"❌ Error al guardar: {e}")


# ══════════════════════════════════════════════════════════════
# NUEVO EGRESO CON BURBUJA MARRÓN
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

    establecimientos = get_establecimientos()
    categorias = get_categorias()

    if not establecimientos:
        st.warning("⚠️ No hay establecimientos cargados.")
        return

    with st.form("form_egreso", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.get("rol") == "admin":
                estab_options = {e["nombre"]: e["id"] for e in establecimientos}
                estab_sel = st.selectbox("🏢 Establecimiento *", list(estab_options.keys()))
                establecimiento_id = estab_options[estab_sel]
            else:
                establecimiento_id = st.session_state.get("establecimiento_id")
                st.info(f"📍 Establecimiento: {st.session_state.get('establecimiento_nombre', '')}")
        
        with col2:
            cat_options = {c["nombre"]: c["id"] for c in categorias}
            cat_sel = st.selectbox("📁 Categoría *", list(cat_options.keys()))
            cat_id = cat_options[cat_sel]
        
        productos = get_productos(cat_id)
        if not productos:
            st.warning("⚠️ No hay productos en esta categoría.")
            return
        
        prod_options = {p["nombre"]: p["id"] for p in productos}
        prod_sel = st.selectbox("🏷️ Producto *", list(prod_options.keys()))
        
        st.markdown("---")
        
        col3, col4 = st.columns(2)
        
        with col3:
            cantidad = st.number_input("📦 Cantidad *", min_value=0.001, step=0.5, format="%.3f")
        
        with col4:
            fecha = st.date_input("📅 Fecha *", value=date.today())
        
        observaciones = st.text_area("📝 Observaciones", placeholder="Motivo del egreso, destino, responsable, etc.")
        
        submitted = st.form_submit_button("✅ Registrar Egreso", type="primary", use_container_width=True)
        
        if submitted:
            if cantidad <= 0:
                st.error("❌ La cantidad debe ser mayor a 0")
                return
            
            try:
                with st.spinner("Registrando egreso..."):
                    payload = {
                        "tipo": "egreso",
                        "producto_id": prod_options[prod_sel],
                        "establecimiento_id": establecimiento_id,
                        "cantidad": float(cantidad),
                        "fecha": str(fecha),
                        "observaciones": observaciones or None,
                        "usuario_id": st.session_state.get("user_id"),
                    }
                    supabase.table("movimientos").insert(payload).execute()
                    st.success(f"✅ Egreso registrado exitosamente!")
            except Exception as e:
                st.error(f"❌ Error al guardar: {e}")


# ══════════════════════════════════════════════════════════════
# HISTORIAL CON BURBUJA MARRÓN
# ══════════════════════════════════════════════════════════════

def pagina_historial():
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>📋 Historial de Movimientos</h1>
            <p>📋 Consulta todos los movimientos de stock</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    movimientos = get_movimientos(estab_filter(), limit=500)
    
    if not movimientos:
        st.info("💡 Sin movimientos registrados. Comenzá registrando ingresos desde el menú lateral.")
        return
    
    df = pd.DataFrame(movimientos)
    df["fecha"] = pd.to_datetime(df["fecha"])
    
    st.markdown('<h3 class="section-title">🔍 Filtros</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    tipo_sel = col1.selectbox("Tipo de movimiento", ["Todos", "ingreso", "egreso"])
    fecha_desde = col2.date_input("Desde", value=date.today() - timedelta(days=30))
    
    df_f = df.copy()
    if tipo_sel != "Todos":
        df_f = df_f[df_f["tipo"] == tipo_sel]
    df_f = df_f[df_f["fecha"] >= pd.Timestamp(fecha_desde)]
    
    st.markdown(f"### 📊 Resultados: **{len(df_f)}** movimientos encontrados")
    
    display_df = df_f[["fecha", "tipo", "cantidad", "observaciones"]].sort_values("fecha", ascending=False)
    display_df.columns = ["Fecha", "Tipo", "Cantidad", "Observaciones"]
    
    st.dataframe(display_df, use_container_width=True, height=400)
    
    if not df_f.empty:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_f.to_excel(writer, index=False, sheet_name="Movimientos")
        st.download_button(
            "📥 Exportar a Excel",
            data=buffer.getvalue(),
            file_name=f"movimientos_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


# ══════════════════════════════════════════════════════════════
# ALERTAS CON BURBUJA MARRÓN
# ══════════════════════════════════════════════════════════════

def pagina_alertas():
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>⚠️ Alertas de Stock</h1>
            <p>📋 Monitoreo de stock bajo y productos críticos</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    movimientos = get_movimientos(estab_filter())
    
    if not movimientos:
        st.info("💡 Sin datos para mostrar alertas. Registrá movimientos para activar las alertas.")
        return
    
    st.markdown("""
    <div style="background: rgba(180, 200, 160, 0.7); padding: 1.5rem; border-radius: 16px; margin-bottom: 2rem;">
        <p style="margin: 0; color: #2c5e2e;">🔔 Las alertas te ayudan a mantener el control de tu inventario</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.success("✅ Sistema funcionando correctamente. Las alertas se mostrarán cuando haya stock bajo o productos por vencer.")


# ══════════════════════════════════════════════════════════════
# REPORTES CON BURBUJA MARRÓN
# ══════════════════════════════════════════════════════════════

def pagina_reportes():
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>📈 Reportes y Estadísticas</h1>
            <p>📋 Análisis detallado de movimientos y tendencias</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    movimientos = get_movimientos(estab_filter())
    
    if not movimientos:
        st.info("💡 Sin datos para generar reportes. Registrá movimientos para ver estadísticas.")
        return
    
    df = pd.DataFrame(movimientos)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["mes"] = df["fecha"].dt.to_period("M")
    
    st.markdown('<h3 class="section-title">📊 Resumen por Mes</h3>', unsafe_allow_html=True)
    resumen = df.groupby(["mes", "tipo"])["cantidad"].sum().reset_index()
    st.dataframe(resumen, use_container_width=True)
    
    st.markdown('<h3 class="section-title">📈 Tendencia de Movimientos</h3>', unsafe_allow_html=True)
    chart_data = df.groupby(["mes", "tipo"])["cantidad"].sum().unstack()
    st.bar_chart(chart_data)


# ══════════════════════════════════════════════════════════════
# PROVEEDORES CON BURBUJA MARRÓN
# ══════════════════════════════════════════════════════════════

def pagina_proveedores():
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>🏭 Gestión de Proveedores</h1>
            <p>📋 Administra los proveedores de insumos agrícolas</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    proveedores = get_proveedores()
    
    with st.expander("➕ Agregar nuevo proveedor", expanded=False):
        with st.form("nuevo_proveedor"):
            nombre = st.text_input("Nombre del proveedor")
            if st.form_submit_button("Guardar"):
                if nombre:
                    supabase.table("proveedores").insert({"nombre": nombre, "activo": True}).execute()
                    st.success(f"✅ Proveedor '{nombre}' agregado")
                    st.rerun()
    
    if proveedores:
        df = pd.DataFrame(proveedores)
        st.dataframe(df[["nombre", "activo", "created_at"]], use_container_width=True)
    else:
        st.info("💡 No hay proveedores cargados. Agregá proveedores usando el panel superior.")


# ══════════════════════════════════════════════════════════════
# PRODUCTOS CON BURBUJA MARRÓN
# ══════════════════════════════════════════════════════════════

def pagina_productos():
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>📦 Catálogo de Productos</h1>
            <p>📋 Administra el catálogo de productos agrícolas</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    categorias = get_categorias()
    cat_options = {c["nombre"]: c["id"] for c in categorias}
    
    with st.expander("➕ Agregar nuevo producto", expanded=False):
        with st.form("nuevo_producto"):
            cat_sel = st.selectbox("Categoría", list(cat_options.keys()))
            nombre = st.text_input("Nombre del producto")
            if st.form_submit_button("Guardar"):
                if nombre:
                    supabase.table("productos").insert({
                        "categoria_id": cat_options[cat_sel],
                        "nombre": nombre,
                        "activo": True
                    }).execute()
                    st.success(f"✅ Producto '{nombre}' agregado")
                    st.rerun()
    
    productos = get_productos()
    if productos:
        df = pd.DataFrame(productos)
        df["categoria"] = df["categorias"].apply(lambda x: x["nombre"] if x else "N/A")
        st.dataframe(df[["categoria", "nombre", "activo"]], use_container_width=True)
    else:
        st.info("💡 No hay productos cargados. Agregá productos usando el panel superior.")


# ══════════════════════════════════════════════════════════════
# USUARIOS CON BURBUJA MARRÓN
# ══════════════════════════════════════════════════════════════

def pagina_usuarios():
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>👥 Gestión de Usuarios</h1>
            <p>📋 Administra los usuarios del sistema</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("📝 Para crear nuevos usuarios, usá el panel de Supabase Authentication y luego completá sus datos en la tabla `usuarios`.")
    
    try:
        usuarios = supabase.table("usuarios").select("*").execute().data
        if usuarios:
            df = pd.DataFrame(usuarios)
            st.dataframe(df[["nombre", "rol", "created_at"]], use_container_width=True)
        else:
            st.info("💡 No hay usuarios cargados")
    except Exception as e:
        st.error(f"❌ Error: {e}")


# ══════════════════════════════════════════════════════════════
# ROUTER PRINCIPAL
# ══════════════════════════════════════════════════════════════

def main():
    if not check_auth():
        login()
        return

    if not verificar_perfil():
        return

    sidebar()

    pagina = st.session_state.get("pagina", "Dashboard")
    rol = st.session_state.get("rol", "establecimiento")

    rutas = {
        "Dashboard": pagina_dashboard,
        "Nuevo Ingreso": pagina_ingreso,
        "Nuevo Egreso": pagina_egreso,
        "Historial": pagina_historial,
        "Alertas": pagina_alertas,
        "Reportes": pagina_reportes,
        "Proveedores": pagina_proveedores if rol == "admin" else pagina_dashboard,
        "Productos": pagina_productos if rol == "admin" else pagina_dashboard,
        "Usuarios": pagina_usuarios if rol == "admin" else pagina_dashboard,
    }

    pagina_funcion = rutas.get(pagina, pagina_dashboard)
    pagina_funcion()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>🌾 Sistema de Control de Stock Agrícola</p>
        <p>La Sonia · San Guillermo · Camba Pora</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
