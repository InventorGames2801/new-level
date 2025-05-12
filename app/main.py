from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging

from app.routes import auth, user, admin
from app.config import settings
from app.templates import templates

# Настройка логирования
level = logging.DEBUG if settings.DEBUG else logging.INFO
logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Инициализация FastAPI приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Приложение для изучения английского через игры",
    debug=settings.DEBUG
)

# Регистрация роутеров
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(admin.router)

# Настройка middleware для сессий
app.add_middleware(
    SessionMiddleware, 
    secret_key=settings.SECRET_KEY,      
    session_cookie="session_id",        
    same_site="strict",                
    https_only=True                   
)

# Создаем директорию для статических файлов в правильном месте
BASE_DIR = Path(__file__).resolve().parent
static_dir = BASE_DIR / "static"
if not static_dir.exists():
    static_dir.mkdir(exist_ok=True)
    logger.info(f"Создана директория для статических файлов: {static_dir.absolute()}")

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Получаем путь к директории шаблонов из объекта templates
templates_dir = None
try:
    # В новых версиях путь можно получить через loader.searchpath
    if hasattr(templates, 'env') and hasattr(templates.env, 'loader') and hasattr(templates.env.loader, 'searchpath'):
        templates_dir = templates.env.loader.searchpath[0]  # Первый путь из списка
    # В случае ошибки используем предполагаемый путь
    if not templates_dir:
        templates_dir = str(BASE_DIR / "templates")
except Exception as e:
    logger.warning(f"Не удалось определить путь к шаблонам: {e}")
    templates_dir = str(BASE_DIR / "templates")

# Печатаем информацию о путях для отладки
logger.info(f"Базовая директория: {BASE_DIR}")
logger.info(f"Директория статических файлов: {static_dir}")
logger.info(f"Директория шаблонов: {templates_dir}")
logger.info(f"DEBUG режим: {settings.DEBUG}")
logger.info(f"Автоматическая инициализация БД: {settings.INIT_DB}")

# Обработчик запуска приложения
@app.on_event("startup")
async def startup_event():
    """
    Выполняется при запуске приложения.
    Инициализирует базу данных, если это возможно.
    """
    logger.info("Приложение запускается...")
    
    # Инициализируем базу данных, если включен флаг INIT_DB
    if settings.INIT_DB:
        try:
            from app.database import init_db
            logger.info("Инициализация базы данных...")
            db_init_success = init_db()
            if db_init_success:
                logger.info("✓ База данных успешно инициализирована")
            else:
                logger.warning("✗ Не удалось инициализировать базу данных")
        except Exception as e:
            logger.error(f"✗ Ошибка при инициализации базы данных: {e}")
    else:
        logger.info("Инициализация базы данных отключена через настройки")

# Корневой маршрут для проверки работы API
@app.get("/api/health")
async def health_check():
    """
    Простой маршрут для проверки работоспособности API.
    """
    return {
        "status": "ok", 
        "message": "API работает",
        "debug": settings.DEBUG,
        "paths": {
            "base_dir": str(BASE_DIR),
            "static_dir": str(static_dir),
            "templates_dir": str(templates_dir)
        },
        "environment": {
            "init_db": settings.INIT_DB,
            "api_prefix": settings.API_V1_PREFIX,
            "project_name": settings.PROJECT_NAME
        }
    }