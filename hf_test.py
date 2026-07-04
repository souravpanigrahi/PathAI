"""Stress test: create 21 orders to exhaust all 20 drivers on the live HF server."""
import requests
import random

BASE = "https://souravpgbhai-city-route-optimizer.hf.space"
random.seed(99)

print(f"Connecting to live server at {BASE} ...")

# Wait for graph to be ready
resp = requests.get(f"{BASE}/")
if not resp.json().get("graph_ready", False):
    print("Warning: The server says 'graph_ready' is False. The Chennai map is still downloading.")
    print("The test will still run, but all Dijkstra routes will return 'None'.")
    print("-" * 50)

print("Creating 21 orders to exhaust all 20 drivers...\n")

for i in range(1, 22):
    lat = round(random.uniform(12.95, 13.20), 4)
    lng = round(random.uniform(80.10, 80.30), 4)

    resp = requests.post(f"{BASE}/api/orders", json={
        "pickup_lat": lat,
        "pickup_lng": lng,
        "delivery_lat": 13.04,
        "delivery_lng": 80.23,
    })
    data = resp.json()
    assignment = data.get("assignment", {})
    result = assignment.get("result", "error")

    if result == "assigned":
        driver = assignment.get("assigned_driver", {})
        route_dist = assignment.get("route_distance_meters", "N/A")
        print(f"  Order #{i:2d} -> ASSIGNED to #{driver.get('driver_id', '?'):2d} {driver.get('name', '?'):<22s}  route: {route_dist} m")
    elif result == "no_drivers_available":
        print(f"  Order #{i:2d} -> NO_DRIVERS_AVAILABLE (order re-queued)")
    else:
        print(f"  Order #{i:2d} -> ERROR: {data}")

# Final driver status
print("\n" + "=" * 50)
drivers_resp = requests.get(f"{BASE}/api/drivers")
drivers = drivers_resp.json().get("drivers", [])
avail = sum(1 for d in drivers if d["status"] == "available")
busy = sum(1 for d in drivers if d["status"] == "busy")
print(f"  Available: {avail}  |  Busy: {busy}")
