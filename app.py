import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import base64
from datetime import datetime

# --- 1. CONFIGURATION & STATE INIT ---
st.set_page_config(page_title="GME TERMINAL", page_icon="Screenshot_20260216_163106_Discord.jpg", layout="wide", initial_sidebar_state="collapsed")

# INITIALISATION PROPRE
if 'osq' not in st.session_state: 
    st.session_state.update(osq=0, osp=0.0, owq=0, owp=0.0, ape_name="", launched=False, show_leaderboard=False)
if 'in_nsq' not in st.session_state:
    st.session_state.update(in_nsq=0, in_nsp=0.0, in_nwq=0, in_nwp=0.0)

def get_b64(path):
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

# --- FULLSCREEN BUTTON ---
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
        btn.style = 'position:fixed; bottom:55px; right:10px; z-index:99999; background:#050505; color:#00FF00; border:2px solid #00FF00; border-radius:10px; width:35px; height:35px; font-size:20px; box-shadow:0 0 10px #00FF00; cursor:pointer; display:flex; justify-content:center; align-items:center;';
        btn.onclick = function() {
            const doc = parent.documentElement;
            if (!parent.fullscreenElement) doc.requestFullscreen(); else parent.exitFullscreen();
        };
        parent.body.appendChild(btn);
    }
    </script>
    """, height=0, width=0
)

# --- CSS (AVEC MARGE HAUT RÉDUITE) ---
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    body, .stApp { background-color: #050505 !important; color: white; }
    #MainMenu, footer, header {visibility: hidden;}
    @keyframes neon-text { 0%, 100% { color: white; text-shadow: none; } 50% { color: #00FF00; text-shadow: 0 0 15px #00FF00; } }
    @keyframes neon-img { 0%, 100% { filter: drop-shadow(0 0 0px transparent); } 50% { filter: drop-shadow(0 0 25px #00FF00); } }
    @keyframes nuclear-neon { 0%, 100% { filter: drop-shadow(0 0 5px #00FF00); transform: translateY(0px) scale(1); } 50% { filter: drop-shadow(0 0 25px #00FF00); transform: translateY(-15px) scale(1.1); } }
    @keyframes neon-flash-red { 0%, 100% { opacity: 1; filter: drop-shadow(0 0 10px #FF0000); } 50% { opacity: 0.4; filter: drop-shadow(0 0 30px #FF0000); } }
    .title-container { text-align: center; margin-bottom: 20px; margin-top: -10px; }
    .gme-title { font-size: 60px; line-height: 1.1; animation: neon-text 1.5s infinite; white-space: nowrap; margin: 0; }
    @media screen and (max-width: 600px) { .gme-title { font-size: 38px; } }
    .table-wrapper { overflow-x: auto; max-width: 100%; border-radius: 10px; border: 1px solid #0259c7; margin-top: 10px; }
    .ldb-t { width: 100%; border-collapse: collapse; color: white; font-family: monospace; text-align: center; }
    .ldb-t th { background: #001f3f; color: #00FF00; padding: 12px; border-bottom: 2px solid #0259c7; white-space: nowrap; }
    .ldb-t td { background: #0f172a; padding: 12px; border-bottom: 1px solid #0259c7; white-space: nowrap; }
    .podium td { font-size: 18px !important; color: #00FF00 !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- UPDATE LOGIC ---
def update_portfolio_logic():
    nsq, nsp = st.session_state.in_nsq, st.session_state.in_nsp
    nwq, nwp = st.session_state.in_nwq, st.session_state.in_nwp
    if nsq > 0 or nwq > 0:
        fq = st.session_state.osq + nsq
        if fq > 0: st.session_state.osp = ((st.session_state.osq * st.session_state.osp) + (nsq * nsp)) / fq
        st.session_state.osq = fq
        fwq = st.session_state.owq + nwq
        if fwq > 0: st.session_state.owp = ((st.session_state.owq * st.session_state.owp) + (nwq * nwp)) / fwq
        st.session_state.owq = fwq
        st.session_state.in_nsq, st.session_state.in_nsp = 0, 0.0
        st.session_state.in_nwq, st.session_state.in_nwp = 0, 0.0

# --- 2. HOME SCREEN ---
if not st.session_state.launched and not st.session_state.show_leaderboard:
    wen_b64 = get_b64('Screenshot_20260216_163106_Discord.jpg')
    st.markdown(f"""<div class="title-container"><img src='data:image/jpeg;base64,{wen_b64}' style='height:80px; vertical-align:middle; animation: neon-img 1.5s infinite; margin-right:10px;'><h1 class='gme-title' style='display:inline-block; vertical-align:middle;'>GME&nbsp;TERMINAL</h1><div style='display:inline-block; font-size:60px; vertical-align:middle; animation: nuclear-neon 1.5s infinite; margin-left:10px;'>🚀</div></div>""", unsafe_allow_html=True)
    with st.expander("⚙️ PORTFOLIO CONFIGURATION"):
        st.session_state.ape_name = st.text_input("Nickname (Optional)", value=st.session_state.ape_name)
        st.markdown("### 🏦 CURRENT HOLDINGS")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.osq = st.number_input("Current Shares", value=st.session_state.osq, min_value=0)
            st.session_state.osp = st.number_input("Avg Cost ($)", value=st.session_state.osp, format="%.3f")
        with col2:
            st.session_state.owq = st.number_input("Current Warrants", value=st.session_state.owq, min_value=0)
            st.session_state.owp = st.number_input("Warrant Avg ($)", value=st.session_state.owp, format="%.3f")
        st.markdown("---"); st.markdown("### 🛒 NEW PURCHASES")
        col3, col4 = st.columns(2)
        with col3: st.number_input("New Shares", min_value=0, key="in_nsq"); st.number_input("New Price ($)", format="%.3f", key="in_nsp")
        with col4: st.number_input("New Warrants", min_value=0, key="in_nwq"); st.number_input("New Price W ($)", format="%.3f", key="in_nwp")
        st.button("UPDATE PORTFOLIO", use_container_width=True, on_click=update_portfolio_logic)
    st.markdown("<br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        if st.button("🏆 LEADERBOARD", use_container_width=True): st.session_state.show_leaderboard = True; st.rerun()
    if st.button("LAUNCH WEN MOON SYSTEM 🚀🌘!", use_container_width=True): st.session_state.launched = True; st.rerun()
    st.markdown("<h4 style='text-align: right; margin-top: 30px; font-family: monospace; animation: neon-text 1.5s infinite;'>By Mr-CRUNK-13</h4>", unsafe_allow_html=True)

# --- 2.5 LEADERBOARD SCREEN ---
elif st.session_state.get('show_leaderboard', False):
    wen_b64 = get_b64('Screenshot_20260216_163106_Discord.jpg')
    st.markdown(f"<div style='text-align:center;'><h1 style='font-size:40px; color:#00FF00; animation:neon-text 1.5s infinite;'>🏆 LEADERBOARD <img src='data:image/jpeg;base64,{wen_b64}' style='height:50px; vertical-align:middle; animation:neon-img 1.5s infinite;'></h1></div>", unsafe_allow_html=True)
    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
    with col_b2:
        if st.button("⬅️ BACK TO HOME", use_container_width=True): st.session_state.show_leaderboard = False; st.rerun()
    lb_tabs = st.tabs(["🌍 GENERAL", "📅 MONTHLY", "📆 WEEKLY"])
    try:
        data = yf.download(["GME", "GME-WT"], period="1d", interval="2m", prepost=True, progress=False)['Close']
        live_p_n, live_p_w = float(data['GME'].dropna().iloc[-1]), float(data['GME-WT'].dropna().iloc[-1])
    except: live_p_n, live_p_w = 24.50, 4.30
    u_name, u_sq, u_wq = st.session_state.get("ape_name", "Anonymous"), st.session_state.get("osq", 0), st.session_state.get("owq", 0)
    u_spru, u_wpru = st.session_state.get("osp", 0.0), st.session_state.get("owp", 0.0)
    u_tv = (u_sq * live_p_n) + (u_wq * live_p_w)
    real_db = [{"name": u_name, "tv": u_tv, "sq": u_sq, "wq": u_wq, "spru": u_spru, "wpru": u_wpru}]
    for t in lb_tabs:
        with t:
            html = """<div class='table-wrapper'><table class='ldb-t'><tr><th class='col-rank'>Rank</th><th class='col-name'>Nickname</th><th class='col-val'>Total Value</th><th class='col-qty'>Shares</th><th class='col-qty'>Warrants</th><th>Avg S</th><th>Avg W</th><th>S%</th><th>W%</th></tr>"""
            for i, r in enumerate(real_db):
                rank_str = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}"
                rc, s_pct, w_pct = ("podium" if i < 3 else ""), (r["sq"]*live_p_n / r["tv"] * 100 if r["tv"] > 0 else 0), (r["wq"]*live_p_w / r["tv"] * 100 if r["tv"] > 0 else 0)
                sc, wc = (f"${r['spru']:.3f}" if r['spru']>0 else "N/A"), (f"${r['wpru']:.3f}" if r['wpru']>0 else "N/A")
                html += f"<tr class='{rc}'><td>{rank_str}</td><td>{r['name']}</td><td>${r['tv']:,.2f}</td><td>{r['sq']:,}</td><td>{r['wq']:,}</td><td>{sc}</td><td>{wc}</td><td>{s_pct:.1f}%</td><td>{w_pct:.1f}%</td></tr>"
            html += "</table></div>"; st.markdown(html, unsafe_allow_html=True)
# --- 3. TERMINAL & LIVE ENGINE ---
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

    # --- TABS ---
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["📊 GME", "📈 WARRANT", "💎 PORTFOLIO", "📋 DATA", "🌘 WEN MOON", "🗃️ WEN MOON DATA", "🏆 LEADERBOARD", "📊 WEN MOON SUMMARY"])
    
    with tab1: ph1 = st.empty()
    with tab2: ph2 = st.empty()
    with tab3: ph3 = st.empty()
    with tab4: ph4 = st.empty()
    with tab5: ph5 = st.empty()
    with tab6: ph6 = st.empty()
    with tab7: ph7 = st.empty()
    with tab8: ph8 = st.empty()

    def draw_live(price, prev, chart):
        pct = ((price - prev) / prev) * 100 if prev > 0 else 0
        diff, clr = price - prev, ("#00FF00" if price >= prev else "#FF0000")
        
        price_str = f"{price:.2f}"
        p_int, p_dec = price_str.split('.')
        
        # LOGIQUE DU P/L SANS LE $
        diff_sign = "+" if diff >= 0 else "-"
        abs_diff = abs(diff)
        
        sz = min(100 + (abs(pct) * 10), 180)
        anim_class = "nuclear-neon" if pct >= 0 else "neon-flash-red"
        icn = f"<div style='animation: {anim_class} 1.5s infinite;'><div style='font-size:{sz}px;'>🚀</div></div>" if pct >= 0 else f"<img src='data:image/jpeg;base64,{get_b64('Screenshot_20260216_163106_Discord.jpg')}' style='height:{sz}px; animation:{anim_class} 1.5s infinite;'>"
        
        st.markdown(f"""
        <div style='display:flex; justify-content:center; align-items:center; gap:20px; margin-top:30px;'>
            <div style='text-align:right; white-space:nowrap;'>
                <span style='font-size:50px; color:{clr}; text-shadow:0 0 20px {clr}; font-weight:bold; vertical-align:top;'>$</span><span style='font-size:100px; color:{clr}; text-shadow:0 0 20px {clr}; font-weight:bold;'>{p_int}.</span><span style='font-size:80px; color:{clr}; text-shadow:0 0 20px {clr}; font-weight:bold;'>{p_dec}</span>
                <h3 style='color:{clr}; margin-top:0px;'>{diff_sign}{abs_diff:.2f} {pct:+.2f}%</h3>
            </div>
            {icn}
        </div>
        """, unsafe_allow_html=True)
        
        if not chart.empty:
            fig, ax = plt.subplots(figsize=(10, 2.5), facecolor='black'); ax.set_facecolor('black')
            v = chart.dropna().values
            ax.bar(np.arange(len(v)), v - np.min(v)*0.99, bottom=np.min(v)*0.99, color=clr, width=0.8); ax.axis('off'); st.pyplot(fig); plt.close(fig)

    @st.fragment(run_every="30s")
    def render_content():
        plt.close('all') # ULTIMATE CACHE KILLER
        p_nsy, p_wt, pr_nsy, pr_wt, ch_gme, ch_wt = fetch_terminal_data()
        
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

        with ph1.container(): draw_live(p_nsy, pr_nsy, ch_gme)
        with ph2.container(): draw_live(p_wt, pr_wt, ch_wt)
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

            # CALCUL ABSOLU DU CENTRAGE HORIZONTAL
            w_deg = (pct_w / 100) * 360
            start_angle = -(w_deg / 2)

            fig4 = plt.figure(figsize=(32, 12)); fig4.patch.set_facecolor("#0f172a")
            gs = GridSpec(1, 3, width_ratios=[1.2, 1.5, 1.2])
            
            # LEFT BLOCK (SHARES -> #00FF00)
            al = fig4.add_subplot(gs[0]); al.set_facecolor("#0f172a"); al.axis('off')
            al.text(0.9, 0.85, "GameStop Shares (GME)", color="#00FF00", fontsize=50, ha="right", weight="bold")
            al.text(0.9, 0.65, f"Val: ${v_s_u:,.2f}", color="white", fontsize=45, ha="right", weight="bold")
            al.text(0.9, 0.45, f"Qty: {qn:,} | Price: ${p_nsy:.2f}", color="#00FF00", fontsize=45, ha="right", weight="bold")
            al.text(0.9, 0.25, f"Avg Cost: ${gp:.2f}", color="white", fontsize=45, ha="right", weight="bold")
            c_s_pl = "#00FF00" if s_pl >= 0 else "#FF0000"
            al.text(0.9, 0.05, f"P/L: {s_pl:+,.2f} ({s_pct_pl:+.2f}%)", color=c_s_pl, fontsize=45, ha="right", weight="bold")

            # CENTER PERFECT GIANT PIE
            ac = fig4.add_subplot(gs[1]); ac.set_facecolor("#0f172a"); ac.axis('equal')
            wedges, texts = ac.pie(
                [val_warrants, val_shares], 
                colors=["#006400", "#00FF00"], radius=2.5, # RAYON GÉANT
                wedgeprops=dict(width=0.8, edgecolor="#0f172a"), startangle=start_angle # ÉPAISSEUR AJUSTÉE
            )
            
            ac.text(0, 0.25, "Total Value:", fontsize=30, color="white", ha="center", va="center")
            ac.text(0, 0.0, f"${t_v_u:,.2f}", fontsize=55, color="white", ha="center", va="center", weight="bold")
            c_t_pl = "#00FF00" if t_pl >= 0 else "#FF0000"
            ac.text(0, -0.25, f"{t_pl:+,.2f} ({t_pct_pl:+.2f}%)", fontsize=35, color=c_t_pl, ha="center", va="center", weight="bold")

            # PERFECT ALIGNED PERCENTAGES & ARROWS (REPOUSSÉS VERS L'EXTÉRIEUR)
            ac.text(-2.8, 0, f"{pct_s:.0f}%", color="#00FF00", fontsize=45, weight="bold", ha="center", va="center")
            ac.plot([-3.0, -3.8], [0, 0], color="#00FF00", lw=6)
            
            ac.text(2.8, 0, f"{pct_w:.0f}%", color="#006400", fontsize=45, weight="bold", ha="center", va="center")
            ac.plot([3.0, 3.8], [0, 0], color="#006400", lw=6)
            ac.set_xlim(-4, 4) # LIMITE ÉLARGIE

            # RIGHT BLOCK (WARRANTS -> #006400)
            ar = fig4.add_subplot(gs[2]); ar.set_facecolor("#0f172a"); ar.axis('off')
            ar.text(0.1, 0.85, "Warrants (GME-WT)", color="#006400", fontsize=50, ha="left", weight="bold")
            ar.text(0.1, 0.65, f"Val: ${v_w_u:,.2f}", color="white", fontsize=45, ha="left", weight="bold")
            ar.text(0.1, 0.45, f"Qty: {qw:,} | Price: ${p_wt:.2f}", color="#006400", fontsize=45, ha="left", weight="bold")
            ar.text(0.1, 0.25, f"Avg Cost: ${pw:.3f}", color="white", fontsize=45, ha="left", weight="bold")
            c_w_pl = "#00FF00" if w_pl >= 0 else "#FF0000"
            ar.text(0.1, 0.05, f"P/L: {w_pl:+,.2f} ({w_pct_pl:+.2f}%)", color=c_w_pl, fontsize=45, ha="left", weight="bold")

            st.pyplot(fig4, bbox_inches='tight', pad_inches=0.1); plt.close(fig4)
        
        with ph4.container():
            html_d = f"""<div class='table-wrapper'><table class='ldb-t'>
            <tr><th>Ticker</th><th>Qty</th><th>Avg</th><th>Price</th><th>Cost</th><th>Value</th><th>P/L</th><th>%</th></tr>
            <tr><td>GME</td><td>{qn:,}</td><td>${gp:.2f}</td><td>${p_nsy:.2f}</td><td>${s_c:,.2f}</td><td>${v_s_u:,.2f}</td><td style="color:{'#00FF00' if s_pl>=0 else '#FF0000'};">${s_pl:+,.2f} ({s_pct_pl:+.2f}%)</td><td>{pct_s:.1f}%</td></tr>
            <tr><td>WARRANT</td><td>{qw:,}</td><td>${pw:.3f}</td><td>${p_wt:.2f}</td><td>${w_c:,.2f}</td><td>${v_w_u:,.2f}</td><td style="color:{'#00FF00' if w_pl>=0 else '#FF0000'};">${w_pl:+,.2f} ({w_pct_pl:+.2f}%)</td><td>{pct_w:.1f}%</td></tr>
            <tr class='podium'><td>TOTAL</td><td></td><td></td><td></td><td>${t_c_u:,.2f}</td><td>${t_v_u:,.2f}</td><td style="color:{'#00FF00' if t_pl>=0 else '#FF0000'};">${t_pl:+,.2f} ({t_pct_pl:+.2f}%)</td><td>100%</td></tr>
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

            fig_c4 = plt.figure(figsize=(32, 12)); fig_c4.patch.set_facecolor("#0f172a")
            gs_c = GridSpec(1, 3, width_ratios=[1.2, 1.5, 1.2])
            
            # LEFT COMMUNITY BLOCK (#4ade80)
            al_c = fig_c4.add_subplot(gs_c[0]); al_c.set_facecolor("#0f172a"); al_c.axis('off')
            al_c.text(0.9, 0.85, "Community Shares (GME)", color="#00FF00", fontsize=50, ha="right", weight="bold")
            al_c.text(0.9, 0.65, f"Val: ${c_v_s:,.2f}", color="white", fontsize=45, ha="right", weight="bold")
            al_c.text(0.9, 0.45, f"Qty: {c_s:,} | Price: ${p_nsy:.2f}", color="#00FF00", fontsize=45, ha="right", weight="bold")
            al_c.text(0.9, 0.25, f"Avg Cost: ${c_gp_val:.2f}", color="white", fontsize=45, ha="right", weight="bold")
            cc_s_pl = "#00FF00" if c_pl_s >= 0 else "#FF0000"
            al_c.text(0.9, 0.05, f"P/L: {c_pl_s:+,.2f} ({c_s_pct:+.2f}%)", color=cc_s_pl, fontsize=45, ha="right", weight="bold")

            # CENTER COMMUNITY GIANT PIE
            ac_c = fig_c4.add_subplot(gs_c[1]); ac_c.set_facecolor("#0f172a"); ac_c.axis('equal')
            wedges_c, texts_c = ac_c.pie(
                [cval_w, cval_s], 
                colors=["#006400", "#00FF00"], radius=2.5, # RAYON GÉANT
                wedgeprops=dict(width=0.8, edgecolor="#0f172a"), startangle=c_start_angle # ÉPAISSEUR AJUSTÉE
            )
            
            ac_c.text(0, 0.25, "WEN MOON Value:", fontsize=30, color="white", ha="center", va="center")
            ac_c.text(0, 0.0, f"${c_t_v:,.2f}", fontsize=55, color="white", ha="center", va="center", weight="bold")
            cc_t_pl = "#00FF00" if ct_pl >= 0 else "#FF0000"
            ac_c.text(0, -0.25, f"{ct_pl:+,.2f} ({ct_pct:+.2f}%)", fontsize=35, color=cc_t_pl, ha="center", va="center", weight="bold")

            # PERFECT COMMUNITY ALIGNED PERCENTAGES & ARROWS (REPOUSSÉS)
            ac_c.text(-2.8, 0, f"{cpct_s:.0f}%", color="#00FF00", fontsize=45, weight="bold", ha="center", va="center")
            ac_c.plot([-3.0, -3.8], [0, 0], color="#00FF00", lw=6)
            
            ac_c.text(2.8, 0, f"{cpct_w:.0f}%", color="#006400", fontsize=45, weight="bold", ha="center", va="center")
            ac_c.plot([3.0, 3.8], [0, 0], color="#006400", lw=6)
            ac_c.set_xlim(-4, 4)

            ar_c = fig_c4.add_subplot(gs_c[2]); ar_c.set_facecolor("#0f172a"); ar_c.axis('off')
            ar_c.text(0.1, 0.85, "Community Warrants", color="#006400", fontsize=50, ha="left", weight="bold")
            ar_c.text(0.1, 0.65, f"Val: ${c_v_w:,.2f}", color="white", fontsize=45, ha="left", weight="bold")
            ar_c.text(0.1, 0.45, f"Qty: {c_w:,} | Price: ${p_wt:.2f}", color="#006400", fontsize=45, ha="left", weight="bold")
            ar_c.text(0.1, 0.25, f"Avg Cost: ${c_pw_val:.3f}", color="white", fontsize=45, ha="left", weight="bold")
            cc_w_pl = "#00FF00" if c_pl_w >= 0 else "#FF0000"
            ar_c.text(0.1, 0.05, f"P/L: {c_pl_w:+,.2f} ({c_w_pct:+.2f}%)", color=cc_w_pl, fontsize=45, ha="left", weight="bold")

            st.pyplot(fig_c4, bbox_inches='tight', pad_inches=0.1); plt.close(fig_c4)
                
        with ph6.container():
            html_w = f"""<div class='table-wrapper'><table class='ldb-t'>
            <tr><th>Ticker</th><th>Qty</th><th>Avg</th><th>Price</th><th>Cost</th><th>Value</th><th>P/L</th><th>%</th></tr>
            <tr><td>GME</td><td>{c_s:,}</td><td>${c_gp_val:.2f}</td><td>${p_nsy:.2f}</td><td>${cs_c:,.2f}</td><td>${c_v_s:,.2f}</td><td style="color:{'#00FF00' if c_pl_s>=0 else '#FF0000'};">${c_pl_s:+,.2f} ({c_s_pct:+.2f}%)</td><td>{cpct_s:.1f}%</td></tr>
            <tr><td>WARRANT</td><td>{c_w:,}</td><td>${c_pw_val:.3f}</td><td>${p_wt:.2f}</td><td>${cw_c:,.2f}</td><td>${c_v_w:,.2f}</td><td style="color:{'#00FF00' if c_pl_w>=0 else '#FF0000'};">${c_pl_w:+,.2f} ({c_w_pct:+.2f}%)</td><td>{cpct_w:.1f}%</td></tr>
            <tr class='podium'><td>TOTAL</td><td></td><td></td><td></td><td>${c_t_c:,.2f}</td><td>${c_t_v:,.2f}</td><td style="color:{'#00FF00' if ct_pl>=0 else '#FF0000'};">${ct_pl:+,.2f} ({ct_pct:+.2f}%)</td><td>100%</td></tr>
            </table></div>"""
            st.markdown(html_w, unsafe_allow_html=True)

        with ph7.container():
            lb_tabs_term = st.tabs(["🌍 GENERAL", "📅 MONTHLY", "📆 WEEKLY"])
            u_name = st.session_state.get("ape_name", "Anonymous")
            real_db = [{"name": u_name, "tv": t_v_u, "sq": qn, "wq": qw, "spru": pn, "wpru": pw}]
            for term_t in lb_tabs_term:
                with term_t:
                    html_ldb = """<div class='table-wrapper'><table class='ldb-t'>
                        <tr><th class='col-rank'>Rank</th><th class='col-name'>Nickname</th><th class='col-val'>Total Value</th><th class='col-qty'>Shares</th><th class='col-qty'>Warrants</th><th>Avg S</th><th>Avg W</th><th>S%</th><th>W%</th></tr>"""
                    for i, r in enumerate(real_db):
                        rank_str = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}"
                        rc = "podium" if i < 3 else ""
                        s_pct = (r["sq"]*p_nsy / r["tv"] * 100) if r["tv"] > 0 else 0
                        w_pct = (r["wq"]*p_wt / r["tv"] * 100) if r["tv"] > 0 else 0
                        sc, wc = (f"${r['spru']:.3f}" if r['spru']>0 else "N/A"), (f"${r['wpru']:.3f}" if r['wpru']>0 else "N/A")
                        html_ldb += f"<tr class='{rc}'><td>{rank_str}</td><td>{r['name']}</td><td>${r['tv']:,.2f}</td><td>{r['sq']:,}</td><td>{r['wq']:,}</td><td>{sc}</td><td>{wc}</td><td>{s_pct:.1f}%</td><td>{w_pct:.1f}%</td></tr>"
                    html_ldb += "</table></div>"
                    st.markdown(html_ldb, unsafe_allow_html=True)

        with ph8.container():
            u_name = st.session_state.get("ape_name", "Anonymous")
            real_db = [{"name": u_name, "tv": t_v_u, "sq": qn, "wq": qw, "spru": pn, "wpru": pw}]
            total_holders = len(real_db)
            avg_s_per_person = c_s / total_holders if total_holders > 0 else 0
            avg_w_per_person = c_w / total_holders if total_holders > 0 else 0

            html_summary = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                @keyframes neon-text {{ 0%, 100% {{ color: white; text-shadow: none; }} 50% {{ color: #00FF00; text-shadow: 0 0 15px #00FF00; }} }}
                body {{ background-color: #050505; color: white; font-family: sans-serif; margin: 0; padding: 0; }}
                .summary-container {{ background-color: #0f172a; padding: 20px; border-radius: 10px; border: 1px solid #0259c7; }}
                .summary-title {{ text-align: center; color: #00FF00; margin-bottom: 30px; animation: neon-text 1.5s infinite; font-size: 32px; }}
                .total-holders {{ text-align: center; margin-bottom: 30px; }}
                .total-holders h3 {{ color: #66c2a5; margin: 0; font-size: 24px; }}
                .total-holders p {{ font-size: 48px; color: white; font-weight: bold; margin: 10px 0 0 0; }}
                .stats-grid {{ display: flex; justify-content: space-around; flex-wrap: wrap; margin-bottom: 30px; gap: 20px; }}
                .stat-box {{ background-color: #001f3f; padding: 20px; border-radius: 8px; border: 1px solid #0259c7; flex: 1 1 300px; text-align: center; }}
                .stat-box h4 {{ margin-top: 0; font-size: 22px; }}
                .stat-box p {{ margin: 10px 0; font-size: 18px; }}
                .stat-box strong {{ font-size: 24px; }}
                .recent-title {{ text-align: center; color: #66c2a5; margin-bottom: 20px; font-size: 24px; }}
                table {{ width: 100%; border-collapse: collapse; font-family: monospace; text-align: center; }}
                th {{ background: #001f3f; color: #00FF00; padding: 12px; border-bottom: 2px solid #0259c7; white-space: nowrap; }}
                td {{ background: #0f172a; padding: 12px; border-bottom: 1px solid #0259c7; white-space: nowrap; }}
            </style>
            </head>
            <body>
            <div class="summary-container">
                <h2 class="summary-title">🌍 WEN MOON COMMUNITY SUMMARY</h2>
                <div class="total-holders">
                    <h3>TOTAL HOLDERS</h3>
                    <p>{total_holders:,}</p>
                </div>
                <div class="stats-grid">
                    <div class="stat-box">
                        <h4 style="color: #00FF00;">GME SHARES</h4>
                        <p>Total Shares: <strong style="color: white;">{c_s:,}</strong></p>
                        <p>Avg Purchase Price: <strong style="color: white;">${c_gp_val:.2f}</strong></p>
                        <p>Avg Shares / Person: <strong style="color: white;">{avg_s_per_person:,.0f}</strong></p>
                    </div>
                    <div class="stat-box">
                        <h4 style="color: #006400;">GME WARRANTS</h4>
                        <p>Total Warrants: <strong style="color: white;">{c_w:,}</strong></p>
                        <p>Avg Purchase Price: <strong style="color: white;">${c_pw_val:.3f}</strong></p>
                        <p>Avg Warrants / Person: <strong style="color: white;">{avg_w_per_person:,.0f}</strong></p>
                    </div>
                </div>
                <h3 class="recent-title">📅 RECENT ACTIVITY (COMMUNITY)</h3>
                <div style="overflow-x: auto;">
                    <table>
                        <tr><th>Asset</th><th>Bought (Last 7 Days)</th><th>Bought (Last 30 Days)</th></tr>
                        <tr><td style="color: #00FF00; font-weight: bold;">GME SHARES</td><td>0</td><td>0</td></tr>
                        <tr><td style="color: #006400; font-weight: bold;">GME WARRANTS</td><td>0</td><td>0</td></tr>
                    </table>
                </div>
            </div>
            </body>
            </html>
            """
            components.html(html_summary, height=900, scrolling=True)

    render_content()
