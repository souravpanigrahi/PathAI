"""
Driver-related API endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from app.data.drivers import drivers
from app.core.kdtree import build_driver_tree, find_nearest_driver

router = APIRouter()


@router.get("/drivers")
async def list_drivers():
    """List all drivers with their current status (for debugging)."""
    return {"count": len(drivers), "drivers": drivers}


@router.get("/drivers/nearest")
async def nearest_driver(
    lat: float = Query(..., description="Query latitude"),
    lng: float = Query(..., description="Query longitude"),
):
    """Find the nearest available driver to the given (lat, lng) point."""
    tree, available = build_driver_tree(drivers)

    if tree is None:
        raise HTTPException(status_code=404, detail="No available drivers found")

    driver, distance = find_nearest_driver(tree, available, lat, lng)

    return {
        "nearest_driver": driver,
        "distance_meters": round(distance, 2),
    }
