from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, buses, bookings, owner, websocket, location

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Privacy-first bus booking system with real-time tracking",
    version="1.0.0",
    debug=settings.DEBUG
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(buses.router)
app.include_router(bookings.router)
app.include_router(owner.router)
app.include_router(websocket.router)
app.include_router(location.router)


@app.get("/")
def read_root():
    """Root endpoint - API health check"""
    return {
        "message": "Welcome to Bus AgentUB API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected"
    }
