from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router as api_router, city_graph, route_cache
from app.api.driver_routes import router as driver_router
from app.api.order_routes import router as order_router
from app.utils.osm import load_chennai_graph
from app.data.seed_drivers import seed as seed_drivers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the Chennai road network and seed drivers once at startup."""
    # --- Load city graph ---
    print("[Startup] Loading Chennai road network ...")
    loaded_graph = load_chennai_graph()

    # Copy the loaded data into the shared graph instance that routes.py uses,
    # so existing route endpoints automatically see the real city data.
    city_graph.nodes = loaded_graph.nodes

    # Clear any stale cache entries from a previous run
    route_cache.cache.clear()

    print(f"[Startup] Graph ready — {len(city_graph.nodes)} nodes loaded.")

    # --- Seed drivers ---
    print("[Startup] Seeding drivers ...")
    seed_drivers()
    print("[Startup] Drivers seeded.")

    yield
    print("[Shutdown] City Route Optimizer shutting down.")


app = FastAPI(title="City Route Optimizer API", lifespan=lifespan)

# Include our routes
app.include_router(api_router, prefix="/api")
app.include_router(driver_router, prefix="/api")
app.include_router(order_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the City Route Optimizer API! Use POST /api/route to find paths."}
