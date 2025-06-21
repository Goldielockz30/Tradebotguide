#streamline script to create a trading bot dashboard using streamlit and ccxt


import streamlit as st
from trade_functions import get_balances, fetch_data, calculate_rsi, place_order, get_exchange
import pandas as pd

st.title("My Trading Bot Dashboard")

# 1. Show Balances
btc, usdt = get_balances()
st.metric("BTC Balance", f"{btc:.4f} BTC")
st.metric("USDT Balance", f"${usdt:.2f}")

# 2. Fetch data + indicators
df = fetch_data()
df = calculate_rsi(df)

# 3. Show current RSI and price
current_rsi = df['rsi'].iloc[-1]
current_price = df['close'].iloc[-1]
st.write(f"**Current RSI**: {current_rsi:.2f}")
st.write(f"**Current BTC Price**: ${current_price:.2f}")

# 4. RSI thresholds
rsi_buy = st.slider("RSI Buy Threshold", 10, 50, 30)
rsi_sell = st.slider("RSI Sell Threshold", 50, 90, 60)


# 5. Show trading signal
if current_rsi < rsi_buy:
    st.success("🚀 Buy Signal!")
elif current_rsi > rsi_sell:
    st.error("📉 Sell Signal!")
else:
    st.info("No clear signal.")

# 6. Show price + RSI chart
st.line_chart(df[['close', 'rsi']])

# 7. Manual order input
order_amount = st.number_input("Order Amount (BTC)", min_value=0.0001, max_value=1.0, value=0.001, step=0.0001)

if st.button("Buy BTC"):
    place_order("buy", amount=order_amount)
    st.success(f"Buy order for {order_amount} BTC placed!")

if st.button("Sell BTC"):
    place_order("sell", amount=order_amount)
    st.success(f"Sell order for {order_amount} BTC placed!")

# 8. Recent trades
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