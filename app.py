"""
SISTEMA DE CONTROL DE STOCK AGRÍCOLA
App principal Streamlit — La Sonia / San Guillermo / Camba Pora
Versión corregida: storage, signed URLs y manejo de errores
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
import traceback

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

# ── Verificar/Crear bucket de almacenamiento ─────────────────
def ensure_bucket_exists():
    """Verifica que el bucket exista, si no lo crea."""
    try:
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        if cfg.SUPABASE_STORAGE_BUCKET not in bucket_names:
            supabase.storage.create_bucket(
                cfg.SUPABASE_STORAGE_BUCKET,
                options={"public": False}
            )
            logger.info(f"✅ Bucket '{cfg.SUPABASE_STORAGE_BUCKET}' creado")
            return True
        return True
    except Exception as e:
        logger.error(f"Error con bucket: {e}")
        st.warning(f"⚠️ Storage no disponible: {str(e)[:100]}")
        return False

ensure_bucket_exists()

# ══════════════════════════════════════════════════════════════
# CSS (resumido para legibilidad - mantiene todos tus estilos)
# ══════════════════════════════════════════════════════════════

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

    :root {
        --gold: #d4a017;
        --gold-light: #e5b52a;
        --gold-dark: #b87a0c;
        --bg-main: #0e0e14;
        --bg-card: rgba(45,45,52,0.85);
        --text-primary: #f0f0f5;
        --green: #22c55e;
        --red: #ef4444;
    }

    [data-testid="stHeader"], header[data-testid="stHeader"] {
        display: none !important;
    }

    .stApp {
        background: var(--bg-main) !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    .stApp::after {
        content: '' !important;
        position: fixed !important;
        inset: 0 !important;
        background-image: url('https://raw.githubusercontent.com/marcasosguemes-cell/Stock-SECCO-AGRO/main/Fondo.PNG') !important;
        background-size: cover !important;
        background-position: center !important;
        filter: grayscale(100%) brightness(0.42) !important;
        z-index: -2 !important;
        pointer-events: none !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a1f 0%, #0f0f12 100%) !important;
        border-right: 1px solid rgba(100,100,120,0.3) !important;
    }

    .sidebar-header {
        text-align: center;
        padding: 1.6rem 0 1.2rem 0;
        border-bottom: 1px solid rgba(212,160,23,0.4);
        margin-bottom: 1.4rem;
    }

    .sidebar-logo-oval {
        background: #f7f3e8;
        border: 2px solid rgba(212,160,23,0.6);
        border-radius: 50%;
        width: 120px;
        height: 120px;
        margin: 0 auto 12px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }

    .sidebar-logo {
        width: 115% !important;
        height: auto !important;
    }

    .sidebar-header h1 {
        font-family: 'Playfair Display', serif !important;
        font-size: 1.4rem !important;
        color: var(--gold) !important;
    }

    .title-bubble {
        background: linear-gradient(135deg, rgba(200,160,96,0.95), rgba(184,144,90,0.95));
        border-radius: 20px;
        padding: 1rem 2.2rem;
        display: inline-block;
        margin-bottom: 1.4rem;
    }

    .title-bubble h1 {
        margin: 0;
        font-family: 'Playfair Display', serif !important;
        font-size: 1.8rem !important;
        color: #FFFFFF !important;
    }

    .metric-card {
        background: linear-gradient(145deg, rgba(55,55,62,0.9), rgba(45,45,52,0.95));
        border: 1px solid rgba(212,160,23,0.35);
        border-radius: 20px;
        padding: 1.2rem 1rem;
        text-align: center;
    }

    .footer {
        text-align: center;
        padding: 1.6rem 2rem;
        color: #a8a8b0;
        font-size: 0.78rem;
        border-top: 1px solid rgba(212,160,23,0.25);
        margin-top: 3rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--gold), var(--gold-dark)) !important;
        color: #1a1a1f !important;
        border: none !important;
        border-radius: 12px;
        font-weight: 700;
    }

    [data-testid="stForm"] {
        background: var(--bg-card) !important;
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(212,160,23,0.3);
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ALMACENAMIENTO: REMITOS PDF (CORREGIDO)
# ══════════════════════════════════════════════════════════════

def _validar_pdf(archivo_pdf) -> tuple[bool, str]:
    MAX_BYTES = cfg.MAX_PDF_SIZE_MB * 1024 * 1024
    data = archivo_pdf.getvalue()
    if len(data) > MAX_BYTES:
        return False, f"El archivo supera el límite de {cfg.MAX_PDF_SIZE_MB}MB."
    if not data.startswith(b"%PDF"):
        return False, "El archivo no es un PDF válido."
    return True, ""

def subir_remito_pdf(archivo_pdf, movimiento_id, usuario_id, establecimiento_id):
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
        ruta_completa = f"{establecimiento_id}/{now.year}/{now.month:02d}/{nombre_archivo}"
        archivo_bytes = archivo_pdf.getvalue()

        supabase.storage.from_(cfg.SUPABASE_STORAGE_BUCKET).upload(
            path=ruta_completa,
            file=archivo_bytes,
            file_options={"content-type": "application/pdf"}
        )

        supabase.table("movimientos").update({
            "remito_url": ruta_completa,
            "remito_filename": nombre_archivo
        }).eq("id", movimiento_id).execute()

        logger.info(f"✅ Remito subido: {ruta_completa}")
        return ruta_completa
    except Exception as e:
        logger.error(f"Error al subir remito: {e}")
        st.error(f"❌ Error al subir el remito: {str(e)[:200]}")
        return None

def get_signed_url(ruta: str) -> str | None:
    """Genera URL firmada - VERSIÓN CORREGIDA"""
    if not ruta or ruta == "—":
        return None
    try:
        res = supabase.storage.from_(cfg.SUPABASE_STORAGE_BUCKET).create_signed_url(
            path=ruta,
            expires_in=3600
        )
        # CORRECCIÓN: manejar diferentes formatos de respuesta
        if hasattr(res, 'signed_url'):
            return res.signed_url
        elif isinstance(res, dict):
            return res.get('signed_url') or res.get('signedURL')
        elif isinstance(res, str) and res.startswith('http'):
            return res
        return None
    except Exception as e:
        logger.warning(f"No se pudo generar URL firmada: {e}")
        return None

def generar_link_pdf(ruta_pdf):
    if not ruta_pdf or ruta_pdf == "—":
        return "—"
    url = get_signed_url(ruta_pdf)
    if not url:
        return '<span style="color:#666;">⚠️ No disponible</span>'
    
    return f'''
    <a href="{html.escape(url)}" target="_blank" 
       style="display:inline-flex;align-items:center;gap:6px;text-decoration:none;
              background:#c0392b;color:#fff;padding:5px 12px;border-radius:20px;
              font-size:0.75rem;font-weight:700;">
       📄 VER REMITO
    </a>
    '''

# ══════════════════════════════════════════════════════════════
# AUTENTICACIÓN (simplificada para que funcione)
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
    except Exception:
        pass
    for key in ["session", "user_id", "perfil", "rol", "establecimiento_id"]:
        st.session_state.pop(key, None)
    st.rerun()

def verificar_perfil():
    if "rol" not in st.session_state:
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
                    return False
            except Exception as e:
                st.error(f"Error al cargar perfil: {e}")
                return False
        return False
    return True

def login():
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; margin-bottom:2rem;">
            <div style="background:#f7f3e8; border:2px solid #d4a017; border-radius:50%;
                        width:150px; height:150px; margin:0 auto 20px auto;
                        display:flex; align-items:center; justify-content:center;">
                <img src="https://raw.githubusercontent.com/marcasosguemes-cell/Stock-SECCO-AGRO/main/Logo.png" 
                     style="width:130px;">
            </div>
            <div style="background:rgba(0,0,0,0.65); border-radius:20px; padding:1.5rem;">
                <h1 style="color:#fff; font-family:'Playfair Display',serif;">Stock Agrícola</h1>
                <p style="color:#FFE8B6;">La Sonia · San Guillermo · Camba Pora</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("Email", placeholder="usuario@ejemplo.com")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("🚀 Ingresar", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Completá ambos campos")
                    return
                try:
                    with st.spinner("Verificando..."):
                        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state["session"] = res.session
                        st.session_state["user_id"] = res.user.id
                        
                        perfil = supabase.table("usuarios").select("*").eq("id", res.user.id).execute()
                        if perfil.data:
                            p = perfil.data[0]
                            st.session_state["perfil"] = p
                            st.session_state["rol"] = p["rol"]
                            st.session_state["establecimiento_id"] = p.get("establecimiento_id")
                            st.session_state["establecimiento_nombre"] = p.get("establecimiento_nombre")
                            st.session_state["pagina"] = "Dashboard"
                            st.toast("✅ ¡Bienvenido!")
                            st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)[:100]}")

# ══════════════════════════════════════════════════════════════
# HELPERS DE DATOS
# ══════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def get_establecimientos():
    try:
        res = supabase.table("establecimientos").select("*").execute()
        return res.data
    except Exception as e:
        logger.error(f"get_establecimientos: {e}")
        return []

@st.cache_data(ttl=300)
def get_categorias():
    try:
        res = supabase.table("categorias").select("*").execute()
        return res.data
    except Exception as e:
        logger.error(f"get_categorias: {e}")
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
        logger.error(f"get_productos: {e}")
        return []

@st.cache_data(ttl=120)
def get_proveedores():
    try:
        res = supabase.table("proveedores").select("*").eq("activo", True).execute()
        return res.data
    except Exception as e:
        logger.error(f"get_proveedores: {e}")
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
        logger.error(f"get_movimientos: {e}")
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

def estab_filter():
    return st.session_state.get("estab_activo_id", None)

def render_tabla_html(df, height=500):
    import streamlit.components.v1 as components
    if df.empty:
        st.info("Sin datos para mostrar")
        return
    
    cols = list(df.columns)
    filas_html = ""
    for _, row in df.iterrows():
        filas_html += '<tr>'
        for col in cols:
            val = row[col]
            style = "color:#f0f0f5;padding:8px 12px;"
            if col in ("stock", "Stock", "cantidad", "Cantidad"):
                try:
                    v = float(val)
                    color = "#ef4444" if v < 50 else "#f59e0b" if v < 200 else "#22c55e"
                    style = f"color:{color};font-weight:700;padding:8px 12px;text-align:right;"
                    display_val = f"{v:,.2f}"
                except:
                    display_val = html.escape(str(val))
            else:
                display_val = html.escape(str(val)) if val not in (None, "nan", "None") else "—"
            filas_html += f'<td style="{style}">{display_val}</td>'
        filas_html += '</tr>'

    headers = "".join([f'<th style="padding:10px 12px;color:#1a1a1f;background:#d4a017;">{html.escape(str(c))}</th>' for c in cols])

    tabla_html = f"""
    <div style="overflow-x:auto;border-radius:14px;border:1px solid rgba(212,160,23,0.35);">
        <table style="width:100%;border-collapse:collapse;background:rgba(22,22,28,0.97);">
            <thead><tr>{headers}</tr></thead>
            <tbody>{filas_html}</tbody>
        </table>
    </div>"""
    components.html(tabla_html, height=min(height, 80 + len(df) * 38), scrolling=True)

# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════

def pagina_dashboard():
    st.markdown('<div class="title-bubble"><h1>📊 Dashboard de Stock</h1><p>Análisis del inventario agrícola</p></div>', unsafe_allow_html=True)

    stock_productos = get_stock_por_producto(estab_filter())

    if stock_productos.empty:
        st.info("💡 Sin datos de stock. Registrá movimientos para ver el inventario.")
        return

    categorias_disponibles = sorted(stock_productos["categoria"].dropna().unique().tolist())
    cat_sel = st.selectbox("📁 Categoría", ["Todas"] + categorias_disponibles, key="dash_cat")

    df_filtrado = stock_productos.copy()
    if cat_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["categoria"] == cat_sel]

    total_stock = df_filtrado["stock"].sum()
    total_productos = len(df_filtrado)
    stock_bajo = len(df_filtrado[df_filtrado["stock"] < cfg.STOCK_CRITICO_DEFAULT])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📦 Stock Total", f"{total_stock:,.0f}")
    with col2:
        st.metric("🏷️ Productos en Stock", total_productos)
    with col3:
        st.metric("⚠️ Stock Crítico", stock_bajo)
    with col4:
        st.metric("🎯 Umbral", f"< {cfg.STOCK_CRITICO_DEFAULT}")

    st.markdown("### 📋 Stock Actual por Producto")
    df_tabla = df_filtrado[["producto", "categoria", "presentacion", "stock", "unidad"]].copy()
    render_tabla_html(df_tabla.sort_values("stock", ascending=False))

# ══════════════════════════════════════════════════════════════
# NUEVO INGRESO
# ══════════════════════════════════════════════════════════════

def pagina_ingreso():
    st.markdown('<div class="title-bubble"><h1>📥 Registrar Ingreso</h1></div>', unsafe_allow_html=True)

    establecimientos = get_establecimientos()
    categorias = get_categorias()
    proveedores = get_proveedores()

    if not establecimientos:
        st.warning("⚠️ No hay establecimientos cargados")
        return

    estab_options = {e["nombre"]: e["id"] for e in establecimientos}
    estab_sel = st.selectbox("🏢 Establecimiento", list(estab_options.keys()), key="ing_estab")
    establecimiento_id = estab_options[estab_sel]

    cat_options = {c["nombre"]: c["id"] for c in categorias}
    cat_sel = st.selectbox("📁 Categoría", list(cat_options.keys()), key="ing_cat")
    cat_id = cat_options[cat_sel]

    productos = get_productos(cat_id)
    if not productos:
        st.warning("⚠️ No hay productos en esta categoría")
        return
    
    prod_options = {p["nombre"]: p["id"] for p in productos}
    prod_sel = st.selectbox("🏷️ Producto", list(prod_options.keys()), key="ing_prod")
    producto_id = prod_options[prod_sel]

    with st.form("form_ingreso"):
        cantidad = st.number_input("📦 Cantidad", min_value=0.001, step=0.5, format="%.3f")
        
        prov_options = {p["nombre"]: p["id"] for p in proveedores}
        if prov_options:
            prov_sel = st.selectbox("🏭 Proveedor", ["Sin proveedor"] + list(prov_options.keys()))
            proveedor_id = prov_options[prov_sel] if prov_sel != "Sin proveedor" else None
        else:
            proveedor_id = None

        observaciones = st.text_area("📝 Observaciones")
        archivo_remito = st.file_uploader("📎 Remito (PDF)", type=["pdf"], key="remito_ingreso")

        if st.form_submit_button("✅ Registrar Ingreso", use_container_width=True):
            if cantidad <= 0:
                st.error("La cantidad debe ser mayor a 0")
                return

            try:
                with st.spinner("Registrando..."):
                    now = datetime.now()
                    payload = {
                        "tipo": "ingreso",
                        "producto_id": producto_id,
                        "establecimiento_id": establecimiento_id,
                        "cantidad": float(cantidad),
                        "fecha": now.isoformat(),
                        "proveedor_id": proveedor_id,
                        "observaciones": observaciones,
                        "usuario_id": st.session_state.get("user_id"),
                    }
                    resultado = supabase.table("movimientos").insert(payload).execute()
                    movimiento_id = resultado.data[0]["id"] if resultado.data else None

                    if movimiento_id and archivo_remito:
                        subir_remito_pdf(archivo_remito, movimiento_id, st.session_state.get("user_id"), establecimiento_id)

                    get_movimientos.clear() if hasattr(get_movimientos, "clear") else None
                    st.toast("✅ Ingreso registrado!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)[:200]}")

# ══════════════════════════════════════════════════════════════
# NUEVO EGRESO
# ══════════════════════════════════════════════════════════════

def pagina_egreso():
    st.markdown('<div class="title-bubble"><h1>📤 Registrar Egreso</h1></div>', unsafe_allow_html=True)

    establecimientos = get_establecimientos()
    categorias = get_categorias()

    if not establecimientos:
        st.warning("⚠️ No hay establecimientos cargados")
        return

    estab_options = {e["nombre"]: e["id"] for e in establecimientos}
    estab_sel = st.selectbox("🏢 Establecimiento", list(estab_options.keys()), key="eg_estab")
    establecimiento_id = estab_options[estab_sel]

    cat_options = {c["nombre"]: c["id"] for c in categorias}
    cat_sel = st.selectbox("📁 Categoría", list(cat_options.keys()), key="eg_cat")
    cat_id = cat_options[cat_sel]

    productos = get_productos(cat_id)
    if not productos:
        st.warning("⚠️ No hay productos en esta categoría")
        return
    
    prod_options = {p["nombre"]: p["id"] for p in productos}
    prod_sel = st.selectbox("🏷️ Producto", list(prod_options.keys()), key="eg_prod")
    producto_id = prod_options[prod_sel]

    with st.form("form_egreso"):
        cantidad = st.number_input("📦 Cantidad", min_value=0.001, step=0.5, format="%.3f")
        observaciones = st.text_area("📝 Observaciones")
        archivo_remito = st.file_uploader("📎 Remito (PDF)", type=["pdf"], key="remito_egreso")

        if st.form_submit_button("✅ Registrar Egreso", use_container_width=True):
            if cantidad <= 0:
                st.error("La cantidad debe ser mayor a 0")
                return

            # Validar stock
            stock_actual_df = get_stock_por_producto(establecimiento_id)
            if not stock_actual_df.empty:
                prod_stock = stock_actual_df[stock_actual_df["producto_id"] == producto_id]
                if not prod_stock.empty and prod_stock.iloc[0]["stock"] < cantidad:
                    st.error(f"Stock insuficiente. Disponible: {prod_stock.iloc[0]['stock']:.2f}")
                    return

            try:
                with st.spinner("Registrando..."):
                    now = datetime.now()
                    payload = {
                        "tipo": "egreso",
                        "producto_id": producto_id,
                        "establecimiento_id": establecimiento_id,
                        "cantidad": float(cantidad),
                        "fecha": now.isoformat(),
                        "observaciones": observaciones,
                        "usuario_id": st.session_state.get("user_id"),
                    }
                    resultado = supabase.table("movimientos").insert(payload).execute()
                    movimiento_id = resultado.data[0]["id"] if resultado.data else None

                    if movimiento_id and archivo_remito:
                        subir_remito_pdf(archivo_remito, movimiento_id, st.session_state.get("user_id"), establecimiento_id)

                    st.toast("✅ Egreso registrado!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)[:200]}")

# ══════════════════════════════════════════════════════════════
# HISTORIAL
# ══════════════════════════════════════════════════════════════

def pagina_historial():
    st.markdown('<div class="title-bubble"><h1>📋 Historial de Movimientos</h1></div>', unsafe_allow_html=True)

    movimientos = get_movimientos(estab_filter(), limit=5000)

    if not movimientos:
        st.info("💡 Sin movimientos registrados")
        return

    df = pd.DataFrame(movimientos)
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"])
        df = df.sort_values("fecha", ascending=False)

    df["producto_nombre"] = df["productos"].apply(lambda x: x.get("nombre", "") if isinstance(x, dict) else "")
    df["establecimiento_nombre"] = df["establecimientos"].apply(lambda x: x.get("nombre", "") if isinstance(x, dict) else "")
    df["fecha_str"] = df["fecha"].dt.strftime("%d/%m/%Y %H:%M")

    display_df = df[["fecha_str", "tipo", "establecimiento_nombre", "producto_nombre", "cantidad", "observaciones"]].copy()
    display_df.columns = ["Fecha", "Tipo", "Establecimiento", "Producto", "Cantidad", "Observaciones"]

    render_tabla_html(display_df)

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════

def sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <div class="sidebar-logo-oval">
                <img src="https://raw.githubusercontent.com/marcasosguemes-cell/Stock-SECCO-AGRO/main/Logo.png" class="sidebar-logo">
            </div>
            <h1>Stock Agrícola</h1>
        </div>
        """, unsafe_allow_html=True)

        perfil = st.session_state.get("perfil", {})
        rol = st.session_state.get("rol", "")

        st.markdown(f"""
        <div style="background:rgba(212,160,23,0.15); border-radius:10px; padding:0.8rem; margin-bottom:1rem; text-align:center;">
            👤 {perfil.get('nombre', 'Usuario')}<br>
            <span style="font-size:0.8rem; color:#d4a017;">{'Admin' if rol == 'admin' else 'Operador'}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📌 MENÚ")

        paginas_menu = [
            ("📊", "Dashboard"),
            ("📥", "Nuevo Ingreso"),
            ("📤", "Nuevo Egreso"),
            ("📋", "Historial"),
        ]

        pagina_actual = st.session_state.get("pagina", "Dashboard")

        for emoji, nombre in paginas_menu:
            if st.button(f"{emoji}  {nombre}", key=f"nav_{nombre}"):
                st.session_state["pagina"] = nombre
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Cerrar sesión"):
            logout()

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    if not check_auth():
        login()
        return

    if not verificar_perfil():
        return

    sidebar()

    pagina = st.session_state.get("pagina", "Dashboard")
    
    if pagina == "Dashboard":
        pagina_dashboard()
    elif pagina == "Nuevo Ingreso":
        pagina_ingreso()
    elif pagina == "Nuevo Egreso":
        pagina_egreso()
    elif pagina == "Historial":
        pagina_historial()
    else:
        pagina_dashboard()

    st.markdown(f"""
    <div class="footer">
        <p>🌾 Sistema de Control de Stock Agrícola | SECCO AGRO</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
