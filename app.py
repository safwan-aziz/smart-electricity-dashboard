import streamlit as st
import pandas as pd
import random
from datetime import date
from streamlit_autorefresh import st_autorefresh

# =====================================================
# CONFIG
# =====================================================

MINUTES_PER_MONTH = 60 * 24 * 30  # 43200
TICK_INTERVAL_MS = 2000  # 2 seconds = 1 simulated minute

SLABS = [
    (100, 5),
    (300, 7),
    (float("inf"), 9)
]

# =====================================================
# SESSION INIT
# =====================================================

if "data" not in st.session_state:
    st.session_state.data = []

if "running" not in st.session_state:
    st.session_state.running = False

if "simulated_minutes" not in st.session_state:
    st.session_state.simulated_minutes = 0

if "daily_usage" not in st.session_state:
    st.session_state.daily_usage = 0

if "current_day" not in st.session_state:
    st.session_state.current_day = date.today()

if "daily_limit" not in st.session_state:
    st.session_state.daily_limit = 5.0

# =====================================================
# SIDEBAR SETTINGS
# =====================================================

st.sidebar.header("⚙ Settings")

st.session_state.daily_limit = st.sidebar.slider(
    "Set Daily Usage Limit (units)",
    min_value=1.0,
    max_value=20.0,
    value=st.session_state.daily_limit,
    step=0.5
)

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


def predict_monthly_bill(data, simulated_minutes):
    if simulated_minutes < 1:
        return None

    avg_per_minute = sum(data) / simulated_minutes
    estimated_monthly_units = avg_per_minute * MINUTES_PER_MONTH
    estimated_bill = calculate_slab_bill(estimated_monthly_units)

    return round(estimated_monthly_units, 2), round(estimated_bill, 2)

# =====================================================
# UI HEADER
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
    st.session_state.simulated_minutes = 0
    st.session_state.daily_usage = 0

# =====================================================
# REAL-TIME ENGINE
# =====================================================

if st.session_state.running:
    st_autorefresh(interval=TICK_INTERVAL_MS, key="live")

    usage = generate_usage()
    st.session_state.data.append(usage)

    # Each tick = 1 simulated minute
    st.session_state.simulated_minutes += 1

    # Daily reset logic
    today = date.today()
    if today != st.session_state.current_day:
        st.session_state.daily_usage = 0
        st.session_state.current_day = today

    st.session_state.daily_usage += usage

# =====================================================
# METRICS
# =====================================================

total_usage = sum(st.session_state.data)
current_bill = calculate_slab_bill(total_usage)
latest = st.session_state.data[-1] if st.session_state.data else 0

m1, m2, m3 = st.columns(3)
m1.metric("Latest Reading", f"{latest} units")
m2.metric("Total Usage (This Month)", f"{round(total_usage,2)} units")
m3.metric("Estimated Current Bill", f"₹{current_bill}")

# Daily exceed warning using custom limit
if st.session_state.daily_usage > st.session_state.daily_limit:
    st.error(
        f"⚠ Daily usage exceeded limit of {st.session_state.daily_limit} units!"
    )

# =====================================================
# GRAPH
# =====================================================

if st.session_state.data:
    df = pd.DataFrame(st.session_state.data, columns=["Usage"])
    df["Cumulative"] = df["Usage"].cumsum()
    st.line_chart(df["Cumulative"])

# =====================================================
# MONTHLY PREDICTION
# =====================================================

st.subheader("📅 Monthly Prediction")

if st.session_state.simulated_minutes >= 1:

    # Update every 5 minutes
    if st.session_state.simulated_minutes % 5 == 0:

        prediction = predict_monthly_bill(
            st.session_state.data,
            st.session_state.simulated_minutes
        )

        if prediction:
            est_units, est_bill = prediction
            c1, c2 = st.columns(2)
            c1.metric("Estimated Monthly Units", est_units)
            c2.metric("Estimated Monthly Bill", f"₹{est_bill}")
    else:
        st.info("Prediction updates every 5 simulated minutes.")
else:
    st.info("Monthly prediction will appear after 1 simulated minute.")