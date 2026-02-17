import streamlit as st
import time
import pandas as pd
import random
import numpy as np
from sklearn.linear_model import LinearRegression

# -----------------------
# CUSTOM DARK UI STYLING
# -----------------------

st.markdown("""
<style>

body {
    background-color: #0E1117;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

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

.stButton>button:hover {
    background-color: #00d4a8;
}

/* RESET BUTTON STYLE */
button[kind="secondary"] {
    background-color: #ff4b4b !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: bold !important;
}

button[kind="secondary"]:hover {
    background-color: #cc0000 !important;
}

</style>
""", unsafe_allow_html=True)
st.set_page_config(page_title="Smart Electricity Dashboard", layout="wide")

st.markdown("""
<style>
body {
    background-color: #0E1117;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

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

.stButton>button:hover {
    background-color: #00d4a8;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# CONFIG
# -----------------------

DAILY_LIMIT = 5.0

SLABS = [
    (3, 5),            # first 3 units at ₹5
    (6, 7),            # next 3 units at ₹7
    (float('inf'), 9)  # remaining at ₹9
]

# -----------------------
# SESSION STATE INIT
# -----------------------

if "data" not in st.session_state:
    st.session_state.data = []

if "running" not in st.session_state:
    st.session_state.running = False

# -----------------------
# FUNCTIONS
# -----------------------

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


def predict_monthly_bill(data):
    if len(data) < 10:
        return None

    avg_usage = np.mean(data)
    estimated_30_day_usage = avg_usage * 30
    projected_bill = calculate_slab_bill(estimated_30_day_usage)

    return round(estimated_30_day_usage, 2), round(projected_bill, 2)

# -----------------------
# UI HEADER
# -----------------------

st.markdown("<h1 style='text-align: center; color: #00FFC6;'>⚡ Smart Electricity Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border:1px solid #00FFC6;'>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

if col1.button("Start Simulation"):
    st.session_state.running = True

if col2.button("Stop Simulation"):
    st.session_state.running = False

if col3.button("Reset"):
    st.session_state.running = False
    st.session_state.data = []
    st.rerun()

placeholder_metrics = st.empty()
placeholder_graph = st.empty()

# -----------------------
# REAL-TIME LOOP
# -----------------------

if st.session_state.running:

    usage = generate_usage()
    st.session_state.data.append(usage)

    total_usage = sum(st.session_state.data)
    bill = calculate_slab_bill(total_usage)

    monthly_result = predict_monthly_bill(st.session_state.data)

    with placeholder_metrics.container():
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Latest Reading", f"{usage} kWh")
        col2.metric("Total Usage", f"{round(total_usage,3)} kWh")
        col3.metric("Estimated Bill", f"₹{bill}")

        if monthly_result:
            usage_30, bill_30 = monthly_result
            col4.metric("Est. 30-Day Usage", f"{usage_30} kWh")
            col5.metric("Projected Monthly Bill", f"₹{bill_30}")
        else:
            col4.metric("Est. 30-Day Usage", "Waiting...")
            col5.metric("Projected Monthly Bill", "Waiting...")

    if total_usage > DAILY_LIMIT:
        st.error("⚠ Daily limit exceeded!")

    df = pd.DataFrame(st.session_state.data, columns=["Usage"])
    df["Cumulative"] = df["Usage"].cumsum()

    placeholder_graph.line_chart(df["Cumulative"])

    time.sleep(1)
    st.rerun()

# -----------------------
# AI SECTION (VISIBLE EVEN WHEN STOPPED)
# -----------------------

st.subheader("AI Prediction")

prediction = predict_next_reading(st.session_state.data)

if prediction:
    st.success(f"Predicted Next Reading: {prediction} kWh")
else:
    st.info("Need at least 10 readings for prediction.")

# -----------------------
# MONTHLY PROJECTION WHEN STOPPED
# -----------------------

if not st.session_state.running:

    st.subheader("📅 Monthly Bill Projection")

    monthly_result = predict_monthly_bill(st.session_state.data)

    if monthly_result:
        usage_30, bill_30 = monthly_result
        st.metric("Estimated Monthly Usage (30 days)", f"{usage_30} kWh")
        st.metric("Projected Monthly Bill", f"₹{bill_30}")
    else:
        st.info("Need at least 10 readings for monthly prediction.")