"""
SISTEMA DE CONTROL DE STOCK AGRÍCOLA
App principal Streamlit — La Sonia / San Guillermo / Camba Pora
Versión con logo más grande y burbujas marrón en Dashboard
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
# CSS MEJORADO
# ══════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* Fondo con tu imagen - MODO MARCA DE AGUA */
    .stApp {
        background-image: url('https://raw.githubusercontent.com/marcasosguemes-cell/Stock-SECCO-AGRO/main/Fondo.PNG') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        background-repeat: no-repeat !important;
    }
    
    /* Capa blanca MUY intensa para que sea como marca de agua */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.96);
        z-index: -1;
        pointer-events: none;
    }
    
    /* Sidebar con color AZUL MARINO */
    [data-testid="stSidebar"] {
        background: rgba(25, 35, 55, 0.95) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(212, 160, 23, 0.3);
    }
    
    [data-testid="stSidebar"] * {
        color: #f0f8f0 !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stSidebar"] .stButton button {
        background: rgba(212, 160, 23, 0.15);
        border: 1px solid rgba(212, 160, 23, 0.3);
        width: 100%;
        text-align: left;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        margin: 6px 0;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(212, 160, 23, 0.35);
        border-color: #d4a017;
        transform: translateX(4px);
    }
    
    /* Cards y formularios - VERDE OLIVA CLARO */
    .metric-card, [data-testid="stForm"], .profile-card {
        background: rgba(180, 200, 160, 0.95) !important;
        border: 1px solid rgba(100, 120, 80, 0.3);
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        text-align: center !important;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
        background: rgba(190, 210, 170, 0.98) !important;
    }
    
    /* Texto en tarjetas */
    .metric-card, .metric-card * {
        color: #1a2a1a !important;
        text-align: center !important;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #2c5e2e !important;
        margin: 0.5rem 0;
        text-align: center !important;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #3a5a2a !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
        text-align: center !important;
    }
    
    /* BURBUJAS MARRÓN CLARO para títulos */
    .title-bubble {
        background: rgba(180, 140, 100, 0.95);
        border: 1px solid rgba(120, 90, 60, 0.4);
        border-radius: 30px;
        padding: 0.5rem 2rem;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .title-bubble:hover {
        transform: translateY(-2px);
        background: rgba(190, 150, 110, 0.98);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .title-bubble h1 {
        margin: 0;
        color: #f5e6d3 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        font-weight: 600;
        font-size: 2rem;
    }
    
    /* Contenedor del título con logo (login) - LOGO MÁS GRANDE */
    .title-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin-bottom: 0.5rem;
        flex-wrap: wrap;
        position: relative;
    }
    
    .title-logo {
        width: 100px;
        height: auto;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.2));
    }
    
    /* Títulos de página alineados a la izquierda */
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1a4a1a, #2c5e2e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 0.5rem 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        text-align: left !important;
    }
    
    /* Título con logo para login */
    .main-title-with-logo {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1a4a1a, #2c5e2e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1a4a1a !important;
        border-left: 4px solid #d4a017;
        padding-left: 1rem;
        margin: 1.5rem 0 1rem 0;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.05);
        text-align: left !important;
    }
    
    /* Texto normal */
    p, span, div, label, .stMarkdown, .stText, .stNumberInput, .stSelectbox, .stDateInput {
        color: #1a1a1a !important;
    }
    
    /* Botones */
    .stButton > button {
        background: linear-gradient(135deg, #2c5e2e, #3d7a3f) !important;
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(44, 94, 46, 0.4);
    }
    
    /* Tablas */
    .stDataFrame {
        background: rgba(180, 200, 160, 0.95);
        border-radius: 16px;
        padding: 0.5rem;
    }
    
    .stDataFrame * {
        color: #1a2a1a !important;
    }
    
    /* Alertas */
    .stAlert {
        background: rgba(180, 200, 160, 0.95) !important;
        border-radius: 12px;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    
    .badge-admin {
        background: linear-gradient(135deg, #d4a017, #b8860b);
        color: white !important;
    }
    
    .badge-operator {
        background: linear-gradient(135deg, #2c5e2e, #3d7a3f);
        color: white !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #4a5b4a !important;
        font-size: 0.8rem;
        border-top: 1px solid rgba(100, 120, 80, 0.3);
        margin-top: 2rem;
        background: rgba(180, 200, 160, 0.9);
        border-radius: 16px;
    }
    
    /* Perfil card en sidebar */
    .profile-card {
        text-align: center;
        padding: 1rem;
        margin: 1rem 0;
        background: rgba(180, 200, 160, 0.25) !important;
        border-radius: 16px;
    }
    
    .profile-name {
        font-size: 1.1rem;
        font-weight: bold;
        color: #f0f8f0 !important;
    }
    
    .sidebar-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #d4a017;
        margin-bottom: 1.5rem;
    }
    
    .sidebar-header h1 {
        font-size: 1.3rem;
        margin: 0;
        color: #d4a017 !important;
    }
    
    /* Animación */
    .main-content {
        animation: fadeIn 0.5s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Inputs */
    input, textarea, select {
        color: #1a2a1a !important;
        background-color: rgba(240, 248, 220, 0.9) !important;
        border-radius: 10px !important;
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
# LOGIN CON LOGO MÁS GRANDE
# ══════════════════════════════════════════════════════════════

def login():
    """Pantalla de login con logo grande"""
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        # Título con logo más grande
        st.markdown("""
        <div class="title-container">
            <img src="https://raw.githubusercontent.com/marcasosguemes-cell/Stock-SECCO-AGRO/main/Logo.png" class="title-logo" alt="Logo Stock Agrícola">
            <h1 class="main-title-with-logo">Stock Agrícola</h1>
        </div>
        <p style="text-align: center; color: #4a5b4a; font-size: 1rem; margin-top: 0.5rem;">La Sonia · San Guillermo · Camba Pora</p>
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
        <div style="text-align: center; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #c0d0b0;">
            <p style="color: #6b8f71; font-size: 0.75rem;">Sistema de Control de Stock Agrícola</p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SIDEBAR CON LOGO
# ══════════════════════════════════════════════════════════════

def sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                <img src="https://raw.githubusercontent.com/marcasosguemes-cell/Stock-SECCO-AGRO/main/Logo.png" style="width: 35px; height: auto; border-radius: 8px;" alt="Logo">
                <h1 style="font-size: 1.3rem; margin: 0; color: #d4a017 !important;">Stock Agrícola</h1>
            </div>
            <p style="margin: 0; font-size: 0.8rem;">SECCO AGRO</p>
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
        
        st.markdown("### 📌 Navegación")
        for emoji, nombre, tooltip in paginas:
            if st.button(f"{emoji}  {nombre}", key=f"nav_{nombre}", help=tooltip):
                st.session_state["pagina"] = nombre
        
        st.markdown("---")
        
        st.markdown("""
        <div style="margin-top: auto; padding-top: 2rem;">
            <p style="font-size: 0.7rem; text-align: center; opacity: 0.6;">
                Versión 2.0<br>
                © 2024 SECCO AGRO
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


def estab_filter():
    if "rol" not in st.session_state:
        return None
    if st.session_state.get("rol") == "admin":
        return None
    return st.session_state.get("establecimiento_id")


# ══════════════════════════════════════════════════════════════
# DASHBOARD CON BURBUJA MARRÓN EN EL TÍTULO
# ══════════════════════════════════════════════════════════════

def pagina_dashboard():
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Título con burbuja marrón
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <div class="title-bubble">
            <h1>📊 Dashboard de Stock</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<p style="color: #6b8f71; margin-bottom: 2rem;">Resumen general del inventario agrícola</p>', unsafe_allow_html=True)

    movimientos = get_movimientos(estab_filter())
    
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
# NUEVO INGRESO, EGRESO, HISTORIAL, ALERTAS, REPORTES, ADMIN
# (Mantener las mismas funciones que en el código anterior)
# ══════════════════════════════════════════════════════════════

def pagina_ingreso():
    st.markdown('<h1 class="main-title">📥 Registrar Ingreso</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6b8f71; margin-bottom: 2rem;">Registra la entrada de productos al inventario</p>', unsafe_allow_html=True)

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


def pagina_egreso():
    st.markdown('<h1 class="main-title">📤 Registrar Egreso</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6b8f71; margin-bottom: 2rem;">Registra la salida de productos del inventario</p>', unsafe_allow_html=True)

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


def pagina_historial():
    st.markdown('<h1 class="main-title">📋 Historial de Movimientos</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6b8f71; margin-bottom: 2rem;">Consulta todos los movimientos de stock</p>', unsafe_allow_html=True)

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


def pagina_alertas():
    st.markdown('<h1 class="main-title">⚠️ Alertas de Stock</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6b8f71; margin-bottom: 2rem;">Monitoreo de stock bajo y productos críticos</p>', unsafe_allow_html=True)
    
    movimientos = get_movimientos(estab_filter())
    
    if not movimientos:
        st.info("💡 Sin datos para mostrar alertas. Registrá movimientos para activar las alertas.")
        return
    
    st.markdown("""
    <div style="background: rgba(180, 200, 160, 0.9); padding: 1.5rem; border-radius: 16px; margin-bottom: 2rem;">
        <p style="margin: 0; color: #2c5e2e;">🔔 Las alertas te ayudan a mantener el control de tu inventario</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.success("✅ Sistema funcionando correctamente. Las alertas se mostrarán cuando haya stock bajo o productos por vencer.")


def pagina_reportes():
    st.markdown('<h1 class="main-title">📈 Reportes y Estadísticas</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6b8f71; margin-bottom: 2rem;">Análisis detallado de movimientos y tendencias</p>', unsafe_allow_html=True)
    
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


def pagina_proveedores():
    st.markdown('<h1 class="main-title">🏭 Gestión de Proveedores</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6b8f71; margin-bottom: 2rem;">Administra los proveedores de insumos agrícolas</p>', unsafe_allow_html=True)
    
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


def pagina_productos():
    st.markdown('<h1 class="main-title">📦 Catálogo de Productos</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6b8f71; margin-bottom: 2rem;">Administra el catálogo de productos agrícolas</p>', unsafe_allow_html=True)
    
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


def pagina_usuarios():
    st.markdown('<h1 class="main-title">👥 Gestión de Usuarios</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6b8f71; margin-bottom: 2rem;">Administra los usuarios del sistema</p>', unsafe_allow_html=True)
    
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
        <p>🌾 Sistema de Control de Stock Agrícola - SECCO AGRO</p>
        <p>La Sonia · San Guillermo · Camba Pora</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
