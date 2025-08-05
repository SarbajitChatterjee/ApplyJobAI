"""
Input validation utilities for CV & Motivation Letter AI Agent
"""

import os
from typing import List

def validate_inputs(job_profile: str, cv_file_path: str, cv_language: str) -> bool:
    """Validate user inputs"""
    # Check if job profile is provided
    if not job_profile.strip():
        print("❌ Error: Job profile cannot be empty")
        return False
    
    # Check if CV file exists
    if not os.path.exists(cv_file_path):
        print(f"❌ Error: CV file not found at {cv_file_path}")
        return False
    
    # Check if CV file is readable
    if not os.access(cv_file_path, os.R_OK):
        print(f"❌ Error: Cannot read CV file at {cv_file_path}")
        return False
    
    # Validate language (basic check)
    if not cv_language.strip():
        print("❌ Error: CV language cannot be empty")
        return False
    
    return True 