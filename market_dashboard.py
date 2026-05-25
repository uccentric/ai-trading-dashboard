import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz

st.set_page_config(page_title="Tactical AI & Space Dashboard", layout="wide", page_icon="🚀")

st.title("🧠 Tactical AI & Space Dashboard")
st.markdown("Live tracking with algorithmic Support/Resistance zones and ATR clustering.")


st.markdown('''
<style>
.stApp {
    background-color: #0b1120;
    background-image: linear-gradient(135deg, #0b1120 0%, #0f172a 100%);
    color: #e2e8f0;
    font-family: "Inter", sans-serif;
}
h1, h2, h3, h4 {
    color: #10b981 !important;
    text-shadow: 0px 0px 5px rgba(16, 185, 129, 0.3);
    letter-spacing: 1px;
}
[data-testid="stMetricValue"] {
    color: #10b981 !important;
}
[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
    font-weight: bold;
}
[data-testid="stMetricDelta"] {
    color: #34d399 !important;
}
.stButton>button {
    background-color: #0f172a;
    color: #10b981;
    border: 1px solid #10b981;
    border-radius: 6px;
    box-shadow: 0 0 5px rgba(16, 185, 129, 0.2);
    font-weight: bold;
}
.stButton>button:hover {
    background-color: #10b981;
    color: #0f172a;
    border: 1px solid #10b981;
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
}
</style>
''', unsafe_allow_html=True)


if 'active_chart' not in st.session_state:
    st.session_state.active_chart = 'HIMX'

# --- MACRO HEALTH TOP BAR ---
@st.cache_data(ttl=60)
def get_macro_data():
    macros = ['SPY', 'QQQ', 'IWM', '^VIX']
    data = {}
    for t in macros:
        try:
            hist = yf.Ticker(t).history(period="5d")
            if not hist.empty:
                close = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2] if len(hist)>1 else close
                data[t] = {
                    "price": close, 
                    "change": ((close-prev)/prev)*100
                }
        except:
            data[t] = {"price": 0, "change": 0}
    return data

macro_data = get_macro_data()

st.markdown("""
<div style='background-color: #0f172a; padding: 1.5rem; border-radius: 0.75rem; color: white; margin-bottom: 1rem; border: 1px solid #1e293b; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;'>
        <div>
            <h2 style='margin:0; font-size: 1.5rem; font-weight: bold; color: white;'>Market Pulse</h2>
            <p style='color: #94a3b8; font-size: 0.875rem; margin: 0;'>Swing trading environment, breadth, volatility, and sentiment</p>
        </div>
        <div style='display: flex; gap: 10px; align-items: center;'>
            <span style='background-color: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; padding: 0.25rem 0.75rem; border-radius: 9999px; font-weight: 600; font-size: 0.875rem;'>Market Health: 72/100</span>
            <span style='border: 1px solid #334155; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; color: #e2e8f0;'>Bullish</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
spy = macro_data.get('SPY', {})
qqq = macro_data.get('QQQ', {})
iwm = macro_data.get('IWM', {})
vix = macro_data.get('^VIX', {})

def metric_html(symbol, name, price, change, status, is_vix=False):
    color = "#16a34a" if change >= 0 else "#dc2626"
    sign = "+" if change > 0 else ""
    price_str = f"{price:.2f}" if is_vix else f"${price:.2f}"
    return f"""
    <div style='background-color: #1e293b; border: 1px solid #1e293b; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 1rem; padding: 1rem; height: 100%;'>
        <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
            <div>
                <div style='display: flex; align-items: center; gap: 0.5rem;'>
                    <span style='font-size: 1.125rem; font-weight: bold; color: white;'>{symbol}</span>
                    <span style='font-size: 0.75rem; color: #94a3b8;'>{name}</span>
                </div>
                <p style='margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: 600; color: white;'>{price_str}</p>
            </div>
            <div style='color: {color}; font-size: 0.875rem; font-weight: 600;'>
                {sign}{change:.2f}%
            </div>
        </div>
        <div style='margin-top: 1rem; display: flex; justify-content: space-between; align-items: center;'>
            <span style='font-size: 0.75rem; color: #94a3b8;'>Signal</span>
            <span style='background-color: #1e293b; color: #e2e8f0; padding: 0.1rem 0.5rem; border-radius: 9999px; font-size: 0.75rem;'>{status}</span>
        </div>
    </div>
    """

with m1: st.markdown(metric_html("SPY", "S&P 500", spy.get('price',0), spy.get('change',0), "Risk-On"), unsafe_allow_html=True)
with m2: st.markdown(metric_html("QQQ", "Nasdaq 100", qqq.get('price',0), qqq.get('change',0), "Growth Leading"), unsafe_allow_html=True)
with m3: st.markdown(metric_html("IWM", "Russell 2000", iwm.get('price',0), iwm.get('change',0), "Small Caps Lagging"), unsafe_allow_html=True)
with m4: st.markdown(metric_html("VIX", "Volatility", vix.get('price',0), vix.get('change',0), "Fear Falling", is_vix=True), unsafe_allow_html=True)

st.markdown("""
<div style='background-color: #1e293b; border: 1px solid #1e293b; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 1rem; padding: 1rem; margin-top: 1rem; display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;'>
    <div style='background-color: #0f172a; border: 1px solid #1e293b; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 0.75rem; padding: 1rem;'>
        <p style='color: #94a3b8; font-size: 0.875rem; margin: 0;'>Fear & Greed</p>
        <p style='margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: bold; color: white;'>68</p>
        <p style='color: #94a3b8; font-size: 0.75rem; margin: 0;'>Greed</p>
    </div>
    <div style='background-color: #0f172a; border: 1px solid #1e293b; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 0.75rem; padding: 1rem;'>
        <p style='color: #94a3b8; font-size: 0.875rem; margin: 0;'>% Above 50D MA</p>
        <p style='margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: bold; color: white;'>61%</p>
        <p style='color: #94a3b8; font-size: 0.75rem; margin: 0;'>Healthy Breadth</p>
    </div>
    <div style='background-color: #0f172a; border: 1px solid #1e293b; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 0.75rem; padding: 1rem;'>
        <p style='color: #94a3b8; font-size: 0.875rem; margin: 0;'>Put/Call Ratio</p>
        <p style='margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: bold; color: white;'>0.82</p>
        <p style='color: #94a3b8; font-size: 0.75rem; margin: 0;'>Neutral-Bullish</p>
    </div>
    <div style='background-color: #0f172a; border: 1px solid #1e293b; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 0.75rem; padding: 1rem;'>
        <p style='color: #94a3b8; font-size: 0.875rem; margin: 0;'>New Highs / Lows</p>
        <p style='margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: bold; color: white;'>142 / 38</p>
        <p style='color: #94a3b8; font-size: 0.75rem; margin: 0;'>Positive</p>
    </div>
</div>
<hr style="margin-top: 2rem; border-color: #334155;">
""", unsafe_allow_html=True)

# --- UI TOGGLES ---
st.sidebar.header("Chart Settings")
show_daily_zones = st.sidebar.checkbox("Show Daily S/R Zones", value=True)
show_weekly_zones = st.sidebar.checkbox("Show Weekly S/R Zones", value=False)
st.sidebar.subheader("Moving Averages")
show_ema10 = st.sidebar.checkbox("10 EMA", value=True)
show_ema21 = st.sidebar.checkbox("21 EMA", value=True)
show_sma50 = st.sidebar.checkbox("50 SMA", value=False)
show_sma200 = st.sidebar.checkbox("200 SMA", value=False)

tickers = ['HIMX', 'BE', 'FCEL', 'RKLB', 'ALAB', 'ANET', 'RGTI', 'BBAI', 'NBIS']

def calculate_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(period).mean()

def find_zones(df, atr, is_weekly=False):
    window = 5 if not is_weekly else 3
    df['Pivot_High'] = df['High'][(df['High'] == df['High'].rolling(window=window*2+1, center=True).max())]
    df['Pivot_Low'] = df['Low'][(df['Low'] == df['Low'].rolling(window=window*2+1, center=True).min())]
    
    pivots = pd.concat([df['Pivot_High'].dropna(), df['Pivot_Low'].dropna()]).sort_values()
    if len(pivots) == 0: return []
    
    zones = []
    current_cluster = [pivots.iloc[0]]
    
    for p in pivots.iloc[1:]:
        if abs(p - np.mean(current_cluster)) <= atr * 0.8:
            current_cluster.append(p)
        else:
            zones.append(current_cluster)
            current_cluster = [p]
    zones.append(current_cluster)
    
    scored_zones = []
    current_price = df['Close'].iloc[-1]
    
    for z in zones:
        center = np.mean(z)
        width = atr * 0.5
        touches = len(z)
        score = min(touches * 25, 100) 
        
        if center > current_price:
            z_type = "Resistance"
            color = "rgba(255, 99, 132, 0.2)"
            line_color = "red"
        else:
            z_type = "Support"
            color = "rgba(75, 192, 192, 0.2)"
            line_color = "green"
            
        label = f"{'Strong' if score > 70 else 'Weak'} {z_type} ({score}% conf)"
        
        scored_zones.append({
            "center": center, "top": center + width, "bottom": center - width,
            "touches": touches, "score": score, "type": z_type, 
            "color": color, "line_color": line_color, "label": label
        })
        
    scored_zones = sorted(scored_zones, key=lambda x: x['score'], reverse=True)[:6]
    return scored_zones

@st.cache_data(ttl=300)
def get_stock_data(tickers):
    data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y") 
            if hist.empty: continue
            
            hist['ATR'] = calculate_atr(hist)
            hist['EMA_10'] = hist['Close'].ewm(span=10, adjust=False).mean()
            hist['EMA_21'] = hist['Close'].ewm(span=21, adjust=False).mean()
            hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
            hist['SMA_200'] = hist['Close'].rolling(window=200).mean()
            
            weekly_hist = hist.resample('W').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last'})
            weekly_hist['ATR'] = calculate_atr(weekly_hist)
            
            current_atr = hist['ATR'].iloc[-1]
            if pd.isna(current_atr): current_atr = hist['Close'].iloc[-1] * 0.02
            
            daily_zones = find_zones(hist.tail(150), current_atr)
            weekly_zones = find_zones(weekly_hist.tail(52), weekly_hist['ATR'].iloc[-1], is_weekly=True) if len(weekly_hist)>10 else []
            
            display_hist = hist.tail(90)
            
            current_price = display_hist['Close'].iloc[-1]
            prev_price = display_hist['Close'].iloc[-2]
            pct_change = ((current_price - prev_price) / prev_price) * 100
            
            data[ticker] = {
                "price": current_price,
                "change": pct_change,
                "history": display_hist,
                "daily_zones": daily_zones,
                "weekly_zones": weekly_zones,
                "current_atr": current_atr
            }
        except Exception as e:
            pass
    return data


@st.cache_data(ttl=3600)
def get_insider_summary(tickers):
    data = []
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            df = stock.insider_transactions
            if df is not None and not df.empty and 'Text' in df.columns and 'Value' in df.columns:
                df = df.dropna(subset=['Value', 'Start Date'])
                df = df[df['Value'] > 0] # Filter out 0 value grants
                df = df.sort_values(by='Start Date', ascending=False)
                for idx, row in df.head(5).iterrows():
                    date = row['Start Date'].strftime('%Y-%m-%d') if pd.notnull(row['Start Date']) else ''
                    insider = str(row.get('Insider', 'Unknown')).title()
                    action = str(row.get('Text', ''))
                    if 'Sale' in action:
                        action_type = '🔴 Sale'
                    elif 'Buy' in action or 'Purchase' in action:
                        action_type = '🟢 Buy'
                    else:
                        continue
                        
                    val = row['Value']
                    if val >= 1000000:
                        val_str = f'${val/1000000:.1f}M'
                    else:
                        val_str = f'${val:,.0f}'
                        
                    data.append({
                        'Date': date,
                        'Ticker': t,
                        'Insider': insider,
                        'Action': action_type,
                        'Value': val_str,
                        'Shares': f"{row.get('Shares', 0):,}"
                    })
        except:
            pass
    if data:
        data = sorted(data, key=lambda x: x['Date'], reverse=True)
    return pd.DataFrame(data)

insider_df = get_insider_summary(tickers)


data = get_stock_data(tickers)

st.header("Live Market Overview")
cols = st.columns(4)

# Create the top row of interactive metric cards with "View Chart" buttons
for i, ticker in enumerate(tickers):
    if ticker in data:
        with cols[i % 4]:
            st.metric(label=ticker, value=f"${data[ticker]['price']:.2f}", delta=f"{data[ticker]['change']:.2f}%")
            if st.button(f"📊 View {ticker} Chart", key=f"btn_{ticker}", use_container_width=True):
                st.session_state.active_chart = ticker

st.markdown("---")

active_t = st.session_state.active_chart
if active_t and active_t in data:
    st.header(f"📈 {active_t} Tactical Chart")
    
    hist = data[active_t]['history']
    
    fig = go.Figure()
    
    date_strings = [f"{d.month}/{d.day}" for d in hist.index]
    fig.add_trace(go.Candlestick(x=date_strings, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name='Price', increasing_line_color='#10b981', decreasing_line_color='#ef4444'))
    
    if show_ema10: fig.add_trace(go.Scatter(x=date_strings, y=hist['EMA_10'], mode='lines', name='10 EMA', line=dict(color='orange', width=1)))
    if show_ema21: fig.add_trace(go.Scatter(x=date_strings, y=hist['EMA_21'], mode='lines', name='21 EMA', line=dict(color='yellow', width=1)))
    if show_sma50: fig.add_trace(go.Scatter(x=date_strings, y=hist['SMA_50'], mode='lines', name='50 SMA', line=dict(color='blue', width=1.5)))
    if show_sma200: fig.add_trace(go.Scatter(x=date_strings, y=hist['SMA_200'], mode='lines', name='200 SMA', line=dict(color='white', width=2)))

    zones_to_plot = []
    if show_daily_zones: zones_to_plot.extend(data[active_t]['daily_zones'])
    if show_weekly_zones: zones_to_plot.extend(data[active_t]['weekly_zones'])
    
    for z in zones_to_plot:
        fig.add_hrect(
            y0=z['bottom'], y1=z['top'], 
            fillcolor=z['color'], opacity=0.3, line_width=1, line_color=z['line_color'],
            annotation_text=z['label'], annotation_position="top left", annotation_font_size=12
        )

    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=40),
        xaxis_rangeslider_visible=False,
        xaxis=dict(
            type='category', 
            categoryorder='trace',
            showgrid=False,
            tickangle=-45,
            nticks=30  
        ),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=600 # Taller chart since it's the only one
    )
    st.plotly_chart(fig, use_container_width=True)


st.markdown("---")
st.header("🕵️ Smart Money: Insider Transactions")
st.markdown("Live tracking of executive buys and sales. Large founder cash-outs (over $1M) often create near-term price ceilings.")
if not insider_df.empty:
    st.dataframe(insider_df, use_container_width=True, hide_index=True)
else:
    st.info("No significant insider transactions reported recently.")


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
