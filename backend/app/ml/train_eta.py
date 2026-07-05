import os
import random
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Ensure we can import from app.core
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from backend.app.core.traffic import get_traffic_factor

def generate_data(num_samples=2000):
    data = []
    road_types = ["primary", "secondary", "residential", "trunk"]
    
    # Map road_types to ints for the model
    rt_mapping = {"primary": 0, "trunk": 1, "secondary": 2, "residential": 3}

    for _ in range(num_samples):
        distance_meters = random.uniform(500, 15000)
        hour_of_day = random.randint(0, 23)
        day_of_week = random.randint(0, 6)
        road_type = random.choice(road_types)
        
        avg_traffic_factor = get_traffic_factor(hour_of_day, day_of_week, road_type)
        
        noise = random.randint(-5, 5)
        num_path_nodes = max(2, int(distance_meters / 55) + noise)
        area_density_score = random.uniform(0.5, 2.0)
        
        # Determine base speed
        is_rush_hour = hour_of_day in [8, 9, 18, 19, 20] and day_of_week < 5
        if is_rush_hour and road_type in ["primary", "trunk"]:
            base_speed = 10.0
        elif is_rush_hour and road_type in ["secondary", "residential"]:
            base_speed = 14.0
        else:
            base_speed = 20.0
            
        base_eta = (distance_meters / 1000.0) / base_speed * 60.0
        
        # Weekday school hours
        if day_of_week < 5 and (hour_of_day == 8 or hour_of_day == 15):
            base_eta += random.uniform(4.0, 8.0)
            
        # Friday evening
        if day_of_week == 4 and 18 <= hour_of_day <= 20:
            base_eta *= random.uniform(1.3, 1.6)
            
        # Incidents
        if random.random() < 0.08:
            base_eta += random.uniform(5.0, 20.0)
            
        # Area density
        if area_density_score > 1.5:
            base_eta += random.uniform(2.0, 5.0)
            
        # Cap at 90
        eta_minutes = min(90.0, base_eta)
        
        data.append({
            "distance_meters": distance_meters,
            "hour_of_day": hour_of_day,
            "day_of_week": day_of_week,
            "road_type_encoded": rt_mapping[road_type],
            "avg_traffic_factor": avg_traffic_factor,
            "num_path_nodes": num_path_nodes,
            "area_density_score": area_density_score,
            "eta_minutes": eta_minutes
        })
        
    return pd.DataFrame(data)

def main():
    print("Generating synthetic dataset...")
    df = generate_data(2000)
    
    features = [
        "distance_meters", 
        "hour_of_day", 
        "day_of_week", 
        "road_type_encoded", 
        "avg_traffic_factor", 
        "num_path_nodes", 
        "area_density_score"
    ]
    
    X = df[features]
    y = df["eta_minutes"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training GradientBoostingRegressor...")
    model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)
    
    print("\n--- Model Performance ---")
    print(f"R² Score: {r2:.4f}")
    print(f"RMSE:     {rmse:.2f} minutes")
    
    print("\n--- Feature Importances ---")
    importances = model.feature_importances_
    for name, imp in sorted(zip(features, importances), key=lambda x: x[1], reverse=True):
        print(f"{name:20}: {imp:.4f}")
        
    out_path = os.path.join(os.path.dirname(__file__), "eta_model.joblib")
    joblib.dump(model, out_path)
    print(f"\nModel saved to {out_path}")

if __name__ == "__main__":
    main()
