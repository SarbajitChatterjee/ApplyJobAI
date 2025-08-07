#!/usr/bin/env python3
"""
CV & Motivation Letter AI Agent - Environment-driven Configuration
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.agent_controller import CVMotivationAgent
from utils.validators import validate_inputs
from utils.logger import get_logger
from config.settings import LM_STUDIO_URL, MODEL_NAME

def check_lm_studio():
    """Check LM Studio connection using environment settings"""
    import requests
    try:
        response = requests.get(f"{LM_STUDIO_URL}/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"📡 LM Studio detected at {LM_STUDIO_URL}")
            print(f"📋 Models available: {len(models.get('data', []))}")
            return True
        return False
    except Exception as e:
        print(f"❌ LM Studio connection failed: {str(e)}")
        return False

def main():
    """Main execution with environment-driven configuration"""
    
    # Initialize logging
    logger = get_logger()
    logger.log_app_start({
        "lm_studio_url": LM_STUDIO_URL,
        "model_name": MODEL_NAME,
        "start_time": datetime.now().isoformat()
    })
    
    print("🚀 CV & Motivation Letter AI Agent")
    print("=" * 50)
    print(f"🔧 Using model: {MODEL_NAME}")
    print(f"🌐 LM Studio URL: {LM_STUDIO_URL}")
    
    try:
        # Check LM Studio
        logger.log_processing_step("Checking LM Studio Connection")
        if not check_lm_studio():
            logger.error_logger.error("LM Studio connection failed")
            print("\n❌ Please ensure:")
            print(f"  1. LM Studio is running on {LM_STUDIO_URL}")
            print(f"  2. {MODEL_NAME} model is loaded and serving")
            print("  3. Local server is enabled in LM Studio")
            return
        
        # Initialize agent with environment settings
        logger.log_processing_step("Initializing Agent")
        agent = CVMotivationAgent()
        
        # Collect user inputs
        logger.log_processing_step("Collecting User Inputs")
        print("\n📝 Please provide the following information:")
        
        # Get job profile
        print("\n📋 Job Profile:")
        print("Paste the complete job description below (press Enter twice when done):")
        job_profile_lines = []
        empty_line_count = 0
        
        while True:
            try:
                line = input()
                if not line.strip():
                    empty_line_count += 1
                    if empty_line_count >= 2:
                        break
                else:
                    empty_line_count = 0
                    job_profile_lines.append(line)
            except KeyboardInterrupt:
                print("\n👋 Application cancelled by user")
                return
        
        job_profile = "\n".join(job_profile_lines)
        logger.log_user_interaction("job_profile_provided", details=f"Length: {len(job_profile)} chars")
        
        if not job_profile.strip():
            print("❌ No job profile provided. Exiting.")
            return
        
        # Get CV file path
        cv_file_path = input("\n📄 Enter the path to your CV file (PDF, DOCX, or TXT): ").strip()
        logger.log_user_interaction("cv_file_provided", details=cv_file_path)
        
        # Get CV language preference
        cv_language = input("\n🌍 CV language preference (default: English): ").strip() or "English"
        logger.log_user_interaction("language_selected", details=cv_language)
        
        # Validate inputs
        logger.log_processing_step("Validating Inputs")
        print("\n🔍 Validating inputs...")
        
        if not validate_inputs(job_profile, cv_file_path, cv_language):
            logger.error_logger.error("Input validation failed")
            print("\n❌ Input validation failed. Please check your inputs and try again.")
            return
        
        print("✅ All inputs validated successfully!")
        
        # Process application
        logger.log_processing_step("Starting Main Application Processing")
        print(f"\n🔄 Processing your application with {MODEL_NAME}...")
        print("⚠️ Note: Local processing may take longer than cloud APIs")
        print("💡 The agent will analyze each CV section interactively")
        
        # Run the main processing workflow
        results = agent.process_application(job_profile, cv_file_path, cv_language)
        
        # Display results
        print("\n🎊 Processing completed successfully!")
        agent.display_results(results)
        
        logger.log_processing_step("Application Completed Successfully")
        
        # Offer to save additional formats or make modifications
        print(f"\n📁 All results have been saved to the data/output/ directory")
        print(f"📧 Your motivation letter is ready to send!")
        print(f"📋 CV suggestions are available for implementation")
        
    except KeyboardInterrupt:
        logger.log_user_interaction("application_cancelled", details="User pressed Ctrl+C")
        print("\n👋 Application cancelled by user")
        
    except Exception as e:
        logger.log_error(e, "Main Application")
        print(f"❌ Unexpected error: {str(e)}")
        print("Check the logs directory for detailed error information")
        
    finally:
        logger.app_logger.info("🏁 Application session ended")

if __name__ == "__main__":
    main()
