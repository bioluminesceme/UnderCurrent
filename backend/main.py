from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import hrv, users, energy_budget
from backend.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CFS-HRV Monitor API",
    description="Heart Rate Variability monitoring for ME/CFS management",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(hrv.router, prefix="/api/hrv", tags=["hrv"])
app.include_router(readiness.router, prefix="/api/readiness", tags=["readiness"])

@app.get("/")
async def root():
    return {
        "message": "CFS-HRV Monitor API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
