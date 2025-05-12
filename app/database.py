from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем URL подключения к базе данных из переменной окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Проверяем наличие URL
if not DATABASE_URL:
    logger.warning("DATABASE_URL не указан. Используется SQLite в памяти.")
    DATABASE_URL = "sqlite:///:memory:"

# Создаем движок базы данных с отладочной информацией
engine = create_engine(
    DATABASE_URL, 
    echo=True,  # Включаем вывод SQL-запросов для отладки
    # Для SQLite нужно убедиться, что check_same_thread=False
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для моделей
Base = declarative_base()

def get_db():
    """
    Создает и возвращает сессию базы данных,
    автоматически закрывая ее после использования.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Инициализирует базу данных (создает таблицы).
    Вызывается отдельно при запуске приложения.
    """
    try:
        # Создаем таблицы
        from app.models import Base
        logger.info("Создаем таблицы в базе данных...")
        Base.metadata.create_all(bind=engine)
        logger.info("Таблицы успешно созданы.")
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        return False