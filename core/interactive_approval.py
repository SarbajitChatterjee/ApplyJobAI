"""
Interactive Approval System
Handles user interaction for CV section approval
"""

from typing import Dict, Any
from utils.api_client import OpenAIClient

class InteractiveApproval:
    """Manages interactive approval process for CV sections"""
    
    def __init__(self, api_client: OpenAIClient):
        self.api_client = api_client
    
    def section_approval_loop(self, section_suggestions: Dict[str, str]) -> Dict[str, str]:
        """
        Interactive section-by-section approval process
        
        Args:
            section_suggestions: Dictionary of section suggestions
            
        Returns:
            Dictionary of approved/modified suggestions
        """
        approved_sections = {}
        
        print("\n" + "="*60)
        print("📋 CV SECTION REVIEW & APPROVAL")
        print("="*60)
        print("Please review each section and choose: approve/modify/ask/skip")
        
        for section, suggestions in section_suggestions.items():
            print(f"\n{'='*20} {section.upper()} {'='*20}")
            print(suggestions)
            print("-" * 60)
            
            while True:
                print(f"\n📌 {section} options:")
                print("  • 'approve' - Accept suggestions as-is")
                print("  • 'modify' - Request modifications")
                print("  • 'ask' - Ask questions about suggestions")
                print("  • 'skip' - Skip this section for now")
                
                user_input = input(f"\nYour choice for {section}: ").lower().strip()
                
                if user_input == "approve":
                    approved_sections[section] = suggestions
                    print(f"✅ {section} approved!")
                    break
                    
                elif user_input == "modify":
                    modification = input("What modifications would you like? ")
                    modified_suggestions = self._modify_suggestions(
                        section, suggestions, modification
                    )
                    print(f"\n📝 Modified suggestions for {section}:")
                    print("-" * 40)
                    print(modified_suggestions)
                    print("-" * 40)
                    
                    confirm = input("Accept these modifications? (y/n): ").lower()
                    if confirm in ['y', 'yes']:
                        approved_sections[section] = modified_suggestions
                        print(f"✅ Modified {section} approved!")
                        break
                    else:
                        print("↩️ Let's try again...")
                        
                elif user_input == "ask":
                    question = input("What would you like to know? ")
                    answer = self._answer_question(section, suggestions, question)
                    print(f"\n💡 Answer: {answer}\n")
                    
                elif user_input == "skip":
                    print(f"⏭️ Skipping {section} for now")
                    break
                    
                else:
                    print("❌ Please enter 'approve', 'modify', 'ask', or 'skip'")
        
        return approved_sections
    
    def _modify_suggestions(self, section_name: str, original_suggestions: str, 
                           modification_request: str) -> str:
        """Apply user-requested modifications to suggestions"""
        
        modification_prompt = f"""
        You are a CV optimization expert. Modify the suggestions for the {section_name} section based on the user's request.
        
        ORIGINAL SUGGESTIONS:
        {original_suggestions}
        
        USER'S MODIFICATION REQUEST:
        {modification_request}
        
        Please provide updated suggestions that incorporate the user's feedback while maintaining:
        - Professional quality and impact
        - ATS optimization
        - Relevance to the target role
        - Honest and constructive tone
        
        Modified suggestions:
        """
        
        return self.api_client.chat_completion(
            messages=[{"role": "user", "content": modification_prompt}],
            temperature=0.4,
            max_tokens=1000
        )
    
    def _answer_question(self, section_name: str, suggestions: str, question: str) -> str:
        """Answer user questions about suggestions"""
        
        qa_prompt = f"""
        You are a helpful CV expert. Answer the user's question about the {section_name} section suggestions.
        
        SECTION SUGGESTIONS:
        {suggestions}
        
        USER'S QUESTION:
        {question}
        
        Provide a clear, helpful answer that explains the reasoning behind suggestions or clarifies any confusion.
        Be specific and actionable in your response.
        
        Answer:
        """
        
        return self.api_client.chat_completion(
            messages=[{"role": "user", "content": qa_prompt}],
            temperature=0.3,
            max_tokens=500
        )
