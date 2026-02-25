import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import base64
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="GME TERMINAL", page_icon="Screenshot_20260216_163106_Discord.jpg", layout="wide", initial_sidebar_state="collapsed")

# --- MANIFEST & FULLSCREEN INJECTION ---
components.html(
    """
    <script>
    const parent = window.parent.document;
    const head = parent.querySelector('head');
    if (!parent.querySelector('#pwa-manifest')) {
        head.insertAdjacentHTML('beforeend', '<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">');
        const manifest = {"name": "GME TERMINAL", "short_name": "GME", "display": "fullscreen", "background_color": "#050505", "theme_color": "#050505"};
        const blob = new Blob([JSON.stringify(manifest)], {type: 'application/json'});
        head.insertAdjacentHTML('beforeend', '<link id="pwa-manifest" rel="manifest" href="' + URL.createObjectURL(blob) + '">');
    }
    if (!parent.getElementById('btn-fs')) {
        const btn = parent.createElement('button');
        btn.id = 'btn-fs'; btn.innerText = '⛶';
        btn.style = 'position:fixed; bottom:70px; right:20px; z-index:99999; background:#050505; color:#00FF00; border:2px solid #00FF00; border-radius:10px; width:55px; height:55px; font-size:30px; box-shadow:0 0 15px #00FF00;';
        btn.onclick = function() {
            const doc = parent.documentElement;
            if (!parent.fullscreenElement) doc.requestFullscreen(); else parent.exitFullscreen();
        };
        parent.body.appendChild(btn);
    }
    </script>
    """, height=0, width=0
)

def get_b64(path):
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

# --- CSS PERFECTED ---
st.markdown("""
<style>
    body, .stApp { background-color: #050505 !important; color: white; }
    #MainMenu, footer, header {visibility: hidden;}
    @keyframes flash { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
    @keyframes rocket-pulse { 0%, 100% { transform: translateY(0px) scale(1); } 50% { transform: translateY(-15px) scale(1.1); } }
    @keyframes neon-text { 0%, 100% { color: white; text-shadow: none; } 50% { color: #00FF00; text-shadow: 0 0 15px #00FF00; } }
    @keyframes neon-img { 0%, 100% { filter: drop-shadow(0 0 0px transparent); } 50% { filter: drop-shadow(0 0 25px #00FF00); } }

    .gme-title { font-size: 70px; line-height: 1; animation: neon-text 1.5s infinite; white-space: nowrap; }
    
    @media screen and (max-width: 600px) {
        .gme-title { font-size: 38px !important; }
    }

    /* Leaderboard Styling */
    .ldb-t { width: 100%; border-collapse: collapse; color: white; font-family: monospace; }
    .ldb-t th { background: #001f3f; color: #00FF00; padding: 12px; border: 1px solid #0259c7; font-size: 14px; text-align: center; }
    .ldb-t td { background: #0f172a; padding: 12px; border: 1px solid #0259c7; text-align: center; white-space: nowrap; }
    .podium td { font-size: 20px !important; color: #00FF00 !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

if 'launched' not in st.session_state: st.session_state.launched = False
if 'show_leaderboard' not in st.session_state: st.session_state.show_leaderboard = False

# --- 2. HOME ---
if not st.session_state.launched and not st.session_state.show_leaderboard:
    wen_b64 = get_b64('Screenshot_20260216_163106_Discord.jpg')
    st.markdown(f"""
    <br><div style='display:flex; justify-content:center; align-items:center; width: 100%; margin-bottom: 40px;'>
        <div style='flex: 0 0 100px; display: flex; justify-content: center;'>
            <img src='data:image/jpeg;base64,{wen_b64}' style='height:80px; animation: neon-img 1.5s infinite;'>
        </div>
        <div style='flex: 1; text-align: center; overflow: hidden;'>
            <h1 class='gme-title'>GME&nbsp;TERMINAL</h1>
        </div>
        <div style='flex: 0 0 100px; display: flex; justify-content: center;'>
            <div style='font-size: 60px; animation: rocket-pulse 1s infinite;'>🚀</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("⚙️ PORTFOLIO CONFIGURATION & NEW PURCHASES"):
        ape_name = st.text_input("Nickname (Optional)", value="")
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🇺🇸 GME Shares")
            osq = st.number_input("Current Shares", value=0, min_value=0)
            osp = st.number_input("Avg Cost ($)", value=0.0, format="%.3f")
            nsq = st.number_input("New Shares", value=0, min_value=0)
            nsp = st.number_input("New Price ($)", value=0.0, format="%.3f")
        with col2:
            st.markdown("### 📜 Warrants")
            owq = st.number_input("Current Warrants", value=0, min_value=0)
            owp = st.number_input("Warrant Avg ($)", value=0.0, format="%.3f")
            nwq = st.number_input("New Warrants", value=0, min_value=0)
            nwp = st.number_input("New Price W ($)", value=0.0, format="%.3f")
        
        fq = osq + nsq
        fp = ((osq*osp)+(nsq*nsp))/fq if fq > 0 else 0.0
        fwq = owq + nwq
        fwp = ((owq*owp)+(nwq*nwp))/fwq if fwq > 0 else 0.0

    st.markdown("<br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown(f"<div style='text-align:center; margin-bottom: 10px;'><img src='data:image/jpeg;base64,{wen_b64}' style='height:60px; animation: neon-img 1.5s infinite;'></div>", unsafe_allow_html=True)
        if st.button("🏆Leaderboard", use_container_width=True):
            st.session_state.show_leaderboard = True
            st.rerun()

    if st.button("LAUNCH WEN MOON SYSTEM 🚀🌘!", use_container_width=True):
        st.session_state.update(ape_name=ape_name if ape_name else "Anonymous", qn=fq, pn=fp, qw=fwq, pw=fwp, gp=fp, launched=True)
        st.rerun()
    st.markdown("<h4 style='text-align: right; margin-top: 30px; font-family: monospace; animation: neon-text 1.5s infinite;'>By Mr-CRUNK-13</h4>", unsafe_allow_html=True)

# --- 2.5 LEADERBOARD SCREEN ---
elif st.session_state.get('show_leaderboard', False):
    wen_b64 = get_b64('Screenshot_20260216_163106_Discord.jpg')
    st.markdown(f"<div style='text-align:center;'><h1 style='font-size:45px; color:#00FF00; animation:neon-text 1.5s infinite;'>🏆 Leaderboard <img src='data:image/jpeg;base64,{wen_b64}' style='height:60px; vertical-align:middle; animation:neon-img 1.5s infinite;'></h1></div>", unsafe_allow_html=True)
    
    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
    with col_b2:
        if st.button("⬅️ BACK TO HOME", use_container_width=True):
            st.session_state.show_leaderboard = False
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    lb_tabs = st.tabs(["🌍 GENERAL", "📅 MONTHLY", "📆 WEEKLY"])
    
    # Récupération des prix en direct pour calculer la valeur du portefeuille
    try:
        ts = ["GME", "GME-WT"]
        data = yf.download(ts, period="1d", interval="2m", prepost=True, progress=False)['Close']
        live_p_n = float(data['GME'].dropna().iloc[-1])
        live_p_w = float(data['GME-WT'].dropna().iloc[-1])
    except:
        live_p_n, live_p_w = 24.50, 4.30

    # Données de l'utilisateur actuel
    u_name = st.session_state.get("ape_name", "Anonymous")
    u_sq = st.session_state.get("qn", 0)
    u_wq = st.session_state.get("qw", 0)
    u_spru = st.session_state.get("pn", 0.0)
    u_wpru = st.session_state.get("pw", 0.0)
    u_tv = (u_sq * live_p_n) + (u_wq * live_p_w)

    # BASE DE DONNÉES RÉELLE (Uniquement l'utilisateur pour le moment)
    real_db = [
        {"name": u_name, "tv": u_tv, "sq": u_sq, "wq": u_wq, "spru": u_spru, "wpru": u_wpru}
    ]
    
    # Tri par Valeur Totale décroissante
    real_db.sort(key=lambda x: x["tv"], reverse=True)

    for t in lb_tabs:
        with t:
            html = """
            <div style="overflow-x:auto;">
            <table class='ldb-t'>
                <tr>
                    <th>Rank</th>
                    <th>Nickname</th>
                    <th>Total Value</th>
                    <th>Shares</th>
                    <th>Warrants</th>
                    <th>Avg S</th>
                    <th>Avg W</th>
                    <th>S%</th>
                    <th>W%</th>
                </tr>
            """
            for i, r in enumerate(real_db):
                # Gestion du podium et des médailles
                rank_str = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}"
                row_class = "podium" if i < 3 else ""
                
                # Calculs des pourcentages de répartition
                t_val = r["tv"]
                s_val = r["sq"] * live_p_n
                w_val = r["wq"] * live_p_w
                s_pct = (s_val / t_val * 100) if t_val > 0 else 0
                w_pct = (w_val / t_val * 100) if t_val > 0 else 0
                
                # Affichage propre des PRU (N/A si 0)
                s_cost = f"${r['spru']:.3f}" if r['spru'] > 0 else "N/A"
                w_cost = f"${r['wpru']:.3f}" if r['wpru'] > 0 else "N/A"
                
                html += f"<tr class='{row_class}'><td>{rank_str}</td><td>{r['name']}</td><td>${r['tv']:,.2f}</td><td>{r['sq']:,}</td><td>{r['wq']:,}</td><td>{s_cost}</td><td>{w_cost}</td><td>{s_pct:.1f}%</td><td>{w_pct:.1f}%</td></tr>"
            html += "</table></div>"
            st.markdown(html, unsafe_allow_html=True)
# --- 3. TERMINAL ---
else:
    @st.cache_data(ttl=30)
    def fetch_terminal_data():
        try:
            ts = ["GME", "GME-WT"]
            data = yf.download(ts, period="1d", interval="2m", prepost=True, progress=False)['Close']
            p_n = float(data['GME'].dropna().iloc[-1])
            p_w = float(data['GME-WT'].dropna().iloc[-1])
            prev_n = float(yf.Ticker("GME").fast_info['previousClose'])
            prev_w = float(yf.Ticker("GME-WT").fast_info['previousClose'])
            return p_n, p_w, prev_n, prev_w, data['GME'], data['GME-WT']
        except: return 24.50, 4.30, 24.0, 4.0, pd.Series(), pd.Series()

    # --- CALCULS DES DONNÉES ---
    p_nsy, p_wt, pr_nsy, pr_wt, ch_gme, ch_wt = fetch_terminal_data()
    qn, pn, qw, pw, gp = st.session_state.qn, st.session_state.pn, st.session_state.qw, st.session_state.pw, st.session_state.gp

    total_shares, v_s_u, v_w_u = qn, qn * p_nsy, qw * p_wt
    t_v_u, t_c_u = v_s_u + v_w_u, (qn * gp) + (qw * pw)

    # --- COMMUNITY DATA (MONDE RÉEL - DÉPART À ZÉRO) ---
    c_s, c_w = qn, qw
    c_gp_val = gp if qn > 0 else 0.0
    c_pw_val = pw if qw > 0 else 0.0
    
    c_v_s, c_v_w = c_s * p_nsy, c_w * p_wt
    c_t_v = c_v_s + c_v_w
    c_t_c = (c_s * c_gp_val) + (c_w * c_pw_val)
    c_t_pl = c_t_v - c_t_c

    # --- INTERFACE TERMINAL ---
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 GME", "📜 WARRANTS", "🇺🇸 US", "📋 DATA", "🌕 WEN MOON US", "🗃️ WEN MOON DATA"])

    def draw_live(price, prev, chart):
        pct = ((price - prev) / prev) * 100 if prev > 0 else 0
        diff, clr = price - prev, ("#00FF00" if price >= prev else "#FF0000")
        
        # Découpe du prix au point décimal pour la symétrie
        price_str = f"{price:.2f}"
        p_int, p_dec = price_str.split('.')
        
        sz = min(100 + (abs(pct) * 10), 200)
        icn = f"<div style='animation: rocket-pulse 1s infinite;'><div style='font-size:{sz}px; animation: nuclear-neon 1.5s infinite;'>🚀</div></div>" if pct >= 0 else f"<img src='data:image/jpeg;base64,{get_b64('Screenshot_20260216_163106_Discord.jpg')}' style='height:{sz}px; animation:flash 1s infinite;'>"
        
        st.markdown(f"""
        <div style='display:flex; justify-content:center; align-items:center; gap:30px; margin-top:30px;'>
            <div style='text-align:right;'>
                <h1 style='font-size:110px; color:{clr}; text-shadow:0 0 20px {clr}; margin:0; line-height:0.9;'>${p_int}.</h1>
                <h1 style='font-size:90px; color:{clr}; text-shadow:0 0 20px {clr}; margin:0; line-height:0.9;'>{p_dec}</h1>
                <h3 style='color:{clr}; margin-top:10px;'>${diff:+.2f} {pct:+.2f}%</h3>
            </div>
            {icn}
        </div>
        """, unsafe_allow_html=True)
        
        if not chart.empty:
            fig, ax = plt.subplots(figsize=(10, 2.5), facecolor='black'); ax.set_facecolor('black')
            v = chart.dropna().values
            ax.bar(np.arange(len(v)), v - np.min(v)*0.99, bottom=np.min(v)*0.99, color=clr, width=0.8); ax.axis('off'); st.pyplot(fig)

    @st.fragment(run_every="30s")
    def render_content():
        with tab1: draw_live(p_nsy, pr_nsy, ch_gme)
        with tab2: draw_live(p_wt, pr_wt, ch_wt)
        with tab3:
            s_pl = v_s_u - (qn * gp)
            w_pl = v_w_u - (qw * pw)
            fig4 = plt.figure(figsize=(32, 18)); fig4.patch.set_facecolor("#0e1621"); gs = GridSpec(1, 3, width_ratios=[1, 2.5, 1])
            al = fig4.add_subplot(gs[0]); al.set_facecolor("#0e1621"); al.axis('off')
            al.text(0.9, 0.55, f"Qty: {qn:,} | P: ${p_nsy:.2f}", color="#00FF00" if s_pl>=0 else "#FF0000", fontsize=84, ha="right", weight="bold")
            al.text(0.9, 0.25, f"P/L: ${s_pl:+,.2f}", color="#00FF00" if s_pl>=0 else "#FF0000", fontsize=84, ha="right", weight="bold")
            ac = fig4.add_subplot(gs[1]); ac.set_facecolor("#0e1621")
            ac.pie([v_s_u if v_s_u > 0 else 1, v_w_u if v_w_u > 0 else 1], colors=["#00FF00", "#006400"], radius=1.35, wedgeprops=dict(width=0.45, edgecolor="#0e1621"))
            ac.text(0, -0.05, f"${t_v_u:,.2f}", fontsize=85, color="white", ha="center", weight="bold")
            ar = fig4.add_subplot(gs[2]); ar.set_facecolor("#0e1621"); ar.axis('off')
            ar.text(0.1, 0.55, f"Qty: {qw:,} | P: ${p_wt:.2f}", color="#00FF00" if w_pl>=0 else "#FF0000", fontsize=84, ha="left", weight="bold")
            ar.text(0.1, 0.25, f"P/L: ${w_pl:+,.2f}", color="#00FF00" if w_pl>=0 else "#FF0000", fontsize=84, ha="left", weight="bold")
            st.pyplot(fig4)
        with tab4:
            fig5, ax5 = plt.subplots(figsize=(14, 6)); fig5.patch.set_facecolor("#0f172a"); ax5.axis('off')
            rows = [["GME",f"{qn:,}",f"${gp:.2f}",f"${p_nsy:.2f}",f"${qn*gp:,.2f}",f"${v_s_u:,.2f}","P/L",f"{v_s_u/t_v_u if t_v_u>0 else 0:.1%}"],["WARRANT",f"{qw:,}",f"${pw:.3f}",f"${p_wt:.2f}",f"${qw*pw:,.2f}",f"${v_w_u:,.2f}","P/L",f"{v_w_u/t_v_u if t_v_u>0 else 0:.1%}"],["","","","","","","",""],["TOTAL", "","","",f"${t_c_u:,.2f}",f"${t_v_u:,.2f}","P/L","100%"]]
            ax5.table(cellText=rows, colLabels=["Ticker","Qty","Avg","Price","Cost","Value","P/L","%"], loc='center', cellLoc='center').scale(1, 2.5)
            st.pyplot(fig5)
        with tab5:
            c_pl_s = c_v_s - (c_s * c_gp_val)
            fig_c4 = plt.figure(figsize=(32, 18)); fig_c4.patch.set_facecolor("#0e1621"); gs_c = GridSpec(1, 3, width_ratios=[1, 2.5, 1])
            al_c = fig_c4.add_subplot(gs_c[0]); al_c.set_facecolor("#0e1621"); al_c.axis('off')
            al_c.text(0.9, 0.25, f"P/L: ${c_pl_s:+,.2f}", color="#00FF00" if c_pl_s>=0 else "#FF0000", fontsize=84, ha="right", weight="bold")
            ac_c = fig_c4.add_subplot(gs_c[1]); ac_c.set_facecolor("#0e1621")
            ac_c.pie([c_v_s if c_v_s > 0 else 1, c_v_w if c_v_w > 0 else 1], colors=["#00FF00", "#006400"], radius=1.35, wedgeprops=dict(width=0.45, edgecolor="#0e1621"))
            ac_c.text(0, -0.05, f"${c_t_v:,.2f}", fontsize=85, color="white", ha="center", weight="bold")
            st.pyplot(fig_c4)
        with tab6:
            fig_c5, ax_c5 = plt.subplots(figsize=(14, 6)); fig_c5.patch.set_facecolor("#0f172a"); ax_c5.axis('off')
            rows_c = [["GME",f"{c_s:,}",f"${c_gp_val:.2f}",f"${p_nsy:.2f}",f"${c_s*c_gp_val:,.2f}",f"${c_v_s:,.2f}","P/L",f"{c_v_s/c_t_v if c_t_v>0 else 0:.1%}"],["WARRANT",f"{c_w:,}",f"${c_pw_val:.3f}",f"${p_wt:.2f}",f"${c_w*c_pw_val:,.2f}",f"${c_v_w:,.2f}","P/L",f"{c_v_w/c_t_v if c_t_v>0 else 0:.1%}"],["","","","","","","",""],["TOTAL","","","",f"${c_t_c:,.2f}",f"${c_t_v:,.2f}","P/L","100%"]]
            ax_c5.table(cellText=rows_c, colLabels=["Ticker","Qty","Avg","Price","Cost","Value","P/L","%"], loc='center', cellLoc='center').scale(1, 2.5)
            st.pyplot(fig_c5)

    render_content()
