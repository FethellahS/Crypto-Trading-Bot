import os
from binance.client import Client
import pandas as pd
import time

# Load API keys from environment variables (recommended for security)
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

# Initialize the Binance client
client = Client(api_key, api_secret)

# Define trading parameters
symbol = 'BTCUSDT'
interval = '1m'  # 1 minute intervals
quantity = 0.001  # Amount of BTC to trade

def get_historical_data(symbol, interval, lookback):
    klines = client.get_historical_klines(symbol, interval, lookback)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

def signal_generator(df):
    # Simple strategy: Buy if the close price is above the moving average, sell if below
    df['SMA'] = df['close'].astype(float).rolling(window=14).mean()
    latest_close = df['close'].astype(float).iloc[-1]
    latest_sma = df['SMA'].iloc[-1]

    if latest_close > latest_sma:
        return 'buy'
    elif latest_close < latest_sma:
        return 'sell'
    return 'hold'

def execute_trade(signal):
    if signal == 'buy':
        print(f"Buying {quantity} of {symbol}")
        client.order_market_buy(symbol=symbol, quantity=quantity)
    elif signal == 'sell':
        print(f"Selling {quantity} of {symbol}")
        client.order_market_sell(symbol=symbol, quantity=quantity)

def main():
    while True:
        df = get_historical_data(symbol, interval, '1 day ago UTC')
        signal = signal_generator(df)
        execute_trade(signal)
        time.sleep(60)  # Wait for 1 minute

if __name__ == '__main__':
    main()
