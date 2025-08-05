"""
OpenAI API Client
Wrapper for OpenAI API calls with error handling and configuration
"""

import openai
from typing import List, Dict, Any, Optional
import time
import json

class OpenAIClient:
    """Wrapper class for OpenAI API interactions"""
    
    def __init__(self, api_key: str, model: str = "gpt-4", temperature: float = 0.5):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
    
    def chat_completion(self, messages: List[Dict[str, str]], 
                       temperature: Optional[float] = None,
                       max_tokens: Optional[int] = None,
                       model: Optional[str] = None) -> str:
        """
        Make a chat completion request to OpenAI
        
        Args:
            messages: List of message dictionaries
            temperature: Override default temperature
            max_tokens: Maximum tokens to generate
            model: Override default model
            
        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or 2000
            )
            
            return response.choices[0].message.content
            
        except openai.RateLimitError:
            print("⏳ Rate limit hit, waiting 60 seconds...")
            time.sleep(60)
            return self.chat_completion(messages, temperature, max_tokens, model)
            
        except openai.APIError as e:
            print(f"❌ OpenAI API Error: {str(e)}")
            raise
            
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            raise
    
    def estimate_tokens(self, text: str) -> int:
        """Rough estimation of token count"""
        return len(text.split()) * 1.3  # Approximation
