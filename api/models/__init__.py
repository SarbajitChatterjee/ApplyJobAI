"""
API Models Package
Contains Pydantic models for requests and responses
"""

# Import all models for easy access
from .request_models import (
    JobApplicationRequest,
    InteractionRequest
)
from .response_models import (
    ProcessingStatus,
    CVSuggestion,
    CompanyResearch,
    JobApplicationResponse,
    InteractionResponse,
    ErrorResponse
)

# Export all models
__all__ = [
    # Request models
    "JobApplicationRequest",
    "InteractionRequest",
    
    # Response models
    "ProcessingStatus",
    "CVSuggestion",
    "CompanyResearch",
    "JobApplicationResponse",
    "InteractionResponse",
    "ErrorResponse"
]
