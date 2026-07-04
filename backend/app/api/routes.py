from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.core.graph import Graph
from app.core.dijkstra import find_shortest_path

router = APIRouter()

# --- Shared Global State ---
# The graph is populated at startup by main.py's lifespan handler
# with real Chennai OSM data. Routes read from this shared instance.
city_graph = Graph()


import time

# Pydantic model to validate incoming JSON requests
class RouteRequest(BaseModel):
    start_node: str
    end_node: str

class RouteResponse(BaseModel):
    path: List[str]
    distance: float
    cached: bool
    response_time_ms: float

@router.post("/route", response_model=RouteResponse)
async def get_route(request: RouteRequest):
    req_start_time = time.time()
    from app.main import route_cache
    
    start = request.start_node
    end = request.end_node

    # 1. Check the Cache first!
    key = (start, end)
    cached_result = route_cache.get(key)
    
    if cached_result:
        print("[Router] CACHE HIT")
        elapsed_ms = round((time.time() - req_start_time) * 1000, 2)
        return RouteResponse(
            path=cached_result["path"], 
            distance=cached_result["distance"], 
            cached=True,
            response_time_ms=elapsed_ms
        )

    # 2. If not in cache, calculate the expensive way using Dijkstra
    print("[Router] CACHE MISS")
    path, distance = find_shortest_path(city_graph, start, end)

    if path is None:
        raise HTTPException(status_code=404, detail="No path found between these nodes")

    # 3. Store the result in the Cache for next time
    route_cache.put(key, {"path": path, "distance": distance})

    elapsed_ms = round((time.time() - req_start_time) * 1000, 2)
    return RouteResponse(path=path, distance=distance, cached=False, response_time_ms=elapsed_ms)


@router.get("/cache/stats")
async def get_cache_stats():
    """Returns the current size, capacity, and hit rate of the route cache."""
    from app.main import route_cache
    return route_cache.stats()

@router.delete("/cache")
async def clear_cache():
    """Clears the route cache and resets stats."""
    from app.main import route_cache
    route_cache.clear()
    return {"message": "Cache cleared successfully"}
