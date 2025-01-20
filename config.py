# config.py
import os
from dotenv import load_dotenv
import pathlib

class Config:
    @classmethod
    def initialize(cls):
        # Get the current directory where config.py is located
        current_dir = pathlib.Path(__file__).parent.resolve()
        env_path = current_dir / '.env'
        
        # Try to load .env and print debug info
        print(f"Looking for .env file at: {env_path}")
        if env_path.exists():
            print(f".env file found at {env_path}")
            load_dotenv(env_path)
        else:
            print(f".env file not found at {env_path}")
            # Try loading from parent directory
            parent_env_path = current_dir.parent / '.env'
            print(f"Trying parent directory: {parent_env_path}")
            if parent_env_path.exists():
                print(f".env file found at {parent_env_path}")
                load_dotenv(parent_env_path)
            else:
                print(f".env file not found at {parent_env_path}")

        # Print environment variables for debugging
        cls.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        print(f"OPENAI_API_KEY loaded: {'Yes' if cls.OPENAI_API_KEY else 'No'}")
        
        cls.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        print(f"GEMINI_API_KEY loaded: {'Yes' if cls.GEMINI_API_KEY else 'No'}")
        
        # Other config variables
        cls.APP_NAME = "Amber"
        cls.APP_VERSION = "1.0.0"
        cls.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        cls.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        cls.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
        cls.MAX_HISTORY_LENGTH = int(os.getenv("MAX_HISTORY_LENGTH", "30"))
        cls.DEFAULT_MODEL = "ollama/llama2"
        cls.DB_PATH = "amber_chat_history.db"

# Initialize config when module is imported
Config.initialize()
