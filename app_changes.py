# ══════════════════════════════════════════════════════════════════════════════
# CAMBIOS A APLICAR EN app.py  —  3 bloques, marcados con # <<< CAMBIO >>>
#
# 1. pantalla_hub()   → agregar tarjeta Indumentaria (solo admin)
# 2. main()           → agregar enrutamiento modulo == "indumentaria"
# 3. pagina_maquinaria() ya existe, no tocar
# ══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# CAMBIO 1 — En pantalla_hub(), reemplazar el bloque de html de las cards:
#
#   <div class="hub-cards">   (actualmente 2 tarjetas)
#
# por este bloque de 3 tarjetas:
# ─────────────────────────────────────────────────────────────────────────────

NUEVO_HUB_CARDS_HTML = """
    <div class="hub-cards">
        <div class="hub-card">
            <div class="hub-card-icon">📦</div>
            <div class="hub-card-title">Gestión de Stock</div>
            <div class="hub-card-desc">Control de ingresos, egresos, inventario y reportes por establecimiento.</div>
        </div>
        <div class="{maq_cls}">
            <div class="hub-card-icon">⚙️</div>
            <div class="hub-card-title">Gestión de Maquinaria</div>
            <div class="hub-card-desc">Seguimiento de mantenimiento preventivo y correctivo de equipos.</div>
            {maq_badge}
        </div>
        <div class="{ind_cls}">
            <div class="hub-card-icon">🧥</div>
            <div class="hub-card-title">Indumentaria</div>
            <div class="hub-card-desc">Talles, asignaciones, stock, cotizaciones y distribución de costos por firma.</div>
            {ind_badge}
        </div>
    </div>
"""

# y el CSS del grid cambia de 2 a 3 columnas:
NUEVO_HUB_CSS_GRID = """
    .hub-cards {
        display:grid;
        grid-template-columns: 300px 300px 300px;
        gap:2rem;
    }
    div[data-testid="stHorizontalBlock"] {
        display:grid !important;
        grid-template-columns: 300px 300px 300px !important;
        gap:2rem !important;
        margin-top:-12px !important;
        padding:0 !important;
        width:fit-content !important;
        margin-left:auto !important;
        margin-right:auto !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        width:300px !important;
        padding:0 !important;
        min-width:0 !important;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button {
        border-radius:0 0 22px 22px !important;
        height:54px !important;
        font-size:0.95rem !important;
        font-weight:700 !important;
        margin:0 !important;
        padding:0 !important;
        width:300px !important;
        letter-spacing:0.03em !important;
        box-shadow:0 6px 18px rgba(0,0,0,0.3) !important;
    }
"""


# ─────────────────────────────────────────────────────────────────────────────
# CAMBIO 2 — pantalla_hub(): lógica de variables y botones
#
# Reemplazar la función pantalla_hub() completa con esta versión:
# ─────────────────────────────────────────────────────────────────────────────

NUEVA_PANTALLA_HUB = '''
def pantalla_hub():
    """Pantalla de inicio con acceso a Stock, Maquinaria e Indumentaria."""
    import time
    rol = st.session_state.get("rol", "")

    # Overlay "Sistema en Desarrollo"
    _ts_maq = st.session_state.get("hub_maq_ts")
    if _ts_maq and (now_arg() - _ts_maq).total_seconds() < 4:
        st.markdown("""
        <div style="position:fixed;inset:0;z-index:99999;
            background:rgba(0,0,0,0.75);backdrop-filter:blur(6px);
            display:flex;align-items:center;justify-content:center;">
          <div style="background:linear-gradient(145deg,#1a1a10,#1c1808);
              border:2px solid rgba(212,160,23,0.75);border-radius:24px;
              padding:3rem 3.5rem;text-align:center;
              box-shadow:0 24px 80px rgba(0,0,0,0.7);
              max-width:480px;width:90%;
              animation:popIn .35s cubic-bezier(.175,.885,.32,1.275);">
            <div style="font-size:4rem;margin-bottom:1rem;">🔧</div>
            <div style="color:#d4a017;font-weight:800;font-size:1.5rem;margin-bottom:0.5rem;">
              Sistema en Desarrollo
            </div>
            <div style="color:#a09060;font-size:0.98rem;margin-bottom:1.5rem;">
              Este módulo estará disponible próximamente.
            </div>
            <div style="color:#706040;font-size:0.8rem;">Cerrando automáticamente...</div>
          </div>
        </div>
        <style>
          @keyframes popIn {
            from { opacity:0; transform:scale(0.75); }
            to   { opacity:1; transform:scale(1); }
          }
        </style>
        """, unsafe_allow_html=True)
        time.sleep(3)
        st.session_state.pop("hub_maq_ts", None)
        st.rerun()
    elif _ts_maq:
        st.session_state.pop("hub_maq_ts", None)

    # Badges y clases según rol
    maq_badge = \'<div class="dev-badge">&#9881; En Desarrollo</div>\' if rol != "admin" else ""
    maq_cls   = "hub-card hub-card-dev" if rol != "admin" else "hub-card"
    ind_badge = "" if rol == "admin" else \'<div class="dev-badge">🔒 Solo Admin</div>\'
    ind_cls   = "hub-card" if rol == "admin" else "hub-card hub-card-dev"

    st.markdown(f"""
    <style>
    .hub-page {{
        display:flex; flex-direction:column;
        align-items:center;
        padding:2rem 1rem 0 1rem;
    }}
    .hub-logo-wrap {{
        background:#f7f3e8;
        border:2px solid rgba(212,160,23,0.6);
        border-radius:50%;
        width:460px; height:276px;
        display:flex; align-items:center; justify-content:center;
        overflow:hidden;
        box-shadow:0 8px 32px rgba(0,0,0,0.45);
        margin-bottom:2.2rem;
    }}
    .hub-logo {{ width:100%; height:100%; object-fit:contain; padding:15px; }}
    .hub-cards {{
        display:grid;
        grid-template-columns: 300px 300px 300px;
        gap:2rem;
    }}
    .hub-card {{
        background:linear-gradient(160deg,rgba(60,60,70,0.97),rgba(40,40,52,0.99));
        border:1px solid rgba(212,160,23,0.42);
        border-radius:22px 22px 0 0;
        padding:2.4rem 2rem 2rem 2rem;
        text-align:center;
        box-shadow:0 8px 24px rgba(0,0,0,0.4);
        display:flex; flex-direction:column;
        align-items:center; justify-content:center;
        min-height:260px; box-sizing:border-box;
    }}
    .hub-card-dev {{
        background:linear-gradient(160deg,rgba(32,32,40,0.97),rgba(22,22,30,0.99));
        border-color:rgba(212,160,23,0.22); opacity:0.85;
    }}
    .hub-card-icon {{ font-size:3.5rem; margin-bottom:0.85rem; line-height:1; }}
    .hub-card-title {{
        font-family:\'Playfair Display\',serif;
        font-size:1.45rem; font-weight:700;
        color:#f0f0f5; margin:0 0 0.5rem 0;
    }}
    .hub-card-desc {{ font-size:0.9rem; color:#9090a8; line-height:1.55; }}
    .dev-badge {{
        display:inline-flex; align-items:center; gap:5px;
        background:rgba(212,160,23,0.13);
        border:1px solid rgba(212,160,23,0.42);
        border-radius:20px; padding:4px 16px;
        font-size:0.82rem; color:#d4a017;
        font-weight:700; margin-top:1rem;
    }}
    div[data-testid="stHorizontalBlock"] {{
        display:grid !important;
        grid-template-columns: 300px 300px 300px !important;
        gap:2rem !important;
        margin-top:-12px !important;
        padding:0 !important;
        width:fit-content !important;
        margin-left:auto !important;
        margin-right:auto !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
        width:300px !important;
        padding:0 !important;
        min-width:0 !important;
    }}
    div[data-testid="stHorizontalBlock"] .stButton > button {{
        border-radius:0 0 22px 22px !important;
        height:54px !important;
        font-size:0.95rem !important;
        font-weight:700 !important;
        margin:0 !important;
        padding:0 !important;
        width:300px !important;
        letter-spacing:0.03em !important;
        box-shadow:0 6px 18px rgba(0,0,0,0.3) !important;
    }}
    </style>
    <div class="hub-page">
        <div class="hub-logo-wrap">
            <img src="https://raw.githubusercontent.com/marcasosguemes-cell/Stock-SECCO-AGRO/main/Logo.png"
                 class="hub-logo" alt="Logo">
        </div>
        <div class="hub-cards">
            <div class="hub-card">
                <div class="hub-card-icon">📦</div>
                <div class="hub-card-title">Gestión de Stock</div>
                <div class="hub-card-desc">Control de ingresos, egresos, inventario y reportes por establecimiento.</div>
            </div>
            <div class="{maq_cls}">
                <div class="hub-card-icon">⚙️</div>
                <div class="hub-card-title">Gestión de Maquinaria</div>
                <div class="hub-card-desc">Seguimiento de mantenimiento preventivo y correctivo de equipos.</div>
                {maq_badge}
            </div>
            <div class="{ind_cls}">
                <div class="hub-card-icon">🧥</div>
                <div class="hub-card-title">Indumentaria</div>
                <div class="hub-card-desc">Talles, asignaciones, stock, cotizaciones y distribución de costos por firma.</div>
                {ind_badge}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Botones — 3 columnas
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Ver Módulo", key="btn_hub_stock", use_container_width=True):
            st.session_state["modulo"] = "stock"
            st.session_state["pagina"] = "Dashboard"
            st.rerun()
    with c2:
        if rol == "admin":
            if st.button("Ver Módulo", key="btn_hub_maq", use_container_width=True):
                st.session_state["modulo"] = "maquinaria"
                st.rerun()
        else:
            if st.button("Ver Módulo", key="btn_hub_maq_dev", use_container_width=True):
                st.session_state["hub_maq_ts"] = now_arg()
                st.rerun()
    with c3:
        if rol == "admin":
            if st.button("Ver Módulo", key="btn_hub_ind", use_container_width=True):
                st.session_state["modulo"] = "indumentaria"
                st.rerun()
        else:
            st.button("Solo Admin", key="btn_hub_ind_lock",
                      use_container_width=True, disabled=True)
'''


# ─────────────────────────────────────────────────────────────────────────────
# CAMBIO 3 — En main(), agregar el enrutamiento para "indumentaria"
#
# Después de:
#     if modulo == "maquinaria":
#         pagina_maquinaria()
#         return
#
# Agregar:
# ─────────────────────────────────────────────────────────────────────────────

NUEVO_ROUTING_INDUMENTARIA = '''
    if modulo == "indumentaria":
        rol = st.session_state.get("rol", "")
        if rol != "admin":
            st.error("⛔ Acceso restringido — solo administradores.")
            if st.button("← Volver"):
                st.session_state["modulo"] = "hub"
                st.rerun()
            return
        from indumentaria_module import pagina_indumentaria
        pagina_indumentaria(supabase)
        return
'''

print("Archivo de cambios generado correctamente.")
print("Ver comentarios internos para aplicar cada bloque en app.py.")
