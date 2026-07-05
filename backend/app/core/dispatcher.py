"""
Dispatcher module — the central hub that connects orders, drivers, and routing.
Orders come in, get queued, matched to the nearest available driver, and dispatched.
"""

import uuid
from collections import deque
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from pydantic import BaseModel, Field

from app.core.kdtree import build_driver_tree, find_nearest_driver
from app.core.dijkstra import find_shortest_path
from app.api.routes import city_graph
from app.utils.osm import find_nearest_graph_node
from app.data.drivers import drivers


# ---------------------------------------------------------------------------
# Order model
# ---------------------------------------------------------------------------

class Order(BaseModel):
    """Represents a pickup-to-delivery order in the system."""
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pickup_lat: float
    pickup_lng: float
    delivery_lat: float
    delivery_lng: float
    status: str = "pending"          # "pending" | "assigned" | "delivered"
    assigned_driver_id: Optional[int] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Route from driver's location to pickup (populated on assignment)
    route_path: Optional[List[str]] = None
    route_distance_meters: Optional[float] = None
    traffic_context: Optional[dict] = None
    eta_minutes: Optional[float] = None
    area_density_score: Optional[float] = None


# ---------------------------------------------------------------------------
# In-memory stores
# ---------------------------------------------------------------------------

# FIFO queue of order_ids waiting to be assigned to a driver
order_queue: deque = deque()

# Lookup table: order_id → Order, so we can check any order's current status
orders_db: Dict[str, Order] = {}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_order(
    pickup_lat: float,
    pickup_lng: float,
    delivery_lat: float,
    delivery_lng: float,
) -> str:
    """
    Build a new Order, store it in orders_db, append its id to the
    order_queue, and return the order_id.
    """
    order = Order(
        pickup_lat=pickup_lat,
        pickup_lng=pickup_lng,
        delivery_lat=delivery_lat,
        delivery_lng=delivery_lng,
    )

    orders_db[order.order_id] = order
    order_queue.append(order.order_id)

    print(f"[Dispatcher] Created order {order.order_id[:8]}... "
          f"pickup=({pickup_lat}, {pickup_lng}) -> "
          f"delivery=({delivery_lat}, {delivery_lng})")

    return order.order_id


def assign_next_order() -> Dict[str, Any]:
    """
    Pop the oldest pending order from the queue and assign it to the
    nearest available driver.  After assignment, compute the Dijkstra
    route from the driver's location to the pickup point.

    Returns a dict summarising what happened:
        - "assigned"            -> order matched to a driver
        - "no_drivers_available"-> no available drivers; order re-queued
        - "queue_empty"         -> nothing to assign
    """
    # --- Nothing in the queue ---
    if not order_queue:
        return {"result": "queue_empty"}

    order_id = order_queue.popleft()
    order = orders_db[order_id]

    # --- Build a fresh KDTree over available drivers ---
    tree, available = build_driver_tree(drivers)

    if tree is None:
        # No drivers available — put the order back at the FRONT so it
        # stays first in line (don't lose it).
        order_queue.appendleft(order_id)
        print(f"[Dispatcher] No available drivers - order {order_id[:8]}... re-queued.")
        return {
            "result": "no_drivers_available",
            "order_id": order_id,
        }

    # --- Find nearest driver to the pickup location ---
    driver, distance_m = find_nearest_driver(
        tree, available, order.pickup_lat, order.pickup_lng
    )

    # --- Mark the driver as busy ---
    driver["status"] = "busy"

    # --- Update the order ---
    order.status = "assigned"
    order.assigned_driver_id = driver["driver_id"]

    # --- Compute route: driver location -> pickup ---
    driver_node = find_nearest_graph_node(driver["lat"], driver["lng"])
    pickup_node = find_nearest_graph_node(order.pickup_lat, order.pickup_lng)

    # 1. Check the Cache first!
    from app.main import route_cache
    key = (driver_node, pickup_node)
    cached_result = route_cache.get(key)
    
    if cached_result:
        print("[Dispatcher] CACHE HIT")
        path = cached_result["path"]
        route_dist = cached_result["distance"]
        traffic_context = cached_result.get("traffic_context")
    else:
        print("[Dispatcher] CACHE MISS")
        path, base_dist, traffic_context = find_shortest_path(city_graph, driver_node, pickup_node)
        if path is not None:
            # The "effective" distance is in traffic_context
            route_dist = traffic_context["effective_distance_meters"]
            # Store the result in the Cache for next time
            route_cache.put(key, {"path": path, "distance": route_dist, "traffic_context": traffic_context})

    from app.ml.eta_predictor import predict_eta, get_area_density
    area_density = get_area_density(order.pickup_lat, order.pickup_lng)
    eta_minutes = None

    if path is not None:
        order.route_path = path
        order.route_distance_meters = round(route_dist, 2)
        order.traffic_context = traffic_context
        order.area_density_score = area_density

        # Compute ETA using the ML model
        ctx = traffic_context or {}
        num_nodes = len(path)
        eta_minutes = predict_eta(
            distance_meters=route_dist,
            hour=ctx.get("current_hour", 12),
            day_of_week=datetime.now().weekday(),
            road_type="primary",  # conservative default for driver->pickup
            avg_traffic_factor=ctx.get("avg_traffic_factor", 1.0),
            num_path_nodes=num_nodes,
            area_density_score=area_density
        )
        order.eta_minutes = eta_minutes
        print(f"[Dispatcher] Route: {len(path)} nodes, {route_dist:.0f} m, ETA: {eta_minutes} min")
    else:
        order.route_path = None
        order.route_distance_meters = None
        order.traffic_context = None
        order.area_density_score = area_density
        traffic_context = None
        print(f"[Dispatcher] Warning: no route found from driver to pickup.")

    orders_db[order_id] = order

    print(f"[Dispatcher] Order {order_id[:8]}... assigned to "
          f"driver {driver['driver_id']} ({driver['name']}) - "
          f"{distance_m:.0f} m away.")

    return {
        "result": "assigned",
        "order_id": order_id,
        "assigned_driver": driver,
        "distance_meters": round(distance_m, 2),
        "route_path": order.route_path,
        "route_distance_meters": order.route_distance_meters,
        "traffic_context": traffic_context,
        "eta_minutes": eta_minutes,
        "area_density_score": area_density
    }


