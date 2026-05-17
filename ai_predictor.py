import csv
from collections import defaultdict
from sklearn.linear_model import LinearRegression
import numpy as np


def predict_next_day_usage():

    daily_totals = defaultdict(float)

    try:
        with open("usage_log.csv", mode="r") as file:

            reader = csv.DictReader(file)

            for row in reader:

                date = row["Timestamp"].split(" ")[0]
                usage = float(row["Usage_kWh"])

                daily_totals[date] += usage

    except FileNotFoundError:
        return None

    # Need minimum historical data
    if len(daily_totals) < 2:
        return None

    # Sort dates
    dates = sorted(daily_totals.keys())

    # Daily total usages
    usages = [daily_totals[d] for d in dates]

    # Prepare ML dataset
    X = np.arange(len(usages)).reshape(-1, 1)
    y = np.array(usages)

    # Linear Regression Model
    model = LinearRegression()
    model.fit(X, y)

    # Predict next day
    prediction = model.predict([[len(usages)]])[0]

    return round(prediction, 3)