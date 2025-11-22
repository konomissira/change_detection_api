from fastapi import FastAPI
from app.database import engine, Base
from app.schemas import HealthCheckResponse

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Change Detection API",
    description="API for detecting changes between user snapshots using set operations",
    version="1.0.0",
)


@app.get("/", response_model=HealthCheckResponse)
def read_root():
    """Root endpoint - health check"""
    return {
        "status": "success",
        "message": "Change Detection API is running! Visit /docs for API documentation.",
    }


@app.get("/health", response_model=HealthCheckResponse)
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is operational, Mo"}