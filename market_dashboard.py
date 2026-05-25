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

# --- UI TOGGLES ---
st.sidebar.header("Chart Settings")
show_daily_zones = st.sidebar.checkbox("Show Daily S/R Zones", value=True)
show_weekly_zones = st.sidebar.checkbox("Show Weekly S/R Zones", value=False)
show_volume_profile = st.sidebar.checkbox("Show High Volume Areas", value=False)
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
    # Simplified Pivot detection
    window = 5 if not is_weekly else 3
    df['Pivot_High'] = df['High'][(df['High'] == df['High'].rolling(window=window*2+1, center=True).max())]
    df['Pivot_Low'] = df['Low'][(df['Low'] == df['Low'].rolling(window=window*2+1, center=True).min())]
    
    pivots = pd.concat([df['Pivot_High'].dropna(), df['Pivot_Low'].dropna()]).sort_values()
    if len(pivots) == 0: return []
    
    # Clustering logic based on ATR
    zones = []
    current_cluster = [pivots.iloc[0]]
    
    for p in pivots.iloc[1:]:
        if abs(p - np.mean(current_cluster)) <= atr * 0.8:
            current_cluster.append(p)
        else:
            zones.append(current_cluster)
            current_cluster = [p]
    zones.append(current_cluster)
    
    # Score and rank zones
    scored_zones = []
    current_price = df['Close'].iloc[-1]
    
    for z in zones:
        center = np.mean(z)
        width = atr * 0.5
        touches = len(z)
        # Score = touches * 10 (capped at 100)
        score = min(touches * 25, 100) 
        
        # Determine polarity
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
        
    # Sort by score and keep top 6
    scored_zones = sorted(scored_zones, key=lambda x: x['score'], reverse=True)[:6]
    return scored_zones

@st.cache_data(ttl=300)
def get_stock_data(tickers):
    data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            # Pull 1 year to get good pivots and 200 SMA
            hist = stock.history(period="1y") 
            if hist.empty: continue
            
            # Technicals
            hist['ATR'] = calculate_atr(hist)
            hist['EMA_10'] = hist['Close'].ewm(span=10, adjust=False).mean()
            hist['EMA_21'] = hist['Close'].ewm(span=21, adjust=False).mean()
            hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
            hist['SMA_200'] = hist['Close'].rolling(window=200).mean()
            
            # Weekly aggregation for weekly zones
            weekly_hist = hist.resample('W').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last'})
            weekly_hist['ATR'] = calculate_atr(weekly_hist)
            
            current_atr = hist['ATR'].iloc[-1]
            if pd.isna(current_atr): current_atr = hist['Close'].iloc[-1] * 0.02
            
            daily_zones = find_zones(hist.tail(150), current_atr)
            weekly_zones = find_zones(weekly_hist.tail(52), weekly_hist['ATR'].iloc[-1], is_weekly=True) if len(weekly_hist)>10 else []
            
            # Trim for display to last 90 days
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

data = get_stock_data(tickers)

st.header("Live Market Overview")
cols = st.columns(4)
for i, ticker in enumerate(tickers):
    if ticker in data:
        cols[i % 4].metric(label=ticker, value=f"${data[ticker]['price']:.2f}", delta=f"{data[ticker]['change']:.2f}%")

st.markdown("---")
st.header("📈 Tactical Algorithmic Charts")

chart_cols = st.columns(2) # 2 columns for wider charts
for i, ticker in enumerate(tickers):
    if ticker in data:
        with chart_cols[i % 2]:
            st.subheader(ticker)
            hist = data[ticker]['history']
            
            fig = go.Figure()
            
            # Candlesticks
            # Convert dates to strings to perfectly skip weekends and show dates clearly
            date_strings = hist.index.strftime('%Y-%m-%d')
            fig.add_trace(go.Candlestick(x=date_strings, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name='Price'))
            
            # MAs
            if show_ema10: fig.add_trace(go.Scatter(x=date_strings, y=hist['EMA_10'], mode='lines', name='10 EMA', line=dict(color='orange', width=1)))
            if show_ema21: fig.add_trace(go.Scatter(x=date_strings, y=hist['EMA_21'], mode='lines', name='21 EMA', line=dict(color='yellow', width=1)))
            if show_sma50: fig.add_trace(go.Scatter(x=date_strings, y=hist['SMA_50'], mode='lines', name='50 SMA', line=dict(color='blue', width=1.5)))
            if show_sma200: fig.add_trace(go.Scatter(x=date_strings, y=hist['SMA_200'], mode='lines', name='200 SMA', line=dict(color='white', width=2)))

            # Zones
            zones_to_plot = []
            if show_daily_zones: zones_to_plot.extend(data[ticker]['daily_zones'])
            if show_weekly_zones: zones_to_plot.extend(data[ticker]['weekly_zones'])
            
            for z in zones_to_plot:
                fig.add_hrect(
                    y0=z['bottom'], y1=z['top'], 
                    fillcolor=z['color'], opacity=0.3, line_width=1, line_color=z['line_color'],
                    annotation_text=z['label'], annotation_position="top left", annotation_font_size=10
                )

            fig.update_layout(
                margin=dict(l=0, r=0, t=30, b=40),
                xaxis_rangeslider_visible=False,
                xaxis=dict(
                    type='category', 
                    categoryorder='category ascending',
                    nticks=10,
                    showgrid=False
                ),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
