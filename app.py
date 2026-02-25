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

# --- MANIFEST INJECTION & FLOATING FULLSCREEN BUTTON ---
components.html(
    """
    <script>
    const parent = window.parent.document;
    const head = parent.querySelector('head');
    
    if (!parent.querySelector('#pwa-manifest')) {
        head.insertAdjacentHTML('beforeend', '<meta name="apple-mobile-web-app-capable" content="yes">');
        head.insertAdjacentHTML('beforeend', '<meta name="mobile-web-app-capable" content="yes">');
        head.insertAdjacentHTML('beforeend', '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">');
        const manifest = {
            "name": "GME TERMINAL", "short_name": "GME",
            "start_url": window.parent.location.href,
            "display": "fullscreen",
            "background_color": "#050505", "theme_color": "#050505"
        };
        const blob = new Blob([JSON.stringify(manifest)], {type: 'application/json'});
        head.insertAdjacentHTML('beforeend', '<link id="pwa-manifest" rel="manifest" href="' + URL.createObjectURL(blob) + '">');
    }

    const handleFsChange = () => {
        if (parent.fullscreenElement || parent.webkitFullscreenElement || parent.msFullscreenElement) {
            parent.body.classList.add('is-fullscreen');
        } else {
            parent.body.classList.remove('is-fullscreen');
        }
    };
    parent.addEventListener('fullscreenchange', handleFsChange);
    parent.addEventListener('webkitfullscreenchange', handleFsChange);
    parent.addEventListener('msfullscreenchange', handleFsChange);

    if (!parent.getElementById('btn-fullscreen')) {
        const btn = parent.createElement('button');
        btn.id = 'btn-fullscreen';
        btn.innerText = '⛶';
        btn.style.position = 'fixed';
        btn.style.bottom = '70px';
        btn.style.right = '20px';
        btn.style.zIndex = '99999';
        btn.style.background = '#050505';
        btn.style.color = '#00FF00';
        btn.style.border = '2px solid #00FF00';
        btn.style.borderRadius = '10px';
        btn.style.width = '55px';
        btn.style.height = '55px';
        btn.style.fontSize = '30px';
        btn.style.cursor = 'pointer';
        btn.style.boxShadow = '0 0 15px #00FF00';
        
        btn.onclick = function() {
            const docEl = parent.documentElement;
            if (!parent.fullscreenElement && !parent.webkitFullscreenElement) {
                if (docEl.requestFullscreen) docEl.requestFullscreen();
                else if (docEl.webkitRequestFullscreen) docEl.webkitRequestFullscreen();
                else if (docEl.msRequestFullscreen) docEl.msRequestFullscreen();
                parent.body.classList.add('is-fullscreen');
            } else {
                if (parent.exitFullscreen) parent.exitFullscreen();
                else if (parent.webkitExitFullscreen) parent.webkitExitFullscreen();
                else if (parent.msExitFullscreen) parent.msExitFullscreen();
                parent.body.classList.remove('is-fullscreen');
            }
        };
        parent.body.appendChild(btn);
    }
    </script>
    """,
    height=0,
    width=0,
)

def get_b64(path):
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

st.markdown("""
<style>
    body, .stApp { background-color: #050505 !important; color: white; }
    #MainMenu, footer, header {visibility: hidden;}
    @keyframes flash { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(1.05); box-shadow: 0 0 30px #FF0000; } 100% { opacity: 1; transform: scale(1); } }
    @keyframes rocket-pulse { 0% { transform: translateY(0px) scale(1); } 50% { transform: translateY(-20px) scale(1.15); } 100% { transform: translateY(0px) scale(1); } }
    @keyframes neon-text { 0%, 100% { color: white; text-shadow: none; } 50% { color: #00FF00; text-shadow: 0 0 15px #00FF00, 0 0 45px #00FF00, 0 0 90px #00FF00; } }
    @keyframes nuclear-neon { 0%, 100% { filter: drop-shadow(0 0 0 transparent); } 50% { filter: drop-shadow(0 0 20px #00FF00) drop-shadow(0 0 60px #00FF00) drop-shadow(0 0 150px #00FF00); } }
    @keyframes nuclear-red-img { 0%, 100% { filter: drop-shadow(0 0 0 transparent); } 50% { filter: drop-shadow(0 0 20px #FF0000) drop-shadow(0 0 70px #FF0000) drop-shadow(0 0 150px #FF0000); } }
    @keyframes neon-img { 0%, 100% { filter: drop-shadow(0 0 0px transparent); } 50% { filter: drop-shadow(0 0 25px #00FF00); } }

    .mobile-break { display: none; }
    .desktop-space { display: inline; }

    body.is-fullscreen #btn-fullscreen {
        bottom: 20px !important;
        left: 20px !important;
        right: auto !important;
        width: 38px !important;
        height: 38px !important;
        font-size: 21px !important;
        border-radius: 8px !important;
    }

    @media screen and (orientation: portrait) {
        body.is-fullscreen .gme-title {
            font-size: 35px !important;
            white-space: normal !important;
            padding-top: 0px !important; 
            line-height: 1.1 !important;
        }
        body.is-fullscreen .desktop-space { display: none !important; }
        body.is-fullscreen .mobile-break { display: none !important; }
        
        body.is-fullscreen .terminal-word::after {
            content: "" !important;
            display: block !important; 
            height: 30px !important;   
        }
        
        body.is-fullscreen .main .block-container,
        body.is-fullscreen [data-testid="stAppViewBlockContainer"] {
            padding-top: 0px !important; 
            padding-bottom: 0px !important; 
            margin-top: -80px !important; 
        }
        body.is-fullscreen div[style*='margin-bottom: 40px'] {
            margin-bottom: 10px !important; 
        }
        body.is-fullscreen h4 {
            margin-top: 0px !important; 
        }
    }
</style>
""", unsafe_allow_html=True)

if 'launched' not in st.session_state:
    st.session_state.launched = False
if 'show_leaderboard' not in st.session_state:
    st.session_state.show_leaderboard = False

# --- 2. HOME ---
if not st.session_state.launched and not st.session_state.show_leaderboard:
    wen_b64 = get_b64('Screenshot_20260216_163106_Discord.jpg')
    st.markdown(f"""
    <br>
    <div style='display:flex; justify-content:center; align-items:center; width: 100%; margin-bottom: 40px;'>
        <div style='flex: 0 0 180px; display: flex; justify-content: center; align-items: center;'>
            <img src='data:image/jpeg;base64,{wen_b64}' style='height:130px; animation: neon-img 1.5s infinite;'>
        </div>
        <div style='flex: 1; text-align: center; white-space: nowrap; padding: 0 10px; display: flex; justify-content: center; align-items: center;'>
            <h1 class='gme-title' style='font-size: 70px; margin: 0; line-height: 1; padding-top: 25px; animation: neon-text 1.5s infinite;'><span class='terminal-word'>GME</span><span class='desktop-space'> </span><br class='mobile-break'>TERMINAL</h1>
        </div>
        <div style='flex: 0 0 180px; display: flex; justify-content: center; align-items: center;'>
            <div style='animation: rocket-pulse 1s ease-in-out infinite;'>
                <div style='font-size: 90px; animation: nuclear-neon 1.5s infinite;'>🚀</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("⚙️ PORTFOLIO CONFIGURATION & NEW PURCHASES"):
        st.markdown("### 🦍 IDENTITY")
        ape_name = st.text_input("Nickname (Optional - Leave blank for anonymous)", value="")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🇺🇸 Existing GME Shares")
            old_s_q = st.number_input("Current Shares Quantity", value=0, min_value=0)
            old_s_p = st.number_input("Current Avg Cost ($)", value=0.0, format="%.3f", min_value=0.0)
            
            st.markdown("#### ➕ New Shares Purchase")
            new_s_q = st.number_input("New Shares Quantity", value=0, min_value=0)
            new_s_p = st.number_input("New Shares Price ($)", value=0.0, format="%.3f", min_value=0.0)
            
        with col2:
            st.markdown("### 📜 Existing Warrants GME-WT")
            old_w_q = st.number_input("Current Warrants Quantity", value=0, min_value=0)
            old_w_p = st.number_input("Current Warrants Avg Cost ($)", value=0.0, format="%.3f", min_value=0.0)
            
            st.markdown("#### ➕ New Warrants Purchase")
            new_w_q = st.number_input("New Warrants Quantity", value=0, min_value=0)
            new_w_p = st.number_input("New Warrants Price ($)", value=0.0, format="%.3f", min_value=0.0)
            
        final_s_q = old_s_q + new_s_q
        final_s_p = ((old_s_q * old_s_p) + (new_s_q * new_s_p)) / final_s_q if final_s_q > 0 else 0.0
        
        final_w_q = old_w_q + new_w_q
        final_w_p = ((old_w_q * old_w_p) + (new_w_q * new_w_p)) / final_w_q if final_w_q > 0 else 0.0

        st.markdown("---")
        st.markdown("### ⚓ Global Portfolio Settings")
        g_p = st.number_input("Global Avg Cost (If different from Shares Avg) ($)", value=final_s_p, format="%.3f", min_value=0.0)

    st.markdown("<br>", unsafe_allow_html=True)

    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown(f"<div style='text-align:center; margin-bottom: 10px;'><img src='data:image/jpeg;base64,{wen_b64}' style='height:60px; filter: drop-shadow(0 0 10px #00FF00); animation: neon-img 1.5s infinite;'></div>", unsafe_allow_html=True)
        if st.button("🏆Leaderboard", use_container_width=True):
            st.session_state.show_leaderboard = True
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("LAUNCH WEN MOON SYSTEM 🚀🌘!", use_container_width=True):
        st.session_state.update(
            ape_name=ape_name if ape_name else "Anonymous", 
            qn=final_s_q, 
            pn=final_s_p, 
            qw=final_w_q, 
            pw=final_w_p, 
            gp=g_p, 
            launched=True
        )
        st.rerun()
    st.markdown("<h4 style='text-align: right; margin-top: 30px; font-family: monospace; animation: neon-text 1.5s infinite;'>By Mr-CRUNK-13</h4>", unsafe_allow_html=True)

# --- 2.5 LEADERBOARD SCREEN ---
elif st.session_state.get('show_leaderboard', False):
    wen_b64 = get_b64('Screenshot_20260216_163106_Discord.jpg')
    st.markdown(f"""
    <div style='text-align: center; padding: 20px;'>
        <h1 style='font-size: 60px; color: #00FF00; animation: neon-text 1.5s infinite; margin: 0;'>
            🏆Leaderboard <img src='data:image/jpeg;base64,{wen_b64}' style='height:80px; vertical-align: middle; animation: neon-img 1.5s infinite;'>
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
    with col_b2:
        if st.button("⬅️ BACK TO HOME", use_container_width=True):
            st.session_state.show_leaderboard = False
            st.rerun()
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    lb_tab1, lb_tab2, lb_tab3 = st.tabs(["🌍 GENERAL RANKING", "📅 MONTHLY RANKING", "📆 WEEKLY RANKING"])
    
    try:
        ts = ["GME", "GME-WT"]
        data = yf.download(ts, period="1d", interval="2m", prepost=True, progress=False)['Close']
        live_p_n = float(data['GME'].dropna().iloc[-1])
        live_p_w = float(data['GME-WT'].dropna().iloc[-1])
    except:
        live_p_n, live_p_w = 24.50, 4.30

    u_name = st.session_state.get("ape_name", "Anonymous")
    u_sq = st.session_state.get("qn", 0)
    u_wq = st.session_state.get("qw", 0)
    u_spru = st.session_state.get("pn", 0.0)
    u_wpru = st.session_state.get("pw", 0.0)
    u_tv = (u_sq * live_p_n) + (u_wq * live_p_w)

    mock_db = [
        {"name": u_name, "tv": u_tv, "sq": u_sq, "wq": u_wq, "spru": u_spru, "wpru": u_wpru},
        {"name": "RoaringKitty", "tv": 245000000, "sq": 10000000, "wq": 0, "spru": 21.0, "wpru": 0},
        {"name": "RyanCohen", "tv": 882000000, "sq": 36000000, "wq": 0, "spru": 15.0, "wpru": 0},
        {"name": "DiamondHands99", "tv": 155000, "sq": 5000, "wq": 7500, "spru": 25.5, "wpru": 4.1},
        {"name": "ApeStrong", "tv": 45000, "sq": 1500, "wq": 2000, "spru": 30.0, "wpru": 5.0}
    ]
    mock_db.sort(key=lambda x: x["tv"], reverse=True)
    
    def render_leaderboard_table(data):
        html = """
        <style>
            .ldb-table { width: 100%; border-collapse: collapse; color: white; text-align: center; font-family: monospace; }
            .ldb-table th { background-color: #001f3f; color: #00FF00; padding: 15px; border: 2px solid #0f172a; font-size: 16px; }
            .ldb-table td { background-color: #0f172a; padding: 15px; border: 2px solid #0259c7; }
            .top-row { font-size: 150%; font-weight: bold; color: #00FF00; background-color: #0a1128 !important; }
            .normal-row { font-size: 100%; }
        </style>
        <table class="ldb-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Nickname</th>
                    <th>Total Value ($)</th>
                    <th>Shares Qty</th>
                    <th>Warrants Qty</th>
                    <th>Share Avg Cost ($)</th>
                    <th>Warrant Avg Cost ($)</th>
                    <th>Shares % (Value)</th>
                    <th>Warrants % (Value)</th>
                </tr>
            </thead>
            <tbody>
        """
        for i, row in enumerate(data):
            row_class = "top-row" if i < 3 else "normal-row"
            if i == 0: rank_str = "🥇"
            elif i == 1: rank_str = "🥈"
            elif i == 2: rank_str = "🥉"
            else: rank_str = f"{i+1}"
            
            total_val = row["tv"]
            s_val = row["sq"] * live_p_n
            w_val = row["wq"] * live_p_w
            s_pct = (s_val / total_val * 100) if total_val > 0 else 0
            w_pct = (w_val / total_val * 100) if total_val > 0 else 0
            
            s_cost_disp = f"${row['spru']:.3f}" if row['spru'] > 0 else "N/A"
            w_cost_disp = f"${row['wpru']:.3f}" if row['wpru'] > 0 else "N/A"
            
            html += f"""
                <tr class="{row_class}">
                    <td>{rank_str}</td>
                    <td>{row['name']}</td>
                    <td>${row['tv']:,.2f}</td>
                    <td>{row['sq']:,}</td>
                    <td>{row['wq']:,}</td>
                    <td>{s_cost_disp}</td>
                    <td>{w_cost_disp}</td>
                    <td>{s_pct:.1f}%</td>
                    <td>{w_pct:.1f}%</td>
                </tr>
            """
        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)

    with lb_tab1: render_leaderboard_table(mock_db)
    with lb_tab2: render_leaderboard_table(mock_db)
    with lb_tab3: render_leaderboard_table(mock_db)

# --- 3. TERMINAL ---
else:
    # Le cache est maintenant réglé sur 15 secondes pour suivre le rythme du pilote automatique
    @st.cache_data(ttl=15)
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

    # Création de la bulle d'actualisation silencieuse (Fragment)
    @st.fragment(run_every="15s")
    def live_terminal_fragment():
        p_nsy, p_wt, pr_nsy, pr_wt, ch_gme, ch_wt = fetch_terminal_data()
        
        qn = st.session_state.qn
        pn = st.session_state.pn
        qw = st.session_state.qw
        pw = st.session_state.pw
        gp = st.session_state.gp

        # --- PERSONAL DATA ---
        total_shares = qn
        v_s_u = total_shares * p_nsy
        v_w_u = qw * p_wt
        
        t_c_u = (total_shares * gp) + (qw * pw)
        t_v_u = v_s_u + v_w_u

        # --- COMMUNITY DATA (MOCK DB) & ZERO-COST SHIELD ---
        db_total_shares = 741000 
        db_qw = 150000
        db_gp = 22.50
        db_pw = 3.10
        
        c_total_shares = db_total_shares + total_shares
        c_qw = db_qw + qw
        
        c_shares_cost_pool = (db_total_shares * db_gp) + (total_shares * gp if gp > 0 else 0)
        c_shares_qty_pool = db_total_shares + (total_shares if gp > 0 else 0)
        c_gp = c_shares_cost_pool / c_shares_qty_pool if c_shares_qty_pool > 0 else 0
        
        c_wt_cost_pool = (db_qw * db_pw) + (qw * pw if pw > 0 else 0)
        c_wt_qty_pool = db_qw + (qw if pw > 0 else 0)
        c_pw = c_wt_cost_pool / c_wt_qty_pool if c_wt_qty_pool > 0 else 0
        
        c_v_s_u = c_total_shares * p_nsy
        c_v_w_u = c_qw * p_wt
        c_t_v_u = c_v_s_u + c_v_w_u
        c_t_c_u = (c_total_shares * c_gp) + (c_qw * c_pw)
        c_t_pl_u = c_t_v_u - c_t_c_u

        # --- TABS CREATION ---
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 GME", "📜 WARRANTS", "🇺🇸 US", "📋 DATA", "🌕 WEN MOON US", "🗃️ WEN MOON DATA"])

        def draw_live(price, prev, chart):
            pct = ((price - prev) / prev) * 100
            diff = price - prev
            clr = "#00FF00" if pct >= 0 else "#FF0000"
            sz = min(100 + (abs(pct) * 10), 200)
            
            if pct >= 0:
                icn = f"<div style='animation: rocket-pulse 1s ease-in-out infinite;'><div style='font-size:{sz}px; animation: nuclear-neon 1.5s infinite;'>🚀</div></div>"
            else:
                icn = f"<img src='data:image/jpeg;base64,{get_b64('Screenshot_20260216_163106_Discord.jpg')}' style='height:{sz}px; animation:flash 1s infinite, nuclear-red-img 1.5s infinite;'>"
                
            st.markdown(f"<div style='display:flex; justify-content:center; align-items:center; gap:40px; margin-top:30px;'><div style='text-align:right;'><h1 style='font-size:100px; color:{clr}; text-shadow:0 0 20px {clr}; margin:0;'>${price:.2f}</h1><h3 style='color:{clr}; margin:0;'>${diff:+.2f} {pct:+.2f}%</h3></div>{icn}</div>", unsafe_allow_html=True)
            if not chart.empty:
                fig, ax = plt.subplots(figsize=(10, 2.5), facecolor='black'); ax.set_facecolor('black')
                v = chart.dropna().values
                ax.bar(np.arange(len(v)), v - np.min(v)*0.99, bottom=np.min(v)*0.99, color=clr, width=0.8); ax.axis('off'); st.pyplot(fig)

        with tab1: draw_live(p_nsy, pr_nsy, ch_gme)
        with tab2: draw_live(p_wt, pr_wt, ch_wt)

        # --- TAB 3: PERSONAL US PIE CHART ---
        with tab3:
            s_cost_txt = f"${gp:.2f}" if gp > 0 else "N/A"
            s_pl = v_s_u - (total_shares * gp)
            s_pl_txt = f"${s_pl:+,.2f} ({s_pl/(total_shares*gp):+.2%})" if gp > 0 and total_shares > 0 else "N/A"
            s_pl_clr = ("#00FF00" if s_pl >= 0 else "#FF0000") if gp > 0 and total_shares > 0 else "white"

            w_cost_txt = f"${pw:.3f}" if pw > 0 else "N/A"
            w_pl = v_w_u - (qw * pw)
            w_pl_txt = f"${w_pl:+,.2f} ({w_pl/(qw*pw):+.2%})" if pw > 0 and qw > 0 else "N/A"
            w_pl_clr = ("#00FF00" if w_pl >= 0 else "#FF0000") if pw > 0 and qw > 0 else "white"
            
            t_cost_txt = f"${t_c_u:,.2f}" if t_c_u > 0 else "N/A"
            t_pl = t_v_u - t_c_u
            t_pl_txt = f"${t_pl:+,.2f} ({t_pl/t_c_u:+.2%})" if t_c_u > 0 else "N/A"
            t_pl_clr = ("#00FF00" if t_pl >= 0 else "#FF0000") if t_c_u > 0 else "white"

            fig4 = plt.figure(figsize=(32, 18)); fig4.patch.set_facecolor("#0e1621"); gs = GridSpec(1, 3, width_ratios=[1, 2.5, 1])
            plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
            
            al = fig4.add_subplot(gs[0]); al.set_facecolor("#0e1621"); al.axis('off')
            al.text(0.9, 0.85, "GameStop Shares (GME)", color="#00FF00", fontsize=84, ha="right", weight="bold")
            al.text(0.9, 0.70, f"Val: ${v_s_u:,.2f}", color="white", fontsize=63, ha="right", weight="bold")
            al.text(0.9, 0.55, f"Qty: {total_shares:,} | Price: ${p_nsy:.2f}", color=s_pl_clr, fontsize=84, ha="right", weight="bold")
            al.text(0.9, 0.40, f"Avg Cost: {s_cost_txt}", color="white", fontsize=63, ha="right", weight="bold")
            al.text(0.9, 0.25, f"P/L: {s_pl_txt}", color=s_pl_clr, fontsize=84, ha="right", weight="bold")
            al.annotate("", xy=(0.95, 0.5), xytext=(1.28, 0.5), arrowprops=dict(arrowstyle="->", color=s_pl_clr, lw=20))
            
            ac = fig4.add_subplot(gs[1]); ac.set_facecolor("#0e1621")
            ac.pie([v_s_u if v_s_u > 0 else 1, v_w_u if v_w_u > 0 else 1], colors=["#00FF00", "#006400"], radius=1.35, wedgeprops=dict(width=0.45, edgecolor="#0e1621"), startangle=21.6)
            ac.text(-1.1, 0, f"{(v_s_u/t_v_u)*100 if t_v_u > 0 else 0:.0f}%", fontsize=75, color="black", ha="center", weight="bold")
            ac.text(1.1, 0, f"{(v_w_u/t_v_u)*100 if t_v_u > 0 else 0:.0f}%", fontsize=75, color="black", ha="center", weight="bold")
            ac.text(0, 0.15, "Total Value:", fontsize=45, color="white", ha="center", weight="bold")
            ac.text(0, -0.05, f"${t_v_u:,.2f}", fontsize=85, color="white", ha="center", weight="bold")
            ac.text(0, -0.25, t_pl_txt, fontsize=48, color=t_pl_clr, ha="center", weight="bold")
            
            ar = fig4.add_subplot(gs[2]); ar.set_facecolor("#0e1621"); ar.axis('off')
            ar.text(0.1, 0.85, "Warrants (GME-WT)", color="#006400", fontsize=84, ha="left", weight="bold")
            ar.text(0.1, 0.70, f"Val: ${v_w_u:,.2f}", color="white", fontsize=63, ha="left", weight="bold")
            ar.text(0.1, 0.55, f"Qty: {qw:,} | Price: ${p_wt:.2f}", color=w_pl_clr, fontsize=84, ha="left", weight="bold")
            ar.text(0.1, 0.40, f"Avg Cost: {w_cost_txt}", color="white", fontsize=63, ha="left", weight="bold")
            ar.text(0.1, 0.25, f"P/L: {w_pl_txt}", color=w_pl_clr, fontsize=84, ha="left", weight="bold")
            ar.annotate("", xy=(0.08, 0.5), xytext=(-0.19, 0.5), arrowprops=dict(arrowstyle="->", color="#006400", lw=20))
            st.pyplot(fig4)

        # --- TAB 4: PERSONAL DATA TABLE ---
        with tab4:
            fig5, ax5 = plt.subplots(figsize=(14, 6)); fig5.patch.set_facecolor("#0f172a"); ax5.axis('off')
            def f5(v, qty, cost):
                if cost <= 0 or qty <= 0: return "N/A"
                s = "+" if v-(qty*cost)>=0 else "-"
                p = ((v-(qty*cost))/(qty*cost))*100
                return f"{s}${abs(v-(qty*cost)):,.2f} ({s}{abs(p):.2f}%)"
                
            r_s_cost = f"${gp:.2f}" if gp > 0 else "N/A"
            r_w_cost = f"${pw:.3f}" if pw > 0 else "N/A"
            r_s_tot = f"${total_shares*gp:,.2f}" if gp > 0 else "N/A"
            r_w_tot = f"${qw*pw:,.2f}" if pw > 0 else "N/A"
            
            rows = [
                ["GME TOTAL", f"{total_shares:,}", r_s_cost, f"${p_nsy:.2f}", r_s_tot, f"${v_s_u:,.2f}", f5(v_s_u, total_shares, gp), f"{v_s_u/t_v_u if t_v_u > 0 else 0:.1%}"],
                ["WARRANTS", f"{qw:,}", r_w_cost, f"${p_wt:.2f}", r_w_tot, f"${v_w_u:,.2f}", f5(v_w_u, qw, pw), f"{v_w_u/t_v_u if t_v_u > 0 else 0:.1%}"],
                ["","","","","","","",""],
                ["TOTAL PORTFOLIO","","","", t_cost_txt, f"${t_v_u:,.2f}", t_pl_txt, "100%"]
            ]
            cw = [0.18, 0.07, 0.09, 0.09, 0.11, 0.14, 0.23, 0.09]
            table = ax5.table(cellText=rows, colLabels=["Ticker","Qty","Avg. Cost","Price","Total Cost","Market Value","Latent P/L","Portfolio %"], loc='center', cellLoc='center', colWidths=cw)
            table.auto_set_font_size(False); table.set_fontsize(12); table.scale(1, 2.5)
            for (r, c), cell in table.get_celld().items():
                if r == 0: cell.set_facecolor("#001f3f"); cell.get_text().set_color("#00FF00"); cell.get_text().set_fontweight('bold')
                elif r in [1, 2, 4]:
                    if r == 4 and c not in [0, 4, 5, 6]: cell.set_facecolor("#0f172a"); cell.set_edgecolor("#0f172a"); continue
                    cell.set_facecolor("#0259c7"); cell.get_text().set_color("white"); cell.get_text().set_fontweight('bold')
                    if c in [1, 3, 5]: cell.get_text().set_color("#00FF00"); cell.get_text().set_fontsize(14)
                    elif c == 6: 
                        txt_val = cell.get_text().get_text()
                        if txt_val == "N/A": cell.get_text().set_color("white")
                        else: cell.get_text().set_color("#00FF00" if "+" in txt_val else "#ef4444")
                        cell.get_text().set_fontsize(14)
                else: cell.set_facecolor("#0f172a"); cell.set_edgecolor("#0f172a")
            st.pyplot(fig5)

        # --- TAB 5: WEN MOON US PIE CHART ---
        with tab5:
            c_pl_s_u, c_pl_w_u = c_v_s_u - (c_total_shares * c_gp), c_v_w_u - (c_qw * c_pw)
            fig_c4 = plt.figure(figsize=(32, 18)); fig_c4.patch.set_facecolor("#0e1621"); gs_c = GridSpec(1, 3, width_ratios=[1, 2.5, 1])
            plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
            
            al_c = fig_c4.add_subplot(gs_c[0]); al_c.set_facecolor("#0e1621"); al_c.axis('off')
            al_c.text(0.9, 0.85, "WEN MOON GME Shares", color="#00FF00", fontsize=84, ha="right", weight="bold")
            al_c.text(0.9, 0.70, f"Val: ${c_v_s_u:,.2f}", color="white", fontsize=63, ha="right", weight="bold")
            al_c.text(0.9, 0.55, f"Qty: {c_total_shares:,} | Price: ${p_nsy:.2f}", color="#00FF00" if c_pl_s_u>=0 else "#FF0000", fontsize=84, ha="right", weight="bold")
            al_c.text(0.9, 0.40, f"Avg Cost: ${c_gp:.2f}", color="white", fontsize=63, ha="right", weight="bold")
            al_c.text(0.9, 0.25, f"P/L: ${c_pl_s_u:+,.2f} ({c_pl_s_u/(c_total_shares*c_gp) if c_total_shares > 0 else 0:+.2%})", color="#00FF00" if c_pl_s_u>=0 else "#FF0000", fontsize=84, ha="right", weight="bold")
            al_c.annotate("", xy=(0.95, 0.5), xytext=(1.28, 0.5), arrowprops=dict(arrowstyle="->", color="#00FF00" if c_pl_s_u>=0 else "#FF0000", lw=20))
            
            ac_c = fig_c4.add_subplot(gs_c[1]); ac_c.set_facecolor("#0e1621")
            ac_c.pie([c_v_s_u if c_v_s_u > 0 else 1, c_v_w_u if c_v_w_u > 0 else 1], colors=["#00FF00", "#006400"], radius=1.35, wedgeprops=dict(width=0.45, edgecolor="#0e1621"), startangle=21.6)
            ac_c.text(-1.1, 0, f"{(c_v_s_u/c_t_v_u)*100 if c_t_v_u > 0 else 0:.0f}%", fontsize=75, color="black", ha="center", weight="bold")
            ac_c.text(1.1, 0, f"{(c_v_w_u/c_t_v_u)*100 if c_t_v_u > 0 else 0:.0f}%", fontsize=75, color="black", ha="center", weight="bold")
            ac_c.text(0, 0.15, "WEN MOON Total Value:", fontsize=45, color="white", ha="center", weight="bold")
            ac_c.text(0, -0.05, f"${c_t_v_u:,.2f}", fontsize=85, color="white", ha="center", weight="bold")
            ac_c.text(0, -0.25, f"${c_t_pl_u:+,.2f} ({c_t_pl_u/c_t_c_u if c_t_c_u > 0 else 0:+.2%})", fontsize=48, color="#00FF00" if c_t_pl_u>=0 else "#FF0000", ha="center", weight="bold")
            
            ar_c = fig_c4.add_subplot(gs_c[2]); ar_c.set_facecolor("#0e1621"); ar_c.axis('off')
            ar_c.text(0.1, 0.85, "WEN MOON Warrants", color="#006400", fontsize=84, ha="left", weight="bold")
            ar_c.text(0.1, 0.70, f"Val: ${c_v_w_u:,.2f}", color="white", fontsize=63, ha="left", weight="bold")
            ar_c.text(0.1, 0.55, f"Qty: {c_qw:,} | Price: ${p_wt:.2f}", color="#00FF00" if c_pl_w_u>=0 else "#FF0000", fontsize=84, ha="left", weight="bold")
            ar_c.text(0.1, 0.40, f"Avg Cost: ${c_pw:.3f}", color="white", fontsize=63, ha="left", weight="bold")
            ar_c.text(0.1, 0.25, f"P/L: ${c_pl_w_u:+,.2f} ({c_pl_w_u/(c_qw*c_pw) if c_qw > 0 else 0:+.2%})", color="#00FF00" if c_pl_w_u>=0 else "#FF0000", fontsize=84, ha="left", weight="bold")
            ar_c.annotate("", xy=(0.08, 0.5), xytext=(-0.19, 0.5), arrowprops=dict(arrowstyle="->", color="#006400", lw=20))
            st.pyplot(fig_c4)

        # --- TAB 6: WEN MOON DATA TABLE ---
        with tab6:
            fig_c5, ax_c5 = plt.subplots(figsize=(14, 6)); fig_c5.patch.set_facecolor("#0f172a"); ax_c5.axis('off')
            def f5_c(v, c): 
                s = "+" if v-c>=0 else "-"
                p = ((v-c)/c)*100 if c!=0 else 0
                return f"{s}${abs(v-c):,.2f} ({s}{abs(p):.2f}%)"
                
            rows_c = [
                ["WEN MOON GME",f"{c_total_shares:,}",f"${c_gp:.2f}",f"${p_nsy:.2f}",f"${c_total_shares*c_gp:,.2f}",f"${c_v_s_u:,.2f}",f5_c(c_v_s_u,c_total_shares*c_gp),f"{c_v_s_u/c_t_v_u if c_t_v_u > 0 else 0:.1%}"],
                ["WEN MOON WT",f"{c_qw:,}",f"${c_pw:.3f}",f"${p_wt:.2f}",f"${c_qw*c_pw:,.2f}",f"${c_v_w_u:,.2f}",f5_c(c_v_w_u,c_qw*c_pw),f"{c_v_w_u/c_t_v_u if c_t_v_u > 0 else 0:.1%}"],
                ["","","","","","","",""],
                ["WEN MOON PORTFOLIO","","","",f"${c_t_c_u:,.2f}",f"${c_t_v_u:,.2f}",f5_c(c_t_v_u,c_t_c_u),"100%"]
            ]
            cw = [0.18, 0.07, 0.09, 0.09, 0.11, 0.14, 0.23, 0.09]
            table_c = ax_c5.table(cellText=rows_c, colLabels=["Ticker","Qty","Avg. Cost","Price","Total Cost","Market Value","Latent P/L","Portfolio %"], loc='center', cellLoc='center', colWidths=cw)
            table_c.auto_set_font_size(False); table_c.set_fontsize(12); table_c.scale(1, 2.5)
            for (r, c), cell in table_c.get_celld().items():
                if r == 0: cell.set_facecolor("#001f3f"); cell.get_text().set_color("#00FF00"); cell.get_text().set_fontweight('bold')
                elif r in [1, 2, 4]:
                    if r == 4 and c not in [0, 4, 5, 6]: cell.set_facecolor("#0f172a"); cell.set_edgecolor("#0f172a"); continue
                    cell.set_facecolor("#0259c7"); cell.get_text().set_color("white"); cell.get_text().set_fontweight('bold')
                    if c in [1, 3, 5]: cell.get_text().set_color("#00FF00"); cell.get_text().set_fontsize(14)
                    elif c == 6: cell.get_text().set_color("#00FF00" if (c_v_s_u-c_total_shares*c_gp if r==1 else c_v_w_u-c_qw*c_pw if r==2 else c_t_pl_u)>=0 else "#ef4444"); cell.get_text().set_fontsize(14)
                else: cell.set_facecolor("#0f172a"); cell.set_edgecolor("#0f172a")
            st.pyplot(fig_c5)

    # Lancement effectif du fragment d'actualisation en direct
    live_terminal_fragment()
