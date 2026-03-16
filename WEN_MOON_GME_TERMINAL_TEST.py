import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import plotly.graph_objects as go
import base64
from datetime import datetime

from datetime import datetime
from streamlit_cookies_manager import EncryptedCookieManager

# --- 1. CONFIGURATION & STATE INIT ---
st.set_page_config(page_title="GME TERMINAL", page_icon="Screenshot_20260216_163106_Discord.jpg", layout="wide", initial_sidebar_state="collapsed")

# --- COOKIE MANAGER INITIALIZATION ---
cookies = EncryptedCookieManager(prefix="gme_ape_", password="wen_moon_secret")
if not cookies.ready():
    st.stop()

# --- LOAD DATA FROM COOKIES TO SESSION STATE ---
if 'osq' not in st.session_state: 
    st.session_state.osq = int(cookies.get("osq", 0))
    st.session_state.osp = float(cookies.get("osp", 0.0))
    st.session_state.owq = int(cookies.get("owq", 0))
    st.session_state.owp = float(cookies.get("owp", 0.0))
    
    st.session_state.drs_osq = int(cookies.get("drs_osq", 0))
    st.session_state.drs_owq = int(cookies.get("drs_owq", 0))
    
    st.session_state.ape_name = cookies.get("ape_name", "")
    
    st.session_state.launched = False
    st.session_state.show_leaderboard = False
    st.session_state.recent_s = 0
    st.session_state.recent_w = 0

# Variables for Weekly/Monthly accumulation tracking
if 'weekly_s' not in st.session_state:
    st.session_state.update(weekly_s=0, weekly_w=0, monthly_s=0, monthly_w=0)

# Input variables for the home screen expander
if 'in_w_sq' not in st.session_state:
    st.session_state.update(in_w_sq=0, in_w_sp=0.0, in_w_wq=0, in_w_wp=0.0)
if 'in_m_sq' not in st.session_state:
    st.session_state.update(in_m_sq=0, in_m_sp=0.0, in_m_wq=0, in_m_wp=0.0)
# --- DRS VARIABLES ---
if 'drs_osq' not in st.session_state:
    st.session_state.update(drs_osq=0, drs_owq=0, weekly_drs_s=0, weekly_drs_w=0, monthly_drs_s=0, monthly_drs_w=0)
    st.session_state.update(ui_drs_osq=0, ui_drs_owq=0, in_drs_t_sq=0, in_drs_t_wq=0)

def get_b64(path):
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

# --- SECRET HOME BUTTON LOGIC ---
if st.button("BACK_HOME_SECRET", key="secret_home"):
    st.session_state.launched = False
    st.session_state.show_leaderboard = False
    st.rerun()

# --- BLINKING BUTTONS (HOME + FULLSCREEN) ---
components.html("""
<script>
    const parent = window.parent.document;
    const head = parent.querySelector('head');

    // 1. NEON ENGINE (Standard CSS)
    if (!parent.getElementById('neon-style')) {
        const style = parent.createElement('style');
        style.id = 'neon-style';
        style.innerHTML = `@keyframes neon-blink { from { box-shadow: 0 0 5px #00FF00; } 50% { box-shadow: 0 0 15px #00FF00; } to { box-shadow: 0 0 5px #00FF00; } }`;
        head.appendChild(style);
    }

    // 2. STEALTH MODE (Hides secret message)
    const hideSecret = () => {
        const ps = parent.querySelectorAll('p');
        ps.forEach(p => { if (p.innerText === 'BACK_HOME_SECRET') { 
            const btn = p.closest('div[data-testid="stButton"]'); 
            if (btn) btn.style.display = 'none'; 
        }});
    };
    hideSecret(); 
    setInterval(hideSecret, 500);

    // 3. PWA MOBILE LOGIC
    if (!parent.querySelector('#pwa-manifest')) {
        const manifest = { "name": "GME TERMINAL", "short_name": "GME", "display": "fullscreen", "background_color": "#050505", "theme_color": "#00FF00" };
        const blob = new Blob([JSON.stringify(manifest)], {type: 'application/json'});
        head.insertAdjacentHTML('beforeend', `<link id="pwa-manifest" rel="manifest" href="${URL.createObjectURL(blob)}">`);
        head.insertAdjacentHTML('beforeend', `<meta name="apple-mobile-web-app-capable" content="yes">`);
    }

    // 4. FLOATING BUTTONS (32px, Square, Bottom 40px)
    let nav = parent.getElementById('floating-nav');
    if (!nav) {
        nav = parent.createElement('div');
        nav.id = 'floating-nav';
        nav.style = "position:fixed; bottom:45px; right:6px; z-index:99999; display:flex; flex-direction:column; gap:4px; transition: opacity 0.5s; opacity: 1;";
        
        const btnStyle = "width:32px; height:32px; border-radius:4px; background:#050505; color:#00FF00; border:1px solid #00FF00; font-size:16px; cursor:pointer; box-shadow: 0 0 5px #00FF00; display:flex; align-items:center; justify-content:center;";

        const btnHome = parent.createElement('button');
        btnHome.innerHTML = '🏠';
        btnHome.style = btnStyle;
        btnHome.onclick = () => {
            const ps = parent.querySelectorAll('p');
            ps.forEach(p => { if(p.innerText === 'BACK_HOME_SECRET') p.closest('div[data-testid="stButton"]').querySelector('button').click(); });
        };

        const btnFs = parent.createElement('button');
        btnFs.innerHTML = '⛶';
        btnFs.style = btnStyle;
        btnFs.onclick = () => {
            if (!parent.fullscreenElement) parent.documentElement.requestFullscreen();
            else parent.exitFullscreen();
        };

        nav.appendChild(btnHome);
        nav.appendChild(btnFs);
        parent.body.appendChild(nav);
    }

    // 5. SMART GHOST LOGIC (4s Delay)
    let timer;
    function showNav() {
        if (!nav) return;
        nav.style.display = 'flex';
        setTimeout(() => { nav.style.opacity = '1'; }, 10);
        clearTimeout(timer);
        timer = setTimeout(() => {
            nav.style.opacity = '0';
            setTimeout(() => { if(nav.style.opacity === '0') nav.style.display = 'none'; }, 500);
        }, 4000);
    }

    ['mousedown', 'mousemove', 'touchstart', 'scroll', 'keydown'].forEach(e => {
        parent.addEventListener(e, showNav);
    });
    showNav();
</script>
""", height=0, width=0)

# --- CSS ---
st.markdown("""
<style>
    /* 👻 PHANTOM KILLER: Destroys invisible boxes from Cookies, Scripts, and CSS */
    div.element-container:has(iframe[height="0"]), div[data-testid="stElementContainer"]:has(iframe[height="0"]) { display: none !important; margin: 0px !important; padding: 0px !important; }
    div.element-container:has(style), div[data-testid="stElementContainer"]:has(style) { display: none !important; margin: 0px !important; padding: 0px !important; }

    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; margin-top: 0px !important; }
    body, .stApp { background-color: #050505 !important; color: white; }
    #MainMenu, footer, header { display: none !important; }
    @keyframes neon-text { 0%, 100% { color: white; text-shadow: none; } 50% { color: #00FF00; text-shadow: 0 0 15px #00FF00; } }
    @keyframes neon-img { 0%, 100% { filter: drop-shadow(0 0 0px transparent); } 50% { filter: drop-shadow(0 0 25px #00FF00); } }
    @keyframes nuclear-neon { 0%, 100% { filter: drop-shadow(0 0 5px #00FF00); transform: translateY(0px) scale(1); } 50% { filter: drop-shadow(0 0 25px #00FF00); transform: translateY(-15px) scale(1.1); } }
    @keyframes neon-flash-red { 0%, 100% { opacity: 1; filter: drop-shadow(0 0 10px #FF0000); } 50% { opacity: 0.4; filter: drop-shadow(0 0 30px #FF0000); } }
    .title-container { text-align: center; margin-bottom: 20px; margin-top: -10px; }
    .gme-title { font-size: 60px; line-height: 1.1; animation: neon-text 1.5s infinite; white-space: nowrap; margin: 0; }
    @media screen and (max-width: 600px) { .gme-title { font-size: 38px; } }
    .table-wrapper { overflow-x: auto; max-width: 100%; border-radius: 10px; border: 2px solid #0259c7; box-shadow: 0 0 15px #0259c7; margin-top: 10px; }
    .ldb-t { width: 100%; border-collapse: collapse; color: white; font-family: monospace; text-align: center; }
    .ldb-t th { background: #001f3f; color: #00FF00; padding: 12px; border-bottom: 2px solid #0259c7; white-space: nowrap; }
    .ldb-t td { background: #0f172a; padding: 12px; border-bottom: 1px solid #0259c7; white-space: nowrap; }
    .podium td { font-size: 18px !important; color: #00FF00 !important; font-weight: bold; }

    /* 4. TABS: NEON GREEN & CUSTOM SIZES */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #00FF00 !important;
    }
    .stTabs [aria-selected="true"] p {
        color: #00FF00 !important;
    }
    
    /* Main Tabs Label Size */
    .stTabs [data-baseweb="tab"] p {
        font-size: 22px !important; /* <--- MODIFY MAIN SIZE HERE */
    }
    
    /* Sub-Tabs Label Size (20% smaller than main) */
    .stTabs .stTabs [data-baseweb="tab"] p {
        font-size: 18px !important; /* <--- MODIFY SUB SIZE HERE */
    }
        div[data-testid="stExpander"] summary p { font-size: 22px !important; }
</style>
""", unsafe_allow_html=True)

# --- UPDATE LOGIC WITH SMART TRANSACTION TRACKER ---
def update_portfolio_logic():
    tx_type = st.session_state.get("in_tx_type", "BUY")
    
    sq = st.session_state.get("in_t_sq", 0)
    sp = st.session_state.get("in_t_sp", 0.0)
    wq = st.session_state.get("in_t_wq", 0)
    wp = st.session_state.get("in_t_wp", 0.0)
    
    # Load from shielded core memory
    new_osq = st.session_state.osq
    new_osp = st.session_state.osp
    new_owq = st.session_state.owq
    new_owp = st.session_state.owp

    if sq > 0:
        if tx_type == "BUY":
            fq = new_osq + sq
            if fq > 0:
                new_osp = ((new_osq * new_osp) + (sq * sp)) / fq
            new_osq = fq
            st.session_state.weekly_s += sq
            st.session_state.monthly_s += sq
        elif tx_type == "SELL":
            new_osq = max(0, new_osq - sq)
            
    if wq > 0:
        if tx_type == "BUY":
            fwq = new_owq + wq
            if fwq > 0:
                new_owp = ((new_owq * new_owp) + (wq * wp)) / fwq
            new_owq = fwq
            st.session_state.weekly_w += wq
            st.session_state.monthly_w += wq
        elif tx_type == "SELL":
            new_owq = max(0, new_owq - wq)

    # Save to shielded core memory
    st.session_state.osq = new_osq
    st.session_state.osp = new_osp
    st.session_state.owq = new_owq
    st.session_state.owp = new_owp
    
    # Force UI widgets to sync with new math
    st.session_state.ui_osq = new_osq
    st.session_state.ui_osp = new_osp
    st.session_state.ui_owq = new_owq
    st.session_state.ui_owp = new_owp
    
    # Reset transaction panel
    st.session_state.in_t_sq = 0
    st.session_state.in_t_sp = 0.0
    st.session_state.in_t_wq = 0
    st.session_state.in_t_wp = 0.0

# --- DRS LOGIC ENGINE ---
def update_drs_logic():
    drs_tx = st.session_state.get("in_drs_tx_type", "ADD TO DRS")
    drs_sq = st.session_state.get("in_drs_t_sq", 0)
    drs_wq = st.session_state.get("in_drs_t_wq", 0)
    
    new_drs_osq = st.session_state.drs_osq
    new_drs_owq = st.session_state.drs_owq
    
    if drs_sq > 0:
        if drs_tx == "ADD TO DRS":
            new_drs_osq += drs_sq
            st.session_state.weekly_drs_s += drs_sq
            st.session_state.monthly_drs_s += drs_sq
        elif drs_tx == "REMOVE FROM DRS":
            new_drs_osq = max(0, new_drs_osq - drs_sq)
            st.session_state.osq = max(0, st.session_state.osq - drs_sq)
            st.session_state.ui_osq = st.session_state.osq
            
    if drs_wq > 0:
        if drs_tx == "ADD TO DRS":
            new_drs_owq += drs_wq
            st.session_state.weekly_drs_w += drs_wq
            st.session_state.monthly_drs_w += drs_wq
        elif drs_tx == "REMOVE FROM DRS":
            new_drs_owq = max(0, new_drs_owq - drs_wq)
            st.session_state.owq = max(0, st.session_state.owq - drs_wq)
            st.session_state.ui_owq = st.session_state.owq
            
    # SECURITY: DRS cannot exceed total portfolio holdings
    st.session_state.drs_osq = min(new_drs_osq, st.session_state.osq)
    st.session_state.drs_owq = min(new_drs_owq, st.session_state.owq)
    
    st.session_state.ui_drs_osq = st.session_state.drs_osq
    st.session_state.ui_drs_owq = st.session_state.drs_owq
    
    st.session_state.in_drs_t_sq = 0
    st.session_state.in_drs_t_wq = 0

# --- 2. HOME SCREEN ---
if not st.session_state.launched and not st.session_state.show_leaderboard:
    # Recover UI states from shielded memory if returning from Terminal
    if "ui_osq" not in st.session_state: st.session_state.ui_osq = st.session_state.osq
    if "ui_osp" not in st.session_state: st.session_state.ui_osp = st.session_state.osp
    if "ui_owq" not in st.session_state: st.session_state.ui_owq = st.session_state.owq
    if "ui_owp" not in st.session_state: st.session_state.ui_owp = st.session_state.owp

    wen_b64 = get_b64('Screenshot_20260216_163106_Discord.jpg')
    st.markdown(f"""<div class="title-container"><img src='data:image/jpeg;base64,{wen_b64}' style='height:80px; vertical-align:middle; animation: neon-img 1.5s infinite; margin-right:10px;'><h1 class='gme-title' style='display:inline-block; vertical-align:middle;'>GME&nbsp;TERMINAL</h1><div style='display:inline-block; font-size:60px; vertical-align:middle; animation: nuclear-neon 1.5s infinite; margin-left:10px;'>🚀</div></div>""", unsafe_allow_html=True)
    
    with st.expander("⚙️ PORTFOLIO CONFIGURATION"):
        st.session_state.ape_name = st.text_input("Nickname (Optional)", value=st.session_state.ape_name)
        st.markdown("### 🏦 CURRENT HOLDINGS")
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Current Shares", min_value=0, key="ui_osq")
            st.number_input("Avg Cost ($)", format="%.3f", key="ui_osp")
        with col2:
            st.number_input("Current Warrants", min_value=0, key="ui_owq")
            st.number_input("Warrant Avg ($)", format="%.3f", key="ui_owp")
            
         # SAVE BUTTON FOR COOKIES STORAGE
        if st.button("SAVE CURRENT HOLDINGS", use_container_width=True):
            st.session_state.osq = st.session_state.ui_osq
            st.session_state.osp = st.session_state.ui_osp
            st.session_state.owq = st.session_state.ui_owq
            st.session_state.owp = st.session_state.ui_owp
            st.session_state.ape_name = st.session_state.ape_name
            
            cookies["osq"] = str(st.session_state.osq)
            cookies["osp"] = str(st.session_state.osp)
            cookies["owq"] = str(st.session_state.owq)
            cookies["owp"] = str(st.session_state.owp)
            cookies["ape_name"] = st.session_state.ape_name
            cookies.save()
            st.success("DATA SAVED TO DEVICE ! 💎🙌")

        st.markdown("---")
        st.markdown("### 🛒 NEW TRANSACTION")
        st.selectbox("TRANSACTION TYPE", ["BUY", "SELL"], key="in_tx_type")

        col3, col4 = st.columns(2)
        with col3:
            st.number_input("Shares Qty", min_value=0, key="in_t_sq")
            st.number_input("Execution Price ($)", format="%.3f", key="in_t_sp")
        with col4:
            st.number_input("Warrants Qty", min_value=0, key="in_t_wq")
            st.number_input("Execution Price W ($)", format="%.3f", key="in_t_wp")

        st.markdown("<br>", unsafe_allow_html=True)
        st.button("💾 UPDATE PORTFOLIO", use_container_width=True, on_click=update_portfolio_logic)
        # --- DRS CONFIGURATION PANEL ---
        st.markdown("<hr style='border: 1px solid #9b51e0; margin-top: 30px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #9b51e0; text-shadow: 0 0 10px #9b51e0; font-family: monospace;'>🟣 DRS REGISTRATION</h3>", unsafe_allow_html=True)
        
        # Recover UI states
        if "ui_drs_osq" not in st.session_state: st.session_state.ui_drs_osq = st.session_state.drs_osq
        if "ui_drs_owq" not in st.session_state: st.session_state.ui_drs_owq = st.session_state.drs_owq

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.number_input("Current DRS Shares", min_value=0, key="ui_drs_osq")
        with col_d2:
            st.number_input("Current DRS Warrants", min_value=0, key="ui_drs_owq")
            
        # SAVE DRS TO COOKIES
        if st.button("SAVE DRS HOLDINGS", use_container_width=True):
            st.session_state.drs_osq = min(st.session_state.ui_drs_osq, st.session_state.osq)
            st.session_state.drs_owq = min(st.session_state.ui_drs_owq, st.session_state.owq)
            
            cookies["drs_osq"] = str(st.session_state.drs_osq)
            cookies["drs_owq"] = str(st.session_state.drs_owq)
            cookies.save()
            st.success("DRS SAVED TO DEVICE ! 🟣")

        st.markdown("---")
        st.markdown("<h4 style='color: #9b51e0;'>🟣 NEW DRS TRANSFER</h4>", unsafe_allow_html=True)
        st.selectbox("TRANSFER TYPE", ["ADD TO DRS", "REMOVE FROM DRS"], key="in_drs_tx_type")

        col_d3, col_d4 = st.columns(2)
        with col_d3:
            st.number_input("Transfer Shares Qty", min_value=0, key="in_drs_t_sq")
        with col_d4:
            st.number_input("Transfer Warrants Qty", min_value=0, key="in_drs_t_wq")

        st.markdown("<br>", unsafe_allow_html=True)
        st.button("🟣 LOCK DRS SHARES", use_container_width=True, on_click=update_drs_logic)

    st.markdown("""
    <style>
    /* 1. PRIMARY BUTTON: WEN MOON */
    button[kind="primary"] {
        min-height: 145px !important;
        border: 2px solid #00FF00 !important;
        box-shadow: 0 0 15px #00FF00 !important;
        background-color: rgba(0, 255, 0, 0.05) !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
    }
    @media screen and (max-width: 600px) {
        button[kind="primary"] { margin-top: -32px !important; }
    }
    
    button[kind="primary"] p {
        color: #00FF00 !important;
        font-size: 30px !important; 
        font-weight: 900 !important;
        animation: neon-blink 0.8s infinite alternate !important;
        text-shadow: 0 0 10px #00FF00, 0 0 20px #00FF00 !important;
        white-space: pre-line !important;
        margin: 0 !important;
    }

    /* 2. YELLOW NEON FOR LEADERBOARD BUTTON */
    button[kind="secondary"] {
        border: 2px solid #FFD700 !important;
        box-shadow: 0 0 15px #FFD700 !important;
        background-color: rgba(255, 215, 0, 0.05) !important;
        min-height: 70px !important;
    }
    button[kind="secondary"] p {
        color: #FFD700 !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        animation: neon-blink-yellow 0.8s infinite alternate !important;
    }

    /* 3. PROTECT THE PORTFOLIO BUTTON */
    div[data-testid="stExpander"] button[kind="secondary"] {
        border: 1px solid rgba(250, 250, 250, 0.2) !important;
        box-shadow: none !important;
        background-color: #0e1621 !important;
        min-height: 40px !important;
    }
    div[data-testid="stExpander"] button[kind="secondary"] p {
        color: white !important;
        font-size: 16px !important;
        font-weight: normal !important;
        animation: none !important;
        text-shadow: none !important;
    }

    @keyframes neon-blink {
        0% { opacity: 1; text-shadow: 0 0 10px #00FF00, 0 0 20px #00FF00; }
        100% { opacity: 0.4; text-shadow: none; }
    }
    
    @keyframes neon-blink-yellow {
        0% { opacity: 1; text-shadow: 0 0 10px #FFD700, 0 0 20px #FFD700; }
        100% { opacity: 0.4; text-shadow: none; }
    }

    @keyframes pulse-purple {
        0% { text-shadow: 0 0 5px #9b51e0; }
        50% { text-shadow: 0 0 15px #b026ff, 0 0 25px #9b51e0; }
        100% { text-shadow: 0 0 5px #9b51e0; }
    }
    .drs-winner {
        animation: pulse-purple 1.5s infinite;
        color: #b026ff !important;
        font-weight: bold;
    }

    /* FIX FOR YOUTUBE VIDEO IN LANDSCAPE MODE */
    @media screen and (orientation: landscape) {
        iframe {
            height: 400px !important;
        }
    }

    </style>
    """, unsafe_allow_html=True)

    with st.container():
        # --- SMART LANDSCAPE FONTS ---
        st.markdown("""
        <style>
            @media screen and (orientation: landscape) {
                button[kind="primary"] p { font-size: 38px !important; line-height: 1.2 !important; }
                button[kind="secondary"] p { font-size: 28px !important; }
                h2 { font-size: 42px !important; }
                h4 { font-size: 32px !important; }
            }
        </style>
        """, unsafe_allow_html=True)

        # FUSED: No space between 🙌💎 and 🚀🌍
        if st.button("LAUNCH WEN MOON SYSTEM\n🙌💎🚀🌍!", type="primary", use_container_width=True):
            st.session_state.launched = True
            st.rerun()

        if st.button("🏆 LEADERBOARD", use_container_width=True):
            st.session_state.show_leaderboard = True
            st.rerun()

        # --- SECURE CONTAINER TO PREVENT DOM LEAK ---
        with st.container():

            st.markdown("<h4 style='text-align: right; margin-top: 10px; font-family: monospace; animation: neon-text 1.5s infinite; color: #00FF00;'>By Mr-CRUNK-13</h4>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            # --- LIVE PRICE FETCH FOR HOLDINGS ---
            try:
                l_data = yf.download(["GME", "GME-WT"], period="1d", interval="2m", prepost=True, progress=False)['Close']
                l_p_n = float(l_data['GME'].dropna().iloc[-1]) if not l_data['GME'].dropna().empty else 24.50
                l_p_w = float(l_data['GME-WT'].dropna().iloc[-1]) if not l_data['GME-WT'].dropna().empty else 4.30
            except:
                l_p_n, l_p_w = 24.50, 4.30
                
            h_osq = st.session_state.osq
            h_owq = st.session_state.owq
            h_osp = st.session_state.osp
            h_owp = st.session_state.owp
            
            l_v_s = h_osq * l_p_n
            l_v_w = h_owq * l_p_w
            l_t_v = l_v_s + l_v_w
            w_pct = (l_v_w / l_t_v * 100) if l_t_v > 0 else 0.0
            
            # --- YOUR HOLDINGS BLOCK ---
            html_holdings = f"""
            <div style="background-color: #0e1621; padding: 20px; border-radius: 10px; border: 2px solid #00FF00; box-shadow: 0 0 15px #00FF00; margin-bottom: 20px;">
            <h2 style="text-align: center; color: #00FF00; margin-top: 0; font-family: monospace; animation: neon-blink 1.5s infinite alternate; text-shadow: 0 0 10px #00FF00;">💎🙌 YOUR HOLDINGS</h2>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px; margin-top: 20px;">
            <div style="background-color: #0f172a; padding: 20px; border-radius: 8px; border: 2px solid #00FF00; box-shadow: 0 0 15px #00FF00; flex: 1; min-width: 140px; text-align: center; display: flex; flex-direction: column; justify-content: center;">
            <p style="color: #00FF00; font-size: 18px; font-weight: bold; margin: 0 0 5px 0;">GME SHARES</p>
            <div style="width: 100%; word-break: break-all;">
            <span style="color: #00FF00; font-weight: bold; font-size: clamp(30px, 8vw, 55px); line-height: 1.1;">{h_osq:,}</span>
            </div>
            <p style="color: #00FF00; font-size: 16px; margin: 5px 0 0 0;">Avg Cost: ${h_osp:,.2f}</p>
            </div>
            <div style="background-color: #0f172a; padding: 20px; border-radius: 8px; border: 2px solid #006400; box-shadow: 0 0 15px #006400; flex: 1; min-width: 140px; text-align: center; display: flex; flex-direction: column; justify-content: center;">
            <p style="color: #006400; font-size: 18px; font-weight: bold; margin: 0 0 5px 0;">WARRANTS</p>
            <div style="width: 100%; word-break: break-all;">
            <span style="color: #006400; font-weight: bold; font-size: clamp(30px, 8vw, 55px); line-height: 1.1;">{h_owq:,}</span>
            </div>
            <p style="color: #006400; font-size: 16px; margin: 5px 0 0 0;">Avg Cost: ${h_owp:,.3f}</p>
            </div>
            </div>
            <div style="margin-top: 25px;">
            <p style="color: #006400; font-size: 16px; font-weight: bold; text-align: center; margin: 0 0 5px 0;">WARRANTS: {w_pct:.1f}% OF LIVE VALUE</p>
            <div style="width: 100%; background-color: #050505; border-radius: 10px; height: 12px; border: 1px solid #00FF00; box-shadow: 0 0 10px #00FF00; overflow: hidden;">
            <div style="width: {w_pct}%; background-color: #006400; height: 100%; box-shadow: 0 0 10px #006400;"></div>
            </div>
            </div>
            </div>
            """
            st.markdown(html_holdings, unsafe_allow_html=True)
           
            # --- YOUR PERSONAL PURCHASES BLOCK ---
            import plotly.graph_objects as go
            p_w_s = st.session_state.get('weekly_s', 0)
            p_m_s = st.session_state.get('monthly_s', 0)
            p_w_w = st.session_state.get('weekly_w', 0)
            p_m_w = st.session_state.get('monthly_w', 0)

            html_personal = f"""
            <div style="background-color: #0e1621; padding: 20px; border-radius: 10px; border: 2px solid #00FF00; box-shadow: 0 0 15px #00FF00; margin-bottom: 0px;">
            <h4 style="color: #00FF00; margin-top: 0; font-size: 24px; font-weight: bold; text-align:center;">🔥 YOUR RECENT PURCHASES</h4>
            <div style="display: flex; justify-content: space-around; margin-top: 15px; flex-wrap: wrap; gap: 15px;">
            <div style="background-color: #0f172a; padding: 15px; border-radius: 8px; border: 2px solid #00FF00; box-shadow: 0 0 15px #00FF00; flex: 1; min-width: 120px; text-align: center;">
            <p style="color: #00FF00; font-size: 18px; margin: 0 0 10px 0; font-weight: bold;">WEEKLY</p>
            <p style="margin: 5px 0; font-size: 16px; color: white;">Shares: <strong>+{p_w_s:,}</strong></p>
            <p style="margin: 5px 0; font-size: 16px; color: white;">Warrants: <strong>+{p_w_w:,}</strong></p>
            </div>
            <div style="background-color: #0f172a; padding: 15px; border-radius: 8px; border: 2px solid #006400; box-shadow: 0 0 15px #006400; flex: 1; min-width: 120px; text-align: center;">
            <p style="color: #006400; font-size: 18px; margin: 0 0 10px 0; font-weight: bold;">MONTHLY</p>
            <p style="margin: 5px 0; font-size: 16px; color: white;">Shares: <strong>+{p_m_s:,}</strong></p>
            <p style="margin: 5px 0; font-size: 16px; color: white;">Warrants: <strong>+{p_m_w:,}</strong></p>
            </div>
            </div>
            </div>
            """
            st.markdown(html_personal, unsafe_allow_html=True)

            fig_pers = go.Figure()
            fig_pers.add_trace(go.Bar(name='Shares', x=['WEEKLY', 'MONTHLY'], y=[p_w_s, p_m_s], marker_color='#00FF00'))
            fig_pers.add_trace(go.Bar(name='Warrants', x=['WEEKLY', 'MONTHLY'], y=[p_w_w, p_m_w], marker_color='#006400'))
            fig_pers.update_layout(barmode='group', template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', title={'text': "YOUR BUYING POWER", 'x': 0.5, 'y': 0.92, 'font': {'color': '#00FF00', 'family': 'monospace'}}, margin=dict(l=20, r=20, t=40, b=20), height=350)

            # --- DIGITAL LOCK TO FIX DOM LEAK ---
            st.plotly_chart(fig_pers, use_container_width=True, key="home_pers_chart_safe")
            # -------------------------------------

        # --- PHASE 2: DRS VAULT DISPLAY ---
        st.markdown(f"""
        <div style="border: 2px solid #9b51e0; box-shadow: 0 0 15px #9b51e0; border-radius: 15px; padding: 20px; background-color: rgba(155, 81, 224, 0.05); margin-bottom: 20px;">
            <h2 style="text-align: center; color: #9b51e0; text-shadow: 0 0 10px #9b51e0; font-family: monospace; margin-top: 0;">🟣 YOUR DRS VAULT</h2>
            <div style="display: flex; justify-content: space-around; text-align: center;">
                <div style="flex: 1; min-width: 120px;">
                    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 5px;">
                        <span style="display:inline-block; width:16px; height:16px; background-color:#9b51e0; border-radius:3px; margin-right:8px;"></span>
                        <span style="color: white; font-weight: bold; font-size: 14px;">SECURED SHARES</span>
                    </div>
                    <p style="color: #9b51e0; font-family: monospace; margin: 0; text-shadow: 0 0 10px rgba(155, 81, 224, 0.5); font-size: 32px; font-weight: bold;">{st.session_state.drs_osq:,}</p>
                </div>
                <div style="flex: 1; min-width: 120px;">
                    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 5px;">
                        <span style="display:inline-block; width:16px; height:16px; background-color:#b026ff; border-radius:3px; margin-right:8px;"></span>
                        <span style="color: white; font-weight: bold; font-size: 14px;">SECURED WARRANTS</span>
                    </div>
                    <p style="color: #b026ff; font-family: monospace; margin: 0; text-shadow: 0 0 10px rgba(176, 38, 255, 0.5); font-size: 32px; font-weight: bold;">{st.session_state.drs_owq:,}</p>
                </div>
            </div>
            <p style="color: #b026ff; font-style: italic; font-size: 0.8em; text-align: center; margin-bottom: 0;">
                "Everything else is just IOUs... These are YOURS." 🟣
            </p>
        </div>
        """, unsafe_allow_html=True)

        # --- DRS PROGRESS BARS (SHARES & WARRANTS) ---
        drs_percent = (st.session_state.drs_osq / st.session_state.osq * 100) if st.session_state.osq > 0 else 0
        drs_w_percent = (st.session_state.drs_owq / st.session_state.owq * 100) if st.session_state.owq > 0 else 0
        st.markdown(f"""
        <div style="width: 100%; background-color: #050505; border-radius: 10px; height: 12px; border: 1px solid #9b51e0; box-shadow: 0 0 10px #9b51e0; overflow: hidden; margin-bottom: 5px;">
        <div style="width: {drs_percent}%; background-color: #9b51e0; height: 100%; box-shadow: 0 0 10px #9b51e0;"></div>
        </div>
        <p style="color: #9b51e0; font-size: 0.7em; text-align: right; font-weight: bold; margin: 0 0 10px 0;">{drs_percent:.1f}% OF SHARES LOCKED</p>
        <div style="width: 100%; background-color: #050505; border-radius: 10px; height: 12px; border: 1px solid #b026ff; box-shadow: 0 0 10px #b026ff; overflow: hidden; margin-bottom: 5px;">
        <div style="width: {drs_w_percent}%; background-color: #b026ff; height: 100%; box-shadow: 0 0 10px #b026ff;"></div>
        </div>
        <p style="color: #b026ff; font-size: 0.7em; text-align: right; font-weight: bold; margin: 0;">{drs_w_percent:.1f}% OF WARRANTS LOCKED</p>
        """, unsafe_allow_html=True)
        
        # --- PERSONAL DRS WEEKLY/MONTHLY VISUALS ---
        p_d_w_s = st.session_state.get('weekly_drs_s', 0)
        p_d_m_s = st.session_state.get('monthly_drs_s', 0)
        p_d_w_w = st.session_state.get('weekly_drs_w', 0)
        p_d_m_w = st.session_state.get('monthly_drs_w', 0)

        st.markdown(f"""
        <div style="background-color: rgba(155, 81, 224, 0.05); padding: 20px; border-radius: 10px; border: 2px solid #9b51e0; box-shadow: 0 0 15px #9b51e0; margin-top: 0px;">
        <h3 style="color: #9b51e0; text-align: center; font-family: monospace; text-shadow: 0 0 5px #9b51e0;">🟣 RECENT SECURED DRS</h3>
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px;">
        <div style="background-color: #0e1621; padding: 15px; border-radius: 8px; border: 2px solid #9b51e0; box-shadow: 0 0 15px #9b51e0; flex: 1; min-width: 120px; text-align: center;">
        <p style="color: #9b51e0; font-weight: bold; margin: 0 0 10px 0;">WEEKLY</p>
        <p style="color: white; margin: 0;">Shares: <strong style="color: #9b51e0;">+{p_d_w_s:,}</strong></p>
        <p style="color: white; margin: 0;">Warrants: <strong style="color: #b026ff;">+{p_d_w_w:,}</strong></p>
        </div>
        <div style="background-color: #0e1621; padding: 15px; border-radius: 8px; border: 2px solid #b026ff; box-shadow: 0 0 15px #b026ff; flex: 1; min-width: 120px; text-align: center;">
        <p style="color: #b026ff; font-weight: bold; margin: 0 0 10px 0;">MONTHLY</p>
        <p style="color: white; margin: 0;">Shares: <strong style="color: #9b51e0;">+{p_d_m_s:,}</strong></p>
        <p style="color: white; margin: 0;">Warrants: <strong style="color: #b026ff;">+{p_d_m_w:,}</strong></p>
        </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        fig_drs_p = go.Figure()
        fig_drs_p.add_trace(go.Bar(name='Shares', x=['WEEKLY', 'MONTHLY'], y=[p_d_w_s, p_d_m_s], marker_color='#9b51e0'))
        fig_drs_p.add_trace(go.Bar(name='Warrants', x=['WEEKLY', 'MONTHLY'], y=[p_d_w_w, p_d_m_w], marker_color='#b026ff'))
        fig_drs_p.update_layout(barmode='group', template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=40, b=20), height=300, legend=dict(y=1.09))
        st.plotly_chart(fig_drs_p, use_container_width=True)

# --- 2.5 LEADERBOARD SCREEN ---
elif st.session_state.get('show_leaderboard', False):
    wen_b64 = get_b64('Screenshot_20260216_163106_Discord.jpg')
    st.markdown(f"<div style='text-align:center;'><h1 style='font-size:40px; color:#00FF00; animation:neon-text 1.5s infinite;'>🏆 LEADERBOARD <img src='data:image/jpeg;base64,{wen_b64}' style='height:50px; vertical-align:middle; animation:neon-img 1.5s infinite;'></h1></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    @keyframes neon-drs { 0% { box-shadow: inset 0 0 5px #a200ff; border-top: 1px solid #a200ff; border-bottom: 1px solid #a200ff; } 50% { box-shadow: inset 0 0 20px #a200ff; border-top: 1px solid #d080ff; border-bottom: 1px solid #d080ff; } 100% { box-shadow: inset 0 0 5px #a200ff; border-top: 1px solid #a200ff; border-bottom: 1px solid #a200ff; } }
    @keyframes neon-gold { 0% { box-shadow: inset 0 0 5px #FFD700; border-top: 1px solid #FFD700; border-bottom: 1px solid #FFD700; } 50% { box-shadow: inset 0 0 20px #FFD700; border-top: 1px solid #FFF8DC; border-bottom: 1px solid #FFF8DC; } 100% { box-shadow: inset 0 0 5px #FFD700; border-top: 1px solid #FFD700; border-bottom: 1px solid #FFD700; } }
    @keyframes neon-silver { 0% { box-shadow: inset 0 0 5px #C0C0C0; border-top: 1px solid #C0C0C0; border-bottom: 1px solid #C0C0C0; } 50% { box-shadow: inset 0 0 20px #C0C0C0; border-top: 1px solid #FFFFFF; border-bottom: 1px solid #FFFFFF; } 100% { box-shadow: inset 0 0 5px #C0C0C0; border-top: 1px solid #C0C0C0; border-bottom: 1px solid #C0C0C0; } }
    @keyframes neon-bronze { 0% { box-shadow: inset 0 0 5px #CD7F32; border-top: 1px solid #CD7F32; border-bottom: 1px solid #CD7F32; } 50% { box-shadow: inset 0 0 20px #CD7F32; border-top: 1px solid #FFA07A; border-bottom: 1px solid #FFA07A; } 100% { box-shadow: inset 0 0 5px #CD7F32; border-top: 1px solid #CD7F32; border-bottom: 1px solid #CD7F32; } }

    @keyframes pulse-purple { 0% { text-shadow: 0 0 5px #9b51e0; } 50% { text-shadow: 0 0 15px #b026ff, 0 0 25px #9b51e0; } 100% { text-shadow: 0 0 5px #9b51e0; } }
    @keyframes pulse-gold-text { 0% { text-shadow: 0 0 5px #FFD700; } 50% { text-shadow: 0 0 15px #FFF8DC, 0 0 25px #FFD700; } 100% { text-shadow: 0 0 5px #FFD700; } }
    @keyframes pulse-silver-text { 0% { text-shadow: 0 0 5px #C0C0C0; } 50% { text-shadow: 0 0 15px #FFFFFF, 0 0 25px #C0C0C0; } 100% { text-shadow: 0 0 5px #C0C0C0; } }
    @keyframes pulse-bronze-text { 0% { text-shadow: 0 0 5px #CD7F32; } 50% { text-shadow: 0 0 15px #FFA07A, 0 0 25px #CD7F32; } 100% { text-shadow: 0 0 5px #CD7F32; } }

    .pulse-drs td { animation: neon-drs 2s infinite; }
    .pulse-gold td { animation: neon-gold 2s infinite; }
    .pulse-silver td { animation: neon-silver 2s infinite; }
    .pulse-bronze td { animation: neon-bronze 2s infinite; }

    .text-drs { animation: pulse-purple 1.5s infinite; color: #b026ff !important; font-weight: bold; }
    .text-gold { animation: pulse-gold-text 1.5s infinite; color: #FFD700 !important; font-weight: bold; }
    .text-silver { animation: pulse-silver-text 1.5s infinite; color: #C0C0C0 !important; font-weight: bold; }
    .text-bronze { animation: pulse-bronze-text 1.5s infinite; color: #CD7F32 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
    
    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
    with col_b2:
        if st.button("⬅️ BACK TO HOME", use_container_width=True): 
            st.session_state.show_leaderboard = False
            st.rerun()
            
    # --- 6-TAB LEADERBOARD WITH TROPHY COLUMN ---
    lb_tabs = st.tabs(["🌍 GENERAL", "📅 MONTHLY", "📆 WEEKLY", "🟣 DRS TOTAL", "🗓️ DRS MONTHLY", "⏳ DRS WEEKLY"])
    
    try:
        data = yf.download(["GME", "GME-WT"], period="1d", interval="2m", prepost=True, progress=False)['Close']
        live_p_n = float(data['GME'].dropna().iloc[-1]) if not data['GME'].dropna().empty else 24.50
        live_p_w = float(data['GME-WT'].dropna().iloc[-1]) if not data['GME-WT'].dropna().empty else 4.30
    except:
        live_p_n, live_p_w = 24.50, 4.30

    drs_tv = (st.session_state.drs_osq * live_p_n) + (st.session_state.drs_owq * live_p_w)
    drs_m_v = (st.session_state.get('monthly_drs_s', 0) * live_p_n) + (st.session_state.get('monthly_drs_w', 0) * live_p_w)
    drs_w_v = (st.session_state.get('weekly_drs_s', 0) * live_p_n) + (st.session_state.get('weekly_drs_w', 0) * live_p_w)

    real_db = [{
        "name": st.session_state.get("ape_name", "Anonymous"),
        "tv": (st.session_state.osq * live_p_n) + (st.session_state.owq * live_p_w),
        "sq": st.session_state.osq, "wq": st.session_state.owq,
        "drs_tv": drs_tv, "drs_mv": drs_m_v, "drs_wv": drs_w_v,
        "drs_sq": st.session_state.drs_osq, "drs_wq": st.session_state.drs_owq,
        "drs_w_s": st.session_state.get('weekly_drs_s', 0),
        "drs_m_s": st.session_state.get('monthly_drs_s', 0),
        "drs_w_w": st.session_state.get('weekly_drs_w', 0),
        "drs_m_w": st.session_state.get('monthly_drs_w', 0)
    }]

    for idx, t in enumerate(lb_tabs):
        with t:
            if idx >= 3:
                sort_key = "drs_tv" if idx == 3 else "drs_mv" if idx == 4 else "drs_wv"
                title = "DRS TOTAL" if idx == 3 else "DRS MONTHLY" if idx == 4 else "DRS WEEKLY"
                
                q_s_key = "drs_sq" if idx == 3 else "drs_m_s" if idx == 4 else "drs_w_s"
                q_w_key = "drs_wq" if idx == 3 else "drs_m_w" if idx == 4 else "drs_w_w"
                
                html = f"<div class='table-wrapper' style='border: 2px solid #9b51e0; box-shadow: 0 0 15px #9b51e0;'><table class='ldb-t' style='border: none;'><tr><th style='color:#9b51e0;'>RANK</th><th style='color:#9b51e0;'>APE</th><th style='color:#9b51e0;'>{title} VALUE</th><th style='color:#9b51e0;'>LOCKED S.</th><th style='color:#9b51e0;'>LOCKED W.</th><th style='color:#9b51e0;'>TROPHIES</th></tr>"
                sorted_db = sorted(real_db, key=lambda x: x.get(sort_key, 0), reverse=True)
                for i, r in enumerate(sorted_db):
                    rank_str = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else str(i+1)
                    user_trophies = "🟣" if r.get('drs_tv', 0) > 0 else ""
                    
                    neon_class = ""
                    text_class = ""
                    if i <= 2 and r.get(sort_key, 0) > 0:
                        neon_class = "pulse-drs"
                        text_class = "class='text-drs'"
                        
                    html += f"<tr class='{neon_class}'><td>{rank_str}</td><td><span {text_class}>{r['name']}</span></td><td style='color:#9b51e0;'>${r.get(sort_key, 0):,.2f}</td><td>{r.get(q_s_key, 0):,}</td><td>{r.get(q_w_key, 0):,}</td><td style='font-size:20px;'>{user_trophies}</td></tr>"
                st.markdown(html + "</table></div>", unsafe_allow_html=True)
            else: 
                html = "<div class='table-wrapper'><table class='ldb-t'><tr><th>RANK</th><th>APE</th><th>TOTAL VALUE</th><th>SHARES</th><th>WARRANTS</th><th>TROPHIES</th></tr>"
                sorted_db = sorted(real_db, key=lambda x: x.get("tv", 0), reverse=True)
                for i, r in enumerate(sorted_db):
                    rank_str = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else str(i+1)
                    user_trophies = "🟣" if r.get('drs_tv', 0) > 0 else ""
                    
                    neon_class = ""
                    text_class = ""
                    if i == 0:
                        neon_class = "pulse-gold"
                        text_class = "class='text-gold'"
                    elif i == 1:
                        neon_class = "pulse-silver"
                        text_class = "class='text-silver'"
                    elif i == 2:
                        neon_class = "pulse-bronze"
                        text_class = "class='text-bronze'"
                        
                    html += f"<tr class='{neon_class}'><td>{rank_str}</td><td><span {text_class}>{r['name']}</span></td><td style='color:#00FF00;'>${r.get('tv', 0):,.2f}</td><td>{r.get('sq', 0):,}</td><td>{r.get('wq', 0):,}</td><td style='font-size:20px;'>{user_trophies}</td></tr>"
                st.markdown(html + "</table></div>", unsafe_allow_html=True)

# --- 3. TERMINAL & LIVE ENGINE ---
else:
    if "sys_load" not in st.session_state:
        st.session_state.sys_load = True
        
        wen_b64 = get_b64('Screenshot_20260216_163106_Discord.jpg')
        
        loader_html = f"""
        <style>
            @keyframes fadeLoader {{ 80% {{opacity: 1;}} 100% {{opacity: 0; visibility: hidden; pointer-events: none;}} }} 
            @keyframes nuclear-neon-giant {{ 0%, 100% {{ filter: drop-shadow(0 0 10px #00FF00); transform: translateY(0px) scale(1); }} 50% {{ filter: drop-shadow(0 0 60px #00FF00); transform: translateY(-20px) scale(1.05); }} }}
            @keyframes blnk-neon {{ 0%, 100% {{ opacity: 1; text-shadow: 0 0 20px #00FF00, 0 0 40px #00FF00; }} 50% {{ opacity: 0.2; text-shadow: none; }} }}
            .t-load {{ position: fixed; top:0; left:0; width: 100vw; height: 100vh; background: #050505; z-index: 999999; display: flex; flex-direction: column; justify-content: center; align-items: center; animation: fadeLoader 3.0s forwards; }}
        </style>
        <div class='t-load'>
            <div style='display: flex; justify-content: center; align-items: center; gap: 30px; margin-bottom: 40px; animation: nuclear-neon-giant 1.5s infinite;'>
                <img src='data:image/jpeg;base64,{wen_b64}' style='height: 180px; border-radius: 20px;'>
                <div style='font-size: 180px;'>🚀</div>
            </div>
            <h1 style='color:#00FF00; font-family:monospace; font-size: 35px; animation: blnk-neon 1s infinite; text-align:center; padding: 0 20px;'>INITIALIZING WEN MOON SYSTEM...</h1>
        </div>
        """
        st.markdown(loader_html, unsafe_allow_html=True)
        
    # 👻 SUPREME CSS CAMOUFLAGE
    st.markdown("""
    <style>
        div[data-testid='stExpander'] { display: none !important; }
        button[kind="primary"], button[kind="secondary"] { display: none !important; }
        div[data-testid="stTabs"] ~ div { display: none !important; }       
    </style>
    """, unsafe_allow_html=True)

    @st.cache_data(ttl=15)
    def fetch_terminal_data():

        try:
            ts = ["GME", "GME-WT"]
            data = yf.download(ts, period="1d", interval="2m", prepost=True, progress=False)['Close']
            p_n = float(data['GME'].dropna().iloc[-1]) if not data['GME'].dropna().empty else 24.50
            p_w = float(data['GME-WT'].dropna().iloc[-1]) if not data['GME-WT'].dropna().empty else 4.30
            
            t_n, t_w = yf.Ticker("GME"), yf.Ticker("GME-WT")
            prev_n = float(t_n.fast_info.get('previousClose', p_n))
            prev_w = float(t_w.fast_info.get('previousClose', p_w))
            
            vol_n = int(t_n.fast_info.get('lastVolume', 0))
            vol_w = int(t_w.fast_info.get('lastVolume', 0))
            
            return p_n, p_w, prev_n, prev_w, vol_n, vol_w, data['GME'], data['GME-WT']
        except: return 24.50, 4.30, 24.0, 4.0, 0, 0, pd.Series(), pd.Series()

    @st.cache_data(ttl=300)
    def fetch_advanced_pro_data():
        gme, wt = yf.Ticker("GME"), yf.Ticker("GME-WT")
        try: info_dict = dict(gme.info)
        except: info_dict = {}
        try: wt_info_dict = dict(wt.fast_info) if hasattr(wt, 'fast_info') else dict(wt.info)
        except: wt_info_dict = {}
        try: news_data = gme.news[:5] if gme.news else []
        except: news_data = []
        return info_dict, wt_info_dict, news_data

    @st.cache_data(ttl=300)
    def fetch_financials_and_options():
        tk = yf.Ticker("GME")
        def safe_get(attr, default):
            try: 
                res = getattr(tk, attr)
                return res if res is not None else default
            except: return default
        
        opts = safe_get('options', ())
        fin = safe_get('financials', pd.DataFrame())
        bs = safe_get('balance_sheet', pd.DataFrame())
        cf = safe_get('cashflow', pd.DataFrame())
        ins = safe_get('insider_transactions', pd.DataFrame())
        earn_dates = safe_get('earnings_dates', pd.DataFrame())
        return opts, fin, bs, cf, ins, earn_dates

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14, tab15, tab16, tab17, tab18 = st.tabs([
        "📊 GME", "📈 WARRANT", "💎 PORTFOLIO", "📋 DATA", "🌘 WEN MOON", "🗃️ WM DATA", "🏆 LEADERBOARD", "📊 WM SUMMARY", 
        "🧬 GME PRO", "⛓️ OPTIONS CHAIN", "🏦 FINANCIALS", "🕵️ INSIDERS", "📈 PRO CHARTS", "🌐 WEB PORTALS", "🐦 𝕏",
        "📺 GME YouTube", "💎🙌13 Music", "💎🙌 By Mr-CRUNK-13"
    ])

    with tab1: ph1 = st.empty()
    with tab2: ph2 = st.empty()
    with tab3: ph3 = st.empty()
    with tab4: ph4 = st.empty()
    with tab5: ph5 = st.empty()
    with tab6: ph6 = st.empty()
    with tab7: ph7 = st.empty()
    with tab8: ph8 = st.empty()
    with tab9: ph9 = st.empty()
    with tab10: ph10 = st.empty()
    with tab11: ph11 = st.empty()
    with tab12: ph12 = st.empty()

    # --- TAB 13 : PRO CHARTS (Static) ---
    with tab13:
        st.markdown("<h2 style='text-align:center; color:#00FF00; font-family:monospace;'>📈 ADVANCED CHARTS TERMINAL</h2>", unsafe_allow_html=True)
        t_chart1, t_chart2 = st.tabs(["🇺🇸 GME (TradingView Pro)", "📜 GME-WT (TradingView Pro)"])
        
        def tv_widget(symbol, cid):
            return f"""
            <style>
                @media screen and (orientation: landscape) {{
                    #{cid}_box {{ height: 400px !important; }}
                }}
            </style>
            <div id="{cid}_box" class="tradingview-widget-container" style="height: 700px; width: 100%;">
              <div id="{cid}" style="height: 100%; width: 100%;"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
              <script type="text/javascript">
              new TradingView.widget({{
                "autosize": true, "symbol": "{symbol}", "interval": "D", "timezone": "Etc/UTC",
                "theme": "dark", "style": "1", "locale": "en", "enable_publishing": false,
                "backgroundColor": "#050505", "gridColor": "#1f2937", "hide_top_toolbar": false,
                "hide_legend": false, "save_image": false, "container_id": "{cid}",
                "toolbar_bg": "#0f172a"
              }});
              </script>
            </div>"""
            
        with t_chart1: components.html(tv_widget("NYSE:GME", "tv_gme"), height=720)
        with t_chart2: components.html(tv_widget("NYSE:GME/W", "tv_gmewt"), height=720)

    # --- TAB 14 : WEB PORTALS (Static) ---
    with tab14:
        st.markdown("<h2 style='text-align:center; color:#00FF00; font-family:monospace;'>🌐 INVESTOR PORTALS</h2>", unsafe_allow_html=True)
        w_t1, w_t2, w_t3, w_t4, w_t5, w_t6, w_t7, w_t8 = st.tabs(["👔 Investors", "📊 ChartEx", "🎀 RedStriped", "🐋 Whales", "🦍 Reddit", "🐳 WhaleWisdom", "📈 TradingView", "📰 Yahoo"])
        
        def portal_btn(title, desc, url):
            return f"<div style='text-align:center; padding:20px; background:#0f172a; border:2px solid #00FF00; box-shadow: 0 0 15px #00FF00; border-radius:10px;'><h3 style='color:white; margin: 0 0 10px 0;'>{title}</h3><p style='color:#ccc; font-size:18px; margin-bottom: 20px;'>{desc}</p><a href='{url}' target='_blank' style='display:inline-block; padding:15px 30px; background:#00FF00; color:black; font-weight:bold; text-decoration:none; border-radius:5px; font-size:20px; border:2px solid #00FF00; box-shadow: 0 0 15px #00FF00;'>OPEN SECURE LINK</a></div>"
            
        with w_t1: st.markdown(portal_btn("GAMESTOP INVESTORS", "Official corporate and SEC filings.", "https://investor.gamestop.com/"), unsafe_allow_html=True)
        with w_t2: st.markdown(portal_btn("CHARTEXCHANGE", "Live Borrow Fee and Dark Pool data.", "https://chartexchange.com/symbol/nyse-gme/borrow-fee/"), unsafe_allow_html=True)
        with w_t3: st.markdown(portal_btn("RED STRIPED TIE", "Direct access to community data.", "https://redstripedtie.com/_/GME?view=largest_trades"), unsafe_allow_html=True)
        with w_t4: st.markdown(portal_btn("UNUSUAL WHALES", "Track options market activity.", "https://unusualwhales.com/stock/GME"), unsafe_allow_html=True)
        with w_t5: st.markdown(portal_btn("r/SUPERSTONK", "The heart of the GME community.", "https://www.reddit.com/r/Superstonk/"), unsafe_allow_html=True)
        with w_t6: st.markdown(portal_btn("WHALEWISDOM (WARRANTS)", "Track institutional holders of GME Warrants.", "https://whalewisdom.com/stock/gmews"), unsafe_allow_html=True)
        with w_t7: st.markdown(portal_btn("TRADINGVIEW", "Advanced technical analysis platform.", "https://www.tradingview.com/symbols/NYSE-GME/"), unsafe_allow_html=True)
        with w_t8: st.markdown(portal_btn("YAHOO FINANCE", "Comprehensive financial overview.", "https://finance.yahoo.com/quote/GME/"), unsafe_allow_html=True)

    # --- TAB 15 : 🐦 𝕏 (Twitter X - Static) ---
    with tab15:
        st.markdown("<h2 style='text-align:center; color:#00FF00; font-family:monospace;'>🐦 𝕏 </h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#ccc; font-size:16px;'>Select a profile below to open their live feed securely.</p>", unsafe_allow_html=True)
        
        def x_btn(handle, name, icon):
            return f"<div style='text-align:center; padding:30px; background:#0f172a; border:2px solid #1DA1F2; box-shadow: 0 0 15px #1DA1F2; border-radius:10px; margin-bottom:15px;'><h3 style='color:white; margin-top:0;'>{icon} {name}</h3><a href='https://twitter.com/{handle}' target='_blank' style='display:inline-block; padding:15px 30px; background:#1DA1F2; color:white; font-weight:bold; text-decoration:none; border-radius:5px; font-size:20px; border:2px solid #1DA1F2; box-shadow: 0 0 15px #1DA1F2;'>OPEN @{handle} ON 𝕏</a></div>"
            
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(x_btn("ryancohen", "Ryan Cohen", "👑"), unsafe_allow_html=True)
            st.markdown(x_btn("michaeljburry", "Michael Burry", "📉"), unsafe_allow_html=True)
            st.markdown(x_btn("buckthebunny", "Buck", "🐰"), unsafe_allow_html=True)
        with c2:
            st.markdown(x_btn("TheRoaringKitty", "Roaring Kitty", "🐱"), unsafe_allow_html=True)
            st.markdown(x_btn("GameStop", "GameStop", "🎮"), unsafe_allow_html=True)
            st.markdown(x_btn("PowerPacks", "PowerPacks", "🃏"), unsafe_allow_html=True)
            
    # --- TAB 16 : 📺 GME YouTube ---
    with tab16:
        st.markdown("<h2 style='text-align:center; color:#FF0000; font-family:monospace; animation: neon-flash-red 1.5s infinite;'>📺 GME YOUTUBE HUB</h2>", unsafe_allow_html=True)

        st.markdown("""
        <style>
            .neon-video {
                border: 2px solid #FF0000 !important;
                box-shadow: 0 0 15px #FF0000 !important;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            @media screen and (orientation: landscape) {
                .neon-video { height: 400px !important; }
            }
        </style>
        <iframe class="neon-video" width="100%" height="220" src="https://www.youtube.com/embed/021_zhXd8T0" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
        """, unsafe_allow_html=True)

        st.markdown("""<div style='display:flex; justify-content:center; margin-bottom:20px;'><div style='background:#0f172a; padding:15px; border-radius:10px; border:2px solid #FF0000; width:100%; max-width:300px; text-align:center; box-shadow: 0 0 15px #FF0000;'><h4 style='color:#FF0000; margin-top:0;'>🎬 ROARING KITTY - GME MIX</h4><div style='display:flex; gap:10px; justify-content:center; margin-top:15px;'><a href='https://youtube.com/playlist?list=PL8E5BqjEa7V0KYhYAq18oYJ6GVMTFKZyR' target='_blank' style='flex:1; padding:10px; background:rgba(255,0,0,0.1); border:2px solid #FF0000; color:#FF0000; text-decoration:none; font-weight:bold; border-radius:5px; box-shadow: 0 0 15px #FF0000;'>🔴 YT VIDEO</a><a href='https://music.youtube.com/playlist?list=PL8E5BqjEa7V0KYhYAq18oYJ6GVMTFKZyR' target='_blank' style='flex:1; padding:10px; background:rgba(176,38,255,0.1); border:2px solid #b026ff; color:#b026ff; text-decoration:none; font-weight:bold; border-radius:5px; box-shadow: 0 0 15px #b026ff;'>🎵 YT MUSIC</a></div></div></div>""", unsafe_allow_html=True)

        def yt_btn(url, name, icon):
            return f"<div style='text-align:center; padding:30px; background:#0f172a; border:2px solid #FF0000; border-radius:10px; margin-bottom:15px; box-shadow: 0 0 15px #FF0000;'><h3 style='color:white; margin-top:0;'>{icon} {name}</h3><a href='{url}' target='_blank' style='display:inline-block; padding:15px 30px; background:#FF0000; color:white; font-weight:bold; text-decoration:none; border-radius:5px; font-size:20px; border:2px solid #FF0000; box-shadow: 0 0 15px #FF0000;'>OPEN ON YOUTUBE</a></div>"

        c16_1, c16_2 = st.columns(2)
        with c16_1:
            st.markdown(yt_btn("https://youtube.com/@roaringkitty", "Roaring Kitty", "🐱"), unsafe_allow_html=True)
        with c16_2:
            st.markdown(yt_btn("https://youtube.com/@gamestop", "GameStop", "🎮"), unsafe_allow_html=True)

    # --- TAB 17 : 💎🙌13 Music ---
    with tab17:
        st.markdown("<style>@keyframes pulse-purple { 0% { text-shadow: 0 0 5px #9b51e0; } 50% { text-shadow: 0 0 15px #b026ff, 0 0 25px #9b51e0; } 100% { text-shadow: 0 0 5px #9b51e0; } }</style>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#b026ff; font-family:monospace; animation: pulse-purple 1.5s infinite;'>🎧 PLAYLISTS 💿</h2>", unsafe_allow_html=True)
        
        playlists = [
            "PL8E5BqjEa7V15KI2Rwf1tRYSd9OzfMktN", "PL8E5BqjEa7V0b-FzghpQ3XdTraUm2tgH4",
            "PL8E5BqjEa7V3xeM98N-Fngd98SK9dz7Kn", "PL8E5BqjEa7V0WnBKEsfI6ieNCqHuOKUyU", "PL8E5BqjEa7V2e19qtG5ukR1vFSYw70ZNi",
            "PL8E5BqjEa7V1IoqgJEqDQorqhKIWPFuBo", "PL8E5BqjEa7V3q0PujDYVypa8k41jmXeG9", "PL8E5BqjEa7V28qu0RKmspB2J0Ka8TOb7y",
            "PL8E5BqjEa7V0M9Luk85joC6Kk79f5IIZE", "PL8E5BqjEa7V0GKewD_-KB0jgycH3NI48N", "PL8E5BqjEa7V1dPXgZvGsOvKA4pTEBuT1M",
            "PL8E5BqjEa7V1AkYN8_JTTupk4AaFVxwNc", "PL8E5BqjEa7V0KYhYAq18oYJ6GVMTFKZyR"
        ]

        playlist_titles = [
    "💎🙌13 - WEN MOON $GME! 🚀",
    "💎🙌13 - WEN MOASS $GME! 🚀",
    "💎🙌13-2026",
    "💎🙌13 - Best of Afro House / Lounge / Deep House / Electro",
    "💎🙌13 - Rap US - Old School",
    "💎🙌13 - Disco / Funk - Old School",
    "💎🙌13 - Top Electro / House - LET THEM SHORT !",
    "💎🙌13 - DJ MAZE",
    "💎🙌13 - Top Afro House / Lounge",
    "💎🙌13 - Electro / House",
    "💎🙌13 - French Music",
    "💎🙌13 - French Rap - Old School",
    "💎🙌13 - GME - 🚀"
]

        grid_html = "<div style='display:flex; flex-wrap:wrap; gap:15px; justify-content:center; margin-bottom:20px;'>"
        for i, pid in enumerate(playlists):
            grid_html += f"<div style='background:#0f172a; padding:15px; border-radius:10px; border:2px solid #b026ff; box-shadow: 0 0 15px #b026ff; width:100%; max-width:300px; text-align:center;'><h4 style='color:#b026ff; margin-top:0;'>MIX VOL. {i+1}<br><span style='color:#FFFFFF; font-size:15px; font-weight:normal;'>{playlist_titles[i]}</span></h4><div style='display:flex; gap:10px; justify-content:center; margin-top:15px;'><a href='https://youtube.com/playlist?list={pid}' target='_blank' style='flex:1; padding:10px; background:rgba(255,0,0,0.1); border:2px solid #FF0000; color:#FF0000; text-decoration:none; font-weight:bold; border-radius:5px; box-shadow: 0 0 15px #FF0000;'>🔴 YT VIDEO</a><a href='https://music.youtube.com/playlist?list={pid}' target='_blank' style='flex:1; padding:10px; background:rgba(176,38,255,0.1); border:2px solid #b026ff; color:#b026ff; text-decoration:none; font-weight:bold; border-radius:5px; box-shadow: 0 0 15px #b026ff;'>🎵 YT MUSIC</a></div></div>"
        st.markdown(grid_html, unsafe_allow_html=True)

    # --- TAB 18 : 💎🙌 ---
    with tab18:
        st.markdown("<h2 style='text-align:center; color:#00FF00; font-family:monospace; animation: neon-text 1.5s infinite;'>💎🙌</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#00FF00; font-size:22px; font-weight:bold; animation: neon-text 1.5s infinite;'>Mr-CRUNK-13 Accounts</p>", unsafe_allow_html=True)

        def social_btn(url, name, color, icon, is_discord=False):
            link = f"href='{url}' target='_blank'" if not is_discord else "href='#' onclick='return false;'"
            return f"<div style='text-align:center; padding:20px; background:#0f172a; border:2px solid {color}; border-radius:10px; margin-bottom:15px; box-shadow: 0 0 15px {color};'><h3 style='color:white; margin:0 0 10px 0;'>{icon} {name}</h3><a {link} style='display:inline-block; padding:12px 25px; background:rgba(0,0,0,0.5); border:2px solid {color}; color:{color}; font-weight:bold; text-decoration:none; border-radius:5px; font-size:18px; width:100%; box-sizing:border-box; border: 2px solid {color}; box-shadow: 0 0 15px {color};'>{'mr_crunk_13' if is_discord else 'OPEN LINK'}</a></div>"
            
        c18_1, c18_2 = st.columns(2)
        with c18_1:
            st.markdown(social_btn("https://youtube.com/@mr-crunk-13", "YouTube Gaming", "#FF0000", "🎮"), unsafe_allow_html=True)
            st.markdown(social_btn("https://www.reddit.com/u/Mr-CRUNK-13/s/GUhcBfd4aq", "Reddit", "#FF4500", "🟠"), unsafe_allow_html=True)
        with c18_2:
            st.markdown(social_btn("https://youtube.com/@mr-crunk-13-741", "YouTube Music", "#FF0000", "🎧"), unsafe_allow_html=True)
            st.markdown(social_btn("https://x.com/MrCRUNK13", "𝕏", "#1DA1F2", "🐦"), unsafe_allow_html=True)
            
        st.markdown(social_btn("mr_crunk_13", "Discord ID", "#5865F2", "👾", True), unsafe_allow_html=True)

    def draw_live(price, prev, chart, vol=0, sym="GME"):
        pct = ((price - prev) / prev) * 100 if prev > 0 else 0
        diff, clr = price - prev, ("#00FF00" if price >= prev else "#FF0000")
        price_str = f"{price:.2f}"
        p_int, p_dec = price_str.split('.')
        diff_sign = "+" if diff >= 0 else "-"
        abs_diff = abs(diff)
        
        sz = min(100 + (abs(pct) * 10), 180)
        anim_class = "nuclear-neon" if pct >= 0 else "neon-flash-red"
        icn = f"<div style='animation: {anim_class} 1.5s infinite;'><div style='font-size:{sz}px;'>🚀</div></div>" if pct >= 0 else f"<img src='data:image/jpeg;base64,{get_b64('Screenshot_20260216_163106_Discord.jpg')}' style='height:{sz}px; animation:{anim_class} 1.5s infinite;'>"
        
        html_live = f"""
        <style>
            .l-box {{ display:flex; justify-content:center; align-items:center; gap:20px; margin-top:30px; }}
            .l-dlr {{ font-size:50px; color:{clr}; text-shadow:0 0 20px {clr}; font-weight:bold; vertical-align:top; }}
            .l-int {{ font-size:100px; color:{clr}; text-shadow:0 0 20px {clr}; font-weight:bold; }}
            .l-dec {{ font-size:80px; color:{clr}; text-shadow:0 0 20px {clr}; font-weight:bold; }}
            .l-sub {{ color:{clr}; margin-top:0px; font-size:24px; font-weight:bold; }}
            .l-icn-w {{ display:flex; align-items:center; justify-content:center; }}
            
            @media screen and (orientation: landscape) {{
                .l-box {{ justify-content:space-between !important; align-items:flex-end !important; padding:0 10% !important; margin-top:125px !important; }}
                .l-dlr {{ font-size:87px !important; }}
                .l-int {{ font-size:175px !important; }}
                .l-dec {{ font-size:140px !important; }}
                .l-sub {{ font-size:42px !important; text-align:right; margin-top:-65px !important; }}
                .l-icn-w {{ transform: scale(1.5); margin-bottom:10px !important; }}
            }}
        </style>
        <div class='l-box'>
            <div style='text-align:right; white-space:nowrap;'>
                <span class='l-dlr'>$</span><span class='l-int'>{p_int}.</span><span class='l-dec'>{p_dec}</span>
                <div class='l-sub'>{diff_sign}{abs_diff:.2f} {pct:+.2f}%</div>
            </div>
            <div class='l-icn-w'>{icn}</div>
        </div>
        """
        st.markdown(html_live, unsafe_allow_html=True)
        
        if not chart.empty:
            fig, ax = plt.subplots(figsize=(10, 2.0), facecolor='black'); ax.set_facecolor('black')
        
        if not chart.empty:
            fig, ax = plt.subplots(figsize=(10, 2.0), facecolor='black'); ax.set_facecolor('black')
    def draw_live(price, prev, chart, vol=0, sym="GME"):
        pct = ((price - prev) / prev) * 100 if prev > 0 else 0
        diff, clr = price - prev, ("#00FF00" if price >= prev else "#FF0000")
        price_str = f"{price:.2f}"
        p_int, p_dec = price_str.split('.')
        diff_sign = "+" if diff >= 0 else "-"
        abs_diff = abs(diff)
        
        sz = min(100 + (abs(pct) * 10), 180)
        anim_class = "nuclear-neon" if pct >= 0 else "neon-flash-red"
        icn = f"<div style='animation: {anim_class} 1.5s infinite;'><div style='font-size:{sz}px;'>🚀</div></div>" if pct >= 0 else f"<img src='data:image/jpeg;base64,{get_b64('Screenshot_20260216_163106_Discord.jpg')}' style='height:{sz}px; animation:{anim_class} 1.5s infinite;'>"
        
        s_id = sym.replace("-", "")
        
        html_live = f"""
        <style>
            .{s_id}-box {{ display:flex; justify-content:center; align-items:center; gap:20px; margin-top:30px; }}
            .{s_id}-dlr {{ font-size:50px; color:{clr}; text-shadow:0 0 20px {clr}; font-weight:bold; vertical-align:top; }}
            .{s_id}-int {{ font-size:100px; color:{clr}; text-shadow:0 0 20px {clr}; font-weight:bold; }}
            .{s_id}-dec {{ font-size:80px; color:{clr}; text-shadow:0 0 20px {clr}; font-weight:bold; }}
            .{s_id}-sub {{ color:{clr}; margin-top:0px; font-size:24px; font-weight:bold; }}
            .{s_id}-icn-w {{ display:flex; align-items:center; justify-content:center; }}
            
            @media screen and (orientation: landscape) {{
                .{s_id}-box {{ justify-content:space-between !important; align-items:flex-end !important; padding:0 10% !important; margin-top:125px !important; }}
                .{s_id}-dlr {{ font-size:87px !important; }}
                .{s_id}-int {{ font-size:175px !important; }}
                .{s_id}-dec {{ font-size:140px !important; }}
                .{s_id}-sub {{ font-size:42px !important; text-align:right; margin-top:-65px !important; }}
                .{s_id}-icn-w {{ transform: scale(1.5); margin-bottom:10px !important; }}
                .{s_id}-icn-w img {{ margin-bottom: 40px !important; }}
            }}
        </style>
        <div class='{s_id}-box'>
            <div style='text-align:right; white-space:nowrap;'>
                <span class='{s_id}-dlr'>$</span><span class='{s_id}-int'>{p_int}.</span><span class='{s_id}-dec'>{p_dec}</span>
                <div class='{s_id}-sub'>{diff_sign}{abs_diff:.2f} {pct:+.2f}%</div>
            </div>
            <div class='{s_id}-icn-w'>{icn}</div>
        </div>
        """
        st.markdown(html_live, unsafe_allow_html=True)
        
        if not chart.empty:
            fig, ax = plt.subplots(figsize=(10, 2.0), facecolor='black'); ax.set_facecolor('black')
            v = chart.dropna().values
            ax.bar(np.arange(len(v)), v - np.min(v)*0.99, bottom=np.min(v)*0.99, color=clr, width=0.8); ax.axis('off')
            st.pyplot(fig, bbox_inches='tight', pad_inches=0); plt.close(fig)
            
        try:
            tk = yf.Ticker(sym)
            fi = tk.fast_info
            inf = tk.info
            d_high = fi.day_high
            d_low = fi.day_low
            d_prev = fi.previous_close
            d_avg = inf.get('averageVolume', inf.get('averageDailyVolume10Day', 'N/A'))
        except:
            d_high, d_low, d_prev, d_avg = 'N/A', 'N/A', 'N/A', 'N/A'

        def fmt_d(val, is_dol=False):
            if val == 'N/A' or val is None or str(val).lower() == 'nan': return "N/A"
            try: 
                if sym == "GME-WT": return f"${float(val):,.3f}" if is_dol else f"{float(val):,.0f}"
                else: return f"${float(val):,.2f}" if is_dol else f"{float(val):,.0f}"
            except: return str(val)

        avg_html = f"<div>AVG VOLUME: {fmt_d(d_avg)}</div>" if (sym == 'GME' or d_avg != 'N/A') else ""
        
        html_vol = (
            f"<div style='text-align:center; color:#888; font-family:monospace; margin-top:5px; line-height:1.6; font-size:18px;'>"
            f"<div>TODAY'S VOLUME: {vol:,.0f}</div>"
            f"{avg_html}"
            f"<div>DAY HIGH: {fmt_d(d_high, True)}</div>"
            f"<div>DAY LOW: {fmt_d(d_low, True)}</div>"
            f"<div>PREV CLOSE: {fmt_d(d_prev, True)}</div>"
            f"</div>"
        )
        st.markdown(html_vol, unsafe_allow_html=True)

    def render_content():
        plt.close('all') 
        p_nsy, p_wt, pr_nsy, pr_wt, vol_n, vol_w, ch_gme, ch_wt = fetch_terminal_data()
        adv_info, wt_info, gme_news = fetch_advanced_pro_data()
        opts, fin, bs, cf, ins, earn_dates = fetch_financials_and_options()
        
        qn, pn = st.session_state.osq, st.session_state.osp
        qw, pw = st.session_state.owq, st.session_state.owp
        gp = st.session_state.osp

        total_shares = qn
        v_s_u = qn * p_nsy
        v_w_u = qw * p_wt
        t_v_u = v_s_u + v_w_u
        t_c_u = (qn * gp) + (qw * pw)

        c_s, c_w = qn, qw
        c_gp_val = gp if qn > 0 else 0.0
        c_pw_val = pw if qw > 0 else 0.0
        
        c_v_s = c_s * p_nsy
        c_v_w = c_w * p_wt
        c_t_v = c_v_s + c_v_w
        c_t_c = (c_s * c_gp_val) + (c_w * c_pw_val)

        with ph1.container():
            @st.fragment(run_every="15s")
            def live_gme_screen():
                p_n, _, pr_n, _, v_n, _, ch_n, _ = fetch_terminal_data()
                draw_live(p_n, pr_n, ch_n, v_n)
            live_gme_screen()

        with ph2.container():
            @st.fragment(run_every="15s")
            def live_wt_screen():
                _, p_w, _, pr_w, _, v_w, _, ch_w = fetch_terminal_data()
                draw_live(p_w, pr_w, ch_w, v_w, sym="GME-WT")
            live_wt_screen()

        with ph3.container():
            s_c = qn * gp
            w_c = qw * pw
            s_pl = v_s_u - s_c
            w_pl = v_w_u - w_c
            t_pl = t_v_u - t_c_u
            
            val_shares = v_s_u if v_s_u > 0 else 0.01
            val_warrants = v_w_u if v_w_u > 0 else 0.01
            pct_s = (val_shares / (val_shares + val_warrants)) * 100
            pct_w = (val_warrants / (val_shares + val_warrants)) * 100
            s_pct_pl = (s_pl / s_c * 100) if s_c > 0 else 0
            w_pct_pl = (w_pl / w_c * 100) if w_c > 0 else 0
            t_pct_pl = (t_pl / t_c_u * 100) if t_c_u > 0 else 0

            w_deg = (pct_w / 100) * 360
            start_angle = -(w_deg / 2)

            fig4 = plt.figure(figsize=(32, 18)); fig4.patch.set_facecolor("#0e1621")
            gs = GridSpec(1, 3, width_ratios=[1, 2.5, 1])
            plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
            
            al = fig4.add_subplot(gs[0]); al.set_facecolor("#0e1621"); al.axis('off')
            al.text(0.9, 0.85, "GameStop Shares (GME)", color="#00FF00", fontsize=84, ha="right", weight="bold")
            al.text(0.9, 0.70, f"Val: ${v_s_u:,.2f}", color="white", fontsize=63, ha="right", weight="bold")
            al.text(0.9, 0.55, f"Qty: {qn:,} | Price: ${p_nsy:.2f}", color="#00FF00", fontsize=84, ha="right", weight="bold")
            al.text(0.9, 0.40, f"Avg Cost: ${gp:.2f}", color="white", fontsize=63, ha="right", weight="bold")
            al.text(0.9, 0.25, f"P/L: ${s_pl:+,.2f} ({s_pct_pl:+.2f}%)", color="#00FF00" if s_pl>=0 else "#FF0000", fontsize=84, ha="right", weight="bold")
            al.annotate("", xy=(0.95, 0.5), xytext=(1.28, 0.5), arrowprops=dict(arrowstyle="->", color="#00FF00", lw=20))

            ac = fig4.add_subplot(gs[1]); ac.set_facecolor("#0e1621"); ac.axis('equal')
            ac.pie([val_warrants, val_shares], colors=["#006400", "#00FF00"], radius=1.35, wedgeprops=dict(width=0.45, edgecolor="#0e1621"), startangle=start_angle)
            ac.text(-1.1, 0, f"{pct_s:.0f}%", fontsize=75, color="black", ha="center", va="center", weight="bold")
            ac.text(1.1, 0, f"{pct_w:.0f}%", fontsize=75, color="black", ha="center", va="center", weight="bold")
            ac.text(0, 0.15, "Total Value:", fontsize=45, color="white", ha="center", va="center", weight="bold")
            ac.text(0, -0.05, f"${t_v_u:,.2f}", fontsize=85, color="white", ha="center", va="center", weight="bold")
            ac.text(0, -0.25, f"${t_pl:+,.2f} ({t_pct_pl:+.2f}%)", fontsize=48, color="#00FF00" if t_pl>=0 else "#FF0000", ha="center", va="center", weight="bold")

            ar = fig4.add_subplot(gs[2]); ar.set_facecolor("#0e1621"); ar.axis('off')
            ar.text(0.1, 0.85, "Warrants (GME-WT)", color="#006400", fontsize=84, ha="left", weight="bold")
            ar.text(0.1, 0.70, f"Val: ${v_w_u:,.2f}", color="white", fontsize=63, ha="left", weight="bold")
            ar.text(0.1, 0.55, f"Qty: {qw:,} | Price: ${p_wt:.2f}", color="#006400", fontsize=84, ha="left", weight="bold")
            ar.text(0.1, 0.40, f"Avg Cost: ${pw:.3f}", color="white", fontsize=63, ha="left", weight="bold")
            ar.text(0.1, 0.25, f"P/L: ${w_pl:+,.2f} ({w_pct_pl:+.2f}%)", color="#00FF00" if w_pl>=0 else "#FF0000", fontsize=84, ha="left", weight="bold")
            ar.annotate("", xy=(0.08, 0.5), xytext=(-0.19, 0.5), arrowprops=dict(arrowstyle="->", color="#006400", lw=20))

            st.markdown('<div id="neon-p3" style="display:none;"></div><style>div[data-testid="stElementContainer"]:has(#neon-p3) + div[data-testid="stElementContainer"], div.element-container:has(#neon-p3) + div.element-container { border: 2px solid #00FF00 !important; box-shadow: 0 0 15px #00FF00 !important; border-radius: 15px !important; padding: 10px !important; background: #0e1621 !important; margin-bottom: 20px !important; }</style>', unsafe_allow_html=True)
            st.pyplot(fig4, bbox_inches='tight', pad_inches=0.1); plt.close(fig4)

        
        with ph4.container():
            html_d = f"""<div class='table-wrapper'><table class='ldb-t'>
            <tr><th>Ticker</th><th>Qty</th><th>Avg</th><th>Price</th><th>Cost</th><th>Value</th><th>P/L</th><th>%</th></tr>
            <tr><td>GME</td><td>{qn:,}</td><td>${gp:.2f}</td><td>${p_nsy:.2f}</td><td>${s_c:,.2f}</td><td>${v_s_u:,.2f}</td><td style="color:{'#00FF00' if s_pl>=0 else '#FF0000'};">${s_pl:+,.2f} ({s_pct_pl:+.2f}%)</td><td>{pct_s:.1f}%</td></tr>
            <tr><td>WARRANT</td><td>{qw:,}</td><td>${pw:.3f}</td><td>${p_wt:.2f}</td><td>${w_c:,.2f}</td><td>${v_w_u:,.2f}</td><td style="color:{'#00FF00' if w_pl>=0 else '#FF0000'};">${w_pl:+,.2f} ({w_pct_pl:+.2f}%)</td><td>{pct_w:.1f}%</td></tr>
            <tr style="font-weight:bold; font-size:18px;"><td style="color:#00FF00;">TOTAL</td><td></td><td></td><td></td><td style="color:#00FF00;">${t_c_u:,.2f}</td><td style="color:#00FF00;">${t_v_u:,.2f}</td><td style="color:{'#00FF00' if t_pl>=0 else '#FF0000'};">${t_pl:+,.2f} ({t_pct_pl:+.2f}%)</td><td style="color:#00FF00;">100%</td></tr>
            </table></div>"""
            st.markdown(html_d, unsafe_allow_html=True)

        with ph5.container():
            cw_c = c_w * c_pw_val
            cs_c = c_s * c_gp_val
            c_pl_s = c_v_s - cs_c
            c_pl_w = c_v_w - cw_c
            ct_pl = c_t_v - c_t_c
            
            cval_s = c_v_s if c_v_s > 0 else 0.01
            cval_w = c_v_w if c_v_w > 0 else 0.01
            cpct_s = (cval_s / (cval_s + cval_w)) * 100
            cpct_w = (cval_w / (cval_s + cval_w)) * 100
            c_s_pct = (c_pl_s / cs_c * 100) if cs_c > 0 else 0
            c_w_pct = (c_pl_w / cw_c * 100) if cw_c > 0 else 0
            ct_pct = (ct_pl / c_t_c * 100) if c_t_c > 0 else 0

            cw_deg = (cpct_w / 100) * 360
            c_start_angle = -(cw_deg / 2)

            fig_c4 = plt.figure(figsize=(32, 18)); fig_c4.patch.set_facecolor("#0e1621")
            gs_c = GridSpec(1, 3, width_ratios=[1, 2.5, 1])
            plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
            
            al_c = fig_c4.add_subplot(gs_c[0]); al_c.set_facecolor("#0e1621"); al_c.axis('off')
            al_c.text(0.9, 0.85, "Community Shares (GME)", color="#00FF00", fontsize=84, ha="right", weight="bold")
            al_c.text(0.9, 0.70, f"Val: ${c_v_s:,.2f}", color="white", fontsize=63, ha="right", weight="bold")
            al_c.text(0.9, 0.55, f"Qty: {c_s:,} | Price: ${p_nsy:.2f}", color="#00FF00", fontsize=84, ha="right", weight="bold")
            al_c.text(0.9, 0.40, f"Avg Cost: ${c_gp_val:.2f}", color="white", fontsize=63, ha="right", weight="bold")
            al_c.text(0.9, 0.25, f"P/L: ${c_pl_s:+,.2f} ({c_s_pct:+.2f}%)", color="#00FF00" if c_pl_s>=0 else "#FF0000", fontsize=84, ha="right", weight="bold")
            al_c.annotate("", xy=(0.95, 0.5), xytext=(1.28, 0.5), arrowprops=dict(arrowstyle="->", color="#00FF00", lw=20))

            ac_c = fig_c4.add_subplot(gs_c[1]); ac_c.set_facecolor("#0e1621"); ac_c.axis('equal')
            ac_c.pie([cval_w, cval_s], colors=["#006400", "#00FF00"], radius=1.35, wedgeprops=dict(width=0.45, edgecolor="#0e1621"), startangle=c_start_angle)
            ac_c.text(-1.1, 0, f"{cpct_s:.0f}%", fontsize=75, color="black", ha="center", va="center", weight="bold")
            ac_c.text(1.1, 0, f"{cpct_w:.0f}%", fontsize=75, color="black", ha="center", va="center", weight="bold")
            ac_c.text(0, 0.15, "WEN MOON Value:", fontsize=45, color="white", ha="center", va="center", weight="bold")
            ac_c.text(0, -0.05, f"${c_t_v:,.2f}", fontsize=85, color="white", ha="center", va="center", weight="bold")
            ac_c.text(0, -0.25, f"${ct_pl:+,.2f} ({ct_pct:+.2f}%)", fontsize=48, color="#00FF00" if ct_pl>=0 else "#FF0000", ha="center", va="center", weight="bold")

            ar_c = fig_c4.add_subplot(gs_c[2]); ar_c.set_facecolor("#0e1621"); ar_c.axis('off')
            ar_c.text(0.1, 0.85, "Community Warrants", color="#006400", fontsize=84, ha="left", weight="bold")
            ar_c.text(0.1, 0.70, f"Val: ${c_v_w:,.2f}", color="white", fontsize=63, ha="left", weight="bold")
            ar_c.text(0.1, 0.55, f"Qty: {c_w:,} | Price: ${p_wt:.2f}", color="#006400", fontsize=84, ha="left", weight="bold")
            ar_c.text(0.1, 0.40, f"Avg Cost: ${c_pw_val:.3f}", color="white", fontsize=63, ha="left", weight="bold")
            ar_c.text(0.1, 0.25, f"P/L: ${c_pl_w:+,.2f} ({c_w_pct:+.2f}%)", color="#00FF00" if c_pl_w>=0 else "#FF0000", fontsize=84, ha="left", weight="bold")
            ar_c.annotate("", xy=(0.08, 0.5), xytext=(-0.19, 0.5), arrowprops=dict(arrowstyle="->", color="#006400", lw=20))

            st.markdown('<div id="neon-p5" style="display:none;"></div><style>div[data-testid="stElementContainer"]:has(#neon-p5) + div[data-testid="stElementContainer"], div.element-container:has(#neon-p5) + div.element-container { border: 2px solid #00FF00 !important; box-shadow: 0 0 15px #00FF00 !important; border-radius: 15px !important; padding: 10px !important; background: #0e1621 !important; margin-bottom: 20px !important; }</style>', unsafe_allow_html=True)
            st.pyplot(fig_c4, bbox_inches='tight', pad_inches=0.1); plt.close(fig_c4)
                
        with ph6.container():
            html_w = f"""<div class='table-wrapper'><table class='ldb-t'>
            <tr><th>Ticker</th><th>Qty</th><th>Avg</th><th>Price</th><th>Cost</th><th>Value</th><th>P/L</th><th>%</th></tr>
            <tr><td>GME</td><td>{c_s:,}</td><td>${c_gp_val:.2f}</td><td>${p_nsy:.2f}</td><td>${cs_c:,.2f}</td><td>${c_v_s:,.2f}</td><td style="color:{'#00FF00' if c_pl_s>=0 else '#FF0000'};">${c_pl_s:+,.2f} ({c_s_pct:+.2f}%)</td><td>{cpct_s:.1f}%</td></tr>
            <tr><td>WARRANT</td><td>{c_w:,}</td><td>${c_pw_val:.3f}</td><td>${p_wt:.2f}</td><td>${cw_c:,.2f}</td><td>${c_v_w:,.2f}</td><td style="color:{'#00FF00' if c_pl_w>=0 else '#FF0000'};">${c_pl_w:+,.2f} ({c_w_pct:+.2f}%)</td><td>{cpct_w:.1f}%</td></tr>
            <tr style="font-weight:bold; font-size:18px;"><td style="color:#00FF00;">TOTAL</td><td></td><td></td><td></td><td style="color:#00FF00;">${c_t_c:,.2f}</td><td style="color:#00FF00;">${c_t_v:,.2f}</td><td style="color:{'#00FF00' if ct_pl>=0 else '#FF0000'};">${ct_pl:+,.2f} ({ct_pct:+.2f}%)</td><td style="color:#00FF00;">100%</td></tr>
            </table></div>"""
            st.markdown(html_w, unsafe_allow_html=True)

        with ph7.container():
                 # --- 6-TAB TERMINAL LEADERBOARD WITH TROPHY COLUMN ---
            st.markdown("""
            <style>
            @keyframes neon-drs { 0% { box-shadow: inset 0 0 5px #a200ff; border-top: 1px solid #a200ff; border-bottom: 1px solid #a200ff; } 50% { box-shadow: inset 0 0 20px #a200ff; border-top: 1px solid #d080ff; border-bottom: 1px solid #d080ff; } 100% { box-shadow: inset 0 0 5px #a200ff; border-top: 1px solid #a200ff; border-bottom: 1px solid #a200ff; } }
            @keyframes neon-gold { 0% { box-shadow: inset 0 0 5px #FFD700; border-top: 1px solid #FFD700; border-bottom: 1px solid #FFD700; } 50% { box-shadow: inset 0 0 20px #FFD700; border-top: 1px solid #FFF8DC; border-bottom: 1px solid #FFF8DC; } 100% { box-shadow: inset 0 0 5px #FFD700; border-top: 1px solid #FFD700; border-bottom: 1px solid #FFD700; } }
            @keyframes neon-silver { 0% { box-shadow: inset 0 0 5px #C0C0C0; border-top: 1px solid #C0C0C0; border-bottom: 1px solid #C0C0C0; } 50% { box-shadow: inset 0 0 20px #C0C0C0; border-top: 1px solid #FFFFFF; border-bottom: 1px solid #FFFFFF; } 100% { box-shadow: inset 0 0 5px #C0C0C0; border-top: 1px solid #C0C0C0; border-bottom: 1px solid #C0C0C0; } }
            @keyframes neon-bronze { 0% { box-shadow: inset 0 0 5px #CD7F32; border-top: 1px solid #CD7F32; border-bottom: 1px solid #CD7F32; } 50% { box-shadow: inset 0 0 20px #CD7F32; border-top: 1px solid #FFA07A; border-bottom: 1px solid #FFA07A; } 100% { box-shadow: inset 0 0 5px #CD7F32; border-top: 1px solid #CD7F32; border-bottom: 1px solid #CD7F32; } }

            @keyframes pulse-purple { 0% { text-shadow: 0 0 5px #9b51e0; } 50% { text-shadow: 0 0 15px #b026ff, 0 0 25px #9b51e0; } 100% { text-shadow: 0 0 5px #9b51e0; } }
            @keyframes pulse-gold-text { 0% { text-shadow: 0 0 5px #FFD700; } 50% { text-shadow: 0 0 15px #FFF8DC, 0 0 25px #FFD700; } 100% { text-shadow: 0 0 5px #FFD700; } }
            @keyframes pulse-silver-text { 0% { text-shadow: 0 0 5px #C0C0C0; } 50% { text-shadow: 0 0 15px #FFFFFF, 0 0 25px #C0C0C0; } 100% { text-shadow: 0 0 5px #C0C0C0; } }
            @keyframes pulse-bronze-text { 0% { text-shadow: 0 0 5px #CD7F32; } 50% { text-shadow: 0 0 15px #FFA07A, 0 0 25px #CD7F32; } 100% { text-shadow: 0 0 5px #CD7F32; } }

            .pulse-drs td { animation: neon-drs 2s infinite; }
            .pulse-gold td { animation: neon-gold 2s infinite; }
            .pulse-silver td { animation: neon-silver 2s infinite; }
            .pulse-bronze td { animation: neon-bronze 2s infinite; }

            .text-drs { animation: pulse-purple 1.5s infinite; color: #b026ff !important; font-weight: bold; }
            .text-gold { animation: pulse-gold-text 1.5s infinite; color: #FFD700 !important; font-weight: bold; }
            .text-silver { animation: pulse-silver-text 1.5s infinite; color: #C0C0C0 !important; font-weight: bold; }
            .text-bronze { animation: pulse-bronze-text 1.5s infinite; color: #CD7F32 !important; font-weight: bold; }
            </style>
            """, unsafe_allow_html=True)

            lb_tabs_t = st.tabs(["🌍 GENERAL", "📅 MONTHLY", "📆 WEEKLY", "🟣 DRS TOTAL", "🗓️ DRS MONTHLY", "⏳ DRS WEEKLY"])
            
            try:
                data = yf.download(["GME", "GME-WT"], period="1d", interval="2m", prepost=True, progress=False)['Close']
                live_p_n = float(data['GME'].dropna().iloc[-1]) if not data['GME'].dropna().empty else 24.50
                live_p_w = float(data['GME-WT'].dropna().iloc[-1]) if not data['GME-WT'].dropna().empty else 4.30
            except:
                live_p_n, live_p_w = 24.50, 4.30

            d_tv = (st.session_state.drs_osq * live_p_n) + (st.session_state.drs_owq * live_p_w)
            d_m_v = (st.session_state.get('monthly_drs_s', 0) * live_p_n) + (st.session_state.get('monthly_drs_w', 0) * live_p_w)
            d_w_v = (st.session_state.get('weekly_drs_s', 0) * live_p_n) + (st.session_state.get('weekly_drs_w', 0) * live_p_w)

            real_db = [{
                "name": st.session_state.get("ape_name", "Anonymous"),
                "tv": (st.session_state.osq * live_p_n) + (st.session_state.owq * live_p_w),
                "sq": st.session_state.osq, "wq": st.session_state.owq,
                "drs_tv": d_tv, "drs_mv": d_m_v, "drs_wv": d_w_v,
                "drs_sq": st.session_state.drs_osq, "drs_wq": st.session_state.drs_owq,
                "drs_w_s": st.session_state.get('weekly_drs_s', 0),
                "drs_m_s": st.session_state.get('monthly_drs_s', 0),
                "drs_w_w": st.session_state.get('weekly_drs_w', 0),
                "drs_m_w": st.session_state.get('monthly_drs_w', 0)
            }]

            for idx, t in enumerate(lb_tabs_t):
                with t:
                    if idx >= 3:
                        sort_k = "drs_tv" if idx == 3 else "drs_mv" if idx == 4 else "drs_wv"
                        ttl = "DRS TOTAL" if idx == 3 else "DRS MONTHLY" if idx == 4 else "DRS WEEKLY"
                        
                        q_s_key = "drs_sq" if idx == 3 else "drs_m_s" if idx == 4 else "drs_w_s"
                        q_w_key = "drs_wq" if idx == 3 else "drs_m_w" if idx == 4 else "drs_w_w"
                        
                        html = f"<div class='table-wrapper' style='border: 2px solid #9b51e0; box-shadow: 0 0 15px #9b51e0;'><table class='ldb-t' style='border: none;'><tr><th style='color:#9b51e0;'>RANK</th><th style='color:#9b51e0;'>APE</th><th style='color:#9b51e0;'>{ttl} VALUE</th><th style='color:#9b51e0;'>LOCKED S.</th><th style='color:#9b51e0;'>LOCKED W.</th><th style='color:#9b51e0;'>TROPHIES</th></tr>"
                        s_db = sorted(real_db, key=lambda x: x.get(sort_k, 0), reverse=True)
                        for i, r in enumerate(s_db):
                            rnk = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else str(i+1)
                            trphs = "🟣" if r.get('drs_tv', 0) > 0 else ""
                            
                            neon_class = ""
                            text_class = ""
                            if i <= 2 and r.get(sort_k, 0) > 0:
                                neon_class = "pulse-drs"
                                text_class = "class='text-drs'"
                                
                            html += f"<tr class='{neon_class}'><td>{rnk}</td><td><span {text_class}>{r['name']}</span></td><td style='color:#9b51e0;'>${r.get(sort_k, 0):,.2f}</td><td>{r.get(q_s_key, 0):,}</td><td>{r.get(q_w_key, 0):,}</td><td style='font-size:20px;'>{trphs}</td></tr>"
                        st.markdown(html + "</table></div>", unsafe_allow_html=True)
                    else: 
                        html = "<div class='table-wrapper'><table class='ldb-t'><tr><th>RANK</th><th>APE</th><th>TOTAL VALUE</th><th>SHARES</th><th>WARRANTS</th><th>TROPHIES</th></tr>"
                        s_db = sorted(real_db, key=lambda x: x.get("tv", 0), reverse=True)
                        for i, r in enumerate(s_db):
                            rnk = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else str(i+1)
                            trphs = "🟣" if r.get('drs_tv', 0) > 0 else ""
                            
                            neon_class = ""
                            text_class = ""
                            if i == 0:
                                neon_class = "pulse-gold"
                                text_class = "class='text-gold'"
                            elif i == 1:
                                neon_class = "pulse-silver"
                                text_class = "class='text-silver'"
                            elif i == 2:
                                neon_class = "pulse-bronze"
                                text_class = "class='text-bronze'"
                                
                            html += f"<tr class='{neon_class}'><td>{rnk}</td><td><span {text_class}>{r['name']}</span></td><td style='color:#00FF00;'>${r.get('tv', 0):,.2f}</td><td>{r.get('sq', 0):,}</td><td>{r.get('wq', 0):,}</td><td style='font-size:20px;'>{trphs}</td></tr>"
                        st.markdown(html + "</table></div>", unsafe_allow_html=True)

        with ph8.container():
            # --- WEN MOON SUMMARY ENGINE ---
            total_holders = len(real_db)
            avg_s_per_person = c_s / total_holders if total_holders > 0 else 0
            avg_w_per_person = c_w / total_holders if total_holders > 0 else 0
            w_s, w_w = st.session_state.get("weekly_s", 0), st.session_state.get("weekly_w", 0)
            m_s, m_w = st.session_state.get("monthly_s", 0), st.session_state.get("monthly_w", 0)

            c_w_pct_val = (c_v_w / c_t_v * 100) if c_t_v > 0 else 0.0

            # --- DYNAMIC HTML DASHBOARD (WEN MOON TOTALS & RECENT PURCHASES) ---
            html_summary = f"""
            <style>
                @keyframes pulse-yellow {{
                    0% {{ text-shadow: 0 0 5px #FFD700; }}
                    50% {{ text-shadow: 0 0 15px #FFD700, 0 0 30px #FFD700; }}
                    100% {{ text-shadow: 0 0 5px #FFD700; }}
                }}
                .neon-yellow {{
                    color: #FFD700 !important;
                    animation: pulse-yellow 1.5s infinite;
                }}
            </style>
            <div style="background-color: #0f172a; padding: 20px; border-radius: 10px; border: 2px solid #0259c7; box-shadow: 0 0 15px #0259c7;">
                <h2 style="text-align: center; color: #00FF00; margin-bottom: 15px; animation: neon-text 1.5s infinite; font-family: monospace;">📊 WEN MOON SUMMARY</h2>
                <div style="text-align: center; margin-bottom: 15px;">
                    <h3 class="neon-yellow" style="margin: 0; font-size: 32px;">TOTAL HOLDERS</h3>
                    <p class="neon-yellow" style="font-size: 62px; font-weight: bold; margin: 5px 0 0 0;">{total_holders:,}</p>
                </div>
                <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin-bottom: 0px; gap: 20px; text-align: center;">
                    <div style="background-color: #0e1621; padding: 20px; border-radius: 8px; border: 2px solid #00FF00; box-shadow: 0 0 15px #00FF00; flex: 1; min-width: 250px;">
                        <h4 style="color: #00FF00; margin-top: 0; font-size: 24px; font-weight: bold;">GME SHARES</h4>
                        <p style="margin: 10px 0; font-size: 18px; color: #ccc;">Total Shares: <strong style="color: white;">{c_s:,.0f}</strong></p>
                        <p style="margin: 10px 0; font-size: 18px; color: #ccc;">Avg Cost: <strong style="color: white;">${c_gp_val:,.2f}</strong></p>
                        <p style="margin: 10px 0; font-size: 18px; color: #ccc;">Avg Shares / Person: <strong style="color: white;">{avg_s_per_person:,.0f}</strong></p>
                    </div>
                    <div style="background-color: #0e1621; padding: 20px; border-radius: 8px; border: 2px solid #006400; box-shadow: 0 0 15px #006400; flex: 1; min-width: 250px;">
                        <h4 style="color: #006400; margin-top: 0; font-size: 24px; font-weight: bold;">GME WARRANTS</h4>
                        <p style="margin: 10px 0; font-size: 18px; color: #ccc;">Total Warrants: <strong style="color: white;">{c_w:,.0f}</strong></p>
                        <p style="margin: 10px 0; font-size: 18px; color: #ccc;">Avg Cost: <strong style="color: white;">${c_pw_val:,.2f}</strong></p>
                        <p style="margin: 10px 0; font-size: 18px; color: #ccc;">Avg Warrants / Person: <strong style="color: white;">{avg_w_per_person:,.0f}</strong></p>
                        <div style="margin-top: 25px;">
                            <p style="color: #006400; font-size: 16px; font-weight: bold; text-align: center; margin: 0 0 5px 0;">WARRANTS: {c_w_pct_val:.1f}% OF LIVE VALUE</p>
                            <div style="width: 100%; background-color: #050505; border-radius: 10px; height: 12px; border: 1px solid #00FF00; box-shadow: 0 0 10px #00FF00; overflow: hidden;">
                                <div style="width: {c_w_pct_val}%; background-color: #006400; height: 100%; box-shadow: 0 0 10px #006400;"></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div style="background-color: #0e1621; padding: 20px; border-radius: 8px; border: 2px solid #FFD700; box-shadow: 0 0 15px #FFD700; margin-top: 20px;">
                    <h4 style="color: #FFD700; margin-top: 0; font-size: 24px; font-weight: bold; text-align: center;">🔥 WEN MOON RECENT PURCHASES</h4>
                    <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px;">
                        <div style="background-color: #0f172a; padding: 15px; border-radius: 8px; border: 2px solid #00FF00; box-shadow: 0 0 15px #00FF00; flex: 1; min-width: 120px; text-align: center;">
                            <p style="color: #00FF00; font-size: 18px; font-weight: bold; margin: 0 0 10px 0; text-align: center;">WEEKLY</p>
                            <p style="margin: 5px 0; font-size: 16px; color: white;">Shares: <strong>+{w_s:,.0f}</strong></p>
                            <p style="margin: 5px 0; font-size: 16px; color: white;">Warrants: <strong>+{w_w:,.0f}</strong></p>
                        </div>
                        <div style="background-color: #0f172a; padding: 15px; border-radius: 8px; border: 2px solid #006400; box-shadow: 0 0 15px #006400; flex: 1; min-width: 120px; text-align: center;">
                            <p style="color: #006400; font-size: 18px; font-weight: bold; margin: 0 0 10px 0; text-align: center;">MONTHLY</p>
                            <p style="margin: 5px 0; font-size: 16px; color: white;">Shares: <strong>+{m_s:,.0f}</strong></p>
                            <p style="margin: 5px 0; font-size: 16px; color: white;">Warrants: <strong>+{m_w:,.0f}</strong></p>
                        </div>
                    </div>
                </div>
            </div>
            """
            st.markdown(html_summary, unsafe_allow_html=True)
            
            # --- WEN MOON COMMUNITY GRAPH ---
            import plotly.graph_objects as go
            fig_comm = go.Figure()
            fig_comm.add_trace(go.Bar(name='Shares', x=['WEEKLY', 'MONTHLY'], y=[w_s, m_s], marker_color='#00FF00'))
            fig_comm.add_trace(go.Bar(name='Warrants', x=['WEEKLY', 'MONTHLY'], y=[w_w, m_w], marker_color='#006400'))
            fig_comm.update_layout(barmode='group', template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', title={'text': "WEN MOON VOLUME", 'x': 0.5, 'y': 0.92, 'font': {'color': '#FFD700', 'family': 'monospace'}}, margin=dict(l=20, r=20, t=70, b=0), height=350)
            st.plotly_chart(fig_comm, use_container_width=True)

            # --- 🟣 WEN MOON DRS POOL ---
            total_comm_drs_s = sum(r.get("drs_sq", 0) for r in real_db)
            total_comm_drs_w = sum(r.get("drs_wq", 0) for r in real_db)
            drs_apes_count = sum(1 for r in real_db if r.get("drs_tv", 0) > 0)
            
            # --- COLOR CONFIGURATION ---
            color_drs_s = "#9b51e0"  # Established Purple
            color_drs_w = "#b026ff"  # Established Electric Pink/Rose
            
            st.markdown(f"""
            <div style="margin-top: 0px; border: 2px solid {color_drs_s}; box-shadow: 0 0 15px {color_drs_s}; border-radius: 15px; padding: 20px; background-color: rgba(155, 81, 224, 0.05);">
                <h2 style="text-align: center; color: {color_drs_s}; text-shadow: 0 0 10px {color_drs_s}; font-family: monospace; margin-bottom: 20px;">🟣 WEN MOON DRS</h2>
                <div style="display: flex; justify-content: space-around; flex-wrap: wrap; text-align: center;">
                    <div style="flex: 1; min-width: 120px;">
                        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 5px;">
                            <span style="display:inline-block; width:16px; height:16px; background-color:{color_drs_s}; border-radius:3px; margin-right:8px;"></span>
                            <span style="color: white; font-weight: bold; font-size: 14px;">SECURED SHARES</span>
                        </div>
                        <p style="color: {color_drs_s}; font-size: 32px; font-weight: bold; margin: 0; text-shadow: 0 0 10px rgba(155, 81, 224, 0.5);">{total_comm_drs_s:,}</p>
                    </div>
                    <div style="flex: 1; min-width: 120px;">
                        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 5px;">
                            <span style="display:inline-block; width:16px; height:16px; background-color:{color_drs_w}; border-radius:3px; margin-right:8px;"></span>
                            <span style="color: white; font-weight: bold; font-size: 14px;">SECURED WARRANTS</span>
                        </div>
                        <p style="color: {color_drs_w}; font-size: 32px; font-weight: bold; margin: 0; text-shadow: 0 0 10px rgba(176, 38, 255, 0.5);">{total_comm_drs_w:,}</p>
                    </div>
                </div>
                <p style="text-align: center; color: #ffffff; font-size: 1.1em; margin-top: 15px;">
                    🚀 <strong>{drs_apes_count}</strong> APES HAVE LOCKED THEIR SHARES 🟣
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # --- 🟣 WEN MOON DRS PROGRESS BARS ---
            c_drs_s_pct = (total_comm_drs_s / c_s * 100) if c_s > 0 else 0
            c_drs_w_pct = (total_comm_drs_w / c_w * 100) if c_w > 0 else 0
            
            st.markdown(f"""
            <div style="width: 100%; background-color: #050505; border-radius: 10px; height: 12px; border: 1px solid {color_drs_s}; box-shadow: 0 0 10px {color_drs_s}; overflow: hidden; margin-bottom: 5px; margin-top: 15px;">
            <div style="width: {c_drs_s_pct}%; background-color: {color_drs_s}; height: 100%; box-shadow: 0 0 10px {color_drs_s};"></div>
            </div>
            <p style="color: {color_drs_s}; font-size: 0.7em; text-align: right; font-weight: bold; margin: 0 0 10px 0;">{c_drs_s_pct:.1f}% OF SHARES LOCKED</p>
            <div style="width: 100%; background-color: #050505; border-radius: 10px; height: 12px; border: 1px solid {color_drs_w}; box-shadow: 0 0 10px {color_drs_w}; overflow: hidden; margin-bottom: 5px;">
            <div style="width: {c_drs_w_pct}%; background-color: {color_drs_w}; height: 100%; box-shadow: 0 0 10px {color_drs_w};"></div>
            </div>
            <p style="color: {color_drs_w}; font-size: 0.7em; text-align: right; font-weight: bold; margin: 0;">{c_drs_w_pct:.1f}% OF WARRANTS LOCKED</p>
            """, unsafe_allow_html=True)

            # --- COMMUNITY DRS WEEKLY/MONTHLY VISUALS ---
            c_d_w_s = sum(r.get("drs_w_s", 0) for r in real_db)
            c_d_m_s = sum(r.get("drs_m_s", 0) for r in real_db)
            c_d_w_w = sum(r.get("drs_w_w", 0) for r in real_db)
            c_d_m_w = sum(r.get("drs_m_w", 0) for r in real_db)

            st.markdown(f"""
            <div style="background-color: rgba(155, 81, 224, 0.05); padding: 20px; border-radius: 10px; border: 2px solid {color_drs_s}; box-shadow: 0 0 15px {color_drs_s}; margin-top: 20px;">
                <h3 style="color: {color_drs_s}; text-align: center; font-family: monospace; text-shadow: 0 0 5px {color_drs_s};">🟣 RECENT SECURED DRS</h3>
                <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px;">
                    <div style="background-color: #0e1621; padding: 15px; border-radius: 8px; border: 2px solid {color_drs_s}; box-shadow: 0 0 15px {color_drs_s}; flex: 1; min-width: 120px; text-align: center;">
                        <p style="color: {color_drs_s}; font-weight: bold; margin: 0 0 10px 0;">WEEKLY</p>
                        <p style="color: white; margin: 0;">Shares: <strong style="color: {color_drs_s};">+{c_d_w_s:,}</strong></p>
                        <p style="color: white; margin: 0;">Warrants: <strong style="color: {color_drs_w};">+{c_d_w_w:,}</strong></p>
                    </div>
                    <div style="background-color: #0e1621; padding: 15px; border-radius: 8px; border: 2px solid {color_drs_w}; box-shadow: 0 0 15px {color_drs_w}; flex: 1; min-width: 120px; text-align: center;">
                        <p style="color: {color_drs_w}; font-weight: bold; margin: 0 0 10px 0;">MONTHLY</p>
                        <p style="color: white; margin: 0;">Shares: <strong style="color: {color_drs_s};">+{c_d_m_s:,}</strong></p>
                        <p style="color: white; margin: 0;">Warrants: <strong style="color: {color_drs_w};">+{c_d_m_w:,}</strong></p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            fig_drs_c = go.Figure()
            fig_drs_c.add_trace(go.Bar(name='Shares', x=['WEEKLY', 'MONTHLY'], y=[c_d_w_s, c_d_m_s], marker_color=color_drs_s))
            fig_drs_c.add_trace(go.Bar(name='Warrants', x=['WEEKLY', 'MONTHLY'], y=[c_d_w_w, c_d_m_w], marker_color=color_drs_w))
            fig_drs_c.update_layout(barmode='group', template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', title={'text': "WEN MOON DRS VOLUME", 'x': 0.5, 'y': 0.92, 'font': {'color': color_drs_s, 'family': 'monospace'}}, margin=dict(l=20, r=20, t=70, b=20), height=350)
            st.plotly_chart(fig_drs_c, use_container_width=True)

        with ph9.container():
            def fmt(val, is_pct=False, is_dol=False):
                if val == 'N/A' or pd.isna(val) or val is None: return "N/A"
                try:
                    v = float(val)
                    if is_pct: return f"{v*100:.2f}%"
                    if is_dol: return f"${v:,.2f}"
                    return f"{v:,.0f}"
                except: return str(val)

            ptab1, ptab2, ptab3 = st.tabs(["🏛️ GME FUNDAMENTALS", "📜 WARRANTS DATA", "📊 NET INCOME"])
            
            with ptab1:
                html_gme = f"""
                <style>
                    .pro-g {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 15px; }}
                    .pb {{ background: #0e1621; border: 2px solid #00FF00; box-shadow: 0 0 10px #00FF00; border-radius: 8px; padding: 15px; text-align: center; }}
                    .pb h4 {{ color: #00FF00; margin: 0 0 5px 0; font-size: 16px; font-family: monospace; }}
                    .pb p {{ color: white; font-size: 22px; font-weight: bold; margin: 0; }}
                </style>
                <div class="pro-g">
                    <div class="pb"><h4>Market Cap</h4><p>{fmt(adv_info.get('marketCap'), is_dol=True)}</p></div>
                    <div class="pb"><h4>Total Cash</h4><p>{fmt(adv_info.get('totalCash'), is_dol=True)}</p></div>
                    <div class="pb"><h4>Total Debt</h4><p>{fmt(adv_info.get('totalDebt'), is_dol=True)}</p></div>
                    <div class="pb"><h4>Shares Outstanding</h4><p>{fmt(adv_info.get('sharesOutstanding'))}</p></div>
                    <div class="pb"><h4>Float Shares</h4><p>{fmt(adv_info.get('floatShares'))}</p></div>
                    <div class="pb"><h4>Total Revenue</h4><p>{fmt(adv_info.get('totalRevenue'), is_dol=True)}</p></div>
                    <div class="pb"><h4>Revenue Per Share</h4><p>{fmt(adv_info.get('revenuePerShare'), is_dol=True)}</p></div>
                    <div class="pb"><h4>Net Income (TTM)</h4><p>{fmt(adv_info.get('netIncomeToCommon'), is_dol=True)}</p></div>
                    <div class="pb"><h4>Net Income Per Share (EPS)</h4><p>{fmt(adv_info.get('trailingEps'), is_dol=True)}</p></div>
                    <div class="pb"><h4>Forward EPS</h4><p>{fmt(adv_info.get('forwardEps'), is_dol=True)}</p></div>
                    <div class="pb"><h4>Book Value Per Share</h4><p>{fmt(adv_info.get('bookValue'), is_dol=True)}</p></div>
                    <div class="pb"><h4>Free Cash Flow</h4><p>{fmt(adv_info.get('freeCashflow'), is_dol=True)}</p></div>
                    <div class="pb"><h4>Short % of Float</h4><p>{fmt(adv_info.get('shortPercentOfFloat'), is_pct=True)}</p></div>
                    <div class="pb"><h4>Days to Cover</h4><p>{fmt(adv_info.get('shortRatio'))}</p></div>
                    <div class="pb"><h4>Held by Insiders</h4><p>{fmt(adv_info.get('heldPercentInsiders'), is_pct=True)}</p></div>
                    <div class="pb"><h4>Held by Institutions</h4><p>{fmt(adv_info.get('heldPercentInstitutions'), is_pct=True)}</p></div>
                    <div class="pb"><h4>52 Week High</h4><p>{fmt(adv_info.get('fiftyTwoWeekHigh'), is_dol=True)}</p></div>
                    <div class="pb"><h4>52 Week Low</h4><p>{fmt(adv_info.get('fiftyTwoWeekLow'), is_dol=True)}</p></div>
                </div>"""
                st.markdown(html_gme, unsafe_allow_html=True)
                
            with ptab2:
                def fmt_w(val, is_vol=False):
                    if val == 'N/A' or pd.isna(val) or val is None: return "N/A"
                    try: return f"{float(val):,.0f}" if is_vol else f"${float(val):,.3f}"
                    except: return str(val)
                
                wt_vol = wt_info.get('lastVolume', wt_info.get('volume', 'N/A'))
                wt_open = wt_info.get('regularMarketOpen', wt_info.get('open', 'N/A'))
                wt_high = wt_info.get('dayHigh', wt_info.get('regularMarketDayHigh', 'N/A'))
                wt_low = wt_info.get('dayLow', wt_info.get('regularMarketDayLow', 'N/A'))
                wt_prev = wt_info.get('previousClose', wt_info.get('regularMarketPreviousClose', 'N/A'))
                
                html_wt = f"""
                <div class="pro-g">
                    <div class="pb" style="border-color:#006400; box-shadow: 0 0 10px #006400;"><h4 style="color:#006400;">Contract Name</h4><p>GME-WT (Warrant)</p></div>
                    <div class="pb" style="border-color:#006400; box-shadow: 0 0 10px #006400;"><h4 style="color:#006400;">Live Price</h4><p>{fmt_w(p_wt)}</p></div>
                    <div class="pb" style="border-color:#006400; box-shadow: 0 0 10px #006400;"><h4 style="color:#006400;">Today's Volume</h4><p>{fmt_w(wt_vol, True)}</p></div>
                    <div class="pb" style="border-color:#006400; box-shadow: 0 0 10px #006400;"><h4 style="color:#006400;">Market Open</h4><p>{fmt_w(wt_open)}</p></div>
                    <div class="pb" style="border-color:#006400; box-shadow: 0 0 10px #006400;"><h4 style="color:#006400;">Day High</h4><p>{fmt_w(wt_high)}</p></div>
                    <div class="pb" style="border-color:#006400; box-shadow: 0 0 10px #006400;"><h4 style="color:#006400;">Day Low</h4><p>{fmt_w(wt_low)}</p></div>
                    <div class="pb" style="border-color:#006400; box-shadow: 0 0 10px #006400;"><h4 style="color:#006400;">Previous Close</h4><p>{fmt_w(wt_prev)}</p></div>
                </div>"""
                st.markdown(html_wt, unsafe_allow_html=True)

            with ptab3:
                st.markdown("<h4 style='color:white; text-align:center;'>GameStop Net Income per Fiscal Quarter (M$)</h4>", unsafe_allow_html=True)
                inc_data = [
                    {"Year": "2025", "Q1": 45, "Q2": 169, "Q3": 77, "Q4": None, "Total": 291},
                    {"Year": "2024", "Q1": -32, "Q2": 15, "Q3": 17, "Q4": 131, "Total": 131},
                    {"Year": "2023", "Q1": -51, "Q2": -3, "Q3": -3, "Q4": 63, "Total": 7},
                    {"Year": "2022", "Q1": -158, "Q2": -109, "Q3": -95, "Q4": 48, "Total": -313}
                ]
                html_inc = "<div class='table-wrapper'><table class='ldb-t'><tr><th>Fiscal Year</th><th>Q1</th><th>Q2</th><th>Q3</th><th>Q4</th><th>Results</th></tr>"
                for r in inc_data:
                    html_inc += f"<tr><td>{r['Year']}</td>"
                    for q in ["Q1", "Q2", "Q3", "Q4", "Total"]:
                        val = r[q]
                        if val is None: html_inc += "<td></td>"
                        else:
                            c = "rgba(0, 255, 0, 0.25)" if val > 0 else "rgba(255, 0, 0, 0.25)" if val < 0 else "transparent"
                            html_inc += f"<td style='background-color:{c}; color:white; font-size:20px; font-weight:bold;'>{val if val < 0 else f'+{val}'}M</td>"
                    html_inc += "</tr>"
                st.markdown(html_inc + "</table></div>", unsafe_allow_html=True)

        with ph10.container():
            st.markdown("<h2 style='text-align:center; color:#00FF00; font-family:monospace;'>⛓️ OPTIONS CHAIN TERMINAL (ATM CENTERED)</h2>", unsafe_allow_html=True)
            if len(opts) > 0:
                selected_expiry = st.selectbox("📅 SELECT EXPIRATION DATE:", opts, key="opt_exp_selector")
                try:
                    tk = yf.Ticker("GME")
                    chain = tk.option_chain(selected_expiry)
                    
                    def build_centered_opt_table(df, title, color, current_price):
                        df['diff'] = (df['strike'] - current_price).abs()
                        atm_idx = df['diff'].idxmin()
                        start_idx = max(0, atm_idx - 12)
                        end_idx = min(len(df), atm_idx + 13)
                        display_df = df.iloc[start_idx:end_idx]
                        
                        html = f"<h4 style='color:{color}; text-align:center;'>{title}</h4><div class='table-wrapper'><table class='ldb-t' style='font-size:14px;'><tr><th>Strike</th><th>Last Price</th><th>Volume</th><th>Open Interest</th><th>Implied Vol</th></tr>"
                        for _, r in display_df.iterrows():
                            is_atm = "style='background-color:rgba(255,255,255,0.1);'" if abs(r['strike']-current_price) < 0.6 else ""
                            html += f"<tr {is_atm}><td>${r.get('strike', 0):.2f}</td><td>${r.get('lastPrice', 0):.2f}</td><td>{r.get('volume', 0)}</td><td>{r.get('openInterest', 0)}</td><td>{r.get('impliedVolatility', 0)*100:.1f}%</td></tr>"
                        return html + "</table></div>"
                    
                    c_col, p_col = st.columns(2)
                    with c_col: st.markdown(build_centered_opt_table(chain.calls, "🔥 CALLS", "#00FF00", p_nsy), unsafe_allow_html=True)
                    with p_col: st.markdown(build_centered_opt_table(chain.puts, "🩸 PUTS", "#FF0000", p_nsy), unsafe_allow_html=True)
                except:
                    st.warning("Options chain data currently unavailable for this date.")
            else:
                st.info("No expiration dates found or market closed.")

        with ph11.container():
            st.markdown("<h2 style='text-align:center; color:#00FF00; font-family:monospace;'>🏦 FINANCIALS & CONSENSUS</h2>", unsafe_allow_html=True)
            fin_t1, fin_t2, fin_t3 = st.tabs(["📊 REVENUE & EPS", "🔮 ANALYST CONSENSUS", "🗃️ RAW STATEMENTS"])
            
            with fin_t1:
                st.markdown("<h4 style='color:white;'>Historical Revenue & Net Income</h4>", unsafe_allow_html=True)
                if not fin.empty and 'Total Revenue' in fin.index:
                    try:
                        revs = fin.loc['Total Revenue'].dropna().iloc[::-1]
                        fig_fin = go.Figure()
                        fig_fin.add_trace(go.Bar(x=revs.index.astype(str), y=revs.values, name='Total Revenue', marker_color='#0259c7'))
                        if 'Net Income' in fin.index:
                            net = fin.loc['Net Income'].dropna().iloc[::-1]
                            fig_fin.add_trace(go.Scatter(x=net.index.astype(str), y=net.values, mode='lines+markers', name='Net Income', line=dict(color='#00FF00', width=4)))
                        fig_fin.update_layout(template="plotly_dark", plot_bgcolor='#050505', paper_bgcolor='#050505', margin=dict(l=0, r=0, t=30, b=0))
                        st.plotly_chart(fig_fin, use_container_width=True)
                    except: st.info("Chart data formatting error.")
                else: st.info("Historical visual data unavailable.")
                
            with fin_t2:
                st.markdown("<h3 style='color:#00FF00; text-align:center;'>Upcoming Earnings & Estimates</h3>", unsafe_allow_html=True)
                
                html_est = """
                <style>
                    .est-g { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-bottom: 20px; }
                    .eb { background: #0e1621; border: 2px solid #00FF00; box-shadow: 0 0 15px #00FF00; border-radius: 8px; padding: 10px; text-align: center; }
                    .eb h4 { color: #00FF00; margin: 0 0 5px 0; font-size: 14px; }
                    .eb p { color: white; font-size: 18px; font-weight: bold; margin: 0; }
                    .hist-t { width: 100%; border-collapse: collapse; font-family: monospace; font-size: 12px; text-align: right; margin-top: 10px; }
                    .hist-t th { background: #001f3f; color: #00FF00; padding: 8px; border-bottom: 1px solid #00FF00; text-align: center; white-space: nowrap; }
                    .hist-t th:first-child { text-align: left; }
                    .hist-t td { background: #0f172a; padding: 8px; border-bottom: 1px solid #1e293b; color: white; white-space: nowrap; text-align: center; }
                    .hist-t td:first-child { text-align: left; font-weight: bold; color: #00FF00; }
                    .beat { color: #00FF00 !important; font-weight: bold; }
                    .miss { color: #FF3333 !important; }
                    .fy-row td { background: #0b2239 !important; border-top: 2px solid #00FF00; font-size: 13px; }
                    /* --- MOBILE RESPONSIVE RULES --- */
                    @media screen and (max-width: 600px) {
                        .sep { display: none; }
                        .eps-val { display: block; margin-top: 5px; }
                    }
                </style>
                <div class="est-g">
                    <div class="eb"><h4>Q4 2025 (Next)</h4><p>Rev: $1.47B<span class="sep"> | </span><span class="eps-val">EPS: $0.37</span></p></div>
                    <div class="eb"><h4>FY 2025 (Proj)</h4><p>Rev: $4.16B<span class="sep"> | </span><span class="eps-val">EPS: $0.99</span></p></div>
                </div>
                <h3 style='color:#00FF00; text-align:center; margin-top:20px;'>5-Year Consensus History</h3>
                """
               
                # Verified Real History Data with Full Years (FY)
                hist_data = [
                    {"p": "Q3 2025", "ee": 0.20, "ae": 0.24, "er": "893.6M", "ar": "821.0M", "fy": False},
                    {"p": "Q2 2025", "ee": 0.16, "ae": 0.25, "er": "823.2M", "ar": "972.2M", "fy": False},
                    {"p": "Q1 2025", "ee": 0.04, "ae": 0.17, "er": "754.2M", "ar": "732.4M", "fy": False},
                    {"p": "FY 2024", "ee": -0.21, "ae": 0.34, "er": "4.36B",  "ar": "3.82B",  "fy": True},
                    {"p": "Q4 2024", "ee": 0.08, "ae": 0.30, "er": "1.50B",  "ar": "1.28B",  "fy": False},
                    {"p": "Q3 2024", "ee": -0.06, "ae": 0.06, "er": "919.9M", "ar": "860.3M", "fy": False},
                    {"p": "Q2 2024", "ee": -0.09, "ae": 0.01, "er": "895.6M", "ar": "798.0M", "fy": False},
                    {"p": "Q1 2024", "ee": -0.14, "ae": -0.03, "er": "1.05B",  "ar": "881.8M", "fy": False},
                    {"p": "FY 2023", "ee": -0.91, "ae": -0.64, "er": "5.47B",  "ar": "5.27B",  "fy": True},
                    {"p": "Q4 2023", "ee": -0.12, "ae": -0.14, "er": "1.79B",  "ar": "1.79B",  "fy": False},
                    {"p": "Q3 2023", "ee": -0.13, "ae": 0.16, "er": "1.18B",  "ar": "1.08B",  "fy": False},
                    {"p": "Q2 2023", "ee": -0.28, "ae": -0.31, "er": "1.14B",  "ar": "1.16B",  "fy": False},
                    {"p": "Q1 2023", "ee": -0.38, "ae": -0.35, "er": "1.36B",  "ar": "1.24B",  "fy": False},
                    {"p": "FY 2022", "ee": -0.46, "ae": -1.52, "er": "6.12B",  "ar": "5.94B",  "fy": True},
                    {"p": "Q4 2022", "ee": -0.37, "ae": -0.52, "er": "2.18B",  "ar": "2.23B",  "fy": False},
                    {"p": "Q3 2022", "ee": 0.21, "ae": -0.46, "er": "1.35B",  "ar": "1.19B",  "fy": False},
                    {"p": "Q2 2022", "ee": -0.13, "ae": -0.35, "er": "1.27B",  "ar": "1.14B",  "fy": False},
                    {"p": "Q1 2022", "ee": -0.17, "ae": -0.19, "er": "1.32B",  "ar": "1.38B",  "fy": False},
                    {"p": "FY 2021", "ee": -0.37, "ae": -0.25, "er": "5.92B",  "ar": "6.01B",  "fy": True},
                    {"p": "Q4 2021", "ee": -0.21, "ae": -0.11, "er": "2.22B",  "ar": "2.25B",  "fy": False},
                    {"p": "Q3 2021", "ee": 0.34, "ae": 0.34, "er": "1.30B",  "ar": "1.30B",  "fy": False},
                    {"p": "Q2 2021", "ee": -0.21, "ae": -0.13, "er": "1.12B",  "ar": "1.18B",  "fy": False},
                    {"p": "Q1 2021", "ee": -0.29, "ae": -0.35, "er": "1.28B",  "ar": "1.28B",  "fy": False},
                    {"p": "FY 2020", "ee": -0.45, "ae": -0.90, "er": "5.41B",  "ar": "5.09B",  "fy": True},
                    {"p": "Q4 2020", "ee": 0.34, "ae": 0.30, "er": "2.21B",  "ar": "2.12B",  "fy": False},
                    {"p": "Q3 2020", "ee": -0.21, "ae": -0.13, "er": "1.09B",  "ar": "1.01B",  "fy": False},
                    {"p": "Q2 2020", "ee": -0.28, "ae": -0.43, "er": "1.02B",  "ar": "942.0M", "fy": False},
                    {"p": "Q1 2020", "ee": -0.30, "ae": -0.64, "er": "1.09B",  "ar": "1.02B",  "fy": False}
                ]

                
                html_hist = "<div class='table-wrapper' style='max-height:400px; overflow-y:auto; overflow-x:auto;'><table class='hist-t'><tr><th>Period</th><th>Est EPS</th><th>Act EPS</th><th>EPS Surp</th><th>Est Rev</th><th>Act Rev</th><th>Rev Surp</th></tr>"
                
                def parse_val(v):
                    if 'B' in v: return float(v.replace('B', '')) * 1000
                    if 'M' in v: return float(v.replace('M', ''))
                    return 0.0

                for r in hist_data:
                    ee, ae = r["ee"], r["ae"]
                    er_str, ar_str = r["er"], r["ar"]
                    
                    # EPS Surprise Calculation
                    eps_surp = ((ae - ee) / abs(ee)) * 100 if ee != 0 else 0
                    eps_surp_cls = "beat" if ae >= ee else "miss"
                    eps_surp_str = f"+{eps_surp:.0f}%" if eps_surp >= 0 else f"{eps_surp:.0f}%"
                    
                    # Revenue Surprise Calculation
                    er_val, ar_val = parse_val(er_str), parse_val(ar_str)
                    rev_surp = ((ar_val - er_val) / abs(er_val)) * 100 if er_val != 0 else 0
                    rev_surp_cls = "beat" if ar_val >= er_val else "miss"
                    rev_surp_str = f"+{rev_surp:.0f}%" if rev_surp >= 0 else f"{rev_surp:.0f}%"
                    
                    # Row and Cell Formatting
                    row_cls = "fy-row" if r["fy"] else ""
                    ae_cls = "beat" if ae >= ee else "miss"
                    ar_cls = "beat" if ar_val >= er_val else "miss"
                    
                    html_hist += f"<tr class='{row_cls}'><td>{r['p']}</td><td>${ee:.2f}</td><td class='{ae_cls}'>${ae:.2f}</td><td class='{eps_surp_cls}'>{eps_surp_str}</td><td>${er_str}</td><td class='{ar_cls}'>${ar_str}</td><td class='{rev_surp_cls}'>{rev_surp_str}</td></tr>"
                    
                html_hist += "</table></div>"
                html_hist += "<p style='color:gray; font-size:11px; text-align:center; margin-top:15px; font-style:italic;'>Note: Data uses split-adjusted Non-GAAP EPS. Wall Street consensus often fails to accurately model GME's performance.</p>"
                
                st.markdown(html_est + html_hist, unsafe_allow_html=True)
                    
            with fin_t3:
                def df_to_html(df, title):
                    if df.empty: return f"<p style='color:white;'>{title} data not available.</p>"
                    cols = [str(c)[:10] for c in df.columns[:3]]
                    html = f"<div class='table-wrapper'><table class='ldb-t'><tr><th>Metric</th>"
                    for c in cols: html += f"<th>{c}</th>"
                    html += "</tr>"
                    for idx, row in df.iloc[:10, :3].iterrows():
                        html += f"<tr><td style='text-align:left; font-weight:bold; color:#00FF00;'>{idx}</td>"
                        for val in row:
                            try: html += f"<td>${float(val):,.0f}</td>"
                            except: html += f"<td>{val}</td>"
                        html += "</tr>"
                    html += "</table></div>"
                    return html

                st.markdown(df_to_html(fin, "Income Statement"), unsafe_allow_html=True)
                st.markdown(df_to_html(bs, "Balance Sheet"), unsafe_allow_html=True)

        with ph12.container():
            st.markdown("<h2 style='text-align:center; color:#00FF00; font-family:monospace;'>🕵️ INSIDER TRACKER</h2>", unsafe_allow_html=True)
            if not ins.empty:
                st.dataframe(ins.astype(str), use_container_width=True)
            else:
                st.info("No recent insider transactions detected.")

    # --- ENGINE LAUNCH (Closes the application) ---
    render_content()
