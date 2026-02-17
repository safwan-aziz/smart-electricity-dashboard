import time
from config import SIMULATION_INTERVAL, DAILY_LIMIT, SLABS
from data_handler import generate_usage_reading, log_usage_to_csv
from visualizer import plot_cumulative_usage
from ai_predictor import predict_next_day_usage
from anomaly_detector import detect_anomalies


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


def run_simulation():
    total_usage = 0.0

    print("\nSimulation Started (Press Ctrl+C to stop)\n")

    try:
        while True:
            usage = generate_usage_reading()
            log_usage_to_csv(usage)

            total_usage += usage
            bill = calculate_slab_bill(total_usage)

            print(f"New Reading: {usage} kWh")
            print(f"Total Usage: {round(total_usage, 3)} kWh")
            print(f"Estimated Bill (Slab): ₹{bill}")

            if total_usage > DAILY_LIMIT:
                print("⚠ Daily limit exceeded!")

            print("-----------------------------------")

            time.sleep(SIMULATION_INTERVAL)

    except KeyboardInterrupt:
        print("\nSimulation stopped.\n")


def main_menu():
    while True:
        print("\nSmart Electricity Monitoring System")
        print("1. Run Simulation")
        print("2. View Graph")
        print("3. Predict Next Day Usage (AI)")
        print("4. Detect Anomalies")
        print("5. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            run_simulation()
        elif choice == "2":
            plot_cumulative_usage()
        elif choice == "3":
            predict_next_day_usage()
        elif choice == "4":
            detect_anomalies()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main_menu()