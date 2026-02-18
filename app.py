import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, date
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

# =====================================================
# CONFIG
# =====================================================

DAILY_LIMIT = 5.0

SLABS = [
    (100, 5),
    (300, 7),
    (float("inf"), 9)
]

TICK_INTERVAL_SECONDS = 2  # real-time speed

# =====================================================
# SESSION INIT
# =====================================================

if "data" not in st.session_state:
    st.session_state.data = []

if "running" not in st.session_state:
    st.session_state.running = False

if "month_start" not in st.session_state:
    today = date.today()
    st.session_state.month_start = date(today.year, today.month, 1)

if "daily_usage" not in st.session_state:
    st.session_state.daily_usage = 0

if "current_day" not in st.session_state:
    st.session_state.current_day = date.today()

# =====================================================
# FUNCTIONS
# =====================================================

def generate_usage():
    return round(random.uniform(0.02, 0.05), 3)


def calculate_slab_bill(total_usage):
    remaining = total_usage
    bill = 0
    prev = 0

    for limit, rate in SLABS:
        slab_units = min(remaining, limit - prev)
        bill += slab_units * rate
        remaining -= slab_units
        prev = limit
        if remaining <= 0:
            break

    return round(bill, 2)


def predict_monthly_estimate(data):
    if len(data) < 10:
        return None

    df = pd.DataFrame(data, columns=["Usage"])
    df["Index"] = np.arange(len(df))

    model = LinearRegression()
    model.fit(df[["Index"]], df["Usage"])

    future_points = 100
    future_index = np.arange(len(df), len(df) + future_points).reshape(-1, 1)
    predictions = model.predict(future_index)

    predicted_total = sum(data) + sum(predictions)
    predicted_bill = calculate_slab_bill(predicted_total)

    return round(predicted_total, 2), round(predicted_bill, 2)

# =====================================================
# HEADER
# =====================================================

st.title("⚡ Household Electricity Consumption Analysis")

# =====================================================
# BUTTONS
# =====================================================

col1, col2, col3 = st.columns(3)

if col1.button("Start"):
    st.session_state.running = True

if col2.button("Stop"):
    st.session_state.running = False

if col3.button("Reset"):
    st.session_state.running = False
    st.session_state.data = []
    st.session_state.daily_usage = 0
    st.session_state.month_start = date.today().replace(day=1)

# =====================================================
# REAL-TIME ENGINE
# =====================================================

if st.session_state.running:
    st_autorefresh(interval=TICK_INTERVAL_SECONDS * 1000, key="live")

    usage = generate_usage()
    st.session_state.data.append(usage)

    today = date.today()

    # Reset daily usage if new day
    if today != st.session_state.current_day:
        st.session_state.daily_usage = 0
        st.session_state.current_day = today

    st.session_state.daily_usage += usage

# =====================================================
# METRICS
# =====================================================

total_usage = sum(st.session_state.data)
monthly_bill = calculate_slab_bill(total_usage)
latest = st.session_state.data[-1] if st.session_state.data else 0

m1, m2, m3 = st.columns(3)

m1.metric("Latest Reading", f"{latest} units")
m2.metric("Total Usage (This Month)", f"{round(total_usage,2)} units")
m3.metric("Estimated Bill (Current Month)", f"₹{monthly_bill}")

# Daily Warning
if st.session_state.daily_usage > DAILY_LIMIT:
    st.error("⚠ Daily usage exceeded 5 units!")

# =====================================================
# GRAPH
# =====================================================

if st.session_state.data:
    df = pd.DataFrame(st.session_state.data, columns=["Usage"])
    df["Cumulative"] = df["Usage"].cumsum()
    st.line_chart(df["Cumulative"])

# =====================================================
# PREDICTION SECTION
# =====================================================

st.subheader("📊 Monthly Prediction")

prediction = predict_monthly_estimate(st.session_state.data)

if prediction:
    predicted_units, predicted_bill = prediction
    c1, c2 = st.columns(2)
    c1.metric("Predicted End-of-Month Units", predicted_units)
    c2.metric("Predicted End-of-Month Bill", f"₹{predicted_bill}")
else:
    st.info("Collect more data for prediction.")