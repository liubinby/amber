# models/openai_model.py
from typing import List, Dict
from .base_model import BaseModel
from openai import AsyncOpenAI
from config import Config

class OpenAIModel(BaseModel):
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is not set")
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
    
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    async def get_title_from_first_message(self, message: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Generate a short, concise title (3-5 words) for this conversation based on the user's first message."},
                    {"role": "user", "content": message}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return "New Chat"