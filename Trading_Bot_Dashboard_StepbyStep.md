
# Step-by-Step Guide to Building a Streamlit Trading Bot Dashboard with VS Code  
**By Nana Johnson**

---

## 1. Prerequisites

- Python 3.9+ installed  

- Create a project folder (e.g., `tradebot`)  

- Create and activate a virtual environment (recommended):  
  ```bash
  python -m venv .venv          # Create the virtual environment (skip if you get a "permission denied" error) 

  source .venv/bin/activate     # On macOS/Linux  

  .\.venv\Scripts\Activate.ps1        # On Windows powershell

  .\.venv\Scripts\activate.bat        # On Windows (Command Prompt):

  deactivate # To leave the environment (if needed)

  ```

- Install the following packages in the virtual environment:  
  ```bash
  pip install ccxt pandas ta streamlit
  ```  

- Create Binance API keys and enable testnet if needed.

---

## 2. Project Structure

Inside your `tradebot` folder, create the following files:

- `trade_functions.py` – contains reusable functions  
- `dashstream.py` – the Streamlit dashboard

---

## 3. Code for `trade_functions.py`

```python
import ccxt
import pandas as pd
import ta

exchange = ccxt.binance({
    # Replace 'YOUR_API_KEY' and 'YOUR_SECRET' with your Binance Testnet API credentials.
    # You can get these safely without risking real money by registering at:
    # https://testnet.binance.vision/ and clicking on “Generate Key”.
    # Using Testnet keys allows you to develop and test your bot without incurring any costs.
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET',
    'enableRateLimit': True,
})

exchange.set_sandbox_mode(True)  # For testnet use

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
    # Use .rsi() method correctly with fillna to avoid NaNs
    rsi_indicator = ta.momentum.RSIIndicator(df['close'])
    df['rsi'] = rsi_indicator.rsi().fillna(0)
    return df

def check_signal(df):
    last_rsi = df['rsi'].iloc[-1]
    print(f"Current RSI: {last_rsi:.2f}")
    if last_rsi < rsi_buy:
        print(">> BUY SIGNAL")
    elif last_rsi > rsi_sell:
        print(">> SELL SIGNAL")

def get_balances():
    balance = exchange.fetch_balance()
    btc = balance['total'].get('BTC', 0)
    usdt = balance['total'].get('USDT', 0)
    return btc, usdt

def place_order(side, amount):
    if side.lower() == "buy":
        order = exchange.create_market_buy_order(symbol, amount)
    elif side.lower() == "sell":
        order = exchange.create_market_sell_order(symbol, amount)
    else:
        raise ValueError("Invalid side, must be 'buy' or 'sell'")
    return order

# Optional: you can create a simple test here to run only when the file is run directly
if __name__ == "__main__":
    df = fetch_data()
    df = calculate_rsi(df)
    check_signal(df)
```

---

## 4. Code for `dashstream.py`

```python
import streamlit as st
from trade_functions import get_balances, fetch_data, calculate_rsi, place_order
import pandas as pd

st.title("My Trading Bot Dashboard")

# 1. Show Balances
btc, usdt = get_balances()
st.metric("BTC Balance", f"{btc:.4f} BTC")
st.metric("USDT Balance", f"${usdt:.2f}")

# 2. Fetch and calculate indicators
df = fetch_data()
df = calculate_rsi(df)

# 3. Current RSI and Price
current_rsi = df['rsi'].iloc[-1]
current_price = df['close'].iloc[-1]
st.write(f"Current RSI: {current_rsi:.2f}")
st.write(f"Current BTC Price: ${current_price:.2f}")

# 4. RSI Threshold sliders (adjustable)
rsi_buy = st.slider('RSI Buy Threshold', min_value=10, max_value=50, value=30)
rsi_sell = st.slider('RSI Sell Threshold', min_value=50, max_value=90, value=60)

# 5. Show Buy/Sell Signals based on slider values
if current_rsi < rsi_buy:
    st.success("🚀 Buy Signal!")
elif current_rsi > rsi_sell:
    st.error("📉 Sell Signal")
else:
    st.info("No clear signal")

# 6. Show price and RSI charts
st.line_chart(df[['close', 'rsi']])

# 7. Manual Order Amount Input
order_amount = st.number_input("Order Amount (BTC)", min_value=0.0001, max_value=1.0, value=0.001, step=0.0001)

if st.button("Buy BTC"):
    place_order("buy", amount=order_amount)
    st.success(f"Buy order for {order_amount} BTC placed!")

if st.button("Sell BTC"):
    place_order("sell", amount=order_amount)
    st.success(f"Sell order for {order_amount} BTC placed!")

# 8. Fetch and display recent trades (optional)
exchange = get_exchange()
try:
    trades = exchange.fetch_my_trades(symbol='BTC/USDT', limit=5)
    trades_df = pd.DataFrame(trades)
    if not trades_df.empty:
        trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'], unit='ms')
        st.subheader("🧾 Recent Trades")
        st.dataframe(trades_df[['timestamp', 'side', 'price', 'amount']])
except Exception as e:
    st.warning(f"Could not fetch recent trades: {e}")
```

---

### To run it:

```bash
streamlit run dashstream.py
```

### If it doesn't auto open

- paste this in your browser:  
  http://localhost:8501

---

## 5. Extra Dashboard Features

- Add chart with RSI and close prices using Plotly or Altair  
- Show open orders or recent trades (requires full API key permissions)  
- Add strategy logs or bot decisions over time  
- Export performance summary as CSV  

---

## 6. Common Errors & Fixes

- **No module named `ta`**  
  ➤ Run: `pip install ta`

- **Streamlit shows blank screen**  
  ➤ Make sure you're running: `streamlit run dashstream.py`

- **API errors**  
  ➤ Ensure keys are correct and you're in testnet mode

- **Chart not showing RSI**  
  ➤ Ensure your data has enough bars (>= 15) for RSI calc

- **Command pip installs to global Python**  
  ➤ You probably didn’t activate the virtual environment.  
    Run:  
    ```bash
    source .venv/bin/activate           # On macOS/Linux  

    .\.venv\Scripts\Activate.ps1        # On Windows powershell

    .\.venv\Scripts\activate.bat        # On Windows (Command Prompt):


    ```

- **Installed packages but still getting ImportError**  
  ➤ Make sure you install packages after activating `.venv`, or they go to the global Python

---

## Final Tip

Keep your trading logic in `trade_functions.py`, and your UI/dashboard code in `dashstream.py`.  
This makes it easier to test, debug, and expand in the future.
