"""
Motivation Letter Generator
Creates personalized, compelling motivation letters
"""

import re
from typing import Dict, Any

from utils.api_client import OpenAIClient
from utils.text_processor import TextProcessor
from config.settings import MOTIVATION_LETTER_MIN_WORDS, MOTIVATION_LETTER_MAX_WORDS

class MotivationLetterGenerator:
    """Generates tailored motivation letters following specific guidelines"""
    
    def __init__(self, api_client: OpenAIClient, user_profile: Dict[str, Any]):
        self.api_client = api_client
        self.user_profile = user_profile
        self.text_processor = TextProcessor()
    
    def generate_letter(self, job_profile: str, cv_data: Dict[str, str], 
                       company_data: Dict[str, Any]) -> str:
        """
        Generate a tailored motivation letter
        
        Args:
            job_profile: Job description
            cv_data: Finalized CV sections
            company_data: Company research data
            
        Returns:
            Generated motivation letter (410-430 words)
        """
        print("✍️ Generating motivation letter...")
        
        # Generate initial letter
        letter = self._generate_initial_letter(job_profile, cv_data, company_data)
        
        # Validate and adjust word count
        final_letter = self._validate_and_adjust_length(letter)
        
        # Final humanization pass
        humanized_letter = self._humanize_text(final_letter)
        
        return humanized_letter
    
    def _generate_initial_letter(self, job_profile: str, cv_data: Dict[str, str],
                                company_data: Dict[str, Any]) -> str:
        """Generate the initial motivation letter"""
        
        generation_prompt = f"""
        You are an expert motivation letter writer specializing in bold, authentic, and compelling letters.
        
        CONTEXT:
        - Target Company: {company_data.get('company_name', 'Unknown')}
        - Target Role: Based on job profile
        - Candidate: Transitioning from QA/DevOps to Product Management
        
        JOB PROFILE:
        {job_profile}
        
        COMPANY RESEARCH:
        {company_data.get('detailed_research', '')}
        
        CANDIDATE PROFILE:
        {self._format_user_profile()}
        
        FINALIZED CV SECTIONS:
        {self._format_cv_data(cv_data)}
        
        WRITING STYLE REQUIREMENTS:
        ✅ Bold and risky (80% bold, 20% safe), warm, natural, genuine, authentic
        ✅ Show personality, excitement, and true voice
        ✅ Avoid generic, ambiguous, cringe, or overly technical text
        ✅ Use simple, clear, skimmable language
        ✅ No contractions (avoid "you're", "I'm", etc.)
        ✅ Write "percent" as "%"
        ✅ Limit em-dash ("—") use to absolute necessity
        ✅ Avoid "and" - use alternatives or restructure sentences
        
        STRUCTURE REQUIREMENTS:
        
        PARAGRAPH 1 - OPENING HOOK:
        - Best possible hook showing genuine human interest
        - Address career pivot reasoning: "Some people pivot careers by chance. I proactively chose to do that. Why? To..."
        - Avoid cringy or overly safe openings
        - Show authentic motivation for transition
        
        PARAGRAPH 2 - WHY THIS COMPANY:
        - Based on company research and "Who we are"/"What we offer" sections
        - Show genuine understanding of company culture
        - Connect personal values with company values
        - Demonstrate research depth and authentic interest
        
        PARAGRAPH 3 - WHY CHOOSE ME:
        - Use solid factual data from CV sections
        - Apply STAR approach abstractly
        - Highlight transferable skills from IT/QA to PM
        - Show leadership, bias to action, readiness to work independently
        - Include international teamwork experience
        - Quantify achievements where possible
        
        PARAGRAPH 4 - WHAT TO LEARN:
        - Based on "What will be your role" sections
        - Turn potential weaknesses into curiosities to learn
        - Mention possibility of MBA thesis through this role
        - Show excitement about growth opportunities
        - Connect learning needs to career ambitions
        
        CLOSING REQUIREMENTS:
        - End with top-notch handshake line (~15 words)
        - Include: "I cannot wait and am open to starting immediately, with relocation being no issue for me."
        - Add: "Additionally, I am fluent in English, Hindi, and Bengali, and I am currently continuing my German language journey at the B2 level with the goal of reaching C1 to better connect with diverse teams and customers."
        
        CONTENT INCLUSIONS:
        ✅ MBA coursework relevance (SEM model, Strategic Management, Marketing of Innovation)
        ✅ Co-founding AI agent project
        ✅ IoT venture and EV analytics projects
        ✅ International collaboration experience
        ✅ Transition from technical to strategic roles
        ✅ Hobbies if space permits (football, movies, Formula 1)
        
        WORD COUNT: Target exactly {MOTIVATION_LETTER_MIN_WORDS}-{MOTIVATION_LETTER_MAX_WORDS} words
        FORMAT: No "Dear" opening, no "Best regards" closing
        TONE: Subtly confident, highly excited, warm, grounded, very human
        
        Generate the motivation letter now:
        """
        
        response = self.api_client.chat_completion(
            messages=[{"role": "user", "content": generation_prompt}],
            temperature=0.6,
            max_tokens=2000
        )
        
        return response
    
    def _format_user_profile(self) -> str:
        """Format user profile for prompt inclusion"""
        profile_text = f"""
        BACKGROUND: {self.user_profile.get('core_background', {}).get('primary_experience', '')}
        TRANSITION: {self.user_profile.get('transition_elements', {}).get('education', '')}
        CERTIFICATIONS: {', '.join(self.user_profile.get('transition_elements', {}).get('certifications', []))}
        PROJECTS: {', '.join(self.user_profile.get('transition_elements', {}).get('strategic_projects', []))}
        PERSONALITY: {', '.join(self.user_profile.get('personality_traits', {}).get('core_traits', []))}
        LANGUAGES: Fluent in {', '.join(self.user_profile.get('language_skills', {}).get('fluent', []))}
        LEARNING: {self.user_profile.get('language_skills', {}).get('learning', {}).get('language', '')} 
                  ({self.user_profile.get('language_skills', {}).get('learning', {}).get('current_level', '')} → 
                   {self.user_profile.get('language_skills', {}).get('learning', {}).get('target_level', '')})
        INTERESTS: {', '.join(self.user_profile.get('interests', {}).get('hobbies', []))}
        """
        return profile_text
    
    def _format_cv_data(self, cv_data: Dict[str, str]) -> str:
        """Format CV data for prompt inclusion"""
        formatted = ""
        for section, content in cv_data.items():
            formatted += f"\n{section.upper()}:\n{content[:300]}...\n"
        return formatted
    
    def _validate_and_adjust_length(self, letter: str) -> str:
        """Validate word count and adjust if necessary"""
        word_count = len(letter.split())
        
        if MOTIVATION_LETTER_MIN_WORDS <= word_count <= MOTIVATION_LETTER_MAX_WORDS:
            return letter
        
        if word_count < MOTIVATION_LETTER_MIN_WORDS:
            return self._expand_letter(letter, MOTIVATION_LETTER_MIN_WORDS - word_count)
        else:
            return self._compress_letter(letter, word_count - MOTIVATION_LETTER_MAX_WORDS)
    
    def _expand_letter(self, letter: str, words_needed: int) -> str:
        """Expand letter to meet minimum word count"""
        expansion_prompt = f"""
        Expand this motivation letter by approximately {words_needed} words while maintaining:
        - The same tone and style
        - Authenticity and genuineness
        - All key messages
        - Target word count: {MOTIVATION_LETTER_MIN_WORDS}-{MOTIVATION_LETTER_MAX_WORDS} words
        
        Current letter:
        {letter}
        
        Add meaningful content, not filler words.
        """
        
        return self.api_client.chat_completion(
            messages=[{"role": "user", "content": expansion_prompt}],
            temperature=0.4
        )
    
    def _compress_letter(self, letter: str, words_to_remove: int) -> str:
        """Compress letter to meet maximum word count"""
        compression_prompt = f"""
        Compress this motivation letter by approximately {words_to_remove} words while maintaining:
        - All key messages and impact
        - The same tone and authenticity
        - Logical flow and coherence
        - Target word count: {MOTIVATION_LETTER_MIN_WORDS}-{MOTIVATION_LETTER_MAX_WORDS} words
        
        Current letter:
        {letter}
        
        Remove redundancy and unnecessary words, not core content.
        """
        
        return self.api_client.chat_completion(
            messages=[{"role": "user", "content": compression_prompt}],
            temperature=0.4
        )
    
    def _humanize_text(self, text: str) -> str:
        """Apply final humanization to make text more natural"""
        humanization_prompt = f"""
        Humanize this motivation letter to sound more natural, engaging, and warm while maintaining professionalism.
        
        GUIDELINES:
        - Make it conversational but professional
        - Remove any robotic or overly formal phrasing
        - Add warmth and personality
        - Keep meaning intact but make more readable
        - Ensure it sounds like a real human wrote it
        - Avoid typical LLM patterns and clichés
        
        Current text:
        {text}
        
        Return the humanized version:
        """
        
        return self.api_client.chat_completion(
            messages=[{"role": "user", "content": humanization_prompt}],
            temperature=0.5
        )
