"""
Response models for the CV & Motivation Letter API
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime

class ProcessingStatus(BaseModel):
    """Processing status response"""
    
    session_id: str
    status: str  # "processing", "waiting_approval", "completed", "error"
    current_step: str
    progress_percentage: int
    message: str

class CVSuggestion(BaseModel):
    """Individual CV section suggestion"""
    
    section_name: str
    original_content: str
    suggestions: str
    status: str  # "pending", "approved", "modified", "skipped"

class CompanyResearch(BaseModel):
    """Company research data"""
    
    company_name: str
    research_date: datetime
    detailed_research: str

class JobApplicationResponse(BaseModel):
    """Complete job application response"""
    
    session_id: str
    timestamp: datetime
    status: str
    
    # Processing results
    company_research: Optional[CompanyResearch] = None
    cv_suggestions: Optional[Dict[str, CVSuggestion]] = None
    motivation_letter: Optional[str] = None
    
    # Metadata
    processing_time: Optional[float] = None
    files_generated: Optional[List[str]] = None
    logs_available: bool = True

class InteractionResponse(BaseModel):
    """Response for section interactions"""
    
    session_id: str
    section_name: str
    action_taken: str
    result: str
    next_section: Optional[str] = None
    is_complete: bool = False

class ErrorResponse(BaseModel):
    """Error response model"""
    
    error: str
    detail: str
    session_id: Optional[str] = None
    timestamp: datetime
