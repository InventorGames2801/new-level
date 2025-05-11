from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()  # Загружаем переменные окружения из .env файла

class Settings(BaseSettings):
    """
    Централизованная конфигурация приложения на основе переменных окружения.
    
    Pydantic автоматически загружает значения из переменных окружения,
    а если они не заданы, использует значения по умолчанию.
    """
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Demo App"
    
    DATABASE_URL: str 
    
    # Настройки JWT токенов
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Создаем экземпляр настроек для использования в приложении
settings = Settings()