from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(title="City Route Optimizer API")

# Include our routes
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the City Route Optimizer API! Use POST /api/route to find paths."}
