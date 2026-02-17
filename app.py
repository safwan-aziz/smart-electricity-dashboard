import streamlit as st
import time
import pandas as pd
import random
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime

# =====================================================
# PRODUCTION CONFIG
# =====================================================

DAILY_LIMIT = 5.0

SLABS = [
    (3, 5),
    (6, 7),
    (float('inf'), 9)
]

# =====================================================
# REALISTIC TIME SCALING OPTIONS
# =====================================================

TIME_SCALING_OPTIONS = {
    "Fast (1 Reading = 5 Seconds)": 5,
    "Medium (1 Reading = 10 Seconds)": 10,
    "Slow (1 Reading = 30 Seconds)": 30
}

# =====================================================
# DARK UI STYLING
# =====================================================

st.markdown("""
<style>
body { background-color: #0E1117; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.stMetric {
    background-color: #1C1F26;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 0px 10px rgba(0, 255, 198, 0.2);
}
.stButton>button {
    background-color: #00FFC6;
    color: black;
    border-radius: 8px;
    font-weight: bold;
}
.stButton>button:hover { background-color: #00d4a8; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE INIT
# =====================================================

if "data" not in st.session_state:
    st.session_state.data = []

if "running" not in st.session_state:
    st.session_state.running = False

if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.now()

if "simulated_minutes" not in st.session_state:
    st.session_state.simulated_minutes = 0

# =====================================================
# CORE FUNCTIONS
# =====================================================

def generate_usage():
    return round(random.uniform(0.05, 0.60), 3)


def calculate_slab_bill(total_usage):
    remaining = total_usage
    bill = 0
    previous_limit = 0

    for limit, rate in SLABS:
        slab_units = min(remaining, limit - previous_limit)
        bill += slab_units * rate
        remaining -= slab_units
        previous_limit = limit
        if remaining <= 0:
            break

    return round(bill, 2)


def predict_next_reading(data):
    if len(data) < 10:
        return None

    df = pd.DataFrame(data, columns=["Usage"])
    df["Index"] = np.arange(len(df))

    X = df[["Index"]]
    y = df["Usage"]

    model = LinearRegression()
    model.fit(X, y)

    prediction = model.predict([[len(df)]])[0]
    return round(prediction, 3)


def predict_monthly_bill(data, simulated_minutes):
    if len(data) < 10 or simulated_minutes == 0:
        return None

    total_usage = sum(data)

    # Calculate usage per minute
    usage_per_minute = total_usage / simulated_minutes

    # 30 days = 30 * 24 * 60 minutes
    monthly_minutes = 30 * 24 * 60

    estimated_monthly_usage = usage_per_minute * monthly_minutes
    monthly_bill = calculate_slab_bill(estimated_monthly_usage)

    return round(estimated_monthly_usage, 2), round(monthly_bill, 2)

# =====================================================
# UI HEADER
# =====================================================

st.markdown("""
<h1 style='text-align: center; color: #00FFC6; font-size: 38px;'>
Household Electricity Consumption Analysis
</h1>
<p style='text-align: center; color: gray; font-size: 18px;'>
AI-Based Forecasting & Cost Optimization Model
</p>
""", unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid #00FFC6;'>", unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid #00FFC6;'>", unsafe_allow_html=True)
# =====================================================
# SIMULATION SETTINGS
# =====================================================

colA, colB = st.columns(2)

time_scale_label = colA.selectbox(
    "Simulation Speed",
    list(TIME_SCALING_OPTIONS.keys())
)

update_interval = TIME_SCALING_OPTIONS[time_scale_label]

minutes_per_reading = 1  # Logical time per reading

# =====================================================
# CONTROL BUTTONS
# =====================================================

col1, col2, col3 = st.columns(3)

if col1.button("Start Simulation"):
    st.session_state.running = True

if col2.button("Stop Simulation"):
    st.session_state.running = False

if col3.button("Reset"):
    st.session_state.running = False
    st.session_state.data = []
    st.session_state.simulated_minutes = 0
    st.rerun()

# =====================================================
# REAL-TIME TICK (Production Safe)
# =====================================================

if st.session_state.running:
    now = datetime.now()
    time_diff = (now - st.session_state.last_update).total_seconds()

    if time_diff >= update_interval:

        usage = generate_usage()
        st.session_state.data.append(usage)

        st.session_state.simulated_minutes += minutes_per_reading
        st.session_state.last_update = now

        st.rerun()

# =====================================================
# METRICS DISPLAY
# =====================================================

total_usage = sum(st.session_state.data)
bill = calculate_slab_bill(total_usage)

m1, m2, m3 = st.columns(3)

m1.metric("Latest Reading", f"{st.session_state.data[-1] if st.session_state.data else 0} kWh")
m2.metric("Total Usage", f"{round(total_usage,3)} kWh")
m3.metric("Estimated Bill", f"₹{bill}")

if total_usage > DAILY_LIMIT:
    st.error("⚠ Daily limit exceeded!")

# =====================================================
# GRAPH
# =====================================================

if st.session_state.data:
    df = pd.DataFrame(st.session_state.data, columns=["Usage"])
    df["Cumulative"] = df["Usage"].cumsum()
    st.line_chart(df["Cumulative"])

# =====================================================
# AI PREDICTION
# =====================================================

st.subheader("Next Reading")

prediction = predict_next_reading(st.session_state.data)

if prediction:
    st.success(f"Predicted Next Reading: {prediction} kWh")
else:
    st.info("Need at least 10 readings.")

# =====================================================
# MONTHLY PROJECTION (REALISTIC)
# =====================================================

st.subheader("📅 Monthly Bill Projection")

monthly_result = predict_monthly_bill(
    st.session_state.data,
    st.session_state.simulated_minutes
)

if monthly_result:
    usage_30, bill_30 = monthly_result
    c1, c2 = st.columns(2)
    c1.metric("Estimated 30-Day Usage", f"{usage_30} kWh")
    c2.metric("Projected Monthly Bill", f"₹{bill_30}")
else:
    st.info("Run simulation longer for accurate projection.")