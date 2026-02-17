import streamlit as st
import time
import pandas as pd
import random
import numpy as np
import matplotlib.pyplot as plt
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

</style>
""", unsafe_allow_html=True)

# -----------------------
# CONFIG
# -----------------------

DAILY_LIMIT = 5.0

SLABS = [
    (3, 5),
    (6, 7),
    (float('inf'), 9)
]

# -----------------------
# SESSION INIT
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

# -----------------------
# UI
# -----------------------

st.markdown("<h1 style='text-align: center; color: #00FFC6;'>⚡ Smart Electricity Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border:1px solid #00FFC6;'>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

if col1.button("Start Simulation"):
    st.session_state.running = True

if col2.button("Stop Simulation"):
    st.session_state.running = False

placeholder_metrics = st.empty()
placeholder_graph = st.empty()

# -----------------------
# REAL-TIME LOOP
# -----------------------

# -----------------------
# REAL-TIME LOOP (SMOOTH VERSION)
# -----------------------

if st.session_state.running:

    chart_placeholder = st.empty()

    while st.session_state.running:

        usage = generate_usage()
        st.session_state.data.append(usage)

        total_usage = sum(st.session_state.data)
        bill = calculate_slab_bill(total_usage)

        # Update metrics
        with placeholder_metrics.container():
          col1, col2, col3 = st.columns(3)

    col1.metric("Latest Reading", f"{usage} kWh")
    col2.metric("Total Usage", f"{round(total_usage,3)} kWh")
    col3.metric("Estimated Bill", f"₹{bill}")

    if total_usage > DAILY_LIMIT:
        st.error("⚠ Daily limit exceeded!")

        # Smooth live graph
        df = pd.DataFrame(st.session_state.data, columns=["Usage"])
        df["Cumulative"] = df["Usage"].cumsum()

        chart_placeholder.line_chart(df["Cumulative"])

        time.sleep(1)
        st.rerun()

# -----------------------
# AI SECTION
# -----------------------

st.subheader("AI Prediction")

prediction = predict_next_reading(st.session_state.data)

if prediction:
    st.success(f"Predicted Next Reading: {prediction} kWh")
else:
    st.info("Need at least 10 readings for prediction.")