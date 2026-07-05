import os
import random
import logging
import joblib

logger = logging.getLogger(__name__)

# Map road_types to ints for the model (same as training)
RT_MAPPING = {"primary": 0, "trunk": 1, "secondary": 2, "residential": 3, "unknown": 2}

# Load the model once at import time
MODEL_PATH = os.path.join(os.path.dirname(__file__), "eta_model.joblib")
try:
    eta_model = joblib.load(MODEL_PATH)
    print(f"[ML] Successfully loaded ETA model from {MODEL_PATH}")
except FileNotFoundError:
    eta_model = None
    logger.warning(f"Could not find {MODEL_PATH}. ETA will fall back to simple heuristic.")
    print(f"[ML] WARNING: Could not find {MODEL_PATH}. ETA will fall back to simple heuristic.")

def predict_eta(
    distance_meters: float, 
    hour: int, 
    day_of_week: int, 
    road_type: str,
    avg_traffic_factor: float, 
    num_path_nodes: int, 
    area_density_score: float = 1.0
) -> float:
    """
    Predicts the ETA in minutes using the trained Gradient Boosting model.
    Falls back to a simple heuristic if the model is missing.
    """
    if eta_model is None:
        # Fallback heuristic
        return round((distance_meters / 1000.0) / 20.0 * 60.0 * avg_traffic_factor, 1)
        
    road_type_encoded = RT_MAPPING.get(road_type, 2)
    
    # Feature vector must perfectly match training order:
    # ["distance_meters", "hour_of_day", "day_of_week", "road_type_encoded", 
    #  "avg_traffic_factor", "num_path_nodes", "area_density_score"]
    import pandas as pd
    feature_df = pd.DataFrame([{
        "distance_meters": distance_meters,
        "hour_of_day": hour,
        "day_of_week": day_of_week,
        "road_type_encoded": road_type_encoded,
        "avg_traffic_factor": avg_traffic_factor,
        "num_path_nodes": num_path_nodes,
        "area_density_score": area_density_score
    }])
    
    eta_minutes = eta_model.predict(feature_df)[0]
    return round(eta_minutes, 1)

def get_area_density(lat: float, lng: float) -> float:
    """
    Returns a deterministic float between 0.8 and 1.8 based on the coordinates.
    """
    # Seed the random number generator deterministically
    random.seed(lat + lng)
    density = random.uniform(0.8, 1.8)
    # Reset seed so we don't accidentally make the whole app deterministic
    random.seed()
    
    return round(density, 2)
