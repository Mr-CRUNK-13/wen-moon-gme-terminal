import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- CORE CONFIG ---
st.set_page_config(page_title="WEN MOON V63", layout="wide", initial_sidebar_state="collapsed")

# --- MOBILE OPTIMIZED CSS ---
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #050505; color: white; }
    .stTabs [data-baseweb="tab-list"] { background-color: #050505; }
    .stTabs [data-baseweb="tab"] { background-color: #0e1621; color: white; border: 1px solid #0259c7; border-radius: 5px; }
    .stTabs [aria-selected="true"] { background-color: #0259c7 !important; border-color: #00FF00 !important; }
    
    /* Dashboard Boxes */
    .metric-card { background-color: #0f172a; border: 1px solid #0259c7; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 10px; }
    .metric-title { color: #66c2a5; font-size: 14px; text-transform: uppercase; margin-bottom: 5px; }
    .metric-value { color: white; font-size: 24px; font-weight: bold; }
    
    /* Financial Table Styling */
    .table-wrapper { overflow-x: auto; margin-top: 10px; }
    .ldb-t { width: 100%; border-collapse: collapse; font-family: monospace; font-size: 12px; }
    .ldb-t th { background-color: #1e293b; color: #00FF00; padding: 10px; border-bottom: 2px solid #0259c7; }
    .ldb-t td { padding: 8px; text-align: center; border-bottom: 1px solid #1e293b; }
</style>
""", unsafe_allow_html=True)

# --- RESILIENT DATA ENGINE ---
@st.cache_data(ttl=60)
def get_data():
    try:
        gme = yf.Ticker("GME")
        wt = yf.Ticker("GME-WT")
        hist = gme.history(period="2d")
        w_hist = wt.history(period="2d")
        
        info = gme.info if gme.info else {}
        w_info = wt.info if wt.info else {}
        
        p = hist['Close'].iloc[-1]
        pr = hist['Close'].iloc[-2]
        ch = ((p - pr) / pr) * 100
        
        pw = w_hist['Close'].iloc[-1] if not w_hist.empty else 0.00
        prw = w_hist['Close'].iloc[-2] if len(w_hist) > 1 else pw
        chw = ((pw - prw) / prw) * 100 if prw > 0 else 0
        
        return p, pw, ch, chw, info, w_info, gme.options
    except:
        return 24.50, 3.50, 0.0, 0.0, {}, {}, []

p, pw, ch, chw, gme_info, wt_info, opt_dates = get_data()

# --- SIDEBAR CONTROL ---
with st.sidebar:
    st.header("USER PORTFOLIO")
    u_name = st.text_input("Ape Nickname", value="Ape_1")
    q_s = st.number_input("GME Shares", value=5500)
    p_s = st.number_input("Avg Cost ($)", value=20.45)
    q_w = st.number_input("GME Warrants", value=6000)
    p_w = st.number_input("Warrant Avg Cost ($)", value=3.000, format="%.3f")
    st.subheader("RECENT PURCHASES")
    w_s = st.number_input("Weekly Shares", value=500)
    w_w = st.number_input("Weekly Warrants", value=1000)
    m_s = st.number_input("Monthly Shares", value=0)
    m_w = st.number_input("Monthly Warrants", value=0)

# --- DASHBOARD HEADER ---
st.markdown("<h1 style='text-align: center; color: #00FF00;'>💎 WEN MOON TERMINAL V63</h1>", unsafe_allow_html=True)

# Live Tickers
c1, c2 = st.columns(2)
with c1:
    color = "#00FF00" if ch >= 0 else "#FF0000"
    st.markdown(f"<div class='metric-card' style='border-color:{color}'><div class='metric-title'>GME LIVE</div><div class='metric-value' style='color:{color}'>${p:.2f} ({ch:+.2f}%)</div></div>", unsafe_allow_html=True)
with c2:
    wcolor = "#00FF00" if chw >= 0 else "#FF0000"
    st.markdown(f"<div class='metric-card' style='border-color:{wcolor}'><div class='metric-title'>WARRANT LIVE</div><div class='metric-value' style='color:{wcolor}'>${pw:.3f} ({chw:+.2f}%)</div></div>", unsafe_allow_html=True)

# --- COMMUNITY SUMMARY ---
st.markdown("""
<div class='metric-card' style='border: 2px solid #FFD700;'>
    <h2 style='color:#FFD700; margin:0;'>🌍 COMMUNITY SUMMARY</h2>
    <div style='display:flex; justify-content: space-around; flex-wrap: wrap; margin-top:15px;'>
        <div style='flex:1; min-width:140px;'>
            <h4 style='color:#00FF00;'>WEEKLY</h4>
            <p style='margin:0;'>Shares: +"""+str(w_s)+"""</p>
            <p style='margin:0;'>Warrants: +"""+str(w_w)+"""</p>
        </div>
        <div style='flex:1; min-width:140px;'>
            <h4 style='color:#0259c7;'>MONTHLY</h4>
            <p style='margin:0;'>Shares: +"""+str(m_s)+"""</p>
            <p style='margin:0;'>Warrants: +"""+str(m_w)+"""</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- PRO TABS ---
t1, t2, t3, t4 = st.tabs(["🏛️ GME DATA", "📊 NET INCOME", "⛓️ OPTIONS", "🎯 TARGETS"])

with t1:
    def n_a(val, dol=False, pct=False):
        if val is None or val == "N/A": return "N/A"
        if dol: return f"${val:,.2f}"
        if pct: return f"{val:.2f}%"
        return f"{val:,}"

    st.markdown("<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;'>", unsafe_allow_html=True)
    metrics = [
        ("Market Cap", n_a(gme_info.get('marketCap'), dol=True)),
        ("Shares Out.", n_a(gme_info.get('sharesOutstanding'))),
        ("Total Cash", n_a(gme_info.get('totalCash'), dol=True)),
        ("Total Debt", n_a(gme_info.get('totalDebt'), dol=True)),
        ("Short % Float", n_a(gme_info.get('shortPercentOfFloat', 0)*100, pct=True)),
        ("Free Cash Flow", n_a(gme_info.get('freeCashflow'), dol=True))
    ]
    for title, val in metrics:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>{title}</div><div class='metric-value'>{val}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with t2:
    st.markdown("<h4 style='text-align:center;'>Historical Net Income (M$)</h4>", unsafe_allow_html=True)
    inc_data = [
        {"Y": "2025", "Q1": 45, "Q2": 169, "Q3": 77, "Q4": None, "Res": 291},
        {"Y": "2024", "Q1": -32, "Q2": 15, "Q3": 17, "Q4": 131, "Res": 131},
        {"Y": "2023", "Q1": -51, "Q2": -3, "Q3": -3, "Q4": 63, "Res": 7}
    ]
    html = "<div class='table-wrapper'><table class='ldb-t'><tr><th>Year</th><th>Q1</th><th>Q2</th><th>Q3</th><th>Q4</th><th>Results</th></tr>"
    for r in inc_data:
        html += f"<tr><td>{r['Y']}</td>"
        for q in ["Q1", "Q2", "Q3", "Q4", "Res"]:
            v = r[q]
            if v is None: html += "<td>-</td>"
            else:
                bg = "#132a13" if v > 0 else "#2a1313" if v < 0 else "transparent"
                html += f"        <td style='background-color:{bg}'>{v:+}M</td>"
        html += "</tr>"
    st.markdown(html + "</table></div>", unsafe_allow_html=True)

with t3:
    if opt_dates:
        sel_date = st.selectbox("Expiry:", opt_dates)
        chain = yf.Ticker("GME").option_chain(sel_date)
        df = chain.calls
        df['diff'] = (df['strike'] - p).abs()
        atm = df['diff'].idxmin()
        st.dataframe(df.iloc[max(0, atm-12):min(len(df), atm+13)][['strike', 'lastPrice', 'volume', 'openInterest']], use_container_width=True)

with t4:
    col_a, col_b = st.columns(2)
    col_a.metric("Target High", n_a(gme_info.get('targetHighPrice'), dol=True))
    col_b.metric("Target Low", n_a(gme_info.get('targetLowPrice'), dol=True))
    st.info(f"Recommendation: {gme_info.get('recommendationKey', 'N/A').upper()}")
