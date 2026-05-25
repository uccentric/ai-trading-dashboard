import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz

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
            hist = stock.history(period="3mo") # Pull 3 months to be safe
            
            # Get earnings dates
            earnings_dates = []
            try:
                edates = stock.earnings_dates
                if edates is not None:
                    # Filter to dates within our history + next 30 days
                    # Reset index to get dates
                    df_dates = edates.reset_index()
                    for idx, row in df_dates.iterrows():
                        edate = row['Earnings Date']
                        if pd.notnull(edate):
                            earnings_dates.append(edate)
            except:
                pass
            
            if not hist.empty:
                hist = hist.tail(30) # Only chart last 30 days
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                pct_change = ((current_price - prev_price) / prev_price) * 100
                data[ticker] = {
                    "price": current_price,
                    "change": pct_change,
                    "history": hist,
                    "earnings": earnings_dates
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
st.header("📈 30-Day Trend Charts with Earnings")

chart_cols = st.columns(3)
for i, ticker in enumerate(tickers):
    if ticker in data:
        with chart_cols[i % 3]:
            st.subheader(ticker)
            hist = data[ticker]['history']
            earnings = data[ticker]['earnings']
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='Price', line=dict(color='#00b4d8', width=2)))
            
            # Find earnings dates in the current window
            min_date = hist.index.min()
            max_date = hist.index.max() + timedelta(days=5) # pad right side
            
            plotted_earnings = False
            for edate in earnings:
                # timezone aware comparison
                if edate.tzinfo is None:
                    edate = edate.replace(tzinfo=pytz.UTC)
                
                # Check if it falls near our chart
                if min_date.date() <= edate.date() <= max_date.date():
                    fig.add_vline(x=edate, line_dash="dash", line_color="red", annotation_text="Earnings", annotation_position="top right")
                    # Add a marker on the line
                    # nearest date
                    nearest_idx = hist.index.get_indexer([edate], method='nearest')[0]
                    if nearest_idx >= 0 and nearest_idx < len(hist):
                        y_val = hist['Close'].iloc[nearest_idx]
                        fig.add_trace(go.Scatter(x=[edate], y=[y_val], mode='markers', name='Earnings', marker=dict(color='red', size=10, symbol='star')))
                        plotted_earnings = True

            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            if not plotted_earnings:
                # Show next earnings date as text if available
                future_dates = [d for d in earnings if d.date() >= datetime.now().date()]
                if future_dates:
                    next_e = min(future_dates)
                    st.caption(f"Next Earnings: {next_e.strftime('%Y-%m-%d')}")

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
