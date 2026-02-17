import random
import csv
import os
from datetime import datetime


def generate_usage_reading():
    return round(random.uniform(0.05, 0.60), 3)


def log_usage_to_csv(usage):
    filename = "usage_log.csv"
    file_exists = os.path.isfile(filename)

    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["Timestamp", "Usage_kWh"])

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, usage])