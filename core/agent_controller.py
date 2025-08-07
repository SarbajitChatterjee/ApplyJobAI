"""
Main Agent Controller with Comprehensive Logging
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

from .company_researcher import CompanyResearcher
from .cv_analyzer import CVAnalyzer
from .motivation_generator import MotivationLetterGenerator
from .interactive_approval import InteractiveApproval
from utils.file_parser import FileParser
from utils.api_client import LMStudioClient
from utils.logger import get_logger, log_function_call

class CVMotivationAgent:
    """Main agent class with comprehensive logging"""
    
    def __init__(self, lm_studio_url: str = "http://localhost:1234", model_name: str = "gpt-oss-20b"):
        """Initialize agent with full logging"""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logger = get_logger(session_id)
        
        # Log startup configuration
        startup_config = {
            "lm_studio_url": lm_studio_url,
            "model_name": model_name,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.log_app_start(startup_config)
        
        # Initialize components with logging
        self.logger.log_processing_step("Initializing API Client")
        self.api_client = LMStudioClient(lm_studio_url, model_name)
        
        self.logger.log_processing_step("Loading User Profile")
        self.user_profile = self._load_user_profile()
        
        self.conversation_state = {
            "current_step": 0,
            "approved_sections": {},
            "session_id": session_id
        }
        
        # Initialize all components
        self.logger.log_processing_step("Initializing Agent Components")
        self.company_researcher = CompanyResearcher(self.api_client)
        self.cv_analyzer = CVAnalyzer(self.api_client, self.user_profile)
        self.motivation_generator = MotivationLetterGenerator(self.api_client, self.user_profile)
        self.interactive_approval = InteractiveApproval(self.api_client)
        self.file_parser = FileParser()
        
        self.logger.app_logger.info(f"🤖 Agent initialized successfully with model: {model_name}")
    
    def _load_user_profile(self) -> Dict[str, Any]:
        """Load user profile with logging"""
        config_path = os.path.join("config", "user_profile.json")
        
        try:
            self.logger.log_file_operation("read", config_path)
            with open(config_path, 'r', encoding='utf-8') as f:
                profile = json.load(f)
            
            self.logger.log_file_operation("read", config_path, success=True)
            self.logger.app_logger.info("✅ User profile loaded successfully")
            return profile
            
        except FileNotFoundError as e:
            self.logger.log_file_operation("read", config_path, success=False, error=str(e))
            self.logger.log_error(e, f"User profile not found at {config_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.log_file_operation("read", config_path, success=False, error=str(e))
            self.logger.log_error(e, f"Invalid JSON in user profile at {config_path}")
            raise
    
    @log_function_call(get_logger())
    def process_application(self, job_profile: str, cv_file_path: str, cv_language: str = "English") -> Dict[str, Any]:
        """Main workflow with comprehensive logging"""
        
        self.logger.log_processing_step("Starting Application Processing", 
                                      f"CV: {cv_file_path}, Language: {cv_language}")
        
        results = {
            "session_id": self.conversation_state["session_id"],
            "timestamp": datetime.now().isoformat(),
            "inputs": {
                "job_profile_length": len(job_profile),
                "cv_file_path": cv_file_path,
                "cv_language": cv_language
            }
        }
        
        try:
            # Step 1: Parse CV file
            self.logger.log_processing_step("Step 1: Parsing CV File")
            cv_content = self.file_parser.parse_file(cv_file_path)
            self.logger.log_processing_step("CV Parsing Completed", f"Content length: {len(cv_content)} chars")
            
            # Step 2: Company Research
            self.logger.log_processing_step("Step 2: Company Research")
            company_data = self.company_researcher.research_company(job_profile)
            results["company_research"] = company_data
            self.logger.log_processing_step("Company Research Completed", 
                                          f"Company: {company_data.get('company_name', 'Unknown')}")
            
            # Step 3: CV Analysis
            self.logger.log_processing_step("Step 3: CV Analysis")
            cv_suggestions = self.cv_analyzer.analyze_sections(
                cv_content, job_profile, company_data, cv_language
            )
            self.logger.log_processing_step("CV Analysis Completed", 
                                          f"Sections analyzed: {len(cv_suggestions)}")
            
            # Step 4: Interactive Approval
            self.logger.log_processing_step("Step 4: Interactive Section Approval")
            finalized_cv = self.interactive_approval.section_approval_loop(cv_suggestions)
            results["cv_suggestions"] = finalized_cv
            self.logger.log_processing_step("Section Approval Completed", 
                                          f"Sections approved: {len(finalized_cv)}")
            
            # Step 5: Generate Motivation Letter
            self.logger.log_processing_step("Step 5: Motivation Letter Generation")
            motivation_letter = self.motivation_generator.generate_letter(
                job_profile, finalized_cv, company_data
            )
            results["motivation_letter"] = motivation_letter
            self.logger.log_processing_step("Motivation Letter Generated", 
                                          f"Word count: {len(motivation_letter.split())}")
            
            # Step 6: Save results
            self.logger.log_processing_step("Step 6: Saving Results")
            self._save_results(results)
            
            self.logger.app_logger.info("🎉 Application processing completed successfully")
            return results
            
        except Exception as e:
            self.logger.log_error(e, "Application Processing")
            self.logger.app_logger.error(f"❌ Application processing failed: {str(e)}")
            raise
    
    def _save_results(self, results: Dict[str, Any]):
        """Save results with detailed logging"""
        session_id = results["session_id"]
        
        try:
            # Save motivation letter
            letter_path = f"data/output/motivation_letters/letter_{session_id}.txt"
            os.makedirs(os.path.dirname(letter_path), exist_ok=True)
            
            self.logger.log_file_operation("write", letter_path)
            with open(letter_path, 'w', encoding='utf-8') as f:
                f.write(results["motivation_letter"])
            self.logger.log_file_operation("write", letter_path, success=True)
            
            # Save CV suggestions
            cv_path = f"data/output/cv_suggestions/suggestions_{session_id}.json"
            os.makedirs(os.path.dirname(cv_path), exist_ok=True)
            
            self.logger.log_file_operation("write", cv_path)
            with open(cv_path, 'w', encoding='utf-8') as f:
                json.dump(results["cv_suggestions"], f, indent=2, ensure_ascii=False)
            self.logger.log_file_operation("write", cv_path, success=True)
            
            # Save complete session log
            session_path = f"data/output/sessions/session_{session_id}.json"
            os.makedirs(os.path.dirname(session_path), exist_ok=True)
            
            session_summary = {
                "session_id": session_id,
                "timestamp": results["timestamp"],
                "inputs": results.get("inputs", {}),
                "outputs": {
                    "motivation_letter_path": letter_path,
                    "cv_suggestions_path": cv_path,
                    "company_research": results.get("company_research", {}).get("company_name", "Unknown")
                },
                "processing_summary": {
                    "motivation_letter_words": len(results["motivation_letter"].split()),
                    "cv_sections_processed": len(results["cv_suggestions"]),
                    "total_processing_time": "logged_separately"
                }
            }
            
            with open(session_path, 'w', encoding='utf-8') as f:
                json.dump(session_summary, f, indent=2, ensure_ascii=False)
            
            self.logger.log_file_operation("write", session_path, success=True)
            self.logger.app_logger.info(f"💾 All results saved for session {session_id}")
            
        except Exception as e:
            self.logger.log_error(e, "Saving Results")
            self.logger.app_logger.error(f"❌ Failed to save results: {str(e)}")
            raise
