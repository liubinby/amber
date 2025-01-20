# models/base_model.py
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
        """Generate a meaningful chat title from the first message.
        Extracts key topics and creates a concise, descriptive title.
        """
        # Extract key phrases (first 100 chars or first sentence)
        summary = message[:100].split('.')[0]
        
        # Remove common filler words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'at', 'by', 'for', 'in', 'of', 'on', 'to', 'with'}
        words = [word for word in summary.split() if word.lower() not in stop_words]
        
        # Create title from remaining words (max 8 words)
        title = ' '.join(words[:8])
        return title.strip() or "New Chat"
