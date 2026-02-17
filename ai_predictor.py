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
        print("No data found.")
        return

    if len(daily_totals) < 2:
        print("Need at least 2 days of data.")
        return

    dates = sorted(daily_totals.keys())
    usages = [daily_totals[d] for d in dates]

    X = np.arange(len(usages)).reshape(-1, 1)
    y = np.array(usages)

    model = LinearRegression()
    model.fit(X, y)

    prediction = model.predict([[len(usages)]])[0]

    print("\nAI Prediction")
    print("-------------")
    print(f"Predicted next-day usage: {round(prediction, 3)} kWh")