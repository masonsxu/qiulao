import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name: str = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    enable_ai: bool = os.getenv("ENABLE_AI", "True").lower() == "true"
    
    class Config:
        env_file = ".env"

settings = Settings()