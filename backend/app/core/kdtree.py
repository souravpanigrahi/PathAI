"""
KD-Tree for fast nearest-driver lookups using scipy.spatial.KDTree.
"""

from typing import Dict, Any, List, Optional, Tuple
from scipy.spatial import KDTree
import numpy as np
import math


def build_driver_tree(drivers: List[Dict[str, Any]]) -> Tuple[Optional[KDTree], List[Dict[str, Any]]]:
    """
    Filters the driver list to only status="available" drivers,
    then builds a KDTree from their (lat, lng) coordinates.

    Returns:
        (tree, available_drivers) — the KDTree and the filtered list
        that maps tree indices back to driver dicts.
        Returns (None, []) if no available drivers exist.
    """
    available = [d for d in drivers if d["status"] == "available"]

    if not available:
        return None, []

    coords = np.array([[d["lat"], d["lng"]] for d in available])
    tree = KDTree(coords)

    return tree, available


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculates the great-circle distance between two points on Earth
    using the haversine formula.

    Returns:
        Distance in metres.
    """
    R = 6_371_000  # Earth's radius in metres

    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = (math.sin(dlat / 2) ** 2
         + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def find_nearest_driver(
    tree: KDTree,
    available_drivers: List[Dict[str, Any]],
    query_lat: float,
    query_lng: float,
) -> Tuple[Dict[str, Any], float]:
    """
    Queries the KDTree for the single nearest available driver
    to the given (lat, lng) point.

    Returns:
        (driver_dict, distance_meters) — the full driver dict and the
        real-world distance in metres (haversine).
    """
    _, index = tree.query([query_lat, query_lng], k=1)

    driver = available_drivers[index]

    # Compute real-world distance using haversine instead of raw degree distance
    distance_m = _haversine(query_lat, query_lng, driver["lat"], driver["lng"])

    return driver, distance_m

