import yfinance as yf
import pandas as pd
import pandas_ta as ta

# --- Define your watchlist here ---
watchlist = ["AAPL", "MSFT", "NVDA"]  # Modify this list as desired

# --- Strategy Parameters ---
start_date = "2024-01-01"
end_date = "2024-08-01"

# --- Function to analyze a single stock ---
def analyze_stock(ticker):
    print(f"\nAnalyzing {ticker}...")

    df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)

    if df.empty:
        print(f"⚠️ No data for {ticker}")
        return None

    # Clean column names if needed
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0].replace(f"_{ticker}", "") for col in df.columns]
    df.columns = [col.replace(f"_{ticker}", "") for col in df.columns]

    # Add indicators
    df.ta.sma(length=20, append=True)
    df.ta.sma(length=50, append=True)

    # Detect trend
    def detect_trend(row):
        if row['Close'] > row['SMA_20'] and row['SMA_20'] > row['SMA_50']:
            return "Uptrend"
        elif row['Close'] < row['SMA_20'] and row['SMA_20'] < row['SMA_50']:
            return "Downtrend"
        else:
            return "Sideways"

    df['Trend'] = df.apply(detect_trend, axis=1)

    # Signal generation
    df['Signal'] = 0
    for i in range(1, len(df)):
        prev_trend = df.iloc[i-1]['Trend']
        curr_trend = df.iloc[i]['Trend']

        if prev_trend != "Uptrend" and curr_trend == "Uptrend":
            df.at[df.index[i], 'Signal'] = 1  # Buy
        elif prev_trend == "Uptrend" and curr_trend != "Uptrend":
            df.at[df.index[i], 'Signal'] = -1  # Sell

    # Extract trade signals
    trades = df[df['Signal'] != 0][['Close', 'Signal']]
    trades['Action'] = trades['Signal'].map({1: 'BUY', -1: 'SELL'})

    print(trades[['Close', 'Action']])
    return trades

# --- Loop through watchlist ---
for ticker in watchlist:
    analyze_stock(ticker)
