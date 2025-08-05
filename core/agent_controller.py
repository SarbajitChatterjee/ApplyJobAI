"""
Main Agent Controller
Orchestrates the entire CV and motivation letter generation workflow
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
from utils.api_client import OpenAIClient

class CVMotivationAgent:
    """Main agent class that coordinates all components"""
    
    def __init__(self, api_key: str):
        """Initialize the agent with API key and load configuration"""
        self.api_client = OpenAIClient(api_key)
        self.user_profile = self._load_user_profile()
        self.conversation_state = {
            "current_step": 0,
            "approved_sections": {},
            "session_id": datetime.now().strftime("%Y%m%d_%H%M%S")
        }
        
        # Initialize components
        self.company_researcher = CompanyResearcher(self.api_client)
        self.cv_analyzer = CVAnalyzer(self.api_client, self.user_profile)
        self.motivation_generator = MotivationLetterGenerator(self.api_client, self.user_profile)
        self.interactive_approval = InteractiveApproval(self.api_client)
        self.file_parser = FileParser()
    
    def _load_user_profile(self) -> Dict[str, Any]:
        """Load user profile from config file"""
        config_path = os.path.join("config", "user_profile.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"User profile not found at {config_path}")
    
    def process_application(self, job_profile: str, cv_file_path: str, cv_language: str = "English") -> Dict[str, Any]:
        """
        Main workflow execution
        
        Args:
            job_profile: The job description text
            cv_file_path: Path to the CV file
            cv_language: Language preference for CV suggestions
            
        Returns:
            Dictionary containing all results
        """
        results = {
            "session_id": self.conversation_state["session_id"],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Step 1: Parse CV file
            print("📖 Parsing CV file...")
            cv_content = self.file_parser.parse_file(cv_file_path)
            
            # Step 2: Company Research
            print("🔍 Researching company...")
            company_data = self.company_researcher.research_company(job_profile)
            results["company_research"] = company_data
            
            # Step 3: CV Analysis
            print("📊 Analyzing CV sections...")
            cv_suggestions = self.cv_analyzer.analyze_sections(
                cv_content, job_profile, company_data, cv_language
            )
            
            # Step 4: Interactive Section Approval
            print("✅ Review and approve CV suggestions...")
            finalized_cv = self.interactive_approval.section_approval_loop(cv_suggestions)
            results["cv_suggestions"] = finalized_cv
            
            # Step 5: Generate Motivation Letter
            print("✍️ Generating motivation letter...")
            motivation_letter = self.motivation_generator.generate_letter(
                job_profile, finalized_cv, company_data
            )
            results["motivation_letter"] = motivation_letter
            
            # Step 6: Save results
            self._save_results(results)
            
            return results
            
        except Exception as e:
            print(f"❌ Error in processing: {str(e)}")
            raise
    
    def display_results(self, results: Dict[str, Any]):
        """Display formatted results to user"""
        print("\n" + "="*60)
        print("🎉 MOTIVATION LETTER GENERATED")
        print("="*60)
        print(results["motivation_letter"])
        
        print("\n" + "="*60)
        print("📋 CV SUGGESTIONS SUMMARY")
        print("="*60)
        for section, suggestion in results["cv_suggestions"].items():
            print(f"\n📌 {section}:")
            preview = suggestion[:150] + "..." if len(suggestion) > 150 else suggestion
            print(preview)
        
        print(f"\n💾 Results saved with session ID: {results['session_id']}")
    
    def _save_results(self, results: Dict[str, Any]):
        """Save results to output directory"""
        session_id = results["session_id"]
        
        # Save motivation letter
        letter_path = f"data/output/motivation_letters/letter_{session_id}.txt"
        os.makedirs(os.path.dirname(letter_path), exist_ok=True)
        with open(letter_path, 'w', encoding='utf-8') as f:
            f.write(results["motivation_letter"])
        
        # Save CV suggestions
        cv_path = f"data/output/cv_suggestions/suggestions_{session_id}.json"
        os.makedirs(os.path.dirname(cv_path), exist_ok=True)
        with open(cv_path, 'w', encoding='utf-8') as f:
            json.dump(results["cv_suggestions"], f, indent=2, ensure_ascii=False)
