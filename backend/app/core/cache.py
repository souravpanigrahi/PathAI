from collections import OrderedDict
from typing import Optional, Tuple

class LRUCache:
    """
    A Least Recently Used (LRU) Cache built on top of Python's OrderedDict.
    It stores recent route calculations so we don't have to re-run Dijkstra 
    if someone asks for the exact same route twice.
    """
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        # OrderedDict remembers the order that keys were inserted or moved.
        self.cache = OrderedDict()

    def get(self, start_node: str, end_node: str) -> Optional[Tuple[list, float]]:
        """Retrieve a route from the cache if it exists."""
        key = f"{start_node}->{end_node}"
        
        if key not in self.cache:
            return None
            
        # VERY IMPORTANT: If we access an item, we need to mark it as "recently used".
        # We do this by moving it to the very end of the OrderedDict.
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, start_node: str, end_node: str, path: list, distance: float):
        """Save a computed route into the cache."""
        key = f"{start_node}->{end_node}"
        
        # Add or update the key
        self.cache[key] = (path, distance)
        
        # Mark as recently used (move to the end)
        self.cache.move_to_end(key)
        
        # If we exceed our memory capacity, we must evict the LEAST recently used item.
        # Because we constantly move recently used items to the right (end),
        # the oldest, most forgotten item is always stuck at the far left (beginning).
        if len(self.cache) > self.capacity:
            # popitem(last=False) removes the item from the beginning (index 0)
            self.cache.popitem(last=False)
