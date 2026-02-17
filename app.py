import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ---------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------

DAILY_LIMIT = 15
SIMULATION_SPEED = 0.5  # seconds

SLABS = [
    (100, 5),
    (300, 7),
    (float("inf"), 9)
]

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

if "data" not in st.session_state:
    st.session_state.data = []

if "running" not in st.session_state:
    st.session_state.running = False

# ---------------------------------------------------
# BILL CALCULATION
# ---------------------------------------------------

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

# ---------------------------------------------------
# REALISTIC TIME-SERIES SIMULATION
# ---------------------------------------------------

def generate_usage(hour):
    base = 0.3 + 0.2 * np.sin(hour / 24 * 2 * np.pi)
    noise = random.uniform(-0.05, 0.05)
    return round(max(base + noise, 0.05), 3)

# ---------------------------------------------------
# FEATURE ENGINEERING
# ---------------------------------------------------

def create_features(data):
    df = pd.DataFrame(data, columns=["Usage"])
    df["lag1"] = df["Usage"].shift(1)
    df["lag2"] = df["Usage"].shift(2)
    df["rolling_mean"] = df["Usage"].rolling(3).mean()
    df.dropna(inplace=True)
    return df

# ---------------------------------------------------
# MODEL TRAINING & EVALUATION
# ---------------------------------------------------

def train_models(data):

    if len(data) < 20:
        return None

    df = create_features(data)

    X = df[["lag1", "lag2", "rolling_mean"]]
    y = df["Usage"]

    split = int(len(df) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    lr = LinearRegression()
    rf = RandomForestRegressor(n_estimators=100)

    lr.fit(X_train, y_train)
    rf.fit(X_train, y_train)

    lr_pred = lr.predict(X_test)
    rf_pred = rf.predict(X_test)

    metrics = {
        "Linear Regression": {
            "MAE": mean_absolute_error(y_test, lr_pred),
            "RMSE": np.sqrt(mean_squared_error(y_test, lr_pred)),
            "R2": r2_score(y_test, lr_pred)
        },
        "Random Forest": {
            "MAE": mean_absolute_error(y_test, rf_pred),
            "RMSE": np.sqrt(mean_squared_error(y_test, rf_pred)),
            "R2": r2_score(y_test, rf_pred)
        }
    }

    return metrics, lr, rf

# ---------------------------------------------------
# ANOMALY DETECTION
# ---------------------------------------------------

def detect_anomalies(data):
    if len(data) < 20:
        return None

    df = pd.DataFrame(data, columns=["Usage"])
    model = IsolationForest(contamination=0.05)
    df["anomaly"] = model.fit_predict(df[["Usage"]])
    return df

# ---------------------------------------------------
# MONTHLY PROJECTION
# ---------------------------------------------------

def project_monthly_bill(data):
    if len(data) < 20:
        return None

    avg_hourly = np.mean(data)
    daily_estimate = avg_hourly * 24
    monthly_usage = daily_estimate * 30
    monthly_bill = calculate_slab_bill(monthly_usage)

    return round(monthly_usage, 2), monthly_bill

# ---------------------------------------------------
# UI
# ---------------------------------------------------

st.title("⚡ Smart Electricity AI Dashboard (Capstone Level)")

col1, col2, col3 = st.columns(3)

if col1.button("Start"):
    st.session_state.running = True

if col2.button("Stop"):
    st.session_state.running = False

if col3.button("Reset"):
    st.session_state.data = []

placeholder = st.empty()

# ---------------------------------------------------
# REAL-TIME SIMULATION LOOP
# ---------------------------------------------------

if st.session_state.running:

    hour = len(st.session_state.data) % 24
    usage = generate_usage(hour)
    st.session_state.data.append(usage)

    total = sum(st.session_state.data)
    bill = calculate_slab_bill(total)

    with placeholder.container():
        m1, m2, m3 = st.columns(3)
        m1.metric("Latest Reading", f"{usage} kWh")
        m2.metric("Total Usage", f"{round(total,2)} kWh")
        m3.metric("Estimated Bill", f"₹{bill}")

        df = pd.DataFrame(st.session_state.data, columns=["Usage"])
        df["Cumulative"] = df["Usage"].cumsum()
        st.line_chart(df["Cumulative"])

        if total > DAILY_LIMIT:
            st.error("⚠ Daily limit exceeded!")

    time.sleep(SIMULATION_SPEED)
    st.rerun()

# ---------------------------------------------------
# AI ANALYSIS SECTION
# ---------------------------------------------------

st.header("AI Model Evaluation")

model_output = train_models(st.session_state.data)

if model_output:
    metrics, lr_model, rf_model = model_output

    for model_name, values in metrics.items():
        st.subheader(model_name)
        st.write(f"MAE: {values['MAE']:.4f}")
        st.write(f"RMSE: {values['RMSE']:.4f}")
        st.write(f"R² Score: {values['R2']:.4f}")
else:
    st.info("Need at least 20 readings for model training.")

# ---------------------------------------------------
# ANOMALY DETECTION
# ---------------------------------------------------

st.header("Anomaly Detection")

anomaly_df = detect_anomalies(st.session_state.data)

if anomaly_df is not None:
    anomalies = anomaly_df[anomaly_df["anomaly"] == -1]
    st.write(f"Detected {len(anomalies)} anomalies")
else:
    st.info("Need at least 20 readings for anomaly detection.")

# ---------------------------------------------------
# MONTHLY BILL PROJECTION
# ---------------------------------------------------

st.header("Monthly Projection")

monthly = project_monthly_bill(st.session_state.data)

if monthly:
    usage_30, bill_30 = monthly
    st.metric("Projected 30-Day Usage", f"{usage_30} kWh")
    st.metric("Projected Monthly Bill", f"₹{bill_30}")
else:
    st.info("Need at least 20 readings for monthly projection.")