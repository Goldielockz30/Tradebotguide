#with functions to call from dashstream

import ccxt
import pandas as pd
import ta


# === Exchange Setup ===
exchange = ccxt.binance({
    'apiKey': 'g0X6kGp8FIPSPPSWUCLS3Y5Wctlm8zyRUf5gi9b6enU87rmVbx4hsI5bT2zyKibh',
    'secret': 'mxkS7BnkyX1LNShJuP7ZxQzJ5OqtJk2lG9XVWLalBmekLbQoLUbs0Sn2d5m1Lqg0',
    'enableRateLimit': True,
})
exchange.set_sandbox_mode(True)  # Ensure we're using the testnet

# === Trading Parameters ===
symbol = 'BTC/USDT'
timeframe = '5m'
rsi_buy = 30
rsi_sell = 60

# === Functions ===
def get_exchange():
    return exchange

def fetch_data():
    bars = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
    df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    return df

def calculate_rsi(df):
    rsi_indicator = ta.momentum.RSIIndicator(df['close'])
    df['rsi'] = rsi_indicator.rsi().fillna(0)
    return df

def check_signal(df, rsi_buy_threshold, rsi_sell_threshold):
    last_rsi = df['rsi'].iloc[-1]
    if last_rsi < rsi_buy_threshold:
        return "buy", last_rsi
    elif last_rsi > rsi_sell_threshold:
        return "sell", last_rsi
    return None, last_rsi


def get_balances():
    balance = exchange.fetch_balance()
    btc = balance['total'].get('BTC', 0)
    usdt = balance['total'].get('USDT', 0)
    return btc, usdt

def place_order(side, amount):
    if side.lower() == "buy":
        return exchange.create_market_buy_order(symbol, amount)
    elif side.lower() == "sell":
        return exchange.create_market_sell_order(symbol, amount)
    else:
        raise ValueError("Invalid order side. Use 'buy' or 'sell'.")

# Optional direct run check
if __name__ == "__main__":
    df = fetch_data()
    df = calculate_rsi(df)
    check_signal(df)

