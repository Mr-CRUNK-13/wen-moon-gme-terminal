import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- TERMINAL CONFIGURATION ---
st.set_page_config(page_title="WEN MOON TERMINAL V62", layout="wide", initial_sidebar_state="collapsed")

# --- INSTITUTIONAL NEON DESIGN (CSS) ---
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #050505; color: white; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #050505; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #0e1621; border: 1px solid #0259c7; border-radius: 5px; color: white; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #0259c7 !important; border-color: #00FF00 !important; }
    
    /* Bloomberg Style Tables */
    .table-wrapper { overflow-x: auto; margin-top: 10px; border: 1px solid #1e293b; border-radius: 8px; }
    .ldb-t { width: 100%; border-collapse: collapse; font-family: monospace; background-color: #0f172a; }
    .ldb-t th { background-color: #1e293b; color: #66c2a5; padding: 12px; text-align: center; border-bottom: 2px solid #0259c7; }
    .ldb-t td { padding: 10px; text-align: center; border-bottom: 1px solid #1e293b; color: white; }
    .podium { background-color: rgba(2, 89, 199, 0.2); font-weight: bold; }
    
    /* Neon Animation */
    @keyframes neon-text { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
</style>
""", unsafe_allow_html=True)

# --- CORE DATA ENGINE ---
@st.cache_data(ttl=60)
def fetch_terminal_data():
    try:
        gme = yf.Ticker("GME")
        wt = yf.Ticker("GME-WT")
        
        # Ticker Data
        g_h = gme.history(period="2d")
        w_h = wt.history(period="2d")
        
        p_n = g_h['Close'].iloc[-1]
        p_w = w_h['Close'].iloc[-1] if not w_h.empty else 0.001
        pr_n = g_h['Close'].iloc[-2]
        pr_w = w_h['Close'].iloc[-2] if len(w_h) > 1 else p_w
        
        v_n = g_h['Volume'].iloc[-1]
        v_w = w_h['Volume'].iloc[-1] if not w_h.empty else 0
        ch_n = ((p_n - pr_n) / pr_n) * 100
        ch_w = ((p_w - pr_w) / pr_w) * 100 if pr_w > 0 else 0
        
        # Professional Analytics
        adv = gme.info
        w_info = wt.info
        opts = gme.options
        ins = gme.insider_transactions
        fin = gme.quarterly_financials
        bs = gme.quarterly_balance_sheet
        earn = gme.earnings_dates
        
        return p_n, p_w, pr_n, pr_w, v_n, v_w, ch_n, ch_w, adv, w_info, opts, ins, fin, bs, earn
    except Exception:
        return 24.50, 3.50, 24.00, 3.40, 5000000, 100000, 2.0, 3.0, {}, {}, [], pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Initial Data Load
p_nsy, p_wt, pr_nsy, pr_wt, vol_n, vol_w, ch_gme, ch_wt, adv_info, wt_info, opts, ins, fin, bs, earn_dates = fetch_terminal_data()
# --- SIDEBAR: PORTFOLIO CONTROL ---
with st.sidebar:
    st.header("👤 USER PROFILE")
    u_n = st.text_input("Nickname", value=st.session_state.get("ape_name", "Ape_1"), key="ape_name")
    
    st.subheader("📦 ASSETS")
    qn = st.number_input("GME Shares", value=5500, step=1)
    pn = st.number_input("Avg Cost ($)", value=20.45, step=0.01)
    qw = st.number_input("GME Warrants", value=6000, step=1)
    pw = st.number_input("Warrant Avg Cost ($)", value=3.000, step=0.001, format="%.3f")
    
    st.subheader("🔥 ACCUMULATION (REPORTS)")
    col_w, col_m = st.columns(2)
    with col_w:
        st.session_state["weekly_s"] = st.number_input("Weekly Shares", value=500, step=1)
        st.session_state["weekly_w"] = st.number_input("Weekly Warrants", value=1000, step=1)
    with col_m:
        st.session_state["monthly_s"] = st.number_input("Monthly Shares", value=0, step=1)
        st.session_state["monthly_w"] = st.number_input("Monthly Warrants", value=0, step=1)

# --- CALCULATION LOGIC ---
t_v_u = (qn * p_nsy) + (qw * p_wt)
# Community Data Simulations
c_s, c_w = qn, qw 
c_gp_val, c_pw_val = pn, pw

# --- LIVE DISPLAY HELPER ---
def draw_live(price, prev_close, change, vol):
    color = "#00FF00" if change >= 0 else "#FF0000"
    arrow = "▲" if change >= 0 else "▼"
    st.markdown(f"""
    <div style="background-color: #000; border: 2px solid {color}; padding: 15px; border-radius: 10px; text-align: center; font-family: 'Courier New', monospace;">
        <h2 style="color: {color}; margin: 0; font-size: 35px; font-weight: bold;">${price:.2f}</h2>
        <p style="color: {color}; margin: 5px 0; font-size: 20px;">{arrow} {abs(change):.2f}%</p>
        <p style="color: #555; margin: 0; font-size: 14px;">VOL: {vol:,}</p>
    </div>
    """, unsafe_allow_html=True)

# --- MAIN INTERFACE SETUP ---
st.markdown(f"<h1 style='text-align: center; color: #00FF00; font-family: monospace;'>💎 WEN MOON TERMINAL V62 💎</h1>", unsafe_allow_html=True)

def render_content():
    # Live Tickers Grid
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        st.markdown("<h4 style='text-align:center; color:#66c2a5;'>📊 GME LIVE</h4>", unsafe_allow_html=True)
        @st.fragment(run_every="30s")
        def live_gme():
            p, _, pr, _, _, _, ch, _, _, _, _, _, _, _, _ = fetch_terminal_data()
            draw_live(p, pr, ch, vol_n)
        live_gme()

    with row1_col2:
        st.markdown("<h4 style='text-align:center; color:#66c2a5;'>📈 WARRANT LIVE</h4>", unsafe_allow_html=True)
        @st.fragment(run_every="30s")
        def live_wt():
            _, p, _, pr, _, _, _, ch, _, _, _, _, _, _, _ = fetch_terminal_data()
            draw_live(p, pr, ch, vol_w)
        live_wt()

    # Functional Containers
    ph7 = st.empty()  # Leaderboard
    ph8 = st.empty()  # Summary
    ph9 = st.empty()  # GME PRO
    ph10 = st.empty() # Options
    ph11 = st.empty() # Consensus
    ph12 = st.empty() # Insiders
    with ph7.container():
        lb_tabs_term = st.tabs(["🌍 GENERAL", "📅 MONTHLY", "📆 WEEKLY"])
        u_name = st.session_state.get("ape_name", "Anonymous")
        # Local database simulation
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
        total_holders = len(real_db)
        avg_s_per_person = c_s / total_holders if total_holders > 0 else 0
        avg_w_per_person = c_w / total_holders if total_holders > 0 else 0
        
        # Pull data from sidebar inputs
        w_s = st.session_state.get("weekly_s", 0)
        w_w = st.session_state.get("weekly_w", 0)
        m_s = st.session_state.get("monthly_s", 0)
        m_w = st.session_state.get("monthly_w", 0)

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
                    <p style="margin: 10px 0; font-size: 18px;">Avg Cost: <strong style="color: white;">${c_gp_val:.2f}</strong></p>
                    <p style="margin: 10px 0; font-size: 18px;">Avg Shares / Person: <strong style="color: white;">{avg_s_per_person:,.0f}</strong></p>
                </div>
                <div style="background-color: #0e1621; padding: 20px; border-radius: 8px; border: 2px solid #006400; flex: 1 1 300px; text-align: center;">
                    <h4 style="color: #006400; margin-top: 0; font-size: 24px; font-weight: bold;">GME WARRANTS</h4>
                    <p style="margin: 10px 0; font-size: 18px;">Total Warrants: <strong style="color: white;">{c_w:,}</strong></p>
                    <p style="margin: 10px 0; font-size: 18px;">Avg Cost: <strong style="color: white;">${c_pw_val:.3f}</strong></p>
                    <p style="margin: 10px 0; font-size: 18px;">Avg Warrants / Person: <strong style="color: white;">{avg_w_per_person:,.0f}</strong></p>
                </div>
            </div>
            <div style="background-color: #0e1621; padding: 20px; border-radius: 8px; border: 1px solid #FFD700; text-align: center; margin-top: 20px;">
                <h4 style="color: #FFD700; margin-top: 0; font-size: 24px; font-weight: bold;">🔥 RECENT PURCHASES</h4>
                <div style="display: flex; justify-content: space-around; margin-top: 15px; flex-wrap: wrap; gap: 10px;">
                    <div style="background-color: #0f172a; padding: 15px; border-radius: 5px; flex: 1; min-width: 140px; border: 1px solid #00FF00;">
                        <h5 style="color: #00FF00; font-size: 18px; margin: 0 0 10px 0;">WEEKLY</h5>
                        <p style="margin: 5px 0; font-size: 16px;">Shares: <strong style="color: white;">+{w_s:,}</strong></p>
                        <p style="margin: 5px 0; font-size: 16px;">Warrants: <strong style="color: white;">+{w_w:,}</strong></p>
                    </div>
                    <div style="background-color: #0f172a; padding: 15px; border-radius: 5px; flex: 1; min-width: 140px; border: 1px solid #006400;">
                        <h5 style="color: #006400; font-size: 18px; margin: 0 0 10px 0;">MONTHLY</h5>
                        <p style="margin: 5px 0; font-size: 16px;">Shares: <strong style="color: white;">+{m_s:,}</strong></p>
                        <p style="margin: 5px 0; font-size: 16px;">Warrants: <strong style="color: white;">+{m_w:,}</strong></p>
                    </div>
                </div>
            </div>
        </div>
        """
        st.markdown(html_summary, unsafe_allow_html=True)
    with ph9.container():
        def fmt(val, is_pct=False, is_dol=False):
            if val == 'N/A' or pd.isna(val) or val is None: return "N/A"
            try:
                v = float(val)
                if is_pct: return f"{v*100:.2f}%"
                if is_dol: return f"${v:,.2f}"
                return f"{v:,.0f}"
            except: return str(val)

        st.markdown("<h2 style='text-align:center; color:#00FF00; font-family:monospace;'>🧬 GME PRO DATA TERMINAL</h2>", unsafe_allow_html=True)
        ptab1, ptab2, ptab3 = st.tabs(["🏛️ FUNDAMENTALS", "📜 WARRANTS", "📊 NET INCOME"])
        
        with ptab1:
            html_gme = f"""
            <style>
                .pro-g {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 15px; }}
                .pb {{ background: #0e1621; border: 1px solid #00FF00; border-radius: 8px; padding: 12px; text-align: center; }}
                .pb h4 {{ color: #00FF00; margin: 0; font-size: 13px; font-family: monospace; text-transform: uppercase; }}
                .pb p {{ color: white; font-size: 18px; font-weight: bold; margin: 5px 0 0 0; }}
            </style>
            <div class="pro-g">
                <div class="pb"><h4>Market Cap</h4><p>{fmt(adv_info.get('marketCap'), is_dol=True)}</p></div>
                <div class="pb"><h4>Shares Out.</h4><p>{fmt(adv_info.get('sharesOutstanding'))}</p></div>
                <div class="pb"><h4>Float Shares</h4><p>{fmt(adv_info.get('floatShares'))}</p></div>
                <div class="pb"><h4>Total Cash</h4><p>{fmt(adv_info.get('totalCash'), is_dol=True)}</p></div>
                <div class="pb"><h4>Total Debt</h4><p>{fmt(adv_info.get('totalDebt'), is_dol=True)}</p></div>
                <div class="pb"><h4>Total Revenue</h4><p>{fmt(adv_info.get('totalRevenue'), is_dol=True)}</p></div>
                <div class="pb"><h4>Net Income</h4><p>{fmt(adv_info.get('netIncomeToCommon'), is_dol=True)}</p></div>
                <div class="pb"><h4>Free Cash Flow</h4><p>{fmt(adv_info.get('freeCashflow'), is_dol=True)}</p></div>
                <div class="pb"><h4>Trailing EPS</h4><p>{fmt(adv_info.get('trailingEps'), is_dol=True)}</p></div>
                <div class="pb"><h4>Forward EPS</h4><p>{fmt(adv_info.get('forwardEps'), is_dol=True)}</p></div>
                <div class="pb"><h4>Short % Float</h4><p>{fmt(adv_info.get('shortPercentOfFloat'), is_pct=True)}</p></div>
                <div class="pb"><h4>Days to Cover</h4><p>{fmt(adv_info.get('shortRatio'))}</p></div>
                <div class="pb"><h4>52W High</h4><p>{fmt(adv_info.get('fiftyTwoWeekHigh'), is_dol=True)}</p></div>
                <div class="pb"><h4>52W Low</h4><p>{fmt(adv_info.get('fiftyTwoWeekLow'), is_dol=True)}</p></div>
                <div class="pb"><h4>Insider %</h4><p>{fmt(adv_info.get('heldPercentInsiders'), is_pct=True)}</p></div>
                <div class="pb"><h4>Inst. %</h4><p>{fmt(adv_info.get('heldPercentInstitutions'), is_pct=True)}</p></div>
            </div>"""
            st.markdown(html_gme, unsafe_allow_html=True)
            
        with ptab2:
            html_wt = f"""
            <div class="pro-g">
                <div class="pb" style="border-color:#006400;"><h4 style="color:#006400;">Current Price</h4><p>${p_wt:.3f}</p></div>
                <div class="pb" style="border-color:#006400;"><h4 style="color:#006400;">Today's Volume</h4><p>{fmt(wt_info.get('volume'))}</p></div>
                <div class="pb" style="border-color:#006400;"><h4 style="color:#006400;">Bid / Ask</h4><p>{fmt(wt_info.get('bid'))} / {fmt(wt_info.get('ask'))}</p></div>
                <div class="pb" style="border-color:#006400;"><h4 style="color:#006400;">52W High</h4><p>{fmt(wt_info.get('fiftyTwoWeekHigh'), is_dol=True)}</p></div>
                <div class="pb" style="border-color:#006400;"><h4 style="color:#006400;">52W Low</h4><p>{fmt(wt_info.get('fiftyTwoWeekLow'), is_dol=True)}</p></div>
                <div class="pb" style="border-color:#006400;"><h4 style="color:#006400;">Prev Close</h4><p>{fmt(wt_info.get('previousClose'), is_dol=True)}</p></div>
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
                        c = "#132a13" if val > 0 else "#2a1313" if val < 0 else "transparent"
                        html_inc += f"<td style='background-color:{c}; color:white;'>{val if val < 0 else f'+{val}'}M</td>"
                html_inc += "</tr>"
            st.markdown(html_inc + "</table></div>", unsafe_allow_html=True)
    with ph10.container():
        st.markdown("<h2 style='text-align:center; color:#00FF00; font-family:monospace;'>⛓️ OPTIONS CHAIN (ATM CENTERED)</h2>", unsafe_allow_html=True)
        if opts:
            selected_expiry = st.selectbox("📅 SELECT EXPIRATION DATE:", opts, key="opt_exp_selector")
            try:
                tk = yf.Ticker("GME")
                chain = tk.option_chain(selected_expiry)
                # Dynamic Centering Logic: +/- 12 strikes around market price
                for df_opt, title, color in [(chain.calls, "🔥 CALLS", "#00FF00"), (chain.puts, "🩸 PUTS", "#FF0000")]:
                    df_opt['diff'] = (df_opt['strike'] - p_nsy).abs()
                    atm_idx = df_opt['diff'].idxmin()
                    start_idx = max(0, atm_idx - 12)
                    end_idx = min(len(df_opt), atm_idx + 13)
                    display_df = df_opt.iloc[start_idx:end_idx]
                    
                    html_opt = f"<h4 style='color:{color}; text-align:center;'>{title}</h4><div class='table-wrapper'><table class='ldb-t' style='font-size:13px;'><tr><th>Strike</th><th>Last</th><th>Vol</th><th>OI</th><th>IV</th></tr>"
                    for _, r in display_df.iterrows():
                        is_atm = "style='background-color:rgba(255,255,255,0.1);'" if abs(r['strike']-p_nsy) < 0.6 else ""
                        html_opt += f"<tr {is_atm}><td>${r['strike']:.1f}</td><td>${r['lastPrice']:.2f}</td><td>{fmt(r['volume'])}</td><td>{fmt(r['openInterest'])}</td><td>{r['impliedVolatility']*100:.1f}%</td></tr>"
                    st.markdown(html_opt + "</table></div>", unsafe_allow_html=True)
            except Exception:
                st.warning("Options feed temporarily unavailable.")

    with ph11.container():
        st.markdown("<h2 style='text-align:center; color:#00FF00; font-family:monospace;'>🏦 WALL STREET CONSENSUS</h2>", unsafe_allow_html=True)
        ctab1, ctab2 = st.tabs(["🎯 PRICE TARGETS", "🗃️ RAW STATEMENTS"])
        with ctab1:
            col_t1, col_t2, col_t3 = st.columns(3)
            col_t1.metric("Target High", fmt(adv_info.get('targetHighPrice'), is_dol=True))
            col_t2.metric("Target Mean", fmt(adv_info.get('targetMeanPrice'), is_dol=True))
            col_t3.metric("Target Low", fmt(adv_info.get('targetLowPrice'), is_dol=True))
            st.info(f"Recommendation: {adv_info.get('recommendationKey', 'N/A').upper()} (based on {adv_info.get('numberOfAnalystOpinions', 0)} analysts)")
        with ctab2:
            if not fin.empty:
                st.dataframe(fin.iloc[:10, :3].astype(str), use_container_width=True)

    with ph12.container():
        st.markdown("<h2 style='text-align:center; color:#00FF00; font-family:monospace;'>🕵️ INSIDER TRADING</h2>", unsafe_allow_html=True)
        if not ins.empty:
            st.dataframe(ins.head(10).astype(str), use_container_width=True)

# --- ENGINE LAUNCH ---
render_content()
