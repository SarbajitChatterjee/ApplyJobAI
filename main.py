#!/usr/bin/env python3
"""
CV & Motivation Letter AI Agent with Comprehensive Logging
"""

import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.agent_controller import CVMotivationAgent
from utils.validators import validate_inputs
from utils.logger import get_logger
from config.settings import LM_STUDIO_URL, MODEL_NAME

def main():
    """Main execution with comprehensive logging"""
    
    # Initialize logging first
    logger = get_logger()
    logger.log_app_start({
        "lm_studio_url": LM_STUDIO_URL,
        "model_name": MODEL_NAME,
        "start_time": datetime.now().isoformat()
    })
    
    print("🚀 CV & Motivation Letter AI Agent (LM Studio)")
    print("=" * 50)
    
    try:
        # Check LM Studio with logging
        logger.log_processing_step("Checking LM Studio Connection")
        if not check_lm_studio():
            logger.error_logger.error("LM Studio connection failed")
            return
        
        # Initialize agent
        logger.log_processing_step("Initializing Agent")
        agent = CVMotivationAgent(LM_STUDIO_URL, MODEL_NAME)
        
        # Collect inputs with logging
        logger.log_processing_step("Collecting User Inputs")
        print("\n📝 Please provide the following information:")
        
        job_profile = input("📋 Paste the job profile: ")
        logger.log_user_interaction("job_profile_provided", details=f"Length: {len(job_profile)} chars")
        
        cv_file_path = input("📄 CV file path: ")
        logger.log_user_interaction("cv_file_provided", details=cv_file_path)
        
        cv_language = input("🌍 CV language preference (default: English): ") or "English"
        logger.log_user_interaction("language_selected", details=cv_language)
        
        # Validate inputs
        logger.log_processing_step("Validating Inputs")
        if not validate_inputs(job_profile, cv_file_path, cv_language):
            logger.error_logger.error("Input validation failed")
            return
        
        # Process application
        logger.log_processing_step("Starting Main Application Processing")
        print(f"\n🔍 Processing with {MODEL_NAME}...")
        print("⚠️ Note: Local processing may take longer than cloud APIs")
        
        results = agent.process_application(job_profile, cv_file_path, cv_language)
        
        # Display results
        agent.display_results(results)
        
        logger.log_processing_step("Application Completed Successfully")
        
    except KeyboardInterrupt:
        logger.log_user_interaction("application_cancelled", details="User pressed Ctrl+C")
        print("\n👋 Application cancelled by user")
        
    except Exception as e:
        logger.log_error(e, "Main Application")
        print(f"❌ Error: {str(e)}")
        
    finally:
        logger.app_logger.info("🏁 Application session ended")

def check_lm_studio():
    """Check LM Studio with logging"""
    logger = get_logger()
    
    try:
        logger.log_processing_step("Testing LM Studio Connection")
        # ... rest of connection check with detailed logging
        return True
    except Exception as e:
        logger.log_error(e, "LM Studio Connection Check")
        return False

if __name__ == "__main__":
    main()