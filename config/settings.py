"""
Configuration settings for CV & Motivation Letter AI Agent
"""

# Supported file types for CV uploads
SUPPORTED_FILE_TYPES = [
    '.pdf',
    '.doc',
    '.docx',
    '.txt'
]

# OpenAI API configuration
OPENAI_MODEL = "gpt-4"
MAX_TOKENS = 2000
TEMPERATURE = 0.7 