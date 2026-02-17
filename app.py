import streamlit as st
import time
import pandas as pd
import random
import numpy as np
from sklearn.linear_model import LinearRegression

# =====================================================
# CONFIG
# =====================================================

DAILY_LIMIT = 5.0

SLABS = [
    (3, 5),
    (6, 7),
    (float('inf'), 9)
]

TIME_OPTIONS = {
    "5 Seconds per Reading": 5,
    "10 Seconds per Reading": 10,
    "30 Seconds per Reading": 30
}

# =====================================================
# DARK UI
# =====================================================

st.markdown("""
<style>
body { background-color: #0E1117; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

.stMetric {
    background-color: #1C1F26;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 0px 12px rgba(0,255,198,0.25);
}

.stButton>button {
    background-color: #00FFC6;
    color: black;
    border-radius: 8px;
    font-weight: bold;
}

.stButton>button:hover {
    background-color: #00d4a8;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE INIT
# =====================================================

if "data" not in st.session_state:
    st.session_state.data = []

if "running" not in st.session_state:
    st.session_state.running = False

if "simulated_seconds" not in st.session_state:
    st.session_state.simulated_seconds = 0

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

    model = LinearRegression()
    model.fit(df[["Index"]], df["Usage"])

    prediction = model.predict([[len(df)]])[0]
    return round(prediction, 3)


def predict_monthly_bill(data, simulated_seconds):
    if len(data) < 10 or simulated_seconds == 0:
        return None

    total_usage = sum(data)

    usage_per_second = total_usage / simulated_seconds

    monthly_seconds = 30 * 24 * 60 * 60

    estimated_monthly_usage = usage_per_second * monthly_seconds
    monthly_bill = calculate_slab_bill(estimated_monthly_usage)

    return round(estimated_monthly_usage, 2), round(monthly_bill, 2)

# =====================================================
# HEADER
# =====================================================

st.markdown(
    "<h1 style='text-align:center;color:#00FFC6;'>⚡ Household Electricity Consumption Analysis (Project Model)</h1>",
    unsafe_allow_html=True
)
st.markdown("<hr style='border:1px solid #00FFC6;'>", unsafe_allow_html=True)

# =====================================================
# SIMULATION SETTINGS
# =====================================================

colA, colB = st.columns(2)

speed_label = colA.selectbox("Simulation Speed", list(TIME_OPTIONS.keys()))
seconds_per_reading = TIME_OPTIONS[speed_label]

# =====================================================
# CONTROL BUTTONS
# =====================================================

c1, c2, c3 = st.columns(3)

if c1.button("Start"):
    st.session_state.running = True

if c2.button("Stop"):
    st.session_state.running = False

if c3.button("Reset"):
    st.session_state.running = False
    st.session_state.data = []
    st.session_state.simulated_seconds = 0
    st.rerun()

# =====================================================
# REAL-TIME LOOP (SAFE VERSION)
# =====================================================

if st.session_state.running:
    usage = generate_usage()
    st.session_state.data.append(usage)
    st.session_state.simulated_seconds += seconds_per_reading

    time.sleep(seconds_per_reading)
    st.rerun()

# =====================================================
# METRICS
# =====================================================

total_usage = sum(st.session_state.data)
bill = calculate_slab_bill(total_usage)

m1, m2, m3 = st.columns(3)

latest = st.session_state.data[-1] if st.session_state.data else 0

m1.metric("Latest Reading", f"{latest} kWh")
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

st.subheader("AI Prediction")

prediction = predict_next_reading(st.session_state.data)

if prediction:
    st.success(f"Predicted Next Reading: {prediction} kWh")
else:
    st.info("Need at least 10 readings.")

# =====================================================
# MONTHLY PROJECTION
# =====================================================

st.subheader("📅 Monthly Bill Projection")

monthly_result = predict_monthly_bill(
    st.session_state.data,
    st.session_state.simulated_seconds
)

if monthly_result:
    u30, b30 = monthly_result
    c1, c2 = st.columns(2)
    c1.metric("Estimated 30-Day Usage", f"{u30} kWh")
    c2.metric("Projected Monthly Bill", f"₹{b30}")
else:
    st.info("Run simulation longer for projection.")