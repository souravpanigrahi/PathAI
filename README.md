# City Route Optimizer 🗺️

A real-time ride-sharing / delivery route optimizer backend built with FastAPI. This project demonstrates core data structures and algorithms in a production-like environment.

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

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/route` | Find shortest path between two graph nodes |
| `GET` | `/api/drivers` | List all drivers with current status |
| `GET` | `/api/drivers/nearest?lat=X&lng=Y` | Find nearest available driver |
| `POST` | `/api/orders` | Create order & auto-assign nearest driver |
| `GET` | `/api/orders/{order_id}` | Check order status, assigned driver & route |

## 🏗️ Architecture

```
backend/
├── app/
│   ├── api/
│   │   ├── routes.py            # Dijkstra routing endpoint
│   │   ├── driver_routes.py     # Driver list & nearest lookup
│   │   └── order_routes.py      # Order creation & status
│   ├── core/
│   │   ├── graph.py             # Adjacency list Graph class
│   │   ├── dijkstra.py          # Shortest path algorithm
│   │   ├── kdtree.py            # Spatial index for drivers
│   │   ├── dispatcher.py        # Order queue & driver assignment
│   │   └── cache.py             # LRU route cache
│   ├── data/
│   │   ├── drivers.py           # In-memory driver store
│   │   └── seed_drivers.py      # Fake driver generator
│   ├── utils/
│   │   └── osm.py               # OSM download & graph loading
│   └── main.py                  # FastAPI app & startup
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
3. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```
   > **Note:** The first run downloads Chennai's road network from OSM (~1-2 min). Subsequent starts load from the cached `data/chennai.graphml` file in seconds.

4. Open the interactive API documentation in your browser:
   `http://127.0.0.1:8000/docs`
