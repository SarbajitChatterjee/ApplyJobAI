"""
Interactive Approval System with Comprehensive Logging
"""

from typing import Dict, Any
from utils.api_client import LMStudioClient
from utils.logger import get_logger

class InteractiveApproval:
    """Manages interactive approval with detailed user interaction logging"""
    
    def __init__(self, api_client: LMStudioClient):
        self.api_client = api_client
        self.logger = get_logger()
    
    def section_approval_loop(self, section_suggestions: Dict[str, str]) -> Dict[str, str]:
        """Interactive approval with comprehensive logging"""
        
        self.logger.log_processing_step("Starting Interactive Approval", 
                                      f"Sections to review: {len(section_suggestions)}")
        
        approved_sections = {}
        
        print("\n" + "="*60)
        print("📋 CV SECTION REVIEW & APPROVAL")
        print("="*60)
        print("Please review each section and choose: approve/modify/ask/skip")
        
        for section_index, (section, suggestions) in enumerate(section_suggestions.items(), 1):
            self.logger.log_user_interaction("section_review_start", section)
            
            print(f"\n{'='*20} {section.upper()} ({section_index}/{len(section_suggestions)}) {'='*20}")
            print(suggestions)
            print("-" * 60)
            
            section_start_time = datetime.now()
            attempt_count = 0
            
            while True:
                attempt_count += 1
                
                print(f"\n📌 {section} options:")
                print("  • 'approve' - Accept suggestions as-is")
                print("  • 'modify' - Request modifications")  
                print("  • 'ask' - Ask questions about suggestions")
                print("  • 'skip' - Skip this section for now")
                
                user_input = input(f"\nYour choice for {section}: ").lower().strip()
                
                # Log user input
                self.logger.log_user_interaction("choice_made", section, user_input)
                
                if user_input == "approve":
                    approved_sections[section] = suggestions
                    
                    # Log approval with timing
                    duration = (datetime.now() - section_start_time).total_seconds()
                    self.logger.log_performance(f"Section Approval - {section}", duration, {
                        "action": "approved",
                        "attempts": attempt_count
                    })
                    
                    self.logger.log_user_interaction("section_approved", section)
                    print(f"✅ {section} approved!")
                    break
                    
                elif user_input == "modify":
                    modification = input("What modifications would you like? ")
                    self.logger.log_user_interaction("modification_requested", section, modification)
                    
                    # Process modification with logging
                    self.logger.log_processing_step("Processing Modification Request", 
                                                  f"Section: {section}")
                    
                    modified_suggestions = self._modify_suggestions(
                        section, suggestions, modification
                    )
                    
                    print(f"\n📝 Modified suggestions for {section}:")
                    print("-" * 40)
                    print(modified_suggestions)
                    print("-" * 40)
                    
                    confirm = input("Accept these modifications? (y/n): ").lower()
                    self.logger.log_user_interaction("modification_confirmation", section, confirm)
                    
                    if confirm in ['y', 'yes']:
                        approved_sections[section] = modified_suggestions
                        
                        # Log successful modification
                        duration = (datetime.now() - section_start_time).total_seconds()
                        self.logger.log_performance(f"Section Modification - {section}", duration, {
                            "action": "modified_and_approved",
                            "attempts": attempt_count
                        })
                        
                        self.logger.log_user_interaction("modified_section_approved", section)
                        print(f"✅ Modified {section} approved!")
                        break
                    else:
                        self.logger.log_user_interaction("modification_rejected", section)
                        print("↩️ Let's try again...")
                        
                elif user_input == "ask":
                    question = input("What would you like to know? ")
                    self.logger.log_user_interaction("question_asked", section, question)
                    
                    # Process question with logging
                    self.logger.log_processing_step("Processing Question", f"Section: {section}")
                    
                    answer = self._answer_question(section, suggestions, question)
                    print(f"\n💡 Answer: {answer}\n")
                    
                    self.logger.log_user_interaction("question_answered", section, f"Q: {question[:50]}...")
                    
                elif user_input == "skip":
                    # Log skip with timing
                    duration = (datetime.now() - section_start_time).total_seconds()
                    self.logger.log_performance(f"Section Skipped - {section}", duration, {
                        "action": "skipped",
                        "attempts": attempt_count
                    })
                    
                    self.logger.log_user_interaction("section_skipped", section)
                    print(f"⏭️ Skipping {section} for now")
                    break
                    
                else:
                    self.logger.log_user_interaction("invalid_choice", section, user_input)
                    print("❌ Please enter 'approve', 'modify', 'ask', or 'skip'")
        
        # Log completion summary
        self.logger.log_processing_step("Interactive Approval Completed", 
                                      f"Approved: {len(approved_sections)}/{len(section_suggestions)} sections")
        
        return approved_sections
    
    def _modify_suggestions(self, section_name: str, original_suggestions: str, 
                           modification_request: str) -> str:
        """Apply modifications with detailed logging"""
        
        self.logger.log_processing_step("Generating Modifications", 
                                      f"Section: {section_name}")
        
        # ... (rest of the method implementation with API logging)
    
    def _answer_question(self, section_name: str, suggestions: str, question: str) -> str:
        """Answer questions with detailed logging"""
        
        self.logger.log_processing_step("Answering User Question", 
                                      f"Section: {section_name}")
        
        # ... (rest of the method implementation with API logging)
