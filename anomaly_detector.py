import csv
import statistics


def detect_anomalies():
    usages = []

    try:
        with open("usage_log.csv", mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                usages.append(float(row["Usage_kWh"]))
    except FileNotFoundError:
        print("No data found.")
        return

    if len(usages) < 5:
        print("Not enough data for anomaly detection.")
        return

    mean = statistics.mean(usages)
    std_dev = statistics.stdev(usages)

    threshold = mean + 2 * std_dev

    print("\nAnomaly Detection Report")
    print("------------------------")

    for value in usages:
        if value > threshold:
            print(f"⚠ Abnormal usage detected: {value} kWh")