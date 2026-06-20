from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.core.graph import Graph
from app.core.dijkstra import find_shortest_path
from app.core.cache import LRUCache

router = APIRouter()

# --- Shared Global State ---
# The graph is populated at startup by main.py's lifespan handler
# with real Chennai OSM data. Routes read from this shared instance.
city_graph = Graph()
route_cache = LRUCache(capacity=100)

# Pydantic model to validate incoming JSON requests
class RouteRequest(BaseModel):
    start_node: str
    end_node: str

class RouteResponse(BaseModel):
    path: List[str]
    distance: float
    cached: bool

@router.post("/route", response_model=RouteResponse)
async def get_route(request: RouteRequest):
    start = request.start_node
    end = request.end_node

    # 1. Check the Cache first!
    cached_result = route_cache.get(start, end)
    if cached_result:
        path, distance = cached_result
        return RouteResponse(path=path, distance=distance, cached=True)

    # 2. If not in cache, calculate the expensive way using Dijkstra
    path, distance = find_shortest_path(city_graph, start, end)

    if path is None:
        raise HTTPException(status_code=404, detail="No path found between these nodes")

    # 3. Store the result in the Cache for next time
    route_cache.put(start, end, path, distance)

    return RouteResponse(path=path, distance=distance, cached=False)
