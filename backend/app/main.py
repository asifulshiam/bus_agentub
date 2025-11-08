from fastapi import FastAPI, Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.routers import auth, buses, bookings, admin, websocket, location

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Privacy-first bus booking system with real-time tracking",
    version="1.0.0",
    debug=settings.DEBUG
)


# Custom CORS middleware to handle all localhost origins
class FlexibleCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        
        # Check if we should allow this origin
        is_allowed = False
        if origin:
            # Always allow localhost and 127.0.0.1 origins for development
            if origin.startswith("http://localhost:") or origin.startswith("http://127.0.0.1:"):
                is_allowed = True
            # Also check against configured origins
            elif origin in settings.CORS_ORIGINS:
                is_allowed = True
        
        # Handle preflight OPTIONS requests
        if request.method == "OPTIONS":
            response = Response(status_code=200)
            if is_allowed and origin:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
                response.headers["Access-Control-Max-Age"] = "3600"
            return response
        
        # Handle actual requests
        response = await call_next(request)
        if is_allowed and origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
        
        return response


# Use custom CORS middleware for development flexibility
app.add_middleware(FlexibleCORSMiddleware)

# Include routers
app.include_router(auth.router)
app.include_router(buses.router)
app.include_router(bookings.router)
app.include_router(admin.router)
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
