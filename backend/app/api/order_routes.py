"""
Order-related API endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.dispatcher import (
    create_order,
    assign_next_order,
    orders_db,
    order_queue,
)


router = APIRouter()


# --- Request / Response models ---

class CreateOrderRequest(BaseModel):
    pickup_lat: float
    pickup_lng: float
    delivery_lat: float
    delivery_lng: float


# --- Endpoints ---

@router.post("/orders")
async def post_order(req: CreateOrderRequest):
    """
    Create a new order and immediately attempt to assign the nearest
    available driver. Returns the order status and assignment details.
    """
    # 1. Create the order (queues it)
    order_id = create_order(
        pickup_lat=req.pickup_lat,
        pickup_lng=req.pickup_lng,
        delivery_lat=req.delivery_lat,
        delivery_lng=req.delivery_lng,
    )

    # 2. Immediately try to assign a driver
    assignment = assign_next_order()

    # 3. Return the order + assignment result
    order = orders_db[order_id]

    return {
        "order": order.model_dump(),
        "assignment": assignment,
    }


@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Look up any order's current status by its order_id."""
    order = orders_db.get(order_id)

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return order.model_dump()
