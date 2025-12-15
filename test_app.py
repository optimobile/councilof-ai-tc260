from fastapi import FastAPI

app = FastAPI(title="Council of AI - Test", version="0.2.0")

@app.get("/")
def read_root():
    return {"message": "Test API", "status": "operational"}

# TC260/EU260 Safety Verification Routes
from tc260_routes_simple import router as tc260_router
app.include_router(tc260_router, prefix="/api/v1", tags=["TC260"])
