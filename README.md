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

## 📚 Study Resources

If you want to dive deeper into the computer science concepts used in this project, here are some of the best resources on the internet:

*   **Graphs & Adjacency Lists**: [Khan Academy: Representing Graphs](https://www.khanacademy.org/computing/computer-science/algorithms/graph-representation/a/representing-graphs) - Great visual explanation of how grids work.
*   **Dijkstra's Algorithm**: [Computerphile: Dijkstra's Algorithm (YouTube)](https://www.youtube.com/watch?v=GazC3A4OQTE) - An absolute classic, visually walks through the math on a whiteboard.
*   **LRU Cache**: [NeetCode: LRU Cache Explanation (YouTube)](https://www.youtube.com/watch?v=7ABFKPK2hD4) - Breaks down exactly how big tech companies ask this question in interviews.

## ☁️ Deployment

When you are ready to put this on the internet for free, here are the best options:
*   **Railway.app** (Recommended): Very generous free tier, insanely easy to use. You just connect your GitHub repository and it auto-detects FastAPI and deploys it in seconds.
*   **Render.com**: Another great alternative with a free tier specifically for Python Web Services.
