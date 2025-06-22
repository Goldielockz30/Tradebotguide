#streamline script to create a trading bot dashboard using streamlit and ccxt


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


# 5. Show buy/sell signals and auto-execute
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

# 9. Recent trades
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