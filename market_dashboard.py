import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Tactical AI & Space Dashboard", layout="wide", page_icon="🚀")

st.title("🧠 Tactical AI & Space Dashboard")
st.markdown("Live tracking for your core AI, Power, and Space infrastructure holdings.")

tickers = ['HIMX', 'BE', 'FCEL', 'RKLB', 'ALAB', 'ANET', 'RGTI', 'BBAI', 'NBIS']

@st.cache_data(ttl=300)
def get_stock_data(tickers):
    data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1mo")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                pct_change = ((current_price - prev_price) / prev_price) * 100
                data[ticker] = {
                    "price": current_price,
                    "change": pct_change,
                    "history": hist['Close']
                }
        except Exception as e:
            pass
    return data

data = get_stock_data(tickers)

st.header("Live Market Overview")
cols = st.columns(4)

for i, ticker in enumerate(tickers):
    if ticker in data:
        col = cols[i % 4]
        price = data[ticker]['price']
        change = data[ticker]['change']
        col.metric(label=ticker, value=f"${price:.2f}", delta=f"{change:.2f}%")

st.markdown("---")
st.header("📈 30-Day Trend Charts")

chart_cols = st.columns(3)
for i, ticker in enumerate(tickers):
    if ticker in data:
        with chart_cols[i % 3]:
            st.subheader(ticker)
            st.line_chart(data[ticker]['history'])

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.header("🎯 Tactical Analyst Notes")
    st.markdown("""
    * **Space / RKLB:** Strong setup going into the SpaceX IPO. Launch cadence accelerating.
    * **AI Power (BE / FCEL):** BE has parabolic momentum from Oracle/Nebius deals. Watch for pullbacks to enter. FCEL remains speculative.
    * **AI Backbone (ALAB / ANET):** Core AI infrastructure holdings. Steady accumulation as data center CapEx expands.
    * **Edge AI (HIMX):** Massive Q1 beat on WiseEye integration. Lock in partial profits if holding.
    * **Quantum / Defense (RGTI / BBAI):** Track government contracts and defense spending closely.
    """)

with col2:
    st.header("🏛️ AI & Space Regulatory Watch")
    st.info("**May 2026 Policy Radar**")
    st.markdown("""
    **Space Sector:**
    * **FCC Satellite Constellation Rules:** Monitoring spectrum allocation fights between terrestrial telecom and direct-to-cell providers (impacts ASTS, SpaceX).
    * **Space Debris Mitigation:** Tighter regulations expected for end-of-life deorbiting, which benefits launch providers (RKLB, SpaceX) via replacement cycles.

    **AI Infrastructure:**
    * **Data Center Grid Constraints:** State-level utility commissions are scrutinizing the massive power draw of AI data centers. Favorable fast-track permitting for on-site fuel cells (Bloom Energy) is a massive tailwind.
    * **CHIPS Act & Export Controls:** Recent $2B injection for domestic Quantum (RGTI ecosystem). Ongoing tightening of AI chip export bans to China (impacts Nvidia, ALAB).
    """)
