"""
SISTEMA DE CONTROL DE STOCK AGRÍCOLA
App principal Streamlit — La Sonia / San Guillermo / Camba Pora
"""

import streamlit as st
from supabase import create_client, Client
import os

# ── Configuración de página ────────────────────────────────────
st.set_page_config(
    page_title="Stock Agrícola",
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

# ========== MODO DEPURACIÓN ==========
# Activar para ver información de depuración
DEBUG = True  # Cambia a False para desactivar


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
                    if DEBUG:
                        st.error(f"🔍 Perfil no encontrado para ID: {user_id}")
                        # Mostrar todos los IDs disponibles
                        todos = supabase.table("usuarios").select("id, nombre").execute()
                        st.write("IDs disponibles en tabla usuarios:")
                        for u in todos.data:
                            st.write(f"  - {u['id']} → {u.get('nombre', 'Sin nombre')}")
                    else:
                        st.error("Perfil no encontrado")
                    logout()
                    return False
            except Exception as e:
                st.error(f"Error al cargar perfil: {e}")
                return False
        return False
    return True


# ── CSS personalizado ──────────────────────────────────────────
st.markdown("""
<style>
    /* Sidebar */
    [data-testid="stSidebar"] { background: #1a2332; }
    [data-testid="stSidebar"] * { color: #e8f4e8 !important; }
    [data-testid="stSidebar"] .stButton button {
        background: transparent; border: 1px solid #3d6b3d;
        color: #e8f4e8 !important; width: 100%; text-align: left;
        padding: 0.5rem 1rem; border-radius: 6px; margin: 2px 0;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background: #2d4a2d; border-color: #5a9e5a;
    }
    /* Métricas */
    [data-testid="metric-container"] {
        background: #f8fffe; border: 1px solid #d4e8d4;
        border-radius: 10px; padding: 1rem;
    }
    /* Alertas */
    .alerta-vencido   { background:#fff0f0; border-left:4px solid #e53e3e; padding:0.5rem 1rem; border-radius:4px; }
    .alerta-vence     { background:#fffbf0; border-left:4px solid #d69e2e; padding:0.5rem 1rem; border-radius:4px; }
    .alerta-stock     { background:#f0f4ff; border-left:4px solid #3182ce; padding:0.5rem 1rem; border-radius:4px; }
    /* Título */
    .titulo-app { font-size:1.8rem; font-weight:700; color:#1a4731; margin-bottom:0; }
    .subtitulo  { font-size:0.9rem; color:#6b8f71; margin-top:0; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# AUTENTICACIÓN - LOGIN
# ══════════════════════════════════════════════════════════════

def login():
    """Pantalla de login"""
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<p class="titulo-app">🌾 Stock Agrícola</p>', unsafe_allow_html=True)
        st.markdown('<p class="subtitulo">La Sonia · San Guillermo · Camba Porca</p>', unsafe_allow_html=True)
        st.markdown("---")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="usuario@ejemplo.com")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Ingresar", use_container_width=True, type="primary")
            
            if submitted:
                try:
                    if DEBUG:
                        st.write(f"🔍 Intentando login con: {email}")
                    
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    
                    if DEBUG:
                        st.success(f"✅ Login exitoso!")
                        st.write(f"🔍 User ID obtenido: {res.user.id}")
                        st.write(f"🔍 Email: {res.user.email}")
                    
                    st.session_state["session"] = res.session
                    st.session_state["user_id"] = res.user.id
                    
                    if DEBUG:
                        st.write("🔍 Buscando en tabla 'usuarios'...")
                    
                    perfil = supabase.table("usuarios").select("*").eq("id", res.user.id).execute()
                    
                    if DEBUG:
                        st.write(f"🔍 Resultado de búsqueda: {perfil.data}")
                    
                    if perfil.data:
                        st.session_state["perfil"] = perfil.data[0]
                        st.session_state["rol"] = perfil.data[0]["rol"]
                        st.session_state["establecimiento_id"] = perfil.data[0].get("establecimiento_id")
                        st.session_state["establecimiento_nombre"] = perfil.data[0].get("establecimiento_nombre")
                        st.session_state["pagina"] = "Dashboard"
                        
                        if DEBUG:
                            st.success(f"✅ Perfil encontrado! Rol: {st.session_state['rol']}")
                            st.balloons()
                        
                        st.rerun()
                    else:
                        st.error("❌ No se encontró tu perfil en la tabla 'usuarios'")
                        
                        if DEBUG:
                            st.write("---")
                            st.write("🔍 Mostrando todos los usuarios en la tabla:")
                            todos = supabase.table("usuarios").select("id, nombre, rol").execute()
                            for u in todos.data:
                                st.write(f"  - ID: {u['id']}")
                                st.write(f"    Nombre: {u.get('nombre', 'Sin nombre')}")
                                st.write(f"    Rol: {u.get('rol', 'Sin rol')}")
                                st.write("")
                            
                            st.warning(f"⚠️ El ID que buscamos es: {res.user.id}")
                            st.info("Si no ves este ID en la lista, debes agregarlo a la tabla 'usuarios'")
                        
                except Exception as e:
                    st.error(f"Error al iniciar sesión: {e}")
                    if DEBUG:
                        st.write(f"🔍 Detalle del error: {str(e)}")


# ══════════════════════════════════════════════════════════════
# SIDEBAR / NAVEGACIÓN
# ══════════════════════════════════════════════════════════════

def sidebar():
    with st.sidebar:
        st.markdown("### 🌾 Stock Agrícola")
        
        # Verificar que exista el perfil
        if "perfil" not in st.session_state:
            st.warning("Cargando...")
            return
            
        perfil = st.session_state.get("perfil", {})
        rol = st.session_state.get("rol", "")
        estab = st.session_state.get("establecimiento_nombre", "Todos")

        st.markdown(f"**👤 {perfil.get('nombre', 'Usuario')}**")
        st.markdown(f"📍 {estab}")
        st.markdown(f"🔑 {'Administrador' if rol == 'admin' else 'Operador'}")
        st.markdown("---")

        paginas = [
            ("📊", "Dashboard"),
            ("📥", "Nuevo Ingreso"),
            ("📤", "Nuevo Egreso"),
            ("📋", "Historial"),
            ("⚠️", "Alertas"),
            ("📈", "Reportes"),
        ]
        if rol == "admin":
            paginas += [
                ("🏭", "Proveedores"),
                ("📦", "Productos"),
                ("👥", "Usuarios"),
            ]

        for emoji, nombre in paginas:
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

def get_productos(categoria_id=None):
    q = supabase.table("productos").select("*,categorias(nombre)").eq("activo", True)
    if categoria_id:
        q = q.eq("categoria_id", categoria_id)
    return q.execute().data

def get_proveedores():
    res = supabase.table("proveedores").select("*").eq("activo", True).execute()
    return res.data

def get_stock(establecimiento_id=None):
    q = supabase.from_("v_stock_completo").select("*")
    if establecimiento_id:
        q = q.eq("establecimiento_id", establecimiento_id)
    return q.execute().data

def get_movimientos(establecimiento_id=None, limit=200):
    q = supabase.from_("v_movimientos_completo").select("*").limit(limit)
    if establecimiento_id:
        q = q.eq("establecimiento_id", establecimiento_id)
    return q.execute().data


def estab_filter():
    """Retorna el establecimiento_id a filtrar según rol."""
    if "rol" not in st.session_state:
        return None
    
    if st.session_state.get("rol") == "admin":
        return None
    return st.session_state.get("establecimiento_id")


# ══════════════════════════════════════════════════════════════
# PÁGINA: DASHBOARD
# ══════════════════════════════════════════════════════════════

def pagina_dashboard():
    st.markdown('<p class="titulo-app">📊 Dashboard de Stock</p>', unsafe_allow_html=True)
    st.markdown("---")

    stock = get_stock(estab_filter())

    if not stock:
        st.info("Sin datos de stock aún. Comenzá registrando ingresos.")
        return

    import pandas as pd
    df = pd.DataFrame(stock)

    # Métricas globales
    col1, col2, col3, col4 = st.columns(4)
    total_prod = df["producto"].nunique()
    vencidos = df[df["alerta"] == "vencido"].shape[0]
    vence_pronto = df[df["alerta"] == "vence_pronto"].shape[0]
    stock_bajo = df[df["alerta"] == "stock_bajo"].shape[0]

    col1.metric("📦 Productos en stock", total_prod)
    col2.metric("🔴 Vencidos", vencidos, delta=None)
    col3.metric("🟡 Vencen en 30 días", vence_pronto)
    col4.metric("🔵 Stock bajo mínimo", stock_bajo)

    st.markdown("---")

    # Filtros
    col_f1, col_f2, col_f3 = st.columns(3)
    categorias = ["Todas"] + df["categoria"].unique().tolist()
    cat_sel = col_f1.selectbox("Categoría", categorias)

    if st.session_state.get("rol") == "admin":
        establecs = ["Todos"] + df["establecimiento"].unique().tolist()
        estab_sel = col_f2.selectbox("Establecimiento", establecs)
    else:
        estab_sel = st.session_state.get("establecimiento_nombre", "Todos")

    alerta_sel = col_f3.selectbox("Alerta", ["Todos", "vencido", "vence_pronto", "stock_bajo", "ok"])

    df_filtrado = df.copy()
    if cat_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["categoria"] == cat_sel]
    if estab_sel not in ("Todos", None):
        df_filtrado = df_filtrado[df_filtrado["establecimiento"] == estab_sel]
    if alerta_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["alerta"] == alerta_sel]

    # Tabla principal
    cols_mostrar = ["establecimiento", "categoria", "producto", "cantidad",
                    "presentacion", "marca", "concentracion", "fecha_vencimiento", "alerta"]
    df_display = df_filtrado[cols_mostrar].rename(columns={
        "establecimiento": "Establecimiento",
        "categoria": "Categoría",
        "producto": "Producto",
        "cantidad": "Cantidad",
        "presentacion": "Presentación",
        "marca": "Marca",
        "concentracion": "Concentración",
        "fecha_vencimiento": "Vto.",
        "alerta": "Estado",
    })

    def color_alerta(val):
        colores = {"vencido": "background-color:#fff0f0",
                   "vence_pronto": "background-color:#fffbf0",
                   "stock_bajo": "background-color:#f0f4ff"}
        return colores.get(val, "")

    st.dataframe(
        df_display.style.applymap(color_alerta, subset=["Estado"]),
        use_container_width=True,
        height=450,
    )

    # Resumen por categoría
    st.markdown("#### Resumen por categoría")
    resumen = df_filtrado.groupby("categoria")["producto"].count().reset_index()
    resumen.columns = ["Categoría", "Productos"]
    st.bar_chart(resumen.set_index("Categoría"))


# ══════════════════════════════════════════════════════════════
# PÁGINA: NUEVO INGRESO (versión simplificada)
# ══════════════════════════════════════════════════════════════

def pagina_ingreso():
    st.markdown('<p class="titulo-app">📥 Registrar Ingreso</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.info("Página en construcción. Para registrar ingresos, asegúrate de tener las tablas configuradas.")


# ══════════════════════════════════════════════════════════════
# PÁGINA: NUEVO EGRESO (versión simplificada)
# ══════════════════════════════════════════════════════════════

def pagina_egreso():
    st.markdown('<p class="titulo-app">📤 Registrar Egreso</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.info("Página en construcción. Para registrar egresos, asegúrate de tener las tablas configuradas.")


# ══════════════════════════════════════════════════════════════
# PÁGINA: HISTORIAL (versión simplificada)
# ══════════════════════════════════════════════════════════════

def pagina_historial():
    st.markdown('<p class="titulo-app">📋 Historial</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.info("Página en construcción.")


# ══════════════════════════════════════════════════════════════
# PÁGINA: ALERTAS (versión simplificada)
# ══════════════════════════════════════════════════════════════

def pagina_alertas():
    st.markdown('<p class="titulo-app">⚠️ Alertas</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.info("Página en construcción.")


# ══════════════════════════════════════════════════════════════
# PÁGINA: REPORTES (versión simplificada)
# ══════════════════════════════════════════════════════════════

def pagina_reportes():
    st.markdown('<p class="titulo-app">📈 Reportes</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.info("Página en construcción.")


# ══════════════════════════════════════════════════════════════
# PÁGINA: PROVEEDORES (solo admin)
# ══════════════════════════════════════════════════════════════

def pagina_proveedores():
    st.markdown('<p class="titulo-app">🏭 Proveedores</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.info("Página en construcción.")


# ══════════════════════════════════════════════════════════════
# PÁGINA: PRODUCTOS (solo admin)
# ══════════════════════════════════════════════════════════════

def pagina_productos():
    st.markdown('<p class="titulo-app">📦 Productos</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.info("Página en construcción.")


# ══════════════════════════════════════════════════════════════
# PÁGINA: USUARIOS (solo admin)
# ══════════════════════════════════════════════════════════════

def pagina_usuarios():
    st.markdown('<p class="titulo-app">👥 Usuarios</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    try:
        usuarios = supabase.table("usuarios").select("*,establecimientos(nombre)").execute().data
        if usuarios:
            import pandas as pd
            df = pd.DataFrame(usuarios)
            df["establecimiento"] = df["establecimientos"].apply(lambda x: x["nombre"] if x else "Admin")
            st.dataframe(df[["nombre", "rol", "establecimiento", "created_at"]].rename(columns={
                "nombre": "Nombre", "rol": "Rol", "establecimiento": "Establecimiento", "created_at": "Creado"
            }), use_container_width=True)
    except Exception as e:
        st.error(f"Error: {e}")


# ══════════════════════════════════════════════════════════════
# ROUTER PRINCIPAL
# ══════════════════════════════════════════════════════════════

def main():
    if not check_auth():
        login()
        return

    # Verificar que el perfil esté cargado
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

    # Ejecutar la página correspondiente
    pagina_funcion = rutas.get(pagina, pagina_dashboard)
    pagina_funcion()


if __name__ == "__main__":
    main()
