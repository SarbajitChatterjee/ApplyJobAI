"""
Input Validation Functions
"""

import os
from typing import Tuple

def validate_inputs(job_profile: str, cv_file_path: str, cv_language: str) -> bool:
    """Validate all user inputs"""
    
    # Validate job profile
    if not job_profile or len(job_profile.strip()) < 50:
        print("❌ Job profile must be at least 50 characters long")
        return False
    
    # Validate CV file
    if not os.path.exists(cv_file_path):
        print(f"❌ CV file not found: {cv_file_path}")
        return False
    
    # Check file extension
    valid_extensions = ['.pdf', '.docx', '.txt']
    file_ext = os.path.splitext(cv_file_path)[1].lower()
    if file_ext not in valid_extensions:
        print(f"❌ Unsupported file type: {file_ext}. Supported: {valid_extensions}")
        return False
    
    # Validate language
    supported_languages = ['English', 'German', 'French', 'Spanish']
    if cv_language not in supported_languages:
        print(f"❌ Unsupported language: {cv_language}. Supported: {supported_languages}")
        return False
    
    return True