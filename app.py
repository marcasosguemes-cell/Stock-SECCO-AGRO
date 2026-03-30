"""
SISTEMA DE CONTROL DE STOCK AGRÍCOLA
App principal Streamlit — La Sonia / San Guillermo / Camba Pora
Versión con gráficos interactivos y filtros dinámicos
"""

import streamlit as st
from supabase import create_client, Client
from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
# CSS MEJORADO - Estilo moderno
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

    /* ── Sidebar header con logo en óvalo blanco ── */
    .sidebar-header {
        text-align: center;
        padding: 1.6rem 0 1.2rem 0;
        border-bottom: 1px solid rgba(212, 160, 23, 0.35);
        margin-bottom: 1.4rem;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .sidebar-logo-oval {
        background: #f7f3e8;
        border: 2px solid rgba(212, 160, 23, 0.5);
        border-radius: 50%;
        width: 100px;
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.25), 0 1px 0 rgba(255,255,255,0.6) inset;
        margin-bottom: 12px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .sidebar-logo-oval:hover {
        transform: scale(1.03);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }

    .sidebar-logo {
        width: 80% !important;
        height: auto !important;
        object-fit: contain !important;
        display: block;
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

    /* ── Título login con logo GRANDE ── */
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

    .logo-oval-wrap:hover {
        transform: scale(1.02);
        box-shadow: 0 14px 42px rgba(0,0,0,0.35);
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

    /* ── Title bubbles ── */
    .title-bubble {
        background: linear-gradient(135deg, #c8a060 0%, #b8905a 100%);
        border-radius: 18px;
        padding: 1rem 2.2rem;
        display: inline-block;
        box-shadow: 0 4px 18px rgba(100, 70, 30, 0.18);
        text-align: center;
        margin-bottom: 1.4rem;
    }

    .title-bubble h1 {
        margin: 0;
        font-family: 'Playfair Display', serif !important;
        font-size: 1.75rem !important;
        color: #2a4a1a !important;
        font-weight: 700;
    }

    .title-bubble p {
        margin: 0.35rem 0 0 0;
        color: #3d5a2a !important;
        font-size: 0.88rem;
    }

    /* ── Metric cards con animación ── */
    .metric-card {
        background: linear-gradient(145deg, rgba(195, 215, 175, 0.9) 0%, rgba(175, 200, 155, 0.95) 100%) !important;
        border: 1px solid rgba(100, 130, 80, 0.3);
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(50, 90, 50, 0.1);
        transition: all 0.3s cubic-bezier(.4,0,.2,1);
        text-align: center !important;
        padding: 1.2rem 1rem;
        cursor: pointer;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 28px rgba(50, 90, 50, 0.2);
    }

    .metric-value {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.6rem !important;
        font-weight: 700;
        color: #173a17 !important;
        margin: 0.4rem 0;
    }

    .metric-label {
        font-size: 0.75rem !important;
        color: #2a4a2a !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
    }

    .trend-up {
        color: #2c5e2e;
        font-size: 0.8rem;
    }

    .trend-down {
        color: #d4a017;
        font-size: 0.8rem;
    }

    /* ── Filtros panel ── */
    .filters-panel {
        background: rgba(195, 215, 175, 0.5);
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(100, 130, 80, 0.2);
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #2c5e2e, #3a7040) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px;
        padding: 0.55rem 1.3rem;
        font-weight: 600;
        transition: all 0.25s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(44, 94, 46, 0.38);
    }

    /* ── Forms ── */
    [data-testid="stForm"] {
        background: rgba(195, 215, 175, 0.45) !important;
        border-radius: 18px;
        padding: 1.2rem;
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
    }

    /* ── Animations ── */
    .main-content {
        animation: fadeUp 0.45s cubic-bezier(.4,0,.2,1);
    }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }

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
        for key in ["session", "user_id", "perfil", "rol", "establecimiento_id", "establecimiento_nombre", "pagina"]:
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
                            st.session_state["pagina"] = "Dashboard"
                            st.success("✅ Login exitoso!")
                            st.rerun()
                        else:
                            st.error("❌ No se encontró tu perfil.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")


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
        estab = st.session_state.get("establecimiento_nombre", "Todos")
        
        badge_class = "badge-admin" if rol == "admin" else "badge-operator"
        badge_text = "Administrador" if rol == "admin" else "Operador"
        
        st.markdown(f"""
        <div class="profile-card">
            <div class="profile-name">👤 {perfil.get('nombre', 'Usuario')}</div>
            <div class="profile-role"><span style="background: {'#c89010' if rol=='admin' else '#2c5e2e'}; padding: 0.22rem 0.7rem; border-radius: 20px; font-size:0.7rem;">{badge_text}</span></div>
            <div class="profile-location">📍 {estab if estab else 'Todos los establecimientos'}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        paginas = [
            ("📊", "Dashboard", "Resumen general"),
            ("📥", "Nuevo Ingreso", "Registrar entrada"),
            ("📤", "Nuevo Egreso", "Registrar salida"),
            ("📋", "Historial", "Ver movimientos"),
            ("⚠️", "Alertas", "Stock bajo"),
            ("📈", "Reportes", "Estadísticas"),
        ]
        
        if rol == "admin":
            paginas += [
                ("🏭", "Proveedores", "Gestionar proveedores"),
                ("📦", "Productos", "Catálogo"),
                ("👥", "Usuarios", "Gestión"),
            ]
        
        st.markdown("### 📌 MENU")
        for emoji, nombre, tooltip in paginas:
            if st.button(f"{emoji}  {nombre}", key=f"nav_{nombre}", help=tooltip):
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

def get_productos(categoria_id=None):
    q = supabase.table("productos").select("*,categorias(nombre)").eq("activo", True)
    if categoria_id:
        q = q.eq("categoria_id", categoria_id)
    return q.execute().data

def get_proveedores():
    res = supabase.table("proveedores").select("*").eq("activo", True).execute()
    return res.data

def get_movimientos(establecimiento_id=None, limit=1000):
    try:
        q = supabase.table("movimientos").select("*, productos!inner(nombre, categorias(nombre)), establecimientos!inner(nombre)").limit(limit)
        if establecimiento_id:
            q = q.eq("establecimiento_id", establecimiento_id)
        return q.execute().data
    except:
        return []


def get_stock_por_producto():
    movimientos = get_movimientos()
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
    
    stock = {}
    for prod_id in set(ingresos.index) | set(egresos.index):
        stock[prod_id] = ingresos.get(prod_id, 0) - egresos.get(prod_id, 0)
    
    result = []
    for prod_id, cantidad in stock.items():
        result.append({
            "producto": nombre_map.get(prod_id, "Desconocido"),
            "categoria": categoria_map.get(prod_id, "Sin categoría"),
            "stock": cantidad
        })
    
    return pd.DataFrame(result).sort_values("stock", ascending=False)


def get_movimientos_con_filtros(establecimiento_id=None, fecha_desde=None, fecha_hasta=None, tipo=None, producto_id=None):
    movimientos = get_movimientos(establecimiento_id, limit=2000)
    if not movimientos:
        return []
    
    df = pd.DataFrame(movimientos)
    df["fecha"] = pd.to_datetime(df["fecha"])
    
    if fecha_desde:
        df = df[df["fecha"] >= pd.Timestamp(fecha_desde)]
    if fecha_hasta:
        df = df[df["fecha"] <= pd.Timestamp(fecha_hasta)]
    if tipo and tipo != "Todos":
        df = df[df["tipo"] == tipo]
    if producto_id:
        df = df[df["producto_id"] == producto_id]
    
    return df.to_dict("records")


def estab_filter():
    if "rol" not in st.session_state:
        return None
    if st.session_state.get("rol") == "admin":
        return None
    return st.session_state.get("establecimiento_id")


# ══════════════════════════════════════════════════════════════
# DASHBOARD CON GRÁFICOS INTERACTIVOS Y FILTROS DINÁMICOS
# ══════════════════════════════════════════════════════════════

def pagina_dashboard():
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>📊 Dashboard de Stock</h1>
            <p>📋 Análisis interactivo del inventario agrícola</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ── FILTROS DINÁMICOS ──────────────────────────────────────────
    st.markdown('<div class="filters-panel">', unsafe_allow_html=True)
    st.markdown("### 🔍 Filtros Dinámicos")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        # Filtro de fecha
        fecha_desde = st.date_input("📅 Desde", value=date.today() - timedelta(days=90))
        fecha_hasta = st.date_input("📅 Hasta", value=date.today())
    
    with col_f2:
        # Filtro de tipo de movimiento
        tipo_filtro = st.selectbox("📌 Tipo de Movimiento", ["Todos", "ingreso", "egreso"])
    
    with col_f3:
        # Filtro de categoría (dinámico)
        categorias = get_categorias()
        cat_options = {c["nombre"]: c["id"] for c in categorias}
        cat_options["Todas"] = None
        cat_seleccionada = st.selectbox("📁 Categoría", list(cat_options.keys()))
        cat_id = cat_options[cat_seleccionada] if cat_seleccionada != "Todas" else None
        
        # Filtro de producto (depende de categoría)
        productos = get_productos(cat_id)
        prod_options = {p["nombre"]: p["id"] for p in productos}
        prod_options["Todos"] = None
        prod_seleccionado = st.selectbox("🏷️ Producto", list(prod_options.keys()))
        prod_id = prod_options[prod_seleccionado] if prod_seleccionado != "Todos" else None
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Obtener datos con filtros
    movimientos = get_movimientos_con_filtros(
        establecimiento_id=estab_filter(),
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        tipo=tipo_filtro if tipo_filtro != "Todos" else None,
        producto_id=prod_id
    )
    
    # ── MÉTRICAS CON TENDENCIAS ─────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    
    if movimientos:
        df_mov = pd.DataFrame(movimientos)
        
        # Calcular métricas
        ingresos = df_mov[df_mov["tipo"] == "ingreso"]["cantidad"].sum() if "ingreso" in df_mov["tipo"].values else 0
        egresos = df_mov[df_mov["tipo"] == "egreso"]["cantidad"].sum() if "egreso" in df_mov["tipo"].values else 0
        stock_total = ingresos - egresos
        total_movimientos = len(df_mov)
        
        # Calcular tendencias (comparar con período anterior)
        fecha_anterior_inicio = fecha_desde - timedelta(days=(fecha_hasta - fecha_desde).days)
        mov_anterior = get_movimientos_con_filtros(
            establecimiento_id=estab_filter(),
            fecha_desde=fecha_anterior_inicio,
            fecha_hasta=fecha_desde - timedelta(days=1),
            tipo=tipo_filtro if tipo_filtro != "Todos" else None,
            producto_id=prod_id
        )
        
        if mov_anterior:
            df_anterior = pd.DataFrame(mov_anterior)
            ingresos_ant = df_anterior[df_anterior["tipo"] == "ingreso"]["cantidad"].sum() if "ingreso" in df_anterior["tipo"].values else 0
            tendencia_ingresos = ((ingresos - ingresos_ant) / ingresos_ant * 100) if ingresos_ant > 0 else 0
        else:
            tendencia_ingresos = 0
        
        with col1:
            trend_class = "trend-up" if tendencia_ingresos >= 0 else "trend-down"
            trend_icon = "↑" if tendencia_ingresos >= 0 else "↓"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📦 Stock Total</div>
                <div class="metric-value">{stock_total:,.0f}</div>
                <div class="{trend_class}">{trend_icon} {abs(tendencia_ingresos):.1f}% vs período anterior</div>
                <div style="font-size:0.7rem;">unidades en inventario</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📥 Ingresos</div>
                <div class="metric-value">{ingresos:,.0f}</div>
                <div style="font-size:0.7rem;">unidades ingresadas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📤 Egresos</div>
                <div class="metric-value">{egresos:,.0f}</div>
                <div style="font-size:0.7rem;">unidades egresadas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">🔄 Movimientos</div>
                <div class="metric-value">{total_movimientos}</div>
                <div style="font-size:0.7rem;">operaciones en el período</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        for col in [col1, col2, col3, col4]:
            with col:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">0</div>
                    <div class="metric-label">Sin datos</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ── GRÁFICO 1: Evolución de Stock (línea temporal) ─────────────────
    if movimientos:
        df_mov = pd.DataFrame(movimientos)
        df_mov["fecha"] = pd.to_datetime(df_mov["fecha"])
        
        # Calcular stock acumulado por día
        df_mov["stock_diario"] = df_mov.apply(lambda x: x["cantidad"] if x["tipo"] == "ingreso" else -x["cantidad"], axis=1)
        df_daily = df_mov.groupby(df_mov["fecha"].dt.date)["stock_diario"].sum().reset_index()
        df_daily.columns = ["fecha", "movimiento_diario"]
        df_daily["stock_acumulado"] = df_daily["movimiento_diario"].cumsum()
        
        fig_evolucion = px.line(
            df_daily, 
            x="fecha", 
            y="stock_acumulado",
            title="📈 Evolución del Stock en el Tiempo",
            labels={"fecha": "Fecha", "stock_acumulado": "Stock Total (unidades)"},
            template="plotly_white",
            line_shape="spline"
        )
        fig_evolucion.update_traces(line=dict(color="#2c5e2e", width=3))
        fig_evolucion.update_layout(
            height=400,
            hovermode="x unified",
            plot_bgcolor="rgba(195, 215, 175, 0.2)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_evolucion, use_container_width=True)
        
        # ── GRÁFICO 2: Distribución por Categoría (torta) ─────────────────
        stock_por_categoria = get_stock_por_producto()
        if not stock_por_categoria.empty:
            stock_cat = stock_por_categoria.groupby("categoria")["stock"].sum().reset_index()
            
            fig_torta = px.pie(
                stock_cat,
                values="stock",
                names="categoria",
                title="🥧 Distribución de Stock por Categoría",
                template="plotly_white",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_torta.update_traces(textposition="inside", textinfo="percent+label")
            fig_torta.update_layout(height=450)
            st.plotly_chart(fig_torta, use_container_width=True)
        
        # ── GRÁFICO 3: Top 10 Productos con Mayor Stock (barras) ──────────
        st.markdown("---")
        stock_productos = get_stock_por_producto()
        if not stock_productos.empty:
            top_productos = stock_productos.head(10)
            
            fig_barras = px.bar(
                top_productos,
                x="producto",
                y="stock",
                title="📊 Top 10 Productos con Mayor Stock",
                labels={"producto": "Producto", "stock": "Stock (unidades)"},
                template="plotly_white",
                color="stock",
                color_continuous_scale="Greens"
            )
            fig_barras.update_layout(
                height=450,
                xaxis_tickangle=-45,
                plot_bgcolor="rgba(195, 215, 175, 0.2)"
            )
            st.plotly_chart(fig_barras, use_container_width=True)
        
        # ── GRÁFICO 4: Movimientos por Mes (barras agrupadas) ────────────
        df_mov["mes"] = df_mov["fecha"].dt.to_period("M").astype(str)
        movimientos_mensuales = df_mov.groupby(["mes", "tipo"])["cantidad"].sum().reset_index()
        
        fig_mensual = px.bar(
            movimientos_mensuales,
            x="mes",
            y="cantidad",
            color="tipo",
            title="📅 Movimientos Mensuales por Tipo",
            labels={"mes": "Mes", "cantidad": "Cantidad (unidades)", "tipo": "Tipo"},
            template="plotly_white",
            barmode="group",
            color_discrete_map={"ingreso": "#2c5e2e", "egreso": "#d4a017"}
        )
        fig_mensual.update_layout(height=450, plot_bgcolor="rgba(195, 215, 175, 0.2)")
        st.plotly_chart(fig_mensual, use_container_width=True)
        
    else:
        st.info("💡 Sin datos en el período seleccionado. Ajustá los filtros o registrá movimientos.")
    
    st.markdown('</div>', unsafe_allow_html=True)


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

    establecimientos = get_establecimientos()
    categorias = get_categorias()
    proveedores = get_proveedores()

    if not establecimientos:
        st.warning("⚠️ No hay establecimientos cargados.")
        return
    
    if not categorias:
        st.warning("⚠️ No hay categorías cargadas.")
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
                st.warning("⚠️ No hay productos en esta categoría.")
                return
            
            prod_options = {p["nombre"]: p["id"] for p in productos}
            prod_sel = st.selectbox("🏷️ Producto *", list(prod_options.keys()))
            producto_id = prod_options[prod_sel]
        
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

    # Filtros dinámicos para historial
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        tipo_filtro = st.selectbox("Tipo de movimiento", ["Todos", "ingreso", "egreso"])
    with col_f2:
        fecha_desde = st.date_input("Desde", value=date.today() - timedelta(days=30))
    with col_f3:
        fecha_hasta = st.date_input("Hasta", value=date.today())
    
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
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha", ascending=False)
    
    st.markdown(f"### 📊 Resultados: **{len(df)}** movimientos encontrados")
    
    display_df = df[["fecha", "tipo", "cantidad", "observaciones"]].copy()
    display_df.columns = ["Fecha", "Tipo", "Cantidad", "Observaciones"]
    
    st.dataframe(display_df, use_container_width=True, height=400)
    
    if not df.empty:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Movimientos")
        st.download_button(
            "📥 Exportar a Excel",
            data=buffer.getvalue(),
            file_name=f"movimientos_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


# ══════════════════════════════════════════════════════════════
# ALERTAS
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
    
    stock_productos = get_stock_por_producto()
    
    if stock_productos.empty:
        st.info("💡 Sin datos para mostrar alertas.")
        return
    
    # Productos con stock bajo (menos de 100 unidades)
    stock_bajo = stock_productos[stock_productos["stock"] < 100]
    stock_critico = stock_productos[stock_productos["stock"] < 50]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⚠️ Stock Bajo</div>
            <div class="metric-value">{len(stock_bajo)}</div>
            <div>productos con menos de 100 unidades</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔴 Stock Crítico</div>
            <div class="metric-value">{len(stock_critico)}</div>
            <div>productos con menos de 50 unidades</div>
        </div>
        """, unsafe_allow_html=True)
    
    if not stock_bajo.empty:
        st.markdown("---")
        st.markdown("### 📋 Productos con Stock Bajo")
        st.dataframe(stock_bajo, use_container_width=True)
    else:
        st.success("✅ Todos los productos tienen stock suficiente.")


# ══════════════════════════════════════════════════════════════
# REPORTES
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
    
    movimientos = get_movimientos(estab_filter(), limit=2000)
    
    if not movimientos:
        st.info("💡 Sin datos para generar reportes.")
        return
    
    df = pd.DataFrame(movimientos)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    df["año"] = df["fecha"].dt.year
    
    # Selector de año
    años = sorted(df["año"].unique())
    año_seleccionado = st.selectbox("📅 Seleccionar año", años, index=len(años)-1)
    
    df_año = df[df["año"] == año_seleccionado]
    
    st.markdown(f"### 📊 Resumen {año_seleccionado}")
    
    resumen = df_año.groupby(["mes", "tipo"])["cantidad"].sum().reset_index()
    st.dataframe(resumen, use_container_width=True)
    
    st.markdown("### 📈 Tendencia de Movimientos")
    chart_data = df_año.groupby(["mes", "tipo"])["cantidad"].sum().unstack()
    st.bar_chart(chart_data)
    
    # Exportar
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_año.to_excel(writer, index=False, sheet_name=f"Reporte_{año_seleccionado}")
    st.download_button(
        "📥 Exportar reporte completo",
        data=buffer.getvalue(),
        file_name=f"reporte_stock_{año_seleccionado}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# ══════════════════════════════════════════════════════════════
# ADMIN: PROVEEDORES, PRODUCTOS, USUARIOS
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
        st.info("💡 No hay proveedores cargados.")


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
        st.info("💡 No hay productos cargados.")


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
    
    st.markdown("""
    <div class="footer">
        <p>🌾 Sistema de Control de Stock Agrícola</p>
        <p>La Sonia · San Guillermo · Camba Pora</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
