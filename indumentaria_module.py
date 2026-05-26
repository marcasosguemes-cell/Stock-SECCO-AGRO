# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO INDUMENTARIA — indumentaria_module.py
# Integra con app.py existente. Solo acceso admin.
# Supabase tables requeridas:
#   indum_personal     (id, numero, firma, nombre, ubicacion, funcion, talle_bombacha,
#                       talle_camisa_grafa, talle_botin, talle_botas_lluvia,
#                       talle_equipo_lluvia, talle_mameluco, talle_poncho,
#                       talle_campera_lona, talle_campera_abrigo, talle_buzo_polar,
#                       talle_chaleco, talle_chomba, talle_pantalon_cargo,
#                       talle_camisa_blanca, created_at, updated_at)
#   indum_asignaciones (id, personal_id, prenda, cantidad, temporada, created_at)
#   indum_stock        (id, prenda, talle, cantidad, deposito, observacion, updated_at)
#   indum_cotizaciones (id, prenda, proveedor, marca, precio_sin_iva, precio_con_iva,
#                       forma_pago, plazo_dias, created_at, temporada)
# ══════════════════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from zoneinfo import ZoneInfo

# ── Constantes ────────────────────────────────────────────────────────────────
FIRMAS    = ["FORT", "IND", "LTDA"]
TEMPORADA = "2026"

PRENDAS = [
    "BOMBACHA", "CAMISA DE GRAFA", "BOTINES",
    "BOTAS LLUVIA", "EQUIPO DE LLUVIA", "MAMELUCO",
    "PONCHO RESERO", "CAMPERA LONA", "CAMPERA ABRIGO",
    "BUZO POLAR", "CHALECO", "CHOMBA",
    "PANTALON CARGO", "CAMISA BLANCA",
]

TALLE_COLS = {
    "BOMBACHA":        "talle_bombacha",
    "CAMISA DE GRAFA": "talle_camisa_grafa",
    "BOTINES":         "talle_botin",
    "BOTAS LLUVIA":    "talle_botas_lluvia",
    "EQUIPO DE LLUVIA":"talle_equipo_lluvia",
    "MAMELUCO":        "talle_mameluco",
    "PONCHO RESERO":   "talle_poncho",
    "CAMPERA LONA":    "talle_campera_lona",
    "CAMPERA ABRIGO":  "talle_campera_abrigo",
    "BUZO POLAR":      "talle_buzo_polar",
    "CHALECO":         "talle_chaleco",
    "CHOMBA":          "talle_chomba",
    "PANTALON CARGO":  "talle_pantalon_cargo",
    "CAMISA BLANCA":   "talle_camisa_blanca",
}

TALLES_NUMERICOS  = ["38","39","40","41","42","43","44","45","46","48","50","52","54","56","58","60"]
TALLES_LETRAS     = ["XS","S","M","L","XL","XXL","XXXL","3XL","4XL"]
TALLES_TODOS      = TALLES_NUMERICOS + TALLES_LETRAS + ["ÚNICO"]
TALLES_ESPECIALES = ["XL", "E", "ÚNICO"]  # poncho, equipo

PROVEEDORES_CONOCIDOS = [
    "Pampero", "Ombu Oz.", "Ombu", "Criolla", "TKW", "El Galpón / Kenay SA",
    "Nueva Regina", "Alibre - SECCO", "Arsenio", "Bladi", "Boro", "Gaucho",
    "NR", "Propia", "Lembu", "Work", "SP", "Lynner", "Yuyos", "Amarillo", "Otro",
]

# ── Helpers ───────────────────────────────────────────────────────────────────
def _now():
    return datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).replace(tzinfo=None)

def _fmt_ars(v):
    try:
        return f"${v:,.0f}".replace(",", ".")
    except Exception:
        return str(v)

@st.cache_data(ttl=60)
def _load_personal():
    try:
        r = st.session_state["_sb"].table("indum_personal").select("*").order("numero").execute()
        return pd.DataFrame(r.data) if r.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error cargando personal: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def _load_asignaciones(temporada=TEMPORADA):
    try:
        r = (st.session_state["_sb"].table("indum_asignaciones")
             .select("*").eq("temporada", temporada).execute())
        return pd.DataFrame(r.data) if r.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error cargando asignaciones: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def _load_stock():
    try:
        r = st.session_state["_sb"].table("indum_stock").select("*").execute()
        return pd.DataFrame(r.data) if r.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error cargando stock: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def _load_cotizaciones(temporada=TEMPORADA):
    try:
        r = (st.session_state["_sb"].table("indum_cotizaciones")
             .select("*").eq("temporada", temporada).execute())
        return pd.DataFrame(r.data) if r.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error cargando cotizaciones: {e}")
        return pd.DataFrame()

def _clear_cache():
    _load_personal.clear()
    _load_asignaciones.clear()
    _load_stock.clear()
    _load_cotizaciones.clear()

def _card(icon, title, value, subtitle="", color="var(--gold)"):
    st.markdown(f"""
    <div style="
        background:linear-gradient(145deg,rgba(55,55,62,0.92),rgba(40,40,50,0.97));
        border:1px solid rgba(212,160,23,0.35);
        border-radius:18px; padding:1.3rem 1.1rem;
        text-align:center; box-shadow:0 4px 16px rgba(0,0,0,0.3);">
      <div style="font-size:2rem;line-height:1;margin-bottom:0.4rem;">{icon}</div>
      <div style="font-size:0.7rem;color:var(--gold);text-transform:uppercase;
                  letter-spacing:0.12em;font-weight:700;margin-bottom:0.3rem;">{title}</div>
      <div style="font-family:'Playfair Display',serif;font-size:2.1rem;
                  font-weight:700;color:{color};line-height:1;">{value}</div>
      {f'<div style="font-size:0.75rem;color:#a0a0b0;margin-top:0.3rem;">{subtitle}</div>' if subtitle else ''}
    </div>""", unsafe_allow_html=True)

def _section_header(title, subtitle=""):
    st.markdown(f"""
    <div style="border-left:3px solid var(--gold);padding:0.4rem 0 0.4rem 1rem;
                margin:1.5rem 0 1rem 0;">
      <div style="font-family:'Playfair Display',serif;font-size:1.25rem;
                  font-weight:700;color:#f0f0f5;">{title}</div>
      {f'<div style="font-size:0.82rem;color:#a0a0b0;margin-top:2px;">{subtitle}</div>' if subtitle else ''}
    </div>""", unsafe_allow_html=True)

def _badge(text, color="#d4a017", bg="rgba(212,160,23,0.15)"):
    return (f'<span style="background:{bg};color:{color};border:1px solid {color}33;'
            f'border-radius:99px;padding:2px 10px;font-size:0.75rem;font-weight:700;">{text}</span>')


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — TALLES DEL PERSONAL
# ══════════════════════════════════════════════════════════════════════════════
def tab_talles():
    _section_header("Talles del Personal", "Registro de talles por prenda para cada empleado")

    df = _load_personal()

    # ── Alta / Edición ────────────────────────────────────────────────────────
    with st.expander("➕  Agregar / Editar empleado", expanded=False):
        with st.form("form_personal", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                numero = st.number_input("N°", min_value=1, step=1)
                firma  = st.selectbox("Firma", FIRMAS)
            with c2:
                nombre    = st.text_input("Nombre completo")
                ubicacion = st.text_input("Ubicación / Establecimiento")
            with c3:
                funcion = st.text_input("Función / Cargo")

            st.markdown("##### Talles por prenda")
            cols_t = st.columns(4)
            talles_ingreso = {}
            for i, (prenda, col_key) in enumerate(TALLE_COLS.items()):
                opts = ["—"] + TALLES_TODOS
                talles_ingreso[col_key] = cols_t[i % 4].selectbox(
                    prenda, opts, key=f"t_{col_key}")

            submitted = st.form_submit_button("💾  Guardar empleado", use_container_width=True)
            if submitted:
                if not nombre.strip():
                    st.warning("Completá el nombre del empleado.")
                else:
                    payload = {
                        "numero": int(numero), "firma": firma,
                        "nombre": nombre.strip(), "ubicacion": ubicacion.strip(),
                        "funcion": funcion.strip(),
                        "updated_at": _now().isoformat(),
                    }
                    for k, v in talles_ingreso.items():
                        payload[k] = v if v != "—" else None
                    try:
                        sb = st.session_state["_sb"]
                        existing = (sb.table("indum_personal")
                                    .select("id").eq("numero", int(numero)).execute())
                        if existing.data:
                            sb.table("indum_personal").update(payload).eq("numero", int(numero)).execute()
                            st.success(f"✅ Empleado #{numero} actualizado.")
                        else:
                            payload["created_at"] = _now().isoformat()
                            sb.table("indum_personal").insert(payload).execute()
                            st.success(f"✅ Empleado #{numero} registrado.")
                        _clear_cache()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ── Tabla ─────────────────────────────────────────────────────────────────
    if df.empty:
        st.info("Sin registros. Usá el formulario para cargar empleados.")
        return

    # Filtros
    fc1, fc2, fc3 = st.columns(3)
    f_firma    = fc1.multiselect("Firma", FIRMAS, default=FIRMAS, key="filt_firma_t")
    f_busqueda = fc2.text_input("Buscar nombre / función", key="filt_nombre_t")
    f_ubicacion= fc3.multiselect("Ubicación", sorted(df["ubicacion"].dropna().unique().tolist()),
                                  key="filt_ubic_t")

    mask = df["firma"].isin(f_firma) if f_firma else pd.Series([True]*len(df))
    if f_busqueda:
        mask &= (df["nombre"].str.contains(f_busqueda, case=False, na=False) |
                 df["funcion"].str.contains(f_busqueda, case=False, na=False))
    if f_ubicacion:
        mask &= df["ubicacion"].isin(f_ubicacion)
    df_vis = df[mask].copy()

    # Métricas rápidas
    mc = st.columns(4)
    mc[0].metric("Total personal", len(df))
    mc[1].metric("FORT", len(df[df.firma=="FORT"]))
    mc[2].metric("IND",  len(df[df.firma=="IND"]))
    mc[3].metric("LTDA", len(df[df.firma=="LTDA"]))

    # Columnas a mostrar
    cols_show = ["numero","firma","nombre","ubicacion","funcion"] + list(TALLE_COLS.values())
    cols_available = [c for c in cols_show if c in df_vis.columns]
    df_show = df_vis[cols_available].fillna("—")
    df_show.columns = (["N°","Firma","Nombre","Ubicación","Función"] +
                       list(TALLE_COLS.keys()))[:len(cols_available)]

    st.dataframe(df_show, use_container_width=True, hide_index=True,
                 column_config={
                     "N°": st.column_config.NumberColumn(width="small"),
                     "Firma": st.column_config.TextColumn(width="small"),
                 })

    # Exportar
    if st.button("⬇️  Exportar CSV", key="exp_talles"):
        csv = df_show.to_csv(index=False).encode()
        st.download_button("Descargar CSV", csv, "talles_personal.csv",
                           "text/csv", key="dl_talles")

    # Borrar
    with st.expander("🗑️  Eliminar empleado", expanded=False):
        nums = df["numero"].tolist()
        n_del = st.selectbox("N° empleado a eliminar", nums, key="del_pers")
        nom_del = df[df.numero==n_del]["nombre"].values[0] if len(df[df.numero==n_del]) else "?"
        st.warning(f"Vas a eliminar: #{n_del} — {nom_del}")
        if st.button("Confirmar eliminación", key="btn_del_pers"):
            try:
                st.session_state["_sb"].table("indum_personal").delete().eq("numero",n_del).execute()
                st.success("Eliminado.")
                _clear_cache(); st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ASIGNACIONES
# ══════════════════════════════════════════════════════════════════════════════
def tab_asignaciones():
    _section_header("Asignaciones", f"Prendas asignadas a cada empleado — Temporada {TEMPORADA}")

    df_pers = _load_personal()
    df_asig = _load_asignaciones()

    # ── Alta de asignación ────────────────────────────────────────────────────
    with st.expander("➕  Registrar asignación", expanded=False):
        if df_pers.empty:
            st.warning("Primero cargá empleados en la pestaña 'Talles'.")
        else:
            with st.form("form_asig", clear_on_submit=True):
                c1, c2, c3, c4 = st.columns(4)
                opciones_pers = {
                    f"#{r.numero} — {r.nombre} ({r.firma})": r.id
                    for _, r in df_pers.iterrows()
                }
                sel_pers  = c1.selectbox("Empleado", list(opciones_pers.keys()), key="asig_pers")
                prenda    = c2.selectbox("Prenda", PRENDAS, key="asig_prenda")
                cantidad  = c3.number_input("Cantidad", min_value=1, max_value=10, value=1)
                temporada = c4.text_input("Temporada", value=TEMPORADA)

                if st.form_submit_button("💾  Guardar asignación", use_container_width=True):
                    try:
                        st.session_state["_sb"].table("indum_asignaciones").insert({
                            "personal_id": opciones_pers[sel_pers],
                            "prenda": prenda, "cantidad": int(cantidad),
                            "temporada": temporada,
                            "created_at": _now().isoformat(),
                        }).execute()
                        st.success("✅ Asignación registrada.")
                        _clear_cache(); st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    if df_asig.empty or df_pers.empty:
        st.info("Sin asignaciones registradas para esta temporada.")
        return

    # ── Join personal + asignaciones ─────────────────────────────────────────
    df_join = df_asig.merge(
        df_pers[["id","numero","firma","nombre","ubicacion"]],
        left_on="personal_id", right_on="id", how="left", suffixes=("","_pers")
    )

    # ── Resumen por firma y prenda ────────────────────────────────────────────
    _section_header("Resumen por firma", "Unidades brutas asignadas")
    pivot = (df_join.groupby(["prenda","firma"])["cantidad"]
             .sum().unstack(fill_value=0).reset_index())
    for f in FIRMAS:
        if f not in pivot.columns:
            pivot[f] = 0
    pivot["TOTAL"] = pivot[FIRMAS].sum(axis=1)
    pivot = pivot.sort_values("TOTAL", ascending=False)

    st.dataframe(pivot.rename(columns={"prenda":"Prenda"}),
                 use_container_width=True, hide_index=True)

    # ── Detalle individual ────────────────────────────────────────────────────
    _section_header("Detalle por empleado")

    fc1, fc2 = st.columns(2)
    f_firma   = fc1.multiselect("Firma", FIRMAS, default=FIRMAS, key="filt_firma_a")
    f_prenda  = fc2.multiselect("Prenda", PRENDAS, key="filt_prenda_a")

    mask = df_join["firma"].isin(f_firma) if f_firma else pd.Series([True]*len(df_join))
    if f_prenda:
        mask &= df_join["prenda"].isin(f_prenda)
    df_vis = df_join[mask][["numero","firma","nombre","prenda","cantidad","temporada"]].copy()
    df_vis.columns = ["N°","Firma","Nombre","Prenda","Cant.","Temporada"]
    st.dataframe(df_vis, use_container_width=True, hide_index=True)

    # ── Gráfico ───────────────────────────────────────────────────────────────
    if not pivot.empty:
        fig = px.bar(pivot.melt(id_vars="prenda", value_vars=FIRMAS,
                                var_name="Firma", value_name="Unidades"),
                     x="prenda", y="Unidades", color="Firma",
                     color_discrete_map={"FORT":"#d4a017","IND":"#3b82f6","LTDA":"#22c55e"},
                     barmode="group", template="plotly_dark",
                     labels={"prenda":"Prenda"})
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#f0f0f5", height=340,
            legend=dict(bgcolor="rgba(40,40,50,0.8)", bordercolor="rgba(212,160,23,0.3)"),
            margin=dict(l=10, r=10, t=30, b=60),
            xaxis_tickangle=-35,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Exportar
    if st.button("⬇️  Exportar CSV asignaciones", key="exp_asig"):
        csv = df_vis.to_csv(index=False).encode()
        st.download_button("Descargar", csv, "asignaciones.csv", "text/csv", key="dl_asig")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — STOCK RESISTENCIA
# ══════════════════════════════════════════════════════════════════════════════
def tab_stock():
    _section_header("Stock en Resistencia", "Inventario disponible en depósito — por prenda y talle")

    df_stock = _load_stock()

    # ── Alta de stock ─────────────────────────────────────────────────────────
    with st.expander("➕  Registrar / actualizar stock", expanded=False):
        with st.form("form_stock", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns(4)
            prenda   = c1.selectbox("Prenda", PRENDAS, key="stk_prenda")
            talle    = c2.selectbox("Talle", TALLES_TODOS + ["E"], key="stk_talle")
            cantidad = c3.number_input("Cantidad", min_value=0, step=1)
            deposito = c4.text_input("Depósito", value="Rosario")
            obs      = st.text_input("Observación (calidad, uso, etc.)", key="stk_obs")

            if st.form_submit_button("💾  Guardar", use_container_width=True):
                try:
                    sb = st.session_state["_sb"]
                    existing = (sb.table("indum_stock")
                                .select("id").eq("prenda",prenda).eq("talle",talle)
                                .eq("deposito",deposito).execute())
                    payload = {
                        "prenda":prenda, "talle":talle, "cantidad":int(cantidad),
                        "deposito":deposito, "observacion":obs,
                        "updated_at":_now().isoformat(),
                    }
                    if existing.data:
                        sb.table("indum_stock").update(payload).eq("id",existing.data[0]["id"]).execute()
                        st.success("✅ Stock actualizado.")
                    else:
                        sb.table("indum_stock").insert(payload).execute()
                        st.success("✅ Stock registrado.")
                    _clear_cache(); st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    if df_stock.empty:
        st.info("Sin stock registrado. Cargá items con el formulario.")
        return

    # ── Métricas globales ─────────────────────────────────────────────────────
    total_units = df_stock["cantidad"].sum()
    prendas_con_stock = df_stock[df_stock.cantidad>0]["prenda"].nunique()
    mc = st.columns(3)
    with mc[0]: _card("🏭", "Unidades en depósito", f"{int(total_units):,}", "total acumulado")
    with mc[1]: _card("👕", "Prendas con stock", prendas_con_stock, f"de {len(PRENDAS)} totales")
    with mc[2]:
        prendas_sin = len(PRENDAS) - prendas_con_stock
        _card("⚠️", "Prendas sin stock", prendas_sin,
              "requieren compra", "#ef4444" if prendas_sin > 0 else "#22c55e")

    # ── Tabla pivot prenda × talle ────────────────────────────────────────────
    _section_header("Inventario por talle")

    f_prenda = st.multiselect("Filtrar prenda", PRENDAS, key="filt_stk_prenda")
    df_vis = df_stock.copy()
    if f_prenda:
        df_vis = df_vis[df_vis.prenda.isin(f_prenda)]

    pivot_stk = (df_vis.groupby(["prenda","talle"])["cantidad"]
                 .sum().unstack(fill_value=0).reset_index())

    # Ordenar columnas de talles razonablemente
    talles_presentes = [t for t in TALLES_TODOS if t in pivot_stk.columns]
    otras = [c for c in pivot_stk.columns if c not in ["prenda"] + talles_presentes]
    pivot_stk = pivot_stk[["prenda"] + talles_presentes + otras]
    pivot_stk.insert(1, "TOTAL", pivot_stk.iloc[:, 1:].sum(axis=1))
    pivot_stk = pivot_stk.rename(columns={"prenda":"Prenda"})

    # Colorear ceros
    def highlight_zero(val):
        if val == 0 or val == "0":
            return "color: #555570"
        return "color: #f0f0f5; font-weight: 600"

    st.dataframe(
        pivot_stk.style.map(highlight_zero, subset=pivot_stk.columns[1:]),
        use_container_width=True, hide_index=True,
    )

    # ── Gráfico ───────────────────────────────────────────────────────────────
    df_chart = df_vis[df_vis.cantidad > 0].groupby("prenda")["cantidad"].sum().reset_index()
    if not df_chart.empty:
        fig = px.bar(df_chart.sort_values("cantidad", ascending=True),
                     x="cantidad", y="prenda", orientation="h",
                     template="plotly_dark",
                     color="cantidad",
                     color_continuous_scale=[[0,"#3b3b4a"],[0.5,"#b87a0c"],[1,"#d4a017"]],
                     labels={"cantidad":"Unidades","prenda":"Prenda"})
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#f0f0f5", height=380,
            showlegend=False, coloraxis_showscale=False,
            margin=dict(l=10, r=20, t=20, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Exportar
    if st.button("⬇️  Exportar CSV stock", key="exp_stk"):
        csv = pivot_stk.to_csv(index=False).encode()
        st.download_button("Descargar", csv, "stock_resistencia.csv", "text/csv", key="dl_stk")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — COTIZACIONES POR PROVEEDOR
# ══════════════════════════════════════════════════════════════════════════════
def tab_cotizaciones():
    _section_header("Cotizaciones por Proveedor", f"Comparativo de precios por prenda — Temporada {TEMPORADA}")

    df_cot = _load_cotizaciones()

    # ── Alta ──────────────────────────────────────────────────────────────────
    with st.expander("➕  Cargar cotización", expanded=False):
        with st.form("form_cot", clear_on_submit=True):
            c1, c2 = st.columns(2)
            prenda    = c1.selectbox("Prenda", PRENDAS, key="cot_prenda")
            proveedor = c2.selectbox("Proveedor", PROVEEDORES_CONOCIDOS, key="cot_prov")

            c3, c4, c5 = st.columns(3)
            marca         = c3.text_input("Marca / modelo", key="cot_marca")
            precio_sin    = c4.number_input("Precio s/IVA $", min_value=0.0, format="%.2f")
            precio_con    = c5.number_input("Precio c/IVA $", min_value=0.0, format="%.2f",
                                             help="Si dejás 0 se calcula con IVA 21%")

            c6, c7, c8 = st.columns(3)
            forma_pago = c6.text_input("Forma de pago", placeholder="30 días / contado")
            plazo      = c7.number_input("Plazo entrega (días)", min_value=0, step=1)
            temporada  = c8.text_input("Temporada", value=TEMPORADA)

            if st.form_submit_button("💾  Guardar cotización", use_container_width=True):
                pc = precio_con if precio_con > 0 else round(precio_sin * 1.21, 2)
                try:
                    st.session_state["_sb"].table("indum_cotizaciones").insert({
                        "prenda":prenda, "proveedor":proveedor, "marca":marca,
                        "precio_sin_iva":precio_sin, "precio_con_iva":pc,
                        "forma_pago":forma_pago, "plazo_dias":int(plazo),
                        "temporada":temporada,
                        "created_at":_now().isoformat(),
                    }).execute()
                    st.success("✅ Cotización registrada.")
                    _clear_cache(); st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    if df_cot.empty:
        st.info("Sin cotizaciones. Cargá precios con el formulario.")
        return

    # ── Filtros ───────────────────────────────────────────────────────────────
    fc1, fc2 = st.columns(2)
    f_prenda = fc1.multiselect("Prenda", PRENDAS, key="filt_cot_prenda")
    f_prov   = fc2.multiselect("Proveedor",
                                sorted(df_cot["proveedor"].unique().tolist()),
                                key="filt_cot_prov")

    df_vis = df_cot.copy()
    if f_prenda: df_vis = df_vis[df_vis.prenda.isin(f_prenda)]
    if f_prov:   df_vis = df_vis[df_vis.proveedor.isin(f_prov)]

    # ── Tabla de comparación ──────────────────────────────────────────────────
    cols_show = ["prenda","proveedor","marca","precio_sin_iva","precio_con_iva",
                 "forma_pago","plazo_dias"]
    cols_available = [c for c in cols_show if c in df_vis.columns]
    df_show = df_vis[cols_available].copy()

    # Mejor precio por prenda
    if "precio_sin_iva" in df_show.columns:
        min_prices = df_vis.groupby("prenda")["precio_sin_iva"].min()
        df_show["mejor"] = df_show.apply(
            lambda r: "⭐" if r["precio_sin_iva"] == min_prices.get(r["prenda"], -1) else "",
            axis=1
        )

    df_show.columns = (["Prenda","Proveedor","Marca","Precio s/IVA","Precio c/IVA",
                         "Forma de pago","Plazo días","Mejor"][:len(df_show.columns)])

    st.dataframe(
        df_show.style.format({"Precio s/IVA": "${:,.0f}", "Precio c/IVA": "${:,.0f}"},
                              na_rep="—"),
        use_container_width=True, hide_index=True,
    )

    # ── Gráfico comparativo ───────────────────────────────────────────────────
    if "precio_sin_iva" in df_vis.columns and not df_vis.empty:
        fig = px.bar(df_vis.sort_values("precio_sin_iva"),
                     x="proveedor", y="precio_sin_iva", color="prenda",
                     facet_col="prenda", facet_col_wrap=4,
                     template="plotly_dark",
                     labels={"precio_sin_iva":"Precio s/IVA $","proveedor":"Proveedor"},
                     height=500)
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#f0f0f5", showlegend=False,
            margin=dict(l=10, r=10, t=50, b=80),
        )
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1],
                                                     font_size=10))
        fig.update_xaxes(tickangle=-40, tickfont_size=9)
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — COSTO MÁS BARATO (NECESIDADES NETAS)
# ══════════════════════════════════════════════════════════════════════════════
def tab_costo_barato():
    _section_header("Costo más barato", "Necesidades netas · Mejor precio por prenda")

    df_asig = _load_asignaciones()
    df_stk  = _load_stock()
    df_pers = _load_personal()
    df_cot  = _load_cotizaciones()

    if df_asig.empty or df_pers.empty:
        st.info("Cargá asignaciones y cotizaciones para ver este análisis.")
        return

    # ── Calcular demanda bruta por prenda ─────────────────────────────────────
    dem_bruta = df_asig.groupby("prenda")["cantidad"].sum().to_dict()

    # ── Calcular stock disponible (solo talles que coincidan con demanda) ──────
    # Acá lo simplificamos con total de stock por prenda
    stk_total = df_stk.groupby("prenda")["cantidad"].sum().to_dict() if not df_stk.empty else {}

    # ── Mejor precio por prenda ───────────────────────────────────────────────
    if not df_cot.empty:
        mejor_precio = (df_cot.groupby("prenda")
                        .apply(lambda g: g.loc[g["precio_sin_iva"].idxmin()])
                        .reset_index(drop=True)
                        [["prenda","proveedor","marca","precio_sin_iva","precio_con_iva",
                          "forma_pago","plazo_dias"]])
    else:
        mejor_precio = pd.DataFrame()

    # ── Tabla resumen ─────────────────────────────────────────────────────────
    rows = []
    total_sin_iva = 0
    for prenda in PRENDAS:
        bruta = dem_bruta.get(prenda, 0)
        stk   = stk_total.get(prenda, 0)
        neta  = max(0, bruta - stk)
        row   = {"Prenda": prenda, "Bruta": bruta, "Stock": stk, "A Comprar": neta}
        if not mejor_precio.empty and prenda in mejor_precio.prenda.values:
            mp = mejor_precio[mejor_precio.prenda == prenda].iloc[0]
            row["Proveedor"]    = mp.get("proveedor","—")
            row["Marca"]        = mp.get("marca","—")
            precio_u            = mp.get("precio_sin_iva",0) or 0
            row["Precio unit $"]= precio_u
            row["Total s/IVA $"]= neta * precio_u
            total_sin_iva      += neta * precio_u
        else:
            row["Proveedor"] = "—"; row["Marca"] = "—"
            row["Precio unit $"] = None; row["Total s/IVA $"] = None
        rows.append(row)

    df_resumen = pd.DataFrame(rows)
    iva      = total_sin_iva * 0.21
    total_c  = total_sin_iva + iva

    # ── Cards totales ─────────────────────────────────────────────────────────
    mc = st.columns(3)
    with mc[0]: _card("🏷️", "Total s/IVA",   _fmt_ars(total_sin_iva))
    with mc[1]: _card("📄", "IVA 21%",        _fmt_ars(iva))
    with mc[2]: _card("💰", "TOTAL c/IVA",    _fmt_ars(total_c), color="#22c55e")

    st.markdown("")

    # ── Tabla principal ───────────────────────────────────────────────────────
    def highlight_neta(val):
        if val == 0: return "color:#555570"
        return "color:#f0f0f5;font-weight:600"

    fmt = {"Precio unit $":"${:,.0f}", "Total s/IVA $":"${:,.0f}"}
    st.dataframe(
        df_resumen.style
            .format(fmt, na_rep="—")
            .map(highlight_neta, subset=["A Comprar"]),
        use_container_width=True, hide_index=True,
    )

    # ── Gráfico torta distribución importe ────────────────────────────────────
    df_chart = df_resumen[df_resumen["Total s/IVA $"].notna() &
                           (df_resumen["Total s/IVA $"] > 0)].copy()
    if not df_chart.empty:
        fig = px.pie(df_chart, values="Total s/IVA $", names="Prenda",
                     template="plotly_dark",
                     color_discrete_sequence=px.colors.sequential.Aggrnyl_r,
                     hole=0.45)
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#f0f0f5", height=360,
            legend=dict(font_size=10, bgcolor="rgba(40,40,50,0.8)"),
            margin=dict(l=10, r=10, t=30, b=10),
        )
        fig.update_traces(textfont_size=11, textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    # Exportar
    if st.button("⬇️  Exportar análisis de costos", key="exp_costos"):
        csv = df_resumen.to_csv(index=False).encode()
        st.download_button("Descargar", csv, "costo_compra.csv", "text/csv", key="dl_costos")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — COSTO POR FIRMA
# ══════════════════════════════════════════════════════════════════════════════
def tab_costo_firma():
    _section_header("Distribución de pago por firma",
                     "Importe s/IVA e IVA por firma según asignaciones netas")

    df_asig = _load_asignaciones()
    df_pers = _load_personal()
    df_stk  = _load_stock()
    df_cot  = _load_cotizaciones()

    if df_asig.empty or df_pers.empty:
        st.info("Cargá asignaciones para ver la distribución.")
        return

    # Join
    df_join = df_asig.merge(
        df_pers[["id","firma"]], left_on="personal_id", right_on="id", how="left"
    )

    # Demanda neta por firma × prenda
    dem_firma = (df_join.groupby(["prenda","firma"])["cantidad"]
                 .sum().unstack(fill_value=0).reset_index())
    for f in FIRMAS:
        if f not in dem_firma.columns:
            dem_firma[f] = 0

    # Stock total por prenda (simplificado: descuenta proporcionalmente)
    stk_total = df_stk.groupby("prenda")["cantidad"].sum().to_dict() if not df_stk.empty else {}

    # Mejor precio
    if not df_cot.empty:
        mejor = (df_cot.groupby("prenda")
                 .apply(lambda g: g.loc[g["precio_sin_iva"].idxmin()])
                 [["prenda","precio_sin_iva","proveedor","marca"]]
                 .reset_index(drop=True))
    else:
        mejor = pd.DataFrame()

    rows = []
    totales_firma = {f: 0.0 for f in FIRMAS}

    for _, row in dem_firma.iterrows():
        prenda    = row["prenda"]
        bruta_tot = sum(row.get(f,0) for f in FIRMAS)
        stk       = stk_total.get(prenda, 0)
        neta_tot  = max(0, bruta_tot - stk)

        # Distribuir stock proporcionalmente
        neta_firma = {}
        if bruta_tot > 0:
            for f in FIRMAS:
                prop = row.get(f,0) / bruta_tot
                neta_firma[f] = round(neta_tot * prop, 2)
        else:
            neta_firma = {f:0 for f in FIRMAS}

        # Precio
        precio = 0
        prov = "—"; marca = "—"
        if not mejor.empty and prenda in mejor.prenda.values:
            mp = mejor[mejor.prenda==prenda].iloc[0]
            precio = mp.get("precio_sin_iva",0) or 0
            prov   = mp.get("proveedor","—")
            marca  = mp.get("marca","—")

        row_out = {"Prenda":prenda, "Proveedor":prov, "Precio unit $":precio}
        for f in FIRMAS:
            u = neta_firma[f]
            imp = u * precio
            row_out[f"{f} u."] = round(u,1)
            row_out[f"{f} $"]  = imp
            totales_firma[f]  += imp
        row_out["Total u."] = neta_tot
        row_out["Total $"]  = neta_tot * precio
        rows.append(row_out)

    df_out = pd.DataFrame(rows)

    # ── Cards por firma ───────────────────────────────────────────────────────
    iva_firma = {f: totales_firma[f]*0.21 for f in FIRMAS}
    total_c   = {f: totales_firma[f]+iva_firma[f] for f in FIRMAS}
    gran_total= sum(total_c.values())

    mc = st.columns(3)
    colores = {"FORT":"#d4a017","IND":"#3b82f6","LTDA":"#22c55e"}
    for i, f in enumerate(FIRMAS):
        with mc[i]:
            pct = total_c[f]/gran_total*100 if gran_total else 0
            _card("🏢", f"TOTAL c/IVA — {f}", _fmt_ars(total_c[f]),
                  f"{pct:.1f}% del total", colores[f])

    st.markdown(f"""
    <div style="text-align:center;padding:0.8rem;margin:1rem 0;
                background:linear-gradient(135deg,rgba(212,160,23,0.12),rgba(180,120,0,0.08));
                border:1px solid rgba(212,160,23,0.35);border-radius:14px;">
      <span style="font-size:0.78rem;color:var(--gold);text-transform:uppercase;
                   letter-spacing:0.1em;font-weight:700;">Gran Total c/IVA</span><br>
      <span style="font-family:'Playfair Display',serif;font-size:2.2rem;
                   font-weight:700;color:#f0f0f5;">{_fmt_ars(gran_total)}</span>
    </div>""", unsafe_allow_html=True)

    # ── Tabla detalle ─────────────────────────────────────────────────────────
    _section_header("Detalle por prenda y firma")
    fmt_cols = {c: "${:,.0f}" for c in df_out.columns if "$" in c}
    fmt_cols["Precio unit $"] = "${:,.0f}"
    st.dataframe(
        df_out.style.format(fmt_cols, na_rep="—"),
        use_container_width=True, hide_index=True,
    )

    # ── Resumen subtotales ────────────────────────────────────────────────────
    _section_header("Resumen s/IVA · IVA · c/IVA por firma")
    resumen_rows = []
    for f in FIRMAS:
        resumen_rows.append({
            "Firma":f,
            "Subtotal s/IVA": totales_firma[f],
            "IVA 21%": iva_firma[f],
            "Total c/IVA": total_c[f],
            "% del total": f"{total_c[f]/gran_total*100:.1f}%" if gran_total else "0%",
        })
    df_res = pd.DataFrame(resumen_rows)
    st.dataframe(
        df_res.style.format({
            "Subtotal s/IVA":"${:,.0f}","IVA 21%":"${:,.0f}","Total c/IVA":"${:,.0f}"
        }),
        use_container_width=True, hide_index=True,
    )

    # ── Gráfico barras apiladas ───────────────────────────────────────────────
    fig = go.Figure()
    prendas = df_out["Prenda"].tolist()
    for f, color in colores.items():
        fig.add_trace(go.Bar(
            name=f, x=prendas,
            y=df_out[f"{f} $"].fillna(0).tolist(),
            marker_color=color, opacity=0.88,
        ))
    fig.update_layout(
        barmode="stack", template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#f0f0f5", height=380,
        legend=dict(bgcolor="rgba(40,40,50,0.8)"),
        margin=dict(l=10, r=10, t=20, b=80),
        xaxis_tickangle=-35,
        yaxis_tickprefix="$",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Exportar
    if st.button("⬇️  Exportar distribución por firma", key="exp_firma"):
        csv = df_out.to_csv(index=False).encode()
        st.download_button("Descargar", csv, "costo_por_firma.csv", "text/csv", key="dl_firma")


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA PRINCIPAL DEL MÓDULO
# ══════════════════════════════════════════════════════════════════════════════
def pagina_indumentaria(supabase_client):
    """
    Punto de entrada del módulo Indumentaria.
    supabase_client: el cliente Supabase ya instanciado en app.py
    """
    # Pasar el cliente al estado de sesión para que los helpers lo usen
    st.session_state["_sb"] = supabase_client

    # Botón volver
    if st.button("← Volver al inicio", key="btn_back_indum"):
        st.session_state["modulo"] = "hub"
        st.rerun()

    # Encabezado
    st.markdown("""
    <div style="
        border-bottom:1px solid rgba(212,160,23,0.4);
        padding-bottom:1rem; margin-bottom:1.5rem;">
      <div style="font-family:'Playfair Display',serif;font-size:1.9rem;
                  font-weight:700;color:#f0f0f5;margin:0;">
        🧥 Gestión de Indumentaria
      </div>
      <div style="font-size:0.88rem;color:#a0a0b0;margin-top:4px;">
        Indumentaria de trabajo 2026 &nbsp;·&nbsp;
        Agropecuaria Fortuna SA &nbsp;/&nbsp;
        Industrias Juan F. Secco SA &nbsp;/&nbsp;
        Juan F. Secco Ltda. SA
      </div>
    </div>""", unsafe_allow_html=True)

    # Tabs
    t1, t2, t3, t4, t5, t6 = st.tabs([
        "👤 Talles del Personal",
        "📋 Asignaciones",
        "🏭 Stock Resistencia",
        "💲 Cotizaciones",
        "🏷️ Costo más barato",
        "🏢 Costo por Firma",
    ])
    with t1: tab_talles()
    with t2: tab_asignaciones()
    with t3: tab_stock()
    with t4: tab_cotizaciones()
    with t5: tab_costo_barato()
    with t6: tab_costo_firma()
