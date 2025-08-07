"""
CV Analysis Engine
Analyzes CV sections and provides tailored suggestions
"""

import json
import re
from typing import Dict, List, Any

from utils.api_client import LMStudioClient
from config.settings import CV_SECTIONS

class CVAnalyzer:
    """Analyzes CV content and provides section-by-section suggestions"""
    
    def __init__(self, api_client: LMStudioClient, user_profile: Dict[str, Any]):
        self.api_client = api_client
        self.user_profile = user_profile
    
    def analyze_sections(self, cv_content: str, job_profile: str, 
                        company_data: Dict[str, Any], cv_language: str = "English") -> Dict[str, str]:
        """
        Analyze CV section by section and provide tailored suggestions
        
        Args:
            cv_content: Full CV text content
            job_profile: Job description
            company_data: Company research data
            cv_language: Language for suggestions
            
        Returns:
            Dictionary of section suggestions
        """
        print("📊 Analyzing CV sections...")
        
        # Extract sections from CV
        cv_sections = self._extract_cv_sections(cv_content)
        section_suggestions = {}
        
        for section_name in CV_SECTIONS:
            if section_name.lower() in [s.lower() for s in cv_sections.keys()]:
                # Find matching section (case-insensitive)
                actual_section = next(s for s in cv_sections.keys() 
                                    if s.lower() == section_name.lower())
                section_content = cv_sections[actual_section]
            else:
                section_content = f"[{section_name} section not found in CV]"
            
            print(f"  🔍 Analyzing {section_name}...")
            suggestions = self._analyze_single_section(
                section_name, section_content, job_profile, company_data, cv_language
            )
            section_suggestions[section_name] = suggestions
        
        return section_suggestions
    
    def _extract_cv_sections(self, cv_content: str) -> Dict[str, str]:
        """Extract different sections from CV content"""
        sections = {}
        
        # Common section headers patterns
        section_patterns = {
            'Professional Profile': r'(?i)(professional\s+profile|profile|summary|objective)',
            'Experience': r'(?i)(experience|work\s+experience|employment|career)',
            'Education': r'(?i)(education|academic|qualifications)',
            'Skills': r'(?i)(skills|technical\s+skills|competencies)',
            'Projects': r'(?i)(projects|key\s+projects|notable\s+projects)',
            'Certifications': r'(?i)(certifications?|certificates?|credentials)'
        }
        
        # Split content into lines
        lines = cv_content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            section_found = False
            for section_name, pattern in section_patterns.items():
                if re.search(pattern, line):
                    # Save previous section
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content)
                    
                    # Start new section
                    current_section = section_name
                    current_content = []
                    section_found = True
                    break
            
            if not section_found and current_section:
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        # If no sections found, treat entire content as experience
        if not sections:
            sections['Experience'] = cv_content
        
        return sections
    
    def _analyze_single_section(self, section_name: str, section_content: str,
                               job_profile: str, company_data: Dict[str, Any], 
                               cv_language: str) -> str:
        """Analyze a single CV section and provide suggestions"""
        
        analysis_prompt = f"""
        You are a brutal but constructive CV optimization expert specializing in {cv_language} CVs.
        
        ANALYSIS CONTEXT:
        - Target Role: Based on job profile below
        - Company: {company_data.get('company_name', 'Unknown')}
        - Section: {section_name}
        - Language: {cv_language}
        
        JOB PROFILE:
        {job_profile[:1500]}...
        
        COMPANY RESEARCH:
        {company_data.get('detailed_research', '')[:1000]}...
        
        USER PROFILE:
        {json.dumps(self.user_profile, indent=2)}
        
        CURRENT CV SECTION - {section_name}:
        {section_content}
        
        CORE PRINCIPLES (MUST FOLLOW):
        ✅ Honest, bold, non-generic, no clichés
        ✅ ATS compliant with keyword alignment  
        ✅ Priority relevance - highest impact first
        ✅ Short, crisp, skimmable content
        ✅ STAR pattern for bullet points (Situation-Task-Action-Result)
        ✅ Maintain impressive storytelling flow
        ✅ Professional transition narrative (QA/automation → product/digitalization)
        
        QUALITY STANDARDS:
        ✅ Every element ties directly to role requirements
        ✅ Avoid long explanations - keep keyword-rich
        ✅ Scrutinize heavily with honest feedback
        ✅ Suggest reorganization for clarity/impact
        ✅ Professional profile: ~32 words, spell out "and"
        
        STRICT RULES:
        ❌ Never fabricate or exaggerate
        ❌ Ask when information incomplete  
        ❌ Measure suggestions against available space
        ❌ Ensure factual accuracy
        
        SPECIFIC INSTRUCTIONS FOR {section_name}:
        {self._get_section_specific_instructions(section_name)}
        
        Provide specific, actionable, and brutally honest suggestions for this {section_name} section.
        Focus on:
        1. 🎯 ATS optimization and keyword alignment
        2. 📈 Relevance to job requirements  
        3. 🎨 Space efficiency and formatting
        4. 💥 Impact and readability
        5. 🔍 Content improvements
        
        Be brutally honest and constructive. No generic feedback. Give specific examples of improvements.
        """
        
        response = self.api_client.chat_completion(
            messages=[{"role": "user", "content": analysis_prompt}],
            temperature=0.4,
            max_tokens=1500
        )
        
        return response
    
    def _get_section_specific_instructions(self, section_name: str) -> str:
        """Get specific instructions for each CV section"""
        instructions = {
            'Professional Profile': """
            - Keep to exactly ~32 words
            - Spell out "and" instead of using "&"
            - Show clear career direction and value proposition
            - Include 2-3 key strengths relevant to the role
            - Mention transition to product/digitalization if relevant
            """,
            'Experience': """
            - Use reverse chronological order
            - Each bullet point should follow STAR pattern
            - Quantify achievements with numbers/percentages where possible
            - Show progression and increasing responsibility
            - Highlight leadership, stakeholder management, cross-functional collaboration
            - Connect QA/DevOps experience to product management skills
            """,
            'Education': """
            - Start with most recent/relevant education (MBA)
            - Include relevant coursework if it aligns with job requirements
            - Mention thesis topic if relevant to role
            - Include GPA only if impressive (>3.5)
            - Add relevant projects or achievements
            """,
            'Skills': """
            - Categorize skills logically (Technical, Management, Languages)
            - Prioritize skills mentioned in job description
            - Use exact keywords from job posting
            - Show skill levels where appropriate
            - Remove outdated or irrelevant skills
            """,
            'Projects': """
            - Focus on projects most relevant to target role
            - Use STAR format: Challenge-Action-Result
            - Quantify impact and outcomes
            - Show leadership and initiative
            - Include MBA projects, IoT venture, EV analytics, AI agent
            """,
            'Certifications': """
            - List most relevant certifications first
            - Include completion dates
            - Add certification IDs if valuable
            - Remove expired or irrelevant certifications
            - Group by category if many certifications
            """
        }
        
        return instructions.get(section_name, "Optimize for relevance and impact.")
