---
title: City Route Optimizer
emoji: 🗺️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# City Route Optimizer 🗺️

A real-time ride-sharing / delivery route optimizer backend built with FastAPI. This project demonstrates core data structures, algorithms, and machine learning in a production-like environment.

## 🚀 Phase 1: Backend Foundation

*   **Graph Adjacency List**: Memory-efficient representation of city intersections and roads.
*   **Dijkstra's Algorithm & Min-Heap**: Calculates the absolute shortest path between nodes using `heapq` for $O(\log N)$ performance.
*   **LRU Cache**: `OrderedDict` implementation to cache and instantly retrieve recently requested routes, saving CPU cycles.
*   **FastAPI REST API**: Asynchronous endpoints to interact with the routing engine.

## 🗺️ Phase 2: Real-World Routing & Dispatch

*   **OpenStreetMap Integration**: Downloads Chennai's drivable road network (~60k+ nodes) via `osmnx` and caches it as GraphML for fast restarts.
*   **KD-Tree Spatial Index**: `scipy.spatial.KDTree` for $O(\log N)$ nearest-driver and nearest-graph-node lookups.
*   **Haversine Distance**: Real-world distance calculation in metres instead of raw Euclidean degree distance.
*   **Driver Management**: 20 seeded drivers with Chennai coordinates, tracked as available/busy in-memory.
*   **Order Dispatcher**: FIFO `deque`-based order queue with automatic driver assignment — nearest available driver is matched, marked busy, and Dijkstra route is computed from driver → pickup.
*   **Anti-Double-Booking**: Drivers marked `"busy"` on assignment; KDTree rebuilt per request to reflect current availability. Orders re-queued (not lost) when no drivers are available.

## 🚦 Phase 3: Dynamic Traffic Weighting

*   **Traffic-Aware Edge Weights**: Every edge in the graph stores both the raw `base_weight` (metres) and the OSMnx `highway` road type. Dijkstra's cost function now calls `get_effective_weight()` at query time, scaling each edge cost by a live traffic multiplier.
*   **`get_traffic_factor(hour, day, road_type)`**: Returns road-type + time-of-day multipliers for Chennai:
    *   `primary` / `trunk` roads: **2.5×** during weekday rush hours (8–10 AM), **2.2×** evening (6–9 PM).
    *   `secondary` roads: **1.6×** during peak hours.
    *   Late-night (11 PM – 6 AM): **0.8×** (faster than normal).
    *   Weekends before noon: **0.9×**.
*   **Path Rerouting**: Dijkstra actively avoids heavily-penalised primary roads during rush hours, choosing longer-but-faster residential detours. Tested: **64-node rush-hour path** vs. **51-node off-peak path** for the same origin/destination.
*   **Traffic Context in Responses**: Every route response now includes a `traffic_context` object with:
    *   `current_hour` — the exact hour used for the traffic calculation.
    *   `avg_traffic_factor` — average multiplier across all edges in the chosen path.
    *   `traffic_level` — `"light"` / `"moderate"` / `"heavy"`.
    *   `effective_distance_meters` — the traffic-weighted cost Dijkstra optimised against.
    *   `base_distance_meters` — the true physical road length of the same path.

## 🤖 Phase 4: Machine Learning — ETA Prediction

*   **Gradient Boosting Regressor**: Trained on 2 000 synthetic but realistic Chennai delivery samples using `scikit-learn`. Achieves **R² ≈ 0.93** and **RMSE ≈ 4.3 minutes**.
*   **Feature Engineering**:
    *   `distance_meters`, `hour_of_day`, `day_of_week`, `road_type_encoded`
    *   `avg_traffic_factor` (from Phase 3 traffic engine)
    *   `num_path_nodes` (proxy for route complexity)
    *   `area_density_score` (deterministic density score seeded by pickup lat/lng)
*   **Realistic Synthetic Data**: Training labels account for school-hour delays (8–9 AM, 3–4 PM), Friday evening multipliers (1.3–1.6×), random 5–20 min incidents (8% of orders), and area density penalties. ETAs are capped at 90 minutes.
*   **`get_area_density(lat, lng)`**: Returns a deterministic float 0.8–1.8 seeded by coordinates — same pickup location always returns the same density score.
*   **Graceful Fallback**: If the `eta_model.joblib` file is missing, predictions fall back to a simple speed-based heuristic so the API never crashes.
*   **Model stored at**: `backend/app/ml/eta_model.joblib` — serialized with `joblib`.

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/route` | Shortest path + traffic context + ML ETA |
| `GET` | `/api/drivers` | List all drivers with current status |
| `GET` | `/api/drivers/nearest?lat=X&lng=Y` | Find nearest available driver |
| `POST` | `/api/orders` | Create order, assign driver, return ETA |
| `GET` | `/api/orders/{order_id}` | Check order status, route & ETA |
| `GET` | `/api/cache/stats` | View LRU cache hit rate, size, and capacity |
| `DELETE` | `/api/cache` | Clear the LRU route cache |

### Example Response — `POST /api/orders`
```json
{
  "order": { "order_id": "...", "status": "assigned", ... },
  "assignment": {
    "result": "assigned",
    "route_distance_meters": 2817.4,
    "eta_minutes": 8.1,
    "area_density_score": 1.37,
    "traffic_context": {
      "current_hour": 14,
      "avg_traffic_factor": 1.0,
      "traffic_level": "light",
      "effective_distance_meters": 2817.4,
      "base_distance_meters": 2817.4
    }
  }
}
```

## 🏗️ Architecture

```
backend/
├── app/
│   ├── api/
│   │   ├── routes.py            # Dijkstra routing endpoint + ETA
│   │   ├── driver_routes.py     # Driver list & nearest lookup
│   │   └── order_routes.py      # Order creation & status
│   ├── core/
│   │   ├── graph.py             # Adjacency list Graph (stores road_type per edge)
│   │   ├── dijkstra.py          # Traffic-aware shortest path + traffic_context
│   │   ├── kdtree.py            # Spatial index for drivers
│   │   ├── dispatcher.py        # Order queue, driver assignment & ETA injection
│   │   ├── traffic.py           # get_traffic_factor & get_effective_weight
│   │   └── cache.py             # LRU route cache (hit/miss stats)
│   ├── ml/
│   │   ├── train_eta.py         # Synthetic data generation + GBR training script
│   │   ├── eta_predictor.py     # Model loader + predict_eta + get_area_density
│   │   └── eta_model.joblib     # Trained GradientBoostingRegressor artifact
│   ├── data/
│   │   ├── drivers.py           # In-memory driver store
│   │   └── seed_drivers.py      # Fake driver generator
│   ├── utils/
│   │   └── osm.py               # OSM download, graph loading (highway field extraction)
│   └── main.py                  # FastAPI app & startup lifecycle
├── data/
│   └── chennai.graphml          # Cached OSM graph (auto-downloaded)
└── requirements.txt
```

## 💻 Local Development

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Train the ETA model (one-time):
   ```bash
   python app/ml/train_eta.py
   ```
4. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```
   > **Note:** The first run downloads Chennai's road network from OSM (~1-2 min). Subsequent starts load from the cached `data/chennai.graphml` file in seconds.

5. Open the interactive API documentation in your browser:
   `http://127.0.0.1:8000/docs`
