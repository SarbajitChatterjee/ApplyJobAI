"""
Request models for the CV & Motivation Letter API
"""

from typing import Optional, List
from pydantic import BaseModel, Field

class JobApplicationRequest(BaseModel):
    """Request model for job application processing"""
    
    job_profile: str = Field(
        ..., 
        min_length=50, 
        description="Complete job description text",
        example="Product Manager - Digital Innovation\nDeutsche Bahn AG\n\nWe are seeking a dynamic Product Manager..."
    )
    
    cv_language: str = Field(
        default="English",
        description="Language preference for CV suggestions",
        example="English"
    )
    
    user_preferences: Optional[dict] = Field(
        default=None,
        description="Optional user preferences for processing"
    )

class InteractionRequest(BaseModel):
    """Request model for section interactions"""
    
    session_id: str = Field(..., description="Processing session ID")
    section_name: str = Field(..., description="CV section name")
    action: str = Field(..., description="User action: approve, modify, ask, skip")
    modification_text: Optional[str] = Field(
        default=None, 
        description="Modification request text (required for 'modify' action)"
    )
    question: Optional[str] = Field(
        default=None,
        description="Question text (required for 'ask' action)"
    )