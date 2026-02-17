# Configuration Settings

SIMULATION_INTERVAL = 1  # seconds
DAILY_LIMIT = 5.0        # kWh

# Slab-based billing
SLABS = [
    (3, 5),   # First 3 units → ₹5/unit
    (6, 7),   # Next 3 units → ₹7/unit
    (float('inf'), 9)  # Above 6 units → ₹9/unit
]