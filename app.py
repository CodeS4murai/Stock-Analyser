import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go


# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="📊 Stock Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HEADER ---
st.title("📈 Stock Price & Volume Analysis Dashboard")
st.markdown("Analyze historical stock data with **Alpha Vantage** API integration and visualize trends using SMA (Simple Moving Average).")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("⚙️ Configuration")

api_key = st.secrets["ALPHA_VANTAGE_API_KEY"] 
symbol = st.sidebar.selectbox("📉 Stock Symbol", ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN", "NVDA"], index=0)
sma_period = st.sidebar.slider("📊 SMA Period (Days)", min_value=5, max_value=100, value=20, step=5)

st.sidebar.markdown("---")
fetch_button = st.sidebar.button("🚀 Fetch & Analyze Data")

# --- FUNCTION DEFINITIONS ---
def fetch_stock_data(symbol, api_key, output_size='full'):
    """Fetch daily stock data from Alpha Vantage API."""
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize={output_size}&apikey={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "Error Message" in data:
            st.error(f"❌ API Error: {data['Error Message']}")
            return None
        if "Note" in data:
            st.warning(f"⚠️ API Rate Limit: {data['Note']}")
            return None

        time_series = data.get("Time Series (Daily)")
        if not time_series:
            st.error("❌ Missing 'Time Series (Daily)' in API response.")
            return None

        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index.name = 'Date'
        return df

    except requests.exceptions.RequestException as e:
        st.error(f"Network Error: {e}")
        return None


def clean_and_feature_engineer(df, sma_period):
    """Clean and prepare DataFrame, calculate SMA."""
    column_mapping = {
        '1. open': 'Open', '2. high': 'High', '3. low': 'Low',
        '4. close': 'Close', '5. volume': 'Volume'
    }
    df = df.rename(columns=column_mapping)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    df = df.dropna()

    df[f'{sma_period}_day_SMA'] = df['Close'].rolling(window=sma_period).mean()
    return df


def plot_stock_data(df, symbol, sma_period):
    """Plot closing price, SMA, and volume using Plotly."""
    fig = go.Figure()
    
    # Closing Price Line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='Closing Price'
    ))

    # SMA Line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[f'{sma_period}_day_SMA'],
        mode='lines',
        name=f'{sma_period}-Day SMA',
        line=dict(dash='dash')
    ))

    # Volume Bars (Secondary Axis)
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        name='Volume',
        opacity=0.3,
        yaxis='y2'
    ))

    # Layout Configuration
    fig.update_layout(
        title=f"📊 {symbol} - Price, SMA & Volume (Last 180 Days)",
        xaxis=dict(title="Date"),

        yaxis=dict(
            title="Closing Price ($)",
            side="left"
        ),

        yaxis2=dict(
            title="Volume",
            overlaying="y",
            side="right",
            showgrid=False
        ),

        legend=dict(x=0, y=1.1, orientation="h"),
        height=600,
        margin=dict(l=40, r=40, t=80, b=40)
    )

    return fig


# --- MAIN APP EXECUTION ---
if fetch_button:
    symbol_to_fetch = symbol
else:
    symbol_to_fetch = symbol  # default AAPL


with st.spinner(f"Fetching data for **{symbol_to_fetch}**..."):
    df_raw = fetch_stock_data(symbol_to_fetch, api_key, "full")

if df_raw is not None and not df_raw.empty:
    df_processed = clean_and_feature_engineer(df_raw, sma_period)
    df_recent = df_processed.tail(180)

    st.subheader(f"📘 Summary for {symbol_to_fetch}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Latest Date", df_recent.index[-1].strftime("%Y-%m-%d"))
    col2.metric("Closing Price", f"${df_recent['Close'].iloc[-1]:.2f}")
    col3.metric(f"{sma_period}-Day SMA", f"${df_recent[f'{sma_period}_day_SMA'].iloc[-1]:.2f}")

    st.subheader("📈 Historical Chart")
    fig = plot_stock_data(df_recent, symbol_to_fetch, sma_period)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df_recent.tail(30))
    st.success("✅ Analysis Complete!")
else:
    st.error("Failed to fetch or process data. Check API key or symbol.")

