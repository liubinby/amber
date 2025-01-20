# models/ollama_model.py
from typing import List, Dict
from .base_model import BaseModel
import requests
import json

class OllamaModel(BaseModel):
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model_name = None
        self.available_models = self.get_available_models()
    
    def get_available_models(self) -> List[str]:
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models_data = response.json().get("models", [])
                return [model["name"] for model in models_data]
            print(f"Failed to get models: HTTP {response.status_code}")
            return []
        except Exception as e:
            print(f"Error getting available models: {str(e)}")
            return []
    
    def set_model(self, model_name: str) -> None:
        """Set the model to use for generation"""
        self.model_name = model_name
    
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        if not self.model_name:
            return "Error: No model selected"
            
        try:
            # Format messages for Ollama
            formatted_messages = [
                {
                    "role": msg["role"],
                    "content": msg["content"]
                }
                for msg in messages
            ]
            
            # Make request to Ollama
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": formatted_messages,
                    "stream": False
                }
            )
            
            # Debug information
            print(f"Request to: {self.base_url}/api/chat")
            print(f"Model: {self.model_name}")
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()["message"]["content"]
            elif response.status_code == 404:
                return f"Error: Model '{self.model_name}' not found. Please make sure the model is properly installed in Ollama."
            else:
                return f"Error: HTTP {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    async def get_title_from_first_message(self, message: str) -> str:
        if not self.model_name:
            return "New Chat"
            
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": "Generate a very short title (3-5 words) for a chat that starts with this message: " + message,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                return response.json()["response"].strip()
            return "New Chat"
        except Exception:
            return "New Chat"