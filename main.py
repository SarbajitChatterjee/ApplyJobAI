#!/usr/bin/env python3
"""
CV & Motivation Letter AI Agent
Main entry point for running the agent
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.agent_controller import CVMotivationAgent
from utils.validators import validate_inputs
from config.settings import SUPPORTED_FILE_TYPES

def main():
    """Main execution function"""
    load_dotenv()
    
    print("🚀 CV & Motivation Letter AI Agent")
    print("=" * 50)
    
    # Initialize agent
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        return
    
    agent = CVMotivationAgent(api_key)
    
    # Collect inputs
    try:
        job_profile = input("📋 Paste the job profile: ")
        cv_file_path = input("📄 CV file path: ")
        cv_language = input("🌍 CV language preference (default: English): ") or "English"
        
        # Validate inputs
        if not validate_inputs(job_profile, cv_file_path, cv_language):
            return
        
        # Process application
        print("\n🔍 Processing your application...")
        results = agent.process_application(job_profile, cv_file_path, cv_language)
        
        # Display results
        agent.display_results(results)
        
    except KeyboardInterrupt:
        print("\n👋 Application cancelled by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()