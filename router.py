# router.py
from typing import Dict, List, Optional
from models.openai_model import OpenAIModel
from models.ollama_model import OllamaModel
from models.gemini_model import GeminiModel
from models.base_model import BaseModel

class ModelRouter:
    def __init__(self):
        """Initialize the ModelRouter with available AI models."""
        self.models: Dict[str, BaseModel] = {}
        self._initialize_models()
        self.default_provider = "ollama"

    def _initialize_models(self) -> None:
        """Initialize available AI models."""
        try:
            self.models["openai"] = OpenAIModel()
        except Exception as e:
            print(f"Failed to initialize OpenAI model: {e}")

        try:
            self.models["ollama"] = OllamaModel()
        except Exception as e:
            print(f"Failed to initialize Ollama model: {e}")

        try:
            self.models["gemini"] = GeminiModel()
        except Exception as e:
            print(f"Failed to initialize Gemini model: {e}")

    def get_model(self, model_name: str) -> Optional[BaseModel]:
        """
        Get a specific model by name.
        
        Args:
            model_name (str): Name of the model to retrieve
            
        Returns:
            Optional[BaseModel]: The requested model instance or None if not found
        """
        return self.models.get(model_name.lower())

    def get_available_models(self) -> Dict[str, List[str]]:
        """
        Get all available models grouped by provider.
        
        Returns:
            Dict[str, List[str]]: Dictionary of available models
        """
        available_models = {}
            
        if "ollama" in self.models:
            try:
                available_models["ollama"] = self.models["ollama"].available_models
            except Exception as e:
                print(f"Failed to get Ollama models: {e}")
                available_models["ollama"] = []

        if "openai" in self.models:
            available_models["openai"] = ["gpt-3.5-turbo", "gpt-4"]

        if "gemini" in self.models:
            try:
                available_models["gemini"] = self.models["gemini"].available_models
            except Exception as e:
                print(f"Failed to get Gemini models: {e}")
                available_models["gemini"] = []
        
        return available_models

    def list_providers(self) -> List[str]:
        """
        Get list of available model providers.
        
        Returns:
            List[str]: List of provider names
        """
        return list(self.models.keys())
