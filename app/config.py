from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()  # Загружаем переменные окружения из .env файла


class Settings(BaseSettings):
    """
    Централизованная конфигурация приложения на основе переменных окружения.

    Pydantic автоматически загружает значения из переменных окружения,
    а если они не заданы, использует значения по умолчанию.
    """

    PROJECT_NAME: str = "FastAPI Demo App"

    DATABASE_URL: str

    # Настройки JWT токенов
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Настройки отладки
    DEBUG: bool = False

    # Инициализация базы данных при запуске
    INIT_DB: bool = False

    # Новый способ конфигурации в Pydantic v2
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "validate_assignment": True,
        "extra": "allow",
        "str_strip_whitespace": True,
    }


# Создаем экземпляр настроек для использования в приложении
settings = Settings()

# Выводим текущие настройки для отладки
if settings.DEBUG:
    print("=== Текущие настройки ===")
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
    print(f"API_V1_PREFIX: {settings.API_V1_PREFIX}")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"INIT_DB: {settings.INIT_DB}")
    print("========================")
