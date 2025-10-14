import requests
import pandas as pd
import matplotlib.pyplot as plt

API_KEY = "1YQNQ3SAOTES4V19"
SYMBOL = "AAPL"
OUTPUT_SIZE = "full"
SMA_PERIOD = 20 # 20-day Simple Moving Average

# API INTEGRATION

def fetch_stock_data(symbol, api_key, output_size='full'):
    """Fetches daily historical stock data from Alpha Vantage."""
    print(f"Fetching data for {symbol}...")
    
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize={output_size}&apikey={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status() 
        data = response.json()
        
        if "Error Message" in data:
            print(f"API Error: {data['Error Message']}")
            return None
        if "Note" in data:
            print(f"API Note (Possible Rate Limit): {data['Note']}")
        
        time_series = data.get("Time Series (Daily)")
        if not time_series:
            print("Could not find 'Time Series (Daily)' in the response.")
            return None
        
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index.name = 'Date'
        print("Data fetched successfully.")
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during API request: {e}")
        return None

#   CLEANING AND FEATURE ENGINEERING

def clean_and_feature_engineer(df, sma_period):
    """Cleans the DataFrame and calculates the Simple Moving Average (SMA)."""
    print("Starting data cleaning and feature engineering...")
    
    # 1. Rename and Type Conversion
    column_mapping = {
        '1. open': 'Open', '2. high': 'High', '3. low': 'Low',
        '4. close': 'Close', '5. volume': 'Volume'
    }
    df = df.rename(columns=column_mapping)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    
    cols_to_numeric = ['Open', 'High', 'Low', 'Close', 'Volume']
    df[cols_to_numeric] = df[cols_to_numeric].apply(pd.to_numeric, errors='coerce')
    df = df.dropna()
    
    # 2. Feature Engineering: Calculate SMA
    df[f'{sma_period}_day_SMA'] = df['Close'].rolling(window=sma_period).mean()
    
    print("Data prepared and SMA calculated.")
    return df

#  VISUALIZATION

def plot_stock_data(df, symbol, sma_period):
    """Creates a dual-axis chart for price, volume, and SMA."""
    print("Generating visualization...")
    
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # --- Primary Y-axis (Closing Price and SMA) ---
    color_price = 'tab:blue'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Closing Price ($)', color=color_price)
    
    ax1.plot(df.index, df['Close'], color=color_price, label='Closing Price', linewidth=1.5)
    ax1.plot(df.index, df[f'{sma_period}_day_SMA'], color='red', 
             label=f'{sma_period}-day SMA', linestyle='--', linewidth=2)
    
    ax1.tick_params(axis='y', labelcolor=color_price)
    ax1.legend(loc='upper left')
    ax1.grid(True, axis='y', linestyle=':', alpha=0.6)
    
    # --- Secondary Y-axis (Trading Volume) ---
    ax2 = ax1.twinx() 
    color_volume = 'tab:gray'
    ax2.set_ylabel('Trading Volume', color=color_volume)
    
    ax2.bar(df.index, df['Volume'], color=color_volume, alpha=0.3, label='Volume')
    ax2.tick_params(axis='y', labelcolor=color_volume)
    ax2.set_ylim(0, df['Volume'].max() * 4) # Scale volume for clarity
    
    # --- Final Styling ---
    plt.title(f'Historical Price and Volume Analysis for {symbol} (Last 180 Days)')
    fig.tight_layout()
    plt.show()
    print("Visualization complete.")

# MAIN EXECUTION BLOCK

if __name__ == "__main__":
    # 1. Fetch Data
    df_raw = fetch_stock_data(SYMBOL, API_KEY, OUTPUT_SIZE)
    
    if df_raw is not None and not df_raw.empty:
        # 2. & 3. Clean, Prep, and Feature Engineer
        df_processed = clean_and_feature_engineer(df_raw.copy(), SMA_PERIOD)
        
        # Filter to the last 180 trading days for a cleaner plot on the screen
        df_recent = df_processed.tail(180) 
        
        # 4. Visualization
        plot_stock_data(df_recent, SYMBOL, SMA_PERIOD)
        
        # 5. Output/Conclusion Data for README
        print("\n--- Data for README Conclusion ---")
        print(f"Stock: {SYMBOL}")
        print(f"Analysis Period End Date: {df_recent.index[-1].strftime('%Y-%m-%d')}")
        print(f"Latest Closing Price: ${df_recent['Close'].iloc[-1]:.2f}")
        print(f"Latest {SMA_PERIOD}-day SMA: ${df_recent[f'{SMA_PERIOD}_day_SMA'].iloc[-1]:.2f}")
    else:
        print("Script execution failed due to data error.")