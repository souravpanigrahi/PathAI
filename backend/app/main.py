import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router as api_router, city_graph, route_cache
from app.api.driver_routes import router as driver_router
from app.api.order_routes import router as order_router
from app.utils.osm import load_chennai_graph
from app.data.seed_drivers import seed as seed_drivers

# Track whether the graph has finished loading
graph_ready = threading.Event()


def _load_graph_background():
    """Heavy graph loading runs in a background thread so the port opens immediately."""
    try:
        print("[Background] Loading Chennai road network ...")
        loaded_graph = load_chennai_graph()
        city_graph.nodes = loaded_graph.nodes
        route_cache.cache.clear()
        print(f"[Background] Graph ready — {len(city_graph.nodes)} nodes loaded.")
    except Exception as e:
        print(f"[Background] ERROR loading graph: {e}")
    finally:
        graph_ready.set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Seed drivers immediately, load graph in background."""
    # --- Seed drivers (fast — runs instantly) ---
    print("[Startup] Seeding drivers ...")
    seed_drivers()
    print("[Startup] Drivers seeded. Server is accepting requests.")

    # --- Load graph in background thread (slow — don't block port) ---
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
