from fastapi import FastAPI
from app.database import engine, Base
from app.schemas import HealthCheckResponse
from app.api.endpoints import router

# Assistant router
from assistant.router import router as assistant_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Change Detection API",
    description="""
API for detecting changes between user snapshots using set operations.

## Features

- **Create User Snapshots**: Store user IDs at different points in time
- **Detect Changes**: Compare snapshots to find new, churned, and retained users
- **Calculate Metrics**: Growth rate, churn rate, and retention rate

## SET Operations Used

- **SET DIFFERENCE** (A - B): Find new users and churned users
- **SET INTERSECTION** (A ∩ B): Find retained users

## Use Cases

- User growth/churn analysis
- Active user tracking
- Customer retention monitoring
- Daily/weekly/monthly user activity comparison
    """,
    version="1.0.0",
)

# Include routers
app.include_router(router)
app.include_router(assistant_router, prefix="/assistant", tags=["assistant"])


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
    return {"status": "healthy", "message": "API is operational"}
