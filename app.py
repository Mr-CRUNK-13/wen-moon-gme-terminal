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

def get_b64(path):
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

# --- CSS & ANIMATIONS ---
st.markdown("""
<style>
    body, .stApp { background-color: #050505 !important; color: white; }
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Animations Green/General */
    @keyframes neon-text { 0%, 100% { color: white; text-shadow: none; } 50% { color: #00FF00; text-shadow: 0 0 15px #00FF00; } }
    @keyframes neon-img { 0%, 100% { filter: drop-shadow(0 0 0px transparent); } 50% { filter: drop-shadow(0 0 25px #00FF00); } }
    @keyframes nuclear-neon { 
        0%, 100% { filter: drop-shadow(0 0 5px #00FF00); transform: translateY(0px) scale(1); } 
        50% { filter: drop-shadow(0 0 25px #00FF00); transform: translateY(-15px) scale(1.1); } 
    }

    /* NEW! Red Neon Flash Animation for Falling Price */
    @keyframes neon-flash-red {
        0%, 100% { opacity: 1; filter: drop-shadow(0 0 10px #FF0000); }
        50% { opacity: 0.4; filter: drop-shadow(0 0 30px #FF0000); }
    }

    /* Layout CSS */
    .title-container { text-align: center; margin-bottom: 30px; }
    .gme-title { font-size: 60px; line-height: 1.1; animation: neon-text 1.5s infinite; white-space: nowrap; margin: 0; }
    @media screen and (max-width: 600px) { .gme-title { font-size: 38px; } }

    /* Tables CSS */
    .table-wrapper { overflow-x: auto; max-width: 100%; border-radius: 10px; border: 1px solid #0259c7; margin-top: 10px; }
    .ldb-t { width: 100%; border-collapse: collapse; color: white; font-family: monospace; text-align: center; }
    .ldb-t th { background: #001f3f; color: #00FF00; padding: 12px; border-bottom: 2px solid #0259c7; white-space: nowrap; }
    .ldb-t td { background: #0f172a; padding: 12px; border-bottom: 1px solid #0259c7; white-space: nowrap; }
    .podium td { font-size: 18px !important; color: #00FF00 !important; font-weight: bold; }
    
    .col-rank { min-width: 70px; }
    .col-name { min-width: 150px; }
    .col-val { min-width: 160px; }
    .col-qty { min-width: 120px; }
</style>
""", unsafe_allow_html=True)

if 'launched' not in st.session_state: st.session_state.launched = False
if 'show_leaderboard' not in st.session_state: st.session_state.show_leaderboard = False

# --- 2. HOME SCREEN ---
if not st.session_state.launched and not st.session_state.show_leaderboard:
    wen_b64 = get_b64('Screenshot_20260216_163106_Discord.jpg')
    
    st.markdown(f"""
    <div class="title-container">
        <img src='data:image/jpeg;base64,{wen_b64}' style='height:80px; vertical-align:middle; animation: neon-img 1.5s infinite; margin-right:10px;'>
        <h1 class='gme-title' style='display:inline-block; vertical-align:middle;'>GME&nbsp;TERMINAL</h1>
        <div style='display:inline-block; font-size:60px; vertical-align:middle; animation: nuclear-neon 1.5s infinite; margin-left:10px;'>🚀</div>
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
        if st.button("🏆 LEADERBOARD", use_container_width=True):
            st.session_state.show_leaderboard = True
            st.rerun()

    if st.button("LAUNCH WEN MOON SYSTEM 🚀🌘!", use_container_width=True):
        st.session_state.update(ape_name=ape_name if ape_name else "Anonymous", qn=fq, pn=fp, qw=fwq, pw=fwp, gp=fp, launched=True)
        st.rerun()
    st.markdown("<h4 style='text-align: right; margin-top: 30px; font-family: monospace; animation: neon-text 1.5s infinite;'>By Mr-CRUNK-13</h4>", unsafe_allow_html=True)

# --- 2.5 LEADERBOARD SCREEN ---
elif st.session_state.get('show_leaderboard', False):
    wen_b64 = get_b64('Screenshot_20260216_163106_Discord.jpg')
    st.markdown(f"<div style='text-align:center;'><h1 style='font-size:40px; color:#00FF00; animation:neon-text 1.5s infinite;'>🏆 LEADERBOARD <img src='data:image/jpeg;base64,{wen_b64}' style='height:50px; vertical-align:middle; animation:neon-img 1.5s infinite;'></h1></div>", unsafe_allow_html=True)
    
    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
    with col_b2:
        if st.button("⬅️ BACK TO HOME", use_container_width=True):
            st.session_state.show_leaderboard = False
            st.rerun()

    lb_tabs = st.tabs(["🌍 GENERAL", "📅 MONTHLY", "📆 WEEKLY"])
    
    try:
        data = yf.download(["GME", "GME-WT"], period="1d", interval="2m", prepost=True, progress=False)['Close']
        live_p_n = float(data['GME'].dropna().iloc[-1])
        live_p_w = float(data['GME-WT'].dropna().iloc[-1])
    except: live_p_n, live_p_w = 24.50, 4.30

    u_name = st.session_state.get("ape_name", "Anonymous")
    u_sq, u_wq = st.session_state.get("qn", 0), st.session_state.get("qw", 0)
    u_spru, u_wpru = st.session_state.get("pn", 0.0), st.session_state.get("pw", 0.0)
    u_tv = (u_sq * live_p_n) + (u_wq * live_p_w)

    real_db = [{"name": u_name, "tv": u_tv, "sq": u_sq, "wq": u_wq, "spru": u_spru, "wpru": u_wpru}]
    
    for t in lb_tabs:
        with t:
            html = """<div class='table-wrapper'><table class='ldb-t'>
                <tr><th class='col-rank'>Rank</th><th class='col-name'>Nickname</th><th class='col-val'>Total Value</th><th class='col-qty'>Shares</th><th class='col-qty'>Warrants</th><th>Avg S</th><th>Avg W</th><th>S%</th><th>W%</th></tr>"""
            for i, r in enumerate(real_db):
                rank_str = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}"
                rc = "podium" if i < 3 else ""
                s_pct = (r["sq"]*live_p_n / r["tv"] * 100) if r["tv"] > 0 else 0
                w_pct = (r["wq"]*live_p_w / r["tv"] * 100) if r["tv"] > 0 else 0
                sc, wc = (f"${r['spru']:.3f}" if r['spru']>0 else "N/A"), (f"${r['wpru']:.3f}" if r['wpru']>0 else "N/A")
                html += f"<tr class='{rc}'><td>{rank_str}</td><td>{r['name']}</td><td>${r['tv']:,.2f}</td><td>{r['sq']:,}</td><td>{r['wq']:,}</td><td>{sc}</td><td>{wc}</td><td>{s_pct:.1f}%</td><td>{w_pct:.1f}%</td></tr>"
            html += "</table></div>"
            st.markdown(html, unsafe_allow_html=True)

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

    # --- CALCULATIONS ---
    p_nsy, p_wt, pr_nsy, pr_wt, ch_gme, ch_wt = fetch_terminal_data()
    qn, pn, qw, pw, gp = st.session_state.qn, st.session_state.pn, st.session_state.qw, st.session_state.pw, st.session_state.gp

    total_shares, v_s_u, v_w_u = qn, qn * p_nsy, qw * p_wt
    t_v_u, t_c_u = v_s_u + v_w_u, (qn * gp) + (qw * pw)

    # --- COMMUNITY (Starting at zero + You) ---
    c_s, c_w = qn, qw
    c_gp_val = gp if qn > 0 else 0.0
    c_pw_val = pw if qw > 0 else 0.0
    
    c_v_s, c_v_w = c_s * p_nsy, c_w * p_wt
    c_t_v = c_v_s + c_v_w
    c_t_c = (c_s * c_gp_val) + (c_w * c_pw_val)

    # --- TABS ---
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 GME", "📜 WARRANTS", "🇺🇸 US", "📋 DATA", "🌕 WEN MOON US", "🗃️ WEN MOON DATA"])

    def draw_live(price, prev, chart):
        pct = ((price - prev) / prev) * 100 if prev > 0 else 0
        diff, clr = price - prev, ("#00FF00" if price >= prev else "#FF0000")
        
        # PRICE SLICING & ANIMATION SELECTION
        price_str = f"{price:.2f}"
        p_int, p_dec = price_str.split('.')
        
        sz = min(100 + (abs(pct) * 10), 180)
        # Use neon-flash-red if price is down
        anim_class = "nuclear-neon" if pct >= 0 else "neon-flash-red"
        icn = f"<div style='animation: {anim_class} 1.5s infinite;'><div style='font-size:{sz}px;'>🚀</div></div>" if pct >= 0 else f"<img src='data:image/jpeg;base64,{get_b64('Screenshot_20260216_163106_Discord.jpg')}' style='height:{sz}px; animation:{anim_class} 1s infinite;'>"
        
        st.markdown(f"""
        <div style='display:flex; justify-content:center; align-items:center; gap:20px; margin-top:30px;'>
            <div style='text-align:right; white-space:nowrap;'>
                <span style='font-size:50px; color:{clr}; text-shadow:0 0 20px {clr}; font-weight:bold; vertical-align:top;'>$</span><span style='font-size:100px; color:{clr}; text-shadow:0 0 20px {clr}; font-weight:bold;'>{p_int}.</span><span style='font-size:80px; color:{clr}; text-shadow:0 0 20px {clr}; font-weight:bold;'>{p_dec}</span>
                <h3 style='color:{clr}; margin-top:0px;'>${diff:+.2f} {pct:+.2f}%</h3>
            </div>
            {icn}
        </div>
        """, unsafe_allow_html=True)
        
        if not chart.empty:
            fig, ax = plt.subplots(figsize=(10, 2.5), facecolor='black'); ax.set_facecolor('black')
            v = chart.dropna().values
            ax.bar(np.arange(len(v)), v - np.min(v)*0.99, bottom=np.min(v)*0.99, color=clr, width=0.8); ax.axis('off'); st.pyplot(fig); plt.close(fig) # Fix duplication

    @st.fragment(run_every="30s")
    def render_content():
        with tab1: draw_live(p_nsy, pr_nsy, ch_gme)
        with tab2: draw_live(p_wt, pr_wt, ch_wt)
        with tab3:
            # --- PERFECT US PIE CHART ---
            s_c = qn * gp
            w_c = qw * pw
            s_pl = v_s_u - s_c
            w_pl = v_w_u - w_c
            t_pl = t_v_u - t_c_u
            
            s_pct_pl = (s_pl / s_c * 100) if s_c > 0 else 0
            w_pct_pl = (w_pl / w_c * 100) if w_c > 0 else 0
            t_pct_pl = (t_pl / t_c_u * 100) if t_c_u > 0 else 0

            fig4 = plt.figure(figsize=(32, 12)); fig4.patch.set_facecolor("#0f172a")
            gs = GridSpec(1, 3, width_ratios=[1.2, 1.5, 1.2])
            
            al = fig4.add_subplot(gs[0]); al.set_facecolor("#0f172a"); al.axis('off')
            al.text(0.9, 0.85, "GameStop Shares (GME)", color="#66c2a5", fontsize=50, ha="right", weight="bold")
            al.text(0.9, 0.65, f"Val: ${v_s_u:,.2f}", color="white", fontsize=45, ha="right", weight="bold")
            al.text(0.9, 0.45, f"Qty: {qn:,} | Price: ${p_nsy:.2f}", color="#66c2a5", fontsize=45, ha="right", weight="bold")
            al.text(0.9, 0.25, f"Avg Cost: ${gp:.2f}", color="white", fontsize=45, ha="right", weight="bold")
            c_s_pl = "#00FF00" if s_pl >= 0 else "#FF0000"
            al.text(0.9, 0.05, f"P/L: {s_pl:+,.2f} ({s_pct_pl:+.2f}%)", color=c_s_pl, fontsize=45, ha="right", weight="bold")

            ac = fig4.add_subplot(gs[1]); ac.set_facecolor("#0f172a")
            wedges, texts, autotexts = ac.pie(
                [v_s_u if v_s_u > 0 else 0.01, v_w_u if v_w_u > 0 else 0.01], 
                colors=["#4ade80", "#166534"], radius=1.3, 
                wedgeprops=dict(width=0.4, edgecolor="#0f172a"),
                autopct='%1.0f%%', pctdistance=0.8
            )
            for autotext in autotexts:
                autotext.set_color('white'); autotext.set_fontsize(40); autotext.set_weight('bold')
            
            ac.text(0, 0.2, "Total Value:", fontsize=35, color="white", ha="center")
            ac.text(0, -0.05, f"${t_v_u:,.2f}", fontsize=65, color="white", ha="center", weight="bold")
            c_t_pl = "#00FF00" if t_pl >= 0 else "#FF0000"
            ac.text(0, -0.3, f"{t_pl:+,.2f} ({t_pct_pl:+.2f}%)", fontsize=40, color=c_t_pl, ha="center", weight="bold")

            ar = fig4.add_subplot(gs[2]); ar.set_facecolor("#0f172a"); ar.axis('off')
            ar.text(0.1, 0.85, "Warrants (GME-WT)", color="#66c2a5", fontsize=50, ha="left", weight="bold")
            ar.text(0.1, 0.65, f"Val: ${v_w_u:,.2f}", color="white", fontsize=45, ha="left", weight="bold")
            ar.text(0.1, 0.45, f"Qty: {qw:,} | Price: ${p_wt:.2f}", color="#66c2a5", fontsize=45, ha="left", weight="bold")
            ar.text(0.1, 0.25, f"Avg Cost: ${pw:.3f}", color="white", fontsize=45, ha="left", weight="bold")
            c_w_pl = "#00FF00" if w_pl >= 0 else "#FF0000"
            ar.text(0.1, 0.05, f"P/L: {w_pl:+,.2f} ({w_pct_pl:+.2f}%)", color=c_w_pl, fontsize=45, ha="left", weight="bold")

            st.pyplot(fig4, bbox_inches='tight', pad_inches=0.1); plt.close(fig4) # Fix duplication
        
        with tab4:
            html_d = f"""<div class='table-wrapper'><table class='ldb-t'>
            <tr><th>Ticker</th><th>Qty</th><th>Avg</th><th>Price</th><th>Cost</th><th>Value</th><th>P/L</th><th>%</th></tr>
            <tr><td>GME</td><td>{qn:,}</td><td>${gp:.2f}</td><td>${p_nsy:.2f}</td><td>${s_c:,.2f}</td><td>${v_s_u:,.2f}</td><td style="color:{'#00FF00' if s_pl>=0 else '#FF0000'};">${s_pl:+,.2f}</td><td>{v_s_u/t_v_u*100 if t_v_u>0 else 0:.1f}%</td></tr>
            <tr><td>WARRANT</td><td>{qw:,}</td><td>${pw:.3f}</td><td>${p_wt:.2f}</td><td>${w_c:,.2f}</td><td>${v_w_u:,.2f}</td><td style="color:{'#00FF00' if w_pl>=0 else '#FF0000'};">${w_pl:+,.2f}</td><td>{v_w_u/t_v_u*100 if t_v_u>0 else 0:.1f}%</td></tr>
            <tr class='podium'><td>TOTAL</td><td></td><td></td><td></td><td>${t_c_u:,.2f}</td><td>${t_v_u:,.2f}</td><td style="color:{'#00FF00' if t_pl>=0 else '#FF0000'};">${t_pl:+,.2f}</td><td>100%</td></tr>
            </table></div>"""
            st.markdown(html_d, unsafe_allow_html=True)
            
        with tab5:
            # --- WEN MOON PIE CHART ---
            cw_c = c_w * c_pw_val
            cs_c = c_s * c_gp_val
            c_pl_s = c_v_s - cs_c
            c_pl_w = c_v_w - cw_c
            ct_pl = c_t_v - c_t_c
            
            c_s_pct = (c_pl_s / cs_c * 100) if cs_c > 0 else 0
            c_w_pct = (c_pl_w / cw_c * 100) if cw_c > 0 else 0
            ct_pct = (ct_pl / c_t_c * 100) if c_t_c > 0 else 0

            fig_c4 = plt.figure(figsize=(32, 12)); fig_c4.patch.set_facecolor("#0f172a")
            gs_c = GridSpec(1, 3, width_ratios=[1.2, 1.5, 1.2])
            
            al_c = fig_c4.add_subplot(gs_c[0]); al_c.set_facecolor("#0f172a"); al_c.axis('off')
            al_c.text(0.9, 0.85, "Community Shares (GME)", color="#66c2a5", fontsize=50, ha="right", weight="bold")
            al_c.text(0.9, 0.65, f"Val: ${c_v_s:,.2f}", color="white", fontsize=45, ha="right", weight="bold")
            al_c.text(0.9, 0.45, f"Qty: {c_s:,} | Price: ${p_nsy:.2f}", color="#66c2a5", fontsize=45, ha="right", weight="bold")
            al_c.text(0.9, 0.25, f"Avg Cost: ${c_gp_val:.2f}", color="white", fontsize=45, ha="right", weight="bold")
            cc_s_pl = "#00FF00" if c_pl_s >= 0 else "#FF0000"
            al_c.text(0.9, 0.05, f"P/L: {c_pl_s:+,.2f} ({c_s_pct:+.2f}%)", color=cc_s_pl, fontsize=45, ha="right", weight="bold")

            ac_c = fig_c4.add_subplot(gs_c[1]); ac_c.set_facecolor("#0f172a")
            wedges_c, texts_c, autotexts_c = ac_c.pie(
                [c_v_s if c_v_s > 0 else 0.01, c_v_w if c_v_w > 0 else 0.01], 
                colors=["#4ade80", "#166534"], radius=1.3, 
                wedgeprops=dict(width=0.4, edgecolor="#0f172a"),
                autopct='%1.0f%%', pctdistance=0.8
            )
            for autotext in autotexts_c:
                autotext.set_color('white'); autotext.set_fontsize(40); autotext.set_weight('bold')
            
            ac_c.text(0, 0.2, "WEN MOON Value:", fontsize=35, color="white", ha="center")
            ac_c.text(0, -0.05, f"${c_t_v:,.2f}", fontsize=65, color="white", ha="center", weight="bold")
            cc_t_pl = "#00FF00" if ct_pl >= 0 else "#FF0000"
            ac_c.text(0, -0.3, f"{ct_pl:+,.2f} ({ct_pct:+.2f}%)", fontsize=40, color=cc_t_pl, ha="center", weight="bold")

            ar_c = fig_c4.add_subplot(gs_c[2]); ar_c.set_facecolor("#0f172a"); ar_c.axis('off')
            ar_c.text(0.1, 0.85, "Community Warrants", color="#66c2a5", fontsize=50, ha="left", weight="bold")
            ar_c.text(0.1, 0.65, f"Val: ${c_v_w:,.2f}", color="white", fontsize=45, ha="left", weight="bold")
            ar_c.text(0.1, 0.45, f"Qty: {c_w:,} | Price: ${p_wt:.2f}", color="#66c2a5", fontsize=45, ha="left", weight="bold")
            ar_c.text(0.1, 0.25, f"Avg Cost: ${c_pw_val:.3f}", color="white", fontsize=45, ha="left", weight="bold")
            cc_w_pl = "#00FF00" if c_pl_w >= 0 else "#FF0000"
            ar_c.text(0.1, 0.05, f"P/L: {c_pl_w:+,.2f} ({c_w_pct:+.2f}%)", color=cc_w_pl, fontsize=45, ha="left", weight="bold")

            st.pyplot(fig_c4, bbox_inches='tight', pad_inches=0.1); plt.close(fig_c4) # Fix duplication
            
        with tab6:
            html_w = f"""<div class='table-wrapper'><table class='ldb-t'>
            <tr><th>Ticker</th><th>Qty</th><th>Avg</th><th>Price</th><th>Cost</th><th>Value</th><th>P/L</th><th>%</th></tr>
            <tr><td>GME</td><td>{c_s:,}</td><td>${c_gp_val:.2f}</td><td>${p_nsy:.2f}</td><td>${cs_c:,.2f}</td><td>${c_v_s:,.2f}</td><td style="color:{'#00FF00' if c_pl_s>=0 else '#FF0000'};">${c_pl_s:+,.2f}</td><td>{c_v_s/c_t_v*100 if c_t_v>0 else 0:.1f}%</td></tr>
            <tr><td>WARRANT</td><td>{c_w:,}</td><td>${c_pw_val:.3f}</td><td>${p_wt:.2f}</td><td>${cw_c:,.2f}</td><td>${c_v_w:,.2f}</td><td style="color:{'#00FF00' if c_pl_w>=0 else '#FF0000'};">${c_pl_w:+,.2f}</td><td>{c_v_w/c_t_v*100 if c_t_v>0 else 0:.1f}%</td></tr>
            <tr class='podium'><td>TOTAL</td><td></td><td></td><td></td><td>${c_t_c:,.2f}</td><td>${c_t_v:,.2f}</td><td style="color:{'#00FF00' if ct_pl>=0 else '#FF0000'};">${ct_pl:+,.2f}</td><td>100%</td></tr>
            </table></div>"""
            st.markdown(html_w, unsafe_allow_html=True)

    render_content()
