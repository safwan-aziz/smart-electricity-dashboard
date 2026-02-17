import csv
import matplotlib.pyplot as plt


def plot_cumulative_usage():
    cumulative = []
    total = 0.0

    try:
        with open("usage_log.csv", mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                usage = float(row["Usage_kWh"])
                total += usage
                cumulative.append(total)
    except FileNotFoundError:
        print("No data available.")
        return

    if not cumulative:
        print("No data to plot.")
        return

    plt.figure()
    plt.plot(cumulative)
    plt.title("Cumulative Electricity Usage")
    plt.xlabel("Reading Number")
    plt.ylabel("Total Usage (kWh)")
    plt.tight_layout()
    plt.show()