import google.generativeai as genai
from typing import List, Dict
from .base_model import BaseModel

class GeminiModel(BaseModel):
    def __init__(self, model_name="gemini-pro"):
        super().__init__(model_name)
        genai.configure(api_key=self.config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name)
        self.available_models = ["gemini-pro", "gemini-2.0-flash-exp"]

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        try:
            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

    async def get_title_from_first_message(self, message: str) -> str:
        """Generate a title from the first message"""
        try:
            response = self.model.generate_content(
                f"Generate a short 2-3 word title for this chat: {message}"
            )
            return response.text.strip().strip('"').strip("'")
        except Exception as e:
            return f"New Chat"
