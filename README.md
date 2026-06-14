# City Route Optimizer 🗺️

A real-time ride-sharing / delivery route optimizer backend built with FastAPI. This project demonstrates core data structures and algorithms in a production-like environment.

## 🚀 Phase 1: Backend Foundation

Currently implemented:
*   **Graph Adjacency List**: Memory-efficient representation of city intersections and roads.
*   **Dijkstra's Algorithm & Min-Heap**: Calculates the absolute shortest path between nodes using `heapq` for $O(\log N)$ performance.
*   **LRU Cache**: `OrderedDict` implementation to cache and instantly retrieve recently requested routes, saving CPU cycles.
*   **FastAPI REST API**: Asynchronous endpoints to interact with the routing engine.

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
4. Open the interactive API documentation in your browser:
   `http://127.0.0.1:8000/docs`
