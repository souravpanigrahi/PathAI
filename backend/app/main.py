import os
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
from app.api.routes import router as api_router, city_graph
from app.api.driver_routes import router as driver_router
from app.api.order_routes import router as order_router
from app.utils.osm import load_chennai_graph
from app.data.seed_drivers import seed as seed_drivers
from app.core.cache import LRUCache

# Track whether the graph has finished loading
graph_ready = threading.Event()

# Create a single global RouteCache instance
route_cache = LRUCache(capacity=100)

# -------------------------------------------------------------------
# ETA Model helpers
# -------------------------------------------------------------------

def _ensure_eta_model():
    """
    Check if eta_model.joblib exists.
    - If NOT: train from scratch and save it.
    - If YES: load the existing model into eta_predictor.
    Logs clearly which path ran.
    """
    from app.ml.train_eta import MODEL_PATH, train_and_save
    import app.ml.eta_predictor as predictor

    if not os.path.exists(MODEL_PATH):
        print("[ML] eta_model.joblib not found — Training ETA model from scratch...")
        train_and_save(out_path=MODEL_PATH)
    else:
        print("[ML] eta_model.joblib found — Loading existing ETA model...")

    # Reload the model into the predictor module so predict_eta uses the fresh artifact
    import joblib
    predictor.eta_model = joblib.load(MODEL_PATH)
    print("[ML] ETA model is ready.")


def _load_graph_background():
    """Heavy graph loading runs in a background thread so the port opens immediately."""
    try:
        print("[Background] Loading Chennai road network ...")
        loaded_graph = load_chennai_graph()
        city_graph.nodes = loaded_graph.nodes
        route_cache.cache.clear()
        print(f"[Background] Graph ready — {len(city_graph.nodes)} nodes loaded.")

        # After the graph is ready, ensure the ETA model is available
        _ensure_eta_model()
    except Exception as e:
        print(f"[Background] ERROR loading graph: {e}")
    finally:
        graph_ready.set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Seed drivers immediately, load graph + ETA model in background."""
    # --- Seed drivers (fast — runs instantly) ---
    print("[Startup] Seeding drivers ...")
    seed_drivers()
    print("[Startup] Drivers seeded. Server is accepting requests.")

    # --- Load graph + ETA model in background thread (slow — don't block port) ---
    loader = threading.Thread(target=_load_graph_background, daemon=True)
    loader.start()

    yield

    print("[Shutdown] City Route Optimizer shutting down.")


app = FastAPI(title="City Route Optimizer API", lifespan=lifespan)

# Include our routes
app.include_router(api_router, prefix="/api")
app.include_router(driver_router, prefix="/api")
app.include_router(order_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "Welcome to the City Route Optimizer API! Use POST /api/route to find paths.",
        "graph_ready": graph_ready.is_set(),
    }


# -------------------------------------------------------------------
# ML Management endpoint
# -------------------------------------------------------------------

def _retrain_blocking():
    """Runs in a background thread — deletes old model and retrains."""
    from app.ml.train_eta import MODEL_PATH, train_and_save
    import app.ml.eta_predictor as predictor
    import joblib

    if os.path.exists(MODEL_PATH):
        os.remove(MODEL_PATH)
        print("[ML] Existing eta_model.joblib deleted.")

    print("[ML] Retraining ETA model from scratch...")
    train_and_save(out_path=MODEL_PATH)

    # Hot-swap the model in the predictor module
    predictor.eta_model = joblib.load(MODEL_PATH)
    print("[ML] ETA model retrained and reloaded successfully.")


@app.post("/api/ml/retrain")
async def retrain_model(background_tasks: BackgroundTasks):
    """
    Deletes the existing eta_model.joblib and retrains the Gradient Boosting model
    from scratch on 2000 new synthetic samples. Runs in the background so the
    endpoint returns immediately.
    """
    background_tasks.add_task(_retrain_blocking)
    return {
        "message": "Retraining started in the background. Check server logs for progress.",
        "status": "accepted"
    }
