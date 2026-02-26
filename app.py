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

if 'osq' not in st.session_state: 
    st.session_state.update(osq=0, osp=0.0, owq=0, owp=0.0, ape_name="", launched=False, show_leaderboard=False, recent_s=0, recent_w=0)
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

# --- BLINKING BUTTONS (HOME + FULLSCREEN) ---
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

# --- CSS ---
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

# --- UPDATE LOGIC WITH ACTIVITY TRACKER ---
def update_portfolio_logic():
    nsq, nsp = st.session_state.in_nsq, st.session_state.in_nsp
    nwq, nwp = st.session_state.in_nwq, st.session_state.in_nwp
    if nsq > 0 or nwq > 0:
        fq = st.session_state.osq + nsq
        if fq > 0: st.session_state.osp = ((st.session_state.osq * st.session_state.osp) + (nsq * nsp)) / fq
        st.session_state.osq = fq
        st.session_state.recent_s += nsq 
        
        fwq = st.session_state.owq + nwq
        if fwq > 0: st.session_state.owp = ((st.session_state.owq * st.session_state.owp) + (nwq * nwp)) / fwq
        st.session_state.owq = fwq
        st.session_state.recent_w += nwq 
        
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
        live_p_n = float(data['GME'].dropna().iloc[-1]) if not data['GME'].dropna().empty else 24.50
        live_p_w = float(data['GME-WT'].dropna().iloc[-1]) if not data['GME-WT'].dropna().empty else 4.30
    except: live_p_n, live_p_w = 24.50, 4.30
    u_name, u_sq, u_wq = st.session_state.get("ape_name", "Anonymous"), st.session_state.get("osq", 0), st.session_state.get("owq", 0)
    u_tv = (u_sq * live_p_n) + (u_wq * live_p_w)
    real_db = [{"name": u_name, "tv": u_tv, "sq": u_sq, "wq": u_wq, "spru": st.session_state.get("osp", 0.0), "wpru": st.session_state.get("owp", 0.0)}]
    for t in lb_tabs:
        with t:
            html = """<div class='table-wrapper'><table class='ldb-t'><tr><th class='col-rank'>Rank</th><th class='col-name'>Nickname</th><th class='col-val'>Total Value</th><th class='col-qty'>Shares</th><th class='col-qty'>Warrants</th><th>Avg S</th><th>Avg W</th><th>S%</th><th>W%</th></tr>"""
            for i, r in enumerate(real_db):
                rank_str = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}"
                s_pct = (r["sq"]*live_p_n / r["tv"] * 100 if r["tv"] > 0 else 0)
                w_pct = (r["wq"]*live_p_w / r["tv"] * 100 if r["tv"] > 0 else 0)
                html += f"<tr class='{'podium' if i<3 else ''}'><td>{rank_str}</td><td>{r['name']}</td><td>${r['tv']:,.2f}</td><td>{r['sq']:,}</td><td>{r['wq']:,}</td><td>${r['spru']:.3f}</td><td>${r['wpru']:.3f}</td><td>{s_pct:.1f}%</td><td>{w_pct:.1f}%</td></tr>"
            st.markdown(html + "</table></div>", unsafe_allow_html=True)

# --- 3. TERMINAL & LIVE ENGINE ---
else:
    @st.cache_data(ttl=30)
    def fetch_terminal_data():
        try:
            ts = ["GME", "GME-WT"]
            data = yf.download(ts, period="1d", interval="2m", prepost=True, progress=False)['Close']
            p_n = float(data['GME'].dropna().iloc[-1]) if not data['GME'].dropna().empty else 24.50
            p_w = float(data['GME-WT'].dropna().iloc[-1]) if not data['GME-WT'].dropna().empty else 4.30
            
            t_n, t_w = yf.Ticker("GME"), yf.Ticker("GME-WT")
            prev_n = float(t_n.fast_info.get('previousClose', p_n))
            prev_w = float(t_w.fast_info.get('previousClose', p_w))
            
            # --- FETCHING DAILY VOLUME HERE ---
            vol_n = int(t_n.fast_info.get('lastVolume', 0))
            vol_w = int(t_w.fast_info.get('lastVolume', 0))
            
            return p_n, p_w, prev_n, prev_w, vol_n, vol_w, data['GME'], data['GME-WT']
        except: return 24.50, 4.30, 24.0, 4.0, 0, 0, pd.Series(), pd.Series()

    @st.cache_data(ttl=1800)
    def fetch_advanced_pro_data():
        try:
            gme, wt = yf.Ticker("GME"), yf.Ticker("GME-WT")
            return gme.info, wt.fast_info, gme.news[:5] if gme.news else []
        except: return {}, {}, []

    @st.cache_data(ttl=3600)
    def fetch_financials_and_options():
        try:
            tk = yf.Ticker("GME")
            opts = tk.options
            fin = tk.financials
            bs = tk.balance_sheet
            cf = tk.cashflow
            ins = tk.insider_transactions
            return opts, fin, bs, cf, ins
        except: return (), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # THE 15 TITAN TABS
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14, tab15 = st.tabs([
        "📊 GME", "📈 WARRANT", "💎 PORTFOLIO", "📋 DATA", "🌘 WEN MOON", "🗃️ WM DATA", "🏆 LEADERBOARD", "📊 SUMMARY", 
        "🧬 GME PRO", "⛓️ OPTIONS CHAIN", "🏦 FINANCIALS", "🕵️ INSIDERS", "📈 PRO CHARTS", "🌐 WEB PORTALS", "🐦 LIVE ALERTS"
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
        t_chart1, t_chart2 = st.tabs(["🇺🇸 GME (TradingView Pro)", "📜 GME-WT (Live Tracker)"])
        with t_chart1:
            tv_html = """
            <div class="tradingview-widget-container" style="height: 700px; width: 100%;">
              <div id="tradingview_gme" style="height: 100%; width: 100%;"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
              <script type="text/javascript">
              new TradingView.widget({
                "autosize": true, "symbol": "NYSE:GME", "interval": "D", "timezone": "Etc/UTC",
                "theme": "dark", "style": "1", "locale": "en", "enable_publishing": false,
                "backgroundColor": "#050505", "gridColor": "#1f2937", "hide_top_toolbar": false,
                "hide_legend": false, "save_image": false, "container_id": "tradingview_gme",
                "toolbar_bg": "#0f172a"
              });
              </script>
            </div>"""
            components.html(tv_html, height=720)
        with t_chart2:
            ph13_wt = st.empty()

    # --- TAB 14 : WEB PORTALS (Static) ---
    with tab14:
        st.markdown("<h2 style='text-align:center; color:#00FF00; font-family:monospace;'>🌐 INVESTOR PORTALS</h2>", unsafe_allow_html=True)
        w_tab1, w_tab2, w_tab3, w_tab4, w_tab5 = st.tabs(["👔 GameStop Investors", "📊 ChartExchange", "🎀 RedStripeTie", "🐋 Unusual Whales", "🦍 r/Superstonk"])
        with w_tab1:
            st.components.v1.iframe("https://investor.gamestop.com/", height=700, scrolling=True)
            st.markdown("<a href='https://investor.gamestop.com/' target='_blank' style='color:#00FF00; display:block; text-align:center; margin-top:10px; font-weight:bold;'>👉 OPEN GAMESTOP INVESTORS</a>", unsafe_allow_html=True)
        with w_tab2:
            st.components.v1.iframe("https://chartexchange.com/symbol/nyse-gme/borrow-fee/", height=700, scrolling=True)
            st.markdown("<a href='https://chartexchange.com/symbol/nyse-gme/borrow-fee/' target='_blank' style='color:#00FF00; display:block; text-align:center; margin-top:10px; font-weight:bold;'>👉 OPEN CHARTEXCHANGE (BORROW FEE)</a>", unsafe_allow_html=True)
        with w_tab3:
            st.markdown("<div style='text-align:center; padding:50px; background:#0f172a; border:1px solid #00FF00; border-radius:10px;'><h3 style='color:white;'>🎀 RED STRIPE TIE</h3><p style='color:#ccc; font-size:18px;'>Direct access to community data.</p><a href='https://redstripetie.com/' target='_blank' style='display:inline-block; margin-top:20px; padding:15px 30px; background:#00FF00; color:black; font-weight:bold; text-decoration:none; border-radius:5px; font-size:20px;'>OPEN SITE</a></div>", unsafe_allow_html=True)
        with w_tab4:
            st.markdown("<div style='text-align:center; padding:50px; background:#0f172a; border:1px solid #00FF00; border-radius:10px;'><h3 style='color:white;'>🐋 UNUSUAL WHALES (OPTIONS FLOW)</h3><p style='color:#ccc; font-size:18px;'>Track options market activity.</p><a href='https://unusualwhales.com/stock/GME' target='_blank' style='display:inline-block; margin-top:20px; padding:15px 30px; background:#00FF00; color:black; font-weight:bold; text-decoration:none; border-radius:5px; font-size:20px;'>OPEN SITE</a></div>", unsafe_allow_html=True)
        with w_tab5:
            st.markdown("<div style='text-align:center; padding:50px; background:#0f172a; border:1px solid #00FF00; border-radius:10px;'><h3 style='color:white;'>🦍 r/SUPERSTONK</h3><p style='color:#ccc; font-size:18px;'>The heart of the GME community.</p><a href='https://www.reddit.com/r/Superstonk/' target='_blank' style='display:inline-block; margin-top:20px; padding:15px 30px; background:#00FF00; color:black; font-weight:bold; text-decoration:none; border-radius:5px; font-size:20px;'>OPEN REDDIT</a></div>", unsafe_allow_html=True)

    # --- TAB 15 : LIVE ALERTS (Twitter X - Static) ---
    with tab15:
        st.markdown("<h2 style='text-align:center; color:#00FF00; font-family:monospace;'>🐦 X LIVE ALERTS</h2>", unsafe_allow_html=True)
        x_tab1, x_tab2, x_tab3, x_tab4, x_tab5, x_tab6 = st.tabs(["👑 Ryan Cohen", "🐱 Roaring Kitty", "📉 Michael Burry", "🎮 GameStop", "🐰 Buck", "🃏 PowerPacks"])
        
        def x_widget(handle):
            return f"""<div style="background:#000; overflow-y:scroll; height:700px;"><a class="twitter-timeline" data-theme="dark" href="https://twitter.com/{handle}?ref_src=twsrc%5Etfw">Tweets by {handle}</a><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script></div>"""
        
        with x_tab1: components.html(x_widget("ryancohen"), height=720)
        with x_tab2: components.html(x_widget("TheRoaringKitty"), height=720)
        with x_tab3: components.html(x_widget("michaeljburry"), height=720)
        with x_tab4: components.html(x_widget("GameStop"), height=720)
        with x_tab5: components.html(x_widget("buckthebunny"), height=720)
        with x_tab6: components.html(x_widget("PowerPacks"), height=720)
    def draw_live(price, prev, chart, vol=0):
        pct = ((price - prev) / prev) * 100 if prev > 0 else 0
        diff, clr = price - prev, ("#00FF00" if price >= prev else "#FF0000")
        price_str = f"{price:.2f}"
        p_int, p_dec = price_str.split('.')
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
            ax.bar(np.arange(len(v)), v - np.min(v)*0.99, bottom=np.min(v)*0.99, color=clr, width=0.8); ax.axis('off')
            st.pyplot(fig, bbox_inches='tight', pad_inches=0); plt.close(fig)
            st.markdown(f"<p style='text-align:center; color:#888; font-family:monospace; font-size:18px; margin-top:5px; margin-bottom:20px;'>TODAY'S VOLUME: {vol:,}</p>", unsafe_allow_html=True)

    @st.fragment(run_every="30s")
    def render_content():
        plt.close('all') 
        p_nsy, p_wt, pr_nsy, pr_wt, vol_n, vol_w, ch_gme, ch_wt = fetch_terminal_data()
        adv_info, wt_info, gme_news = fetch_advanced_pro_data()
        opts, fin, bs, cf, ins = fetch_financials_and_options()
        
        qn, pn = st.session_state.osq, st.session_state.osp
        qw, pw = st.session_state.owq, st.session_state.owp
        gp = st.session_state.osp

        total_shares = qn
        v_s_u = qn * p_nsy
        v_w_u = qw * p_wt
        t_v_u = v_s_u + v_w_u
        t_c_u = (qn * gp) + (qw * pw)

        # --- COMMUNITY SIMULATION ---
        c_s, c_w = qn, qw
        c_gp_val = gp if qn > 0 else 0.0
        c_pw_val = pw if qw > 0 else 0.0
        
        c_v_s = c_s * p_nsy
        c_v_w = c_w * p_wt
        c_t_v = c_v_s + c_v_w
        c_t_c = (c_s * c_gp_val) + (c_w * c_pw_val)

        with ph1.container(): draw_live(p_nsy, pr_nsy, ch_gme, vol_n)
        with ph2.container(): draw_live(p_wt, pr_wt, ch_wt, vol_w)

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
            rec_s, rec_w = st.session_state.get("recent_s", 0), st.session_state.get("recent_w", 0)

            html_summary = f"""
            <div style="background-color: #0f172a; padding: 20px; border-radius: 10px; border: 1px solid #0259c7;">
                <h2 style="text-align: center; color: #00FF00; margin-bottom: 30px; animation: neon-text 1.5s infinite; font-size: 32px;">🌍 WEN MOON COMMUNITY SUMMARY</h2>
                <div style="text-align: center; margin-bottom: 30px;">
                    <h3 style="color: #66c2a5; margin: 0; font-size: 24px;">TOTAL HOLDERS</h3>
                    <p style="font-size: 48px; color: white; font-weight: bold; margin: 10px 0 0 0;">{total_holders:,}</p>
                </div>
                <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin-bottom: 30px; gap: 20px;">
                    <div style="background-color: #0e1621; padding: 20px; border-radius: 8px; border: 2px solid #00FF00; flex: 1 1 300px; text-align: center;">
                        <h4 style="color: #00FF00; margin-top: 0; font-size: 24px; font-weight: bold;">GME SHARES</h4>
                        <p style="margin: 10px 0; font-size: 18px;">Total Shares: <strong style="color: white;">{c_s:,}</strong></p>
                        <p style="margin: 10px 0; font-size: 18px;">Avg Purchase Price: <strong style="color: white;">${c_gp_val:.2f}</strong></p>
                        <p style="margin: 10px 0; font-size: 18px;">Avg Shares / Person: <strong style="color: white;">{avg_s_per_person:,.0f}</strong></p>
                    </div>
                    <div style="background-color: #0e1621; padding: 20px; border-radius: 8px; border: 2px solid #006400; flex: 1 1 300px; text-align: center;">
                        <h4 style="color: #006400; margin-top: 0; font-size: 24px; font-weight: bold;">GME WARRANTS</h4>
                        <p style="margin: 10px 0; font-size: 18px;">Total Warrants: <strong style="color: white;">{c_w:,}</strong></p>
                        <p style="margin: 10px 0; font-size: 18px;">Avg Purchase Price: <strong style="color: white;">${c_pw_val:.3f}</strong></p>
                        <p style="margin: 10px 0; font-size: 18px;">Avg Warrants / Person: <strong style="color: white;">{avg_w_per_person:,.0f}</strong></p>
                    </div>
                </div>
                <h3 style="text-align: center; color: #66c2a5; margin-bottom: 20px; font-size: 24px;">📅 RECENT ACTIVITY (COMMUNITY)</h3>
                <div class='table-wrapper'><table class='ldb-t'>
                    <tr><th>Asset</th><th>Bought (Last 7 Days)</th><th>Bought (Last 30 Days)</th></tr>
                    <tr><td style="color: #00FF00; font-weight: bold;">GME SHARES</td><td>{rec_s:,}</td><td>{rec_s:,}</td></tr>
                    <tr><td style="color: #006400; font-weight: bold;">GME WARRANTS</td><td>{rec_w:,}</td><td>{rec_w:,}</td></tr>
                </table></div>
            </div>
            """
            st.markdown(html_summary, unsafe_allow_html=True)

        with ph13_wt.container():
            if not ch_wt.empty:
                fig_wt, ax_wt = plt.subplots(figsize=(16, 7), facecolor='#050505')
                ax_wt.set_facecolor('#0f172a')
                v_wt = ch_wt.dropna().values
                ax_wt.plot(np.arange(len(v_wt)), v_wt, color='#006400', linewidth=4)
                ax_wt.fill_between(np.arange(len(v_wt)), v_wt, min(v_wt)*0.98, color='#006400', alpha=0.3)
                ax_wt.set_title("GME-WT INTRADAY PRICE ACTION", color="#006400", fontsize=24, weight='bold', pad=20)
                ax_wt.tick_params(colors='white', labelsize=14)
                ax_wt.grid(color='#1f2937', linestyle='--', alpha=0.5)
                st.pyplot(fig_wt); plt.close(fig_wt)
        with ph9.container():
            def fmt(val, is_pct=False, is_dol=False):
                if val == 'N/A' or pd.isna(val) or val is None: return "N/A"
                try:
                    v = float(val)
                    if is_pct: return f"{v*100:.2f}%"
                    if is_dol: return f"${v:,.2f}"
                    return f"{v:,.0f}"
                except: return str(val)

            ptab1, ptab2, ptab3 = st.tabs(["🏛️ GME FUNDAMENTALS", "📜 WARRANTS DATA", "📰 LATEST NEWS"])
            
            with ptab1:
                html_gme = f"""
                <style>
                    .pro-g {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 15px; }}
                    .pb {{ background: #0e1621; border: 1px solid #00FF00; border-radius: 8px; padding: 15px; text-align: center; }}
                    .pb h4 {{ color: #00FF00; margin: 0 0 5px 0; font-size: 16px; font-family: monospace; }}
                    .pb p {{ color: white; font-size: 22px; font-weight: bold; margin: 0; }}
                </style>
                <div class="pro-g">
                    <div class="pb"><h4>Market Cap</h4><p>{fmt(adv_info.get('marketCap'), is_dol=True)}</p></div>
                    <div class="pb"><h4>Total Cash</h4><p>{fmt(adv_info.get('totalCash'), is_dol=True)}</p></div>
                    <div class="pb"><h4>Total Debt</h4><p>{fmt(adv_info.get('totalDebt'), is_dol=True)}</p></div>
                    <div class="pb"><h4>Shares Outstanding</h4><p>{fmt(adv_info.get('sharesOutstanding'))}</p></div>
                    <div class="pb"><h4>Short % of Float</h4><p>{fmt(adv_info.get('shortPercentOfFloat'), is_pct=True)}</p></div>
                    <div class="pb"><h4>Days to Cover</h4><p>{fmt(adv_info.get('shortRatio'))}</p></div>
                    <div class="pb"><h4>Held by Insiders</h4><p>{fmt(adv_info.get('heldPercentInsiders'), is_pct=True)}</p></div>
                    <div class="pb"><h4>Held by Institutions</h4><p>{fmt(adv_info.get('heldPercentInstitutions'), is_pct=True)}</p></div>
                    <div class="pb"><h4>Avg Volume (10 Days)</h4><p>{fmt(adv_info.get('averageVolume10days'))}</p></div>
                    <div class="pb"><h4>Avg Volume (3 Months)</h4><p>{fmt(adv_info.get('averageVolume'))}</p></div>
                    <div class="pb"><h4>Trailing P/E</h4><p>{fmt(adv_info.get('trailingPE'))}</p></div>
                    <div class="pb"><h4>Beta (Volatility)</h4><p>{fmt(adv_info.get('beta'))}</p></div>
                </div>"""
                st.markdown(html_gme, unsafe_allow_html=True)
                
            with ptab2:
                wt_vol = getattr(wt_info, 'lastVolume', 'N/A')
                wt_open = getattr(wt_info, 'regularMarketOpen', 'N/A')
                wt_high = getattr(wt_info, 'dayHigh', 'N/A')
                wt_low = getattr(wt_info, 'dayLow', 'N/A')
                wt_prev = getattr(wt_info, 'previousClose', 'N/A')
                html_wt = f"""
                <div class="pro-g">
                    <div class="pb" style="border-color:#006400;"><h4 style="color:#006400;">Contract Name</h4><p>GME-WT (Warrant)</p></div>
                    <div class="pb" style="border-color:#006400;"><h4 style="color:#006400;">Today's Volume</h4><p>{fmt(wt_vol)}</p></div>
                    <div class="pb" style="border-color:#006400;"><h4 style="color:#006400;">Market Open</h4><p>{fmt(wt_open, is_dol=True)}</p></div>
                    <div class="pb" style="border-color:#006400;"><h4 style="color:#006400;">Day High</h4><p>{fmt(wt_high, is_dol=True)}</p></div>
                    <div class="pb" style="border-color:#006400;"><h4 style="color:#006400;">Day Low</h4><p>{fmt(wt_low, is_dol=True)}</p></div>
                    <div class="pb" style="border-color:#006400;"><h4 style="color:#006400;">Previous Close</h4><p>{fmt(wt_prev, is_dol=True)}</p></div>
                </div>"""
                st.markdown(html_wt, unsafe_allow_html=True)

            with ptab3:
                st.markdown("<h3 style='color:#00FF00; font-family:monospace; margin-top:20px;'>🗞️ LATEST FINANCIAL NEWS (LIVE)</h3>", unsafe_allow_html=True)
                for n in gme_news:
                    ts = datetime.fromtimestamp(n.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M')
                    st.markdown(f"""
                    <div style="background:#0f172a; border-left:4px solid #00FF00; padding:15px; margin-bottom:10px; border-radius:4px;">
                        <small style="color:#888;">{n.get('publisher', 'News')} • {ts}</small><br>
                        <a href="{n.get('link', '#')}" target="_blank" style="color:white; font-size:18px; text-decoration:none; font-weight:bold;">{n.get('title', 'No Title')}</a>
                    </div>""", unsafe_allow_html=True)

        with ph10.container():
            st.markdown("<h2 style='text-align:center; color:#00FF00; font-family:monospace;'>⛓️ OPTIONS CHAIN SUMMARY</h2>", unsafe_allow_html=True)
            if len(opts) > 0:
                exp = opts[0]
                st.markdown(f"<p style='text-align:center; color:white; font-size:18px;'>Next expiration detected: <b>{exp}</b></p>", unsafe_allow_html=True)
                try:
                    tk = yf.Ticker("GME")
                    opt_chain = tk.option_chain(exp)
                    calls = opt_chain.calls.head(8)
                    html_opt = "<h4 style='color:#00FF00;'>🔥 Top 8 Calls (In & Out of Money)</h4><div class='table-wrapper'><table class='ldb-t'><tr><th>Strike</th><th>Last Price</th><th>Volume</th><th>Implied Volatility</th></tr>"
                    for _, r in calls.iterrows():
                        html_opt += f"<tr><td>${r.get('strike', 0)}</td><td>${r.get('lastPrice', 0)}</td><td>{r.get('volume', 0)}</td><td>{r.get('impliedVolatility', 0)*100:.1f}%</td></tr>"
                    html_opt += "</table></div>"
                    st.markdown(html_opt, unsafe_allow_html=True)
                except:
                    st.warning("Options chain data currently unavailable.")
            else:
                st.info("No expiration date found or market closed.")

        with ph11.container():
            st.markdown("<h2 style='text-align:center; color:#00FF00; font-family:monospace;'>🏦 FINANCIALS & EARNINGS</h2>", unsafe_allow_html=True)
            f_tab1, f_tab2, f_tab3 = st.tabs(["📈 INCOME STATEMENT", "⚖️ BALANCE SHEET", "💸 CASH FLOW"])
            
            def df_to_html(df, title):
                if df.empty: return f"<p style='color:white;'>{title} data not available.</p>"
                cols = [str(c)[:10] for c in df.columns[:3]]
                html = f"<div class='table-wrapper'><table class='ldb-t'><tr><th>Metric</th>"
                for c in cols: html += f"<th>{c}</th>"
                html += "</tr>"
                for idx, row in df.iloc[:8, :3].iterrows():
                    html += f"<tr><td style='text-align:left; font-weight:bold; color:#00FF00;'>{idx}</td>"
                    for val in row:
                        try: html += f"<td>${float(val):,.0f}</td>"
                        except: html += f"<td>{val}</td>"
                    html += "</tr>"
                html += "</table></div>"
                return html

            with f_tab1: st.markdown(df_to_html(fin, "Income Statement"), unsafe_allow_html=True)
            with f_tab2: st.markdown(df_to_html(bs, "Balance Sheet"), unsafe_allow_html=True)
            with f_tab3: st.markdown(df_to_html(cf, "Cash Flow"), unsafe_allow_html=True)

        with ph12.container():
            st.markdown("<h2 style='text-align:center; color:#00FF00; font-family:monospace;'>🕵️ INSIDER TRACKER</h2>", unsafe_allow_html=True)
            if not ins.empty:
                st.dataframe(ins.astype(str), use_container_width=True)
            else:
                st.info("No recent insider transactions detected.")

    # --- ENGINE LAUNCH (Closes the application) ---
    render_content()
