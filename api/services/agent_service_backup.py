"""
Service layer to bridge FastAPI with your existing CV & Motivation Letter Agent
"""

import asyncio
import tempfile
import os
from typing import Dict, Any, Optional
from datetime import datetime
import threading
import queue

from core.agent_controller import CVMotivationAgent
from utils.logger import get_logger
from api.models.response_models import ProcessingStatus, JobApplicationResponse

class AgentService:
    """Service to manage CV & Motivation Letter Agent operations"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger()
    
    def create_session(self, session_id: str) -> ProcessingStatus:
        """Create a new processing session"""
        
        self.active_sessions[session_id] = {
            "status": "initialized",
            "current_step": "waiting_for_input",
            "progress": 0,
            "agent": None,
            "results": {},
            "created_at": datetime.now(),
            "interaction_queue": queue.Queue(),
            "response_queue": queue.Queue()
        }
        
        return ProcessingStatus(
            session_id=session_id,
            status="initialized",
            current_step="waiting_for_input",
            progress_percentage=0,
            message="Session created successfully"
        )
    
    async def process_application_async(
        self, 
        session_id: str, 
        job_profile: str, 
        cv_file_path: str, 
        cv_language: str = "English"
    ) -> ProcessingStatus:
        """Start asynchronous processing of job application"""
        
        if session_id not in self.active_sessions:
            self.create_session(session_id)
        
        # Update session status
        self.active_sessions[session_id].update({
            "status": "processing",
            "current_step": "initializing_agent",
            "progress": 10
        })
        
        try:
            # Initialize agent
            agent = CVMotivationAgent()
            self.active_sessions[session_id]["agent"] = agent
            
            # Update progress
            self.active_sessions[session_id].update({
                "current_step": "processing_application",
                "progress": 20
            })
            
            # Start processing in background thread
            processing_thread = threading.Thread(
                target=self._process_in_background,
                args=(session_id, job_profile, cv_file_path, cv_language)
            )
            processing_thread.start()
            
            return ProcessingStatus(
                session_id=session_id,
                status="processing",
                current_step="processing_application",
                progress_percentage=20,
                message="Application processing started"
            )
            
        except Exception as e:
            self.logger.log_error(e, f"Agent initialization failed for session {session_id}")
            
            self.active_sessions[session_id].update({
                "status": "error",
                "error": str(e)
            })
            
            return ProcessingStatus(
                session_id=session_id,
                status="error",
                current_step="initialization_failed",
                progress_percentage=0,
                message=f"Failed to initialize: {str(e)}"
            )
    
    def _process_in_background(self, session_id: str, job_profile: str, cv_file_path: str, cv_language: str):
        """Background processing method"""
        
        try:
            agent = self.active_sessions[session_id]["agent"]
            
            # Update progress for each step
            self.active_sessions[session_id].update({
                "current_step": "parsing_cv",
                "progress": 30
            })
            
            # Parse CV
            cv_content = agent.file_parser.parse_file(cv_file_path)
            
            self.active_sessions[session_id].update({
                "current_step": "researching_company",
                "progress": 40
            })
            
            # Research company
            company_data = agent.company_researcher.research_company(job_profile)
            
            self.active_sessions[session_id].update({
                "current_step": "analyzing_cv",
                "progress": 60
            })
            
            # Analyze CV sections
            cv_suggestions = agent.cv_analyzer.analyze_sections(
                cv_content, job_profile, company_data, cv_language
            )
            
            # Store results and move to interaction phase
            self.active_sessions[session_id].update({
                "status": "waiting_approval",
                "current_step": "cv_section_approval",
                "progress": 80,
                "results": {
                    "company_research": company_data,
                    "cv_suggestions": cv_suggestions,
                    "cv_content": cv_content,
                    "job_profile": job_profile
                }
            })
            
        except Exception as e:
            self.logger.log_error(e, f"Background processing failed for session {session_id}")
            self.active_sessions[session_id].update({
                "status": "error",
                "error": str(e)
            })
    
    def get_session_status(self, session_id: str) -> Optional[ProcessingStatus]:
        """Get current session status"""
        
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        return ProcessingStatus(
            session_id=session_id,
            status=session["status"],
            current_step=session["current_step"],
            progress_percentage=session.get("progress", 0),
            message=session.get("message", "Processing...")
        )
    
    def handle_section_interaction(
        self, 
        session_id: str, 
        section_name: str, 
        action: str, 
        modification_text: Optional[str] = None,
        question: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle user interaction with CV sections"""
        
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        if session["status"] != "waiting_approval":
            return {"error": "Session not ready for interactions"}
        
        agent = session["agent"]
        cv_suggestions = session["results"]["cv_suggestions"]
        
        if section_name not in cv_suggestions:
            return {"error": f"Section '{section_name}' not found"}
        
        try:
            if action == "approve":
                result = f"Section '{section_name}' approved"
                
            elif action == "modify":
                if not modification_text:
                    return {"error": "Modification text required for 'modify' action"}
                
                modified_suggestions = agent.interactive_approval._modify_suggestions(
                    section_name, cv_suggestions[section_name], modification_text
                )
                cv_suggestions[section_name] = modified_suggestions
                result = modified_suggestions
                
            elif action == "ask":
                if not question:
                    return {"error": "Question required for 'ask' action"}
                
                answer = agent.interactive_approval._answer_question(
                    section_name, cv_suggestions[section_name], question
                )
                result = answer
                
            elif action == "skip":
                result = f"Section '{section_name}' skipped"
                
            else:
                return {"error": f"Invalid action: {action}"}
            
            return {
                "session_id": session_id,
                "section_name": section_name,
                "action_taken": action,
                "result": result,
                "success": True
            }
            
        except Exception as e:
            self.logger.log_error(e, f"Section interaction failed for session {session_id}")
            return {"error": f"Interaction failed: {str(e)}"}
    
    async def finalize_processing(self, session_id: str) -> JobApplicationResponse:
        """Finalize processing and generate motivation letter"""
        
        if session_id not in self.active_sessions:
            raise ValueError("Session not found")
        
        session = self.active_sessions[session_id]
        
        if session["status"] != "waiting_approval":
            raise ValueError("Session not ready for finalization")
        
        try:
            # Update status
            self.active_sessions[session_id].update({
                "status": "finalizing",
                "current_step": "generating_motivation_letter",
                "progress": 90
            })
            
            agent = session["agent"]
            results = session["results"]
            
            # Generate motivation letter
            motivation_letter = agent.motivation_generator.generate_letter(
                results["job_profile"],
                results["cv_suggestions"],
                results["company_research"]
            )
            
            # Save results
            final_results = {
                "session_id": session_id,
                "timestamp": datetime.now(),
                "status": "completed",
                "company_research": results["company_research"],
                "cv_suggestions": results["cv_suggestions"],
                "motivation_letter": motivation_letter,
                "processing_time": (datetime.now() - session["created_at"]).total_seconds()
            }
            
            # Save to files
            agent._save_results(final_results)
            
            # Update session
            self.active_sessions[session_id].update({
                "status": "completed",
                "progress": 100,
                "final_results": final_results
            })
            
            return JobApplicationResponse(**final_results)
            
        except Exception as e:
            self.logger.log_error(e, f"Finalization failed for session {session_id}")
            
            self.active_sessions[session_id].update({
                "status": "error",
                "error": str(e)
            })
            
            raise

# Global service instance
agent_service = AgentService()
