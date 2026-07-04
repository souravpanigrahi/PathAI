import requests
import time

BASE = "http://127.0.0.1:8000"

print("Waiting for graph to load on local server...")
while True:
    try:
        if requests.get(f"{BASE}/").json().get("graph_ready"):
            break
    except:
        pass
    time.sleep(1)
print("Graph ready!\n")

# 1. Clear the cache
print("--- 1. Clearing Cache ---")
print(requests.delete(f"{BASE}/api/cache").json())

# 2. Check initial stats
print("\n--- 2. Initial Stats ---")
print(requests.get(f"{BASE}/api/cache/stats").json())

# 3. Request a route (should be a MISS)
print("\n--- 3. First Route Request (Expect Miss) ---")
payload = {"start_node": "30037235", "end_node": "2197652486"}
r1 = requests.post(f"{BASE}/api/route", json=payload).json()
print(f"Cached: {r1.get('cached')} | Time: {r1.get('response_time_ms')} ms")

# 4. Request the exact same route (should be a HIT)
print("\n--- 4. Second Route Request (Expect Hit) ---")
r2 = requests.post(f"{BASE}/api/route", json=payload).json()
print(f"Cached: {r2.get('cached')} | Time: {r2.get('response_time_ms')} ms")

# 5. Check stats again
print("\n--- 5. Final Stats ---")
print(requests.get(f"{BASE}/api/cache/stats").json())
