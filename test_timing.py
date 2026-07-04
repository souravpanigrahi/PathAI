import requests
import time

# Pick two coordinates in Chennai
START_LAT, START_LNG = 13.0827, 80.2707
END_LAT, END_LNG = 12.9716, 80.2496

print(f"Waiting for local server to load the graph...")
while True:
    try:
        if requests.get("http://127.0.0.1:8000/").json().get("graph_ready"):
            break
    except:
        pass
    time.sleep(1)

# Hack to grab two valid node IDs using the loaded graph on the local server via a Python script
# We'll just execute this logic inside the test script.
# Wait, this test script is running outside the app process. We don't have access to the app's KDTree.
# So I'll just use two known nodes from the graphml that are far apart.
# Node near central Chennai: 261763717
# Node near Guindy: 2168393563

URL = "http://127.0.0.1:8000/api/route"
PAYLOAD = {
    "start_node": "30037235", 
    "end_node": "2197652486"
}

print("Running first request (Uncached / Dijkstra) ...")
r1 = requests.post(URL, json=PAYLOAD)
data1 = r1.json()

if "detail" in data1:
    print("Error:", data1["detail"])
else:
    print(f"Request 1 -> Cached: {data1.get('cached')}, Time: {data1.get('response_time_ms')} ms, Distance: {data1.get('distance')} m")

print("\nRunning second request (Cached) ...")
r2 = requests.post(URL, json=PAYLOAD)
data2 = r2.json()

if "detail" in data2:
    print("Error:", data2["detail"])
else:
    print(f"Request 2 -> Cached: {data2.get('cached')}, Time: {data2.get('response_time_ms')} ms, Distance: {data2.get('distance')} m")
