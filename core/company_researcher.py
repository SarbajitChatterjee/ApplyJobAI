"""
Company Research Module
Performs comprehensive company analysis for job applications
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from utils.api_client import OpenAIClient

class CompanyResearcher:
    """Handles comprehensive company research and analysis"""
    
    def __init__(self, api_client: OpenAIClient):
        self.api_client = api_client
        self.cache_dir = "data/cache"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def research_company(self, job_profile: str) -> Dict[str, Any]:
        """
        Extract company name and perform comprehensive research
        
        Args:
            job_profile: The complete job description text
            
        Returns:
            Dictionary containing company research data
        """
        # Extract company name from job profile
        company_name = self._extract_company_name(job_profile)
        
        # Check cache first
        cached_data = self._get_cached_research(company_name)
        if cached_data:
            print(f"📋 Using cached research for {company_name}")
            return cached_data
        
        # Perform fresh research
        print(f"🔍 Researching {company_name}...")
        research_data = self._perform_research(company_name, job_profile)
        
        # Cache the results
        self._cache_research(company_name, research_data)
        
        return research_data
    
    def _extract_company_name(self, job_profile: str) -> str:
        """Extract company name from job profile"""
        prompt = f"""
        Extract the company name from this job profile. Return ONLY the company name, nothing else.
        
        Job Profile:
        {job_profile[:1000]}...
        
        Company Name:
        """
        
        response = self.api_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=50
        )
        
        return response.strip()
    
    def _perform_research(self, company_name: str, job_profile: str) -> Dict[str, Any]:
        """Perform comprehensive company research"""
        
        research_prompt = f"""
        You are an expert company researcher. Research {company_name} comprehensively for a job application context.
        
        JOB PROFILE CONTEXT:
        {job_profile}
        
        Provide detailed research covering:
        
        1. COMPANY OVERVIEW:
           - Industry and market position
           - Company size and global presence
           - Core business areas and services
        
        2. CULTURE & VALUES:
           - Company mission and vision
           - Core values and principles
           - Work culture and environment
           - Employee value proposition
        
        3. RECENT DEVELOPMENTS (Last 6 months):
           - Major news and announcements
           - New initiatives or projects
           - Strategic partnerships
           - Market expansions or changes
        
        4. HIRING PREFERENCES:
           - What they typically look for in candidates
           - Preferred backgrounds and experiences
           - Skills they value most
           - Career development opportunities
        
        5. COMMUNICATION STYLE:
           - Company tone and personality
           - How they present themselves
           - Brand voice characteristics
        
        6. COMPETITIVE ADVANTAGES:
           - What sets them apart from competitors
           - Unique selling propositions
           - Innovation areas
        
        Be specific, factual, and focus on information relevant for tailoring job applications.
        Avoid generic corporate speak - provide actionable insights.
        """
        
        research_response = self.api_client.chat_completion(
            messages=[{"role": "user", "content": research_prompt}],
            temperature=0.3,
            max_tokens=3000
        )
        
        return {
            "company_name": company_name,
            "research_date": datetime.now().isoformat(),
            "detailed_research": research_response,
            "job_profile_context": job_profile[:500] + "..." if len(job_profile) > 500 else job_profile
        }
    
    def _get_cached_research(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Check if we have recent cached research for this company"""
        cache_file = os.path.join(self.cache_dir, f"{company_name.replace(' ', '_').lower()}_research.json")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # Check if cache is less than 7 days old
            cache_date = datetime.fromisoformat(cached_data.get('research_date', ''))
            if datetime.now() - cache_date < timedelta(days=7):
                return cached_data
            
        except (json.JSONDecodeError, ValueError, KeyError):
            pass
        
        return None
    
    def _cache_research(self, company_name: str, research_data: Dict[str, Any]):
        """Cache research data for future use"""
        cache_file = os.path.join(self.cache_dir, f"{company_name.replace(' ', '_').lower()}_research.json")
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(research_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Warning: Could not cache research data: {str(e)}")
