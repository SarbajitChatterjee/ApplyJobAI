#!/usr/bin/env python3
"""
Setup script for CV & Motivation Letter AI Agent
"""

from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
def read_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read long description from README
def read_readme():
    readme_path = 'README.md'
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "CV & Motivation Letter AI Agent using LM Studio"

# Create directories function
def create_project_structure():
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
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # Create __init__.py files for Python packages
        if directory in ['core', 'utils', 'config']:
            init_file = os.path.join(directory, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write('# Package initialization\n')

setup(
    name='cv-motivation-agent',
    version='1.0.0',
    description='AI-powered CV and Motivation Letter Generator using LM Studio',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/cv-motivation-agent',
    
    # Package discovery
    packages=find_packages(include=['core', 'core.*', 'utils', 'utils.*', 'config', 'config.*']),
    
    # Python version requirement
    python_requires='>=3.8',
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Optional dependencies
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'black>=23.0.0', 
            'flake8>=6.0.0',
        ],
        'enhanced': [
            'colorlog>=6.7.0',
            'loguru>=0.7.0',
        ]
    },
    
    # Entry points (command-line interfaces)
    entry_points={
        'console_scripts': [
            'cv-agent=main:main',
        ],
    },
    
    # Package data
    include_package_data=True,
    package_data={
        'config': ['*.json'],
        'templates': ['*.txt'],
    },
    
    # Project metadata
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Office/Business :: Human Resources',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    
    keywords='cv resume motivation letter ai lm-studio job application'

    # {Optional}
    # project_urls={
    #     'Bug Reports': 'https://github.com/yourusername/cv-motivation-agent/issues',
    #     'Documentation': 'https://github.com/yourusername/cv-motivation-agent/wiki',
    # },
)

# Post-installation setup
if __name__ == "__main__":
    print("🚀 Setting up CV & Motivation Letter Agent...")
    create_project_structure()
    print("✅ Project structure created!")
    print("\nNext steps:")
    print("1. Edit config/user_profile.json with your information") 
    print("2. Create .env file with your LM Studio settings")
    print("3. Start LM Studio and load your GPT-OSS 20B model")
    print("4. Run: python main.py")