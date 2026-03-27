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
# AUTENTICACIÓN
# ══════════════════════════════════════════════════════════════

def login():
    """Pantalla de login."""
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<p class="titulo-app">🌾 Stock Agrícola</p>', unsafe_allow_html=True)
        st.markdown('<p class="subtitulo">La Sonia · San Guillermo · Camba Pora</p>', unsafe_allow_html=True)
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
        perfil = st.session_state.get("perfil", {})
        rol = st.session_state.get("rol", "")
        estab = st.session_state.get("establecimiento_nombre", "Todos")

        st.markdown(f"**👤 {perfil.get('nombre','Usuario')}**")
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
    if st.session_state["rol"] == "admin":
        return None  # Admin ve todo
    return st.session_state["establecimiento_id"]


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

    if st.session_state["rol"] == "admin":
        establecs = ["Todos"] + df["establecimiento"].unique().tolist()
        estab_sel = col_f2.selectbox("Establecimiento", establecs)
    else:
        estab_sel = st.session_state["establecimiento_nombre"]

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
# PÁGINA: NUEVO INGRESO
# ══════════════════════════════════════════════════════════════

def pagina_ingreso():
    st.markdown('<p class="titulo-app">📥 Registrar Ingreso</p>', unsafe_allow_html=True)
    st.markdown("---")

    establecs = get_establecimientos()
    categorias = get_categorias()
    proveedores = get_proveedores()

    with st.form("form_ingreso", clear_on_submit=True):
        st.subheader("Producto")
        col1, col2 = st.columns(2)

        # Establecimiento
        if st.session_state["rol"] == "admin":
            estab_opciones = {e["nombre"]: e["id"] for e in establecs}
            estab_sel = col1.selectbox("Establecimiento *", list(estab_opciones.keys()))
            establecimiento_id = estab_opciones[estab_sel]
        else:
            establecimiento_id = st.session_state["establecimiento_id"]
            col1.info(f"📍 {st.session_state['establecimiento_nombre']}")

        # Categoría → producto en cascada
        cat_opciones = {c["nombre"]: c["id"] for c in categorias}
        cat_sel = col2.selectbox("Categoría *", list(cat_opciones.keys()))
        cat_id = cat_opciones[cat_sel]

        productos = get_productos(cat_id)
        prod_opciones = {p["nombre"]: p["id"] for p in productos}
        prod_sel = st.selectbox("Producto *", list(prod_opciones.keys()))
        producto_id = prod_opciones[prod_sel]

        st.subheader("Detalle")
        c1, c2, c3 = st.columns(3)
        cantidad = c1.number_input("Cantidad *", min_value=0.001, step=0.5, format="%.3f")
        presentacion = c2.text_input("Presentación", placeholder="Bolsa 25kg / Bidón 20L")
        marca = c3.text_input("Marca", placeholder="Ej: Bayer, YPF")
        c4, c5 = st.columns(2)
        concentracion = c4.text_input("Concentración", placeholder="Ej: 60% / 480 g/L")
        fecha_vencimiento = c5.date_input("Fecha de vencimiento", value=None)

        st.subheader("Origen")
        origen_tipo = st.radio("Tipo de ingreso *", ["proveedor", "traslado"], horizontal=True)

        c6, c7, c8 = st.columns(3)
        if origen_tipo == "proveedor":
            prov_opciones = {p["nombre"]: p["id"] for p in proveedores}
            if prov_opciones:
                prov_sel = c6.selectbox("Proveedor *", list(prov_opciones.keys()))
                proveedor_id = prov_opciones[prov_sel]
            else:
                c6.warning("Sin proveedores cargados.")
                proveedor_id = None
            origen_estab_id = None
        else:
            estab_opciones2 = {e["nombre"]: e["id"] for e in establecs if e["id"] != establecimiento_id}
            origen_sel = c6.selectbox("Establecimiento origen *", list(estab_opciones2.keys()))
            origen_estab_id = estab_opciones2[origen_sel]
            proveedor_id = None

        numero_factura = c7.text_input("N° Factura / Remito")
        fecha_factura = c8.date_input("Fecha factura")
        fecha_mov = st.date_input("Fecha del movimiento *")
        observaciones = st.text_area("Observaciones", height=60)

        submitted = st.form_submit_button("✅ Registrar Ingreso", type="primary", use_container_width=True)

    if submitted:
        if cantidad <= 0:
            st.error("La cantidad debe ser mayor a 0.")
            return
        try:
            payload = {
                "tipo": "ingreso",
                "producto_id": producto_id,
                "establecimiento_id": establecimiento_id,
                "cantidad": float(cantidad),
                "presentacion": presentacion or None,
                "marca": marca or None,
                "concentracion": concentracion or None,
                "fecha_vencimiento": str(fecha_vencimiento) if fecha_vencimiento else None,
                "origen_tipo": origen_tipo,
                "proveedor_id": proveedor_id,
                "origen_establecimiento_id": origen_estab_id,
                "numero_factura": numero_factura or None,
                "fecha_factura": str(fecha_factura) if fecha_factura else None,
                "fecha": str(fecha_mov),
                "observaciones": observaciones or None,
                "usuario_id": st.session_state["user_id"],
            }
            supabase.table("movimientos").insert(payload).execute()
            st.success(f"✅ Ingreso registrado: {cantidad} unidades de **{prod_sel}**")
        except Exception as e:
            st.error(f"Error al guardar: {e}")


# ══════════════════════════════════════════════════════════════
# PÁGINA: NUEVO EGRESO
# ══════════════════════════════════════════════════════════════

def pagina_egreso():
    st.markdown('<p class="titulo-app">📤 Registrar Egreso</p>', unsafe_allow_html=True)
    st.markdown("---")

    establecs = get_establecimientos()
    categorias = get_categorias()

    with st.form("form_egreso", clear_on_submit=True):
        st.subheader("Producto")
        col1, col2 = st.columns(2)

        if st.session_state["rol"] == "admin":
            estab_opciones = {e["nombre"]: e["id"] for e in establecs}
            estab_sel = col1.selectbox("Establecimiento *", list(estab_opciones.keys()))
            establecimiento_id = estab_opciones[estab_sel]
        else:
            establecimiento_id = st.session_state["establecimiento_id"]
            col1.info(f"📍 {st.session_state['establecimiento_nombre']}")

        cat_opciones = {c["nombre"]: c["id"] for c in categorias}
        cat_sel = col2.selectbox("Categoría *", list(cat_opciones.keys()))
        cat_id = cat_opciones[cat_sel]

        productos = get_productos(cat_id)
        prod_opciones = {p["nombre"]: p["id"] for p in productos}
        prod_sel = st.selectbox("Producto *", list(prod_opciones.keys()))
        producto_id = prod_opciones[prod_sel]

        st.subheader("Detalle")
        c1, c2 = st.columns(2)
        cantidad = c1.number_input("Cantidad *", min_value=0.001, step=0.5, format="%.3f")
        fecha_mov = c2.date_input("Fecha del egreso *")

        st.subheader("Destino")
        destino_tipo = st.radio("Tipo de egreso *", ["uso", "traslado"], horizontal=True)

        c3, c4 = st.columns(2)
        if destino_tipo == "traslado":
            estab_opciones2 = {e["nombre"]: e["id"] for e in establecs if e["id"] != establecimiento_id}
            dest_sel = c3.selectbox("Establecimiento destino *", list(estab_opciones2.keys()))
            destino_estab_id = estab_opciones2[dest_sel]
        else:
            destino_estab_id = None

        numero_remito = c4.text_input("N° Remito")
        observaciones = st.text_area("Observaciones / Detalle de uso", height=60)

        submitted = st.form_submit_button("✅ Registrar Egreso", type="primary", use_container_width=True)

    if submitted:
        if cantidad <= 0:
            st.error("La cantidad debe ser mayor a 0.")
            return
        try:
            payload = {
                "tipo": "egreso",
                "producto_id": producto_id,
                "establecimiento_id": establecimiento_id,
                "cantidad": float(cantidad),
                "destino_tipo": destino_tipo,
                "destino_establecimiento_id": destino_estab_id,
                "numero_remito": numero_remito or None,
                "fecha": str(fecha_mov),
                "observaciones": observaciones or None,
                "usuario_id": st.session_state["user_id"],
            }
            supabase.table("movimientos").insert(payload).execute()
            st.success(f"✅ Egreso registrado: {cantidad} unidades de **{prod_sel}**")
        except Exception as e:
            st.error(f"Error al guardar: {e}")


# ══════════════════════════════════════════════════════════════
# PÁGINA: HISTORIAL DE MOVIMIENTOS
# ══════════════════════════════════════════════════════════════

def pagina_historial():
    import pandas as pd
    st.markdown('<p class="titulo-app">📋 Historial de Movimientos</p>', unsafe_allow_html=True)
    st.markdown("---")

    movs = get_movimientos(estab_filter(), limit=500)
    if not movs:
        st.info("Sin movimientos registrados.")
        return

    df = pd.DataFrame(movs)

    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    tipo_sel = col1.selectbox("Tipo", ["Todos", "ingreso", "egreso"])
    cat_sel = col2.selectbox("Categoría", ["Todas"] + df["categoria"].unique().tolist())
    if st.session_state["rol"] == "admin":
        estab_sel = col3.selectbox("Establecimiento", ["Todos"] + df["establecimiento"].unique().tolist())
    else:
        estab_sel = st.session_state["establecimiento_nombre"]

    # Filtrar
    df_f = df.copy()
    if tipo_sel != "Todos":
        df_f = df_f[df_f["tipo"] == tipo_sel]
    if cat_sel != "Todas":
        df_f = df_f[df_f["categoria"] == cat_sel]
    if estab_sel not in ("Todos", None):
        df_f = df_f[df_f["establecimiento"] == estab_sel]

    st.markdown(f"**{len(df_f)} movimientos**")

    cols = ["fecha", "tipo", "establecimiento", "categoria", "producto", "cantidad",
            "presentacion", "marca", "origen_tipo", "proveedor", "numero_factura",
            "destino_tipo", "destino_establecimiento", "numero_remito", "usuario"]

    cols_existentes = [c for c in cols if c in df_f.columns]
    st.dataframe(df_f[cols_existentes].rename(columns={
        "fecha": "Fecha", "tipo": "Tipo", "establecimiento": "Establecimiento",
        "categoria": "Categoría", "producto": "Producto", "cantidad": "Cantidad",
        "presentacion": "Presentación", "marca": "Marca", "origen_tipo": "Origen",
        "proveedor": "Proveedor", "numero_factura": "N° Factura",
        "destino_tipo": "Destino", "destino_establecimiento": "Est. Destino",
        "numero_remito": "N° Remito", "usuario": "Usuario",
    }), use_container_width=True, height=500)

    # Exportar
    from io import BytesIO
    import openpyxl
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_f[cols_existentes].to_excel(writer, index=False, sheet_name="Movimientos")
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
    import pandas as pd
    st.markdown('<p class="titulo-app">⚠️ Alertas de Stock</p>', unsafe_allow_html=True)
    st.markdown("---")

    stock = get_stock(estab_filter())
    if not stock:
        st.info("Sin datos de stock.")
        return

    df = pd.DataFrame(stock)

    # Vencidos
    vencidos = df[df["alerta"] == "vencido"]
    if not vencidos.empty:
        st.error(f"🔴 **{len(vencidos)} productos vencidos**")
        st.dataframe(vencidos[["establecimiento", "categoria", "producto", "cantidad",
                                "marca", "fecha_vencimiento"]].rename(columns={
            "establecimiento":"Establecimiento","categoria":"Categoría","producto":"Producto",
            "cantidad":"Cantidad","marca":"Marca","fecha_vencimiento":"Vencimiento"}),
            use_container_width=True)
    else:
        st.success("✅ Sin productos vencidos")

    st.markdown("---")

    # Por vencer
    vence_pronto = df[df["alerta"] == "vence_pronto"]
    if not vence_pronto.empty:
        st.warning(f"🟡 **{len(vence_pronto)} productos vencen en los próximos 30 días**")
        st.dataframe(vence_pronto[["establecimiento", "categoria", "producto", "cantidad",
                                    "marca", "fecha_vencimiento"]].rename(columns={
            "establecimiento":"Establecimiento","categoria":"Categoría","producto":"Producto",
            "cantidad":"Cantidad","marca":"Marca","fecha_vencimiento":"Vencimiento"}),
            use_container_width=True)
    else:
        st.success("✅ Sin productos próximos a vencer")

    st.markdown("---")

    # Stock bajo mínimo
    bajo = df[df["alerta"] == "stock_bajo"]
    if not bajo.empty:
        st.info(f"🔵 **{len(bajo)} productos bajo stock mínimo**")
        st.dataframe(bajo[["establecimiento", "categoria", "producto", "cantidad",
                            "stock_minimo", "marca"]].rename(columns={
            "establecimiento":"Establecimiento","categoria":"Categoría","producto":"Producto",
            "cantidad":"Stock actual","stock_minimo":"Mínimo","marca":"Marca"}),
            use_container_width=True)
    else:
        st.success("✅ Todos los productos sobre stock mínimo")


# ══════════════════════════════════════════════════════════════
# PÁGINA: REPORTES
# ══════════════════════════════════════════════════════════════

def pagina_reportes():
    import pandas as pd
    from io import BytesIO
    st.markdown('<p class="titulo-app">📈 Reportes</p>', unsafe_allow_html=True)
    st.markdown("---")

    reporte = st.selectbox("Seleccionar reporte", [
        "Stock actual consolidado",
        "Resumen por proveedor",
        "Movimientos por período",
        "Stock por establecimiento comparado",
    ])

    if reporte == "Stock actual consolidado":
        stock = get_stock(estab_filter())
        df = pd.DataFrame(stock) if stock else pd.DataFrame()
        if df.empty:
            st.info("Sin datos.")
            return
        pivot = df.pivot_table(index=["categoria", "producto", "marca"],
                               columns="establecimiento", values="cantidad",
                               aggfunc="sum", fill_value=0).reset_index()
        st.dataframe(pivot, use_container_width=True)

    elif reporte == "Resumen por proveedor":
        movs = get_movimientos(estab_filter())
        df = pd.DataFrame(movs) if movs else pd.DataFrame()
        if df.empty or "proveedor" not in df.columns:
            st.info("Sin datos.")
            return
        df_prov = df[df["tipo"] == "ingreso"].groupby(
            ["proveedor", "categoria", "producto"])["cantidad"].sum().reset_index()
        df_prov.columns = ["Proveedor", "Categoría", "Producto", "Total ingresado"]
        st.dataframe(df_prov, use_container_width=True)

    elif reporte == "Movimientos por período":
        col1, col2 = st.columns(2)
        from datetime import date, timedelta
        fecha_desde = col1.date_input("Desde", value=date.today() - timedelta(days=30))
        fecha_hasta = col2.date_input("Hasta", value=date.today())
        movs = get_movimientos(estab_filter(), limit=1000)
        df = pd.DataFrame(movs) if movs else pd.DataFrame()
        if not df.empty and "fecha" in df.columns:
            df["fecha"] = pd.to_datetime(df["fecha"])
            mask = (df["fecha"] >= pd.Timestamp(fecha_desde)) & (df["fecha"] <= pd.Timestamp(fecha_hasta))
            df = df[mask]
        st.dataframe(df[["fecha","tipo","establecimiento","categoria","producto","cantidad",
                          "proveedor","numero_factura","numero_remito"]].rename(columns={
            "fecha":"Fecha","tipo":"Tipo","establecimiento":"Establecimiento",
            "categoria":"Categoría","producto":"Producto","cantidad":"Cantidad",
            "proveedor":"Proveedor","numero_factura":"N° Factura","numero_remito":"N° Remito"
        }) if not df.empty else df, use_container_width=True)

    elif reporte == "Stock por establecimiento comparado":
        stock = get_stock()  # Admin siempre ve todo
        df = pd.DataFrame(stock) if stock else pd.DataFrame()
        if df.empty:
            st.info("Sin datos.")
            return
        pivot = df.pivot_table(index=["categoria", "producto"],
                               columns="establecimiento", values="cantidad",
                               aggfunc="sum", fill_value=0)
        st.dataframe(pivot, use_container_width=True)

    # Exportar Excel siempre disponible
    if "df" in dir() and not df.empty:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=reporte[:30])
        st.download_button("⬇️ Exportar Excel", buffer.getvalue(),
                           f"reporte_{reporte[:20].replace(' ','_')}.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ══════════════════════════════════════════════════════════════
# PÁGINA: PROVEEDORES (solo admin)
# ══════════════════════════════════════════════════════════════

def pagina_proveedores():
    st.markdown('<p class="titulo-app">🏭 Gestión de Proveedores</p>', unsafe_allow_html=True)
    st.markdown("---")

    proveedores = get_proveedores()

    col1, col2 = st.columns([2, 1])
    with col2:
        with st.form("nuevo_proveedor"):
            st.subheader("Nuevo proveedor")
            nombre = st.text_input("Nombre")
            if st.form_submit_button("➕ Agregar"):
                if nombre:
                    try:
                        supabase.table("proveedores").insert({"nombre": nombre}).execute()
                        st.success(f"Proveedor '{nombre}' agregado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    with col1:
        import pandas as pd
        if proveedores:
            df = pd.DataFrame(proveedores)[["nombre", "activo", "created_at"]]
            df.columns = ["Nombre", "Activo", "Creado"]
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Sin proveedores cargados.")


# ══════════════════════════════════════════════════════════════
# PÁGINA: PRODUCTOS (solo admin)
# ══════════════════════════════════════════════════════════════

def pagina_productos():
    import pandas as pd
    st.markdown('<p class="titulo-app">📦 Gestión de Productos</p>', unsafe_allow_html=True)
    st.markdown("---")

    categorias = get_categorias()
    cat_opciones = {c["nombre"]: c["id"] for c in categorias}

    col1, col2 = st.columns([2, 1])
    with col2:
        with st.form("nuevo_producto"):
            st.subheader("Nuevo producto")
            cat_sel = st.selectbox("Categoría", list(cat_opciones.keys()))
            nombre = st.text_input("Nombre del producto")
            if st.form_submit_button("➕ Agregar"):
                if nombre:
                    try:
                        supabase.table("productos").insert({
                            "categoria_id": cat_opciones[cat_sel],
                            "nombre": nombre,
                        }).execute()
                        st.success(f"Producto '{nombre}' agregado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    with col1:
        cat_filtro = st.selectbox("Filtrar por categoría", ["Todas"] + list(cat_opciones.keys()))
        productos = get_productos(cat_opciones.get(cat_filtro) if cat_filtro != "Todas" else None)
        if productos:
            df = pd.DataFrame(productos)
            df["categoria"] = df["categorias"].apply(lambda x: x["nombre"] if x else "")
            st.dataframe(df[["categoria", "nombre", "activo"]].rename(columns={
                "categoria": "Categoría", "nombre": "Nombre", "activo": "Activo"
            }), use_container_width=True)


# ══════════════════════════════════════════════════════════════
# PÁGINA: USUARIOS (solo admin)
# ══════════════════════════════════════════════════════════════

def pagina_usuarios():
    import pandas as pd
    st.markdown('<p class="titulo-app">👥 Gestión de Usuarios</p>', unsafe_allow_html=True)
    st.markdown("---")

    st.info("Para crear nuevos usuarios, usá el panel de Supabase Authentication y luego completá sus datos en la tabla `usuarios`.")

    try:
        usuarios = supabase.table("usuarios").select("*,establecimientos(nombre)").execute().data
        if usuarios:
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

    rutas.get(pagina, pagina_dashboard)()


if __name__ == "__main__":
    main()
