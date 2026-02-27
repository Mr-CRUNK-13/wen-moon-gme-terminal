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

# --- 1. CONFIGURATION & STATE INIT ---
st.set_page_config(page_title="GME TERMINAL", layout="wide", initial_sidebar_state="collapsed")

# Session State Persistence
if 'osq' not in st.session_state: 
    st.session_state.update(osq=5500, osp=20.45, owq=6000, owp=3.0, ape_name="Ape_1", launched=False, show_leaderboard=False, recent_s=0, recent_w=0)
if 'in_nsq' not in st.session_state:
    st.session_state.update(in_nsq=0, in_nsp=0.0, in_nwq=0, in_nwp=0.0)

def get_b64(path):
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

# --- SECRET HOME BUTTON LOGIC ---
if st.button("BACK_HOME_SECRET", key="secret_home"):
    st.session_state.launched = False
    st.session_state.show_leaderboard = False
    st.rerun()

# --- BLINKING BUTTONS & PWA ENGINE (JS) ---
components.html(
    """
    <script>
    const parent = window.parent.document;
    const head = parent.querySelector('head');
    
    if (!parent.getElementById('neon-style')) {
        const style = parent.createElement('style');
        style.id = 'neon-style';
        style.innerHTML = `@keyframes neon-blink { 0%, 100% { box-shadow: 0 0 5px #00FF00, inset 0 0 2px #00FF00; } 50% { box-shadow: 0 0 20px #00FF00, inset 0 0 8px #00FF00; } }`;
        head.appendChild(style);
    }
    
    const ps = parent.querySelectorAll('p');
    ps.forEach(p => { if(p.innerText === 'BACK_HOME_SECRET') p.closest('div[data-testid="stButton"]').style.display = 'none'; });

    if (!parent.querySelector('#pwa-manifest')) {
        head.insertAdjacentHTML('beforeend', '<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">');
        const manifest = {"name": "GME TERMINAL", "short_name": "GME", "display": "fullscreen", "background_color": "#050505", "theme_color": "#050505"};
        const blob = new Blob([JSON.stringify(manifest)], {type: 'application/json'});
        head.insertAdjacentHTML('beforeend', '<link id="pwa-manifest" rel="manifest" href="' + URL.createObjectURL(blob) + '">');
    }

    if (!parent.getElementById('btn-fs')) {
        const btn = parent.createElement('button');
        btn.id = 'btn-fs'; btn.innerText = '⛶';
        btn.style = 'position:fixed; bottom:55px; right:10px; z-index:99999; background:#050505; color:#00FF00; border:2px solid #00FF00; border-radius:10px; width:35px; height:35px; font-size:20px; cursor:pointer; display:flex; justify-content:center; align-items:center; animation: neon-blink 1.5s infinite;';
        btn.onclick = function() {
            const doc = parent.documentElement;
            if (!parent.fullscreenElement) doc.requestFullscreen(); else parent.exitFullscreen();
        };
        parent.body.appendChild(btn);
    }
    
    if (!parent.getElementById('btn-home')) {
        const btnHome = parent.createElement('button');
        btnHome.id = 'btn-home'; btnHome.innerText = '🏠';
        btnHome.style = 'position:fixed; bottom:100px; right:10px; z-index:99999; background:#050505; color:#00FF00; border:2px solid #00FF00; border-radius:10px; width:35px; height:35px; font-size:20px; cursor:pointer; display:flex; justify-content:center; align-items:center; animation: neon-blink 1.5s infinite;';
        btnHome.onclick = function() {
            ps.forEach(p => { if(p.innerText === 'BACK_HOME_SECRET') p.closest('button').click(); });
        };
        parent.body.appendChild(btnHome);
    }
    </script>
    """, height=0, width=0
)

# --- GLOBAL CSS STYLES ---
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    body, .stApp { background-color: #050505 !important; color: white; }
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Animations */
    @keyframes neon-text { 0%, 100% { color: white; text-shadow: none; } 50% { color: #00FF00; text-shadow: 0 0 15px #00FF00; } }
    @keyframes neon-img { 0%, 100% { filter: drop-shadow(0 0 0px transparent); } 50% { filter: drop-shadow(0 0 25px #00FF00); } }
    @keyframes nuclear-neon { 0%, 100% { filter: drop-shadow(0 0 5px #00FF00); transform: scale(1); } 50% { filter: drop-shadow(0 0 25px #00FF00); transform: scale(1.1); } }
    @keyframes neon-flash-red { 0%, 100% { opacity: 1; filter: drop-shadow(0 0 10px #FF0000); } 50% { opacity: 0.4; filter: drop-shadow(0 0 30px #FF0000); } }
    
    /* Headers & UI */
    .title-container { text-align: center; margin-bottom: 20px; margin-top: -10px; }
    .gme-title { font-size: 60px; line-height: 1.1; animation: neon-text 1.5s infinite; margin: 0; }
    @media screen and (max-width: 600px) { .gme-title { font-size: 38px; } }
    
    /* Tables */
    .table-wrapper { overflow-x: auto; max-width: 100%; border-radius: 10px; border: 1px solid #0259c7; margin-top: 10px; }
    .ldb-t { width: 100%; border-collapse: collapse; color: white; font-family: monospace; text-align: center; font-size: 13px; }
    .ldb-t th { background: #001f3f; color: #00FF00; padding: 12px; border-bottom: 2px solid #0259c7; }
    .ldb-t td { background: #0f172a; padding: 12px; border-bottom: 1px solid #0259c7; }
    .podium td { font-size: 16px !important; color: #00FF00 !important; font-weight: bold; }
    
    /* Pro Grid */
    .pro-g { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin-top: 15px; }
    .pb { background: #0e1621; border: 1px solid #00FF00; border-radius: 8px; padding: 12px; text-align: center; }
    .pb h4 { color: #00FF00; margin: 0; font-size: 12px; text-transform: uppercase; }
    .pb p { color: white; font-size: 18px; font-weight: bold; margin: 5px 0 0 0; }
</style>
""", unsafe_allow_html=True)
# --- 2. PORTFOLIO UPDATE LOGIC ---
def update_portfolio_logic():
    nsq, nsp = st.session_state.in_nsq, st.session_state.in_nsp
    nwq, nwp = st.session_state.in_nwq, st.session_state.in_nwp
    if nsq > 0 or nwq > 0:
        # Calculate new GME Average
        fq = st.session_state.osq + nsq
        if fq > 0: 
            st.session_state.osp = ((st.session_state.osq * st.session_state.osp) + (nsq * nsp)) / fq
        st.session_state.osq = fq
        st.session_state.recent_s = nsq # Track last weekly/monthly entry
        
        # Calculate new Warrant Average
        fwq = st.session_state.owq + nwq
        if fwq > 0: 
            st.session_state.owp = ((st.session_state.owq * st.session_state.owp) + (nwq * nwp)) / fwq
        st.session_state.owq = fwq
        st.session_state.recent_w = nwq 
        
        # Reset inputs
        st.session_state.in_nsq, st.session_state.in_nsp = 0, 0.0
        st.session_state.in_nwq, st.session_state.in_nwp = 0, 0.0

# --- 3. HOME SCREEN ---
if not st.session_state.launched and not st.session_state.show_leaderboard:
    wen_b64 = get_b64('Screenshot_20260216_163106_Discord.jpg')
    st.markdown(f"""<div class="title-container"><img src='data:image/jpeg;base64,{wen_b64}' style='height:80px; vertical-align:middle; animation: neon-img 1.5s infinite; margin-right:10px;'><h1 class='gme-title' style='display:inline-block; vertical-align:middle;'>GME&nbsp;TERMINAL</h1><div style='display:inline-block; font-size:60px; vertical-align:middle; animation: nuclear-neon 1.5s infinite; margin-left:10px;'>🚀</div></div>""", unsafe_allow_html=True)
    
    with st.expander("⚙️ PORTFOLIO CONFIGURATION"):
        st.session_state.ape_name = st.text_input("Nickname", value=st.session_state.ape_name)
        st.markdown("### 🏦 CURRENT HOLDINGS")
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.osq = st.number_input("Total Shares", value=st.session_state.osq, min_value=0)
            st.session_state.osp = st.number_input("Avg Cost ($)", value=st.session_state.osp, format="%.3f")
        with c2:
            st.session_state.owq = st.number_input("Total Warrants", value=st.session_state.owq, min_value=0)
            st.session_state.owp = st.number_input("Warrant Avg ($)", value=st.session_state.owp, format="%.3f")
        
        st.markdown("---")
        st.markdown("### 🛒 NEW PURCHASES (WEEKLY/MONTHLY)")
        c3, c4 = st.columns(2)
        with c3:
            st.number_input("New Shares", min_value=0, key="in_nsq")
            st.number_input("New Price ($)", format="%.3f", key="in_nsp")
        with c4:
            st.number_input("New Warrants", min_value=0, key="in_nwq")
            st.number_input("New Price W ($)", format="%.3f", key="in_nwp")
        st.button("UPDATE PORTFOLIO", use_container_width=True, on_click=update_portfolio_logic)

    st.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("🏆 LEADERBOARD", use_container_width=True): 
            st.session_state.show_leaderboard = True
            st.rerun()
    if st.button("LAUNCH WEN MOON SYSTEM 🚀🌘!", use_container_width=True): 
        st.session_state.launched = True
        st.rerun()
    st.markdown("<h4 style='text-align: right; margin-top: 30px; font-family: monospace; animation: neon-text 1.5s infinite;'>By Mr-CRUNK-13</h4>", unsafe_allow_html=True)

# --- 4. TERMINAL ENGINE & DATA FETCHING ---
else:
    @st.cache_data(ttl=30)
    def fetch_live_data():
        try:
            gme, wt = yf.Ticker("GME"), yf.Ticker("GME-WT")
            g_h = gme.history(period="2d")
            w_h = wt.history(period="2d")
            p_n, pr_n = g_h['Close'].iloc[-1], g_h['Close'].iloc[-2]
            p_w = w_h['Close'].iloc[-1] if not w_h.empty else 0.001
            pr_w = w_h['Close'].iloc[-2] if len(w_h) > 1 else p_w
            return p_n, p_w, pr_n, pr_w, int(g_h['Volume'].iloc[-1]), int(w_h['Volume'].iloc[-1] if not w_h.empty else 0)
        except: return 24.50, 4.30, 24.0, 4.0, 0, 0

    @st.cache_data(ttl=3600)
    def fetch_pro_data():
        tk = yf.Ticker("GME")
        return tk.info, tk.options, tk.quarterly_financials, tk.insider_transactions
    # --- 5. TERMINAL UI TABS ---
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "📊 GME LIVE", "📈 WARRANT LIVE", "💎 PORTFOLIO", "📊 SUMMARY", 
        "🧬 GME PRO", "⛓️ OPTIONS CHAIN", "🏦 FINANCIALS", "🕵️ INSIDERS", 
        "📈 PRO CHARTS", "🌐 WEB PORTALS"
    ])

    # Dynamic Helpers
    def fmt(val, is_pct=False, is_dol=False, is_w=False):
        if val == 'N/A' or pd.isna(val) or val is None: return "N/A"
        try:
            v = float(val)
            if is_pct: return f"{v:+.2f}%"
            if is_dol: return f"${v:,.2f}"
            if is_w: return f"${v:,.3f}"
            return f"{v:,.0f}"
        except: return str(val)

    def draw_price_card(price, prev, vol, title, is_w=False):
        change = price - prev
        pct = (change / prev * 100) if prev > 0 else 0
        clr = "#00FF00" if change >= 0 else "#FF0000"
        anim = "nuclear-neon" if change >= 0 else "neon-flash-red"
        p_str = f"{price:.3f}" if is_w else f"{price:.2f}"
        p_int, p_dec = p_str.split('.')
        
        st.markdown(f"""
        <div style='display:flex; justify-content:center; align-items:center; gap:20px; margin-top:30px;'>
            <div style='text-align:right;'>
                <span style='font-size:50px; color:{clr}; text-shadow:0 0 20px {clr}; font-weight:bold; vertical-align:top;'>$</span><span style='font-size:100px; color:{clr}; text-shadow:0 0 20px {clr}; font-weight:bold;'>{p_int}.</span><span style='font-size:80px; color:{clr}; text-shadow:0 0 20px {clr}; font-weight:bold;'>{p_dec}</span>
                <h3 style='color:{clr}; margin-top:0px;'>{change:+.2f} ({pct:+.2f}%)</h3>
                <p style='color:#888; font-family:monospace; font-size:18px;'>VOLUME: {vol:,}</p>
            </div>
            <div style='animation: {anim} 1.5s infinite; font-size:120px;'>{'🚀' if change >= 0 else '📉'}</div>
        </div>
        """, unsafe_allow_html=True)

    def render_content():
        p_n, p_w, pr_n, pr_w, vol_n, vol_w = fetch_live_data()
        adv_info, opt_dates, fin, ins = fetch_pro_data()
        
        # UI TABS RENDERING
        with tab1: draw_price_card(p_n, pr_n, vol_n, "GME")
        with tab2: draw_price_card(p_w, pr_w, vol_w, "WARRANTS", is_w=True)
        
        with tab3:
            # Portfolio Visuals (Donut + Stats)
            val_s, val_w = st.session_state.osq * p_n, st.session_state.owq * p_w
            total_val = val_s + val_w
            cost_s, cost_w = st.session_state.osq * st.session_state.osp, st.session_state.owq * st.session_state.owp
            pl_s, pl_w = val_s - cost_s, val_w - cost_w
            
            fig = go.Figure(data=[go.Pie(labels=['Shares', 'Warrants'], values=[val_s, val_w], 
                            hole=.4, marker_colors=['#00FF00', '#006400'])])
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            html_p = f"""<div class='table-wrapper'><table class='ldb-t'>
                <tr><th>Asset</th><th>Qty</th><th>Avg</th><th>Price</th><th>Value</th><th>P/L</th></tr>
                <tr><td>GME</td><td>{st.session_state.osq:,}</td><td>${st.session_state.osp:.2f}</td><td>${p_n:.2f}</td><td>${val_s:,.2f}</td><td style='color:{"#00FF00" if pl_s>=0 else "#FF0000"}'>{pl_s:+,.2f}</td></tr>
                <tr><td>WARRANT</td><td>{st.session_state.owq:,}</td><td>${st.session_state.owp:.3f}</td><td>${p_w:.3f}</td><td>${val_w:,.2f}</td><td style='color:{"#00FF00" if pl_w>=0 else "#FF0000"}'>{pl_w:+,.2f}</td></tr>
                <tr class='podium'><td>TOTAL</td><td></td><td></td><td></td><td>${total_val:,.2f}</td><td>{(pl_s+pl_w):+,.2f}</td></tr>
            </table></div>"""
            st.markdown(html_p, unsafe_allow_html=True)

        with tab4:
            # Community Summary
            st.markdown(f"""<div style='background:#0f172a; padding:20px; border:1px solid #0259c7; border-radius:10px; text-align:center;'>
                <h2 style='color:#00FF00; animation:neon-text 1.5s infinite;'>🌍 COMMUNITY SUMMARY</h2>
                <div style='display:flex; justify-content:space-around; margin-top:20px;'>
                    <div><h4>WEEKLY</h4><p>Shares: +{st.session_state.recent_s:,}</p><p>Warrants: +{st.session_state.recent_w:,}</p></div>
                </div></div>""", unsafe_allow_html=True)

        with tab5:
            # Pro Grid Fundamentals
            st.markdown("<div class='pro-g'>", unsafe_allow_html=True)
            pro_metrics = [
                ("Market Cap", fmt(adv_info.get('marketCap'), is_dol=True)),
                ("Shares Float", fmt(adv_info.get('floatShares'))),
                ("Total Cash", fmt(adv_info.get('totalCash'), is_dol=True)),
                ("Total Debt", fmt(adv_info.get('totalDebt'), is_dol=True)),
                ("Short % Float", fmt(adv_info.get('shortPercentOfFloat', 0)*100, is_pct=True)),
                ("Free Cash Flow", fmt(adv_info.get('freeCashflow'), is_dol=True))
            ]
            for title, val in pro_metrics:
                st.markdown(f"<div class='pb'><h4>{title}</h4><p>{val}</p></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Net Income Historical Table
            st.markdown("<h4 style='text-align:center; margin-top:30px;'>📊 HISTORICAL NET INCOME (M$)</h4>", unsafe_allow_html=True)
            inc_data = [
                {"Y": "2025", "Q1": 45, "Q2": 169, "Q3": 77, "Q4": None, "R": 291},
                {"Y": "2024", "Q1": -32, "Q2": 15, "Q3": 17, "Q4": 131, "R": 131},
                {"Y": "2023", "Q1": -51, "Q2": -3, "Q3": -3, "Q4": 63, "R": 7}
            ]
            html_i = "<div class='table-wrapper'><table class='ldb-t'><tr><th>Year</th><th>Q1</th><th>Q2</th><th>Q3</th><th>Q4</th><th>Results</th></tr>"
            for r in inc_data:
                html_i += f"<tr><td>{r['Y']}</td>"
                for q in ["Q1", "Q2", "Q3", "Q4", "R"]:
                    v = r[q]
                    bg = "#132a13" if v and v > 0 else "#2a1313" if v and v < 0 else "transparent"
                    html_i += f"<td style='background-color:{bg}'>{v if v else ''}</td>"
                html_i += "</tr>"
            st.markdown(html_i + "</table></div>", unsafe_allow_html=True)

        with tab6:
            # Options centered +/- 12 strikes
            if opt_dates:
                sel_exp = st.selectbox("EXPIRY DATE:", opt_dates)
                chain = yf.Ticker("GME").option_chain(sel_exp)
                df = chain.calls
                df['diff'] = (df['strike'] - p_n).abs()
                idx = df['diff'].idxmin()
                st.dataframe(df.iloc[max(0, idx-12):idx+13][['strike', 'lastPrice', 'volume', 'openInterest']], use_container_width=True)

        with tab7:
            # Consensus & Targets
            c_a, c_b, c_c = st.columns(3)
            c_a.metric("Target High", fmt(adv_info.get('targetHighPrice'), is_dol=True))
            c_b.metric("Target Mean", fmt(adv_info.get('targetMeanPrice'), is_dol=True))
            c_c.metric("Target Low", fmt(adv_info.get('targetLowPrice'), is_dol=True))
            st.info(f"Recommendation: {adv_info.get('recommendationKey', 'N/A').upper()}")

    render_content()
