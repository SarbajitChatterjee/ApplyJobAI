"""
API Routers Package
Contains all API endpoint routers
"""

# Import all routers for easy access
from .cv_routes import router as cv_router
from .health import router as health_router

# List all available routers
__all__ = [
    "cv_router",
    "health_router"
]

# Optional: Router registry for dynamic loading
AVAILABLE_ROUTERS = {
    "cv": cv_router,
    "health": health_router
}
