from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "CryptoSentiment AI API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Las hacemos opcionales para que Docker no explote si no existen
    GEMINI_API_KEY: Optional[str] = None
    CRYPTOPANIC_API_KEY: Optional[str] = None
    
    GEMINI_MODEL: str = "gemini-3.1-pro-preview" # Actualizado a tu versión
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()