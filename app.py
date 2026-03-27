"""
SISTEMA DE CONTROL DE STOCK AGRÍCOLA
App principal Streamlit — La Sonia / San Guillermo / Camba Pora
"""

import streamlit as st
from supabase import create_client, Client
import os
from datetime import date, timedelta
import pandas as pd
from io import BytesIO

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
                        st.rerun()
                    else:
                        st.error("No se encontró tu perfil. Verifica que tu usuario esté registrado en la tabla 'usuarios'")
                        
                except Exception as e:
                    st.error(f"Error al iniciar sesión: {e}")


# ══════════════════════════════════════════════════════════════
# SIDEBAR / NAVEGACIÓN
# ══════════════════════════════════════════════════════════════

def sidebar():
    with st.sidebar:
        st.markdown("### 🌾 Stock Agrícola")
        
        if "perfil" not in st.session_state:
            st.warning("Cargando...")
            return
            
        perfil = st.session_state.get("perfil", {})
        rol = st.session_state.get("rol", "")
        estab = st.session_state.get("establecimiento_nombre", "Todos")

        st.markdown(f"**👤 {perfil.get('nombre', 'Usuario')}**")
        st.markdown(f"📍 {estab if estab else 'Admin - Todos los establecimientos'}")
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
    try:
        q = supabase.table("stock").select("*")
        if establecimiento_id:
            q = q.eq("establecimiento_id", establecimiento_id)
        return q.execute().data
    except:
        # Si la vista no existe, usar consulta alternativa
        return []

def get_movimientos(establecimiento_id=None, limit=200):
    try:
        q = supabase.table("movimientos").select("*, productos(nombre, categorias(nombre)), establecimientos(nombre)").limit(limit)
        if establecimiento_id:
            q = q.eq("establecimiento_id", establecimiento_id)
        return q.execute().data
    except:
        return []


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

    movimientos = get_movimientos(estab_filter())
    
    if not movimientos:
        st.info("Sin datos de stock aún. Comenzá registrando ingresos.")
        return

    df = pd.DataFrame(movimientos)
    
    # Calcular stock actual (ingresos - egresos)
    ingresos = df[df["tipo"] == "ingreso"].groupby("producto_id")["cantidad"].sum()
    egresos = df[df["tipo"] == "egreso"].groupby("producto_id")["cantidad"].sum()
    
    stock_actual = {}
    for prod in set(ingresos.index) | set(egresos.index):
        stock_actual[prod] = ingresos.get(prod, 0) - egresos.get(prod, 0)
    
    total_productos = len(stock_actual)
    total_unidades = sum(stock_actual.values())
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Productos en stock", total_productos)
    col2.metric("📊 Unidades totales", f"{total_unidades:,.0f}")
    col3.metric("📥 Ingresos", len(df[df["tipo"] == "ingreso"]))
    col4.metric("📤 Egresos", len(df[df["tipo"] == "egreso"]))
    
    st.markdown("---")
    st.subheader("📋 Últimos movimientos")
    ultimos = df.sort_values("fecha", ascending=False).head(10)
    
    if not ultimos.empty:
        st.dataframe(ultimos[["fecha", "tipo", "cantidad", "observaciones"]], use_container_width=True)


# ══════════════════════════════════════════════════════════════
# PÁGINA: NUEVO INGRESO
# ══════════════════════════════════════════════════════════════

def pagina_ingreso():
    st.markdown('<p class="titulo-app">📥 Registrar Ingreso</p>', unsafe_allow_html=True)
    st.markdown("---")

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
        # Establecimiento
        if st.session_state.get("rol") == "admin":
            estab_options = {e["nombre"]: e["id"] for e in establecimientos}
            estab_sel = st.selectbox("Establecimiento *", list(estab_options.keys()))
            establecimiento_id = estab_options[estab_sel]
        else:
            establecimiento_id = st.session_state.get("establecimiento_id")
            st.info(f"📍 Establecimiento: {st.session_state.get('establecimiento_nombre', '')}")
        
        # Categoría
        cat_options = {c["nombre"]: c["id"] for c in categorias}
        cat_sel = st.selectbox("Categoría *", list(cat_options.keys()))
        cat_id = cat_options[cat_sel]
        
        # Producto
        productos = get_productos(cat_id)
        if not productos:
            st.warning("⚠️ No hay productos en esta categoría.")
            return
        
        prod_options = {p["nombre"]: p["id"] for p in productos}
        prod_sel = st.selectbox("Producto *", list(prod_options.keys()))
        producto_id = prod_options[prod_sel]
        
        # Detalles
        col1, col2 = st.columns(2)
        cantidad = col1.number_input("Cantidad *", min_value=0.001, step=0.5, format="%.3f")
        fecha = col2.date_input("Fecha *", value=date.today())
        
        # Proveedor
        prov_options = {p["nombre"]: p["id"] for p in proveedores}
        if prov_options:
            prov_sel = st.selectbox("Proveedor", ["Sin proveedor"] + list(prov_options.keys()))
            proveedor_id = prov_options[prov_sel] if prov_sel != "Sin proveedor" else None
        else:
            proveedor_id = None
            st.info("💡 Puedes agregar proveedores desde el menú Proveedores")
        
        observaciones = st.text_area("Observaciones", placeholder="N° factura, lote, etc.")
        
        submitted = st.form_submit_button("✅ Registrar Ingreso", type="primary", use_container_width=True)
        
        if submitted:
            if cantidad <= 0:
                st.error("La cantidad debe ser mayor a 0")
                return
            
            try:
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
                st.success(f"✅ Ingreso registrado: {cantidad} unidades de {prod_sel}")
                st.balloons()
            except Exception as e:
                st.error(f"Error al guardar: {e}")


# ══════════════════════════════════════════════════════════════
# PÁGINA: NUEVO EGRESO
# ══════════════════════════════════════════════════════════════

def pagina_egreso():
    st.markdown('<p class="titulo-app">📤 Registrar Egreso</p>', unsafe_allow_html=True)
    st.markdown("---")

    establecimientos = get_establecimientos()
    categorias = get_categorias()

    if not establecimientos:
        st.warning("⚠️ No hay establecimientos cargados.")
        return

    with st.form("form_egreso", clear_on_submit=True):
        # Establecimiento
        if st.session_state.get("rol") == "admin":
            estab_options = {e["nombre"]: e["id"] for e in establecimientos}
            estab_sel = st.selectbox("Establecimiento *", list(estab_options.keys()))
            establecimiento_id = estab_options[estab_sel]
        else:
            establecimiento_id = st.session_state.get("establecimiento_id")
            st.info(f"📍 Establecimiento: {st.session_state.get('establecimiento_nombre', '')}")
        
        # Categoría
        cat_options = {c["nombre"]: c["id"] for c in categorias}
        cat_sel = st.selectbox("Categoría *", list(cat_options.keys()))
        cat_id = cat_options[cat_sel]
        
        # Producto
        productos = get_productos(cat_id)
        if not productos:
            st.warning("⚠️ No hay productos en esta categoría.")
            return
        
        prod_options = {p["nombre"]: p["id"] for p in productos}
        prod_sel = st.selectbox("Producto *", list(prod_options.keys()))
        producto_id = prod_options[prod_sel]
        
        # Detalles
        col1, col2 = st.columns(2)
        cantidad = col1.number_input("Cantidad *", min_value=0.001, step=0.5, format="%.3f")
        fecha = col2.date_input("Fecha *", value=date.today())
        
        observaciones = st.text_area("Observaciones", placeholder="Motivo del egreso, destino, etc.")
        
        submitted = st.form_submit_button("✅ Registrar Egreso", type="primary", use_container_width=True)
        
        if submitted:
            if cantidad <= 0:
                st.error("La cantidad debe ser mayor a 0")
                return
            
            try:
                payload = {
                    "tipo": "egreso",
                    "producto_id": producto_id,
                    "establecimiento_id": establecimiento_id,
                    "cantidad": float(cantidad),
                    "fecha": str(fecha),
                    "observaciones": observaciones or None,
                    "usuario_id": st.session_state.get("user_id"),
                }
                supabase.table("movimientos").insert(payload).execute()
                st.success(f"✅ Egreso registrado: {cantidad} unidades de {prod_sel}")
            except Exception as e:
                st.error(f"Error al guardar: {e}")


# ══════════════════════════════════════════════════════════════
# PÁGINA: HISTORIAL
# ══════════════════════════════════════════════════════════════

def pagina_historial():
    st.markdown('<p class="titulo-app">📋 Historial de Movimientos</p>', unsafe_allow_html=True)
    st.markdown("---")

    movimientos = get_movimientos(estab_filter(), limit=500)
    
    if not movimientos:
        st.info("Sin movimientos registrados.")
        return
    
    df = pd.DataFrame(movimientos)
    
    # Procesar datos para mostrar
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["producto_nombre"] = df["productos"].apply(lambda x: x["nombre"] if x else "N/A")
    
    # Filtros
    col1, col2 = st.columns(2)
    tipo_sel = col1.selectbox("Tipo", ["Todos", "ingreso", "egreso"])
    fecha_desde = col2.date_input("Desde", value=date.today() - timedelta(days=30))
    
    df_f = df.copy()
    if tipo_sel != "Todos":
        df_f = df_f[df_f["tipo"] == tipo_sel]
    df_f = df_f[df_f["fecha"] >= pd.Timestamp(fecha_desde)]
    
    st.markdown(f"**{len(df_f)} movimientos**")
    
    # Mostrar tabla
    display_df = df_f[["fecha", "tipo", "producto_nombre", "cantidad", "observaciones"]].sort_values("fecha", ascending=False)
    display_df.columns = ["Fecha", "Tipo", "Producto", "Cantidad", "Observaciones"]
    st.dataframe(display_df, use_container_width=True, height=400)
    
    # Exportar
    if not df_f.empty:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_f.to_excel(writer, index=False, sheet_name="Movimientos")
        st.download_button(
            "⬇️ Exportar Excel",
            data=buffer.getvalue(),
            file_name="movimientos_stock.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


# ══════════════════════════════════════════════════════════════
# PÁGINA: ALERTAS
# ══════════════════════════════════════════════════════════════

def pagina_alertas():
    st.markdown('<p class="titulo-app">⚠️ Alertas</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    movimientos = get_movimientos(estab_filter())
    
    if not movimientos:
        st.info("Sin datos para mostrar alertas.")
        return
    
    st.info("🔔 Las alertas te avisarán cuando los productos estén por vencer o tengan stock bajo.")
    st.markdown("---")
    
    # Mostrar productos con poco stock (menos de 10 unidades)
    df = pd.DataFrame(movimientos)
    ingresos = df[df["tipo"] == "ingreso"].groupby("producto_id")["cantidad"].sum()
    egresos = df[df["tipo"] == "egreso"].groupby("producto_id")["cantidad"].sum()
    
    stock_bajo = []
    for prod in ingresos.index:
        stock = ingresos.get(prod, 0) - egresos.get(prod, 0)
        if stock < 10 and stock > 0:
            stock_bajo.append({"producto": prod, "stock": stock})
    
    if stock_bajo:
        st.warning(f"⚠️ {len(stock_bajo)} productos con stock bajo (< 10 unidades)")
    else:
        st.success("✅ Todos los productos tienen stock suficiente")


# ══════════════════════════════════════════════════════════════
# PÁGINA: REPORTES
# ══════════════════════════════════════════════════════════════

def pagina_reportes():
    st.markdown('<p class="titulo-app">📈 Reportes</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    movimientos = get_movimientos(estab_filter())
    
    if not movimientos:
        st.info("Sin datos para generar reportes.")
        return
    
    df = pd.DataFrame(movimientos)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["mes"] = df["fecha"].dt.to_period("M")
    
    reporte = st.selectbox("Seleccionar reporte", [
        "Movimientos por mes",
        "Resumen por producto",
    ])
    
    if reporte == "Movimientos por mes":
        resumen = df.groupby(["mes", "tipo"])["cantidad"].sum().reset_index()
        st.dataframe(resumen, use_container_width=True)
        
        # Gráfico
        chart_data = df.groupby(["mes", "tipo"])["cantidad"].sum().unstack()
        st.bar_chart(chart_data)
    
    elif reporte == "Resumen por producto":
        resumen = df.groupby("producto_id")["cantidad"].sum().reset_index()
        st.dataframe(resumen, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# PÁGINA: PROVEEDORES (solo admin)
# ══════════════════════════════════════════════════════════════

def pagina_proveedores():
    st.markdown('<p class="titulo-app">🏭 Gestión de Proveedores</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    proveedores = get_proveedores()
    
    # Formulario para agregar
    with st.expander("➕ Agregar nuevo proveedor"):
        with st.form("nuevo_proveedor"):
            nombre = st.text_input("Nombre del proveedor")
            if st.form_submit_button("Guardar"):
                if nombre:
                    supabase.table("proveedores").insert({"nombre": nombre, "activo": True}).execute()
                    st.success(f"Proveedor '{nombre}' agregado")
                    st.rerun()
    
    # Listar proveedores
    if proveedores:
        df = pd.DataFrame(proveedores)
        st.dataframe(df[["nombre", "activo"]], use_container_width=True)
    else:
        st.info("No hay proveedores cargados")


# ══════════════════════════════════════════════════════════════
# PÁGINA: PRODUCTOS (solo admin)
# ══════════════════════════════════════════════════════════════

def pagina_productos():
    st.markdown('<p class="titulo-app">📦 Gestión de Productos</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    categorias = get_categorias()
    cat_options = {c["nombre"]: c["id"] for c in categorias}
    
    # Formulario para agregar
    with st.expander("➕ Agregar nuevo producto"):
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
                    st.success(f"Producto '{nombre}' agregado")
                    st.rerun()
    
    # Listar productos
    productos = get_productos()
    if productos:
        df = pd.DataFrame(productos)
        df["categoria"] = df["categorias"].apply(lambda x: x["nombre"] if x else "N/A")
        st.dataframe(df[["categoria", "nombre", "activo"]], use_container_width=True)
    else:
        st.info("No hay productos cargados")


# ══════════════════════════════════════════════════════════════
# PÁGINA: USUARIOS (solo admin)
# ══════════════════════════════════════════════════════════════

def pagina_usuarios():
    st.markdown('<p class="titulo-app">👥 Gestión de Usuarios</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    try:
        usuarios = supabase.table("usuarios").select("*").execute().data
        if usuarios:
            df = pd.DataFrame(usuarios)
            st.dataframe(df[["nombre", "rol", "created_at"]], use_container_width=True)
        else:
            st.info("No hay usuarios cargados")
    except Exception as e:
        st.error(f"Error: {e}")


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


if __name__ == "__main__":
    main()
