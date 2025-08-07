#!/usr/bin/env python3
"""
Simple setup script for CV & Motivation Letter Agent
Creates directory structure and initializes configuration files
"""

import os
import json

def create_directories():
    """Create all required directories for the agent"""
    directories = [
        "logs",
        "data/input/job_profiles", 
        "data/input/cvs",
        "data/output/motivation_letters",
        "data/output/cv_suggestions", 
        "data/output/sessions",
        "data/cache",
        "config",
        "core",
        "utils", 
        "templates",
        "tests",
        "docs"
    ]
    
    print("📁 Creating directory structure...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ {directory}")

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        env_content = """# LM Studio Configuration
LM_STUDIO_URL=http://localhost:1234
MODEL_NAME=gpt-oss-20b
REQUEST_TIMEOUT=300

# Logging Configuration
LOG_LEVEL=INFO
LOG_TO_CONSOLE=true

# Processing Settings
CACHE_COMPANY_RESEARCH=true
MAX_FILE_SIZE_MB=10
SAVE_RESULTS_LOCALLY=true
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("  ✅ .env file created")
    else:
        print("  ✅ .env file already exists")

def create_config_files():
    """Create configuration files"""
    
    # Create sample user profile
    profile_path = "config/user_profile.json"
    if not os.path.exists(profile_path):
        sample_profile = {
            "personal_info": {
                "name": "Your Name",
                "current_location": "Germany", 
                "relocation_ready": True,
                "availability": "immediate"
            },
            "core_background": {
                "primary_experience": "Delivery management, QA automation, DevOps, stakeholder coordination",
                "international_experience": "Cross-functional teams, international collaboration", 
                "years_experience": 5
            },
            "transition_elements": {
                "education": "MBA in European Management (Germany)",
                "certifications": ["IBM Product Management", "Coursera PM courses"],
                "strategic_projects": ["IoT venture", "EV analytics", "AI agent development"]
            },
            "personality_traits": {
                "core_traits": ["confident", "excited to learn", "highly motivated"],
                "work_style": ["ready for high-pressure environments", "honest", "bold", "non-generic"]
            },
            "language_skills": {
                "fluent": ["English", "Hindi", "Bengali"],
                "learning": {"language": "German", "current_level": "B2", "target_level": "C1"}
            },
            "interests": {
                "hobbies": ["Football", "Movies", "Series", "Formula 1"]
            }
        }
        
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(sample_profile, f, indent=2, ensure_ascii=False)
        print("  ✅ config/user_profile.json created")

def create_init_files():
    """Create __init__.py files to make directories Python packages"""
    init_dirs = ["core", "utils", "config"]
    
    for directory in init_dirs:
        init_file = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write(f'"""{directory.title()} module for CV & Motivation Letter Agent"""\n')
            print(f"  ✅ {init_file}")

def main():
    """Main setup function"""
    print("🚀 Setting up CV & Motivation Letter AI Agent...")
    print("=" * 50)
    
    # Create directory structure
    create_directories()
    print()
    
    # Create configuration files
    print("⚙️ Creating configuration files...")
    create_env_file()
    create_config_files()
    create_init_files() 
    print()
    
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit config/user_profile.json with your information")
    print("2. Start LM Studio and load your GPT-OSS 20B model")  
    print("3. Enable local server in LM Studio (http://localhost:1234)")
    print("4. Run: python main.py")
    print("\n💡 Your agent is ready to generate CVs and motivation letters!")

if __name__ == "__main__":
    main()
