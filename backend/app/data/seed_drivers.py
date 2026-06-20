"""
Generates 20 fake drivers with realistic Chennai coordinates.
Run directly:  python -m app.data.seed_drivers   (from backend/)
Or call seed() programmatically at startup.
"""

import random
from app.data.drivers import drivers

# Chennai bounding box
LAT_MIN, LAT_MAX = 12.95, 13.20
LNG_MIN, LNG_MAX = 80.10, 80.30

# Simple Indian-sounding fake names
FIRST_NAMES = [
    "Arun", "Priya", "Karthik", "Divya", "Rajesh",
    "Meena", "Suresh", "Lakshmi", "Venkat", "Anitha",
    "Ganesh", "Kavitha", "Mohan", "Deepa", "Vijay",
    "Revathi", "Senthil", "Nithya", "Prakash", "Sangeetha",
]

LAST_NAMES = [
    "Kumar", "Rajan", "Subramanian", "Iyer", "Pillai",
    "Naidu", "Reddy", "Murugan", "Krishnan", "Sundaram",
    "Sharma", "Nair", "Rao", "Pandian", "Selvam",
    "Babu", "Devi", "Natarajan", "Chandra", "Balaji",
]


def seed(count: int = 20) -> None:
    """Generate `count` fake drivers and append them to the shared drivers list."""
    random.seed(42)  # Reproducible results

    drivers.clear()

    for i in range(1, count + 1):
        driver = {
            "driver_id": i,
            "name": f"{FIRST_NAMES[i - 1]} {random.choice(LAST_NAMES)}",
            "lat": round(random.uniform(LAT_MIN, LAT_MAX), 6),
            "lng": round(random.uniform(LNG_MIN, LNG_MAX), 6),
            "status": "available",
        }
        drivers.append(driver)


def print_drivers() -> None:
    """Pretty-print the current driver list."""
    print(f"\n{'='*65}")
    print(f"  {'ID':<5} {'Name':<25} {'Lat':>10} {'Lng':>10}  {'Status'}")
    print(f"{'='*65}")
    for d in drivers:
        print(f"  {d['driver_id']:<5} {d['name']:<25} {d['lat']:>10.6f} {d['lng']:>10.6f}  {d['status']}")
    print(f"{'='*65}")
    print(f"  Total: {len(drivers)} drivers\n")


if __name__ == "__main__":
    seed()
    print_drivers()
