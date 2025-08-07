"""
Application Settings - Configuration from Environment Variables
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LM Studio Configuration (from .env)
LM_STUDIO_URL = os.getenv('LM_STUDIO_URL', 'http://localhost:1234')
MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-oss-20b')
DEFAULT_TEMPERATURE = float(os.getenv('DEFAULT_TEMPERATURE', '0.5'))
DEFAULT_MAX_TOKENS = int(os.getenv('DEFAULT_MAX_TOKENS', '2000'))
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '300'))

# Model-specific temperatures (from .env)
CV_ANALYSIS_TEMPERATURE = float(os.getenv('CV_ANALYSIS_TEMPERATURE', '0.4'))
MOTIVATION_GENERATION_TEMPERATURE = float(os.getenv('MOTIVATION_GENERATION_TEMPERATURE', '0.6'))
COMPANY_RESEARCH_TEMPERATURE = float(os.getenv('COMPANY_RESEARCH_TEMPERATURE', '0.3'))

# Logging Configuration (from .env)
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_TO_CONSOLE = os.getenv('LOG_TO_CONSOLE', 'true').lower() == 'true'

# File Processing (from .env)
SUPPORTED_FILE_TYPES = os.getenv('SUPPORTED_FILE_TYPES', '.pdf,.docx,.txt').split(',')
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '10'))

# Output Configuration (from .env)
MOTIVATION_LETTER_MIN_WORDS = int(os.getenv('MOTIVATION_LETTER_MIN_WORDS', '410'))
MOTIVATION_LETTER_MAX_WORDS = int(os.getenv('MOTIVATION_LETTER_MAX_WORDS', '430'))
CV_PROFILE_TARGET_WORDS = int(os.getenv('CV_PROFILE_TARGET_WORDS', '32'))
SAVE_RESULTS_LOCALLY = os.getenv('SAVE_RESULTS_LOCALLY', 'true').lower() == 'true'

# Caching (from .env)
CACHE_COMPANY_RESEARCH = os.getenv('CACHE_COMPANY_RESEARCH', 'true').lower() == 'true'
CACHE_DURATION_DAYS = int(os.getenv('CACHE_DURATION_DAYS', '7'))

# Directories - these can stay hardcoded as they're structural
DATA_DIR = "data"
INPUT_DIR = os.path.join(DATA_DIR, "input")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
CONFIG_DIR = "config"
TEMPLATES_DIR = "templates"
LOGS_DIR = "logs"

# CV Sections for Analysis - structural, can stay
CV_SECTIONS = [
    "Professional Profile",
    "Experience", 
    "Education",
    "Skills",
    "Projects",
    "Certifications"
]
