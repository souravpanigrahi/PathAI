"""
In-memory driver store.
Populated at startup by seed_drivers.py — will move to PostgreSQL later.
"""

from typing import List, Dict, Any

# The shared driver list that the rest of the app reads from
drivers: List[Dict[str, Any]] = []
