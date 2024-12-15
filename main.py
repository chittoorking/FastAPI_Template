from fastapi import FastAPI
from app.database import create_tables
from app.routers import products

# Create FastAPI application
app = FastAPI(
    title="Product Management API",
    description="A comprehensive API for managing product inventory",
    version="0.1.0"
)

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()

# Include routers
app.include_router(products.router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Product Management API",
        "available_endpoints": [
            "/products (GET, POST)",
            "/products/{product_id} (GET, PUT, DELETE)",
            "/products/bulk (POST)"
        ]
    }