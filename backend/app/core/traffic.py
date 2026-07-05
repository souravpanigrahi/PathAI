from datetime import datetime

def get_traffic_factor(hour: int, day_of_week: int, road_type: str) -> float:
    """
    Returns a traffic multiplier for Chennai roads based on time and road type.
    hour: 0-23
    day_of_week: 0 (Monday) to 6 (Sunday)
    """
    is_weekday = day_of_week < 5  # 0 to 4 are weekdays
    
    # hours 23-6 any road any day: return 0.8
    if hour >= 23 or hour < 6:
        return 0.8
        
    # weekends (day_of_week 5 or 6) before noon: return 0.9
    if not is_weekday and hour < 12:
        return 0.9
        
    if is_weekday:
        # road_type "primary" or "trunk" during weekday hours 8-10: return 2.5
        if road_type in ("primary", "trunk") and 8 <= hour < 10:
            return 2.5
        # road_type "primary" or "trunk" during weekday hours 18-21: return 2.2
        if road_type in ("primary", "trunk") and 18 <= hour < 21:
            return 2.2
        # road_type "secondary" during weekday hours 8-10 or 18-21: return 1.6
        if road_type == "secondary" and (8 <= hour < 10 or 18 <= hour < 21):
            return 1.6
            
    # all other cases: return 1.0
    return 1.0

def get_effective_weight(base_weight: float, road_type: str) -> tuple[float, int]:
    """
    Calculates the effective weight (distance/time) of an edge by applying 
    the current real-world traffic factor. Returns the effective weight and the hour used.
    """
    now = datetime.now()
    hour = now.hour
    day_of_week = now.weekday()
    
    traffic_factor = get_traffic_factor(hour, day_of_week, road_type)
    return base_weight * traffic_factor, hour
