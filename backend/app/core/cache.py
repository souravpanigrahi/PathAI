from collections import OrderedDict
from typing import Optional, Tuple, Dict, Any

class LRUCache:
    """
    A Least Recently Used (LRU) Cache built on top of Python's OrderedDict.
    Stores up to `capacity` items. Removes the least recently used when full.
    """
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: Tuple[str, str]) -> Optional[Dict[str, Any]]:
        """Retrieve a cached value if it exists, tracking hits and misses."""
        if key not in self.cache:
            self.misses += 1
            return None
            
        self.hits += 1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: Tuple[str, str], value: Dict[str, Any]):
        """Save a value into the cache, evicting the oldest if full."""
        # If key already exists, move it to the end (recently used)
        if key in self.cache:
            self.cache.move_to_end(key)
            
        self.cache[key] = value
        
        # If we exceed our memory capacity, evict the LEAST recently used item (first item)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def clear(self):
        """Flush the cache and reset stats."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def stats(self) -> Dict[str, Any]:
        """Return statistics about the cache's usage."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100.0) if total > 0 else 0.0
        
        return {
            "size": len(self.cache),
            "capacity": self.capacity,
            "hit_rate": round(hit_rate, 2)
        }
