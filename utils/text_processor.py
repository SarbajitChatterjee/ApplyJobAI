"""
Text Processing Utilities
Helper functions for text manipulation and analysis
"""

import re
from typing import List, Dict

class TextProcessor:
    """Utility class for text processing operations"""
    
    def __init__(self):
        self.word_count_cache = {}
    
    def count_words(self, text: str) -> int:
        """Count words in text"""
        if text in self.word_count_cache:
            return self.word_count_cache[text]
        
        # Remove extra whitespace and count
        cleaned_text = re.sub(r'\s+', ' ', text.strip())
        word_count = len(cleaned_text.split())
        
        self.word_count_cache[text] = word_count
        return word_count
    
    def extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction
        words = re.findall(r'\b[A-Za-z]{' + str(min_length) + ',}\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 
            'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its',
            'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'man', 'men',
            'put', 'say', 'she', 'too', 'use', 'with', 'have', 'this', 'will', 'your',
            'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very',
            'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 'such',
            'take', 'than', 'them', 'well', 'were'
        }
        
        keywords = [word for word in words if word not in stop_words]
        return list(set(keywords))  # Remove duplicates
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\(\)\'\"]+', '', text)
        
        return text.strip()
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def calculate_readability_score(self, text: str) -> Dict[str, float]:
        """Calculate basic readability metrics"""
        words = text.split()
        sentences = self.split_into_sentences(text)
        
        if not sentences or not words:
            return {"words_per_sentence": 0, "avg_word_length": 0}
        
        words_per_sentence = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        return {
            "words_per_sentence": round(words_per_sentence, 2),
            "avg_word_length": round(avg_word_length, 2),
            "total_words": len(words),
            "total_sentences": len(sentences)
        }
