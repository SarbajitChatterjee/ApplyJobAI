"""
FastAPI routes for CV & Motivation Letter processing
"""

import os
import tempfile
import uuid
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, File, Form, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from api.models.request_models import JobApplicationRequest, InteractionRequest
from api.models.response_models import (
    ProcessingStatus, JobApplicationResponse, InteractionResponse, ErrorResponse
)
from api.services.agent_service import agent_service
from utils.validators import validate_inputs

router = APIRouter(
    prefix="/api/v1",
    tags=["CV & Motivation Letter Processing"]
)

@router.post("/upload-and-process", response_model=ProcessingStatus)
async def upload_and_process(
    background_tasks: BackgroundTasks,
    cv_file: UploadFile = File(..., description="CV file (PDF, DOCX, or TXT)"),
    job_profile: str = Form(..., description="Complete job description"),
    cv_language: str = Form("English", description="Language preference for CV suggestions")
):
    """
    Upload CV file and job profile, start processing
    
    This endpoint:
    1. Accepts CV file upload and job description
    2. Validates inputs
    3. Starts background processing
    4. Returns session ID for tracking progress
    """
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    try:
        # Validate file type
        if not cv_file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        file_extension = os.path.splitext(cv_file.filename)[1].lower()
        if file_extension not in ['.pdf', '.docx', '.txt']:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}. Supported: .pdf, .docx, .txt"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await cv_file.read()
            tmp_file.write(content)
            temp_file_path = tmp_file.name
        
        # Validate inputs
        if not validate_inputs(job_profile, temp_file_path, cv_language):
            os.unlink(temp_file_path)  # Clean up temp file
            raise HTTPException(status_code=422, detail="Input validation failed")
        
        # Create session
        agent_service.create_session(session_id)
        
        # Start background processing
        background_tasks.add_task(
            agent_service.process_application_async,
            session_id, job_profile, temp_file_path, cv_language
        )
        
        return ProcessingStatus(
            session_id=session_id,
            status="processing",
            current_step="initializing",
            progress_percentage=5,
            message="Processing started successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.get("/status/{session_id}", response_model=ProcessingStatus)
async def get_processing_status(session_id: str):
    """
    Get current processing status for a session
    
    Use this endpoint to poll processing progress
    """
    
    status = agent_service.get_session_status(session_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return status

@router.post("/interact", response_model=InteractionResponse)
async def interact_with_section(request: InteractionRequest):
    """
    Interact with CV section suggestions
    
    Actions:
    - approve: Accept suggestions as-is
    - modify: Request modifications (requires modification_text)
    - ask: Ask questions about suggestions (requires question)
    - skip: Skip this section
    """
    
    try:
        result = agent_service.handle_section_interaction(
            request.session_id,
            request.section_name,
            request.action,
            request.modification_text,
            request.question
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return InteractionResponse(
            session_id=result["session_id"],
            section_name=result["section_name"],
            action_taken=result["action_taken"],
            result=result["result"],
            is_complete=False  # You can implement logic to check if all sections are done
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interaction failed: {str(e)}")

@router.post("/finalize/{session_id}", response_model=JobApplicationResponse)
async def finalize_processing(session_id: str):
    """
    Finalize processing and generate motivation letter
    
    Call this after all CV section interactions are complete
    """
    
    try:
        result = await agent_service.finalize_processing(session_id)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Finalization failed: {str(e)}")

@router.get("/download/{session_id}/motivation-letter")
async def download_motivation_letter(session_id: str):
    """Download generated motivation letter as text file"""
    
    status = agent_service.get_session_status(session_id)
    
    if not status or status.status != "completed":
        raise HTTPException(status_code=404, detail="Session not found or not completed")
    
    try:
        # Check if file exists
        file_path = f"data/output/motivation_letters/letter_{session_id}.txt"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Motivation letter file not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        from fastapi.responses import PlainTextResponse
        
        return PlainTextResponse(
            content=content,
            headers={
                "Content-Disposition": f"attachment; filename=motivation_letter_{session_id}.txt"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.get("/download/{session_id}/cv-suggestions")
async def download_cv_suggestions(session_id: str):
    """Download CV suggestions as JSON file"""
    
    status = agent_service.get_session_status(session_id)
    
    if not status or status.status != "completed":
        raise HTTPException(status_code=404, detail="Session not found or not completed")
    
    try:
        file_path = f"data/output/cv_suggestions/suggestions_{session_id}.json"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="CV suggestions file not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            import json
            content = json.load(f)
        
        return JSONResponse(
            content=content,
            headers={
                "Content-Disposition": f"attachment; filename=cv_suggestions_{session_id}.json"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")
