from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Google Calendar API
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    # Application Settings
    APP_NAME: str = "Personal Calendar Assistant"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Calendar Settings
    DEFAULT_TIMEZONE: str = "UTC"
    DEFAULT_EVENT_DURATION: int = 60  # minutes
    MIN_EVENT_DURATION: int = 15  # minutes
    MAX_EVENT_DURATION: int = 480  # minutes (8 hours)
    
    # NLP Settings
    MODEL_NAME: str = "gemini-1.5-flash"
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.7
    
    # Priority Levels
    PRIORITY_LEVELS: list = ["low", "medium", "high", "urgent"]
    
    # Reminder Settings
    DEFAULT_REMINDER_MINUTES: int = 30
    REMINDER_LEVELS: list = ["email", "popup", "sms"]
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings() 