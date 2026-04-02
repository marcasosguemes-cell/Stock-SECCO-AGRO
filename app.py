"""
SISTEMA DE CONTROL DE STOCK AGRÍCOLA
App principal Streamlit — La Sonia / San Guillermo / Camba Pora
Versión con gráficos interactivos y filtros dinámicos
Estructura mejorada: Admin con visión global + usuarios por establecimiento
CON CAMBIO DE CONTRASEÑA OBLIGATORIO EN CADA INGRESO HASTA QUE SE CAMBIE
"""

import streamlit as st
from supabase import create_client, Client
from datetime import date, datetime, timedelta
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
# CSS MEJORADO - Estilo moderno con tonos grises
# ══════════════════════════════════════════════════════════════

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

    /* ── Barra superior de Streamlit: ocultar ─────────────── */
    [data-testid="stHeader"],
    header[data-testid="stHeader"],
    .stAppHeader {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        border: none !important;
        background: none !important;
    }

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
        background: linear-gradient(135deg, rgba(8, 8, 11, 0.96) 0%, rgba(5, 5, 8, 0.97) 100%);
        z-index: -1;
        pointer-events: none;
    }

    [data-testid="stSidebarCollapsedControl"] {
        background: linear-gradient(135deg, #1a1a1f, #0f0f12) !important;
        border: 1px solid rgba(212, 160, 23, 0.5) !important;
        border-radius: 0 10px 10px 0 !important;
        box-shadow: 3px 0 12px rgba(0,0,0,0.4) !important;
        overflow: hidden !important;
    }

    [data-testid="stSidebarCollapsedControl"] button {
        color: transparent !important;
        background: transparent !important;
        border: none !important;
        position: relative !important;
        overflow: hidden !important;
    }

    [data-testid="stSidebarCollapsedControl"] button > *,
    [data-testid="stSidebarCollapsedControl"] button span,
    [data-testid="stSidebarCollapsedControl"] button p,
    [data-testid="stSidebarCollapsedControl"] button svg,
    [data-testid="stSidebarCollapsedControl"] button div {
        color: transparent !important;
        fill: transparent !important;
        opacity: 0 !important;
        font-size: 0px !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
        position: absolute !important;
    }

    [data-testid="stSidebarCollapsedControl"] button::before {
        content: "›" !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        font-size: 2.2rem !important;
        color: #d4a017 !important;
        font-weight: 900 !important;
        line-height: 1 !important;
        opacity: 1 !important;
        width: auto !important;
        height: auto !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button {
        color: transparent !important;
        background: transparent !important;
        position: relative !important;
        overflow: hidden !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button > *,
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button span,
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button p,
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button svg,
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button div {
        color: transparent !important;
        fill: transparent !important;
        opacity: 0 !important;
        font-size: 0px !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
        position: absolute !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button::before {
        content: "‹" !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        font-size: 2.2rem !important;
        color: #d4a017 !important;
        font-weight: 900 !important;
        line-height: 1 !important;
        opacity: 1 !important;
        width: auto !important;
        height: auto !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a1f 0%, #0f0f12 60%, #0a0a0c 100%) !important;
        border-right: 1px solid rgba(100, 100, 120, 0.3) !important;
        box-shadow: 4px 0 24px rgba(0,0,0,0.4) !important;
    }

    [data-testid="stSidebar"] .stButton button {
        background: rgba(50, 50, 60, 0.8) !important;
        border: 1px solid rgba(212, 160, 23, 0.5) !important;
        width: 100%;
        text-align: left;
        padding: 0.7rem 1.1rem;
        border-radius: 12px;
        margin: 5px 0;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.25s ease;
        color: #000000 !important;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background: #d4a017 !important;
        border-color: #b87a0c !important;
        transform: translateX(5px);
        color: #1a1a1f !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="tooltip"] {
        display: none !important;
    }
    
    [data-baseweb="tooltip"] {
        display: none !important;
    }

    .sidebar-header {
        text-align: center;
        padding: 1.6rem 0 1.2rem 0;
        border-bottom: 1px solid rgba(212, 160, 23, 0.4);
        margin-bottom: 1.4rem;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .sidebar-logo-oval {
        background: #f7f3e8;
        border: 2px solid rgba(212, 160, 23, 0.6);
        border-radius: 50%;
        width: 120px;
        height: 120px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3), 0 1px 0 rgba(255,255,255,0.3) inset;
        margin-bottom: 12px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .sidebar-logo-oval:hover {
        transform: scale(1.03);
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    }

    .sidebar-logo {
        width: 115% !important;
        height: auto !important;
        object-fit: contain !important;
        display: block;
        padding: 0px;
    }

    .sidebar-header h1 {
        font-family: 'Playfair Display', serif !important;
        font-size: 1.4rem !important;
        margin: 0;
        color: #d4a017 !important;
        letter-spacing: 0.04em;
        font-weight: 700;
    }

    .profile-card {
        text-align: center;
        padding: 0.9rem 1rem;
        margin: 0.5rem 0 1rem 0;
        background: rgba(40, 40, 48, 0.7) !important;
        border: 1px solid rgba(212, 160, 23, 0.25);
        border-radius: 16px;
        backdrop-filter: blur(8px);
    }

    .profile-name {
        font-size: 0.95rem;
        font-weight: 600;
        color: #f0f0f5 !important;
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

    .title-bubble {
        background: linear-gradient(135deg, rgba(200, 160, 96, 0.95) 0%, rgba(184, 144, 90, 0.95) 100%);
        border-radius: 20px;
        padding: 1rem 2.2rem;
        display: inline-block;
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
        text-align: center;
        margin-bottom: 1.4rem;
        backdrop-filter: blur(4px);
    }

    .title-bubble h1 {
        margin: 0;
        font-family: 'Playfair Display', serif !important;
        font-size: 1.8rem !important;
        color: #1a3a1a !important;
        font-weight: 700;
        letter-spacing: 0.02em;
    }

    .title-bubble p {
        margin: 0.35rem 0 0 0;
        color: #2a4a2a !important;
        font-size: 0.9rem;
        font-weight: 500;
    }

    .filters-panel {
        background: rgba(45, 45, 52, 0.85) !important;
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.8rem;
        border: 1px solid rgba(212, 160, 23, 0.3);
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }

    .filters-panel h3, .filters-panel .stMarkdown h3 {
        color: #d4a017 !important;
        font-weight: 700;
        letter-spacing: 0.05em;
        margin-bottom: 1rem;
        text-transform: uppercase;
    }

    .metric-card {
        background: linear-gradient(145deg, rgba(55, 55, 62, 0.9) 0%, rgba(45, 45, 52, 0.95) 100%) !important;
        border: 1px solid rgba(212, 160, 23, 0.35);
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
        border-color: rgba(212, 160, 23, 0.6);
    }

    .metric-value {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.6rem !important;
        font-weight: 700;
        color: #f0f0f5 !important;
        margin: 0.4rem 0;
    }

    .metric-label {
        font-size: 0.75rem !important;
        color: #d4a017 !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 700;
    }

    .trend-up {
        color: #6fcf97;
        font-size: 0.8rem;
        font-weight: 500;
    }

    .trend-down {
        color: #e67e22;
        font-size: 0.8rem;
        font-weight: 500;
    }

    .section-title {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 1.2rem !important;
        font-weight: 700;
        color: #d4a017 !important;
        border-left: 4px solid #d4a017;
        padding-left: 1rem;
        margin: 1.8rem 0 1.2rem 0;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    .stButton > button {
        background: linear-gradient(135deg, #d4a017, #b87a0c) !important;
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
        background: linear-gradient(135deg, #e5b52a, #c98a1a) !important;
        color: #000000 !important;
    }
    
    button[kind="primary"]::after {
        content: " →";
        font-size: 1.1rem;
    }

    [data-testid="stForm"] {
        background: rgba(45, 45, 52, 0.85) !important;
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(212, 160, 23, 0.3);
    }

    .stSelectbox > div,
    .stSelectbox div[data-baseweb="select"] {
        background-color: #2d2d34 !important;
        border-radius: 10px !important;
        border: 1px solid #d4a017 !important;
    }

    .stSelectbox div[data-baseweb="select"] > div,
    .stSelectbox div[data-baseweb="select"] div,
    .stSelectbox div[data-baseweb="select"] span,
    .stSelectbox [data-baseweb="select"] * {
        color: #f0f0f5 !important;
        font-weight: 600 !important;
        background-color: transparent !important;
    }

    .stSelectbox input,
    .stSelectbox [data-baseweb="select"] input {
        caret-color: transparent !important;
        cursor: pointer !important;
        color: transparent !important;
        text-shadow: 0 0 0 #f0f0f5 !important;
        width: 1px !important;
        min-width: 0 !important;
        max-width: 1px !important;
        opacity: 0 !important;
    }

    .stSelectbox div[data-baseweb="select"] > div:first-child {
        padding-right: 2rem !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
    }

    .stSelectbox svg {
        fill: #d4a017 !important;
        stroke: #d4a017 !important;
    }

    body [data-baseweb="popover"],
    body [data-baseweb="popover"] *:not(svg):not(path),
    body div[data-baseweb="popover"],
    body div[data-baseweb="popover"] > div {
        background-color: #2d2d34 !important;
        color: #f0f0f5 !important;
    }

    body [data-baseweb="popover"] {
        border: 1px solid #d4a017 !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5) !important;
    }

    body [data-baseweb="menu"],
    body ul[data-baseweb="menu"],
    body [data-baseweb="menu"] > div,
    body [data-baseweb="menu"] > div > div {
        background-color: #2d2d34 !important;
        color: #f0f0f5 !important;
    }

    body [data-baseweb="menu"] li,
    body [data-baseweb="menu"] [role="option"],
    body [role="option"] {
        background-color: #2d2d34 !important;
        color: #f0f0f5 !important;
        font-weight: 500 !important;
    }

    body [data-baseweb="menu"] li *,
    body [data-baseweb="menu"] [role="option"] *,
    body [role="option"] * {
        color: #f0f0f5 !important;
        background-color: transparent !important;
    }

    body [data-baseweb="menu"] li:hover,
    body [data-baseweb="menu"] [role="option"]:hover,
    body [role="option"]:hover {
        background-color: rgba(212, 160, 23, 0.25) !important;
        color: #f0f0f5 !important;
    }

    input, textarea {
        color: #f0f0f5 !important;
        background-color: #2d2d34 !important;
        border-radius: 10px !important;
        border: 1px solid #d4a017 !important;
        font-weight: 500 !important;
    }

    input:focus, textarea:focus {
        border-color: #d4a017 !important;
        box-shadow: 0 0 0 2px rgba(212, 160, 23, 0.2) !important;
        outline: none !important;
    }

    label {
        color: #f0f0f5 !important;
        font-weight: 600 !important;
        text-shadow: 0 1px 4px rgba(0,0,0,0.9), 0 0px 8px rgba(0,0,0,0.8) !important;
    }

    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        color: #f0f0f5 !important;
        text-shadow: 0 1px 6px rgba(0,0,0,0.95), 0 0 12px rgba(0,0,0,0.8) !important;
    }

    [data-testid="stWidgetLabel"] > div,
    [data-testid="stWidgetLabel"] p {
        color: #f0f0f5 !important;
        font-weight: 600 !important;
        text-shadow: 0 1px 6px rgba(0,0,0,0.95) !important;
        background: rgba(10,10,12,0.55) !important;
        border-radius: 4px !important;
        padding: 0 4px !important;
        display: inline-block !important;
    }

    .stDataFrame {
        background: rgba(35, 35, 42, 0.7);
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(0,0,0,0.2);
    }

    .stDataFrame * {
        color: #e8e8ec !important;
    }

    .stAlert {
        background: rgba(45, 45, 52, 0.85) !important;
        backdrop-filter: blur(8px);
        border-radius: 14px !important;
        border: 1px solid rgba(212, 160, 23, 0.4) !important;
        color: #e8e8ec !important;
    }

    .badge-admin {
        background: linear-gradient(135deg, #d4a017, #b87a0c);
        color: #1a1a1f !important;
        padding: 0.22rem 0.7rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
    }

    .badge-operator {
        background: linear-gradient(135deg, #2c5e2e, #1e3a1e);
        color: #e8e8ec !important;
        padding: 0.22rem 0.7rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
    }

    .footer {
        text-align: center;
        padding: 1.6rem 2rem;
        color: #a8a8b0 !important;
        font-size: 0.78rem;
        border-top: 1px solid rgba(212, 160, 23, 0.25);
        margin-top: 2.5rem;
        background: rgba(35, 35, 42, 0.7);
        backdrop-filter: blur(8px);
        border-radius: 16px;
    }

    p, span, div, label, .stMarkdown {
        color: #e8e8ec !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    h1, h2, h3, h4 {
        color: #f0f0f5 !important;
    }

    .main-content {
        animation: fadeUp 0.45s cubic-bezier(.4,0,.2,1);
    }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }

    hr {
        border: none !important;
        border-top: 1px solid rgba(212, 160, 23, 0.25) !important;
        margin: 1.5rem 0 !important;
    }

    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown div {
        color: #e8e8ec !important;
    }
    
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #d4a017 !important;
    }
    
    [role="tooltip"] {
        display: none !important;
    }
    
    .stTooltipContent {
        display: none !important;
    }

    [data-testid="stExpander"],
    [data-testid="stExpander"] > details,
    details[data-testid="stExpander"] {
        background: #1e1e24 !important;
        border: 1px solid rgba(212, 160, 23, 0.4) !important;
        border-radius: 14px !important;
        position: relative !important;
        z-index: 10 !important;
    }

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] > details > summary,
    details[data-testid="stExpander"] > summary {
        background: #1e1e24 !important;
        color: #f0f0f5 !important;
        font-weight: 600 !important;
        border-radius: 14px !important;
        padding: 0.8rem 1rem !important;
    }
    
    .password-warning {
        background: linear-gradient(135deg, rgba(212, 160, 23, 0.2), rgba(184, 122, 12, 0.2));
        border-left: 4px solid #d4a017;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .password-warning h3 {
        color: #d4a017 !important;
        margin-top: 0 !important;
    }
</style>
""", unsafe_allow_html=True)


# ── JS: Reemplazar texto del botón colapsar sidebar ──────────
import streamlit.components.v1 as components
components.html("""
<script>
(function() {
    function fixSidebarBtn() {
        var doc = window.parent.document;
        var allElems = doc.querySelectorAll('button, span, p, div');
        allElems.forEach(function(el) {
            var txt = (el.innerText || el.textContent || '').trim().toLowerCase();
            if (
                (txt.includes('keyboard') || txt.includes('do_double') || txt.includes('double_arrow')) &&
                el.children.length === 0
            ) {
                el.style.fontSize = '0px';
                el.style.color = 'transparent';
                el.style.display = 'none';
            }
        });
        var collapsed = doc.querySelector('[data-testid="stSidebarCollapsedControl"]');
        if (collapsed && !collapsed.querySelector('.flecha-custom')) {
            var btn = collapsed.querySelector('button');
            if (btn) {
                btn.innerHTML = '';
                var flecha = doc.createElement('span');
                flecha.className = 'flecha-custom';
                flecha.textContent = '›';
                flecha.style.cssText = 'font-size:2rem;color:#d4a017;font-weight:900;line-height:1;';
                btn.appendChild(flecha);
            }
        }
    }
    setTimeout(fixSidebarBtn, 500);
    setTimeout(fixSidebarBtn, 1500);
    var observer = new MutationObserver(function() {
        fixSidebarBtn();
    });
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
})();
</script>
""", height=0, scrolling=False)


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
        keys_to_clear = ["session", "user_id", "perfil", "rol", "establecimiento_id", 
                         "establecimiento_nombre", "pagina", "password_changed", "skip_password_check"]
        for key in keys_to_clear:
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
                    st.session_state["password_changed"] = perfil.data[0].get("password_changed", False)
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
                            st.session_state["password_changed"] = perfil.data[0].get("password_changed", False)
                            st.session_state["pagina"] = "Dashboard"
                            # Limpiar bandera temporal de sesión anterior
                            st.session_state.pop("skip_password_check", None)
                            st.success("✅ Login exitoso!")
                            st.rerun()
                        else:
                            st.error("❌ No se encontró tu perfil.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")


# ══════════════════════════════════════════════════════════════
# FUNCIÓN PARA MOSTRAR CAMBIO DE CONTRASEÑA - CORREGIDA
# ══════════════════════════════════════════════════════════════

def mostrar_cambio_password():
    st.markdown("""
    <div class="password-warning">
        <h3>🔐 Cambio de Contraseña Obligatorio</h3>
        <p>Por razones de seguridad, debes cambiar tu contraseña.</p>
        <p><strong>Importante:</strong> Esta contraseña temporal caducará pronto. Por favor, establécela ahora.</p>
        <p>Si eliges "Más Tarde", el sistema te recordará en cada ingreso hasta que la cambies.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("cambiar_password_form_main"):
        nueva_password = st.text_input("Nueva Contraseña", type="password", placeholder="Mínimo 6 caracteres")
        confirmar_password = st.text_input("Confirmar Contraseña", type="password", placeholder="Repite tu nueva contraseña")
        
        col1, col2 = st.columns(2)
        with col1:
            cambiar_btn = st.form_submit_button("✅ Cambiar Contraseña", use_container_width=True)
        with col2:
            mas_tarde_btn = st.form_submit_button("⏰ Más Tarde", use_container_width=True)
        
        if cambiar_btn:
            if not nueva_password:
                st.error("❌ Por favor ingresa una nueva contraseña")
            elif len(nueva_password) < 6:
                st.error("❌ La contraseña debe tener al menos 6 caracteres")
            elif nueva_password != confirmar_password:
                st.error("❌ Las contraseñas no coinciden")
            else:
                try:
                    with st.spinner("Actualizando contraseña..."):
                        supabase.auth.update_user({"password": nueva_password})
                        supabase.table("usuarios").update({"password_changed": True}).eq("id", st.session_state["user_id"]).execute()
                        st.session_state["password_changed"] = True
                        # Limpiar bandera temporal
                        st.session_state.pop("skip_password_check", None)
                        st.success("✅ Contraseña actualizada correctamente!")
                        st.balloons()
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al actualizar contraseña: {e}")
        
        if mas_tarde_btn:
            # Establecer bandera temporal para esta sesión
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
                st.error("⚠️ No tienes un establecimiento asignado. Contacta al administrador.")
                st.markdown("---")
                if st.button("🚪 Cerrar sesión"):
                    logout()
                return
            
            opciones_estab = [mi_estab_nombre]
            st.session_state["estab_seleccionado"] = mi_estab_nombre
            st.session_state["estab_activo_id"] = mi_estab_id
            st.session_state["estab_activo_nombre"] = mi_estab_nombre
            st.markdown(f"""
            <div style="background:rgba(212,160,23,0.2); border-radius:10px; padding:0.5rem; text-align:center; margin-bottom:0.8rem;">
                <span style="color:#d4a017;">📍 {mi_estab_nombre}</span>
            </div>
            """, unsafe_allow_html=True)

        if rol == "admin":
            if "estab_seleccionado" not in st.session_state:
                st.session_state["estab_seleccionado"] = "🌐 Consolidado"

            estab_sel = st.selectbox(
                "Seleccionar",
                opciones_estab,
                index=opciones_estab.index(st.session_state["estab_seleccionado"]) if st.session_state["estab_seleccionado"] in opciones_estab else 0,
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

        estab_activo = st.session_state.get("estab_activo_nombre", "Consolidado" if rol == "admin" else st.session_state.get("establecimiento_nombre", ""))
        es_consolidado = (estab_activo == "Consolidado")

        st.markdown(f"""
        <div class="profile-card">
            <div class="profile-name">👤 {perfil.get('nombre', 'Usuario')}</div>
            <div class="profile-role"><span class="{badge_class}">{badge_text}</span></div>
            <div class="profile-location">📍 {'🌐 Todos los establecimientos' if es_consolidado else estab_activo}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📌 MENÚ")

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
            st.error("⚠️ Configuración incompleta. Contacta al administrador.")
            st.markdown("---")
            if st.button("🚪 Cerrar sesión"):
                logout()
            return

        pagina_actual = st.session_state.get("pagina", "Dashboard")
        nombres_menu = [n for _, n in paginas_menu]
        if pagina_actual not in nombres_menu:
            st.session_state["pagina"] = nombres_menu[0]

        for emoji, nombre in paginas_menu:
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

def get_productos(categoria_id=None, subcategoria=None):
    q = supabase.table("productos").select("*,categorias(nombre)").eq("activo", True)
    if categoria_id:
        q = q.eq("categoria_id", categoria_id)
    if subcategoria:
        q = q.eq("subcategoria", subcategoria)
    return q.execute().data

def get_proveedores():
    res = supabase.table("proveedores").select("*").eq("activo", True).execute()
    return res.data

def get_movimientos(establecimiento_id=None, limit=5000):
    try:
        q = supabase.table("movimientos").select("*").limit(limit)
        if establecimiento_id:
            q = q.eq("establecimiento_id", establecimiento_id)
        movimientos = q.execute().data
        
        if not movimientos:
            return []
        
        producto_ids = list(set([m.get("producto_id") for m in movimientos if m.get("producto_id")]))
        establecimiento_ids = list(set([m.get("establecimiento_id") for m in movimientos if m.get("establecimiento_id")]))
        
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
    categoria_map = {p["id"]: p.get("categorias", {}).get("nombre", "Sin categoría") if p.get("categorias") else "Sin categoría" for p in productos}
    presentacion_map = {p["id"]: p.get("presentacion", "") for p in productos}
    unidad_map = {p["id"]: p.get("unidad_medida", "unidad") for p in productos}
    
    stock = {}
    for prod_id in set(ingresos.index) | set(egresos.index):
        stock[prod_id] = ingresos.get(prod_id, 0) - egresos.get(prod_id, 0)
    
    result = []
    for prod_id, cantidad in stock.items():
        if cantidad != 0:
            result.append({
                "producto_id": prod_id,
                "producto": nombre_map.get(prod_id, "Desconocido"),
                "categoria": categoria_map.get(prod_id, "Sin categoría"),
                "presentacion": presentacion_map.get(prod_id, ""),
                "unidad": unidad_map.get(prod_id, "unidad"),
                "stock": cantidad
            })
    
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
            df = df[df["fecha"] <= pd.Timestamp(fecha_hasta)]
    
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

    ingresos = df[df["tipo"] == "ingreso"].groupby(["producto_nombre", "producto_presentacion", "producto_unidad", "categoria_nombre", "establecimiento_nombre"])["cantidad"].sum()
    egresos = df[df["tipo"] == "egreso"].groupby(["producto_nombre", "producto_presentacion", "producto_unidad", "categoria_nombre", "establecimiento_nombre"])["cantidad"].sum()

    stock_df = (ingresos - egresos.reindex(ingresos.index, fill_value=0)).reset_index()
    stock_df.columns = ["producto", "presentacion", "unidad", "categoria", "establecimiento", "stock"]
    return stock_df[stock_df["stock"] != 0].sort_values(["establecimiento", "producto"])


# ══════════════════════════════════════════════════════════════
# DASHBOARD CON GRÁFICOS INTERACTIVOS Y FILTROS DINÁMICOS
# ══════════════════════════════════════════════════════════════

def pagina_dashboard():
    # ── CSS exclusivo del Dashboard ────────────────────────────
    st.markdown("""
    <style>
        /* Fondo más oscuro solo en el Dashboard */
        .stApp {
            background-image: none !important;
            background: linear-gradient(160deg, #0d0d14 0%, #09090f 60%, #06060b 100%) !important;
        }
        .stApp::before { background: none !important; }

        /* Panel de filtros */
        .dash-filtros {
            background: rgba(22, 22, 32, 0.98) !important;
            border: 1px solid rgba(212, 160, 23, 0.35) !important;
            border-radius: 18px !important;
            padding: 1.2rem 1.5rem !important;
            margin-bottom: 1.5rem !important;
        }

        /* Título de sección */
        .dash-section-title {
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.78rem !important;
            font-weight: 700 !important;
            color: #d4a017 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.13em !important;
            margin: 0 0 0.8rem 0 !important;
        }

        /* Contenedor de cada gráfico */
        .dash-chart-box {
            background: #14141e !important;
            border: 1px solid rgba(212, 160, 23, 0.28) !important;
            border-radius: 18px !important;
            padding: 1rem 1.2rem 0.4rem 1.2rem !important;
            margin-bottom: 1.4rem !important;
            box-shadow: 0 4px 24px rgba(0,0,0,0.5) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>📊 Dashboard de Stock</h1>
            <p>📋 Análisis interactivo del inventario agrícola</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    estab_activo = st.session_state.get("estab_activo_nombre", "")
    if estab_activo and estab_activo != "Consolidado":
        st.markdown(f"""
        <div style="background:rgba(212,160,23,0.15);border:1px solid rgba(212,160,23,0.5);border-radius:12px;padding:0.6rem 1.2rem;margin-bottom:1rem;display:inline-block;">
            <span style="color:#d4a017;font-weight:700;">🏢 Establecimiento activo:</span>
            <span style="color:#f0f0f5;font-weight:600;"> {estab_activo}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="dash-filtros">', unsafe_allow_html=True)
    st.markdown('<div class="dash-section-title">🔍 Filtros dinámicos</div>', unsafe_allow_html=True)

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        fecha_desde = st.date_input("📅 Desde", value=date.today() - timedelta(days=90))
        fecha_hasta = st.date_input("📅 Hasta", value=date.today())
    
    with col_f2:
        tipo_filtro = st.selectbox("📌 Tipo de Movimiento", ["Todos", "ingreso", "egreso"])

    with col_f3:
        categorias = get_categorias()
        cat_options = {c["nombre"]: c["id"] for c in categorias}
        cat_options["Todas"] = None
        cat_seleccionada = st.selectbox("📁 Categoría", list(cat_options.keys()))
        cat_id = cat_options[cat_seleccionada] if cat_seleccionada != "Todas" else None

        # Subcategoría agroquímicos
        es_agro_dash = cat_seleccionada and ("agroquimico" in cat_seleccionada.lower() or "agroquímico" in cat_seleccionada.lower())
        subcategoria_dash = None
        if es_agro_dash:
            subcategoria_dash = st.selectbox(
                "🌿 Tipo Agroquímico",
                ["Todos", "Herbicidas", "Insecticidas", "Coadyuvantes"],
                key="dash_subcategoria"
            )

        productos = get_productos(cat_id, subcategoria_dash if (es_agro_dash and subcategoria_dash != "Todos") else None)
        prod_options = {p["nombre"]: p["id"] for p in productos}
        prod_options["Todos"] = None
        prod_seleccionado = st.selectbox("🏷️ Producto", list(prod_options.keys()))
        prod_id = prod_options[prod_seleccionado] if prod_seleccionado != "Todos" else None
    
    with col_f4:
        stock_min = st.number_input("⚠️ Stock mínimo (alerta)", min_value=0, value=50, step=10)

    st.markdown('</div>', unsafe_allow_html=True)  # cierra dash-filtros

    movimientos = get_movimientos_con_filtros(
        establecimiento_id=estab_filter(),
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        tipo=tipo_filtro if tipo_filtro != "Todos" else None,
        producto_id=prod_id,
        categoria_id=cat_id
    )

    # Filtrar por subcategoría en el DataFrame si corresponde
    if movimientos and es_agro_dash and subcategoria_dash and subcategoria_dash != "Todos":
        ids_subcat = {p["id"] for p in get_productos(cat_id, subcategoria_dash)}
        movimientos = [m for m in movimientos if m.get("producto_id") in ids_subcat]
    
    col1, col2, col3, col4 = st.columns(4)
    
    if movimientos:
        df_mov = pd.DataFrame(movimientos)
        
        ingresos = df_mov[df_mov["tipo"] == "ingreso"]["cantidad"].sum() if "ingreso" in df_mov["tipo"].values else 0
        egresos = df_mov[df_mov["tipo"] == "egreso"]["cantidad"].sum() if "egreso" in df_mov["tipo"].values else 0
        stock_total = ingresos - egresos
        total_movimientos = len(df_mov)
        
        fecha_anterior_inicio = fecha_desde - timedelta(days=(fecha_hasta - fecha_desde).days)
        mov_anterior = get_movimientos_con_filtros(
            establecimiento_id=estab_filter(),
            fecha_desde=fecha_anterior_inicio,
            fecha_hasta=fecha_desde - timedelta(days=1),
            tipo=tipo_filtro if tipo_filtro != "Todos" else None,
            producto_id=prod_id,
            categoria_id=cat_id
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
                <div class="metric-label">📦 STOCK TOTAL</div>
                <div class="metric-value">{stock_total:,.0f}</div>
                <div class="{trend_class}">{trend_icon} {abs(tendencia_ingresos):.1f}% vs período anterior</div>
                <div style="font-size:0.7rem; color:#a8a8b0;">unidades en inventario</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📥 INGRESOS</div>
                <div class="metric-value">{ingresos:,.0f}</div>
                <div style="font-size:0.7rem; color:#a8a8b0;">unidades ingresadas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📤 EGRESOS</div>
                <div class="metric-value">{egresos:,.0f}</div>
                <div style="font-size:0.7rem; color:#a8a8b0;">unidades egresadas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">🔄 MOVIMIENTOS</div>
                <div class="metric-value">{total_movimientos}</div>
                <div style="font-size:0.7rem; color:#a8a8b0;">operaciones en el período</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        for col in [col1, col2, col3, col4]:
            with col:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">0</div>
                    <div class="metric-label">SIN DATOS</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if movimientos:
        df_mov = pd.DataFrame(movimientos)
        df_mov["fecha"] = pd.to_datetime(df_mov["fecha"])

        # Enriquecer con nombre de producto
        df_mov["producto_nombre"] = df_mov["productos"].apply(
            lambda x: x.get("nombre", "") if isinstance(x, dict) else ""
        )
        df_mov["categoria_nombre"] = df_mov["productos"].apply(
            lambda x: x.get("categorias", {}).get("nombre", "") if isinstance(x, dict) else ""
        )

        # Título dinámico según filtros activos
        filtro_desc = []
        if prod_seleccionado != "Todos":
            filtro_desc.append(f"Producto: **{prod_seleccionado}**")
        elif cat_seleccionada != "Todas":
            filtro_desc.append(f"Categoría: **{cat_seleccionada}**")
            if es_agro_dash and subcategoria_dash and subcategoria_dash != "Todos":
                filtro_desc.append(f"Tipo: **{subcategoria_dash}**")
        if filtro_desc:
            st.markdown(f"🔎 Mostrando datos para — {' | '.join(filtro_desc)}")

        # ── Evolución del stock ──────────────────────────────────
        df_mov["stock_diario"] = df_mov.apply(
            lambda x: x["cantidad"] if x["tipo"] == "ingreso" else -x["cantidad"], axis=1
        )
        df_daily = df_mov.groupby(df_mov["fecha"].dt.date)["stock_diario"].sum().reset_index()
        df_daily.columns = ["fecha", "movimiento_diario"]
        df_daily["stock_acumulado"] = df_daily["movimiento_diario"].cumsum()

        titulo_evol = f"📈 Evolución del Stock — {prod_seleccionado}" if prod_seleccionado != "Todos" else "📈 Evolución del Stock en el Tiempo"
        fig_evolucion = px.line(
            df_daily,
            x="fecha",
            y="stock_acumulado",
            title=titulo_evol,
            labels={"fecha": "Fecha", "stock_acumulado": "Stock (unidades)"},
            template="plotly_dark",
            line_shape="spline"
        )
        fig_evolucion.update_traces(
            line=dict(color="#d4a017", width=3),
            fill="tozeroy",
            fillcolor="rgba(212,160,23,0.08)"
        )
        fig_evolucion.update_layout(
            height=420,
            hovermode="x unified",
            plot_bgcolor="#14141e",
            paper_bgcolor="#14141e",
            font=dict(color="#e8e8ec", size=13, family="DM Sans"),
            title=dict(font=dict(size=16, color="#f0f0f5"), x=0.01),
            xaxis=dict(gridcolor="rgba(255,255,255,0.07)", linecolor="rgba(255,255,255,0.12)",
                       tickfont=dict(size=12, color="#c8c8d8"), title_font=dict(size=13, color="#d4a017")),
            yaxis=dict(gridcolor="rgba(255,255,255,0.07)", linecolor="rgba(255,255,255,0.12)",
                       tickfont=dict(size=12, color="#c8c8d8"), title_font=dict(size=13, color="#d4a017")),
            margin=dict(l=10, r=10, t=50, b=10),
        )
        st.markdown('<div class="dash-chart-box">', unsafe_allow_html=True)
        st.plotly_chart(fig_evolucion, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Torta: distribución por categoría (o por producto si hay filtro) ──
        stock_productos = get_stock_por_producto(estab_filter())
        if not stock_productos.empty:
            # Aplicar mismo filtro de producto/categoría/subcategoría al stock
            stock_filtrado = stock_productos.copy()
            if prod_id:
                stock_filtrado = stock_filtrado[stock_filtrado["producto_id"] == prod_id]
            elif cat_id:
                stock_filtrado = stock_filtrado[stock_filtrado["categoria_id"] == cat_id] if "categoria_id" in stock_filtrado.columns else stock_filtrado[stock_filtrado["categoria"] == cat_seleccionada]
                if es_agro_dash and subcategoria_dash and subcategoria_dash != "Todos":
                    ids_sub = {p["id"] for p in get_productos(cat_id, subcategoria_dash)}
                    stock_filtrado = stock_filtrado[stock_filtrado["producto_id"].isin(ids_sub)]

            if not stock_filtrado.empty:
                # Si hay un producto específico: torta por establecimiento; si no: por categoría
                if prod_id:
                    if "establecimiento" in stock_filtrado.columns:
                        pie_data = stock_filtrado.groupby("establecimiento")["stock"].sum().reset_index()
                        pie_names = "establecimiento"
                        pie_title = f"🥧 Stock de {prod_seleccionado} por Establecimiento"
                    else:
                        pie_data = stock_filtrado
                        pie_names = "producto"
                        pie_title = f"🥧 Stock — {prod_seleccionado}"
                else:
                    pie_data = stock_filtrado.groupby("categoria")["stock"].sum().reset_index()
                    pie_names = "categoria"
                    pie_title = "🥧 Distribución de Stock por Categoría"

                fig_torta = px.pie(
                    pie_data,
                    values="stock",
                    names=pie_names,
                    title=pie_title,
                    template="plotly_dark",
                    color_discrete_sequence=px.colors.sequential.Oranges_r
                )
                fig_torta.update_traces(
                    textposition="inside",
                    textinfo="percent+label",
                    textfont=dict(size=13, color="#ffffff"),
                    insidetextorientation="radial"
                )
                fig_torta.update_layout(
                    height=460,
                    paper_bgcolor="#14141e",
                    font=dict(color="#e8e8ec", size=13, family="DM Sans"),
                    title=dict(font=dict(size=16, color="#f0f0f5"), x=0.01),
                    legend=dict(font=dict(size=13, color="#e8e8ec"),
                                bgcolor="rgba(20,20,30,0.95)", bordercolor="rgba(212,160,23,0.3)", borderwidth=1),
                    margin=dict(l=10, r=10, t=50, b=10),
                )
                st.markdown('<div class="dash-chart-box">', unsafe_allow_html=True)
                st.plotly_chart(fig_torta, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # ── Barras: Top productos ────────────────────────────────
            st.markdown("---")
            if not stock_filtrado.empty:
                titulo_barras = f"📊 Stock — {prod_seleccionado}" if prod_id else "📊 Top 10 Productos con Mayor Stock"
                top_n = stock_filtrado if prod_id else stock_filtrado.sort_values("stock", ascending=False).head(10)
                fig_barras = px.bar(
                    top_n, x="producto", y="stock", title=titulo_barras,
                    labels={"producto": "Producto", "stock": "Stock (unidades)"},
                    template="plotly_dark", color="stock",
                    color_continuous_scale="Oranges", text="stock"
                )
                fig_barras.update_traces(
                    texttemplate="%{text:,.0f}", textposition="outside",
                    textfont=dict(size=12, color="#e8e8ec"),
                    marker_line_color="rgba(212,160,23,0.4)", marker_line_width=1,
                )
                fig_barras.update_layout(
                    height=480, xaxis_tickangle=-40,
                    plot_bgcolor="#14141e", paper_bgcolor="#14141e",
                    font=dict(color="#e8e8ec", size=13, family="DM Sans"),
                    title=dict(font=dict(size=16, color="#f0f0f5"), x=0.01),
                    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.12)",
                               tickfont=dict(size=11, color="#c8c8d8"), title_font=dict(size=13, color="#d4a017")),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.07)", linecolor="rgba(255,255,255,0.12)",
                               tickfont=dict(size=12, color="#c8c8d8"), title_font=dict(size=13, color="#d4a017")),
                    coloraxis_showscale=False,
                    margin=dict(l=10, r=10, t=55, b=10),
                )
                st.markdown('<div class="dash-chart-box">', unsafe_allow_html=True)
                st.plotly_chart(fig_barras, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # ── Tabla de stock actual ────────────────────────────────
            st.markdown("### 📋 Detalle de Stock Actual")
            stock_display = stock_filtrado.copy()
            stock_display["alerta"] = stock_display["stock"].apply(
                lambda x: "🔴 Crítico" if x < stock_min else ("⚠️ Bajo" if x < stock_min * 2 else "✅ Normal")
            )
            cols_disp = [c for c in ["producto", "categoria", "presentacion", "stock", "unidad", "alerta"] if c in stock_display.columns]
            st.dataframe(stock_display[cols_disp], use_container_width=True, height=400)

            # ── Exportar stock a Excel ───────────────────────────────
            st.markdown("#### 📥 Exportar Stock")
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                buf_stock = BytesIO()
                with pd.ExcelWriter(buf_stock, engine="openpyxl") as writer:
                    stock_display[cols_disp].to_excel(writer, index=False, sheet_name="Stock_Actual")
                label_stock = f"📥 Exportar stock — {prod_seleccionado}" if prod_id else "📥 Exportar stock actual"
                st.download_button(
                    label_stock,
                    data=buf_stock.getvalue(),
                    file_name=f"stock_{prod_seleccionado.replace(' ','_') if prod_id else 'general'}_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_stock"
                )
            with col_exp2:
                buf_mov = BytesIO()
                df_export = df_mov.copy()
                df_export["fecha"] = df_export["fecha"].dt.strftime("%d/%m/%Y %H:%M")
                cols_mov = [c for c in ["fecha", "tipo", "producto_nombre", "categoria_nombre", "cantidad", "observaciones"] if c in df_export.columns]
                with pd.ExcelWriter(buf_mov, engine="openpyxl") as writer:
                    df_export[cols_mov].to_excel(writer, index=False, sheet_name="Movimientos")
                label_mov = f"📥 Exportar movimientos — {prod_seleccionado}" if prod_id else "📥 Exportar movimientos"
                st.download_button(
                    label_mov,
                    data=buf_mov.getvalue(),
                    file_name=f"movimientos_{prod_seleccionado.replace(' ','_') if prod_id else 'general'}_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_mov"
                )

        # ── Movimientos mensuales ────────────────────────────────
        df_mov["mes"] = df_mov["fecha"].dt.to_period("M").astype(str)
        movimientos_mensuales = df_mov.groupby(["mes", "tipo"])["cantidad"].sum().reset_index()
        fig_mensual = px.bar(
            movimientos_mensuales, x="mes", y="cantidad", color="tipo",
            title="📅 Movimientos Mensuales por Tipo",
            labels={"mes": "Mes", "cantidad": "Cantidad (unidades)", "tipo": "Tipo"},
            template="plotly_dark", barmode="group",
            color_discrete_map={"ingreso": "#d4a017", "egreso": "#e67e22"},
            text="cantidad"
        )
        fig_mensual.update_traces(
            texttemplate="%{text:,.0f}", textposition="outside",
            textfont=dict(size=11, color="#e8e8ec"),
            marker_line_color="rgba(255,255,255,0.08)", marker_line_width=1,
        )
        fig_mensual.update_layout(
            height=460,
            plot_bgcolor="#14141e", paper_bgcolor="#14141e",
            font=dict(color="#e8e8ec", size=13, family="DM Sans"),
            title=dict(font=dict(size=16, color="#f0f0f5"), x=0.01),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.12)",
                       tickfont=dict(size=12, color="#c8c8d8"), title_font=dict(size=13, color="#d4a017")),
            yaxis=dict(gridcolor="rgba(255,255,255,0.07)", linecolor="rgba(255,255,255,0.12)",
                       tickfont=dict(size=12, color="#c8c8d8"), title_font=dict(size=13, color="#d4a017")),
            legend=dict(font=dict(size=13, color="#e8e8ec"),
                        bgcolor="rgba(20,20,30,0.95)", bordercolor="rgba(212,160,23,0.3)", borderwidth=1,
                        title_font=dict(size=12, color="#d4a017")),
            margin=dict(l=10, r=10, t=55, b=10),
        )
        st.markdown('<div class="dash-chart-box">', unsafe_allow_html=True)
        st.plotly_chart(fig_mensual, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

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

    if st.session_state.get("rol") == "admin":
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

    # ── Subcategoría Agroquímicos ──────────────────────────────
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
            if es_agroquimico_ing:
                st.warning(f"⚠️ No hay productos cargados como '{subcategoria_ing}' en esta categoría.")
            else:
                st.warning("⚠️ No hay productos en esta categoría.")
            return
        prod_options = {p["nombre"]: p["id"] for p in productos}
        prod_sel = st.selectbox("🏷️ Producto *", list(prod_options.keys()), key="ing_prod")
        producto_id = prod_options[prod_sel]
        
        prod_info = next((p for p in productos if p["id"] == producto_id), None)
        if prod_info:
            def _safe(v, default=''): return str(v).strip() if v and str(v).strip() not in ('None', 'none', '') else default
            marca_str = _safe(prod_info.get('marca'))
            conc_str = _safe(prod_info.get('concentracion'))
            presentacion_str = _safe(prod_info.get('presentacion'), 'Sin presentación')
            unidad_str = _safe(prod_info.get('unidad_medida'), 'unidad')
            extra = " | ".join(x for x in [marca_str, conc_str] if x)
            parts = [x for x in [presentacion_str, unidad_str, extra] if x]
            st.caption("📦 " + " | ".join(parts))

    # ── Fecha de vencimiento: selectbox reactivo FUERA del form ──
    from zoneinfo import ZoneInfo
    _now_arg = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).replace(tzinfo=None)
    st.caption(f"🕐 Fecha y hora del registro: **{_now_arg.strftime('%d/%m/%Y  %H:%M')}** (se guarda automáticamente)")

    col_venc_sel, col_venc_fecha = st.columns([1, 2])
    with col_venc_sel:
        tiene_vencimiento_sel = st.selectbox(
            "📅 ¿Tiene fecha de vencimiento?",
            ["No", "Sí — Vigente", "Sí — Vencido"],
            key="ing_tiene_venc"
        )
    with col_venc_fecha:
        fecha_vencimiento = None
        if tiene_vencimiento_sel == "Sí — Vigente":
            fecha_vencimiento = st.date_input(
                "Fecha de vencimiento",
                value=date.today().replace(year=date.today().year + 1),
                min_value=date.today(),
                key="fecha_venc_ing"
            )
        elif tiene_vencimiento_sel == "Sí — Vencido":
            fecha_vencimiento = st.date_input(
                "Fecha de vencimiento (pasada)",
                value=date.today().replace(year=date.today().year - 1),
                max_value=date.today(),
                key="fecha_venc_ing"
            )

    with st.form("form_ingreso", clear_on_submit=True):
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
                st.info("💡 No hay proveedores cargados")

        with col5:
            tipo_ingreso = st.selectbox("📌 Tipo de Ingreso", ["Compra", "Devolución", "Traslado", "Otro"])

        col_mc1, col_mc2 = st.columns(2)
        with col_mc1:
            marca_ing = st.text_input("🏷️ Marca", placeholder="Ej: Bayer, YPF Agro, Dow...")
        with col_mc2:
            concentracion_ing = st.text_input("🧪 Concentración", placeholder="Ej: 48%, 500 g/L...")

        observaciones = st.text_area("📝 Observaciones", placeholder="N° factura, lote, detalles adicionales...")

        submitted = st.form_submit_button("✅ Registrar Ingreso", use_container_width=True)

        if submitted:
            if cantidad <= 0:
                st.error("❌ La cantidad debe ser mayor a 0")
                return

            try:
                with st.spinner("Registrando ingreso..."):
                    obs_parts = [f"[{tipo_ingreso}]"]
                    if tiene_vencimiento_sel == "Sí — Vigente" and fecha_vencimiento:
                        obs_parts.append(f"Vence: {fecha_vencimiento.strftime('%d/%m/%Y')}")
                    elif tiene_vencimiento_sel == "Sí — Vencido" and fecha_vencimiento:
                        obs_parts.append(f"⚠️ VENCIDO: {fecha_vencimiento.strftime('%d/%m/%Y')}")
                    else:
                        obs_parts.append("No contiene fecha de Vec.")
                    if observaciones:
                        obs_parts.append(observaciones)
                    observaciones_full = " | ".join(obs_parts)

                    now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).replace(tzinfo=None)
                    fecha_con_hora = now.isoformat()
                    payload = {
                        "tipo": "ingreso",
                        "producto_id": producto_id,
                        "establecimiento_id": establecimiento_id,
                        "cantidad": float(cantidad),
                        "fecha": fecha_con_hora,
                        "proveedor_id": proveedor_id,
                        "observaciones": observaciones_full,
                        "usuario_id": st.session_state.get("user_id"),
                        "marca": marca_ing.strip() if marca_ing and marca_ing.strip() else None,
                        "concentracion": concentracion_ing.strip() if concentracion_ing and concentracion_ing.strip() else None,
                    }
                    if tiene_vencimiento_sel in ("Sí — Vigente", "Sí — Vencido") and fecha_vencimiento:
                        payload["fecha_vencimiento"] = fecha_vencimiento.isoformat()

                    try:
                        supabase.table("movimientos").insert(payload).execute()
                    except Exception as e_inner:
                        if "fecha_vencimiento" in str(e_inner):
                            payload.pop("fecha_vencimiento", None)
                            supabase.table("movimientos").insert(payload).execute()
                        else:
                            raise e_inner

                    tiene_venc = tiene_vencimiento_sel in ("Sí — Vigente", "Sí — Vencido") and fecha_vencimiento
                    st.success(
                        "✅ Ingreso registrado exitosamente!"
                        + (f" — Vencimiento: {fecha_vencimiento.strftime('%d/%m/%Y')}" if tiene_venc else " — Sin fecha de vencimiento")
                    )
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

    if st.session_state.get("rol") == "admin":
        estab_options = {e["nombre"]: e["id"] for e in establecimientos}
        estab_sel = st.selectbox("🏢 Establecimiento *", list(estab_options.keys()), key="egr_estab")
        establecimiento_id = estab_options[estab_sel]
        establecimiento_nombre = estab_sel
    else:
        establecimiento_id = st.session_state.get("establecimiento_id")
        establecimiento_nombre = st.session_state.get("establecimiento_nombre", "")
        st.info(f"📍 Establecimiento: {establecimiento_nombre}")

    col1, col2 = st.columns(2)
    with col1:
        cat_options = {c["nombre"]: c["id"] for c in categorias}
        cat_sel = st.selectbox("📁 Categoría *", list(cat_options.keys()), key="egr_cat")
        cat_id = cat_options[cat_sel]

    # ── Subcategoría Agroquímicos ──────────────────────────────
    es_agroquimico_egr = "agroquimico" in cat_sel.lower() or "agroquímico" in cat_sel.lower()
    subcategoria_egr = None
    if es_agroquimico_egr:
        subcategoria_egr = st.selectbox(
            "🌿 Tipo de Agroquímico *",
            ["Herbicidas", "Insecticidas", "Coadyuvantes"],
            key="egr_subcategoria"
        )

    with col2:
        productos = get_productos(cat_id, subcategoria_egr if es_agroquimico_egr else None)
        if not productos:
            if es_agroquimico_egr:
                st.warning(f"⚠️ No hay productos cargados como '{subcategoria_egr}' en esta categoría.")
            else:
                st.warning("⚠️ No hay productos en esta categoría.")
            return
        prod_options = {p["nombre"]: p["id"] for p in productos}
        prod_sel = st.selectbox("🏷️ Producto *", list(prod_options.keys()), key="egr_prod")
        producto_id = prod_options[prod_sel]
        
        prod_info_egr = next((p for p in productos if p["id"] == producto_id), None)
        if prod_info_egr:
            def _safe2(v, default=''): return str(v).strip() if v and str(v).strip() not in ('None', 'none', '') else default
            marca_egr = _safe2(prod_info_egr.get('marca'))
            conc_egr = _safe2(prod_info_egr.get('concentracion'))
            extra_egr = " | ".join(x for x in [marca_egr, conc_egr] if x)
            if extra_egr:
                st.caption(f"🏷️ {extra_egr}")
        
        stock_actual_df = get_stock_por_producto(establecimiento_id)
        if not stock_actual_df.empty:
            prod_stock = stock_actual_df[stock_actual_df["producto_id"] == producto_id]
            if not prod_stock.empty:
                stock_disponible = prod_stock.iloc[0]["stock"]
                st.caption(f"📊 Stock disponible: {stock_disponible:.2f} {prod_stock.iloc[0]['unidad']}")
            else:
                st.caption("📊 Stock disponible: 0")

    from zoneinfo import ZoneInfo
    _now_arg_egr = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).replace(tzinfo=None)
    st.caption(f"🕐 Fecha y hora del registro: **{_now_arg_egr.strftime('%d/%m/%Y  %H:%M')}** (se guarda automáticamente)")

    with st.form("form_egreso", clear_on_submit=True):
        col3, col4, col5 = st.columns(3)

        with col3:
            cantidad = st.number_input("📦 Cantidad *", min_value=0.001, step=0.5, format="%.3f")

        with col4:
            tipo_egreso = st.selectbox("📌 Tipo de Egreso", ["Uso", "Venta", "Traslado", "Merma", "Otro"])

        with col5:
            pass  # columna reservada para equilibrio visual

        col_mc1e, col_mc2e = st.columns(2)
        with col_mc1e:
            marca_egr_form = st.text_input("🏷️ Marca", placeholder="Ej: Bayer, YPF Agro, Dow...")
        with col_mc2e:
            concentracion_egr_form = st.text_input("🧪 Concentración", placeholder="Ej: 48%, 500 g/L...")

        observaciones = st.text_area("📝 Observaciones", placeholder="Motivo del egreso, destino, responsable, etc.")

        submitted = st.form_submit_button("✅ Registrar Egreso", use_container_width=True)

        if submitted:
            if cantidad <= 0:
                st.error("❌ La cantidad debe ser mayor a 0")
                return

            stock_actual_df = get_stock_por_producto(establecimiento_id)
            if not stock_actual_df.empty:
                prod_stock = stock_actual_df[stock_actual_df["producto_id"] == producto_id]
                if not prod_stock.empty and prod_stock.iloc[0]["stock"] < cantidad:
                    st.error(f"❌ Stock insuficiente. Disponible: {prod_stock.iloc[0]['stock']:.2f} {prod_stock.iloc[0]['unidad']}")
                    return

            try:
                with st.spinner("Registrando egreso..."):
                    observaciones_full = f"[{tipo_egreso}] {observaciones}" if observaciones else f"[{tipo_egreso}]"
                    now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).replace(tzinfo=None)
                    fecha_con_hora = now.isoformat()
                    payload = {
                        "tipo": "egreso",
                        "producto_id": producto_id,
                        "establecimiento_id": establecimiento_id,
                        "cantidad": float(cantidad),
                        "fecha": fecha_con_hora,
                        "observaciones": observaciones_full,
                        "usuario_id": st.session_state.get("user_id"),
                        "marca": marca_egr_form.strip() if marca_egr_form and marca_egr_form.strip() else None,
                        "concentracion": concentracion_egr_form.strip() if concentracion_egr_form and concentracion_egr_form.strip() else None,
                    }
                    supabase.table("movimientos").insert(payload).execute()
                    st.success(f"✅ Egreso registrado exitosamente!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error al guardar: {e}")


# ══════════════════════════════════════════════════════════════
# HISTORIAL - VERSIÓN CORREGIDA (ACTUALIZA DIRECTAMENTE SIN DUPLICAR)
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

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        tipo_filtro = st.selectbox("Tipo de movimiento", ["Todos", "ingreso", "egreso"])
    with col_f2:
        fecha_desde = st.date_input("Desde", value=date.today() - timedelta(days=30))
    with col_f3:
        fecha_hasta = st.date_input("Hasta", value=date.today())
    with col_f4:
        categorias = get_categorias()
        cat_options = {c["nombre"]: c["id"] for c in categorias}
        cat_options["Todas"] = None
        cat_seleccionada = st.selectbox("Categoría", list(cat_options.keys()))
        cat_id = cat_options[cat_seleccionada] if cat_seleccionada != "Todas" else None

    # Subcategoría agroquímicos (fila extra si corresponde)
    es_agro_hist = cat_seleccionada and ("agroquimico" in cat_seleccionada.lower() or "agroquímico" in cat_seleccionada.lower())
    subcategoria_hist = None
    if es_agro_hist:
        subcategoria_hist = st.selectbox(
            "🌿 Tipo de Agroquímico",
            ["Todos", "Herbicidas", "Insecticidas", "Coadyuvantes"],
            key="hist_subcategoria"
        )

    movimientos = get_movimientos_con_filtros(
        establecimiento_id=estab_filter(),
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        tipo=tipo_filtro if tipo_filtro != "Todos" else None,
        categoria_id=cat_id
    )

    # Filtrar por subcategoría en el DataFrame si corresponde
    if movimientos and es_agro_hist and subcategoria_hist and subcategoria_hist != "Todos":
        ids_subcat = {p["id"] for p in get_productos(cat_id, subcategoria_hist)}
        movimientos = [m for m in movimientos if m.get("producto_id") in ids_subcat]
    
    if not movimientos:
        st.info("💡 Sin movimientos en el período seleccionado.")
        return
    
    df = pd.DataFrame(movimientos)
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], utc=True).dt.tz_convert("America/Argentina/Buenos_Aires").dt.tz_localize(None)
        df = df.sort_values("fecha", ascending=False)
    
    df["producto_nombre"] = df["productos"].apply(lambda x: x.get("nombre", "") if isinstance(x, dict) else "")
    def _safe_str(v):
        return str(v).strip() if v and str(v).strip() not in ("None", "none", "") else ""
    df["producto_marca"] = df.apply(lambda r: _safe_str(r.get("marca")), axis=1)
    df["producto_concentracion"] = df.apply(lambda r: _safe_str(r.get("concentracion")), axis=1)
    df["producto_presentacion"] = df["productos"].apply(lambda x: x.get("presentacion", "") if isinstance(x, dict) else "")
    df["producto_unidad"] = df["productos"].apply(lambda x: x.get("unidad_medida", "unidad") if isinstance(x, dict) else "unidad")
    df["categoria"] = df["productos"].apply(lambda x: x.get("categorias", {}).get("nombre", "") if isinstance(x, dict) else "")
    df["establecimiento"] = df["establecimientos"].apply(lambda x: x.get("nombre", "") if isinstance(x, dict) else "")
    
    # Separar fecha y hora
    df["fecha_solo"] = df["fecha"].dt.strftime("%d/%m/%Y")
    df["hora_solo"] = df["fecha"].dt.strftime("%H:%M")

    # Formatear fecha de vencimiento si existe
    if "fecha_vencimiento" in df.columns:
        df["vencimiento"] = pd.to_datetime(df["fecha_vencimiento"], errors="coerce").dt.strftime("%d/%m/%Y").fillna("—")
    else:
        df["vencimiento"] = "—"

    st.markdown(f"### 📊 Resultados: **{len(df)}** movimientos encontrados")

    display_df = df[["fecha_solo", "hora_solo", "tipo", "establecimiento", "categoria", "producto_nombre", "producto_marca", "producto_concentracion", "producto_presentacion", "cantidad", "producto_unidad", "vencimiento", "observaciones"]].copy()
    display_df.columns = ["Fecha", "Hora", "Tipo", "Establecimiento", "Categoría", "Producto", "Marca", "Concentración", "Presentación", "Cantidad", "Unidad", "Vencimiento", "Observaciones"]

    st.dataframe(
        display_df,
        use_container_width=True,
        height=500,
        column_config={
            "Fecha":         st.column_config.TextColumn("Fecha",        width="small"),
            "Hora":          st.column_config.TextColumn("Hora",         width="small"),
            "Tipo":          st.column_config.TextColumn("Tipo",         width="small"),
            "Establecimiento": st.column_config.TextColumn("Estab.",     width="small"),
            "Categoría":     st.column_config.TextColumn("Categoría",    width="medium"),
            "Producto":      st.column_config.TextColumn("Producto",     width="medium"),
            "Marca":         st.column_config.TextColumn("Marca",        width="medium"),
            "Concentración": st.column_config.TextColumn("Conc.",        width="small"),
            "Presentación":  st.column_config.TextColumn("Presentación", width="small"),
            "Cantidad":      st.column_config.NumberColumn("Cantidad",   width="small"),
            "Unidad":        st.column_config.TextColumn("Unidad",       width="small"),
            "Vencimiento":   st.column_config.TextColumn("Vencimiento",  width="small"),
            "Observaciones": st.column_config.TextColumn("Observaciones",width="large"),
        }
    )

    # ── Exportar Historial a Excel ────────────────────────────
    st.markdown("#### 📥 Exportar Historial")
    buf_hist = BytesIO()
    with pd.ExcelWriter(buf_hist, engine="openpyxl") as writer:
        display_df.to_excel(writer, index=False, sheet_name="Historial_Movimientos")
    filtro_nombre = cat_seleccionada if cat_seleccionada != "Todas" else "general"
    if es_agro_hist and subcategoria_hist and subcategoria_hist != "Todos":
        filtro_nombre = f"{filtro_nombre}_{subcategoria_hist}"
    st.download_button(
        f"📥 Exportar {len(display_df)} movimientos a Excel",
        data=buf_hist.getvalue(),
        file_name=f"historial_{filtro_nombre}_{fecha_desde}_{fecha_hasta}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_hist"
    )

    # ── Sección Admin: Editar y Eliminar ──────────────────────────
    if st.session_state.get("rol") == "admin":

        # Construir opciones con ID del movimiento (compartido entre editar y eliminar)
        df_ids = df.copy()
        df_ids["etiqueta"] = df_ids.apply(
            lambda r: f"[{r['fecha_solo']} {r['hora_solo']}] {r['tipo'].upper()} — {r['producto_nombre']} — {r['establecimiento']} — {r['cantidad']} {r['producto_unidad']}",
            axis=1
        )
        opciones_mov = {row["etiqueta"]: row["id"] for _, row in df_ids.iterrows()}

        # ── EDITAR REGISTRO (ACTUALIZACIÓN DIRECTA - SIN DUPLICAR) ────────────────────────────────────────
        st.markdown("---")
        st.markdown("### ✏️ Editar registro (Admin)")
        st.info("ℹ️ Se actualizará el registro existente con los cambios realizados.")

        mov_a_editar_label = st.selectbox(
            "Seleccionar movimiento a editar",
            ["— Seleccioná un registro —"] + list(opciones_mov.keys()),
            key="sel_editar_mov"
        )

        if mov_a_editar_label != "— Seleccioná un registro —":
            mov_edit_id = opciones_mov[mov_a_editar_label]
            mov_orig = df_ids[df_ids["id"] == mov_edit_id].iloc[0]

            # Obtener datos completos del movimiento original desde Supabase
            mov_full = supabase.table("movimientos").select("*").eq("id", mov_edit_id).execute().data
            mov_full = mov_full[0] if mov_full else {}

            fv_orig = mov_full.get("fecha_vencimiento")
            fecha_venc_orig = date.fromisoformat(fv_orig) if fv_orig else None

            st.markdown("**Datos del registro original:**")
            st.caption(mov_a_editar_label)
            st.markdown("**Modificar campos:**")

            # Conservar fecha/hora original del movimiento
            nueva_fecha = mov_orig["fecha"].date() if hasattr(mov_orig["fecha"], "date") else date.today()
            nueva_hora = mov_orig["fecha"].time() if hasattr(mov_orig["fecha"], "time") else datetime.now().time()

            nueva_cantidad = st.number_input(
                "📦 Cantidad",
                min_value=0.001, step=0.5, format="%.3f",
                value=float(mov_orig.get("cantidad", 1)),
                key="ed_cantidad"
            )

            # Checkbox FUERA del form para que reactive la UI inmediatamente
            col_ed4, col_ed5 = st.columns([1, 2])
            with col_ed4:
                actualizar_venc_edit = st.checkbox(
                    "📅 Agregar / actualizar fecha de vencimiento",
                    value=fecha_venc_orig is not None,
                    key="chk_venc_edit"
                )
            with col_ed5:
                nueva_fecha_venc_edit = None
                if actualizar_venc_edit:
                    nueva_fecha_venc_edit = st.date_input(
                        "Fecha de vencimiento",
                        value=fecha_venc_orig if fecha_venc_orig else date.today().replace(year=date.today().year + 1),
                        key="fv_edit_hist"
                    )

            nueva_obs = st.text_area(
                "📝 Observaciones corregidas",
                value=mov_full.get("observaciones", "") or "",
                placeholder="Podés modificar las observaciones del registro...",
                key="ed_obs"
            )
            motivo_edicion = st.text_input(
                "📋 Motivo de la corrección *",
                placeholder="Ej: Error en cantidad, fecha de vencimiento incorrecta, etc.",
                key="ed_motivo"
            )

            if st.button("💾 Guardar corrección", use_container_width=True, key="btn_guardar_correccion"):
                if not motivo_edicion.strip():
                    st.error("❌ El motivo de la corrección es obligatorio.")
                else:
                    try:
                        from zoneinfo import ZoneInfo
                        now_arg = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).replace(tzinfo=None)
                        fecha_nueva_con_hora = datetime.combine(nueva_fecha, nueva_hora).isoformat()

                        # Construir las nuevas observaciones con el motivo de corrección
                        obs_original = mov_full.get("observaciones", "") or ""
                        nuevas_obs = f"{nueva_obs.strip()} | [CORREGIDO {now_arg.strftime('%d/%m/%Y %H:%M')} — {motivo_edicion.strip()}]"
                        if obs_original and not nuevas_obs.strip().startswith(obs_original):
                            nuevas_obs = f"{obs_original} | {nuevas_obs}"
                        
                        # Preparar payload con los datos actualizados
                        update_payload = {
                            "cantidad": float(nueva_cantidad),
                            "fecha": fecha_nueva_con_hora,
                            "observaciones": nuevas_obs,
                        }
                        
                        # Actualizar fecha de vencimiento si corresponde
                        if actualizar_venc_edit and nueva_fecha_venc_edit:
                            update_payload["fecha_vencimiento"] = nueva_fecha_venc_edit.isoformat()
                        elif not actualizar_venc_edit:
                            update_payload["fecha_vencimiento"] = None
                        
                        # ACTUALIZAR DIRECTAMENTE EL REGISTRO EXISTENTE
                        supabase.table("movimientos").update(update_payload).eq("id", mov_edit_id).execute()

                        venc_msg = f" | Vencimiento: {nueva_fecha_venc_edit.strftime('%d/%m/%Y')}" if (actualizar_venc_edit and nueva_fecha_venc_edit) else (" | Vencimiento eliminado" if not actualizar_venc_edit and fecha_venc_orig else "")
                        st.success(f"✅ Registro actualizado correctamente.{venc_msg}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al actualizar: {e}")

        # ── ELIMINAR REGISTRO ──────────────────────────────────────
        st.markdown("---")
        st.markdown("### 🗑️ Eliminar registro (Admin)")
        st.warning("⚠️ Al eliminar un registro se guardará un log de auditoría con tu usuario, fecha y hora.")

        mov_a_eliminar_label = st.selectbox("Seleccionar movimiento a eliminar", ["— Seleccioná un registro —"] + list(opciones_mov.keys()), key="sel_eliminar_mov")
        motivo_eliminacion = st.text_input("📝 Motivo de la eliminación *", placeholder="Ej: Error de carga, duplicado, etc.", key="motivo_eliminacion")

        col_del1, col_del2 = st.columns([1, 3])
        with col_del1:
            confirmar_delete = st.checkbox("✅ Confirmar eliminación", key="confirmar_del")
        with col_del2:
            if st.button("🗑️ Eliminar registro", key="btn_eliminar_mov"):
                if mov_a_eliminar_label == "— Seleccioná un registro —":
                    st.error("❌ Seleccioná un registro a eliminar.")
                elif not motivo_eliminacion.strip():
                    st.error("❌ El motivo de eliminación es obligatorio.")
                elif not confirmar_delete:
                    st.error("❌ Marcá la casilla de confirmación antes de eliminar.")
                else:
                    mov_id = opciones_mov[mov_a_eliminar_label]
                    try:
                        audit_payload = {
                            "accion": "ELIMINACION",
                            "tabla": "movimientos",
                            "registro_id": str(mov_id),
                            "usuario_id": st.session_state.get("user_id"),
                            "motivo": motivo_eliminacion.strip(),
                            "detalle": f"{mov_a_eliminar_label}",
                            "fecha_accion": datetime.utcnow().isoformat(),
                        }
                        try:
                            supabase.table("auditoria_eliminaciones").insert(audit_payload).execute()
                        except Exception:
                            pass
                        supabase.table("movimientos").delete().eq("id", mov_id).execute()
                        st.success(f"✅ Registro eliminado y auditoría guardada.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al eliminar: {e}")
    
    if not df.empty:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            display_df.to_excel(writer, index=False, sheet_name="Movimientos")
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
    
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        umbral_bajo = st.number_input("⚠️ Umbral de stock bajo (unidades)", min_value=0, value=100, step=10)
    with col_u2:
        umbral_critico = st.number_input("🔴 Umbral de stock crítico (unidades)", min_value=0, value=50, step=10)
    
    stock_productos = get_stock_por_producto(estab_filter())
    
    if stock_productos.empty:
        st.info("💡 Sin datos para mostrar alertas.")
        return
    
    stock_bajo = stock_productos[stock_productos["stock"] < umbral_bajo]
    stock_critico = stock_productos[stock_productos["stock"] < umbral_critico]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⚠️ STOCK BAJO</div>
            <div class="metric-value">{len(stock_bajo)}</div>
            <div style="font-size:0.7rem;">productos con menos de {umbral_bajo} unidades</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔴 STOCK CRÍTICO</div>
            <div class="metric-value">{len(stock_critico)}</div>
            <div style="font-size:0.7rem;">productos con menos de {umbral_critico} unidades</div>
        </div>
        """, unsafe_allow_html=True)
    
    if not stock_bajo.empty:
        st.markdown("---")
        st.markdown("### 📋 Productos con Stock Bajo")
        stock_bajo["alerta"] = stock_bajo["stock"].apply(lambda x: "🔴 Crítico" if x < umbral_critico else "⚠️ Bajo")
        st.dataframe(stock_bajo[["producto", "categoria", "presentacion", "stock", "unidad", "alerta"]], use_container_width=True)
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
    
    movimientos = get_movimientos(estab_filter(), limit=5000)
    
    if not movimientos:
        st.info("💡 Sin datos para generar reportes.")
        return
    
    df = pd.DataFrame(movimientos)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    df["año"] = df["fecha"].dt.year
    df["producto_nombre"] = df["productos"].apply(lambda x: x.get("nombre", "") if isinstance(x, dict) else "")
    
    años = sorted(df["año"].unique())
    año_seleccionado = st.selectbox("📅 Seleccionar año", años, index=len(años)-1)
    
    df_año = df[df["año"] == año_seleccionado]
    
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        total_ingresos = df_año[df_año["tipo"] == "ingreso"]["cantidad"].sum() if "ingreso" in df_año["tipo"].values else 0
        st.metric("📥 Total Ingresos", f"{total_ingresos:,.0f}")
    with col_r2:
        total_egresos = df_año[df_año["tipo"] == "egreso"]["cantidad"].sum() if "egreso" in df_año["tipo"].values else 0
        st.metric("📤 Total Egresos", f"{total_egresos:,.0f}")
    with col_r3:
        total_movimientos = len(df_año)
        st.metric("🔄 Total Movimientos", total_movimientos)
    
    st.markdown(f"### 📊 Resumen Mensual {año_seleccionado}")
    
    resumen = df_año.groupby(["mes", "tipo"])["cantidad"].sum().reset_index()
    st.dataframe(resumen, use_container_width=True)
    
    st.markdown("### 📈 Tendencia de Movimientos")
    chart_data = df_año.groupby(["mes", "tipo"])["cantidad"].sum().unstack()
    st.bar_chart(chart_data)
    
    st.markdown("### 🏆 Top 10 Productos más movidos")
    top_movidos = df_año.groupby("producto_nombre")["cantidad"].sum().sort_values(ascending=False).head(10).reset_index()
    top_movidos.columns = ["Producto", "Cantidad total movida"]
    st.dataframe(top_movidos, use_container_width=True)
    
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
            contacto = st.text_input("Contacto (teléfono/email)", placeholder="Opcional")
            if st.form_submit_button("Guardar"):
                if nombre:
                    supabase.table("proveedores").insert({
                        "nombre": nombre,
                        "contacto": contacto if contacto else None,
                        "activo": True
                    }).execute()
                    st.success(f"✅ Proveedor '{nombre}' agregado")
                    st.rerun()
    
    if proveedores:
        df = pd.DataFrame(proveedores)
        display_cols = ["nombre", "contacto", "activo", "created_at"] if "contacto" in df.columns else ["nombre", "activo", "created_at"]
        st.dataframe(df[display_cols], use_container_width=True)
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
        # ── Selectores reactivos FUERA del form ───────────────────
        cat_sel = st.selectbox("Categoría", list(cat_options.keys()), key="nuevo_prod_cat")
        es_agro_nuevo = "agroquimico" in cat_sel.lower() or "agroquímico" in cat_sel.lower()
        subcategoria_nuevo = None
        if es_agro_nuevo:
            subcategoria_nuevo = st.selectbox(
                "🌿 Tipo de Agroquímico *",
                ["Herbicidas", "Insecticidas", "Coadyuvantes"],
                key="nuevo_prod_subcategoria"
            )

        with st.form("nuevo_producto"):
            nombre = st.text_input("Nombre del producto")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                marca = st.text_input("🏷️ Marca", placeholder="Ej: Bayer, YPF Agro, etc.")
                presentacion = st.text_input("Presentación", placeholder="Ej: Bidón 20L, Bolsa 50kg, etc.")
            with col_p2:
                concentracion = st.text_input("🧪 Concentración", placeholder="Ej: 48%, 500 g/L, etc.")
                unidad_medida = st.selectbox("Unidad de medida", ["litros", "kg", "unidades", "bolsas", "bidones", "otros"])
            if st.form_submit_button("Guardar"):
                if nombre:
                    # Verificar si ya existe un producto con el mismo nombre (sin distinción de mayúsculas)
                    existentes = supabase.table("productos").select("id, nombre, presentacion, activo") \
                        .ilike("nombre", nombre.strip()).execute().data
                    duplicado = next(
                        (p for p in existentes if (p.get("presentacion") or "").strip().lower() == presentacion.strip().lower()),
                        None
                    ) if existentes else None

                    if duplicado and not st.session_state.get("confirmar_duplicado"):
                        estado = "activo" if duplicado.get("activo") else "inactivo (desactivado)"
                        st.session_state["confirmar_duplicado"] = True
                        st.session_state["prod_duplicado_info"] = {
                            "nombre": nombre, "cat_sel": cat_sel, "marca": marca,
                            "presentacion": presentacion, "concentracion": concentracion,
                            "unidad_medida": unidad_medida, "estado": estado,
                            "subcategoria": subcategoria_nuevo
                        }
                        st.rerun()
                    else:
                        # No hay duplicado o el admin confirmó continuar
                        st.session_state.pop("confirmar_duplicado", None)
                        st.session_state.pop("prod_duplicado_info", None)
                        supabase.table("productos").insert({
                            "categoria_id": cat_options[cat_sel],
                            "nombre": nombre,
                            "marca": marca if marca else None,
                            "concentracion": concentracion if concentracion else None,
                            "presentacion": presentacion if presentacion else None,
                            "unidad_medida": unidad_medida,
                            "subcategoria": subcategoria_nuevo,
                            "activo": True
                        }).execute()
                        st.success(f"✅ Producto '{nombre}' agregado")
                        st.rerun()
                else:
                    st.warning("⚠️ El nombre del producto no puede estar vacío.")

        # Aviso de duplicado FUERA del form (para poder mostrar el botón de confirmar)
        if st.session_state.get("confirmar_duplicado"):
            info = st.session_state.get("prod_duplicado_info", {})
            st.warning(
                f"⚠️ **Producto ya se encuentra en el sistema**\n\n"
                f"El producto **\"{info.get('nombre')}\"** "
                f"({'con presentación: ' + info.get('presentacion') if info.get('presentacion') else 'sin presentación especificada'}) "
                f"ya existe y está **{info.get('estado', 'registrado')}**.\n\n"
                f"¿Deseás agregarlo de todas formas?"
            )
            col_c1, col_c2 = st.columns([1, 3])
            with col_c1:
                if st.button("✅ Sí, agregar igual", key="btn_confirmar_dup"):
                    d = info
                    supabase.table("productos").insert({
                        "categoria_id": cat_options[d["cat_sel"]],
                        "nombre": d["nombre"],
                        "marca": d["marca"] if d["marca"] else None,
                        "concentracion": d["concentracion"] if d["concentracion"] else None,
                        "presentacion": d["presentacion"] if d["presentacion"] else None,
                        "unidad_medida": d["unidad_medida"],
                        "subcategoria": d.get("subcategoria"),
                        "activo": True
                    }).execute()
                    st.session_state.pop("confirmar_duplicado", None)
                    st.session_state.pop("prod_duplicado_info", None)
                    st.success(f"✅ Producto '{d['nombre']}' agregado igualmente.")
                    st.rerun()
            with col_c2:
                if st.button("❌ Cancelar", key="btn_cancelar_dup"):
                    st.session_state.pop("confirmar_duplicado", None)
                    st.session_state.pop("prod_duplicado_info", None)
                    st.rerun()
    
    productos = get_productos()
    if productos:
        df = pd.DataFrame(productos)
        df["categoria"] = df["categorias"].apply(lambda x: x["nombre"] if x else "N/A")
        if "marca" not in df.columns:
            df["marca"] = ""
        if "concentracion" not in df.columns:
            df["concentracion"] = ""

        with st.expander("✏️ Editar producto existente", expanded=False):
            prod_opciones = {
                f"{row['nombre']} — {row['categoria']} ({row.get('presentacion') or 'sin presentación'})": row["id"]
                for _, row in df.iterrows()
            }
            prod_sel_label = st.selectbox("Seleccionar producto a editar", list(prod_opciones.keys()), key="edit_prod_sel")
            prod_sel_id = prod_opciones[prod_sel_label]
            prod_data = df[df["id"] == prod_sel_id].iloc[0]

            # Buscar el último ingreso de este producto para mostrar/editar su fecha de vencimiento
            ultimo_ingreso = None
            fecha_venc_actual = None
            try:
                ingresos = supabase.table("movimientos")                     .select("id, fecha, fecha_vencimiento")                     .eq("producto_id", prod_sel_id)                     .eq("tipo", "ingreso")                     .order("fecha", desc=True)                     .limit(1)                     .execute().data
                if ingresos:
                    ultimo_ingreso = ingresos[0]
                    fv = ultimo_ingreso.get("fecha_vencimiento")
                    if fv:
                        fecha_venc_actual = date.fromisoformat(fv)
            except Exception:
                pass

            if ultimo_ingreso:
                fecha_ing_str = ultimo_ingreso.get("fecha", "")[:10] if ultimo_ingreso.get("fecha") else "—"
                if fecha_venc_actual:
                    dias_restantes = (fecha_venc_actual - date.today()).days
                    if dias_restantes < 0:
                        estado_venc = f"🔴 Vencido hace {abs(dias_restantes)} días"
                    elif dias_restantes <= 30:
                        estado_venc = f"🟠 Vence en {dias_restantes} días"
                    else:
                        estado_venc = f"🟢 Vence en {dias_restantes} días"
                    st.info(f"📦 Último ingreso: **{fecha_ing_str}** | 📅 Vencimiento actual: **{fecha_venc_actual.strftime('%d/%m/%Y')}** — {estado_venc}")
                else:
                    st.info(f"📦 Último ingreso: **{fecha_ing_str}** | 📅 Sin fecha de vencimiento registrada")
            else:
                st.caption("ℹ️ Este producto no tiene ingresos registrados.")

            with st.form("editar_producto"):
                cat_sel_edit = st.selectbox(
                    "Categoría",
                    list(cat_options.keys()),
                    index=list(cat_options.keys()).index(prod_data["categoria"]) if prod_data["categoria"] in cat_options else 0
                )
                es_agro_edit = "agroquimico" in cat_sel_edit.lower() or "agroquímico" in cat_sel_edit.lower()
                subcategoria_edit = None
                if es_agro_edit:
                    subcats = ["Herbicidas", "Insecticidas", "Coadyuvantes"]
                    subcat_actual = prod_data.get("subcategoria") or "Herbicidas"
                    subcat_idx = subcats.index(subcat_actual) if subcat_actual in subcats else 0
                    subcategoria_edit = st.selectbox(
                        "🌿 Tipo de Agroquímico *",
                        subcats,
                        index=subcat_idx,
                        key="edit_subcategoria"
                    )
                nombre_edit = st.text_input("Nombre del producto", value=prod_data["nombre"])
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    marca_edit = st.text_input("🏷️ Marca", value=prod_data.get("marca") or "")
                    presentacion_edit = st.text_input("Presentación", value=prod_data.get("presentacion") or "")
                with col_e2:
                    concentracion_edit = st.text_input("🧪 Concentración", value=prod_data.get("concentracion") or "")
                    unidades = ["litros", "kg", "unidades", "bolsas", "bidones", "otros"]
                    unidad_actual = prod_data.get("unidad_medida") or "unidades"
                    unidad_edit = st.selectbox(
                        "Unidad de medida",
                        unidades,
                        index=unidades.index(unidad_actual) if unidad_actual in unidades else 0
                    )
                activo_edit = st.checkbox("Producto activo", value=bool(prod_data.get("activo", True)))

                st.markdown("---")
                col_venc_e1, col_venc_e2 = st.columns([1, 2])
                with col_venc_e1:
                    actualizar_venc = st.checkbox(
                        "📅 Actualizar fecha de vencimiento",
                        value=False,
                        help="Modifica la fecha de vencimiento del último ingreso de este producto"
                    )
                with col_venc_e2:
                    nueva_fecha_venc = None
                    if actualizar_venc:
                        nueva_fecha_venc = st.date_input(
                            "Nueva fecha de vencimiento",
                            value=fecha_venc_actual if fecha_venc_actual else date.today().replace(year=date.today().year + 1),
                            key="nueva_fecha_venc_edit"
                        )

                col_btn1, col_btn2 = st.columns([3, 1])
                with col_btn1:
                    guardar = st.form_submit_button("💾 Guardar cambios")
                with col_btn2:
                    eliminar = st.form_submit_button("🗑️ Desactivar")

                if guardar:
                    if nombre_edit:
                        supabase.table("productos").update({
                            "categoria_id": cat_options[cat_sel_edit],
                            "nombre": nombre_edit,
                            "marca": marca_edit if marca_edit else None,
                            "concentracion": concentracion_edit if concentracion_edit else None,
                            "presentacion": presentacion_edit if presentacion_edit else None,
                            "unidad_medida": unidad_edit,
                            "subcategoria": subcategoria_edit,
                            "activo": activo_edit
                        }).eq("id", prod_sel_id).execute()

                        # Actualizar fecha_vencimiento del último ingreso si se indicó
                        if actualizar_venc and nueva_fecha_venc and ultimo_ingreso:
                            supabase.table("movimientos").update({
                                "fecha_vencimiento": nueva_fecha_venc.isoformat()
                            }).eq("id", ultimo_ingreso["id"]).execute()
                            st.success(f"✅ Producto '{nombre_edit}' actualizado | Vencimiento: {nueva_fecha_venc.strftime('%d/%m/%Y')}")
                        else:
                            st.success(f"✅ Producto '{nombre_edit}' actualizado correctamente")
                        st.rerun()
                    else:
                        st.warning("⚠️ El nombre del producto no puede estar vacío.")

                if eliminar:
                    supabase.table("productos").update({"activo": False}).eq("id", prod_sel_id).execute()
                    st.warning(f"⚠️ Producto '{prod_data['nombre']}' desactivado.")
                    st.rerun()

        display_cols = ["categoria", "nombre", "subcategoria", "marca", "concentracion", "presentacion", "unidad_medida", "activo"]
        df["subcategoria"] = df.get("subcategoria", pd.Series([""] * len(df)))
        df_display = df[[c for c in display_cols if c in df.columns]].copy()
        col_names = {"categoria": "Categoría", "nombre": "Producto", "subcategoria": "Subcategoría",
                     "marca": "Marca", "concentracion": "Concentración",
                     "presentacion": "Presentación", "unidad_medida": "Unidad", "activo": "Activo"}
        df_display.columns = [col_names.get(c, c) for c in df_display.columns]
        st.dataframe(df_display, use_container_width=True)
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
            display_cols = ["nombre", "email", "rol", "establecimiento_nombre", "password_changed", "created_at"]
            st.dataframe(df[display_cols], use_container_width=True)
        else:
            st.info("💡 No hay usuarios cargados")
    except Exception as e:
        st.error(f"❌ Error: {e}")
    
    st.markdown("---")
    st.markdown("### 📝 Asignar usuario a establecimiento")
    
    usuarios_sin_estab = supabase.table("usuarios").select("*").is_("establecimiento_id", "null").execute().data
    if usuarios_sin_estab:
        usuario_opciones = {u["nombre"]: u["id"] for u in usuarios_sin_estab if u["rol"] != "admin"}
        if usuario_opciones:
            usuario_sel = st.selectbox("Seleccionar usuario", list(usuario_opciones.keys()))
            establecimientos = get_establecimientos()
            estab_opciones = {e["nombre"]: e["id"] for e in establecimientos}
            estab_sel = st.selectbox("Asignar a establecimiento", list(estab_opciones.keys()))
            
            if st.button("Asignar establecimiento"):
                supabase.table("usuarios").update({
                    "establecimiento_id": estab_opciones[estab_sel],
                    "establecimiento_nombre": estab_sel
                }).eq("id", usuario_opciones[usuario_sel]).execute()
                st.success(f"✅ Usuario '{usuario_sel}' asignado a {estab_sel}")
                st.rerun()
        else:
            st.info("Todos los usuarios ya tienen establecimiento asignado")
    else:
        st.info("No hay usuarios sin establecimiento asignado")


# ══════════════════════════════════════════════════════════════
# VISTA CONSOLIDADO — Estadísticas consolidadas de todos los establecimientos
# ══════════════════════════════════════════════════════════════

def pagina_consolidado():
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    st.markdown("""
    <div>
        <div class="title-bubble">
            <h1>🌐 Vista Consolidada</h1>
            <p>📋 Estadísticas consolidadas de todos los establecimientos</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    stock_df = get_stock_por_establecimiento()

    if stock_df.empty:
        st.info("💡 Sin datos para mostrar. Registrá movimientos en los establecimientos.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    establecimientos_lista = sorted(stock_df["establecimiento"].unique())

    total_stock = stock_df["stock"].sum()
    total_productos_distintos = stock_df["producto"].nunique()
    total_establecimientos = stock_df["establecimiento"].nunique()
    stock_critico = (stock_df["stock"] < 50).sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📦 STOCK TOTAL</div>
            <div class="metric-value">{total_stock:,.0f}</div>
            <div style="font-size:0.7rem; color:#a8a8b0;">unidades en todos los establecimientos</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🏢 ESTABLECIMIENTOS</div>
            <div class="metric-value">{total_establecimientos}</div>
            <div style="font-size:0.7rem; color:#a8a8b0;">con movimientos registrados</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🏷️ PRODUCTOS</div>
            <div class="metric-value">{total_productos_distintos}</div>
            <div style="font-size:0.7rem; color:#a8a8b0;">productos distintos en stock</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔴 CRÍTICOS</div>
            <div class="metric-value">{stock_critico}</div>
            <div style="font-size:0.7rem; color:#a8a8b0;">ítems con stock bajo 50 unidades</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🏢 Stock por Establecimiento")

    tabs = st.tabs(["📊 Consolidado"] + [f"🏠 {e}" for e in establecimientos_lista])

    with tabs[0]:
        pivot = stock_df.pivot_table(
            index=["categoria", "producto", "presentacion", "unidad"],
            columns="establecimiento",
            values="stock",
            aggfunc="sum",
            fill_value=0
        ).reset_index()
        pivot["TOTAL"] = pivot[establecimientos_lista].sum(axis=1) if establecimientos_lista else 0
        pivot = pivot.sort_values("TOTAL", ascending=False)
        st.dataframe(pivot, use_container_width=True, height=500)

        stock_por_estab = stock_df.groupby("establecimiento")["stock"].sum().reset_index()
        if not stock_por_estab.empty:
            fig_estab = px.bar(
                stock_por_estab,
                x="establecimiento",
                y="stock",
                title="📊 Stock Total por Establecimiento",
                labels={"establecimiento": "Establecimiento", "stock": "Stock (unidades)"},
                template="plotly_dark",
                color="stock",
                color_continuous_scale="Oranges"
            )
            fig_estab.update_layout(
                height=380,
                plot_bgcolor="rgba(30,30,35,0.8)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e8e8ec"),
                showlegend=False,
            )
            st.plotly_chart(fig_estab, use_container_width=True)

        stock_cat = stock_df.groupby("categoria")["stock"].sum().reset_index()
        if not stock_cat.empty:
            fig_torta = px.pie(
                stock_cat,
                values="stock",
                names="categoria",
                title="🥧 Distribución Global por Categoría",
                template="plotly_dark",
                color_discrete_sequence=px.colors.sequential.Oranges_r
            )
            fig_torta.update_traces(textposition="inside", textinfo="percent+label")
            fig_torta.update_layout(
                height=420,
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e8e8ec")
            )
            st.plotly_chart(fig_torta, use_container_width=True)

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            pivot.to_excel(writer, index=False, sheet_name="Consolidado")
            for estab in establecimientos_lista:
                df_e = stock_df[stock_df["establecimiento"] == estab]
                df_e.to_excel(writer, index=False, sheet_name=estab[:30])
        st.download_button(
            "📥 Exportar reporte consolidado",
            data=buffer.getvalue(),
            file_name=f"consolidado_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    for i, estab in enumerate(establecimientos_lista):
        with tabs[i + 1]:
            df_e = stock_df[stock_df["establecimiento"] == estab].copy()
            df_e = df_e.sort_values("stock", ascending=False)

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">📦 STOCK TOTAL</div>
                    <div class="metric-value">{df_e['stock'].sum():,.0f}</div>
                    <div style="font-size:0.7rem; color:#a8a8b0;">unidades</div>
                </div>""", unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">🏷️ PRODUCTOS</div>
                    <div class="metric-value">{len(df_e)}</div>
                    <div style="font-size:0.7rem; color:#a8a8b0;">en inventario</div>
                </div>""", unsafe_allow_html=True)
            with col_c:
                criticos_e = (df_e["stock"] < 50).sum()
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">🔴 CRÍTICOS</div>
                    <div class="metric-value">{criticos_e}</div>
                    <div style="font-size:0.7rem; color:#a8a8b0;">stock bajo 50</div>
                </div>""", unsafe_allow_html=True)

            st.dataframe(df_e[["categoria", "producto", "presentacion", "stock", "unidad"]], use_container_width=True, height=400)

            if not df_e.empty:
                fig_e = px.bar(
                    df_e.head(15),
                    x="producto",
                    y="stock",
                    title=f"📊 Top 15 Productos — {estab}",
                    labels={"producto": "Producto", "stock": "Stock"},
                    template="plotly_dark",
                    color="stock",
                    color_continuous_scale="Oranges"
                )
                fig_e.update_layout(
                    height=400,
                    xaxis_tickangle=-40,
                    plot_bgcolor="rgba(30,30,35,0.8)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e8e8ec"),
                )
                st.plotly_chart(fig_e, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    if not check_auth():
        login()
        return

    if not verificar_perfil():
        return

    # Verificar si el usuario necesita cambiar la contraseña
    # Solo si NO es admin Y password_changed es False Y no hay bandera temporal
    if (st.session_state.get("rol") != "admin" and 
        not st.session_state.get("password_changed", False) and
        not st.session_state.get("skip_password_check", False)):
        mostrar_cambio_password()
        return

    sidebar()

    pagina = st.session_state.get("pagina", "Dashboard")
    rol = st.session_state.get("rol", "establecimiento")
    consolidado = es_vista_consolidado()

    if consolidado and rol == "admin":
        rutas_consolidado = {
            "Consolidado": pagina_consolidado,
            "Alertas": pagina_alertas,
            "Reportes": pagina_reportes,
            "Proveedores": pagina_proveedores,
            "Productos": pagina_productos,
            "Usuarios": pagina_usuarios,
        }
        pagina_funcion = rutas_consolidado.get(pagina, pagina_consolidado)
    elif rol == "admin":
        rutas_admin = {
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
        pagina_funcion = rutas_admin.get(pagina, pagina_dashboard)
    elif rol == "establecimiento" and st.session_state.get("establecimiento_id"):
        rutas_operador = {
            "Dashboard": pagina_dashboard,
            "Nuevo Ingreso": pagina_ingreso,
            "Nuevo Egreso": pagina_egreso,
            "Historial": pagina_historial,
            "Alertas": pagina_alertas,
            "Reportes": pagina_reportes,
        }
        pagina_funcion = rutas_operador.get(pagina, pagina_dashboard)
    else:
        st.error("⚠️ Configuración de usuario incompleta. Contacta al administrador.")
        if st.button("Cerrar sesión"):
            logout()
        return

    pagina_funcion()

    estab_nombre = st.session_state.get("estab_activo_nombre", 
                                         st.session_state.get("establecimiento_nombre", "Consolidado"))
    st.markdown(f"""
    <div class="footer">
        <p>🌾 Sistema de Control de Stock Agrícola</p>
        <p>La Sonia · San Guillermo · Camba Pora &nbsp;|&nbsp; 📍 {estab_nombre}</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
