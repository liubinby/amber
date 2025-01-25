# models/base_model.py
import re
from abc import ABC, abstractmethod
from typing import List, Dict
from config import Config

class BaseModel(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.config = Config()
    
    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response from the model"""
        pass
    
    @abstractmethod
    async def get_title_from_first_message(self, message: str) -> str:
        """Generate a concise chat title from the first message.
        Creates a focused title under 32 characters from key topics.
        """
        # Extract key phrases (first 100 chars or first sentence) before any "or" 
        summary = re.split(r'(?i)\s*or\s*', message[:100].split('.')[0])[0]
        
        # Remove common filler words and split phrases
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'at', 'by', 'for', 
                     'in', 'of', 'on', 'to', 'with', 'how', 'what', 'why', 'where', 'who', 'which', 'this', 'that'}
        # Split words including contractions/hyphens
        words = [word for word in re.findall(r"\b[\w'-]+\b", summary) if word.lower() not in stop_words]
        
        # Build title with exact length tracking (including spaces)
        title_parts = []
        current_length = 0
        for word in words:
            # Calculate length with space if not first word
            word_length = len(word) + (1 if title_parts else 0)
            if current_length + word_length <= 32:
                title_parts.append(word)
                current_length += word_length
            else:
                break
        title = ' '.join(title_parts).strip()
        return title or "New Chat"
