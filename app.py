import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

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

api_key = st.sidebar.text_input("🔑 Enter your Alpha Vantage API Key", type="password", value="1YQNQ3SAOTES4V19")
symbol = st.sidebar.text_input("📉 Stock Symbol", value="AAPL", help="Example: AAPL, TSLA, GOOGL, MSFT, etc.")
output_size = st.sidebar.selectbox("📦 Output Size", ["compact", "full"], index=1)
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
    """Plot closing price, SMA, and volume."""
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Primary axis (Price & SMA)
    ax1.plot(df.index, df['Close'], color='tab:blue', label='Closing Price', linewidth=1.5)
    ax1.plot(df.index, df[f'{sma_period}_day_SMA'], color='red', linestyle='--',
             label=f'{sma_period}-Day SMA', linewidth=2)
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Closing Price ($)")
    ax1.legend(loc='upper left')
    ax1.grid(True, linestyle=':', alpha=0.6)

    # Secondary axis (Volume)
    ax2 = ax1.twinx()
    ax2.bar(df.index, df['Volume'], color='gray', alpha=0.3, label='Volume')
    ax2.set_ylabel("Trading Volume")

    plt.title(f"📊 {symbol} - Price, SMA & Volume (Last 180 Days)")
    fig.tight_layout()
    return fig


# --- MAIN APP EXECUTION ---
if fetch_button:
    if not api_key or not symbol:
        st.warning("⚠️ Please enter both API Key and Stock Symbol.")
    else:
        with st.spinner(f"Fetching data for **{symbol}**..."):
            df_raw = fetch_stock_data(symbol, api_key, output_size)

        if df_raw is not None and not df_raw.empty:
            df_processed = clean_and_feature_engineer(df_raw, sma_period)
            df_recent = df_processed.tail(180)

            # Display Summary Metrics
            st.subheader(f"📘 Summary for {symbol}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Latest Date", df_recent.index[-1].strftime("%Y-%m-%d"))
            col2.metric("Closing Price", f"${df_recent['Close'].iloc[-1]:.2f}")
            col3.metric(f"{sma_period}-Day SMA", f"${df_recent[f'{sma_period}_day_SMA'].iloc[-1]:.2f}")

            # Chart
            st.subheader("📈 Historical Chart")
            fig = plot_stock_data(df_recent, symbol, sma_period)
            st.pyplot(fig)

            # Raw Data Option
           # with st.expander("📄 View Processed DataFrame"):
            st.dataframe(df_recent.tail(30))

            st.success("✅ Analysis Complete!")
        else:
            st.error("Failed to fetch or process data. Check API key or symbol.")
