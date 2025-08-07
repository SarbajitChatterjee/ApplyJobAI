"""
Health check and system status routes
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter(
    prefix="/health",
    tags=["System Health"]
)

@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "service": "CV & Motivation Letter API",
        "version": "1.0.0"
    }

@router.get("/lm-studio")
async def check_lm_studio():
    """Check LM Studio connectivity"""
    try:
        import requests
        from config.settings import LM_STUDIO_URL
        
        response = requests.get(f"{LM_STUDIO_URL}/v1/models", timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            return {
                "status": "connected",
                "url": LM_STUDIO_URL,
                "models_available": len(models.get('data', [])),
                "timestamp": datetime.now()
            }
        else:
            return {
                "status": "error",
                "url": LM_STUDIO_URL,
                "error": f"HTTP {response.status_code}",
                "timestamp": datetime.now()
            }
            
    except Exception as e:
        return {
            "status": "error",
            "url": LM_STUDIO_URL,
            "error": str(e),
            "timestamp": datetime.now()
        }