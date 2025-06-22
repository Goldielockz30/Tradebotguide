
# Step-by-Step Guide to Building a Streamlit Trading Bot Dashboard with VS Code  
**By Nana Johnson**

## Need Help Installing This Bot?

### I offer full setup & dashboard hosting:
- 1-on-1 call
- Bot installation
- Custom settings
- API help

Book now → [Calendly or Stripe link]


---

## 1. Okay Lets Gat Started ! - Prerequisites

- Open VS Code: install the Python extension to effectively work with Python in Visual Studio Code (VS Code)

- Check if you have Python 3.9+ installed: to check that it has been installed run this in the VS Code command line

```bash

  python --version           # verify you have python - If Python is accessible, it will return its version 
```
```bash
  # or, on macOS/Linux:
  python3 --version

```
-   If Python is on your PATH, you’ll see something like:
```bash 

Python 3.12.1

```
- If you get an error like 'python' is not recognized, or no version number appears, Python isn’t installed or not added to your PATH.

- Windows: Download and install from python.org or via the Microsoft Store. Be sure to check “Add Python to PATH” in the installer .

- macOS/Linux: Usually comes pre-installed, or install via:

```bash
brew install python  # macOS (Homebrew)
sudo apt-get install python3  # Ubuntu/Debian

```
- from the VS Code command line navigate into desktop
```bash
  cd ~/Desktop

```
- Create a project folder (e.g., `tradebot`)  
```bash 
   mkdir tradebot
   cd tradebot              # this takes you into your folder where you will create your files
```
- !!! Once you have creater the folder open it on VS Code for easy monitoring and editing please click file at the top left and then open folder go into your tradebot folder that you just created on your desktop

- Create and activate a virtual environment (recommended):  
  

  ```bash
  python -m venv .venv          # This step isolates your project's dependencies, preventing conflicts with other Python projects: (skip if you get a "permission denied" error) 
  ```
  - Virtual Environment Activation: Ensure that your virtual environment is activated before running pip freeze. This ensures that only the packages installed within the virtual environment are included in the requirements.txt file, not global packages.

  - We will use this first command

  ```bash
  .\.venv\Scripts\Activate.ps1        # On Windows powershell - works in VS Code
  ```
  - alternatively

  ```bash
  .\.venv\Scripts\activate.bat        # On Windows (Command Prompt):
  ```

  ```bash
  source .venv/bin/activate     # On macOS/Linux  
  ```
  - To deactivate

  ```bash
  deactivate # To leave the environment (if needed)

  ``` 

- Install the following packages in the virtual environment:  
  ```bash
  pip install ccxt pandas ta streamlit tzlocal
  ```



- Create Binance API keys and save them into a note file because these wont be shown to you again

- https://testnet.binance.vision/ and log in then click on “Generate Key”.


---

## 2. Project Structure

- Inside your `tradebot` folder, create the following files:

- Once all required packages are installed, generate the requirements.txt file:

```bash 
pip freeze > requirements.txt       # you will see the requirements file appear in your tradebot folder

```

- Global Packages: If you run pip freeze without activating a virtual environment, it will list all globally installed packages, which may not be relevant to your project. In such cases, you can manually edit the requirements.txt file to include only the necessary packages.
- Copy and paste this into your requirements file you wont need the whole list that generates if its more than this.
```bash

ccxt==4.4.90          # For exchange access (Binance, etc.)
pandas==2.3.0         # For data manipulation
ta==0.11.0            # For technical analysis indicators (e.g. RSI)
streamlit==1.46.0     # For building the dashboard
tzlocal==5.3.1        # Detects user's local timezone :contentReference[oaicite:1]{index=1

# Optional but recommended
altair==5.5.0         # Optional: for interactive charts
plotly==5.21.0        # Optional: advanced plotting
numpy==2.3.0          # Required by many data libraries
requests==2.32.4      # For API calls, sometimes used with ccxt

```
- When setting up the project on a new system, install all dependencies using:
```bash
pip install -r requirements.txt

```

- Then create a file for your tradebot and name it `trade_functions.py` – contains reusable functions  
- Then create a file for your dashboard to call functions from `trade_functions` and name it `dashstream.py` – the Streamlit dashboard
- You can add these files manually in your tradebot folder or in the vs code command line
```bash
ni trade_functions.py
ni dashstream.py

```
- or 
```bash
New-Item trade_functions.py -ItemType File
New-Item dashstream.py -ItemType File

```
- Once your files are created, paste the corresponding code into each one (e.g., trade_functions.py, dashstream.py) to get your bot and dashboard running.
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

def check_signal(df, rsi_buy, rsi_sell):
    last_rsi = df['rsi'].iloc[-1]
    print(f"Current RSI: {last_rsi:.2f}")
    if last_rsi < rsi_buy:
        print(">> BUY SIGNAL")
        return "buy", last_rsi
    elif last_rsi > rsi_sell:
        print(">> SELL SIGNAL")
        return "sell", last_rsi
    else:
        print(">> NO CLEAR SIGNAL")
        return None, last_rsi  # Or return "hold", last_rsi

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
from trade_functions import get_exchange, get_balances, fetch_data, calculate_rsi, place_order, check_signal
import pandas as pd
from tzlocal import get_localzone

if 'last_action' not in st.session_state:
    st.session_state.last_action = None

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

# 5. Show Buy/Sell Signals and auto execute
signal, current_rsi = check_signal(df, rsi_buy, rsi_sell)
if current_rsi < rsi_buy:
    signal = "buy"
    st.success("🚀 Buy Signal!")
elif current_rsi > rsi_sell:
    signal = "sell"
    st.error("📉 Sell Signal")
else:
    st.info("No clear signal")

# 6. Auto-trade logic (once per signal)
if signal and signal != st.session_state.last_action:
    order_amount = st.number_input(
        "Order Amount (BTC)", min_value=0.0001, max_value=1.0, value=0.001, step=0.0001, format="%.4f", key="order_amount"
    )
    # Execute trade
    place_order(signal, order_amount)
    st.success(f"🔄 Auto {signal.capitalize()} Order executed for {order_amount} BTC")
    st.session_state.last_action = signal

# 7. Show price + RSI chart
st.line_chart(df[['close', 'rsi']])

# 8. Manual order input
manual_order_amount = st.number_input("Order Amount (BTC)", min_value=0.0001, max_value=1.0, value=0.001, step=0.0001, format="%.4f", key="manual_order_amount")

if st.button("Buy BTC"):
    place_order("buy", amount=manual_order_amount)
    st.success(f"Buy order for {manual_order_amount} BTC placed!")

if st.button("Sell BTC"):
    place_order("sell", amount=manual_order_amount)
    st.success(f"Sell order for {manual_order_amount} BTC placed!")

# 9. Fetch and display recent trades (optional)
exchange = get_exchange()
try:
    trades = exchange.fetch_my_trades(symbol='BTC/USDT', limit=5)
    trades_df = pd.DataFrame(trades)

    if not trades_df.empty:
        # 1. Convert to datetime with UTC timezone awareness
        trades_df['timestamp'] = pd.to_datetime(
            trades_df['timestamp'], unit='ms', utc=True
        )

        # 2. Convert to local timezone (auto-detected)
        local_tz = get_localzone()
        trades_df['timestamp'] = trades_df['timestamp'].dt.tz_convert(local_tz)

        # 3. Remove timezone info for display, so it's shown naively in local time
        trades_df['timestamp'] = trades_df['timestamp'].dt.tz_localize(None)

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

Once your dashboard is running you will start off with 0 BTC and around 15K USDT you need to manually buy the BTC your bot dashboard, you will need enough so that your bot can auto trade for you, it can't do this with 0 BTC

- Manually click your dashboard's "Buy BTC" button—this uses USDT to purchase BTC at market price.

- After that, you'll have some BTC (e.g., 0.001 BTC) stored in your testnet account.

- With BTC in your balance, your automation logic (based on RSI thresholds or other rules) can now operate, placing buy/sell orders as designed.

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
