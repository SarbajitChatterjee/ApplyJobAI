from typing import Dict, Any, Optional
from datetime import datetime
import queue
import os
import json
import tempfile
import threading
from fastapi import UploadFile

# Add back core imports one by one
from core.agent_controller import CVMotivationAgent
from utils.logger import get_logger

class AgentService:
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger()
    
    def create_session(self, session_id: str) -> Dict[str, Any]:
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
        
        return {
            "session_id": session_id,
            "status": "initialized",
            "current_step": "waiting_for_input",
            "progress_percentage": 0,
            "message": "Session created successfully"
        }
    
    async def process_files_async(
        self, 
        session_id: str, 
        cv_file: UploadFile,
        job_profile_file: UploadFile,
        cv_language: str = "English"
    ) -> Dict[str, Any]:
        """Process CV and job profile files asynchronously"""
        
        if session_id not in self.active_sessions:
            self.create_session(session_id)
        
        # Update session status
        self.active_sessions[session_id].update({
            "status": "processing",
            "current_step": "saving_files",
            "progress": 10
        })
        
        try:
            # Create temp directory for this session
            temp_dir = f"temp/{session_id}"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Save CV file
            cv_file_extension = cv_file.filename.split('.')[-1]
            cv_file_path = f"{temp_dir}/cv.{cv_file_extension}"
            
            with open(cv_file_path, "wb") as buffer:
                cv_content = await cv_file.read()
                buffer.write(cv_content)
            
            # Save job profile file
            job_file_extension = job_profile_file.filename.split('.')[-1]
            job_file_path = f"{temp_dir}/job_profile.{job_file_extension}"
            
            with open(job_file_path, "wb") as buffer:
                job_content = await job_profile_file.read()
                buffer.write(job_content)
            
            # Update progress
            self.active_sessions[session_id].update({
                "current_step": "initializing_agent",
                "progress": 20
            })
            
            # Initialize agent
            agent = CVMotivationAgent()
            self.active_sessions[session_id]["agent"] = agent
            
            # Store file paths for background processing
            self.active_sessions[session_id]["file_paths"] = {
                "cv_file": cv_file_path,
                "job_profile": job_file_path,
                "cv_language": cv_language
            }
            
            # Start background processing
            processing_thread = threading.Thread(
                target=self._process_in_background,
                args=(session_id,)
            )
            processing_thread.start()
            
            return {
                "session_id": session_id,
                "status": "processing",
                "current_step": "processing_files",
                "progress_percentage": 30,
                "message": "Files uploaded and processing started"
            }
            
        except Exception as e:
            self.logger.log_error(e, f"File processing failed for session {session_id}")
            
            self.active_sessions[session_id].update({
                "status": "error",
                "error": str(e)
            })
            
            return {
                "session_id": session_id,
                "status": "error",
                "current_step": "file_processing_failed",
                "progress_percentage": 0,
                "message": f"Failed to process files: {str(e)}"
            }
    
    def _process_in_background(self, session_id: str):
        """Background processing method"""
        
        try:
            session = self.active_sessions[session_id]
            agent = session["agent"]
            file_paths = session["file_paths"]
            
            # Update progress for each step
            self.active_sessions[session_id].update({
                "current_step": "parsing_cv",
                "progress": 40
            })
            
            # Parse CV file
            cv_content = agent.file_parser.parse_file(file_paths["cv_file"])
            
            self.active_sessions[session_id].update({
                "current_step": "parsing_job_profile",
                "progress": 50
            })
            
            # Parse job profile file
            job_profile_content = agent.file_parser.parse_file(file_paths["job_profile"])
            
            self.active_sessions[session_id].update({
                "current_step": "researching_company",
                "progress": 60
            })
            
            # Research company from job profile
            company_data = agent.company_researcher.research_company(job_profile_content)
            
            self.active_sessions[session_id].update({
                "current_step": "analyzing_cv",
                "progress": 70
            })
            
            # Analyze CV sections
            cv_suggestions = agent.cv_analyzer.analyze_sections(
                cv_content, job_profile_content, company_data, file_paths["cv_language"]
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
                    "job_profile": job_profile_content
                }
            })
            
        except Exception as e:
            self.logger.log_error(e, f"Background processing failed for session {session_id}")
            self.active_sessions[session_id].update({
                "status": "error",
                "error": str(e)
            })
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current session status"""
        
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "status": session["status"],
            "current_step": session["current_step"],
            "progress_percentage": session.get("progress", 0),
            "message": session.get("message", "Processing...")
        }
    
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
        
        try:
            if action == "approve":
                result = f"Section '{section_name}' approved"
                
            elif action == "modify":
                if not modification_text:
                    return {"error": "Modification text required for 'modify' action"}
                result = f"Section '{section_name}' modified with: {modification_text}"
                
            elif action == "ask":
                if not question:
                    return {"error": "Question required for 'ask' action"}
                result = f"Question about '{section_name}': {question}. Answer: This is a sample response."
                
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

    async def finalize_processing(self, session_id: str) -> Dict[str, Any]:
        """Finalize processing and generate motivation letter"""
        
        if session_id not in self.active_sessions:
            raise ValueError("Session not found")
        
        session = self.active_sessions[session_id]
        
        try:
            # Update status to finalizing
            self.active_sessions[session_id].update({
                "status": "finalizing",
                "current_step": "generating_motivation_letter",
                "progress": 90
            })
            
            # Create output directories if they don't exist
            os.makedirs("data/output/motivation_letters", exist_ok=True)
            os.makedirs("data/output/cv_suggestions", exist_ok=True)
            
            # Generate sample results (replace with actual processing later)
            motivation_letter = f"""Dear Hiring Manager,

    I am writing to express my strong interest in the Product Manager position at your company. 

    Based on my analysis of the job requirements and my professional background, I believe I would be an excellent fit for this role. My experience in digital transformation and agile methodologies aligns perfectly with your needs.

    I am excited about the opportunity to contribute to your team's success and would welcome the chance to discuss how my skills can benefit your organization.

    Thank you for your consideration.

    Sincerely,
    [Your Name]

    Generated for session: {session_id}
    """
            

            cv_suggestions = {
                "Professional Profile": {
                    "title": "Professional Profile",
                    "content": "Updated professional profile with relevant keywords",
                    "suggestions": ["Add relevant keywords", "Quantify achievements"],
                    "status": "enhanced"
                },
                "Experience": {
                    "title": "Experience", 
                    "content": "Enhanced experience section highlighting relevant achievements",
                    "suggestions": ["Use action verbs", "Include metrics", "Show career progression"],
                    "status": "enhanced"
                },
                "Skills": {
                    "title": "Skills",
                    "content": "Optimized skills section for the target role", 
                    "suggestions": ["Match job requirements", "Include technical skills", "Add certifications"],
                    "status": "enhanced"
                },
                "Education": {
                    "title": "Education",
                    "content": "Formatted education section appropriately",
                    "suggestions": ["Include relevant coursework", "Add certifications", "Highlight honors"],
                    "status": "enhanced"
                }
            }
            
            # Save results to files
            motivation_file_path = f"data/output/motivation_letters/letter_{session_id}.txt"
            with open(motivation_file_path, 'w', encoding='utf-8') as f:
                f.write(motivation_letter)
            
            cv_suggestions_file_path = f"data/output/cv_suggestions/suggestions_{session_id}.json"
            with open(cv_suggestions_file_path, 'w', encoding='utf-8') as f:
                json.dump(cv_suggestions, f, indent=2, ensure_ascii=False)
            
            # Final results
            final_results = {
                "session_id": session_id,
                "timestamp": datetime.now(),
                "status": "completed",
                "company_research": {
                    "company_name": "Sample Company",
                    "research_date": datetime.now(),
                    "detailed_research": "Sample company research data"
                },
                "cv_suggestions": cv_suggestions,
                "motivation_letter": motivation_letter,
                "processing_time": (datetime.now() - session["created_at"]).total_seconds()
            }
            
            # Update session to completed
            self.active_sessions[session_id].update({
                "status": "completed",
                "progress": 100,
                "final_results": final_results
            })
            
            return final_results
            
        except Exception as e:
            self.logger.log_error(e, f"Finalization failed for session {session_id}")
            
            self.active_sessions[session_id].update({
                "status": "error",
                "error": str(e)
            })
            
            raise Exception(f"Finalization failed: {str(e)}")

    # Create Dummy Session ID for testing.
    def create_dummy_completed_session(self, session_id: str):
        """Create a fake completed session for testing"""
        print(f"🔥 START: Creating dummy session {session_id}")
        
        try:
            print("✅ Step 1: Creating session dict")
            self.active_sessions[session_id] = {
                "status": "completed",
                "current_step": "completed",
                "progress": 100,
                "agent": None,
                "results": {},
                "created_at": datetime.now(),
                "interaction_queue": queue.Queue(),
                "response_queue": queue.Queue(),
                "final_results": {
                    "session_id": session_id,
                    "timestamp": datetime.now(),
                    "status": "completed",
                    "company_research": {
                        "company_name": "Test Company",
                        "detailed_research": "Mock company research data for testing"
                    },
                    "cv_suggestions": {
                        "Professional Profile": {
                            "section_name": "Professional Profile",
                            "title": "Professional Profile",
                            "original_content": "Original professional profile content from CV",
                            "content": "Mock updated professional profile with relevant keywords",
                            "suggestions": "Add relevant keywords and quantify achievements",
                            "status": "enhanced"
                        },
                        "Experience": {
                            "section_name": "Experience",
                            "title": "Experience", 
                            "original_content": "Original experience section content from CV",
                            "content": "Mock enhanced experience section highlighting relevant achievements",
                            "suggestions": "Use action verbs, include metrics, and show career progression",
                            "status": "enhanced"
                        },
                        "Skills": {
                            "section_name": "Skills",
                            "title": "Skills",
                            "original_content": "Original skills section content from CV",
                            "content": "Mock optimized skills section for the target role", 
                            "suggestions": "Match job requirements, include technical skills, and add certifications",
                            "status": "enhanced"
                        },
                        "Education": {
                            "section_name": "Education",
                            "title": "Education",
                            "original_content": "Original education section content from CV",
                            "content": "Mock formatted education section appropriately",
                            "suggestions": "Include relevant coursework, add certifications, and highlight honors",
                            "status": "enhanced"
                        }
                    },
                    "motivation_letter": f"""Dear Hiring Manager,

    I am writing to express my strong interest in the Product Manager position at your company.

    Based on my analysis of the job requirements and my professional background, I believe I would be an excellent fit for this role. My experience in digital transformation and agile methodologies aligns perfectly with your needs.

    I am excited about the opportunity to contribute to your team's success and would welcome the chance to discuss how my skills can benefit your organization.

    Thank you for your consideration.

    Sincerely,
    [Your Name]

    Generated for MOCK session: {session_id}
    """,
                    "processing_time": 0.1
                }
            }
            
            print("✅ Step 2: Creating directories")
            os.makedirs("data/output/motivation_letters", exist_ok=True)
            os.makedirs("data/output/cv_suggestions", exist_ok=True)
            
            print("✅ Step 3: Writing motivation letter")
            motivation_file_path = f"data/output/motivation_letters/letter_{session_id}.txt"
            with open(motivation_file_path, 'w', encoding='utf-8') as f:
                f.write(self.active_sessions[session_id]["final_results"]["motivation_letter"])
            
            print("✅ Step 4: Writing CV suggestions")
            cv_suggestions_file_path = f"data/output/cv_suggestions/suggestions_{session_id}.json"
            with open(cv_suggestions_file_path, 'w', encoding='utf-8') as f:
                # Get only the cv_suggestions part (without datetime objects)
                cv_suggestions_data = self.active_sessions[session_id]["final_results"]["cv_suggestions"]
                json.dump(cv_suggestions_data, f, indent=2, ensure_ascii=False)
            
            print("✅ SUCCESS: Dummy session created")
            
        except Exception as e:
            print(f"❌ ERROR in create_dummy_completed_session: {str(e)}")
            print(f"❌ ERROR type: {type(e)}")
            import traceback
            print(f"❌ FULL TRACEBACK: {traceback.format_exc()}")
            raise e

agent_service = AgentService()